# Enhanced API Key Manager Documentation

## Overview

The Enhanced API Key Manager provides a secure way to store and retrieve API keys and OAuth tokens for various services used by ApexAgent plugins. This document covers the security features, usage instructions, and migration steps for transitioning from the legacy API Key Manager.

## Security Features

The Enhanced API Key Manager implements several security best practices:

### 1. Hierarchical Key Management

The manager uses a three-tier key hierarchy:

- **Master Key**: The root key stored in the system's secure keyring (Windows Credential Manager, macOS Keychain, or Linux Secret Service)
- **Key Encryption Keys (KEKs)**: Used to encrypt Data Encryption Keys
- **Data Encryption Keys (DEKs)**: Used to encrypt actual credentials, with separate DEKs for different credential types

This approach limits the exposure of the master key and allows for efficient key rotation.

### 2. Advanced Encryption

- Uses PyNaCl (libsodium) for authenticated encryption with high security guarantees
- Implements authenticated encryption to prevent tampering with encrypted data
- Supports versioning of encryption keys to maintain access to previously encrypted data

### 3. Secure Storage

- Stores the master key in the system's secure keyring rather than environment variables
- Applies restrictive file permissions (600) to all credential files
- Organizes credentials in a structured directory layout with separate files for different credential types

### 4. Access Control

- Plugin-level permissions for credential access
- Comprehensive audit logging of all credential access attempts
- Secure retrieval methods that enforce access policies

### 5. Key Rotation

- Support for rotating all levels of keys (master, KEK, DEK)
- Configurable rotation intervals with status checking
- Automatic re-encryption of credentials during key rotation

## Usage Instructions

### Basic Usage

```python
from src.core.enhanced_api_key_manager import EnhancedApiKeyManager

# Initialize the manager
manager = EnhancedApiKeyManager()

# Store an API key
manager.set_api_key("openai", "sk-your-api-key")

# Retrieve an API key
api_key = manager.get_api_key("openai")

# Store OAuth token data
token_data = {
    "access_token": "your-access-token",
    "refresh_token": "your-refresh-token",
    "expires_at": 1621234567,
    "token_type": "Bearer"
}
manager.set_oauth_token("google", token_data)

# Retrieve OAuth token data
token = manager.get_oauth_token("google")

# Delete a credential
manager.delete_credential("openai", "api_key")

# List all configured services
services = manager.list_configured_services()
```

### Access Control

```python
# Enable access control
manager.enable_access_control(True)

# Set permissions for a plugin
manager.set_plugin_permissions("my_plugin", ["openai", "google"])

# Securely retrieve credentials with access control
api_key = manager.get_api_key_secure("my_plugin", "openai")
token = manager.get_oauth_token_secure("my_plugin", "google")
```

### Key Rotation

```python
# Check if any keys are due for rotation
status = manager.check_key_rotation_status()

# Rotate the master key
manager.rotate_master_key()

# Rotate encryption keys
manager.rotate_encryption_keys("all")  # Options: "kek", "dek", "all"

# Set custom rotation intervals (in days)
manager.set_key_rotation_interval("master_key", 365)  # Annual rotation
manager.set_key_rotation_interval("key_encryption_keys", 180)  # Semi-annual
manager.set_key_rotation_interval("data_encryption_keys", 90)  # Quarterly
```

## Migration from Legacy API Key Manager

The Enhanced API Key Manager provides automatic migration from the legacy API Key Manager. When initialized with `migrate_legacy=True` (the default), it will:

1. Look for the legacy credentials file at `~/.apex_agent_api_keys.enc`
2. Decrypt the legacy credentials using the master key
3. Import all API keys and OAuth tokens into the new storage format
4. Rename the legacy file to `~/.apex_agent_api_keys.enc.bak` as a backup

### Manual Migration

If automatic migration fails or you need more control over the process:

```python
# Initialize without automatic migration
manager = EnhancedApiKeyManager(migrate_legacy=False)

# Manually trigger migration
manager._migrate_legacy_credentials()
```

### Backward Compatibility

The Enhanced API Key Manager maintains backward compatibility with legacy encrypted data. If it encounters data encrypted with the legacy format (Fernet), it will automatically attempt to decrypt it using the legacy method.

## Configuration

The manager can be configured with custom directories and settings:

```python
manager = EnhancedApiKeyManager(
    config_dir="/path/to/config",
    credentials_dir="/path/to/credentials",
    create_dirs=True,
    migrate_legacy=True
)
```

Default locations:
- Config directory: `~/.apex_agent/security/`
- Credentials directory: `~/.apex_agent/credentials/`

## Security Best Practices

1. **Regular Key Rotation**: Rotate keys according to your security policy
2. **Access Control**: Enable access control and set appropriate permissions for plugins
3. **Audit Logging**: Monitor the logs for unauthorized access attempts
4. **Secure Backup**: Regularly back up the encrypted credentials
5. **Environment Isolation**: Use separate credential stores for development and production

## Troubleshooting

### Common Issues

1. **Keyring Access Issues**: If the system keyring is not available, the manager will fall back to environment variables. Set the `APEX_AGENT_MASTER_KEY` environment variable with a base64-encoded 32-byte key.

2. **Permission Errors**: Ensure the user running ApexAgent has read/write permissions to the config and credentials directories.

3. **Migration Failures**: If automatic migration fails, check the logs for specific errors and try manual migration.

### Error Handling

The manager defines several exception types for specific error scenarios:

- `ApiKeyManagerError`: Base exception for all errors
- `MasterKeyError`: Issues with the master key
- `EncryptionError`: Encryption or decryption failures
- `StorageError`: File storage or retrieval issues

## Advanced Topics

### Custom Key Derivation

For advanced users who need to derive keys from passwords:

```python
import nacl.pwhash
import nacl.secret
import base64

# Derive a key from a password
salt = nacl.utils.random(nacl.pwhash.SALTBYTES)
key = nacl.pwhash.argon2id.kdf(
    nacl.secret.SecretBox.KEY_SIZE,
    b"your-password",
    salt,
    opslimit=nacl.pwhash.OPSLIMIT_SENSITIVE,
    memlimit=nacl.pwhash.MEMLIMIT_SENSITIVE
)

# Convert to base64 for storage
key_b64 = base64.b64encode(key).decode()

# Set as master key in environment variable
import os
os.environ["APEX_AGENT_MASTER_KEY"] = key_b64
```

### Custom Audit Logging

To integrate with external logging systems:

```python
import logging

# Configure custom logger
logger = logging.getLogger("api_key_manager")
handler = logging.FileHandler("/path/to/audit.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# The manager will use the configured logger
```
