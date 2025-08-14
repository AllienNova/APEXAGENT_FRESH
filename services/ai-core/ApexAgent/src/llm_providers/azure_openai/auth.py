"""
Azure OpenAI authentication module for the LLM Providers integration.

This module provides authentication functionality for the Azure OpenAI provider,
supporting various authentication methods including API key, Microsoft Entra ID
(formerly Azure Active Directory), and managed identity.
"""

import logging
import os
from enum import Enum
from typing import Dict, Optional, Any, Union

import requests
from azure.identity import DefaultAzureCredential, ClientSecretCredential, ManagedIdentityCredential

logger = logging.getLogger(__name__)


class AzureAuthType(Enum):
    """Authentication types for Azure OpenAI."""
    API_KEY = "api_key"
    ENTRA_ID = "entra_id"  # Formerly Azure AD
    MANAGED_IDENTITY = "managed_identity"
    DEFAULT_CREDENTIAL = "default_credential"


class AzureCredentials:
    """
    Credentials for Azure OpenAI authentication.
    
    This class encapsulates the credentials needed for authenticating with
    Azure OpenAI, supporting multiple authentication methods.
    """
    
    def __init__(
        self,
        auth_type: AzureAuthType,
        api_key: Optional[str] = None,
        api_version: str = "2023-12-01-preview",  # Latest version with GPT-4 Turbo support
        endpoint: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        managed_identity_client_id: Optional[str] = None
    ):
        """
        Initialize Azure OpenAI credentials.
        
        Args:
            auth_type: Authentication type to use
            api_key: API key for API_KEY auth type
            api_version: Azure OpenAI API version
            endpoint: Azure OpenAI endpoint URL
            tenant_id: Microsoft Entra ID tenant ID for ENTRA_ID auth type
            client_id: Microsoft Entra ID client ID for ENTRA_ID auth type
            client_secret: Microsoft Entra ID client secret for ENTRA_ID auth type
            managed_identity_client_id: Client ID for MANAGED_IDENTITY auth type
        """
        self.auth_type = auth_type
        self.api_key = api_key
        self.api_version = api_version
        self.endpoint = endpoint
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.managed_identity_client_id = managed_identity_client_id
        
        # Validate required fields based on auth type
        self._validate_credentials()
    
    def _validate_credentials(self) -> None:
        """
        Validate that the required credentials are provided for the selected auth type.
        
        Raises:
            ValueError: If required credentials are missing
        """
        if self.auth_type == AzureAuthType.API_KEY:
            if not self.api_key:
                raise ValueError("API key is required for API_KEY auth type")
            if not self.endpoint:
                raise ValueError("Endpoint is required for API_KEY auth type")
        
        elif self.auth_type == AzureAuthType.ENTRA_ID:
            if not self.tenant_id:
                raise ValueError("Tenant ID is required for ENTRA_ID auth type")
            if not self.client_id:
                raise ValueError("Client ID is required for ENTRA_ID auth type")
            if not self.client_secret:
                raise ValueError("Client secret is required for ENTRA_ID auth type")
            if not self.endpoint:
                raise ValueError("Endpoint is required for ENTRA_ID auth type")
        
        elif self.auth_type == AzureAuthType.MANAGED_IDENTITY:
            if not self.endpoint:
                raise ValueError("Endpoint is required for MANAGED_IDENTITY auth type")
        
        elif self.auth_type == AzureAuthType.DEFAULT_CREDENTIAL:
            if not self.endpoint:
                raise ValueError("Endpoint is required for DEFAULT_CREDENTIAL auth type")


class AzureAuthManager:
    """
    Authentication manager for Azure OpenAI.
    
    This class handles authentication with Azure OpenAI, providing methods
    for obtaining access tokens and managing authentication headers.
    """
    
    def __init__(self, credentials: AzureCredentials):
        """
        Initialize the Azure authentication manager.
        
        Args:
            credentials: Azure OpenAI credentials
        """
        self.credentials = credentials
        self._token_cache: Dict[str, Any] = {}
        self._azure_credential = None
        
        # Initialize Azure credential if using token-based auth
        if self.credentials.auth_type in [AzureAuthType.ENTRA_ID, AzureAuthType.MANAGED_IDENTITY, AzureAuthType.DEFAULT_CREDENTIAL]:
            self._initialize_azure_credential()
    
    def _initialize_azure_credential(self) -> None:
        """Initialize the appropriate Azure credential based on auth type."""
        try:
            if self.credentials.auth_type == AzureAuthType.ENTRA_ID:
                self._azure_credential = ClientSecretCredential(
                    tenant_id=self.credentials.tenant_id,
                    client_id=self.credentials.client_id,
                    client_secret=self.credentials.client_secret
                )
            elif self.credentials.auth_type == AzureAuthType.MANAGED_IDENTITY:
                self._azure_credential = ManagedIdentityCredential(
                    client_id=self.credentials.managed_identity_client_id
                )
            elif self.credentials.auth_type == AzureAuthType.DEFAULT_CREDENTIAL:
                self._azure_credential = DefaultAzureCredential()
        except Exception as e:
            logger.error(f"Failed to initialize Azure credential: {str(e)}")
            raise
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for Azure OpenAI API requests.
        
        Returns:
            Dictionary of authentication headers
        """
        headers = {
            "Content-Type": "application/json",
            "api-version": self.credentials.api_version
        }
        
        if self.credentials.auth_type == AzureAuthType.API_KEY:
            headers["api-key"] = self.credentials.api_key
        else:
            # Token-based authentication
            token = self.get_access_token()
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def get_access_token(self) -> str:
        """
        Get an access token for Azure OpenAI.
        
        Returns:
            Access token string
            
        Raises:
            RuntimeError: If token acquisition fails
        """
        if self.credentials.auth_type == AzureAuthType.API_KEY:
            raise ValueError("Access tokens are not used with API_KEY auth type")
        
        # Check cache first
        cache_key = f"{self.credentials.auth_type.value}_{self.credentials.endpoint}"
        if cache_key in self._token_cache:
            return self._token_cache[cache_key]
        
        # Get token from Azure credential
        try:
            # The scope for Azure OpenAI is the endpoint URL with .default appended
            scope = f"{self.credentials.endpoint}/.default"
            token = self._azure_credential.get_token(scope)
            self._token_cache[cache_key] = token.token
            return token.token
        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            raise RuntimeError(f"Failed to get access token: {str(e)}")
    
    def test_authentication(self) -> bool:
        """
        Test authentication with Azure OpenAI.
        
        Returns:
            True if authentication is successful, False otherwise
        """
        try:
            headers = self.get_auth_headers()
            
            # Make a simple request to the models endpoint
            url = f"{self.credentials.endpoint}/openai/models"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Authentication test failed: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Authentication test failed: {str(e)}")
            return False
