"""
Firebase Performance Monitoring integration for Aideon AI Lite.

This module provides comprehensive performance monitoring and analytics
through Firebase Performance Monitoring, enabling real-time performance
tracking and optimization.
"""

import os
import time
import logging
import threading
import uuid
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import firebase_admin
from firebase_admin import credentials
from firebase_admin.exceptions import FirebaseError
from flask import Flask, request, g, jsonify
import psutil
import gc

# Configure logging
logger = logging.getLogger(__name__)

class FirebasePerformanceManager:
    """Manages performance monitoring through Firebase Performance Monitoring."""
    
    # Performance metric types
    METRIC_TYPES = {
        'HTTP_REQUEST': 'http_request',
        'DATABASE_QUERY': 'database_query',
        'EXTERNAL_API': 'external_api',
        'AI_GENERATION': 'ai_generation',
        'FILE_OPERATION': 'file_operation',
        'AUTHENTICATION': 'authentication',
        'CUSTOM_TRACE': 'custom_trace',
        'SYSTEM_RESOURCE': 'system_resource'
    }
    
    # Performance thresholds (in seconds)
    PERFORMANCE_THRESHOLDS = {
        'HTTP_REQUEST': {
            'good': 1.0,
            'acceptable': 3.0,
            'poor': 5.0
        },
        'DATABASE_QUERY': {
            'good': 0.1,
            'acceptable': 0.5,
            'poor': 1.0
        },
        'EXTERNAL_API': {
            'good': 2.0,
            'acceptable': 5.0,
            'poor': 10.0
        },
        'AI_GENERATION': {
            'good': 5.0,
            'acceptable': 15.0,
            'poor': 30.0
        },
        'FILE_OPERATION': {
            'good': 0.5,
            'acceptable': 2.0,
            'poor': 5.0
        }
    }
    
    def __init__(self, app: Optional[Flask] = None,
                 credentials_path: Optional[str] = None,
                 enable_auto_collection: bool = True):
        """Initialize Firebase Performance manager.
        
        Args:
            app: Flask application instance
            credentials_path: Path to Firebase service account credentials
            enable_auto_collection: Enable automatic performance collection
        """
        self.app = app
        self.credentials_path = credentials_path
        self.enable_auto_collection = enable_auto_collection
        self._initialized = False
        
        # Performance tracking
        self._active_traces = {}
        self._performance_stats = {
            'total_traces': 0,
            'traces_by_type': {},
            'average_durations': {},
            'slow_operations': [],
            'system_metrics': {}
        }
        
        # Background monitoring
        self._monitoring_thread = None
        self._shutdown_event = threading.Event()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize Performance Monitoring with Flask app.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        # Initialize Firebase if not already done
        if not self._initialized:
            self._initialize_firebase()
        
        # Register request handlers
        self._register_request_handlers(app)
        
        # Start background monitoring
        if self.enable_auto_collection:
            self._start_background_monitoring()
        
        # Register shutdown handler
        app.teardown_appcontext(self._teardown_handler)
        
        logger.info("Firebase Performance Monitoring initialized with Flask app")
    
    def _initialize_firebase(self) -> bool:
        """Initialize Firebase Admin SDK for Performance Monitoring.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                if self.credentials_path and os.path.exists(self.credentials_path):
                    # Use service account credentials
                    cred = credentials.Certificate(self.credentials_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Use default credentials (for production environment)
                    firebase_admin.initialize_app()
            
            self._initialized = True
            logger.info("Firebase Performance Monitoring initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Performance Monitoring: {str(e)}")
            return False
    
    def _register_request_handlers(self, app: Flask):
        """Register Flask request handlers for automatic performance tracking.
        
        Args:
            app: Flask application instance
        """
        @app.before_request
        def before_request():
            """Start request performance tracking."""
            g.request_start_time = time.time()
            g.request_id = str(uuid.uuid4())
            g.performance_trace = self.start_trace(
                name=f"{request.method} {request.endpoint or 'unknown'}",
                trace_type='HTTP_REQUEST',
                attributes={
                    'method': request.method,
                    'endpoint': request.endpoint or 'unknown',
                    'url': request.url,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'ip_address': request.remote_addr
                }
            )
        
        @app.after_request
        def after_request(response):
            """End request performance tracking."""
            if hasattr(g, 'performance_trace'):
                # Add response attributes
                g.performance_trace.add_attribute('status_code', response.status_code)
                g.performance_trace.add_attribute('response_size', len(response.get_data()))
                
                # Stop the trace
                self.stop_trace(g.performance_trace)
            
            return response
    
    def _start_background_monitoring(self):
        """Start background thread for system monitoring."""
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            self._monitoring_thread = threading.Thread(
                target=self._monitor_system_metrics,
                daemon=True
            )
            self._monitoring_thread.start()
            logger.info("Started background system monitoring thread")
    
    def _monitor_system_metrics(self):
        """Monitor system metrics in background."""
        while not self._shutdown_event.is_set():
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Update performance stats
                self._performance_stats['system_metrics'] = metrics
                
                # Check for performance issues
                self._check_performance_thresholds(metrics)
                
                # Sleep for monitoring interval
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics.
        
        Returns:
            System metrics dictionary
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_sent = network.bytes_sent
                network_recv = network.bytes_recv
            except:
                network_sent = 0
                network_recv = 0
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss
            process_cpu = process.cpu_percent()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'percent': memory_percent,
                    'available_bytes': memory_available,
                    'total_bytes': memory.total
                },
                'disk': {
                    'percent': disk_percent,
                    'free_bytes': disk_free,
                    'total_bytes': disk.total
                },
                'network': {
                    'bytes_sent': network_sent,
                    'bytes_received': network_recv
                },
                'process': {
                    'memory_bytes': process_memory,
                    'cpu_percent': process_cpu
                }
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}
    
    def _check_performance_thresholds(self, metrics: Dict[str, Any]):
        """Check if system metrics exceed performance thresholds.
        
        Args:
            metrics: System metrics dictionary
        """
        try:
            # Check CPU usage
            cpu_percent = metrics.get('cpu', {}).get('percent', 0)
            if cpu_percent > 80:
                self._log_performance_issue(
                    'High CPU usage detected',
                    'SYSTEM_RESOURCE',
                    {'cpu_percent': cpu_percent}
                )
            
            # Check memory usage
            memory_percent = metrics.get('memory', {}).get('percent', 0)
            if memory_percent > 85:
                self._log_performance_issue(
                    'High memory usage detected',
                    'SYSTEM_RESOURCE',
                    {'memory_percent': memory_percent}
                )
            
            # Check disk usage
            disk_percent = metrics.get('disk', {}).get('percent', 0)
            if disk_percent > 90:
                self._log_performance_issue(
                    'High disk usage detected',
                    'SYSTEM_RESOURCE',
                    {'disk_percent': disk_percent}
                )
        except Exception as e:
            logger.error(f"Error checking performance thresholds: {str(e)}")
    
    def _log_performance_issue(self, message: str, issue_type: str, 
                              context: Dict[str, Any]):
        """Log a performance issue.
        
        Args:
            message: Issue message
            issue_type: Type of performance issue
            context: Additional context
        """
        issue = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': issue_type,
            'context': context
        }
        
        self._performance_stats['slow_operations'].append(issue)
        
        # Keep only last 100 issues
        if len(self._performance_stats['slow_operations']) > 100:
            self._performance_stats['slow_operations'] = \
                self._performance_stats['slow_operations'][-100:]
        
        logger.warning(f"Performance issue: {message} - {context}")
    
    def _teardown_handler(self, exception):
        """Handle Flask app teardown."""
        if exception:
            logger.error(f"Request teardown with exception: {str(exception)}")
    
    def start_trace(self, name: str, trace_type: str = 'CUSTOM_TRACE',
                   attributes: Optional[Dict[str, Any]] = None) -> 'PerformanceTrace':
        """Start a performance trace.
        
        Args:
            name: Trace name
            trace_type: Type of trace
            attributes: Initial attributes
            
        Returns:
            PerformanceTrace instance
        """
        trace = PerformanceTrace(
            name=name,
            trace_type=trace_type,
            manager=self,
            attributes=attributes or {}
        )
        
        # Store active trace
        self._active_traces[trace.trace_id] = trace
        
        return trace
    
    def stop_trace(self, trace: 'PerformanceTrace'):
        """Stop a performance trace.
        
        Args:
            trace: PerformanceTrace instance to stop
        """
        if trace.trace_id in self._active_traces:
            trace.stop()
            del self._active_traces[trace.trace_id]
            
            # Update statistics
            self._update_trace_stats(trace)
    
    def _update_trace_stats(self, trace: 'PerformanceTrace'):
        """Update trace statistics.
        
        Args:
            trace: Completed PerformanceTrace instance
        """
        self._performance_stats['total_traces'] += 1
        
        # Update traces by type
        trace_type = trace.trace_type
        self._performance_stats['traces_by_type'][trace_type] = \
            self._performance_stats['traces_by_type'].get(trace_type, 0) + 1
        
        # Update average durations
        duration = trace.duration
        if trace_type not in self._performance_stats['average_durations']:
            self._performance_stats['average_durations'][trace_type] = []
        
        durations = self._performance_stats['average_durations'][trace_type]
        durations.append(duration)
        
        # Keep only last 100 durations for average calculation
        if len(durations) > 100:
            self._performance_stats['average_durations'][trace_type] = durations[-100:]
        
        # Check if operation is slow
        self._check_slow_operation(trace)
    
    def _check_slow_operation(self, trace: 'PerformanceTrace'):
        """Check if a trace represents a slow operation.
        
        Args:
            trace: PerformanceTrace instance to check
        """
        thresholds = self.PERFORMANCE_THRESHOLDS.get(trace.trace_type)
        if not thresholds:
            return
        
        duration = trace.duration
        
        if duration > thresholds['poor']:
            self._log_performance_issue(
                f"Slow {trace.trace_type} operation: {trace.name}",
                trace.trace_type,
                {
                    'duration': duration,
                    'threshold': thresholds['poor'],
                    'attributes': trace.attributes
                }
            )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics.
        
        Returns:
            Performance statistics dictionary
        """
        # Calculate average durations
        avg_durations = {}
        for trace_type, durations in self._performance_stats['average_durations'].items():
            if durations:
                avg_durations[trace_type] = sum(durations) / len(durations)
        
        return {
            'total_traces': self._performance_stats['total_traces'],
            'traces_by_type': dict(self._performance_stats['traces_by_type']),
            'average_durations': avg_durations,
            'active_traces': len(self._active_traces),
            'slow_operations_count': len(self._performance_stats['slow_operations']),
            'recent_slow_operations': self._performance_stats['slow_operations'][-10:],
            'system_metrics': self._performance_stats['system_metrics'],
            'monitoring_thread_alive': self._monitoring_thread.is_alive() if self._monitoring_thread else False
        }
    
    def get_trace_summary(self, trace_type: Optional[str] = None) -> Dict[str, Any]:
        """Get trace summary statistics.
        
        Args:
            trace_type: Filter by trace type (optional)
            
        Returns:
            Trace summary dictionary
        """
        if trace_type:
            durations = self._performance_stats['average_durations'].get(trace_type, [])
            count = self._performance_stats['traces_by_type'].get(trace_type, 0)
        else:
            all_durations = []
            for durations_list in self._performance_stats['average_durations'].values():
                all_durations.extend(durations_list)
            durations = all_durations
            count = self._performance_stats['total_traces']
        
        if not durations:
            return {
                'count': count,
                'average_duration': 0,
                'min_duration': 0,
                'max_duration': 0,
                'p95_duration': 0,
                'p99_duration': 0
            }
        
        durations_sorted = sorted(durations)
        
        return {
            'count': count,
            'average_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'p95_duration': durations_sorted[int(len(durations_sorted) * 0.95)],
            'p99_duration': durations_sorted[int(len(durations_sorted) * 0.99)]
        }
    
    def shutdown(self):
        """Shutdown the performance manager."""
        logger.info("Shutting down Firebase Performance manager")
        
        # Signal shutdown to background thread
        self._shutdown_event.set()
        
        # Wait for background thread to finish
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5.0)
        
        # Stop any active traces
        for trace in list(self._active_traces.values()):
            trace.stop()
        
        self._active_traces.clear()

