# src/core/subscription_manager.py
from enum import Enum
from typing import List, Dict, Any, Optional, Set
import datetime

# --- Define Subscription Tiers and Features ---

class Feature(Enum):
    # Core Features (Potentially Free or Basic Tier)
    BASIC_LLM_ACCESS = "basic_llm_access"  # Access to a default set of LLMs
    STANDARD_WEB_AUTOMATION = "standard_web_automation"
    STANDARD_DESKTOP_AUTOMATION = "standard_desktop_automation"
    PROJECT_BASED_CHAT = "project_based_chat"
    BASIC_TASK_ORCHESTRATION = "basic_task_orchestration"

    # Advanced Features (Potentially Premium Tiers)
    ADVANCED_LLM_ACCESS = "advanced_llm_access"  # Access to more powerful/specialized LLMs
    LOCAL_LLM_USAGE = "local_llm_usage"
    UNLIMITED_WEB_AUTOMATION = "unlimited_web_automation" # Higher limits or more complex scenarios
    ADVANCED_DESKTOP_AUTOMATION = "advanced_desktop_automation" # More complex app interactions
    PRIORITY_SUPPORT = "priority_support"
    CUSTOM_PLUGIN_DEVELOPMENT = "custom_plugin_development"
    UNLIMITED_TASK_HISTORY = "unlimited_task_history"
    COLLABORATIVE_PROJECTS = "collaborative_projects"
    API_ACCESS_FOR_INTEGRATION = "api_access_for_integration"

class SubscriptionTier:
    def __init__(self, tier_id: str, name: str, price_monthly: float, features: Set[Feature], description: Optional[str] = None):
        self.tier_id = tier_id
        self.name = name
        self.price_monthly = price_monthly
        self.features = features
        self.description = description

    def has_feature(self, feature: Feature) -> bool:
        return feature in self.features

# Define available tiers
# These are examples and can be configured elsewhere (e.g., a config file or database)
AVAILABLE_TIERS: Dict[str, SubscriptionTier] = {
    "free": SubscriptionTier(
        tier_id="free",
        name="Free Tier",
        price_monthly=0.00,
        features={
            Feature.BASIC_LLM_ACCESS,
            Feature.STANDARD_WEB_AUTOMATION, # Limited usage
            Feature.PROJECT_BASED_CHAT
        },
        description="Basic features for individual use with limitations."
    ),
    "basic": SubscriptionTier(
        tier_id="basic",
        name="Basic Plan",
        price_monthly=9.99,
        features={
            Feature.BASIC_LLM_ACCESS,
            Feature.STANDARD_WEB_AUTOMATION,
            Feature.STANDARD_DESKTOP_AUTOMATION, # Limited usage
            Feature.PROJECT_BASED_CHAT,
            Feature.BASIC_TASK_ORCHESTRATION,
            Feature.UNLIMITED_TASK_HISTORY
        },
        description="More features and higher usage limits for regular users."
    ),
    "premium": SubscriptionTier(
        tier_id="premium",
        name="Premium Plan",
        price_monthly=29.99,
        features={
            Feature.ADVANCED_LLM_ACCESS,
            Feature.LOCAL_LLM_USAGE,
            Feature.UNLIMITED_WEB_AUTOMATION,
            Feature.ADVANCED_DESKTOP_AUTOMATION,
            Feature.PROJECT_BASED_CHAT,
            Feature.BASIC_TASK_ORCHESTRATION,
            Feature.UNLIMITED_TASK_HISTORY,
            Feature.PRIORITY_SUPPORT,
            Feature.COLLABORATIVE_PROJECTS
        },
        description="Full access to all features, including advanced capabilities and local LLM usage."
    ),
    "enterprise": SubscriptionTier(
        tier_id="enterprise",
        name="Enterprise Plan",
        price_monthly=99.99, # Or custom pricing
        features=set(Feature), # All features
        description="All features, plus custom plugin development support and API access for business integration."
    )
}
AVAILABLE_TIERS["enterprise"].features.add(Feature.CUSTOM_PLUGIN_DEVELOPMENT)
AVAILABLE_TIERS["enterprise"].features.add(Feature.API_ACCESS_FOR_INTEGRATION)


# --- User Subscription Management ---

