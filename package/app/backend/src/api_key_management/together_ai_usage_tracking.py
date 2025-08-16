"""
Usage tracking and quotas for Together AI integration.

This module implements usage tracking and quotas for Together AI integration,
ensuring proper monitoring and enforcement of usage limits.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
import json
import asyncio
import threading
from enum import Enum

from src.api_key_management.together_ai_free_tier import (
    get_together_ai_free_tier_manager,
    FreeTierFeature,
    FreeTierQuotaType
)
from src.api_key_management.together_ai_model_selector import (
    ModelModality,
    ModelPurpose
)
from src.user.subscription import UserTier, get_user_tier
from src.config.feature_flags import FeatureFlag, is_feature_enabled
from src.monitoring.metrics import record_usage_event, record_quota_exceeded_event
from src.admin.dashboard.models import UsageRecord, QuotaConfig

logger = logging.getLogger(__name__)

class UsageMetricType(str, Enum):
    """Enum for usage metric types."""
    API_CALLS = "api_calls"
    TOKENS = "tokens"
    IMAGES = "images"
    AUDIO_SECONDS = "audio_seconds"
    CHARACTERS = "characters"
    ERRORS = "errors"
    LATENCY_MS = "latency_ms"

class TogetherAIUsageTracker:
    """
    Usage tracker for Together AI integration.
    
    This class handles tracking and reporting of usage metrics
    for Together AI integration across all tiers.
    """
    
    # Flush interval in seconds
    FLUSH_INTERVAL = 60
    
    # Maximum buffer size before forced flush
    MAX_BUFFER_SIZE = 1000
    
    def __init__(self):
        """Initialize the usage tracker."""
        self.usage_buffer = []
        self.buffer_lock = threading.Lock()
        self.last_flush = datetime.now()
        self.flush_thread = None
        self.running = False
        
        # Start background flush thread
        self._start_flush_thread()
    
    def _start_flush_thread(self):
        """Start background flush thread."""
        if self.flush_thread is None or not self.flush_thread.is_alive():
            self.running = True
            self.flush_thread = threading.Thread(target=self._background_flush)
            self.flush_thread.daemon = True
            self.flush_thread.start()
            logger.info("Started usage tracker flush thread")
    
    def _background_flush(self):
        """Background thread for periodic flushing."""
        while self.running:
            try:
                # Sleep for a bit
                time.sleep(5)
                
                # Check if it's time to flush
                current_time = datetime.now()
                if (current_time - self.last_flush).total_seconds() >= self.FLUSH_INTERVAL:
                    self.flush()
                
            except Exception as e:
                logger.error(f"Error in usage tracker flush thread: {str(e)}")
    
    def stop(self):
        """Stop the usage tracker."""
        self.running = False
        if self.flush_thread and self.flush_thread.is_alive():
            self.flush_thread.join(timeout=5)
        
        # Final flush
        self.flush()
    
    def track_usage(
        self,
        user_id: str,
        metric_type: UsageMetricType,
        provider: str = "together_ai",
        model_id: Optional[str] = None,
        modality: Optional[ModelModality] = None,
        feature: Optional[FreeTierFeature] = None,
        amount: Union[int, float] = 1,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Track usage metric.
        
        Args:
            user_id: User identifier
            metric_type: Type of usage metric
            provider: Provider identifier
            model_id: Optional model identifier
            modality: Optional model modality
            feature: Optional free tier feature
            amount: Amount to record
            metadata: Optional additional metadata
        """
        # Get user tier
        user_tier = get_user_tier(user_id) or UserTier.FREE
        
        # Create usage record
        record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "tier": str(user_tier),
            "provider": provider,
            "metric_type": str(metric_type),
            "amount": amount
        }
        
        # Add optional fields
        if model_id:
            record["model_id"] = model_id
        if modality:
            record["modality"] = str(modality)
        if feature:
            record["feature"] = str(feature)
        if metadata:
            record["metadata"] = metadata
        
        # Add to buffer
        with self.buffer_lock:
            self.usage_buffer.append(record)
            
            # Force flush if buffer is too large
            if len(self.usage_buffer) >= self.MAX_BUFFER_SIZE:
                self._flush_buffer()
        
        # Record metric
        record_usage_event(
            provider=provider,
            metric_type=str(metric_type),
            amount=amount,
            user_id=user_id,
            tier=str(user_tier)
        )
    
    def track_api_call(
        self,
        user_id: str,
        endpoint: str,
        model_id: Optional[str] = None,
        modality: Optional[ModelModality] = None,
        latency_ms: Optional[float] = None
    ):
        """
        Track API call.
        
        Args:
            user_id: User identifier
            endpoint: API endpoint
            model_id: Optional model identifier
            modality: Optional model modality
            latency_ms: Optional latency in milliseconds
        """
        # Track API call
        self.track_usage(
            user_id=user_id,
            metric_type=UsageMetricType.API_CALLS,
            model_id=model_id,
            modality=modality,
            metadata={"endpoint": endpoint}
        )
        
        # Track latency if provided
        if latency_ms is not None:
            self.track_usage(
                user_id=user_id,
                metric_type=UsageMetricType.LATENCY_MS,
                model_id=model_id,
                modality=modality,
                amount=latency_ms,
                metadata={"endpoint": endpoint}
            )
    
    def track_token_usage(
        self,
        user_id: str,
        token_count: int,
        model_id: str,
        modality: ModelModality,
        is_prompt: bool = False
    ):
        """
        Track token usage.
        
        Args:
            user_id: User identifier
            token_count: Number of tokens
            model_id: Model identifier
            modality: Model modality
            is_prompt: Whether tokens are for prompt or completion
        """
        # Map modality to feature
        feature = None
        if modality == ModelModality.TEXT:
            feature = FreeTierFeature.TEXT_GENERATION
        elif modality == ModelModality.CODE:
            feature = FreeTierFeature.CODE_GENERATION
        
        # Track token usage
        self.track_usage(
            user_id=user_id,
            metric_type=UsageMetricType.TOKENS,
            model_id=model_id,
            modality=modality,
            feature=feature,
            amount=token_count,
            metadata={"is_prompt": is_prompt}
        )
    
    def track_image_generation(
        self,
        user_id: str,
        model_id: str,
        width: int,
        height: int
    ):
        """
        Track image generation.
        
        Args:
            user_id: User identifier
            model_id: Model identifier
            width: Image width
            height: Image height
        """
        # Track image generation
        self.track_usage(
            user_id=user_id,
            metric_type=UsageMetricType.IMAGES,
            model_id=model_id,
            modality=ModelModality.IMAGE,
            feature=FreeTierFeature.IMAGE_GENERATION,
            metadata={"width": width, "height": height}
        )
    
    def track_audio_processing(
        self,
        user_id: str,
        model_id: str,
        duration_seconds: float,
        is_tts: bool = True
    ):
        """
        Track audio processing.
        
        Args:
            user_id: User identifier
            model_id: Model identifier
            duration_seconds: Audio duration in seconds
            is_tts: Whether this is text-to-speech (True) or speech-to-text (False)
        """
        # Determine modality and feature
        if is_tts:
            modality = ModelModality.AUDIO_TTS
            feature = FreeTierFeature.AUDIO_TTS
        else:
            modality = ModelModality.AUDIO_STT
            feature = FreeTierFeature.AUDIO_STT
        
        # Track audio processing
        self.track_usage(
            user_id=user_id,
            metric_type=UsageMetricType.AUDIO_SECONDS,
            model_id=model_id,
            modality=modality,
            feature=feature,
            amount=duration_seconds
        )
    
    def track_error(
        self,
        user_id: str,
        error_type: str,
        model_id: Optional[str] = None,
        modality: Optional[ModelModality] = None,
        error_message: Optional[str] = None
    ):
        """
        Track error.
        
        Args:
            user_id: User identifier
            error_type: Type of error
            model_id: Optional model identifier
            modality: Optional model modality
            error_message: Optional error message
        """
        # Track error
        self.track_usage(
            user_id=user_id,
            metric_type=UsageMetricType.ERRORS,
            model_id=model_id,
            modality=modality,
            metadata={
                "error_type": error_type,
                "error_message": error_message
            }
        )
    
    def track_quota_exceeded(
        self,
        user_id: str,
        quota_type: FreeTierQuotaType,
        feature: FreeTierFeature,
        current_usage: int,
        quota_limit: int
    ):
        """
        Track quota exceeded event.
        
        Args:
            user_id: User identifier
            quota_type: Quota type
            feature: Feature
            current_usage: Current usage
            quota_limit: Quota limit
        """
        # Record quota exceeded event
        record_quota_exceeded_event(
            provider="together_ai",
            user_id=user_id,
            quota_type=str(quota_type),
            feature=str(feature),
            current_usage=current_usage,
            quota_limit=quota_limit
        )
        
        # Track in usage metrics
        self.track_usage(
            user_id=user_id,
            metric_type=UsageMetricType.API_CALLS,
            feature=feature,
            metadata={
                "quota_exceeded": True,
                "quota_type": str(quota_type),
                "current_usage": current_usage,
                "quota_limit": quota_limit
            }
        )
    
    def _flush_buffer(self):
        """Flush usage buffer to storage."""
        if not self.usage_buffer:
            return
        
        try:
            # Get records to flush
            with self.buffer_lock:
                records = self.usage_buffer.copy()
                self.usage_buffer = []
            
            # Save to database
            self._save_records_to_database(records)
            
            # Update last flush time
            self.last_flush = datetime.now()
            
            logger.info(f"Flushed {len(records)} usage records")
            
        except Exception as e:
            logger.error(f"Error flushing usage buffer: {str(e)}")
    
    def _save_records_to_database(self, records: List[Dict[str, Any]]):
        """
        Save usage records to database.
        
        Args:
            records: List of usage records
        """
        try:
            # Convert to UsageRecord objects
            usage_records = []
            for record in records:
                # Convert timestamp string to datetime
                if isinstance(record["timestamp"], str):
                    timestamp = datetime.fromisoformat(record["timestamp"])
                else:
                    timestamp = record["timestamp"]
                
                # Create UsageRecord object
                usage_record = UsageRecord(
                    timestamp=timestamp,
                    user_id=record["user_id"],
                    tier=record["tier"],
                    provider=record["provider"],
                    metric_type=record["metric_type"],
                    amount=record["amount"],
                    model_id=record.get("model_id"),
                    modality=record.get("modality"),
                    feature=record.get("feature"),
                    metadata=json.dumps(record.get("metadata", {}))
                )
                usage_records.append(usage_record)
            
            # Save to database
            from src.database.usage_repository import save_usage_records
            save_usage_records(usage_records)
            
        except Exception as e:
            logger.error(f"Error saving usage records to database: {str(e)}")
            
            # Fallback to file storage
            self._save_records_to_file(records)
    
    def _save_records_to_file(self, records: List[Dict[str, Any]]):
        """
        Save usage records to file as fallback.
        
        Args:
            records: List of usage records
        """
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/together_ai_usage_{timestamp}.json"
            
            # Write to file
            with open(filename, "w") as f:
                json.dump(records, f)
            
            logger.info(f"Saved {len(records)} usage records to file {filename}")
            
        except Exception as e:
            logger.error(f"Error saving usage records to file: {str(e)}")
    
    def flush(self):
        """Flush usage buffer."""
        self._flush_buffer()


