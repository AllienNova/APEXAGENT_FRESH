"""
Usage Tracking and Quota Management module for ApexAgent Subscription and Licensing System.

This module provides functionality for tracking resource usage, enforcing quotas,
and generating usage analytics for the subscription system.
"""

import json
import os
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from subscription.core.license_generator import LicenseFeature
from subscription.core.subscription_manager import SubscriptionService, SubscriptionTier


class ResourceType(Enum):
    """Enumeration of trackable resource types."""
    API_CALLS = "api_calls"
    STORAGE = "storage"
    COMPUTE_TIME = "compute_time"
    BANDWIDTH = "bandwidth"
    PLUGIN_EXECUTION = "plugin_execution"
    MODEL_TOKENS = "model_tokens"
    USER_SEATS = "user_seats"
    EXPORT_COUNT = "export_count"
    CUSTOM_INTEGRATION = "custom_integration"
    BATCH_PROCESSING = "batch_processing"


class QuotaType(Enum):
    """Enumeration of quota types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    TOTAL = "total"  # Lifetime quota


class QuotaAction(Enum):
    """Enumeration of actions to take when quota is exceeded."""
    BLOCK = "block"  # Block the operation
    THROTTLE = "throttle"  # Slow down operations
    NOTIFY = "notify"  # Notify but allow
    UPGRADE = "upgrade"  # Prompt for upgrade
    LOG = "log"  # Just log the overage


class QuotaDefinition:
    """Class representing a quota definition for a resource."""

    def __init__(
        self,
        resource_type: ResourceType,
        quota_type: QuotaType,
        limit: int,
        action: QuotaAction,
        tier_id: str,
        feature: Optional[LicenseFeature] = None,
        reset_day: Optional[int] = None,
        custom_attributes: Optional[Dict[str, str]] = None
    ):
        """
        Initialize quota definition.

        Args:
            resource_type: Type of resource being limited
            quota_type: Time period for the quota
            limit: Maximum allowed usage
            action: Action to take when quota is exceeded
            tier_id: Subscription tier this quota applies to
            feature: Feature this quota is associated with
            reset_day: Day of month/week when quota resets (for MONTHLY/WEEKLY)
            custom_attributes: Additional custom attributes
        """
        self.resource_type = resource_type
        self.quota_type = quota_type
        self.limit = limit
        self.action = action
        self.tier_id = tier_id
        self.feature = feature
        self.reset_day = reset_day
        self.custom_attributes = custom_attributes or {}

    def to_dict(self) -> Dict[str, Union[str, int, Dict[str, str]]]:
        """
        Convert quota definition to dictionary.

        Returns:
            Dictionary representation of the quota definition
        """
        result = {
            "resource_type": self.resource_type.value,
            "quota_type": self.quota_type.value,
            "limit": self.limit,
            "action": self.action.value,
            "tier_id": self.tier_id,
            "custom_attributes": self.custom_attributes
        }

        if self.feature:
            result["feature"] = self.feature.value

        if self.reset_day is not None:
            result["reset_day"] = self.reset_day

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, int, Dict[str, str]]]) -> 'QuotaDefinition':
        """
        Create quota definition from dictionary.

        Args:
            data: Dictionary representation of quota definition

        Returns:
            QuotaDefinition instance
        """
        feature = None
        if "feature" in data:
            feature = LicenseFeature(data["feature"])

        return cls(
            resource_type=ResourceType(data["resource_type"]),
            quota_type=QuotaType(data["quota_type"]),
            limit=data["limit"],
            action=QuotaAction(data["action"]),
            tier_id=data["tier_id"],
            feature=feature,
            reset_day=data.get("reset_day"),
            custom_attributes=data.get("custom_attributes", {})
        )


class UsageRecord:
    """Class representing a usage record for a resource."""

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
        """
        Initialize usage record.

        Args:
            record_id: Unique identifier for the record
            customer_id: Identifier for the customer
            resource_type: Type of resource used
            quantity: Amount of resource used
            timestamp: When the usage occurred
            subscription_id: Associated subscription ID
            feature: Feature associated with the usage
            metadata: Additional metadata about the usage
        """
        self.record_id = record_id
        self.customer_id = customer_id
        self.resource_type = resource_type
        self.quantity = quantity
        self.timestamp = timestamp
        self.subscription_id = subscription_id
        self.feature = feature
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Union[str, int, Dict[str, str]]]:
        """
        Convert usage record to dictionary.

        Returns:
            Dictionary representation of the usage record
        """
        result = {
            "record_id": self.record_id,
            "customer_id": self.customer_id,
            "resource_type": self.resource_type.value,
            "quantity": self.quantity,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

        if self.subscription_id:
            result["subscription_id"] = self.subscription_id

        if self.feature:
            result["feature"] = self.feature.value

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, int, Dict[str, str]]]) -> 'UsageRecord':
        """
        Create usage record from dictionary.

        Args:
            data: Dictionary representation of usage record

        Returns:
            UsageRecord instance
        """
        feature = None
        if "feature" in data:
            feature = LicenseFeature(data["feature"])

        return cls(
            record_id=data["record_id"],
            customer_id=data["customer_id"],
            resource_type=ResourceType(data["resource_type"]),
            quantity=data["quantity"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            subscription_id=data.get("subscription_id"),
            feature=feature,
            metadata=data.get("metadata", {})
        )


class QuotaManager:
    """Class for managing quota definitions."""

    def __init__(self, storage_path: str):
        """
        Initialize quota manager.

        Args:
            storage_path: Path to store quota data
        """
        self.storage_path = storage_path
        self.quotas: Dict[str, QuotaDefinition] = {}
        os.makedirs(storage_path, exist_ok=True)
        self._load_quotas()

    def _get_quotas_file(self) -> str:
        """
        Get path to quotas definition file.

        Returns:
            Path to quotas file
        """
        return os.path.join(self.storage_path, "quota_definitions.json")

    def _load_quotas(self) -> None:
        """Load quota definitions from storage."""
        quotas_file = self._get_quotas_file()
        
        if not os.path.exists(quotas_file):
            # Create default quotas if file doesn't exist
            self._create_default_quotas()
            return

        try:
            with open(quotas_file, "r") as f:
                quotas_data = json.load(f)
                
            for quota_id, quota_data in quotas_data.items():
                quota = QuotaDefinition.from_dict(quota_data)
                self.quotas[quota_id] = quota
        except Exception as e:
            print(f"Failed to load quota definitions: {str(e)}")
            # Create default quotas as fallback
            self._create_default_quotas()

    def _save_quotas(self) -> None:
        """Save quota definitions to storage."""
        quotas_file = self._get_quotas_file()
        
        try:
            quotas_data = {quota_id: quota.to_dict() for quota_id, quota in self.quotas.items()}
            with open(quotas_file, "w") as f:
                json.dump(quotas_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save quota definitions: {str(e)}")

    def _create_default_quotas(self) -> None:
        """Create default quota definitions."""
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
            limit=100 * 1024 * 1024,  # 100 MB
            action=QuotaAction.BLOCK,
            tier_id="free"
        )
        
        self.quotas["free_tokens_monthly"] = QuotaDefinition(
            resource_type=ResourceType.MODEL_TOKENS,
            quota_type=QuotaType.MONTHLY,
            limit=10000,
            action=QuotaAction.BLOCK,
            tier_id="free",
            reset_day=1
        )
        
        # Basic tier quotas
        self.quotas["basic_api_daily"] = QuotaDefinition(
            resource_type=ResourceType.API_CALLS,
            quota_type=QuotaType.DAILY,
            limit=1000,
            action=QuotaAction.THROTTLE,
            tier_id="basic"
        )
        
        self.quotas["basic_storage"] = QuotaDefinition(
            resource_type=ResourceType.STORAGE,
            quota_type=QuotaType.TOTAL,
            limit=1024 * 1024 * 1024,  # 1 GB
            action=QuotaAction.NOTIFY,
            tier_id="basic"
        )
        
        self.quotas["basic_tokens_monthly"] = QuotaDefinition(
            resource_type=ResourceType.MODEL_TOKENS,
            quota_type=QuotaType.MONTHLY,
            limit=100000,
            action=QuotaAction.NOTIFY,
            tier_id="basic",
            reset_day=1
        )
        
        # Professional tier quotas
        self.quotas["pro_api_daily"] = QuotaDefinition(
            resource_type=ResourceType.API_CALLS,
            quota_type=QuotaType.DAILY,
            limit=10000,
            action=QuotaAction.THROTTLE,
            tier_id="professional"
        )
        
        self.quotas["pro_storage"] = QuotaDefinition(
            resource_type=ResourceType.STORAGE,
            quota_type=QuotaType.TOTAL,
            limit=10 * 1024 * 1024 * 1024,  # 10 GB
            action=QuotaAction.NOTIFY,
            tier_id="professional"
        )
        
        self.quotas["pro_tokens_monthly"] = QuotaDefinition(
            resource_type=ResourceType.MODEL_TOKENS,
            quota_type=QuotaType.MONTHLY,
            limit=1000000,
            action=QuotaAction.NOTIFY,
            tier_id="professional",
            reset_day=1
        )
        
        # Enterprise tier quotas
        self.quotas["enterprise_api_daily"] = QuotaDefinition(
            resource_type=ResourceType.API_CALLS,
            quota_type=QuotaType.DAILY,
            limit=100000,
            action=QuotaAction.LOG,
            tier_id="enterprise"
        )
        
        self.quotas["enterprise_storage"] = QuotaDefinition(
            resource_type=ResourceType.STORAGE,
            quota_type=QuotaType.TOTAL,
            limit=100 * 1024 * 1024 * 1024,  # 100 GB
            action=QuotaAction.NOTIFY,
            tier_id="enterprise"
        )
        
        self.quotas["enterprise_tokens_monthly"] = QuotaDefinition(
            resource_type=ResourceType.MODEL_TOKENS,
            quota_type=QuotaType.MONTHLY,
            limit=10000000,
            action=QuotaAction.LOG,
            tier_id="enterprise",
            reset_day=1
        )
        
        # Save default quotas
        self._save_quotas()

    def get_quota(self, quota_id: str) -> Optional[QuotaDefinition]:
        """
        Get quota definition by ID.

        Args:
            quota_id: Quota ID to retrieve

        Returns:
            QuotaDefinition or None if not found
        """
        return self.quotas.get(quota_id)

    def get_quotas_for_tier(self, tier_id: str) -> List[QuotaDefinition]:
        """
        Get all quota definitions for a subscription tier.

        Args:
            tier_id: Subscription tier ID

        Returns:
            List of quota definitions for the tier
        """
        return [quota for quota in self.quotas.values() if quota.tier_id == tier_id]

    def get_quotas_for_resource(self, resource_type: ResourceType) -> List[QuotaDefinition]:
        """
        Get all quota definitions for a resource type.

        Args:
            resource_type: Resource type

        Returns:
            List of quota definitions for the resource type
        """
        return [quota for quota in self.quotas.values() if quota.resource_type == resource_type]

    def add_quota(self, quota_id: str, quota: QuotaDefinition) -> bool:
        """
        Add a new quota definition.

        Args:
            quota_id: Unique ID for the quota
            quota: Quota definition to add

        Returns:
            True if successful, False if quota ID already exists
        """
        if quota_id in self.quotas:
            return False
            
        self.quotas[quota_id] = quota
        self._save_quotas()
        return True

    def update_quota(self, quota_id: str, quota: QuotaDefinition) -> bool:
        """
        Update an existing quota definition.

        Args:
            quota_id: ID of quota to update
            quota: Updated quota definition

        Returns:
            True if successful, False if quota not found
        """
        if quota_id not in self.quotas:
            return False
            
        self.quotas[quota_id] = quota
        self._save_quotas()
        return True

    def delete_quota(self, quota_id: str) -> bool:
        """
        Delete a quota definition.

        Args:
            quota_id: ID of quota to delete

        Returns:
            True if successful, False if quota not found
        """
        if quota_id not in self.quotas:
            return False
            
        del self.quotas[quota_id]
        self._save_quotas()
        return True


class UsageTracker:
    """Class for tracking resource usage."""

    def __init__(self, storage_path: str):
        """
        Initialize usage tracker.

        Args:
            storage_path: Path to store usage data
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Create subdirectories for different time periods
        self.daily_path = os.path.join(storage_path, "daily")
        self.monthly_path = os.path.join(storage_path, "monthly")
        self.customer_path = os.path.join(storage_path, "customers")
        
        os.makedirs(self.daily_path, exist_ok=True)
        os.makedirs(self.monthly_path, exist_ok=True)
        os.makedirs(self.customer_path, exist_ok=True)

    def _get_daily_file(self, date: datetime) -> str:
        """
        Get path to daily usage file.

        Args:
            date: Date for the usage file

        Returns:
            Path to daily usage file
        """
        date_str = date.strftime("%Y-%m-%d")
        return os.path.join(self.daily_path, f"usage_{date_str}.json")

    def _get_monthly_file(self, date: datetime) -> str:
        """
        Get path to monthly usage file.

        Args:
            date: Date for the usage file

        Returns:
            Path to monthly usage file
        """
        month_str = date.strftime("%Y-%m")
        return os.path.join(self.monthly_path, f"usage_{month_str}.json")

    def _get_customer_file(self, customer_id: str) -> str:
        """
        Get path to customer usage file.

        Args:
            customer_id: Customer ID

        Returns:
            Path to customer usage file
        """
        return os.path.join(self.customer_path, f"usage_{customer_id}.json")

    def _append_usage_record(self, file_path: str, record: UsageRecord) -> None:
        """
        Append usage record to a file.

        Args:
            file_path: Path to usage file
            record: Usage record to append
        """
        records = []
        
        # Load existing records if file exists
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    records = json.load(f)
            except Exception:
                records = []
        
        # Append new record
        records.append(record.to_dict())
        
        # Save updated records
        with open(file_path, "w") as f:
            json.dump(records, f, indent=2)

    def track_usage(
        self,
        customer_id: str,
        resource_type: ResourceType,
        quantity: int,
        subscription_id: Optional[str] = None,
        feature: Optional[LicenseFeature] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> UsageRecord:
        """
        Track resource usage.

        Args:
            customer_id: Customer ID
            resource_type: Type of resource used
            quantity: Amount of resource used
            subscription_id: Associated subscription ID
            feature: Feature associated with the usage
            metadata: Additional metadata about the usage

        Returns:
            Created usage record
        """
        # Generate record ID
        import uuid
        record_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.now()
        
        # Create usage record
        record = UsageRecord(
            record_id=record_id,
            customer_id=customer_id,
            resource_type=resource_type,
            quantity=quantity,
            timestamp=timestamp,
            subscription_id=subscription_id,
            feature=feature,
            metadata=metadata
        )
        
        # Append to daily file
        self._append_usage_record(self._get_daily_file(timestamp), record)
        
        # Append to monthly file
        self._append_usage_record(self._get_monthly_file(timestamp), record)
        
        # Append to customer file
        self._append_usage_record(self._get_customer_file(customer_id), record)
        
        return record

    def get_daily_usage(
        self,
        date: datetime,
        customer_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None
    ) -> List[UsageRecord]:
        """
        Get usage records for a specific day.

        Args:
            date: Date to get usage for
            customer_id: Filter by customer ID
            resource_type: Filter by resource type

        Returns:
            List of usage records
        """
        daily_file = self._get_daily_file(date)
        
        if not os.path.exists(daily_file):
            return []
            
        try:
            with open(daily_file, "r") as f:
                records_data = json.load(f)
                
            records = [UsageRecord.from_dict(data) for data in records_data]
            
            # Apply filters
            if customer_id:
                records = [r for r in records if r.customer_id == customer_id]
                
            if resource_type:
                records = [r for r in records if r.resource_type == resource_type]
                
            return records
        except Exception as e:
            print(f"Failed to get daily usage: {str(e)}")
            return []

    def get_monthly_usage(
        self,
        year: int,
        month: int,
        customer_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None
    ) -> List[UsageRecord]:
        """
        Get usage records for a specific month.

        Args:
            year: Year to get usage for
            month: Month to get usage for
            customer_id: Filter by customer ID
            resource_type: Filter by resource type

        Returns:
            List of usage records
        """
        date = datetime(year, month, 1)
        monthly_file = self._get_monthly_file(date)
        
        if not os.path.exists(monthly_file):
            return []
            
        try:
            with open(monthly_file, "r") as f:
                records_data = json.load(f)
                
            records = [UsageRecord.from_dict(data) for data in records_data]
            
            # Apply filters
            if customer_id:
                records = [r for r in records if r.customer_id == customer_id]
                
            if resource_type:
                records = [r for r in records if r.resource_type == resource_type]
                
            return records
        except Exception as e:
            print(f"Failed to get monthly usage: {str(e)}")
            return []

    def get_customer_usage(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        resource_type: Optional[ResourceType] = None
    ) -> List[UsageRecord]:
        """
        Get usage records for a specific customer.

        Args:
            customer_id: Customer ID to get usage for
            start_date: Filter by start date
            end_date: Filter by end date
            resource_type: Filter by resource type

        Returns:
            List of usage records
        """
        customer_file = self._get_customer_file(customer_id)
        
        if not os.path.exists(customer_file):
            return []
            
        try:
            with open(customer_file, "r") as f:
                records_data = json.load(f)
                
            records = [UsageRecord.from_dict(data) for data in records_data]
            
            # Apply filters
            if start_date:
                records = [r for r in records if r.timestamp >= start_date]
                
            if end_date:
                records = [r for r in records if r.timestamp <= end_date]
                
            if resource_type:
                records = [r for r in records if r.resource_type == resource_type]
                
            return records
        except Exception as e:
            print(f"Failed to get customer usage: {str(e)}")
            return []

    def get_usage_summary(
        self,
        customer_id: str,
        resource_type: ResourceType,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """
        Get total usage for a specific resource and time period.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            start_date: Start date for the period
            end_date: End date for the period

        Returns:
            Total usage quantity
        """
        records = self.get_customer_usage(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            resource_type=resource_type
        )
        
        return sum(record.quantity for record in records)

    def get_daily_summary(
        self,
        customer_id: str,
        resource_type: ResourceType,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Get daily usage summary for the past N days.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            days: Number of days to include

        Returns:
            Dictionary mapping date strings to usage quantities
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        records = self.get_customer_usage(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            resource_type=resource_type
        )
        
        # Group by day
        daily_summary = {}
        for record in records:
            date_str = record.timestamp.strftime("%Y-%m-%d")
            if date_str not in daily_summary:
                daily_summary[date_str] = 0
            daily_summary[date_str] += record.quantity
            
        return daily_summary

    def get_resource_usage_by_customer(
        self,
        resource_type: ResourceType,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """
        Get usage of a resource grouped by customer.

        Args:
            resource_type: Resource type
            start_date: Start date for the period
            end_date: End date for the period

        Returns:
            Dictionary mapping customer IDs to usage quantities
        """
        # This would be more efficient with a database
        # For file-based storage, we need to scan all daily files
        
        current_date = start_date
        customer_usage = {}
        
        while current_date <= end_date:
            records = self.get_daily_usage(
                date=current_date,
                resource_type=resource_type
            )
            
            for record in records:
                if record.customer_id not in customer_usage:
                    customer_usage[record.customer_id] = 0
                customer_usage[record.customer_id] += record.quantity
                
            current_date += timedelta(days=1)
            
        return customer_usage


class QuotaEnforcer:
    """Class for enforcing usage quotas."""

    def __init__(
        self,
        quota_manager: QuotaManager,
        usage_tracker: UsageTracker,
        subscription_service: SubscriptionService
    ):
        """
        Initialize quota enforcer.

        Args:
            quota_manager: Manager for quota definitions
            usage_tracker: Tracker for resource usage
            subscription_service: Service for subscription management
        """
        self.quota_manager = quota_manager
        self.usage_tracker = usage_tracker
        self.subscription_service = subscription_service

    def _get_applicable_quota(
        self,
        customer_id: str,
        resource_type: ResourceType
    ) -> Optional[QuotaDefinition]:
        """
        Get the applicable quota for a customer and resource.

        Args:
            customer_id: Customer ID
            resource_type: Resource type

        Returns:
            Applicable quota definition or None
        """
        # Get active subscriptions for the customer
        active_subscriptions = self.subscription_service.get_active_customer_subscriptions(customer_id)
        
        if not active_subscriptions:
            # No active subscriptions, use free tier quotas
            quotas = self.quota_manager.get_quotas_for_tier("free")
            for quota in quotas:
                if quota.resource_type == resource_type:
                    return quota
            return None
            
        # Find the most permissive quota across all subscriptions
        applicable_quota = None
        highest_limit = -1
        
        for subscription in active_subscriptions:
            quotas = self.quota_manager.get_quotas_for_tier(subscription.tier_id)
            for quota in quotas:
                if quota.resource_type == resource_type and quota.limit > highest_limit:
                    applicable_quota = quota
                    highest_limit = quota.limit
                    
        return applicable_quota

    def _get_current_usage(
        self,
        customer_id: str,
        resource_type: ResourceType,
        quota_type: QuotaType
    ) -> int:
        """
        Get current usage for a specific quota type.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            quota_type: Quota type (daily, monthly, etc.)

        Returns:
            Current usage quantity
        """
        now = datetime.now()
        
        if quota_type == QuotaType.DAILY:
            # Daily quota - get usage for today
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            
        elif quota_type == QuotaType.WEEKLY:
            # Weekly quota - get usage for this week
            # Assuming weeks start on Monday (0 = Monday in Python's weekday())
            days_since_monday = now.weekday()
            start_date = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            
        elif quota_type == QuotaType.MONTHLY:
            # Monthly quota - get usage for this month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            
        elif quota_type == QuotaType.ANNUAL:
            # Annual quota - get usage for this year
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            
        else:  # QuotaType.TOTAL
            # Total quota - get all usage
            start_date = datetime(2000, 1, 1)  # Far in the past
            end_date = now
            
        return self.usage_tracker.get_usage_summary(
            customer_id=customer_id,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date
        )

    def check_quota(
        self,
        customer_id: str,
        resource_type: ResourceType,
        quantity: int
    ) -> Tuple[bool, Optional[QuotaAction], Optional[str]]:
        """
        Check if a usage operation would exceed quota.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            quantity: Quantity to check

        Returns:
            Tuple of (allowed, action, message)
        """
        # Get applicable quota
        quota = self._get_applicable_quota(customer_id, resource_type)
        
        if not quota:
            # No quota defined, allow the operation
            return True, None, None
            
        # Get current usage
        current_usage = self._get_current_usage(
            customer_id=customer_id,
            resource_type=resource_type,
            quota_type=quota.quota_type
        )
        
        # Check if operation would exceed quota
        if current_usage + quantity > quota.limit:
            message = (
                f"Quota exceeded for {resource_type.value}. "
                f"Current usage: {current_usage}, "
                f"Requested: {quantity}, "
                f"Limit: {quota.limit}"
            )
            
            # For BLOCK action, deny the operation
            if quota.action == QuotaAction.BLOCK:
                return False, quota.action, message
                
            # For other actions, allow but return the action
            return True, quota.action, message
            
        # Within quota, allow the operation
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
        """
        Track usage and enforce quota in one operation.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            quantity: Quantity to track
            subscription_id: Associated subscription ID
            feature: Feature associated with the usage
            metadata: Additional metadata about the usage

        Returns:
            Tuple of (allowed, usage_record, message)
        """
        # Check quota first
        allowed, action, message = self.check_quota(
            customer_id=customer_id,
            resource_type=resource_type,
            quantity=quantity
        )
        
        if not allowed:
            # Quota exceeded and action is BLOCK
            return False, None, message
            
        # Track the usage
        record = self.usage_tracker.track_usage(
            customer_id=customer_id,
            resource_type=resource_type,
            quantity=quantity,
            subscription_id=subscription_id,
            feature=feature,
            metadata=metadata
        )
        
        # Return result based on action
        if action:
            # Quota will be exceeded but operation is allowed
            return True, record, message
            
        # Within quota
        return True, record, None

    def get_quota_status(
        self,
        customer_id: str,
        resource_type: ResourceType
    ) -> Dict[str, Union[int, float, str]]:
        """
        Get quota status for a customer and resource.

        Args:
            customer_id: Customer ID
            resource_type: Resource type

        Returns:
            Dictionary with quota status information
        """
        # Get applicable quota
        quota = self._get_applicable_quota(customer_id, resource_type)
        
        if not quota:
            return {
                "has_quota": False,
                "resource_type": resource_type.value
            }
            
        # Get current usage
        current_usage = self._get_current_usage(
            customer_id=customer_id,
            resource_type=resource_type,
            quota_type=quota.quota_type
        )
        
        # Calculate percentage used
        percentage_used = (current_usage / quota.limit) * 100 if quota.limit > 0 else 100
        
        return {
            "has_quota": True,
            "resource_type": resource_type.value,
            "quota_type": quota.quota_type.value,
            "limit": quota.limit,
            "current_usage": current_usage,
            "remaining": max(0, quota.limit - current_usage),
            "percentage_used": percentage_used,
            "action_on_exceed": quota.action.value,
            "tier_id": quota.tier_id
        }

    def get_all_quota_statuses(self, customer_id: str) -> Dict[str, Dict[str, Union[int, float, str]]]:
        """
        Get status for all quotas applicable to a customer.

        Args:
            customer_id: Customer ID

        Returns:
            Dictionary mapping resource types to quota status information
        """
        # Get active subscriptions for the customer
        active_subscriptions = self.subscription_service.get_active_customer_subscriptions(customer_id)
        
        tier_ids = ["free"]  # Always include free tier
        if active_subscriptions:
            tier_ids.extend([sub.tier_id for sub in active_subscriptions])
            
        # Get all quotas for these tiers
        all_quotas = []
        for tier_id in tier_ids:
            all_quotas.extend(self.quota_manager.get_quotas_for_tier(tier_id))
            
        # Get unique resource types
        resource_types = set(quota.resource_type for quota in all_quotas)
        
        # Get status for each resource type
        statuses = {}
        for resource_type in resource_types:
            status = self.get_quota_status(customer_id, resource_type)
            statuses[resource_type.value] = status
            
        return statuses


class UsageAnalytics:
    """Class for generating usage analytics."""

    def __init__(self, usage_tracker: UsageTracker):
        """
        Initialize usage analytics.

        Args:
            usage_tracker: Tracker for resource usage
        """
        self.usage_tracker = usage_tracker

    def get_usage_trend(
        self,
        customer_id: str,
        resource_type: ResourceType,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Get usage trend for the past N days.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            days: Number of days to include

        Returns:
            Dictionary mapping date strings to usage quantities
        """
        return self.usage_tracker.get_daily_summary(
            customer_id=customer_id,
            resource_type=resource_type,
            days=days
        )

    def get_resource_distribution(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """
        Get distribution of usage across different resource types.

        Args:
            customer_id: Customer ID
            start_date: Start date for the period
            end_date: End date for the period

        Returns:
            Dictionary mapping resource types to usage quantities
        """
        # Get all resource types
        resource_types = [rt for rt in ResourceType]
        
        # Get usage for each resource type
        distribution = {}
        for resource_type in resource_types:
            usage = self.usage_tracker.get_usage_summary(
                customer_id=customer_id,
                resource_type=resource_type,
                start_date=start_date,
                end_date=end_date
            )
            
            if usage > 0:
                distribution[resource_type.value] = usage
                
        return distribution

    def get_feature_usage(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """
        Get usage grouped by feature.

        Args:
            customer_id: Customer ID
            start_date: Start date for the period
            end_date: End date for the period

        Returns:
            Dictionary mapping features to usage quantities
        """
        # Get all usage records for the period
        records = self.usage_tracker.get_customer_usage(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Group by feature
        feature_usage = {}
        for record in records:
            feature_key = record.feature.value if record.feature else "unknown"
            
            if feature_key not in feature_usage:
                feature_usage[feature_key] = 0
                
            feature_usage[feature_key] += record.quantity
            
        return feature_usage

    def get_usage_by_subscription(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """
        Get usage grouped by subscription.

        Args:
            customer_id: Customer ID
            start_date: Start date for the period
            end_date: End date for the period

        Returns:
            Dictionary mapping subscription IDs to usage quantities
        """
        # Get all usage records for the period
        records = self.usage_tracker.get_customer_usage(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Group by subscription
        subscription_usage = {}
        for record in records:
            subscription_key = record.subscription_id or "unknown"
            
            if subscription_key not in subscription_usage:
                subscription_usage[subscription_key] = 0
                
            subscription_usage[subscription_key] += record.quantity
            
        return subscription_usage

    def get_usage_report(
        self,
        customer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Union[Dict[str, int], int]]:
        """
        Generate a comprehensive usage report.

        Args:
            customer_id: Customer ID
            start_date: Start date for the period
            end_date: End date for the period

        Returns:
            Dictionary with various usage metrics
        """
        # Get all usage records for the period
        records = self.usage_tracker.get_customer_usage(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculate total usage
        total_usage = sum(record.quantity for record in records)
        
        # Group by resource type
        resource_usage = {}
        for record in records:
            resource_key = record.resource_type.value
            
            if resource_key not in resource_usage:
                resource_usage[resource_key] = 0
                
            resource_usage[resource_key] += record.quantity
            
        # Group by feature
        feature_usage = {}
        for record in records:
            feature_key = record.feature.value if record.feature else "unknown"
            
            if feature_key not in feature_usage:
                feature_usage[feature_key] = 0
                
            feature_usage[feature_key] += record.quantity
            
        # Group by day
        daily_usage = {}
        for record in records:
            date_key = record.timestamp.strftime("%Y-%m-%d")
            
            if date_key not in daily_usage:
                daily_usage[date_key] = 0
                
            daily_usage[date_key] += record.quantity
            
        # Return comprehensive report
        return {
            "total_usage": total_usage,
            "resource_usage": resource_usage,
            "feature_usage": feature_usage,
            "daily_usage": daily_usage,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }

    def get_top_customers(
        self,
        resource_type: ResourceType,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> Dict[str, int]:
        """
        Get top customers by usage for a specific resource.

        Args:
            resource_type: Resource type
            start_date: Start date for the period
            end_date: End date for the period
            limit: Maximum number of customers to return

        Returns:
            Dictionary mapping customer IDs to usage quantities
        """
        # Get usage by customer
        customer_usage = self.usage_tracker.get_resource_usage_by_customer(
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date
        )
        
        # Sort by usage (descending)
        sorted_customers = sorted(
            customer_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top N customers
        return dict(sorted_customers[:limit])


class UsageService:
    """Main service class for usage tracking and quota management."""

    def __init__(
        self,
        quota_manager: QuotaManager,
        usage_tracker: UsageTracker,
        quota_enforcer: QuotaEnforcer,
        usage_analytics: UsageAnalytics
    ):
        """
        Initialize usage service.

        Args:
            quota_manager: Manager for quota definitions
            usage_tracker: Tracker for resource usage
            quota_enforcer: Enforcer for usage quotas
            usage_analytics: Analytics for usage data
        """
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
        """
        Track resource usage with optional quota enforcement.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            quantity: Quantity to track
            subscription_id: Associated subscription ID
            feature: Feature associated with the usage
            metadata: Additional metadata about the usage
            enforce_quota: Whether to enforce quota

        Returns:
            Tuple of (allowed, usage_record, message)
        """
        if enforce_quota:
            return self.quota_enforcer.track_and_enforce(
                customer_id=customer_id,
                resource_type=resource_type,
                quantity=quantity,
                subscription_id=subscription_id,
                feature=feature,
                metadata=metadata
            )
        else:
            # Just track without enforcing
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
    ) -> Union[Dict[str, Union[int, float, str]], Dict[str, Dict[str, Union[int, float, str]]]]:
        """
        Get quota status for a customer.

        Args:
            customer_id: Customer ID
            resource_type: Resource type or None for all resources

        Returns:
            Quota status information
        """
        if resource_type:
            return self.quota_enforcer.get_quota_status(
                customer_id=customer_id,
                resource_type=resource_type
            )
        else:
            return self.quota_enforcer.get_all_quota_statuses(customer_id)

    def get_usage_report(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "month"
    ) -> Dict[str, Union[Dict[str, int], int]]:
        """
        Generate a usage report for a customer.

        Args:
            customer_id: Customer ID
            start_date: Start date or None for automatic period
            end_date: End date or None for automatic period
            period: Period type if dates not provided ("day", "week", "month", "year")

        Returns:
            Usage report data
        """
        # Set default dates based on period if not provided
        now = datetime.now()
        
        if not end_date:
            end_date = now
            
        if not start_date:
            if period == "day":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                days_since_monday = now.weekday()
                start_date = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "month":
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "year":
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                # Default to last 30 days
                start_date = now - timedelta(days=30)
                
        return self.usage_analytics.get_usage_report(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )

    def get_usage_trend(
        self,
        customer_id: str,
        resource_type: ResourceType,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Get usage trend for a customer.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            days: Number of days to include

        Returns:
            Usage trend data
        """
        return self.usage_analytics.get_usage_trend(
            customer_id=customer_id,
            resource_type=resource_type,
            days=days
        )

    def update_quota_definition(
        self,
        quota_id: str,
        resource_type: ResourceType,
        quota_type: QuotaType,
        limit: int,
        action: QuotaAction,
        tier_id: str,
        feature: Optional[LicenseFeature] = None,
        reset_day: Optional[int] = None
    ) -> bool:
        """
        Update or create a quota definition.

        Args:
            quota_id: Quota ID
            resource_type: Resource type
            quota_type: Quota type
            limit: Usage limit
            action: Action on exceed
            tier_id: Subscription tier ID
            feature: Associated feature
            reset_day: Day for quota reset

        Returns:
            True if successful, False otherwise
        """
        quota = QuotaDefinition(
            resource_type=resource_type,
            quota_type=quota_type,
            limit=limit,
            action=action,
            tier_id=tier_id,
            feature=feature,
            reset_day=reset_day
        )
        
        # Try to update first
        if self.quota_manager.update_quota(quota_id, quota):
            return True
            
        # If update fails, try to add
        return self.quota_manager.add_quota(quota_id, quota)

    def delete_quota_definition(self, quota_id: str) -> bool:
        """
        Delete a quota definition.

        Args:
            quota_id: Quota ID to delete

        Returns:
            True if successful, False otherwise
        """
        return self.quota_manager.delete_quota(quota_id)

    def get_customer_resource_usage(
        self,
        customer_id: str,
        resource_type: ResourceType,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """
        Get total usage for a specific resource and time period.

        Args:
            customer_id: Customer ID
            resource_type: Resource type
            start_date: Start date
            end_date: End date

        Returns:
            Total usage quantity
        """
        return self.usage_tracker.get_usage_summary(
            customer_id=customer_id,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date
        )


if __name__ == "__main__":
    # Example usage
    from subscription.core.subscription_manager import SubscriptionManager, SubscriptionRepository, FeatureGate, SubscriptionService
    
    # Create managers and services
    subscription_manager = SubscriptionManager("subscription_data")
    subscription_repository = SubscriptionRepository("subscription_data")
    feature_gate = FeatureGate(subscription_manager, subscription_repository)
    subscription_service = SubscriptionService(subscription_manager, subscription_repository, feature_gate)
    
    quota_manager = QuotaManager("usage_data")
    usage_tracker = UsageTracker("usage_data")
    quota_enforcer = QuotaEnforcer(quota_manager, usage_tracker, subscription_service)
    usage_analytics = UsageAnalytics(usage_tracker)
    
    usage_service = UsageService(quota_manager, usage_tracker, quota_enforcer, usage_analytics)
    
    # Track some usage
    allowed, record, message = usage_service.track_usage(
        customer_id="customer123",
        resource_type=ResourceType.API_CALLS,
        quantity=10,
        subscription_id="subscription456",
        feature=LicenseFeature.CORE,
        metadata={"endpoint": "/api/data", "method": "GET"}
    )
    
    print(f"Usage tracking allowed: {allowed}")
    if message:
        print(f"Message: {message}")
        
    # Check quota status
    status = usage_service.get_quota_status("customer123", ResourceType.API_CALLS)
    print(f"Quota status: {status}")
    
    # Get usage report
    now = datetime.now()
    start_date = now - timedelta(days=30)
    report = usage_service.get_usage_report("customer123", start_date, now)
    print(f"Total usage: {report['total_usage']}")
    
    # Get usage trend
    trend = usage_service.get_usage_trend("customer123", ResourceType.API_CALLS)
    print(f"Usage trend: {trend}")
