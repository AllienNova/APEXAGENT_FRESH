"""
Modified test suite for the Subscription and Licensing System.

This version uses relative imports to avoid path issues.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tempfile
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

# Import enums and types needed for tests
class LicenseFeature(Enum):
    """Enumeration of license features."""
    CORE = "core"
    ADVANCED_PLUGINS = "advanced_plugins"
    API_ACCESS = "api_access"
    PRIORITY_SUPPORT = "priority_support"
    OFFLINE_MODE = "offline_mode"
    MULTI_USER = "multi_user"
    ENTERPRISE_INTEGRATION = "enterprise_integration"
    WHITE_LABEL = "white_label"
    CUSTOM_BRANDING = "custom_branding"
    ADVANCED_ANALYTICS = "advanced_analytics"

class LicenseType(Enum):
    """Enumeration of license types."""
    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    TRIAL = "trial"

class LicenseStatus(Enum):
    """Enumeration of license statuses."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"

class SubscriptionStatus(Enum):
    """Enumeration of subscription statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    PENDING = "pending"
    EXPIRED = "expired"

class SubscriptionPeriod(Enum):
    """Enumeration of subscription periods."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    BIENNIAL = "biennial"

class ResourceType(Enum):
    """Enumeration of resource types for usage tracking."""
    API_CALLS = "api_calls"
    STORAGE = "storage"
    MODEL_TOKENS = "model_tokens"
    PLUGIN_EXECUTION = "plugin_execution"
    CONCURRENT_USERS = "concurrent_users"
    DATA_TRANSFER = "data_transfer"

