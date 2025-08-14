"""
Backup module for the Data Protection Framework.

This package provides comprehensive backup and recovery capabilities,
including scheduled backups, incremental backups, point-in-time recovery,
and disaster recovery.
"""

from .backup_recovery import (
    BackupType,
    BackupStatus,
    RecoveryStatus,
    BackupError,
    RecoveryError,
    BackupMetadata,
    RecoveryMetadata,
    BackupSchedule,
    BackupService
)

__all__ = [
    'BackupType',
    'BackupStatus',
    'RecoveryStatus',
    'BackupError',
    'RecoveryError',
    'BackupMetadata',
    'RecoveryMetadata',
    'BackupSchedule',
    'BackupService'
]
