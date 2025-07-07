"""
AWS Bedrock module for the LLM Providers integration.

This module provides the AWS Bedrock provider implementation for the LLM Providers
integration system.
"""

from .auth import AWSAuthManager, AWSCredentials, AWSAuthType
from .api_client import AWSBedrockProvider

__all__ = [
    'AWSAuthManager',
    'AWSCredentials',
    'AWSAuthType',
    'AWSBedrockProvider'
]