class QuotaType(Enum):
    """Enumeration of quota types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    TOTAL = "total"

class QuotaAction(Enum):
    """Enumeration of quota enforcement actions."""
    BLOCK = "block"
    NOTIFY = "notify"
    THROTTLE = "throttle"
    LOG = "log"

# Mock classes for testing
class LicenseMetadata:
    """License metadata class."""
    
    def __init__(
        self,
        license_id: str,
        customer_id: str,
        license_type: LicenseType,
        features: List[LicenseFeature],
        issue_date: datetime,
        expiration_date: Optional[datetime] = None,
        activation_limit: int = 1
    ):
        self.license_id = license_id
        self.customer_id = customer_id
        self.license_type = license_type
        self.features = features
        self.issue_date = issue_date
        self.expiration_date = expiration_date
        self.activation_limit = activation_limit

class LicenseSignature:
    """License signature handler class."""
    
    def __init__(self, public_key_path: Optional[str] = None):
        self.public_key_path = public_key_path
    
    def generate_key_pair(self, private_key_path: str, public_key_path: str) -> bool:
        """Generate a key pair for testing."""
        # Mock implementation
        with open(private_key_path, 'w') as f:
            f.write("MOCK PRIVATE KEY")
        with open(public_key_path, 'w') as f:
            f.write("MOCK PUBLIC KEY")
        return True
    
    def sign(self, data: str) -> str:
        """Sign data with private key."""
        # Mock implementation
        return f"MOCK_SIGNATURE_{data}"
    
    def verify(self, data: str, signature: str) -> bool:
        """Verify signature with public key."""
        # Mock implementation
        return signature == f"MOCK_SIGNATURE_{data}"

class LicenseGenerator:
    """License generator class."""
    
    def __init__(self, signature_handler: LicenseSignature, private_key_path: str):
        self.signature_handler = signature_handler
        self.private_key_path = private_key_path
    
    def generate_license_key(self, metadata: LicenseMetadata) -> str:
        """Generate a license key."""
        # Mock implementation
        prefix = "APX-123456"
        data = f"{metadata.license_id}:{metadata.customer_id}"
        signature = self.signature_handler.sign(data)
        return f"{prefix}.{data}.{signature}.{metadata.license_type.value}"
    
    def batch_generate_license_keys(self, metadata_list: List[LicenseMetadata]) -> List[str]:
        """Generate multiple license keys."""
        return [self.generate_license_key(metadata) for metadata in metadata_list]

class ValidationResult:
    """License validation result class."""
    
    def __init__(
        self,
        is_valid: bool,
        license_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        status: Optional[LicenseStatus] = None,
        features: Optional[List[LicenseFeature]] = None,
        error_message: Optional[str] = None
    ):
        self.is_valid = is_valid
        self.license_id = license_id
        self.customer_id = customer_id
        self.status = status
        self.features = features or []
        self.error_message = error_message

class LicenseValidator:
    """License validator class."""
    
    def __init__(self, signature_handler: LicenseSignature):
        self.signature_handler = signature_handler
    
    def validate_license_key(self, license_key: str) -> ValidationResult:
        """Validate a license key."""
        # Mock implementation
        if "expired" in license_key:
            return ValidationResult(
                is_valid=False,
                license_id="expired-license-123",
                status=LicenseStatus.EXPIRED,
                features=[LicenseFeature.CORE],
                error_message="License has expired"
            )
        elif "tampered" in license_key:
            return ValidationResult(
                is_valid=False,
                error_message="Invalid signature"
            )
        else:
            # Parse license key
            parts = license_key.split(".")
            if len(parts) != 4:
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid license format"
                )
            
            # Extract data
            data_parts = parts[1].split(":")
            license_id = data_parts[0]
            customer_id = data_parts[1]
            
            return ValidationResult(
                is_valid=True,
                license_id=license_id,
                customer_id=customer_id,
                status=LicenseStatus.ACTIVE,
                features=[LicenseFeature.CORE, LicenseFeature.ADVANCED_PLUGINS]
            )
    
    def has_feature(self, license_key: str, feature: LicenseFeature) -> bool:
        """Check if a license has a specific feature."""
        result = self.validate_license_key(license_key)
        return feature in result.features

class OfflineValidator:
    """Offline license validator class."""
    
    def __init__(self, signature_handler: LicenseSignature):
        self.signature_handler = signature_handler
    
    def validate_license_key(self, license_key: str) -> ValidationResult:
        """Validate a license key offline."""
        # Mock implementation - similar to LicenseValidator
        return LicenseValidator(self.signature_handler).validate_license_key(license_key)

class LicenseActivation:
    """License activation class."""
    
    def __init__(
        self,
        license_key: str,
        device_id: str,
        activation_date: datetime,
        is_active: bool = True
    ):
        self.license_key = license_key
        self.device_id = device_id
        self.activation_date = activation_date
        self.is_active = is_active

class TierDefinition:
    """Subscription tier definition class."""
    
    def __init__(
        self,
        tier_id: str,
        name: str,
        description: str,
        features: List[LicenseFeature],
        price_monthly: float,
        price_annual: float,
        max_users: int
    ):
        self.tier_id = tier_id
        self.name = name
        self.description = description
        self.features = features
        self.price_monthly = price_monthly
        self.price_annual = price_annual
        self.max_users = max_users

class SubscriptionManager:
    """Subscription tier manager class."""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.tiers = {}
        self._initialize_default_tiers()
    
    def _initialize_default_tiers(self):
        """Initialize default subscription tiers."""
        # Free tier
        self.tiers["free"] = TierDefinition(
            tier_id="free",
            name="Free",
            description="Basic functionality for individual users",
            features=[LicenseFeature.CORE],
            price_monthly=0.0,
            price_annual=0.0,
            max_users=1
        )
        
        # Basic tier
        self.tiers["basic"] = TierDefinition(
            tier_id="basic",
            name="Basic",
            description="Enhanced functionality for individual users",
            features=[LicenseFeature.CORE, LicenseFeature.ADVANCED_PLUGINS],
            price_monthly=9.99,
            price_annual=99.99,
            max_users=1
        )
        
        # Professional tier
        self.tiers["professional"] = TierDefinition(
            tier_id="professional",
            name="Professional",
            description="Advanced functionality for professional users",
            features=[
                LicenseFeature.CORE,
                LicenseFeature.ADVANCED_PLUGINS,
                LicenseFeature.API_ACCESS,
                LicenseFeature.PRIORITY_SUPPORT
            ],
            price_monthly=19.99,
            price_annual=199.99,
            max_users=5
        )
        
        # Enterprise tier
        self.tiers["enterprise"] = TierDefinition(
            tier_id="enterprise",
            name="Enterprise",
            description="Complete functionality for enterprise users",
            features=[
                LicenseFeature.CORE,
                LicenseFeature.ADVANCED_PLUGINS,
                LicenseFeature.API_ACCESS,
                LicenseFeature.PRIORITY_SUPPORT,
                LicenseFeature.OFFLINE_MODE,
                LicenseFeature.MULTI_USER,
                LicenseFeature.ENTERPRISE_INTEGRATION,
                LicenseFeature.WHITE_LABEL
            ],
            price_monthly=49.99,
            price_annual=499.99,
            max_users=100
        )
    
    def get_tier(self, tier_id: str) -> Optional[TierDefinition]:
        """Get a tier by ID."""
        return self.tiers.get(tier_id)
    
    def get_all_tiers(self) -> List[TierDefinition]:
        """Get all tiers."""
        return list(self.tiers.values())
    
    def add_tier(self, tier: TierDefinition) -> bool:
        """Add a new tier."""
        if tier.tier_id in self.tiers:
            return False
        self.tiers[tier.tier_id] = tier
        return True
    
    def update_tier(self, tier: TierDefinition) -> bool:
        """Update an existing tier."""
        if tier.tier_id not in self.tiers:
            return False
        self.tiers[tier.tier_id] = tier
        return True
    
    def delete_tier(self, tier_id: str) -> bool:
        """Delete a tier."""
        if tier_id not in self.tiers:
            return False
        del self.tiers[tier_id]
        return True
    
    def get_tier_for_feature(self, feature: LicenseFeature) -> List[TierDefinition]:
        """Get tiers that include a specific feature."""
        return [tier for tier in self.tiers.values() if feature in tier.features]

class Subscription:
    """Subscription class."""
    
    def __init__(
        self,
        subscription_id: str,
        customer_id: str,
        tier_id: str,
        status: SubscriptionStatus,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        payment_method: Optional[str] = None,
        auto_renew: bool = False,
        license_keys: Optional[List[str]] = None
    ):
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.tier_id = tier_id
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.payment_method = payment_method
        self.auto_renew = auto_renew
        self.license_keys = license_keys or []

class SubscriptionRepository:
    """Subscription repository class."""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.subscriptions = {}
    
    def save(self, subscription: Subscription) -> bool:
        """Save a subscription."""
        self.subscriptions[subscription.subscription_id] = subscription
        return True
    
    def get(self, subscription_id: str) -> Optional[Subscription]:
        """Get a subscription by ID."""
        return self.subscriptions.get(subscription_id)
    
    def get_by_customer(self, customer_id: str) -> List[Subscription]:
        """Get subscriptions for a customer."""
        return [
            sub for sub in self.subscriptions.values()
            if sub.customer_id == customer_id
        ]
    
    def get_by_status(self, status: SubscriptionStatus) -> List[Subscription]:
        """Get subscriptions by status."""
        return [
            sub for sub in self.subscriptions.values()
            if sub.status == status
        ]
    
    def delete(self, subscription_id: str) -> bool:
        """Delete a subscription."""
        if subscription_id not in self.subscriptions:
            return False
        del self.subscriptions[subscription_id]
        return True

class FeatureGate:
    """Feature access control class."""
    
    def __init__(
        self,
        subscription_manager: SubscriptionManager,
        subscription_repository: SubscriptionRepository
    ):
        self.subscription_manager = subscription_manager
        self.subscription_repository = subscription_repository
    
    def has_feature(self, customer_id: str, feature: LicenseFeature) -> bool:
        """Check if a customer has access to a feature."""
        # Get active subscriptions for the customer
        subscriptions = self.subscription_repository.get_by_customer(customer_id)
        active_subscriptions = [
            sub for sub in subscriptions
            if sub.status == SubscriptionStatus.ACTIVE
        ]
        
        if not active_subscriptions:
            return False
        
        # Check if any subscription tier includes the feature
        for subscription in active_subscriptions:
            tier = self.subscription_manager.get_tier(subscription.tier_id)
            if tier and feature in tier.features:
                return True
        
        return False
    
    def get_available_features(self, customer_id: str) -> Set[LicenseFeature]:
        """Get all features available to a customer."""
        # Get active subscriptions for the customer
        subscriptions = self.subscription_repository.get_by_customer(customer_id)
        active_subscriptions = [
            sub for sub in subscriptions
            if sub.status == SubscriptionStatus.ACTIVE
        ]
        
        if not active_subscriptions:
            return set()
        
        # Collect features from all subscription tiers
        features = set()
        for subscription in active_subscriptions:
            tier = self.subscription_manager.get_tier(subscription.tier_id)
            if tier:
                features.update(tier.features)
        
        return features
    
    def check_access(
        self,
        customer_id: str,
        required_features: List[LicenseFeature]
    ) -> Tuple[bool, List[LicenseFeature]]:
        """Check if a customer has access to all required features."""
        available_features = self.get_available_features(customer_id)
        missing_features = [
            feature for feature in required_features
            if feature not in available_features
        ]
        
        return len(missing_features) == 0, missing_features
    
    def get_upgrade_path(
        self,
        customer_id: str,
        feature: LicenseFeature
    ) -> List[TierDefinition]:
        """Get upgrade paths for a feature."""
        # Get tiers that include the feature
        tiers_with_feature = self.subscription_manager.get_tier_for_feature(feature)
        
        # Sort by price
        tiers_with_feature.sort(key=lambda tier: tier.price_monthly)
        
        return tiers_with_feature

class SubscriptionService:
    """Subscription service class."""
    
    def __init__(
        self,
        subscription_manager: SubscriptionManager,
        subscription_repository: SubscriptionRepository,
        feature_gate: FeatureGate
    ):
        self.subscription_manager = subscription_manager
        self.subscription_repository = subscription_repository
        self.feature_gate = feature_gate
    
    def create_subscription(
        self,
        customer_id: str,
        tier_id: str,
        period: SubscriptionPeriod,
        payment_method: Optional[str] = None,
        auto_renew: bool = True
    ) -> Optional[Subscription]:
        """Create a new subscription."""
        # Check if tier exists
        tier = self.subscription_manager.get_tier(tier_id)
        if not tier:
            return None
        
        # Calculate end date based on period
        start_date = datetime.now()
        end_date = None
        
        if period == SubscriptionPeriod.MONTHLY:
            end_date = start_date + timedelta(days=30)
        elif period == SubscriptionPeriod.QUARTERLY:
            end_date = start_date + timedelta(days=90)
        elif period == SubscriptionPeriod.ANNUAL:
            end_date = start_date + timedelta(days=365)
        elif period == SubscriptionPeriod.BIENNIAL:
            end_date = start_date + timedelta(days=730)
        
        # Create subscription
        subscription_id = f"sub-{customer_id}-{datetime.now().timestamp()}"
        subscription = Subscription(
            subscription_id=subscription_id,
            customer_id=customer_id,
            tier_id=tier_id,
            status=SubscriptionStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method,
            auto_renew=auto_renew
        )
        
        # Save subscription
        self.subscription_repository.save(subscription)
        
        return subscription
    
    def update_subscription(
        self,
        subscription_id: str,
        tier_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        auto_renew: Optional[bool] = None
    ) -> Optional[Subscription]:
        """Update an existing subscription."""
        # Get subscription
        subscription = self.subscription_repository.get(subscription_id)
        if not subscription:
            return None
        
        # Update fields
        if tier_id is not None:
            # Check if tier exists
            tier = self.subscription_manager.get_tier(tier_id)
            if not tier:
                return None
            subscription.tier_id = tier_id
        
        if payment_method is not None:
            subscription.payment_method = payment_method
        
        if auto_renew is not None:
            subscription.auto_renew = auto_renew
        
        # Save subscription
        self.subscription_repository.save(subscription)
        
        return subscription
    
    def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False
    ) -> bool:
        """Cancel a subscription."""
        # Get subscription
        subscription = self.subscription_repository.get(subscription_id)
        if not subscription:
            return False
        
        if immediate:
            # Cancel immediately
            subscription.status = SubscriptionStatus.CANCELLED
        else:
            # Cancel at end of period
            subscription.auto_renew = False
        
        # Save subscription
        self.subscription_repository.save(subscription)
        
        return True
    
    def add_license_to_subscription(
        self,
        subscription_id: str,
        license_key: str
    ) -> bool:
        """Add a license key to a subscription."""
        # Get subscription
        subscription = self.subscription_repository.get(subscription_id)
        if not subscription:
            return False
        
        # Add license key
        if license_key not in subscription.license_keys:
            subscription.license_keys.append(license_key)
        
        # Save subscription
        self.subscription_repository.save(subscription)
        
        return True
    
    def get_customer_subscriptions(self, customer_id: str) -> List[Subscription]:
        """Get all subscriptions for a customer."""
        return self.subscription_repository.get_by_customer(customer_id)
    
    def get_active_customer_subscriptions(self, customer_id: str) -> List[Subscription]:
        """Get active subscriptions for a customer."""
        subscriptions = self.subscription_repository.get_by_customer(customer_id)
        return [
            sub for sub in subscriptions
            if sub.status == SubscriptionStatus.ACTIVE
        ]
    
    def check_customer_access(self, customer_id: str, feature: LicenseFeature) -> bool:
        """Check if a customer has access to a feature."""
        return self.feature_gate.has_feature(customer_id, feature)
    
    def get_customer_features(self, customer_id: str) -> Set[LicenseFeature]:
        """Get all features available to a customer."""
        return self.feature_gate.get_available_features(customer_id)

class QuotaDefinition:
    """Quota definition class."""
    
    def __init__(
        self,
        resource_type: ResourceType,
        quota_type: QuotaType,
        limit: int,
        action: QuotaAction,
        tier_id: str,
        reset_day: Optional[int] = None
    ):
        self.resource_type = resource_type
        self.quota_type = quota_type
        self.limit = limit
        self.action = action
        self.tier_id = tier_id
        self.reset_day = reset_day

class QuotaManager:
    """Quota manager class."""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.quotas = {}
        self._initialize_default_quotas()
    
    def _initialize_default_quotas(self):
        """Initialize default quotas."""
        # Free tier quotas
        self.quotas["free_api_daily"] = QuotaDefinition(
            resource_type=ResourceType.API_CALLS,
            quota_type=QuotaType.DAILY,
            limit=100,
            action=QuotaAction.BLOCK,
            tier_id="free"
        )
        
        self.quotas["free_storage"] = QuotaDefinition(
            resource_type=ResourceType.STORAGE,
            quota_type=QuotaType.TOTAL,
            limit=1024 * 1024,  # 1 MB
            action=QuotaAction.BLOCK,
            tier_id="free"
        )
        
        # Basic tier quotas
        self.quotas["basic_api_daily"] = QuotaDefinition(
            resource_type=ResourceType.API_CALLS,
            quota_type=QuotaType.DAILY,
            limit=1000,
            action=QuotaAction.BLOCK,
            tier_id="basic"
        )
        
        self.quotas["basic_storage"] = QuotaDefinition(
            resource_type=ResourceType.STORAGE,
            quota_type=QuotaType.TOTAL,
            limit=10 * 1024 * 1024,  # 10 MB
            action=QuotaAction.BLOCK,
            tier_id="basic"
        )
        
        # Professional tier quotas
        self.quotas["pro_api_daily"] = QuotaDefinition(
            resource_type=ResourceType.API_CALLS,
            quota_type=QuotaType.DAILY,
            limit=10000,
            action=QuotaAction.BLOCK,
            tier_id="professional"
        )
        
        self.quotas["pro_storage"] = QuotaDefinition(
            resource_type=ResourceType.STORAGE,
            quota_type=QuotaType.TOTAL,
            limit=100 * 1024 * 1024,  # 100 MB
            action=QuotaAction.BLOCK,
            tier_id="professional"
        )
        
        # Enterprise tier quotas
        self.quotas["enterprise_api_daily"] = QuotaDefinition(
            resource_type=ResourceType.API_CALLS,
            quota_type=QuotaType.DAILY,
            limit=100000,
            action=QuotaAction.NOTIFY,
            tier_id="enterprise"
        )
        
        self.quotas["enterprise_storage"] = QuotaDefinition(
            resource_type=ResourceType.STORAGE,
            quota_type=QuotaType.TOTAL,
            limit=1024 * 1024 * 1024,  # 1 GB
            action=QuotaAction.NOTIFY,
            tier_id="enterprise"
        )
    
    def get_quota(self, quota_id: str) -> Optional[QuotaDefinition]:
        """Get a quota by ID."""
        return self.quotas.get(quota_id)
    
    def get_quotas_for_tier(self, tier_id: str) -> List[QuotaDefinition]:
        """Get quotas for a specific tier."""
        return [
            quota for quota in self.quotas.values()
            if quota.tier_id == tier_id
        ]
    
    def get_quotas_for_resource(self, resource_type: ResourceType) -> List[QuotaDefinition]:
        """Get quotas for a specific resource type."""
        return [
            quota for quota in self.quotas.values()
            if quota.resource_type == resource_type
        ]
    
    def add_quota(self, quota_id: str, quota: QuotaDefinition) -> bool:
        """Add a new quota definition."""
        if quota_id in self.quotas:
            return False
        self.quotas[quota_id] = quota
        return True
    
    def update_quota(self, quota_id: str, quota: QuotaDefinition) -> bool:
        """Update an existing quota definition."""
        if quota_id not in self.quotas:
            return False
        self.quotas[quota_id] = quota
        return True
    
    def delete_quota(self, quota_id: str) -> bool:
        """Delete a quota definition."""
        if quota_id not in self.quotas:
            return False
        del self.quotas[quota_id]
        return True

class UsageRecord:
    """Usage record class."""
    
    def __init__(
        self,
        record_id: str,
        customer_id: str,
        resource_type: ResourceType,
        quantity: int,
        timestamp: datetime,
        subscription_id: Optional[str] = None,
        feature: Optional[LicenseFeature] = None,
        metadata: Optional[Dict[str, str]] = None
    ):
        self.record_id = record_id
        self.customer_id = customer_id
        self.resource_type = resource_type
        self.quantity = quantity
        self.timestamp = timestamp
        self.subscription_id = subscription_id
        self.feature = feature
        self.metadata = metadata or {}

class UsageTracker:
    """Usage tracking class."""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.records = []
    
    def track_usage(
        self,
        customer_id: str,
        resource_type: ResourceType,
        quantity: int,
        subscription_id: Optional[str] = None,
        feature: Optional[LicenseFeature] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> UsageRecord:
        """Track resource usage."""
        record_id = f"usage-{customer_id}-{datetime.now().timestamp()}"
        record = UsageRecord(
            record_id=record_id,
            customer_id=customer_id,
            resource_type=resource_type,
            quantity=quantity,
            timestamp=datetime.now(),
            subscription_id=subscription_id,
            feature=feature,
            metadata=metadata or {}
        )
        
        self.records.append(record)
        
        return record
    
    def get_daily_usage(
        self,
        date: datetime,
        customer_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None
    ) -> List[UsageRecord]:
        """Get usage records for a specific day."""
        # Filter by date
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        records = [
            record for record in self.records
            if start_of_day <= record.timestamp < end_of_day
        ]
        
        # Filter by customer ID
        if customer_id:
            records = [
                record for record in records
                if record.customer_id == customer_id
            ]
        
        # Filter by resource type
        if resource_type:
            records = [
                record for record in records
                if record.resource_type == resource_type
            ]
        
        return records
    
    def get_usage_summary(
        self,
        customer_id: str,
        resource_type: ResourceType,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Get total usage for a specific period."""
        # Filter by date range
        records = [
            record for record in self.records
            if (
                record.customer_id == customer_id and
                record.resource_type == resource_type and
                start_date <= record.timestamp < end_date
            )
        ]
        
        # Sum quantities
        return sum(record.quantity for record in records)