class TogetherAIQuotaEnforcer:
    """
    Quota enforcer for Together AI integration.
    
    This class handles enforcement of usage quotas for Together AI integration,
    working in conjunction with the free tier manager.
    """
    
    def __init__(self):
        """Initialize the quota enforcer."""
        self.free_tier_manager = get_together_ai_free_tier_manager()
        self.usage_tracker = get_together_ai_usage_tracker()
    
    async def check_and_enforce_quota(
        self,
        user_id: str,
        feature: FreeTierFeature,
        token_count: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check and enforce quota for a user.
        
        Args:
            user_id: User identifier
            feature: Feature to check
            token_count: Optional token count for text/code requests
            
        Returns:
            Tuple of (allowed, reason)
        """
        # Get user tier
        user_tier = get_user_tier(user_id) or UserTier.FREE
        
        # Premium users bypass quota enforcement
        if user_tier != UserTier.FREE:
            return True, None
        
        # Check if user can use feature
        can_use, reason = self.free_tier_manager.can_use_feature(user_id, feature)
        if not can_use:
            # Track quota exceeded
            quota_type = FreeTierQuotaType.REQUESTS_PER_DAY
            current_usage = self.free_tier_manager._get_usage(user_id, quota_type, feature)
            quota_limit = self.free_tier_manager._get_quota(user_id, quota_type, feature)
            
            self.usage_tracker.track_quota_exceeded(
                user_id=user_id,
                quota_type=quota_type,
                feature=feature,
                current_usage=current_usage,
                quota_limit=quota_limit
            )
            
            return False, reason
        
        # Check token quota if applicable
        if token_count is not None:
            within_quota, reason = self.free_tier_manager.check_token_quota(
                user_id=user_id,
                feature=feature,
                token_count=token_count
            )
            
            if not within_quota:
                # Track quota exceeded
                if "Token per request" in reason:
                    quota_type = FreeTierQuotaType.TOKENS_PER_REQUEST
                else:
                    quota_type = FreeTierQuotaType.TOKENS_PER_DAY
                
                current_usage = self.free_tier_manager._get_usage(user_id, quota_type, feature)
                quota_limit = self.free_tier_manager._get_quota(user_id, quota_type, feature)
                
                self.usage_tracker.track_quota_exceeded(
                    user_id=user_id,
                    quota_type=quota_type,
                    feature=feature,
                    current_usage=current_usage,
                    quota_limit=quota_limit
                )
                
                return False, reason
        
        return True, None
    
    def record_usage(
        self,
        user_id: str,
        modality: ModelModality,
        token_count: Optional[int] = None,
        model_id: Optional[str] = None
    ):
        """
        Record usage for quota tracking.
        
        Args:
            user_id: User identifier
            modality: Model modality
            token_count: Optional token count for text/code requests
            model_id: Optional model identifier
        """
        # Record in free tier manager
        self.free_tier_manager.record_request(
            user_id=user_id,
            modality=modality,
            token_count=token_count
        )
        
        # Record in usage tracker
        if token_count is not None and modality in [ModelModality.TEXT, ModelModality.CODE]:
            self.usage_tracker.track_token_usage(
                user_id=user_id,
                token_count=token_count,
                model_id=model_id or "unknown",
                modality=modality
            )
        elif modality == ModelModality.IMAGE:
            self.usage_tracker.track_image_generation(
                user_id=user_id,
                model_id=model_id or "unknown",
                width=1024,  # Default values
                height=1024
            )
    
    def record_audio_usage(
        self,
        user_id: str,
        modality: ModelModality,
        duration_seconds: float,
        model_id: Optional[str] = None
    ):
        """
        Record audio usage for quota tracking.
        
        Args:
            user_id: User identifier
            modality: Audio modality (TTS or STT)
            duration_seconds: Audio duration in seconds
            model_id: Optional model identifier
        """
        # Record in free tier manager
        self.free_tier_manager.record_audio_usage(
            user_id=user_id,
            modality=modality,
            minutes=duration_seconds / 60
        )
        
        # Record in usage tracker
        is_tts = modality == ModelModality.AUDIO_TTS
        self.usage_tracker.track_audio_processing(
            user_id=user_id,
            model_id=model_id or "unknown",
            duration_seconds=duration_seconds,
            is_tts=is_tts
        )
    
    def get_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get usage summary for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with usage summary
        """
        return self.free_tier_manager.get_usage_summary(user_id)


# Singleton instances
_usage_tracker_instance = None
_quota_enforcer_instance = None

def get_together_ai_usage_tracker() -> TogetherAIUsageTracker:
    """
    Get the singleton instance of the Together AI usage tracker.
    
    Returns:
        Together AI usage tracker instance
    """
    global _usage_tracker_instance
    if _usage_tracker_instance is None:
        _usage_tracker_instance = TogetherAIUsageTracker()
    return _usage_tracker_instance

def get_together_ai_quota_enforcer() -> TogetherAIQuotaEnforcer:
    """
    Get the singleton instance of the Together AI quota enforcer.
    
    Returns:
        Together AI quota enforcer instance
    """
    global _quota_enforcer_instance
    if _quota_enforcer_instance is None:
        _quota_enforcer_instance = TogetherAIQuotaEnforcer()
    return _quota_enforcer_instance


# API middleware integration
class UsageTrackingMiddleware:
    """
    Middleware for tracking API usage.
    
    This middleware automatically tracks API usage for Together AI endpoints.
    """
    
    def __init__(self):
        """Initialize the middleware."""
        self.usage_tracker = get_together_ai_usage_tracker()
    
    async def process_request(self, request, call_next):
        """
        Process a request.
        
        Args:
            request: Request object
            call_next: Next middleware function
            
        Returns:
            Response object
        """
        # Check if this is a Together AI endpoint
        if not request.url.path.startswith("/api/v1/together"):
            return await call_next(request)
        
        # Get user ID from request
        user_id = None
        if hasattr(request.state, "user") and hasattr(request.state.user, "id"):
            user_id = request.state.user.id
        
        # Record start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Track API call
            if user_id:
                self.usage_tracker.track_api_call(
                    user_id=user_id,
                    endpoint=request.url.path,
                    latency_ms=latency_ms
                )
            
            return response
            
        except Exception as e:
            # Track error
            if user_id:
                self.usage_tracker.track_error(
                    user_id=user_id,
                    error_type="api_error",
                    error_message=str(e)
                )
            
            # Re-raise exception
            raise


# Register middleware
def register_usage_tracking_middleware(app):
    """
    Register the usage tracking middleware.
    
    Args:
        app: FastAPI app
    """
    try:
        from fastapi import FastAPI
        
        @app.middleware("http")
        async def usage_tracking_middleware(request, call_next):
            middleware = UsageTrackingMiddleware()
            return await middleware.process_request(request, call_next)
        
        logger.info("Registered usage tracking middleware")
    except Exception as e:
        logger.error(f"Failed to register usage tracking middleware: {str(e)}")


# Initialize usage tracking
def initialize_usage_tracking():
    """Initialize usage tracking."""
    try:
        # Get usage tracker
        usage_tracker = get_together_ai_usage_tracker()
        
        # Start flush thread
        usage_tracker._start_flush_thread()
        
        logger.info("Initialized Together AI usage tracking")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize usage tracking: {str(e)}")
        return False
