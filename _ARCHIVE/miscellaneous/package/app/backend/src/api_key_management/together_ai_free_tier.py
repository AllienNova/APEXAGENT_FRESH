"""
Free tier manager for Together AI integration.

This module implements the free tier manager for Together AI integration,
handling user access control, quota enforcement, and feature gating.
"""

import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, List, Any, Set, Tuple

from src.api_key_management.together_ai_model_selector import (
    get_together_ai_model_selector,
    ModelModality,
    ModelPurpose,
    TogetherAIModelSelector
)
from src.user.subscription import UserTier, get_user_tier
from src.config.feature_flags import FeatureFlag, is_feature_enabled
from src.monitoring.metrics import record_usage, record_quota_exceeded
from src.admin.dashboard.models import QuotaConfig, QuotaUsage

logger = logging.getLogger(__name__)

class FreeTierFeature(str, Enum):
    """Enum for free tier features."""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    VISION_ANALYSIS = "vision_analysis"
    IMAGE_GENERATION = "image_generation"
    AUDIO_TTS = "audio_tts"
    AUDIO_STT = "audio_stt"

class FreeTierQuotaType(str, Enum):
    """Enum for free tier quota types."""
    REQUESTS_PER_DAY = "requests_per_day"
    TOKENS_PER_DAY = "tokens_per_day"
    TOKENS_PER_REQUEST = "tokens_per_request"
    IMAGES_PER_DAY = "images_per_day"
    AUDIO_MINUTES_PER_DAY = "audio_minutes_per_day"

