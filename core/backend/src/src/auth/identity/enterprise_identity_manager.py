"""
Enterprise Identity Integration module for ApexAgent.

This module provides integration with enterprise identity systems,
including SAML, OAuth, and directory services.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from src.core.error_handling.errors import AuthenticationError, ConfigurationError
from src.core.event_system.event_manager import EventManager
from src.auth.identity.identity_manager import IdentityProvider, OAuthProvider
from src.auth.identity.saml_directory_provider import SAMLProvider, DirectoryServiceProvider
from src.auth.authentication.auth_manager import User, AuthenticationManager

logger = logging.getLogger(__name__)

class EnterpriseIdentityManager:
    """
    Manages enterprise identity integration, including SSO and directory services.
    """
    def __init__(
        self,
        auth_manager: AuthenticationManager = None,
        event_manager: EventManager = None
    ):
        self.auth_manager = auth_manager or AuthenticationManager()
        self.event_manager = event_manager or EventManager()
        
        # Identity providers
        self.providers: Dict[str, IdentityProvider] = {}
        
        # User identity mappings
        self.user_identities: Dict[str, Dict[str, Dict[str, Any]]] = {}  # user_id -> provider_id -> identity_data
        
        # Provider type indexes
        self.provider_types: Dict[str, List[str]] = {}  # provider_type -> [provider_id]
        
    def register_provider(self, provider: IdentityProvider) -> IdentityProvider:
        """
        Register an identity provider.
        
        Args:
            provider: IdentityProvider instance
            
        Returns:
            Registered IdentityProvider
            
        Raises:
            ConfigurationError: If provider ID already exists
        """
        if provider.provider_id in self.providers:
            raise ConfigurationError(f"Identity provider '{provider.provider_id}' already registered")
            
        # Store provider
        self.providers[provider.provider_id] = provider
        
        # Update provider type index
        if provider.provider_type not in self.provider_types:
            self.provider_types[provider.provider_type] = []
        self.provider_types[provider.provider_type].append(provider.provider_id)
        
        # Emit event
        self.event_manager.emit_event("identity.provider_registered", {
            "provider_id": provider.provider_id,
            "provider_type": provider.provider_type,
            "name": provider.name,
            "timestamp": datetime.now().isoformat()
        })
        
        return provider
    
    def get_provider(self, provider_id: str) -> Optional[IdentityProvider]:
        """
        Get an identity provider by ID.
        
        Args:
            provider_id: Provider ID to get
            
        Returns:
            IdentityProvider instance or None if not found
        """
        return self.providers.get(provider_id)
    
    def get_providers_by_type(self, provider_type: str) -> List[IdentityProvider]:
        """
        Get all identity providers of a specific type.
        
        Args:
            provider_type: Provider type to filter by
            
        Returns:
            List of IdentityProvider instances
        """
        if provider_type not in self.provider_types:
            return []
            
        return [self.providers[provider_id] for provider_id in self.provider_types[provider_type]
                if provider_id in self.providers]
    
    def get_login_options(self) -> List[Dict[str, Any]]:
        """
        Get all available login options.
        
        Returns:
            List of login option details
        """
        login_options = []
        
        for provider_id, provider in self.providers.items():
            if not provider.is_active:
                continue
                
            option = {
                "provider_id": provider_id,
                "name": provider.name,
                "type": provider.provider_type
            }
            
            login_options.append(option)
            
        return login_options
    
    def initiate_sso_login(self, provider_id: str) -> Dict[str, Any]:
        """
        Initiate SSO login with a specific provider.
        
        Args:
            provider_id: Provider ID to use
            
        Returns:
            Dictionary containing login details
            
        Raises:
            ConfigurationError: If provider does not exist or is not active
            AuthenticationError: If login initiation fails
        """
        provider = self.get_provider(provider_id)
        if not provider:
            raise ConfigurationError(f"Identity provider '{provider_id}' not found")
            
        if not provider.is_active:
            raise ConfigurationError(f"Identity provider '{provider_id}' is not active")
            
        if provider.provider_type == "saml":
            if not isinstance(provider, SAMLProvider):
                raise ConfigurationError(f"Provider '{provider_id}' is not a SAML provider")
                
            try:
                login_data = provider.get_login_url()
                
                # Emit event
                self.event_manager.emit_event("identity.sso_initiated", {
                    "provider_id": provider_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                return login_data
                
            except Exception as e:
                logger.error(f"Error initiating SAML login: {e}")
                raise AuthenticationError(f"Failed to initiate SAML login: {e}")
                
        elif provider.provider_type == "oauth":
            if not isinstance(provider, OAuthProvider):
                raise ConfigurationError(f"Provider '{provider_id}' is not an OAuth provider")
                
            try:
                # Generate state for CSRF protection
                state = os.urandom(16).hex()
                
                # Get authorization URL
                redirect_uri = provider.config.get("redirect_uri", "")
                scopes = provider.config.get("scopes", ["openid", "profile", "email"])
                
                auth_url = provider.get_authorization_url(
                    redirect_uri=redirect_uri,
                    state=state,
                    scopes=scopes
                )
                
                # Emit event
                self.event_manager.emit_event("identity.sso_initiated", {
                    "provider_id": provider_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "login_url": auth_url,
                    "state": state
                }
                
            except Exception as e:
                logger.error(f"Error initiating OAuth login: {e}")
                raise AuthenticationError(f"Failed to initiate OAuth login: {e}")
                
        else:
            raise ConfigurationError(f"Provider type '{provider.provider_type}' does not support SSO login")
    
    def complete_sso_login(
        self,
        provider_id: str,
        response_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Complete SSO login with a specific provider.
        
        Args:
            provider_id: Provider ID used
            response_data: Response data from the provider
            
        Returns:
            Tuple of (success, user, error_message)
            
        Raises:
            ConfigurationError: If provider does not exist or is not active
            AuthenticationError: If login completion fails
        """
        provider = self.get_provider(provider_id)
        if not provider:
            raise ConfigurationError(f"Identity provider '{provider_id}' not found")
            
        if not provider.is_active:
            raise ConfigurationError(f"Identity provider '{provider_id}' is not active")
            
        if provider.provider_type == "saml":
            if not isinstance(provider, SAMLProvider):
                raise ConfigurationError(f"Provider '{provider_id}' is not a SAML provider")
                
            try:
                saml_response = response_data.get("SAMLResponse")
                relay_state = response_data.get("RelayState")
                
                if not saml_response:
                    return False, None, "SAML response is missing"
                    
                # Process SAML response
                success, user_info, error = provider.process_saml_response(saml_response, relay_state)
                
                if not success or not user_info:
                    return False, None, error or "SAML authentication failed"
                    
                # Find or create user
                return self._process_identity_login(provider_id, user_info)
                
            except Exception as e:
                logger.error(f"Error completing SAML login: {e}")
                raise AuthenticationError(f"Failed to complete SAML login: {e}")
                
        elif provider.provider_type == "oauth":
            if not isinstance(provider, OAuthProvider):
                raise ConfigurationError(f"Provider '{provider_id}' is not an OAuth provider")
                
            try:
                code = response_data.get("code")
                state = response_data.get("state")
                error = response_data.get("error")
                
                if error:
                    return False, None, f"OAuth error: {error}"
                    
                if not code:
                    return False, None, "Authorization code is missing"
                    
                # Exchange code for token
                redirect_uri = provider.config.get("redirect_uri", "")
                token_data = provider.exchange_code_for_token(code, redirect_uri)
                
                if not token_data or "access_token" not in token_data:
                    return False, None, "Failed to exchange code for token"
                    
                # Get user info
                success, user_info, error = provider.get_user_info(token_data["access_token"])
                
                if not success or not user_info:
                    return False, None, error or "Failed to get user info"
                    
                # Find or create user
                return self._process_identity_login(provider_id, user_info)
                
            except Exception as e:
                logger.error(f"Error completing OAuth login: {e}")
                raise AuthenticationError(f"Failed to complete OAuth login: {e}")
                
        else:
            raise ConfigurationError(f"Provider type '{provider.provider_type}' does not support SSO login")
    
    def authenticate_with_directory(
        self,
        provider_id: str,
        username: str,
        password: str
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate a user with a directory service.
        
        Args:
            provider_id: Provider ID to use
            username: Username to authenticate
            password: Password to authenticate
            
        Returns:
            Tuple of (success, user, error_message)
            
        Raises:
            ConfigurationError: If provider does not exist or is not active
            AuthenticationError: If authentication fails
        """
        provider = self.get_provider(provider_id)
        if not provider:
            raise ConfigurationError(f"Identity provider '{provider_id}' not found")
            
        if not provider.is_active:
            raise ConfigurationError(f"Identity provider '{provider_id}' is not active")
            
        if provider.provider_type != "directory":
            raise ConfigurationError(f"Provider '{provider_id}' is not a directory service provider")
            
        if not isinstance(provider, DirectoryServiceProvider):
            raise ConfigurationError(f"Provider '{provider_id}' is not a directory service provider")
            
        try:
            # Authenticate with directory
            credentials = {
                "username": username,
                "password": password
            }
            
            success, user_info, error = provider.authenticate(credentials)
            
            if not success or not user_info:
                return False, None, error or "Directory authentication failed"
                
            # Find or create user
            return self._process_identity_login(provider_id, user_info)
            
        except Exception as e:
            logger.error(f"Error authenticating with directory: {e}")
            raise AuthenticationError(f"Failed to authenticate with directory: {e}")
    
    def _process_identity_login(
        self,
        provider_id: str,
        user_info: Dict[str, Any]
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Process a successful identity login.
        
        Args:
            provider_id: Provider ID used
            user_info: User information from the provider
            
        Returns:
            Tuple of (success, user, error_message)
        """
        try:
            # Extract identity identifier
            identity_id = user_info.get("user_id")
            if not identity_id:
                return False, None, "Identity identifier is missing"
                
            # Check if we have a user mapping for this identity
            existing_user_id = self._find_user_by_identity(provider_id, identity_id)
            
            if existing_user_id:
                # User exists, update identity data
                user = self.auth_manager.get_user_by_id(existing_user_id)
                if not user:
                    return False, None, "User not found"
                    
                if not user.is_active:
                    return False, None, "User account is disabled"
                    
                # Update identity data
                self._update_user_identity(user.user_id, provider_id, user_info)
                
                # Update user profile if needed
                self._sync_user_profile(user, user_info)
                
                # Create session
                session = self.auth_manager.create_session(user.user_id)
                
                # Emit event
                self.event_manager.emit_event("identity.login_success", {
                    "user_id": user.user_id,
                    "provider_id": provider_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                return True, user, None
                
            else:
                # User doesn't exist, create new user if auto-provisioning is enabled
                provider = self.get_provider(provider_id)
                auto_provision = provider.config.get("auto_provision_users", False)
                
                if not auto_provision:
                    return False, None, "User not found and auto-provisioning is disabled"
                    
                # Create new user
                email = user_info.get("email")
                if not email:
                    return False, None, "Email is required for user provisioning"
                    
                # Generate username if not provided
                username = user_info.get("username")
                if not username:
                    username = email.split("@")[0]
                    
                    # Ensure username is unique
                    base_username = username
                    suffix = 1
                    while self.auth_manager.get_user_by_username(username):
                        username = f"{base_username}{suffix}"
                        suffix += 1
                
                # Generate random password for the user
                # In a real system, you might want to force password change on first login
                password = os.urandom(16).hex()
                
                # Create user
                user = self.auth_manager.register_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=user_info.get("first_name"),
                    last_name=user_info.get("last_name"),
                    metadata={
                        "provisioned_by": provider_id,
                        "provisioned_at": datetime.now().isoformat()
                    }
                )
                
                # Store identity mapping
                self._store_user_identity(user.user_id, provider_id, user_info)
                
                # Create session
                session = self.auth_manager.create_session(user.user_id)
                
                # Emit event
                self.event_manager.emit_event("identity.user_provisioned", {
                    "user_id": user.user_id,
                    "provider_id": provider_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                return True, user, None
                
        except Exception as e:
            logger.error(f"Error processing identity login: {e}")
            return False, None, f"Failed to process identity login: {e}"
    
    def _find_user_by_identity(self, provider_id: str, identity_id: str) -> Optional[str]:
        """
        Find a user by identity.
        
        Args:
            provider_id: Provider ID
            identity_id: Identity identifier
            
        Returns:
            User ID or None if not found
        """
        for user_id, identities in self.user_identities.items():
            if provider_id in identities:
                if identities[provider_id].get("identity_id") == identity_id:
                    return user_id
        return None
    
    def _store_user_identity(self, user_id: str, provider_id: str, user_info: Dict[str, Any]) -> None:
        """
        Store a user identity mapping.
        
        Args:
            user_id: User ID
            provider_id: Provider ID
            user_info: User information from the provider
        """
        identity_data = {
            "identity_id": user_info.get("user_id"),
            "provider_id": provider_id,
            "provider_type": user_info.get("provider_type"),
            "linked_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "user_info": user_info
        }
        
        # Initialize user identities if needed
        if user_id not in self.user_identities:
            self.user_identities[user_id] = {}
            
        # Store identity data
        self.user_identities[user_id][provider_id] = identity_data
    
    def _update_user_identity(self, user_id: str, provider_id: str, user_info: Dict[str, Any]) -> None:
        """
        Update a user identity mapping.
        
        Args:
            user_id: User ID
            provider_id: Provider ID
            user_info: User information from the provider
        """
        if user_id not in self.user_identities or provider_id not in self.user_identities[user_id]:
            # Identity doesn't exist, store it
            self._store_user_identity(user_id, provider_id, user_info)
            return
            
        # Update existing identity
        identity_data = self.user_identities[user_id][provider_id]
        identity_data["last_login"] = datetime.now().isoformat()
        identity_data["user_info"] = user_info
    
    def _sync_user_profile(self, user: User, user_info: Dict[str, Any]) -> None:
        """
        Synchronize user profile with identity provider data.
        
        Args:
            user: User object
            user_info: User information from the provider
        """
        # Check if profile sync is needed
        provider_id = user_info.get("provider_id")
        provider = self.get_provider(provider_id)
        
        if not provider:
            return
            
        sync_profile = provider.config.get("sync_user_profile", False)
        if not sync_profile:
            return
            
        # Check for profile updates
        updates = {}
        
        if "email" in user_info and user_info["email"] != user.email:
            updates["email"] = user_info["email"]
            
        if "first_name" in user_info and user_info["first_name"] != user.first_name:
            updates["first_name"] = user_info["first_name"]
            
        if "last_name" in user_info and user_info["last_name"] != user.last_name:
            updates["last_name"] = user_info["last_name"]
            
        # Apply updates if needed
        if updates:
            self.auth_manager.update_user(
                user_id=user.user_id,
                **updates
            )
    
    def get_user_identities(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all identities for a user.
        
        Args:
            user_id: User ID to get identities for
            
        Returns:
            List of identity details
        """
        if user_id not in self.user_identities:
            return []
            
        identities = []
        for provider_id, identity_data in self.user_identities[user_id].items():
            provider = self.get_provider(provider_id)
            
            identity = {
                "provider_id": provider_id,
                "provider_name": provider.name if provider else "Unknown",
                "provider_type": identity_data.get("provider_type", "unknown"),
                "identity_id": identity_data.get("identity_id"),
                "linked_at": identity_data.get("linked_at"),
                "last_login": identity_data.get("last_login")
            }
            
            identities.append(identity)
            
        return identities
    
    def link_identity(
        self,
        user_id: str,
        provider_id: str,
        identity_id: str,
        user_info: Dict[str, Any]
    ) -> bool:
        """
        Link an identity to a user.
        
        Args:
            user_id: User ID to link identity to
            provider_id: Provider ID
            identity_id: Identity identifier
            user_info: User information from the provider
            
        Returns:
            True if identity was linked, False otherwise
            
        Raises:
            AuthenticationError: If identity is already linked to another user
        """
        # Check if identity is already linked to another user
        existing_user_id = self._find_user_by_identity(provider_id, identity_id)
        if existing_user_id and existing_user_id != user_id:
            raise AuthenticationError("Identity is already linked to another user")
            
        # Store identity mapping
        user_info["user_id"] = identity_id
        self._store_user_identity(user_id, provider_id, user_info)
        
        # Emit event
        self.event_manager.emit_event("identity.identity_linked", {
            "user_id": user_id,
            "provider_id": provider_id,
            "identity_id": identity_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def unlink_identity(self, user_id: str, provider_id: str) -> bool:
        """
        Unlink an identity from a user.
        
        Args:
            user_id: User ID to unlink identity from
            provider_id: Provider ID
            
        Returns:
            True if identity was unlinked, False otherwise
        """
        if user_id not in self.user_identities or provider_id not in self.user_identities[user_id]:
            return False
            
        # Remove identity
        identity_data = self.user_identities[user_id].pop(provider_id)
        
        # Emit event
        self.event_manager.emit_event("identity.identity_unlinked", {
            "user_id": user_id,
            "provider_id": provider_id,
            "identity_id": identity_data.get("identity_id"),
            "timestamp": datetime.now().isoformat()
        })
        
        return True
