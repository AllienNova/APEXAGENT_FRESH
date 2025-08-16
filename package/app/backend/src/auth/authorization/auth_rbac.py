"""
Authorization module for ApexAgent.

This module provides the core authorization functionality for the ApexAgent platform,
including role-based access control, permission management, and access enforcement.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple

from src.core.error_handling.errors import AuthorizationError
from src.core.event_system.event_manager import EventManager

logger = logging.getLogger(__name__)

class Permission:
    """
    Represents a permission in the system.
    """
    def __init__(
        self,
        name: str,
        description: str,
        permission_id: str = None,
        resource_type: str = None,
        actions: List[str] = None,
        is_system: bool = False,
        metadata: Dict[str, Any] = None
    ):
        self.permission_id = permission_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.resource_type = resource_type
        self.actions = actions or []
        self.is_system = is_system
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
            "resource_type": self.resource_type,
            "actions": self.actions,
            "is_system": self.is_system,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, permission_dict: Dict[str, Any]) -> 'Permission':
        """
        Create a permission object from dictionary representation.
        
        Args:
            permission_dict: Dictionary representation of the permission
            
        Returns:
            Permission object
        """
        return cls(
            name=permission_dict["name"],
            description=permission_dict["description"],
            permission_id=permission_dict.get("permission_id"),
            resource_type=permission_dict.get("resource_type"),
            actions=permission_dict.get("actions", []),
            is_system=permission_dict.get("is_system", False),
            metadata=permission_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"Permission(id={self.permission_id}, name={self.name})"


class Role:
    """
    Represents a role in the system with associated permissions.
    """
    def __init__(
        self,
        name: str,
        description: str,
        role_id: str = None,
        permissions: List[str] = None,
        parent_roles: List[str] = None,
        is_system: bool = False,
        created_at: datetime = None,
        metadata: Dict[str, Any] = None
    ):
        self.role_id = role_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.permissions = permissions or []  # List of permission_ids
        self.parent_roles = parent_roles or []  # List of parent role_ids
        self.is_system = is_system
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert role object to dictionary representation.
        
        Returns:
            Dictionary representation of the role
        """
        return {
            "role_id": self.role_id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "parent_roles": self.parent_roles,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, role_dict: Dict[str, Any]) -> 'Role':
        """
        Create a role object from dictionary representation.
        
        Args:
            role_dict: Dictionary representation of the role
            
        Returns:
            Role object
        """
        created_at = role_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        return cls(
            name=role_dict["name"],
            description=role_dict["description"],
            role_id=role_dict.get("role_id"),
            permissions=role_dict.get("permissions", []),
            parent_roles=role_dict.get("parent_roles", []),
            is_system=role_dict.get("is_system", False),
            created_at=created_at,
            metadata=role_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"Role(id={self.role_id}, name={self.name})"


class UserRoleAssignment:
    """
    Represents a user-role assignment.
    """
    def __init__(
        self,
        user_id: str,
        role_id: str,
        assignment_id: str = None,
        assigned_by: str = None,
        assigned_at: datetime = None,
        expires_at: datetime = None,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.assignment_id = assignment_id or str(uuid.uuid4())
        self.user_id = user_id
        self.role_id = role_id
        self.assigned_by = assigned_by
        self.assigned_at = assigned_at or datetime.now()
        self.expires_at = expires_at
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert assignment object to dictionary representation.
        
        Returns:
            Dictionary representation of the assignment
        """
        return {
            "assignment_id": self.assignment_id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "assigned_by": self.assigned_by,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, assignment_dict: Dict[str, Any]) -> 'UserRoleAssignment':
        """
        Create an assignment object from dictionary representation.
        
        Args:
            assignment_dict: Dictionary representation of the assignment
            
        Returns:
            UserRoleAssignment object
        """
        assigned_at = assignment_dict.get("assigned_at")
        if assigned_at and isinstance(assigned_at, str):
            assigned_at = datetime.fromisoformat(assigned_at)
            
        expires_at = assignment_dict.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        return cls(
            user_id=assignment_dict["user_id"],
            role_id=assignment_dict["role_id"],
            assignment_id=assignment_dict.get("assignment_id"),
            assigned_by=assignment_dict.get("assigned_by"),
            assigned_at=assigned_at,
            expires_at=expires_at,
            is_active=assignment_dict.get("is_active", True),
            metadata=assignment_dict.get("metadata", {})
        )
    
    def is_expired(self) -> bool:
        """
        Check if the assignment is expired.
        
        Returns:
            True if assignment is expired, False otherwise
        """
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def __str__(self) -> str:
        return f"UserRoleAssignment(user={self.user_id}, role={self.role_id})"


class AuthorizationManager:
    """
    Manages role-based access control, including roles, permissions, and access enforcement.
    """
    def __init__(self, event_manager: EventManager = None):
        self.permissions: Dict[str, Permission] = {}  # permission_id -> Permission
        self.roles: Dict[str, Role] = {}  # role_id -> Role
        self.user_role_assignments: Dict[str, UserRoleAssignment] = {}  # assignment_id -> UserRoleAssignment
        
        # Indexes for efficient lookups
        self.permission_name_index: Dict[str, str] = {}  # permission_name -> permission_id
        self.role_name_index: Dict[str, str] = {}  # role_name -> role_id
        self.user_roles_index: Dict[str, List[str]] = {}  # user_id -> [assignment_id]
        
        self.event_manager = event_manager or EventManager()
        
        # Initialize system roles and permissions
        self._initialize_system_roles_and_permissions()
        
    def _initialize_system_roles_and_permissions(self) -> None:
        """
        Initialize system roles and permissions.
        """
        # Create system permissions
        system_permissions = [
            Permission(
                name="system.admin",
                description="Full system administration access",
                is_system=True
            ),
            Permission(
                name="user.read",
                description="Read user information",
                resource_type="user",
                actions=["read"],
                is_system=True
            ),
            Permission(
                name="user.create",
                description="Create new users",
                resource_type="user",
                actions=["create"],
                is_system=True
            ),
            Permission(
                name="user.update",
                description="Update user information",
                resource_type="user",
                actions=["update"],
                is_system=True
            ),
            Permission(
                name="user.delete",
                description="Delete users",
                resource_type="user",
                actions=["delete"],
                is_system=True
            ),
            Permission(
                name="role.read",
                description="Read role information",
                resource_type="role",
                actions=["read"],
                is_system=True
            ),
            Permission(
                name="role.create",
                description="Create new roles",
                resource_type="role",
                actions=["create"],
                is_system=True
            ),
            Permission(
                name="role.update",
                description="Update role information",
                resource_type="role",
                actions=["update"],
                is_system=True
            ),
            Permission(
                name="role.delete",
                description="Delete roles",
                resource_type="role",
                actions=["delete"],
                is_system=True
            ),
            Permission(
                name="role.assign",
                description="Assign roles to users",
                resource_type="role",
                actions=["assign"],
                is_system=True
            )
        ]
        
        # Register system permissions
        for permission in system_permissions:
            self.register_permission(permission)
        
        # Create system roles
        admin_role = Role(
            name="Administrator",
            description="System administrator with full access",
            permissions=[self.get_permission_by_name("system.admin").permission_id],
            is_system=True
        )
        
        user_manager_role = Role(
            name="User Manager",
            description="Can manage users and their roles",
            permissions=[
                self.get_permission_by_name("user.read").permission_id,
                self.get_permission_by_name("user.create").permission_id,
                self.get_permission_by_name("user.update").permission_id,
                self.get_permission_by_name("user.delete").permission_id,
                self.get_permission_by_name("role.read").permission_id,
                self.get_permission_by_name("role.assign").permission_id
            ],
            is_system=True
        )
        
        user_role = Role(
            name="User",
            description="Standard user with basic access",
            permissions=[],
            is_system=True
        )
        
        # Register system roles
        self.register_role(admin_role)
        self.register_role(user_manager_role)
        self.register_role(user_role)
    
    def register_permission(self, permission: Permission) -> Permission:
        """
        Register a new permission.
        
        Args:
            permission: Permission object to register
            
        Returns:
            Registered Permission object
            
        Raises:
            AuthorizationError: If permission name already exists
        """
        # Check if permission name already exists
        if permission.name in self.permission_name_index:
            raise AuthorizationError(f"Permission '{permission.name}' already exists")
        
        # Store the permission
        self.permissions[permission.permission_id] = permission
        self.permission_name_index[permission.name] = permission.permission_id
        
        # Emit permission registered event
        self.event_manager.emit_event("permission.registered", {
            "permission_id": permission.permission_id,
            "name": permission.name,
            "timestamp": datetime.now().isoformat()
        })
        
        return permission
    
    def register_role(self, role: Role) -> Role:
        """
        Register a new role.
        
        Args:
            role: Role object to register
            
        Returns:
            Registered Role object
            
        Raises:
            AuthorizationError: If role name already exists
        """
        # Check if role name already exists
        if role.name in self.role_name_index:
            raise AuthorizationError(f"Role '{role.name}' already exists")
        
        # Validate permissions
        for permission_id in role.permissions:
            if permission_id not in self.permissions:
                raise AuthorizationError(f"Permission with ID '{permission_id}' does not exist")
        
        # Validate parent roles
        for parent_role_id in role.parent_roles:
            if parent_role_id not in self.roles:
                raise AuthorizationError(f"Parent role with ID '{parent_role_id}' does not exist")
        
        # Store the role
        self.roles[role.role_id] = role
        self.role_name_index[role.name] = role.role_id
        
        # Emit role registered event
        self.event_manager.emit_event("role.registered", {
            "role_id": role.role_id,
            "name": role.name,
            "timestamp": datetime.now().isoformat()
        })
        
        return role
    
    def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str = None,
        expires_at: datetime = None,
        metadata: Dict[str, Any] = None
    ) -> UserRoleAssignment:
        """
        Assign a role to a user.
        
        Args:
            user_id: User ID to assign role to
            role_id: Role ID to assign
            assigned_by: User ID of the assigner
            expires_at: Expiration date for the assignment
            metadata: Additional assignment metadata
            
        Returns:
            UserRoleAssignment object
            
        Raises:
            AuthorizationError: If role does not exist
        """
        # Check if role exists
        if role_id not in self.roles:
            raise AuthorizationError(f"Role with ID '{role_id}' does not exist")
        
        # Create the assignment
        assignment = UserRoleAssignment(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
            expires_at=expires_at,
            metadata=metadata
        )
        
        # Store the assignment
        self.user_role_assignments[assignment.assignment_id] = assignment
        
        # Add to user roles index
        if user_id not in self.user_roles_index:
            self.user_roles_index[user_id] = []
        self.user_roles_index[user_id].append(assignment.assignment_id)
        
        # Emit role assigned event
        self.event_manager.emit_event("role.assigned", {
            "assignment_id": assignment.assignment_id,
            "user_id": user_id,
            "role_id": role_id,
            "assigned_by": assigned_by,
            "timestamp": datetime.now().isoformat()
        })
        
        return assignment
    
    def revoke_role_from_user(
        self,
        user_id: str,
        role_id: str
    ) -> bool:
        """
        Revoke a role from a user.
        
        Args:
            user_id: User ID to revoke role from
            role_id: Role ID to revoke
            
        Returns:
            True if role was revoked, False if user doesn't have the role
        """
        # Check if user has any roles
        if user_id not in self.user_roles_index:
            return False
        
        # Find matching assignments
        revoked = False
        for assignment_id in list(self.user_roles_index[user_id]):
            assignment = self.user_role_assignments.get(assignment_id)
            if assignment and assignment.role_id == role_id and assignment.is_active:
                # Deactivate the assignment
                assignment.is_active = False
                revoked = True
                
                # Emit role revoked event
                self.event_manager.emit_event("role.revoked", {
                    "assignment_id": assignment_id,
                    "user_id": user_id,
                    "role_id": role_id,
                    "timestamp": datetime.now().isoformat()
                })
        
        return revoked
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """
        Get all roles assigned to a user.
        
        Args:
            user_id: User ID to get roles for
            
        Returns:
            List of Role objects
        """
        if user_id not in self.user_roles_index:
            return []
        
        roles = []
        for assignment_id in self.user_roles_index[user_id]:
            assignment = self.user_role_assignments.get(assignment_id)
            if assignment and assignment.is_active and not assignment.is_expired():
                role = self.roles.get(assignment.role_id)
                if role:
                    roles.append(role)
        
        return roles
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """
        Get all permissions granted to a user through their roles.
        
        Args:
            user_id: User ID to get permissions for
            
        Returns:
            List of Permission objects
        """
        # Get all roles assigned to the user
        roles = self.get_user_roles(user_id)
        
        # Get all permissions from roles and their parent roles
        permission_ids = set()
        processed_roles = set()
        
        def collect_role_permissions(role_id: str) -> None:
            """Recursively collect permissions from a role and its parent roles."""
            if role_id in processed_roles:
                return
            
            processed_roles.add(role_id)
            role = self.roles.get(role_id)
            if not role:
                return
            
            # Add direct permissions
            for permission_id in role.permissions:
                permission_ids.add(permission_id)
            
            # Add parent role permissions
            for parent_role_id in role.parent_roles:
                collect_role_permissions(parent_role_id)
        
        # Collect permissions from all roles
        for role in roles:
            collect_role_permissions(role.role_id)
        
        # Convert permission IDs to Permission objects
        return [self.permissions[pid] for pid in permission_ids if pid in self.permissions]
    
    def has_permission(self, user_id: str, permission_name: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: User ID to check
            permission_name: Permission name to check
            
        Returns:
            True if user has the permission, False otherwise
        """
        # Get the permission ID from name
        permission_id = self.permission_name_index.get(permission_name)
        if not permission_id:
            return False
        
        # Get all user permissions
        user_permissions = self.get_user_permissions(user_id)
        
        # Check if the permission is in the user's permissions
        return any(p.permission_id == permission_id for p in user_permissions)
    
    def has_role(self, user_id: str, role_name: str) -> bool:
        """
        Check if a user has a specific role.
        
        Args:
            user_id: User ID to check
            role_name: Role name to check
            
        Returns:
            True if user has the role, False otherwise
        """
        # Get the role ID from name
        role_id = self.role_name_index.get(role_name)
        if not role_id:
            return False
        
        # Get all user roles
        user_roles = self.get_user_roles(user_id)
        
        # Check if the role is in the user's roles
        return any(r.role_id == role_id for r in user_roles)
    
    def check_permission(self, user_id: str, permission_name: str) -> None:
        """
        Check if a user has a specific permission and raise an error if not.
        
        Args:
            user_id: User ID to check
            permission_name: Permission name to check
            
        Raises:
            AuthorizationError: If user does not have the permission
        """
        if not self.has_permission(user_id, permission_name):
            raise AuthorizationError(f"User does not have permission: {permission_name}")
    
    def update_permission(
        self,
        permission_id: str,
        name: str = None,
        description: str = None,
        resource_type: str = None,
        actions: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[Permission], Optional[str]]:
        """
        Update a permission.
        
        Args:
            permission_id: Permission ID to update
            name: New permission name
            description: New description
            resource_type: New resource type
            actions: New actions
            metadata: New or updated metadata
            
        Returns:
            Tuple of (success, permission, error_message)
        """
        # Check if permission exists
        if permission_id not in self.permissions:
            return False, None, "Permission not found"
        
        permission = self.permissions[permission_id]
        
        # Check if permission is a system permission
        if permission.is_system:
            return False, permission, "Cannot modify system permissions"
        
        # Update name if provided and different
        if name and name != permission.name:
            # Check if name already exists
            if name in self.permission_name_index:
                return False, permission, f"Permission name '{name}' already exists"
            
            # Update name index
            del self.permission_name_index[permission.name]
            self.permission_name_index[name] = permission_id
            permission.name = name
        
        # Update other fields if provided
        if description is not None:
            permission.description = description
        
        if resource_type is not None:
            permission.resource_type = resource_type
        
        if actions is not None:
            permission.actions = actions
        
        if metadata is not None:
            # Update metadata (merge with existing)
            permission.metadata.update(metadata)
        
        # Emit permission updated event
        self.event_manager.emit_event("permission.updated", {
            "permission_id": permission_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, permission, None
    
    def update_role(
        self,
        role_id: str,
        name: str = None,
        description: str = None,
        permissions: List[str] = None,
        parent_roles: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[Role], Optional[str]]:
        """
        Update a role.
        
        Args:
            role_id: Role ID to update
            name: New role name
            description: New description
            permissions: New permissions
            parent_roles: New parent roles
            metadata: New or updated metadata
            
        Returns:
            Tuple of (success, role, error_message)
        """
        # Check if role exists
        if role_id not in self.roles:
            return False, None, "Role not found"
        
        role = self.roles[role_id]
        
        # Check if role is a system role
        if role.is_system:
            return False, role, "Cannot modify system roles"
        
        # Update name if provided and different
        if name and name != role.name:
            # Check if name already exists
            if name in self.role_name_index:
                return False, role, f"Role name '{name}' already exists"
            
            # Update name index
            del self.role_name_index[role.name]
            self.role_name_index[name] = role_id
            role.name = name
        
        # Update description if provided
        if description is not None:
            role.description = description
        
        # Update permissions if provided
        if permissions is not None:
            # Validate permissions
            for permission_id in permissions:
                if permission_id not in self.permissions:
                    return False, role, f"Permission with ID '{permission_id}' does not exist"
            
            role.permissions = permissions
        
        # Update parent roles if provided
        if parent_roles is not None:
            # Validate parent roles
            for parent_role_id in parent_roles:
                if parent_role_id not in self.roles:
                    return False, role, f"Parent role with ID '{parent_role_id}' does not exist"
                
                # Check for circular references
                if parent_role_id == role_id:
                    return False, role, "Role cannot be its own parent"
                
                # Check for indirect circular references
                if self._has_circular_reference(role_id, parent_role_id):
                    return False, role, "Circular reference detected in role hierarchy"
            
            role.parent_roles = parent_roles
        
        # Update metadata if provided
        if metadata is not None:
            # Update metadata (merge with existing)
            role.metadata.update(metadata)
        
        # Emit role updated event
        self.event_manager.emit_event("role.updated", {
            "role_id": role_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, role, None
    
    def delete_permission(self, permission_id: str) -> bool:
        """
        Delete a permission.
        
        Args:
            permission_id: Permission ID to delete
            
        Returns:
            True if permission was deleted, False if permission doesn't exist or is a system permission
        """
        # Check if permission exists
        if permission_id not in self.permissions:
            return False
        
        permission = self.permissions[permission_id]
        
        # Check if permission is a system permission
        if permission.is_system:
            return False
        
        # Check if permission is used by any roles
        for role in self.roles.values():
            if permission_id in role.permissions:
                return False
        
        # Remove from indexes
        del self.permission_name_index[permission.name]
        
        # Remove permission
        del self.permissions[permission_id]
        
        # Emit permission deleted event
        self.event_manager.emit_event("permission.deleted", {
            "permission_id": permission_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def delete_role(self, role_id: str) -> bool:
        """
        Delete a role.
        
        Args:
            role_id: Role ID to delete
            
        Returns:
            True if role was deleted, False if role doesn't exist, is a system role, or is used as a parent role
        """
        # Check if role exists
        if role_id not in self.roles:
            return False
        
        role = self.roles[role_id]
        
        # Check if role is a system role
        if role.is_system:
            return False
        
        # Check if role is used as a parent role
        for other_role in self.roles.values():
            if role_id in other_role.parent_roles:
                return False
        
        # Revoke this role from all users
        for user_id in list(self.user_roles_index.keys()):
            self.revoke_role_from_user(user_id, role_id)
        
        # Remove from indexes
        del self.role_name_index[role.name]
        
        # Remove role
        del self.roles[role_id]
        
        # Emit role deleted event
        self.event_manager.emit_event("role.deleted", {
            "role_id": role_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """
        Get a permission by ID.
        
        Args:
            permission_id: Permission ID to get
            
        Returns:
            Permission object or None if not found
        """
        return self.permissions.get(permission_id)
    
    def get_permission_by_name(self, permission_name: str) -> Optional[Permission]:
        """
        Get a permission by name.
        
        Args:
            permission_name: Permission name to get
            
        Returns:
            Permission object or None if not found
        """
        permission_id = self.permission_name_index.get(permission_name)
        if permission_id:
            return self.permissions.get(permission_id)
        return None
    
    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """
        Get a role by ID.
        
        Args:
            role_id: Role ID to get
            
        Returns:
            Role object or None if not found
        """
        return self.roles.get(role_id)
    
    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            role_name: Role name to get
            
        Returns:
            Role object or None if not found
        """
        role_id = self.role_name_index.get(role_name)
        if role_id:
            return self.roles.get(role_id)
        return None
    
    def get_all_permissions(self) -> List[Permission]:
        """
        Get all permissions.
        
        Returns:
            List of all Permission objects
        """
        return list(self.permissions.values())
    
    def get_all_roles(self) -> List[Role]:
        """
        Get all roles.
        
        Returns:
            List of all Role objects
        """
        return list(self.roles.values())
    
    def get_user_role_assignments(self, user_id: str) -> List[UserRoleAssignment]:
        """
        Get all role assignments for a user.
        
        Args:
            user_id: User ID to get assignments for
            
        Returns:
            List of UserRoleAssignment objects
        """
        if user_id not in self.user_roles_index:
            return []
        
        assignments = []
        for assignment_id in self.user_roles_index[user_id]:
            assignment = self.user_role_assignments.get(assignment_id)
            if assignment:
                assignments.append(assignment)
        
        return assignments
    
    def _has_circular_reference(self, role_id: str, parent_role_id: str) -> bool:
        """
        Check if adding a parent role would create a circular reference.
        
        Args:
            role_id: Role ID to check
            parent_role_id: Parent role ID to check
            
        Returns:
            True if circular reference would be created, False otherwise
        """
        # Check if parent role has the role as a parent (direct or indirect)
        visited = set()
        
        def check_parents(current_role_id: str) -> bool:
            """Recursively check parent roles for circular references."""
            if current_role_id in visited:
                return False
            
            visited.add(current_role_id)
            
            if current_role_id == role_id:
                return True
            
            current_role = self.roles.get(current_role_id)
            if not current_role:
                return False
            
            for parent_id in current_role.parent_roles:
                if check_parents(parent_id):
                    return True
            
            return False
        
        return check_parents(parent_role_id)
