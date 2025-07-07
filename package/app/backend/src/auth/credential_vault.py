"""
Secure Credential Vault and Authentication Manager for Aideon AI Lite

This module provides secure storage and management of OAuth tokens, API keys,
and other credentials with encryption, automatic refresh, and audit logging.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import secrets
from cryptography.fernet import Fernet
import base64

from .oauth_integration import OAuthTokens, OAuthProvider, OAuthManager
from ..core.enhanced_api_key_manager import EnhancedApiKeyManager, ProviderType
from ..core.plugin_exceptions import (
    PluginError,
    PluginConfigurationError,
    PluginActionExecutionError
)

logger = logging.getLogger(__name__)


class CredentialType(Enum):
    """Types of credentials that can be stored."""
    OAUTH_TOKEN = "oauth_token"
    API_KEY = "api_key"
    APP_PASSWORD = "app_password"
    SERVICE_ACCOUNT = "service_account"
    WEBHOOK_SECRET = "webhook_secret"


class CredentialStatus(Enum):
    """Status of stored credentials."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_REFRESH = "pending_refresh"
    ERROR = "error"


@dataclass
class StoredCredential:
    """Stored credential with metadata."""
    credential_id: str
    user_id: str
    provider: str
    credential_type: CredentialType
    status: CredentialStatus
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    scopes: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def is_expired(self) -> bool:
        """Check if credential is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at
    
    def expires_soon(self, buffer_minutes: int = 5) -> bool:
        """Check if credential expires soon."""
        if not self.expires_at:
            return False
        buffer_time = datetime.utcnow() + timedelta(minutes=buffer_minutes)
        return buffer_time >= self.expires_at


@dataclass
class AuditLogEntry:
    """Audit log entry for credential operations."""
    entry_id: str
    user_id: str
    credential_id: str
    action: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SecureCredentialVault:
    """
    Secure credential vault with encryption and audit logging.
    
    Provides secure storage for OAuth tokens, API keys, and other credentials
    with automatic encryption, rotation, and comprehensive audit logging.
    """
    
    def __init__(self, api_key_manager: EnhancedApiKeyManager):
        """
        Initialize secure credential vault.
        
        Args:
            api_key_manager: Enhanced API key manager for encryption
        """
        self.api_key_manager = api_key_manager
        self.credentials: Dict[str, StoredCredential] = {}
        self.encrypted_data: Dict[str, bytes] = {}
        self.audit_log: List[AuditLogEntry] = []
        
        # Initialize encryption
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption system."""
        try:
            # Use the existing API key manager's encryption capabilities
            self.encryption_key = self._derive_vault_key()
            self.cipher = Fernet(self.encryption_key)
            logger.info("Credential vault encryption initialized")
        except Exception as e:
            logger.error(f"Failed to initialize vault encryption: {e}")
            raise PluginConfigurationError(f"Vault encryption initialization failed: {e}")
    
    def _derive_vault_key(self) -> bytes:
        """Derive encryption key for credential vault."""
        # Use the API key manager's master key to derive vault key
        vault_salt = b"aideon_credential_vault_salt_v1"
        master_key_data = str(self.api_key_manager._get_master_key()).encode()
        
        # Derive key using PBKDF2
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key_data,
            vault_salt,
            100000,  # iterations
            32  # key length
        )
        
        return base64.urlsafe_b64encode(derived_key)
    
    def _generate_credential_id(self) -> str:
        """Generate unique credential ID."""
        return f"cred_{secrets.token_urlsafe(16)}"
    
    def _generate_audit_id(self) -> str:
        """Generate unique audit log entry ID."""
        return f"audit_{secrets.token_urlsafe(16)}"
    
    async def store_oauth_tokens(
        self,
        user_id: str,
        provider: OAuthProvider,
        tokens: OAuthTokens,
        scopes: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store OAuth tokens securely.
        
        Args:
            user_id: User ID
            provider: OAuth provider
            tokens: OAuth tokens to store
            scopes: OAuth scopes
            metadata: Additional metadata
            
        Returns:
            Credential ID
        """
        try:
            credential_id = self._generate_credential_id()
            
            # Create credential record
            credential = StoredCredential(
                credential_id=credential_id,
                user_id=user_id,
                provider=provider.value,
                credential_type=CredentialType.OAUTH_TOKEN,
                status=CredentialStatus.ACTIVE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=tokens.expires_at,
                scopes=scopes or [],
                metadata=metadata or {}
            )
            
            # Encrypt and store token data
            token_data = asdict(tokens)
            encrypted_data = self.cipher.encrypt(json.dumps(token_data).encode())
            
            # Store in memory (in production, this would be in a database)
            self.credentials[credential_id] = credential
            self.encrypted_data[credential_id] = encrypted_data
            
            # Log the operation
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="store_oauth_tokens",
                metadata={"provider": provider.value, "scopes": scopes}
            )
            
            logger.info(f"Stored OAuth tokens for user {user_id}, provider {provider.value}")
            return credential_id
            
        except Exception as e:
            logger.error(f"Failed to store OAuth tokens: {e}")
            await self._log_audit_event(
                user_id=user_id,
                credential_id="",
                action="store_oauth_tokens",
                success=False,
                error_message=str(e)
            )
            raise PluginActionExecutionError(f"Failed to store OAuth tokens: {e}")
    
    async def retrieve_oauth_tokens(
        self,
        user_id: str,
        credential_id: str
    ) -> OAuthTokens:
        """
        Retrieve OAuth tokens.
        
        Args:
            user_id: User ID
            credential_id: Credential ID
            
        Returns:
            OAuth tokens
        """
        try:
            # Verify credential exists and belongs to user
            credential = self.credentials.get(credential_id)
            if not credential:
                raise PluginActionExecutionError("Credential not found")
            
            if credential.user_id != user_id:
                raise PluginActionExecutionError("Access denied")
            
            if credential.credential_type != CredentialType.OAUTH_TOKEN:
                raise PluginActionExecutionError("Invalid credential type")
            
            # Decrypt token data
            encrypted_data = self.encrypted_data.get(credential_id)
            if not encrypted_data:
                raise PluginActionExecutionError("Credential data not found")
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            token_data = json.loads(decrypted_data.decode())
            
            # Reconstruct OAuth tokens
            tokens = OAuthTokens(**token_data)
            
            # Update last used timestamp
            credential.last_used_at = datetime.utcnow()
            
            # Log the operation
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="retrieve_oauth_tokens",
                metadata={"provider": credential.provider}
            )
            
            return tokens
            
        except Exception as e:
            logger.error(f"Failed to retrieve OAuth tokens: {e}")
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="retrieve_oauth_tokens",
                success=False,
                error_message=str(e)
            )
            raise PluginActionExecutionError(f"Failed to retrieve OAuth tokens: {e}")
    
    async def update_oauth_tokens(
        self,
        user_id: str,
        credential_id: str,
        tokens: OAuthTokens
    ) -> bool:
        """
        Update stored OAuth tokens (e.g., after refresh).
        
        Args:
            user_id: User ID
            credential_id: Credential ID
            tokens: Updated OAuth tokens
            
        Returns:
            True if successful
        """
        try:
            # Verify credential exists and belongs to user
            credential = self.credentials.get(credential_id)
            if not credential:
                raise PluginActionExecutionError("Credential not found")
            
            if credential.user_id != user_id:
                raise PluginActionExecutionError("Access denied")
            
            # Encrypt and store updated token data
            token_data = asdict(tokens)
            encrypted_data = self.cipher.encrypt(json.dumps(token_data).encode())
            
            # Update stored data
            self.encrypted_data[credential_id] = encrypted_data
            credential.updated_at = datetime.utcnow()
            credential.expires_at = tokens.expires_at
            credential.status = CredentialStatus.ACTIVE
            
            # Log the operation
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="update_oauth_tokens",
                metadata={"provider": credential.provider}
            )
            
            logger.info(f"Updated OAuth tokens for credential {credential_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update OAuth tokens: {e}")
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="update_oauth_tokens",
                success=False,
                error_message=str(e)
            )
            return False
    
    async def store_api_key(
        self,
        user_id: str,
        provider: str,
        api_key: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store API key securely.
        
        Args:
            user_id: User ID
            provider: API provider name
            api_key: API key to store
            metadata: Additional metadata
            
        Returns:
            Credential ID
        """
        try:
            credential_id = self._generate_credential_id()
            
            # Create credential record
            credential = StoredCredential(
                credential_id=credential_id,
                user_id=user_id,
                provider=provider,
                credential_type=CredentialType.API_KEY,
                status=CredentialStatus.ACTIVE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Encrypt and store API key
            key_data = {"api_key": api_key}
            encrypted_data = self.cipher.encrypt(json.dumps(key_data).encode())
            
            # Store in memory
            self.credentials[credential_id] = credential
            self.encrypted_data[credential_id] = encrypted_data
            
            # Log the operation
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="store_api_key",
                metadata={"provider": provider}
            )
            
            logger.info(f"Stored API key for user {user_id}, provider {provider}")
            return credential_id
            
        except Exception as e:
            logger.error(f"Failed to store API key: {e}")
            await self._log_audit_event(
                user_id=user_id,
                credential_id="",
                action="store_api_key",
                success=False,
                error_message=str(e)
            )
            raise PluginActionExecutionError(f"Failed to store API key: {e}")
    
    async def retrieve_api_key(
        self,
        user_id: str,
        credential_id: str
    ) -> str:
        """
        Retrieve API key.
        
        Args:
            user_id: User ID
            credential_id: Credential ID
            
        Returns:
            API key
        """
        try:
            # Verify credential exists and belongs to user
            credential = self.credentials.get(credential_id)
            if not credential:
                raise PluginActionExecutionError("Credential not found")
            
            if credential.user_id != user_id:
                raise PluginActionExecutionError("Access denied")
            
            if credential.credential_type != CredentialType.API_KEY:
                raise PluginActionExecutionError("Invalid credential type")
            
            # Decrypt API key data
            encrypted_data = self.encrypted_data.get(credential_id)
            if not encrypted_data:
                raise PluginActionExecutionError("Credential data not found")
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            key_data = json.loads(decrypted_data.decode())
            
            # Update last used timestamp
            credential.last_used_at = datetime.utcnow()
            
            # Log the operation
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="retrieve_api_key",
                metadata={"provider": credential.provider}
            )
            
            return key_data["api_key"]
            
        except Exception as e:
            logger.error(f"Failed to retrieve API key: {e}")
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="retrieve_api_key",
                success=False,
                error_message=str(e)
            )
            raise PluginActionExecutionError(f"Failed to retrieve API key: {e}")
    
    async def list_user_credentials(
        self,
        user_id: str,
        credential_type: Optional[CredentialType] = None,
        provider: Optional[str] = None
    ) -> List[StoredCredential]:
        """
        List user's stored credentials.
        
        Args:
            user_id: User ID
            credential_type: Filter by credential type
            provider: Filter by provider
            
        Returns:
            List of credentials (without sensitive data)
        """
        try:
            user_credentials = []
            
            for credential in self.credentials.values():
                if credential.user_id != user_id:
                    continue
                
                if credential_type and credential.credential_type != credential_type:
                    continue
                
                if provider and credential.provider != provider:
                    continue
                
                user_credentials.append(credential)
            
            # Log the operation
            await self._log_audit_event(
                user_id=user_id,
                credential_id="",
                action="list_credentials",
                metadata={
                    "credential_type": credential_type.value if credential_type else None,
                    "provider": provider,
                    "count": len(user_credentials)
                }
            )
            
            return user_credentials
            
        except Exception as e:
            logger.error(f"Failed to list user credentials: {e}")
            await self._log_audit_event(
                user_id=user_id,
                credential_id="",
                action="list_credentials",
                success=False,
                error_message=str(e)
            )
            raise PluginActionExecutionError(f"Failed to list credentials: {e}")
    
    async def revoke_credential(
        self,
        user_id: str,
        credential_id: str
    ) -> bool:
        """
        Revoke a stored credential.
        
        Args:
            user_id: User ID
            credential_id: Credential ID
            
        Returns:
            True if successful
        """
        try:
            # Verify credential exists and belongs to user
            credential = self.credentials.get(credential_id)
            if not credential:
                raise PluginActionExecutionError("Credential not found")
            
            if credential.user_id != user_id:
                raise PluginActionExecutionError("Access denied")
            
            # Update credential status
            credential.status = CredentialStatus.REVOKED
            credential.updated_at = datetime.utcnow()
            
            # Remove encrypted data
            if credential_id in self.encrypted_data:
                del self.encrypted_data[credential_id]
            
            # Log the operation
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="revoke_credential",
                metadata={"provider": credential.provider}
            )
            
            logger.info(f"Revoked credential {credential_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke credential: {e}")
            await self._log_audit_event(
                user_id=user_id,
                credential_id=credential_id,
                action="revoke_credential",
                success=False,
                error_message=str(e)
            )
            return False
    
    async def _log_audit_event(
        self,
        user_id: str,
        credential_id: str,
        action: str,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log audit event."""
        try:
            audit_entry = AuditLogEntry(
                entry_id=self._generate_audit_id(),
                user_id=user_id,
                credential_id=credential_id,
                action=action,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message,
                metadata=metadata
            )
            
            self.audit_log.append(audit_entry)
            
            # Keep only last 10000 audit entries in memory
            if len(self.audit_log) > 10000:
                self.audit_log = self.audit_log[-10000:]
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    async def get_audit_log(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """
        Get audit log entries.
        
        Args:
            user_id: Filter by user ID
            start_date: Filter by start date
            end_date: Filter by end date
            action: Filter by action
            limit: Maximum number of entries
            
        Returns:
            List of audit log entries
        """
        try:
            filtered_entries = []
            
            for entry in reversed(self.audit_log):  # Most recent first
                if user_id and entry.user_id != user_id:
                    continue
                
                if start_date and entry.timestamp < start_date:
                    continue
                
                if end_date and entry.timestamp > end_date:
                    continue
                
                if action and entry.action != action:
                    continue
                
                filtered_entries.append(entry)
                
                if len(filtered_entries) >= limit:
                    break
            
            return filtered_entries
            
        except Exception as e:
            logger.error(f"Failed to get audit log: {e}")
            return []


class AuthenticationManager:
    """
    High-level authentication manager that coordinates OAuth and credential management.
    
    Provides a unified interface for all authentication operations in Aideon AI Lite.
    """
    
    def __init__(
        self,
        oauth_manager: OAuthManager,
        credential_vault: SecureCredentialVault,
        api_key_manager: EnhancedApiKeyManager
    ):
        """
        Initialize authentication manager.
        
        Args:
            oauth_manager: OAuth manager instance
            credential_vault: Secure credential vault
            api_key_manager: Enhanced API key manager
        """
        self.oauth_manager = oauth_manager
        self.credential_vault = credential_vault
        self.api_key_manager = api_key_manager
        
        # User session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def initiate_platform_connection(
        self,
        user_id: str,
        provider: str,
        connection_type: str = "oauth",
        scopes: List[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate connection to a platform.
        
        Args:
            user_id: User ID
            provider: Platform provider
            connection_type: Type of connection (oauth, api_key)
            scopes: OAuth scopes (for OAuth connections)
            
        Returns:
            Connection initiation result
        """
        try:
            if connection_type == "oauth":
                # Handle OAuth connection
                oauth_provider = OAuthProvider(provider)
                
                # Get default scopes if none provided
                if not scopes:
                    provider_scopes = self.oauth_manager.get_provider_scopes(oauth_provider)
                    scopes = provider_scopes.get("basic", [])
                
                # Generate authorization URL
                auth_url = await self.oauth_manager.initiate_oauth_flow(
                    provider=oauth_provider,
                    user_id=user_id,
                    requested_scopes=scopes
                )
                
                return {
                    "success": True,
                    "connection_type": "oauth",
                    "provider": provider,
                    "authorization_url": auth_url,
                    "scopes": scopes,
                    "instructions": f"Visit the authorization URL to grant access to {provider}"
                }
            
            elif connection_type == "api_key":
                # Handle API key connection
                return {
                    "success": True,
                    "connection_type": "api_key",
                    "provider": provider,
                    "instructions": f"Please provide your {provider} API key through the admin dashboard"
                }
            
            else:
                raise PluginActionExecutionError(f"Unsupported connection type: {connection_type}")
                
        except Exception as e:
            logger.error(f"Failed to initiate platform connection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def complete_oauth_connection(
        self,
        user_id: str,
        provider: str,
        authorization_code: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Complete OAuth connection flow.
        
        Args:
            user_id: User ID
            provider: OAuth provider
            authorization_code: Authorization code from callback
            state: State parameter
            
        Returns:
            Connection completion result
        """
        try:
            oauth_provider = OAuthProvider(provider)
            
            # Complete OAuth flow
            tokens, user_info = await self.oauth_manager.complete_oauth_flow(
                provider=oauth_provider,
                authorization_code=authorization_code,
                state=state
            )
            
            # Store tokens in credential vault
            credential_id = await self.credential_vault.store_oauth_tokens(
                user_id=user_id,
                provider=oauth_provider,
                tokens=tokens,
                metadata={"user_info": user_info}
            )
            
            return {
                "success": True,
                "provider": provider,
                "credential_id": credential_id,
                "user_info": user_info,
                "expires_at": tokens.expires_at.isoformat() if tokens.expires_at else None,
                "scopes": tokens.scope
            }
            
        except Exception as e:
            logger.error(f"Failed to complete OAuth connection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def store_api_key_credential(
        self,
        user_id: str,
        provider: str,
        api_key: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Store API key credential.
        
        Args:
            user_id: User ID
            provider: API provider
            api_key: API key
            metadata: Additional metadata
            
        Returns:
            Storage result
        """
        try:
            credential_id = await self.credential_vault.store_api_key(
                user_id=user_id,
                provider=provider,
                api_key=api_key,
                metadata=metadata
            )
            
            return {
                "success": True,
                "provider": provider,
                "credential_id": credential_id,
                "message": f"API key for {provider} stored successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to store API key: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_connections(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get all user's platform connections.
        
        Args:
            user_id: User ID
            
        Returns:
            User's connections
        """
        try:
            # Get all credentials for user
            credentials = await self.credential_vault.list_user_credentials(user_id)
            
            # Group by provider and type
            connections = {}
            for credential in credentials:
                provider = credential.provider
                if provider not in connections:
                    connections[provider] = []
                
                connection_info = {
                    "credential_id": credential.credential_id,
                    "type": credential.credential_type.value,
                    "status": credential.status.value,
                    "created_at": credential.created_at.isoformat(),
                    "updated_at": credential.updated_at.isoformat(),
                    "expires_at": credential.expires_at.isoformat() if credential.expires_at else None,
                    "last_used_at": credential.last_used_at.isoformat() if credential.last_used_at else None,
                    "scopes": credential.scopes,
                    "is_expired": credential.is_expired(),
                    "expires_soon": credential.expires_soon()
                }
                
                connections[provider].append(connection_info)
            
            return {
                "success": True,
                "user_id": user_id,
                "connections": connections,
                "total_connections": len(credentials)
            }
            
        except Exception as e:
            logger.error(f"Failed to get user connections: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def refresh_connection_if_needed(
        self,
        user_id: str,
        credential_id: str
    ) -> Dict[str, Any]:
        """
        Refresh connection credentials if needed.
        
        Args:
            user_id: User ID
            credential_id: Credential ID
            
        Returns:
            Refresh result
        """
        try:
            # Get credential info
            credentials = await self.credential_vault.list_user_credentials(user_id)
            credential = next((c for c in credentials if c.credential_id == credential_id), None)
            
            if not credential:
                raise PluginActionExecutionError("Credential not found")
            
            if credential.credential_type != CredentialType.OAUTH_TOKEN:
                return {
                    "success": True,
                    "message": "Credential type does not require refresh",
                    "refreshed": False
                }
            
            # Get current tokens
            tokens = await self.credential_vault.retrieve_oauth_tokens(user_id, credential_id)
            
            if not tokens.expires_soon():
                return {
                    "success": True,
                    "message": "Tokens do not need refresh yet",
                    "refreshed": False
                }
            
            # Refresh tokens
            oauth_provider = OAuthProvider(credential.provider)
            refreshed_tokens = await self.oauth_manager.refresh_tokens_if_needed(
                provider=oauth_provider,
                tokens=tokens
            )
            
            # Update stored tokens
            await self.credential_vault.update_oauth_tokens(
                user_id=user_id,
                credential_id=credential_id,
                tokens=refreshed_tokens
            )
            
            return {
                "success": True,
                "message": "Tokens refreshed successfully",
                "refreshed": True,
                "new_expires_at": refreshed_tokens.expires_at.isoformat() if refreshed_tokens.expires_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh connection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def revoke_connection(
        self,
        user_id: str,
        credential_id: str
    ) -> Dict[str, Any]:
        """
        Revoke a platform connection.
        
        Args:
            user_id: User ID
            credential_id: Credential ID
            
        Returns:
            Revocation result
        """
        try:
            # Get credential info
            credentials = await self.credential_vault.list_user_credentials(user_id)
            credential = next((c for c in credentials if c.credential_id == credential_id), None)
            
            if not credential:
                raise PluginActionExecutionError("Credential not found")
            
            # For OAuth tokens, revoke with provider
            if credential.credential_type == CredentialType.OAUTH_TOKEN:
                tokens = await self.credential_vault.retrieve_oauth_tokens(user_id, credential_id)
                oauth_provider = OAuthProvider(credential.provider)
                
                # Attempt to revoke with provider
                await self.oauth_manager.revoke_user_tokens(
                    provider=oauth_provider,
                    tokens=tokens
                )
            
            # Revoke in credential vault
            success = await self.credential_vault.revoke_credential(user_id, credential_id)
            
            return {
                "success": success,
                "message": f"Connection to {credential.provider} revoked successfully" if success else "Failed to revoke connection"
            }
            
        except Exception as e:
            logger.error(f"Failed to revoke connection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_credential_for_provider(
        self,
        user_id: str,
        provider: str,
        credential_type: CredentialType = None
    ) -> Optional[Tuple[str, Any]]:
        """
        Get active credential for a provider.
        
        Args:
            user_id: User ID
            provider: Provider name
            credential_type: Credential type filter
            
        Returns:
            Tuple of (credential_id, credential_data) or None
        """
        try:
            credentials = await self.credential_vault.list_user_credentials(
                user_id=user_id,
                provider=provider,
                credential_type=credential_type
            )
            
            # Find active, non-expired credential
            for credential in credentials:
                if credential.status != CredentialStatus.ACTIVE:
                    continue
                
                if credential.is_expired():
                    continue
                
                # Get credential data
                if credential.credential_type == CredentialType.OAUTH_TOKEN:
                    tokens = await self.credential_vault.retrieve_oauth_tokens(
                        user_id, credential.credential_id
                    )
                    return credential.credential_id, tokens
                
                elif credential.credential_type == CredentialType.API_KEY:
                    api_key = await self.credential_vault.retrieve_api_key(
                        user_id, credential.credential_id
                    )
                    return credential.credential_id, api_key
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get credential for provider {provider}: {e}")
            return None
    
    async def cleanup(self):
        """Clean up authentication manager resources."""
        await self.oauth_manager.cleanup()
        logger.info("Authentication manager cleaned up")

