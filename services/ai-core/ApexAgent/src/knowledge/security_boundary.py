"""
Security Boundaries for Dr. TARDIS

This module provides security boundary functionality for the Dr. TARDIS system,
including access control, permission checking, and query sanitization.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from enum import Enum, auto

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AccessLevel(Enum):
    """
    Enumeration of access levels for security boundaries.
    
    Levels:
        PUBLIC: Accessible to all users
        STANDARD: Accessible to authenticated users
        ELEVATED: Accessible to users with elevated privileges
        ADMIN: Accessible to administrators only
    """
    PUBLIC = auto()
    STANDARD = auto()
    ELEVATED = auto()
    ADMIN = auto()


class SecurityBoundary:
    """
    Provides security boundary functionality for the Dr. TARDIS system.
    
    This class manages access control, permission checking, and query
    sanitization to ensure secure information access.
    
    Attributes:
        logger (logging.Logger): Logger for security boundary
    """
    
    def __init__(self):
        """Initialize the Security Boundary."""
        self.logger = logging.getLogger("SecurityBoundary")
        self.logger.info("SecurityBoundary initialized")
    
    def check_access_permission(self, user_context: Dict[str, Any], 
                              resource: Dict[str, Any]) -> bool:
        """
        Check if a user has permission to access a resource.
        
        Args:
            user_context: User context information
            resource: Resource to check access for
            
        Returns:
            bool: True if access is allowed, False otherwise
        """
        # Get user access level
        user_access_level = user_context.get("access_level", AccessLevel.PUBLIC)
        
        # Get resource required access level
        resource_access_level = resource.get("required_access_level", AccessLevel.PUBLIC)
        
        # Check if user has sufficient access level
        if user_access_level.value < resource_access_level.value:
            self.logger.debug(f"Access denied: User level {user_access_level} < Required level {resource_access_level}")
            return False
        
        # Check if resource is restricted to specific users
        if resource.get("restricted", False):
            allowed_users = resource.get("allowed_users", [])
            user_id = user_context.get("user_id")
            
            if user_id not in allowed_users:
                self.logger.debug(f"Access denied: User {user_id} not in allowed users list")
                return False
        
        # Access allowed
        return True
    
    def filter_results_by_permission(self, user_context: Dict[str, Any], 
                                   results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter results based on user permissions.
        
        Args:
            user_context: User context information
            results: List of results to filter
            
        Returns:
            List: Filtered results
        """
        filtered_results = []
        
        for result in results:
            if self.check_access_permission(user_context, result):
                filtered_results.append(result)
        
        self.logger.debug(f"Filtered {len(results)} results to {len(filtered_results)} based on permissions")
        return filtered_results
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitize a query to remove sensitive information and prevent injection attacks.
        
        Args:
            query: Query string to sanitize
            
        Returns:
            str: Sanitized query
        """
        # Remove potential SQL injection patterns
        sql_patterns = [
            r";\s*DROP\s+TABLE",
            r";\s*DELETE\s+FROM",
            r";\s*INSERT\s+INTO",
            r";\s*UPDATE\s+",
            r"--",
            r"/\*.*\*/",
            r"UNION\s+SELECT"
        ]
        
        sanitized = query
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        
        # Remove potential command injection patterns
        cmd_patterns = [
            r"&&",
            r"\|\|",
            r"`.*`",
            r"\$\(.*\)",
            r";\s*",
            r">\s*",
            r"<\s*"
        ]
        
        for pattern in cmd_patterns:
            sanitized = re.sub(pattern, "", sanitized)
        
        # Remove potential sensitive information
        sensitive_patterns = [
            # Credit card numbers
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            # Social security numbers
            r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
            # Passwords - Fix: Improved pattern to capture the entire password phrase
            r"password\s*[:=]\s*\S+",
            r"passwd\s*[:=]\s*\S+",
            r"pwd\s*[:=]\s*\S+",
            # API keys (generic pattern)
            r"api[-_]?key\s*[:=]\s*\S+"
        ]
        
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        
        # Additional patterns for specific sensitive information - Fix for test_sanitize_query
        # Look for common password words and redact surrounding content
        password_keywords = ["password", "secret", "credential", "key"]
        for keyword in password_keywords:
            # Find any word containing the keyword and redact it plus surrounding words
            pattern = r'\b\w*' + keyword + r'\w*\b.{0,20}'
            matches = re.finditer(pattern, sanitized, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)
                sanitized = sanitized.replace(matched_text, "[REDACTED]")
        
        # Log if query was modified
        if sanitized != query:
            self.logger.info("Query was sanitized")
        
        return sanitized
    
    def validate_data_access(self, user_context: Dict[str, Any], 
                           data_source: str, operation: str) -> bool:
        """
        Validate if a user can access a data source for a specific operation.
        
        Args:
            user_context: User context information
            data_source: Data source identifier
            operation: Operation to perform (e.g., "read", "write", "delete")
            
        Returns:
            bool: True if access is allowed, False otherwise
        """
        # Get user access level
        user_access_level = user_context.get("access_level", AccessLevel.PUBLIC)
        
        # Define operation requirements
        operation_requirements = {
            "read": AccessLevel.PUBLIC,
            "search": AccessLevel.PUBLIC,
            "write": AccessLevel.STANDARD,
            "update": AccessLevel.STANDARD,
            "delete": AccessLevel.ELEVATED,
            "admin": AccessLevel.ADMIN
        }
        
        # Get required access level for operation
        required_level = operation_requirements.get(operation, AccessLevel.ADMIN)
        
        # Check if user has sufficient access level
        if user_access_level.value < required_level.value:
            self.logger.debug(f"Data access denied: User level {user_access_level} < Required level {required_level} for {operation} on {data_source}")
            return False
        
        # Additional checks for specific data sources could be added here
        
        # Access allowed
        return True
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive data for secure storage or transmission.
        
        Args:
            data: Data to encrypt
            
        Returns:
            str: Encrypted data
        """
        # This is a placeholder for actual encryption
        # In a real implementation, use a proper encryption library
        self.logger.info("Encrypting sensitive data")
        return f"ENCRYPTED:{data}"
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            str: Decrypted data
        """
        # This is a placeholder for actual decryption
        # In a real implementation, use a proper encryption library
        if encrypted_data.startswith("ENCRYPTED:"):
            self.logger.info("Decrypting sensitive data")
            return encrypted_data[10:]  # Remove "ENCRYPTED:" prefix
        return encrypted_data
    
    def log_access_attempt(self, user_context: Dict[str, Any], 
                         resource: Dict[str, Any], allowed: bool):
        """
        Log an access attempt for auditing purposes.
        
        Args:
            user_context: User context information
            resource: Resource being accessed
            allowed: Whether access was allowed
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_context.get("user_id", "unknown"),
            "resource_id": resource.get("id", "unknown"),
            "resource_type": resource.get("type", "unknown"),
            "access_allowed": allowed,
            "user_access_level": str(user_context.get("access_level", AccessLevel.PUBLIC)),
            "required_access_level": str(resource.get("required_access_level", AccessLevel.PUBLIC))
        }
        
        self.logger.info(f"Access {'allowed' if allowed else 'denied'}: {log_entry}")
        
        # In a real implementation, log to a secure audit log
        # This is a placeholder for demonstration purposes


# Example usage
def example_usage():
    # Create security boundary
    security = SecurityBoundary()
    
    # Define user context
    user_context = {
        "user_id": "user123",
        "access_level": AccessLevel.STANDARD
    }
    
    # Define resources
    public_resource = {
        "id": "resource1",
        "type": "document",
        "required_access_level": AccessLevel.PUBLIC,
        "restricted": False
    }
    
    restricted_resource = {
        "id": "resource2",
        "type": "document",
        "required_access_level": AccessLevel.ELEVATED,
        "restricted": True,
        "allowed_users": ["admin1", "user456"]
    }
    
    # Check permissions
    print(f"Access to public resource: {security.check_access_permission(user_context, public_resource)}")
    print(f"Access to restricted resource: {security.check_access_permission(user_context, restricted_resource)}")
    
    # Filter results
    results = [public_resource, restricted_resource]
    filtered = security.filter_results_by_permission(user_context, results)
    print(f"Filtered results: {len(filtered)}")
    
    # Sanitize query
    query = "SELECT * FROM users WHERE password = 'secret123'"
    sanitized = security.sanitize_query(query)
    print(f"Sanitized query: {sanitized}")

if __name__ == "__main__":
    example_usage()
