"""
Subscription Tier Management module for ApexAgent Subscription and Licensing System.

This module provides functionality for defining subscription tiers, managing feature
access based on subscription levels, and controlling feature gating.
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union

from subscription.core.license_generator import LicenseFeature, LicenseType
from subscription.core.license_validator import LicenseValidator


class SubscriptionTier(Enum):
    """Enumeration of subscription tiers."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class SubscriptionPeriod(Enum):
    """Enumeration of subscription periods."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    BIENNIAL = "biennial"
    CUSTOM = "custom"


class SubscriptionStatus(Enum):
    """Enumeration of subscription statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    GRACE_PERIOD = "grace_period"


class TierDefinition:
    """Class representing a subscription tier definition."""

    def __init__(
        self,
        tier_id: str,
        name: str,
        description: str,
        features: List[LicenseFeature],
        price_monthly: float,
        price_annual: float,
        max_users: Optional[int] = None,
        custom_attributes: Optional[Dict[str, str]] = None
    ):
        """
        Initialize tier definition.

        Args:
            tier_id: Unique identifier for the tier
            name: Display name for the tier
            description: Description of the tier
            features: List of features included in the tier
            price_monthly: Monthly price for the tier
            price_annual: Annual price for the tier
            max_users: Maximum number of users allowed (None for unlimited)
            custom_attributes: Additional custom attributes for the tier
        """
        self.tier_id = tier_id
        self.name = name
        self.description = description
        self.features = features
        self.price_monthly = price_monthly
        self.price_annual = price_annual
        self.max_users = max_users
        self.custom_attributes = custom_attributes or {}

    def to_dict(self) -> Dict[str, Union[str, float, int, List[str], Dict[str, str]]]:
        """
        Convert tier definition to dictionary.

        Returns:
            Dictionary representation of the tier definition
        """
        result = {
            "tier_id": self.tier_id,
            "name": self.name,
            "description": self.description,
            "features": [feature.value for feature in self.features],
            "price_monthly": self.price_monthly,
            "price_annual": self.price_annual,
            "custom_attributes": self.custom_attributes
        }

        if self.max_users is not None:
            result["max_users"] = self.max_users

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, float, int, List[str], Dict[str, str]]]) -> 'TierDefinition':
        """
        Create tier definition from dictionary.

        Args:
            data: Dictionary representation of tier definition

        Returns:
            TierDefinition instance
        """
        features = [LicenseFeature(feature) for feature in data.get("features", [])]

        return cls(
            tier_id=data["tier_id"],
            name=data["name"],
            description=data["description"],
            features=features,
            price_monthly=data["price_monthly"],
            price_annual=data["price_annual"],
            max_users=data.get("max_users"),
            custom_attributes=data.get("custom_attributes", {})
        )

    def has_feature(self, feature: LicenseFeature) -> bool:
        """
        Check if tier includes a specific feature.

        Args:
            feature: Feature to check

        Returns:
            True if tier includes the feature, False otherwise
        """
        return feature in self.features


