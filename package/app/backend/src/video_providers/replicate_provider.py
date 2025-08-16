"""
Replicate video provider implementation for Aideon AI Lite.

This module implements the Replicate provider for free tier video generation,
offering cost-effective video capabilities for free tier users.
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

class ReplicateVideoProvider(VideoProvider):
    """Replicate video provider implementation."""
    
    def __init__(self, api_key: str):
        """Initialize the provider with API key.
        
        Args:
            api_key: Replicate API key
        """
        self.api_key = api_key
        self.base_url = "https://api.replicate.com/v1"
        
        # Model mappings for text-to-video
        self.text_to_video_models = {
            "zeroscope-v2": {
                "id": "zeroscope-v2",
                "name": "ZeroScope v2",
                "description": "Text-to-video generation model",
                "replicate_id": "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                "max_duration": 5.0,
                "min_duration": 1.0,
                "default_fps": 24,
                "supported_formats": [VideoFormat.MP4],
                "supported_qualities": [VideoQuality.LOW, VideoQuality.MEDIUM],
                "supported_styles": [VideoStyle.ARTISTIC, VideoStyle.STYLIZED]
            },
            "modelscope-t2v": {
                "id": "modelscope-t2v",
                "name": "ModelScope Text-to-Video",
                "description": "ModelScope's text-to-video generation model",
                "replicate_id": "damo-vilab/text-to-video-ms:b790cc5addec66ae18c825b1680f4c4a90a2e4b5e8b5e04d07c3fd62e7fda0e4",
                "max_duration": 4.0,
                "min_duration": 1.0,
                "default_fps": 8,
                "supported_formats": [VideoFormat.MP4],
                "supported_qualities": [VideoQuality.LOW],
                "supported_styles": [VideoStyle.REALISTIC]
            }
        }
        
        # Model mappings for image-to-video
        self.image_to_video_models = {
            "stable-video-diffusion": {
                "id": "stable-video-diffusion",
                "name": "Stable Video Diffusion",
                "description": "Image-to-video generation model",
                "replicate_id": "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                "max_duration": 4.0,
                "min_duration": 1.0,
                "default_fps": 6,
                "supported_formats": [VideoFormat.MP4, VideoFormat.GIF],
                "supported_qualities": [VideoQuality.LOW, VideoQuality.MEDIUM],
                "supported_styles": [VideoStyle.REALISTIC]
            },
            "animatediff": {
                "id": "animatediff",
                "name": "AnimateDiff",
                "description": "Image animation model",
                "replicate_id": "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae20d6d341e85acd5c22b",
                "max_duration": 3.0,
                "min_duration": 1.0,
                "default_fps": 8,
                "supported_formats": [VideoFormat.MP4, VideoFormat.GIF],
                "supported_qualities": [VideoQuality.LOW],
                "supported_styles": [VideoStyle.ANIMATION]
            }
        }
    
    def get_provider_name(self) -> str:
        """Get provider name.
        
        Returns:
            Provider name
        """
        return "replicate"
    
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
        
        # Use zeroscope-v2 model by default
        model_id = model or "zeroscope-v2"
        
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
            # Create model-specific input parameters
            input_params = {}
            
            if model_id == "zeroscope-v2":
                # ZeroScope v2 parameters
                input_params = {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt or "",
                    "video_length": str(int(duration * model_info["default_fps"])),  # Number of frames
                    "fps": fps,
                    "width": width,
                    "height": height,
                    "guidance_scale": kwargs.get("guidance_scale", 7.5),
                    "num_inference_steps": kwargs.get("num_inference_steps", 50)
                }
            elif model_id == "modelscope-t2v":
                # ModelScope parameters
                input_params = {
                    "text": prompt,
                    "negative_prompt": negative_prompt or "",
                    "num_frames": int(duration * model_info["default_fps"]),
                    "width": width,
                    "height": height,
                    "guidance_scale": kwargs.get("guidance_scale", 9.0),
                    "num_inference_steps": kwargs.get("num_inference_steps", 50)
                }
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key not in input_params:
                    input_params[key] = value
            
            # Create prediction
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/predictions",
                    json={
                        "version": model_info["replicate_id"],
                        "input": input_params
                    },
                    headers={
                        "Authorization": f"Token {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 201:
                        error_data = await response.json()
                        raise VideoProviderError(
                            message=error_data.get("detail", "Unknown error"),
                            error_type=VideoProviderErrorType.PROVIDER_ERROR,
                            provider=self.get_provider_name(),
                            status_code=response.status,
                            details=error_data
                        )
                    
                    data = await response.json()
                    
                    # Return result
                    return {
                        "video_url": None,  # Will be available when job completes
                        "preview_url": None,  # Will be available when job completes
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
                            "style": style.value if style else None,
                            "status_url": data.get("urls", {}).get("get")
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
        
        # Use stable-video-diffusion model by default
        model_id = model or "stable-video-diffusion"
        
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
            # Create model-specific input parameters
            input_params = {}
            
            if model_id == "stable-video-diffusion":
                # Stable Video Diffusion parameters
                input_params = {
                    "image": image_url,
                    "prompt": prompt or "",
                    "negative_prompt": negative_prompt or "",
                    "motion_bucket_id": kwargs.get("motion_bucket_id", 127),
                    "num_frames": int(duration * model_info["default_fps"]),
                    "fps": model_info["default_fps"],
                    "noise_aug_strength": kwargs.get("noise_aug_strength", 0.02),
                    "output_format": format.value
                }
            elif model_id == "animatediff":
                # AnimateDiff parameters
                input_params = {
                    "image": image_url,
                    "prompt": prompt or "",
                    "negative_prompt": negative_prompt or "",
                    "num_frames": int(duration * model_info["default_fps"]),
                    "guidance_scale": kwargs.get("guidance_scale", 7.5),
                    "num_inference_steps": kwargs.get("num_inference_steps", 50)
                }
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key not in input_params:
                    input_params[key] = value
            
            # Create prediction
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/predictions",
                    json={
                        "version": model_info["replicate_id"],
                        "input": input_params
                    },
                    headers={
                        "Authorization": f"Token {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 201:
                        error_data = await response.json()
                        raise VideoProviderError(
                            message=error_data.get("detail", "Unknown error"),
                            error_type=VideoProviderErrorType.PROVIDER_ERROR,
                            provider=self.get_provider_name(),
                            status_code=response.status,
                            details=error_data
                        )
                    
                    data = await response.json()
                    
                    # Return result
                    return {
                        "video_url": None,  # Will be available when job completes
                        "preview_url": image_url,
                        "duration": duration,
                        "width": width,
                        "height": height,
                        "model_id": model_id,
                        "provider": self.get_provider_name(),
                        "metadata": {
                            "job_id": data.get("id"),
                            "fps": model_info["default_fps"],
                            "prompt": prompt,
                            "negative_prompt": negative_prompt,
                            "format": format.value,
                            "quality": quality.value,
                            "style": style.value if style else None,
                            "status_url": data.get("urls", {}).get("get")
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
                    f"{self.base_url}/predictions/{job_id}",
                    headers={
                        "Authorization": f"Token {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise VideoProviderError(
                            message=error_data.get("detail", "Unknown error"),
                            error_type=VideoProviderErrorType.PROVIDER_ERROR,
                            provider=self.get_provider_name(),
                            status_code=response.status,
                            details=error_data
                        )
                    
                    data = await response.json()
                    
                    # Map status
                    status_map = {
                        "starting": "processing",
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
                        # Replicate doesn't provide progress percentage, so we estimate
                        if data.get("logs"):
                            # Count the number of step logs
                            step_logs = [log for log in data.get("logs", "").split("\n") if "Step" in log]
                            if step_logs:
                                # Extract the current step and total steps
                                last_step_log = step_logs[-1]
                                try:
                                    current_step = int(last_step_log.split("Step")[1].split("/")[0].strip())
                                    total_steps = int(last_step_log.split("/")[1].split(":")[0].strip())
                                    progress = (current_step / total_steps) * 100
                                except (IndexError, ValueError):
                                    progress = 50  # Default to 50% if parsing fails
                            else:
                                progress = 25  # Early stage
                        else:
                            progress = 10  # Just started
                    
                    # Get output URL
                    output = data.get("output", None)
                    video_url = None
                    
                    if isinstance(output, str):
                        # Single output URL
                        video_url = output
                    elif isinstance(output, list) and output:
                        # List of output URLs, use the first one
                        video_url = output[0]
                    
                    # Return result
                    return {
                        "status": status,
                        "progress": progress,
                        "video_url": video_url,
                        "preview_url": None,  # Replicate doesn't provide preview images
                        "error": data.get("error"),
                        "metadata": {
                            "created_at": data.get("created_at"),
                            "completed_at": data.get("completed_at"),
                            "logs": data.get("logs"),
                            "metrics": data.get("metrics")
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
            # Replicate doesn't have a dedicated quota API, so we check the account
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/account",
                    headers={
                        "Authorization": f"Token {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise VideoProviderError(
                            message=error_data.get("detail", "Unknown error"),
                            error_type=VideoProviderErrorType.PROVIDER_ERROR,
                            provider=self.get_provider_name(),
                            status_code=response.status,
                            details=error_data
                        )
                    
                    data = await response.json()
                    
                    # Return result
                    return {
                        "username": data.get("username"),
                        "name": data.get("name"),
                        "is_active": data.get("is_active", False),
                        "balance": data.get("balance", 0),
                        "quota_used": None,  # Not provided by Replicate
                        "quota_total": None,  # Not provided by Replicate
                        "quota_remaining": None  # Not provided by Replicate
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
