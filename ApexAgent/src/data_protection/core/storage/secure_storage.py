"""
Secure Storage module for the Data Protection Framework.

This module provides secure storage capabilities for different types of data,
including object storage, file storage, database storage, and cache storage.
"""

import os
import io
import json
import time
import uuid
import hashlib
import logging
import base64
from typing import Dict, List, Optional, Tuple, Union, Any, BinaryIO, Set
from enum import Enum
import threading
import shutil

from ..crypto import CryptoCore, HashAlgorithm
from ..key_management import KeyManagementService, KeyType, KeyUsage
from ..encryption import EncryptionService, RestEncryptionService, EncryptionContext

# Configure logging
logger = logging.getLogger(__name__)

class StorageType(Enum):
    """Types of storage supported by the secure storage system."""
    OBJECT = "object"     # Object storage for unstructured data
    FILE = "file"         # File storage for documents and media
    DATABASE = "database" # Database storage for structured data
    CACHE = "cache"       # Cache storage for temporary data

class StorageError(Exception):
    """Base exception for storage operations."""
    pass

class ObjectNotFoundError(StorageError):
    """Exception raised when an object is not found."""
    pass

class AccessDeniedError(StorageError):
    """Exception raised when access to an object is denied."""
    pass

class StorageQuotaExceededError(StorageError):
    """Exception raised when storage quota is exceeded."""
    pass

class StorageIntegrityError(StorageError):
    """Exception raised when object integrity verification fails."""
    pass

