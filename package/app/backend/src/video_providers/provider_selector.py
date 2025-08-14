"""
Video provider selector and switching capability for Aideon AI Lite.

This module implements seamless provider switching for video generation,
supporting multiple providers including Google, Runway ML, Replicate,
and future Together AI video capabilities.
"""

import os
import logging
import json
import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Tuple, Type
import random

from video_providers.base_provider import (
    VideoProvider,
    VideoProviderError,
    VideoProviderErrorType,
    VideoFormat,
    VideoQuality,
    VideoStyle,
    get_video_provider_registry
)

logger = logging.getLogger(__name__)

class ProviderTier(Enum):
    """Provider tier options."""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class VideoProviderSelector:
    """Video provider selector and manager."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super(VideoProviderSelector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        config_path: str = "/etc/aideon/video/provider_config.json"
    ):
        """Initialize the selector.
        
        Args:
            config_path: Path to configuration file
        """
        if self._initialized:
            return
        
        self.config_path = config_path
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize provider instances
        self.providers = {}
        self._initialize_providers()
        
        # Feature flags
        self.feature_flags = self.config.get("feature_flags", {})
        
        # Provider tier mappings
        self.tier_mappings = self.config.get("tier_mappings", {
            "free": ["google", "replicate"],
            "premium": ["runway_ml", "replicate", "google"],
            "enterprise": ["runway_ml", "replicate", "google"]
        })
        
        # Provider weights for random selection
        self.provider_weights = self.config.get("provider_weights", {
            "free": {
                "google": 0.6,
                "replicate": 0.4
            },
            "premium": {
                "runway_ml": 0.7,
                "replicate": 0.2,
                "google": 0.1
            },
            "enterprise": {
                "runway_ml": 0.8,
                "replicate": 0.1,
                "google": 0.1
            }
        })
        
        # Model mappings
        self.model_mappings = self.config.get("model_mappings", {
            "text_to_video": {
                "free": {
                    "default": {
                        "provider": "google",
                        "model": "text_to_speech_video"
                    },
                    "artistic": {
                        "provider": "replicate",
                        "model": "zeroscope-v2"
                    },
                    "realistic": {
                        "provider": "replicate",
                        "model": "modelscope-t2v"
                    }
                },
                "premium": {
                    "default": {
                        "provider": "runway_ml",
                        "model": "gen-2"
                    },
                    "cinematic": {
                        "provider": "runway_ml",
                        "model": "gen-2-cinematic"
                    },
                    "artistic": {
                        "provider": "replicate",
                        "model": "zeroscope-v2"
                    }
                }
            },
            "image_to_video": {
                "free": {
                    "default": {
                        "provider": "replicate",
                        "model": "stable-video-diffusion"
                    },
                    "animation": {
                        "provider": "replicate",
                        "model": "animatediff"
                    }
                },
                "premium": {
                    "default": {
                        "provider": "runway_ml",
                        "model": "gen-2-image-to-video"
                    },
                    "artistic": {
                        "provider": "runway_ml",
                        "model": "motion-brush"
                    }
                }
            }
        })
        
        # Fallback chains
        self.fallback_chains = self.config.get("fallback_chains", {
            "text_to_video": {
                "free": ["google", "replicate"],
                "premium": ["runway_ml", "replicate", "google"]
            },
            "image_to_video": {
                "free": ["replicate", "google"],
                "premium": ["runway_ml", "replicate", "google"]
            }
        })
        
        self._initialized = True
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        try:
            if not os.path.exists(self.config_path):
                # Create default configuration
                default_config = {
                    "feature_flags": {
                        "together_ai_video": False
                    },
                    "tier_mappings": {
                        "free": ["google", "replicate"],
                        "premium": ["runway_ml", "replicate", "google"],
                        "enterprise": ["runway_ml", "replicate", "google"]
                    },
                    "provider_weights": {
                        "free": {
                            "google": 0.6,
                            "replicate": 0.4
                        },
                        "premium": {
                            "runway_ml": 0.7,
                            "replicate": 0.2,
                            "google": 0.1
                        },
                        "enterprise": {
                            "runway_ml": 0.8,
                            "replicate": 0.1,
                            "google": 0.1
                        }
                    },
                    "model_mappings": {
                        "text_to_video": {
                            "free": {
                                "default": {
                                    "provider": "google",
                                    "model": "text_to_speech_video"
                                },
                                "artistic": {
                                    "provider": "replicate",
                                    "model": "zeroscope-v2"
                                },
                                "realistic": {
                                    "provider": "replicate",
                                    "model": "modelscope-t2v"
                                }
                            },
                            "premium": {
                                "default": {
                                    "provider": "runway_ml",
                                    "model": "gen-2"
                                },
                                "cinematic": {
                                    "provider": "runway_ml",
                                    "model": "gen-2-cinematic"
                                },
                                "artistic": {
                                    "provider": "replicate",
                                    "model": "zeroscope-v2"
                                }
                            }
                        },
                        "image_to_video": {
                            "free": {
                                "default": {
                                    "provider": "replicate",
                                    "model": "stable-video-diffusion"
                                },
                                "animation": {
                                    "provider": "replicate",
                                    "model": "animatediff"
                                }
                            },
                            "premium": {
                                "default": {
                                    "provider": "runway_ml",
                                    "model": "gen-2-image-to-video"
                                },
                                "artistic": {
                                    "provider": "runway_ml",
                                    "model": "motion-brush"
                                }
                            }
                        }
                    },
                    "fallback_chains": {
                        "text_to_video": {
                            "free": ["google", "replicate"],
                            "premium": ["runway_ml", "replicate", "google"]
                        },
                        "image_to_video": {
                            "free": ["replicate", "google"],
                            "premium": ["runway_ml", "replicate", "google"]
                        }
                    },
                    "api_keys": {
                        "runway_ml": "",
                        "replicate": "",
                        "google": ""
                    }
                }
                
                # Create directory if not exists
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                
                # Save default configuration
                with open(self.config_path, "w") as f:
                    json.dump(default_config, f, indent=2)
                
                return default_config
            
            # Load configuration
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return {
                "feature_flags": {},
                "tier_mappings": {},
                "provider_weights": {},
                "model_mappings": {},
                "fallback_chains": {},
                "api_keys": {}
            }
    
    def _save_config(self) -> bool:
        """Save configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if not exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save configuration
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def _initialize_providers(self) -> None:
        """Initialize provider instances."""
        try:
            # Get provider registry
            registry = get_video_provider_registry()
            
            # Get API keys
            api_keys = self.config.get("api_keys", {})
            
            # Initialize Google provider
            try:
                from src.video_providers.google_provider import GoogleVideoProvider
                google_credentials = api_keys.get("google", "")
                if google_credentials:
                    self.providers["google"] = GoogleVideoProvider(google_credentials)
                    logger.info("Initialized Google Video Provider")
            except Exception as e:
                logger.error(f"Error initializing Google Video Provider: {str(e)}")
            
            # Initialize Replicate provider
            try:
                from src.video_providers.replicate_provider import ReplicateVideoProvider
                replicate_api_key = api_keys.get("replicate", "")
                if replicate_api_key:
                    self.providers["replicate"] = ReplicateVideoProvider(replicate_api_key)
                    logger.info("Initialized Replicate Video Provider")
            except Exception as e:
                logger.error(f"Error initializing Replicate Video Provider: {str(e)}")
            
            # Initialize Runway ML provider
            try:
                from src.video_providers.runway_ml_provider import RunwayMLVideoProvider
                runway_api_key = api_keys.get("runway_ml", "")
                if runway_api_key:
                    self.providers["runway_ml"] = RunwayMLVideoProvider(runway_api_key)
                    logger.info("Initialized Runway ML Video Provider")
            except Exception as e:
                logger.error(f"Error initializing Runway ML Video Provider: {str(e)}")
            
            # Initialize Together AI provider if available
            if self.feature_flags.get("together_ai_video", False):
                try:
                    from src.video_providers.together_ai_provider import TogetherAIVideoProvider
                    together_api_key = api_keys.get("together_ai", "")
                    if together_api_key:
                        self.providers["together_ai"] = TogetherAIVideoProvider(together_api_key)
                        logger.info("Initialized Together AI Video Provider")
                except Exception as e:
                    logger.error(f"Error initializing Together AI Video Provider: {str(e)}")
        except Exception as e:
            logger.error(f"Error initializing providers: {str(e)}")
    
    def update_feature_flags(self, flags: Dict[str, bool]) -> bool:
        """Update feature flags.
        
        Args:
            flags: Dictionary of feature flags
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update feature flags
            for key, value in flags.items():
                self.feature_flags[key] = value
            
            # Update configuration
            self.config["feature_flags"] = self.feature_flags
            
            # Save configuration
            return self._save_config()
        except Exception as e:
            logger.error(f"Error updating feature flags: {str(e)}")
            return False
    
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Set API key for a provider.
        
        Args:
            provider: Provider name
            api_key: API key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update API key
            if "api_keys" not in self.config:
                self.config["api_keys"] = {}
            
            self.config["api_keys"][provider] = api_key
            
            # Save configuration
            if self._save_config():
                # Re-initialize providers
                self._initialize_providers()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error setting API key: {str(e)}")
            return False
    
    def get_provider_for_tier(
        self,
        tier: Union[str, ProviderTier],
        operation_type: str,
        style: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get provider and model for a tier.
        
        Args:
            tier: User tier
            operation_type: Operation type (text_to_video or image_to_video)
            style: Optional style
            
        Returns:
            Tuple of (provider_name, model_id) or (None, None) if not found
        """
        try:
            # Convert tier to string if needed
            if isinstance(tier, ProviderTier):
                tier_str = tier.value
            else:
                tier_str = tier
            
            # Get model mappings for operation type and tier
            tier_mappings = self.model_mappings.get(operation_type, {}).get(tier_str, {})
            
            # Get provider and model for style
            if style and style in tier_mappings:
                return tier_mappings[style]["provider"], tier_mappings[style]["model"]
            
            # Get default provider and model
            if "default" in tier_mappings:
                return tier_mappings["default"]["provider"], tier_mappings["default"]["model"]
            
            # No provider found
            return None, None
        except Exception as e:
            logger.error(f"Error getting provider for tier: {str(e)}")
            return None, None
    
    def get_random_provider_for_tier(self, tier: Union[str, ProviderTier]) -> Optional[str]:
        """Get random provider for a tier based on weights.
        
        Args:
            tier: User tier
            
        Returns:
            Provider name or None if not found
        """
        try:
            # Convert tier to string if needed
            if isinstance(tier, ProviderTier):
                tier_str = tier.value
            else:
                tier_str = tier
            
            # Get providers for tier
            providers = self.tier_mappings.get(tier_str, [])
            
            # Get weights for tier
            weights = []
            for provider in providers:
                weight = self.provider_weights.get(tier_str, {}).get(provider, 0)
                weights.append(weight)
            
            # Normalize weights
            if weights and sum(weights) > 0:
                weights = [w / sum(weights) for w in weights]
                
                # Select random provider
                return random.choices(providers, weights=weights, k=1)[0]
            
            # No providers found
            return None
        except Exception as e:
            logger.error(f"Error getting random provider for tier: {str(e)}")
            return None
    
    def get_fallback_chain(
        self,
        tier: Union[str, ProviderTier],
        operation_type: str
    ) -> List[str]:
        """Get fallback chain for a tier and operation type.
        
        Args:
            tier: User tier
            operation_type: Operation type (text_to_video or image_to_video)
            
        Returns:
            List of provider names in fallback order
        """
        try:
            # Convert tier to string if needed
            if isinstance(tier, ProviderTier):
                tier_str = tier.value
            else:
                tier_str = tier
            
            # Get fallback chain
            return self.fallback_chains.get(operation_type, {}).get(tier_str, [])
        except Exception as e:
            logger.error(f"Error getting fallback chain: {str(e)}")
            return []
    
    def get_provider(self, provider_name: str) -> Optional[VideoProvider]:
        """Get provider instance by name.
        
        Args:
            provider_name: Provider name
            
        Returns:
            Provider instance or None if not found
        """
        return self.providers.get(provider_name)
    
    async def generate_video_from_text(
        self,
        prompt: str,
        tier: Union[str, ProviderTier],
        model: Optional[str] = None,
        provider: Optional[str] = None,
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
            tier: User tier
            model: Model ID to use
            provider: Provider name to use
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
        # Convert tier to string if needed
        if isinstance(tier, ProviderTier):
            tier_str = tier.value
        else:
            tier_str = tier
        
        # Get style string if provided
        style_str = style.value if style else None
        
        # If provider and model are not specified, get them from tier mappings
        if not provider:
            provider, model = self.get_provider_for_tier(tier_str, "text_to_video", style_str)
        
        # If provider is specified but model is not, use default model for that provider
        if provider and not model:
            _, default_model = self.get_provider_for_tier(tier_str, "text_to_video", "default")
            model = default_model
        
        # Get fallback chain
        fallback_chain = self.get_fallback_chain(tier_str, "text_to_video")
        
        # If provider is still not specified, use first provider in fallback chain
        if not provider and fallback_chain:
            provider = fallback_chain[0]
        
        # Try providers in fallback chain
        errors = []
        tried_providers = set()
        
        # Start with specified provider
        if provider:
            providers_to_try = [provider] + [p for p in fallback_chain if p != provider]
        else:
            providers_to_try = fallback_chain
        
        for provider_name in providers_to_try:
            # Skip if already tried
            if provider_name in tried_providers:
                continue
            
            tried_providers.add(provider_name)
            
            # Get provider instance
            provider_instance = self.get_provider(provider_name)
            if not provider_instance:
                continue
            
            try:
                # Generate video
                result = await provider_instance.generate_video_from_text(
                    prompt=prompt,
                    model=model,
                    negative_prompt=negative_prompt,
                    duration=duration,
                    fps=fps,
                    width=width,
                    height=height,
                    format=format,
                    quality=quality,
                    style=style,
                    **kwargs
                )
                
                # Add fallback info
                result["fallback_info"] = {
                    "original_provider": provider,
                    "used_provider": provider_name,
                    "tried_providers": list(tried_providers),
                    "errors": errors
                }
                
                return result
            except VideoProviderError as e:
                # Add error to list
                errors.append({
                    "provider": provider_name,
                    "message": str(e),
                    "error_type": e.error_type.value if hasattr(e, "error_type") else "unknown"
                })
                
                # Log error
                logger.error(f"Error generating video with provider {provider_name}: {str(e)}")
                
                # Continue with next provider
                continue
        
        # All providers failed
        raise VideoProviderError(
            message=f"All providers failed to generate video: {errors}",
            error_type=VideoProviderErrorType.PROVIDER_ERROR,
            provider=provider,
            details={"errors": errors}
        )
    
    async def generate_video_from_image(
        self,
        image_url: str,
        tier: Union[str, ProviderTier],
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
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
            tier: User tier
            prompt: Optional text prompt to guide generation
            model: Model ID to use
            provider: Provider name to use
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
        # Convert tier to string if needed
        if isinstance(tier, ProviderTier):
            tier_str = tier.value
        else:
            tier_str = tier
        
        # Get style string if provided
        style_str = style.value if style else None
        
        # If provider and model are not specified, get them from tier mappings
        if not provider:
            provider, model = self.get_provider_for_tier(tier_str, "image_to_video", style_str)
        
        # If provider is specified but model is not, use default model for that provider
        if provider and not model:
            _, default_model = self.get_provider_for_tier(tier_str, "image_to_video", "default")
            model = default_model
        
        # Get fallback chain
        fallback_chain = self.get_fallback_chain(tier_str, "image_to_video")
        
        # If provider is still not specified, use first provider in fallback chain
        if not provider and fallback_chain:
            provider = fallback_chain[0]
        
        # Try providers in fallback chain
        errors = []
        tried_providers = set()
        
        # Start with specified provider
        if provider:
            providers_to_try = [provider] + [p for p in fallback_chain if p != provider]
        else:
            providers_to_try = fallback_chain
        
        for provider_name in providers_to_try:
            # Skip if already tried
            if provider_name in tried_providers:
                continue
            
            tried_providers.add(provider_name)
            
            # Get provider instance
            provider_instance = self.get_provider(provider_name)
            if not provider_instance:
                continue
            
            try:
                # Generate video
                result = await provider_instance.generate_video_from_image(
                    image_url=image_url,
                    prompt=prompt,
                    model=model,
                    negative_prompt=negative_prompt,
                    duration=duration,
                    fps=fps,
                    format=format,
                    quality=quality,
                    style=style,
                    **kwargs
                )
                
                # Add fallback info
                result["fallback_info"] = {
                    "original_provider": provider,
                    "used_provider": provider_name,
                    "tried_providers": list(tried_providers),
                    "errors": errors
                }
                
                return result
            except VideoProviderError as e:
                # Add error to list
                errors.append({
                    "provider": provider_name,
                    "message": str(e),
                    "error_type": e.error_type.value if hasattr(e, "error_type") else "unknown"
                })
                
                # Log error
                logger.error(f"Error generating video with provider {provider_name}: {str(e)}")
                
                # Continue with next provider
                continue
        
        # All providers failed
        raise VideoProviderError(
            message=f"All providers failed to generate video: {errors}",
            error_type=VideoProviderErrorType.PROVIDER_ERROR,
            provider=provider,
            details={"errors": errors}
        )
    
    async def check_status(
        self,
        job_id: str,
        provider: str
    ) -> Dict[str, Any]:
        """Check status of a video generation job.
        
        Args:
            job_id: Job ID returned from a previous request
            provider: Provider name
            
        Returns:
            Dictionary containing job status information
                
        Raises:
            VideoProviderError: If status check fails
        """
        # Get provider instance
        provider_instance = self.get_provider(provider)
        if not provider_instance:
            raise VideoProviderError(
                message=f"Provider not found: {provider}",
                error_type=VideoProviderErrorType.INVALID_REQUEST
            )
        
        # Check status
        return await provider_instance.check_status(job_id)
    
    async def get_quota_info(
        self,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get quota information for providers.
        
        Args:
            provider: Optional provider name to get quota for
            
        Returns:
            Dictionary containing quota information
                
        Raises:
            VideoProviderError: If quota check fails
        """
        result = {}
        errors = []
        
        # If provider is specified, get quota for that provider only
        if provider:
            provider_instance = self.get_provider(provider)
            if not provider_instance:
                raise VideoProviderError(
                    message=f"Provider not found: {provider}",
                    error_type=VideoProviderErrorType.INVALID_REQUEST
                )
            
            try:
                result[provider] = await provider_instance.get_quota_info()
            except VideoProviderError as e:
                errors.append({
                    "provider": provider,
                    "message": str(e),
                    "error_type": e.error_type.value if hasattr(e, "error_type") else "unknown"
                })
        else:
            # Get quota for all providers
            for provider_name, provider_instance in self.providers.items():
                try:
                    result[provider_name] = await provider_instance.get_quota_info()
                except VideoProviderError as e:
                    errors.append({
                        "provider": provider_name,
                        "message": str(e),
                        "error_type": e.error_type.value if hasattr(e, "error_type") else "unknown"
                    })
        
        return {
            "quotas": result,
            "errors": errors
        }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
    
    def get_available_models(
        self,
        provider: Optional[str] = None,
        operation_type: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Get available models.
        
        Args:
            provider: Optional provider name to filter by
            operation_type: Optional operation type to filter by
            
        Returns:
            Dictionary of provider name to list of model IDs
        """
        result = {}
        
        # If provider is specified, get models for that provider only
        if provider:
            provider_instance = self.get_provider(provider)
            if provider_instance:
                result[provider] = provider_instance.get_supported_models()
        else:
            # Get models for all providers
            for provider_name, provider_instance in self.providers.items():
                result[provider_name] = provider_instance.get_supported_models()
        
        # Filter by operation type if specified
        if operation_type:
            filtered_result = {}
            
            for provider_name, models in result.items():
                if operation_type == "text_to_video":
                    # Filter text-to-video models
                    if provider_name == "google":
                        filtered_result[provider_name] = [m for m in models if "text" in m.lower()]
                    elif provider_name == "replicate":
                        filtered_result[provider_name] = [m for m in models if m in self.text_to_video_models.get(provider_name, {})]
                    elif provider_name == "runway_ml":
                        filtered_result[provider_name] = [m for m in models if m in self.text_to_video_models.get(provider_name, {})]
                    else:
                        filtered_result[provider_name] = models
                elif operation_type == "image_to_video":
                    # Filter image-to-video models
                    if provider_name == "google":
                        filtered_result[provider_name] = [m for m in models if "image" in m.lower() or "slide" in m.lower()]
                    elif provider_name == "replicate":
                        filtered_result[provider_name] = [m for m in models if m in self.image_to_video_models.get(provider_name, {})]
                    elif provider_name == "runway_ml":
                        filtered_result[provider_name] = [m for m in models if m in self.image_to_video_models.get(provider_name, {})]
                    else:
                        filtered_result[provider_name] = models
            
            return filtered_result
        
        return result

def get_video_provider_selector() -> VideoProviderSelector:
    """Get the video provider selector singleton.
    
    Returns:
        Video provider selector instance
    """
    return VideoProviderSelector()
