"""
Data Anonymization module for the Data Protection Framework.

This module provides comprehensive data anonymization capabilities including
PII detection, tokenization, masking, and privacy-preserving analytics.
"""

import re
import os
import time
import json
import uuid
import hashlib
import logging
import random
import base64
from typing import Dict, List, Optional, Tuple, Union, Any, Set, Callable
from enum import Enum
import numpy as np

from ..crypto import CryptoCore, HashAlgorithm
from ..key_management import KeyManagementService, KeyType, KeyUsage

# Configure logging
logger = logging.getLogger(__name__)

class AnonymizationLevel(Enum):
    """Levels of anonymization with increasing privacy protection."""
    MINIMAL = "minimal"       # Basic masking of direct identifiers
    STANDARD = "standard"     # Comprehensive anonymization of direct and some indirect identifiers
    ENHANCED = "enhanced"     # Advanced anonymization with statistical disclosure controls
    MAXIMUM = "maximum"       # Complete anonymization with synthetic data generation

class DataCategory(Enum):
    """Categories of data for anonymization purposes."""
    DIRECT_IDENTIFIER = "direct_identifier"       # Directly identifies an individual (e.g., name, SSN)
    QUASI_IDENTIFIER = "quasi_identifier"         # Can identify an individual when combined (e.g., ZIP, birthdate)
    SENSITIVE_ATTRIBUTE = "sensitive_attribute"   # Sensitive information (e.g., health condition, salary)
    NON_SENSITIVE = "non_sensitive"               # Non-sensitive information

class AnonymizationMethod(Enum):
    """Methods for anonymizing data."""
    REDACTION = "redaction"           # Complete removal of data
    MASKING = "masking"               # Partial masking with characters like '*'
    TOKENIZATION = "tokenization"     # Replacing with a token that can be reversed
    GENERALIZATION = "generalization" # Reducing precision (e.g., age to age range)
    PERTURBATION = "perturbation"     # Adding noise to numerical values
    SYNTHETIC = "synthetic"           # Replacing with synthetic data

class AnonymizationError(Exception):
    """Base exception for anonymization operations."""
    pass

class PIIDetectionError(AnonymizationError):
    """Exception raised when PII detection fails."""
    pass

class TokenizationError(AnonymizationError):
    """Exception raised when tokenization operations fail."""
    pass

class AnonymizationPolicyError(AnonymizationError):
    """Exception raised when policy validation or application fails."""
    pass

class PIIType(Enum):
    """Types of personally identifiable information."""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    DOB = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    MEDICAL_RECORD = "medical_record"
    FINANCIAL_ACCOUNT = "financial_account"
    USERNAME = "username"
    PASSWORD = "password"
    LOCATION = "location"
    BIOMETRIC = "biometric"
    CUSTOM = "custom"

class PIIDetector:
    """
    Detector for personally identifiable information (PII).
    
    This class provides methods for detecting various types of PII
    in text and structured data.
    """
    
    def __init__(self):
        """Initialize the PII detector with regex patterns."""
        # Compile regex patterns for common PII types
        self._patterns = {
            PIIType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            PIIType.PHONE: re.compile(r'\b(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'),
            PIIType.SSN: re.compile(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'),
            PIIType.CREDIT_CARD: re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            PIIType.IP_ADDRESS: re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
            PIIType.DOB: re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b')
        }
        
        # Name detection is more complex and may require NLP techniques
        # This is a simplified pattern for demonstration
        self._patterns[PIIType.NAME] = re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b')
        
        logger.info("PII Detector initialized")
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text.
        
        Args:
            text: Text to analyze for PII
        
        Returns:
            List[Dict]: List of detected PII with type, value, and position
        
        Raises:
            PIIDetectionError: If PII detection fails
        """
        try:
            results = []
            
            # Check each PII type
            for pii_type, pattern in self._patterns.items():
                for match in pattern.finditer(text):
                    results.append({
                        'type': pii_type.value,
                        'value': match.group(),
                        'start': match.start(),
                        'end': match.end()
                    })
            
            return results
        except Exception as e:
            logger.error(f"PII detection failed: {str(e)}")
            raise PIIDetectionError(f"PII detection failed: {str(e)}")
    
    def detect_pii_in_dict(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect PII in a dictionary.
        
        Args:
            data: Dictionary to analyze for PII
        
        Returns:
            Dict: Dictionary mapping keys to lists of detected PII
        
        Raises:
            PIIDetectionError: If PII detection fails
        """
        try:
            results = {}
            
            for key, value in data.items():
                if isinstance(value, str):
                    pii = self.detect_pii(value)
                    if pii:
                        results[key] = pii
                elif isinstance(value, dict):
                    nested_results = self.detect_pii_in_dict(value)
                    for nested_key, nested_pii in nested_results.items():
                        results[f"{key}.{nested_key}"] = nested_pii
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, str):
                            pii = self.detect_pii(item)
                            if pii:
                                results[f"{key}[{i}]"] = pii
                        elif isinstance(item, dict):
                            nested_results = self.detect_pii_in_dict(item)
                            for nested_key, nested_pii in nested_results.items():
                                results[f"{key}[{i}].{nested_key}"] = nested_pii
            
            return results
        except Exception as e:
            logger.error(f"PII detection in dictionary failed: {str(e)}")
            raise PIIDetectionError(f"PII detection in dictionary failed: {str(e)}")
    
    def add_custom_pattern(self, pii_type: PIIType, pattern: str):
        """
        Add a custom regex pattern for PII detection.
        
        Args:
            pii_type: Type of PII to detect
            pattern: Regex pattern as string
        
        Raises:
            PIIDetectionError: If pattern compilation fails
        """
        try:
            self._patterns[pii_type] = re.compile(pattern)
            logger.info(f"Added custom pattern for {pii_type.value}")
        except Exception as e:
            logger.error(f"Failed to add custom pattern: {str(e)}")
            raise PIIDetectionError(f"Failed to add custom pattern: {str(e)}")

