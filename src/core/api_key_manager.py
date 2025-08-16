# API Key and OAuth Token Manager for ApexAgent

import os
import json
from cryptography.fernet import Fernet
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

API_KEYS_FILE = os.path.join(os.path.expanduser("~"), ".apex_agent_api_keys.enc")
MASTER_KEY_ENV_VAR = "APEX_AGENT_MASTER_KEY"

def load_master_key_from_env():
    """Loads the master encryption key from the environment variable."""
    master_key_b64 = os.environ.get(MASTER_KEY_ENV_VAR)
    if not master_key_b64:
        error_msg = (
            f"Master encryption key not found. Please set the "
            f"'{MASTER_KEY_ENV_VAR}' environment variable. "
            f"You can generate a suitable key using Fernet.generate_key().decode()"
        )
        logging.error(error_msg)
        raise ValueError(error_msg)
    try:
        # Ensure the key is bytes
        return master_key_b64.encode()
    except Exception as e:
        logging.error(f"Invalid master key format in {MASTER_KEY_ENV_VAR}: {e}")
        raise ValueError(f"Invalid master key format in {MASTER_KEY_ENV_VAR}")

class ApiKeyManager:
    def __init__(self):
        """Initializes the ApiKeyManager, loading the encryption key from env."""
        self.master_key = load_master_key_from_env()
        try:
            self.fernet = Fernet(self.master_key)
        except Exception as e:
            logging.error(f"Failed to initialize Fernet with the provided master key: {e}")
            raise ValueError("Invalid master key, cannot initialize encryption engine.")
        
        self.api_keys_file = API_KEYS_FILE
        self._ensure_secure_file_permissions() # Attempt to set, or warn
        self.credentials = self._load_credentials()

    def _ensure_secure_file_permissions(self):
        """Ensures the API keys file has secure permissions if it exists."""
        if os.path.exists(self.api_keys_file):
            try:
                os.chmod(self.api_keys_file, 0o600) # Read/Write for owner only
                logging.info(f"Permissions set to 600 for {self.api_keys_file}")
            except OSError as e:
                logging.warning(
                    f"Could not set secure permissions for {self.api_keys_file}. "
                    f"Please ensure it has restrictive permissions (e.g., 600): {e}"
                )
        else:
            # If file doesn't exist, it will be created with default umask, 
            # then permissions set on next load if _save_credentials is called first.
            # We can also try to set permissions after first save.
            pass 

    def _load_credentials(self):
        """Loads and decrypts credentials from the storage file."""
        if not os.path.exists(self.api_keys_file):
            return {}
        try:
            with open(self.api_keys_file, "rb") as f:
                encrypted_data = f.read()
            if not encrypted_data:
                return {}
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logging.error(f"Error loading or decrypting credentials from {self.api_keys_file}: {e}. Starting with empty credentials.")
            # Consider if we should raise an error here or allow re-initialization
            # For now, returning empty to allow potential re-saving if the file was corrupted
            # but the key is correct.
            return {}

    def _save_credentials(self):
        """Encrypts and saves credentials to the storage file."""
        try:
            data_to_encrypt = json.dumps(self.credentials).encode()
            encrypted_data = self.fernet.encrypt(data_to_encrypt)
            
            # Create file with restrictive permissions if it doesn't exist
            # This is a bit tricky due to umask. We'll write then chmod.
            with open(self.api_keys_file, "wb") as f:
                f.write(encrypted_data)
            self._ensure_secure_file_permissions() # Ensure permissions after writing

        except Exception as e:
            logging.error(f"Error encrypting or saving credentials to {self.api_keys_file}: {e}")
            # In a production system, this should be handled more robustly.

    def set_api_key(self, service_name: str, api_key: str):
        """Stores a simple API key for a given service."""
        if "api_keys" not in self.credentials:
            self.credentials["api_keys"] = {}
        self.credentials["api_keys"][service_name] = api_key
        self._save_credentials()
        logging.info(f"API key set for service: {service_name}")

    def get_api_key(self, service_name: str) -> str | None:
        """Retrieves an API key for a given service."""
        key = self.credentials.get("api_keys", {}).get(service_name)
        if key:
            logging.debug(f"API key retrieved for service: {service_name}")
        else:
            logging.debug(f"No API key found for service: {service_name}")
        return key

    def set_oauth_token(self, service_name: str, token_data: dict):
        """
        Stores OAuth token data for a given service.
        token_data should be a dictionary, e.g.:
        {
            "access_token": "xyz",
            "refresh_token": "abc",
            "expires_at": 1678886400, # Unix timestamp for expiry
            "token_type": "Bearer",
            "scope": "read write"
        }
        """
        if "oauth_tokens" not in self.credentials:
            self.credentials["oauth_tokens"] = {}
        self.credentials["oauth_tokens"][service_name] = token_data
        self._save_credentials()
        logging.info(f"OAuth token set for service: {service_name}")

    def get_oauth_token(self, service_name: str) -> dict | None:
        """Retrieves OAuth token data for a given service."""
        token_info = self.credentials.get("oauth_tokens", {}).get(service_name)
        # Basic check for token expiry if 'expires_at' is present
        # A real implementation would also handle token refresh logic here or in the plugin itself.
        if token_info and "expires_at" in token_info:
            import time
            if time.time() > token_info["expires_at"]:
                logging.warning(f"OAuth token for {service_name} has expired. Refresh needed.")
                # Potentially trigger refresh logic here or return a specific status
                # For now, returning the expired token; calling code should check expiry.
        if token_info:
            logging.debug(f"OAuth token retrieved for service: {service_name}")
        else:
            logging.debug(f"No OAuth token found for service: {service_name}")
        return token_info

    def delete_credential(self, service_name: str, credential_type: str = "all"):
        """
        Deletes a credential for a given service.
        credential_type can be "api_key", "oauth_token", or "all".
        """
        removed = False
        if credential_type == "api_key" or credential_type == "all":
            if self.credentials.get("api_keys", {}).pop(service_name, None):
                removed = True
                logging.info(f"API key deleted for service: {service_name}")
        if credential_type == "oauth_token" or credential_type == "all":
            if self.credentials.get("oauth_tokens", {}).pop(service_name, None):
                removed = True
                logging.info(f"OAuth token deleted for service: {service_name}")
        
        if removed:
            self._save_credentials()
        return removed

    def list_configured_services(self) -> dict:
        """
        Lists all services for which API keys or OAuth tokens are configured.
        Returns a dictionary with keys "api_keys" and "oauth_tokens", 
        each containing a list of service names.
        """
        return {
            "api_keys": list(self.credentials.get("api_keys", {}).keys()),
            "oauth_tokens": list(self.credentials.get("oauth_tokens", {}).keys())
        }

