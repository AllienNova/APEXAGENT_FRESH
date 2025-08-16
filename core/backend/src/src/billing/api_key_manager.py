"""
API Key Management module for ApexAgent.

This module handles storage, validation, and usage tracking of user-provided API keys
for various LLM providers.
"""

import os
import json
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ProviderType(Enum):
    """Enumeration of supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    COHERE = "cohere"
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"
    AWS_BEDROCK = "aws_bedrock"


class ModelCategory(Enum):
    """Enumeration of model categories."""
    STANDARD = "standard"
    HIGH_REASONING = "high_reasoning"


class ApiKeyManager:
    """Manages API keys for various LLM providers."""

    def __init__(self, database_connector, encryption_key=None):
        """Initialize the API key manager.
        
        Args:
            database_connector: Connection to the database
            encryption_key: Key used for encrypting API keys (generated if not provided)
        """
        self.db = database_connector
        self._initialize_encryption(encryption_key)
        self._initialize_provider_config()
    
    def _initialize_encryption(self, encryption_key=None):
        """Initialize encryption for API keys.
        
        Args:
            encryption_key: Key used for encrypting API keys (generated if not provided)
        """
        if encryption_key:
            # Ensure the encryption key is properly formatted for Fernet
            try:
                # If it's already a valid Fernet key, use it directly
                Fernet(encryption_key)
                self.encryption_key = encryption_key
            except Exception:
                # If not, convert it to a valid Fernet key
                if isinstance(encryption_key, bytes):
                    key_material = encryption_key
                else:
                    key_material = str(encryption_key).encode()
                
                # Generate a proper Fernet key using PBKDF2
                salt = b'apexagent_salt'  # Fixed salt for reproducibility in tests
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                derived_key = kdf.derive(key_material)
                self.encryption_key = base64.urlsafe_b64encode(derived_key)
        else:
            # Generate a key from environment or create a new one
            env_key = os.environ.get("APEX_ENCRYPTION_KEY")
            if env_key:
                try:
                    # Try to use the environment key directly
                    Fernet(env_key.encode())
                    self.encryption_key = env_key.encode()
                except Exception:
                    # Convert to a valid Fernet key
                    salt = b'apexagent_salt'
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                    )
                    derived_key = kdf.derive(env_key.encode())
                    self.encryption_key = base64.urlsafe_b64encode(derived_key)
            else:
                # Generate a new key that's properly formatted for Fernet
                self.encryption_key = base64.urlsafe_b64encode(os.urandom(32))
                
                # In production, this key should be stored securely
                # For now, we'll just print a warning
                print("WARNING: Generated new encryption key. This should be stored securely.")
                print(f"APEX_ENCRYPTION_KEY={self.encryption_key.decode()}")
        
        # Initialize Fernet cipher for encryption/decryption
        self.cipher = Fernet(self.encryption_key)
    
    def _initialize_provider_config(self):
        """Initialize configuration for supported providers."""
        self.provider_config = {
            ProviderType.OPENAI: {
                "validation_url": "https://api.openai.com/v1/models",
                "header_name": "Authorization",
                "header_format": "Bearer {key}",
                "test_endpoint": "https://api.openai.com/v1/models",
                "rate_limits": {
                    "requests_per_minute": 60,
                    "tokens_per_minute": 90000
                },
                "models": {
                    "gpt-3.5-turbo": ModelCategory.STANDARD,
                    "gpt-4": ModelCategory.HIGH_REASONING,
                    "gpt-4-turbo": ModelCategory.HIGH_REASONING
                }
            },
            ProviderType.ANTHROPIC: {
                "validation_url": "https://api.anthropic.com/v1/messages",
                "header_name": "x-api-key",
                "header_format": "{key}",
                "test_endpoint": "https://api.anthropic.com/v1/models",
                "rate_limits": {
                    "requests_per_minute": 50,
                    "tokens_per_minute": 100000
                },
                "models": {
                    "claude-instant-1": ModelCategory.STANDARD,
                    "claude-2": ModelCategory.HIGH_REASONING,
                    "claude-3-opus": ModelCategory.HIGH_REASONING,
                    "claude-3-sonnet": ModelCategory.HIGH_REASONING,
                    "claude-3-haiku": ModelCategory.STANDARD
                }
            },
            ProviderType.GOOGLE: {
                "validation_url": "https://generativelanguage.googleapis.com/v1/models",
                "header_name": "x-goog-api-key",
                "header_format": "{key}",
                "test_endpoint": "https://generativelanguage.googleapis.com/v1/models",
                "rate_limits": {
                    "requests_per_minute": 60,
                    "tokens_per_minute": 120000
                },
                "models": {
                    "gemini-pro": ModelCategory.STANDARD,
                    "gemini-ultra": ModelCategory.HIGH_REASONING
                }
            },
            ProviderType.META: {
                "validation_url": "https://api.meta.ai/v1/models",
                "header_name": "Authorization",
                "header_format": "Bearer {key}",
                "test_endpoint": "https://api.meta.ai/v1/models",
                "rate_limits": {
                    "requests_per_minute": 40,
                    "tokens_per_minute": 80000
                },
                "models": {
                    "llama-2-7b": ModelCategory.STANDARD,
                    "llama-2-13b": ModelCategory.STANDARD,
                    "llama-2-70b": ModelCategory.HIGH_REASONING
                }
            },
            ProviderType.COHERE: {
                "validation_url": "https://api.cohere.ai/v1/models",
                "header_name": "Authorization",
                "header_format": "Bearer {key}",
                "test_endpoint": "https://api.cohere.ai/v1/models",
                "rate_limits": {
                    "requests_per_minute": 60,
                    "tokens_per_minute": 90000
                },
                "models": {
                    "command": ModelCategory.STANDARD,
                    "command-light": ModelCategory.STANDARD,
                    "command-r": ModelCategory.HIGH_REASONING
                }
            },
            ProviderType.MISTRAL: {
                "validation_url": "https://api.mistral.ai/v1/models",
                "header_name": "Authorization",
                "header_format": "Bearer {key}",
                "test_endpoint": "https://api.mistral.ai/v1/models",
                "rate_limits": {
                    "requests_per_minute": 50,
                    "tokens_per_minute": 100000
                },
                "models": {
                    "mistral-small": ModelCategory.STANDARD,
                    "mistral-medium": ModelCategory.STANDARD,
                    "mistral-large": ModelCategory.HIGH_REASONING
                }
            },
            ProviderType.AZURE_OPENAI: {
                "validation_url": None,  # Requires endpoint URL
                "header_name": "api-key",
                "header_format": "{key}",
                "test_endpoint": None,  # Requires endpoint URL
                "rate_limits": {
                    "requests_per_minute": 240,
                    "tokens_per_minute": 240000
                },
                "models": {
                    "gpt-35-turbo": ModelCategory.STANDARD,
                    "gpt-4": ModelCategory.HIGH_REASONING,
                    "gpt-4-turbo": ModelCategory.HIGH_REASONING
                }
            },
            ProviderType.AWS_BEDROCK: {
                "validation_url": None,  # Uses AWS SDK
                "header_name": None,     # Uses AWS SDK
                "header_format": None,   # Uses AWS SDK
                "test_endpoint": None,   # Uses AWS SDK
                "rate_limits": {
                    "requests_per_minute": 100,
                    "tokens_per_minute": 150000
                },
                "models": {
                    "amazon.titan-text": ModelCategory.STANDARD,
                    "anthropic.claude-v2": ModelCategory.HIGH_REASONING,
                    "anthropic.claude-3-sonnet": ModelCategory.HIGH_REASONING,
                    "meta.llama2-13b": ModelCategory.STANDARD,
                    "meta.llama2-70b": ModelCategory.HIGH_REASONING
                }
            }
        }
    
    def _encrypt_key(self, api_key: str) -> bytes:
        """Encrypt an API key.
        
        Args:
            api_key: The API key to encrypt
            
        Returns:
            Encrypted API key as bytes
        """
        try:
            return self.cipher.encrypt(api_key.encode())
        except Exception as e:
            raise ValueError(f"Failed to encrypt API key: {str(e)}")
    
    def _decrypt_key(self, encrypted_key: bytes) -> str:
        """Decrypt an API key.
        
        Args:
            encrypted_key: The encrypted API key
            
        Returns:
            Decrypted API key as string
        """
        try:
            return self.cipher.decrypt(encrypted_key).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {str(e)}")
    
    def _generate_key_id(self, user_id: str, provider: ProviderType, api_key: str) -> str:
        """Generate a unique ID for an API key.
        
        Args:
            user_id: Unique identifier for the user
            provider: Provider type for this API key
            api_key: The API key
            
        Returns:
            Unique key ID
        """
        # Create a hash that doesn't expose the actual key
        key_material = f"{user_id}:{provider.value}:{api_key}"
        return hashlib.sha256(key_material.encode()).hexdigest()[:16]
    
    def _validate_key_format(self, provider: ProviderType, api_key: str) -> bool:
        """Validate the format of an API key.
        
        Args:
            provider: Provider type for this API key
            api_key: The API key to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Basic validation based on provider
        if provider == ProviderType.OPENAI:
            if not api_key.startswith("sk-"):
                raise ValueError("OpenAI API keys should start with 'sk-'")
        elif provider == ProviderType.ANTHROPIC:
            if len(api_key) < 20:
                raise ValueError("Anthropic API keys should be at least 20 characters")
        
        # Generic validation
        if len(api_key) < 8:
            raise ValueError("API key is too short")
        
        return True
    
    def _validate_special_provider(self, provider: ProviderType, api_key: str, 
                                  additional_config: Dict[str, Any]) -> bool:
        """Validate API keys for providers that need special handling.
        
        Args:
            provider: Provider type
            api_key: The API key
            additional_config: Additional configuration
            
        Returns:
            True if valid, False otherwise
        """
        if provider == ProviderType.AZURE_OPENAI:
            # Azure OpenAI requires endpoint URL
            endpoint = additional_config.get("endpoint")
            if not endpoint:
                return False
            
            import requests
            headers = {"api-key": api_key}
            try:
                response = requests.get(f"{endpoint}/models", headers=headers, timeout=5)
                return response.status_code == 200
            except Exception:
                return False
                
        elif provider == ProviderType.AWS_BEDROCK:
            # AWS Bedrock uses AWS credentials
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                # Extract AWS credentials
                aws_access_key = api_key
                aws_secret_key = additional_config.get("aws_secret_key")
                region = additional_config.get("region", "us-east-1")
                
                if not aws_secret_key:
                    return False
                
                # Create a Bedrock client
                session = boto3.Session(
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region
                )
                
                bedrock = session.client("bedrock")
                
                # Try to list models
                response = bedrock.list_foundation_models()
                return "modelSummaries" in response
            except (ImportError, ClientError):
                return False
        
        return False
    
    def add_api_key(self, user_id: str, provider: ProviderType, api_key: str, 
                   additional_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add an API key for a user.
        
        Args:
            user_id: Unique identifier for the user
            provider: Provider type for this API key
            api_key: The API key to store
            additional_config: Additional configuration for specific providers
            
        Returns:
            Dictionary with API key details (excluding the actual key)
        """
        try:
            # Validate the API key format
            self._validate_key_format(provider, api_key)
            
            # Encrypt the API key
            encrypted_key = self._encrypt_key(api_key)
            
            # Generate a key ID for reference (without exposing the actual key)
            key_id = self._generate_key_id(user_id, provider, api_key)
            
            # Create API key record
            now = datetime.now()
            
            api_key_data = {
                "user_id": user_id,
                "provider": provider.value,
                "key_id": key_id,
                "encrypted_key": encrypted_key,
                "created_at": now,
                "last_used": None,
                "is_valid": True,
                "usage_count": 0,
                "additional_config": json.dumps(additional_config) if additional_config else None
            }
            
            # Store in database
            record_id = self.db.insert_api_key(api_key_data)
            
            # Return the created record (without the encrypted key)
            result = {k: v for k, v in api_key_data.items() if k != "encrypted_key"}
            result["id"] = record_id
            return result
        except Exception as e:
            raise ValueError(f"Failed to add API key: {str(e)}")
    
    def get_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of API key details (excluding the actual keys)
        """
        try:
            keys = self.db.get_user_api_keys(user_id)
            
            # Remove encrypted keys from results
            for key in keys:
                if "encrypted_key" in key:
                    del key["encrypted_key"]
            
            return keys
        except Exception as e:
            raise ValueError(f"Failed to get API keys: {str(e)}")
    
    def get_api_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific API key by ID.
        
        Args:
            key_id: Unique identifier for the API key
            
        Returns:
            API key details (excluding the actual key) or None if not found
        """
        try:
            key = self.db.get_api_key(key_id)
            
            if key and "encrypted_key" in key:
                del key["encrypted_key"]
            
            return key
        except Exception as e:
            raise ValueError(f"Failed to get API key: {str(e)}")
    
    def delete_api_key(self, user_id: str, key_id: str) -> bool:
        """Delete an API key.
        
        Args:
            user_id: Unique identifier for the user
            key_id: Unique identifier for the API key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify the key belongs to the user
            key = self.db.get_api_key(key_id)
            if not key or key.get("user_id") != user_id:
                return False
            
            return self.db.delete_api_key(key_id)
        except Exception as e:
            raise ValueError(f"Failed to delete API key: {str(e)}")
    
    def validate_api_key(self, key_id: str) -> bool:
        """Validate an API key with the provider.
        
        Args:
            key_id: Unique identifier for the API key
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Get the key from database
            key_record = self.db.get_api_key(key_id)
            if not key_record:
                return False
            
            # Decrypt the key
            encrypted_key = key_record.get("encrypted_key")
            if not encrypted_key:
                return False
            
            api_key = self._decrypt_key(encrypted_key)
            provider = ProviderType(key_record.get("provider"))
            
            # Get provider configuration
            provider_config = self.provider_config.get(provider)
            if not provider_config:
                return False
            
            # Special handling for providers that need additional configuration
            if provider in [ProviderType.AZURE_OPENAI, ProviderType.AWS_BEDROCK]:
                additional_config = json.loads(key_record.get("additional_config") or "{}")
                return self._validate_special_provider(provider, api_key, additional_config)
            
            # Standard validation for other providers
            validation_url = provider_config.get("validation_url")
            header_name = provider_config.get("header_name")
            header_format = provider_config.get("header_format")
            
            if not all([validation_url, header_name, header_format]):
                return False
            
            # Make validation request
            import requests
            headers = {header_name: header_format.format(key=api_key)}
            
            try:
                response = requests.get(validation_url, headers=headers, timeout=5)
                is_valid = response.status_code == 200
                
                # Update validation status in database
                self.db.update_api_key(key_id, {"is_valid": is_valid})
                
                return is_valid
            except Exception:
                # If request fails, mark as invalid
                self.db.update_api_key(key_id, {"is_valid": False})
                return False
        except Exception as e:
            # Log the error but don't expose details
            print(f"Error validating API key: {str(e)}")
            return False
    
    def get_api_key_for_request(self, user_id: str, provider: ProviderType, model: str) -> Tuple[Optional[str], bool]:
        """Get a valid API key for making a request.
        
        Args:
            user_id: Unique identifier for the user
            provider: Provider type for the API key
            model: Model name to use
            
        Returns:
            Tuple of (decrypted API key or None if no valid key is available, is_user_provided)
        """
        try:
            # Get all valid keys for this user and provider
            keys = self.db.get_valid_api_keys(user_id, provider.value)
            
            if not keys:
                return None, False
            
            # Select the least used key
            selected_key = min(keys, key=lambda k: k.get("usage_count", 0))
            
            # Decrypt the key
            encrypted_key = selected_key.get("encrypted_key")
            if not encrypted_key:
                return None, False
            
            api_key = self._decrypt_key(encrypted_key)
            
            # Update usage statistics
            self.db.update_api_key(selected_key["key_id"], {
                "last_used": datetime.now(),
                "usage_count": selected_key.get("usage_count", 0) + 1
            })
            
            return api_key, True
        except Exception as e:
            # Log the error but don't expose details
            print(f"Error getting API key for request: {str(e)}")
            return None, False
    
    def track_api_usage(self, key_id: str, tokens_used: int, request_type: str, model: str) -> bool:
        """Track API key usage.
        
        Args:
            key_id: Unique identifier for the API key
            tokens_used: Number of tokens used in the request
            request_type: Type of request made
            model: Model used for the request
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the key from database
            key_record = self.db.get_api_key(key_id)
            if not key_record:
                return False
            
            # Log usage
            usage_data = {
                "key_id": key_id,
                "tokens_used": tokens_used,
                "request_type": request_type,
                "model": model,
                "timestamp": datetime.now()
            }
            
            self.db.log_api_key_usage(usage_data)
            
            # Update usage count
            current_count = key_record.get("usage_count", 0)
            self.db.update_api_key(key_id, {"usage_count": current_count + 1})
            
            return True
        except Exception as e:
            # Log the error but don't expose details
            print(f"Error tracking API usage: {str(e)}")
            return False
    
    def get_model_category(self, provider: ProviderType, model: str) -> ModelCategory:
        """Get the category of a model.
        
        Args:
            provider: Provider type
            model: Model name
            
        Returns:
            ModelCategory (defaults to STANDARD if unknown)
        """
        try:
            provider_config = self.provider_config.get(provider)
            if not provider_config:
                return ModelCategory.STANDARD
            
            models = provider_config.get("models", {})
            return models.get(model, ModelCategory.STANDARD)
        except Exception:
            # Default to standard for any errors
            return ModelCategory.STANDARD
    
    def has_access_to_model_category(self, user_id: str, category: ModelCategory) -> bool:
        """Check if a user has access to a model category.
        
        Args:
            user_id: Unique identifier for the user
            category: Model category to check
            
        Returns:
            True if the user has access, False otherwise
        """
        try:
            # This would typically check the user's subscription level
            # For now, we'll assume all users have access to all categories
            return True
        except Exception:
            # Default to no access for any errors
            return False
    
    def get_usage_statistics(self, user_id: str, start_date: datetime = None, 
                            end_date: datetime = None) -> Dict[str, Any]:
        """Get API key usage statistics for a user.
        
        Args:
            user_id: Unique identifier for the user
            start_date: Start date for statistics (optional)
            end_date: End date for statistics (optional)
            
        Returns:
            Dictionary with usage statistics
        """
        try:
            # Get all keys for this user
            keys = self.db.get_user_api_keys(user_id)
            
            # Get usage data
            usage_data = self.db.get_api_key_usage(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Aggregate statistics
            total_tokens = sum(usage.get("tokens_used", 0) for usage in usage_data)
            requests_by_provider = {}
            tokens_by_provider = {}
            
            for usage in usage_data:
                key_id = usage.get("key_id")
                tokens = usage.get("tokens_used", 0)
                
                # Find the provider for this key
                provider = None
                for key in keys:
                    if key.get("key_id") == key_id:
                        provider = key.get("provider")
                        break
                
                if provider:
                    requests_by_provider[provider] = requests_by_provider.get(provider, 0) + 1
                    tokens_by_provider[provider] = tokens_by_provider.get(provider, 0) + tokens
            
            return {
                "total_requests": len(usage_data),
                "total_tokens": total_tokens,
                "requests_by_provider": requests_by_provider,
                "tokens_by_provider": tokens_by_provider,
                "start_date": start_date,
                "end_date": end_date
            }
        except Exception as e:
            raise ValueError(f"Failed to get usage statistics: {str(e)}")
