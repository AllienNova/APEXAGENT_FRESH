#!/usr/bin/env python3
"""
Validation script for the Enhanced API Key Manager.

This script tests the functionality of the Enhanced API Key Manager,
including encryption, key rotation, access control, and migration.
"""

import os
import sys
import time
import base64
import shutil
import tempfile
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure keyring to use the alt backend before importing the manager
import keyring
from keyrings.alt.file import PlaintextKeyring
keyring.set_keyring(PlaintextKeyring())

# Import the Enhanced API Key Manager
from src.core.enhanced_api_key_manager import EnhancedApiKeyManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def setup_test_environment() -> Dict[str, Any]:
    """Set up a test environment for validation."""
    logger.info("Setting up test environment")
    
    # Create temporary directories
    test_dir = tempfile.mkdtemp()
    config_dir = os.path.join(test_dir, "security")
    credentials_dir = os.path.join(test_dir, "credentials")
    
    # Create a legacy credentials file for migration testing
    legacy_dir = os.path.join(test_dir, "legacy")
    os.makedirs(legacy_dir, exist_ok=True)
    legacy_file = os.path.join(legacy_dir, ".apex_agent_api_keys.enc")
    
    # Return the test environment
    return {
        "test_dir": test_dir,
        "config_dir": config_dir,
        "credentials_dir": credentials_dir,
        "legacy_dir": legacy_dir,
        "legacy_file": legacy_file
    }

def cleanup_test_environment(env: Dict[str, Any]) -> None:
    """Clean up the test environment."""
    logger.info("Cleaning up test environment")
    shutil.rmtree(env["test_dir"])

def test_basic_functionality(env: Dict[str, Any]) -> bool:
    """Test basic functionality of the Enhanced API Key Manager."""
    logger.info("Testing basic functionality")
    
    try:
        # Initialize the manager
        manager = EnhancedApiKeyManager(
            config_dir=env["config_dir"],
            credentials_dir=env["credentials_dir"],
            create_dirs=True,
            migrate_legacy=False
        )
        
        # Test API key storage and retrieval
        test_api_key = "sk-test1234567890"
        manager.set_api_key("openai_test", test_api_key)
        retrieved_key = manager.get_api_key("openai_test")
        assert retrieved_key == test_api_key, f"API key mismatch: {retrieved_key} != {test_api_key}"
        
        # Test OAuth token storage and retrieval
        test_token = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": int(time.time()) + 3600,
            "token_type": "Bearer"
        }
        manager.set_oauth_token("google_test", test_token)
        retrieved_token = manager.get_oauth_token("google_test")
        assert retrieved_token["access_token"] == test_token["access_token"], "Token mismatch"
        
        # Test listing services
        services = manager.list_configured_services()
        assert "openai_test" in services["api_keys"], "API key service not listed"
        assert "google_test" in services["oauth_tokens"], "OAuth token service not listed"
        
        # Test credential deletion
        assert manager.delete_credential("openai_test", "api_key"), "Failed to delete API key"
        assert manager.get_api_key("openai_test") is None, "API key not deleted"
        
        logger.info("Basic functionality tests passed")
        return True
    
    except Exception as e:
        logger.error(f"Basic functionality test failed: {e}")
        return False

def test_key_rotation(env: Dict[str, Any]) -> bool:
    """Test key rotation functionality."""
    logger.info("Testing key rotation")
    
    try:
        # Initialize the manager
        manager = EnhancedApiKeyManager(
            config_dir=env["config_dir"],
            credentials_dir=env["credentials_dir"],
            create_dirs=True,
            migrate_legacy=False
        )
        
        # Store test credentials
        manager.set_api_key("rotation_test", "test_api_key")
        
        # Test master key rotation
        original_master_key = manager.master_key
        manager.rotate_master_key()
        assert original_master_key != manager.master_key, "Master key not rotated"
        
        # Verify credentials are still accessible
        assert manager.get_api_key("rotation_test") == "test_api_key", "Credentials lost after master key rotation"
        
        # Test KEK rotation
        original_kek_count = len(manager.key_encryption_keys)
        manager.rotate_encryption_keys("kek")
        assert len(manager.key_encryption_keys) > original_kek_count, "KEK count not increased after rotation"
        
        # Test DEK rotation
        original_dek_count = len(manager.data_encryption_keys.get("api_keys", {}))
        manager.rotate_encryption_keys("dek")
        assert len(manager.data_encryption_keys.get("api_keys", {})) > original_dek_count, "DEK count not increased after rotation"
        
        # Verify credentials are still accessible
        assert manager.get_api_key("rotation_test") == "test_api_key", "Credentials lost after DEK rotation"
        
        logger.info("Key rotation tests passed")
        return True
    
    except Exception as e:
        logger.error(f"Key rotation test failed: {e}")
        return False

