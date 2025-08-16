"""
API Key Manager Integration for Gemini Live API

This module integrates the EnhancedApiKeyManager with the Gemini Live API provider,
ensuring secure storage and retrieval of API keys.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import logging
import json
from typing import Dict, Optional, Any

# Import the EnhancedApiKeyManager from the ApexAgent codebase
# This assumes the ApexAgent code is available in the Python path
try:
    from apexagent.security.api_key_manager import EnhancedApiKeyManager
except ImportError:
    # Fallback implementation for development/testing
    class EnhancedApiKeyManager:
        """Fallback implementation of EnhancedApiKeyManager for development."""
        
        def __init__(self):
            self.logger = logging.getLogger("EnhancedApiKeyManager")
            self.logger.warning("Using fallback EnhancedApiKeyManager implementation")
            self._keys = {}
        
        def store_api_key(self, service_name: str, key_id: str, api_key: str) -> bool:
            """Store an API key."""
            self._keys[f"{service_name}:{key_id}"] = api_key
            return True
        
        def get_api_key(self, service_name: str, key_id: str) -> Optional[str]:
            """Retrieve an API key."""
            return self._keys.get(f"{service_name}:{key_id}")
        
        def delete_api_key(self, service_name: str, key_id: str) -> bool:
            """Delete an API key."""
            key = f"{service_name}:{key_id}"
            if key in self._keys:
                del self._keys[key]
                return True
            return False
        
        def list_keys(self, service_name: Optional[str] = None) -> Dict[str, Any]:
            """List available keys."""
            result = {}
            for key in self._keys:
                svc, kid = key.split(":", 1)
                if service_name is None or svc == service_name:
                    if svc not in result:
                        result[svc] = []
                    result[svc].append(kid)
            return result

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class GeminiKeyManager:
    """
    Manages API keys for the Gemini Live API integration using the EnhancedApiKeyManager.
    
    This class provides a secure interface for storing, retrieving, and managing
    Google API keys used by the Gemini Live API provider.
    
    Attributes:
        SERVICE_NAME (str): Service name used for key storage
        api_key_manager (EnhancedApiKeyManager): Instance of the EnhancedApiKeyManager
        logger (logging.Logger): Logger for the key manager
    """
    
    SERVICE_NAME = "google_gemini"
    
    def __init__(self):
        """Initialize the Gemini Key Manager."""
        self.api_key_manager = EnhancedApiKeyManager()
        self.logger = logging.getLogger("GeminiKeyManager")
        self.logger.info("GeminiKeyManager initialized")
    
    def store_api_key(self, key_id: str, api_key: str) -> bool:
        """
        Store a Google API key securely.
        
        Args:
            key_id: Identifier for the API key (e.g., "default", "production")
            api_key: The actual API key to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.api_key_manager.store_api_key(
                self.SERVICE_NAME, key_id, api_key
            )
            if result:
                self.logger.info(f"Successfully stored API key with ID: {key_id}")
            else:
                self.logger.error(f"Failed to store API key with ID: {key_id}")
            return result
        except Exception as e:
            self.logger.error(f"Error storing API key: {e}")
            return False
    
    def get_api_key(self, key_id: str = "default") -> Optional[str]:
        """
        Retrieve a Google API key.
        
        Args:
            key_id: Identifier for the API key (defaults to "default")
            
        Returns:
            str: The API key if found, None otherwise
        """
        try:
            api_key = self.api_key_manager.get_api_key(self.SERVICE_NAME, key_id)
            if api_key:
                self.logger.debug(f"Retrieved API key with ID: {key_id}")
            else:
                self.logger.warning(f"API key with ID {key_id} not found")
            return api_key
        except Exception as e:
            self.logger.error(f"Error retrieving API key: {e}")
            return None
    
    def delete_api_key(self, key_id: str) -> bool:
        """
        Delete a Google API key.
        
        Args:
            key_id: Identifier for the API key to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.api_key_manager.delete_api_key(self.SERVICE_NAME, key_id)
            if result:
                self.logger.info(f"Successfully deleted API key with ID: {key_id}")
            else:
                self.logger.warning(f"API key with ID {key_id} not found for deletion")
            return result
        except Exception as e:
            self.logger.error(f"Error deleting API key: {e}")
            return False
    
    def list_available_keys(self) -> Dict[str, Any]:
        """
        List all available Google API keys.
        
        Returns:
            Dict: Dictionary containing information about available keys
        """
        try:
            keys_info = self.api_key_manager.list_keys(self.SERVICE_NAME)
            return keys_info.get(self.SERVICE_NAME, [])
        except Exception as e:
            self.logger.error(f"Error listing API keys: {e}")
            return {}
    
    def import_from_env(self, env_var: str = "GOOGLE_API_KEY", key_id: str = "default") -> bool:
        """
        Import an API key from an environment variable.
        
        Args:
            env_var: Name of the environment variable containing the API key
            key_id: Identifier to use for storing the key
            
        Returns:
            bool: True if successful, False otherwise
        """
        api_key = os.getenv(env_var)
        if not api_key:
            self.logger.error(f"Environment variable {env_var} not found or empty")
            return False
        
        return self.store_api_key(key_id, api_key)
    
    def import_from_file(self, file_path: str, key_id: str = "default") -> bool:
        """
        Import an API key from a file.
        
        Args:
            file_path: Path to the file containing the API key
            key_id: Identifier to use for storing the key
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
            
            # Check if the file contains JSON
            try:
                data = json.loads(content)
                # Extract API key from JSON structure (assuming Google Cloud format)
                if isinstance(data, dict):
                    api_key = data.get('api_key') or data.get('key')
                    if not api_key:
                        self.logger.error(f"Could not find API key in JSON file: {file_path}")
                        return False
                else:
                    api_key = content
            except json.JSONDecodeError:
                # Not JSON, treat as plain text API key
                api_key = content
            
            return self.store_api_key(key_id, api_key)
        except Exception as e:
            self.logger.error(f"Error importing API key from file: {e}")
            return False

# Example usage
def example_usage():
    # Create a key manager
    key_manager = GeminiKeyManager()
    
    # Import API key from environment variable
    if key_manager.import_from_env():
        print("Successfully imported API key from environment variable")
    
    # Store a new API key
    key_manager.store_api_key("test", "test-api-key-123")
    
    # List available keys
    keys = key_manager.list_available_keys()
    print(f"Available keys: {keys}")
    
    # Retrieve an API key
    api_key = key_manager.get_api_key("test")
    print(f"Retrieved API key: {api_key}")
    
    # Delete an API key
    key_manager.delete_api_key("test")

if __name__ == "__main__":
    example_usage()
