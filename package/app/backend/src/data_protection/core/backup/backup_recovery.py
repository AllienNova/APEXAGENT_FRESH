"""
Backup and Recovery module for the Data Protection Framework.

This module provides comprehensive backup and recovery capabilities,
including scheduled backups, incremental backups, point-in-time recovery,
and disaster recovery.
"""

import os
import io
import json
import time
import uuid
import hashlib
import logging
import base64
import shutil
import tarfile
import zipfile
import threading
import datetime
from typing import Dict, List, Optional, Tuple, Union, Any, BinaryIO, Set, Callable
from enum import Enum
import concurrent.futures

from ..crypto import CryptoCore, HashAlgorithm
from ..key_management import KeyManagementService, KeyType, KeyUsage
from ..encryption import EncryptionService, RestEncryptionService, EncryptionContext
from ..storage import (
    StorageType, StorageMetadata, StorageBackend, 
    SecureStorageService, StorageManager,
    StorageError, ObjectNotFoundError
)

# Configure logging
logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Types of backups supported by the backup system."""
    FULL = "full"           # Complete backup of all data
    INCREMENTAL = "incremental"  # Backup of changes since last backup
    DIFFERENTIAL = "differential"  # Backup of changes since last full backup
    SNAPSHOT = "snapshot"    # Point-in-time snapshot

class BackupStatus(Enum):
    """Status of a backup operation."""
    PENDING = "pending"      # Backup is scheduled but not started
    IN_PROGRESS = "in_progress"  # Backup is in progress
    COMPLETED = "completed"  # Backup completed successfully
    FAILED = "failed"        # Backup failed
    ABORTED = "aborted"      # Backup was aborted

class RecoveryStatus(Enum):
    """Status of a recovery operation."""
    PENDING = "pending"      # Recovery is scheduled but not started
    IN_PROGRESS = "in_progress"  # Recovery is in progress
    COMPLETED = "completed"  # Recovery completed successfully
    FAILED = "failed"        # Recovery failed
    ABORTED = "aborted"      # Recovery was aborted

class BackupError(Exception):
    """Base exception for backup operations."""
    pass

class RecoveryError(Exception):
    """Base exception for recovery operations."""
    pass

class BackupMetadata:
    """Metadata for backup operations."""
    
    def __init__(
        self,
        backup_id: str,
        backup_type: BackupType,
        storage_type: StorageType,
        created_at: int,
        status: BackupStatus,
        owner: str,
        source_path: Optional[str] = None,
        destination_path: Optional[str] = None,
        size: int = 0,
        object_count: int = 0,
        encryption_info: Optional[Dict[str, Any]] = None,
        parent_backup_id: Optional[str] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        error_message: Optional[str] = None
    ):
        """
        Initialize backup metadata.
        
        Args:
            backup_id: Unique identifier for the backup
            backup_type: Type of backup
            storage_type: Type of storage being backed up
            created_at: Creation timestamp (Unix time)
            status: Status of the backup
            owner: Owner of the backup
            source_path: Source path or pattern
            destination_path: Destination path
            size: Size in bytes
            object_count: Number of objects in the backup
            encryption_info: Information about encryption
            parent_backup_id: ID of parent backup (for incremental/differential)
            retention_period: Retention period in seconds
            tags: User-defined tags
            error_message: Error message if backup failed
        """
        self.backup_id = backup_id
        self.backup_type = backup_type
        self.storage_type = storage_type
        self.created_at = created_at
        self.status = status
        self.owner = owner
        self.source_path = source_path
        self.destination_path = destination_path
        self.size = size
        self.object_count = object_count
        self.encryption_info = encryption_info or {}
        self.parent_backup_id = parent_backup_id
        self.retention_period = retention_period
        self.tags = tags or {}
        self.error_message = error_message
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'backup_id': self.backup_id,
            'backup_type': self.backup_type.value,
            'storage_type': self.storage_type.value,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'status': self.status.value,
            'owner': self.owner,
            'source_path': self.source_path,
            'destination_path': self.destination_path,
            'size': self.size,
            'object_count': self.object_count,
            'encryption_info': self.encryption_info,
            'parent_backup_id': self.parent_backup_id,
            'retention_period': self.retention_period,
            'tags': self.tags,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupMetadata':
        """Create metadata from dictionary."""
        metadata = cls(
            backup_id=data['backup_id'],
            backup_type=BackupType(data['backup_type']),
            storage_type=StorageType(data['storage_type']),
            created_at=data['created_at'],
            status=BackupStatus(data['status']),
            owner=data['owner'],
            source_path=data.get('source_path'),
            destination_path=data.get('destination_path'),
            size=data.get('size', 0),
            object_count=data.get('object_count', 0),
            encryption_info=data.get('encryption_info'),
            parent_backup_id=data.get('parent_backup_id'),
            retention_period=data.get('retention_period'),
            tags=data.get('tags'),
            error_message=data.get('error_message')
        )
        metadata.completed_at = data.get('completed_at')
        return metadata

class RecoveryMetadata:
    """Metadata for recovery operations."""
    
    def __init__(
        self,
        recovery_id: str,
        backup_id: str,
        created_at: int,
        status: RecoveryStatus,
        owner: str,
        destination_path: Optional[str] = None,
        point_in_time: Optional[int] = None,
        size: int = 0,
        object_count: int = 0,
        tags: Optional[Dict[str, str]] = None,
        error_message: Optional[str] = None
    ):
        """
        Initialize recovery metadata.
        
        Args:
            recovery_id: Unique identifier for the recovery
            backup_id: ID of the backup being recovered
            created_at: Creation timestamp (Unix time)
            status: Status of the recovery
            owner: Owner of the recovery
            destination_path: Destination path
            point_in_time: Point-in-time for recovery (Unix time)
            size: Size in bytes
            object_count: Number of objects recovered
            tags: User-defined tags
            error_message: Error message if recovery failed
        """
        self.recovery_id = recovery_id
        self.backup_id = backup_id
        self.created_at = created_at
        self.status = status
        self.owner = owner
        self.destination_path = destination_path
        self.point_in_time = point_in_time
        self.size = size
        self.object_count = object_count
        self.tags = tags or {}
        self.error_message = error_message
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'recovery_id': self.recovery_id,
            'backup_id': self.backup_id,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'status': self.status.value,
            'owner': self.owner,
            'destination_path': self.destination_path,
            'point_in_time': self.point_in_time,
            'size': self.size,
            'object_count': self.object_count,
            'tags': self.tags,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecoveryMetadata':
        """Create metadata from dictionary."""
        metadata = cls(
            recovery_id=data['recovery_id'],
            backup_id=data['backup_id'],
            created_at=data['created_at'],
            status=RecoveryStatus(data['status']),
            owner=data['owner'],
            destination_path=data.get('destination_path'),
            point_in_time=data.get('point_in_time'),
            size=data.get('size', 0),
            object_count=data.get('object_count', 0),
            tags=data.get('tags'),
            error_message=data.get('error_message')
        )
        metadata.completed_at = data.get('completed_at')
        return metadata

class BackupSchedule:
    """Schedule for backup operations."""
    
    def __init__(
        self,
        schedule_id: str,
        backup_type: BackupType,
        storage_type: StorageType,
        owner: str,
        source_path: Optional[str] = None,
        destination_path: Optional[str] = None,
        frequency: str = "daily",
        start_time: Optional[str] = None,
        retention_period: Optional[int] = None,
        enabled: bool = True,
        tags: Optional[Dict[str, str]] = None,
        last_run: Optional[int] = None,
        next_run: Optional[int] = None
    ):
        """
        Initialize backup schedule.
        
        Args:
            schedule_id: Unique identifier for the schedule
            backup_type: Type of backup
            storage_type: Type of storage to back up
            owner: Owner of the schedule
            source_path: Source path or pattern
            destination_path: Destination path
            frequency: Frequency of backups (daily, weekly, monthly)
            start_time: Start time in HH:MM format
            retention_period: Retention period in seconds
            enabled: Whether the schedule is enabled
            tags: User-defined tags
            last_run: Timestamp of last run (Unix time)
            next_run: Timestamp of next run (Unix time)
        """
        self.schedule_id = schedule_id
        self.backup_type = backup_type
        self.storage_type = storage_type
        self.owner = owner
        self.source_path = source_path
        self.destination_path = destination_path
        self.frequency = frequency
        self.start_time = start_time
        self.retention_period = retention_period
        self.enabled = enabled
        self.tags = tags or {}
        self.last_run = last_run
        self.next_run = next_run
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schedule to dictionary."""
        return {
            'schedule_id': self.schedule_id,
            'backup_type': self.backup_type.value,
            'storage_type': self.storage_type.value,
            'owner': self.owner,
            'source_path': self.source_path,
            'destination_path': self.destination_path,
            'frequency': self.frequency,
            'start_time': self.start_time,
            'retention_period': self.retention_period,
            'enabled': self.enabled,
            'tags': self.tags,
            'last_run': self.last_run,
            'next_run': self.next_run
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupSchedule':
        """Create schedule from dictionary."""
        return cls(
            schedule_id=data['schedule_id'],
            backup_type=BackupType(data['backup_type']),
            storage_type=StorageType(data['storage_type']),
            owner=data['owner'],
            source_path=data.get('source_path'),
            destination_path=data.get('destination_path'),
            frequency=data.get('frequency', 'daily'),
            start_time=data.get('start_time'),
            retention_period=data.get('retention_period'),
            enabled=data.get('enabled', True),
            tags=data.get('tags'),
            last_run=data.get('last_run'),
            next_run=data.get('next_run')
        )
    
    def calculate_next_run(self) -> int:
        """
        Calculate the next run time based on frequency and start time.
        
        Returns:
            int: Timestamp of next run (Unix time)
        """
        now = datetime.datetime.now()
        
        # Parse start time
        if self.start_time:
            try:
                hour, minute = map(int, self.start_time.split(':'))
            except:
                hour, minute = 0, 0
        else:
            hour, minute = 0, 0
        
        # Calculate next run based on frequency
        if self.frequency == 'daily':
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += datetime.timedelta(days=1)
        
        elif self.frequency == 'weekly':
            # Run on Sunday
            days_ahead = 6 - now.weekday()
            if days_ahead < 0 or (days_ahead == 0 and now.replace(hour=hour, minute=minute) <= now):
                days_ahead += 7
            
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + datetime.timedelta(days=days_ahead)
        
        elif self.frequency == 'monthly':
            # Run on the 1st of the month
            if now.day == 1 and now.replace(hour=hour, minute=minute) > now:
                next_run = now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
            else:
                if now.month == 12:
                    next_run = now.replace(year=now.year+1, month=1, day=1, hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month+1, day=1, hour=hour, minute=minute, second=0, microsecond=0)
        
        else:
            # Default to daily
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += datetime.timedelta(days=1)
        
        return int(next_run.timestamp())

class BackupService:
    """
    Service for backup operations.
    
    This class provides methods for creating, managing, and restoring backups
    of data stored in the secure storage system.
    """
    
    def __init__(
        self,
        storage_manager: StorageManager,
        backup_storage_path: str,
        encryption_service: Optional[EncryptionService] = None,
        crypto_core: Optional[CryptoCore] = None,
        key_manager: Optional[KeyManagementService] = None,
        max_concurrent_operations: int = 5
    ):
        """
        Initialize the backup service.
        
        Args:
            storage_manager: Storage manager
            backup_storage_path: Path for storing backups
            encryption_service: Encryption service
            crypto_core: Cryptographic core
            key_manager: Key management service
            max_concurrent_operations: Maximum number of concurrent operations
        """
        self._storage_manager = storage_manager
        self._backup_storage_path = os.path.abspath(backup_storage_path)
        self._encryption = encryption_service or RestEncryptionService()
        self._crypto = crypto_core or CryptoCore()
        self._key_manager = key_manager or KeyManagementService()
        self._max_concurrent_operations = max_concurrent_operations
        
        # Create backup storage directory
        os.makedirs(self._backup_storage_path, exist_ok=True)
        
        # Create metadata directory
        self._metadata_path = os.path.join(self._backup_storage_path, "metadata")
        os.makedirs(self._metadata_path, exist_ok=True)
        
        # Create schedules directory
        self._schedules_path = os.path.join(self._backup_storage_path, "schedules")
        os.makedirs(self._schedules_path, exist_ok=True)
        
        # Create recovery metadata directory
        self._recovery_metadata_path = os.path.join(self._backup_storage_path, "recovery_metadata")
        os.makedirs(self._recovery_metadata_path, exist_ok=True)
        
        # Thread pool for concurrent operations
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_operations)
        
        # Active operations
        self._active_backups = {}
        self._active_recoveries = {}
        
        logger.info(f"Backup Service initialized with storage path {self._backup_storage_path}")
    
    def _get_backup_path(self, backup_id: str) -> str:
        """Get the path for a backup."""
        return os.path.join(self._backup_storage_path, backup_id)
    
    def _get_backup_metadata_path(self, backup_id: str) -> str:
        """Get the path for backup metadata."""
        return os.path.join(self._metadata_path, f"{backup_id}.json")
    
    def _get_schedule_path(self, schedule_id: str) -> str:
        """Get the path for a backup schedule."""
        return os.path.join(self._schedules_path, f"{schedule_id}.json")
    
    def _get_recovery_metadata_path(self, recovery_id: str) -> str:
        """Get the path for recovery metadata."""
        return os.path.join(self._recovery_metadata_path, f"{recovery_id}.json")
    
    def create_backup(
        self,
        backup_type: BackupType,
        storage_type: StorageType,
        owner: str,
        source_path: Optional[str] = None,
        destination_path: Optional[str] = None,
        encrypt: bool = True,
        parent_backup_id: Optional[str] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        async_operation: bool = True
    ) -> BackupMetadata:
        """
        Create a backup.
        
        Args:
            backup_type: Type of backup
            storage_type: Type of storage to back up
            owner: Owner of the backup
            source_path: Source path or pattern
            destination_path: Destination path (if None, use default)
            encrypt: Whether to encrypt the backup
            parent_backup_id: ID of parent backup (for incremental/differential)
            retention_period: Retention period in seconds
            tags: User-defined tags
            async_operation: Whether to perform the backup asynchronously
        
        Returns:
            BackupMetadata: Backup metadata
        
        Raises:
            BackupError: If backup creation fails
        """
        try:
            # Generate backup ID
            backup_id = str(uuid.uuid4())
            
            # Create backup directory
            backup_path = self._get_backup_path(backup_id)
            os.makedirs(backup_path, exist_ok=True)
            
            # Set destination path if not provided
            if destination_path is None:
                destination_path = backup_path
            
            # Create metadata
            now = int(time.time())
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=backup_type,
                storage_type=storage_type,
                created_at=now,
                status=BackupStatus.PENDING,
                owner=owner,
                source_path=source_path,
                destination_path=destination_path,
                encryption_info={'encrypted': encrypt},
                parent_backup_id=parent_backup_id,
                retention_period=retention_period,
                tags=tags
            )
            
            # Save metadata
            self._save_backup_metadata(metadata)
            
            # Start backup operation
            if async_operation:
                self._active_backups[backup_id] = self._executor.submit(
                    self._perform_backup, metadata
                )
            else:
                metadata = self._perform_backup(metadata)
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            raise BackupError(f"Failed to create backup: {str(e)}")
    
    def _perform_backup(self, metadata: BackupMetadata) -> BackupMetadata:
        """
        Perform the actual backup operation.
        
        Args:
            metadata: Backup metadata
        
        Returns:
            BackupMetadata: Updated metadata
        """
        try:
            # Update status
            metadata.status = BackupStatus.IN_PROGRESS
            self._save_backup_metadata(metadata)
            
            # Get storage service
            storage = self._storage_manager.get_storage(metadata.storage_type)
            
            # List objects to backup
            objects, _ = storage.list_objects(
                requester=metadata.owner,
                prefix=metadata.source_path
            )
            
            # Create manifest
            manifest = {
                'backup_id': metadata.backup_id,
                'backup_type': metadata.backup_type.value,
                'storage_type': metadata.storage_type.value,
                'created_at': metadata.created_at,
                'owner': metadata.owner,
                'objects': []
            }
            
            # Process each object
            total_size = 0
            object_count = 0
            
            for obj_metadata in objects:
                try:
                    # Skip objects that haven't changed for incremental/differential backups
                    if self._should_skip_object(obj_metadata, metadata):
                        continue
                    
                    # Retrieve object
                    data_stream, _ = storage.retrieve_object(
                        obj_metadata.object_id,
                        requester=metadata.owner
                    )
                    
                    # Read data
                    data = data_stream.read()
                    data_stream.close()
                    
                    # Encrypt if requested
                    if metadata.encryption_info.get('encrypted', False):
                        # Create encryption context
                        context = EncryptionContext(
                            owner=metadata.owner,
                            content_type=obj_metadata.content_type,
                            object_id=obj_metadata.object_id
                        )
                        
                        # Encrypt data
                        encrypted_data = self._encryption.encrypt(data, context)
                        
                        # Update encryption info
                        metadata.encryption_info.update({
                            'algorithm': encrypted_data.algorithm.value,
                            'key_id': encrypted_data.key_id
                        })
                        
                        # Use encrypted data
                        data = encrypted_data.ciphertext
                    
                    # Save object to backup
                    object_path = os.path.join(
                        metadata.destination_path,
                        obj_metadata.object_id
                    )
                    
                    # Create directory if needed
                    os.makedirs(os.path.dirname(object_path), exist_ok=True)
                    
                    # Write data
                    with open(object_path, 'wb') as f:
                        f.write(data)
                    
                    # Update manifest
                    manifest['objects'].append({
                        'object_id': obj_metadata.object_id,
                        'content_type': obj_metadata.content_type,
                        'size': obj_metadata.size,
                        'created_at': obj_metadata.created_at,
                        'modified_at': obj_metadata.modified_at,
                        'path': object_path
                    })
                    
                    # Update statistics
                    total_size += obj_metadata.size
                    object_count += 1
                
                except Exception as e:
                    logger.error(f"Failed to backup object {obj_metadata.object_id}: {str(e)}")
                    # Continue with next object
            
            # Save manifest
            manifest_path = os.path.join(metadata.destination_path, "manifest.json")
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f)
            
            # Update metadata
            metadata.size = total_size
            metadata.object_count = object_count
            metadata.status = BackupStatus.COMPLETED
            metadata.completed_at = int(time.time())
            
            # Save updated metadata
            self._save_backup_metadata(metadata)
            
            logger.info(f"Backup {metadata.backup_id} completed successfully")
            return metadata
        
        except Exception as e:
            logger.error(f"Backup {metadata.backup_id} failed: {str(e)}")
            
            # Update metadata
            metadata.status = BackupStatus.FAILED
            metadata.error_message = str(e)
            self._save_backup_metadata(metadata)
            
            return metadata
    
    def _should_skip_object(
        self,
        obj_metadata: StorageMetadata,
        backup_metadata: BackupMetadata
    ) -> bool:
        """
        Determine if an object should be skipped for incremental/differential backups.
        
        Args:
            obj_metadata: Object metadata
            backup_metadata: Backup metadata
        
        Returns:
            bool: Whether to skip the object
        """
        # Always include objects for full backups
        if backup_metadata.backup_type == BackupType.FULL:
            return False
        
        # Always include objects for snapshots
        if backup_metadata.backup_type == BackupType.SNAPSHOT:
            return False
        
        # Skip objects if no parent backup
        if not backup_metadata.parent_backup_id:
            return False
        
        try:
            # Get parent backup metadata
            parent_metadata = self.get_backup_metadata(backup_metadata.parent_backup_id)
            
            # Get parent backup manifest
            manifest_path = os.path.join(parent_metadata.destination_path, "manifest.json")
            if not os.path.exists(manifest_path):
                return False
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Find object in manifest
            for obj in manifest.get('objects', []):
                if obj['object_id'] == obj_metadata.object_id:
                    # For incremental backups, skip if modified time is the same
                    if backup_metadata.backup_type == BackupType.INCREMENTAL:
                        return obj['modified_at'] >= obj_metadata.modified_at
                    
                    # For differential backups, check against the full backup
                    if backup_metadata.backup_type == BackupType.DIFFERENTIAL:
                        # If parent is full, compare directly
                        if parent_metadata.backup_type == BackupType.FULL:
                            return obj['modified_at'] >= obj_metadata.modified_at
                        
                        # If parent is not full, need to find the full backup
                        if parent_metadata.parent_backup_id:
                            full_metadata = self._find_full_backup(parent_metadata.parent_backup_id)
                            if full_metadata:
                                full_manifest_path = os.path.join(full_metadata.destination_path, "manifest.json")
                                if os.path.exists(full_manifest_path):
                                    with open(full_manifest_path, 'r') as f:
                                        full_manifest = json.load(f)
                                    
                                    for full_obj in full_manifest.get('objects', []):
                                        if full_obj['object_id'] == obj_metadata.object_id:
                                            return full_obj['modified_at'] >= obj_metadata.modified_at
            
            # If object not found in parent, include it
            return False
        
        except Exception as e:
            logger.error(f"Error checking if object should be skipped: {str(e)}")
            # If there's an error, include the object to be safe
            return False
    
    def _find_full_backup(self, backup_id: str) -> Optional[BackupMetadata]:
        """
        Find the full backup that is the ancestor of the given backup.
        
        Args:
            backup_id: Backup ID
        
        Returns:
            Optional[BackupMetadata]: Full backup metadata or None
        """
        try:
            metadata = self.get_backup_metadata(backup_id)
            
            # If this is a full backup, return it
            if metadata.backup_type == BackupType.FULL:
                return metadata
            
            # If no parent, return None
            if not metadata.parent_backup_id:
                return None
            
            # Recursively find full backup
            return self._find_full_backup(metadata.parent_backup_id)
        
        except Exception:
            return None
    
    def _save_backup_metadata(self, metadata: BackupMetadata) -> None:
        """
        Save backup metadata to disk.
        
        Args:
            metadata: Backup metadata
        """
        metadata_path = self._get_backup_metadata_path(metadata.backup_id)
        with open(metadata_path, 'w') as f:
            json.dump(metadata.to_dict(), f)
    
    def get_backup_metadata(self, backup_id: str) -> BackupMetadata:
        """
        Get backup metadata.
        
        Args:
            backup_id: Backup ID
        
        Returns:
            BackupMetadata: Backup metadata
        
        Raises:
            BackupError: If metadata retrieval fails
        """
        try:
            metadata_path = self._get_backup_metadata_path(backup_id)
            
            if not os.path.exists(metadata_path):
                raise BackupError(f"Backup {backup_id} not found")
            
            with open(metadata_path, 'r') as f:
                metadata_dict = json.load(f)
            
            return BackupMetadata.from_dict(metadata_dict)
        
        except Exception as e:
            logger.error(f"Failed to get backup metadata: {str(e)}")
            raise BackupError(f"Failed to get backup metadata: {str(e)}")
    
    def list_backups(
        self,
        owner: Optional[str] = None,
        status: Optional[BackupStatus] = None,
        backup_type: Optional[BackupType] = None,
        storage_type: Optional[StorageType] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[BackupMetadata]:
        """
        List backups with optional filtering.
        
        Args:
            owner: Filter by owner
            status: Filter by status
            backup_type: Filter by backup type
            storage_type: Filter by storage type
            start_time: Filter by start time (Unix time)
            end_time: Filter by end time (Unix time)
            tags: Filter by tags
        
        Returns:
            List[BackupMetadata]: List of backup metadata
        
        Raises:
            BackupError: If listing fails
        """
        try:
            results = []
            
            # List all metadata files
            for filename in os.listdir(self._metadata_path):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    # Read metadata
                    with open(os.path.join(self._metadata_path, filename), 'r') as f:
                        metadata_dict = json.load(f)
                    
                    metadata = BackupMetadata.from_dict(metadata_dict)
                    
                    # Apply filters
                    if owner and metadata.owner != owner:
                        continue
                    
                    if status and metadata.status != status:
                        continue
                    
                    if backup_type and metadata.backup_type != backup_type:
                        continue
                    
                    if storage_type and metadata.storage_type != storage_type:
                        continue
                    
                    if start_time and metadata.created_at < start_time:
                        continue
                    
                    if end_time and metadata.created_at > end_time:
                        continue
                    
                    if tags:
                        match = True
                        for key, value in tags.items():
                            if key not in metadata.tags or metadata.tags[key] != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    results.append(metadata)
                
                except Exception as e:
                    logger.error(f"Error processing metadata file {filename}: {str(e)}")
                    # Continue with next file
            
            # Sort by creation time (newest first)
            results.sort(key=lambda x: x.created_at, reverse=True)
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            raise BackupError(f"Failed to list backups: {str(e)}")
    
    def delete_backup(self, backup_id: str, owner: str) -> None:
        """
        Delete a backup.
        
        Args:
            backup_id: Backup ID
            owner: Owner requesting deletion
        
        Raises:
            BackupError: If deletion fails
        """
        try:
            # Get metadata
            metadata = self.get_backup_metadata(backup_id)
            
            # Check ownership
            if metadata.owner != owner and owner != "system":
                raise BackupError(f"Access denied: {owner} is not the owner of backup {backup_id}")
            
            # Check if backup is in progress
            if metadata.status == BackupStatus.IN_PROGRESS:
                raise BackupError(f"Cannot delete backup {backup_id} because it is in progress")
            
            # Delete backup files
            backup_path = self._get_backup_path(backup_id)
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            
            # Delete metadata
            metadata_path = self._get_backup_metadata_path(backup_id)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            logger.info(f"Backup {backup_id} deleted successfully")
        
        except Exception as e:
            logger.error(f"Failed to delete backup: {str(e)}")
            raise BackupError(f"Failed to delete backup: {str(e)}")
    
    def create_recovery(
        self,
        backup_id: str,
        owner: str,
        destination_path: Optional[str] = None,
        point_in_time: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        async_operation: bool = True
    ) -> RecoveryMetadata:
        """
        Create a recovery operation.
        
        Args:
            backup_id: ID of the backup to recover
            owner: Owner of the recovery
            destination_path: Destination path (if None, use original path)
            point_in_time: Point-in-time for recovery (Unix time)
            tags: User-defined tags
            async_operation: Whether to perform the recovery asynchronously
        
        Returns:
            RecoveryMetadata: Recovery metadata
        
        Raises:
            RecoveryError: If recovery creation fails
        """
        try:
            # Get backup metadata
            backup_metadata = self.get_backup_metadata(backup_id)
            
            # Check ownership
            if backup_metadata.owner != owner and owner != "system":
                raise RecoveryError(f"Access denied: {owner} is not the owner of backup {backup_id}")
            
            # Check if backup is completed
            if backup_metadata.status != BackupStatus.COMPLETED:
                raise RecoveryError(f"Cannot recover from backup {backup_id} because it is not completed")
            
            # Generate recovery ID
            recovery_id = str(uuid.uuid4())
            
            # Set destination path if not provided
            if destination_path is None:
                destination_path = backup_metadata.source_path
            
            # Create metadata
            now = int(time.time())
            metadata = RecoveryMetadata(
                recovery_id=recovery_id,
                backup_id=backup_id,
                created_at=now,
                status=RecoveryStatus.PENDING,
                owner=owner,
                destination_path=destination_path,
                point_in_time=point_in_time,
                tags=tags
            )
            
            # Save metadata
            self._save_recovery_metadata(metadata)
            
            # Start recovery operation
            if async_operation:
                self._active_recoveries[recovery_id] = self._executor.submit(
                    self._perform_recovery, metadata
                )
            else:
                metadata = self._perform_recovery(metadata)
            
            return metadata
        
        except Exception as e:
            logger.error(f"Failed to create recovery: {str(e)}")
            raise RecoveryError(f"Failed to create recovery: {str(e)}")
    
    def _perform_recovery(self, metadata: RecoveryMetadata) -> RecoveryMetadata:
        """
        Perform the actual recovery operation.
        
        Args:
            metadata: Recovery metadata
        
        Returns:
            RecoveryMetadata: Updated metadata
        """
        try:
            # Update status
            metadata.status = RecoveryStatus.IN_PROGRESS
            self._save_recovery_metadata(metadata)
            
            # Get backup metadata
            backup_metadata = self.get_backup_metadata(metadata.backup_id)
            
            # Get storage service
            storage = self._storage_manager.get_storage(backup_metadata.storage_type)
            
            # Read manifest
            manifest_path = os.path.join(backup_metadata.destination_path, "manifest.json")
            if not os.path.exists(manifest_path):
                raise RecoveryError(f"Backup manifest not found for {metadata.backup_id}")
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Process each object
            total_size = 0
            object_count = 0
            
            for obj in manifest.get('objects', []):
                try:
                    # Skip objects based on point-in-time
                    if metadata.point_in_time and obj['modified_at'] > metadata.point_in_time:
                        continue
                    
                    # Read object data
                    object_path = obj['path']
                    if not os.path.exists(object_path):
                        logger.warning(f"Object file not found: {object_path}")
                        continue
                    
                    with open(object_path, 'rb') as f:
                        data = f.read()
                    
                    # Decrypt if encrypted
                    if backup_metadata.encryption_info.get('encrypted', False):
                        # Create encryption context
                        context = EncryptionContext(
                            owner=backup_metadata.owner,
                            content_type=obj['content_type'],
                            object_id=obj['object_id']
                        )
                        
                        # Decrypt data
                        data = self._encryption.decrypt(data, context)
                    
                    # Store object in destination
                    object_id = obj['object_id']
                    content_type = obj['content_type']
                    
                    # Create destination path if needed
                    if metadata.destination_path:
                        # If destination is a storage path, store in storage
                        if metadata.destination_path.startswith('/'):
                            # Create directory if needed
                            os.makedirs(metadata.destination_path, exist_ok=True)
                            
                            # Write to file
                            dest_path = os.path.join(metadata.destination_path, object_id)
                            with open(dest_path, 'wb') as f:
                                f.write(data)
                        else:
                            # Store in storage service
                            storage.store_object(
                                data=data,
                                content_type=content_type,
                                owner=metadata.owner,
                                object_id=object_id,
                                encrypt=False,  # Already encrypted if needed
                                verify_integrity=True
                            )
                    else:
                        # Store in original location
                        storage.store_object(
                            data=data,
                            content_type=content_type,
                            owner=metadata.owner,
                            object_id=object_id,
                            encrypt=False,  # Already encrypted if needed
                            verify_integrity=True
                        )
                    
                    # Update statistics
                    total_size += obj['size']
                    object_count += 1
                
                except Exception as e:
                    logger.error(f"Failed to recover object {obj['object_id']}: {str(e)}")
                    # Continue with next object
            
            # Update metadata
            metadata.size = total_size
            metadata.object_count = object_count
            metadata.status = RecoveryStatus.COMPLETED
            metadata.completed_at = int(time.time())
            
            # Save updated metadata
            self._save_recovery_metadata(metadata)
            
            logger.info(f"Recovery {metadata.recovery_id} completed successfully")
            return metadata
        
        except Exception as e:
            logger.error(f"Recovery {metadata.recovery_id} failed: {str(e)}")
            
            # Update metadata
            metadata.status = RecoveryStatus.FAILED
            metadata.error_message = str(e)
            self._save_recovery_metadata(metadata)
            
            return metadata
    
    def _save_recovery_metadata(self, metadata: RecoveryMetadata) -> None:
        """
        Save recovery metadata to disk.
        
        Args:
            metadata: Recovery metadata
        """
        metadata_path = self._get_recovery_metadata_path(metadata.recovery_id)
        with open(metadata_path, 'w') as f:
            json.dump(metadata.to_dict(), f)
    
    def get_recovery_metadata(self, recovery_id: str) -> RecoveryMetadata:
        """
        Get recovery metadata.
        
        Args:
            recovery_id: Recovery ID
        
        Returns:
            RecoveryMetadata: Recovery metadata
        
        Raises:
            RecoveryError: If metadata retrieval fails
        """
        try:
            metadata_path = self._get_recovery_metadata_path(recovery_id)
            
            if not os.path.exists(metadata_path):
                raise RecoveryError(f"Recovery {recovery_id} not found")
            
            with open(metadata_path, 'r') as f:
                metadata_dict = json.load(f)
            
            return RecoveryMetadata.from_dict(metadata_dict)
        
        except Exception as e:
            logger.error(f"Failed to get recovery metadata: {str(e)}")
            raise RecoveryError(f"Failed to get recovery metadata: {str(e)}")
    
    def list_recoveries(
        self,
        owner: Optional[str] = None,
        status: Optional[RecoveryStatus] = None,
        backup_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[RecoveryMetadata]:
        """
        List recoveries with optional filtering.
        
        Args:
            owner: Filter by owner
            status: Filter by status
            backup_id: Filter by backup ID
            start_time: Filter by start time (Unix time)
            end_time: Filter by end time (Unix time)
            tags: Filter by tags
        
        Returns:
            List[RecoveryMetadata]: List of recovery metadata
        
        Raises:
            RecoveryError: If listing fails
        """
        try:
            results = []
            
            # List all metadata files
            for filename in os.listdir(self._recovery_metadata_path):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    # Read metadata
                    with open(os.path.join(self._recovery_metadata_path, filename), 'r') as f:
                        metadata_dict = json.load(f)
                    
                    metadata = RecoveryMetadata.from_dict(metadata_dict)
                    
                    # Apply filters
                    if owner and metadata.owner != owner:
                        continue
                    
                    if status and metadata.status != status:
                        continue
                    
                    if backup_id and metadata.backup_id != backup_id:
                        continue
                    
                    if start_time and metadata.created_at < start_time:
                        continue
                    
                    if end_time and metadata.created_at > end_time:
                        continue
                    
                    if tags:
                        match = True
                        for key, value in tags.items():
                            if key not in metadata.tags or metadata.tags[key] != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    results.append(metadata)
                
                except Exception as e:
                    logger.error(f"Error processing recovery metadata file {filename}: {str(e)}")
                    # Continue with next file
            
            # Sort by creation time (newest first)
            results.sort(key=lambda x: x.created_at, reverse=True)
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to list recoveries: {str(e)}")
            raise RecoveryError(f"Failed to list recoveries: {str(e)}")
    
    def create_backup_schedule(
        self,
        backup_type: BackupType,
        storage_type: StorageType,
        owner: str,
        source_path: Optional[str] = None,
        destination_path: Optional[str] = None,
        frequency: str = "daily",
        start_time: Optional[str] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> BackupSchedule:
        """
        Create a backup schedule.
        
        Args:
            backup_type: Type of backup
            storage_type: Type of storage to back up
            owner: Owner of the schedule
            source_path: Source path or pattern
            destination_path: Destination path
            frequency: Frequency of backups (daily, weekly, monthly)
            start_time: Start time in HH:MM format
            retention_period: Retention period in seconds
            tags: User-defined tags
        
        Returns:
            BackupSchedule: Backup schedule
        
        Raises:
            BackupError: If schedule creation fails
        """
        try:
            # Generate schedule ID
            schedule_id = str(uuid.uuid4())
            
            # Create schedule
            schedule = BackupSchedule(
                schedule_id=schedule_id,
                backup_type=backup_type,
                storage_type=storage_type,
                owner=owner,
                source_path=source_path,
                destination_path=destination_path,
                frequency=frequency,
                start_time=start_time,
                retention_period=retention_period,
                enabled=True,
                tags=tags
            )
            
            # Calculate next run time
            schedule.next_run = schedule.calculate_next_run()
            
            # Save schedule
            self._save_backup_schedule(schedule)
            
            logger.info(f"Backup schedule {schedule_id} created successfully")
            return schedule
        
        except Exception as e:
            logger.error(f"Failed to create backup schedule: {str(e)}")
            raise BackupError(f"Failed to create backup schedule: {str(e)}")
    
    def _save_backup_schedule(self, schedule: BackupSchedule) -> None:
        """
        Save backup schedule to disk.
        
        Args:
            schedule: Backup schedule
        """
        schedule_path = self._get_schedule_path(schedule.schedule_id)
        with open(schedule_path, 'w') as f:
            json.dump(schedule.to_dict(), f)
    
    def get_backup_schedule(self, schedule_id: str) -> BackupSchedule:
        """
        Get backup schedule.
        
        Args:
            schedule_id: Schedule ID
        
        Returns:
            BackupSchedule: Backup schedule
        
        Raises:
            BackupError: If schedule retrieval fails
        """
        try:
            schedule_path = self._get_schedule_path(schedule_id)
            
            if not os.path.exists(schedule_path):
                raise BackupError(f"Backup schedule {schedule_id} not found")
            
            with open(schedule_path, 'r') as f:
                schedule_dict = json.load(f)
            
            return BackupSchedule.from_dict(schedule_dict)
        
        except Exception as e:
            logger.error(f"Failed to get backup schedule: {str(e)}")
            raise BackupError(f"Failed to get backup schedule: {str(e)}")
    
    def list_backup_schedules(
        self,
        owner: Optional[str] = None,
        enabled: Optional[bool] = None,
        backup_type: Optional[BackupType] = None,
        storage_type: Optional[StorageType] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[BackupSchedule]:
        """
        List backup schedules with optional filtering.
        
        Args:
            owner: Filter by owner
            enabled: Filter by enabled status
            backup_type: Filter by backup type
            storage_type: Filter by storage type
            tags: Filter by tags
        
        Returns:
            List[BackupSchedule]: List of backup schedules
        
        Raises:
            BackupError: If listing fails
        """
        try:
            results = []
            
            # List all schedule files
            for filename in os.listdir(self._schedules_path):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    # Read schedule
                    with open(os.path.join(self._schedules_path, filename), 'r') as f:
                        schedule_dict = json.load(f)
                    
                    schedule = BackupSchedule.from_dict(schedule_dict)
                    
                    # Apply filters
                    if owner and schedule.owner != owner:
                        continue
                    
                    if enabled is not None and schedule.enabled != enabled:
                        continue
                    
                    if backup_type and schedule.backup_type != backup_type:
                        continue
                    
                    if storage_type and schedule.storage_type != storage_type:
                        continue
                    
                    if tags:
                        match = True
                        for key, value in tags.items():
                            if key not in schedule.tags or schedule.tags[key] != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    results.append(schedule)
                
                except Exception as e:
                    logger.error(f"Error processing schedule file {filename}: {str(e)}")
                    # Continue with next file
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to list backup schedules: {str(e)}")
            raise BackupError(f"Failed to list backup schedules: {str(e)}")
    
    def update_backup_schedule(
        self,
        schedule_id: str,
        owner: str,
        enabled: Optional[bool] = None,
        frequency: Optional[str] = None,
        start_time: Optional[str] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> BackupSchedule:
        """
        Update a backup schedule.
        
        Args:
            schedule_id: Schedule ID
            owner: Owner requesting update
            enabled: Whether the schedule is enabled
            frequency: Frequency of backups (daily, weekly, monthly)
            start_time: Start time in HH:MM format
            retention_period: Retention period in seconds
            tags: User-defined tags
        
        Returns:
            BackupSchedule: Updated backup schedule
        
        Raises:
            BackupError: If update fails
        """
        try:
            # Get schedule
            schedule = self.get_backup_schedule(schedule_id)
            
            # Check ownership
            if schedule.owner != owner and owner != "system":
                raise BackupError(f"Access denied: {owner} is not the owner of schedule {schedule_id}")
            
            # Update fields
            if enabled is not None:
                schedule.enabled = enabled
            
            if frequency is not None:
                schedule.frequency = frequency
            
            if start_time is not None:
                schedule.start_time = start_time
            
            if retention_period is not None:
                schedule.retention_period = retention_period
            
            if tags is not None:
                schedule.tags = tags
            
            # Recalculate next run time
            schedule.next_run = schedule.calculate_next_run()
            
            # Save updated schedule
            self._save_backup_schedule(schedule)
            
            logger.info(f"Backup schedule {schedule_id} updated successfully")
            return schedule
        
        except Exception as e:
            logger.error(f"Failed to update backup schedule: {str(e)}")
            raise BackupError(f"Failed to update backup schedule: {str(e)}")
    
    def delete_backup_schedule(self, schedule_id: str, owner: str) -> None:
        """
        Delete a backup schedule.
        
        Args:
            schedule_id: Schedule ID
            owner: Owner requesting deletion
        
        Raises:
            BackupError: If deletion fails
        """
        try:
            # Get schedule
            schedule = self.get_backup_schedule(schedule_id)
            
            # Check ownership
            if schedule.owner != owner and owner != "system":
                raise BackupError(f"Access denied: {owner} is not the owner of schedule {schedule_id}")
            
            # Delete schedule
            schedule_path = self._get_schedule_path(schedule_id)
            if os.path.exists(schedule_path):
                os.remove(schedule_path)
            
            logger.info(f"Backup schedule {schedule_id} deleted successfully")
        
        except Exception as e:
            logger.error(f"Failed to delete backup schedule: {str(e)}")
            raise BackupError(f"Failed to delete backup schedule: {str(e)}")
    
    def run_scheduled_backups(self) -> List[str]:
        """
        Run all scheduled backups that are due.
        
        Returns:
            List[str]: List of backup IDs that were started
        
        Raises:
            BackupError: If scheduling fails
        """
        try:
            now = int(time.time())
            backup_ids = []
            
            # List all schedules
            schedules = self.list_backup_schedules(enabled=True)
            
            for schedule in schedules:
                try:
                    # Check if schedule is due
                    if schedule.next_run and schedule.next_run <= now:
                        # Create backup
                        metadata = self.create_backup(
                            backup_type=schedule.backup_type,
                            storage_type=schedule.storage_type,
                            owner=schedule.owner,
                            source_path=schedule.source_path,
                            destination_path=schedule.destination_path,
                            retention_period=schedule.retention_period,
                            tags=schedule.tags,
                            async_operation=True
                        )
                        
                        backup_ids.append(metadata.backup_id)
                        
                        # Update schedule
                        schedule.last_run = now
                        schedule.next_run = schedule.calculate_next_run()
                        self._save_backup_schedule(schedule)
                
                except Exception as e:
                    logger.error(f"Failed to run scheduled backup {schedule.schedule_id}: {str(e)}")
                    # Continue with next schedule
            
            return backup_ids
        
        except Exception as e:
            logger.error(f"Failed to run scheduled backups: {str(e)}")
            raise BackupError(f"Failed to run scheduled backups: {str(e)}")
    
    def cleanup_expired_backups(self) -> List[str]:
        """
        Clean up expired backups.
        
        Returns:
            List[str]: List of backup IDs that were deleted
        
        Raises:
            BackupError: If cleanup fails
        """
        try:
            now = int(time.time())
            deleted_ids = []
            
            # List all backups
            backups = self.list_backups(status=BackupStatus.COMPLETED)
            
            for backup in backups:
                try:
                    # Check if backup has expired
                    if backup.retention_period and backup.created_at + backup.retention_period <= now:
                        # Delete backup
                        self.delete_backup(backup.backup_id, "system")
                        deleted_ids.append(backup.backup_id)
                
                except Exception as e:
                    logger.error(f"Failed to clean up backup {backup.backup_id}: {str(e)}")
                    # Continue with next backup
            
            return deleted_ids
        
        except Exception as e:
            logger.error(f"Failed to clean up expired backups: {str(e)}")
            raise BackupError(f"Failed to clean up expired backups: {str(e)}")
    
    def get_backup_status(self, backup_id: str) -> BackupStatus:
        """
        Get the status of a backup.
        
        Args:
            backup_id: Backup ID
        
        Returns:
            BackupStatus: Backup status
        
        Raises:
            BackupError: If status retrieval fails
        """
        try:
            # Check if backup is active
            if backup_id in self._active_backups:
                future = self._active_backups[backup_id]
                
                if future.done():
                    try:
                        # Get result and remove from active backups
                        metadata = future.result()
                        del self._active_backups[backup_id]
                        return metadata.status
                    except Exception:
                        # If there was an exception, assume failed
                        del self._active_backups[backup_id]
                        return BackupStatus.FAILED
                else:
                    # Still running
                    return BackupStatus.IN_PROGRESS
            
            # Get from metadata
            metadata = self.get_backup_metadata(backup_id)
            return metadata.status
        
        except Exception as e:
            logger.error(f"Failed to get backup status: {str(e)}")
            raise BackupError(f"Failed to get backup status: {str(e)}")
    
    def get_recovery_status(self, recovery_id: str) -> RecoveryStatus:
        """
        Get the status of a recovery.
        
        Args:
            recovery_id: Recovery ID
        
        Returns:
            RecoveryStatus: Recovery status
        
        Raises:
            RecoveryError: If status retrieval fails
        """
        try:
            # Check if recovery is active
            if recovery_id in self._active_recoveries:
                future = self._active_recoveries[recovery_id]
                
                if future.done():
                    try:
                        # Get result and remove from active recoveries
                        metadata = future.result()
                        del self._active_recoveries[recovery_id]
                        return metadata.status
                    except Exception:
                        # If there was an exception, assume failed
                        del self._active_recoveries[recovery_id]
                        return RecoveryStatus.FAILED
                else:
                    # Still running
                    return RecoveryStatus.IN_PROGRESS
            
            # Get from metadata
            metadata = self.get_recovery_metadata(recovery_id)
            return metadata.status
        
        except Exception as e:
            logger.error(f"Failed to get recovery status: {str(e)}")
            raise RecoveryError(f"Failed to get recovery status: {str(e)}")
    
    def abort_backup(self, backup_id: str, owner: str) -> None:
        """
        Abort a running backup.
        
        Args:
            backup_id: Backup ID
            owner: Owner requesting abort
        
        Raises:
            BackupError: If abort fails
        """
        try:
            # Get metadata
            metadata = self.get_backup_metadata(backup_id)
            
            # Check ownership
            if metadata.owner != owner and owner != "system":
                raise BackupError(f"Access denied: {owner} is not the owner of backup {backup_id}")
            
            # Check if backup is in progress
            if metadata.status != BackupStatus.IN_PROGRESS:
                raise BackupError(f"Cannot abort backup {backup_id} because it is not in progress")
            
            # Check if backup is active
            if backup_id in self._active_backups:
                future = self._active_backups[backup_id]
                
                if not future.done():
                    # Cancel future
                    future.cancel()
                
                # Remove from active backups
                del self._active_backups[backup_id]
            
            # Update metadata
            metadata.status = BackupStatus.ABORTED
            metadata.error_message = "Backup aborted by user"
            self._save_backup_metadata(metadata)
            
            logger.info(f"Backup {backup_id} aborted successfully")
        
        except Exception as e:
            logger.error(f"Failed to abort backup: {str(e)}")
            raise BackupError(f"Failed to abort backup: {str(e)}")
    
    def abort_recovery(self, recovery_id: str, owner: str) -> None:
        """
        Abort a running recovery.
        
        Args:
            recovery_id: Recovery ID
            owner: Owner requesting abort
        
        Raises:
            RecoveryError: If abort fails
        """
        try:
            # Get metadata
            metadata = self.get_recovery_metadata(recovery_id)
            
            # Check ownership
            if metadata.owner != owner and owner != "system":
                raise RecoveryError(f"Access denied: {owner} is not the owner of recovery {recovery_id}")
            
            # Check if recovery is in progress
            if metadata.status != RecoveryStatus.IN_PROGRESS:
                raise RecoveryError(f"Cannot abort recovery {recovery_id} because it is not in progress")
            
            # Check if recovery is active
            if recovery_id in self._active_recoveries:
                future = self._active_recoveries[recovery_id]
                
                if not future.done():
                    # Cancel future
                    future.cancel()
                
                # Remove from active recoveries
                del self._active_recoveries[recovery_id]
            
            # Update metadata
            metadata.status = RecoveryStatus.ABORTED
            metadata.error_message = "Recovery aborted by user"
            self._save_recovery_metadata(metadata)
            
            logger.info(f"Recovery {recovery_id} aborted successfully")
        
        except Exception as e:
            logger.error(f"Failed to abort recovery: {str(e)}")
            raise RecoveryError(f"Failed to abort recovery: {str(e)}")