def test_access_control(env: Dict[str, Any]) -> bool:
    """Test access control functionality."""
    logger.info("Testing access control")
    
    try:
        # Initialize the manager
        manager = EnhancedApiKeyManager(
            config_dir=env["config_dir"],
            credentials_dir=env["credentials_dir"],
            create_dirs=True,
            migrate_legacy=False
        )
        
        # Store test credentials
        manager.set_api_key("access_test", "test_api_key")
        
        # Enable access control
        manager.enable_access_control(True)
        
        # Set permissions for plugins
        manager.set_plugin_permissions("allowed_plugin", ["access_test"])
        
        # Test secure retrieval
        assert manager.get_api_key_secure("allowed_plugin", "access_test") == "test_api_key", "Allowed plugin denied access"
        assert manager.get_api_key_secure("denied_plugin", "access_test") is None, "Denied plugin granted access"
        
        # Test permission checking
        assert manager.check_plugin_permission("allowed_plugin", "access_test"), "Permission check failed for allowed plugin"
        assert not manager.check_plugin_permission("denied_plugin", "access_test"), "Permission check failed for denied plugin"
        
        # Test getting permissions
        permissions = manager.get_plugin_permissions("allowed_plugin")
        assert "access_test" in permissions, "Permissions not retrieved correctly"
        
        logger.info("Access control tests passed")
        return True
    
    except Exception as e:
        logger.error(f"Access control test failed: {e}")
        return False

def test_migration(env: Dict[str, Any]) -> bool:
    """Test migration from legacy credentials."""
    logger.info("Testing migration from legacy credentials")
    
    try:
        # Create a mock legacy credentials file
        from cryptography.fernet import Fernet
        import json
        
        # Generate a key for Fernet encryption
        key = Fernet.generate_key()
        fernet = Fernet(key)
        
        # Create legacy credentials
        legacy_credentials = {
            "api_keys": {
                "legacy_service": "legacy_api_key"
            },
            "oauth_tokens": {
                "legacy_oauth": {
                    "access_token": "legacy_access_token"
                }
            }
        }
        
        # Encrypt and save legacy credentials
        encrypted_data = fernet.encrypt(json.dumps(legacy_credentials).encode())
        with open(env["legacy_file"], "wb") as f:
            f.write(encrypted_data)
        
        # Set the environment variable for the legacy master key
        os.environ["APEX_AGENT_MASTER_KEY"] = base64.b64encode(key).decode()
        
        # Patch the LEGACY_API_KEYS_FILE constant in the EnhancedApiKeyManager
        import src.core.enhanced_api_key_manager as eakm
        original_legacy_path = eakm.LEGACY_API_KEYS_FILE
        eakm.LEGACY_API_KEYS_FILE = env["legacy_file"]
        
        # Patch the _decrypt_legacy_credentials method to use our test key
        original_decrypt_legacy = eakm.EnhancedApiKeyManager._decrypt_legacy_credentials
        
        def patched_decrypt_legacy(self, encrypted_data):
            try:
                # Use the key we created for the test
                fernet = Fernet(key)
                decrypted_data = fernet.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode())
            except Exception as e:
                raise eakm.EncryptionError(f"Failed to decrypt legacy credentials: {e}")
        
        eakm.EnhancedApiKeyManager._decrypt_legacy_credentials = patched_decrypt_legacy
        
        try:
            # Initialize the manager with migration
            manager = EnhancedApiKeyManager(
                config_dir=env["config_dir"],
                credentials_dir=env["credentials_dir"],
                create_dirs=True,
                migrate_legacy=True
            )
            
            # Check if migration was successful
            assert manager.get_api_key("legacy_service") == "legacy_api_key", "Legacy API key not migrated"
            assert manager.get_oauth_token("legacy_oauth")["access_token"] == "legacy_access_token", "Legacy OAuth token not migrated"
            
            logger.info("Migration tests passed")
            return True
        
        finally:
            # Restore the original methods and constants
            eakm.LEGACY_API_KEYS_FILE = original_legacy_path
            eakm.EnhancedApiKeyManager._decrypt_legacy_credentials = original_decrypt_legacy
    
    except Exception as e:
        logger.error(f"Migration test failed: {e}")
        return False

