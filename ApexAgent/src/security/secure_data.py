"""
Secure Data Handling with Encryption for Dr. TARDIS.

This module provides comprehensive encryption capabilities for secure data handling
in the Dr. TARDIS system, including symmetric and asymmetric encryption, key management,
and secure storage mechanisms.

Author: Manus Agent
Date: May 26, 2025
"""

import base64
import json
import os
import secrets
import time
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.security import SecurityLevel, DataCategory


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""
    AES_256_GCM = "AES-256-GCM"
    AES_256_CBC = "AES-256-CBC"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"


class KeyType(Enum):
    """Types of encryption keys."""
    MASTER = "master"
    DATA = "data"
    SESSION = "session"
    USER = "user"
    BACKUP = "backup"


class SecureDataManager:
    """
    Manages secure data handling with encryption for Dr. TARDIS.
    
    This class provides comprehensive encryption capabilities including:
    - Symmetric and asymmetric encryption
    - Key management with rotation
    - Secure storage with integrity verification
    - Data categorization and security level enforcement
    """
    
    def __init__(self, keys_dir: Optional[Path] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SecureDataManager.
        
        Args:
            keys_dir: Directory for storing encryption keys
            config: Configuration options for the secure data manager
        """
        self.keys_dir = keys_dir or Path("/tmp/dr_tardis_keys")
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.config = {
            "key_rotation_days": 30,
            "default_algorithm": EncryptionAlgorithm.AES_256_GCM,
            "min_password_length": 12,
            "pbkdf2_iterations": 100000,
            "rsa_key_size": 4096,
            "secure_storage_dir": Path("/tmp/dr_tardis_secure_storage")
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        # Initialize key storage
        self.keys = {}
        self._old_keys = {}  # Store old keys for backward compatibility
        self.load_or_generate_keys()
        
        # Initialize secure storage directory
        self.secure_storage_dir = self.config["secure_storage_dir"]
        self.secure_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger("dr_tardis.security.secure_data")
    
    def load_or_generate_keys(self) -> None:
        """Load existing keys or generate new ones if they don't exist."""
        master_key_path = self.keys_dir / "master.key"
        
        if master_key_path.exists():
            # Load master key
            with open(master_key_path, "rb") as f:
                master_key_data = json.loads(f.read())
                self.keys[KeyType.MASTER] = {
                    "key": base64.b64decode(master_key_data["key"]),
                    "created": datetime.fromisoformat(master_key_data["created"]),
                    "algorithm": EncryptionAlgorithm(master_key_data["algorithm"]),
                }
        else:
            # Generate new master key
            self.generate_key(KeyType.MASTER)
    
    def generate_key(self, key_type: KeyType, algorithm: Optional[EncryptionAlgorithm] = None) -> bytes:
        """
        Generate a new encryption key.
        
        Args:
            key_type: Type of key to generate
            algorithm: Encryption algorithm to use
            
        Returns:
            The generated key
        """
        algorithm = algorithm or self.config["default_algorithm"]
        
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC, 
                         EncryptionAlgorithm.CHACHA20_POLY1305]:
            # Generate symmetric key
            key = Fernet.generate_key()
        elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            # Generate asymmetric key pair
            key_size = 2048 if algorithm == EncryptionAlgorithm.RSA_2048 else 4096
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
        
        # Store the key
        self.keys[key_type] = {
            "key": key,
            "created": datetime.now(),
            "algorithm": algorithm,
        }
        
        # Save to disk if it's a persistent key
        if key_type in [KeyType.MASTER, KeyType.DATA, KeyType.BACKUP]:
            key_path = self.keys_dir / f"{key_type.value}.key"
            with open(key_path, "w") as f:
                key_data = {
                    "key": base64.b64encode(key).decode("utf-8"),
                    "created": self.keys[key_type]["created"].isoformat(),
                    "algorithm": self.keys[key_type]["algorithm"].value,
                }
                f.write(json.dumps(key_data))
        
        return key
    
    def rotate_encryption_keys(self, key_types: Optional[List[KeyType]] = None) -> Dict[KeyType, bytes]:
        """
        Rotate encryption keys while maintaining backward compatibility.
        
        Args:
            key_types: List of key types to rotate, or None for all keys
            
        Returns:
            Dictionary of rotated keys
        """
        # Store old keys for backward compatibility before rotation
        for key_type in self.keys:
            self._old_keys[key_type] = {
                "key": self.keys[key_type]["key"],
                "algorithm": self.keys[key_type]["algorithm"],
                "created": self.keys[key_type]["created"]
            }
        
        # Perform key rotation
        rotated_keys = self.rotate_keys(key_types)
        
        return rotated_keys
    
    def rotate_keys(self, key_types: Optional[List[KeyType]] = None) -> Dict[KeyType, bytes]:
        """
        Rotate encryption keys.
        
        Args:
            key_types: List of key types to rotate, or None for all keys
            
        Returns:
            Dictionary of rotated keys
        """
        key_types = key_types or [k for k in self.keys.keys()]
        rotated_keys = {}
        
        for key_type in key_types:
            if key_type in self.keys:
                # Save old key for re-encryption
                old_key = self.keys[key_type]["key"]
                old_algorithm = self.keys[key_type]["algorithm"]
                
                # Generate new key
                new_key = self.generate_key(key_type, old_algorithm)
                
                # Re-encrypt data if needed
                if key_type in [KeyType.DATA, KeyType.USER]:
                    self.re_encrypt_data(key_type, old_key, new_key)
                
                rotated_keys[key_type] = new_key
        
        return rotated_keys
    
    def re_encrypt_data(self, key_type: KeyType, old_key: bytes, new_key: bytes) -> None:
        """
        Re-encrypt data after key rotation.
        
        Args:
            key_type: Type of key being rotated
            old_key: Previous encryption key
            new_key: New encryption key
        """
        # Get the data storage directory for this key type
        data_dir = self.keys_dir / f"{key_type.value}_data"
        if not data_dir.exists():
            return  # No data to re-encrypt
            
        # Create Fernet instances for old and new keys
        old_fernet = Fernet(old_key)
        new_fernet = Fernet(new_key)
        
        # Process all encrypted files in the directory
        for file_path in data_dir.glob("*.encrypted"):
            try:
                # Read encrypted data
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                
                # Decrypt with old key
                try:
                    decrypted_data = old_fernet.decrypt(encrypted_data)
                except cryptography.fernet.InvalidToken:
                    self.logger.error(f"Failed to decrypt {file_path} with old key")
                    continue
                
                # Re-encrypt with new key
                new_encrypted_data = new_fernet.encrypt(decrypted_data)
                
                # Write back to file
                with open(file_path, "wb") as f:
                    f.write(new_encrypted_data)
                    
                self.logger.info(f"Successfully re-encrypted {file_path}")
                
            except Exception as e:
                self.logger.error(f"Error re-encrypting {file_path}: {e}")
                
        # Update metadata files to reference new key
        metadata_file = self.keys_dir / f"{key_type.value}_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                
                # Update key reference
                if "key_id" in metadata:
                    metadata["previous_key_id"] = metadata["key_id"]
                metadata["key_id"] = secrets.token_hex(8)
                metadata["key_updated"] = datetime.now().isoformat()
                
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f)
            except Exception as e:
                self.logger.error(f"Error updating metadata file: {e}")
    
    def encrypt_data(self, data: Union[str, bytes], security_level: Optional[SecurityLevel] = None, 
                    data_category: Optional[DataCategory] = None, key_type: Optional[KeyType] = None) -> Dict[str, Any]:
        """
        Encrypt data with appropriate security level and categorization.
        
        Args:
            data: Data to encrypt
            security_level: Security level of the data (optional, defaults to MEDIUM)
            data_category: Category of the data (optional, defaults to GENERAL)
            key_type: Type of key to use for encryption
            
        Returns:
            Dictionary containing encrypted data and metadata
        """
        # Set default values if not provided
        security_level = security_level or SecurityLevel.MEDIUM
        data_category = data_category or DataCategory.GENERAL
        
        # Convert string to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data
        
        # Determine key to use
        key_type = key_type or KeyType.DATA
        if key_type not in self.keys:
            self.generate_key(key_type)
        
        key = self.keys[key_type]["key"]
        algorithm = self.keys[key_type]["algorithm"]
        
        # Encrypt based on algorithm
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC, 
                         EncryptionAlgorithm.CHACHA20_POLY1305]:
            # Symmetric encryption
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data_bytes)
        elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            # Asymmetric encryption
            # For simplicity, we're using a hybrid approach for larger data
            # Generate a one-time symmetric key
            symmetric_key = Fernet.generate_key()
            fernet = Fernet(symmetric_key)
            
            # Encrypt data with symmetric key
            encrypted_data = fernet.encrypt(data_bytes)
            
            # Load the RSA public key
            private_key = serialization.load_pem_private_key(
                key,
                password=None,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # Encrypt the symmetric key with RSA
            encrypted_symmetric_key = public_key.encrypt(
                symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Combine encrypted key and data
            encrypted_data = base64.b64encode(json.dumps({
                "key": base64.b64encode(encrypted_symmetric_key).decode("utf-8"),
                "data": base64.b64encode(encrypted_data).decode("utf-8")
            }).encode("utf-8"))
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
        
        # Create metadata
        metadata = {
            "encrypted": True,
            "timestamp": datetime.now().isoformat(),
            "algorithm": algorithm.value,
            "key_type": key_type.value,
            "security_level": security_level.value,
            "data_category": data_category.value,
            "checksum": self._calculate_checksum(data_bytes),
        }
        
        return {
            "data": base64.b64encode(encrypted_data).decode("utf-8"),
            "metadata": metadata
        }
    
    def decrypt_data(self, encrypted_package: Dict[str, Any]) -> Union[str, bytes]:
        """
        Decrypt data from an encrypted package.
        
        Args:
            encrypted_package: Dictionary containing encrypted data and metadata
            
        Returns:
            Decrypted data as string or bytes
        """
        # Extract data and metadata
        encrypted_data = base64.b64decode(encrypted_package["data"])
        metadata = encrypted_package["metadata"]
        
        # Get key information
        key_type = KeyType(metadata["key_type"])
        algorithm = EncryptionAlgorithm(metadata["algorithm"])
        
        # Try to use current key first
        if key_type in self.keys:
            key = self.keys[key_type]["key"]
            
            # Try to decrypt with current key
            try:
                return self._decrypt_with_key(encrypted_data, key, algorithm)
            except (cryptography.fernet.InvalidToken, ValueError) as e:
                self.logger.warning(f"Failed to decrypt with current key: {e}")
                
                # If current key fails, try old keys if available
                if hasattr(self, '_old_keys') and key_type in self._old_keys:
                    old_key = self._old_keys[key_type]["key"]
                    try:
                        return self._decrypt_with_key(encrypted_data, old_key, algorithm)
                    except Exception as e2:
                        self.logger.error(f"Failed to decrypt with old key: {e2}")
                        raise ValueError("Failed to decrypt data with any available key")
                else:
                    raise ValueError("Failed to decrypt data with current key and no old keys available")
        else:
            raise ValueError(f"Key type {key_type.value} not found")
    
    def _decrypt_with_key(self, encrypted_data: bytes, key: bytes, algorithm: EncryptionAlgorithm) -> Union[str, bytes]:
        """
        Helper method to decrypt data with a specific key.
        
        Args:
            encrypted_data: Data to decrypt
            key: Key to use for decryption
            algorithm: Encryption algorithm used
            
        Returns:
            Decrypted data
        """
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC, 
                         EncryptionAlgorithm.CHACHA20_POLY1305]:
            # Symmetric decryption
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
        elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            # Asymmetric decryption (hybrid approach)
            # Parse the encrypted package
            hybrid_package = json.loads(base64.b64decode(encrypted_data))
            encrypted_symmetric_key = base64.b64decode(hybrid_package["key"])
            encrypted_data = base64.b64decode(hybrid_package["data"])
            
            # Load the RSA private key
            private_key = serialization.load_pem_private_key(
                key,
                password=None,
                backend=default_backend()
            )
            
            # Decrypt the symmetric key
            symmetric_key = private_key.decrypt(
                encrypted_symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt the data with the symmetric key
            fernet = Fernet(symmetric_key)
            decrypted_data = fernet.decrypt(encrypted_data)
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
        
        # Try to decode as UTF-8 string if possible
        try:
            return decrypted_data.decode("utf-8")
        except UnicodeDecodeError:
            # Return as bytes if not a valid UTF-8 string
            return decrypted_data
    
    def store_secure_data(self, data: Union[str, bytes], 
                         security_level: Optional[SecurityLevel] = None,
                         data_category: Optional[DataCategory] = None) -> str:
        """
        Store data securely with encryption.
        
        Args:
            data: Data to store securely
            security_level: Security level of the data
            data_category: Category of the data
            
        Returns:
            Path to the stored encrypted data
        """
        # Generate a unique identifier
        identifier = f"data_{secrets.token_hex(8)}"
        
        # Encrypt the data
        encrypted_package = self.encrypt_data(data, security_level, data_category)
        
        # Create a secure filename
        secure_filename = f"{identifier}.encrypted"
        file_path = self.secure_storage_dir / secure_filename
        
        # Store the encrypted data
        with open(file_path, "w") as f:
            f.write(json.dumps(encrypted_package))
        
        return str(file_path)
    
    def retrieve_secure_data(self, file_path: Union[str, Path]) -> Union[str, bytes]:
        """
        Retrieve securely stored data.
        
        Args:
            file_path: Path to the encrypted data file
            
        Returns:
            Decrypted data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Encrypted data file not found: {file_path}")
        
        # Read the encrypted package
        with open(file_path, "r") as f:
            encrypted_package = json.loads(f.read())
        
        # Decrypt the data
        return self.decrypt_data(encrypted_package)
    
    def delete_secure_data(self, file_path: Union[str, Path]) -> bool:
        """
        Securely delete stored data.
        
        Args:
            file_path: Path to the encrypted data file
            
        Returns:
            True if deletion was successful
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False
        
        # Securely overwrite the file before deletion
        file_size = file_path.stat().st_size
        
        with open(file_path, "wb") as f:
            # First pass: zeros
            f.write(b"\x00" * file_size)
            f.flush()
            os.fsync(f.fileno())
            
            # Second pass: ones
            f.seek(0)
            f.write(b"\xFF" * file_size)
            f.flush()
            os.fsync(f.fileno())
            
            # Third pass: random data
            f.seek(0)
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())
        
        # Delete the file
        file_path.unlink()
        
        return True
    
    def _calculate_checksum(self, data: bytes) -> str:
        """
        Calculate a checksum for data integrity verification.
        
        Args:
            data: Data to calculate checksum for
            
        Returns:
            Checksum as a hex string
        """
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data)
        return digest.finalize().hex()
    
    def generate_password(self, length: Optional[int] = None) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Length of the password to generate
            
        Returns:
            Secure random password
        """
        length = length or self.config["min_password_length"]
        
        # Ensure minimum length
        if length < 8:
            length = 8
        
        # Character sets
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digits = "0123456789"
        special = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill the rest with random characters from all sets
        all_chars = lowercase + uppercase + digits + special
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle the password characters
        secrets.SystemRandom().shuffle(password)
        
        return "".join(password)
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive an encryption key from a password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation, or None to generate a new one
            
        Returns:
            Derived key
        """
        # Generate salt if not provided
        if salt is None:
            salt = os.urandom(16)
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.config["pbkdf2_iterations"],
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return key
