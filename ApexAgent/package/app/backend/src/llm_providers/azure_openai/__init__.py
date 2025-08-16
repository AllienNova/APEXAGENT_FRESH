"""
Azure OpenAI module for the LLM Providers integration.

This module provides the Azure OpenAI provider implementation for the LLM Providers
integration system.
"""

from .auth import AzureAuthManager, AzureCredentials, AzureAuthType
from .api_client import AzureOpenAIProvider

__all__ = [
    'AzureAuthManager',
    'AzureCredentials',
    'AzureAuthType',
    'AzureOpenAIProvider'
]
