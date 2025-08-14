"""
LLM Providers integration for the ApexAgent project.

This module updates the main LLM Providers integration module to include
Azure OpenAI provider support alongside AWS Bedrock.
"""

import logging
import os
from typing import Dict, List, Optional, Union

from .core.provider_interface import (
    LLMProvider,
    ProviderType,
    ChatMessage,
    TextGenerationOptions,
    ChatGenerationOptions,
    EmbeddingOptions,
    ImageGenerationOptions,
    TextGenerationResult,
    ChatGenerationResult,
    EmbeddingResult,
    ImageGenerationResult
)
from .provider_manager import ProviderManager
from .aws_bedrock import AWSBedrockProvider, AWSCredentials, AWSAuthType
from .azure_openai import AzureOpenAIProvider, AzureCredentials, AzureAuthType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProviders:
    """
    Main entry point for the LLM Providers integration system.
    
    This class provides factory methods for creating providers and the provider manager,
    as well as convenience methods for common operations.
    """
    
    @staticmethod
    def create_provider_manager() -> ProviderManager:
        """
        Create a new provider manager.
        
        Returns:
            Provider manager instance
        """
        return ProviderManager()
    
    @staticmethod
    def create_aws_bedrock_provider(
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        session_token: Optional[str] = None,
        region: str = "us-east-1",
        profile_name: Optional[str] = None,
        role_arn: Optional[str] = None
    ) -> AWSBedrockProvider:
        """
        Create a new AWS Bedrock provider.
        
        Args:
            access_key_id: AWS access key ID (for access_key auth type)
            secret_access_key: AWS secret access key (for access_key auth type)
            session_token: AWS session token (for temporary_credentials auth type)
            region: AWS region
            profile_name: AWS profile name (for profile auth type)
            role_arn: AWS role ARN (for iam_role auth type with role assumption)
            
        Returns:
            AWS Bedrock provider instance
        """
        # Determine auth type based on provided credentials
        if access_key_id and secret_access_key:
            if session_token:
                auth_type = AWSAuthType.TEMPORARY_CREDENTIALS
            else:
                auth_type = AWSAuthType.ACCESS_KEY
        elif profile_name:
            auth_type = AWSAuthType.PROFILE
        elif role_arn:
            auth_type = AWSAuthType.IAM_ROLE
        else:
            # Default to environment-based authentication
            auth_type = AWSAuthType.ENVIRONMENT
        
        credentials = AWSCredentials(
            auth_type=auth_type,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            profile_name=profile_name,
            role_arn=role_arn,
            region=region
        )
        
        return AWSBedrockProvider(credentials=credentials)
    
    @staticmethod
    def create_azure_openai_provider(
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: str = "2023-12-01-preview",
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        managed_identity_client_id: Optional[str] = None
    ) -> AzureOpenAIProvider:
        """
        Create a new Azure OpenAI provider.
        
        Args:
            api_key: Azure OpenAI API key (for API_KEY auth type)
            endpoint: Azure OpenAI endpoint URL
            api_version: Azure OpenAI API version
            tenant_id: Microsoft Entra ID tenant ID (for ENTRA_ID auth type)
            client_id: Microsoft Entra ID client ID (for ENTRA_ID auth type)
            client_secret: Microsoft Entra ID client secret (for ENTRA_ID auth type)
            managed_identity_client_id: Client ID for managed identity (for MANAGED_IDENTITY auth type)
            
        Returns:
            Azure OpenAI provider instance
        """
        # Determine auth type based on provided credentials
        if api_key:
            auth_type = AzureAuthType.API_KEY
        elif tenant_id and client_id and client_secret:
            auth_type = AzureAuthType.ENTRA_ID
        elif managed_identity_client_id:
            auth_type = AzureAuthType.MANAGED_IDENTITY
        else:
            # Default to default credential
            auth_type = AzureAuthType.DEFAULT_CREDENTIAL
        
        credentials = AzureCredentials(
            auth_type=auth_type,
            api_key=api_key,
            api_version=api_version,
            endpoint=endpoint,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            managed_identity_client_id=managed_identity_client_id
        )
        
        return AzureOpenAIProvider(credentials=credentials)
    
    @staticmethod
    def create_together_ai_provider(
        api_key: str,
        base_url: str = "https://api.together.xyz/v1"
    ) -> "TogetherAIProvider":
        """
        Create a new Together AI provider.
        
        Args:
            api_key: Together AI API key
            base_url: Together AI API base URL
            
        Returns:
            Together AI provider instance
        """
        from .together_ai import create_together_ai_provider
        return create_together_ai_provider(api_key=api_key, base_url=base_url)
    
    @staticmethod
    def setup_default_providers() -> ProviderManager:
        """
        Set up a provider manager with default providers based on environment variables.
        
        Returns:
            Provider manager with default providers
        """
        manager = LLMProviders.create_provider_manager()
        
        # Check for AWS Bedrock configuration
        if (
            os.environ.get("AWS_ACCESS_KEY_ID") or
            os.environ.get("AWS_PROFILE") or
            os.environ.get("AWS_ROLE_ARN") or
            os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI")  # ECS/Lambda environment
        ):
            try:
                aws_provider = LLMProviders.create_aws_bedrock_provider(
                    access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                    secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                    session_token=os.environ.get("AWS_SESSION_TOKEN"),
                    region=os.environ.get("AWS_REGION", "us-east-1"),
                    profile_name=os.environ.get("AWS_PROFILE"),
                    role_arn=os.environ.get("AWS_ROLE_ARN")
                )
                manager.register_provider("aws_bedrock", aws_provider)
                logger.info("Registered AWS Bedrock provider")
            except Exception as e:
                logger.error(f"Failed to register AWS Bedrock provider: {str(e)}")
        
        # Check for Azure OpenAI configuration
        if (
            os.environ.get("AZURE_OPENAI_API_KEY") or
            os.environ.get("AZURE_TENANT_ID") or
            os.environ.get("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        ):
            try:
                azure_provider = LLMProviders.create_azure_openai_provider(
                    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                    endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
                    tenant_id=os.environ.get("AZURE_TENANT_ID"),
                    client_id=os.environ.get("AZURE_CLIENT_ID"),
                    client_secret=os.environ.get("AZURE_CLIENT_SECRET"),
                    managed_identity_client_id=os.environ.get("AZURE_MANAGED_IDENTITY_CLIENT_ID")
                )
                manager.register_provider("azure_openai", azure_provider)
                logger.info("Registered Azure OpenAI provider")
            except Exception as e:
                logger.error(f"Failed to register Azure OpenAI provider: {str(e)}")
        
        # Check for Together AI configuration
        if os.environ.get("TOGETHER_AI_API_KEY"):
            try:
                together_provider = LLMProviders.create_together_ai_provider(
                    api_key=os.environ.get("TOGETHER_AI_API_KEY"),
                    base_url=os.environ.get("TOGETHER_AI_BASE_URL", "https://api.together.xyz/v1")
                )
                manager.register_provider("together_ai", together_provider)
                logger.info("Registered Together AI provider")
            except Exception as e:
                logger.error(f"Failed to register Together AI provider: {str(e)}")
        
        return manager


# Convenience functions for common operations

def generate_text(
    prompt: str,
    model: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    provider: Optional[str] = None
) -> str:
    """
    Generate text from a prompt using the best available provider.
    
    Args:
        prompt: The text prompt
        model: Model identifier
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        provider: Optional preferred provider ID
        
    Returns:
        Generated text
    """
    manager = LLMProviders.setup_default_providers()
    options = TextGenerationOptions(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        provider=provider
    )
    result = manager.generate_text(prompt, options)
    return result.text


def generate_chat_response(
    messages: List[Union[Dict, ChatMessage]],
    model: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    provider: Optional[str] = None
) -> str:
    """
    Generate a chat response from a conversation using the best available provider.
    
    Args:
        messages: List of chat messages (can be ChatMessage objects or dicts with role/content keys)
        model: Model identifier
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        provider: Optional preferred provider ID
        
    Returns:
        Generated response text
    """
    manager = LLMProviders.setup_default_providers()
    
    # Convert dict messages to ChatMessage objects if needed
    chat_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            chat_messages.append(ChatMessage(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                name=msg.get("name"),
                function_call=msg.get("function_call")
            ))
        else:
            chat_messages.append(msg)
    
    options = ChatGenerationOptions(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        provider=provider
    )
    result = manager.generate_chat(chat_messages, options)
    return result.message.content


def generate_embedding(
    text: str,
    model: str,
    provider: Optional[str] = None
) -> List[float]:
    """
    Generate embeddings for text using the best available provider.
    
    Args:
        text: The text to generate embeddings for
        model: Model identifier
        provider: Optional preferred provider ID
        
    Returns:
        Generated embedding vector
    """
    manager = LLMProviders.setup_default_providers()
    options = EmbeddingOptions(
        model=model,
        provider=provider
    )
    result = manager.generate_embedding(text, options)
    return result.embedding


def generate_image(
    prompt: str,
    model: Optional[str] = None,
    size: Optional[str] = None,
    provider: Optional[str] = None
) -> List[str]:
    """
    Generate images from a prompt using the best available provider.
    
    Args:
        prompt: The text prompt
        model: Model identifier (optional)
        size: Image size (e.g., "1024x1024", "square", "portrait")
        provider: Optional preferred provider ID
        
    Returns:
        List of generated image data (base64 encoded or URLs)
    """
    manager = LLMProviders.setup_default_providers()
    options = ImageGenerationOptions(
        model=model,
        size=size,
        provider=provider
    )
    result = manager.generate_image(prompt, options)
    return result.images
