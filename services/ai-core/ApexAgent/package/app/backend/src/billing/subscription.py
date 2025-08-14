"""
Subscription management module for ApexAgent.

This module handles subscription tier management, user subscription status,
and subscription-related operations.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any


class SubscriptionTier(Enum):
    """Enumeration of available subscription tiers."""
    BASIC = "basic"
    PRO = "pro"
    EXPERT = "expert"
    ENTERPRISE = "enterprise"


class LicenseType(Enum):
    """Enumeration of available license types for enterprise subscriptions."""
    PER_SEAT = "per_seat"
    PER_DEVICE = "per_device"
    SITE_LICENSE = "site_license"


class InstitutionType(Enum):
    """Enumeration of special institution types with custom pricing."""
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"


class SubscriptionManager:
    """Manages user subscriptions and related operations."""

    def __init__(self, database_connector):
        """Initialize the subscription manager.
        
        Args:
            database_connector: Connection to the subscription database
        """
        self.db = database_connector
        self._initialize_tier_config()
    
    def _initialize_tier_config(self):
        """Initialize the configuration for subscription tiers."""
        self.tier_config = {
            SubscriptionTier.BASIC: {
                "price_monthly": 24.99,
                "price_annual": 249.90,  # ~17% discount
                "credits_monthly": 2000,
                "max_standard_models": 2,
                "max_advanced_models": 0,
                "features": ["core_conversation", "basic_file_system", "standard_models", 
                             "document_creation", "document_editing"]
            },
            SubscriptionTier.PRO: {
                "price_monthly": 89.99,
                "price_annual": 899.90,  # ~17% discount
                "credits_monthly": 5000,
                "max_standard_models": 3,
                "max_advanced_models": 2,
                "features": ["full_conversation", "file_system_integration", 
                             "document_creation", "document_editing", "system_integration",
                             "enhanced_stability", "extended_context", "priority_access",
                             "beta_features"]
            },
            SubscriptionTier.EXPERT: {
                "price_monthly": 149.99,
                "price_annual": 1499.90,  # ~17% discount
                "credits_monthly": 15000,
                "max_standard_models": -1,  # Unlimited
                "max_advanced_models": -1,  # Unlimited
                "features": ["custom_plugins", "advanced_analytics", "api_access", 
                             "priority_support", "early_access", "high_effort_mode",
                             "document_creation", "document_editing", "system_integration",
                             "enhanced_stability", "extended_context", "priority_access"]
            },
            SubscriptionTier.ENTERPRISE: {
                "price_monthly": None,  # Custom pricing
                "price_annual": None,  # Custom pricing
                "credits_monthly": None,  # Custom allocation
                "max_standard_models": -1,  # Unlimited
                "max_advanced_models": -1,  # Unlimited
                "features": ["all_models", "custom_deployment", "advanced_security",
                             "account_management", "custom_integrations", "team_collaboration",
                             "admin_dashboard", "sso_integration", "compliance_features",
                             "document_creation", "document_editing", "system_integration"]
            }
        }
        
        # Enterprise pricing for per-seat licensing
        self.enterprise_seat_pricing = {
            "small": {"min_users": 5, "max_users": 20, "price_per_user": 79.0},
            "medium": {"min_users": 21, "max_users": 100, "price_per_user": 69.0},
            "large": {"min_users": 101, "max_users": 500, "price_per_user": 59.0},
            "enterprise": {"min_users": 501, "max_users": None, "price_per_user": None}  # Custom pricing
        }
        
        # Enterprise pricing for per-device licensing
        self.enterprise_device_pricing = {
            "standard": 129.0,
            "high_usage": 189.0,
            "shared": 259.0
        }
        
        # Site license pricing for educational/healthcare institutions
        self.site_license_pricing = {
            "small": {"max_users": 500, "annual_price": 18000.0},
            "medium": {"min_users": 501, "max_users": 2000, "annual_price": 39000.0},
            "large": {"min_users": 2001, "max_users": 10000, "annual_price": 79000.0},
            "enterprise": {"min_users": 10001, "max_users": None, "annual_price": None}  # Custom pricing
        }
        
        # Discount rates for special institutions
        self.institution_discounts = {
            InstitutionType.EDUCATION: 0.35,  # 35% discount
            InstitutionType.HEALTHCARE: 0.20,  # 20% discount
            InstitutionType.NONPROFIT: 0.25,  # 25% discount
            InstitutionType.GOVERNMENT: 0.15,  # 15% discount
            InstitutionType.CORPORATE: 0.0     # No default discount
        }
        
        # User-provided API key pricing
        self.user_api_key_pricing = {
            SubscriptionTier.BASIC: 19.99,
            SubscriptionTier.PRO: 49.99,
            SubscriptionTier.EXPERT: 99.99,
            SubscriptionTier.ENTERPRISE: None  # Custom pricing
        }
        
        # Credit extension pricing
        self.credit_extension_pricing = {
            "pay_as_you_go": 0.018,  # Per credit
            "credit_pack": {"credits": 1000, "price": 14.0},  # 22% savings
            "enterprise_bulk": None  # Custom pricing
        }

    def create_subscription(self, user_id: str, tier: SubscriptionTier, 
                           payment_method_id: str, is_annual: bool = False,
                           user_api_keys: bool = False) -> Dict[str, Any]:
        """Create a new subscription for a user.
        
        Args:
            user_id: Unique identifier for the user
            tier: Subscription tier to create
            payment_method_id: ID of the payment method to use
            is_annual: Whether this is an annual subscription
            user_api_keys: Whether the user is providing their own API keys
            
        Returns:
            Dictionary with subscription details
        """
        # Calculate price based on tier, billing cycle, and API key option
        price = self._calculate_subscription_price(tier, is_annual, user_api_keys)
        
        # Calculate expiration date
        now = datetime.now()
        expiration = now + timedelta(days=365 if is_annual else 30)
        
        # Create subscription record
        subscription_data = {
            "user_id": user_id,
            "tier": tier.value,
            "created_at": now,
            "expires_at": expiration,
            "is_annual": is_annual,
            "user_api_keys": user_api_keys,
            "payment_method_id": payment_method_id,
            "status": "active",
            "price": price,
            "credits_remaining": self.tier_config[tier]["credits_monthly"],
            "auto_renew": True
        }
        
        # Store in database
        subscription_id = self.db.insert_subscription(subscription_data)
        
        # Return the created subscription with ID
        subscription_data["id"] = subscription_id
        return subscription_data
    
    def create_enterprise_subscription(self, organization_id: str, license_type: LicenseType,
                                      institution_type: Optional[InstitutionType] = None,
                                      seats: Optional[int] = None,
                                      devices: Optional[int] = None,
                                      device_type: Optional[str] = None,
                                      potential_users: Optional[int] = None) -> Dict[str, Any]:
        """Create an enterprise subscription.
        
        Args:
            organization_id: Unique identifier for the organization
            license_type: Type of licensing for this subscription
            institution_type: Type of institution for special pricing
            seats: Number of user seats (for per-seat licensing)
            devices: Number of devices (for per-device licensing)
            device_type: Type of device deployment (for per-device licensing)
            potential_users: Number of potential users (for site licensing)
            
        Returns:
            Dictionary with subscription details
        """
        # Calculate price based on license type and parameters
        if license_type == LicenseType.PER_SEAT and seats:
            price = self._calculate_per_seat_price(seats, institution_type)
            quantity = seats
        elif license_type == LicenseType.PER_DEVICE and devices and device_type:
            price = self._calculate_per_device_price(devices, device_type)
            quantity = devices
        elif license_type == LicenseType.SITE_LICENSE and potential_users:
            price = self._calculate_site_license_price(potential_users, institution_type)
            quantity = potential_users
        else:
            raise ValueError("Invalid parameters for enterprise subscription")
        
        # Create subscription record
        now = datetime.now()
        expiration = now + timedelta(days=365)  # Enterprise is always annual
        
        subscription_data = {
            "organization_id": organization_id,
            "tier": SubscriptionTier.ENTERPRISE.value,
            "license_type": license_type.value,
            "created_at": now,
            "expires_at": expiration,
            "institution_type": institution_type.value if institution_type else None,
            "quantity": quantity,
            "price": price,
            "status": "active",
            "credits_allocated": self._calculate_enterprise_credits(license_type, quantity),
            "auto_renew": True
        }
        
        # Store in database
        subscription_id = self.db.insert_enterprise_subscription(subscription_data)
        
        # Return the created subscription with ID
        subscription_data["id"] = subscription_id
        return subscription_data
    
    def get_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the current subscription for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with subscription details or None if no active subscription
        """
        return self.db.get_active_subscription(user_id)
    
    def get_enterprise_subscription(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get the current enterprise subscription.
        
        Args:
            organization_id: Unique identifier for the organization
            
        Returns:
            Dictionary with subscription details or None if no active subscription
        """
        return self.db.get_active_enterprise_subscription(organization_id)
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription.
        
        Args:
            subscription_id: Unique identifier for the subscription
            
        Returns:
            True if successful, False otherwise
        """
        return self.db.update_subscription(subscription_id, {"status": "cancelled"})
    
    def update_subscription_tier(self, subscription_id: str, new_tier: SubscriptionTier) -> Dict[str, Any]:
        """Update the tier of an existing subscription.
        
        Args:
            subscription_id: Unique identifier for the subscription
            new_tier: New subscription tier
            
        Returns:
            Updated subscription details
        """
        subscription = self.db.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        # Calculate new price
        is_annual = subscription.get("is_annual", False)
        user_api_keys = subscription.get("user_api_keys", False)
        new_price = self._calculate_subscription_price(new_tier, is_annual, user_api_keys)
        
        # Update subscription
        updates = {
            "tier": new_tier.value,
            "price": new_price,
            "credits_remaining": self.tier_config[new_tier]["credits_monthly"]
        }
        
        self.db.update_subscription(subscription_id, updates)
        
        # Return updated subscription
        return self.db.get_subscription(subscription_id)
    
    def add_credits(self, subscription_id: str, credits: int, payment_method_id: str) -> Dict[str, Any]:
        """Add additional credits to a subscription.
        
        Args:
            subscription_id: Unique identifier for the subscription
            credits: Number of credits to add
            payment_method_id: ID of the payment method to use
            
        Returns:
            Updated subscription details
        """
        subscription = self.db.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        # Calculate price for additional credits
        price = self._calculate_credit_price(credits)
        
        # Process payment (would integrate with payment processor)
        # payment_successful = self._process_payment(payment_method_id, price)
        payment_successful = True  # Placeholder
        
        if payment_successful:
            # Update credits in database
            current_credits = subscription.get("credits_remaining", 0)
            new_credits = current_credits + credits
            
            self.db.update_subscription(subscription_id, {"credits_remaining": new_credits})
            
            # Log credit purchase
            self.db.log_credit_purchase({
                "subscription_id": subscription_id,
                "credits_purchased": credits,
                "price": price,
                "timestamp": datetime.now()
            })
            
            # Return updated subscription
            return self.db.get_subscription(subscription_id)
        else:
            raise ValueError("Payment processing failed")
    
    def check_feature_access(self, user_id: str, feature: str) -> bool:
        """Check if a user has access to a specific feature.
        
        Args:
            user_id: Unique identifier for the user
            feature: Feature to check access for
            
        Returns:
            True if user has access, False otherwise
        """
        subscription = self.get_subscription(user_id)
        if not subscription or subscription["status"] != "active":
            return False
        
        tier = SubscriptionTier(subscription["tier"])
        return feature in self.tier_config[tier]["features"]
    
    def deduct_credits(self, user_id: str, credits: int, operation: str) -> bool:
        """Deduct credits from a user's subscription.
        
        Args:
            user_id: Unique identifier for the user
            credits: Number of credits to deduct
            operation: Description of the operation using credits
            
        Returns:
            True if successful, False if insufficient credits
        """
        subscription = self.get_subscription(user_id)
        if not subscription or subscription["status"] != "active":
            return False
        
        current_credits = subscription.get("credits_remaining", 0)
        if current_credits < credits:
            return False
        
        new_credits = current_credits - credits
        self.db.update_subscription(subscription["id"], {"credits_remaining": new_credits})
        
        # Log credit usage
        self.db.log_credit_usage({
            "subscription_id": subscription["id"],
            "credits_used": credits,
            "operation": operation,
            "timestamp": datetime.now()
        })
        
        return True
    
    def _calculate_subscription_price(self, tier: SubscriptionTier, is_annual: bool, 
                                     user_api_keys: bool) -> float:
        """Calculate the price for a subscription.
        
        Args:
            tier: Subscription tier
            is_annual: Whether this is an annual subscription
            user_api_keys: Whether the user is providing their own API keys
            
        Returns:
            Calculated price
        """
        if tier == SubscriptionTier.ENTERPRISE:
            raise ValueError("Enterprise pricing requires custom calculation")
        
        # Get base price
        if user_api_keys:
            base_price = self.user_api_key_pricing[tier]
        else:
            base_price = self.tier_config[tier]["price_monthly"]
        
        # Apply annual discount if applicable
        if is_annual:
            return base_price * 12 * 0.83  # 17% discount
        
        return base_price
    
    def _calculate_per_seat_price(self, seats: int, institution_type: Optional[InstitutionType] = None) -> float:
        """Calculate the price for per-seat licensing.
        
        Args:
            seats: Number of seats
            institution_type: Type of institution for special pricing
            
        Returns:
            Calculated price
        """
        # Determine price tier based on number of seats
        if seats <= 20:
            tier = "small"
        elif seats <= 100:
            tier = "medium"
        elif seats <= 500:
            tier = "large"
        else:
            tier = "enterprise"
        
        if tier == "enterprise":
            raise ValueError("Enterprise tier requires custom pricing")
        
        # Get base price per seat
        price_per_seat = self.enterprise_seat_pricing[tier]["price_per_user"]
        
        # Apply institution discount if applicable
        if institution_type:
            discount = self.institution_discounts.get(institution_type, 0)
            price_per_seat = price_per_seat * (1 - discount)
        
        return price_per_seat * seats
    
    def _calculate_per_device_price(self, devices: int, device_type: str) -> float:
        """Calculate the price for per-device licensing.
        
        Args:
            devices: Number of devices
            device_type: Type of device deployment
            
        Returns:
            Calculated price
        """
        if device_type not in self.enterprise_device_pricing:
            raise ValueError(f"Unknown device type: {device_type}")
        
        price_per_device = self.enterprise_device_pricing[device_type]
        return price_per_device * devices
    
    def _calculate_site_license_price(self, potential_users: int, 
                                     institution_type: Optional[InstitutionType] = None) -> float:
        """Calculate the price for site licensing.
        
        Args:
            potential_users: Number of potential users
            institution_type: Type of institution for special pricing
            
        Returns:
            Calculated price
        """
        # Determine price tier based on number of potential users
        if potential_users <= 500:
            tier = "small"
        elif potential_users <= 2000:
            tier = "medium"
        elif potential_users <= 10000:
            tier = "large"
        else:
            tier = "enterprise"
        
        if tier == "enterprise":
            raise ValueError("Enterprise tier requires custom pricing")
        
        # Get base price
        base_price = self.site_license_pricing[tier]["annual_price"]
        
        # Apply institution discount if applicable
        if institution_type:
            discount = self.institution_discounts.get(institution_type, 0)
            base_price = base_price * (1 - discount)
        
        return base_price
    
    def _calculate_enterprise_credits(self, license_type: LicenseType, quantity: int) -> int:
        """Calculate the credit allocation for an enterprise subscription.
        
        Args:
            license_type: Type of licensing
            quantity: Number of seats, devices, or potential users
            
        Returns:
            Calculated credit allocation
        """
        if license_type == LicenseType.PER_SEAT:
            # 10,000 credits per seat
            return quantity * 10000
        elif license_type == LicenseType.PER_DEVICE:
            # 7,500 credits per device
            return quantity * 7500
        elif license_type == LicenseType.SITE_LICENSE:
            # Base allocation plus per-user allocation
            base_allocation = 500000
            per_user_allocation = 1000
            return base_allocation + (quantity * per_user_allocation)
        else:
            raise ValueError(f"Unknown license type: {license_type}")
    
    def _calculate_credit_price(self, credits: int) -> float:
        """Calculate the price for additional credits.
        
        Args:
            credits: Number of credits to purchase
            
        Returns:
            Calculated price
        """
        # Check if credit pack is more economical
        credit_pack = self.credit_extension_pricing["credit_pack"]
        if credits % credit_pack["credits"] == 0:
            # Exact multiple of credit pack
            packs = credits // credit_pack["credits"]
            return packs * credit_pack["price"]
        
        # Otherwise use pay-as-you-go pricing
        return credits * self.credit_extension_pricing["pay_as_you_go"]
