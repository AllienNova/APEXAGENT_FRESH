import unittest
import os
import tempfile
import shutil
import time
import json
import base64
import nacl.secret
import nacl.utils
import keyring
from unittest.mock import patch, MagicMock

# Import the module to test
from src.core.enhanced_api_key_manager import (
    EnhancedApiKeyManager,
    MasterKeyError,
    EncryptionError,
    StorageError
)

class TestEnhancedApiKeyManager(unittest.TestCase):
    """
    Unit tests for the EnhancedApiKeyManager class.
    """
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.test_dir, "security")
        self.credentials_dir = os.path.join(self.test_dir, "credentials")
        
        # Create a mock master key for testing
        self.mock_master_key = base64.b64encode(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)).decode()
        
        # Mock keyring for testing - ensure it returns the same key for all tests
        self.keyring_patcher = patch('keyring.get_password')
        self.mock_get_password = self.keyring_patcher.start()
        self.mock_get_password.return_value = self.mock_master_key
        
        self.keyring_set_patcher = patch('keyring.set_password')
        self.mock_set_password = self.keyring_set_patcher.start()
        
        # Create manager instance for testing
        self.manager = EnhancedApiKeyManager(
            config_dir=self.config_dir,
            credentials_dir=self.credentials_dir,
            create_dirs=True,
            migrate_legacy=False
        )
    
    def tearDown(self):
        """Clean up after each test."""
        # Stop patches
        self.keyring_patcher.stop()
        self.keyring_set_patcher.stop()
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        # Check that directories were created
        self.assertTrue(os.path.exists(self.config_dir))
        self.assertTrue(os.path.exists(self.credentials_dir))
        
        # Check that keystore and config files were created
        self.assertTrue(os.path.exists(os.path.join(self.config_dir, "keystore.enc")))
        self.assertTrue(os.path.exists(os.path.join(self.config_dir, "config.json")))
        
        # Check that the manager has the expected attributes
        self.assertIsNotNone(self.manager.master_key)
        self.assertIsInstance(self.manager.key_encryption_keys, dict)
        self.assertIsInstance(self.manager.data_encryption_keys, dict)
        self.assertIsInstance(self.manager.api_keys, dict)
        self.assertIsInstance(self.manager.oauth_tokens, dict)
    
    def test_api_key_storage(self):
        """Test storing and retrieving API keys."""
        # Store an API key
        self.manager.set_api_key("test_service", "test_api_key")
        
        # Check that the API key was stored
        self.assertEqual(self.manager.get_api_key("test_service"), "test_api_key")
        
        # Check that the API key file was created
        self.assertTrue(os.path.exists(os.path.join(self.credentials_dir, "api_keys.enc")))
        
        # Check that a non-existent key returns None
        self.assertIsNone(self.manager.get_api_key("non_existent_service"))
    
    def test_oauth_token_storage(self):
        """Test storing and retrieving OAuth tokens."""
        # Create a test token
        token_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": int(time.time()) + 3600,
            "token_type": "Bearer"
        }
        
        # Store the token
        self.manager.set_oauth_token("test_service", token_data)
        
        # Check that the token was stored
        retrieved_token = self.manager.get_oauth_token("test_service")
        self.assertEqual(retrieved_token["access_token"], "test_access_token")
        self.assertEqual(retrieved_token["refresh_token"], "test_refresh_token")
        
        # Check that the token file was created
        self.assertTrue(os.path.exists(os.path.join(self.credentials_dir, "oauth_tokens.enc")))
        
        # Check that a non-existent token returns None
        self.assertIsNone(self.manager.get_oauth_token("non_existent_service"))
    
    def test_credential_deletion(self):
        """Test deleting credentials."""
        # Store test credentials
        self.manager.set_api_key("test_service", "test_api_key")
        token_data = {"access_token": "test_access_token"}
        self.manager.set_oauth_token("test_service", token_data)
        
        # Delete API key
        result = self.manager.delete_credential("test_service", "api_key")
        self.assertTrue(result)
        self.assertIsNone(self.manager.get_api_key("test_service"))
        self.assertIsNotNone(self.manager.get_oauth_token("test_service"))
        
        # Delete OAuth token
        result = self.manager.delete_credential("test_service", "oauth_token")
        self.assertTrue(result)
        self.assertIsNone(self.manager.get_oauth_token("test_service"))
        
        # Try to delete non-existent credential
        result = self.manager.delete_credential("non_existent_service")
        self.assertFalse(result)
    
    def test_list_configured_services(self):
        """Test listing configured services."""
        # Initially, no services should be configured
        services = self.manager.list_configured_services()
        self.assertEqual(len(services["api_keys"]), 0)
        self.assertEqual(len(services["oauth_tokens"]), 0)
        
        # Add some credentials
        self.manager.set_api_key("test_api_service", "test_api_key")
        self.manager.set_oauth_token("test_oauth_service", {"access_token": "test"})
        
        # Check that the services are listed
        services = self.manager.list_configured_services()
        self.assertIn("test_api_service", services["api_keys"])
        self.assertIn("test_oauth_service", services["oauth_tokens"])
    
    def test_master_key_rotation(self):
        """Test rotating the master key."""
        # Store a test API key
        self.manager.set_api_key("test_service", "test_api_key")
        
        # Get the original master key
        original_master_key = self.manager.master_key
        
        # Rotate the master key
        self.manager.rotate_master_key()
        
        # Check that the master key changed
        self.assertNotEqual(original_master_key, self.manager.master_key)
        
        # Check that we can still access the API key
        self.assertEqual(self.manager.get_api_key("test_service"), "test_api_key")
    
    def test_key_rotation(self):
        """Test key rotation."""
        # Store test credentials
        self.manager.set_api_key("test_service", "test_api_key")
        
        # Get the initial number of DEKs for api_keys
        initial_dek_count = len(self.manager.data_encryption_keys.get("api_keys", {}))
        
        # Rotate DEKs
        self.manager.rotate_encryption_keys("dek")
        
        # Get the new number of DEKs for api_keys
        new_dek_count = len(self.manager.data_encryption_keys.get("api_keys", {}))
        
        # Check that the number of DEKs increased
        self.assertGreater(
            new_dek_count,
            initial_dek_count,
            f"DEK count should increase after rotation. Before: {initial_dek_count}, After: {new_dek_count}"
        )
        
        # Check that we can still access the API key
        self.assertEqual(self.manager.get_api_key("test_service"), "test_api_key")
    
    def test_access_control(self):
        """Test access control for plugins."""
        # Store a test API key
        self.manager.set_api_key("test_service", "test_api_key")
        
        # Initially, access control is disabled
        self.assertTrue(self.manager.check_plugin_permission("test_plugin", "test_service"))
        
        # Enable access control
        self.manager.enable_access_control(True)
        
        # No permissions set yet, so access should be denied
        self.assertFalse(self.manager.check_plugin_permission("test_plugin", "test_service"))
        
        # Set permissions
        self.manager.set_plugin_permissions("test_plugin", ["test_service"])
        
        # Now access should be allowed
        self.assertTrue(self.manager.check_plugin_permission("test_plugin", "test_service"))
        
        # But access to other services should be denied
        self.assertFalse(self.manager.check_plugin_permission("test_plugin", "other_service"))
    
    def test_secure_retrieval(self):
        """Test secure retrieval of credentials with access control."""
        # Store test credentials
        self.manager.set_api_key("test_service", "test_api_key")
        token_data = {"access_token": "test_access_token"}
        self.manager.set_oauth_token("test_service", token_data)
        
        # Enable access control
        self.manager.enable_access_control(True)
        
        # Set permissions for one plugin but not another
        self.manager.set_plugin_permissions("allowed_plugin", ["test_service"])
        
        # Test API key retrieval
        self.assertEqual(
            self.manager.get_api_key_secure("allowed_plugin", "test_service"),
            "test_api_key"
        )
        self.assertIsNone(
            self.manager.get_api_key_secure("denied_plugin", "test_service")
        )
        
        # Test OAuth token retrieval
        self.assertEqual(
            self.manager.get_oauth_token_secure("allowed_plugin", "test_service")["access_token"],
            "test_access_token"
        )
        self.assertIsNone(
            self.manager.get_oauth_token_secure("denied_plugin", "test_service")
        )
    
    def test_key_rotation_intervals(self):
        """Test setting and checking key rotation intervals."""
        # Set custom rotation intervals
        self.manager.set_key_rotation_interval("master_key", 30)  # 30 days
        self.manager.set_key_rotation_interval("key_encryption_keys", 60)  # 60 days
        self.manager.set_key_rotation_interval("data_encryption_keys", 90)  # 90 days
        
        # Check that the intervals were set correctly
        status = self.manager.check_key_rotation_status()
        self.assertEqual(status["master_key"]["rotation_interval_days"], 30)
        self.assertEqual(status["key_encryption_keys"]["rotation_interval_days"], 60)
        self.assertEqual(status["data_encryption_keys"]["rotation_interval_days"], 90)
    
    def test_error_handling(self):
        """Test error handling."""
        # Test with invalid key type
        with self.assertRaises(ValueError):
            self.manager.set_key_rotation_interval("invalid_key_type", 30)
        
        # Test with storage error
        with patch('builtins.open', side_effect=IOError("Test error")):
            with self.assertRaises(StorageError):
                self.manager.set_api_key("test_service", "test_api_key")
    
    def test_file_permissions(self):
        """Test that files have secure permissions."""
        # Store a test API key to ensure files are created
        self.manager.set_api_key("test_service", "test_api_key")
        
        # Check keystore file permissions
        keystore_path = os.path.join(self.config_dir, "keystore.enc")
        self.assertTrue(os.path.exists(keystore_path))
        
        # Check API keys file permissions
        api_keys_path = os.path.join(self.credentials_dir, "api_keys.enc")
        self.assertTrue(os.path.exists(api_keys_path))
        
        # Note: We can't reliably test the actual permission bits in a cross-platform way,
        # but we can verify that the files exist and were created by our code
    
    def test_migration_from_legacy(self):
        """Test migration from legacy credentials."""
        # This test is more complex and would require setting up mock legacy files
        # For now, we'll just test that the method exists and doesn't crash
        try:
            self.manager._migrate_legacy_credentials()
            # If we get here, the method didn't crash
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"_migrate_legacy_credentials raised {type(e).__name__} unexpectedly: {e}")
    
    def test_config_management(self):
        """Test configuration management."""
        # Check that the config file exists
        config_path = os.path.join(self.config_dir, "config.json")
        self.assertTrue(os.path.exists(config_path))
        
        # Modify a config value
        self.manager.config["test_value"] = "test"
        self.manager._save_config()
        
        # Create a new manager instance to load the config
        # Use the same mock master key to ensure decryption works
        with patch('keyring.get_password', return_value=self.mock_master_key):
            new_manager = EnhancedApiKeyManager(
                config_dir=self.config_dir,
                credentials_dir=self.credentials_dir,
                create_dirs=False,
                migrate_legacy=False
            )
            
            # Check that the config value was saved and loaded
            self.assertEqual(new_manager.config.get("test_value"), "test")


if __name__ == '__main__':
    unittest.main()
