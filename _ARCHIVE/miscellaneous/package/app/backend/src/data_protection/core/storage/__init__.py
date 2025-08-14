"""
Storage module for the Data Protection Framework.

This package provides secure storage capabilities for different types of data,
including object storage, file storage, database storage, and cache storage.
"""

from .secure_storage import (
    StorageType,
    StorageMetadata,
    StorageBackend,
    FileSystemBackend,
    MemoryCacheBackend,
    SecureStorageService,
    StorageManager,
    StorageError,
    ObjectNotFoundError,
    AccessDeniedError,
    StorageQuotaExceededError,
    StorageIntegrityError
)

__all__ = [
    'StorageType',
    'StorageMetadata',
    'StorageBackend',
    'FileSystemBackend',
    'MemoryCacheBackend',
    'SecureStorageService',
    'StorageManager',
    'StorageError',
    'ObjectNotFoundError',
    'AccessDeniedError',
    'StorageQuotaExceededError',
    'StorageIntegrityError'
]
