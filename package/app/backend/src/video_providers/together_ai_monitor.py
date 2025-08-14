"""
Manual monitoring trigger and admin notifications for Together AI video model releases.

This module provides functionality to manually check for new Together AI video models
and send notifications to administrators when new models are detected.
"""

import os
import logging
import json
import time
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class TogetherAIModelMonitor:
    """Together AI model monitor for video capabilities."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super(TogetherAIModelMonitor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        config_path: str = "/etc/aideon/together_ai/model_monitor.json",
        api_key: Optional[str] = None
    ):
        """Initialize the monitor.
        
        Args:
            config_path: Path to configuration file
            api_key: Together AI API key (optional)
        """
        if self._initialized:
            return
        
        self.config_path = config_path
        self.api_key = api_key
        
        # Load configuration
        self.config = self._load_config()
        
        # Set API key if provided
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self.config.get("api_key", "")
        
        # Known models
        self.known_models = self.config.get("known_models", {})
        
        # Admin notification settings
        self.notification_settings = self.config.get("notification_settings", {
            "enabled": True,
            "email_recipients": [],
            "slack_webhook": "",
            "admin_dashboard_notifications": True
        })
        
        # Last check timestamp
        self.last_check = self.config.get("last_check", None)
        
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
                    "api_key": "",
                    "known_models": {},
                    "notification_settings": {
                        "enabled": True,
                        "email_recipients": [],
                        "slack_webhook": "",
                        "admin_dashboard_notifications": True
                    },
                    "last_check": None
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
                "api_key": "",
                "known_models": {},
                "notification_settings": {
                    "enabled": True,
                    "email_recipients": [],
                    "slack_webhook": "",
                    "admin_dashboard_notifications": True
                },
                "last_check": None
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
    
    def set_api_key(self, api_key: str) -> bool:
        """Set Together AI API key.
        
        Args:
            api_key: Together AI API key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.api_key = api_key
            self.config["api_key"] = api_key
            return self._save_config()
        except Exception as e:
            logger.error(f"Error setting API key: {str(e)}")
            return False
    
    def update_notification_settings(self, settings: Dict[str, Any]) -> bool:
        """Update notification settings.
        
        Args:
            settings: Notification settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in settings.items():
                self.notification_settings[key] = value
            
            self.config["notification_settings"] = self.notification_settings
            return self._save_config()
        except Exception as e:
            logger.error(f"Error updating notification settings: {str(e)}")
            return False
    
    async def fetch_available_models(self) -> Dict[str, Any]:
        """Fetch available models from Together AI API.
        
        Returns:
            Dictionary containing available models
                
        Raises:
            Exception: If API request fails
        """
        if not self.api_key:
            raise ValueError("API key not set")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.together.xyz/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(f"API request failed: {error_data}")
                    
                    data = await response.json()
                    return data
        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            raise
    
    def _detect_video_models(self, models_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect video models from API response.
        
        Args:
            models_data: API response data
            
        Returns:
            List of video models
        """
        video_models = []
        
        # Extract models list
        models = models_data.get("models", [])
        
        for model in models:
            # Check if model is a video model
            is_video_model = False
            
            # Check model name
            model_name = model.get("name", "").lower()
            if any(keyword in model_name for keyword in ["video", "motion", "animation", "animate", "mov"]):
                is_video_model = True
            
            # Check model description
            model_description = model.get("description", "").lower()
            if any(keyword in model_description for keyword in ["video", "motion", "animation", "animate", "mov"]):
                is_video_model = True
            
            # Check model tags
            model_tags = model.get("tags", [])
            if any(keyword in tag.lower() for tag in model_tags for keyword in ["video", "motion", "animation", "animate", "mov"]):
                is_video_model = True
            
            # Check model capabilities
            model_capabilities = model.get("capabilities", [])
            if "video-generation" in model_capabilities or "video" in model_capabilities:
                is_video_model = True
            
            if is_video_model:
                video_models.append(model)
        
        return video_models
    
    def _detect_new_models(self, video_models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect new video models.
        
        Args:
            video_models: List of video models
            
        Returns:
            List of new video models
        """
        new_models = []
        
        for model in video_models:
            model_id = model.get("id", "")
            
            # Check if model is new
            if model_id not in self.known_models:
                new_models.append(model)
                
                # Add to known models
                self.known_models[model_id] = {
                    "name": model.get("name", ""),
                    "description": model.get("description", ""),
                    "discovered_at": datetime.now().isoformat()
                }
        
        return new_models
    
    async def _send_notifications(self, new_models: List[Dict[str, Any]]) -> bool:
        """Send notifications about new models.
        
        Args:
            new_models: List of new models
            
        Returns:
            True if notifications were sent, False otherwise
        """
        if not self.notification_settings.get("enabled", True):
            return False
        
        if not new_models:
            return False
        
        # Format notification message
        message = f"🎉 {len(new_models)} new Together AI video model(s) detected!\n\n"
        
        for model in new_models:
            message += f"• {model.get('name', 'Unknown')}: {model.get('description', 'No description')}\n"
        
        message += f"\nDetected at: {datetime.now().isoformat()}"
        
        # Send email notifications
        email_recipients = self.notification_settings.get("email_recipients", [])
        if email_recipients:
            try:
                # In a real implementation, this would use an email service
                logger.info(f"Would send email to {email_recipients}: {message}")
            except Exception as e:
                logger.error(f"Error sending email notifications: {str(e)}")
        
        # Send Slack notifications
        slack_webhook = self.notification_settings.get("slack_webhook", "")
        if slack_webhook:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        slack_webhook,
                        json={
                            "text": message
                        }
                    )
            except Exception as e:
                logger.error(f"Error sending Slack notifications: {str(e)}")
        
        # Send admin dashboard notifications
        if self.notification_settings.get("admin_dashboard_notifications", True):
            try:
                # In a real implementation, this would use the admin dashboard notification system
                logger.info(f"Would send admin dashboard notification: {message}")
                
                # Store notification in admin notifications database
                from src.admin.notifications import AdminNotificationManager
                try:
                    notification_manager = AdminNotificationManager()
                    await notification_manager.add_notification(
                        title="New Together AI Video Models Detected",
                        message=message,
                        notification_type="model_update",
                        priority="high",
                        data={
                            "models": [
                                {
                                    "id": model.get("id", ""),
                                    "name": model.get("name", ""),
                                    "description": model.get("description", "")
                                }
                                for model in new_models
                            ]
                        }
                    )
                except Exception as e:
                    logger.error(f"Error storing admin notification: {str(e)}")
            except Exception as e:
                logger.error(f"Error sending admin dashboard notifications: {str(e)}")
        
        return True
    
    async def check_for_new_models(self) -> Dict[str, Any]:
        """Check for new Together AI video models.
        
        Returns:
            Dictionary containing check results
        """
        try:
            # Fetch available models
            models_data = await self.fetch_available_models()
            
            # Detect video models
            video_models = self._detect_video_models(models_data)
            
            # Detect new models
            new_models = self._detect_new_models(video_models)
            
            # Send notifications
            notifications_sent = await self._send_notifications(new_models)
            
            # Update last check timestamp
            self.last_check = datetime.now().isoformat()
            self.config["last_check"] = self.last_check
            
            # Update known models
            self.config["known_models"] = self.known_models
            
            # Save configuration
            self._save_config()
            
            # Return results
            return {
                "timestamp": self.last_check,
                "total_models": len(models_data.get("models", [])),
                "video_models": len(video_models),
                "new_models": len(new_models),
                "new_model_details": [
                    {
                        "id": model.get("id", ""),
                        "name": model.get("name", ""),
                        "description": model.get("description", "")
                    }
                    for model in new_models
                ],
                "notifications_sent": notifications_sent
            }
        except Exception as e:
            logger.error(f"Error checking for new models: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_last_check_info(self) -> Dict[str, Any]:
        """Get information about the last check.
        
        Returns:
            Dictionary containing last check information
        """
        return {
            "last_check": self.last_check,
            "known_models_count": len(self.known_models),
            "notification_settings": self.notification_settings
        }
    
    def get_known_models(self) -> Dict[str, Any]:
        """Get known models.
        
        Returns:
            Dictionary of known models
        """
        return self.known_models

def get_together_ai_model_monitor(api_key: Optional[str] = None) -> TogetherAIModelMonitor:
    """Get the Together AI model monitor singleton.
    
    Args:
        api_key: Together AI API key (optional)
        
    Returns:
        Together AI model monitor instance
    """
    return TogetherAIModelMonitor(api_key=api_key)