class UserSubscription:
    def __init__(self, user_id: str, tier_id: str, start_date: datetime.datetime, end_date: Optional[datetime.datetime] = None, is_active: bool = True):
        self.user_id = user_id
        self.tier_id = tier_id
        self.start_date = start_date
        self.end_date = end_date # None for non-expiring or manually managed subscriptions initially
        self.is_active = is_active
        self.tier: Optional[SubscriptionTier] = AVAILABLE_TIERS.get(tier_id)

    def is_subscription_active(self) -> bool:
        if not self.is_active:
            return False
        if self.end_date and datetime.datetime.now(datetime.timezone.utc) > self.end_date.replace(tzinfo=datetime.timezone.utc):
            return False
        return True

    def has_feature_access(self, feature: Feature) -> bool:
        if not self.is_subscription_active() or not self.tier:
            return False
        return self.tier.has_feature(feature)

# --- Subscription Manager Service ---

class SubscriptionManager:
    def __init__(self):
        # In a real application, this would interact with a database.
        # For this framework, we_ll use an in-memory dictionary for user subscriptions.
        self.user_subscriptions: Dict[str, UserSubscription] = {}

    def get_available_tiers(self) -> List[SubscriptionTier]:
        return list(AVAILABLE_TIERS.values())

    def get_tier_by_id(self, tier_id: str) -> Optional[SubscriptionTier]:
        return AVAILABLE_TIERS.get(tier_id)

    def subscribe_user(self, user_id: str, tier_id: str, duration_days: Optional[int] = None) -> Optional[UserSubscription]:
        if tier_id not in AVAILABLE_TIERS:
            print(f"Error: Tier ID 	{tier_id}	 not found.")
            return None
        
        start_date = datetime.datetime.now(datetime.timezone.utc)
        end_date = None
        if duration_days:
            end_date = start_date + datetime.timedelta(days=duration_days)
        
        subscription = UserSubscription(user_id, tier_id, start_date, end_date)
        self.user_subscriptions[user_id] = subscription
        print(f"User {user_id} subscribed to {AVAILABLE_TIERS[tier_id].name}. Active until: {end_date or 'Perpetual'}")
        return subscription

    def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        return self.user_subscriptions.get(user_id)

    def check_feature_access(self, user_id: str, feature: Feature) -> bool:
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            # Default to free tier or no access if no explicit subscription
            # For simplicity, let_s assume a new user might get free tier by default
            # This logic would be more complex in a real system (e.g., user creation assigns default tier)
            free_tier_sub = UserSubscription(user_id, "free", datetime.datetime.now(datetime.timezone.utc))
            return free_tier_sub.has_feature_access(feature)
        
        return subscription.has_feature_access(feature)

    def cancel_subscription(self, user_id: str) -> bool:
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].is_active = False
            # Optionally set end_date to now if it_s a hard cancel
            # self.user_subscriptions[user_id].end_date = datetime.datetime.now(datetime.timezone.utc)
            print(f"Subscription for user {user_id} has been marked as inactive.")
            return True
        print(f"No active subscription found for user {user_id} to cancel.")
        return False

# Example Usage (Conceptual - would be integrated into the agent_s user management)
# if __name__ == "__main__":
#     manager = SubscriptionManager()

#     # Get available tiers
#     tiers = manager.get_available_tiers()
#     for tier in tiers:
#         print(f"Tier: {tier.name}, Price: ${tier.price_monthly}/month, Features: {[f.name for f in tier.features]}")

#     # Simulate a user subscribing
#     user1_id = "user_123"
#     manager.subscribe_user(user1_id, "premium", duration_days=30)

#     # Check feature access
#     print(f"User {user1_id} has access to LOCAL_LLM_USAGE: {manager.check_feature_access(user1_id, Feature.LOCAL_LLM_USAGE)}")
#     print(f"User {user1_id} has access to CUSTOM_PLUGIN_DEVELOPMENT: {manager.check_feature_access(user1_id, Feature.CUSTOM_PLUGIN_DEVELOPMENT)}")

#     user2_id = "user_456" # New user, defaults to free tier access check
#     print(f"User {user2_id} (default) has access to BASIC_LLM_ACCESS: {manager.check_feature_access(user2_id, Feature.BASIC_LLM_ACCESS)}")
#     print(f"User {user2_id} (default) has access to LOCAL_LLM_USAGE: {manager.check_feature_access(user2_id, Feature.LOCAL_LLM_USAGE)}")

#     manager.subscribe_user(user2_id, "basic")
#     print(f"User {user2_id} (basic) has access to LOCAL_LLM_USAGE: {manager.check_feature_access(user2_id, Feature.LOCAL_LLM_USAGE)}")


