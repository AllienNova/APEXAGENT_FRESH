"""
Enhanced Role-Based Access Control module for ApexAgent.

This module provides advanced RBAC functionality for the ApexAgent platform,
including dynamic permission evaluation, delegation, and attribute-based access control.
"""

import os
import json
import uuid
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable

from src.core.error_handling.errors import AuthorizationError, ConfigurationError
from src.core.event_system.event_manager import EventManager
from src.auth.authorization.auth_rbac import Permission, Role, UserRoleAssignment, AuthorizationManager

logger = logging.getLogger(__name__)

class ResourceOwnership:
    """
    Represents ownership of a resource by a user.
    """
    def __init__(
        self,
        resource_id: str,
        resource_type: str,
        owner_id: str,
        created_at: datetime = None,
        metadata: Dict[str, Any] = None
    ):
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.owner_id = owner_id
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ownership object to dictionary representation.
        
        Returns:
            Dictionary representation of the ownership
        """
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, ownership_dict: Dict[str, Any]) -> 'ResourceOwnership':
        """
        Create an ownership object from dictionary representation.
        
        Args:
            ownership_dict: Dictionary representation of the ownership
            
        Returns:
            ResourceOwnership object
        """
        created_at = ownership_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        return cls(
            resource_id=ownership_dict["resource_id"],
            resource_type=ownership_dict["resource_type"],
            owner_id=ownership_dict["owner_id"],
            created_at=created_at,
            metadata=ownership_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"ResourceOwnership(resource={self.resource_id}, type={self.resource_type}, owner={self.owner_id})"


class PermissionDelegation:
    """
    Represents a delegation of permissions from one user to another.
    """
    def __init__(
        self,
        delegation_id: str,
        delegator_id: str,
        delegatee_id: str,
        permissions: List[str],
        resource_type: str = None,
        resource_id: str = None,
        created_at: datetime = None,
        expires_at: datetime = None,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.delegation_id = delegation_id or str(uuid.uuid4())
        self.delegator_id = delegator_id
        self.delegatee_id = delegatee_id
        self.permissions = permissions
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert delegation object to dictionary representation.
        
        Returns:
            Dictionary representation of the delegation
        """
        return {
            "delegation_id": self.delegation_id,
            "delegator_id": self.delegator_id,
            "delegatee_id": self.delegatee_id,
            "permissions": self.permissions,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, delegation_dict: Dict[str, Any]) -> 'PermissionDelegation':
        """
        Create a delegation object from dictionary representation.
        
        Args:
            delegation_dict: Dictionary representation of the delegation
            
        Returns:
            PermissionDelegation object
        """
        created_at = delegation_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        expires_at = delegation_dict.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        return cls(
            delegation_id=delegation_dict.get("delegation_id"),
            delegator_id=delegation_dict["delegator_id"],
            delegatee_id=delegation_dict["delegatee_id"],
            permissions=delegation_dict["permissions"],
            resource_type=delegation_dict.get("resource_type"),
            resource_id=delegation_dict.get("resource_id"),
            created_at=created_at,
            expires_at=expires_at,
            is_active=delegation_dict.get("is_active", True),
            metadata=delegation_dict.get("metadata", {})
        )
    
    def is_expired(self) -> bool:
        """
        Check if the delegation is expired.
        
        Returns:
            True if delegation is expired, False otherwise
        """
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def __str__(self) -> str:
        return f"PermissionDelegation(id={self.delegation_id}, from={self.delegator_id}, to={self.delegatee_id})"


