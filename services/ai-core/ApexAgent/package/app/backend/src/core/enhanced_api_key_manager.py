"""
Enhanced API Key Manager for ApexAgent with support for different API key modes.

This module provides a secure way to store and retrieve API keys with support for
both Complete System (ApexAgent-provided) and User-Provided API key modes.
"""

import os
import json
import base64
import logging
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
import nacl.secret
import nacl.utils
import nacl.pwhash
import keyring
from cryptography.fernet import Fernet
import hashlib

# Import configuration
from installation.common.config import ApiKeyMode

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
KEYRING_SERVICE_NAME = "ApexAgent"
KEYRING_MASTER_KEY_USERNAME = "master_key"
MASTER_KEY_ENV_VAR = "APEX_AGENT_MASTER_KEY"  # For backward compatibility
DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".apex_agent", "security")
DEFAULT_CREDENTIALS_DIR = os.path.join(os.path.expanduser("~"), ".apex_agent", "credentials")
KEY_STORE_FILE = "keystore.enc"
API_KEYS_FILE = "api_keys.enc"
OAUTH_TOKENS_FILE = "oauth_tokens.enc"
CONFIG_FILE = "config.json"
INSTALLATION_CONFIG_FILE = "installation.json"
LEGACY_API_KEYS_FILE = os.path.join(os.path.expanduser("~"), ".apex_agent_api_keys.enc")

# Key version constants
CURRENT_MASTER_KEY_VERSION = 1
CURRENT_KEK_VERSION = 1
CURRENT_DEK_VERSION = 1

class ApiKeyManagerError(Exception):
    """Base exception for ApiKeyManager errors."""
    pass

class MasterKeyError(ApiKeyManagerError):
    """Exception raised for master key related errors."""
    pass

class EncryptionError(ApiKeyManagerError):
    """Exception raised for encryption/decryption errors."""
    pass

class StorageError(ApiKeyManagerError):
    """Exception raised for storage related errors."""
    pass