class PerformanceTrace:
    """Represents a performance trace for monitoring operations."""
    
    def __init__(self, name: str, trace_type: str, manager: FirebasePerformanceManager,
                 attributes: Optional[Dict[str, Any]] = None):
        """Initialize performance trace.
        
        Args:
            name: Trace name
            trace_type: Type of trace
            manager: Performance manager instance
            attributes: Initial attributes
        """
        self.trace_id = str(uuid.uuid4())
        self.name = name
        self.trace_type = trace_type
        self.manager = manager
        self.attributes = attributes or {}
        self.start_time = time.time()
        self.end_time = None
        self.duration = None
        self._stopped = False
    
    def add_attribute(self, key: str, value: Any):
        """Add an attribute to the trace.
        
        Args:
            key: Attribute key
            value: Attribute value
        """
        self.attributes[key] = value
    
    def add_metric(self, metric_name: str, value: Union[int, float]):
        """Add a custom metric to the trace.
        
        Args:
            metric_name: Metric name
            value: Metric value
        """
        if 'metrics' not in self.attributes:
            self.attributes['metrics'] = {}
        
        self.attributes['metrics'][metric_name] = value
    
    def stop(self):
        """Stop the performance trace."""
        if not self._stopped:
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time
            self._stopped = True
            
            # Add duration to attributes
            self.attributes['duration'] = self.duration
            
            logger.debug(f"Trace completed: {self.name} ({self.duration:.3f}s)")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type:
            self.add_attribute('exception_type', exc_type.__name__)
            self.add_attribute('exception_message', str(exc_val))
        
        self.stop()

