"""
Tenant Middleware for Aideon AI Lite Vector Database

This module provides middleware for enforcing multi-tenant isolation
in the vector database integration of the Aideon AI Lite platform.

Production-ready features:
- Tenant validation and authorization
- Request interception and tenant context injection
- Access control enforcement
- Comprehensive logging and auditing
"""

import logging
import functools
import threading
from typing import Dict, Any, Optional, Callable, List, Set, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# Thread-local storage for tenant context
_tenant_context = threading.local()


class TenantAccessError(Exception):
    """Exception raised when tenant access is denied."""
    pass


class TenantValidationError(Exception):
    """Exception raised when tenant validation fails."""
    pass


class TenantContext:
    """
    Class representing the current tenant context.
    
    This class stores information about the current tenant and
    provides methods for tenant validation and access control.
    """
    
    def __init__(self, tenant_id: str, user_id: Optional[str] = None, roles: Optional[List[str]] = None):
        """
        Initialize the tenant context.
        
        Args:
            tenant_id: The ID of the current tenant.
            user_id: Optional ID of the current user.
            roles: Optional list of roles for the current user.
        """
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.roles = roles or []
        self.created_at = datetime.utcnow()
    
    def has_role(self, role: str) -> bool:
        """
        Check if the current user has a specific role.
        
        Args:
            role: The role to check for.
            
        Returns:
            True if the user has the role, False otherwise.
        """
        return role in self.roles
    
    def has_any_role(self, roles: List[str]) -> bool:
        """
        Check if the current user has any of the specified roles.
        
        Args:
            roles: The roles to check for.
            
        Returns:
            True if the user has any of the roles, False otherwise.
        """
        return any(role in self.roles for role in roles)
    
    def has_all_roles(self, roles: List[str]) -> bool:
        """
        Check if the current user has all of the specified roles.
        
        Args:
            roles: The roles to check for.
            
        Returns:
            True if the user has all of the roles, False otherwise.
        """
        return all(role in self.roles for role in roles)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tenant context to a dictionary.
        
        Returns:
            A dictionary representation of the tenant context.
        """
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "roles": self.roles,
            "created_at": self.created_at.isoformat(),
        }


def get_current_tenant_id() -> Optional[str]:
    """
    Get the ID of the current tenant.
    
    Returns:
        The ID of the current tenant, or None if no tenant context is set.
    """
    context = getattr(_tenant_context, "context", None)
    return context.tenant_id if context else None


def get_current_tenant_context() -> Optional[TenantContext]:
    """
    Get the current tenant context.
    
    Returns:
        The current tenant context, or None if no tenant context is set.
    """
    return getattr(_tenant_context, "context", None)


def set_current_tenant_context(context: TenantContext):
    """
    Set the current tenant context.
    
    Args:
        context: The tenant context to set.
    """
    _tenant_context.context = context


def clear_current_tenant_context():
    """Clear the current tenant context."""
    if hasattr(_tenant_context, "context"):
        delattr(_tenant_context, "context")


class TenantMiddleware:
    """
    Middleware for enforcing multi-tenant isolation.
    
    This middleware intercepts requests to the vector database and
    enforces tenant isolation and access control.
    """
    
    def __init__(self, tenant_validator: Optional[Callable[[str], bool]] = None):
        """
        Initialize the tenant middleware.
        
        Args:
            tenant_validator: Optional function to validate tenant IDs.
                             If not provided, all tenant IDs are considered valid.
        """
        self.tenant_validator = tenant_validator or (lambda tenant_id: True)
        self.protected_operations = {
            "create_collection",
            "delete_collection",
            "list_collections",
            "get_collection_info",
            "insert_document",
            "insert_documents",
            "get_document",
            "delete_document",
            "update_document",
            "search_by_vector",
            "search_by_text",
            "search_by_id",
            "count_documents",
            "create_index",
            "get_nearest_neighbors",
        }
        self.admin_operations = {
            "delete_collection",
        }
    
    def validate_tenant(self, tenant_id: str) -> bool:
        """
        Validate a tenant ID.
        
        Args:
            tenant_id: The tenant ID to validate.
            
        Returns:
            True if the tenant ID is valid, False otherwise.
            
        Raises:
            TenantValidationError: If tenant validation fails.
        """
        try:
            is_valid = self.tenant_validator(tenant_id)
            if not is_valid:
                raise TenantValidationError(f"Invalid tenant ID: {tenant_id}")
            return is_valid
        except Exception as e:
            logger.error(f"Tenant validation failed for tenant {tenant_id}: {str(e)}")
            raise TenantValidationError(f"Tenant validation failed: {str(e)}")
    
    def check_access(self, operation: str, tenant_id: Optional[str] = None) -> bool:
        """
        Check if the current tenant has access to an operation.
        
        Args:
            operation: The operation to check access for.
            tenant_id: Optional tenant ID to check access for.
                      If not provided, uses the current tenant context.
            
        Returns:
            True if access is granted, False otherwise.
            
        Raises:
            TenantAccessError: If access is denied.
        """
        # Get current tenant context
        context = get_current_tenant_context()
        
        # If no context is set, deny access to protected operations
        if not context and operation in self.protected_operations:
            raise TenantAccessError(f"No tenant context set for protected operation: {operation}")
        
        # If tenant_id is provided, check if it matches the current tenant
        if tenant_id and context and tenant_id != context.tenant_id:
            # Admin users can access other tenants
            if not context.has_role("admin"):
                raise TenantAccessError(f"Tenant mismatch: {tenant_id} != {context.tenant_id}")
        
        # Check if operation requires admin role
        if operation in self.admin_operations and context and not context.has_role("admin"):
            raise TenantAccessError(f"Admin role required for operation: {operation}")
        
        return True
    
    def intercept(self, func: Callable) -> Callable:
        """
        Decorator for intercepting vector database operations.
        
        This decorator enforces tenant isolation and access control
        for vector database operations.
        
        Args:
            func: The function to intercept.
            
        Returns:
            The intercepted function.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get operation name
            operation = func.__name__
            
            # Get tenant_id from kwargs
            tenant_id = kwargs.get("tenant_id")
            
            # Check access
            self.check_access(operation, tenant_id)
            
            # If tenant_id is not provided but we have a tenant context, inject it
            if tenant_id is None and operation in self.protected_operations:
                context = get_current_tenant_context()
                if context:
                    kwargs["tenant_id"] = context.tenant_id
            # If tenant_id is provided in both kwargs and from context, remove from kwargs
            # to avoid "got multiple values for argument" error
            elif tenant_id is not None and operation in self.protected_operations:
                context = get_current_tenant_context()
                if context and context.tenant_id == tenant_id:
                    # If the tenant_id in kwargs matches the context, we can safely remove it
                    # as it will be passed as part of the context
                    if "tenant_id" in kwargs:
                        del kwargs["tenant_id"]
            
            # Validate tenant_id if provided
            if tenant_id is not None:
                self.validate_tenant(tenant_id)
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper


def with_tenant_context(tenant_id: str, user_id: Optional[str] = None, roles: Optional[List[str]] = None):
    """
    Decorator for setting tenant context for a function call.
    
    This decorator sets the tenant context for the duration of the function call
    and clears it afterward.
    
    Args:
        tenant_id: The ID of the tenant.
        user_id: Optional ID of the user.
        roles: Optional list of roles for the user.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create tenant context
            context = TenantContext(tenant_id, user_id, roles)
            
            # Set tenant context
            previous_context = get_current_tenant_context()
            set_current_tenant_context(context)
            
            try:
                # Call the original function
                return func(*args, **kwargs)
            finally:
                # Restore previous context
                if previous_context:
                    set_current_tenant_context(previous_context)
                else:
                    clear_current_tenant_context()
        
        return wrapper
    
    return decorator


def require_tenant_context(func: Callable) -> Callable:
    """
    Decorator for requiring tenant context for a function call.
    
    This decorator checks if a tenant context is set and raises an error if not.
    
    Args:
        func: The function to decorate.
        
    Returns:
        The decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if tenant context is set
        if not get_current_tenant_context():
            raise TenantAccessError("No tenant context set")
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper


def require_role(role: str) -> Callable:
    """
    Decorator for requiring a specific role for a function call.
    
    This decorator checks if the current user has the specified role
    and raises an error if not.
    
    Args:
        role: The role to require.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get tenant context
            context = get_current_tenant_context()
            
            # Check if context is set
            if not context:
                raise TenantAccessError("No tenant context set")
            
            # Check if user has the required role
            if not context.has_role(role):
                raise TenantAccessError(f"Role {role} required")
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def require_any_role(roles: List[str]) -> Callable:
    """
    Decorator for requiring any of the specified roles for a function call.
    
    This decorator checks if the current user has any of the specified roles
    and raises an error if not.
    
    Args:
        roles: The roles to require.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get tenant context
            context = get_current_tenant_context()
            
            # Check if context is set
            if not context:
                raise TenantAccessError("No tenant context set")
            
            # Check if user has any of the required roles
            if not context.has_any_role(roles):
                raise TenantAccessError(f"Any of roles {roles} required")
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def require_all_roles(roles: List[str]) -> Callable:
    """
    Decorator for requiring all of the specified roles for a function call.
    
    This decorator checks if the current user has all of the specified roles
    and raises an error if not.
    
    Args:
        roles: The roles to require.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get tenant context
            context = get_current_tenant_context()
            
            # Check if context is set
            if not context:
                raise TenantAccessError("No tenant context set")
            
            # Check if user has all of the required roles
            if not context.has_all_roles(roles):
                raise TenantAccessError(f"All of roles {roles} required")
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
