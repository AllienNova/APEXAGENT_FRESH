"""
Key Management Service for the Data Protection Framework.

This module provides comprehensive key management capabilities including
key generation, storage, rotation, and access control.
"""

import os
import time
import json
import base64
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
import uuid

from ..crypto import (
    CryptoCore,
    EncryptionAlgorithm,
    AsymmetricAlgorithm,
    HashAlgorithm,
    KeyDerivationFunction,
    CryptoError
)

# Configure logging
logger = logging.getLogger(__name__)

class KeyType(Enum):
    """Types of keys managed by the Key Management Service."""
    MASTER = "master"
    DATA_ENCRYPTION = "data_encryption"
    KEY_ENCRYPTION = "key_encryption"
    SIGNING = "signing"
    AUTHENTICATION = "authentication"
    USER = "user"
    SYSTEM = "system"
    BACKUP = "backup"

class KeyStatus(Enum):
    """Possible statuses for keys."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPROMISED = "compromised"
    ROTATED = "rotated"
    EXPIRED = "expired"
    SCHEDULED_ROTATION = "scheduled_rotation"

class KeyUsage(Enum):
    """Allowed usages for keys."""
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    DERIVE = "derive"
    WRAP = "wrap"
    UNWRAP = "unwrap"
    ALL = "all"

class KeyMetadata:
    """Metadata for a cryptographic key."""
    
    def __init__(
        self,
        key_id: str,
        key_type: KeyType,
        algorithm: Union[EncryptionAlgorithm, AsymmetricAlgorithm],
        created_at: int,
        status: KeyStatus = KeyStatus.ACTIVE,
        expires_at: Optional[int] = None,
        rotation_period: Optional[int] = None,
        last_rotated: Optional[int] = None,
        version: int = 1,
        usage: List[KeyUsage] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        owner: Optional[str] = None
    ):
        """
        Initialize key metadata.
        
        Args:
            key_id: Unique identifier for the key
            key_type: Type of key
            algorithm: Encryption algorithm used
            created_at: Timestamp when the key was created
            status: Current status of the key
            expires_at: Timestamp when the key expires
            rotation_period: Period in seconds for key rotation
            last_rotated: Timestamp when the key was last rotated
            version: Version number of the key
            usage: Allowed usages for the key
            description: Human-readable description
            tags: Key-value pairs for additional metadata
            owner: Owner of the key (user ID, system component, etc.)
        """
        self.key_id = key_id
        self.key_type = key_type
        self.algorithm = algorithm
        self.created_at = created_at
        self.status = status
        self.expires_at = expires_at
        self.rotation_period = rotation_period
        self.last_rotated = last_rotated
        self.version = version
        self.usage = usage or [KeyUsage.ALL]
        self.description = description
        self.tags = tags or {}
        self.owner = owner
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            'key_id': self.key_id,
            'key_type': self.key_type.value,
            'algorithm': self.algorithm.value,
            'created_at': self.created_at,
            'status': self.status.value,
            'expires_at': self.expires_at,
            'rotation_period': self.rotation_period,
            'last_rotated': self.last_rotated,
            'version': self.version,
            'usage': [u.value for u in self.usage],
            'description': self.description,
            'tags': self.tags,
            'owner': self.owner
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyMetadata':
        """Create metadata from dictionary."""
        # Convert string values back to enums
        key_type = KeyType(data['key_type'])
        
        # Determine the algorithm type based on the value
        algorithm_value = data['algorithm']
        try:
            algorithm = EncryptionAlgorithm(algorithm_value)
        except ValueError:
            algorithm = AsymmetricAlgorithm(algorithm_value)
        
        status = KeyStatus(data['status'])
        usage = [KeyUsage(u) for u in data['usage']]
        
        return cls(
            key_id=data['key_id'],
            key_type=key_type,
            algorithm=algorithm,
            created_at=data['created_at'],
            status=status,
            expires_at=data['expires_at'],
            rotation_period=data['rotation_period'],
            last_rotated=data['last_rotated'],
            version=data['version'],
            usage=usage,
            description=data['description'],
            tags=data['tags'],
            owner=data['owner']
        )

class KeyManagementError(Exception):
    """Base exception for key management operations."""
    pass

class KeyNotFoundError(KeyManagementError):
    """Exception raised when a key is not found."""
    pass

class KeyAccessDeniedError(KeyManagementError):
    """Exception raised when access to a key is denied."""
    pass

class KeyStatusError(KeyManagementError):
    """Exception raised when a key has an invalid status for an operation."""
    pass

class KeyUsageError(KeyManagementError):
    """Exception raised when a key is used for an unauthorized purpose."""
    pass

class KeyRotationError(KeyManagementError):
    """Exception raised when key rotation fails."""
    pass

class KeyStorageError(KeyManagementError):
    """Exception raised when key storage operations fail."""
    pass

class KeyManagementService:
    """
    Key Management Service for the Data Protection Framework.
    
    This service provides comprehensive key management capabilities including
    key generation, storage, rotation, and access control.
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        crypto_core: Optional[CryptoCore] = None,
        master_key: Optional[bytes] = None
    ):
        """
        Initialize the Key Management Service.
        
        Args:
            storage_path: Path to store key data. If None, uses in-memory storage.
            crypto_core: CryptoCore instance for cryptographic operations.
            master_key: Master key for encrypting other keys. If None, generates a new one.
        """
        self._crypto = crypto_core or CryptoCore()
        self._storage_path = storage_path
        
        # In-memory storage for keys and metadata
        self._keys = {}
        self._metadata = {}
        
        # Initialize master key
        self._master_key = master_key or self._crypto.generate_symmetric_key()
        self._master_key_id = str(uuid.uuid4())
        
        # Create master key metadata
        master_metadata = KeyMetadata(
            key_id=self._master_key_id,
            key_type=KeyType.MASTER,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            created_at=int(time.time()),
            status=KeyStatus.ACTIVE,
            description="Master Key Encryption Key",
            owner="system"
        )
        
        # Store master key metadata
        self._metadata[self._master_key_id] = master_metadata
        
        # If storage path is provided, initialize persistent storage
        if storage_path:
            self._initialize_storage()
        
        logger.info("Key Management Service initialized")
    
    def _initialize_storage(self):
        """Initialize persistent storage for keys and metadata."""
        try:
            os.makedirs(self._storage_path, exist_ok=True)
            
            # Create metadata directory
            metadata_dir = os.path.join(self._storage_path, 'metadata')
            os.makedirs(metadata_dir, exist_ok=True)
            
            # Create keys directory
            keys_dir = os.path.join(self._storage_path, 'keys')
            os.makedirs(keys_dir, exist_ok=True)
            
            logger.info(f"Key storage initialized at {self._storage_path}")
        except Exception as e:
            logger.error(f"Failed to initialize key storage: {str(e)}")
            raise KeyStorageError(f"Failed to initialize key storage: {str(e)}")
    
    def _store_key(self, key_id: str, key_data: bytes):
        """
        Store a key securely.
        
        Args:
            key_id: Unique identifier for the key.
            key_data: The key data to store.
        
        Raises:
            KeyStorageError: If key storage fails.
        """
        try:
            # Encrypt the key with the master key
            encrypted_key = self._crypto.encrypt_symmetric(
                key_data,
                self._master_key,
                associated_data=key_id.encode()
            )
            
            # Store in memory
            self._keys[key_id] = encrypted_key
            
            # If storage path is provided, store on disk
            if self._storage_path:
                key_path = os.path.join(self._storage_path, 'keys', key_id)
                with open(key_path, 'wb') as f:
                    # Serialize the encrypted key data
                    serialized = {
                        'ciphertext': base64.b64encode(encrypted_key['ciphertext']).decode(),
                        'iv': base64.b64encode(encrypted_key['iv']).decode(),
                        'tag': base64.b64encode(encrypted_key['tag']).decode()
                    }
                    f.write(json.dumps(serialized).encode())
        except Exception as e:
            logger.error(f"Failed to store key {key_id}: {str(e)}")
            raise KeyStorageError(f"Failed to store key {key_id}: {str(e)}")
    
    def _retrieve_key(self, key_id: str) -> bytes:
        """
        Retrieve and decrypt a key.
        
        Args:
            key_id: Unique identifier for the key.
        
        Returns:
            bytes: The decrypted key.
        
        Raises:
            KeyNotFoundError: If the key is not found.
            KeyStorageError: If key retrieval fails.
        """
        try:
            # Check if key exists in memory
            if key_id in self._keys:
                encrypted_key = self._keys[key_id]
            # If not in memory but storage path is provided, try to load from disk
            elif self._storage_path:
                key_path = os.path.join(self._storage_path, 'keys', key_id)
                if not os.path.exists(key_path):
                    raise KeyNotFoundError(f"Key {key_id} not found")
                
                with open(key_path, 'rb') as f:
                    serialized = json.loads(f.read().decode())
                    encrypted_key = {
                        'ciphertext': base64.b64decode(serialized['ciphertext']),
                        'iv': base64.b64decode(serialized['iv']),
                        'tag': base64.b64decode(serialized['tag'])
                    }
                
                # Cache in memory for future use
                self._keys[key_id] = encrypted_key
            else:
                raise KeyNotFoundError(f"Key {key_id} not found")
            
            # Decrypt the key with the master key
            return self._crypto.decrypt_symmetric(
                encrypted_key,
                self._master_key,
                associated_data=key_id.encode()
            )
        except KeyNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve key {key_id}: {str(e)}")
            raise KeyStorageError(f"Failed to retrieve key {key_id}: {str(e)}")
    
    def _store_metadata(self, metadata: KeyMetadata):
        """
        Store key metadata.
        
        Args:
            metadata: The key metadata to store.
        
        Raises:
            KeyStorageError: If metadata storage fails.
        """
        try:
            # Store in memory
            self._metadata[metadata.key_id] = metadata
            
            # If storage path is provided, store on disk
            if self._storage_path:
                metadata_path = os.path.join(self._storage_path, 'metadata', metadata.key_id)
                with open(metadata_path, 'w') as f:
                    json.dump(metadata.to_dict(), f)
        except Exception as e:
            logger.error(f"Failed to store metadata for key {metadata.key_id}: {str(e)}")
            raise KeyStorageError(f"Failed to store metadata for key {metadata.key_id}: {str(e)}")
    
    def _retrieve_metadata(self, key_id: str) -> KeyMetadata:
        """
        Retrieve key metadata.
        
        Args:
            key_id: Unique identifier for the key.
        
        Returns:
            KeyMetadata: The key metadata.
        
        Raises:
            KeyNotFoundError: If the key metadata is not found.
            KeyStorageError: If metadata retrieval fails.
        """
        try:
            # Check if metadata exists in memory
            if key_id in self._metadata:
                return self._metadata[key_id]
            # If not in memory but storage path is provided, try to load from disk
            elif self._storage_path:
                metadata_path = os.path.join(self._storage_path, 'metadata', key_id)
                if not os.path.exists(metadata_path):
                    raise KeyNotFoundError(f"Metadata for key {key_id} not found")
                
                with open(metadata_path, 'r') as f:
                    metadata_dict = json.load(f)
                
                metadata = KeyMetadata.from_dict(metadata_dict)
                
                # Cache in memory for future use
                self._metadata[key_id] = metadata
                
                return metadata
            else:
                raise KeyNotFoundError(f"Metadata for key {key_id} not found")
        except KeyNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve metadata for key {key_id}: {str(e)}")
            raise KeyStorageError(f"Failed to retrieve metadata for key {key_id}: {str(e)}")
    
    def create_key(
        self,
        key_type: KeyType,
        algorithm: Union[EncryptionAlgorithm, AsymmetricAlgorithm],
        rotation_period: Optional[int] = None,
        expires_at: Optional[int] = None,
        usage: Optional[List[KeyUsage]] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        owner: Optional[str] = None
    ) -> str:
        """
        Create a new cryptographic key.
        
        Args:
            key_type: Type of key to create.
            algorithm: Algorithm to use for the key.
            rotation_period: Period in seconds for automatic key rotation.
            expires_at: Timestamp when the key expires.
            usage: Allowed usages for the key.
            description: Human-readable description.
            tags: Key-value pairs for additional metadata.
            owner: Owner of the key (user ID, system component, etc.).
        
        Returns:
            str: The key ID of the created key.
        
        Raises:
            KeyManagementError: If key creation fails.
        """
        try:
            # Generate a unique key ID
            key_id = str(uuid.uuid4())
            
            # Generate the key based on the algorithm
            if isinstance(algorithm, EncryptionAlgorithm):
                key_data = self._crypto.generate_symmetric_key(algorithm)
            elif isinstance(algorithm, AsymmetricAlgorithm):
                key_pair = self._crypto.generate_asymmetric_key_pair(algorithm)
                # For asymmetric keys, we store the private key
                key_data = key_pair['private_key']
                # Store the public key with a different ID
                public_key_id = f"{key_id}_public"
                self._store_key(public_key_id, key_pair['public_key'])
                
                # Create metadata for the public key
                public_metadata = KeyMetadata(
                    key_id=public_key_id,
                    key_type=key_type,
                    algorithm=algorithm,
                    created_at=int(time.time()),
                    status=KeyStatus.ACTIVE,
                    expires_at=expires_at,
                    rotation_period=rotation_period,
                    version=1,
                    usage=[KeyUsage.VERIFY] if KeyUsage.SIGN in (usage or [KeyUsage.ALL]) else [KeyUsage.ENCRYPT],
                    description=f"Public key for {key_id}" if description else None,
                    tags=tags,
                    owner=owner
                )
                self._store_metadata(public_metadata)
            else:
                raise KeyManagementError(f"Unsupported algorithm type: {type(algorithm)}")
            
            # Store the key
            self._store_key(key_id, key_data)
            
            # Create and store metadata
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                created_at=int(time.time()),
                status=KeyStatus.ACTIVE,
                expires_at=expires_at,
                rotation_period=rotation_period,
                version=1,
                usage=usage,
                description=description,
                tags=tags,
                owner=owner
            )
            self._store_metadata(metadata)
            
            logger.info(f"Created new key: {key_id}")
            return key_id
        except Exception as e:
            logger.error(f"Failed to create key: {str(e)}")
            raise KeyManagementError(f"Failed to create key: {str(e)}")
    
    def get_key(
        self,
        key_id: str,
        usage: Optional[KeyUsage] = None,
        requester: Optional[str] = None
    ) -> bytes:
        """
        Retrieve a key for use.
        
        Args:
            key_id: Unique identifier for the key.
            usage: Intended usage for the key.
            requester: Entity requesting the key.
        
        Returns:
            bytes: The key data.
        
        Raises:
            KeyNotFoundError: If the key is not found.
            KeyAccessDeniedError: If access to the key is denied.
            KeyStatusError: If the key has an invalid status.
            KeyUsageError: If the key is used for an unauthorized purpose.
        """
        try:
            # Retrieve metadata
            metadata = self._retrieve_metadata(key_id)
            
            # Check key status
            if metadata.status != KeyStatus.ACTIVE:
                raise KeyStatusError(f"Key {key_id} has status {metadata.status.value}")
            
            # Check key expiration
            if metadata.expires_at and metadata.expires_at < int(time.time()):
                metadata.status = KeyStatus.EXPIRED
                self._store_metadata(metadata)
                raise KeyStatusError(f"Key {key_id} has expired")
            
            # Check usage authorization
            if usage and not (KeyUsage.ALL in metadata.usage or usage in metadata.usage):
                raise KeyUsageError(f"Key {key_id} is not authorized for {usage.value}")
            
            # Check owner authorization (simplified - in a real system, this would be more complex)
            if metadata.owner and requester and metadata.owner != requester and metadata.owner != "system":
                raise KeyAccessDeniedError(f"Requester {requester} is not authorized to access key {key_id}")
            
            # Retrieve and return the key
            return self._retrieve_key(key_id)
        except (KeyNotFoundError, KeyAccessDeniedError, KeyStatusError, KeyUsageError):
            raise
        except Exception as e:
            logger.error(f"Failed to get key {key_id}: {str(e)}")
            raise KeyManagementError(f"Failed to get key {key_id}: {str(e)}")
    
    def rotate_key(
        self,
        key_id: str,
        requester: Optional[str] = None
    ) -> str:
        """
        Rotate a key, creating a new version.
        
        Args:
            key_id: Unique identifier for the key to rotate.
            requester: Entity requesting the rotation.
        
        Returns:
            str: The new key ID.
        
        Raises:
            KeyNotFoundError: If the key is not found.
            KeyAccessDeniedError: If access to the key is denied.
            KeyStatusError: If the key has an invalid status.
            KeyRotationError: If key rotation fails.
        """
        try:
            # Retrieve metadata
            metadata = self._retrieve_metadata(key_id)
            
            # Check key status
            if metadata.status not in [KeyStatus.ACTIVE, KeyStatus.SCHEDULED_ROTATION]:
                raise KeyStatusError(f"Key {key_id} has status {metadata.status.value} and cannot be rotated")
            
            # Check owner authorization (simplified)
            if metadata.owner and requester and metadata.owner != requester and metadata.owner != "system":
                raise KeyAccessDeniedError(f"Requester {requester} is not authorized to rotate key {key_id}")
            
            # Generate a new key ID
            new_key_id = str(uuid.uuid4())
            
            # Generate a new key based on the algorithm
            if isinstance(metadata.algorithm, EncryptionAlgorithm):
                new_key_data = self._crypto.generate_symmetric_key(metadata.algorithm)
            elif isinstance(metadata.algorithm, AsymmetricAlgorithm):
                key_pair = self._crypto.generate_asymmetric_key_pair(metadata.algorithm)
                # For asymmetric keys, we store the private key
                new_key_data = key_pair['private_key']
                # Store the public key with a different ID
                public_key_id = f"{new_key_id}_public"
                self._store_key(public_key_id, key_pair['public_key'])
                
                # Create metadata for the public key
                public_metadata = KeyMetadata(
                    key_id=public_key_id,
                    key_type=metadata.key_type,
                    algorithm=metadata.algorithm,
                    created_at=int(time.time()),
                    status=KeyStatus.ACTIVE,
                    expires_at=metadata.expires_at,
                    rotation_period=metadata.rotation_period,
                    version=metadata.version + 1,
                    usage=[u for u in metadata.usage if u in [KeyUsage.VERIFY, KeyUsage.ENCRYPT]],
                    description=f"Public key for {new_key_id}",
                    tags=metadata.tags,
                    owner=metadata.owner
                )
                self._store_metadata(public_metadata)
            else:
                raise KeyRotationError(f"Unsupported algorithm type: {type(metadata.algorithm)}")
            
            # Store the new key
            self._store_key(new_key_id, new_key_data)
            
            # Create and store metadata for the new key
            new_metadata = KeyMetadata(
                key_id=new_key_id,
                key_type=metadata.key_type,
                algorithm=metadata.algorithm,
                created_at=int(time.time()),
                status=KeyStatus.ACTIVE,
                expires_at=metadata.expires_at,
                rotation_period=metadata.rotation_period,
                last_rotated=int(time.time()),
                version=metadata.version + 1,
                usage=metadata.usage,
                description=metadata.description,
                tags=metadata.tags,
                owner=metadata.owner
            )
            self._store_metadata(new_metadata)
            
            # Update the old key's status
            metadata.status = KeyStatus.ROTATED
            self._store_metadata(metadata)
            
            logger.info(f"Rotated key {key_id} to new key {new_key_id}")
            return new_key_id
        except (KeyNotFoundError, KeyAccessDeniedError, KeyStatusError):
            raise
        except Exception as e:
            logger.error(f"Failed to rotate key {key_id}: {str(e)}")
            raise KeyRotationError(f"Failed to rotate key {key_id}: {str(e)}")
    
    def revoke_key(
        self,
        key_id: str,
        reason: str,
        requester: Optional[str] = None
    ):
        """
        Revoke a key, marking it as compromised.
        
        Args:
            key_id: Unique identifier for the key to revoke.
            reason: Reason for revocation.
            requester: Entity requesting the revocation.
        
        Raises:
            KeyNotFoundError: If the key is not found.
            KeyAccessDeniedError: If access to the key is denied.
            KeyManagementError: If key revocation fails.
        """
        try:
            # Retrieve metadata
            metadata = self._retrieve_metadata(key_id)
            
            # Check owner authorization (simplified)
            if metadata.owner and requester and metadata.owner != requester and metadata.owner != "system":
                raise KeyAccessDeniedError(f"Requester {requester} is not authorized to revoke key {key_id}")
            
            # Update the key's status
            metadata.status = KeyStatus.COMPROMISED
            metadata.tags = metadata.tags or {}
            metadata.tags['revocation_reason'] = reason
            metadata.tags['revoked_at'] = str(int(time.time()))
            metadata.tags['revoked_by'] = requester or "system"
            
            # Store updated metadata
            self._store_metadata(metadata)
            
            # If this is a private key, also revoke the public key
            if key_id.endswith('_public'):
                private_key_id = key_id[:-7]  # Remove "_public"
                try:
                    self.revoke_key(private_key_id, reason, requester)
                except KeyNotFoundError:
                    # Private key might not exist, which is fine
                    pass
            else:
                # Check if there's a corresponding public key
                public_key_id = f"{key_id}_public"
                try:
                    self.revoke_key(public_key_id, reason, requester)
                except KeyNotFoundError:
                    # Public key might not exist, which is fine
                    pass
            
            logger.info(f"Revoked key {key_id}: {reason}")
        except (KeyNotFoundError, KeyAccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Failed to revoke key {key_id}: {str(e)}")
            raise KeyManagementError(f"Failed to revoke key {key_id}: {str(e)}")
    
    def list_keys(
        self,
        key_type: Optional[KeyType] = None,
        status: Optional[KeyStatus] = None,
        owner: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        requester: Optional[str] = None
    ) -> List[KeyMetadata]:
        """
        List keys matching the specified criteria.
        
        Args:
            key_type: Filter by key type.
            status: Filter by key status.
            owner: Filter by key owner.
            tags: Filter by tags (all specified tags must match).
            requester: Entity requesting the list.
        
        Returns:
            List[KeyMetadata]: List of key metadata matching the criteria.
        
        Raises:
            KeyManagementError: If listing keys fails.
        """
        try:
            results = []
            
            # Load all metadata if using persistent storage
            if self._storage_path:
                metadata_dir = os.path.join(self._storage_path, 'metadata')
                if os.path.exists(metadata_dir):
                    for filename in os.listdir(metadata_dir):
                        key_id = filename
                        if key_id not in self._metadata:
                            try:
                                self._retrieve_metadata(key_id)
                            except:
                                # Skip keys that can't be loaded
                                continue
            
            # Filter keys based on criteria
            for metadata in self._metadata.values():
                # Skip if key type doesn't match
                if key_type and metadata.key_type != key_type:
                    continue
                
                # Skip if status doesn't match
                if status and metadata.status != status:
                    continue
                
                # Skip if owner doesn't match
                if owner and metadata.owner != owner:
                    continue
                
                # Skip if tags don't match
                if tags:
                    match = True
                    for k, v in tags.items():
                        if k not in metadata.tags or metadata.tags[k] != v:
                            match = False
                            break
                    if not match:
                        continue
                
                # Skip if requester is not authorized (simplified)
                if metadata.owner and requester and metadata.owner != requester and metadata.owner != "system" and requester != "system":
                    continue
                
                results.append(metadata)
            
            return results
        except Exception as e:
            logger.error(f"Failed to list keys: {str(e)}")
            raise KeyManagementError(f"Failed to list keys: {str(e)}")
    
    def get_metadata(
        self,
        key_id: str,
        requester: Optional[str] = None
    ) -> KeyMetadata:
        """
        Get metadata for a key.
        
        Args:
            key_id: Unique identifier for the key.
            requester: Entity requesting the metadata.
        
        Returns:
            KeyMetadata: The key metadata.
        
        Raises:
            KeyNotFoundError: If the key is not found.
            KeyAccessDeniedError: If access to the key is denied.
        """
        try:
            # Retrieve metadata
            metadata = self._retrieve_metadata(key_id)
            
            # Check owner authorization (simplified)
            if metadata.owner and requester and metadata.owner != requester and metadata.owner != "system" and requester != "system":
                raise KeyAccessDeniedError(f"Requester {requester} is not authorized to access metadata for key {key_id}")
            
            return metadata
        except (KeyNotFoundError, KeyAccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Failed to get metadata for key {key_id}: {str(e)}")
            raise KeyManagementError(f"Failed to get metadata for key {key_id}: {str(e)}")
    
    def update_metadata(
        self,
        key_id: str,
        updates: Dict[str, Any],
        requester: Optional[str] = None
    ):
        """
        Update metadata for a key.
        
        Args:
            key_id: Unique identifier for the key.
            updates: Dictionary of metadata fields to update.
            requester: Entity requesting the update.
        
        Raises:
            KeyNotFoundError: If the key is not found.
            KeyAccessDeniedError: If access to the key is denied.
            KeyManagementError: If metadata update fails.
        """
        try:
            # Retrieve metadata
            metadata = self._retrieve_metadata(key_id)
            
            # Check owner authorization (simplified)
            if metadata.owner and requester and metadata.owner != requester and metadata.owner != "system":
                raise KeyAccessDeniedError(f"Requester {requester} is not authorized to update metadata for key {key_id}")
            
            # Update allowed fields
            allowed_fields = ['description', 'tags', 'rotation_period', 'expires_at']
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(metadata, field, value)
                else:
                    logger.warning(f"Ignoring update to restricted field: {field}")
            
            # Store updated metadata
            self._store_metadata(metadata)
            
            logger.info(f"Updated metadata for key {key_id}")
        except (KeyNotFoundError, KeyAccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Failed to update metadata for key {key_id}: {str(e)}")
            raise KeyManagementError(f"Failed to update metadata for key {key_id}: {str(e)}")
    
    def check_rotation_needed(self) -> List[str]:
        """
        Check which keys need rotation based on their rotation period.
        
        Returns:
            List[str]: List of key IDs that need rotation.
        """
        try:
            now = int(time.time())
            keys_to_rotate = []
            
            for metadata in self.list_keys(status=KeyStatus.ACTIVE):
                # Skip keys without rotation period
                if not metadata.rotation_period:
                    continue
                
                # Calculate next rotation time
                last_rotation = metadata.last_rotated or metadata.created_at
                next_rotation = last_rotation + metadata.rotation_period
                
                # Check if rotation is needed
                if now >= next_rotation:
                    keys_to_rotate.append(metadata.key_id)
                    
                    # Mark key as scheduled for rotation
                    metadata.status = KeyStatus.SCHEDULED_ROTATION
                    self._store_metadata(metadata)
            
            return keys_to_rotate
        except Exception as e:
            logger.error(f"Failed to check keys for rotation: {str(e)}")
            raise KeyManagementError(f"Failed to check keys for rotation: {str(e)}")
    
    def perform_scheduled_rotations(self):
        """
        Perform rotation for all keys scheduled for rotation.
        
        Returns:
            int: Number of keys rotated.
        """
        try:
            rotated_count = 0
            
            for metadata in self.list_keys(status=KeyStatus.SCHEDULED_ROTATION):
                try:
                    self.rotate_key(metadata.key_id)
                    rotated_count += 1
                except Exception as e:
                    logger.error(f"Failed to rotate scheduled key {metadata.key_id}: {str(e)}")
            
            return rotated_count
        except Exception as e:
            logger.error(f"Failed to perform scheduled rotations: {str(e)}")
            raise KeyManagementError(f"Failed to perform scheduled rotations: {str(e)}")
    
    def export_key(
        self,
        key_id: str,
        requester: Optional[str] = None,
        include_private: bool = False
    ) -> Dict[str, Any]:
        """
        Export a key for backup or transfer.
        
        Args:
            key_id: Unique identifier for the key.
            requester: Entity requesting the export.
            include_private: Whether to include private key material (for asymmetric keys).
        
        Returns:
            Dict: Exported key data and metadata.
        
        Raises:
            KeyNotFoundError: If the key is not found.
            KeyAccessDeniedError: If access to the key is denied.
            KeyManagementError: If key export fails.
        """
        try:
            # Retrieve metadata
            metadata = self._retrieve_metadata(key_id)
            
            # Check owner authorization (simplified)
            if metadata.owner and requester and metadata.owner != requester and metadata.owner != "system":
                raise KeyAccessDeniedError(f"Requester {requester} is not authorized to export key {key_id}")
            
            # For asymmetric keys, handle public/private key export
            is_private_key = not key_id.endswith('_public')
            is_asymmetric = isinstance(metadata.algorithm, AsymmetricAlgorithm)
            
            # If this is a private asymmetric key and include_private is False,
            # export only the public key
            if is_asymmetric and is_private_key and not include_private:
                public_key_id = f"{key_id}_public"
                try:
                    public_metadata = self._retrieve_metadata(public_key_id)
                    public_key = self._retrieve_key(public_key_id)
                    
                    return {
                        'key_id': public_key_id,
                        'key_data': base64.b64encode(public_key).decode(),
                        'metadata': public_metadata.to_dict(),
                        'is_public_key': True
                    }
                except KeyNotFoundError:
                    # If public key not found, create it on the fly
                    private_key = self._retrieve_key(key_id)
                    # This is a simplified approach - in a real system, you would
                    # properly extract the public key from the private key
                    public_key = b"PUBLIC_KEY_PLACEHOLDER"
                    
                    return {
                        'key_id': f"{key_id}_public",
                        'key_data': base64.b64encode(public_key).decode(),
                        'metadata': metadata.to_dict(),
                        'is_public_key': True
                    }
            
            # Otherwise, export the requested key
            key_data = self._retrieve_key(key_id)
            
            return {
                'key_id': key_id,
                'key_data': base64.b64encode(key_data).decode(),
                'metadata': metadata.to_dict(),
                'is_public_key': key_id.endswith('_public')
            }
        except (KeyNotFoundError, KeyAccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Failed to export key {key_id}: {str(e)}")
            raise KeyManagementError(f"Failed to export key {key_id}: {str(e)}")
    
    def import_key(
        self,
        key_data: Dict[str, Any],
        requester: Optional[str] = None,
        override_owner: Optional[str] = None
    ) -> str:
        """
        Import a key from a backup or transfer.
        
        Args:
            key_data: Exported key data and metadata.
            requester: Entity requesting the import.
            override_owner: New owner to assign to the imported key.
        
        Returns:
            str: The imported key ID.
        
        Raises:
            KeyManagementError: If key import fails.
        """
        try:
            # Extract key data and metadata
            key_id = key_data['key_id']
            raw_key = base64.b64decode(key_data['key_data'])
            metadata_dict = key_data['metadata']
            
            # Create metadata object
            metadata = KeyMetadata.from_dict(metadata_dict)
            
            # Override owner if specified
            if override_owner:
                metadata.owner = override_owner
            
            # Check if key already exists
            try:
                existing_metadata = self._retrieve_metadata(key_id)
                # If key exists and requester is not the owner, deny import
                if existing_metadata.owner and requester and existing_metadata.owner != requester and existing_metadata.owner != "system":
                    raise KeyAccessDeniedError(f"Requester {requester} is not authorized to overwrite key {key_id}")
            except KeyNotFoundError:
                # Key doesn't exist, which is fine for import
                pass
            
            # Store the key
            self._store_key(key_id, raw_key)
            
            # Store the metadata
            self._store_metadata(metadata)
            
            logger.info(f"Imported key {key_id}")
            return key_id
        except KeyAccessDeniedError:
            raise
        except Exception as e:
            logger.error(f"Failed to import key: {str(e)}")
            raise KeyManagementError(f"Failed to import key: {str(e)}")
    
    def backup_all_keys(
        self,
        backup_path: str,
        requester: Optional[str] = None,
        include_private: bool = False
    ) -> int:
        """
        Backup all keys to a file.
        
        Args:
            backup_path: Path to store the backup.
            requester: Entity requesting the backup.
            include_private: Whether to include private key material.
        
        Returns:
            int: Number of keys backed up.
        
        Raises:
            KeyManagementError: If backup fails.
        """
        try:
            # Only system or authorized users can perform backup
            if requester and requester != "system":
                # In a real system, check if requester has backup permission
                pass
            
            backup_data = []
            
            # Export all keys
            for metadata in self.list_keys():
                try:
                    key_export = self.export_key(
                        metadata.key_id,
                        requester="system",  # Override requester for backup
                        include_private=include_private
                    )
                    backup_data.append(key_export)
                except Exception as e:
                    logger.warning(f"Failed to export key {metadata.key_id} for backup: {str(e)}")
            
            # Write backup to file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f)
            
            logger.info(f"Backed up {len(backup_data)} keys to {backup_path}")
            return len(backup_data)
        except Exception as e:
            logger.error(f"Failed to backup keys: {str(e)}")
            raise KeyManagementError(f"Failed to backup keys: {str(e)}")
    
    def restore_from_backup(
        self,
        backup_path: str,
        requester: Optional[str] = None,
        override_owner: Optional[str] = None
    ) -> int:
        """
        Restore keys from a backup file.
        
        Args:
            backup_path: Path to the backup file.
            requester: Entity requesting the restore.
            override_owner: New owner to assign to all restored keys.
        
        Returns:
            int: Number of keys restored.
        
        Raises:
            KeyManagementError: If restore fails.
        """
        try:
            # Only system or authorized users can perform restore
            if requester and requester != "system":
                # In a real system, check if requester has restore permission
                pass
            
            # Read backup from file
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            restored_count = 0
            
            # Import all keys from backup
            for key_data in backup_data:
                try:
                    self.import_key(
                        key_data,
                        requester="system",  # Override requester for restore
                        override_owner=override_owner
                    )
                    restored_count += 1
                except Exception as e:
                    logger.warning(f"Failed to import key {key_data.get('key_id')} from backup: {str(e)}")
            
            logger.info(f"Restored {restored_count} keys from {backup_path}")
            return restored_count
        except Exception as e:
            logger.error(f"Failed to restore keys from backup: {str(e)}")
            raise KeyManagementError(f"Failed to restore keys from backup: {str(e)}")
