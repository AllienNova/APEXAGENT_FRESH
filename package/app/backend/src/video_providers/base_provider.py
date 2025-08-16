"""
Video provider registry and interface for Aideon AI Lite.

This module implements the unified video provider interface, ensuring seamless
integration of multiple video providers including Google, Runway ML, Replicate,
and future Together AI video capabilities.
"""

import os
import logging
import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Tuple, Type

logger = logging.getLogger(__name__)

class VideoFormat(Enum):
    """Video format options."""
    MP4 = "mp4"
    WEBM = "webm"
    MOV = "mov"
    GIF = "gif"

class VideoQuality(Enum):
    """Video quality options."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

class VideoStyle(Enum):
    """Video style options."""
    REALISTIC = "realistic"
    CINEMATIC = "cinematic"
    ANIMATION = "animation"
    ARTISTIC = "artistic"
    STYLIZED = "stylized"

class VideoProviderErrorType(Enum):
    """Video provider error types."""
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    QUOTA_EXCEEDED = "quota_exceeded"
    INVALID_REQUEST = "invalid_request"
    MODEL_ERROR = "model_error"
    PROVIDER_ERROR = "provider_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

class VideoProviderError(Exception):
    """Video provider error."""
    
    def __init__(
        self,
        message: str,
        error_type: VideoProviderErrorType = VideoProviderErrorType.UNKNOWN,
        provider: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the error.
        
        Args:
            message: Error message
            error_type: Error type
            provider: Provider name
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.error_type = error_type
        self.provider = provider
        self.status_code = status_code
        self.details = details or {}
        
        super().__init__(message)

class VideoProvider:
    """Base class for video providers."""
    
    def get_provider_name(self) -> str:
        """Get provider name.
        
        Returns:
            Provider name
        """
        raise NotImplementedError("Subclasses must implement get_provider_name")
    
    def get_supported_models(self) -> List[str]:
        """Get supported models.
        
        Returns:
            List of supported model IDs
        """
        raise NotImplementedError("Subclasses must implement get_supported_models")
    
    async def generate_video_from_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        duration: float = 3.0,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        format: VideoFormat = VideoFormat.MP4,
        quality: VideoQuality = VideoQuality.MEDIUM,
        style: Optional[VideoStyle] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video from text prompt.
        
        Args:
            prompt: Text prompt describing the video
            model: Model ID to use
            negative_prompt: Text prompt describing what to avoid
            duration: Video duration in seconds
            fps: Frames per second
            width: Video width in pixels
            height: Video height in pixels
            format: Video format
            quality: Video quality
            style: Video style
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing video generation results
                
        Raises:
            VideoProviderError: If video generation fails
        """
        raise NotImplementedError("Subclasses must implement generate_video_from_text")
    
    async def generate_video_from_image(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        duration: float = 3.0,
        fps: int = 24,
        format: VideoFormat = VideoFormat.MP4,
        quality: VideoQuality = VideoQuality.MEDIUM,
        style: Optional[VideoStyle] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video from image.
        
        Args:
            image_url: URL to the source image
            prompt: Optional text prompt to guide generation
            model: Model ID to use
            negative_prompt: Text prompt describing what to avoid
            duration: Video duration in seconds
            fps: Frames per second
            format: Video format
            quality: Video quality
            style: Video style
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing video generation results
                
        Raises:
            VideoProviderError: If video generation fails
        """
        raise NotImplementedError("Subclasses must implement generate_video_from_image")
    
    async def check_status(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """Check status of a video generation job.
        
        Args:
            job_id: Job ID returned from a previous request
            
        Returns:
            Dictionary containing job status information
                
        Raises:
            VideoProviderError: If status check fails
        """
        raise NotImplementedError("Subclasses must implement check_status")
    
    async def get_quota_info(self) -> Dict[str, Any]:
        """Get quota information for the current API key.
        
        Returns:
            Dictionary containing quota information
                
        Raises:
            VideoProviderError: If quota check fails
        """
        raise NotImplementedError("Subclasses must implement get_quota_info")
    
    def validate_parameters(
        self,
        duration: float,
        fps: int,
        width: int,
        height: int,
        format: VideoFormat,
        quality: VideoQuality
    ) -> None:
        """Validate parameters.
        
        Args:
            duration: Video duration in seconds
            fps: Frames per second
            width: Video width in pixels
            height: Video height in pixels
            format: Video format
            quality: Video quality
            
        Raises:
            VideoProviderError: If parameters are invalid
        """
        # Validate duration
        if duration <= 0:
            raise VideoProviderError(
                message="Duration must be positive",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate FPS
        if fps <= 0:
            raise VideoProviderError(
                message="FPS must be positive",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate width
        if width <= 0:
            raise VideoProviderError(
                message="Width must be positive",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate height
        if height <= 0:
            raise VideoProviderError(
                message="Height must be positive",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )

class VideoProviderRegistry:
    """Registry for video providers."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super(VideoProviderRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if self._initialized:
            return
        
        self.providers = {}
        self._initialized = True
    
    def register_provider(self, provider_class: Type[VideoProvider]) -> None:
        """Register a provider class.
        
        Args:
            provider_class: Provider class
        """
        self.providers[provider_class.__name__] = provider_class
    
    def get_provider_class(self, provider_name: str) -> Optional[Type[VideoProvider]]:
        """Get provider class by name.
        
        Args:
            provider_name: Provider name
            
        Returns:
            Provider class or None if not found
        """
        return self.providers.get(provider_name)
    
    def get_provider_classes(self) -> Dict[str, Type[VideoProvider]]:
        """Get all provider classes.
        
        Returns:
            Dictionary of provider name to provider class
        """
        return self.providers.copy()

def get_video_provider_registry() -> VideoProviderRegistry:
    """Get the video provider registry singleton.
    
    Returns:
        Video provider registry instance
    """
    return VideoProviderRegistry()

# Register provider classes
def register_providers() -> None:
    """Register all provider classes."""
    registry = get_video_provider_registry()
    
    # Import provider classes
    from src.video_providers.runway_ml_provider import RunwayMLVideoProvider
    from src.video_providers.replicate_provider import ReplicateVideoProvider
    from src.video_providers.google_provider import GoogleVideoProvider
    
    # Register provider classes
    registry.register_provider(RunwayMLVideoProvider)
    registry.register_provider(ReplicateVideoProvider)
    registry.register_provider(GoogleVideoProvider)
    
    # Register Together AI provider if available
    try:
        from src.video_providers.together_ai_provider import TogetherAIVideoProvider
        registry.register_provider(TogetherAIVideoProvider)
    except ImportError:
        # Together AI provider not available yet
        pass
    
    logger.info(f"Registered {len(registry.get_provider_classes())} video providers")
