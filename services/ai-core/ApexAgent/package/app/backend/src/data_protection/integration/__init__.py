"""
Integration module for the Data Protection Framework.

This module provides integration points between the Data Protection Framework
and other ApexAgent components.
"""

from .auth_integration import (
    AuthIntegrationManager,
    SubscriptionIntegrationManager,
    DataProtectionIntegration
)

__all__ = [
    'AuthIntegrationManager',
    'SubscriptionIntegrationManager',
    'DataProtectionIntegration'
]
