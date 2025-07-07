"""
Together AI API Key Management System

This module implements secure API key management for Together AI integration,
ensuring all keys are managed exclusively through the admin dashboard.
"""

import os
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

# Import encryption utilities
from data_protection.core.encryption.encryption_service import EncryptionService, EncryptedData, EncryptionContext
from security.validation import validate_api_key_format
from admin.dashboard.models import ApiKeyEntry, ApiKeyProvider
from admin.dashboard.api_key_registry import register_provider

logger = logging.getLogger(__name__)

class TogetherAIKeyManager:
    """
    Secure API key manager for Together AI integration.
    
    This class handles the secure storage, retrieval, and rotation of
    Together AI API keys, ensuring all keys are managed exclusively
    through the admin dashboard.
    """
    
    PROVIDER_ID = "together_ai"
    PROVIDER_NAME = "Together AI"
    ENV_VAR_NAME = "TOGETHER_API_KEY"
    KEY_FILE_PATH = "config/secure/together_ai_keys.enc"
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the Together AI key manager.
        
        Args:
            config_dir: Optional configuration directory path
        """
        self.config_dir = config_dir or os.environ.get("AIDEON_CONFIG_DIR", ".")
        self.key_file_path = Path(self.config_dir) / self.KEY_FILE_PATH
        self.system_key = None
        self.user_keys = {}
        self.last_refresh = datetime.now()
        self.refresh_interval = timedelta(minutes=5)  # Refresh keys every 5 minutes
        self.encryption_service = EncryptionService() # Instantiate EncryptionService
        
        # Ensure the key file directory exists
        os.makedirs(os.path.dirname(self.key_file_path), exist_ok=True)
        
        # Initialize by loading keys
        self._load_keys()
    
    def _load_keys(self) -> None:
        """
        Load API keys from secure storage.
        
        This method loads both system default and user-provided keys
        from the encrypted key file.
        """
        try:
            if not os.path.exists(self.key_file_path):
                logger.info(f"API key file not found at {self.key_file_path}. Creating new file.")
                self._save_keys()
                return
            
            # Read and decrypt the key file
            with open(self.key_file_path, "rb") as f:
                encrypted_data_bytes = f.read()
            
            if not encrypted_data_bytes:
                logger.warning("Empty API key file. Initializing with empty keys.")
                return
            
            # Deserialize EncryptedData object
            encrypted_data_obj = EncryptedData.deserialize(encrypted_data_bytes)
            
            # Decrypt the data
            decrypted_json_bytes = self.encryption_service.decrypt(encrypted_data_obj)
            key_data = json.loads(decrypted_json_bytes.decode("utf-8"))
            
            # Extract keys
            self.system_key = key_data.get("system_key")
            self.user_keys = key_data.get("user_keys", {})
            
            logger.info(f"Successfully loaded API keys for {len(self.user_keys)} users")
            
        except Exception as e:
            logger.error(f"Failed to load API keys: {str(e)}")
            # Initialize with empty keys on error
            self.system_key = None
            self.user_keys = {}
    
    def _save_keys(self) -> None:
        """
        Save API keys to secure storage.
        
        This method encrypts and saves both system default and user-provided
        keys to the secure key file.
        """
        try:
            # Prepare data for encryption
            key_data = {
                "system_key": self.system_key,
                "user_keys": self.user_keys,
                "updated_at": datetime.now().isoformat()
            }
            
            # Encrypt the data
            json_data_bytes = json.dumps(key_data).encode("utf-8")
            encrypted_data_obj = self.encryption_service.encrypt(json_data_bytes)
            
            # Serialize EncryptedData object to bytes
            encrypted_data_bytes = encrypted_data_obj.serialize()
            
            # Save to file
            with open(self.key_file_path, "wb") as f:
                f.write(encrypted_data_bytes)
            
            logger.info(f"Successfully saved API keys to {self.key_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save API keys: {str(e)}")
    
    def refresh_keys(self) -> None:
        """
        Refresh API keys from the admin dashboard.
        
        This method should be called periodically to ensure the latest
        keys are being used.
        """
        current_time = datetime.now()
        if current_time - self.last_refresh < self.refresh_interval:
            # Skip refresh if within interval
            return
        
        try:
            # Reload keys from storage
            self._load_keys()
            
            # Update last refresh time
            self.last_refresh = current_time
            
            logger.info("Successfully refreshed API keys")
            
        except Exception as e:
            logger.error(f"Failed to refresh API keys: {str(e)}")
    
    def get_system_key(self) -> Optional[str]:
        """
        Get the system default API key.
        
        Returns:
            System default API key or None if not set
        """
        # Refresh keys if needed
        self.refresh_keys()
        
        # Try environment variable first (for development/testing)
        env_key = os.environ.get(self.ENV_VAR_NAME)
        if env_key:
            return env_key
        
        # Return system key from secure storage
        return self.system_key
    
    def get_user_key(self, user_id: str) -> Optional[str]:
        """
        Get the API key for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User's API key or None if not set
        """
        # Refresh keys if needed
        self.refresh_keys()
        
        # Return user key from secure storage
        return self.user_keys.get(user_id)
    
    def get_api_key(self, user_id: Optional[str] = None) -> Optional[str]:
        """
        Get the appropriate API key for the request.
        
        This method returns the user's API key if available,
        otherwise falls back to the system default key.
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            API key to use or None if no key is available
        """
        # If user ID is provided, try to get their key
        if user_id:
            user_key = self.get_user_key(user_id)
            if user_key:
                return user_key
        
        # Fall back to system key
        return self.get_system_key()
    
    def set_system_key(self, api_key: str) -> bool:
        """
        Set the system default API key.
        
        This method should only be called by the admin dashboard.
        
        Args:
            api_key: API key to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate the API key format
            if not validate_api_key_format(api_key, provider=self.PROVIDER_ID):
                logger.error(f"Invalid API key format for {self.PROVIDER_NAME}")
                return False
            
            # Set the system key
            self.system_key = api_key
            
            # Save to secure storage
            self._save_keys()
            
            logger.info(f"Successfully set system API key for {self.PROVIDER_NAME}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set system API key: {str(e)}")
            return False
    
    def set_user_key(self, user_id: str, api_key: str) -> bool:
        """
        Set the API key for a specific user.
        
        This method should only be called by the admin dashboard.
        
        Args:
            user_id: User identifier
            api_key: API key to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate the API key format
            if not validate_api_key_format(api_key, provider=self.PROVIDER_ID):
                logger.error(f"Invalid API key format for {self.PROVIDER_NAME}")
                return False
            
            # Set the user key
            self.user_keys[user_id] = api_key
            
            # Save to secure storage
            self._save_keys()
            
            logger.info(f"Successfully set user API key for {self.PROVIDER_NAME} (user: {user_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set user API key: {str(e)}")
            return False
    
    def delete_user_key(self, user_id: str) -> bool:
        """
        Delete the API key for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove the user key if it exists
            if user_id in self.user_keys:
                del self.user_keys[user_id]
                
                # Save to secure storage
                self._save_keys()
                
                logger.info(f"Successfully deleted user API key for {self.PROVIDER_NAME} (user: {user_id})")
                return True
            else:
                logger.warning(f"No API key found for user {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete user API key: {str(e)}")
            return False
    
    def rotate_system_key(self, new_api_key: str) -> bool:
        """
        Rotate the system default API key.
        
        This method should only be called by the admin dashboard.
        
        Args:
            new_api_key: New API key to set
            
        Returns:
            True if successful, False otherwise
        """
        old_key = self.system_key
        
        # Set the new key
        success = self.set_system_key(new_api_key)
        
        if success:
            logger.info(f"Successfully rotated system API key for {self.PROVIDER_NAME}")
            
            # Log key rotation event (masked keys)
            if old_key:
                old_masked = f"{old_key[:4]}...{old_key[-4:]}" if len(old_key) > 8 else "****"
                new_masked = f"{new_api_key[:4]}...{new_api_key[-4:]}" if len(new_api_key) > 8 else "****"
                logger.info(f"Rotated key from {old_masked} to {new_masked}")
        
        return success
    
    def register_with_admin_dashboard(self) -> None:
        """
        Register this key manager with the admin dashboard.
        
        This method should be called during application startup to ensure
        the admin dashboard is aware of this provider.
        """
        try:
            # Create provider entry
            provider_entry = ApiKeyProvider(
                id=self.PROVIDER_ID,
                name=self.PROVIDER_NAME,
                description="Together AI API key for accessing 100+ open-source models",
                env_var=self.ENV_VAR_NAME,
                required_for_tier="free",  # Required for free tier
                format_regex=r"^[a-zA-Z0-9]{40}$",  # Example format validation
                format_description="40-character alphanumeric API key",
                docs_url="https://docs.together.ai/docs/api-reference",
                has_system_key=self.system_key is not None,
                user_configurable=True  # Allow users to provide their own keys
            )
            
            # Register with admin dashboard
            register_provider(provider_entry)
            
            logger.info(f"Successfully registered {self.PROVIDER_NAME} with admin dashboard")
            
        except Exception as e:
            logger.error(f"Failed to register with admin dashboard: {str(e)}")
    
    def get_key_status(self) -> Dict[str, Any]:
        """
        Get the status of API keys.
        
        Returns:
            Dictionary with key status information
        """
        return {
            "provider": self.PROVIDER_NAME,
            "system_key_available": self.system_key is not None,
            "user_key_count": len(self.user_keys),
            "last_refresh": self.last_refresh.isoformat()
        }


# Singleton instance
_instance = None

def get_together_ai_key_manager() -> TogetherAIKeyManager:
    """
    Get the singleton instance of the Together AI key manager.
    
    Returns:
        Together AI key manager instance
    """
    global _instance
    if _instance is None:
        _instance = TogetherAIKeyManager()
    return _instance


