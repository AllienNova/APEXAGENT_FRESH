"""
Encryption Service Layer for the Data Protection Framework.

This module provides high-level encryption services for data in transit,
data at rest, and end-to-end message encryption.
"""

import os
import time
import json
import base64
import logging
import uuid
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum

from ..crypto import (
    CryptoCore,
    EncryptionAlgorithm,
    AsymmetricAlgorithm,
    HashAlgorithm,
    KeyDerivationFunction,
    CryptoError
)

from ..key_management import (
    KeyManagementService,
    KeyType,
    KeyStatus,
    KeyUsage,
    KeyMetadata,
    KeyManagementError,
    KeyNotFoundError
)

# Configure logging
logger = logging.getLogger(__name__)

class EncryptionContext:
    """
    Context information for encryption operations.
    
    This class encapsulates metadata and context information for
    encryption operations, allowing for consistent handling of
    encryption parameters across the system.
    """
    
    def __init__(
        self,
        context_id: Optional[str] = None,
        algorithm: Optional[EncryptionAlgorithm] = None,
        key_id: Optional[str] = None,
        associated_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        sensitivity_level: Optional[str] = None,
        created_at: Optional[int] = None,
        expires_at: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize an encryption context.
        
        Args:
            context_id: Unique identifier for this context
            algorithm: Encryption algorithm to use
            key_id: ID of the key to use for encryption/decryption
            associated_data: Additional authenticated data for AEAD modes
            user_id: ID of the user associated with this context
            resource_id: ID of the resource being encrypted
            resource_type: Type of resource being encrypted
            sensitivity_level: Sensitivity level of the data
            created_at: Timestamp when this context was created
            expires_at: Timestamp when this context expires
            tags: Additional metadata tags
        """
        self.context_id = context_id or str(uuid.uuid4())
        self.algorithm = algorithm or EncryptionAlgorithm.AES_256_GCM
        self.key_id = key_id
        self.associated_data = associated_data or {}
        self.user_id = user_id
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.sensitivity_level = sensitivity_level
        self.created_at = created_at or int(time.time())
        self.expires_at = expires_at
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            'context_id': self.context_id,
            'algorithm': self.algorithm.value,
            'key_id': self.key_id,
            'associated_data': self.associated_data,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'sensitivity_level': self.sensitivity_level,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptionContext':
        """Create context from dictionary."""
        # Convert string values back to enums
        algorithm = EncryptionAlgorithm(data['algorithm'])
        
        return cls(
            context_id=data['context_id'],
            algorithm=algorithm,
            key_id=data['key_id'],
            associated_data=data['associated_data'],
            user_id=data['user_id'],
            resource_id=data['resource_id'],
            resource_type=data['resource_type'],
            sensitivity_level=data['sensitivity_level'],
            created_at=data['created_at'],
            expires_at=data['expires_at'],
            tags=data['tags']
        )
    
    def get_associated_data_bytes(self) -> bytes:
        """
        Convert associated data to bytes for use in encryption.
        
        Returns:
            bytes: Serialized associated data
        """
        # Create a copy of associated data with context information
        data = self.associated_data.copy()
        data.update({
            'context_id': self.context_id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'created_at': self.created_at
        })
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        # Serialize to JSON and encode as bytes
        return json.dumps(data, sort_keys=True).encode('utf-8')

class EncryptedData:
    """
    Container for encrypted data and associated metadata.
    
    This class encapsulates encrypted data along with the necessary
    metadata for decryption, providing a standardized format for
    storing and transmitting encrypted data.
    """
    
    def __init__(
        self,
        ciphertext: bytes,
        context: EncryptionContext,
        iv: Optional[bytes] = None,
        tag: Optional[bytes] = None,
        key_id: Optional[str] = None,
        version: int = 1
    ):
        """
        Initialize encrypted data container.
        
        Args:
            ciphertext: The encrypted data
            context: The encryption context
            iv: Initialization vector or nonce
            tag: Authentication tag for AEAD modes
            key_id: ID of the key used for encryption
            version: Format version
        """
        self.ciphertext = ciphertext
        self.context = context
        self.iv = iv
        self.tag = tag
        self.key_id = key_id or context.key_id
        self.version = version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'ciphertext': base64.b64encode(self.ciphertext).decode('utf-8'),
            'context': self.context.to_dict(),
            'iv': base64.b64encode(self.iv).decode('utf-8') if self.iv else None,
            'tag': base64.b64encode(self.tag).decode('utf-8') if self.tag else None,
            'key_id': self.key_id,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptedData':
        """Create from dictionary."""
        context = EncryptionContext.from_dict(data['context'])
        
        return cls(
            ciphertext=base64.b64decode(data['ciphertext']),
            context=context,
            iv=base64.b64decode(data['iv']) if data['iv'] else None,
            tag=base64.b64decode(data['tag']) if data['tag'] else None,
            key_id=data['key_id'],
            version=data['version']
        )
    
    def serialize(self) -> bytes:
        """Serialize to bytes for storage or transmission."""
        return json.dumps(self.to_dict()).encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'EncryptedData':
        """Deserialize from bytes."""
        return cls.from_dict(json.loads(data.decode('utf-8')))

class EncryptionError(Exception):
    """Base exception for encryption service operations."""
    pass

class EncryptionService:
    """
    High-level encryption service for the Data Protection Framework.
    
    This service provides a unified interface for encryption operations,
    abstracting the underlying cryptographic operations and key management.
    """
    
    def __init__(
        self,
        crypto_core: Optional[CryptoCore] = None,
        key_manager: Optional[KeyManagementService] = None
    ):
        """
        Initialize the encryption service.
        
        Args:
            crypto_core: CryptoCore instance for cryptographic operations
            key_manager: KeyManagementService instance for key management
        """
        self._crypto = crypto_core or CryptoCore()
        self._key_manager = key_manager or KeyManagementService()
        
        logger.info("Encryption Service initialized")
    
    def encrypt(
        self,
        plaintext: bytes,
        context: Optional[EncryptionContext] = None,
        key_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> EncryptedData:
        """
        Encrypt data using the specified context and key.
        
        Args:
            plaintext: Data to encrypt
            context: Encryption context
            key_id: ID of the key to use (overrides context.key_id)
            user_id: ID of the user performing the operation
        
        Returns:
            EncryptedData: The encrypted data and metadata
        
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Create or update context
            if context is None:
                context = EncryptionContext(user_id=user_id)
            
            # Override key_id if provided
            if key_id:
                context.key_id = key_id
            
            # If no key_id is specified, create a new data encryption key
            if not context.key_id:
                context.key_id = self._key_manager.create_key(
                    key_type=KeyType.DATA_ENCRYPTION,
                    algorithm=context.algorithm,
                    usage=[KeyUsage.ENCRYPT, KeyUsage.DECRYPT],
                    owner=user_id
                )
            
            # Get the encryption key
            key = self._key_manager.get_key(
                context.key_id,
                usage=KeyUsage.ENCRYPT,
                requester=user_id
            )
            
            # Get associated data
            associated_data = context.get_associated_data_bytes()
            
            # Encrypt the data
            encrypted = self._crypto.encrypt_symmetric(
                plaintext,
                key,
                algorithm=context.algorithm,
                associated_data=associated_data
            )
            
            # Create and return encrypted data container
            return EncryptedData(
                ciphertext=encrypted['ciphertext'],
                context=context,
                iv=encrypted.get('iv') or encrypted.get('nonce'),
                tag=encrypted.get('tag'),
                key_id=context.key_id
            )
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(
        self,
        encrypted_data: EncryptedData,
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Decrypt data using the specified context and key.
        
        Args:
            encrypted_data: The encrypted data and metadata
            user_id: ID of the user performing the operation
        
        Returns:
            bytes: The decrypted plaintext
        
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Get the decryption key
            key = self._key_manager.get_key(
                encrypted_data.key_id,
                usage=KeyUsage.DECRYPT,
                requester=user_id
            )
            
            # Get associated data
            associated_data = encrypted_data.context.get_associated_data_bytes()
            
            # Prepare ciphertext data for decryption
            ciphertext_data = {
                'ciphertext': encrypted_data.ciphertext,
                'iv': encrypted_data.iv
            }
            
            # Add tag if present
            if encrypted_data.tag:
                ciphertext_data['tag'] = encrypted_data.tag
            
            # Decrypt the data
            plaintext = self._crypto.decrypt_symmetric(
                ciphertext_data,
                key,
                algorithm=encrypted_data.context.algorithm,
                associated_data=associated_data
            )
            
            return plaintext
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def create_encryption_context(
        self,
        algorithm: Optional[EncryptionAlgorithm] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        sensitivity_level: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> EncryptionContext:
        """
        Create a new encryption context.
        
        Args:
            algorithm: Encryption algorithm to use
            user_id: ID of the user associated with this context
            resource_id: ID of the resource being encrypted
            resource_type: Type of resource being encrypted
            sensitivity_level: Sensitivity level of the data
            tags: Additional metadata tags
        
        Returns:
            EncryptionContext: The created context
        """
        return EncryptionContext(
            algorithm=algorithm,
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            sensitivity_level=sensitivity_level,
            tags=tags
        )
    
    def rotate_encryption_key(
        self,
        encrypted_data: EncryptedData,
        user_id: Optional[str] = None
    ) -> EncryptedData:
        """
        Re-encrypt data with a new key.
        
        Args:
            encrypted_data: The encrypted data to re-encrypt
            user_id: ID of the user performing the operation
        
        Returns:
            EncryptedData: The re-encrypted data with new key
        
        Raises:
            EncryptionError: If key rotation fails
        """
        try:
            # Decrypt the data with the old key
            plaintext = self.decrypt(encrypted_data, user_id)
            
            # Rotate the key
            new_key_id = self._key_manager.rotate_key(
                encrypted_data.key_id,
                requester=user_id
            )
            
            # Create a new context with the new key
            new_context = EncryptionContext.from_dict(encrypted_data.context.to_dict())
            new_context.key_id = new_key_id
            
            # Re-encrypt with the new key
            return self.encrypt(plaintext, new_context, user_id=user_id)
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise EncryptionError(f"Key rotation failed: {str(e)}")

class TransitEncryptionService:
    """
    Service for encrypting data in transit.
    
    This service provides encryption for data being transmitted over
    networks, including API payloads and WebSocket communications.
    """
    
    def __init__(
        self,
        encryption_service: Optional[EncryptionService] = None,
        default_algorithm: Optional[EncryptionAlgorithm] = None
    ):
        """
        Initialize the transit encryption service.
        
        Args:
            encryption_service: EncryptionService instance
            default_algorithm: Default encryption algorithm
        """
        self._encryption = encryption_service or EncryptionService()
        self._default_algorithm = default_algorithm or EncryptionAlgorithm.AES_256_GCM
        
        logger.info("Transit Encryption Service initialized")
    
    def encrypt_payload(
        self,
        payload: bytes,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        sensitivity_level: Optional[str] = None
    ) -> bytes:
        """
        Encrypt an API or message payload.
        
        Args:
            payload: The payload to encrypt
            user_id: ID of the user sending the payload
            resource_type: Type of resource in the payload
            sensitivity_level: Sensitivity level of the payload
        
        Returns:
            bytes: Serialized encrypted payload
        
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Create encryption context
            context = self._encryption.create_encryption_context(
                algorithm=self._default_algorithm,
                user_id=user_id,
                resource_type=resource_type,
                sensitivity_level=sensitivity_level,
                tags={'purpose': 'transit'}
            )
            
            # Encrypt the payload
            encrypted = self._encryption.encrypt(payload, context, user_id=user_id)
            
            # Serialize for transmission
            return encrypted.serialize()
        except Exception as e:
            logger.error(f"Payload encryption failed: {str(e)}")
            raise EncryptionError(f"Payload encryption failed: {str(e)}")
    
    def decrypt_payload(
        self,
        encrypted_payload: bytes,
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Decrypt an API or message payload.
        
        Args:
            encrypted_payload: The encrypted payload
            user_id: ID of the user receiving the payload
        
        Returns:
            bytes: The decrypted payload
        
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Deserialize the encrypted payload
            encrypted_data = EncryptedData.deserialize(encrypted_payload)
            
            # Decrypt the payload
            return self._encryption.decrypt(encrypted_data, user_id=user_id)
        except Exception as e:
            logger.error(f"Payload decryption failed: {str(e)}")
            raise EncryptionError(f"Payload decryption failed: {str(e)}")
    
    def secure_channel_handshake(
        self,
        client_public_key: bytes,
        user_id: Optional[str] = None
    ) -> Dict[str, bytes]:
        """
        Perform a secure channel handshake.
        
        Args:
            client_public_key: Client's public key
            user_id: ID of the user establishing the channel
        
        Returns:
            Dict: Server's public key and encrypted session information
        
        Raises:
            EncryptionError: If handshake fails
        """
        try:
            # Create a new key pair for the server
            server_key_id = self._encryption._key_manager.create_key(
                key_type=KeyType.SYSTEM,
                algorithm=AsymmetricAlgorithm.ECC_P256,
                usage=[KeyUsage.ENCRYPT, KeyUsage.DECRYPT],
                owner="system",
                tags={'purpose': 'handshake'}
            )
            
            # Get the server's public key
            server_public_key = self._encryption._key_manager.get_key(
                f"{server_key_id}_public",
                usage=KeyUsage.ENCRYPT,
                requester="system"
            )
            
            # Generate a session key
            session_key = self._encryption._crypto.generate_symmetric_key()
            
            # Encrypt the session key with the client's public key
            encrypted_session_key = self._encryption._crypto.encrypt_asymmetric(
                session_key,
                client_public_key
            )
            
            # Create a session ID
            session_id = str(uuid.uuid4())
            
            # Return the handshake information
            return {
                'server_public_key': server_public_key,
                'encrypted_session_key': encrypted_session_key,
                'session_id': session_id.encode('utf-8')
            }
        except Exception as e:
            logger.error(f"Secure channel handshake failed: {str(e)}")
            raise EncryptionError(f"Secure channel handshake failed: {str(e)}")

class RestEncryptionService:
    """
    Service for encrypting data at rest.
    
    This service provides encryption for stored data, including
    files, database records, and configuration values.
    """
    
    def __init__(
        self,
        encryption_service: Optional[EncryptionService] = None,
        default_algorithm: Optional[EncryptionAlgorithm] = None
    ):
        """
        Initialize the rest encryption service.
        
        Args:
            encryption_service: EncryptionService instance
            default_algorithm: Default encryption algorithm
        """
        self._encryption = encryption_service or EncryptionService()
        self._default_algorithm = default_algorithm or EncryptionAlgorithm.AES_256_GCM
        
        logger.info("Rest Encryption Service initialized")
    
    def encrypt_data(
        self,
        data: bytes,
        resource_id: str,
        resource_type: str,
        user_id: Optional[str] = None,
        sensitivity_level: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> bytes:
        """
        Encrypt data for storage.
        
        Args:
            data: The data to encrypt
            resource_id: ID of the resource being encrypted
            resource_type: Type of resource being encrypted
            user_id: ID of the user owning the data
            sensitivity_level: Sensitivity level of the data
            tags: Additional metadata tags
        
        Returns:
            bytes: Serialized encrypted data
        
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Create encryption context
            context = self._encryption.create_encryption_context(
                algorithm=self._default_algorithm,
                user_id=user_id,
                resource_id=resource_id,
                resource_type=resource_type,
                sensitivity_level=sensitivity_level,
                tags=tags
            )
            
            # Add storage-specific tags
            context.tags['purpose'] = 'storage'
            
            # Encrypt the data
            encrypted = self._encryption.encrypt(data, context, user_id=user_id)
            
            # Serialize for storage
            return encrypted.serialize()
        except Exception as e:
            logger.error(f"Data encryption failed: {str(e)}")
            raise EncryptionError(f"Data encryption failed: {str(e)}")
    
    def decrypt_data(
        self,
        encrypted_data: bytes,
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Decrypt stored data.
        
        Args:
            encrypted_data: The encrypted data
            user_id: ID of the user accessing the data
        
        Returns:
            bytes: The decrypted data
        
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Deserialize the encrypted data
            encrypted_obj = EncryptedData.deserialize(encrypted_data)
            
            # Decrypt the data
            return self._encryption.decrypt(encrypted_obj, user_id=user_id)
        except Exception as e:
            logger.error(f"Data decryption failed: {str(e)}")
            raise EncryptionError(f"Data decryption failed: {str(e)}")
    
    def encrypt_file(
        self,
        input_path: str,
        output_path: str,
        resource_id: str,
        resource_type: str,
        user_id: Optional[str] = None,
        sensitivity_level: Optional[str] = None,
        chunk_size: int = 4096
    ):
        """
        Encrypt a file.
        
        Args:
            input_path: Path to the file to encrypt
            output_path: Path to save the encrypted file
            resource_id: ID of the resource being encrypted
            resource_type: Type of resource being encrypted
            user_id: ID of the user owning the file
            sensitivity_level: Sensitivity level of the file
            chunk_size: Size of chunks to process at once
        
        Raises:
            EncryptionError: If file encryption fails
        """
        try:
            # Create encryption context
            context = self._encryption.create_encryption_context(
                algorithm=self._default_algorithm,
                user_id=user_id,
                resource_id=resource_id,
                resource_type=resource_type,
                sensitivity_level=sensitivity_level,
                tags={'purpose': 'file_storage'}
            )
            
            # Create a key for this file
            key_id = self._encryption._key_manager.create_key(
                key_type=KeyType.DATA_ENCRYPTION,
                algorithm=self._default_algorithm,
                usage=[KeyUsage.ENCRYPT, KeyUsage.DECRYPT],
                owner=user_id,
                tags={'resource_id': resource_id, 'resource_type': resource_type}
            )
            
            # Set the key ID in the context
            context.key_id = key_id
            
            # Get the encryption key
            key = self._encryption._key_manager.get_key(
                key_id,
                usage=KeyUsage.ENCRYPT,
                requester=user_id
            )
            
            # Open the input and output files
            with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                # Write the serialized context as a header
                header = json.dumps(context.to_dict()).encode('utf-8')
                header_length = len(header).to_bytes(4, byteorder='big')
                outfile.write(header_length)
                outfile.write(header)
                
                # Generate IV
                iv = self._encryption._crypto.generate_random_bytes(16)
                outfile.write(iv)
                
                # Initialize cipher
                cipher = self._encryption._crypto._create_cipher(key, iv, context.algorithm)
                
                # Process the file in chunks
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Encrypt the chunk
                    encrypted_chunk = cipher.update(chunk)
                    outfile.write(encrypted_chunk)
                
                # Finalize encryption
                final_chunk = cipher.finalize()
                outfile.write(final_chunk)
                
                # Write authentication tag if using AEAD mode
                if hasattr(cipher, 'tag'):
                    outfile.write(cipher.tag)
        except Exception as e:
            logger.error(f"File encryption failed: {str(e)}")
            raise EncryptionError(f"File encryption failed: {str(e)}")
    
    def decrypt_file(
        self,
        input_path: str,
        output_path: str,
        user_id: Optional[str] = None,
        chunk_size: int = 4096
    ):
        """
        Decrypt a file.
        
        Args:
            input_path: Path to the encrypted file
            output_path: Path to save the decrypted file
            user_id: ID of the user accessing the file
            chunk_size: Size of chunks to process at once
        
        Raises:
            EncryptionError: If file decryption fails
        """
        try:
            # Open the input file
            with open(input_path, 'rb') as infile:
                # Read the header length
                header_length = int.from_bytes(infile.read(4), byteorder='big')
                
                # Read and parse the context
                header = infile.read(header_length)
                context_dict = json.loads(header.decode('utf-8'))
                context = EncryptionContext.from_dict(context_dict)
                
                # Read the IV
                iv = infile.read(16)
                
                # Get the decryption key
                key = self._encryption._key_manager.get_key(
                    context.key_id,
                    usage=KeyUsage.DECRYPT,
                    requester=user_id
                )
                
                # Initialize cipher
                cipher = self._encryption._crypto._create_decipher(key, iv, context.algorithm)
                
                # Open the output file
                with open(output_path, 'wb') as outfile:
                    # Process the file in chunks
                    while True:
                        chunk = infile.read(chunk_size)
                        if not chunk:
                            break
                        
                        # Decrypt the chunk
                        decrypted_chunk = cipher.update(chunk)
                        outfile.write(decrypted_chunk)
                    
                    # Finalize decryption
                    final_chunk = cipher.finalize()
                    outfile.write(final_chunk)
        except Exception as e:
            logger.error(f"File decryption failed: {str(e)}")
            raise EncryptionError(f"File decryption failed: {str(e)}")
    
    def encrypt_config_value(
        self,
        value: str,
        config_key: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Encrypt a configuration value.
        
        Args:
            value: The configuration value to encrypt
            config_key: The configuration key
            user_id: ID of the user accessing the configuration
        
        Returns:
            str: Base64-encoded encrypted value
        
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Create encryption context
            context = self._encryption.create_encryption_context(
                algorithm=self._default_algorithm,
                resource_id=config_key,
                resource_type='config',
                user_id=user_id,
                tags={'purpose': 'configuration'}
            )
            
            # Encrypt the value
            encrypted = self._encryption.encrypt(
                value.encode('utf-8'),
                context,
                user_id=user_id
            )
            
            # Serialize and encode for storage
            return base64.b64encode(encrypted.serialize()).decode('utf-8')
        except Exception as e:
            logger.error(f"Configuration encryption failed: {str(e)}")
            raise EncryptionError(f"Configuration encryption failed: {str(e)}")
    
    def decrypt_config_value(
        self,
        encrypted_value: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Decrypt a configuration value.
        
        Args:
            encrypted_value: The encrypted configuration value
            user_id: ID of the user accessing the configuration
        
        Returns:
            str: The decrypted configuration value
        
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Decode and deserialize the encrypted value
            encrypted_data = base64.b64decode(encrypted_value)
            encrypted_obj = EncryptedData.deserialize(encrypted_data)
            
            # Decrypt the value
            decrypted = self._encryption.decrypt(encrypted_obj, user_id=user_id)
            
            # Decode and return
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Configuration decryption failed: {str(e)}")
            raise EncryptionError(f"Configuration decryption failed: {str(e)}")

class MessageEncryptionService:
    """
    Service for end-to-end message encryption.
    
    This service provides end-to-end encryption for messages between
    users, ensuring that only the intended recipients can decrypt the content.
    """
    
    def __init__(
        self,
        encryption_service: Optional[EncryptionService] = None,
        key_manager: Optional[KeyManagementService] = None,
        default_algorithm: Optional[EncryptionAlgorithm] = None
    ):
        """
        Initialize the message encryption service.
        
        Args:
            encryption_service: EncryptionService instance
            key_manager: KeyManagementService instance
            default_algorithm: Default encryption algorithm
        """
        self._encryption = encryption_service or EncryptionService()
        self._key_manager = key_manager or self._encryption._key_manager
        self._default_algorithm = default_algorithm or EncryptionAlgorithm.AES_256_GCM
        
        logger.info("Message Encryption Service initialized")
    
    def generate_user_keypair(
        self,
        user_id: str
    ) -> Dict[str, str]:
        """
        Generate a key pair for a user.
        
        Args:
            user_id: ID of the user
        
        Returns:
            Dict: Public key ID and public key
        
        Raises:
            EncryptionError: If key generation fails
        """
        try:
            # Create a new key pair for the user
            key_id = self._key_manager.create_key(
                key_type=KeyType.USER,
                algorithm=AsymmetricAlgorithm.ECC_P256,
                usage=[KeyUsage.ENCRYPT, KeyUsage.DECRYPT, KeyUsage.SIGN, KeyUsage.VERIFY],
                owner=user_id,
                tags={'purpose': 'messaging'}
            )
            
            # Get the public key
            public_key = self._key_manager.get_key(
                f"{key_id}_public",
                usage=KeyUsage.ENCRYPT,
                requester=user_id
            )
            
            # Return the public key information
            return {
                'public_key_id': f"{key_id}_public",
                'public_key': base64.b64encode(public_key).decode('utf-8')
            }
        except Exception as e:
            logger.error(f"User key pair generation failed: {str(e)}")
            raise EncryptionError(f"User key pair generation failed: {str(e)}")
    
    def encrypt_message(
        self,
        message: bytes,
        sender_id: str,
        recipient_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Encrypt a message for multiple recipients.
        
        Args:
            message: The message to encrypt
            sender_id: ID of the sender
            recipient_ids: IDs of the recipients
        
        Returns:
            Dict: Encrypted message data
        
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Generate a random message key
            message_key = self._encryption._crypto.generate_symmetric_key()
            
            # Create encryption context
            context = self._encryption.create_encryption_context(
                algorithm=self._default_algorithm,
                user_id=sender_id,
                resource_type='message',
                tags={'purpose': 'messaging'}
            )
            
            # Encrypt the message with the message key
            encrypted_message = self._encryption._crypto.encrypt_symmetric(
                message,
                message_key,
                algorithm=context.algorithm,
                associated_data=context.get_associated_data_bytes()
            )
            
            # Get sender's private key for signing
            sender_keys = self._key_manager.list_keys(
                key_type=KeyType.USER,
                owner=sender_id,
                tags={'purpose': 'messaging'}
            )
            
            if not sender_keys:
                raise EncryptionError(f"No messaging keys found for sender {sender_id}")
            
            sender_key_id = sender_keys[0].key_id
            sender_private_key = self._key_manager.get_key(
                sender_key_id,
                usage=KeyUsage.SIGN,
                requester=sender_id
            )
            
            # Sign the encrypted message
            signature = self._encryption._crypto.sign_data(
                encrypted_message['ciphertext'],
                sender_private_key
            )
            
            # Encrypt the message key for each recipient
            recipient_keys = {}
            for recipient_id in recipient_ids:
                # Find recipient's public key
                recipient_public_keys = self._key_manager.list_keys(
                    key_type=KeyType.USER,
                    owner=recipient_id,
                    tags={'purpose': 'messaging'}
                )
                
                if not recipient_public_keys:
                    logger.warning(f"No messaging keys found for recipient {recipient_id}")
                    continue
                
                recipient_public_key_id = f"{recipient_public_keys[0].key_id}_public"
                recipient_public_key = self._key_manager.get_key(
                    recipient_public_key_id,
                    usage=KeyUsage.ENCRYPT,
                    requester="system"
                )
                
                # Encrypt the message key with recipient's public key
                encrypted_key = self._encryption._crypto.encrypt_asymmetric(
                    message_key,
                    recipient_public_key
                )
                
                # Store the encrypted key
                recipient_keys[recipient_id] = {
                    'key': base64.b64encode(encrypted_key).decode('utf-8'),
                    'key_id': recipient_public_key_id
                }
            
            # Return the encrypted message data
            return {
                'sender_id': sender_id,
                'sender_key_id': f"{sender_key_id}_public",
                'recipients': recipient_keys,
                'ciphertext': base64.b64encode(encrypted_message['ciphertext']).decode('utf-8'),
                'iv': base64.b64encode(encrypted_message['iv']).decode('utf-8'),
                'tag': base64.b64encode(encrypted_message['tag']).decode('utf-8'),
                'signature': base64.b64encode(signature).decode('utf-8'),
                'algorithm': context.algorithm.value,
                'timestamp': int(time.time()),
                'context': context.to_dict()
            }
        except Exception as e:
            logger.error(f"Message encryption failed: {str(e)}")
            raise EncryptionError(f"Message encryption failed: {str(e)}")
    
    def decrypt_message(
        self,
        encrypted_message: Dict[str, Any],
        recipient_id: str
    ) -> bytes:
        """
        Decrypt a message for a recipient.
        
        Args:
            encrypted_message: The encrypted message data
            recipient_id: ID of the recipient
        
        Returns:
            bytes: The decrypted message
        
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Check if recipient is in the recipients list
            if recipient_id not in encrypted_message['recipients']:
                raise EncryptionError(f"Message is not encrypted for recipient {recipient_id}")
            
            # Get recipient's encrypted key
            recipient_data = encrypted_message['recipients'][recipient_id]
            encrypted_key = base64.b64decode(recipient_data['key'])
            
            # Get recipient's private key
            recipient_key_id = recipient_data['key_id'].replace('_public', '')
            recipient_private_key = self._key_manager.get_key(
                recipient_key_id,
                usage=KeyUsage.DECRYPT,
                requester=recipient_id
            )
            
            # Decrypt the message key
            message_key = self._encryption._crypto.decrypt_asymmetric(
                encrypted_key,
                recipient_private_key
            )
            
            # Get sender's public key for verification
            sender_public_key = self._key_manager.get_key(
                encrypted_message['sender_key_id'],
                usage=KeyUsage.VERIFY,
                requester="system"
            )
            
            # Verify the signature
            ciphertext = base64.b64decode(encrypted_message['ciphertext'])
            signature = base64.b64decode(encrypted_message['signature'])
            
            if not self._encryption._crypto.verify_signature(
                ciphertext,
                signature,
                sender_public_key
            ):
                raise EncryptionError("Message signature verification failed")
            
            # Reconstruct the encrypted message
            encrypted_data = {
                'ciphertext': ciphertext,
                'iv': base64.b64decode(encrypted_message['iv']),
                'tag': base64.b64decode(encrypted_message['tag'])
            }
            
            # Create context for associated data
            context = EncryptionContext.from_dict(encrypted_message['context'])
            
            # Decrypt the message
            return self._encryption._crypto.decrypt_symmetric(
                encrypted_data,
                message_key,
                algorithm=EncryptionAlgorithm(encrypted_message['algorithm']),
                associated_data=context.get_associated_data_bytes()
            )
        except Exception as e:
            logger.error(f"Message decryption failed: {str(e)}")
            raise EncryptionError(f"Message decryption failed: {str(e)}")
    
    def create_secure_channel(
        self,
        user1_id: str,
        user2_id: str
    ) -> str:
        """
        Create a secure communication channel between two users.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
        
        Returns:
            str: Channel ID
        
        Raises:
            EncryptionError: If channel creation fails
        """
        try:
            # Generate a unique channel ID
            channel_id = str(uuid.uuid4())
            
            # Generate a shared key for the channel
            channel_key_id = self._key_manager.create_key(
                key_type=KeyType.DATA_ENCRYPTION,
                algorithm=self._default_algorithm,
                usage=[KeyUsage.ENCRYPT, KeyUsage.DECRYPT],
                owner="system",
                tags={
                    'purpose': 'secure_channel',
                    'channel_id': channel_id,
                    'user1_id': user1_id,
                    'user2_id': user2_id
                }
            )
            
            # Return the channel ID
            return channel_id
        except Exception as e:
            logger.error(f"Secure channel creation failed: {str(e)}")
            raise EncryptionError(f"Secure channel creation failed: {str(e)}")
    
    def encrypt_channel_message(
        self,
        channel_id: str,
        message: bytes,
        sender_id: str
    ) -> Dict[str, Any]:
        """
        Encrypt a message for a secure channel.
        
        Args:
            channel_id: ID of the secure channel
            message: The message to encrypt
            sender_id: ID of the sender
        
        Returns:
            Dict: Encrypted message data
        
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Find the channel key
            channel_keys = self._key_manager.list_keys(
                key_type=KeyType.DATA_ENCRYPTION,
                tags={
                    'purpose': 'secure_channel',
                    'channel_id': channel_id
                }
            )
            
            if not channel_keys:
                raise EncryptionError(f"No key found for channel {channel_id}")
            
            channel_key_id = channel_keys[0].key_id
            
            # Check if sender is authorized to use the channel
            channel_tags = channel_keys[0].tags
            if sender_id != channel_tags.get('user1_id') and sender_id != channel_tags.get('user2_id'):
                raise EncryptionError(f"Sender {sender_id} is not authorized for channel {channel_id}")
            
            # Get the channel key
            channel_key = self._key_manager.get_key(
                channel_key_id,
                usage=KeyUsage.ENCRYPT,
                requester=sender_id
            )
            
            # Create encryption context
            context = self._encryption.create_encryption_context(
                algorithm=self._default_algorithm,
                user_id=sender_id,
                resource_type='channel_message',
                tags={
                    'purpose': 'secure_channel',
                    'channel_id': channel_id
                }
            )
            
            # Encrypt the message
            encrypted = self._encryption._crypto.encrypt_symmetric(
                message,
                channel_key,
                algorithm=context.algorithm,
                associated_data=context.get_associated_data_bytes()
            )
            
            # Return the encrypted message data
            return {
                'channel_id': channel_id,
                'sender_id': sender_id,
                'ciphertext': base64.b64encode(encrypted['ciphertext']).decode('utf-8'),
                'iv': base64.b64encode(encrypted['iv']).decode('utf-8'),
                'tag': base64.b64encode(encrypted['tag']).decode('utf-8'),
                'algorithm': context.algorithm.value,
                'timestamp': int(time.time()),
                'context': context.to_dict()
            }
        except Exception as e:
            logger.error(f"Channel message encryption failed: {str(e)}")
            raise EncryptionError(f"Channel message encryption failed: {str(e)}")
    
    def decrypt_channel_message(
        self,
        encrypted_message: Dict[str, Any],
        recipient_id: str
    ) -> bytes:
        """
        Decrypt a message from a secure channel.
        
        Args:
            encrypted_message: The encrypted message data
            recipient_id: ID of the recipient
        
        Returns:
            bytes: The decrypted message
        
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Get channel ID from the message
            channel_id = encrypted_message['channel_id']
            
            # Find the channel key
            channel_keys = self._key_manager.list_keys(
                key_type=KeyType.DATA_ENCRYPTION,
                tags={
                    'purpose': 'secure_channel',
                    'channel_id': channel_id
                }
            )
            
            if not channel_keys:
                raise EncryptionError(f"No key found for channel {channel_id}")
            
            channel_key_id = channel_keys[0].key_id
            
            # Check if recipient is authorized to use the channel
            channel_tags = channel_keys[0].tags
            if recipient_id != channel_tags.get('user1_id') and recipient_id != channel_tags.get('user2_id'):
                raise EncryptionError(f"Recipient {recipient_id} is not authorized for channel {channel_id}")
            
            # Get the channel key
            channel_key = self._key_manager.get_key(
                channel_key_id,
                usage=KeyUsage.DECRYPT,
                requester=recipient_id
            )
            
            # Reconstruct the encrypted message
            encrypted_data = {
                'ciphertext': base64.b64decode(encrypted_message['ciphertext']),
                'iv': base64.b64decode(encrypted_message['iv']),
                'tag': base64.b64decode(encrypted_message['tag'])
            }
            
            # Create context for associated data
            context = EncryptionContext.from_dict(encrypted_message['context'])
            
            # Decrypt the message
            return self._encryption._crypto.decrypt_symmetric(
                encrypted_data,
                channel_key,
                algorithm=EncryptionAlgorithm(encrypted_message['algorithm']),
                associated_data=context.get_associated_data_bytes()
            )
        except Exception as e:
            logger.error(f"Channel message decryption failed: {str(e)}")
            raise EncryptionError(f"Channel message decryption failed: {str(e)}")
