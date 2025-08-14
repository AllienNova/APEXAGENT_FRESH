"""
Cryptographic core module for the Data Protection Framework.

This package provides the foundational cryptographic operations used throughout
the Data Protection Framework, including symmetric and asymmetric encryption,
hashing, signatures, and secure random generation.
"""

from .crypto_core import (
    CryptoCore,
    EncryptionAlgorithm,
    AsymmetricAlgorithm,
    HashAlgorithm,
    KeyDerivationFunction,
    CryptoError,
    EncryptionError,
    DecryptionError,
    SignatureError,
    KeyGenerationError
)

__all__ = [
    'CryptoCore',
    'EncryptionAlgorithm',
    'AsymmetricAlgorithm',
    'HashAlgorithm',
    'KeyDerivationFunction',
    'CryptoError',
    'EncryptionError',
    'DecryptionError',
    'SignatureError',
    'KeyGenerationError'
]