# Example Usage (for testing - not part of the class itself)
if __name__ == "__main__":
    # To test this, you MUST set the APEX_AGENT_MASTER_KEY environment variable.
    # Example: export APEX_AGENT_MASTER_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    # Then run this script.
    print(f"Attempting to load master key from env var: {MASTER_KEY_ENV_VAR}")
    master_key_value = os.environ.get(MASTER_KEY_ENV_VAR)
    if not master_key_value:
        print(f"{MASTER_KEY_ENV_VAR} is not set. Please set it to run the example.")
        print("You can generate a key with: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" ")
        exit(1)
    
    print(f"{MASTER_KEY_ENV_VAR} found.")

    try:
        manager = ApiKeyManager()
        print("ApiKeyManager initialized successfully.")

        # Test API Key
        manager.set_api_key("openai_test", "sk-testkey1234567890")
        print(f"OpenAI Test Key: {manager.get_api_key('openai_test')}")

        # Test OAuth Token
        import time
        google_token_data = {
            "access_token": "google_access_token_example_secure",
            "refresh_token": "google_refresh_token_example_secure",
            "expires_at": int(time.time()) + 3600, # Expires in 1 hour
            "token_type": "Bearer",
            "scope": "calendar.readonly email.read"
        }
        manager.set_oauth_token("google_calendar_test", google_token_data)
        retrieved_google_token = manager.get_oauth_token("google_calendar_test")
        print(f"Google Calendar Test Token: {retrieved_google_token}")

        print(f"Configured Services: {manager.list_configured_services()}")

        # Test loading from scratch (simulates a new run of the agent)
        print("\n--- Testing loading from scratch (new ApiKeyManager instance) ---")
        manager2 = ApiKeyManager()
        print(f"OpenAI Test Key (manager2): {manager2.get_api_key('openai_test')}")
        print(f"Google Calendar Test Token (manager2): {manager2.get_oauth_token('google_calendar_test')}")
        print(f"Configured Services (manager2): {manager2.list_configured_services()}")

        # Clean up test keys
        # manager.delete_credential("openai_test")
        # manager.delete_credential("google_calendar_test")
        # print(f"Configured Services after cleanup: {manager.list_configured_services()}")

    except ValueError as ve:
        print(f"Error during ApiKeyManager usage: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