def test_fallback_to_env_var(env: Dict[str, Any]) -> bool:
    """Test fallback to environment variable when keyring is unavailable."""
    logger.info("Testing fallback to environment variable")
    
    try:
        # Create a new test directory for this specific test
        fallback_dir = os.path.join(env["test_dir"], "fallback")
        fallback_config_dir = os.path.join(fallback_dir, "security")
        fallback_credentials_dir = os.path.join(fallback_dir, "credentials")
        os.makedirs(fallback_config_dir, exist_ok=True)
        os.makedirs(fallback_credentials_dir, exist_ok=True)
        
        # Generate a master key
        import nacl.secret
        import nacl.utils
        master_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        master_key_b64 = base64.b64encode(master_key).decode()
        
        # Set the environment variable
        os.environ["APEX_AGENT_MASTER_KEY"] = master_key_b64
        
        # Patch keyring.get_password to return None (simulating no keyring)
        original_get_password = keyring.get_password
        
        def mock_get_password(service_name, username):
            # Always return None to simulate no keyring
            return None
        
        keyring.get_password = mock_get_password
        
        try:
            # Initialize the manager with the environment variable as fallback
            manager = EnhancedApiKeyManager(
                config_dir=fallback_config_dir,
                credentials_dir=fallback_credentials_dir,
                create_dirs=True,
                migrate_legacy=False
            )
            
            # Test basic functionality
            manager.set_api_key("fallback_test", "test_api_key")
            retrieved_key = manager.get_api_key("fallback_test")
            
            assert retrieved_key == "test_api_key", f"API key mismatch: {retrieved_key} != test_api_key"
            
            logger.info("Fallback to environment variable tests passed")
            return True
        
        finally:
            # Restore the original keyring.get_password
            keyring.get_password = original_get_password
    
    except Exception as e:
        logger.error(f"Fallback to environment variable test failed: {e}")
        return False

def run_validation() -> bool:
    """Run all validation tests."""
    logger.info("Starting Enhanced API Key Manager validation")
    
    # Set up test environment
    env = setup_test_environment()
    
    try:
        # Run tests
        basic_result = test_basic_functionality(env)
        rotation_result = test_key_rotation(env)
        access_result = test_access_control(env)
        migration_result = test_migration(env)
        fallback_result = test_fallback_to_env_var(env)
        
        # Check overall result
        overall_result = all([basic_result, rotation_result, access_result, migration_result, fallback_result])
        
        if overall_result:
            logger.info("All validation tests passed")
        else:
            logger.error("Some validation tests failed")
            
            # Log specific test results
            logger.info(f"Basic functionality: {'PASS' if basic_result else 'FAIL'}")
            logger.info(f"Key rotation: {'PASS' if rotation_result else 'FAIL'}")
            logger.info(f"Access control: {'PASS' if access_result else 'FAIL'}")
            logger.info(f"Migration: {'PASS' if migration_result else 'FAIL'}")
            logger.info(f"Fallback to environment variable: {'PASS' if fallback_result else 'FAIL'}")
        
        return overall_result
    
    finally:
        # Clean up test environment
        cleanup_test_environment(env)

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
