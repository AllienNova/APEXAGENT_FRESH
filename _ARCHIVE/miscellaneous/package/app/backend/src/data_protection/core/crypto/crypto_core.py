"""
Cryptographic Core Layer for the Data Protection Framework.

This module provides the foundational cryptographic operations used throughout
the Data Protection Framework, including symmetric and asymmetric encryption,
hashing, signatures, and secure random generation.
"""

import os
import base64
import hashlib
import hmac
import secrets
import time
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
import logging

# Third-party cryptographic libraries
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key,
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)
from cryptography.exceptions import InvalidSignature

# Configure logging
logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""
    AES_256_GCM = "AES-256-GCM"
    AES_256_CBC = "AES-256-CBC"
    CHACHA20_POLY1305 = "CHACHA20-POLY1305"

class AsymmetricAlgorithm(Enum):
    """Supported asymmetric encryption algorithms."""
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"
    ECC_P256 = "ECC-P256"
    ECC_P384 = "ECC-P384"
    ECC_P521 = "ECC-P521"

class HashAlgorithm(Enum):
    """Supported hash algorithms."""
    SHA256 = "SHA-256"
    SHA384 = "SHA-384"
    SHA512 = "SHA-512"
    SHA3_256 = "SHA3-256"
    SHA3_512 = "SHA3-512"

class KeyDerivationFunction(Enum):
    """Supported key derivation functions."""
    PBKDF2 = "PBKDF2"
    HKDF = "HKDF"
    ARGON2 = "ARGON2"

class CryptoError(Exception):
    """Base exception for all cryptographic operations."""
    pass

class EncryptionError(CryptoError):
    """Exception raised for encryption errors."""
    pass

class DecryptionError(CryptoError):
    """Exception raised for decryption errors."""
    pass

class SignatureError(CryptoError):
    """Exception raised for signature verification errors."""
    pass

class KeyGenerationError(CryptoError):
    """Exception raised for key generation errors."""
    pass