# Decorator for automatic performance monitoring
def performance_monitor(name: Optional[str] = None, 
                       trace_type: str = 'CUSTOM_TRACE',
                       attributes: Optional[Dict[str, Any]] = None):
    """Decorator to automatically monitor function performance.
    
    Args:
        name: Trace name (defaults to function name)
        trace_type: Type of trace
        attributes: Additional attributes
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            trace_name = name or f"{func.__module__}.{func.__name__}"
            
            # Get performance manager
            manager = get_performance_manager()
            
            # Create trace attributes
            trace_attributes = attributes or {}
            trace_attributes.update({
                'function': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            })
            
            # Start trace
            with manager.start_trace(trace_name, trace_type, trace_attributes) as trace:
                try:
                    result = func(*args, **kwargs)
                    trace.add_attribute('success', True)
                    return result
                except Exception as e:
                    trace.add_attribute('success', False)
                    trace.add_attribute('error', str(e))
                    raise
        
        return wrapper
    return decorator

# Global instance for easy access
performance_manager = None

def get_performance_manager() -> FirebasePerformanceManager:
    """Get the global performance manager instance.
    
    Returns:
        FirebasePerformanceManager instance
    """
    global performance_manager
    
    if performance_manager is None:
        performance_manager = FirebasePerformanceManager()
    
    return performance_manager

def init_performance_monitoring(app: Flask, 
                               credentials_path: Optional[str] = None) -> FirebasePerformanceManager:
    """Initialize Performance Monitoring with Flask app.
    
    Args:
        app: Flask application instance
        credentials_path: Path to Firebase service account credentials
        
    Returns:
        FirebasePerformanceManager instance
    """
    global performance_manager
    
    performance_manager = FirebasePerformanceManager(
        app=app,
        credentials_path=credentials_path
    )
    
    # Store in app context
    app.performance_manager = performance_manager
    
    return performance_manager