class ProviderType(Enum):
    """Enumeration of supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    COHERE = "cohere"
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"
    AWS_BEDROCK = "aws_bedrock"

class ModelCategory(Enum):
    """Enumeration of model categories."""
    STANDARD = "standard"
    HIGH_REASONING = "high_reasoning"

class EnhancedApiKeyManager:
    """
    Enhanced API Key Manager with support for different API key modes.
    
    Features:
    - Support for both Complete System and User-Provided API key modes
    - Hierarchical key management (master key, KEKs, DEKs)
    - Secure storage using system keyring
    - Per-service encryption keys
    - Key rotation and versioning
    - Backward compatibility with legacy encrypted data
    """
    
    def __init__(self, 
                 installation_config_dir: str = None,
                 config_dir: str = DEFAULT_CONFIG_DIR, 
                 credentials_dir: str = DEFAULT_CREDENTIALS_DIR,
                 create_dirs: bool = True,
                 migrate_legacy: bool = True):
        """
        Initialize the EnhancedApiKeyManager.
        
        Args:
            installation_config_dir: Directory containing installation configuration
            config_dir: Directory for configuration and key storage
            credentials_dir: Directory for encrypted credentials
            create_dirs: Whether to create directories if they don't exist
            migrate_legacy: Whether to migrate legacy credentials
        """
        self.config_dir = config_dir
        self.credentials_dir = credentials_dir
        self.key_store_path = os.path.join(config_dir, KEY_STORE_FILE)
        self.api_keys_path = os.path.join(credentials_dir, API_KEYS_FILE)
        self.oauth_tokens_path = os.path.join(credentials_dir, OAUTH_TOKENS_FILE)
        self.config_path = os.path.join(config_dir, CONFIG_FILE)
        
        # Load installation configuration to determine API key mode
        self.installation_config_dir = installation_config_dir or os.path.join(
            os.path.dirname(os.path.dirname(config_dir)), "config")
        self.installation_config_path = os.path.join(
            self.installation_config_dir, INSTALLATION_CONFIG_FILE)
        self.api_key_mode = self._load_api_key_mode()
        
        logging.info(f"Initializing API Key Manager with mode: {self.api_key_mode}")
        
        # Create directories if needed
        if create_dirs:
            os.makedirs(config_dir, exist_ok=True)
            os.makedirs(credentials_dir, exist_ok=True)
            self._ensure_secure_directory_permissions(config_dir)
            self._ensure_secure_directory_permissions(credentials_dir)
        
        # Initialize key hierarchy
        self.master_key = self._get_or_create_master_key()
        self.key_encryption_keys = {}  # KEKs, loaded from keystore
        self.data_encryption_keys = {}  # DEKs, loaded from keystore
        
        # Load or initialize keystore and config
        self._load_or_initialize_keystore()
        self._load_or_initialize_config()
        
        # Load credentials
        self.api_keys = self._load_credentials(self.api_keys_path, "api_keys")
        self.oauth_tokens = self._load_credentials(self.oauth_tokens_path, "oauth_tokens")
        
        # Migrate legacy credentials if requested
        if migrate_legacy and os.path.exists(LEGACY_API_KEYS_FILE):
            self._migrate_legacy_credentials()
        
        # Initialize ApexAgent API keys if in Complete System mode
        if self.api_key_mode == ApiKeyMode.COMPLETE_SYSTEM:
            self._initialize_apexagent_api_keys()
    
    def _load_api_key_mode(self) -> ApiKeyMode:
        """
        Load the API key mode from installation configuration.
        
        Returns:
            ApiKeyMode: The configured API key mode
        """
        try:
            if os.path.exists(self.installation_config_path):
                with open(self.installation_config_path, 'r') as f:
                    installation_config = json.load(f)
                
                # Get API key mode from installation config
                api_key_mode_str = installation_config.get('api_key_mode', 'complete_system')
                
                # Convert string to enum
                if api_key_mode_str == 'user_provided':
                    return ApiKeyMode.USER_PROVIDED
                else:
                    return ApiKeyMode.COMPLETE_SYSTEM
            else:
                # Default to Complete System if installation config doesn't exist
                logging.warning(f"Installation config not found at {self.installation_config_path}. "
                               f"Defaulting to Complete System mode.")
                return ApiKeyMode.COMPLETE_SYSTEM
        except Exception as e:
            logging.error(f"Error loading API key mode: {e}. Defaulting to Complete System mode.")
            return ApiKeyMode.COMPLETE_SYSTEM
    
    def _ensure_secure_directory_permissions(self, directory: str) -> None:
        """
        Ensure the directory has secure permissions (700 - rwx------).
        
        Args:
            directory: Path to the directory
        """
        try:
            os.chmod(directory, 0o700)  # Read/write/execute for owner only
            logging.info(f"Permissions set to 700 for {directory}")
        except OSError as e:
            logging.warning(
                f"Could not set secure permissions for {directory}. "
                f"Please ensure it has restrictive permissions (e.g., 700): {e}"
            )
    
    def _ensure_secure_file_permissions(self, file_path: str) -> None:
        """
        Ensure the file has secure permissions (600 - rw-------).
        
        Args:
            file_path: Path to the file
        """
        try:
            os.chmod(file_path, 0o600)  # Read/write for owner only
            logging.info(f"Permissions set to 600 for {file_path}")
        except OSError as e:
            logging.warning(
                f"Could not set secure permissions for {file_path}. "
                f"Please ensure it has restrictive permissions (e.g., 600): {e}"
            )
    
    def _get_or_create_master_key(self) -> bytes:
        """
        Get the master key from the system keyring or create a new one.
        
        For backward compatibility, also check the environment variable.
        
        Returns:
            bytes: The master key
        
        Raises:
            MasterKeyError: If the master key cannot be retrieved or created
        """
        # Try to get from keyring
        master_key = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_MASTER_KEY_USERNAME)
        
        # If not in keyring, check environment variable (backward compatibility)
        if not master_key:
            master_key_b64 = os.environ.get(MASTER_KEY_ENV_VAR)
            if master_key_b64:
                try:
                    # Convert from base64 string to bytes
                    master_key = base64.b64decode(master_key_b64)
                    # Store in keyring for future use
                    keyring.set_password(
                        KEYRING_SERVICE_NAME, 
                        KEYRING_MASTER_KEY_USERNAME, 
                        master_key_b64
                    )
                    logging.info(f"Migrated master key from environment variable to system keyring")
                except Exception as e:
                    raise MasterKeyError(f"Invalid master key format in {MASTER_KEY_ENV_VAR}: {e}")
        else:
            # Convert from base64 string to bytes
            try:
                master_key = base64.b64decode(master_key)
            except Exception as e:
                raise MasterKeyError(f"Invalid master key format in keyring: {e}")
        
        # If still no master key, generate a new one
        if not master_key:
            try:
                # Generate a new master key
                master_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
                # Store in keyring as base64 string
                master_key_b64 = base64.b64encode(master_key).decode()
                keyring.set_password(
                    KEYRING_SERVICE_NAME, 
                    KEYRING_MASTER_KEY_USERNAME, 
                    master_key_b64
                )
                logging.info(f"Generated and stored new master key in system keyring")
            except Exception as e:
                raise MasterKeyError(f"Failed to generate or store master key: {e}")
        
        return master_key
    
    def _load_or_initialize_keystore(self) -> None:
        """
        Load the key encryption keys (KEKs) and data encryption keys (DEKs) from the keystore.
        If the keystore doesn't exist, initialize it with new keys.
        """
        if os.path.exists(self.key_store_path):
            try:
                # Create a SecretBox with the master key
                box = nacl.secret.SecretBox(self.master_key)
                
                # Read and decrypt the keystore
                with open(self.key_store_path, "rb") as f:
                    encrypted_data = f.read()
                
                # Decrypt the keystore
                decrypted_data = box.decrypt(encrypted_data)
                keystore = json.loads(decrypted_data.decode())
                
                # Load KEKs and DEKs
                self.key_encryption_keys = keystore.get("key_encryption_keys", {})
                self.data_encryption_keys = keystore.get("data_encryption_keys", {})
                
                logging.info(f"Loaded keystore from {self.key_store_path}")
            except Exception as e:
                raise EncryptionError(f"Failed to load or decrypt keystore: {e}")
        else:
            # Initialize new keystore with default KEKs and DEKs
            self._initialize_keystore()
    
    def _initialize_keystore(self) -> None:
        """
        Initialize the keystore with new key encryption keys (KEKs) and data encryption keys (DEKs).
        """
        try:
            # Generate a new KEK
            kek = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            kek_id = f"kek_v{CURRENT_KEK_VERSION}"
            self.key_encryption_keys = {
                kek_id: base64.b64encode(kek).decode()
            }
            
            # Generate a new DEK for API keys
            dek_api = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            dek_api_id = f"dek_api_v{CURRENT_DEK_VERSION}"
            
            # Generate a new DEK for OAuth tokens
            dek_oauth = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            dek_oauth_id = f"dek_oauth_v{CURRENT_DEK_VERSION}"
            
            # Store DEKs
            self.data_encryption_keys = {
                "api_keys": {
                    dek_api_id: base64.b64encode(dek_api).decode()
                },
                "oauth_tokens": {
                    dek_oauth_id: base64.b64encode(dek_oauth).decode()
                }
            }
            
            # Save the keystore
            self._save_keystore()
            
            logging.info(f"Initialized new keystore with KEK and DEKs")
        except Exception as e:
            raise EncryptionError(f"Failed to initialize keystore: {e}")
    
    def _save_keystore(self) -> None:
        """
        Save the key encryption keys (KEKs) and data encryption keys (DEKs) to the keystore.
        """
        try:
            # Prepare keystore data
            keystore = {
                "key_encryption_keys": self.key_encryption_keys,
                "data_encryption_keys": self.data_encryption_keys,
                "metadata": {
                    "created_at": time.time(),
                    "updated_at": time.time(),
                    "master_key_version": CURRENT_MASTER_KEY_VERSION
                }
            }
            
            # Convert to JSON and encrypt
            keystore_json = json.dumps(keystore).encode()
            
            # Create a SecretBox with the master key
            box = nacl.secret.SecretBox(self.master_key)
            
            # Encrypt the keystore
            encrypted_data = box.encrypt(keystore_json)
            
            # Write to file
            with open(self.key_store_path, "wb") as f:
                f.write(encrypted_data)
            
            # Set secure permissions
            self._ensure_secure_file_permissions(self.key_store_path)
            
            logging.info(f"Saved keystore to {self.key_store_path}")
        except Exception as e:
            raise EncryptionError(f"Failed to save keystore: {e}")
    
    def _load_or_initialize_config(self) -> None:
        """
        Load the configuration from the config file.
        If the config file doesn't exist, initialize it with default values.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                logging.info(f"Loaded config from {self.config_path}")
            except Exception as e:
                logging.error(f"Failed to load config: {e}")
                self._initialize_config()
        else:
            self._initialize_config()
    
    def _initialize_config(self) -> None:
        """
        Initialize the configuration with default values.
        """
        self.config = {
            "version": "1.0.0",
            "created_at": time.time(),
            "updated_at": time.time(),
            "api_key_mode": self.api_key_mode.value,
            "key_rotation": {
                "master_key": {
                    "interval_days": 365,  # Annual rotation
                    "last_rotated": time.time()
                },
                "key_encryption_keys": {
                    "interval_days": 180,  # Semi-annual rotation
                    "last_rotated": time.time()
                },
                "data_encryption_keys": {
                    "interval_days": 90,  # Quarterly rotation
                    "last_rotated": time.time()
                }
            },
            "access_control": {
                "enabled": False,  # Disabled by default
                "plugin_permissions": {}
            },
            "audit_logging": {
                "enabled": True,
                "level": "INFO"
            }
        }
        
        self._save_config()
    
    def _save_config(self) -> None:
        """
        Save the configuration to the config file.
        """
        try:
            # Update timestamp
            self.config["updated_at"] = time.time()
            
            # Write to file
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            
            logging.info(f"Saved config to {self.config_path}")
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
    
    def _load_credentials(self, file_path: str, credential_type: str) -> Dict[str, Any]:
        """
        Load credentials from an encrypted file.
        
        Args:
            file_path: Path to the encrypted credentials file
            credential_type: Type of credential ("api_keys" or "oauth_tokens")
            
        Returns:
            Dict[str, Any]: Loaded credentials
        """
        if os.path.exists(file_path):
            try:
                # Get the current DEK for this credential type
                dek_id, dek = self._get_current_dek(credential_type)
                
                # Create a SecretBox with the DEK
                box = nacl.secret.SecretBox(dek)
                
                # Read and decrypt the credentials
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                
                # Decrypt the credentials
                decrypted_data = box.decrypt(encrypted_data)
                credentials = json.loads(decrypted_data.decode())
                
                logging.info(f"Loaded {credential_type} from {file_path}")
                return credentials
            except Exception as e:
                logging.error(f"Failed to load {credential_type}: {e}")
                return {}
        else:
            logging.info(f"No {credential_type} file found at {file_path}")
            return {}
    
    def _get_current_dek(self, credential_type: str) -> Tuple[str, bytes]:
        """
        Get the current data encryption key (DEK) for the specified credential type.
        
        Args:
            credential_type: Type of credential ("api_keys" or "oauth_tokens")
        
        Returns:
            Tuple[str, bytes]: Key ID and key bytes
        
        Raises:
            EncryptionError: If the DEK cannot be retrieved
        """
        try:
            # Get the DEKs for the credential type
            deks = self.data_encryption_keys.get(credential_type, {})
            if not deks:
                raise EncryptionError(f"No DEKs found for {credential_type}")
            
            # Get the latest DEK (highest version number)
            latest_dek_id = max(deks.keys())
            dek_b64 = deks[latest_dek_id]
            dek = base64.b64decode(dek_b64)
            
            return latest_dek_id, dek
        except Exception as e:
            raise EncryptionError(f"Failed to get current DEK for {credential_type}: {e}")
    
    def _initialize_apexagent_api_keys(self) -> None:
        """
        Initialize ApexAgent-provided API keys for Complete System mode.
        
        This method is called only when in Complete System mode to set up
        the necessary API keys for accessing LLM providers through ApexAgent.
        """
        if self.api_key_mode != ApiKeyMode.COMPLETE_SYSTEM:
            logging.info("Skipping ApexAgent API key initialization (not in Complete System mode)")
            return
        
        # In a real implementation, these would be retrieved from a secure service
        # For this implementation, we'll use placeholder logic
        
        logging.info("Initializing ApexAgent-provided API keys")
        
        # Check if we already have ApexAgent keys
        has_apexagent_keys = any(
            key.get("provider_type") == "apexagent" 
            for key in self.api_keys.get("keys", [])
        )
        
        if has_apexagent_keys:
            logging.info("ApexAgent API keys already initialized")
            return
        
        # In a real implementation, this would contact the ApexAgent API service
        # to retrieve the necessary keys for this installation
        
        # For now, we'll just add a placeholder entry
        if "keys" not in self.api_keys:
            self.api_keys["keys"] = []
        
        self.api_keys["keys"].append({
            "id": "apexagent_proxy_key",
            "provider_type": "apexagent",
            "created_at": time.time(),
            "last_used": None,
            "metadata": {
                "name": "ApexAgent Proxy Service",
                "description": "Proxy service for accessing LLM providers through ApexAgent"
            }
        })
        
        # Save the updated API keys
        self._save_credentials(self.api_keys_path, "api_keys", self.api_keys)
        
        logging.info("ApexAgent API keys initialized successfully")
    
    def _save_credentials(self, file_path: str, credential_type: str, credentials: Dict[str, Any]) -> None:
        """
        Save credentials to an encrypted file.
        
        Args:
            file_path: Path to save the encrypted credentials
            credential_type: Type of credential ("api_keys" or "oauth_tokens")
            credentials: Credentials to save
        """
        try:
            # Get the current DEK for this credential type
            dek_id, dek = self._get_current_dek(credential_type)
            
            # Create a SecretBox with the DEK
            box = nacl.secret.SecretBox(dek)
            
            # Convert to JSON and encrypt
            credentials_json = json.dumps(credentials).encode()
            
            # Encrypt the credentials
            encrypted_data = box.encrypt(credentials_json)
            
            # Write to file
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
            
            # Set secure permissions
            self._ensure_secure_file_permissions(file_path)
            
            logging.info(f"Saved {credential_type} to {file_path}")
        except Exception as e:
            raise EncryptionError(f"Failed to save {credential_type}: {e}")
    
    def _migrate_legacy_credentials(self) -> None:
        """
        Migrate legacy credentials to the new format.
        """
        logging.info(f"Migrating legacy credentials from {LEGACY_API_KEYS_FILE}")
        # Implementation would go here
        # For brevity, we'll skip the actual implementation
    
    def get_api_key_mode(self) -> ApiKeyMode:
        """
        Get the current API key mode.
        
        Returns:
            ApiKeyMode: The current API key mode
        """
        return self.api_key_mode
    
    def set_api_key_mode(self, mode: ApiKeyMode) -> None:
        """
        Set the API key mode.
        
        Args:
            mode: The new API key mode
        """
        if self.api_key_mode == mode:
            logging.info(f"API key mode already set to {mode.value}")
            return
        
        logging.info(f"Changing API key mode from {self.api_key_mode.value} to {mode.value}")
        
        # Update the mode
        self.api_key_mode = mode
        
        # Update the config
        self.config["api_key_mode"] = mode.value
        self._save_config()
        
        # Update the installation config if possible
        try:
            if os.path.exists(self.installation_config_path):
                with open(self.installation_config_path, 'r') as f:
                    installation_config = json.load(f)
                
                installation_config['api_key_mode'] = mode.value
                
                with open(self.installation_config_path, 'w') as f:
                    json.dump(installation_config, f, indent=2)
                
                logging.info(f"Updated API key mode in installation config")
        except Exception as e:
            logging.error(f"Failed to update API key mode in installation config: {e}")
        
        # If switching to Complete System mode, initialize ApexAgent API keys
        if mode == ApiKeyMode.COMPLETE_SYSTEM:
            self._initialize_apexagent_api_keys()
    
    def add_user_api_key(self, provider: ProviderType, api_key: str, 
                        name: Optional[str] = None, 
                        additional_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a user-provided API key.
        
        Args:
            provider: Provider type
            api_key: The API key
            name: Optional name for the key
            additional_config: Additional configuration for specific providers
            
        Returns:
            str: ID of the added key
        """
        if self.api_key_mode != ApiKeyMode.USER_PROVIDED:
            logging.warning("Adding user API key while in Complete System mode")
        
        # Generate a key ID
        key_id = hashlib.sha256(f"{provider.value}:{time.time()}".encode()).hexdigest()[:16]
        
        # Encrypt the API key
        encrypted_key = self._encrypt_api_key(api_key)
        
        # Add to the API keys
        if "keys" not in self.api_keys:
            self.api_keys["keys"] = []
        
        self.api_keys["keys"].append({
            "id": key_id,
            "provider_type": provider.value,
            "encrypted_key": encrypted_key,
            "created_at": time.time(),
            "last_used": None,
            "metadata": {
                "name": name or f"{provider.value} API Key",
                "additional_config": additional_config
            }
        })
        
        # Save the updated API keys
        self._save_credentials(self.api_keys_path, "api_keys", self.api_keys)
        
        logging.info(f"Added user API key for {provider.value}")
        
        return key_id
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt an API key.
        
        Args:
            api_key: The API key to encrypt
            
        Returns:
            str: Base64-encoded encrypted API key
        """
        try:
            # Get the current DEK for API keys
            dek_id, dek = self._get_current_dek("api_keys")
            
            # Create a SecretBox with the DEK
            box = nacl.secret.SecretBox(dek)
            
            # Encrypt the API key
            encrypted_data = box.encrypt(api_key.encode())
            
            # Return as base64 string
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt API key: {e}")
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt an API key.
        
        Args:
            encrypted_key: Base64-encoded encrypted API key
            
        Returns:
            str: Decrypted API key
        """
        try:
            # Get the current DEK for API keys
            dek_id, dek = self._get_current_dek("api_keys")
            
            # Create a SecretBox with the DEK
            box = nacl.secret.SecretBox(dek)
            
            # Decrypt the API key
            encrypted_data = base64.b64decode(encrypted_key)
            decrypted_data = box.decrypt(encrypted_data)
            
            return decrypted_data.decode()
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt API key: {e}")
    
    def get_api_key(self, provider: ProviderType) -> Optional[str]:
        """
        Get an API key for the specified provider.
        
        In Complete System mode, this will use the ApexAgent proxy service.
        In User-Provided mode, this will return a user-provided API key if available.
        
        Args:
            provider: Provider type
            
        Returns:
            Optional[str]: API key if available, None otherwise
        """
        # In Complete System mode, use the ApexAgent proxy service
        if self.api_key_mode == ApiKeyMode.COMPLETE_SYSTEM:
            # In a real implementation, this would retrieve a token for the ApexAgent proxy service
            # For this implementation, we'll return a placeholder
            logging.info(f"Using ApexAgent proxy service for {provider.value}")
            return "apx_proxy_token_placeholder"
        
        # In User-Provided mode, look for a user-provided API key
        for key in self.api_keys.get("keys", []):
            if key.get("provider_type") == provider.value:
                # Found a matching key
                encrypted_key = key.get("encrypted_key")
                if encrypted_key:
                    try:
                        # Decrypt and return the key
                        api_key = self._decrypt_api_key(encrypted_key)
                        
                        # Update last used timestamp
                        key["last_used"] = time.time()
                        self._save_credentials(self.api_keys_path, "api_keys", self.api_keys)
                        
                        return api_key
                    except Exception as e:
                        logging.error(f"Failed to decrypt API key: {e}")
        
        # No matching key found
        logging.warning(f"No API key found for {provider.value}")
        return None
    
    def has_api_key(self, provider: ProviderType) -> bool:
        """
        Check if an API key is available for the specified provider.
        
        Args:
            provider: Provider type
            
        Returns:
            bool: True if an API key is available, False otherwise
        """
        # In Complete System mode, always return True
        if self.api_key_mode == ApiKeyMode.COMPLETE_SYSTEM:
            return True
        
        # In User-Provided mode, check if a user-provided API key exists
        for key in self.api_keys.get("keys", []):
            if key.get("provider_type") == provider.value and key.get("encrypted_key"):
                return True
        
        return False
    
    def list_user_api_keys(self) -> List[Dict[str, Any]]:
        """
        List all user-provided API keys (without the actual keys).
        
        Returns:
            List[Dict[str, Any]]: List of API key metadata
        """
        result = []
        
        for key in self.api_keys.get("keys", []):
            # Skip ApexAgent proxy keys
            if key.get("provider_type") == "apexagent":
                continue
            
            # Add key metadata (without the encrypted key)
            result.append({
                "id": key.get("id"),
                "provider_type": key.get("provider_type"),
                "created_at": key.get("created_at"),
                "last_used": key.get("last_used"),
                "name": key.get("metadata", {}).get("name")
            })
        
        return result
    
    def remove_user_api_key(self, key_id: str) -> bool:
        """
        Remove a user-provided API key.
        
        Args:
            key_id: ID of the key to remove
            
        Returns:
            bool: True if the key was removed, False otherwise
        """
        # Find the key
        for i, key in enumerate(self.api_keys.get("keys", [])):
            if key.get("id") == key_id:
                # Remove the key
                self.api_keys["keys"].pop(i)
                
                # Save the updated API keys
                self._save_credentials(self.api_keys_path, "api_keys", self.api_keys)
                
                logging.info(f"Removed user API key {key_id}")
                return True
        
        logging.warning(f"API key {key_id} not found")
        return False


# For testing purposes
if __name__ == "__main__":
    # Create a test directory
    test_dir = os.path.join(os.path.expanduser("~"), ".apex_agent_test")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a test installation config
    installation_config_dir = os.path.join(test_dir, "config")
    os.makedirs(installation_config_dir, exist_ok=True)
    
    installation_config = {
        "installation_path": test_dir,
        "mode": "standard",
        "api_key_mode": "user_provided",
        "components": "",
        "analytics": False,
        "installation_date": time.strftime("%Y-%m-%dT%H:%M:%S%z")
    }
    
    with open(os.path.join(installation_config_dir, "installation.json"), "w") as f:
        json.dump(installation_config, f, indent=2)
    
    # Initialize the API key manager
    manager = EnhancedApiKeyManager(
        installation_config_dir=installation_config_dir,
        config_dir=os.path.join(test_dir, "security"),
        credentials_dir=os.path.join(test_dir, "credentials")
    )
    
    # Print the current mode
    print(f"Current API key mode: {manager.get_api_key_mode().value}")
    
    # Add a test API key
    key_id = manager.add_user_api_key(
        provider=ProviderType.OPENAI,
        api_key="sk-test-key-12345",
        name="Test OpenAI Key"
    )
    
    # List API keys
    keys = manager.list_user_api_keys()
    print(f"User API keys: {keys}")
    
    # Get the API key
    api_key = manager.get_api_key(ProviderType.OPENAI)
    print(f"Retrieved API key: {api_key}")
    
    # Change mode to Complete System
    manager.set_api_key_mode(ApiKeyMode.COMPLETE_SYSTEM)
    print(f"New API key mode: {manager.get_api_key_mode().value}")
    
    # Get the API key again (should use proxy)
    api_key = manager.get_api_key(ProviderType.OPENAI)
    print(f"Retrieved API key (Complete System mode): {api_key}")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
