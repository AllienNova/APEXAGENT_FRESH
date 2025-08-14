"""
Encryption module for the Data Protection Framework.

This package provides encryption services for data in transit,
data at rest, and end-to-end message encryption.
"""

from .encryption_service import (
    EncryptionService,
    EncryptionContext,
    EncryptedData,
    EncryptionError,
    TransitEncryptionService,
    RestEncryptionService,
    MessageEncryptionService
)

__all__ = [
    'EncryptionService',
    'EncryptionContext',
    'EncryptedData',
    'EncryptionError',
    'TransitEncryptionService',
    'RestEncryptionService',
    'MessageEncryptionService'
]
