"""
Feature flag middleware for Aideon AI Lite.

This middleware integrates with Firebase Remote Config to provide
feature flag functionality throughout the application.
"""

import logging
from typing import Dict, Any, Optional
from functools import wraps
from flask import request, jsonify, g
from .firebase_remote_config import get_remote_config_manager

# Configure logging
logger = logging.getLogger(__name__)

class FeatureFlagMiddleware:
    """Middleware for handling feature flags in Flask applications."""
    
    def __init__(self, app=None):
        """Initialize the feature flag middleware.
        
        Args:
            app: Flask application instance (optional)
        """
        self.app = app
        self.remote_config_manager = get_remote_config_manager()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with a Flask app.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        # Register before_request handler
        app.before_request(self.before_request)
        
        # Register context processor for templates
        app.context_processor(self.inject_feature_flags)
    
    def before_request(self):
        """Before request handler to load feature flags."""
        try:
            # Load feature flags into Flask's g object
            g.feature_flags = self.remote_config_manager.get_remote_config()
            g.is_maintenance_mode = self.remote_config_manager.is_maintenance_mode()
            
            # Check maintenance mode
            if g.is_maintenance_mode and not self._is_admin_request():
                maintenance_message = self.remote_config_manager.get_maintenance_message()
                return jsonify({
                    "error": "maintenance_mode",
                    "message": maintenance_message
                }), 503
        except Exception as e:
            logger.error(f"Error in feature flag middleware: {str(e)}")
            # Continue with default behavior if feature flags fail
            g.feature_flags = {}
            g.is_maintenance_mode = False
    
    def _is_admin_request(self) -> bool:
        """Check if the current request is from an admin.
        
        Returns:
            True if admin request, False otherwise
        """
        # Check for admin authentication
        # This should be implemented based on your authentication system
        auth_header = request.headers.get('Authorization', '')
        
        # For now, check for a simple admin token
        # In production, this should use proper JWT validation
        return 'admin-token' in auth_header.lower()
    
    def inject_feature_flags(self) -> Dict[str, Any]:
        """Inject feature flags into template context.
        
        Returns:
            Dictionary of feature flags for templates
        """
        return {
            'feature_flags': getattr(g, 'feature_flags', {}),
            'is_maintenance_mode': getattr(g, 'is_maintenance_mode', False)
        }

def require_feature(feature_name: str, enabled: bool = True):
    """Decorator to require a specific feature flag.
    
    Args:
        feature_name: Name of the feature flag
        enabled: Required state of the feature flag
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                manager = get_remote_config_manager()
                is_enabled = manager.is_feature_enabled(feature_name)
                
                if is_enabled != enabled:
                    return jsonify({
                        "error": "feature_disabled",
                        "message": f"Feature '{feature_name}' is not available"
                    }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error checking feature flag {feature_name}: {str(e)}")
                # Allow access if feature flag check fails
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled in the current request context.
    
    Args:
        feature_name: Name of the feature
        
    Returns:
        True if feature is enabled, False otherwise
    """
    try:
        feature_flags = getattr(g, 'feature_flags', {})
        flag_key = f"{feature_name}_enabled"
        return feature_flags.get(flag_key, False)
    except Exception as e:
        logger.error(f"Error checking feature {feature_name}: {str(e)}")
        return False

def get_config_value(param_name: str, default: Any = None) -> Any:
    """Get a configuration value in the current request context.
    
    Args:
        param_name: Name of the configuration parameter
        default: Default value if parameter is not found
        
    Returns:
        Configuration value
    """
    try:
        feature_flags = getattr(g, 'feature_flags', {})
        return feature_flags.get(param_name, default)
    except Exception as e:
        logger.error(f"Error getting config value {param_name}: {str(e)}")
        return default

def tier_rate_limit(tier: str):
    """Decorator to apply rate limiting based on user tier.
    
    Args:
        tier: User tier (free, premium, expert)
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                manager = get_remote_config_manager()
                daily_limit = manager.get_tier_daily_limit(tier)
                
                # Here you would implement actual rate limiting logic
                # This is a placeholder for the rate limiting implementation
                # You would typically check against a database or cache
                
                # For now, just log the limit
                logger.info(f"Rate limit for {tier} tier: {daily_limit} requests per day")
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error applying rate limit for tier {tier}: {str(e)}")
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Convenience decorators for common features
require_together_ai = lambda f: require_feature("together_ai")(f)
require_video_generation = lambda f: require_feature("video_generation")(f)
require_llamacoder = lambda f: require_feature("llamacoder_integration")(f)
require_analytics = lambda f: require_feature("analytics")(f)