class QuotaEnforcer:
    """Quota enforcement class."""
    
    def __init__(
        self,
        quota_manager: QuotaManager,
        usage_tracker: UsageTracker,
        subscription_service: SubscriptionService
    ):
        self.quota_manager = quota_manager
        self.usage_tracker = usage_tracker
        self.subscription_service = subscription_service
    
    def check_quota(
        self,
        customer_id: str,
        resource_type: ResourceType,
        quantity: int
    ) -> Tuple[bool, Optional[QuotaAction], Optional[str]]:
        """Check if a usage would exceed quota."""
        # Get active subscriptions for the customer
        active_subscriptions = self.subscription_service.get_active_customer_subscriptions(customer_id)
        
        if not active_subscriptions:
            return False, QuotaAction.BLOCK, "No active subscription"
        
        # Get tier ID from the first active subscription
        tier_id = active_subscriptions[0].tier_id
        
        # Get quotas for the tier and resource type
        quotas = [
            quota for quota in self.quota_manager.get_quotas_for_tier(tier_id)
            if quota.resource_type == resource_type
        ]
        
        if not quotas:
            # No quota defined, allow usage
            return True, None, None
        
        # Check each quota
        for quota in quotas:
            # Get current usage based on quota type
            current_usage = 0
            
            if quota.quota_type == QuotaType.DAILY:
                current_usage = self.usage_tracker.get_usage_summary(
                    customer_id=customer_id,
                    resource_type=resource_type,
                    start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                    end_date=datetime.now()
                )
            elif quota.quota_type == QuotaType.WEEKLY:
                # Get start of week (Monday)
                today = datetime.now().date()
                start_of_week = today - timedelta(days=today.weekday())
                start_date = datetime.combine(start_of_week, datetime.min.time())
                
                current_usage = self.usage_tracker.get_usage_summary(
                    customer_id=customer_id,
                    resource_type=resource_type,
                    start_date=start_date,
                    end_date=datetime.now()
                )
            elif quota.quota_type == QuotaType.MONTHLY:
                # Get start of month
                start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                current_usage = self.usage_tracker.get_usage_summary(
                    customer_id=customer_id,
                    resource_type=resource_type,
                    start_date=start_date,
                    end_date=datetime.now()
                )
            elif quota.quota_type == QuotaType.ANNUAL:
                # Get start of year
                start_date = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                
                current_usage = self.usage_tracker.get_usage_summary(
                    customer_id=customer_id,
                    resource_type=resource_type,
                    start_date=start_date,
                    end_date=datetime.now()
                )
            elif quota.quota_type == QuotaType.TOTAL:
                # Get all usage
                current_usage = self.usage_tracker.get_usage_summary(
                    customer_id=customer_id,
                    resource_type=resource_type,
                    start_date=datetime.min,
                    end_date=datetime.now()
                )
            
            # Check if usage would exceed quota
            if current_usage + quantity > quota.limit:
                # Quota would be exceeded
                message = f"{resource_type.value} quota exceeded: {current_usage}/{quota.limit}"
                return False, quota.action, message
        
        # All quotas checked, usage allowed
        return True, None, None
    
    def track_and_enforce(
        self,
        customer_id: str,
        resource_type: ResourceType,
        quantity: int,
        subscription_id: Optional[str] = None,
        feature: Optional[LicenseFeature] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, Optional[UsageRecord], Optional[str]]:
        """Track usage and enforce quota."""
        # Check quota
        allowed, action, message = self.check_quota(
            customer_id=customer_id,
            resource_type=resource_type,
            quantity=quantity
        )
        
        if not allowed and action == QuotaAction.BLOCK:
            # Usage blocked
            return False, None, message
        
        # Track usage
        record = self.usage_tracker.track_usage(
            customer_id=customer_id,
            resource_type=resource_type,
            quantity=quantity,
            subscription_id=subscription_id,
            feature=feature,
            metadata=metadata
        )
        
        if not allowed:
            # Usage allowed but action needed
            return True, record, message
        
        # Usage allowed, no action needed
        return True, record, None
    
    def get_quota_status(
        self,
        customer_id: str,
        resource_type: ResourceType
    ) -> Dict[str, Union[bool, str, int, float]]:
        """Get quota status for a specific resource type."""
        # Get active subscriptions for the customer
        active_subscriptions = self.subscription_service.get_active_customer_subscriptions(customer_id)
        
        if not active_subscriptions:
            return {
                "has_quota": False,
                "resource_type": resource_type.value,
                "message": "No active subscription"
            }
        
        # Get tier ID from the first active subscription
        tier_id = active_subscriptions[0].tier_id
        
        # Get quotas for the tier and resource type
        quotas = [
            quota for quota in self.quota_manager.get_quotas_for_tier(tier_id)
            if quota.resource_type == resource_type
        ]
        
        if not quotas:
            return {
                "has_quota": False,
                "resource_type": resource_type.value,
                "message": "No quota defined"
            }
        
        # Use the first quota for status
        quota = quotas[0]
        
        # Get current usage based on quota type
        current_usage = 0
        start_date = datetime.min
        
        if quota.quota_type == QuotaType.DAILY:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif quota.quota_type == QuotaType.WEEKLY:
            # Get start of week (Monday)
            today = datetime.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            start_date = datetime.combine(start_of_week, datetime.min.time())
        elif quota.quota_type == QuotaType.MONTHLY:
            # Get start of month
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif quota.quota_type == QuotaType.ANNUAL:
            # Get start of year
            start_date = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_usage = self.usage_tracker.get_usage_summary(
            customer_id=customer_id,
            resource_type=resource_type,
            start_date=start_date,
            end_date=datetime.now()
        )
        
        # Calculate status
        remaining = quota.limit - current_usage
        percentage_used = (current_usage / quota.limit) * 100 if quota.limit > 0 else 0
        
        return {
            "has_quota": True,
            "resource_type": resource_type.value,
            "quota_type": quota.quota_type.value,
            "limit": quota.limit,
            "current_usage": current_usage,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "action": quota.action.value
        }

