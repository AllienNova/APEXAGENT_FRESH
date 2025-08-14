"""
Identity integration module for ApexAgent.

This module provides integration with external identity providers,
including Single Sign-On (SSO), OAuth 2.0, and directory services.
"""

import os
import json
import uuid
import base64
import logging
import secrets
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable

from src.core.error_handling.errors import AuthenticationError, ConfigurationError
from src.core.event_system.event_manager import EventManager
from src.auth.authentication.auth_manager import User, Session, AuthenticationManager

logger = logging.getLogger(__name__)

class OAuthClient:
    """
    Represents an OAuth 2.0 client application.
    """
    def __init__(
        self,
        client_id: str,
        client_name: str,
        client_secret: str = None,
        redirect_uris: List[str] = None,
        allowed_scopes: List[str] = None,
        client_type: str = "confidential",
        created_at: datetime = None,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.client_id = client_id
        self.client_name = client_name
        self.client_secret = client_secret
        self.redirect_uris = redirect_uris or []
        self.allowed_scopes = allowed_scopes or []
        self.client_type = client_type  # "confidential" or "public"
        self.created_at = created_at or datetime.now()
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self, include_secret: bool = False) -> Dict[str, Any]:
        """
        Convert client object to dictionary representation.
        
        Args:
            include_secret: Whether to include client secret
            
        Returns:
            Dictionary representation of the client
        """
        client_dict = {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "redirect_uris": self.redirect_uris,
            "allowed_scopes": self.allowed_scopes,
            "client_type": self.client_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
        
        if include_secret and self.client_secret:
            client_dict["client_secret"] = self.client_secret
            
        return client_dict
    
    @classmethod
    def from_dict(cls, client_dict: Dict[str, Any]) -> 'OAuthClient':
        """
        Create a client object from dictionary representation.
        
        Args:
            client_dict: Dictionary representation of the client
            
        Returns:
            OAuthClient object
        """
        created_at = client_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        return cls(
            client_id=client_dict["client_id"],
            client_name=client_dict["client_name"],
            client_secret=client_dict.get("client_secret"),
            redirect_uris=client_dict.get("redirect_uris", []),
            allowed_scopes=client_dict.get("allowed_scopes", []),
            client_type=client_dict.get("client_type", "confidential"),
            created_at=created_at,
            is_active=client_dict.get("is_active", True),
            metadata=client_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"OAuthClient(id={self.client_id}, name={self.client_name})"


class OAuthToken:
    """
    Represents an OAuth 2.0 token.
    """
    def __init__(
        self,
        token_type: str,
        access_token: str,
        client_id: str,
        user_id: str = None,
        refresh_token: str = None,
        expires_at: datetime = None,
        scopes: List[str] = None,
        created_at: datetime = None,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.token_type = token_type  # "bearer", "mac", etc.
        self.access_token = access_token
        self.client_id = client_id
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.created_at = created_at or datetime.now()
        # Default token expiration is 1 hour
        self.expires_at = expires_at or (self.created_at + timedelta(hours=1))
        self.scopes = scopes or []
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert token object to dictionary representation.
        
        Returns:
            Dictionary representation of the token
        """
        return {
            "token_type": self.token_type,
            "access_token": self.access_token,
            "client_id": self.client_id,
            "user_id": self.user_id,
            "refresh_token": self.refresh_token,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "scopes": self.scopes,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, token_dict: Dict[str, Any]) -> 'OAuthToken':
        """
        Create a token object from dictionary representation.
        
        Args:
            token_dict: Dictionary representation of the token
            
        Returns:
            OAuthToken object
        """
        created_at = token_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        expires_at = token_dict.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        return cls(
            token_type=token_dict["token_type"],
            access_token=token_dict["access_token"],
            client_id=token_dict["client_id"],
            user_id=token_dict.get("user_id"),
            refresh_token=token_dict.get("refresh_token"),
            created_at=created_at,
            expires_at=expires_at,
            scopes=token_dict.get("scopes", []),
            is_active=token_dict.get("is_active", True),
            metadata=token_dict.get("metadata", {})
        )
    
    def is_expired(self) -> bool:
        """
        Check if the token is expired.
        
        Returns:
            True if token is expired, False otherwise
        """
        return datetime.now() > self.expires_at
    
    def __str__(self) -> str:
        return f"OAuthToken(type={self.token_type}, client={self.client_id}, user={self.user_id})"


class OAuthAuthorizationCode:
    """
    Represents an OAuth 2.0 authorization code.
    """
    def __init__(
        self,
        code: str,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        expires_at: datetime = None,
        scopes: List[str] = None,
        code_challenge: str = None,
        code_challenge_method: str = None,
        created_at: datetime = None,
        is_used: bool = False,
        metadata: Dict[str, Any] = None
    ):
        self.code = code
        self.client_id = client_id
        self.user_id = user_id
        self.redirect_uri = redirect_uri
        self.created_at = created_at or datetime.now()
        # Default code expiration is 10 minutes
        self.expires_at = expires_at or (self.created_at + timedelta(minutes=10))
        self.scopes = scopes or []
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method
        self.is_used = is_used
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert authorization code object to dictionary representation.
        
        Returns:
            Dictionary representation of the authorization code
        """
        return {
            "code": self.code,
            "client_id": self.client_id,
            "user_id": self.user_id,
            "redirect_uri": self.redirect_uri,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "scopes": self.scopes,
            "code_challenge": self.code_challenge,
            "code_challenge_method": self.code_challenge_method,
            "is_used": self.is_used,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, code_dict: Dict[str, Any]) -> 'OAuthAuthorizationCode':
        """
        Create an authorization code object from dictionary representation.
        
        Args:
            code_dict: Dictionary representation of the authorization code
            
        Returns:
            OAuthAuthorizationCode object
        """
        created_at = code_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        expires_at = code_dict.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        return cls(
            code=code_dict["code"],
            client_id=code_dict["client_id"],
            user_id=code_dict["user_id"],
            redirect_uri=code_dict["redirect_uri"],
            created_at=created_at,
            expires_at=expires_at,
            scopes=code_dict.get("scopes", []),
            code_challenge=code_dict.get("code_challenge"),
            code_challenge_method=code_dict.get("code_challenge_method"),
            is_used=code_dict.get("is_used", False),
            metadata=code_dict.get("metadata", {})
        )
    
    def is_expired(self) -> bool:
        """
        Check if the authorization code is expired.
        
        Returns:
            True if code is expired, False otherwise
        """
        return datetime.now() > self.expires_at
    
    def __str__(self) -> str:
        return f"OAuthAuthorizationCode(client={self.client_id}, user={self.user_id})"


class IdentityProvider:
    """
    Base class for external identity providers.
    """
    def __init__(
        self,
        provider_id: str,
        name: str,
        provider_type: str,
        config: Dict[str, Any],
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.provider_id = provider_id
        self.name = name
        self.provider_type = provider_type
        self.config = config
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """
        Convert provider object to dictionary representation.
        
        Args:
            include_secrets: Whether to include secret configuration values
            
        Returns:
            Dictionary representation of the provider
        """
        provider_dict = {
            "provider_id": self.provider_id,
            "name": self.name,
            "provider_type": self.provider_type,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
        
        if include_secrets:
            provider_dict["config"] = self.config
        else:
            # Filter out secret values
            filtered_config = {}
            for key, value in self.config.items():
                if not key.endswith("_secret") and not key.endswith("_key") and not key.endswith("_password"):
                    filtered_config[key] = value
            provider_dict["config"] = filtered_config
            
        return provider_dict
    
    @classmethod
    def from_dict(cls, provider_dict: Dict[str, Any]) -> 'IdentityProvider':
        """
        Create a provider object from dictionary representation.
        
        Args:
            provider_dict: Dictionary representation of the provider
            
        Returns:
            IdentityProvider object
        """
        return cls(
            provider_id=provider_dict["provider_id"],
            name=provider_dict["name"],
            provider_type=provider_dict["provider_type"],
            config=provider_dict.get("config", {}),
            is_active=provider_dict.get("is_active", True),
            metadata=provider_dict.get("metadata", {})
        )
    
    def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate a user with the identity provider.
        
        Args:
            credentials: Authentication credentials
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        raise NotImplementedError("Subclasses must implement authenticate method")
    
    def get_user_info(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get user information from the identity provider.
        
        Args:
            token: Authentication token
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        raise NotImplementedError("Subclasses must implement get_user_info method")
    
    def __str__(self) -> str:
        return f"IdentityProvider(id={self.provider_id}, name={self.name}, type={self.provider_type})"


class OAuthProvider(IdentityProvider):
    """
    Identity provider for OAuth 2.0 / OpenID Connect.
    """
    def __init__(
        self,
        provider_id: str,
        name: str,
        config: Dict[str, Any],
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            provider_id=provider_id,
            name=name,
            provider_type="oauth",
            config=config,
            is_active=is_active,
            metadata=metadata
        )
        
        # Validate required configuration
        required_fields = ["client_id", "client_secret", "authorization_endpoint", "token_endpoint"]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required configuration field: {field}")
    
    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: List[str] = None,
        response_type: str = "code",
        prompt: str = None,
        code_challenge: str = None,
        code_challenge_method: str = None
    ) -> str:
        """
        Get the authorization URL for the OAuth flow.
        
        Args:
            redirect_uri: Redirect URI after authorization
            state: State parameter for CSRF protection
            scopes: Requested scopes
            response_type: Response type (code, token)
            prompt: Prompt parameter (none, login, consent, select_account)
            code_challenge: PKCE code challenge
            code_challenge_method: PKCE code challenge method (S256, plain)
            
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": response_type,
            "state": state
        }
        
        if scopes:
            params["scope"] = " ".join(scopes)
        
        if prompt:
            params["prompt"] = prompt
        
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = code_challenge_method or "S256"
        
        # Build query string
        query_string = "&".join([f"{key}={requests.utils.quote(str(value))}" for key, value in params.items()])
        
        return f"{self.config['authorization_endpoint']}?{query_string}"
    
    def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: str = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Exchange an authorization code for an access token.
        
        Args:
            code: Authorization code
            redirect_uri: Redirect URI used in authorization request
            code_verifier: PKCE code verifier
            
        Returns:
            Tuple of (success, token_response, error_message)
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"]
        }
        
        if code_verifier:
            data["code_verifier"] = code_verifier
        
        try:
            response = requests.post(
                self.config["token_endpoint"],
                data=data,
                headers={"Accept": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json(), None
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error_description", error_data.get("error", f"HTTP {response.status_code}"))
                return False, None, error_message
                
        except Exception as e:
            return False, None, str(e)
    
    def refresh_token(
        self,
        refresh_token: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Tuple of (success, token_response, error_message)
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"]
        }
        
        try:
            response = requests.post(
                self.config["token_endpoint"],
                data=data,
                headers={"Accept": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json(), None
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error_description", error_data.get("error", f"HTTP {response.status_code}"))
                return False, None, error_message
                
        except Exception as e:
            return False, None, str(e)
    
    def get_user_info(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get user information using an access token.
        
        Args:
            token: Access token
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        if "userinfo_endpoint" not in self.config:
            return False, None, "Userinfo endpoint not configured"
        
        try:
            response = requests.get(
                self.config["userinfo_endpoint"],
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json(), None
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error_description", error_data.get("error", f"HTTP {response.status_code}"))
                return False, None, error_message
                
        except Exception as e:
            return False, None, str(e)
    
    def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate a user with the identity provider.
        
        Args:
            credentials: Authentication credentials
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # OAuth providers typically don't support direct authentication
        # Authentication is done through the authorization flow
        return False, None, "Direct authentication not supported for OAuth providers"


class SAMLProvider(IdentityProvider):
    """
    Identity provider for SAML 2.0.
    """
    def __init__(
        self,
        provider_id: str,
        name: str,
        config: Dict[str, Any],
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            provider_id=provider_id,
            name=name,
            provider_type="saml",
            config=config,
            is_active=is_active,
            metadata=metadata
        )
        
        # Validate required configuration
        required_fields = ["idp_metadata_url", "sp_entity_id", "acs_url"]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required configuration field: {field}")
    
    def get_login_url(self, relay_state: str = None) -> str:
        """
        Get the SAML login URL.
        
        Args:
            relay_state: Optional relay state
            
        Returns:
            SAML login URL
        """
        # In a real implementation, this would generate a SAML AuthnRequest
        # and redirect to the IdP's SSO URL
        # For simplicity, we'll just return the SSO URL
        sso_url = self.config.get("sso_url", "")
        if not sso_url:
            raise ConfigurationError("SSO URL not configured")
        
        if relay_state:
            return f"{sso_url}?RelayState={requests.utils.quote(relay_state)}"
        return sso_url
    
    def parse_saml_response(self, saml_response: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse a SAML response.
        
        Args:
            saml_response: SAML response XML
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # In a real implementation, this would validate the SAML response
        # and extract user information
        # For simplicity, we'll just return a mock success
        return True, {"mock": "user_info"}, None
    
    def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate a user with the identity provider.
        
        Args:
            credentials: Authentication credentials
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # SAML providers typically don't support direct authentication
        # Authentication is done through the SAML flow
        return False, None, "Direct authentication not supported for SAML providers"
    
    def get_user_info(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get user information from the identity provider.
        
        Args:
            token: Authentication token
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # SAML doesn't use tokens in the same way as OAuth
        return False, None, "Not applicable for SAML providers"


class LDAPProvider(IdentityProvider):
    """
    Identity provider for LDAP / Active Directory.
    """
    def __init__(
        self,
        provider_id: str,
        name: str,
        config: Dict[str, Any],
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            provider_id=provider_id,
            name=name,
            provider_type="ldap",
            config=config,
            is_active=is_active,
            metadata=metadata
        )
        
        # Validate required configuration
        required_fields = ["server_url", "base_dn", "user_search_filter"]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required configuration field: {field}")
    
    def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate a user with the identity provider.
        
        Args:
            credentials: Authentication credentials (username, password)
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # Check required credentials
        if "username" not in credentials or "password" not in credentials:
            return False, None, "Missing required credentials: username, password"
        
        # In a real implementation, this would connect to the LDAP server
        # and authenticate the user
        # For simplicity, we'll just return a mock success
        
        # Mock user info
        user_info = {
            "username": credentials["username"],
            "email": f"{credentials['username']}@example.com",
            "first_name": "Mock",
            "last_name": "User",
            "groups": ["Users"]
        }
        
        return True, user_info, None
    
    def get_user_info(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Get user information from the identity provider.
        
        Args:
            token: Authentication token
            
        Returns:
            Tuple of (success, user_info, error_message)
        """
        # LDAP doesn't use tokens in the same way as OAuth
        return False, None, "Not applicable for LDAP providers"


class IdentityManager:
    """
    Manages external identity providers and OAuth functionality.
    """
    def __init__(
        self,
        auth_manager: AuthenticationManager = None,
        event_manager: EventManager = None
    ):
        self.auth_manager = auth_manager or AuthenticationManager()
        self.event_manager = event_manager or EventManager()
        
        # Identity providers
        self.providers: Dict[str, IdentityProvider] = {}  # provider_id -> IdentityProvider
        self.provider_name_index: Dict[str, str] = {}  # provider_name -> provider_id
        
        # OAuth clients
        self.oauth_clients: Dict[str, OAuthClient] = {}  # client_id -> OAuthClient
        
        # OAuth tokens
        self.oauth_tokens: Dict[str, OAuthToken] = {}  # access_token -> OAuthToken
        self.oauth_refresh_tokens: Dict[str, str] = {}  # refresh_token -> access_token
        
        # OAuth authorization codes
        self.oauth_auth_codes: Dict[str, OAuthAuthorizationCode] = {}  # code -> OAuthAuthorizationCode
        
        # User identity mappings
        self.user_identities: Dict[str, Dict[str, str]] = {}  # user_id -> {provider_id: external_id}
    
    def register_provider(self, provider: IdentityProvider) -> IdentityProvider:
        """
        Register a new identity provider.
        
        Args:
            provider: IdentityProvider object to register
            
        Returns:
            Registered IdentityProvider object
            
        Raises:
            ConfigurationError: If provider name already exists
        """
        # Check if provider name already exists
        if provider.name in self.provider_name_index:
            raise ConfigurationError(f"Provider '{provider.name}' already exists")
        
        # Store the provider
        self.providers[provider.provider_id] = provider
        self.provider_name_index[provider.name] = provider.provider_id
        
        # Emit provider registered event
        self.event_manager.emit_event("identity.provider_registered", {
            "provider_id": provider.provider_id,
            "name": provider.name,
            "type": provider.provider_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return provider
    
    def register_oauth_client(self, client: OAuthClient) -> OAuthClient:
        """
        Register a new OAuth client.
        
        Args:
            client: OAuthClient object to register
            
        Returns:
            Registered OAuthClient object
            
        Raises:
            ConfigurationError: If client ID already exists
        """
        # Check if client ID already exists
        if client.client_id in self.oauth_clients:
            raise ConfigurationError(f"OAuth client with ID '{client.client_id}' already exists")
        
        # Store the client
        self.oauth_clients[client.client_id] = client
        
        # Emit client registered event
        self.event_manager.emit_event("identity.oauth_client_registered", {
            "client_id": client.client_id,
            "name": client.client_name,
            "timestamp": datetime.now().isoformat()
        })
        
        return client
    
    def authenticate_with_provider(
        self,
        provider_id: str,
        credentials: Dict[str, Any]
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate a user with an external identity provider.
        
        Args:
            provider_id: Provider ID to authenticate with
            credentials: Authentication credentials
            
        Returns:
            Tuple of (success, user, error_message)
        """
        # Check if provider exists
        if provider_id not in self.providers:
            return False, None, f"Provider with ID '{provider_id}' not found"
        
        provider = self.providers[provider_id]
        
        # Check if provider is active
        if not provider.is_active:
            return False, None, f"Provider '{provider.name}' is not active"
        
        # Authenticate with provider
        success, user_info, error = provider.authenticate(credentials)
        if not success:
            return False, None, error
        
        # Get or create user
        return self._get_or_create_user(provider_id, user_info)
    
    def create_authorization_code(
        self,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        scopes: List[str] = None,
        code_challenge: str = None,
        code_challenge_method: str = None,
        metadata: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[OAuthAuthorizationCode], Optional[str]]:
        """
        Create an OAuth authorization code.
        
        Args:
            client_id: OAuth client ID
            user_id: User ID
            redirect_uri: Redirect URI
            scopes: Requested scopes
            code_challenge: PKCE code challenge
            code_challenge_method: PKCE code challenge method
            metadata: Additional metadata
            
        Returns:
            Tuple of (success, auth_code, error_message)
        """
        # Check if client exists
        if client_id not in self.oauth_clients:
            return False, None, f"Client with ID '{client_id}' not found"
        
        client = self.oauth_clients[client_id]
        
        # Check if client is active
        if not client.is_active:
            return False, None, f"Client '{client.client_name}' is not active"
        
        # Check if redirect URI is allowed
        if redirect_uri not in client.redirect_uris:
            return False, None, f"Redirect URI '{redirect_uri}' not allowed for this client"
        
        # Check if scopes are allowed
        if scopes:
            for scope in scopes:
                if scope not in client.allowed_scopes and "*" not in client.allowed_scopes:
                    return False, None, f"Scope '{scope}' not allowed for this client"
        
        # Generate authorization code
        code = secrets.token_urlsafe(32)
        
        # Create authorization code object
        auth_code = OAuthAuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            metadata=metadata
        )
        
        # Store the authorization code
        self.oauth_auth_codes[code] = auth_code
        
        # Emit authorization code created event
        self.event_manager.emit_event("identity.oauth_code_created", {
            "code": code,
            "client_id": client_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, auth_code, None
    
    def exchange_authorization_code(
        self,
        code: str,
        client_id: str,
        client_secret: str = None,
        redirect_uri: str = None,
        code_verifier: str = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Exchange an OAuth authorization code for tokens.
        
        Args:
            code: Authorization code
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Redirect URI
            code_verifier: PKCE code verifier
            
        Returns:
            Tuple of (success, token_response, error_message)
        """
        # Check if authorization code exists
        if code not in self.oauth_auth_codes:
            return False, None, "Invalid authorization code"
        
        auth_code = self.oauth_auth_codes[code]
        
        # Check if code is expired
        if auth_code.is_expired():
            return False, None, "Authorization code expired"
        
        # Check if code is already used
        if auth_code.is_used:
            return False, None, "Authorization code already used"
        
        # Check if client ID matches
        if auth_code.client_id != client_id:
            return False, None, "Client ID mismatch"
        
        # Check if redirect URI matches (if provided)
        if redirect_uri and auth_code.redirect_uri != redirect_uri:
            return False, None, "Redirect URI mismatch"
        
        # Check client authentication
        client = self.oauth_clients.get(client_id)
        if not client:
            return False, None, "Invalid client ID"
        
        if client.client_type == "confidential" and client.client_secret != client_secret:
            return False, None, "Invalid client secret"
        
        # Check PKCE code verifier (if applicable)
        if auth_code.code_challenge:
            if not code_verifier:
                return False, None, "Code verifier required"
            
            if auth_code.code_challenge_method == "S256":
                # S256 method: base64url(sha256(code_verifier))
                verifier_hash = hashlib.sha256(code_verifier.encode()).digest()
                challenge = base64.urlsafe_b64encode(verifier_hash).decode().rstrip("=")
                if challenge != auth_code.code_challenge:
                    return False, None, "Invalid code verifier"
            elif auth_code.code_challenge_method == "plain":
                # Plain method: code_verifier
                if code_verifier != auth_code.code_challenge:
                    return False, None, "Invalid code verifier"
            else:
                return False, None, f"Unsupported code challenge method: {auth_code.code_challenge_method}"
        
        # Mark code as used
        auth_code.is_used = True
        
        # Generate tokens
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        # Create token object
        token = OAuthToken(
            token_type="bearer",
            access_token=access_token,
            client_id=client_id,
            user_id=auth_code.user_id,
            refresh_token=refresh_token,
            scopes=auth_code.scopes,
            expires_at=datetime.now() + timedelta(hours=1)  # 1 hour expiration
        )
        
        # Store the token
        self.oauth_tokens[access_token] = token
        self.oauth_refresh_tokens[refresh_token] = access_token
        
        # Emit token created event
        self.event_manager.emit_event("identity.oauth_token_created", {
            "client_id": client_id,
            "user_id": auth_code.user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Prepare token response
        token_response = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,  # 1 hour in seconds
            "refresh_token": refresh_token
        }
        
        if auth_code.scopes:
            token_response["scope"] = " ".join(auth_code.scopes)
        
        return True, token_response, None
    
    def refresh_access_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Refresh an OAuth access token.
        
        Args:
            refresh_token: Refresh token
            client_id: OAuth client ID
            client_secret: OAuth client secret
            
        Returns:
            Tuple of (success, token_response, error_message)
        """
        # Check if refresh token exists
        if refresh_token not in self.oauth_refresh_tokens:
            return False, None, "Invalid refresh token"
        
        # Get the access token
        access_token = self.oauth_refresh_tokens[refresh_token]
        
        # Get the token object
        token = self.oauth_tokens.get(access_token)
        if not token:
            # Clean up the refresh token mapping
            del self.oauth_refresh_tokens[refresh_token]
            return False, None, "Invalid refresh token"
        
        # Check if client ID matches
        if token.client_id != client_id:
            return False, None, "Client ID mismatch"
        
        # Check client authentication
        client = self.oauth_clients.get(client_id)
        if not client:
            return False, None, "Invalid client ID"
        
        if client.client_type == "confidential" and client.client_secret != client_secret:
            return False, None, "Invalid client secret"
        
        # Invalidate the old token
        token.is_active = False
        
        # Generate new tokens
        new_access_token = secrets.token_urlsafe(32)
        new_refresh_token = secrets.token_urlsafe(32)
        
        # Create new token object
        new_token = OAuthToken(
            token_type="bearer",
            access_token=new_access_token,
            client_id=client_id,
            user_id=token.user_id,
            refresh_token=new_refresh_token,
            scopes=token.scopes,
            expires_at=datetime.now() + timedelta(hours=1)  # 1 hour expiration
        )
        
        # Store the new token
        self.oauth_tokens[new_access_token] = new_token
        self.oauth_refresh_tokens[new_refresh_token] = new_access_token
        
        # Remove the old refresh token mapping
        del self.oauth_refresh_tokens[refresh_token]
        
        # Emit token refreshed event
        self.event_manager.emit_event("identity.oauth_token_refreshed", {
            "client_id": client_id,
            "user_id": token.user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Prepare token response
        token_response = {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 3600,  # 1 hour in seconds
            "refresh_token": new_refresh_token
        }
        
        if token.scopes:
            token_response["scope"] = " ".join(token.scopes)
        
        return True, token_response, None
    
    def validate_access_token(
        self,
        access_token: str
    ) -> Tuple[bool, Optional[OAuthToken], Optional[str]]:
        """
        Validate an OAuth access token.
        
        Args:
            access_token: Access token to validate
            
        Returns:
            Tuple of (is_valid, token, error_message)
        """
        # Check if token exists
        if access_token not in self.oauth_tokens:
            return False, None, "Invalid access token"
        
        token = self.oauth_tokens[access_token]
        
        # Check if token is active
        if not token.is_active:
            return False, token, "Token is inactive"
        
        # Check if token is expired
        if token.is_expired():
            return False, token, "Token expired"
        
        return True, token, None
    
    def revoke_token(
        self,
        token: str,
        token_type_hint: str = None,
        client_id: str = None,
        client_secret: str = None
    ) -> bool:
        """
        Revoke an OAuth token.
        
        Args:
            token: Token to revoke
            token_type_hint: Token type hint (access_token, refresh_token)
            client_id: OAuth client ID
            client_secret: OAuth client secret
            
        Returns:
            True if token was revoked, False otherwise
        """
        # Try to find the token based on the hint
        if token_type_hint == "refresh_token":
            if token in self.oauth_refresh_tokens:
                access_token = self.oauth_refresh_tokens[token]
                if access_token in self.oauth_tokens:
                    oauth_token = self.oauth_tokens[access_token]
                    
                    # Check client authentication if provided
                    if client_id and oauth_token.client_id != client_id:
                        return False
                    
                    if client_id and client_secret:
                        client = self.oauth_clients.get(client_id)
                        if not client or (client.client_type == "confidential" and client.client_secret != client_secret):
                            return False
                    
                    # Invalidate the token
                    oauth_token.is_active = False
                    
                    # Emit token revoked event
                    self.event_manager.emit_event("identity.oauth_token_revoked", {
                        "client_id": oauth_token.client_id,
                        "user_id": oauth_token.user_id,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return True
        else:  # Default to access_token
            if token in self.oauth_tokens:
                oauth_token = self.oauth_tokens[token]
                
                # Check client authentication if provided
                if client_id and oauth_token.client_id != client_id:
                    return False
                
                if client_id and client_secret:
                    client = self.oauth_clients.get(client_id)
                    if not client or (client.client_type == "confidential" and client.client_secret != client_secret):
                        return False
                
                # Invalidate the token
                oauth_token.is_active = False
                
                # Emit token revoked event
                self.event_manager.emit_event("identity.oauth_token_revoked", {
                    "client_id": oauth_token.client_id,
                    "user_id": oauth_token.user_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                return True
        
        return False
    
    def link_user_identity(
        self,
        user_id: str,
        provider_id: str,
        external_id: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Link a user to an external identity.
        
        Args:
            user_id: User ID to link
            provider_id: Provider ID to link to
            external_id: External user ID from the provider
            metadata: Additional metadata
            
        Returns:
            True if identity was linked, False otherwise
        """
        # Check if user exists
        user = self.auth_manager.get_user_by_id(user_id)
        if not user:
            return False
        
        # Check if provider exists
        if provider_id not in self.providers:
            return False
        
        # Initialize user identities if needed
        if user_id not in self.user_identities:
            self.user_identities[user_id] = {}
        
        # Link the identity
        self.user_identities[user_id][provider_id] = external_id
        
        # Store metadata in user metadata
        if metadata:
            identity_metadata = user.metadata.get("identities", {})
            identity_metadata[provider_id] = metadata
            user.metadata["identities"] = identity_metadata
        
        # Emit identity linked event
        self.event_manager.emit_event("identity.user_identity_linked", {
            "user_id": user_id,
            "provider_id": provider_id,
            "external_id": external_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def unlink_user_identity(
        self,
        user_id: str,
        provider_id: str
    ) -> bool:
        """
        Unlink a user from an external identity.
        
        Args:
            user_id: User ID to unlink
            provider_id: Provider ID to unlink from
            
        Returns:
            True if identity was unlinked, False otherwise
        """
        # Check if user has any identities
        if user_id not in self.user_identities:
            return False
        
        # Check if user has the specified identity
        if provider_id not in self.user_identities[user_id]:
            return False
        
        # Unlink the identity
        del self.user_identities[user_id][provider_id]
        
        # Remove metadata if exists
        user = self.auth_manager.get_user_by_id(user_id)
        if user and "identities" in user.metadata and provider_id in user.metadata["identities"]:
            del user.metadata["identities"][provider_id]
        
        # Emit identity unlinked event
        self.event_manager.emit_event("identity.user_identity_unlinked", {
            "user_id": user_id,
            "provider_id": provider_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def get_user_identities(
        self,
        user_id: str
    ) -> Dict[str, str]:
        """
        Get all external identities for a user.
        
        Args:
            user_id: User ID to get identities for
            
        Returns:
            Dictionary of provider_id -> external_id
        """
        return self.user_identities.get(user_id, {})
    
    def get_provider_by_id(self, provider_id: str) -> Optional[IdentityProvider]:
        """
        Get an identity provider by ID.
        
        Args:
            provider_id: Provider ID to get
            
        Returns:
            IdentityProvider object or None if not found
        """
        return self.providers.get(provider_id)
    
    def get_provider_by_name(self, provider_name: str) -> Optional[IdentityProvider]:
        """
        Get an identity provider by name.
        
        Args:
            provider_name: Provider name to get
            
        Returns:
            IdentityProvider object or None if not found
        """
        provider_id = self.provider_name_index.get(provider_name)
        if provider_id:
            return self.providers.get(provider_id)
        return None
    
    def get_oauth_client(self, client_id: str) -> Optional[OAuthClient]:
        """
        Get an OAuth client by ID.
        
        Args:
            client_id: Client ID to get
            
        Returns:
            OAuthClient object or None if not found
        """
        return self.oauth_clients.get(client_id)
    
    def get_all_providers(self) -> List[IdentityProvider]:
        """
        Get all identity providers.
        
        Returns:
            List of all IdentityProvider objects
        """
        return list(self.providers.values())
    
    def get_all_oauth_clients(self) -> List[OAuthClient]:
        """
        Get all OAuth clients.
        
        Returns:
            List of all OAuthClient objects
        """
        return list(self.oauth_clients.values())
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens.
        
        Returns:
            Number of tokens cleaned up
        """
        count = 0
        current_time = datetime.now()
        
        # Clean up expired tokens
        for access_token, token in list(self.oauth_tokens.items()):
            if token.expires_at < current_time:
                token.is_active = False
                count += 1
                
                # Remove refresh token mapping if exists
                if token.refresh_token and token.refresh_token in self.oauth_refresh_tokens:
                    del self.oauth_refresh_tokens[token.refresh_token]
        
        # Clean up expired authorization codes
        for code, auth_code in list(self.oauth_auth_codes.items()):
            if auth_code.expires_at < current_time:
                auth_code.is_used = True
                count += 1
        
        return count
    
    def _get_or_create_user(
        self,
        provider_id: str,
        user_info: Dict[str, Any]
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Get or create a user based on external identity information.
        
        Args:
            provider_id: Provider ID
            user_info: User information from the provider
            
        Returns:
            Tuple of (success, user, error_message)
        """
        # Extract required fields
        if "id" not in user_info:
            return False, None, "External ID not found in user info"
        
        external_id = str(user_info["id"])
        
        # Check if this identity is already linked to a user
        for user_id, identities in self.user_identities.items():
            if provider_id in identities and identities[provider_id] == external_id:
                # Identity already linked, get the user
                user = self.auth_manager.get_user_by_id(user_id)
                if user:
                    return True, user, None
        
        # Identity not linked, check if we can match by email
        email = user_info.get("email")
        if email:
            user = self.auth_manager.get_user_by_email(email)
            if user:
                # Link the identity to this user
                self.link_user_identity(user.user_id, provider_id, external_id, user_info)
                return True, user, None
        
        # No matching user found, create a new one
        try:
            # Extract user information
            username = user_info.get("username") or user_info.get("preferred_username") or email
            if not username:
                # Generate a username based on provider and external ID
                provider = self.providers[provider_id]
                username = f"{provider.name.lower()}_{external_id}"
            
            # Generate a random password for the user
            password = secrets.token_urlsafe(16)
            
            # Create the user
            user = self.auth_manager.register_user(
                username=username,
                email=email or f"{username}@example.com",  # Fallback email
                password=password,
                first_name=user_info.get("given_name") or user_info.get("first_name"),
                last_name=user_info.get("family_name") or user_info.get("last_name"),
                metadata={"source": "external", "provider": provider_id}
            )
            
            # Link the identity to the new user
            self.link_user_identity(user.user_id, provider_id, external_id, user_info)
            
            return True, user, None
            
        except Exception as e:
            return False, None, str(e)
