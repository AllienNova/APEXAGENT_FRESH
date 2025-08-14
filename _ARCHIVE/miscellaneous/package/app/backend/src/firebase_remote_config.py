"""
Firebase Remote Config integration for Aideon AI Lite.

This module provides feature flag management through Firebase Remote Config,
enabling dynamic configuration updates without requiring app redeployment.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, remote_config
from firebase_admin.exceptions import FirebaseError

# Configure logging
logger = logging.getLogger(__name__)

class FirebaseRemoteConfigManager:
    """Manages feature flags and remote configuration through Firebase Remote Config."""
    
    # Default feature flags
    DEFAULT_FEATURE_FLAGS = {
        "together_ai_enabled": True,
        "video_generation_enabled": True,
        "llamacoder_integration_enabled": False,
        "free_tier_enabled": True,
        "premium_tier_enabled": True,
        "analytics_enabled": True,
        "debug_mode": False,
        "maintenance_mode": False,
        "new_user_registration": True,
        "experimental_features": False
    }
    
    # Default configuration parameters
    DEFAULT_CONFIG_PARAMS = {
        "max_concurrent_requests": 10,
        "request_timeout_seconds": 30,
        "cache_ttl_minutes": 60,
        "rate_limit_per_minute": 100,
        "free_tier_daily_limit": 50,
        "premium_tier_daily_limit": 1000,
        "maintenance_message": "System maintenance in progress. Please try again later.",
        "feature_announcement": "",
        "api_version": "v1"
    }
    
    def __init__(self, project_id: str = "aideonlite-ai", 
                 credentials_path: Optional[str] = None):
        """Initialize Firebase Remote Config manager.
        
        Args:
            project_id: Firebase project ID
            credentials_path: Path to Firebase service account credentials
        """
        self.project_id = project_id
        self.credentials_path = credentials_path
        self._app = None
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = timedelta(minutes=5)  # 5-minute cache
        
        self._initialize_firebase()
    
    def _initialize_firebase(self) -> bool:
        """Initialize Firebase Admin SDK.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                if self.credentials_path and os.path.exists(self.credentials_path):
                    # Use service account credentials
                    cred = credentials.Certificate(self.credentials_path)
                    self._app = firebase_admin.initialize_app(cred, {
                        'projectId': self.project_id
                    })
                else:
                    # Use default credentials (for production environment)
                    self._app = firebase_admin.initialize_app(options={
                        'projectId': self.project_id
                    })
            else:
                self._app = firebase_admin.get_app()
            
            logger.info("Firebase Remote Config initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Remote Config: {str(e)}")
            return False
    
    def _is_cache_valid(self) -> bool:
        """Check if the cache is still valid.
        
        Returns:
            True if cache is valid, False otherwise
        """
        if self._cache_timestamp is None:
            return False
        
        return datetime.now() - self._cache_timestamp < self._cache_ttl
    
    def _update_cache(self, config_data: Dict[str, Any]) -> None:
        """Update the local cache with new configuration data.
        
        Args:
            config_data: Configuration data to cache
        """
        self._cache = config_data
        self._cache_timestamp = datetime.now()
    
    def get_remote_config(self, use_cache: bool = True) -> Dict[str, Any]:
        """Fetch the current remote configuration.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            Remote configuration dictionary
        """
        try:
            # Return cached data if valid and requested
            if use_cache and self._is_cache_valid():
                return self._cache
            
            # Fetch from Firebase Remote Config
            template = remote_config.get_template()
            
            config_data = {}
            
            # Extract parameters
            for param_name, param in template.parameters.items():
                try:
                    # Get the default value
                    default_value = param.default_value.value
                    
                    # Try to parse as JSON for complex types
                    try:
                        config_data[param_name] = json.loads(default_value)
                    except (json.JSONDecodeError, TypeError):
                        # Use as string if not valid JSON
                        config_data[param_name] = default_value
                except Exception as e:
                    logger.warning(f"Error processing parameter {param_name}: {str(e)}")
                    continue
            
            # Update cache
            self._update_cache(config_data)
            
            return config_data
        except FirebaseError as e:
            logger.error(f"Firebase error fetching remote config: {str(e)}")
            return self._get_fallback_config()
        except Exception as e:
            logger.error(f"Error fetching remote config: {str(e)}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration when remote config is unavailable.
        
        Returns:
            Fallback configuration dictionary
        """
        fallback_config = {}
        fallback_config.update(self.DEFAULT_FEATURE_FLAGS)
        fallback_config.update(self.DEFAULT_CONFIG_PARAMS)
        
        # Use cached data if available
        if self._cache:
            fallback_config.update(self._cache)
        
        return fallback_config
    
    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get a feature flag value.
        
        Args:
            flag_name: Name of the feature flag
            default: Default value if flag is not found
            
        Returns:
            Feature flag value
        """
        try:
            config = self.get_remote_config()
            value = config.get(flag_name, default)
            
            # Ensure boolean type
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            
            return bool(value)
        except Exception as e:
            logger.error(f"Error getting feature flag {flag_name}: {str(e)}")
            return default
    
    def get_config_parameter(self, param_name: str, 
                           default: Union[str, int, float] = None) -> Union[str, int, float]:
        """Get a configuration parameter value.
        
        Args:
            param_name: Name of the configuration parameter
            default: Default value if parameter is not found
            
        Returns:
            Configuration parameter value
        """
        try:
            config = self.get_remote_config()
            value = config.get(param_name, default)
            
            # Try to convert to appropriate type
            if isinstance(value, str):
                # Try integer conversion
                try:
                    return int(value)
                except ValueError:
                    pass
                
                # Try float conversion
                try:
                    return float(value)
                except ValueError:
                    pass
            
            return value
        except Exception as e:
            logger.error(f"Error getting config parameter {param_name}: {str(e)}")
            return default
    
    def update_remote_config(self, updates: Dict[str, Any]) -> bool:
        """Update remote configuration parameters.
        
        Args:
            updates: Dictionary of parameter updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current template
            template = remote_config.get_template()
            
            # Update parameters
            for param_name, value in updates.items():
                # Convert value to string for Firebase
                if isinstance(value, (dict, list)):
                    string_value = json.dumps(value)
                else:
                    string_value = str(value)
                
                # Create or update parameter
                template.parameters[param_name] = remote_config.Parameter(
                    default_value=remote_config.ParameterValue(string_value),
                    description=f"Updated via API at {datetime.now().isoformat()}"
                )
            
            # Validate and publish template
            validated_template = remote_config.validate_template(template)
            remote_config.publish_template(validated_template)
            
            # Clear cache to force refresh
            self._cache = {}
            self._cache_timestamp = None
            
            logger.info(f"Successfully updated {len(updates)} remote config parameters")
            return True
        except FirebaseError as e:
            logger.error(f"Firebase error updating remote config: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating remote config: {str(e)}")
            return False
    
    def initialize_default_config(self) -> bool:
        """Initialize remote config with default values.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Combine default feature flags and config parameters
            default_config = {}
            default_config.update(self.DEFAULT_FEATURE_FLAGS)
            default_config.update(self.DEFAULT_CONFIG_PARAMS)
            
            return self.update_remote_config(default_config)
        except Exception as e:
            logger.error(f"Error initializing default config: {str(e)}")
            return False
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a specific feature is enabled.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            True if feature is enabled, False otherwise
        """
        return self.get_feature_flag(f"{feature_name}_enabled", False)
    
    def is_maintenance_mode(self) -> bool:
        """Check if the system is in maintenance mode.
        
        Returns:
            True if in maintenance mode, False otherwise
        """
        return self.get_feature_flag("maintenance_mode", False)
    
    def get_maintenance_message(self) -> str:
        """Get the maintenance mode message.
        
        Returns:
            Maintenance message
        """
        return self.get_config_parameter("maintenance_message", 
                                       "System maintenance in progress. Please try again later.")
    
    def get_rate_limit(self) -> int:
        """Get the current rate limit per minute.
        
        Returns:
            Rate limit value
        """
        return self.get_config_parameter("rate_limit_per_minute", 100)
    
    def get_tier_daily_limit(self, tier: str) -> int:
        """Get the daily limit for a specific tier.
        
        Args:
            tier: Tier name (free, premium, etc.)
            
        Returns:
            Daily limit value
        """
        param_name = f"{tier}_tier_daily_limit"
        default_limits = {
            "free": 50,
            "premium": 1000,
            "expert": 10000
        }
        
        return self.get_config_parameter(param_name, default_limits.get(tier, 50))
    
    def refresh_cache(self) -> bool:
        """Force refresh of the configuration cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._cache = {}
            self._cache_timestamp = None
            self.get_remote_config(use_cache=False)
            return True
        except Exception as e:
            logger.error(f"Error refreshing cache: {str(e)}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state.
        
        Returns:
            Cache information dictionary
        """
        return {
            "cache_size": len(self._cache),
            "cache_timestamp": self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            "cache_valid": self._is_cache_valid(),
            "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60
        }

# Global instance for easy access
remote_config_manager = None

def get_remote_config_manager() -> FirebaseRemoteConfigManager:
    """Get the global remote config manager instance.
    
    Returns:
        FirebaseRemoteConfigManager instance
    """
    global remote_config_manager
    
    if remote_config_manager is None:
        remote_config_manager = FirebaseRemoteConfigManager()
    
    return remote_config_manager

def is_feature_enabled(feature_name: str) -> bool:
    """Convenience function to check if a feature is enabled.
    
    Args:
        feature_name: Name of the feature
        
    Returns:
        True if feature is enabled, False otherwise
    """
    manager = get_remote_config_manager()
    return manager.is_feature_enabled(feature_name)

def get_config_value(param_name: str, default: Any = None) -> Any:
    """Convenience function to get a configuration value.
    
    Args:
        param_name: Name of the configuration parameter
        default: Default value if parameter is not found
        
    Returns:
        Configuration value
    """
    manager = get_remote_config_manager()
    return manager.get_config_parameter(param_name, default)