class StorageMetadata:
    """Metadata for stored objects."""
    
    def __init__(
        self,
        object_id: str,
        content_type: str,
        size: int,
        created_at: int,
        modified_at: int,
        owner: str,
        encryption_info: Optional[Dict[str, Any]] = None,
        integrity_info: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        retention_policy: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize storage metadata.
        
        Args:
            object_id: Unique identifier for the object
            content_type: MIME type of the content
            size: Size in bytes
            created_at: Creation timestamp (Unix time)
            modified_at: Last modification timestamp (Unix time)
            owner: Owner of the object
            encryption_info: Information about encryption
            integrity_info: Information about integrity verification
            tags: User-defined tags
            retention_policy: Data retention policy
            access_control: Access control information
        """
        self.object_id = object_id
        self.content_type = content_type
        self.size = size
        self.created_at = created_at
        self.modified_at = modified_at
        self.owner = owner
        self.encryption_info = encryption_info or {}
        self.integrity_info = integrity_info or {}
        self.tags = tags or {}
        self.retention_policy = retention_policy or {}
        self.access_control = access_control or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'object_id': self.object_id,
            'content_type': self.content_type,
            'size': self.size,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'owner': self.owner,
            'encryption_info': self.encryption_info,
            'integrity_info': self.integrity_info,
            'tags': self.tags,
            'retention_policy': self.retention_policy,
            'access_control': self.access_control
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorageMetadata':
        """Create metadata from dictionary."""
        return cls(
            object_id=data['object_id'],
            content_type=data['content_type'],
            size=data['size'],
            created_at=data['created_at'],
            modified_at=data['modified_at'],
            owner=data['owner'],
            encryption_info=data.get('encryption_info'),
            integrity_info=data.get('integrity_info'),
            tags=data.get('tags'),
            retention_policy=data.get('retention_policy'),
            access_control=data.get('access_control')
        )

class StorageBackend:
    """Abstract base class for storage backends."""
    
    def __init__(self):
        """Initialize the storage backend."""
        pass
    
    def put_object(
        self,
        object_id: str,
        data: Union[bytes, BinaryIO],
        metadata: StorageMetadata
    ) -> StorageMetadata:
        """
        Store an object.
        
        Args:
            object_id: Object identifier
            data: Object data
            metadata: Object metadata
        
        Returns:
            StorageMetadata: Updated metadata
        
        Raises:
            StorageError: If storage fails
        """
        raise NotImplementedError("Subclasses must implement put_object")
    
    def get_object(
        self,
        object_id: str
    ) -> Tuple[BinaryIO, StorageMetadata]:
        """
        Retrieve an object.
        
        Args:
            object_id: Object identifier
        
        Returns:
            Tuple[BinaryIO, StorageMetadata]: Object data and metadata
        
        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: If retrieval fails
        """
        raise NotImplementedError("Subclasses must implement get_object")
    
    def delete_object(self, object_id: str) -> None:
        """
        Delete an object.
        
        Args:
            object_id: Object identifier
        
        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: If deletion fails
        """
        raise NotImplementedError("Subclasses must implement delete_object")
    
    def get_metadata(self, object_id: str) -> StorageMetadata:
        """
        Get object metadata.
        
        Args:
            object_id: Object identifier
        
        Returns:
            StorageMetadata: Object metadata
        
        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: If retrieval fails
        """
        raise NotImplementedError("Subclasses must implement get_metadata")
    
    def update_metadata(
        self,
        object_id: str,
        metadata: StorageMetadata
    ) -> StorageMetadata:
        """
        Update object metadata.
        
        Args:
            object_id: Object identifier
            metadata: New metadata
        
        Returns:
            StorageMetadata: Updated metadata
        
        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: If update fails
        """
        raise NotImplementedError("Subclasses must implement update_metadata")
    
    def list_objects(
        self,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
        marker: Optional[str] = None
    ) -> Tuple[List[StorageMetadata], Optional[str]]:
        """
        List objects.
        
        Args:
            prefix: Prefix to filter objects
            max_keys: Maximum number of keys to return
            marker: Pagination marker
        
        Returns:
            Tuple[List[StorageMetadata], Optional[str]]: List of metadata and next marker
        
        Raises:
            StorageError: If listing fails
        """
        raise NotImplementedError("Subclasses must implement list_objects")

class FileSystemBackend(StorageBackend):
    """Storage backend using the local file system."""
    
    def __init__(self, base_path: str):
        """
        Initialize the file system backend.
        
        Args:
            base_path: Base directory for storage
        """
        super().__init__()
        self.base_path = os.path.abspath(base_path)
        self.metadata_path = os.path.join(self.base_path, ".metadata")
        
        # Create directories if they don't exist
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.metadata_path, exist_ok=True)
        
        logger.info(f"FileSystemBackend initialized at {self.base_path}")
    
    def _get_object_path(self, object_id: str) -> str:
        """Get the file path for an object."""
        # Use a directory structure based on the first few characters of the ID
        # to avoid having too many files in a single directory
        if len(object_id) >= 4:
            return os.path.join(self.base_path, object_id[:2], object_id[2:4], object_id)
        else:
            return os.path.join(self.base_path, object_id)
    
    def _get_metadata_path(self, object_id: str) -> str:
        """Get the file path for object metadata."""
        if len(object_id) >= 4:
            return os.path.join(self.metadata_path, object_id[:2], object_id[2:4], f"{object_id}.meta")
        else:
            return os.path.join(self.metadata_path, f"{object_id}.meta")
    
    def put_object(
        self,
        object_id: str,
        data: Union[bytes, BinaryIO],
        metadata: StorageMetadata
    ) -> StorageMetadata:
        """Store an object in the file system."""
        try:
            # Create directory structure if it doesn't exist
            object_path = self._get_object_path(object_id)
            os.makedirs(os.path.dirname(object_path), exist_ok=True)
            
            # Write data to file
            mode = "wb"
            if hasattr(data, "read"):
                # If data is a file-like object, read from it
                with open(object_path, mode) as f:
                    shutil.copyfileobj(data, f)
            else:
                # If data is bytes, write it directly
                with open(object_path, mode) as f:
                    f.write(data)
            
            # Update metadata
            file_size = os.path.getsize(object_path)
            metadata.size = file_size
            metadata.modified_at = int(time.time())
            
            # Save metadata
            metadata_path = self._get_metadata_path(object_id)
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            with open(metadata_path, "w") as f:
                json.dump(metadata.to_dict(), f)
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to store object {object_id}: {str(e)}")
            raise StorageError(f"Failed to store object: {str(e)}")
    
    def get_object(
        self,
        object_id: str
    ) -> Tuple[BinaryIO, StorageMetadata]:
        """Retrieve an object from the file system."""
        try:
            # Get object path
            object_path = self._get_object_path(object_id)
            
            # Check if object exists
            if not os.path.exists(object_path):
                raise ObjectNotFoundError(f"Object {object_id} not found")
            
            # Get metadata
            metadata = self.get_metadata(object_id)
            
            # Open file for reading
            file_obj = open(object_path, "rb")
            
            return file_obj, metadata
        except ObjectNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve object {object_id}: {str(e)}")
            raise StorageError(f"Failed to retrieve object: {str(e)}")
    
    def delete_object(self, object_id: str) -> None:
        """Delete an object from the file system."""
        try:
            # Get paths
            object_path = self._get_object_path(object_id)
            metadata_path = self._get_metadata_path(object_id)
            
            # Check if object exists
            if not os.path.exists(object_path):
                raise ObjectNotFoundError(f"Object {object_id} not found")
            
            # Delete object and metadata
            os.remove(object_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            # Try to remove empty directories
            try:
                os.rmdir(os.path.dirname(object_path))
                os.rmdir(os.path.dirname(os.path.dirname(object_path)))
            except:
                pass
            
            try:
                os.rmdir(os.path.dirname(metadata_path))
                os.rmdir(os.path.dirname(os.path.dirname(metadata_path)))
            except:
                pass
        except ObjectNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete object {object_id}: {str(e)}")
            raise StorageError(f"Failed to delete object: {str(e)}")
    
    def get_metadata(self, object_id: str) -> StorageMetadata:
        """Get object metadata from the file system."""
        try:
            # Get metadata path
            metadata_path = self._get_metadata_path(object_id)
            
            # Check if metadata exists
            if not os.path.exists(metadata_path):
                # Check if object exists
                object_path = self._get_object_path(object_id)
                if not os.path.exists(object_path):
                    raise ObjectNotFoundError(f"Object {object_id} not found")
                
                # If object exists but metadata doesn't, create default metadata
                file_size = os.path.getsize(object_path)
                file_time = int(os.path.getmtime(object_path))
                
                metadata = StorageMetadata(
                    object_id=object_id,
                    content_type="application/octet-stream",
                    size=file_size,
                    created_at=file_time,
                    modified_at=file_time,
                    owner="system"
                )
                
                # Save metadata
                os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
                with open(metadata_path, "w") as f:
                    json.dump(metadata.to_dict(), f)
                
                return metadata
            
            # Read metadata
            with open(metadata_path, "r") as f:
                metadata_dict = json.load(f)
            
            return StorageMetadata.from_dict(metadata_dict)
        except ObjectNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get metadata for object {object_id}: {str(e)}")
            raise StorageError(f"Failed to get metadata: {str(e)}")
    
    def update_metadata(
        self,
        object_id: str,
        metadata: StorageMetadata
    ) -> StorageMetadata:
        """Update object metadata in the file system."""
        try:
            # Get metadata path
            metadata_path = self._get_metadata_path(object_id)
            
            # Check if object exists
            object_path = self._get_object_path(object_id)
            if not os.path.exists(object_path):
                raise ObjectNotFoundError(f"Object {object_id} not found")
            
            # Update modification time
            metadata.modified_at = int(time.time())
            
            # Save metadata
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            with open(metadata_path, "w") as f:
                json.dump(metadata.to_dict(), f)
            
            return metadata
        except ObjectNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update metadata for object {object_id}: {str(e)}")
            raise StorageError(f"Failed to update metadata: {str(e)}")
    
    def list_objects(
        self,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
        marker: Optional[str] = None
    ) -> Tuple[List[StorageMetadata], Optional[str]]:
        """List objects in the file system."""
        try:
            results = []
            count = 0
            next_marker = None
            
            # Walk through the metadata directory
            for root, _, files in os.walk(self.metadata_path):
                for file in sorted(files):
                    if not file.endswith(".meta"):
                        continue
                    
                    # Get object ID from metadata filename
                    object_id = file[:-5]  # Remove .meta suffix
                    
                    # Skip objects before the marker
                    if marker and object_id <= marker:
                        continue
                    
                    # Skip objects that don't match the prefix
                    if prefix and not object_id.startswith(prefix):
                        continue
                    
                    # Get metadata
                    try:
                        metadata_path = os.path.join(root, file)
                        with open(metadata_path, "r") as f:
                            metadata_dict = json.load(f)
                        
                        metadata = StorageMetadata.from_dict(metadata_dict)
                        results.append(metadata)
                        count += 1
                        
                        # Stop if we've reached the maximum number of keys
                        if count >= max_keys:
                            next_marker = object_id
                            break
                    except:
                        # Skip invalid metadata
                        continue
                
                # Stop if we've reached the maximum number of keys
                if count >= max_keys:
                    break
            
            return results, next_marker
        except Exception as e:
            logger.error(f"Failed to list objects: {str(e)}")
            raise StorageError(f"Failed to list objects: {str(e)}")

class MemoryCacheBackend(StorageBackend):
    """In-memory cache storage backend."""
    
    def __init__(self, max_size_bytes: int = 1024 * 1024 * 100):
        """
        Initialize the memory cache backend.
        
        Args:
            max_size_bytes: Maximum cache size in bytes (default: 100MB)
        """
        super().__init__()
        self.max_size_bytes = max_size_bytes
        self.current_size_bytes = 0
        self.objects = {}  # object_id -> (data, metadata)
        self.lock = threading.RLock()
        
        logger.info(f"MemoryCacheBackend initialized with max size {max_size_bytes} bytes")
    
    def _evict_if_needed(self, required_bytes: int) -> None:
        """
        Evict objects if needed to make room for a new object.
        
        Args:
            required_bytes: Number of bytes required
        
        Raises:
            StorageQuotaExceededError: If there's not enough space
        """
        with self.lock:
            # Check if we need to evict
            if self.current_size_bytes + required_bytes <= self.max_size_bytes:
                return
            
            # Sort objects by last access time
            sorted_objects = sorted(
                self.objects.items(),
                key=lambda x: x[1][1].modified_at
            )
            
            # Evict objects until we have enough space
            for object_id, (data, metadata) in sorted_objects:
                if self.current_size_bytes + required_bytes <= self.max_size_bytes:
                    break
                
                # Remove object
                del self.objects[object_id]
                self.current_size_bytes -= metadata.size
            
            # Check if we have enough space now
            if self.current_size_bytes + required_bytes > self.max_size_bytes:
                raise StorageQuotaExceededError(
                    f"Not enough space in cache (required: {required_bytes}, "
                    f"available: {self.max_size_bytes - self.current_size_bytes})"
                )
    
    def put_object(
        self,
        object_id: str,
        data: Union[bytes, BinaryIO],
        metadata: StorageMetadata
    ) -> StorageMetadata:
        """Store an object in memory."""
        try:
            # Convert data to bytes if it's a file-like object
            if hasattr(data, "read"):
                data = data.read()
            
            # Make sure data is bytes
            if not isinstance(data, bytes):
                raise StorageError("Data must be bytes or a file-like object")
            
            # Update metadata
            metadata.size = len(data)
            metadata.modified_at = int(time.time())
            
            with self.lock:
                # Check if object already exists
                if object_id in self.objects:
                    old_size = self.objects[object_id][1].size
                    self.current_size_bytes -= old_size
                
                # Evict if needed
                self._evict_if_needed(metadata.size)
                
                # Store object
                self.objects[object_id] = (data, metadata)
                self.current_size_bytes += metadata.size
            
            return metadata
        except StorageQuotaExceededError:
            raise
        except Exception as e:
            logger.error(f"Failed to store object {object_id} in memory: {str(e)}")
            raise StorageError(f"Failed to store object in memory: {str(e)}")
    
    def get_object(
        self,
        object_id: str
    ) -> Tuple[BinaryIO, StorageMetadata]:
        """Retrieve an object from memory."""
        try:
            with self.lock:
                # Check if object exists
                if object_id not in self.objects:
                    raise ObjectNotFoundError(f"Object {object_id} not found in cache")
                
                # Get object
                data, metadata = self.objects[object_id]
                
                # Update access time
                metadata.modified_at = int(time.time())
                self.objects[object_id] = (data, metadata)
            
            # Return as file-like object
            return io.BytesIO(data), metadata
        except ObjectNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve object {object_id} from memory: {str(e)}")
            raise StorageError(f"Failed to retrieve object from memory: {str(e)}")
    
    def delete_object(self, object_id: str) -> None:
        """Delete an object from memory."""
        try:
            with self.lock:
                # Check if object exists
                if object_id not in self.objects:
                    raise ObjectNotFoundError(f"Object {object_id} not found in cache")
                
                # Get object size
                _, metadata = self.objects[object_id]
                
                # Remove object
                del self.objects[object_id]
                self.current_size_bytes -= metadata.size
        except ObjectNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete object {object_id} from memory: {str(e)}")
            raise StorageError(f"Failed to delete object from memory: {str(e)}")
    
    def get_metadata(self, object_id: str) -> StorageMetadata:
        """Get object metadata from memory."""
        try:
            with self.lock:
                # Check if object exists
                if object_id not in self.objects:
                    raise ObjectNotFoundError(f"Object {object_id} not found in cache")
                
                # Get metadata
                _, metadata = self.objects[object_id]
                
                return metadata
        except ObjectNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get metadata for object {object_id} from memory: {str(e)}")
            raise StorageError(f"Failed to get metadata from memory: {str(e)}")
    
    def update_metadata(
        self,
        object_id: str,
        metadata: StorageMetadata
    ) -> StorageMetadata:
        """Update object metadata in memory."""
        try:
            with self.lock:
                # Check if object exists
                if object_id not in self.objects:
                    raise ObjectNotFoundError(f"Object {object_id} not found in cache")
                
                # Get object
                data, old_metadata = self.objects[object_id]
                
                # Update metadata
                metadata.size = old_metadata.size
                metadata.modified_at = int(time.time())
                
                # Store updated metadata
                self.objects[object_id] = (data, metadata)
                
                return metadata
        except ObjectNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update metadata for object {object_id} in memory: {str(e)}")
            raise StorageError(f"Failed to update metadata in memory: {str(e)}")
    
    def list_objects(
        self,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
        marker: Optional[str] = None
    ) -> Tuple[List[StorageMetadata], Optional[str]]:
        """List objects in memory."""
        try:
            results = []
            count = 0
            next_marker = None
            
            with self.lock:
                # Get all object IDs
                object_ids = sorted(self.objects.keys())
                
                # Filter by marker
                if marker:
                    object_ids = [oid for oid in object_ids if oid > marker]
                
                # Filter by prefix
                if prefix:
                    object_ids = [oid for oid in object_ids if oid.startswith(prefix)]
                
                # Get metadata for each object
                for object_id in object_ids:
                    if count >= max_keys:
                        next_marker = object_id
                        break
                    
                    _, metadata = self.objects[object_id]
                    results.append(metadata)
                    count += 1
            
            return results, next_marker
        except Exception as e:
            logger.error(f"Failed to list objects in memory: {str(e)}")
            raise StorageError(f"Failed to list objects in memory: {str(e)}")

class SecureStorageService:
    """
    Service for secure storage operations.
    
    This class provides a unified interface for secure storage operations,
    including encryption, integrity verification, and access control.
    """
    
    def __init__(
        self,
        storage_backend: StorageBackend,
        encryption_service: Optional[EncryptionService] = None,
        crypto_core: Optional[CryptoCore] = None,
        key_manager: Optional[KeyManagementService] = None
    ):
        """
        Initialize the secure storage service.
        
        Args:
            storage_backend: Storage backend
            encryption_service: Encryption service
            crypto_core: Cryptographic core
            key_manager: Key management service
        """
        self._backend = storage_backend
        self._encryption = encryption_service or RestEncryptionService()
        self._crypto = crypto_core or CryptoCore()
        self._key_manager = key_manager or KeyManagementService()
        
        logger.info("Secure Storage Service initialized")
    
    def store_object(
        self,
        data: Union[bytes, BinaryIO],
        content_type: str,
        owner: str,
        object_id: Optional[str] = None,
        encrypt: bool = True,
        verify_integrity: bool = True,
        tags: Optional[Dict[str, str]] = None,
        retention_policy: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> StorageMetadata:
        """
        Store an object securely.
        
        Args:
            data: Object data
            content_type: MIME type of the content
            owner: Owner of the object
            object_id: Object ID (generated if None)
            encrypt: Whether to encrypt the data
            verify_integrity: Whether to verify integrity
            tags: User-defined tags
            retention_policy: Data retention policy
            access_control: Access control information
        
        Returns:
            StorageMetadata: Object metadata
        
        Raises:
            StorageError: If storage fails
        """
        try:
            # Generate object ID if not provided
            if object_id is None:
                object_id = str(uuid.uuid4())
            
            # Create initial metadata
            now = int(time.time())
            metadata = StorageMetadata(
                object_id=object_id,
                content_type=content_type,
                size=0,  # Will be updated after processing
                created_at=now,
                modified_at=now,
                owner=owner,
                tags=tags,
                retention_policy=retention_policy,
                access_control=access_control
            )
            
            # Process data
            processed_data = data
            
            # Calculate integrity hash if requested
            if verify_integrity:
                # Convert to bytes if it's a file-like object
                if hasattr(data, "read"):
                    if hasattr(data, "seek"):
                        data.seek(0)
                    data_bytes = data.read()
                    processed_data = data_bytes
                else:
                    data_bytes = data
                
                # Calculate hash
                hash_value = self._crypto.hash(
                    data_bytes,
                    HashAlgorithm.SHA256
                )
                
                # Store integrity information
                metadata.integrity_info = {
                    'algorithm': HashAlgorithm.SHA256.value,
                    'hash': base64.b64encode(hash_value).decode('utf-8')
                }
            
            # Encrypt data if requested
            if encrypt:
                # Convert to bytes if it's a file-like object
                if hasattr(processed_data, "read"):
                    if hasattr(processed_data, "seek"):
                        processed_data.seek(0)
                    processed_data = processed_data.read()
                
                # Create encryption context
                context = EncryptionContext(
                    owner=owner,
                    content_type=content_type,
                    object_id=object_id
                )
                
                # Encrypt data
                encrypted_data = self._encryption.encrypt(processed_data, context)
                
                # Store encryption information
                metadata.encryption_info = {
                    'encrypted': True,
                    'algorithm': encrypted_data.algorithm.value,
                    'key_id': encrypted_data.key_id
                }
                
                # Use encrypted data for storage
                processed_data = encrypted_data.ciphertext
            
            # Store object
            return self._backend.put_object(object_id, processed_data, metadata)
        except Exception as e:
            logger.error(f"Failed to store object securely: {str(e)}")
            raise StorageError(f"Failed to store object securely: {str(e)}")
    
    def retrieve_object(
        self,
        object_id: str,
        requester: str
    ) -> Tuple[BinaryIO, StorageMetadata]:
        """
        Retrieve an object securely.
        
        Args:
            object_id: Object ID
            requester: Entity requesting the object
        
        Returns:
            Tuple[BinaryIO, StorageMetadata]: Object data and metadata
        
        Raises:
            ObjectNotFoundError: If object is not found
            AccessDeniedError: If access is denied
            StorageIntegrityError: If integrity verification fails
            StorageError: If retrieval fails
        """
        try:
            # Get object and metadata
            data_stream, metadata = self._backend.get_object(object_id)
            
            # Check access control
            if not self._check_access(metadata, requester, 'read'):
                raise AccessDeniedError(f"Access denied for {requester} to read object {object_id}")
            
            # Read all data
            data = data_stream.read()
            data_stream.close()
            
            # Decrypt if encrypted
            if metadata.encryption_info and metadata.encryption_info.get('encrypted', False):
                # Create encryption context
                context = EncryptionContext(
                    owner=metadata.owner,
                    content_type=metadata.content_type,
                    object_id=object_id
                )
                
                # Decrypt data
                decrypted_data = self._encryption.decrypt(data, context)
                data = decrypted_data
            
            # Verify integrity if hash is available
            if metadata.integrity_info and 'hash' in metadata.integrity_info:
                # Get stored hash
                algorithm_name = metadata.integrity_info.get('algorithm', HashAlgorithm.SHA256.value)
                algorithm = HashAlgorithm(algorithm_name)
                stored_hash = base64.b64decode(metadata.integrity_info['hash'])
                
                # Calculate hash
                calculated_hash = self._crypto.hash(data, algorithm)
                
                # Compare hashes
                if stored_hash != calculated_hash:
                    raise StorageIntegrityError(
                        f"Integrity verification failed for object {object_id}"
                    )
            
            # Return data as file-like object
            return io.BytesIO(data), metadata
        except (ObjectNotFoundError, AccessDeniedError, StorageIntegrityError):
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve object securely: {str(e)}")
            raise StorageError(f"Failed to retrieve object securely: {str(e)}")
    
    def delete_object(
        self,
        object_id: str,
        requester: str
    ) -> None:
        """
        Delete an object securely.
        
        Args:
            object_id: Object ID
            requester: Entity requesting deletion
        
        Raises:
            ObjectNotFoundError: If object is not found
            AccessDeniedError: If access is denied
            StorageError: If deletion fails
        """
        try:
            # Get metadata
            metadata = self._backend.get_metadata(object_id)
            
            # Check access control
            if not self._check_access(metadata, requester, 'delete'):
                raise AccessDeniedError(f"Access denied for {requester} to delete object {object_id}")
            
            # Delete object
            self._backend.delete_object(object_id)
        except (ObjectNotFoundError, AccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Failed to delete object securely: {str(e)}")
            raise StorageError(f"Failed to delete object securely: {str(e)}")
    
    def update_metadata(
        self,
        object_id: str,
        requester: str,
        tags: Optional[Dict[str, str]] = None,
        retention_policy: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> StorageMetadata:
        """
        Update object metadata.
        
        Args:
            object_id: Object ID
            requester: Entity requesting update
            tags: User-defined tags
            retention_policy: Data retention policy
            access_control: Access control information
        
        Returns:
            StorageMetadata: Updated metadata
        
        Raises:
            ObjectNotFoundError: If object is not found
            AccessDeniedError: If access is denied
            StorageError: If update fails
        """
        try:
            # Get metadata
            metadata = self._backend.get_metadata(object_id)
            
            # Check access control
            if not self._check_access(metadata, requester, 'update'):
                raise AccessDeniedError(f"Access denied for {requester} to update object {object_id}")
            
            # Update metadata
            if tags is not None:
                metadata.tags = tags
            
            if retention_policy is not None:
                metadata.retention_policy = retention_policy
            
            if access_control is not None:
                metadata.access_control = access_control
            
            # Save updated metadata
            return self._backend.update_metadata(object_id, metadata)
        except (ObjectNotFoundError, AccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Failed to update metadata: {str(e)}")
            raise StorageError(f"Failed to update metadata: {str(e)}")
    
    def list_objects(
        self,
        requester: str,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
        marker: Optional[str] = None
    ) -> Tuple[List[StorageMetadata], Optional[str]]:
        """
        List objects.
        
        Args:
            requester: Entity requesting listing
            prefix: Prefix to filter objects
            max_keys: Maximum number of keys to return
            marker: Pagination marker
        
        Returns:
            Tuple[List[StorageMetadata], Optional[str]]: List of metadata and next marker
        
        Raises:
            StorageError: If listing fails
        """
        try:
            # List objects
            objects, next_marker = self._backend.list_objects(prefix, max_keys, marker)
            
            # Filter by access control
            filtered_objects = [
                obj for obj in objects
                if self._check_access(obj, requester, 'list')
            ]
            
            return filtered_objects, next_marker
        except Exception as e:
            logger.error(f"Failed to list objects: {str(e)}")
            raise StorageError(f"Failed to list objects: {str(e)}")
    
    def _check_access(
        self,
        metadata: StorageMetadata,
        requester: str,
        operation: str
    ) -> bool:
        """
        Check if a requester has access to perform an operation.
        
        Args:
            metadata: Object metadata
            requester: Entity requesting access
            operation: Operation to perform (read, write, delete, update, list)
        
        Returns:
            bool: Whether access is granted
        """
        # Owner always has access
        if requester == metadata.owner:
            return True
        
        # System always has access
        if requester == "system":
            return True
        
        # Check access control
        access_control = metadata.access_control
        
        if not access_control:
            # Default: only owner and system have access
            return False
        
        # Check if requester is explicitly granted access
        if 'users' in access_control:
            user_permissions = access_control['users'].get(requester, [])
            if operation in user_permissions or '*' in user_permissions:
                return True
        
        # Check if requester is in a role with access
        if 'roles' in access_control and 'user_roles' in access_control:
            user_roles = access_control['user_roles'].get(requester, [])
            
            for role in user_roles:
                role_permissions = access_control['roles'].get(role, [])
                if operation in role_permissions or '*' in role_permissions:
                    return True
        
        # Check public access
        if 'public' in access_control:
            public_permissions = access_control['public']
            if operation in public_permissions or '*' in public_permissions:
                return True
        
        return False

class StorageManager:
    """
    Manager for different types of storage.
    
    This class provides a unified interface for different storage types,
    including object storage, file storage, database storage, and cache storage.
    """
    
    def __init__(
        self,
        base_path: str,
        encryption_service: Optional[EncryptionService] = None,
        crypto_core: Optional[CryptoCore] = None,
        key_manager: Optional[KeyManagementService] = None
    ):
        """
        Initialize the storage manager.
        
        Args:
            base_path: Base directory for storage
            encryption_service: Encryption service
            crypto_core: Cryptographic core
            key_manager: Key management service
        """
        self._base_path = os.path.abspath(base_path)
        self._encryption = encryption_service or RestEncryptionService()
        self._crypto = crypto_core or CryptoCore()
        self._key_manager = key_manager or KeyManagementService()
        
        # Create storage services
        self._object_storage = SecureStorageService(
            FileSystemBackend(os.path.join(self._base_path, "objects")),
            self._encryption,
            self._crypto,
            self._key_manager
        )
        
        self._file_storage = SecureStorageService(
            FileSystemBackend(os.path.join(self._base_path, "files")),
            self._encryption,
            self._crypto,
            self._key_manager
        )
        
        self._database_storage = SecureStorageService(
            FileSystemBackend(os.path.join(self._base_path, "database")),
            self._encryption,
            self._crypto,
            self._key_manager
        )
        
        self._cache_storage = SecureStorageService(
            MemoryCacheBackend(),
            self._encryption,
            self._crypto,
            self._key_manager
        )
        
        logger.info(f"Storage Manager initialized at {self._base_path}")
    
    def get_storage(self, storage_type: StorageType) -> SecureStorageService:
        """
        Get a storage service by type.
        
        Args:
            storage_type: Type of storage
        
        Returns:
            SecureStorageService: Storage service
        
        Raises:
            ValueError: If storage type is invalid
        """
        if storage_type == StorageType.OBJECT:
            return self._object_storage
        elif storage_type == StorageType.FILE:
            return self._file_storage
        elif storage_type == StorageType.DATABASE:
            return self._database_storage
        elif storage_type == StorageType.CACHE:
            return self._cache_storage
        else:
            raise ValueError(f"Invalid storage type: {storage_type}")
    
    def store_object(
        self,
        storage_type: StorageType,
        data: Union[bytes, BinaryIO],
        content_type: str,
        owner: str,
        object_id: Optional[str] = None,
        encrypt: bool = True,
        verify_integrity: bool = True,
        tags: Optional[Dict[str, str]] = None,
        retention_policy: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> StorageMetadata:
        """
        Store an object in the specified storage.
        
        Args:
            storage_type: Type of storage
            data: Object data
            content_type: MIME type of the content
            owner: Owner of the object
            object_id: Object ID (generated if None)
            encrypt: Whether to encrypt the data
            verify_integrity: Whether to verify integrity
            tags: User-defined tags
            retention_policy: Data retention policy
            access_control: Access control information
        
        Returns:
            StorageMetadata: Object metadata
        
        Raises:
            StorageError: If storage fails
        """
        storage = self.get_storage(storage_type)
        return storage.store_object(
            data,
            content_type,
            owner,
            object_id,
            encrypt,
            verify_integrity,
            tags,
            retention_policy,
            access_control
        )
    
    def retrieve_object(
        self,
        storage_type: StorageType,
        object_id: str,
        requester: str
    ) -> Tuple[BinaryIO, StorageMetadata]:
        """
        Retrieve an object from the specified storage.
        
        Args:
            storage_type: Type of storage
            object_id: Object ID
            requester: Entity requesting the object
        
        Returns:
            Tuple[BinaryIO, StorageMetadata]: Object data and metadata
        
        Raises:
            ObjectNotFoundError: If object is not found
            AccessDeniedError: If access is denied
            StorageIntegrityError: If integrity verification fails
            StorageError: If retrieval fails
        """
        storage = self.get_storage(storage_type)
        return storage.retrieve_object(object_id, requester)
    
    def delete_object(
        self,
        storage_type: StorageType,
        object_id: str,
        requester: str
    ) -> None:
        """
        Delete an object from the specified storage.
        
        Args:
            storage_type: Type of storage
            object_id: Object ID
            requester: Entity requesting deletion
        
        Raises:
            ObjectNotFoundError: If object is not found
            AccessDeniedError: If access is denied
            StorageError: If deletion fails
        """
        storage = self.get_storage(storage_type)
        storage.delete_object(object_id, requester)
    
    def update_metadata(
        self,
        storage_type: StorageType,
        object_id: str,
        requester: str,
        tags: Optional[Dict[str, str]] = None,
        retention_policy: Optional[Dict[str, Any]] = None,
        access_control: Optional[Dict[str, Any]] = None
    ) -> StorageMetadata:
        """
        Update object metadata in the specified storage.
        
        Args:
            storage_type: Type of storage
            object_id: Object ID
            requester: Entity requesting update
            tags: User-defined tags
            retention_policy: Data retention policy
            access_control: Access control information
        
        Returns:
            StorageMetadata: Updated metadata
        
        Raises:
            ObjectNotFoundError: If object is not found
            AccessDeniedError: If access is denied
            StorageError: If update fails
        """
        storage = self.get_storage(storage_type)
        return storage.update_metadata(
            object_id,
            requester,
            tags,
            retention_policy,
            access_control
        )
    
    def list_objects(
        self,
        storage_type: StorageType,
        requester: str,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
        marker: Optional[str] = None
    ) -> Tuple[List[StorageMetadata], Optional[str]]:
        """
        List objects in the specified storage.
        
        Args:
            storage_type: Type of storage
            requester: Entity requesting listing
            prefix: Prefix to filter objects
            max_keys: Maximum number of keys to return
            marker: Pagination marker
        
        Returns:
            Tuple[List[StorageMetadata], Optional[str]]: List of metadata and next marker
        
        Raises:
            StorageError: If listing fails
        """
        storage = self.get_storage(storage_type)
        return storage.list_objects(requester, prefix, max_keys, marker)
