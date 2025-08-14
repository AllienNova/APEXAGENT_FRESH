"""
API endpoints for Firebase Remote Config management.

This module provides REST API endpoints for managing feature flags
and configuration parameters through Firebase Remote Config.
"""

import logging
from typing import Dict, Any
from flask import Blueprint, request, jsonify, g
from .firebase_remote_config import get_remote_config_manager
from .feature_flags import require_feature

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint for remote config endpoints
remote_config_bp = Blueprint('remote_config', __name__, url_prefix='/api/v1/config')

@remote_config_bp.route('/feature-flags', methods=['GET'])
def get_feature_flags():
    """Get all feature flags.
    
    Returns:
        JSON response with feature flags
    """
    try:
        manager = get_remote_config_manager()
        config = manager.get_remote_config()
        
        # Filter only feature flags (ending with '_enabled')
        feature_flags = {
            key: value for key, value in config.items()
            if key.endswith('_enabled') or key in ['maintenance_mode', 'debug_mode']
        }
        
        return jsonify({
            "success": True,
            "feature_flags": feature_flags,
            "cache_info": manager.get_cache_info()
        })
    except Exception as e:
        logger.error(f"Error getting feature flags: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/feature-flags/<feature_name>', methods=['GET'])
def get_feature_flag(feature_name: str):
    """Get a specific feature flag.
    
    Args:
        feature_name: Name of the feature flag
        
    Returns:
        JSON response with feature flag value
    """
    try:
        manager = get_remote_config_manager()
        is_enabled = manager.is_feature_enabled(feature_name)
        
        return jsonify({
            "success": True,
            "feature_name": feature_name,
            "enabled": is_enabled
        })
    except Exception as e:
        logger.error(f"Error getting feature flag {feature_name}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/feature-flags/<feature_name>', methods=['PUT'])
def update_feature_flag(feature_name: str):
    """Update a specific feature flag.
    
    Args:
        feature_name: Name of the feature flag
        
    Returns:
        JSON response with update status
    """
    try:
        # Check admin permissions (implement proper auth)
        if not _is_admin_user():
            return jsonify({
                "success": False,
                "error": "Admin access required"
            }), 403
        
        data = request.get_json()
        if not data or 'enabled' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'enabled' field in request body"
            }), 400
        
        enabled = bool(data['enabled'])
        flag_key = f"{feature_name}_enabled"
        
        manager = get_remote_config_manager()
        success = manager.update_remote_config({flag_key: enabled})
        
        if success:
            return jsonify({
                "success": True,
                "feature_name": feature_name,
                "enabled": enabled,
                "message": f"Feature flag '{feature_name}' updated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update feature flag"
            }), 500
    except Exception as e:
        logger.error(f"Error updating feature flag {feature_name}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/parameters', methods=['GET'])
def get_config_parameters():
    """Get all configuration parameters.
    
    Returns:
        JSON response with configuration parameters
    """
    try:
        manager = get_remote_config_manager()
        config = manager.get_remote_config()
        
        # Filter out feature flags, keep only config parameters
        parameters = {
            key: value for key, value in config.items()
            if not key.endswith('_enabled') and key not in ['maintenance_mode', 'debug_mode']
        }
        
        return jsonify({
            "success": True,
            "parameters": parameters,
            "cache_info": manager.get_cache_info()
        })
    except Exception as e:
        logger.error(f"Error getting config parameters: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/parameters/<param_name>', methods=['GET'])
def get_config_parameter(param_name: str):
    """Get a specific configuration parameter.
    
    Args:
        param_name: Name of the configuration parameter
        
    Returns:
        JSON response with parameter value
    """
    try:
        manager = get_remote_config_manager()
        value = manager.get_config_parameter(param_name)
        
        return jsonify({
            "success": True,
            "parameter_name": param_name,
            "value": value
        })
    except Exception as e:
        logger.error(f"Error getting config parameter {param_name}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/parameters/<param_name>', methods=['PUT'])
def update_config_parameter(param_name: str):
    """Update a specific configuration parameter.
    
    Args:
        param_name: Name of the configuration parameter
        
    Returns:
        JSON response with update status
    """
    try:
        # Check admin permissions (implement proper auth)
        if not _is_admin_user():
            return jsonify({
                "success": False,
                "error": "Admin access required"
            }), 403
        
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'value' field in request body"
            }), 400
        
        value = data['value']
        
        manager = get_remote_config_manager()
        success = manager.update_remote_config({param_name: value})
        
        if success:
            return jsonify({
                "success": True,
                "parameter_name": param_name,
                "value": value,
                "message": f"Configuration parameter '{param_name}' updated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update configuration parameter"
            }), 500
    except Exception as e:
        logger.error(f"Error updating config parameter {param_name}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/bulk-update', methods=['PUT'])
def bulk_update_config():
    """Bulk update multiple configuration parameters and feature flags.
    
    Returns:
        JSON response with update status
    """
    try:
        # Check admin permissions (implement proper auth)
        if not _is_admin_user():
            return jsonify({
                "success": False,
                "error": "Admin access required"
            }), 403
        
        data = request.get_json()
        if not data or 'updates' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'updates' field in request body"
            }), 400
        
        updates = data['updates']
        if not isinstance(updates, dict):
            return jsonify({
                "success": False,
                "error": "'updates' must be a dictionary"
            }), 400
        
        manager = get_remote_config_manager()
        success = manager.update_remote_config(updates)
        
        if success:
            return jsonify({
                "success": True,
                "updated_count": len(updates),
                "message": f"Successfully updated {len(updates)} configuration items"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update configuration"
            }), 500
    except Exception as e:
        logger.error(f"Error bulk updating config: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/refresh', methods=['POST'])
def refresh_config():
    """Force refresh of the configuration cache.
    
    Returns:
        JSON response with refresh status
    """
    try:
        manager = get_remote_config_manager()
        success = manager.refresh_cache()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Configuration cache refreshed successfully",
                "cache_info": manager.get_cache_info()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to refresh configuration cache"
            }), 500
    except Exception as e:
        logger.error(f"Error refreshing config cache: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/initialize', methods=['POST'])
def initialize_default_config():
    """Initialize remote config with default values.
    
    Returns:
        JSON response with initialization status
    """
    try:
        # Check admin permissions (implement proper auth)
        if not _is_admin_user():
            return jsonify({
                "success": False,
                "error": "Admin access required"
            }), 403
        
        manager = get_remote_config_manager()
        success = manager.initialize_default_config()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Default configuration initialized successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to initialize default configuration"
            }), 500
    except Exception as e:
        logger.error(f"Error initializing default config: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@remote_config_bp.route('/status', methods=['GET'])
def get_config_status():
    """Get the current status of remote configuration.
    
    Returns:
        JSON response with configuration status
    """
    try:
        manager = get_remote_config_manager()
        
        # Get basic status information
        is_maintenance = manager.is_maintenance_mode()
        cache_info = manager.get_cache_info()
        
        # Get some key configuration values
        rate_limit = manager.get_rate_limit()
        free_tier_limit = manager.get_tier_daily_limit('free')
        premium_tier_limit = manager.get_tier_daily_limit('premium')
        
        return jsonify({
            "success": True,
            "status": {
                "maintenance_mode": is_maintenance,
                "maintenance_message": manager.get_maintenance_message() if is_maintenance else None,
                "rate_limit_per_minute": rate_limit,
                "tier_limits": {
                    "free": free_tier_limit,
                    "premium": premium_tier_limit
                },
                "cache_info": cache_info
            }
        })
    except Exception as e:
        logger.error(f"Error getting config status: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def _is_admin_user() -> bool:
    """Check if the current user has admin privileges.
    
    Returns:
        True if user is admin, False otherwise
    """
    # This is a placeholder implementation
    # In production, implement proper authentication and authorization
    auth_header = request.headers.get('Authorization', '')
    
    # For now, check for a simple admin token
    # In production, this should use proper JWT validation
    return 'admin-token' in auth_header.lower()

# Error handlers
@remote_config_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@remote_config_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405

@remote_config_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