class TokenizationService:
    """
    Service for tokenizing sensitive data.
    
    This service provides methods for replacing sensitive data with tokens
    that can be securely stored and later detokenized if needed.
    """
    
    def __init__(
        self,
        crypto_core: Optional[CryptoCore] = None,
        key_manager: Optional[KeyManagementService] = None,
        token_format: str = "uuid"
    ):
        """
        Initialize the tokenization service.
        
        Args:
            crypto_core: CryptoCore instance for cryptographic operations
            key_manager: KeyManagementService instance for key management
            token_format: Format for generated tokens (uuid, numeric, alphanumeric)
        """
        self._crypto = crypto_core or CryptoCore()
        self._key_manager = key_manager or KeyManagementService()
        self._token_format = token_format
        self._token_vault = {}  # In-memory token storage (would be a database in production)
        
        # Create a tokenization key if not exists
        self._tokenization_keys = self._key_manager.list_keys(
            key_type=KeyType.SYSTEM,
            tags={'purpose': 'tokenization'}
        )
        
        if not self._tokenization_keys:
            self._tokenization_key_id = self._key_manager.create_key(
                key_type=KeyType.SYSTEM,
                algorithm=self._crypto.EncryptionAlgorithm.AES_256_GCM,
                usage=[KeyUsage.ENCRYPT, KeyUsage.DECRYPT],
                owner="system",
                tags={'purpose': 'tokenization'}
            )
        else:
            self._tokenization_key_id = self._tokenization_keys[0].key_id
        
        logger.info("Tokenization Service initialized")
    
    def tokenize(
        self,
        value: str,
        data_type: Optional[PIIType] = None,
        context: Optional[Dict[str, Any]] = None,
        preserve_format: bool = False
    ) -> str:
        """
        Tokenize a sensitive value.
        
        Args:
            value: Value to tokenize
            data_type: Type of data being tokenized
            context: Additional context for tokenization
            preserve_format: Whether to preserve format (e.g., for credit cards)
        
        Returns:
            str: Token representing the value
        
        Raises:
            TokenizationError: If tokenization fails
        """
        try:
            # Get the tokenization key
            key = self._key_manager.get_key(
                self._tokenization_key_id,
                usage=KeyUsage.ENCRYPT,
                requester="system"
            )
            
            # Create a unique ID for this tokenization
            token_id = str(uuid.uuid4())
            
            # Encrypt the value
            encrypted = self._crypto.encrypt_symmetric(
                value.encode('utf-8'),
                key,
                associated_data=token_id.encode('utf-8')
            )
            
            # Generate a token based on the format
            if self._token_format == "uuid":
                token = token_id
            elif self._token_format == "numeric":
                token = ''.join(random.choices('0123456789', k=16))
            elif self._token_format == "alphanumeric":
                token = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=16))
            else:
                token = token_id
            
            # If format preservation is requested, handle special cases
            if preserve_format and data_type:
                if data_type == PIIType.CREDIT_CARD:
                    # Preserve the last 4 digits and format
                    last_four = value[-4:] if len(value) >= 4 else value
                    token = f"{'X' * (len(value) - 4)}{last_four}"
                elif data_type == PIIType.PHONE:
                    # Preserve the format but replace digits
                    token = ''.join(['X' if c.isdigit() else c for c in value])
                elif data_type == PIIType.EMAIL:
                    # Create a fake but realistic-looking email
                    parts = value.split('@')
                    if len(parts) == 2:
                        domain = parts[1]
                        token = f"{'X' * len(parts[0])}@{domain}"
            
            # Store the token mapping
            self._token_vault[token] = {
                'encrypted_value': {
                    'ciphertext': base64.b64encode(encrypted['ciphertext']).decode('utf-8'),
                    'iv': base64.b64encode(encrypted['iv']).decode('utf-8'),
                    'tag': base64.b64encode(encrypted['tag']).decode('utf-8')
                },
                'token_id': token_id,
                'data_type': data_type.value if data_type else None,
                'created_at': int(time.time()),
                'context': context
            }
            
            return token
        except Exception as e:
            logger.error(f"Tokenization failed: {str(e)}")
            raise TokenizationError(f"Tokenization failed: {str(e)}")
    
    def detokenize(
        self,
        token: str,
        requester: Optional[str] = None
    ) -> str:
        """
        Detokenize a token back to its original value.
        
        Args:
            token: Token to detokenize
            requester: Entity requesting detokenization
        
        Returns:
            str: Original value
        
        Raises:
            TokenizationError: If detokenization fails
        """
        try:
            # Check if token exists
            if token not in self._token_vault:
                raise TokenizationError(f"Token {token} not found")
            
            # Get token data
            token_data = self._token_vault[token]
            
            # Get the tokenization key
            key = self._key_manager.get_key(
                self._tokenization_key_id,
                usage=KeyUsage.DECRYPT,
                requester="system"
            )
            
            # Decrypt the value
            encrypted_data = {
                'ciphertext': base64.b64decode(token_data['encrypted_value']['ciphertext']),
                'iv': base64.b64decode(token_data['encrypted_value']['iv']),
                'tag': base64.b64decode(token_data['encrypted_value']['tag'])
            }
            
            plaintext = self._crypto.decrypt_symmetric(
                encrypted_data,
                key,
                associated_data=token_data['token_id'].encode('utf-8')
            )
            
            return plaintext.decode('utf-8')
        except Exception as e:
            logger.error(f"Detokenization failed: {str(e)}")
            raise TokenizationError(f"Detokenization failed: {str(e)}")
    
    def tokenize_dict(
        self,
        data: Dict[str, Any],
        fields_to_tokenize: Dict[str, PIIType],
        preserve_format: bool = False
    ) -> Dict[str, Any]:
        """
        Tokenize specified fields in a dictionary.
        
        Args:
            data: Dictionary containing data to tokenize
            fields_to_tokenize: Mapping of field paths to PII types
            preserve_format: Whether to preserve format
        
        Returns:
            Dict: Dictionary with tokenized values
        
        Raises:
            TokenizationError: If tokenization fails
        """
        try:
            result = data.copy()
            
            for field_path, pii_type in fields_to_tokenize.items():
                # Handle nested paths (e.g., "user.contact.email")
                parts = field_path.split('.')
                current = result
                
                # Navigate to the parent object
                for part in parts[:-1]:
                    if part in current:
                        current = current[part]
                    else:
                        # Path doesn't exist, skip
                        break
                else:
                    # Process the final part if it exists
                    last_part = parts[-1]
                    if last_part in current and isinstance(current[last_part], str):
                        current[last_part] = self.tokenize(
                            current[last_part],
                            pii_type,
                            {'field_path': field_path},
                            preserve_format
                        )
            
            return result
        except Exception as e:
            logger.error(f"Dictionary tokenization failed: {str(e)}")
            raise TokenizationError(f"Dictionary tokenization failed: {str(e)}")
    
    def detokenize_dict(
        self,
        data: Dict[str, Any],
        fields_to_detokenize: List[str],
        requester: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detokenize specified fields in a dictionary.
        
        Args:
            data: Dictionary containing tokenized data
            fields_to_detokenize: List of field paths to detokenize
            requester: Entity requesting detokenization
        
        Returns:
            Dict: Dictionary with detokenized values
        
        Raises:
            TokenizationError: If detokenization fails
        """
        try:
            result = data.copy()
            
            for field_path in fields_to_detokenize:
                # Handle nested paths (e.g., "user.contact.email")
                parts = field_path.split('.')
                current = result
                
                # Navigate to the parent object
                for part in parts[:-1]:
                    if part in current:
                        current = current[part]
                    else:
                        # Path doesn't exist, skip
                        break
                else:
                    # Process the final part if it exists
                    last_part = parts[-1]
                    if last_part in current and isinstance(current[last_part], str):
                        current[last_part] = self.detokenize(
                            current[last_part],
                            requester
                        )
            
            return result
        except Exception as e:
            logger.error(f"Dictionary detokenization failed: {str(e)}")
            raise TokenizationError(f"Dictionary detokenization failed: {str(e)}")

class AnonymizationPolicy:
    """
    Policy for data anonymization.
    
    This class defines how different types of data should be anonymized,
    including methods, levels, and specific rules.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        default_level: AnonymizationLevel = AnonymizationLevel.STANDARD
    ):
        """
        Initialize an anonymization policy.
        
        Args:
            policy_id: Unique identifier for the policy
            name: Human-readable name
            description: Description of the policy
            default_level: Default anonymization level
        """
        self.policy_id = policy_id or str(uuid.uuid4())
        self.name = name or f"Policy-{self.policy_id[:8]}"
        self.description = description
        self.default_level = default_level
        self.rules = {}
        self.field_mappings = {}
        
        logger.info(f"Anonymization Policy {self.name} initialized")
    
    def add_rule(
        self,
        data_category: DataCategory,
        anonymization_method: AnonymizationMethod,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Add a rule for anonymizing a category of data.
        
        Args:
            data_category: Category of data
            anonymization_method: Method to use
            parameters: Additional parameters for the method
        """
        self.rules[data_category] = {
            'method': anonymization_method,
            'parameters': parameters or {}
        }
        
        logger.info(f"Added rule for {data_category.value} using {anonymization_method.value}")
    
    def map_field(
        self,
        field_path: str,
        data_category: DataCategory,
        pii_type: Optional[PIIType] = None,
        override_method: Optional[AnonymizationMethod] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Map a specific field to a data category and optionally override the method.
        
        Args:
            field_path: Path to the field (e.g., "user.contact.email")
            data_category: Category of data
            pii_type: Type of PII (if applicable)
            override_method: Method to use (overrides category rule)
            parameters: Additional parameters for the method
        """
        self.field_mappings[field_path] = {
            'category': data_category,
            'pii_type': pii_type,
            'method': override_method,
            'parameters': parameters or {}
        }
        
        logger.info(f"Mapped field {field_path} to {data_category.value}")
    
    def get_field_anonymization_rule(
        self,
        field_path: str
    ) -> Dict[str, Any]:
        """
        Get the anonymization rule for a specific field.
        
        Args:
            field_path: Path to the field
        
        Returns:
            Dict: Anonymization rule
        
        Raises:
            AnonymizationPolicyError: If no rule is found
        """
        # Check if field has a specific mapping
        if field_path in self.field_mappings:
            mapping = self.field_mappings[field_path]
            category = mapping['category']
            
            # If method is overridden, use it
            if mapping['method']:
                return {
                    'method': mapping['method'],
                    'parameters': mapping['parameters'],
                    'pii_type': mapping['pii_type']
                }
            
            # Otherwise, use the category rule
            if category in self.rules:
                rule = self.rules[category].copy()
                rule['parameters'] = {**rule['parameters'], **mapping['parameters']}
                rule['pii_type'] = mapping['pii_type']
                return rule
        
        # If no specific rule, try to infer from field name
        for category, rule in self.rules.items():
            if category == DataCategory.DIRECT_IDENTIFIER and any(
                identifier in field_path.lower() 
                for identifier in ['name', 'email', 'phone', 'ssn', 'address', 'id']
            ):
                return {**rule, 'pii_type': None}
            elif category == DataCategory.QUASI_IDENTIFIER and any(
                identifier in field_path.lower() 
                for identifier in ['zip', 'postal', 'birth', 'age', 'gender', 'race', 'ethnicity']
            ):
                return {**rule, 'pii_type': None}
            elif category == DataCategory.SENSITIVE_ATTRIBUTE and any(
                identifier in field_path.lower() 
                for identifier in ['health', 'medical', 'salary', 'income', 'religion', 'politics']
            ):
                return {**rule, 'pii_type': None}
        
        # If no rule is found, raise an error
        raise AnonymizationPolicyError(f"No anonymization rule found for field {field_path}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary for serialization."""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'default_level': self.default_level.value,
            'rules': {
                category.value: {
                    'method': rule['method'].value,
                    'parameters': rule['parameters']
                }
                for category, rule in self.rules.items()
            },
            'field_mappings': {
                field: {
                    'category': mapping['category'].value,
                    'pii_type': mapping['pii_type'].value if mapping['pii_type'] else None,
                    'method': mapping['method'].value if mapping['method'] else None,
                    'parameters': mapping['parameters']
                }
                for field, mapping in self.field_mappings.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnonymizationPolicy':
        """Create policy from dictionary."""
        policy = cls(
            policy_id=data['policy_id'],
            name=data['name'],
            description=data['description'],
            default_level=AnonymizationLevel(data['default_level'])
        )
        
        # Add rules
        for category_value, rule_data in data['rules'].items():
            policy.add_rule(
                DataCategory(category_value),
                AnonymizationMethod(rule_data['method']),
                rule_data['parameters']
            )
        
        # Add field mappings
        for field, mapping_data in data['field_mappings'].items():
            policy.map_field(
                field,
                DataCategory(mapping_data['category']),
                PIIType(mapping_data['pii_type']) if mapping_data['pii_type'] else None,
                AnonymizationMethod(mapping_data['method']) if mapping_data['method'] else None,
                mapping_data['parameters']
            )
        
        return policy

class DataAnonymizer:
    """
    Service for anonymizing data.
    
    This class provides methods for anonymizing data according to
    policies, including various anonymization techniques.
    """
    
    def __init__(
        self,
        pii_detector: Optional[PIIDetector] = None,
        tokenization_service: Optional[TokenizationService] = None,
        crypto_core: Optional[CryptoCore] = None
    ):
        """
        Initialize the data anonymizer.
        
        Args:
            pii_detector: PIIDetector instance
            tokenization_service: TokenizationService instance
            crypto_core: CryptoCore instance
        """
        self._pii_detector = pii_detector or PIIDetector()
        self._tokenization = tokenization_service or TokenizationService()
        self._crypto = crypto_core or CryptoCore()
        self._policies = {}
        
        logger.info("Data Anonymizer initialized")
    
    def add_policy(self, policy: AnonymizationPolicy):
        """
        Add an anonymization policy.
        
        Args:
            policy: AnonymizationPolicy instance
        """
        self._policies[policy.policy_id] = policy
        logger.info(f"Added policy {policy.name} ({policy.policy_id})")
    
    def get_policy(self, policy_id: str) -> AnonymizationPolicy:
        """
        Get an anonymization policy by ID.
        
        Args:
            policy_id: Policy ID
        
        Returns:
            AnonymizationPolicy: The policy
        
        Raises:
            AnonymizationPolicyError: If policy is not found
        """
        if policy_id not in self._policies:
            raise AnonymizationPolicyError(f"Policy {policy_id} not found")
        
        return self._policies[policy_id]
    
    def create_standard_policy(self) -> str:
        """
        Create a standard anonymization policy.
        
        Returns:
            str: Policy ID
        """
        policy = AnonymizationPolicy(
            name="Standard Anonymization Policy",
            description="Standard policy for anonymizing common data types",
            default_level=AnonymizationLevel.STANDARD
        )
        
        # Add rules for different data categories
        policy.add_rule(
            DataCategory.DIRECT_IDENTIFIER,
            AnonymizationMethod.TOKENIZATION,
            {'preserve_format': False}
        )
        
        policy.add_rule(
            DataCategory.QUASI_IDENTIFIER,
            AnonymizationMethod.GENERALIZATION,
            {'level': 2}
        )
        
        policy.add_rule(
            DataCategory.SENSITIVE_ATTRIBUTE,
            AnonymizationMethod.PERTURBATION,
            {'noise_level': 0.1}
        )
        
        policy.add_rule(
            DataCategory.NON_SENSITIVE,
            AnonymizationMethod.REDACTION,
            {'replace_with': None}
        )
        
        # Add common field mappings
        policy.map_field("*.name", DataCategory.DIRECT_IDENTIFIER, PIIType.NAME)
        policy.map_field("*.email", DataCategory.DIRECT_IDENTIFIER, PIIType.EMAIL)
        policy.map_field("*.phone", DataCategory.DIRECT_IDENTIFIER, PIIType.PHONE)
        policy.map_field("*.address", DataCategory.DIRECT_IDENTIFIER, PIIType.ADDRESS)
        policy.map_field("*.ssn", DataCategory.DIRECT_IDENTIFIER, PIIType.SSN)
        policy.map_field("*.credit_card", DataCategory.DIRECT_IDENTIFIER, PIIType.CREDIT_CARD)
        policy.map_field("*.ip_address", DataCategory.DIRECT_IDENTIFIER, PIIType.IP_ADDRESS)
        policy.map_field("*.dob", DataCategory.QUASI_IDENTIFIER, PIIType.DOB)
        policy.map_field("*.age", DataCategory.QUASI_IDENTIFIER)
        policy.map_field("*.zip", DataCategory.QUASI_IDENTIFIER)
        policy.map_field("*.postal_code", DataCategory.QUASI_IDENTIFIER)
        policy.map_field("*.gender", DataCategory.QUASI_IDENTIFIER)
        policy.map_field("*.race", DataCategory.QUASI_IDENTIFIER)
        policy.map_field("*.ethnicity", DataCategory.QUASI_IDENTIFIER)
        policy.map_field("*.salary", DataCategory.SENSITIVE_ATTRIBUTE)
        policy.map_field("*.income", DataCategory.SENSITIVE_ATTRIBUTE)
        policy.map_field("*.health", DataCategory.SENSITIVE_ATTRIBUTE)
        policy.map_field("*.medical", DataCategory.SENSITIVE_ATTRIBUTE)
        policy.map_field("*.religion", DataCategory.SENSITIVE_ATTRIBUTE)
        policy.map_field("*.politics", DataCategory.SENSITIVE_ATTRIBUTE)
        
        # Add the policy
        self.add_policy(policy)
        
        return policy.policy_id
    
    def _apply_anonymization_method(
        self,
        value: Any,
        method: AnonymizationMethod,
        parameters: Dict[str, Any],
        pii_type: Optional[PIIType] = None,
        field_path: Optional[str] = None
    ) -> Any:
        """
        Apply an anonymization method to a value.
        
        Args:
            value: Value to anonymize
            method: Anonymization method
            parameters: Method parameters
            pii_type: Type of PII
            field_path: Path to the field
        
        Returns:
            Any: Anonymized value
        
        Raises:
            AnonymizationError: If anonymization fails
        """
        try:
            if method == AnonymizationMethod.REDACTION:
                replace_with = parameters.get('replace_with', None)
                return replace_with
            
            elif method == AnonymizationMethod.MASKING:
                mask_char = parameters.get('mask_char', '*')
                preserve_length = parameters.get('preserve_length', True)
                num_visible = parameters.get('num_visible', 0)
                
                if not isinstance(value, str):
                    return value
                
                if num_visible <= 0:
                    return mask_char * len(value) if preserve_length else mask_char
                
                # Keep some characters visible
                visible_start = parameters.get('visible_start', False)
                if visible_start:
                    return value[:num_visible] + mask_char * (len(value) - num_visible)
                else:
                    return mask_char * (len(value) - num_visible) + value[-num_visible:]
            
            elif method == AnonymizationMethod.TOKENIZATION:
                preserve_format = parameters.get('preserve_format', False)
                
                if not isinstance(value, str):
                    return value
                
                return self._tokenization.tokenize(
                    value,
                    pii_type,
                    {'field_path': field_path} if field_path else None,
                    preserve_format
                )
            
            elif method == AnonymizationMethod.GENERALIZATION:
                level = parameters.get('level', 1)
                
                if not isinstance(value, (str, int, float)):
                    return value
                
                # Handle different types of values
                if isinstance(value, int) or isinstance(value, float):
                    # For numeric values, round to nearest multiple of 10^level
                    multiplier = 10 ** level
                    return round(value / multiplier) * multiplier
                
                elif pii_type == PIIType.DOB or any(date_part in field_path.lower() for date_part in ['date', 'dob', 'birth']):
                    # For dates, generalize based on level
                    if level == 1:
                        # Keep year and month
                        parts = value.split('/')
                        if len(parts) == 3:
                            return f"{parts[0]}/{parts[1]}/XXXX"
                    elif level == 2:
                        # Keep only year
                        parts = value.split('/')
                        if len(parts) == 3:
                            return f"XX/XX/{parts[2]}"
                    else:
                        # Redact completely
                        return "XX/XX/XXXX"
                
                elif pii_type == PIIType.ADDRESS or 'address' in field_path.lower():
                    # For addresses, generalize based on level
                    if level == 1:
                        # Remove house number
                        parts = value.split(' ', 1)
                        if len(parts) > 1 and parts[0].isdigit():
                            return parts[1]
                    elif level == 2:
                        # Keep only city and state/country
                        parts = value.split(',')
                        if len(parts) >= 2:
                            return parts[-2].strip() + ', ' + parts[-1].strip()
                    else:
                        # Redact completely
                        return "REDACTED ADDRESS"
                
                # Default generalization for strings
                return value[:max(1, len(value) // (level * 2))] + "..."
            
            elif method == AnonymizationMethod.PERTURBATION:
                noise_level = parameters.get('noise_level', 0.1)
                
                if not isinstance(value, (int, float)):
                    return value
                
                # Add random noise
                noise = value * noise_level * (2 * random.random() - 1)
                result = value + noise
                
                # Round to same precision as original
                if isinstance(value, int):
                    return int(round(result))
                else:
                    # Determine original precision
                    str_value = str(value)
                    if '.' in str_value:
                        decimals = len(str_value.split('.')[1])
                        return round(result, decimals)
                    else:
                        return round(result)
            
            elif method == AnonymizationMethod.SYNTHETIC:
                # This is a simplified implementation
                # A real system would use more sophisticated synthetic data generation
                
                if pii_type == PIIType.NAME:
                    return "John Doe"
                elif pii_type == PIIType.EMAIL:
                    return "user@example.com"
                elif pii_type == PIIType.PHONE:
                    return "(555) 123-4567"
                elif pii_type == PIIType.ADDRESS:
                    return "123 Main St, Anytown, USA"
                elif pii_type == PIIType.SSN:
                    return "123-45-6789"
                elif pii_type == PIIType.CREDIT_CARD:
                    return "4111-1111-1111-1111"
                elif pii_type == PIIType.DOB:
                    return "01/01/1980"
                elif isinstance(value, int):
                    return random.randint(value // 2, value * 2)
                elif isinstance(value, float):
                    return value * (0.5 + random.random())
                else:
                    return "SYNTHETIC_DATA"
            
            # If no method matched or value couldn't be processed, return as is
            return value
        
        except Exception as e:
            logger.error(f"Anonymization method application failed: {str(e)}")
            raise AnonymizationError(f"Anonymization method application failed: {str(e)}")
    
    def anonymize_value(
        self,
        value: Any,
        policy_id: str,
        field_path: str
    ) -> Any:
        """
        Anonymize a single value using a policy.
        
        Args:
            value: Value to anonymize
            policy_id: ID of the policy to use
            field_path: Path to the field
        
        Returns:
            Any: Anonymized value
        
        Raises:
            AnonymizationError: If anonymization fails
        """
        try:
            # Get the policy
            policy = self.get_policy(policy_id)
            
            # Get the rule for this field
            try:
                rule = policy.get_field_anonymization_rule(field_path)
            except AnonymizationPolicyError:
                # If no rule is found, return the value as is
                return value
            
            # Apply the anonymization method
            return self._apply_anonymization_method(
                value,
                rule['method'],
                rule['parameters'],
                rule.get('pii_type'),
                field_path
            )
        except Exception as e:
            logger.error(f"Value anonymization failed: {str(e)}")
            raise AnonymizationError(f"Value anonymization failed: {str(e)}")
    
    def anonymize_dict(
        self,
        data: Dict[str, Any],
        policy_id: str,
        prefix: str = ""
    ) -> Dict[str, Any]:
        """
        Anonymize a dictionary using a policy.
        
        Args:
            data: Dictionary to anonymize
            policy_id: ID of the policy to use
            prefix: Prefix for field paths
        
        Returns:
            Dict: Anonymized dictionary
        
        Raises:
            AnonymizationError: If anonymization fails
        """
        try:
            result = {}
            
            for key, value in data.items():
                field_path = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    # Recursively anonymize nested dictionaries
                    result[key] = self.anonymize_dict(value, policy_id, field_path)
                elif isinstance(value, list):
                    # Anonymize lists
                    result[key] = [
                        self.anonymize_dict(item, policy_id, f"{field_path}[{i}]")
                        if isinstance(item, dict)
                        else self.anonymize_value(item, policy_id, f"{field_path}[{i}]")
                        for i, item in enumerate(value)
                    ]
                else:
                    # Anonymize scalar values
                    result[key] = self.anonymize_value(value, policy_id, field_path)
            
            return result
        except Exception as e:
            logger.error(f"Dictionary anonymization failed: {str(e)}")
            raise AnonymizationError(f"Dictionary anonymization failed: {str(e)}")
    
    def anonymize_text(
        self,
        text: str,
        policy_id: str
    ) -> str:
        """
        Anonymize text by detecting and anonymizing PII.
        
        Args:
            text: Text to anonymize
            policy_id: ID of the policy to use
        
        Returns:
            str: Anonymized text
        
        Raises:
            AnonymizationError: If anonymization fails
        """
        try:
            # Detect PII in the text
            detected_pii = self._pii_detector.detect_pii(text)
            
            # Sort PII by position in reverse order to avoid offset issues
            detected_pii.sort(key=lambda x: x['start'], reverse=True)
            
            # Create a mutable copy of the text
            result = list(text)
            
            # Get the policy
            policy = self.get_policy(policy_id)
            
            # Process each detected PII
            for pii in detected_pii:
                pii_type = PIIType(pii['type'])
                pii_value = pii['value']
                start = pii['start']
                end = pii['end']
                
                # Find the appropriate rule
                try:
                    # Try to find a rule for this PII type
                    field_path = f"*.{pii_type.value}"
                    rule = policy.get_field_anonymization_rule(field_path)
                except AnonymizationPolicyError:
                    # If no rule is found, use the direct identifier rule
                    try:
                        rule = policy.rules.get(DataCategory.DIRECT_IDENTIFIER, {})
                        if not rule:
                            continue
                    except:
                        continue
                
                # Apply the anonymization method
                anonymized = self._apply_anonymization_method(
                    pii_value,
                    rule['method'],
                    rule['parameters'],
                    pii_type
                )
                
                # Replace the PII in the result
                result[start:end] = anonymized
            
            return ''.join(result)
        except Exception as e:
            logger.error(f"Text anonymization failed: {str(e)}")
            raise AnonymizationError(f"Text anonymization failed: {str(e)}")
    
    def anonymize_dataset(
        self,
        data: List[Dict[str, Any]],
        policy_id: str
    ) -> List[Dict[str, Any]]:
        """
        Anonymize a dataset (list of dictionaries).
        
        Args:
            data: Dataset to anonymize
            policy_id: ID of the policy to use
        
        Returns:
            List[Dict]: Anonymized dataset
        
        Raises:
            AnonymizationError: If anonymization fails
        """
        try:
            return [self.anonymize_dict(item, policy_id) for item in data]
        except Exception as e:
            logger.error(f"Dataset anonymization failed: {str(e)}")
            raise AnonymizationError(f"Dataset anonymization failed: {str(e)}")

class DifferentialPrivacy:
    """
    Implementation of differential privacy techniques.
    
    This class provides methods for adding noise to queries and
    aggregations to preserve privacy while allowing statistical analysis.
    """
    
    def __init__(self, epsilon: float = 1.0):
        """
        Initialize the differential privacy service.
        
        Args:
            epsilon: Privacy parameter (smaller values provide more privacy)
        """
        self.epsilon = epsilon
        logger.info(f"Differential Privacy initialized with epsilon={epsilon}")
    
    def add_laplace_noise(self, value: float, sensitivity: float) -> float:
        """
        Add Laplace noise to a numeric value.
        
        Args:
            value: Original value
            sensitivity: Sensitivity of the query
        
        Returns:
            float: Value with noise added
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise
    
    def noisy_count(self, count: int, sensitivity: int = 1) -> int:
        """
        Add noise to a count query.
        
        Args:
            count: Original count
            sensitivity: Sensitivity of the count
        
        Returns:
            int: Noisy count
        """
        noisy = self.add_laplace_noise(count, sensitivity)
        return max(0, int(round(noisy)))
    
    def noisy_sum(self, values: List[float], sensitivity: float) -> float:
        """
        Add noise to a sum query.
        
        Args:
            values: Values to sum
            sensitivity: Sensitivity of the sum
        
        Returns:
            float: Noisy sum
        """
        original_sum = sum(values)
        return self.add_laplace_noise(original_sum, sensitivity)
    
    def noisy_average(self, values: List[float], sensitivity: float) -> float:
        """
        Add noise to an average query.
        
        Args:
            values: Values to average
            sensitivity: Sensitivity of the average
        
        Returns:
            float: Noisy average
        """
        if not values:
            return 0
        
        count = len(values)
        noisy_sum = self.noisy_sum(values, sensitivity)
        return noisy_sum / count
    
    def noisy_histogram(
        self,
        data: List[Any],
        bins: Optional[List[Any]] = None,
        sensitivity: int = 1
    ) -> Dict[Any, int]:
        """
        Create a noisy histogram.
        
        Args:
            data: Data points
            bins: Bin categories (if None, uses unique values)
            sensitivity: Sensitivity of the histogram
        
        Returns:
            Dict: Mapping of bins to noisy counts
        """
        # Create bins if not provided
        if bins is None:
            bins = list(set(data))
        
        # Count occurrences in each bin
        counts = {bin_val: data.count(bin_val) for bin_val in bins}
        
        # Add noise to each count
        noisy_counts = {
            bin_val: self.noisy_count(count, sensitivity)
            for bin_val, count in counts.items()
        }
        
        return noisy_counts
    
    def private_quantile(
        self,
        data: List[float],
        quantile: float,
        sensitivity: float,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> float:
        """
        Compute a differentially private quantile.
        
        Args:
            data: Data points
            quantile: Quantile to compute (0-1)
            sensitivity: Sensitivity of the quantile
            min_val: Minimum possible value
            max_val: Maximum possible value
        
        Returns:
            float: Noisy quantile
        """
        if not data:
            return 0
        
        # Determine min and max if not provided
        if min_val is None:
            min_val = min(data)
        if max_val is None:
            max_val = max(data)
        
        # Compute the true quantile
        sorted_data = sorted(data)
        index = int(quantile * (len(sorted_data) - 1))
        true_quantile = sorted_data[index]
        
        # Scale sensitivity to the range
        range_size = max_val - min_val
        scaled_sensitivity = sensitivity * range_size
        
        # Add noise
        noisy_quantile = self.add_laplace_noise(true_quantile, scaled_sensitivity)
        
        # Clamp to range
        return max(min_val, min(noisy_quantile, max_val))

class PrivacyPreservingAnalytics:
    """
    Service for privacy-preserving analytics.
    
    This class provides methods for performing analytics on data
    while preserving privacy through anonymization and differential privacy.
    """
    
    def __init__(
        self,
        anonymizer: Optional[DataAnonymizer] = None,
        differential_privacy: Optional[DifferentialPrivacy] = None
    ):
        """
        Initialize the privacy-preserving analytics service.
        
        Args:
            anonymizer: DataAnonymizer instance
            differential_privacy: DifferentialPrivacy instance
        """
        self._anonymizer = anonymizer or DataAnonymizer()
        self._dp = differential_privacy or DifferentialPrivacy()
        
        logger.info("Privacy-Preserving Analytics initialized")
    
    def analyze_dataset(
        self,
        data: List[Dict[str, Any]],
        policy_id: str,
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a dataset with privacy preservation.
        
        Args:
            data: Dataset to analyze
            policy_id: ID of the anonymization policy to use
            metrics: List of metrics to compute
        
        Returns:
            Dict: Analysis results
        
        Raises:
            AnonymizationError: If analysis fails
        """
        try:
            # Anonymize the dataset
            anonymized_data = self._anonymizer.anonymize_dataset(data, policy_id)
            
            results = {}
            
            # Compute each requested metric
            for metric in metrics:
                metric_type = metric['type']
                field = metric.get('field')
                
                if metric_type == 'count':
                    # Count records
                    count = len(anonymized_data)
                    results[f'count'] = self._dp.noisy_count(count)
                
                elif metric_type == 'sum' and field:
                    # Sum a field
                    values = [
                        item.get(field, 0)
                        for item in anonymized_data
                        if isinstance(item.get(field), (int, float))
                    ]
                    
                    sensitivity = metric.get('sensitivity', 1.0)
                    results[f'sum_{field}'] = self._dp.noisy_sum(values, sensitivity)
                
                elif metric_type == 'average' and field:
                    # Average a field
                    values = [
                        item.get(field, 0)
                        for item in anonymized_data
                        if isinstance(item.get(field), (int, float))
                    ]
                    
                    sensitivity = metric.get('sensitivity', 1.0)
                    results[f'avg_{field}'] = self._dp.noisy_average(values, sensitivity)
                
                elif metric_type == 'histogram' and field:
                    # Create a histogram
                    values = [item.get(field) for item in anonymized_data if field in item]
                    bins = metric.get('bins')
                    sensitivity = metric.get('sensitivity', 1)
                    
                    results[f'histogram_{field}'] = self._dp.noisy_histogram(
                        values, bins, sensitivity
                    )
                
                elif metric_type == 'quantile' and field:
                    # Compute a quantile
                    values = [
                        item.get(field, 0)
                        for item in anonymized_data
                        if isinstance(item.get(field), (int, float))
                    ]
                    
                    quantile = metric.get('quantile', 0.5)
                    sensitivity = metric.get('sensitivity', 1.0)
                    min_val = metric.get('min_val')
                    max_val = metric.get('max_val')
                    
                    results[f'quantile_{quantile}_{field}'] = self._dp.private_quantile(
                        values, quantile, sensitivity, min_val, max_val
                    )
            
            return results
        except Exception as e:
            logger.error(f"Privacy-preserving analysis failed: {str(e)}")
            raise AnonymizationError(f"Privacy-preserving analysis failed: {str(e)}")
    
    def generate_synthetic_dataset(
        self,
        data: List[Dict[str, Any]],
        schema: Dict[str, Any],
        num_records: int
    ) -> List[Dict[str, Any]]:
        """
        Generate a synthetic dataset based on original data.
        
        Args:
            data: Original dataset
            schema: Schema describing the data
            num_records: Number of synthetic records to generate
        
        Returns:
            List[Dict]: Synthetic dataset
        
        Raises:
            AnonymizationError: If generation fails
        """
        try:
            # This is a simplified implementation
            # A real system would use more sophisticated techniques
            
            synthetic_data = []
            
            # Extract field distributions
            distributions = {}
            
            for field, field_schema in schema.items():
                field_type = field_schema.get('type', 'string')
                
                if field_type in ['string', 'category']:
                    # For categorical fields, compute frequency distribution
                    values = [item.get(field) for item in data if field in item]
                    unique_values = list(set(values))
                    counts = {val: values.count(val) for val in unique_values}
                    total = sum(counts.values())
                    probabilities = {val: count / total for val, count in counts.items()}
                    
                    distributions[field] = {
                        'type': field_type,
                        'values': unique_values,
                        'probabilities': probabilities
                    }
                
                elif field_type in ['integer', 'float']:
                    # For numeric fields, compute min, max, mean, std
                    values = [
                        item.get(field)
                        for item in data
                        if field in item and isinstance(item.get(field), (int, float))
                    ]
                    
                    if values:
                        min_val = min(values)
                        max_val = max(values)
                        mean = sum(values) / len(values)
                        std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
                        
                        distributions[field] = {
                            'type': field_type,
                            'min': min_val,
                            'max': max_val,
                            'mean': mean,
                            'std': std
                        }
                
                elif field_type == 'boolean':
                    # For boolean fields, compute probability of True
                    values = [item.get(field) for item in data if field in item]
                    true_count = sum(1 for v in values if v)
                    prob_true = true_count / len(values) if values else 0.5
                    
                    distributions[field] = {
                        'type': field_type,
                        'prob_true': prob_true
                    }
            
            # Generate synthetic records
            for _ in range(num_records):
                record = {}
                
                for field, dist in distributions.items():
                    field_type = dist['type']
                    
                    if field_type in ['string', 'category']:
                        # Sample from categorical distribution
                        values = dist['values']
                        probabilities = list(dist['probabilities'].values())
                        record[field] = np.random.choice(values, p=probabilities)
                    
                    elif field_type == 'integer':
                        # Sample from normal distribution and round
                        mean = dist['mean']
                        std = dist['std']
                        min_val = dist['min']
                        max_val = dist['max']
                        
                        value = int(round(np.random.normal(mean, std)))
                        record[field] = max(min_val, min(value, max_val))
                    
                    elif field_type == 'float':
                        # Sample from normal distribution
                        mean = dist['mean']
                        std = dist['std']
                        min_val = dist['min']
                        max_val = dist['max']
                        
                        value = np.random.normal(mean, std)
                        record[field] = max(min_val, min(value, max_val))
                    
                    elif field_type == 'boolean':
                        # Sample from Bernoulli distribution
                        prob_true = dist['prob_true']
                        record[field] = random.random() < prob_true
                
                synthetic_data.append(record)
            
            return synthetic_data
        except Exception as e:
            logger.error(f"Synthetic dataset generation failed: {str(e)}")
            raise AnonymizationError(f"Synthetic dataset generation failed: {str(e)}")

class DataAnonymizationService:
    """
    Main service for data anonymization.
    
    This class provides a unified interface for all anonymization
    operations, including PII detection, tokenization, anonymization,
    and privacy-preserving analytics.
    """
    
    def __init__(
        self,
        pii_detector: Optional[PIIDetector] = None,
        tokenization_service: Optional[TokenizationService] = None,
        data_anonymizer: Optional[DataAnonymizer] = None,
        privacy_analytics: Optional[PrivacyPreservingAnalytics] = None
    ):
        """
        Initialize the data anonymization service.
        
        Args:
            pii_detector: PIIDetector instance
            tokenization_service: TokenizationService instance
            data_anonymizer: DataAnonymizer instance
            privacy_analytics: PrivacyPreservingAnalytics instance
        """
        self._pii_detector = pii_detector or PIIDetector()
        self._tokenization = tokenization_service or TokenizationService()
        self._anonymizer = data_anonymizer or DataAnonymizer()
        self._analytics = privacy_analytics or PrivacyPreservingAnalytics(self._anonymizer)
        
        # Create a standard policy if none exists
        self._standard_policy_id = self._anonymizer.create_standard_policy()
        
        logger.info("Data Anonymization Service initialized")
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text.
        
        Args:
            text: Text to analyze
        
        Returns:
            List[Dict]: Detected PII
        """
        return self._pii_detector.detect_pii(text)
    
    def detect_pii_in_dict(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect PII in a dictionary.
        
        Args:
            data: Dictionary to analyze
        
        Returns:
            Dict: Detected PII by field
        """
        return self._pii_detector.detect_pii_in_dict(data)
    
    def tokenize(
        self,
        value: str,
        data_type: Optional[PIIType] = None,
        preserve_format: bool = False
    ) -> str:
        """
        Tokenize a sensitive value.
        
        Args:
            value: Value to tokenize
            data_type: Type of data
            preserve_format: Whether to preserve format
        
        Returns:
            str: Tokenized value
        """
        return self._tokenization.tokenize(value, data_type, None, preserve_format)
    
    def detokenize(self, token: str, requester: Optional[str] = None) -> str:
        """
        Detokenize a token.
        
        Args:
            token: Token to detokenize
            requester: Entity requesting detokenization
        
        Returns:
            str: Original value
        """
        return self._tokenization.detokenize(token, requester)
    
    def tokenize_dict(
        self,
        data: Dict[str, Any],
        fields_to_tokenize: Dict[str, PIIType],
        preserve_format: bool = False
    ) -> Dict[str, Any]:
        """
        Tokenize fields in a dictionary.
        
        Args:
            data: Dictionary to tokenize
            fields_to_tokenize: Fields to tokenize with their types
            preserve_format: Whether to preserve format
        
        Returns:
            Dict: Tokenized dictionary
        """
        return self._tokenization.tokenize_dict(data, fields_to_tokenize, preserve_format)
    
    def detokenize_dict(
        self,
        data: Dict[str, Any],
        fields_to_detokenize: List[str],
        requester: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detokenize fields in a dictionary.
        
        Args:
            data: Dictionary to detokenize
            fields_to_detokenize: Fields to detokenize
            requester: Entity requesting detokenization
        
        Returns:
            Dict: Detokenized dictionary
        """
        return self._tokenization.detokenize_dict(data, fields_to_detokenize, requester)
    
    def create_anonymization_policy(
        self,
        name: str,
        description: Optional[str] = None,
        default_level: AnonymizationLevel = AnonymizationLevel.STANDARD
    ) -> str:
        """
        Create a new anonymization policy.
        
        Args:
            name: Policy name
            description: Policy description
            default_level: Default anonymization level
        
        Returns:
            str: Policy ID
        """
        policy = AnonymizationPolicy(name=name, description=description, default_level=default_level)
        self._anonymizer.add_policy(policy)
        return policy.policy_id
    
    def get_standard_policy_id(self) -> str:
        """
        Get the ID of the standard anonymization policy.
        
        Returns:
            str: Policy ID
        """
        return self._standard_policy_id
    
    def anonymize_text(self, text: str, policy_id: Optional[str] = None) -> str:
        """
        Anonymize text.
        
        Args:
            text: Text to anonymize
            policy_id: Policy ID (uses standard policy if None)
        
        Returns:
            str: Anonymized text
        """
        policy_id = policy_id or self._standard_policy_id
        return self._anonymizer.anonymize_text(text, policy_id)
    
    def anonymize_dict(
        self,
        data: Dict[str, Any],
        policy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Anonymize a dictionary.
        
        Args:
            data: Dictionary to anonymize
            policy_id: Policy ID (uses standard policy if None)
        
        Returns:
            Dict: Anonymized dictionary
        """
        policy_id = policy_id or self._standard_policy_id
        return self._anonymizer.anonymize_dict(data, policy_id)
    
    def anonymize_dataset(
        self,
        data: List[Dict[str, Any]],
        policy_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Anonymize a dataset.
        
        Args:
            data: Dataset to anonymize
            policy_id: Policy ID (uses standard policy if None)
        
        Returns:
            List[Dict]: Anonymized dataset
        """
        policy_id = policy_id or self._standard_policy_id
        return self._anonymizer.anonymize_dataset(data, policy_id)
    
    def analyze_dataset(
        self,
        data: List[Dict[str, Any]],
        metrics: List[Dict[str, Any]],
        policy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a dataset with privacy preservation.
        
        Args:
            data: Dataset to analyze
            metrics: Metrics to compute
            policy_id: Policy ID (uses standard policy if None)
        
        Returns:
            Dict: Analysis results
        """
        policy_id = policy_id or self._standard_policy_id
        return self._analytics.analyze_dataset(data, policy_id, metrics)
    
    def generate_synthetic_dataset(
        self,
        data: List[Dict[str, Any]],
        schema: Dict[str, Any],
        num_records: int
    ) -> List[Dict[str, Any]]:
        """
        Generate a synthetic dataset.
        
        Args:
            data: Original dataset
            schema: Data schema
            num_records: Number of records to generate
        
        Returns:
            List[Dict]: Synthetic dataset
        """
        return self._analytics.generate_synthetic_dataset(data, schema, num_records)