class SubscriptionManager:
    """Class for managing subscription tiers and definitions."""

    def __init__(self, storage_path: str):
        """
        Initialize subscription manager.

        Args:
            storage_path: Path to store subscription data
        """
        self.storage_path = storage_path
        self.tiers: Dict[str, TierDefinition] = {}
        self._load_tiers()

    def _get_tiers_file(self) -> str:
        """
        Get path to tiers definition file.

        Returns:
            Path to tiers file
        """
        return os.path.join(self.storage_path, "subscription_tiers.json")

    def _load_tiers(self) -> None:
        """Load tier definitions from storage."""
        os.makedirs(self.storage_path, exist_ok=True)
        tiers_file = self._get_tiers_file()
        
        if not os.path.exists(tiers_file):
            # Create default tiers if file doesn't exist
            self._create_default_tiers()
            return

        try:
            with open(tiers_file, "r") as f:
                tiers_data = json.load(f)
                
            for tier_data in tiers_data:
                tier = TierDefinition.from_dict(tier_data)
                self.tiers[tier.tier_id] = tier
        except Exception as e:
            print(f"Failed to load subscription tiers: {str(e)}")
            # Create default tiers as fallback
            self._create_default_tiers()

    def _save_tiers(self) -> None:
        """Save tier definitions to storage."""
        tiers_file = self._get_tiers_file()
        
        try:
            tiers_data = [tier.to_dict() for tier in self.tiers.values()]
            with open(tiers_file, "w") as f:
                json.dump(tiers_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save subscription tiers: {str(e)}")

    def _create_default_tiers(self) -> None:
        """Create default subscription tiers."""
        # Free tier
        free_tier = TierDefinition(
            tier_id="free",
            name="Free",
            description="Basic functionality with limited features",
            features=[
                LicenseFeature.CORE
            ],
            price_monthly=0.0,
            price_annual=0.0,
            max_users=1
        )
        
        # Basic tier
        basic_tier = TierDefinition(
            tier_id="basic",
            name="Basic",
            description="Essential features for individual users",
            features=[
                LicenseFeature.CORE,
                LicenseFeature.ADVANCED_PLUGINS
            ],
            price_monthly=9.99,
            price_annual=99.99,
            max_users=1
        )
        
        # Professional tier
        pro_tier = TierDefinition(
            tier_id="professional",
            name="Professional",
            description="Advanced features for power users",
            features=[
                LicenseFeature.CORE,
                LicenseFeature.ADVANCED_PLUGINS,
                LicenseFeature.API_ACCESS,
                LicenseFeature.PRIORITY_SUPPORT,
                LicenseFeature.OFFLINE_MODE
            ],
            price_monthly=29.99,
            price_annual=299.99,
            max_users=5
        )
        
        # Enterprise tier
        enterprise_tier = TierDefinition(
            tier_id="enterprise",
            name="Enterprise",
            description="Complete solution for organizations",
            features=[
                LicenseFeature.CORE,
                LicenseFeature.ADVANCED_PLUGINS,
                LicenseFeature.API_ACCESS,
                LicenseFeature.PRIORITY_SUPPORT,
                LicenseFeature.OFFLINE_MODE,
                LicenseFeature.MULTI_USER,
                LicenseFeature.ENTERPRISE_INTEGRATION,
                LicenseFeature.WHITE_LABEL,
                LicenseFeature.CUSTOM_BRANDING,
                LicenseFeature.ADVANCED_ANALYTICS
            ],
            price_monthly=99.99,
            price_annual=999.99,
            max_users=None  # Unlimited
        )
        
        # Add tiers to manager
        self.tiers = {
            "free": free_tier,
            "basic": basic_tier,
            "professional": pro_tier,
            "enterprise": enterprise_tier
        }
        
        # Save default tiers
        self._save_tiers()

    def get_tier(self, tier_id: str) -> Optional[TierDefinition]:
        """
        Get tier definition by ID.

        Args:
            tier_id: Tier ID to retrieve

        Returns:
            TierDefinition or None if not found
        """
        return self.tiers.get(tier_id)

    def get_all_tiers(self) -> List[TierDefinition]:
        """
        Get all tier definitions.

        Returns:
            List of all tier definitions
        """
        return list(self.tiers.values())

    def add_tier(self, tier: TierDefinition) -> bool:
        """
        Add a new tier definition.

        Args:
            tier: Tier definition to add

        Returns:
            True if successful, False otherwise
        """
        if tier.tier_id in self.tiers:
            return False
            
        self.tiers[tier.tier_id] = tier
        self._save_tiers()
        return True

    def update_tier(self, tier: TierDefinition) -> bool:
        """
        Update an existing tier definition.

        Args:
            tier: Updated tier definition

        Returns:
            True if successful, False if tier not found
        """
        if tier.tier_id not in self.tiers:
            return False
            
        self.tiers[tier.tier_id] = tier
        self._save_tiers()
        return True

    def delete_tier(self, tier_id: str) -> bool:
        """
        Delete a tier definition.

        Args:
            tier_id: ID of tier to delete

        Returns:
            True if successful, False if tier not found
        """
        if tier_id not in self.tiers:
            return False
            
        del self.tiers[tier_id]
        self._save_tiers()
        return True

    def get_tier_for_feature(self, feature: LicenseFeature) -> List[TierDefinition]:
        """
        Get all tiers that include a specific feature.

        Args:
            feature: Feature to check

        Returns:
            List of tiers that include the feature
        """
        return [tier for tier in self.tiers.values() if tier.has_feature(feature)]

    def get_tier_comparison(self) -> Dict[str, Dict[str, Union[str, bool, float]]]:
        """
        Generate a comparison of all tiers.

        Returns:
            Dictionary with tier comparison data
        """
        # Get all unique features across all tiers
        all_features = set()
        for tier in self.tiers.values():
            all_features.update(tier.features)
            
        # Create comparison data
        comparison = {}
        for tier in self.tiers.values():
            tier_data = {
                "name": tier.name,
                "description": tier.description,
                "price_monthly": tier.price_monthly,
                "price_annual": tier.price_annual,
                "max_users": tier.max_users
            }
            
            # Add feature availability
            for feature in all_features:
                tier_data[feature.value] = feature in tier.features
                
            comparison[tier.tier_id] = tier_data
            
        return comparison


class Subscription:
    """Class representing a user subscription."""

    def __init__(
        self,
        subscription_id: str,
        customer_id: str,
        tier_id: str,
        status: SubscriptionStatus,
        start_date: datetime,
        end_date: Optional[datetime],
        payment_method: Optional[str] = None,
        auto_renew: bool = True,
        license_keys: Optional[List[str]] = None,
        custom_attributes: Optional[Dict[str, str]] = None
    ):
        """
        Initialize subscription.

        Args:
            subscription_id: Unique identifier for the subscription
            customer_id: Identifier for the customer
            tier_id: Identifier for the subscription tier
            status: Status of the subscription
            start_date: Date when the subscription starts
            end_date: Date when the subscription ends (None for lifetime)
            payment_method: Identifier for the payment method
            auto_renew: Whether the subscription should auto-renew
            license_keys: List of license keys associated with the subscription
            custom_attributes: Additional custom attributes for the subscription
        """
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.tier_id = tier_id
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.payment_method = payment_method
        self.auto_renew = auto_renew
        self.license_keys = license_keys or []
        self.custom_attributes = custom_attributes or {}

    def to_dict(self) -> Dict[str, Union[str, bool, List[str], Dict[str, str]]]:
        """
        Convert subscription to dictionary.

        Returns:
            Dictionary representation of the subscription
        """
        result = {
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "tier_id": self.tier_id,
            "status": self.status.value,
            "start_date": self.start_date.isoformat(),
            "auto_renew": self.auto_renew,
            "license_keys": self.license_keys,
            "custom_attributes": self.custom_attributes
        }

        if self.end_date:
            result["end_date"] = self.end_date.isoformat()

        if self.payment_method:
            result["payment_method"] = self.payment_method

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, bool, List[str], Dict[str, str]]]) -> 'Subscription':
        """
        Create subscription from dictionary.

        Args:
            data: Dictionary representation of subscription

        Returns:
            Subscription instance
        """
        start_date = datetime.fromisoformat(data["start_date"])
        end_date = None
        if "end_date" in data and data["end_date"]:
            end_date = datetime.fromisoformat(data["end_date"])

        return cls(
            subscription_id=data["subscription_id"],
            customer_id=data["customer_id"],
            tier_id=data["tier_id"],
            status=SubscriptionStatus(data["status"]),
            start_date=start_date,
            end_date=end_date,
            payment_method=data.get("payment_method"),
            auto_renew=data.get("auto_renew", True),
            license_keys=data.get("license_keys", []),
            custom_attributes=data.get("custom_attributes", {})
        )

    def is_active(self) -> bool:
        """
        Check if subscription is active.

        Returns:
            True if subscription is active, False otherwise
        """
        if self.status != SubscriptionStatus.ACTIVE and self.status != SubscriptionStatus.TRIAL:
            return False

        current_date = datetime.now()
        if self.end_date and current_date > self.end_date:
            return False

        return True


