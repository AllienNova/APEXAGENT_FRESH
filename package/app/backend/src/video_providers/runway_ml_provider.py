"""
Runway ML video provider implementation for Aideon AI Lite.

This module implements the Runway ML provider for premium tier video generation,
offering high-quality video capabilities for premium users.
"""

import os
import logging
import json
import time
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union, Tuple

from video_providers.base_provider import (
    VideoProvider,
    VideoProviderError,
    VideoProviderErrorType,
    VideoFormat,
    VideoQuality,
    VideoStyle
)

logger = logging.getLogger(__name__)

class RunwayMLVideoProvider(VideoProvider):
    """Runway ML video provider implementation."""
    
    def __init__(self, api_key: str):
        """Initialize the provider with API key.
        
        Args:
            api_key: Runway ML API key
        """
        self.api_key = api_key
        self.base_url = "https://api.runwayml.com/v1"
        
        # Model mappings
        self.text_to_video_models = {
            "gen-2": {
                "id": "gen-2",
                "name": "Gen-2",
                "description": "Runway's flagship text-to-video model",
                "max_duration": 16.0,
                "min_duration": 1.0,
                "default_fps": 24,
                "supported_formats": [VideoFormat.MP4],
                "supported_qualities": [VideoQuality.MEDIUM, VideoQuality.HIGH],
                "supported_styles": [VideoStyle.CINEMATIC, VideoStyle.REALISTIC]
            },
            "gen-2-cinematic": {
                "id": "gen-2-cinematic",
                "name": "Gen-2 Cinematic",
                "description": "Runway's cinematic text-to-video model",
                "max_duration": 10.0,
                "min_duration": 1.0,
                "default_fps": 30,
                "supported_formats": [VideoFormat.MP4],
                "supported_qualities": [VideoQuality.HIGH, VideoQuality.ULTRA],
                "supported_styles": [VideoStyle.CINEMATIC]
            }
        }
        
        self.image_to_video_models = {
            "gen-2-image-to-video": {
                "id": "gen-2-image-to-video",
                "name": "Gen-2 Image to Video",
                "description": "Runway's image-to-video model",
                "max_duration": 8.0,
                "min_duration": 1.0,
                "default_fps": 24,
                "supported_formats": [VideoFormat.MP4],
                "supported_qualities": [VideoQuality.MEDIUM, VideoQuality.HIGH],
                "supported_styles": [VideoStyle.REALISTIC]
            },
            "motion-brush": {
                "id": "motion-brush",
                "name": "Motion Brush",
                "description": "Runway's motion brush model for selective animation",
                "max_duration": 4.0,
                "min_duration": 1.0,
                "default_fps": 24,
                "supported_formats": [VideoFormat.MP4, VideoFormat.GIF],
                "supported_qualities": [VideoQuality.MEDIUM],
                "supported_styles": [VideoStyle.ARTISTIC]
            }
        }
    
    def get_provider_name(self) -> str:
        """Get provider name.
        
        Returns:
            Provider name
        """
        return "runway_ml"
    
    def get_supported_models(self) -> List[str]:
        """Get supported models.
        
        Returns:
            List of supported model IDs
        """
        return list(self.text_to_video_models.keys()) + list(self.image_to_video_models.keys())
    
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
        # Validate parameters
        self.validate_parameters(duration, fps, width, height, format, quality)
        
        # Use gen-2 model by default
        model_id = model or "gen-2"
        
        # Check if model is supported
        if model_id not in self.text_to_video_models:
            raise VideoProviderError(
                message=f"Unsupported model: {model_id}",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Get model info
        model_info = self.text_to_video_models[model_id]
        
        # Validate duration
        if duration < model_info["min_duration"] or duration > model_info["max_duration"]:
            raise VideoProviderError(
                message=f"Duration must be between {model_info['min_duration']} and {model_info['max_duration']} seconds",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate format
        if format not in model_info["supported_formats"]:
            raise VideoProviderError(
                message=f"Unsupported format: {format.value}",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate quality
        if quality not in model_info["supported_qualities"]:
            raise VideoProviderError(
                message=f"Unsupported quality: {quality.value}",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate style
        if style and style not in model_info["supported_styles"]:
            raise VideoProviderError(
                message=f"Unsupported style: {style.value}",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        try:
            # Create request payload
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_frames": int(duration * fps),
                "fps": fps,
                "width": width,
                "height": height,
                "output_format": format.value,
                "quality": quality.value
            }
            
            if style:
                payload["style"] = style.value
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/text-to-video/{model_id}",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise VideoProviderError(
                            message=error_data.get("message", "Unknown error"),
                            error_type=VideoProviderErrorType.PROVIDER_ERROR,
                            provider=self.get_provider_name(),
                            status_code=response.status,
                            details=error_data
                        )
                    
                    data = await response.json()
                    
                    # Return result
                    return {
                        "video_url": data.get("video_url"),
                        "preview_url": data.get("preview_url"),
                        "duration": duration,
                        "width": width,
                        "height": height,
                        "model_id": model_id,
                        "provider": self.get_provider_name(),
                        "metadata": {
                            "job_id": data.get("id"),
                            "fps": fps,
                            "prompt": prompt,
                            "negative_prompt": negative_prompt,
                            "format": format.value,
                            "quality": quality.value,
                            "style": style.value if style else None
                        }
                    }
        except VideoProviderError:
            raise
        except Exception as e:
            logger.error(f"Error generating video from text: {str(e)}")
            raise VideoProviderError(
                message=f"Error generating video from text: {str(e)}",
                error_type=VideoProviderErrorType.PROVIDER_ERROR,
                provider=self.get_provider_name()
            )
    
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
        # Extract width and height from kwargs
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 576)
        
        # Validate parameters
        self.validate_parameters(duration, fps, width, height, format, quality)
        
        # Use gen-2-image-to-video model by default
        model_id = model or "gen-2-image-to-video"
        
        # Check if model is supported
        if model_id not in self.image_to_video_models:
            raise VideoProviderError(
                message=f"Unsupported model: {model_id}",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Get model info
        model_info = self.image_to_video_models[model_id]
        
        # Validate duration
        if duration < model_info["min_duration"] or duration > model_info["max_duration"]:
            raise VideoProviderError(
                message=f"Duration must be between {model_info['min_duration']} and {model_info['max_duration']} seconds",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate format
        if format not in model_info["supported_formats"]:
            raise VideoProviderError(
                message=f"Unsupported format: {format.value}",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate quality
        if quality not in model_info["supported_qualities"]:
            raise VideoProviderError(
                message=f"Unsupported quality: {quality.value}",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        # Validate style
        if style and style not in model_info["supported_styles"]:
            raise VideoProviderError(
                message=f"Unsupported style: {style.value}",
                error_type=VideoProviderErrorType.INVALID_REQUEST,
                provider=self.get_provider_name()
            )
        
        try:
            # Create request payload
            payload = {
                "image_url": image_url,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_frames": int(duration * fps),
                "fps": fps,
                "width": width,
                "height": height,
                "output_format": format.value,
                "quality": quality.value
            }
            
            if style:
                payload["style"] = style.value
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key not in payload and key not in ["width", "height"]:
                    payload[key] = value
            
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/image-to-video/{model_id}",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise VideoProviderError(
                            message=error_data.get("message", "Unknown error"),
                            error_type=VideoProviderErrorType.PROVIDER_ERROR,
                            provider=self.get_provider_name(),
                            status_code=response.status,
                            details=error_data
                        )
                    
                    data = await response.json()
                    
                    # Return result
                    return {
                        "video_url": data.get("video_url"),
                        "preview_url": image_url,
                        "duration": duration,
                        "width": width,
                        "height": height,
                        "model_id": model_id,
                        "provider": self.get_provider_name(),
                        "metadata": {
                            "job_id": data.get("id"),
                            "fps": fps,
                            "prompt": prompt,
                            "negative_prompt": negative_prompt,
                            "format": format.value,
                            "quality": quality.value,
                            "style": style.value if style else None
                        }
                    }
        except VideoProviderError:
            raise
        except Exception as e:
            logger.error(f"Error generating video from image: {str(e)}")
            raise VideoProviderError(
                message=f"Error generating video from image: {str(e)}",
                error_type=VideoProviderErrorType.PROVIDER_ERROR,
                provider=self.get_provider_name()
            )
    
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
        try:
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/jobs/{job_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise VideoProviderError(
                            message=error_data.get("message", "Unknown error"),
                            error_type=VideoProviderErrorType.PROVIDER_ERROR,
                            provider=self.get_provider_name(),
                            status_code=response.status,
                            details=error_data
                        )
                    
                    data = await response.json()
                    
                    # Map status
                    status_map = {
                        "pending": "processing",
                        "processing": "processing",
                        "succeeded": "completed",
                        "failed": "failed",
                        "canceled": "canceled"
                    }
                    
                    status = status_map.get(data.get("status", "processing"), "processing")
                    
                    # Calculate progress
                    progress = 0
                    if status == "completed":
                        progress = 100
                    elif status == "processing":
                        progress = data.get("progress", 0) * 100
                    
                    # Return result
                    return {
                        "status": status,
                        "progress": progress,
                        "video_url": data.get("video_url") if status == "completed" else None,
                        "preview_url": data.get("preview_url"),
                        "error": data.get("error"),
                        "metadata": {
                            "created_at": data.get("created_at"),
                            "updated_at": data.get("updated_at"),
                            "model_id": data.get("model_id")
                        }
                    }
        except VideoProviderError:
            raise
        except Exception as e:
            logger.error(f"Error checking job status: {str(e)}")
            raise VideoProviderError(
                message=f"Error checking job status: {str(e)}",
                error_type=VideoProviderErrorType.PROVIDER_ERROR,
                provider=self.get_provider_name()
            )
    
    async def get_quota_info(self) -> Dict[str, Any]:
        """Get quota information for the current API key.
        
        Returns:
            Dictionary containing quota information
                
        Raises:
            VideoProviderError: If quota check fails
        """
        try:
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/quota",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise VideoProviderError(
                            message=error_data.get("message", "Unknown error"),
                            error_type=VideoProviderErrorType.PROVIDER_ERROR,
                            provider=self.get_provider_name(),
                            status_code=response.status,
                            details=error_data
                        )
                    
                    data = await response.json()
                    
                    # Return result
                    return {
                        "quota_used": data.get("used", 0),
                        "quota_total": data.get("total", 0),
                        "quota_remaining": data.get("remaining", 0),
                        "reset_time": data.get("reset_time"),
                        "tier": data.get("tier")
                    }
        except VideoProviderError:
            raise
        except Exception as e:
            logger.error(f"Error getting quota information: {str(e)}")
            raise VideoProviderError(
                message=f"Error getting quota information: {str(e)}",
                error_type=VideoProviderErrorType.PROVIDER_ERROR,
                provider=self.get_provider_name()
            )
