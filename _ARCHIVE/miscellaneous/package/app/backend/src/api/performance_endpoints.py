"""
API endpoints for Firebase Performance Monitoring management.

This module provides REST API endpoints for performance monitoring,
metrics collection, and system health tracking.
"""

import logging
import json
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, g
from .firebase_performance import get_performance_manager, performance_monitor
from .feature_flags import require_feature
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint for performance endpoints
performance_bp = Blueprint('performance', __name__, url_prefix='/api/v1/performance')

@performance_bp.route('/start-trace', methods=['POST'])
@require_feature("firebase_performance")
def start_trace():
    """Start a custom performance trace.
    
    Returns:
        JSON response with trace start result
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
        if 'name' not in data:
            return jsonify({
                "success": False,
                "error": "Trace name is required",
                "error_code": "MISSING_NAME"
            }), 400
        
        # Extract trace details
        name = data['name']
        trace_type = data.get('trace_type', 'CUSTOM_TRACE')
        attributes = data.get('attributes', {})
        
        # Validate trace type
        manager = get_performance_manager()
        if trace_type not in manager.METRIC_TYPES:
            return jsonify({
                "success": False,
                "error": f"Invalid trace type: {trace_type}",
                "error_code": "INVALID_TRACE_TYPE"
            }), 400
        
        # Add request context
        attributes.update({
            'started_via': 'api',
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        })
        
        # Start trace
        trace = manager.start_trace(
            name=name,
            trace_type=trace_type,
            attributes=attributes
        )
        
        # Store trace in session for later stopping
        if not hasattr(g, 'active_traces'):
            g.active_traces = {}
        g.active_traces[trace.trace_id] = trace
        
        return jsonify({
            "success": True,
            "trace_id": trace.trace_id,
            "message": "Trace started successfully"
        })
    except Exception as e:
        logger.error(f"Error in start-trace endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@performance_bp.route('/stop-trace', methods=['POST'])
@require_feature("firebase_performance")
def stop_trace():
    """Stop a custom performance trace.
    
    Returns:
        JSON response with trace stop result
    """
    try:
        data = request.get_json()
        if not data or 'trace_id' not in data:
            return jsonify({
                "success": False,
                "error": "Trace ID is required",
                "error_code": "MISSING_TRACE_ID"
            }), 400
        
        trace_id = data['trace_id']
        
        # Get trace from session or active traces
        manager = get_performance_manager()
        trace = None
        
        if hasattr(g, 'active_traces') and trace_id in g.active_traces:
            trace = g.active_traces[trace_id]
        elif trace_id in manager._active_traces:
            trace = manager._active_traces[trace_id]
        
        if not trace:
            return jsonify({
                "success": False,
                "error": "Trace not found",
                "error_code": "TRACE_NOT_FOUND"
            }), 404
        
        # Add any additional attributes
        additional_attributes = data.get('attributes', {})
        for key, value in additional_attributes.items():
            trace.add_attribute(key, value)
        
        # Stop trace
        manager.stop_trace(trace)
        
        # Remove from session
        if hasattr(g, 'active_traces') and trace_id in g.active_traces:
            del g.active_traces[trace_id]
        
        return jsonify({
            "success": True,
            "trace_id": trace_id,
            "duration": trace.duration,
            "message": "Trace stopped successfully"
        })
    except Exception as e:
        logger.error(f"Error in stop-trace endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@performance_bp.route('/add-metric', methods=['POST'])
@require_feature("firebase_performance")
def add_metric():
    """Add a custom metric to a trace.
    
    Returns:
        JSON response with metric addition result
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
        required_fields = ['trace_id', 'metric_name', 'value']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"{field} is required",
                    "error_code": "MISSING_FIELD"
                }), 400
        
        trace_id = data['trace_id']
        metric_name = data['metric_name']
        value = data['value']
        
        # Validate value type
        if not isinstance(value, (int, float)):
            return jsonify({
                "success": False,
                "error": "Metric value must be a number",
                "error_code": "INVALID_VALUE_TYPE"
            }), 400
        
        # Get trace
        manager = get_performance_manager()
        trace = None
        
        if hasattr(g, 'active_traces') and trace_id in g.active_traces:
            trace = g.active_traces[trace_id]
        elif trace_id in manager._active_traces:
            trace = manager._active_traces[trace_id]
        
        if not trace:
            return jsonify({
                "success": False,
                "error": "Trace not found",
                "error_code": "TRACE_NOT_FOUND"
            }), 404
        
        # Add metric
        trace.add_metric(metric_name, value)
        
        return jsonify({
            "success": True,
            "message": "Metric added successfully"
        })
    except Exception as e:
        logger.error(f"Error in add-metric endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@performance_bp.route('/stats', methods=['GET'])
def get_performance_stats():
    """Get performance statistics.
    
    Returns:
        JSON response with performance statistics
    """
    try:
        manager = get_performance_manager()
        stats = manager.get_performance_stats()
        
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

@performance_bp.route('/trace-summary', methods=['GET'])
def get_trace_summary():
    """Get trace summary statistics.
    
    Returns:
        JSON response with trace summary
    """
    try:
        trace_type = request.args.get('trace_type')
        
        manager = get_performance_manager()
        summary = manager.get_trace_summary(trace_type)
        
        return jsonify({
            "success": True,
            "summary": summary,
            "trace_type": trace_type
        })
    except Exception as e:
        logger.error(f"Error in trace-summary endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@performance_bp.route('/system-metrics', methods=['GET'])
def get_system_metrics():
    """Get current system metrics.
    
    Returns:
        JSON response with system metrics
    """
    try:
        manager = get_performance_manager()
        stats = manager.get_performance_stats()
        system_metrics = stats.get('system_metrics', {})
        
        return jsonify({
            "success": True,
            "metrics": system_metrics
        })
    except Exception as e:
        logger.error(f"Error in system-metrics endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@performance_bp.route('/slow-operations', methods=['GET'])
def get_slow_operations():
    """Get recent slow operations.
    
    Returns:
        JSON response with slow operations
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        
        manager = get_performance_manager()
        stats = manager.get_performance_stats()
        slow_ops = stats.get('recent_slow_operations', [])
        
        # Limit results
        if limit > 0:
            slow_ops = slow_ops[-limit:]
        
        return jsonify({
            "success": True,
            "slow_operations": slow_ops,
            "total_count": stats.get('slow_operations_count', 0)
        })
    except Exception as e:
        logger.error(f"Error in slow-operations endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@performance_bp.route('/health', methods=['GET'])
def health_check():
    """Check performance monitoring system health.
    
    Returns:
        JSON response with health status
    """
    try:
        manager = get_performance_manager()
        stats = manager.get_performance_stats()
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        # Check monitoring thread
        if not stats.get('monitoring_thread_alive', False):
            health_status = "error"
            issues.append("Background monitoring thread not running")
        
        # Check system metrics
        system_metrics = stats.get('system_metrics', {})
        if system_metrics:
            cpu_percent = system_metrics.get('cpu', {}).get('percent', 0)
            memory_percent = system_metrics.get('memory', {}).get('percent', 0)
            disk_percent = system_metrics.get('disk', {}).get('percent', 0)
            
            if cpu_percent > 80:
                health_status = "warning" if health_status == "healthy" else health_status
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory_percent > 85:
                health_status = "warning" if health_status == "healthy" else health_status
                issues.append(f"High memory usage: {memory_percent:.1f}%")
            
            if disk_percent > 90:
                health_status = "warning" if health_status == "healthy" else health_status
                issues.append(f"High disk usage: {disk_percent:.1f}%")
        
        # Check slow operations
        slow_ops_count = stats.get('slow_operations_count', 0)
        if slow_ops_count > 10:
            health_status = "warning" if health_status == "healthy" else health_status
            issues.append(f"High number of slow operations: {slow_ops_count}")
        
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

@performance_bp.route('/metric-types', methods=['GET'])
def get_metric_types():
    """Get available metric types.
    
    Returns:
        JSON response with metric types
    """
    try:
        manager = get_performance_manager()
        
        return jsonify({
            "success": True,
            "metric_types": list(manager.METRIC_TYPES.keys()),
            "type_mapping": manager.METRIC_TYPES
        })
    except Exception as e:
        logger.error(f"Error in metric-types endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@performance_bp.route('/thresholds', methods=['GET'])
def get_performance_thresholds():
    """Get performance thresholds.
    
    Returns:
        JSON response with performance thresholds
    """
    try:
        manager = get_performance_manager()
        
        return jsonify({
            "success": True,
            "thresholds": manager.PERFORMANCE_THRESHOLDS
        })
    except Exception as e:
        logger.error(f"Error in thresholds endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@performance_bp.route('/benchmark', methods=['POST'])
@require_feature("firebase_performance")
@performance_monitor(name="benchmark_test", trace_type="CUSTOM_TRACE")
def run_benchmark():
    """Run a performance benchmark test.
    
    Returns:
        JSON response with benchmark results
    """
    try:
        data = request.get_json() or {}
        test_type = data.get('test_type', 'cpu')
        duration = data.get('duration', 1.0)
        
        # Validate duration
        if duration > 10.0:
            return jsonify({
                "success": False,
                "error": "Duration cannot exceed 10 seconds",
                "error_code": "DURATION_TOO_LONG"
            }), 400
        
        import time
        start_time = time.time()
        
        if test_type == 'cpu':
            # CPU intensive test
            result = 0
            end_time = start_time + duration
            while time.time() < end_time:
                result += 1
        elif test_type == 'memory':
            # Memory allocation test
            data_list = []
            end_time = start_time + duration
            while time.time() < end_time:
                data_list.append([0] * 1000)
            result = len(data_list)
        else:
            return jsonify({
                "success": False,
                "error": "Invalid test type",
                "error_code": "INVALID_TEST_TYPE"
            }), 400
        
        actual_duration = time.time() - start_time
        
        return jsonify({
            "success": True,
            "benchmark": {
                "test_type": test_type,
                "requested_duration": duration,
                "actual_duration": actual_duration,
                "result": result
            }
        })
    except Exception as e:
        logger.error(f"Error in benchmark endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

# Middleware for automatic performance context
@performance_bp.before_request
def before_request():
    """Set up request context for performance tracking."""
    # Store performance manager in request context
    g.performance_manager = get_performance_manager()

# Error handlers
@performance_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "error_code": "ENDPOINT_NOT_FOUND"
    }), 404

@performance_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "error_code": "METHOD_NOT_ALLOWED"
    }), 405

@performance_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "error_code": "INTERNAL_ERROR"
    }), 500