class RoleAssignmentApproval:
    """
    Represents an approval for a role assignment.
    """
    def __init__(
        self,
        approval_id: str,
        assignment_id: str,
        approver_id: str,
        status: str,
        comments: str = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        metadata: Dict[str, Any] = None
    ):
        self.approval_id = approval_id or str(uuid.uuid4())
        self.assignment_id = assignment_id
        self.approver_id = approver_id
        self.status = status  # "pending", "approved", "rejected"
        self.comments = comments
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert approval object to dictionary representation.
        
        Returns:
            Dictionary representation of the approval
        """
        return {
            "approval_id": self.approval_id,
            "assignment_id": self.assignment_id,
            "approver_id": self.approver_id,
            "status": self.status,
            "comments": self.comments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, approval_dict: Dict[str, Any]) -> 'RoleAssignmentApproval':
        """
        Create an approval object from dictionary representation.
        
        Args:
            approval_dict: Dictionary representation of the approval
            
        Returns:
            RoleAssignmentApproval object
        """
        created_at = approval_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        updated_at = approval_dict.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
            
        return cls(
            approval_id=approval_dict.get("approval_id"),
            assignment_id=approval_dict["assignment_id"],
            approver_id=approval_dict["approver_id"],
            status=approval_dict["status"],
            comments=approval_dict.get("comments"),
            created_at=created_at,
            updated_at=updated_at,
            metadata=approval_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"RoleAssignmentApproval(id={self.approval_id}, assignment={self.assignment_id}, status={self.status})"


class DynamicPermissionRule:
    """
    Represents a rule for dynamic permission evaluation.
    """
    def __init__(
        self,
        rule_id: str,
        permission_id: str,
        resource_type: str,
        condition: Callable[[Dict[str, Any]], bool],
        description: str = None,
        priority: int = 0,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.rule_id = rule_id or str(uuid.uuid4())
        self.permission_id = permission_id
        self.resource_type = resource_type
        self.condition = condition
        self.description = description
        self.priority = priority
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate the rule with the given context.
        
        Args:
            context: Context for evaluation
            
        Returns:
            True if rule condition is satisfied, False otherwise
        """
        try:
            return self.condition(context)
        except Exception as e:
            logger.error(f"Error evaluating rule {self.rule_id}: {e}")
            return False
    
    def __str__(self) -> str:
        return f"DynamicPermissionRule(id={self.rule_id}, permission={self.permission_id}, type={self.resource_type})"