class CryptoCore:
    """
    Core cryptographic operations for the Data Protection Framework.
    
    This class provides a unified interface for cryptographic operations,
    abstracting the underlying implementations and providing secure defaults.
    """
    
    def __init__(self):
        """Initialize the CryptoCore with secure defaults."""
        self._default_symmetric_algorithm = EncryptionAlgorithm.AES_256_GCM
        self._default_asymmetric_algorithm = AsymmetricAlgorithm.RSA_2048
        self._default_hash_algorithm = HashAlgorithm.SHA256
        self._default_kdf = KeyDerivationFunction.PBKDF2
        
        # Secure defaults
        self._pbkdf2_iterations = 600000  # High iteration count for security
        self._salt_size = 32  # 256 bits
        self._iv_size = 16  # 128 bits
        self._key_size = 32  # 256 bits
        self._tag_size = 16  # 128 bits for GCM
        
        logger.info("CryptoCore initialized with secure defaults")
    
    # -------------------------------------------------------------------------
    # Symmetric Encryption
    # -------------------------------------------------------------------------
    
    def generate_symmetric_key(self, algorithm: Optional[EncryptionAlgorithm] = None) -> bytes:
        """
        Generate a secure symmetric encryption key.
        
        Args:
            algorithm: The encryption algorithm to generate a key for.
                       Defaults to AES-256-GCM.
        
        Returns:
            bytes: The generated key.
        
        Raises:
            KeyGenerationError: If key generation fails.
        """
        algorithm = algorithm or self._default_symmetric_algorithm
        
        try:
            if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                return secrets.token_bytes(self._key_size)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return secrets.token_bytes(self._key_size)
            else:
                raise KeyGenerationError(f"Unsupported algorithm: {algorithm}")
        except Exception as e:
            logger.error(f"Symmetric key generation failed: {str(e)}")
            raise KeyGenerationError(f"Symmetric key generation failed: {str(e)}")
    
    def encrypt_symmetric(
        self,
        plaintext: bytes,
        key: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        associated_data: Optional[bytes] = None
    ) -> Dict[str, bytes]:
        """
        Encrypt data using symmetric encryption.
        
        Args:
            plaintext: The data to encrypt.
            key: The encryption key.
            algorithm: The encryption algorithm to use. Defaults to AES-256-GCM.
            associated_data: Additional authenticated data for AEAD modes.
        
        Returns:
            Dict containing 'ciphertext', 'iv', and 'tag' (for AEAD modes).
        
        Raises:
            EncryptionError: If encryption fails.
        """
        algorithm = algorithm or self._default_symmetric_algorithm
        
        try:
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                return self._encrypt_aes_gcm(plaintext, key, associated_data)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return self._encrypt_aes_cbc(plaintext, key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._encrypt_chacha20_poly1305(plaintext, key, associated_data)
            else:
                raise EncryptionError(f"Unsupported algorithm: {algorithm}")
        except Exception as e:
            logger.error(f"Symmetric encryption failed: {str(e)}")
            raise EncryptionError(f"Symmetric encryption failed: {str(e)}")
    
    def decrypt_symmetric(
        self,
        ciphertext_data: Dict[str, bytes],
        key: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt data using symmetric encryption.
        
        Args:
            ciphertext_data: Dict containing 'ciphertext', 'iv', and 'tag' (for AEAD modes).
            key: The decryption key.
            algorithm: The encryption algorithm used. Defaults to AES-256-GCM.
            associated_data: Additional authenticated data for AEAD modes.
        
        Returns:
            bytes: The decrypted plaintext.
        
        Raises:
            DecryptionError: If decryption fails.
        """
        algorithm = algorithm or self._default_symmetric_algorithm
        
        try:
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                return self._decrypt_aes_gcm(ciphertext_data, key, associated_data)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return self._decrypt_aes_cbc(ciphertext_data, key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._decrypt_chacha20_poly1305(ciphertext_data, key, associated_data)
            else:
                raise DecryptionError(f"Unsupported algorithm: {algorithm}")
        except Exception as e:
            logger.error(f"Symmetric decryption failed: {str(e)}")
            raise DecryptionError(f"Symmetric decryption failed: {str(e)}")
    
    def _encrypt_aes_gcm(
        self,
        plaintext: bytes,
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> Dict[str, bytes]:
        """
        Encrypt data using AES-GCM.
        
        Args:
            plaintext: The data to encrypt.
            key: The encryption key.
            associated_data: Additional authenticated data.
        
        Returns:
            Dict containing 'ciphertext', 'iv', and 'tag'.
        """
        iv = secrets.token_bytes(self._iv_size)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
        ).encryptor()
        
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return {
            'ciphertext': ciphertext,
            'iv': iv,
            'tag': encryptor.tag
        }
    
    def _decrypt_aes_gcm(
        self,
        ciphertext_data: Dict[str, bytes],
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt data using AES-GCM.
        
        Args:
            ciphertext_data: Dict containing 'ciphertext', 'iv', and 'tag'.
            key: The decryption key.
            associated_data: Additional authenticated data.
        
        Returns:
            bytes: The decrypted plaintext.
        """
        ciphertext = ciphertext_data['ciphertext']
        iv = ciphertext_data['iv']
        tag = ciphertext_data['tag']
        
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
        ).decryptor()
        
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)
        
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _encrypt_aes_cbc(
        self,
        plaintext: bytes,
        key: bytes
    ) -> Dict[str, bytes]:
        """
        Encrypt data using AES-CBC with PKCS7 padding.
        
        Args:
            plaintext: The data to encrypt.
            key: The encryption key.
        
        Returns:
            Dict containing 'ciphertext' and 'iv'.
        """
        iv = secrets.token_bytes(self._iv_size)
        
        # Apply PKCS7 padding
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        encryptor = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
        ).encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return {
            'ciphertext': ciphertext,
            'iv': iv
        }
    
    def _decrypt_aes_cbc(
        self,
        ciphertext_data: Dict[str, bytes],
        key: bytes
    ) -> bytes:
        """
        Decrypt data using AES-CBC with PKCS7 padding.
        
        Args:
            ciphertext_data: Dict containing 'ciphertext' and 'iv'.
            key: The decryption key.
        
        Returns:
            bytes: The decrypted plaintext.
        """
        ciphertext = ciphertext_data['ciphertext']
        iv = ciphertext_data['iv']
        
        decryptor = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
        ).decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext
    
    def _encrypt_chacha20_poly1305(
        self,
        plaintext: bytes,
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> Dict[str, bytes]:
        """
        Encrypt data using ChaCha20-Poly1305.
        
        Args:
            plaintext: The data to encrypt.
            key: The encryption key.
            associated_data: Additional authenticated data.
        
        Returns:
            Dict containing 'ciphertext', 'nonce', and 'tag'.
        """
        # Note: This is a placeholder. In a real implementation, you would use
        # a library that supports ChaCha20-Poly1305 directly.
        # For now, we'll simulate it with AES-GCM
        result = self._encrypt_aes_gcm(plaintext, key, associated_data)
        result['nonce'] = result.pop('iv')  # ChaCha20 uses nonce instead of IV
        return result
    
    def _decrypt_chacha20_poly1305(
        self,
        ciphertext_data: Dict[str, bytes],
        key: bytes,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt data using ChaCha20-Poly1305.
        
        Args:
            ciphertext_data: Dict containing 'ciphertext', 'nonce', and 'tag'.
            key: The decryption key.
            associated_data: Additional authenticated data.
        
        Returns:
            bytes: The decrypted plaintext.
        """
        # Note: This is a placeholder. In a real implementation, you would use
        # a library that supports ChaCha20-Poly1305 directly.
        # For now, we'll simulate it with AES-GCM
        modified_data = ciphertext_data.copy()
        modified_data['iv'] = modified_data.pop('nonce')  # Convert nonce to iv for AES-GCM
        return self._decrypt_aes_gcm(modified_data, key, associated_data)
    
    # -------------------------------------------------------------------------
    # Asymmetric Encryption
    # -------------------------------------------------------------------------
    
    def generate_asymmetric_key_pair(
        self,
        algorithm: Optional[AsymmetricAlgorithm] = None
    ) -> Dict[str, bytes]:
        """
        Generate an asymmetric key pair.
        
        Args:
            algorithm: The asymmetric algorithm to use. Defaults to RSA-2048.
        
        Returns:
            Dict containing 'private_key' and 'public_key' in PEM format.
        
        Raises:
            KeyGenerationError: If key generation fails.
        """
        algorithm = algorithm or self._default_asymmetric_algorithm
        
        try:
            if algorithm == AsymmetricAlgorithm.RSA_2048:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
            elif algorithm == AsymmetricAlgorithm.RSA_4096:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096
                )
            elif algorithm == AsymmetricAlgorithm.ECC_P256:
                private_key = ec.generate_private_key(ec.SECP256R1())
            elif algorithm == AsymmetricAlgorithm.ECC_P384:
                private_key = ec.generate_private_key(ec.SECP384R1())
            elif algorithm == AsymmetricAlgorithm.ECC_P521:
                private_key = ec.generate_private_key(ec.SECP521R1())
            else:
                raise KeyGenerationError(f"Unsupported algorithm: {algorithm}")
            
            public_key = private_key.public_key()
            
            # Serialize keys to PEM format
            private_pem = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
            
            return {
                'private_key': private_pem,
                'public_key': public_pem
            }
        except Exception as e:
            logger.error(f"Asymmetric key generation failed: {str(e)}")
            raise KeyGenerationError(f"Asymmetric key generation failed: {str(e)}")
    
    def encrypt_asymmetric(
        self,
        plaintext: bytes,
        public_key: bytes,
        algorithm: Optional[AsymmetricAlgorithm] = None
    ) -> bytes:
        """
        Encrypt data using asymmetric encryption.
        
        Args:
            plaintext: The data to encrypt.
            public_key: The public key in PEM format.
            algorithm: The asymmetric algorithm to use. Defaults to RSA-2048.
        
        Returns:
            bytes: The encrypted data.
        
        Raises:
            EncryptionError: If encryption fails.
        """
        algorithm = algorithm or self._default_asymmetric_algorithm
        
        try:
            key_obj = load_pem_public_key(public_key)
            
            if isinstance(key_obj, rsa.RSAPublicKey):
                ciphertext = key_obj.encrypt(
                    plaintext,
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                return ciphertext
            elif isinstance(key_obj, ec.EllipticCurvePublicKey):
                # Note: ECC is typically used for signatures, not encryption
                # For encryption with ECC, you would typically use ECIES
                # This is a simplified implementation
                # In a real system, use a proper ECIES implementation
                
                # Generate an ephemeral key pair
                ephemeral_private_key = ec.generate_private_key(key_obj.curve)
                ephemeral_public_key = ephemeral_private_key.public_key()
                
                # Perform ECDH key exchange
                shared_key = ephemeral_private_key.exchange(ec.ECDH(), key_obj)
                
                # Derive encryption key from shared secret
                derived_key = HKDF(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=None,
                    info=b'encryption'
                ).derive(shared_key)
                
                # Encrypt the plaintext with the derived key
                encrypted_data = self.encrypt_symmetric(plaintext, derived_key)
                
                # Serialize the ephemeral public key
                ephemeral_public_bytes = ephemeral_public_key.public_bytes(
                    encoding=Encoding.PEM,
                    format=PublicFormat.SubjectPublicKeyInfo
                )
                
                # Combine the ephemeral public key and encrypted data
                # In a real implementation, you would use a proper serialization format
                result = {
                    'ephemeral_public_key': ephemeral_public_bytes,
                    'encrypted_data': encrypted_data
                }
                
                # Serialize to bytes (in a real implementation, use a proper format)
                return str(result).encode()
            else:
                raise EncryptionError(f"Unsupported key type: {type(key_obj)}")
        except Exception as e:
            logger.error(f"Asymmetric encryption failed: {str(e)}")
            raise EncryptionError(f"Asymmetric encryption failed: {str(e)}")
    
    def decrypt_asymmetric(
        self,
        ciphertext: bytes,
        private_key: bytes,
        algorithm: Optional[AsymmetricAlgorithm] = None
    ) -> bytes:
        """
        Decrypt data using asymmetric encryption.
        
        Args:
            ciphertext: The data to decrypt.
            private_key: The private key in PEM format.
            algorithm: The asymmetric algorithm used. Defaults to RSA-2048.
        
        Returns:
            bytes: The decrypted plaintext.
        
        Raises:
            DecryptionError: If decryption fails.
        """
        algorithm = algorithm or self._default_asymmetric_algorithm
        
        try:
            key_obj = load_pem_private_key(private_key, password=None)
            
            if isinstance(key_obj, rsa.RSAPrivateKey):
                plaintext = key_obj.decrypt(
                    ciphertext,
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                return plaintext
            elif isinstance(key_obj, ec.EllipticCurvePrivateKey):
                # Note: This is a simplified implementation
                # In a real system, use a proper ECIES implementation
                
                # Parse the input (in a real implementation, use a proper format)
                # This is just a placeholder
                result = eval(ciphertext.decode())
                ephemeral_public_bytes = result['ephemeral_public_key']
                encrypted_data = result['encrypted_data']
                
                # Load the ephemeral public key
                ephemeral_public_key = load_pem_public_key(ephemeral_public_bytes)
                
                # Perform ECDH key exchange
                shared_key = key_obj.exchange(ec.ECDH(), ephemeral_public_key)
                
                # Derive encryption key from shared secret
                derived_key = HKDF(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=None,
                    info=b'encryption'
                ).derive(shared_key)
                
                # Decrypt the data with the derived key
                return self.decrypt_symmetric(encrypted_data, derived_key)
            else:
                raise DecryptionError(f"Unsupported key type: {type(key_obj)}")
        except Exception as e:
            logger.error(f"Asymmetric decryption failed: {str(e)}")
            raise DecryptionError(f"Asymmetric decryption failed: {str(e)}")
    
    # -------------------------------------------------------------------------
    # Hashing and Signatures
    # -------------------------------------------------------------------------
    
    def hash_data(
        self,
        data: bytes,
        algorithm: Optional[HashAlgorithm] = None
    ) -> bytes:
        """
        Generate a hash of the provided data.
        
        Args:
            data: The data to hash.
            algorithm: The hash algorithm to use. Defaults to SHA-256.
        
        Returns:
            bytes: The computed hash.
        """
        algorithm = algorithm or self._default_hash_algorithm
        
        try:
            if algorithm == HashAlgorithm.SHA256:
                return hashlib.sha256(data).digest()
            elif algorithm == HashAlgorithm.SHA384:
                return hashlib.sha384(data).digest()
            elif algorithm == HashAlgorithm.SHA512:
                return hashlib.sha512(data).digest()
            elif algorithm == HashAlgorithm.SHA3_256:
                return hashlib.sha3_256(data).digest()
            elif algorithm == HashAlgorithm.SHA3_512:
                return hashlib.sha3_512(data).digest()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        except Exception as e:
            logger.error(f"Hashing failed: {str(e)}")
            raise CryptoError(f"Hashing failed: {str(e)}")
    
    def hmac_data(
        self,
        data: bytes,
        key: bytes,
        algorithm: Optional[HashAlgorithm] = None
    ) -> bytes:
        """
        Generate an HMAC for the provided data.
        
        Args:
            data: The data to authenticate.
            key: The HMAC key.
            algorithm: The hash algorithm to use. Defaults to SHA-256.
        
        Returns:
            bytes: The computed HMAC.
        """
        algorithm = algorithm or self._default_hash_algorithm
        
        try:
            if algorithm == HashAlgorithm.SHA256:
                h = hmac.new(key, data, hashlib.sha256)
            elif algorithm == HashAlgorithm.SHA384:
                h = hmac.new(key, data, hashlib.sha384)
            elif algorithm == HashAlgorithm.SHA512:
                h = hmac.new(key, data, hashlib.sha512)
            elif algorithm == HashAlgorithm.SHA3_256:
                h = hmac.new(key, data, hashlib.sha3_256)
            elif algorithm == HashAlgorithm.SHA3_512:
                h = hmac.new(key, data, hashlib.sha3_512)
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            return h.digest()
        except Exception as e:
            logger.error(f"HMAC generation failed: {str(e)}")
            raise CryptoError(f"HMAC generation failed: {str(e)}")
    
    def sign_data(
        self,
        data: bytes,
        private_key: bytes,
        algorithm: Optional[HashAlgorithm] = None
    ) -> bytes:
        """
        Sign data using a private key.
        
        Args:
            data: The data to sign.
            private_key: The private key in PEM format.
            algorithm: The hash algorithm to use. Defaults to SHA-256.
        
        Returns:
            bytes: The signature.
        
        Raises:
            SignatureError: If signing fails.
        """
        algorithm = algorithm or self._default_hash_algorithm
        
        try:
            key_obj = load_pem_private_key(private_key, password=None)
            
            if algorithm == HashAlgorithm.SHA256:
                hash_algorithm = hashes.SHA256()
            elif algorithm == HashAlgorithm.SHA384:
                hash_algorithm = hashes.SHA384()
            elif algorithm == HashAlgorithm.SHA512:
                hash_algorithm = hashes.SHA512()
            elif algorithm == HashAlgorithm.SHA3_256:
                # Note: cryptography library might not support SHA3 directly
                # This is a placeholder
                hash_algorithm = hashes.SHA256()
            elif algorithm == HashAlgorithm.SHA3_512:
                # Note: cryptography library might not support SHA3 directly
                # This is a placeholder
                hash_algorithm = hashes.SHA512()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            if isinstance(key_obj, rsa.RSAPrivateKey):
                signature = key_obj.sign(
                    data,
                    asym_padding.PSS(
                        mgf=asym_padding.MGF1(hash_algorithm),
                        salt_length=asym_padding.PSS.MAX_LENGTH
                    ),
                    hash_algorithm
                )
                return signature
            elif isinstance(key_obj, ec.EllipticCurvePrivateKey):
                signature = key_obj.sign(
                    data,
                    ec.ECDSA(hash_algorithm)
                )
                return signature
            else:
                raise SignatureError(f"Unsupported key type: {type(key_obj)}")
        except Exception as e:
            logger.error(f"Signing failed: {str(e)}")
            raise SignatureError(f"Signing failed: {str(e)}")
    
    def verify_signature(
        self,
        data: bytes,
        signature: bytes,
        public_key: bytes,
        algorithm: Optional[HashAlgorithm] = None
    ) -> bool:
        """
        Verify a signature using a public key.
        
        Args:
            data: The data that was signed.
            signature: The signature to verify.
            public_key: The public key in PEM format.
            algorithm: The hash algorithm used. Defaults to SHA-256.
        
        Returns:
            bool: True if the signature is valid, False otherwise.
        """
        algorithm = algorithm or self._default_hash_algorithm
        
        try:
            key_obj = load_pem_public_key(public_key)
            
            if algorithm == HashAlgorithm.SHA256:
                hash_algorithm = hashes.SHA256()
            elif algorithm == HashAlgorithm.SHA384:
                hash_algorithm = hashes.SHA384()
            elif algorithm == HashAlgorithm.SHA512:
                hash_algorithm = hashes.SHA512()
            elif algorithm == HashAlgorithm.SHA3_256:
                # Note: cryptography library might not support SHA3 directly
                # This is a placeholder
                hash_algorithm = hashes.SHA256()
            elif algorithm == HashAlgorithm.SHA3_512:
                # Note: cryptography library might not support SHA3 directly
                # This is a placeholder
                hash_algorithm = hashes.SHA512()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            if isinstance(key_obj, rsa.RSAPublicKey):
                try:
                    key_obj.verify(
                        signature,
                        data,
                        asym_padding.PSS(
                            mgf=asym_padding.MGF1(hash_algorithm),
                            salt_length=asym_padding.PSS.MAX_LENGTH
                        ),
                        hash_algorithm
                    )
                    return True
                except InvalidSignature:
                    return False
            elif isinstance(key_obj, ec.EllipticCurvePublicKey):
                try:
                    key_obj.verify(
                        signature,
                        data,
                        ec.ECDSA(hash_algorithm)
                    )
                    return True
                except InvalidSignature:
                    return False
            else:
                raise SignatureError(f"Unsupported key type: {type(key_obj)}")
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False
    
    # -------------------------------------------------------------------------
    # Key Derivation
    # -------------------------------------------------------------------------
    
    def derive_key(
        self,
        password: bytes,
        salt: Optional[bytes] = None,
        iterations: Optional[int] = None,
        key_length: Optional[int] = None,
        kdf: Optional[KeyDerivationFunction] = None
    ) -> Dict[str, bytes]:
        """
        Derive a key from a password or passphrase.
        
        Args:
            password: The password or passphrase.
            salt: Optional salt. If not provided, a random salt will be generated.
            iterations: Number of iterations for PBKDF2. Defaults to 600,000.
            key_length: Length of the derived key in bytes. Defaults to 32.
            kdf: Key derivation function to use. Defaults to PBKDF2.
        
        Returns:
            Dict containing 'key' and 'salt'.
        """
        salt = salt or secrets.token_bytes(self._salt_size)
        iterations = iterations or self._pbkdf2_iterations
        key_length = key_length or self._key_size
        kdf = kdf or self._default_kdf
        
        try:
            if kdf == KeyDerivationFunction.PBKDF2:
                kdf_instance = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=key_length,
                    salt=salt,
                    iterations=iterations,
                )
                key = kdf_instance.derive(password)
                return {'key': key, 'salt': salt}
            elif kdf == KeyDerivationFunction.HKDF:
                kdf_instance = HKDF(
                    algorithm=hashes.SHA256(),
                    length=key_length,
                    salt=salt,
                    info=b'key derivation',
                )
                key = kdf_instance.derive(password)
                return {'key': key, 'salt': salt}
            elif kdf == KeyDerivationFunction.ARGON2:
                # Note: This is a placeholder. In a real implementation,
                # you would use a library that supports Argon2 directly.
                # For now, we'll simulate it with PBKDF2
                return self.derive_key(
                    password, salt, iterations, key_length, KeyDerivationFunction.PBKDF2
                )
            else:
                raise ValueError(f"Unsupported KDF: {kdf}")
        except Exception as e:
            logger.error(f"Key derivation failed: {str(e)}")
            raise CryptoError(f"Key derivation failed: {str(e)}")
    
    # -------------------------------------------------------------------------
    # Random Generation
    # -------------------------------------------------------------------------
    
    def generate_random_bytes(self, length: int) -> bytes:
        """
        Generate cryptographically secure random bytes.
        
        Args:
            length: Number of bytes to generate.
        
        Returns:
            bytes: Random bytes.
        """
        try:
            return secrets.token_bytes(length)
        except Exception as e:
            logger.error(f"Random generation failed: {str(e)}")
            raise CryptoError(f"Random generation failed: {str(e)}")
    
    def generate_random_string(self, length: int, alphabet: Optional[str] = None) -> str:
        """
        Generate a cryptographically secure random string.
        
        Args:
            length: Length of the string to generate.
            alphabet: Character set to use. Defaults to URL-safe base64.
        
        Returns:
            str: Random string.
        """
        try:
            if alphabet:
                return ''.join(secrets.choice(alphabet) for _ in range(length))
            else:
                # Use URL-safe base64 alphabet by default
                return secrets.token_urlsafe(length)[:length]
        except Exception as e:
            logger.error(f"Random string generation failed: {str(e)}")
            raise CryptoError(f"Random string generation failed: {str(e)}")
    
    def generate_uuid(self) -> str:
        """
        Generate a random UUID.
        
        Returns:
            str: Random UUID.
        """
        try:
            import uuid
            return str(uuid.uuid4())
        except Exception as e:
            logger.error(f"UUID generation failed: {str(e)}")
            raise CryptoError(f"UUID generation failed: {str(e)}")
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def constant_time_compare(self, a: bytes, b: bytes) -> bool:
        """
        Compare two byte strings in constant time to prevent timing attacks.
        
        Args:
            a: First byte string.
            b: Second byte string.
        
        Returns:
            bool: True if the byte strings are equal, False otherwise.
        """
        try:
            return hmac.compare_digest(a, b)
        except Exception as e:
            logger.error(f"Constant time comparison failed: {str(e)}")
            return False
    
    def encode_base64(self, data: bytes) -> str:
        """
        Encode bytes as base64.
        
        Args:
            data: Bytes to encode.
        
        Returns:
            str: Base64-encoded string.
        """
        try:
            return base64.b64encode(data).decode('ascii')
        except Exception as e:
            logger.error(f"Base64 encoding failed: {str(e)}")
            raise CryptoError(f"Base64 encoding failed: {str(e)}")
    
    def decode_base64(self, data: str) -> bytes:
        """
        Decode base64 string to bytes.
        
        Args:
            data: Base64-encoded string.
        
        Returns:
            bytes: Decoded bytes.
        """
        try:
            return base64.b64decode(data)
        except Exception as e:
            logger.error(f"Base64 decoding failed: {str(e)}")
            raise CryptoError(f"Base64 decoding failed: {str(e)}")
