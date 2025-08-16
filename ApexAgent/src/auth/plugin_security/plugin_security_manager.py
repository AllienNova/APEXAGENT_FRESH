"""
Plugin Permission Management module for ApexAgent.

This module provides a comprehensive security model for plugin permissions,
including isolation, user consent flows, and inter-plugin communication security.
"""

import os
import json
import uuid
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable

from src.core.error_handling.errors import SecurityError, ConfigurationError
from src.core.event_system.event_manager import EventManager
from src.core.plugin_security import PluginSecurityContext
from src.auth.authorization.enhanced_rbac import EnhancedRBACManager

logger = logging.getLogger(__name__)

class PluginPermission:
    """
    Represents a permission that can be granted to a plugin.
    """
    def __init__(
        self,
        permission_id: str,
        name: str,
        description: str,
        risk_level: str,
        category: str,
        is_dangerous: bool = False,
        requires_explicit_consent: bool = False,
        metadata: Dict[str, Any] = None
    ):
        self.permission_id = permission_id
        self.name = name
        self.description = description
        self.risk_level = risk_level  # "low", "medium", "high", "critical"
        self.category = category
        self.is_dangerous = is_dangerous
        self.requires_explicit_consent = requires_explicit_consent
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert permission object to dictionary representation.
        
        Returns:
            Dictionary representation of the permission
        """
        return {
            "permission_id": self.permission_id,
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level,
            "category": self.category,
            "is_dangerous": self.is_dangerous,
            "requires_explicit_consent": self.requires_explicit_consent,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, permission_dict: Dict[str, Any]) -> 'PluginPermission':
        """
        Create a permission object from dictionary representation.
        
        Args:
            permission_dict: Dictionary representation of the permission
            
        Returns:
            PluginPermission object
        """
        return cls(
            permission_id=permission_dict["permission_id"],
            name=permission_dict["name"],
            description=permission_dict["description"],
            risk_level=permission_dict["risk_level"],
            category=permission_dict["category"],
            is_dangerous=permission_dict.get("is_dangerous", False),
            requires_explicit_consent=permission_dict.get("requires_explicit_consent", False),
            metadata=permission_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"PluginPermission(id={self.permission_id}, name={self.name}, risk={self.risk_level})"


class PluginManifest:
    """
    Represents a plugin manifest with metadata and requested permissions.
    """
    def __init__(
        self,
        plugin_id: str,
        name: str,
        version: str,
        author: str,
        description: str,
        requested_permissions: List[str],
        entry_point: str,
        min_api_version: str,
        max_api_version: Optional[str] = None,
        homepage: Optional[str] = None,
        repository: Optional[str] = None,
        license: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.requested_permissions = requested_permissions
        self.entry_point = entry_point
        self.min_api_version = min_api_version
        self.max_api_version = max_api_version
        self.homepage = homepage
        self.repository = repository
        self.license = license
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert manifest object to dictionary representation.
        
        Returns:
            Dictionary representation of the manifest
        """
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "requested_permissions": self.requested_permissions,
            "entry_point": self.entry_point,
            "min_api_version": self.min_api_version,
            "max_api_version": self.max_api_version,
            "homepage": self.homepage,
            "repository": self.repository,
            "license": self.license,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, manifest_dict: Dict[str, Any]) -> 'PluginManifest':
        """
        Create a manifest object from dictionary representation.
        
        Args:
            manifest_dict: Dictionary representation of the manifest
            
        Returns:
            PluginManifest object
        """
        return cls(
            plugin_id=manifest_dict["plugin_id"],
            name=manifest_dict["name"],
            version=manifest_dict["version"],
            author=manifest_dict["author"],
            description=manifest_dict["description"],
            requested_permissions=manifest_dict["requested_permissions"],
            entry_point=manifest_dict["entry_point"],
            min_api_version=manifest_dict["min_api_version"],
            max_api_version=manifest_dict.get("max_api_version"),
            homepage=manifest_dict.get("homepage"),
            repository=manifest_dict.get("repository"),
            license=manifest_dict.get("license"),
            metadata=manifest_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"PluginManifest(id={self.plugin_id}, name={self.name}, version={self.version})"


class PluginConsent:
    """
    Represents a user's consent for plugin permissions.
    """
    def __init__(
        self,
        consent_id: str,
        user_id: str,
        plugin_id: str,
        granted_permissions: List[str],
        denied_permissions: List[str],
        created_at: datetime = None,
        expires_at: Optional[datetime] = None,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.consent_id = consent_id or str(uuid.uuid4())
        self.user_id = user_id
        self.plugin_id = plugin_id
        self.granted_permissions = granted_permissions
        self.denied_permissions = denied_permissions
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert consent object to dictionary representation.
        
        Returns:
            Dictionary representation of the consent
        """
        return {
            "consent_id": self.consent_id,
            "user_id": self.user_id,
            "plugin_id": self.plugin_id,
            "granted_permissions": self.granted_permissions,
            "denied_permissions": self.denied_permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, consent_dict: Dict[str, Any]) -> 'PluginConsent':
        """
        Create a consent object from dictionary representation.
        
        Args:
            consent_dict: Dictionary representation of the consent
            
        Returns:
            PluginConsent object
        """
        created_at = consent_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        expires_at = consent_dict.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        return cls(
            consent_id=consent_dict.get("consent_id"),
            user_id=consent_dict["user_id"],
            plugin_id=consent_dict["plugin_id"],
            granted_permissions=consent_dict["granted_permissions"],
            denied_permissions=consent_dict["denied_permissions"],
            created_at=created_at,
            expires_at=expires_at,
            is_active=consent_dict.get("is_active", True),
            metadata=consent_dict.get("metadata", {})
        )
    
    def is_expired(self) -> bool:
        """
        Check if the consent is expired.
        
        Returns:
            True if consent is expired, False otherwise
        """
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def has_permission(self, permission_id: str) -> bool:
        """
        Check if a permission is granted.
        
        Args:
            permission_id: Permission ID to check
            
        Returns:
            True if permission is granted, False otherwise
        """
        if not self.is_active or self.is_expired():
            return False
            
        if permission_id in self.denied_permissions:
            return False
            
        return permission_id in self.granted_permissions
    
    def __str__(self) -> str:
        return f"PluginConsent(id={self.consent_id}, user={self.user_id}, plugin={self.plugin_id})"


class PluginSecurityToken:
    """
    Represents a security token for plugin authentication.
    """
    def __init__(
        self,
        token_id: str,
        plugin_id: str,
        user_id: str,
        token_value: str,
        created_at: datetime = None,
        expires_at: Optional[datetime] = None,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.token_id = token_id or str(uuid.uuid4())
        self.plugin_id = plugin_id
        self.user_id = user_id
        self.token_value = token_value
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert token object to dictionary representation.
        
        Returns:
            Dictionary representation of the token
        """
        return {
            "token_id": self.token_id,
            "plugin_id": self.plugin_id,
            "user_id": self.user_id,
            "token_value": self.token_value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, token_dict: Dict[str, Any]) -> 'PluginSecurityToken':
        """
        Create a token object from dictionary representation.
        
        Args:
            token_dict: Dictionary representation of the token
            
        Returns:
            PluginSecurityToken object
        """
        created_at = token_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        expires_at = token_dict.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        return cls(
            token_id=token_dict.get("token_id"),
            plugin_id=token_dict["plugin_id"],
            user_id=token_dict["user_id"],
            token_value=token_dict["token_value"],
            created_at=created_at,
            expires_at=expires_at,
            is_active=token_dict.get("is_active", True),
            metadata=token_dict.get("metadata", {})
        )
    
    def is_expired(self) -> bool:
        """
        Check if the token is expired.
        
        Returns:
            True if token is expired, False otherwise
        """
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """
        Check if the token is valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        return self.is_active and not self.is_expired()
    
    def __str__(self) -> str:
        return f"PluginSecurityToken(id={self.token_id}, plugin={self.plugin_id}, user={self.user_id})"


class PluginSecurityManager:
    """
    Manages plugin security, permissions, and consent.
    """
    def __init__(
        self,
        rbac_manager: EnhancedRBACManager = None,
        event_manager: EventManager = None
    ):
        self.rbac_manager = rbac_manager or EnhancedRBACManager()
        self.event_manager = event_manager or EventManager()
        
        # Plugin permissions
        self.permissions: Dict[str, PluginPermission] = {}
        self.permission_categories: Dict[str, List[str]] = {}  # category -> [permission_id]
        
        # Plugin manifests
        self.manifests: Dict[str, PluginManifest] = {}
        
        # User consents
        self.consents: Dict[str, PluginConsent] = {}  # consent_id -> PluginConsent
        self.user_plugin_consents: Dict[str, Dict[str, str]] = {}  # user_id -> plugin_id -> consent_id
        
        # Security tokens
        self.tokens: Dict[str, PluginSecurityToken] = {}  # token_id -> PluginSecurityToken
        self.token_values: Dict[str, str] = {}  # token_value -> token_id
        
        # Plugin security contexts
        self.security_contexts: Dict[str, Dict[str, PluginSecurityContext]] = {}  # plugin_id -> user_id -> PluginSecurityContext
        
        # Register default permissions
        self._register_default_permissions()
        
    def _register_default_permissions(self) -> None:
        """
        Register default plugin permissions.
        """
        # File system permissions
        self.register_permission(PluginPermission(
            permission_id="file.read",
            name="Read Files",
            description="Read files from the file system",
            risk_level="medium",
            category="file_system",
            is_dangerous=False,
            requires_explicit_consent=True
        ))
        
        self.register_permission(PluginPermission(
            permission_id="file.write",
            name="Write Files",
            description="Write files to the file system",
            risk_level="high",
            category="file_system",
            is_dangerous=True,
            requires_explicit_consent=True
        ))
        
        self.register_permission(PluginPermission(
            permission_id="file.delete",
            name="Delete Files",
            description="Delete files from the file system",
            risk_level="high",
            category="file_system",
            is_dangerous=True,
            requires_explicit_consent=True
        ))
        
        # Network permissions
        self.register_permission(PluginPermission(
            permission_id="network.connect",
            name="Network Connection",
            description="Connect to network resources",
            risk_level="medium",
            category="network",
            is_dangerous=False,
            requires_explicit_consent=True
        ))
        
        self.register_permission(PluginPermission(
            permission_id="network.listen",
            name="Network Listening",
            description="Listen for incoming network connections",
            risk_level="high",
            category="network",
            is_dangerous=True,
            requires_explicit_consent=True
        ))
        
        # System permissions
        self.register_permission(PluginPermission(
            permission_id="system.execute",
            name="Execute Commands",
            description="Execute system commands",
            risk_level="critical",
            category="system",
            is_dangerous=True,
            requires_explicit_consent=True
        ))
        
        self.register_permission(PluginPermission(
            permission_id="system.info",
            name="System Information",
            description="Access system information",
            risk_level="medium",
            category="system",
            is_dangerous=False,
            requires_explicit_consent=True
        ))
        
        # User data permissions
        self.register_permission(PluginPermission(
            permission_id="user.profile",
            name="User Profile",
            description="Access user profile information",
            risk_level="medium",
            category="user_data",
            is_dangerous=False,
            requires_explicit_consent=True
        ))
        
        self.register_permission(PluginPermission(
            permission_id="user.contacts",
            name="User Contacts",
            description="Access user contacts",
            risk_level="high",
            category="user_data",
            is_dangerous=True,
            requires_explicit_consent=True
        ))
        
        # Inter-plugin communication permissions
        self.register_permission(PluginPermission(
            permission_id="plugin.communicate",
            name="Inter-Plugin Communication",
            description="Communicate with other plugins",
            risk_level="medium",
            category="plugin",
            is_dangerous=False,
            requires_explicit_consent=True
        ))
        
        self.register_permission(PluginPermission(
            permission_id="plugin.data_access",
            name="Plugin Data Access",
            description="Access data from other plugins",
            risk_level="high",
            category="plugin",
            is_dangerous=True,
            requires_explicit_consent=True
        ))
    
    def register_permission(self, permission: PluginPermission) -> PluginPermission:
        """
        Register a plugin permission.
        
        Args:
            permission: PluginPermission instance
            
        Returns:
            Registered PluginPermission
            
        Raises:
            ConfigurationError: If permission ID already exists
        """
        if permission.permission_id in self.permissions:
            raise ConfigurationError(f"Permission '{permission.permission_id}' already registered")
            
        # Store permission
        self.permissions[permission.permission_id] = permission
        
        # Update category index
        if permission.category not in self.permission_categories:
            self.permission_categories[permission.category] = []
        self.permission_categories[permission.category].append(permission.permission_id)
        
        # Emit event
        self.event_manager.emit_event("plugin_security.permission_registered", {
            "permission_id": permission.permission_id,
            "name": permission.name,
            "category": permission.category,
            "risk_level": permission.risk_level,
            "timestamp": datetime.now().isoformat()
        })
        
        return permission
    
    def get_permission(self, permission_id: str) -> Optional[PluginPermission]:
        """
        Get a permission by ID.
        
        Args:
            permission_id: Permission ID to get
            
        Returns:
            PluginPermission instance or None if not found
        """
        return self.permissions.get(permission_id)
    
    def get_permissions_by_category(self, category: str) -> List[PluginPermission]:
        """
        Get all permissions in a category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of PluginPermission instances
        """
        if category not in self.permission_categories:
            return []
            
        return [self.permissions[permission_id] for permission_id in self.permission_categories[category]
                if permission_id in self.permissions]
    
    def register_plugin_manifest(self, manifest: PluginManifest) -> PluginManifest:
        """
        Register a plugin manifest.
        
        Args:
            manifest: PluginManifest instance
            
        Returns:
            Registered PluginManifest
            
        Raises:
            ConfigurationError: If plugin ID already exists or requested permissions are invalid
        """
        if manifest.plugin_id in self.manifests:
            raise ConfigurationError(f"Plugin '{manifest.plugin_id}' already registered")
            
        # Validate requested permissions
        for permission_id in manifest.requested_permissions:
            if permission_id not in self.permissions:
                raise ConfigurationError(f"Invalid permission '{permission_id}' requested by plugin '{manifest.plugin_id}'")
        
        # Store manifest
        self.manifests[manifest.plugin_id] = manifest
        
        # Emit event
        self.event_manager.emit_event("plugin_security.manifest_registered", {
            "plugin_id": manifest.plugin_id,
            "name": manifest.name,
            "version": manifest.version,
            "requested_permissions": manifest.requested_permissions,
            "timestamp": datetime.now().isoformat()
        })
        
        return manifest
    
    def get_plugin_manifest(self, plugin_id: str) -> Optional[PluginManifest]:
        """
        Get a plugin manifest by ID.
        
        Args:
            plugin_id: Plugin ID to get
            
        Returns:
            PluginManifest instance or None if not found
        """
        return self.manifests.get(plugin_id)
    
    def request_user_consent(
        self,
        user_id: str,
        plugin_id: str,
        requested_permissions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Request user consent for plugin permissions.
        
        Args:
            user_id: User ID to request consent from
            plugin_id: Plugin ID to request consent for
            requested_permissions: Optional list of specific permissions to request
            
        Returns:
            Dictionary containing consent request details
            
        Raises:
            ConfigurationError: If plugin does not exist
            SecurityError: If requested permissions are invalid
        """
        manifest = self.get_plugin_manifest(plugin_id)
        if not manifest:
            raise ConfigurationError(f"Plugin '{plugin_id}' not found")
            
        # Determine permissions to request
        if requested_permissions is None:
            requested_permissions = manifest.requested_permissions
        else:
            # Validate requested permissions
            for permission_id in requested_permissions:
                if permission_id not in manifest.requested_permissions:
                    raise SecurityError(f"Permission '{permission_id}' not declared in plugin manifest")
        
        # Get permission details
        permission_details = []
        for permission_id in requested_permissions:
            permission = self.get_permission(permission_id)
            if permission:
                permission_details.append(permission.to_dict())
        
        # Check for existing consent
        existing_consent = self.get_user_plugin_consent(user_id, plugin_id)
        
        # Create consent request
        request_id = str(uuid.uuid4())
        request = {
            "request_id": request_id,
            "user_id": user_id,
            "plugin_id": plugin_id,
            "plugin_name": manifest.name,
            "plugin_author": manifest.author,
            "plugin_description": manifest.description,
            "requested_permissions": permission_details,
            "existing_consent": existing_consent.to_dict() if existing_consent else None,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat()
        }
        
        # Emit event
        self.event_manager.emit_event("plugin_security.consent_requested", {
            "request_id": request_id,
            "user_id": user_id,
            "plugin_id": plugin_id,
            "requested_permissions": requested_permissions,
            "timestamp": datetime.now().isoformat()
        })
        
        return request
    
    def process_consent_response(
        self,
        request_id: str,
        user_id: str,
        plugin_id: str,
        granted_permissions: List[str],
        denied_permissions: List[str],
        expires_in: Optional[timedelta] = None
    ) -> PluginConsent:
        """
        Process a user's response to a consent request.
        
        Args:
            request_id: Request ID from the consent request
            user_id: User ID responding to the request
            plugin_id: Plugin ID the consent is for
            granted_permissions: List of permission IDs granted by the user
            denied_permissions: List of permission IDs denied by the user
            expires_in: Optional expiration time delta
            
        Returns:
            PluginConsent instance
            
        Raises:
            SecurityError: If permissions are invalid
        """
        manifest = self.get_plugin_manifest(plugin_id)
        if not manifest:
            raise ConfigurationError(f"Plugin '{plugin_id}' not found")
            
        # Validate permissions
        for permission_id in granted_permissions + denied_permissions:
            if permission_id not in manifest.requested_permissions:
                raise SecurityError(f"Permission '{permission_id}' not declared in plugin manifest")
        
        # Calculate expiration time if provided
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.now() + expires_in
        
        # Create or update consent
        consent_id = str(uuid.uuid4())
        consent = PluginConsent(
            consent_id=consent_id,
            user_id=user_id,
            plugin_id=plugin_id,
            granted_permissions=granted_permissions,
            denied_permissions=denied_permissions,
            expires_at=expires_at,
            metadata={
                "request_id": request_id
            }
        )
        
        # Store consent
        self.consents[consent_id] = consent
        
        # Update user-plugin consent index
        if user_id not in self.user_plugin_consents:
            self.user_plugin_consents[user_id] = {}
        self.user_plugin_consents[user_id][plugin_id] = consent_id
        
        # Emit event
        self.event_manager.emit_event("plugin_security.consent_processed", {
            "consent_id": consent_id,
            "user_id": user_id,
            "plugin_id": plugin_id,
            "granted_permissions": granted_permissions,
            "denied_permissions": denied_permissions,
            "timestamp": datetime.now().isoformat()
        })
        
        return consent
    
    def get_user_plugin_consent(
        self,
        user_id: str,
        plugin_id: str
    ) -> Optional[PluginConsent]:
        """
        Get a user's consent for a plugin.
        
        Args:
            user_id: User ID to get consent for
            plugin_id: Plugin ID to get consent for
            
        Returns:
            PluginConsent instance or None if not found
        """
        if user_id not in self.user_plugin_consents:
            return None
            
        if plugin_id not in self.user_plugin_consents[user_id]:
            return None
            
        consent_id = self.user_plugin_consents[user_id][plugin_id]
        return self.consents.get(consent_id)
    
    def revoke_user_consent(
        self,
        user_id: str,
        plugin_id: str
    ) -> bool:
        """
        Revoke a user's consent for a plugin.
        
        Args:
            user_id: User ID to revoke consent for
            plugin_id: Plugin ID to revoke consent for
            
        Returns:
            True if consent was revoked, False otherwise
        """
        consent = self.get_user_plugin_consent(user_id, plugin_id)
        if not consent:
            return False
            
        # Deactivate consent
        consent.is_active = False
        
        # Emit event
        self.event_manager.emit_event("plugin_security.consent_revoked", {
            "consent_id": consent.consent_id,
            "user_id": user_id,
            "plugin_id": plugin_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def check_plugin_permission(
        self,
        user_id: str,
        plugin_id: str,
        permission_id: str
    ) -> bool:
        """
        Check if a plugin has permission to perform an action.
        
        Args:
            user_id: User ID the plugin is running as
            plugin_id: Plugin ID to check
            permission_id: Permission ID to check
            
        Returns:
            True if plugin has permission, False otherwise
        """
        # Check if permission exists
        if permission_id not in self.permissions:
            return False
            
        # Check if plugin exists
        manifest = self.get_plugin_manifest(plugin_id)
        if not manifest:
            return False
            
        # Check if permission is requested by plugin
        if permission_id not in manifest.requested_permissions:
            return False
            
        # Check user consent
        consent = self.get_user_plugin_consent(user_id, plugin_id)
        if not consent:
            return False
            
        # Check if consent is valid
        if not consent.is_active or consent.is_expired():
            return False
            
        # Check if permission is granted
        return consent.has_permission(permission_id)
    
    def enforce_plugin_permission(
        self,
        user_id: str,
        plugin_id: str,
        permission_id: str
    ) -> None:
        """
        Enforce a plugin permission check and raise an error if not allowed.
        
        Args:
            user_id: User ID the plugin is running as
            plugin_id: Plugin ID to check
            permission_id: Permission ID to check
            
        Raises:
            SecurityError: If plugin does not have permission
        """
        if not self.check_plugin_permission(user_id, plugin_id, permission_id):
            permission = self.get_permission(permission_id)
            permission_name = permission.name if permission else permission_id
            raise SecurityError(f"Plugin '{plugin_id}' does not have permission: {permission_name}")
    
    def generate_security_token(
        self,
        user_id: str,
        plugin_id: str,
        expires_in: timedelta = timedelta(hours=1)
    ) -> PluginSecurityToken:
        """
        Generate a security token for a plugin.
        
        Args:
            user_id: User ID the token is for
            plugin_id: Plugin ID the token is for
            expires_in: Expiration time delta
            
        Returns:
            PluginSecurityToken instance
            
        Raises:
            ConfigurationError: If plugin does not exist
        """
        manifest = self.get_plugin_manifest(plugin_id)
        if not manifest:
            raise ConfigurationError(f"Plugin '{plugin_id}' not found")
            
        # Generate token value
        token_value = secrets.token_urlsafe(32)
        
        # Calculate expiration time
        expires_at = datetime.now() + expires_in
        
        # Create token
        token_id = str(uuid.uuid4())
        token = PluginSecurityToken(
            token_id=token_id,
            plugin_id=plugin_id,
            user_id=user_id,
            token_value=token_value,
            expires_at=expires_at
        )
        
        # Store token
        self.tokens[token_id] = token
        self.token_values[token_value] = token_id
        
        # Emit event
        self.event_manager.emit_event("plugin_security.token_generated", {
            "token_id": token_id,
            "user_id": user_id,
            "plugin_id": plugin_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return token
    
    def validate_security_token(
        self,
        token_value: str
    ) -> Tuple[bool, Optional[PluginSecurityToken], Optional[str]]:
        """
        Validate a security token.
        
        Args:
            token_value: Token value to validate
            
        Returns:
            Tuple of (is_valid, token, error_message)
        """
        if token_value not in self.token_values:
            return False, None, "Invalid token"
            
        token_id = self.token_values[token_value]
        token = self.tokens.get(token_id)
        
        if not token:
            return False, None, "Token not found"
            
        if not token.is_active:
            return False, None, "Token is inactive"
            
        if token.is_expired():
            return False, None, "Token has expired"
            
        return True, token, None
    
    def revoke_security_token(
        self,
        token_value: str
    ) -> bool:
        """
        Revoke a security token.
        
        Args:
            token_value: Token value to revoke
            
        Returns:
            True if token was revoked, False otherwise
        """
        if token_value not in self.token_values:
            return False
            
        token_id = self.token_values[token_value]
        token = self.tokens.get(token_id)
        
        if not token:
            return False
            
        # Deactivate token
        token.is_active = False
        
        # Emit event
        self.event_manager.emit_event("plugin_security.token_revoked", {
            "token_id": token.token_id,
            "user_id": token.user_id,
            "plugin_id": token.plugin_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def create_security_context(
        self,
        user_id: str,
        plugin_id: str
    ) -> PluginSecurityContext:
        """
        Create a security context for a plugin.
        
        Args:
            user_id: User ID the context is for
            plugin_id: Plugin ID the context is for
            
        Returns:
            PluginSecurityContext instance
            
        Raises:
            ConfigurationError: If plugin does not exist
        """
        manifest = self.get_plugin_manifest(plugin_id)
        if not manifest:
            raise ConfigurationError(f"Plugin '{plugin_id}' not found")
            
        # Get user consent
        consent = self.get_user_plugin_consent(user_id, plugin_id)
        if not consent or not consent.is_active or consent.is_expired():
            raise SecurityError(f"User has not granted consent for plugin '{plugin_id}'")
            
        # Create security context
        context = PluginSecurityContext(
            plugin_id=plugin_id,
            user_id=user_id,
            permissions=consent.granted_permissions,
            check_permission=lambda permission_id: self.check_plugin_permission(user_id, plugin_id, permission_id),
            enforce_permission=lambda permission_id: self.enforce_plugin_permission(user_id, plugin_id, permission_id)
        )
        
        # Store context
        if plugin_id not in self.security_contexts:
            self.security_contexts[plugin_id] = {}
        self.security_contexts[plugin_id][user_id] = context
        
        # Emit event
        self.event_manager.emit_event("plugin_security.context_created", {
            "user_id": user_id,
            "plugin_id": plugin_id,
            "permissions": consent.granted_permissions,
            "timestamp": datetime.now().isoformat()
        })
        
        return context
    
    def get_security_context(
        self,
        user_id: str,
        plugin_id: str
    ) -> Optional[PluginSecurityContext]:
        """
        Get a security context for a plugin.
        
        Args:
            user_id: User ID the context is for
            plugin_id: Plugin ID the context is for
            
        Returns:
            PluginSecurityContext instance or None if not found
        """
        if plugin_id not in self.security_contexts:
            return None
            
        return self.security_contexts[plugin_id].get(user_id)
    
    def authorize_plugin_communication(
        self,
        source_plugin_id: str,
        target_plugin_id: str,
        user_id: str
    ) -> bool:
        """
        Authorize communication between plugins.
        
        Args:
            source_plugin_id: Source plugin ID
            target_plugin_id: Target plugin ID
            user_id: User ID the plugins are running as
            
        Returns:
            True if communication is authorized, False otherwise
        """
        # Check if source plugin has permission to communicate
        if not self.check_plugin_permission(user_id, source_plugin_id, "plugin.communicate"):
            return False
            
        # Check if target plugin exists
        target_manifest = self.get_plugin_manifest(target_plugin_id)
        if not target_manifest:
            return False
            
        # Check if user has granted consent for target plugin
        target_consent = self.get_user_plugin_consent(user_id, target_plugin_id)
        if not target_consent or not target_consent.is_active or target_consent.is_expired():
            return False
            
        # Communication is authorized
        return True
    
    def authorize_plugin_data_access(
        self,
        source_plugin_id: str,
        target_plugin_id: str,
        user_id: str,
        data_type: str
    ) -> bool:
        """
        Authorize data access between plugins.
        
        Args:
            source_plugin_id: Source plugin ID
            target_plugin_id: Target plugin ID
            user_id: User ID the plugins are running as
            data_type: Type of data being accessed
            
        Returns:
            True if data access is authorized, False otherwise
        """
        # Check if source plugin has permission to access plugin data
        if not self.check_plugin_permission(user_id, source_plugin_id, "plugin.data_access"):
            return False
            
        # Check if communication is authorized
        if not self.authorize_plugin_communication(source_plugin_id, target_plugin_id, user_id):
            return False
            
        # In a real implementation, you would check data type permissions
        # For this example, we'll authorize all data access if communication is authorized
        
        # Data access is authorized
        return True
