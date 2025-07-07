"""
API endpoints for Firebase Crashlytics management and monitoring.

This module provides REST API endpoints for error reporting,
crash analytics, and system health monitoring.
"""

import logging
import json
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, g
from .firebase_crashlytics import get_crashlytics_manager, crashlytics_monitor
from .feature_flags import require_feature
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint for crashlytics endpoints
crashlytics_bp = Blueprint('crashlytics', __name__, url_prefix='/api/v1/crashlytics')

@crashlytics_bp.route('/report-error', methods=['POST'])
@require_feature("firebase_crashlytics")
def report_error():
    """Report a custom error to Crashlytics.
    
    Returns:
        JSON response with error reporting result
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
                "error_code": "NO_DATA"
            }), 400
        
        # Validate required fields
        if 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required",
                "error_code": "MISSING_MESSAGE"
            }), 400
        
        # Extract error details
        message = data['message']
        severity = data.get('severity', 'ERROR')
        category = data.get('category', 'USER_ERROR')
        context = data.get('context', {})
        user_id = data.get('user_id')
        
        # Validate severity
        crashlytics_manager = get_crashlytics_manager()
        if severity not in crashlytics_manager.SEVERITY_LEVELS:
            return jsonify({
                "success": False,
                "error": f"Invalid severity level: {severity}",
                "error_code": "INVALID_SEVERITY"
            }), 400
        
        # Validate category
        if category not in crashlytics_manager.ERROR_CATEGORIES:
            return jsonify({
                "success": False,
                "error": f"Invalid error category: {category}",
                "error_code": "INVALID_CATEGORY"
            }), 400
        
        # Add request context
        context.update({
            'reported_via': 'api',
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'endpoint': request.endpoint
        })
        
        # Log error to Crashlytics
        error_id = crashlytics_manager.log_error(
            message=message,
            severity=severity,
            category=category,
            context=context,
            user_id=user_id
        )
        
        return jsonify({
            "success": True,
            "error_id": error_id,
            "message": "Error reported successfully"
        })
    except Exception as e:
        logger.error(f"Error in report-error endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@crashlytics_bp.route('/report-exception', methods=['POST'])
@require_feature("firebase_crashlytics")
def report_exception():
    """Report an exception with stack trace to Crashlytics.
    
    Returns:
        JSON response with exception reporting result
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
                "error_code": "NO_DATA"
            }), 400
        
        # Validate required fields
        required_fields = ['exception_type', 'exception_message']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"{field} is required",
                    "error_code": "MISSING_FIELD"
                }), 400
        
        # Extract exception details
        exception_type = data['exception_type']
        exception_message = data['exception_message']
        stack_trace = data.get('stack_trace', [])
        severity = data.get('severity', 'ERROR')
        category = data.get('category', 'SYSTEM_ERROR')
        context = data.get('context', {})
        user_id = data.get('user_id')
        
        # Create a synthetic exception for logging
        try:
            # Create exception class dynamically
            exception_class = type(exception_type, (Exception,), {})
            exception = exception_class(exception_message)
            
            # Add stack trace information to context
            context.update({
                'stack_trace': stack_trace,
                'reported_via': 'api',
                'user_agent': request.headers.get('User-Agent', ''),
                'ip_address': request.remote_addr
            })
            
            # Log exception to Crashlytics
            crashlytics_manager = get_crashlytics_manager()
            error_id = crashlytics_manager.log_exception(
                exception=exception,
                severity=severity,
                category=category,
                context=context,
                user_id=user_id
            )
            
            return jsonify({
                "success": True,
                "error_id": error_id,
                "message": "Exception reported successfully"
            })
        except Exception as inner_e:
            # If we can't create the exception, log as a regular error
            crashlytics_manager = get_crashlytics_manager()
            error_id = crashlytics_manager.log_error(
                message=f"{exception_type}: {exception_message}",
                severity=severity,
                category=category,
                context=context,
                user_id=user_id
            )
            
            return jsonify({
                "success": True,
                "error_id": error_id,
                "message": "Exception reported as error"
            })
    except Exception as e:
        logger.error(f"Error in report-exception endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@crashlytics_bp.route('/set-user', methods=['POST'])
@require_feature("firebase_crashlytics")
def set_user():
    """Set user identifier for crash reports.
    
    Returns:
        JSON response with user setting result
    """
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({
                "success": False,
                "error": "User ID is required",
                "error_code": "MISSING_USER_ID"
            }), 400
        
        user_id = data['user_id']
        user_email = data.get('user_email')
        user_name = data.get('user_name')
        
        # Set user identifier
        crashlytics_manager = get_crashlytics_manager()
        crashlytics_manager.set_user_identifier(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name
        )
        
        return jsonify({
            "success": True,
            "message": "User identifier set successfully"
        })
    except Exception as e:
        logger.error(f"Error in set-user endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@crashlytics_bp.route('/set-custom-key', methods=['POST'])
@require_feature("firebase_crashlytics")
def set_custom_key():
    """Set a custom key-value pair for crash reports.
    
    Returns:
        JSON response with custom key setting result
    """
    try:
        data = request.get_json()
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({
                "success": False,
                "error": "Key and value are required",
                "error_code": "MISSING_KEY_VALUE"
            }), 400
        
        key = data['key']
        value = data['value']
        
        # Validate key format
        if not isinstance(key, str) or len(key) == 0:
            return jsonify({
                "success": False,
                "error": "Key must be a non-empty string",
                "error_code": "INVALID_KEY"
            }), 400
        
        # Set custom key
        crashlytics_manager = get_crashlytics_manager()
        crashlytics_manager.set_custom_key(key, value)
        
        return jsonify({
            "success": True,
            "message": "Custom key set successfully"
        })
    except Exception as e:
        logger.error(f"Error in set-custom-key endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@crashlytics_bp.route('/breadcrumb', methods=['POST'])
@require_feature("firebase_crashlytics")
def log_breadcrumb():
    """Log a breadcrumb for debugging context.
    
    Returns:
        JSON response with breadcrumb logging result
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required",
                "error_code": "MISSING_MESSAGE"
            }), 400
        
        message = data['message']
        category = data.get('category', 'general')
        level = data.get('level', 'info')
        breadcrumb_data = data.get('data', {})
        
        # Log breadcrumb
        crashlytics_manager = get_crashlytics_manager()
        crashlytics_manager.log_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=breadcrumb_data
        )
        
        return jsonify({
            "success": True,
            "message": "Breadcrumb logged successfully"
        })
    except Exception as e:
        logger.error(f"Error in breadcrumb endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@crashlytics_bp.route('/stats', methods=['GET'])
def get_error_stats():
    """Get error tracking statistics.
    
    Returns:
        JSON response with error statistics
    """
    try:
        crashlytics_manager = get_crashlytics_manager()
        stats = crashlytics_manager.get_error_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error in stats endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@crashlytics_bp.route('/health', methods=['GET'])
def health_check():
    """Check Crashlytics system health.
    
    Returns:
        JSON response with health status
    """
    try:
        crashlytics_manager = get_crashlytics_manager()
        stats = crashlytics_manager.get_error_stats()
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        # Check error rate
        if stats['total_errors'] > 100:  # Threshold for concern
            health_status = "warning"
            issues.append("High error count detected")
        
        # Check background thread
        if not stats.get('background_thread_alive', False):
            health_status = "error"
            issues.append("Background processing thread not running")
        
        # Check queue size
        if stats.get('queue_size', 0) > 50:  # Threshold for concern
            health_status = "warning"
            issues.append("Error queue is backing up")
        
        return jsonify({
            "success": True,
            "health": {
                "status": health_status,
                "issues": issues,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error in health endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@crashlytics_bp.route('/test-crash', methods=['POST'])
@require_feature("firebase_crashlytics")
def test_crash():
    """Force a test crash for testing purposes.
    
    Returns:
        This endpoint will always raise an exception
    """
    try:
        data = request.get_json() or {}
        message = data.get('message', 'Test crash from API')
        
        # Force crash
        crashlytics_manager = get_crashlytics_manager()
        crashlytics_manager.force_crash(message)
        
        # This line should never be reached
        return jsonify({
            "success": False,
            "error": "Crash test failed",
            "error_code": "CRASH_FAILED"
        }), 500
    except Exception as e:
        # The exception should be caught by the global error handler
        # and automatically reported to Crashlytics
        raise

@crashlytics_bp.route('/severity-levels', methods=['GET'])
def get_severity_levels():
    """Get available error severity levels.
    
    Returns:
        JSON response with severity levels
    """
    try:
        crashlytics_manager = get_crashlytics_manager()
        
        return jsonify({
            "success": True,
            "severity_levels": list(crashlytics_manager.SEVERITY_LEVELS.keys()),
            "severity_mapping": crashlytics_manager.SEVERITY_LEVELS
        })
    except Exception as e:
        logger.error(f"Error in severity-levels endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@crashlytics_bp.route('/error-categories', methods=['GET'])
def get_error_categories():
    """Get available error categories.
    
    Returns:
        JSON response with error categories
    """
    try:
        crashlytics_manager = get_crashlytics_manager()
        
        return jsonify({
            "success": True,
            "error_categories": list(crashlytics_manager.ERROR_CATEGORIES.keys()),
            "category_mapping": crashlytics_manager.ERROR_CATEGORIES
        })
    except Exception as e:
        logger.error(f"Error in error-categories endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

# Middleware for automatic error context
@crashlytics_bp.before_request
def before_request():
    """Set up request context for error tracking."""
    # Store crashlytics manager in request context
    g.crashlytics_manager = get_crashlytics_manager()
    
    # Log breadcrumb for API request
    g.crashlytics_manager.log_breadcrumb(
        message=f"API Request: {request.method} {request.path}",
        category='api',
        level='info',
        data={
            'method': request.method,
            'path': request.path,
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }
    )

# Error handlers
@crashlytics_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "error_code": "ENDPOINT_NOT_FOUND"
    }), 404

@crashlytics_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "error_code": "METHOD_NOT_ALLOWED"
    }), 405

@crashlytics_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "error_code": "INTERNAL_ERROR"
    }), 500

