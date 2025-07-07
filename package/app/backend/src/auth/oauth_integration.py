"""
OAuth 2.0 Integration System for Aideon AI Lite

This module provides comprehensive OAuth 2.0 integration for multiple platforms
including Google, Microsoft, LinkedIn, Twitter, Facebook, and other services.
It handles the complete OAuth flow from authorization to token management.
"""

import asyncio
import json
import logging
import secrets
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum

from ..core.plugin_exceptions import (
    PluginError,
    PluginConfigurationError,
    PluginActionExecutionError
)

logger = logging.getLogger(__name__)


class OAuthProvider(Enum):
    """Supported OAuth 2.0 providers."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    GITHUB = "github"
    REDDIT = "reddit"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"


@dataclass
class OAuthConfig:
    """OAuth configuration for a provider."""
    provider: OAuthProvider
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    scope: List[str]
    redirect_uri: str
    additional_params: Dict[str, str] = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


@dataclass
class OAuthTokens:
    """OAuth tokens and metadata."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    provider: Optional[OAuthProvider] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.expires_in and not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(seconds=self.expires_in)
    
    def is_expired(self) -> bool:
        """Check if the access token is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at
    
    def expires_soon(self, buffer_minutes: int = 5) -> bool:
        """Check if the token expires soon."""
        if not self.expires_at:
            return False
        buffer_time = datetime.utcnow() + timedelta(minutes=buffer_minutes)
        return buffer_time >= self.expires_at


class OAuthIntegrationSystem:
    """
    Comprehensive OAuth 2.0 integration system for Aideon AI Lite.
    
    Handles OAuth flows for multiple platforms with PKCE support,
    secure token storage, and automatic refresh capabilities.
    """
    
    def __init__(self, base_redirect_uri: str = "http://localhost:8000/auth/callback"):
        """
        Initialize the OAuth integration system.
        
        Args:
            base_redirect_uri: Base redirect URI for OAuth callbacks
        """
        self.base_redirect_uri = base_redirect_uri
        self.session: Optional[aiohttp.ClientSession] = None
        self.active_states: Dict[str, Dict[str, Any]] = {}  # CSRF protection
        
        # Provider configurations
        self.provider_configs = self._initialize_provider_configs()
        
        # Initialize HTTP session
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize HTTP session for OAuth requests."""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                "User-Agent": "Aideon-AI-Lite/1.0",
                "Accept": "application/json"
            }
        )
    
    def _initialize_provider_configs(self) -> Dict[OAuthProvider, Dict[str, Any]]:
        """Initialize OAuth provider configurations."""
        return {
            OAuthProvider.GOOGLE: {
                "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "revoke_url": "https://oauth2.googleapis.com/revoke",
                "scopes": {
                    "email": ["https://www.googleapis.com/auth/userinfo.email"],
                    "calendar": ["https://www.googleapis.com/auth/calendar"],
                    "gmail": ["https://www.googleapis.com/auth/gmail.modify"],
                    "drive": ["https://www.googleapis.com/auth/drive"],
                    "youtube": ["https://www.googleapis.com/auth/youtube"]
                },
                "supports_pkce": True,
                "supports_refresh": True
            },
            OAuthProvider.MICROSOFT: {
                "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_url": "https://graph.microsoft.com/v1.0/me",
                "scopes": {
                    "email": ["https://graph.microsoft.com/mail.read"],
                    "calendar": ["https://graph.microsoft.com/calendars.readwrite"],
                    "profile": ["https://graph.microsoft.com/user.read"],
                    "files": ["https://graph.microsoft.com/files.readwrite"]
                },
                "supports_pkce": True,
                "supports_refresh": True
            },
            OAuthProvider.LINKEDIN: {
                "authorization_url": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "userinfo_url": "https://api.linkedin.com/v2/people/~",
                "scopes": {
                    "profile": ["r_liteprofile", "r_emailaddress"],
                    "posting": ["w_member_social"],
                    "company": ["r_organization_social"]
                },
                "supports_pkce": False,
                "supports_refresh": True
            },
            OAuthProvider.TWITTER: {
                "authorization_url": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token",
                "userinfo_url": "https://api.twitter.com/2/users/me",
                "revoke_url": "https://api.twitter.com/2/oauth2/revoke",
                "scopes": {
                    "read": ["tweet.read", "users.read"],
                    "write": ["tweet.write", "tweet.read", "users.read"],
                    "dm": ["dm.read", "dm.write"]
                },
                "supports_pkce": True,
                "supports_refresh": True
            },
            OAuthProvider.FACEBOOK: {
                "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "userinfo_url": "https://graph.facebook.com/v18.0/me",
                "scopes": {
                    "pages": ["pages_manage_posts", "pages_read_engagement"],
                    "profile": ["public_profile", "email"],
                    "instagram": ["instagram_basic", "instagram_content_publish"]
                },
                "supports_pkce": False,
                "supports_refresh": False  # Uses long-lived tokens
            },
            OAuthProvider.GITHUB: {
                "authorization_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "scopes": {
                    "repo": ["repo"],
                    "user": ["user:email"],
                    "gist": ["gist"]
                },
                "supports_pkce": False,
                "supports_refresh": False
            },
            OAuthProvider.REDDIT: {
                "authorization_url": "https://www.reddit.com/api/v1/authorize",
                "token_url": "https://www.reddit.com/api/v1/access_token",
                "userinfo_url": "https://oauth.reddit.com/api/v1/me",
                "scopes": {
                    "basic": ["identity"],
                    "posting": ["submit", "edit"],
                    "reading": ["read", "history"]
                },
                "supports_pkce": False,
                "supports_refresh": True
            }
        }
    
    async def generate_authorization_url(
        self,
        provider: OAuthProvider,
        client_id: str,
        scopes: List[str],
        user_id: str,
        additional_params: Dict[str, str] = None
    ) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL with PKCE support.
        
        Args:
            provider: OAuth provider
            client_id: OAuth client ID
            scopes: Requested scopes
            user_id: User ID for state tracking
            additional_params: Additional OAuth parameters
            
        Returns:
            Tuple of (authorization_url, state)
        """
        try:
            provider_config = self.provider_configs.get(provider)
            if not provider_config:
                raise PluginConfigurationError(f"Unsupported OAuth provider: {provider}")
            
            # Generate state for CSRF protection
            state = self._generate_state()
            
            # Generate PKCE parameters if supported
            code_verifier = None
            code_challenge = None
            if provider_config.get("supports_pkce", False):
                code_verifier = self._generate_code_verifier()
                code_challenge = self._generate_code_challenge(code_verifier)
            
            # Store state information
            self.active_states[state] = {
                "provider": provider,
                "user_id": user_id,
                "code_verifier": code_verifier,
                "timestamp": datetime.utcnow(),
                "scopes": scopes
            }
            
            # Build authorization parameters
            auth_params = {
                "client_id": client_id,
                "response_type": "code",
                "redirect_uri": f"{self.base_redirect_uri}/{provider.value}",
                "scope": " ".join(scopes),
                "state": state
            }
            
            # Add PKCE parameters
            if code_challenge:
                auth_params.update({
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256"
                })
            
            # Add provider-specific parameters
            if additional_params:
                auth_params.update(additional_params)
            
            # Add provider-specific required parameters
            if provider == OAuthProvider.MICROSOFT:
                auth_params["response_mode"] = "query"
            elif provider == OAuthProvider.LINKEDIN:
                auth_params["response_type"] = "code"
            
            # Build authorization URL
            authorization_url = f"{provider_config['authorization_url']}?{urlencode(auth_params)}"
            
            logger.info(f"Generated OAuth authorization URL for {provider.value}")
            return authorization_url, state
            
        except Exception as e:
            logger.error(f"Failed to generate authorization URL for {provider}: {e}")
            raise PluginActionExecutionError(f"Authorization URL generation failed: {e}")
    
    async def exchange_code_for_tokens(
        self,
        provider: OAuthProvider,
        client_id: str,
        client_secret: str,
        authorization_code: str,
        state: str
    ) -> OAuthTokens:
        """
        Exchange authorization code for access tokens.
        
        Args:
            provider: OAuth provider
            client_id: OAuth client ID
            client_secret: OAuth client secret
            authorization_code: Authorization code from callback
            state: State parameter for validation
            
        Returns:
            OAuth tokens
        """
        try:
            # Validate state
            state_info = self.active_states.get(state)
            if not state_info:
                raise PluginActionExecutionError("Invalid or expired state parameter")
            
            # Check state expiration (30 minutes)
            if datetime.utcnow() - state_info["timestamp"] > timedelta(minutes=30):
                del self.active_states[state]
                raise PluginActionExecutionError("State parameter expired")
            
            provider_config = self.provider_configs.get(provider)
            if not provider_config:
                raise PluginConfigurationError(f"Unsupported OAuth provider: {provider}")
            
            # Prepare token request
            token_data = {
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": authorization_code,
                "redirect_uri": f"{self.base_redirect_uri}/{provider.value}"
            }
            
            # Add PKCE code verifier if used
            if state_info.get("code_verifier"):
                token_data["code_verifier"] = state_info["code_verifier"]
            
            # Make token request
            headers = {"Accept": "application/json"}
            if provider == OAuthProvider.REDDIT:
                # Reddit requires basic auth
                auth = aiohttp.BasicAuth(client_id, client_secret)
                del token_data["client_secret"]
            else:
                auth = None
            
            async with self.session.post(
                provider_config["token_url"],
                data=token_data,
                headers=headers,
                auth=auth
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Token exchange failed for {provider}: {error_text}")
                    raise PluginActionExecutionError(f"Token exchange failed: {error_text}")
                
                token_response = await response.json()
            
            # Parse token response
            tokens = OAuthTokens(
                access_token=token_response["access_token"],
                refresh_token=token_response.get("refresh_token"),
                token_type=token_response.get("token_type", "Bearer"),
                expires_in=token_response.get("expires_in"),
                scope=token_response.get("scope"),
                provider=provider,
                user_id=state_info["user_id"]
            )
            
            # Clean up state
            del self.active_states[state]
            
            logger.info(f"Successfully exchanged code for tokens: {provider.value}")
            return tokens
            
        except Exception as e:
            logger.error(f"Token exchange failed for {provider}: {e}")
            raise PluginActionExecutionError(f"Token exchange failed: {e}")
    
    async def refresh_access_token(
        self,
        provider: OAuthProvider,
        client_id: str,
        client_secret: str,
        refresh_token: str
    ) -> OAuthTokens:
        """
        Refresh access token using refresh token.
        
        Args:
            provider: OAuth provider
            client_id: OAuth client ID
            client_secret: OAuth client secret
            refresh_token: Refresh token
            
        Returns:
            New OAuth tokens
        """
        try:
            provider_config = self.provider_configs.get(provider)
            if not provider_config:
                raise PluginConfigurationError(f"Unsupported OAuth provider: {provider}")
            
            if not provider_config.get("supports_refresh", False):
                raise PluginActionExecutionError(f"Provider {provider} does not support token refresh")
            
            # Prepare refresh request
            refresh_data = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
            }
            
            headers = {"Accept": "application/json"}
            auth = None
            
            if provider == OAuthProvider.REDDIT:
                auth = aiohttp.BasicAuth(client_id, client_secret)
                del refresh_data["client_secret"]
            
            async with self.session.post(
                provider_config["token_url"],
                data=refresh_data,
                headers=headers,
                auth=auth
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Token refresh failed for {provider}: {error_text}")
                    raise PluginActionExecutionError(f"Token refresh failed: {error_text}")
                
                token_response = await response.json()
            
            # Parse refreshed tokens
            tokens = OAuthTokens(
                access_token=token_response["access_token"],
                refresh_token=token_response.get("refresh_token", refresh_token),  # Some providers don't return new refresh token
                token_type=token_response.get("token_type", "Bearer"),
                expires_in=token_response.get("expires_in"),
                scope=token_response.get("scope"),
                provider=provider
            )
            
            logger.info(f"Successfully refreshed tokens for {provider.value}")
            return tokens
            
        except Exception as e:
            logger.error(f"Token refresh failed for {provider}: {e}")
            raise PluginActionExecutionError(f"Token refresh failed: {e}")
    
    async def get_user_info(
        self,
        provider: OAuthProvider,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get user information using access token.
        
        Args:
            provider: OAuth provider
            access_token: Access token
            
        Returns:
            User information
        """
        try:
            provider_config = self.provider_configs.get(provider)
            if not provider_config:
                raise PluginConfigurationError(f"Unsupported OAuth provider: {provider}")
            
            userinfo_url = provider_config.get("userinfo_url")
            if not userinfo_url:
                raise PluginConfigurationError(f"No userinfo URL configured for {provider}")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            async with self.session.get(userinfo_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"User info request failed for {provider}: {error_text}")
                    raise PluginActionExecutionError(f"User info request failed: {error_text}")
                
                user_info = await response.json()
            
            logger.info(f"Successfully retrieved user info for {provider.value}")
            return user_info
            
        except Exception as e:
            logger.error(f"Failed to get user info for {provider}: {e}")
            raise PluginActionExecutionError(f"User info retrieval failed: {e}")
    
    async def revoke_token(
        self,
        provider: OAuthProvider,
        token: str,
        client_id: str = None,
        client_secret: str = None
    ) -> bool:
        """
        Revoke access token.
        
        Args:
            provider: OAuth provider
            token: Token to revoke
            client_id: OAuth client ID (if required)
            client_secret: OAuth client secret (if required)
            
        Returns:
            True if successful
        """
        try:
            provider_config = self.provider_configs.get(provider)
            if not provider_config:
                raise PluginConfigurationError(f"Unsupported OAuth provider: {provider}")
            
            revoke_url = provider_config.get("revoke_url")
            if not revoke_url:
                logger.warning(f"No revoke URL configured for {provider}")
                return True  # Assume success if no revoke endpoint
            
            # Prepare revoke request
            revoke_data = {"token": token}
            if client_id:
                revoke_data["client_id"] = client_id
            if client_secret:
                revoke_data["client_secret"] = client_secret
            
            headers = {"Accept": "application/json"}
            
            async with self.session.post(revoke_url, data=revoke_data, headers=headers) as response:
                success = response.status in [200, 204]
                if success:
                    logger.info(f"Successfully revoked token for {provider.value}")
                else:
                    logger.warning(f"Token revocation may have failed for {provider}: {response.status}")
                
                return success
                
        except Exception as e:
            logger.error(f"Token revocation failed for {provider}: {e}")
            return False
    
    def _generate_state(self) -> str:
        """Generate secure state parameter for CSRF protection."""
        return secrets.token_urlsafe(32)
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier."""
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
        
        # Clean up expired states
        current_time = datetime.utcnow()
        expired_states = [
            state for state, info in self.active_states.items()
            if current_time - info["timestamp"] > timedelta(minutes=30)
        ]
        for state in expired_states:
            del self.active_states[state]
        
        logger.info("OAuth integration system cleaned up")


class OAuthManager:
    """
    High-level OAuth management interface for Aideon AI Lite.
    
    Provides simplified methods for common OAuth operations
    and integrates with the existing credential management system.
    """
    
    def __init__(self, oauth_system: OAuthIntegrationSystem):
        """
        Initialize OAuth manager.
        
        Args:
            oauth_system: OAuth integration system instance
        """
        self.oauth_system = oauth_system
        self.provider_credentials: Dict[OAuthProvider, Dict[str, str]] = {}
    
    def configure_provider(
        self,
        provider: OAuthProvider,
        client_id: str,
        client_secret: str,
        additional_config: Dict[str, Any] = None
    ):
        """
        Configure OAuth provider credentials.
        
        Args:
            provider: OAuth provider
            client_id: OAuth client ID
            client_secret: OAuth client secret
            additional_config: Additional configuration
        """
        self.provider_credentials[provider] = {
            "client_id": client_id,
            "client_secret": client_secret,
            **(additional_config or {})
        }
        logger.info(f"Configured OAuth provider: {provider.value}")
    
    async def initiate_oauth_flow(
        self,
        provider: OAuthProvider,
        user_id: str,
        requested_scopes: List[str]
    ) -> str:
        """
        Initiate OAuth flow for a user.
        
        Args:
            provider: OAuth provider
            user_id: User ID
            requested_scopes: Requested OAuth scopes
            
        Returns:
            Authorization URL for user to visit
        """
        credentials = self.provider_credentials.get(provider)
        if not credentials:
            raise PluginConfigurationError(f"Provider {provider} not configured")
        
        auth_url, state = await self.oauth_system.generate_authorization_url(
            provider=provider,
            client_id=credentials["client_id"],
            scopes=requested_scopes,
            user_id=user_id
        )
        
        return auth_url
    
    async def complete_oauth_flow(
        self,
        provider: OAuthProvider,
        authorization_code: str,
        state: str
    ) -> Tuple[OAuthTokens, Dict[str, Any]]:
        """
        Complete OAuth flow and get tokens + user info.
        
        Args:
            provider: OAuth provider
            authorization_code: Authorization code from callback
            state: State parameter for validation
            
        Returns:
            Tuple of (tokens, user_info)
        """
        credentials = self.provider_credentials.get(provider)
        if not credentials:
            raise PluginConfigurationError(f"Provider {provider} not configured")
        
        # Exchange code for tokens
        tokens = await self.oauth_system.exchange_code_for_tokens(
            provider=provider,
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            authorization_code=authorization_code,
            state=state
        )
        
        # Get user information
        user_info = await self.oauth_system.get_user_info(
            provider=provider,
            access_token=tokens.access_token
        )
        
        return tokens, user_info
    
    async def refresh_tokens_if_needed(
        self,
        provider: OAuthProvider,
        tokens: OAuthTokens
    ) -> OAuthTokens:
        """
        Refresh tokens if they are expired or expiring soon.
        
        Args:
            provider: OAuth provider
            tokens: Current tokens
            
        Returns:
            Refreshed tokens or original tokens if refresh not needed
        """
        if not tokens.expires_soon():
            return tokens
        
        if not tokens.refresh_token:
            raise PluginActionExecutionError("No refresh token available")
        
        credentials = self.provider_credentials.get(provider)
        if not credentials:
            raise PluginConfigurationError(f"Provider {provider} not configured")
        
        refreshed_tokens = await self.oauth_system.refresh_access_token(
            provider=provider,
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            refresh_token=tokens.refresh_token
        )
        
        # Preserve user_id from original tokens
        refreshed_tokens.user_id = tokens.user_id
        
        return refreshed_tokens
    
    async def revoke_user_tokens(
        self,
        provider: OAuthProvider,
        tokens: OAuthTokens
    ) -> bool:
        """
        Revoke user's OAuth tokens.
        
        Args:
            provider: OAuth provider
            tokens: Tokens to revoke
            
        Returns:
            True if successful
        """
        credentials = self.provider_credentials.get(provider)
        if not credentials:
            raise PluginConfigurationError(f"Provider {provider} not configured")
        
        return await self.oauth_system.revoke_token(
            provider=provider,
            token=tokens.access_token,
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"]
        )
    
    def get_supported_providers(self) -> List[OAuthProvider]:
        """Get list of supported OAuth providers."""
        return list(OAuthProvider)
    
    def get_provider_scopes(self, provider: OAuthProvider) -> Dict[str, List[str]]:
        """Get available scopes for a provider."""
        provider_config = self.oauth_system.provider_configs.get(provider, {})
        return provider_config.get("scopes", {})
    
    async def cleanup(self):
        """Clean up OAuth manager resources."""
        await self.oauth_system.cleanup()
        logger.info("OAuth manager cleaned up")