class TogetherAIFreeTierManager:
    """
    Free tier manager for Together AI integration.
    
    This class handles user access control, quota enforcement, and
    feature gating for the free tier of Together AI integration.
    """
    
    # Default quotas for free tier
    DEFAULT_QUOTAS = {
        FreeTierQuotaType.REQUESTS_PER_DAY: {
            FreeTierFeature.TEXT_GENERATION: 50,
            FreeTierFeature.CODE_GENERATION: 30,
            FreeTierFeature.VISION_ANALYSIS: 20,
            FreeTierFeature.IMAGE_GENERATION: 10,
            FreeTierFeature.AUDIO_TTS: 15,
            FreeTierFeature.AUDIO_STT: 15,
        },
        FreeTierQuotaType.TOKENS_PER_DAY: {
            FreeTierFeature.TEXT_GENERATION: 50000,
            FreeTierFeature.CODE_GENERATION: 30000,
        },
        FreeTierQuotaType.TOKENS_PER_REQUEST: {
            FreeTierFeature.TEXT_GENERATION: 2000,
            FreeTierFeature.CODE_GENERATION: 3000,
        },
        FreeTierQuotaType.IMAGES_PER_DAY: {
            FreeTierFeature.IMAGE_GENERATION: 10,
        },
        FreeTierQuotaType.AUDIO_MINUTES_PER_DAY: {
            FreeTierFeature.AUDIO_TTS: 10,
            FreeTierFeature.AUDIO_STT: 10,
        },
    }
    
    # Mapping from modality to feature
    MODALITY_TO_FEATURE = {
        ModelModality.TEXT: FreeTierFeature.TEXT_GENERATION,
        ModelModality.CODE: FreeTierFeature.CODE_GENERATION,
        ModelModality.VISION: FreeTierFeature.VISION_ANALYSIS,
        ModelModality.IMAGE: FreeTierFeature.IMAGE_GENERATION,
        ModelModality.AUDIO_TTS: FreeTierFeature.AUDIO_TTS,
        ModelModality.AUDIO_STT: FreeTierFeature.AUDIO_STT,
    }
    
    def __init__(self):
        """Initialize the free tier manager."""
        self.model_selector = get_together_ai_model_selector()
        self.usage_data = {}
        self.last_reset = {}
        self.custom_quotas = {}
    
    def _get_feature_for_modality(self, modality: ModelModality) -> FreeTierFeature:
        """
        Get the corresponding feature for a modality.
        
        Args:
            modality: Model modality
            
        Returns:
            Corresponding free tier feature
        """
        return self.MODALITY_TO_FEATURE.get(modality, FreeTierFeature.TEXT_GENERATION)
    
    def _get_quota(
        self,
        user_id: str,
        quota_type: FreeTierQuotaType,
        feature: FreeTierFeature
    ) -> int:
        """
        Get the quota for a specific user, type, and feature.
        
        Args:
            user_id: User identifier
            quota_type: Quota type
            feature: Feature
            
        Returns:
            Quota value
        """
        # Check for custom quota
        if user_id in self.custom_quotas:
            user_quotas = self.custom_quotas[user_id]
            if quota_type in user_quotas and feature in user_quotas[quota_type]:
                return user_quotas[quota_type][feature]
        
        # Fall back to default quota
        return self.DEFAULT_QUOTAS.get(quota_type, {}).get(feature, 0)
    
    def _get_usage(
        self,
        user_id: str,
        quota_type: FreeTierQuotaType,
        feature: FreeTierFeature
    ) -> int:
        """
        Get the current usage for a specific user, type, and feature.
        
        Args:
            user_id: User identifier
            quota_type: Quota type
            feature: Feature
            
        Returns:
            Current usage value
        """
        # Check if usage data exists
        if user_id not in self.usage_data:
            self.usage_data[user_id] = {}
        
        user_usage = self.usage_data[user_id]
        
        # Check if quota type exists
        if quota_type not in user_usage:
            user_usage[quota_type] = {}
        
        # Check if feature exists
        if feature not in user_usage[quota_type]:
            user_usage[quota_type][feature] = 0
        
        # Check if reset is needed
        self._check_reset_usage(user_id)
        
        return user_usage[quota_type][feature]
    
    def _increment_usage(
        self,
        user_id: str,
        quota_type: FreeTierQuotaType,
        feature: FreeTierFeature,
        amount: int = 1
    ) -> None:
        """
        Increment usage for a specific user, type, and feature.
        
        Args:
            user_id: User identifier
            quota_type: Quota type
            feature: Feature
            amount: Amount to increment
        """
        # Check if usage data exists
        if user_id not in self.usage_data:
            self.usage_data[user_id] = {}
        
        user_usage = self.usage_data[user_id]
        
        # Check if quota type exists
        if quota_type not in user_usage:
            user_usage[quota_type] = {}
        
        # Check if feature exists
        if feature not in user_usage[quota_type]:
            user_usage[quota_type][feature] = 0
        
        # Increment usage
        user_usage[quota_type][feature] += amount
        
        # Record usage in monitoring
        record_usage(
            provider="together_ai",
            tier="free",
            feature=str(feature),
            quota_type=str(quota_type),
            amount=amount
        )
    
    def _check_reset_usage(self, user_id: str) -> None:
        """
        Check if usage should be reset for a user.
        
        Args:
            user_id: User identifier
        """
        current_time = datetime.now()
        
        # Check if last reset exists
        if user_id not in self.last_reset:
            self.last_reset[user_id] = current_time
            return
        
        last_reset = self.last_reset[user_id]
        
        # Check if a day has passed since last reset
        if current_time.date() > last_reset.date():
            # Reset daily quotas
            if user_id in self.usage_data:
                user_usage = self.usage_data[user_id]
                
                # Reset requests per day
                if FreeTierQuotaType.REQUESTS_PER_DAY in user_usage:
                    user_usage[FreeTierQuotaType.REQUESTS_PER_DAY] = {}
                
                # Reset tokens per day
                if FreeTierQuotaType.TOKENS_PER_DAY in user_usage:
                    user_usage[FreeTierQuotaType.TOKENS_PER_DAY] = {}
                
                # Reset images per day
                if FreeTierQuotaType.IMAGES_PER_DAY in user_usage:
                    user_usage[FreeTierQuotaType.IMAGES_PER_DAY] = {}
                
                # Reset audio minutes per day
                if FreeTierQuotaType.AUDIO_MINUTES_PER_DAY in user_usage:
                    user_usage[FreeTierQuotaType.AUDIO_MINUTES_PER_DAY] = {}
            
            # Update last reset
            self.last_reset[user_id] = current_time
            
            logger.info(f"Reset daily quotas for user {user_id}")
    
    def set_custom_quota(
        self,
        user_id: str,
        quota_type: FreeTierQuotaType,
        feature: FreeTierFeature,
        value: int
    ) -> None:
        """
        Set a custom quota for a specific user, type, and feature.
        
        Args:
            user_id: User identifier
            quota_type: Quota type
            feature: Feature
            value: Quota value
        """
        # Check if custom quotas exist for user
        if user_id not in self.custom_quotas:
            self.custom_quotas[user_id] = {}
        
        user_quotas = self.custom_quotas[user_id]
        
        # Check if quota type exists
        if quota_type not in user_quotas:
            user_quotas[quota_type] = {}
        
        # Set custom quota
        user_quotas[quota_type][feature] = value
        
        logger.info(f"Set custom quota for user {user_id}: {quota_type}/{feature} = {value}")
    
    def is_free_tier_enabled(self) -> bool:
        """
        Check if free tier is enabled globally.
        
        Returns:
            True if free tier is enabled, False otherwise
        """
        return is_feature_enabled(FeatureFlag.TOGETHER_AI_FREE_TIER)
    
    def is_feature_enabled(self, feature: FreeTierFeature) -> bool:
        """
        Check if a specific feature is enabled for free tier.
        
        Args:
            feature: Feature to check
            
        Returns:
            True if feature is enabled, False otherwise
        """
        if not self.is_free_tier_enabled():
            return False
        
        # Check feature-specific flag
        flag_name = f"TOGETHER_AI_FREE_TIER_{feature.upper()}"
        return is_feature_enabled(flag_name)
    
    def can_use_feature(
        self,
        user_id: str,
        feature: FreeTierFeature
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a user can use a specific feature.
        
        Args:
            user_id: User identifier
            feature: Feature to check
            
        Returns:
            Tuple of (can_use, reason)
        """
        # Check if user is on free tier
        user_tier = get_user_tier(user_id)
        if user_tier != UserTier.FREE:
            # Premium users bypass free tier restrictions
            return True, None
        
        # Check if free tier is enabled
        if not self.is_free_tier_enabled():
            return False, "Free tier is not enabled"
        
        # Check if feature is enabled
        if not self.is_feature_enabled(feature):
            return False, f"Feature {feature} is not enabled for free tier"
        
        # Check requests per day quota
        requests_used = self._get_usage(user_id, FreeTierQuotaType.REQUESTS_PER_DAY, feature)
        requests_quota = self._get_quota(user_id, FreeTierQuotaType.REQUESTS_PER_DAY, feature)
        
        if requests_used >= requests_quota:
            reason = f"Daily request quota exceeded ({requests_used}/{requests_quota})"
            record_quota_exceeded(
                provider="together_ai",
                tier="free",
                feature=str(feature),
                quota_type=str(FreeTierQuotaType.REQUESTS_PER_DAY)
            )
            return False, reason
        
        return True, None
    
    def check_token_quota(
        self,
        user_id: str,
        feature: FreeTierFeature,
        token_count: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a token request is within quota limits.
        
        Args:
            user_id: User identifier
            feature: Feature to check
            token_count: Number of tokens in the request
            
        Returns:
            Tuple of (within_quota, reason)
        """
        # Check if user is on free tier
        user_tier = get_user_tier(user_id)
        if user_tier != UserTier.FREE:
            # Premium users bypass free tier restrictions
            return True, None
        
        # Check tokens per request quota
        tokens_per_request_quota = self._get_quota(user_id, FreeTierQuotaType.TOKENS_PER_REQUEST, feature)
        
        if token_count > tokens_per_request_quota:
            reason = f"Token per request quota exceeded ({token_count}/{tokens_per_request_quota})"
            record_quota_exceeded(
                provider="together_ai",
                tier="free",
                feature=str(feature),
                quota_type=str(FreeTierQuotaType.TOKENS_PER_REQUEST)
            )
            return False, reason
        
        # Check tokens per day quota
        tokens_used = self._get_usage(user_id, FreeTierQuotaType.TOKENS_PER_DAY, feature)
        tokens_quota = self._get_quota(user_id, FreeTierQuotaType.TOKENS_PER_DAY, feature)
        
        if tokens_used + token_count > tokens_quota:
            reason = f"Daily token quota exceeded ({tokens_used}/{tokens_quota})"
            record_quota_exceeded(
                provider="together_ai",
                tier="free",
                feature=str(feature),
                quota_type=str(FreeTierQuotaType.TOKENS_PER_DAY)
            )
            return False, reason
        
        return True, None
    
    def record_request(
        self,
        user_id: str,
        modality: ModelModality,
        token_count: Optional[int] = None
    ) -> None:
        """
        Record a request for quota tracking.
        
        Args:
            user_id: User identifier
            modality: Model modality
            token_count: Optional token count for text/code requests
        """
        # Get corresponding feature
        feature = self._get_feature_for_modality(modality)
        
        # Increment requests per day
        self._increment_usage(user_id, FreeTierQuotaType.REQUESTS_PER_DAY, feature)
        
        # Increment tokens per day if applicable
        if token_count is not None and modality in [ModelModality.TEXT, ModelModality.CODE]:
            self._increment_usage(user_id, FreeTierQuotaType.TOKENS_PER_DAY, feature, token_count)
        
        # Increment images per day if applicable
        if modality == ModelModality.IMAGE:
            self._increment_usage(user_id, FreeTierQuotaType.IMAGES_PER_DAY, feature)
    
    def record_audio_usage(
        self,
        user_id: str,
        modality: ModelModality,
        minutes: float
    ) -> None:
        """
        Record audio usage for quota tracking.
        
        Args:
            user_id: User identifier
            modality: Audio modality (TTS or STT)
            minutes: Audio duration in minutes
        """
        # Get corresponding feature
        feature = self._get_feature_for_modality(modality)
        
        # Increment audio minutes per day
        self._increment_usage(
            user_id,
            FreeTierQuotaType.AUDIO_MINUTES_PER_DAY,
            feature,
            int(minutes * 60)  # Convert to seconds for more precise tracking
        )
    
    def get_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get usage summary for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with usage summary
        """
        result = {
            "user_id": user_id,
            "tier": str(get_user_tier(user_id) or UserTier.FREE),
            "quotas": {},
            "usage": {},
            "last_reset": self.last_reset.get(user_id, datetime.now()).isoformat()
        }
        
        # Add quotas
        for quota_type in FreeTierQuotaType:
            result["quotas"][str(quota_type)] = {}
            for feature in FreeTierFeature:
                quota = self._get_quota(user_id, quota_type, feature)
                if quota > 0:
                    result["quotas"][str(quota_type)][str(feature)] = quota
        
        # Add usage
        if user_id in self.usage_data:
            for quota_type, features in self.usage_data[user_id].items():
                result["usage"][str(quota_type)] = {}
                for feature, usage in features.items():
                    result["usage"][str(quota_type)][str(feature)] = usage
        
        return result
    
    def register_with_admin_dashboard(self) -> None:
        """
        Register this free tier manager with the admin dashboard.
        
        This method should be called during application startup to ensure
        the admin dashboard is aware of free tier quotas.
        """
        try:
            # Create quota configs for admin dashboard
            quota_configs = []
            
            for quota_type in FreeTierQuotaType:
                for feature in FreeTierFeature:
                    quota = self.DEFAULT_QUOTAS.get(quota_type, {}).get(feature)
                    if quota is not None:
                        quota_config = QuotaConfig(
                            provider="together_ai",
                            tier="free",
                            feature=str(feature),
                            quota_type=str(quota_type),
                            default_value=quota,
                            description=f"{feature} {quota_type} quota for Together AI free tier",
                            user_configurable=True
                        )
                        quota_configs.append(quota_config)
            
            # Register with admin dashboard
            from src.admin.dashboard.quota_registry import register_quota_configs
            register_quota_configs(quota_configs)
            
            logger.info(f"Successfully registered Together AI free tier quotas with admin dashboard")
            
        except Exception as e:
            logger.error(f"Failed to register with admin dashboard: {str(e)}")


# Singleton instance
_instance = None

def get_together_ai_free_tier_manager() -> TogetherAIFreeTierManager:
    """
    Get the singleton instance of the Together AI free tier manager.
    
    Returns:
        Together AI free tier manager instance
    """
    global _instance
    if _instance is None:
        _instance = TogetherAIFreeTierManager()
    return _instance


# Example usage functions

def can_use_text_generation(user_id: str, token_count: int) -> Tuple[bool, Optional[str]]:
    """
    Check if a user can use text generation.
    
    Args:
        user_id: User identifier
        token_count: Number of tokens in the request
        
    Returns:
        Tuple of (can_use, reason)
    """
    manager = get_together_ai_free_tier_manager()
    
    # Check if user can use the feature
    can_use, reason = manager.can_use_feature(user_id, FreeTierFeature.TEXT_GENERATION)
    if not can_use:
        return False, reason
    
    # Check token quota
    within_quota, reason = manager.check_token_quota(
        user_id, FreeTierFeature.TEXT_GENERATION, token_count
    )
    if not within_quota:
        return False, reason
    
    return True, None

def record_text_generation_usage(user_id: str, token_count: int) -> None:
    """
    Record text generation usage.
    
    Args:
        user_id: User identifier
        token_count: Number of tokens used
    """
    manager = get_together_ai_free_tier_manager()
    manager.record_request(user_id, ModelModality.TEXT, token_count)

def can_use_image_generation(user_id: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a user can use image generation.
    
    Args:
        user_id: User identifier
        
    Returns:
        Tuple of (can_use, reason)
    """
    manager = get_together_ai_free_tier_manager()
    return manager.can_use_feature(user_id, FreeTierFeature.IMAGE_GENERATION)

def record_image_generation_usage(user_id: str) -> None:
    """
    Record image generation usage.
    
    Args:
        user_id: User identifier
    """
    manager = get_together_ai_free_tier_manager()
    manager.record_request(user_id, ModelModality.IMAGE)
