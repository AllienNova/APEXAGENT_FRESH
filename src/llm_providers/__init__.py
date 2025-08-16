"""
Main module initialization for the LLM Providers integration.

This module provides the main package initialization for the LLM Providers
integration system, including both AWS Bedrock and Azure OpenAI providers.
"""

from .core.provider_interface import (
    LLMProvider,
    ProviderType,
    LLMErrorType,
    FinishReason,
    ChatMessage,
    FunctionDefinition,
    ModelInfo,
    ProviderCapabilities,
    HealthStatus,
    UsageInfo,
    TextGenerationOptions,
    ChatGenerationOptions,
    EmbeddingOptions,
    ImageGenerationOptions,
    TextGenerationResult,
    ChatGenerationResult,
    EmbeddingResult,
    ImageGenerationResult,
    TextGenerationChunk,
    ChatGenerationChunk,
    LLMError
)
from .provider_manager import ProviderManager
from .aws_bedrock import AWSBedrockProvider, AWSCredentials, AWSAuthType
from .azure_openai import AzureOpenAIProvider, AzureCredentials, AzureAuthType
from .llm_providers import LLMProviders, generate_text, generate_chat_response, generate_embedding, generate_image

__all__ = [
    # Core interfaces
    'LLMProvider',
    'ProviderType',
    'LLMErrorType',
    'FinishReason',
    'ChatMessage',
    'FunctionDefinition',
    'ModelInfo',
    'ProviderCapabilities',
    'HealthStatus',
    'UsageInfo',
    'TextGenerationOptions',
    'ChatGenerationOptions',
    'EmbeddingOptions',
    'ImageGenerationOptions',
    'TextGenerationResult',
    'ChatGenerationResult',
    'EmbeddingResult',
    'ImageGenerationResult',
    'TextGenerationChunk',
    'ChatGenerationChunk',
    'LLMError',
    
    # Provider management
    'ProviderManager',
    
    # AWS Bedrock
    'AWSBedrockProvider',
    'AWSCredentials',
    'AWSAuthType',
    
    # Azure OpenAI
    'AzureOpenAIProvider',
    'AzureCredentials',
    'AzureAuthType',
    
    # Main entry point
    'LLMProviders',
    
    # Convenience functions
    'generate_text',
    'generate_chat_response',
    'generate_embedding',
    'generate_image'
]
