"""
Integration module for connecting the Subscription and Licensing System with the Authentication and Authorization modules.

This module provides the necessary interfaces and adapters to ensure seamless operation
between user authentication, subscription management, and access control.
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

# Import from Authentication and Authorization modules
from auth.authentication.auth_manager import AuthManager
from auth.authorization.auth_rbac import RBACManager, Permission, Resource, Role
from auth.identity.identity_manager import IdentityManager
from auth.plugin_security.plugin_security_manager import PluginSecurityManager

# Import from Subscription and Licensing modules
from subscription.core.license_generator import LicenseFeature, LicenseType
from subscription.core.license_validator import LicenseValidator
from subscription.core.subscription_manager import (
    SubscriptionManager, SubscriptionRepository, SubscriptionService,
    FeatureGate, Subscription, SubscriptionStatus, SubscriptionTier
)
from subscription.core.usage_tracking import (
    UsageService, ResourceType, QuotaManager, UsageTracker,
    QuotaEnforcer, UsageAnalytics
)


class SubscriptionPermission(Enum):
    """Enumeration of subscription-related permissions."""
    VIEW_SUBSCRIPTION = "view_subscription"
    MANAGE_SUBSCRIPTION = "manage_subscription"
    VIEW_USAGE = "view_usage"
    VIEW_BILLING = "view_billing"
    MANAGE_BILLING = "manage_billing"
    MANAGE_LICENSES = "manage_licenses"
    UPGRADE_SUBSCRIPTION = "upgrade_subscription"
    DOWNGRADE_SUBSCRIPTION = "downgrade_subscription"
    CANCEL_SUBSCRIPTION = "cancel_subscription"


class SubscriptionResource(Enum):
    """Enumeration of subscription-related resources."""
    SUBSCRIPTION = "subscription"
    LICENSE = "license"
    USAGE = "usage"
    BILLING = "billing"
    PAYMENT_METHOD = "payment_method"
    INVOICE = "invoice"


class SubscriptionRole(Enum):
    """Enumeration of subscription-related roles."""
    SUBSCRIPTION_VIEWER = "subscription_viewer"
    SUBSCRIPTION_MANAGER = "subscription_manager"
    BILLING_VIEWER = "billing_viewer"
    BILLING_MANAGER = "billing_manager"
    LICENSE_MANAGER = "license_manager"


class SubscriptionAuthAdapter:
    """Adapter for integrating subscription system with authentication and authorization."""

    def __init__(
        self,
        auth_manager: AuthManager,
        rbac_manager: RBACManager,
        identity_manager: IdentityManager,
        subscription_service: SubscriptionService,
        license_validator: LicenseValidator,
        usage_service: UsageService
    ):
        """
        Initialize subscription auth adapter.

        Args:
            auth_manager: Authentication manager
            rbac_manager: RBAC manager for authorization
            identity_manager: Identity manager
            subscription_service: Subscription service
            license_validator: License validator
            usage_service: Usage service
        """
        self.auth_manager = auth_manager
        self.rbac_manager = rbac_manager
        self.identity_manager = identity_manager
        self.subscription_service = subscription_service
        self.license_validator = license_validator
        self.usage_service = usage_service
        
        # Initialize subscription-related roles and permissions
        self._initialize_rbac()

    def _initialize_rbac(self) -> None:
        """Initialize subscription-related roles and permissions in RBAC system."""
        # Define permissions
        subscription_permissions = {
            SubscriptionPermission.VIEW_SUBSCRIPTION: "View subscription details",
            SubscriptionPermission.MANAGE_SUBSCRIPTION: "Manage subscription settings",
            SubscriptionPermission.VIEW_USAGE: "View usage statistics",
            SubscriptionPermission.VIEW_BILLING: "View billing information",
            SubscriptionPermission.MANAGE_BILLING: "Manage billing settings",
            SubscriptionPermission.MANAGE_LICENSES: "Manage license keys",
            SubscriptionPermission.UPGRADE_SUBSCRIPTION: "Upgrade subscription tier",
            SubscriptionPermission.DOWNGRADE_SUBSCRIPTION: "Downgrade subscription tier",
            SubscriptionPermission.CANCEL_SUBSCRIPTION: "Cancel subscription"
        }
        
        # Register permissions
        for perm, description in subscription_permissions.items():
            self.rbac_manager.register_permission(
                Permission(perm.value, description)
            )
            
        # Define roles with permissions
        subscription_roles = {
            SubscriptionRole.SUBSCRIPTION_VIEWER: {
                SubscriptionPermission.VIEW_SUBSCRIPTION,
                SubscriptionPermission.VIEW_USAGE
            },
            SubscriptionRole.SUBSCRIPTION_MANAGER: {
                SubscriptionPermission.VIEW_SUBSCRIPTION,
                SubscriptionPermission.MANAGE_SUBSCRIPTION,
                SubscriptionPermission.VIEW_USAGE,
                SubscriptionPermission.UPGRADE_SUBSCRIPTION,
                SubscriptionPermission.DOWNGRADE_SUBSCRIPTION
            },
            SubscriptionRole.BILLING_VIEWER: {
                SubscriptionPermission.VIEW_BILLING,
                SubscriptionPermission.VIEW_SUBSCRIPTION
            },
            SubscriptionRole.BILLING_MANAGER: {
                SubscriptionPermission.VIEW_BILLING,
                SubscriptionPermission.MANAGE_BILLING,
                SubscriptionPermission.VIEW_SUBSCRIPTION
            },
            SubscriptionRole.LICENSE_MANAGER: {
                SubscriptionPermission.MANAGE_LICENSES,
                SubscriptionPermission.VIEW_SUBSCRIPTION
            }
        }
        
        # Register roles
        for role_enum, permissions in subscription_roles.items():
            role = Role(
                role_enum.value,
                f"{role_enum.value} role",
                {perm.value for perm in permissions}
            )
            self.rbac_manager.register_role(role)

    def get_customer_id_for_user(self, user_id: str) -> str:
        """
        Get customer ID for a user.

        In many cases, this might be the same as the user ID, but this method
        allows for more complex mappings if needed.

        Args:
            user_id: User ID

        Returns:
            Customer ID
        """
        # Get user profile from identity manager
        user_profile = self.identity_manager.get_user_profile(user_id)
        
        if user_profile and "customer_id" in user_profile.attributes:
            return user_profile.attributes["customer_id"]
            
        # Default to using user ID as customer ID
        return user_id

    def check_subscription_permission(
        self,
        user_id: str,
        permission: SubscriptionPermission,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Check if a user has a subscription-related permission.

        Args:
            user_id: User ID
            permission: Subscription permission to check
            resource_id: Optional resource ID (e.g., subscription ID)

        Returns:
            True if user has permission, False otherwise
        """
        # Create resource context
        context = {}
        if resource_id:
            context["resource_id"] = resource_id
            
            # If checking subscription resource, add ownership information
            if permission in [
                SubscriptionPermission.MANAGE_SUBSCRIPTION,
                SubscriptionPermission.CANCEL_SUBSCRIPTION,
                SubscriptionPermission.UPGRADE_SUBSCRIPTION,
                SubscriptionPermission.DOWNGRADE_SUBSCRIPTION
            ]:
                # Check if user is the owner of the subscription
                customer_id = self.get_customer_id_for_user(user_id)
                subscription = self.subscription_service.subscription_repository.get(resource_id)
                
                if subscription and subscription.customer_id == customer_id:
                    context["is_owner"] = True
        
        # Check permission using RBAC manager
        return self.rbac_manager.check_permission(
            user_id=user_id,
            permission=permission.value,
            resource=SubscriptionResource.SUBSCRIPTION.value,
            context=context
        )

    def check_feature_access(self, user_id: str, feature: LicenseFeature) -> bool:
        """
        Check if a user has access to a feature based on their subscription.

        Args:
            user_id: User ID
            feature: Feature to check

        Returns:
            True if user has access, False otherwise
        """
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Check feature access using subscription service
        return self.subscription_service.check_customer_access(customer_id, feature)

    def get_user_subscription_tier(self, user_id: str) -> Optional[SubscriptionTier]:
        """
        Get the subscription tier for a user.

        Args:
            user_id: User ID

        Returns:
            Subscription tier or None if no active subscription
        """
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Get active subscriptions
        active_subscriptions = self.subscription_service.get_active_customer_subscriptions(customer_id)
        
        if not active_subscriptions:
            return None
            
        # Get tier for the first active subscription
        # In a more complex system, you might want to handle multiple subscriptions differently
        subscription = active_subscriptions[0]
        tier = self.subscription_service.subscription_manager.get_tier(subscription.tier_id)
        
        return tier

    def track_user_usage(
        self,
        user_id: str,
        resource_type: ResourceType,
        quantity: int,
        feature: Optional[LicenseFeature] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Track resource usage for a user.

        Args:
            user_id: User ID
            resource_type: Resource type
            quantity: Quantity to track
            feature: Feature associated with the usage
            metadata: Additional metadata about the usage

        Returns:
            Tuple of (allowed, message)
        """
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Get active subscriptions
        active_subscriptions = self.subscription_service.get_active_customer_subscriptions(customer_id)
        
        # Default subscription ID
        subscription_id = None
        
        # If there are active subscriptions, use the first one
        if active_subscriptions:
            subscription_id = active_subscriptions[0].subscription_id
            
        # Track usage with quota enforcement
        allowed, record, message = self.usage_service.track_usage(
            customer_id=customer_id,
            resource_type=resource_type,
            quantity=quantity,
            subscription_id=subscription_id,
            feature=feature,
            metadata=metadata,
            enforce_quota=True
        )
        
        return allowed, message

    def get_user_quota_status(self, user_id: str) -> Dict[str, Dict[str, Union[int, float, str]]]:
        """
        Get quota status for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with quota status information
        """
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Get quota status for all resources
        return self.usage_service.get_quota_status(customer_id)

    def validate_user_license(self, user_id: str, license_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a license key for a user.

        Args:
            user_id: User ID
            license_key: License key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate the license
        result = self.license_validator.validate_license_key(license_key)
        
        if not result.is_valid:
            return False, result.error_message
            
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Check if license is already associated with a subscription
        active_subscriptions = self.subscription_service.get_active_customer_subscriptions(customer_id)
        
        for subscription in active_subscriptions:
            if license_key in subscription.license_keys:
                return True, None
                
        # License is valid but not associated with any subscription
        # In a real system, you might want to associate it automatically
        return True, "License is valid but not associated with any subscription"

    def associate_license_with_user(
        self,
        user_id: str,
        license_key: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Associate a license key with a user's subscription.

        Args:
            user_id: User ID
            license_key: License key to associate

        Returns:
            Tuple of (success, error_message)
        """
        # Validate the license first
        result = self.license_validator.validate_license_key(license_key)
        
        if not result.is_valid:
            return False, result.error_message
            
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Get active subscriptions
        active_subscriptions = self.subscription_service.get_active_customer_subscriptions(customer_id)
        
        if not active_subscriptions:
            return False, "No active subscription found for user"
            
        # Associate license with the first active subscription
        # In a more complex system, you might want to handle multiple subscriptions differently
        subscription_id = active_subscriptions[0].subscription_id
        
        success = self.subscription_service.add_license_to_subscription(
            subscription_id=subscription_id,
            license_key=license_key
        )
        
        if not success:
            return False, "Failed to associate license with subscription"
            
        return True, None

    def get_user_features(self, user_id: str) -> Set[LicenseFeature]:
        """
        Get all features available to a user.

        Args:
            user_id: User ID

        Returns:
            Set of available features
        """
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Get features from subscription service
        return self.subscription_service.get_customer_features(customer_id)

    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        Get all subscriptions for a user.

        Args:
            user_id: User ID

        Returns:
            List of subscriptions
        """
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Get subscriptions from subscription service
        return self.subscription_service.get_customer_subscriptions(customer_id)

    def get_user_active_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        Get active subscriptions for a user.

        Args:
            user_id: User ID

        Returns:
            List of active subscriptions
        """
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Get active subscriptions from subscription service
        return self.subscription_service.get_active_customer_subscriptions(customer_id)

    def create_subscription_for_user(
        self,
        user_id: str,
        tier_id: str,
        period: str,
        payment_method: Optional[str] = None,
        auto_renew: bool = True
    ) -> Tuple[bool, Optional[Subscription], Optional[str]]:
        """
        Create a new subscription for a user.

        Args:
            user_id: User ID
            tier_id: Subscription tier ID
            period: Subscription period
            payment_method: Payment method ID
            auto_renew: Whether to auto-renew

        Returns:
            Tuple of (success, subscription, error_message)
        """
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Convert period string to enum
        from subscription.core.subscription_manager import SubscriptionPeriod
        try:
            period_enum = SubscriptionPeriod(period)
        except ValueError:
            return False, None, f"Invalid subscription period: {period}"
            
        # Create subscription
        subscription = self.subscription_service.create_subscription(
            customer_id=customer_id,
            tier_id=tier_id,
            period=period_enum,
            payment_method=payment_method,
            auto_renew=auto_renew
        )
        
        if not subscription:
            return False, None, "Failed to create subscription"
            
        return True, subscription, None

    def cancel_user_subscription(
        self,
        user_id: str,
        subscription_id: str,
        immediate: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Cancel a subscription for a user.

        Args:
            user_id: User ID
            subscription_id: Subscription ID to cancel
            immediate: Whether to cancel immediately or at the end of the period

        Returns:
            Tuple of (success, error_message)
        """
        # Check permission
        has_permission = self.check_subscription_permission(
            user_id=user_id,
            permission=SubscriptionPermission.CANCEL_SUBSCRIPTION,
            resource_id=subscription_id
        )
        
        if not has_permission:
            return False, "User does not have permission to cancel this subscription"
            
        # Cancel subscription
        success = self.subscription_service.cancel_subscription(
            subscription_id=subscription_id,
            immediate=immediate
        )
        
        if not success:
            return False, "Failed to cancel subscription"
            
        return True, None

    def get_user_usage_report(
        self,
        user_id: str,
        period: str = "month"
    ) -> Dict[str, Union[Dict[str, int], int]]:
        """
        Get usage report for a user.

        Args:
            user_id: User ID
            period: Period type ("day", "week", "month", "year")

        Returns:
            Usage report data
        """
        # Check permission
        has_permission = self.check_subscription_permission(
            user_id=user_id,
            permission=SubscriptionPermission.VIEW_USAGE
        )
        
        if not has_permission:
            return {"error": "User does not have permission to view usage"}
            
        # Get customer ID for the user
        customer_id = self.get_customer_id_for_user(user_id)
        
        # Get usage report
        return self.usage_service.get_usage_report(
            customer_id=customer_id,
            period=period
        )


class AuthSubscriptionMiddleware:
    """Middleware for integrating subscription checks into authentication flows."""

    def __init__(
        self,
        auth_manager: AuthManager,
        subscription_auth_adapter: SubscriptionAuthAdapter
    ):
        """
        Initialize auth subscription middleware.

        Args:
            auth_manager: Authentication manager
            subscription_auth_adapter: Subscription auth adapter
        """
        self.auth_manager = auth_manager
        self.subscription_adapter = subscription_auth_adapter
        
        # Register middleware with auth manager
        self.auth_manager.register_post_authentication_hook(self._post_auth_hook)

    def _post_auth_hook(self, user_id: str, auth_context: Dict[str, any]) -> Dict[str, any]:
        """
        Post-authentication hook to add subscription information.

        Args:
            user_id: User ID
            auth_context: Authentication context

        Returns:
            Updated authentication context
        """
        # Get user's subscription tier
        tier = self.subscription_adapter.get_user_subscription_tier(user_id)
        
        # Get user's features
        features = self.subscription_adapter.get_user_features(user_id)
        
        # Get user's quota status
        quota_status = self.subscription_adapter.get_user_quota_status(user_id)
        
        # Add subscription information to auth context
        subscription_context = {
            "has_active_subscription": tier is not None,
            "subscription_tier": tier.tier_id if tier else "free",
            "features": [feature.value for feature in features],
            "quota_status": {
                resource: status.get("percentage_used", 0)
                for resource, status in quota_status.items()
                if isinstance(status, dict) and "percentage_used" in status
            }
        }
        
        # Update auth context
        auth_context["subscription"] = subscription_context
        
        return auth_context


class FeaturePermissionIntegrator:
    """Integrator for mapping subscription features to RBAC permissions."""

    def __init__(
        self,
        rbac_manager: RBACManager,
        subscription_auth_adapter: SubscriptionAuthAdapter
    ):
        """
        Initialize feature permission integrator.

        Args:
            rbac_manager: RBAC manager
            subscription_auth_adapter: Subscription auth adapter
        """
        self.rbac_manager = rbac_manager
        self.subscription_adapter = subscription_auth_adapter
        
        # Register permission check hook with RBAC manager
        self.rbac_manager.register_permission_check_hook(self._permission_check_hook)
        
        # Initialize feature to permission mappings
        self.feature_permission_map = self._initialize_feature_permission_map()

    def _initialize_feature_permission_map(self) -> Dict[str, Set[LicenseFeature]]:
        """
        Initialize mapping between permissions and required features.

        Returns:
            Dictionary mapping permission names to required features
        """
        # This is a simplified example - in a real system, this might be loaded from a database
        # or configuration file
        return {
            "api:access": {LicenseFeature.API_ACCESS},
            "plugins:advanced": {LicenseFeature.ADVANCED_PLUGINS},
            "support:priority": {LicenseFeature.PRIORITY_SUPPORT},
            "offline:use": {LicenseFeature.OFFLINE_MODE},
            "users:multiple": {LicenseFeature.MULTI_USER},
            "integration:enterprise": {LicenseFeature.ENTERPRISE_INTEGRATION},
            "branding:white_label": {LicenseFeature.WHITE_LABEL},
            "branding:custom": {LicenseFeature.CUSTOM_BRANDING},
            "analytics:advanced": {LicenseFeature.ADVANCED_ANALYTICS}
        }

    def _permission_check_hook(
        self,
        user_id: str,
        permission: str,
        resource: str,
        context: Dict[str, any]
    ) -> Optional[bool]:
        """
        Permission check hook to integrate subscription features.

        Args:
            user_id: User ID
            permission: Permission name
            resource: Resource name
            context: Context information

        Returns:
            True if allowed, False if denied, None to continue normal checks
        """
        # Check if permission requires specific features
        if permission in self.feature_permission_map:
            required_features = self.feature_permission_map[permission]
            
            # Check if user has all required features
            for feature in required_features:
                if not self.subscription_adapter.check_feature_access(user_id, feature):
                    # User doesn't have required feature, deny permission
                    return False
                    
        # No feature requirements or all requirements met, continue normal checks
        return None

    def add_feature_permission_mapping(self, permission: str, features: Set[LicenseFeature]) -> None:
        """
        Add a mapping between a permission and required features.

        Args:
            permission: Permission name
            features: Set of required features
        """
        self.feature_permission_map[permission] = features

    def remove_feature_permission_mapping(self, permission: str) -> bool:
        """
        Remove a feature-permission mapping.

        Args:
            permission: Permission name

        Returns:
            True if mapping was removed, False if not found
        """
        if permission in self.feature_permission_map:
            del self.feature_permission_map[permission]
            return True
            
        return False

    def get_permissions_for_feature(self, feature: LicenseFeature) -> Set[str]:
        """
        Get all permissions that require a specific feature.

        Args:
            feature: Feature to check

        Returns:
            Set of permission names
        """
        permissions = set()
        
        for permission, required_features in self.feature_permission_map.items():
            if feature in required_features:
                permissions.add(permission)
                
        return permissions


class PluginSubscriptionIntegrator:
    """Integrator for subscription-based plugin security."""

    def __init__(
        self,
        plugin_security_manager: PluginSecurityManager,
        subscription_auth_adapter: SubscriptionAuthAdapter
    ):
        """
        Initialize plugin subscription integrator.

        Args:
            plugin_security_manager: Plugin security manager
            subscription_auth_adapter: Subscription auth adapter
        """
        self.plugin_security_manager = plugin_security_manager
        self.subscription_adapter = subscription_auth_adapter
        
        # Register plugin activation hook
        self.plugin_security_manager.register_plugin_activation_hook(self._plugin_activation_hook)

    def _plugin_activation_hook(
        self,
        user_id: str,
        plugin_id: str,
        plugin_metadata: Dict[str, any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Plugin activation hook to check subscription requirements.

        Args:
            user_id: User ID
            plugin_id: Plugin ID
            plugin_metadata: Plugin metadata

        Returns:
            Tuple of (allowed, error_message)
        """
        # Check if plugin requires advanced plugins feature
        if plugin_metadata.get("is_advanced", False):
            has_feature = self.subscription_adapter.check_feature_access(
                user_id=user_id,
                feature=LicenseFeature.ADVANCED_PLUGINS
            )
            
            if not has_feature:
                return False, "This plugin requires the Advanced Plugins feature. Please upgrade your subscription."
                
        # Check if plugin has specific feature requirements
        required_features = plugin_metadata.get("required_features", [])
        for feature_name in required_features:
            try:
                feature = LicenseFeature(feature_name)
                has_feature = self.subscription_adapter.check_feature_access(
                    user_id=user_id,
                    feature=feature
                )
                
                if not has_feature:
                    return False, f"This plugin requires the {feature_name} feature. Please upgrade your subscription."
            except ValueError:
                # Invalid feature name, ignore
                pass
                
        # Track plugin activation in usage
        allowed, message = self.subscription_adapter.track_user_usage(
            user_id=user_id,
            resource_type=ResourceType.PLUGIN_EXECUTION,
            quantity=1,
            metadata={"plugin_id": plugin_id, "action": "activation"}
        )
        
        if not allowed:
            return False, message or "Usage quota exceeded for plugin activations."
            
        # All checks passed
        return True, None

    def track_plugin_usage(
        self,
        user_id: str,
        plugin_id: str,
        action: str,
        quantity: int = 1
    ) -> Tuple[bool, Optional[str]]:
        """
        Track plugin usage for quota purposes.

        Args:
            user_id: User ID
            plugin_id: Plugin ID
            action: Action being performed
            quantity: Usage quantity

        Returns:
            Tuple of (allowed, error_message)
        """
        return self.subscription_adapter.track_user_usage(
            user_id=user_id,
            resource_type=ResourceType.PLUGIN_EXECUTION,
            quantity=quantity,
            metadata={"plugin_id": plugin_id, "action": action}
        )


class SubscriptionIntegrationService:
    """Main service for subscription system integration."""

    def __init__(
        self,
        auth_manager: AuthManager,
        rbac_manager: RBACManager,
        identity_manager: IdentityManager,
        plugin_security_manager: PluginSecurityManager,
        subscription_service: SubscriptionService,
        license_validator: LicenseValidator,
        usage_service: UsageService
    ):
        """
        Initialize subscription integration service.

        Args:
            auth_manager: Authentication manager
            rbac_manager: RBAC manager
            identity_manager: Identity manager
            plugin_security_manager: Plugin security manager
            subscription_service: Subscription service
            license_validator: License validator
            usage_service: Usage service
        """
        # Create subscription auth adapter
        self.subscription_adapter = SubscriptionAuthAdapter(
            auth_manager=auth_manager,
            rbac_manager=rbac_manager,
            identity_manager=identity_manager,
            subscription_service=subscription_service,
            license_validator=license_validator,
            usage_service=usage_service
        )
        
        # Create middleware and integrators
        self.auth_middleware = AuthSubscriptionMiddleware(
            auth_manager=auth_manager,
            subscription_auth_adapter=self.subscription_adapter
        )
        
        self.feature_integrator = FeaturePermissionIntegrator(
            rbac_manager=rbac_manager,
            subscription_auth_adapter=self.subscription_adapter
        )
        
        self.plugin_integrator = PluginSubscriptionIntegrator(
            plugin_security_manager=plugin_security_manager,
            subscription_auth_adapter=self.subscription_adapter
        )

    def initialize(self) -> None:
        """Initialize all integration components."""
        # Nothing to do here - components are initialized in constructor
        pass

    def get_subscription_adapter(self) -> SubscriptionAuthAdapter:
        """
        Get the subscription auth adapter.

        Returns:
            Subscription auth adapter
        """
        return self.subscription_adapter

    def get_auth_middleware(self) -> AuthSubscriptionMiddleware:
        """
        Get the auth subscription middleware.

        Returns:
            Auth subscription middleware
        """
        return self.auth_middleware

    def get_feature_integrator(self) -> FeaturePermissionIntegrator:
        """
        Get the feature permission integrator.

        Returns:
            Feature permission integrator
        """
        return self.feature_integrator

    def get_plugin_integrator(self) -> PluginSubscriptionIntegrator:
        """
        Get the plugin subscription integrator.

        Returns:
            Plugin subscription integrator
        """
        return self.plugin_integrator


if __name__ == "__main__":
    # Example usage
    # This would typically be set up in an application initialization module
    
    # Create auth components
    auth_manager = AuthManager()
    rbac_manager = RBACManager()
    identity_manager = IdentityManager()
    plugin_security_manager = PluginSecurityManager()
    
    # Create subscription components
    subscription_manager = SubscriptionManager("subscription_data")
    subscription_repository = SubscriptionRepository("subscription_data")
    feature_gate = FeatureGate(subscription_manager, subscription_repository)
    subscription_service = SubscriptionService(
        subscription_manager, 
        subscription_repository, 
        feature_gate
    )
    
    # Create license validator
    from subscription.core.license_generator import LicenseSignature
    signature_handler = LicenseSignature(public_key_path="public_key.pem")
    license_validator = LicenseValidator(signature_handler)
    
    # Create usage components
    quota_manager = QuotaManager("usage_data")
    usage_tracker = UsageTracker("usage_data")
    quota_enforcer = QuotaEnforcer(quota_manager, usage_tracker, subscription_service)
    usage_analytics = UsageAnalytics(usage_tracker)
    usage_service = UsageService(quota_manager, usage_tracker, quota_enforcer, usage_analytics)
    
    # Create integration service
    integration_service = SubscriptionIntegrationService(
        auth_manager=auth_manager,
        rbac_manager=rbac_manager,
        identity_manager=identity_manager,
        plugin_security_manager=plugin_security_manager,
        subscription_service=subscription_service,
        license_validator=license_validator,
        usage_service=usage_service
    )
    
    # Initialize integration
    integration_service.initialize()
    
    # Now the subscription system is integrated with authentication and authorization
    print("Subscription system integration complete")