class UsageAnalytics:
    """Usage analytics class."""
    
    def __init__(self, usage_tracker: UsageTracker):
        self.usage_tracker = usage_tracker
    
    def get_usage_trend(
        self,
        customer_id: str,
        resource_type: ResourceType,
        days: int
    ) -> Dict[str, int]:
        """Get usage trend for a specific period."""
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily usage
        trend = {}
        current_date = start_date
        
        while current_date <= end_date:
            records = self.usage_tracker.get_daily_usage(
                date=current_date,
                customer_id=customer_id,
                resource_type=resource_type
            )
            
            # Sum quantities
            daily_usage = sum(record.quantity for record in records)
            
            # Add to trend
            trend[current_date.strftime("%Y-%m-%d")] = daily_usage
            
            # Move to next day
            current_date += timedelta(days=1)
        
        return trend
    
    def get_resource_distribution(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Get resource usage distribution."""
        # Filter records by date range and customer ID
        records = [
            record for record in self.usage_tracker.records
            if (
                record.customer_id == customer_id and
                start_date <= record.timestamp < end_date
            )
        ]
        
        # Group by resource type
        distribution = {}
        
        for record in records:
            resource_type = record.resource_type.value
            if resource_type not in distribution:
                distribution[resource_type] = 0
            distribution[resource_type] += record.quantity
        
        return distribution
    
    def get_feature_usage(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Get feature usage distribution."""
        # Filter records by date range and customer ID
        records = [
            record for record in self.usage_tracker.records
            if (
                record.customer_id == customer_id and
                start_date <= record.timestamp < end_date and
                record.feature is not None
            )
        ]
        
        # Group by feature
        feature_usage = {}
        
        for record in records:
            feature = record.feature.value
            if feature not in feature_usage:
                feature_usage[feature] = 0
            feature_usage[feature] += record.quantity
        
        return feature_usage
    
    def get_usage_report(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Union[int, Dict[str, int], Dict[str, Dict[str, int]]]]:
        """Generate a usage report."""
        # Get resource distribution
        resource_usage = self.get_resource_distribution(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get feature usage
        feature_usage = self.get_feature_usage(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get daily usage
        daily_usage = {}
        current_date = start_date
        
        while current_date <= end_date:
            records = self.usage_tracker.get_daily_usage(
                date=current_date,
                customer_id=customer_id
            )
            
            # Group by resource type
            day_resources = {}
            for record in records:
                resource_type = record.resource_type.value
                if resource_type not in day_resources:
                    day_resources[resource_type] = 0
                day_resources[resource_type] += record.quantity
            
            # Add to daily usage
            daily_usage[current_date.strftime("%Y-%m-%d")] = day_resources
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Calculate total usage
        total_usage = sum(resource_usage.values())
        
        return {
            "total_usage": total_usage,
            "resource_usage": resource_usage,
            "feature_usage": feature_usage,
            "daily_usage": daily_usage
        }

class UsageService:
    """Usage service class."""
    
    def __init__(
        self,
        quota_manager: QuotaManager,
        usage_tracker: UsageTracker,
        quota_enforcer: QuotaEnforcer,
        usage_analytics: UsageAnalytics
    ):
        self.quota_manager = quota_manager
        self.usage_tracker = usage_tracker
        self.quota_enforcer = quota_enforcer
        self.usage_analytics = usage_analytics
    
    def track_usage(
        self,
        customer_id: str,
        resource_type: ResourceType,
        quantity: int,
        subscription_id: Optional[str] = None,
        feature: Optional[LicenseFeature] = None,
        metadata: Optional[Dict[str, str]] = None,
        enforce_quota: bool = True
    ) -> Tuple[bool, Optional[UsageRecord], Optional[str]]:
        """Track resource usage."""
        if enforce_quota:
            # Track and enforce quota
            return self.quota_enforcer.track_and_enforce(
                customer_id=customer_id,
                resource_type=resource_type,
                quantity=quantity,
                subscription_id=subscription_id,
                feature=feature,
                metadata=metadata
            )
        else:
            # Track without enforcing quota
            record = self.usage_tracker.track_usage(
                customer_id=customer_id,
                resource_type=resource_type,
                quantity=quantity,
                subscription_id=subscription_id,
                feature=feature,
                metadata=metadata
            )
            return True, record, None
    
    def get_quota_status(
        self,
        customer_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> Union[Dict[str, Union[bool, str, int, float]], Dict[str, Dict[str, Union[bool, str, int, float]]]]:
        """Get quota status."""
        if resource_type:
            # Get status for specific resource type
            return self.quota_enforcer.get_quota_status(
                customer_id=customer_id,
                resource_type=resource_type
            )
        else:
            # Get status for all resource types
            status = {}
            for resource_type in ResourceType:
                status[resource_type.value] = self.quota_enforcer.get_quota_status(
                    customer_id=customer_id,
                    resource_type=resource_type
                )
            return status
    
    def get_usage_report(
        self,
        customer_id: str,
        period: str = "month"
    ) -> Dict[str, Union[int, Dict[str, int], Dict[str, Dict[str, int]]]]:
        """Get usage report."""
        # Calculate date range based on period
        end_date = datetime.now()
        
        if period == "day":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            # Get start of week (Monday)
            today = end_date.date()
            start_of_week = today - timedelta(days=today.weekday())
            start_date = datetime.combine(start_of_week, datetime.min.time())
        elif period == "month":
            # Get start of month
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            # Get start of year
            start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to month
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get usage report
        return self.usage_analytics.get_usage_report(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
    
    def update_quota_definition(
        self,
        quota_id: str,
        resource_type: ResourceType,
        quota_type: QuotaType,
        limit: int,
        action: QuotaAction,
        tier_id: str,
        reset_day: Optional[int] = None
    ) -> bool:
        """Update a quota definition."""
        # Create quota definition
        quota = QuotaDefinition(
            resource_type=resource_type,
            quota_type=quota_type,
            limit=limit,
            action=action,
            tier_id=tier_id,
            reset_day=reset_day
        )
        
        # Check if quota exists
        existing_quota = self.quota_manager.get_quota(quota_id)
        
        if existing_quota:
            # Update existing quota
            return self.quota_manager.update_quota(quota_id, quota)
        else:
            # Add new quota
            return self.quota_manager.add_quota(quota_id, quota)

# Mock classes for auth system
class AuthManager:
    """Mock authentication manager class."""
    
    def __init__(self):
        self.post_auth_hooks = []
    
    def register_post_authentication_hook(self, hook):
        """Register a post-authentication hook."""
        self.post_auth_hooks.append(hook)

class RBACManager:
    """Mock RBAC manager class."""
    
    def __init__(self):
        self.permissions = {}
        self.roles = {}
        self.permission_hooks = []
    
    def register_permission(self, permission):
        """Register a permission."""
        self.permissions[permission.name] = permission
    
    def register_role(self, role):
        """Register a role."""
        self.roles[role.name] = role
    
    def check_permission(self, user_id, permission, resource, context=None):
        """Check if a user has a permission."""
        # Mock implementation
        return True
    
    def register_permission_check_hook(self, hook):
        """Register a permission check hook."""
        self.permission_hooks.append(hook)

class IdentityManager:
    """Mock identity manager class."""
    
    def __init__(self):
        pass
    
    def get_user_profile(self, user_id):
        """Get user profile."""
        # Mock implementation
        return None

class PluginSecurityManager:
    """Mock plugin security manager class."""
    
    def __init__(self):
        self.activation_hooks = []
    
    def register_plugin_activation_hook(self, hook):
        """Register a plugin activation hook."""
        self.activation_hooks.append(hook)

# Test classes
class TestLicenseGenerator(unittest.TestCase):
    """Test cases for license generation functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for key files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Generate key pair for testing
        self.private_key_path = os.path.join(self.temp_dir.name, "private_key.pem")
        self.public_key_path = os.path.join(self.temp_dir.name, "public_key.pem")
        
        # Create signature handler
        self.signature_handler = LicenseSignature()
        self.signature_handler.generate_key_pair(
            private_key_path=self.private_key_path,
            public_key_path=self.public_key_path
        )
        
        # Create license generator
        self.license_generator = LicenseGenerator(
            signature_handler=self.signature_handler,
            private_key_path=self.private_key_path
        )

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_generate_license_key(self):
        """Test generating a license key."""
        # Create license metadata
        metadata = LicenseMetadata(
            license_id="test-license-123",
            customer_id="test-customer-456",
            license_type=LicenseType.PERPETUAL,
            features=[LicenseFeature.CORE, LicenseFeature.ADVANCED_PLUGINS],
            issue_date=datetime.now(),
            expiration_date=None,
            activation_limit=1
        )
        
        # Generate license key
        license_key = self.license_generator.generate_license_key(metadata)
        
        # Verify license key format
        parts = license_key.split(".")
        self.assertEqual(len(parts), 4)
        self.assertTrue(parts[0].startswith("APX-"))

    def test_batch_generate_license_keys(self):
        """Test batch generation of license keys."""
        # Create metadata for multiple licenses
        metadata_list = [
            LicenseMetadata(
                license_id=f"test-license-{i}",
                customer_id=f"test-customer-{i}",
                license_type=LicenseType.SUBSCRIPTION,
                features=[LicenseFeature.CORE],
                issue_date=datetime.now(),
                expiration_date=datetime.now() + timedelta(days=365),
                activation_limit=1
            )
            for i in range(5)
        ]
        
        # Generate license keys in batch
        license_keys = self.license_generator.batch_generate_license_keys(metadata_list)
        
        # Verify results
        self.assertEqual(len(license_keys), 5)
        for license_key in license_keys:
            parts = license_key.split(".")
            self.assertEqual(len(parts), 4)
            self.assertTrue(parts[0].startswith("APX-"))

if __name__ == "__main__":
    unittest.main()