class EnhancedRBACManager:
    """
    Enhanced RBAC manager with advanced features.
    """
    def __init__(
        self,
        base_rbac_manager: AuthorizationManager = None,
        event_manager: EventManager = None
    ):
        self.base_rbac_manager = base_rbac_manager or AuthorizationManager()
        self.event_manager = event_manager or EventManager()
        
        # Resource ownership
        self.resource_ownerships: Dict[str, Dict[str, ResourceOwnership]] = {}  # resource_type -> resource_id -> ResourceOwnership
        
        # Permission delegations
        self.delegations: Dict[str, PermissionDelegation] = {}  # delegation_id -> PermissionDelegation
        self.delegator_index: Dict[str, List[str]] = {}  # delegator_id -> [delegation_id]
        self.delegatee_index: Dict[str, List[str]] = {}  # delegatee_id -> [delegation_id]
        
        # Role assignment approvals
        self.approvals: Dict[str, RoleAssignmentApproval] = {}  # approval_id -> RoleAssignmentApproval
        self.assignment_approvals: Dict[str, List[str]] = {}  # assignment_id -> [approval_id]
        
        # Dynamic permission rules
        self.dynamic_rules: Dict[str, DynamicPermissionRule] = {}  # rule_id -> DynamicPermissionRule
        self.permission_rules: Dict[str, List[str]] = {}  # permission_id -> [rule_id]
        self.resource_type_rules: Dict[str, List[str]] = {}  # resource_type -> [rule_id]
        
    def register_resource_ownership(
        self,
        resource_id: str,
        resource_type: str,
        owner_id: str,
        metadata: Dict[str, Any] = None
    ) -> ResourceOwnership:
        """
        Register ownership of a resource.
        
        Args:
            resource_id: Resource ID
            resource_type: Resource type
            owner_id: Owner user ID
            metadata: Additional metadata
            
        Returns:
            ResourceOwnership object
        """
        ownership = ResourceOwnership(
            resource_id=resource_id,
            resource_type=resource_type,
            owner_id=owner_id,
            metadata=metadata
        )
        
        # Initialize resource type dict if needed
        if resource_type not in self.resource_ownerships:
            self.resource_ownerships[resource_type] = {}
            
        # Store ownership
        self.resource_ownerships[resource_type][resource_id] = ownership
        
        # Emit event
        self.event_manager.emit_event("rbac.ownership_registered", {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "owner_id": owner_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return ownership
    
    def get_resource_owner(
        self,
        resource_id: str,
        resource_type: str
    ) -> Optional[str]:
        """
        Get the owner of a resource.
        
        Args:
            resource_id: Resource ID
            resource_type: Resource type
            
        Returns:
            Owner user ID or None if not found
        """
        if (resource_type in self.resource_ownerships and 
            resource_id in self.resource_ownerships[resource_type]):
            return self.resource_ownerships[resource_type][resource_id].owner_id
        return None
    
    def is_resource_owner(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str
    ) -> bool:
        """
        Check if a user is the owner of a resource.
        
        Args:
            user_id: User ID to check
            resource_id: Resource ID
            resource_type: Resource type
            
        Returns:
            True if user is the owner, False otherwise
        """
        owner_id = self.get_resource_owner(resource_id, resource_type)
        return owner_id == user_id
    
    def transfer_ownership(
        self,
        resource_id: str,
        resource_type: str,
        new_owner_id: str,
        current_owner_id: str = None
    ) -> bool:
        """
        Transfer ownership of a resource.
        
        Args:
            resource_id: Resource ID
            resource_type: Resource type
            new_owner_id: New owner user ID
            current_owner_id: Current owner user ID (for verification)
            
        Returns:
            True if ownership was transferred, False otherwise
        """
        if resource_type not in self.resource_ownerships:
            return False
            
        if resource_id not in self.resource_ownerships[resource_type]:
            return False
            
        ownership = self.resource_ownerships[resource_type][resource_id]
        
        # Verify current owner if provided
        if current_owner_id and ownership.owner_id != current_owner_id:
            return False
            
        # Update owner
        old_owner_id = ownership.owner_id
        ownership.owner_id = new_owner_id
        
        # Emit event
        self.event_manager.emit_event("rbac.ownership_transferred", {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "old_owner_id": old_owner_id,
            "new_owner_id": new_owner_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def delegate_permission(
        self,
        delegator_id: str,
        delegatee_id: str,
        permissions: List[str],
        resource_type: str = None,
        resource_id: str = None,
        expires_in: Optional[timedelta] = None,
        metadata: Dict[str, Any] = None
    ) -> PermissionDelegation:
        """
        Delegate permissions from one user to another.
        
        Args:
            delegator_id: User ID delegating permissions
            delegatee_id: User ID receiving permissions
            permissions: List of permission IDs to delegate
            resource_type: Optional resource type to restrict delegation
            resource_id: Optional resource ID to restrict delegation
            expires_in: Optional expiration time delta
            metadata: Additional metadata
            
        Returns:
            PermissionDelegation object
            
        Raises:
            AuthorizationError: If delegator does not have the permissions
        """
        # Verify delegator has the permissions
        for permission_id in permissions:
            if not self.base_rbac_manager.has_permission(delegator_id, permission_id):
                raise AuthorizationError(f"Delegator does not have permission: {permission_id}")
        
        # Calculate expiration time if provided
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.now() + expires_in
        
        # Create delegation
        delegation = PermissionDelegation(
            delegation_id=str(uuid.uuid4()),
            delegator_id=delegator_id,
            delegatee_id=delegatee_id,
            permissions=permissions,
            resource_type=resource_type,
            resource_id=resource_id,
            expires_at=expires_at,
            metadata=metadata
        )
        
        # Store delegation
        self.delegations[delegation.delegation_id] = delegation
        
        # Update indexes
        if delegator_id not in self.delegator_index:
            self.delegator_index[delegator_id] = []
        self.delegator_index[delegator_id].append(delegation.delegation_id)
        
        if delegatee_id not in self.delegatee_index:
            self.delegatee_index[delegatee_id] = []
        self.delegatee_index[delegatee_id].append(delegation.delegation_id)
        
        # Emit event
        self.event_manager.emit_event("rbac.permission_delegated", {
            "delegation_id": delegation.delegation_id,
            "delegator_id": delegator_id,
            "delegatee_id": delegatee_id,
            "permissions": permissions,
            "timestamp": datetime.now().isoformat()
        })
        
        return delegation
    
    def revoke_delegation(
        self,
        delegation_id: str,
        revoker_id: str = None
    ) -> bool:
        """
        Revoke a permission delegation.
        
        Args:
            delegation_id: Delegation ID to revoke
            revoker_id: Optional user ID performing the revocation (for verification)
            
        Returns:
            True if delegation was revoked, False otherwise
        """
        if delegation_id not in self.delegations:
            return False
            
        delegation = self.delegations[delegation_id]
        
        # Verify revoker if provided
        if revoker_id and revoker_id != delegation.delegator_id:
            return False
            
        # Deactivate delegation
        delegation.is_active = False
        
        # Emit event
        self.event_manager.emit_event("rbac.delegation_revoked", {
            "delegation_id": delegation_id,
            "delegator_id": delegation.delegator_id,
            "delegatee_id": delegation.delegatee_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def get_delegated_permissions(
        self,
        user_id: str,
        resource_type: str = None,
        resource_id: str = None
    ) -> List[str]:
        """
        Get permissions delegated to a user.
        
        Args:
            user_id: User ID to get delegated permissions for
            resource_type: Optional resource type to filter by
            resource_id: Optional resource ID to filter by
            
        Returns:
            List of delegated permission IDs
        """
        if user_id not in self.delegatee_index:
            return []
            
        delegated_permissions = set()
        
        for delegation_id in self.delegatee_index[user_id]:
            if delegation_id not in self.delegations:
                continue
                
            delegation = self.delegations[delegation_id]
            
            # Skip inactive or expired delegations
            if not delegation.is_active or delegation.is_expired():
                continue
                
            # Filter by resource type if provided
            if resource_type and delegation.resource_type and delegation.resource_type != resource_type:
                continue
                
            # Filter by resource ID if provided
            if resource_id and delegation.resource_id and delegation.resource_id != resource_id:
                continue
                
            # Add permissions
            delegated_permissions.update(delegation.permissions)
            
        return list(delegated_permissions)
    
    def request_role_assignment(
        self,
        user_id: str,
        role_id: str,
        requested_by: str,
        approvers: List[str],
        justification: str = None,
        expires_at: datetime = None,
        metadata: Dict[str, Any] = None
    ) -> Tuple[str, List[str]]:
        """
        Request a role assignment that requires approval.
        
        Args:
            user_id: User ID to assign role to
            role_id: Role ID to assign
            requested_by: User ID of the requester
            approvers: List of user IDs who can approve the request
            justification: Optional justification for the request
            expires_at: Optional expiration time for the assignment
            metadata: Additional metadata
            
        Returns:
            Tuple of (assignment_id, approval_ids)
            
        Raises:
            AuthorizationError: If role does not exist
        """
        # Check if role exists
        if not self.base_rbac_manager.get_role_by_id(role_id):
            raise AuthorizationError(f"Role with ID '{role_id}' does not exist")
            
        # Create a pending assignment
        assignment = self.base_rbac_manager.assign_role_to_user(
            user_id=user_id,
            role_id=role_id,
            assigned_by=requested_by,
            expires_at=expires_at,
            metadata={
                "status": "pending",
                "justification": justification,
                **(metadata or {})
            }
        )
        
        # Create approval requests
        approval_ids = []
        for approver_id in approvers:
            approval = RoleAssignmentApproval(
                approval_id=str(uuid.uuid4()),
                assignment_id=assignment.assignment_id,
                approver_id=approver_id,
                status="pending"
            )
            
            # Store approval
            self.approvals[approval.approval_id] = approval
            
            # Update index
            if assignment.assignment_id not in self.assignment_approvals:
                self.assignment_approvals[assignment.assignment_id] = []
            self.assignment_approvals[assignment.assignment_id].append(approval.approval_id)
            
            approval_ids.append(approval.approval_id)
            
            # Emit event
            self.event_manager.emit_event("rbac.approval_requested", {
                "approval_id": approval.approval_id,
                "assignment_id": assignment.assignment_id,
                "approver_id": approver_id,
                "timestamp": datetime.now().isoformat()
            })
            
        return assignment.assignment_id, approval_ids
    
    def approve_role_assignment(
        self,
        approval_id: str,
        approver_id: str,
        comments: str = None
    ) -> bool:
        """
        Approve a role assignment request.
        
        Args:
            approval_id: Approval ID to approve
            approver_id: User ID of the approver
            comments: Optional comments
            
        Returns:
            True if approval was successful, False otherwise
        """
        if approval_id not in self.approvals:
            return False
            
        approval = self.approvals[approval_id]
        
        # Verify approver
        if approval.approver_id != approver_id:
            return False
            
        # Check if already processed
        if approval.status != "pending":
            return False
            
        # Update approval
        approval.status = "approved"
        approval.comments = comments
        approval.updated_at = datetime.now()
        
        # Check if all approvals are complete
        assignment_id = approval.assignment_id
        if assignment_id in self.assignment_approvals:
            all_approved = True
            for approval_id in self.assignment_approvals[assignment_id]:
                if self.approvals[approval_id].status != "approved":
                    all_approved = False
                    break
                    
            if all_approved:
                # Activate the assignment
                # Note: This assumes the assignment metadata contains the assignment object
                # In a real implementation, you would retrieve the assignment from storage
                assignment = self.base_rbac_manager.get_user_role_assignment(assignment_id)
                if assignment:
                    assignment.metadata["status"] = "approved"
                    
                    # Emit event
                    self.event_manager.emit_event("rbac.assignment_approved", {
                        "assignment_id": assignment_id,
                        "user_id": assignment.user_id,
                        "role_id": assignment.role_id,
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Emit event
        self.event_manager.emit_event("rbac.approval_updated", {
            "approval_id": approval_id,
            "status": "approved",
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def reject_role_assignment(
        self,
        approval_id: str,
        approver_id: str,
        comments: str = None
    ) -> bool:
        """
        Reject a role assignment request.
        
        Args:
            approval_id: Approval ID to reject
            approver_id: User ID of the approver
            comments: Optional comments
            
        Returns:
            True if rejection was successful, False otherwise
        """
        if approval_id not in self.approvals:
            return False
            
        approval = self.approvals[approval_id]
        
        # Verify approver
        if approval.approver_id != approver_id:
            return False
            
        # Check if already processed
        if approval.status != "pending":
            return False
            
        # Update approval
        approval.status = "rejected"
        approval.comments = comments
        approval.updated_at = datetime.now()
        
        # Update the assignment
        assignment_id = approval.assignment_id
        assignment = self.base_rbac_manager.get_user_role_assignment(assignment_id)
        if assignment:
            assignment.metadata["status"] = "rejected"
            
            # Emit event
            self.event_manager.emit_event("rbac.assignment_rejected", {
                "assignment_id": assignment_id,
                "user_id": assignment.user_id,
                "role_id": assignment.role_id,
                "timestamp": datetime.now().isoformat()
            })
        
        # Emit event
        self.event_manager.emit_event("rbac.approval_updated", {
            "approval_id": approval_id,
            "status": "rejected",
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def register_dynamic_rule(
        self,
        permission_id: str,
        resource_type: str,
        condition: Callable[[Dict[str, Any]], bool],
        description: str = None,
        priority: int = 0,
        metadata: Dict[str, Any] = None
    ) -> DynamicPermissionRule:
        """
        Register a dynamic permission rule.
        
        Args:
            permission_id: Permission ID the rule applies to
            resource_type: Resource type the rule applies to
            condition: Function that evaluates the rule
            description: Optional description of the rule
            priority: Priority of the rule (higher values take precedence)
            metadata: Additional metadata
            
        Returns:
            DynamicPermissionRule object
        """
        rule = DynamicPermissionRule(
            rule_id=str(uuid.uuid4()),
            permission_id=permission_id,
            resource_type=resource_type,
            condition=condition,
            description=description,
            priority=priority,
            metadata=metadata
        )
        
        # Store rule
        self.dynamic_rules[rule.rule_id] = rule
        
        # Update indexes
        if permission_id not in self.permission_rules:
            self.permission_rules[permission_id] = []
        self.permission_rules[permission_id].append(rule.rule_id)
        
        if resource_type not in self.resource_type_rules:
            self.resource_type_rules[resource_type] = []
        self.resource_type_rules[resource_type].append(rule.rule_id)
        
        # Emit event
        self.event_manager.emit_event("rbac.dynamic_rule_registered", {
            "rule_id": rule.rule_id,
            "permission_id": permission_id,
            "resource_type": resource_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return rule
    
    def evaluate_permission(
        self,
        user_id: str,
        permission_id: str,
        resource_type: str,
        resource_id: str = None,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Evaluate if a user has a permission, considering dynamic rules.
        
        Args:
            user_id: User ID to check
            permission_id: Permission ID to check
            resource_type: Resource type to check
            resource_id: Optional resource ID to check
            context: Additional context for rule evaluation
            
        Returns:
            True if user has the permission, False otherwise
        """
        # Initialize context
        eval_context = context or {}
        eval_context.update({
            "user_id": user_id,
            "permission_id": permission_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "timestamp": datetime.now()
        })
        
        # Check if user is resource owner
        if resource_id and self.is_resource_owner(user_id, resource_id, resource_type):
            # Resource owners typically have full access to their resources
            return True
            
        # Check base RBAC permissions
        has_base_permission = self.base_rbac_manager.has_permission(user_id, permission_id)
        
        # Check delegated permissions
        delegated_permissions = self.get_delegated_permissions(user_id, resource_type, resource_id)
        has_delegated_permission = permission_id in delegated_permissions
        
        # If user has the permission through base RBAC or delegation, apply dynamic rules
        if has_base_permission or has_delegated_permission:
            # Get applicable rules
            applicable_rules = []
            
            # Add permission-specific rules
            if permission_id in self.permission_rules:
                for rule_id in self.permission_rules[permission_id]:
                    if rule_id in self.dynamic_rules:
                        rule = self.dynamic_rules[rule_id]
                        if rule.is_active and rule.resource_type == resource_type:
                            applicable_rules.append(rule)
            
            # Add resource type rules
            if resource_type in self.resource_type_rules:
                for rule_id in self.resource_type_rules[resource_type]:
                    if rule_id in self.dynamic_rules:
                        rule = self.dynamic_rules[rule_id]
                        if rule.is_active and rule.permission_id == permission_id:
                            # Avoid duplicates
                            if not any(r.rule_id == rule.rule_id for r in applicable_rules):
                                applicable_rules.append(rule)
            
            # If no rules apply, return the base permission
            if not applicable_rules:
                return has_base_permission or has_delegated_permission
            
            # Sort rules by priority (descending)
            applicable_rules.sort(key=lambda r: r.priority, reverse=True)
            
            # Evaluate rules
            for rule in applicable_rules:
                if rule.evaluate(eval_context):
                    return True
            
            # If no rules match, deny access
            return False
        
        # User doesn't have the permission through base RBAC or delegation
        return False
    
    def check_permission(
        self,
        user_id: str,
        permission_id: str,
        resource_type: str,
        resource_id: str = None,
        context: Dict[str, Any] = None
    ) -> None:
        """
        Check if a user has a permission and raise an error if not.
        
        Args:
            user_id: User ID to check
            permission_id: Permission ID to check
            resource_type: Resource type to check
            resource_id: Optional resource ID to check
            context: Additional context for rule evaluation
            
        Raises:
            AuthorizationError: If user does not have the permission
        """
        if not self.evaluate_permission(user_id, permission_id, resource_type, resource_id, context):
            resource_str = f" on {resource_type}"
            if resource_id:
                resource_str += f":{resource_id}"
            raise AuthorizationError(f"User does not have permission: {permission_id}{resource_str}")
    
    def get_user_permissions_for_resource(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str = None
    ) -> List[str]:
        """
        Get all permissions a user has for a specific resource.
        
        Args:
            user_id: User ID to get permissions for
            resource_type: Resource type
            resource_id: Optional resource ID
            
        Returns:
            List of permission IDs
        """
        # Get base permissions
        base_permissions = [p.permission_id for p in self.base_rbac_manager.get_user_permissions(user_id)]
        
        # Get delegated permissions
        delegated_permissions = self.get_delegated_permissions(user_id, resource_type, resource_id)
        
        # Combine permissions
        all_permissions = set(base_permissions + delegated_permissions)
        
        # Filter by dynamic rules
        result_permissions = []
        for permission_id in all_permissions:
            if self.evaluate_permission(user_id, permission_id, resource_type, resource_id):
                result_permissions.append(permission_id)
                
        return result_permissions