class SubscriptionRepository:
    """Class for storing and retrieving subscriptions."""

    def __init__(self, storage_path: str):
        """
        Initialize subscription repository.

        Args:
            storage_path: Path to store subscription data
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def _get_subscription_file(self, subscription_id: str) -> str:
        """
        Get path to subscription file.

        Args:
            subscription_id: Subscription ID

        Returns:
            Path to subscription file
        """
        return os.path.join(self.storage_path, f"subscription_{subscription_id}.json")

    def _get_customer_index_file(self) -> str:
        """
        Get path to customer index file.

        Returns:
            Path to customer index file
        """
        return os.path.join(self.storage_path, "customer_index.json")

    def _update_customer_index(self, customer_id: str, subscription_id: str, remove: bool = False) -> None:
        """
        Update customer index with subscription mapping.

        Args:
            customer_id: Customer ID
            subscription_id: Subscription ID
            remove: Whether to remove the mapping
        """
        index_file = self._get_customer_index_file()
        customer_index = {}
        
        # Load existing index if it exists
        if os.path.exists(index_file):
            try:
                with open(index_file, "r") as f:
                    customer_index = json.load(f)
            except Exception:
                customer_index = {}
        
        # Update index
        if customer_id not in customer_index:
            customer_index[customer_id] = []
            
        if remove:
            if subscription_id in customer_index[customer_id]:
                customer_index[customer_id].remove(subscription_id)
        else:
            if subscription_id not in customer_index[customer_id]:
                customer_index[customer_id].append(subscription_id)
        
        # Save updated index
        with open(index_file, "w") as f:
            json.dump(customer_index, f)

    def save(self, subscription: Subscription) -> bool:
        """
        Save a subscription.

        Args:
            subscription: Subscription to save

        Returns:
            True if successful, False otherwise
        """
        try:
            subscription_file = self._get_subscription_file(subscription.subscription_id)
            
            with open(subscription_file, "w") as f:
                json.dump(subscription.to_dict(), f, indent=2)
                
            # Update customer index
            self._update_customer_index(subscription.customer_id, subscription.subscription_id)
            
            return True
        except Exception as e:
            print(f"Failed to save subscription: {str(e)}")
            return False

    def get(self, subscription_id: str) -> Optional[Subscription]:
        """
        Get a subscription by ID.

        Args:
            subscription_id: Subscription ID to retrieve

        Returns:
            Subscription or None if not found
        """
        subscription_file = self._get_subscription_file(subscription_id)
        
        if not os.path.exists(subscription_file):
            return None
            
        try:
            with open(subscription_file, "r") as f:
                subscription_data = json.load(f)
                
            return Subscription.from_dict(subscription_data)
        except Exception as e:
            print(f"Failed to load subscription {subscription_id}: {str(e)}")
            return None

    def delete(self, subscription_id: str) -> bool:
        """
        Delete a subscription.

        Args:
            subscription_id: Subscription ID to delete

        Returns:
            True if successful, False otherwise
        """
        subscription_file = self._get_subscription_file(subscription_id)
        
        if not os.path.exists(subscription_file):
            return False
            
        try:
            # Get customer ID before deleting
            subscription = self.get(subscription_id)
            if subscription:
                customer_id = subscription.customer_id
                
                # Delete subscription file
                os.remove(subscription_file)
                
                # Update customer index
                self._update_customer_index(customer_id, subscription_id, remove=True)
                
                return True
            return False
        except Exception as e:
            print(f"Failed to delete subscription {subscription_id}: {str(e)}")
            return False

    def get_by_customer(self, customer_id: str) -> List[Subscription]:
        """
        Get all subscriptions for a customer.

        Args:
            customer_id: Customer ID to retrieve subscriptions for

        Returns:
            List of subscriptions for the customer
        """
        index_file = self._get_customer_index_file()
        
        if not os.path.exists(index_file):
            return []
            
        try:
            with open(index_file, "r") as f:
                customer_index = json.load(f)
                
            if customer_id not in customer_index:
                return []
                
            subscriptions = []
            for subscription_id in customer_index[customer_id]:
                subscription = self.get(subscription_id)
                if subscription:
                    subscriptions.append(subscription)
                    
            return subscriptions
        except Exception as e:
            print(f"Failed to get subscriptions for customer {customer_id}: {str(e)}")
            return []

    def get_all(self) -> List[Subscription]:
        """
        Get all subscriptions.

        Returns:
            List of all subscriptions
        """
        subscriptions = []
        
        try:
            for filename in os.listdir(self.storage_path):
                if filename.startswith("subscription_") and filename.endswith(".json"):
                    subscription_id = filename[12:-5]  # Extract ID from filename
                    subscription = self.get(subscription_id)
                    if subscription:
                        subscriptions.append(subscription)
                        
            return subscriptions
        except Exception as e:
            print(f"Failed to get all subscriptions: {str(e)}")
            return []

    def get_by_status(self, status: SubscriptionStatus) -> List[Subscription]:
        """
        Get subscriptions by status.

        Args:
            status: Status to filter by

        Returns:
            List of subscriptions with the specified status
        """
        return [sub for sub in self.get_all() if sub.status == status]

    def get_expiring_soon(self, days: int = 30) -> List[Subscription]:
        """
        Get subscriptions expiring within the specified number of days.

        Args:
            days: Number of days to check for expiration

        Returns:
            List of subscriptions expiring soon
        """
        current_date = datetime.now()
        expiry_threshold = current_date.replace(hour=23, minute=59, second=59)
        expiry_threshold = expiry_threshold.replace(day=expiry_threshold.day + days)
        
        return [
            sub for sub in self.get_all() 
            if sub.end_date and current_date <= sub.end_date <= expiry_threshold
        ]


class FeatureGate:
    """Class for controlling access to features based on subscriptions."""

    def __init__(
        self,
        subscription_manager: SubscriptionManager,
        subscription_repository: SubscriptionRepository,
        license_validator: Optional[LicenseValidator] = None
    ):
        """
        Initialize feature gate.

        Args:
            subscription_manager: Manager for subscription tiers
            subscription_repository: Repository for subscriptions
            license_validator: Validator for license keys
        """
        self.subscription_manager = subscription_manager
        self.subscription_repository = subscription_repository
        self.license_validator = license_validator

    def _get_customer_tier(self, customer_id: str) -> Optional[TierDefinition]:
        """
        Get the highest tier for a customer.

        Args:
            customer_id: Customer ID to check

        Returns:
            Highest tier definition or None if no active subscriptions
        """
        # Get all subscriptions for the customer
        subscriptions = self.subscription_repository.get_by_customer(customer_id)
        
        # Filter active subscriptions
        active_subscriptions = [sub for sub in subscriptions if sub.is_active()]
        
        if not active_subscriptions:
            return None
            
        # Get tier definitions for active subscriptions
        tiers = []
        for subscription in active_subscriptions:
            tier = self.subscription_manager.get_tier(subscription.tier_id)
            if tier:
                tiers.append(tier)
                
        if not tiers:
            return None
            
        # Return tier with the most features
        return max(tiers, key=lambda t: len(t.features))

    def has_feature(self, customer_id: str, feature: LicenseFeature) -> bool:
        """
        Check if a customer has access to a feature.

        Args:
            customer_id: Customer ID to check
            feature: Feature to check access for

        Returns:
            True if customer has access to the feature, False otherwise
        """
        # Get customer's tier
        tier = self._get_customer_tier(customer_id)
        
        # If no tier found, check if there's a valid license with the feature
        if not tier and self.license_validator:
            # Get all subscriptions for the customer
            subscriptions = self.subscription_repository.get_by_customer(customer_id)
            
            # Check each license key
            for subscription in subscriptions:
                for license_key in subscription.license_keys:
                    if self.license_validator.has_feature(license_key, feature):
                        return True
            
            return False
            
        # If tier found, check if it includes the feature
        return tier is not None and tier.has_feature(feature)

    def get_available_features(self, customer_id: str) -> Set[LicenseFeature]:
        """
        Get all features available to a customer.

        Args:
            customer_id: Customer ID to check

        Returns:
            Set of available features
        """
        # Get customer's tier
        tier = self._get_customer_tier(customer_id)
        
        features = set()
        
        # Add features from tier
        if tier:
            features.update(tier.features)
            
        # Add features from licenses if validator is available
        if self.license_validator:
            # Get all subscriptions for the customer
            subscriptions = self.subscription_repository.get_by_customer(customer_id)
            
            # Check each license key
            for subscription in subscriptions:
                for license_key in subscription.license_keys:
                    result = self.license_validator.validate_license_key(license_key)
                    if result.is_valid and result.features:
                        features.update(result.features)
        
        return features

    def check_access(self, customer_id: str, required_features: List[LicenseFeature]) -> Tuple[bool, List[LicenseFeature]]:
        """
        Check if a customer has access to all required features.

        Args:
            customer_id: Customer ID to check
            required_features: List of features required for access

        Returns:
            Tuple of (has_access, missing_features)
        """
        available_features = self.get_available_features(customer_id)
        missing_features = [f for f in required_features if f not in available_features]
        
        return len(missing_features) == 0, missing_features

    def get_upgrade_path(self, customer_id: str, required_feature: LicenseFeature) -> List[TierDefinition]:
        """
        Get possible upgrade paths to access a feature.

        Args:
            customer_id: Customer ID to check
            required_feature: Feature needed

        Returns:
            List of tiers that would provide the feature, sorted by price
        """
        # Get tiers that include the feature
        tiers_with_feature = self.subscription_manager.get_tier_for_feature(required_feature)
        
        # Sort by monthly price
        return sorted(tiers_with_feature, key=lambda t: t.price_monthly)


class SubscriptionService:
    """Main service class for subscription management."""

    def __init__(
        self,
        subscription_manager: SubscriptionManager,
        subscription_repository: SubscriptionRepository,
        feature_gate: FeatureGate
    ):
        """
        Initialize subscription service.

        Args:
            subscription_manager: Manager for subscription tiers
            subscription_repository: Repository for subscriptions
            feature_gate: Gate for feature access control
        """
        self.subscription_manager = subscription_manager
        self.subscription_repository = subscription_repository
        self.feature_gate = feature_gate

    def create_subscription(
        self,
        customer_id: str,
        tier_id: str,
        period: SubscriptionPeriod,
        payment_method: Optional[str] = None,
        auto_renew: bool = True,
        custom_attributes: Optional[Dict[str, str]] = None
    ) -> Optional[Subscription]:
        """
        Create a new subscription.

        Args:
            customer_id: Customer ID
            tier_id: Subscription tier ID
            period: Subscription period
            payment_method: Payment method ID
            auto_renew: Whether to auto-renew
            custom_attributes: Additional custom attributes

        Returns:
            Created subscription or None if failed
        """
        # Verify tier exists
        tier = self.subscription_manager.get_tier(tier_id)
        if not tier:
            return None
            
        # Generate subscription ID
        import uuid
        subscription_id = str(uuid.uuid4())
        
        # Set dates based on period
        start_date = datetime.now()
        end_date = None
        
        if period == SubscriptionPeriod.MONTHLY:
            end_date = start_date.replace(month=start_date.month + 1)
        elif period == SubscriptionPeriod.QUARTERLY:
            end_date = start_date.replace(month=start_date.month + 3)
        elif period == SubscriptionPeriod.ANNUAL:
            end_date = start_date.replace(year=start_date.year + 1)
        elif period == SubscriptionPeriod.BIENNIAL:
            end_date = start_date.replace(year=start_date.year + 2)
        
        # Create subscription
        subscription = Subscription(
            subscription_id=subscription_id,
            customer_id=customer_id,
            tier_id=tier_id,
            status=SubscriptionStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method,
            auto_renew=auto_renew,
            custom_attributes=custom_attributes
        )
        
        # Save subscription
        if self.subscription_repository.save(subscription):
            return subscription
        
        return None

    def update_subscription(
        self,
        subscription_id: str,
        tier_id: Optional[str] = None,
        status: Optional[SubscriptionStatus] = None,
        end_date: Optional[datetime] = None,
        payment_method: Optional[str] = None,
        auto_renew: Optional[bool] = None,
        custom_attributes: Optional[Dict[str, str]] = None
    ) -> Optional[Subscription]:
        """
        Update an existing subscription.

        Args:
            subscription_id: Subscription ID to update
            tier_id: New tier ID
            status: New status
            end_date: New end date
            payment_method: New payment method
            auto_renew: New auto-renew setting
            custom_attributes: New custom attributes

        Returns:
            Updated subscription or None if failed
        """
        # Get existing subscription
        subscription = self.subscription_repository.get(subscription_id)
        if not subscription:
            return None
            
        # Update fields if provided
        if tier_id is not None:
            # Verify tier exists
            tier = self.subscription_manager.get_tier(tier_id)
            if not tier:
                return None
                
            subscription.tier_id = tier_id
            
        if status is not None:
            subscription.status = status
            
        if end_date is not None:
            subscription.end_date = end_date
            
        if payment_method is not None:
            subscription.payment_method = payment_method
            
        if auto_renew is not None:
            subscription.auto_renew = auto_renew
            
        if custom_attributes is not None:
            subscription.custom_attributes = custom_attributes
            
        # Save updated subscription
        if self.subscription_repository.save(subscription):
            return subscription
            
        return None

    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """
        Cancel a subscription.

        Args:
            subscription_id: Subscription ID to cancel
            immediate: Whether to cancel immediately or at the end of the period

        Returns:
            True if successful, False otherwise
        """
        # Get existing subscription
        subscription = self.subscription_repository.get(subscription_id)
        if not subscription:
            return False
            
        if immediate:
            # Cancel immediately
            subscription.status = SubscriptionStatus.CANCELLED
        else:
            # Cancel at end of period
            subscription.auto_renew = False
            
        # Save updated subscription
        return self.subscription_repository.save(subscription)

    def renew_subscription(self, subscription_id: str, extend_months: int = 1) -> Optional[Subscription]:
        """
        Renew a subscription.

        Args:
            subscription_id: Subscription ID to renew
            extend_months: Number of months to extend

        Returns:
            Renewed subscription or None if failed
        """
        # Get existing subscription
        subscription = self.subscription_repository.get(subscription_id)
        if not subscription:
            return None
            
        # Calculate new end date
        if subscription.end_date:
            new_end_date = subscription.end_date.replace(month=subscription.end_date.month + extend_months)
        else:
            # If no end date, use current date as reference
            current_date = datetime.now()
            new_end_date = current_date.replace(month=current_date.month + extend_months)
            
        # Update subscription
        subscription.end_date = new_end_date
        subscription.status = SubscriptionStatus.ACTIVE
        
        # Save updated subscription
        if self.subscription_repository.save(subscription):
            return subscription
            
        return None

    def add_license_to_subscription(self, subscription_id: str, license_key: str) -> bool:
        """
        Add a license key to a subscription.

        Args:
            subscription_id: Subscription ID
            license_key: License key to add

        Returns:
            True if successful, False otherwise
        """
        # Get existing subscription
        subscription = self.subscription_repository.get(subscription_id)
        if not subscription:
            return False
            
        # Add license key if not already present
        if license_key not in subscription.license_keys:
            subscription.license_keys.append(license_key)
            
            # Save updated subscription
            return self.subscription_repository.save(subscription)
            
        return True

    def remove_license_from_subscription(self, subscription_id: str, license_key: str) -> bool:
        """
        Remove a license key from a subscription.

        Args:
            subscription_id: Subscription ID
            license_key: License key to remove

        Returns:
            True if successful, False otherwise
        """
        # Get existing subscription
        subscription = self.subscription_repository.get(subscription_id)
        if not subscription:
            return False
            
        # Remove license key if present
        if license_key in subscription.license_keys:
            subscription.license_keys.remove(license_key)
            
            # Save updated subscription
            return self.subscription_repository.save(subscription)
            
        return True

    def get_customer_subscriptions(self, customer_id: str) -> List[Subscription]:
        """
        Get all subscriptions for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of subscriptions for the customer
        """
        return self.subscription_repository.get_by_customer(customer_id)

    def get_active_customer_subscriptions(self, customer_id: str) -> List[Subscription]:
        """
        Get active subscriptions for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of active subscriptions for the customer
        """
        subscriptions = self.subscription_repository.get_by_customer(customer_id)
        return [sub for sub in subscriptions if sub.is_active()]

    def get_customer_features(self, customer_id: str) -> Set[LicenseFeature]:
        """
        Get all features available to a customer.

        Args:
            customer_id: Customer ID

        Returns:
            Set of available features
        """
        return self.feature_gate.get_available_features(customer_id)

    def check_customer_access(self, customer_id: str, feature: LicenseFeature) -> bool:
        """
        Check if a customer has access to a feature.

        Args:
            customer_id: Customer ID
            feature: Feature to check

        Returns:
            True if customer has access, False otherwise
        """
        return self.feature_gate.has_feature(customer_id, feature)

    def get_upgrade_options(self, customer_id: str, feature: LicenseFeature) -> List[TierDefinition]:
        """
        Get upgrade options for a customer to access a feature.

        Args:
            customer_id: Customer ID
            feature: Feature needed

        Returns:
            List of tier options that would provide the feature
        """
        return self.feature_gate.get_upgrade_path(customer_id, feature)

    def process_expiring_subscriptions(self) -> int:
        """
        Process subscriptions that are expiring soon.

        Returns:
            Number of subscriptions processed
        """
        # Get subscriptions expiring in the next 7 days
        expiring_soon = self.subscription_repository.get_expiring_soon(days=7)
        processed_count = 0
        
        for subscription in expiring_soon:
            # Check if auto-renew is enabled
            if subscription.auto_renew:
                # Attempt to renew the subscription
                renewed = self.renew_subscription(subscription.subscription_id)
                if renewed:
                    processed_count += 1
                    
        return processed_count


if __name__ == "__main__":
    # Example usage
    # Create subscription manager
    subscription_manager = SubscriptionManager("subscription_data")
    
    # Create subscription repository
    subscription_repository = SubscriptionRepository("subscription_data")
    
    # Create feature gate
    feature_gate = FeatureGate(subscription_manager, subscription_repository)
    
    # Create subscription service
    subscription_service = SubscriptionService(
        subscription_manager, 
        subscription_repository, 
        feature_gate
    )
    
    # Create a subscription
    subscription = subscription_service.create_subscription(
        customer_id="customer123",
        tier_id="professional",
        period=SubscriptionPeriod.MONTHLY,
        payment_method="pm_123456",
        auto_renew=True
    )
    
    if subscription:
        print(f"Created subscription: {subscription.subscription_id}")
        
        # Check feature access
        has_access = subscription_service.check_customer_access(
            "customer123", 
            LicenseFeature.PRIORITY_SUPPORT
        )
        print(f"Has access to priority support: {has_access}")
        
        # Get available features
        features = subscription_service.get_customer_features("customer123")
        print(f"Available features: {[f.value for f in features]}")
        
        # Get upgrade options for a feature
        upgrade_options = subscription_service.get_upgrade_options(
            "customer123", 
            LicenseFeature.WHITE_LABEL
        )
        print(f"Upgrade options: {[tier.name for tier in upgrade_options]}")
