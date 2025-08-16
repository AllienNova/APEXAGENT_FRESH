"""
Firebase Crashlytics integration for Aideon AI Lite.

This module provides comprehensive error reporting and crash analytics
through Firebase Crashlytics, enabling real-time monitoring and debugging.
"""

import os
import sys
import traceback
import logging
import json
import uuid
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from functools import wraps
import firebase_admin
from firebase_admin import credentials, crashlytics
from firebase_admin.exceptions import FirebaseError
from flask import Flask, request, g
import threading
import queue
import time

# Configure logging
logger = logging.getLogger(__name__)

class FirebaseCrashlyticsManager:
    """Manages error reporting and crash analytics through Firebase Crashlytics."""
    
    # Error severity levels
    SEVERITY_LEVELS = {
        'FATAL': 'fatal',
        'ERROR': 'error', 
        'WARNING': 'warning',
        'INFO': 'info',
        'DEBUG': 'debug'
    }
    
    # Error categories for better organization
    ERROR_CATEGORIES = {
        'API_ERROR': 'api_error',
        'DATABASE_ERROR': 'database_error',
        'AUTHENTICATION_ERROR': 'auth_error',
        'VALIDATION_ERROR': 'validation_error',
        'EXTERNAL_SERVICE_ERROR': 'external_service_error',
        'SYSTEM_ERROR': 'system_error',
        'USER_ERROR': 'user_error',
        'PERFORMANCE_ERROR': 'performance_error',
        'SECURITY_ERROR': 'security_error',
        'INTEGRATION_ERROR': 'integration_error'
    }
    
    def __init__(self, app: Optional[Flask] = None, 
                 credentials_path: Optional[str] = None,
                 enable_auto_collection: bool = True):
        """Initialize Firebase Crashlytics manager.
        
        Args:
            app: Flask application instance
            credentials_path: Path to Firebase service account credentials
            enable_auto_collection: Enable automatic crash collection
        """
        self.app = app
        self.credentials_path = credentials_path
        self.enable_auto_collection = enable_auto_collection
        self._initialized = False
        self._error_queue = queue.Queue()
        self._background_thread = None
        self._shutdown_event = threading.Event()
        
        # Error tracking statistics
        self._error_stats = {
            'total_errors': 0,
            'errors_by_severity': {},
            'errors_by_category': {},
            'last_error_time': None
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize Crashlytics with Flask app.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        # Initialize Firebase if not already done
        if not self._initialized:
            self._initialize_firebase()
        
        # Register error handlers
        self._register_error_handlers(app)
        
        # Set up request context processors
        self._setup_request_context(app)
        
        # Start background error processing
        if self.enable_auto_collection:
            self._start_background_processing()
        
        # Register shutdown handler
        app.teardown_appcontext(self._teardown_handler)
        
        logger.info("Firebase Crashlytics initialized with Flask app")
    
    def _initialize_firebase(self) -> bool:
        """Initialize Firebase Admin SDK for Crashlytics.
        
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
            logger.info("Firebase Crashlytics initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Crashlytics: {str(e)}")
            return False
    
    def _register_error_handlers(self, app: Flask):
        """Register Flask error handlers for automatic crash reporting.
        
        Args:
            app: Flask application instance
        """
        @app.errorhandler(Exception)
        def handle_exception(error):
            """Handle all unhandled exceptions."""
            # Log the error to Crashlytics
            self.log_exception(
                error,
                severity='FATAL',
                category='SYSTEM_ERROR',
                context={
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'url': request.url,
                    'user_agent': request.headers.get('User-Agent'),
                    'ip_address': request.remote_addr
                }
            )
            
            # Return appropriate error response
            if hasattr(error, 'code'):
                return {'error': 'Internal server error', 'code': error.code}, error.code
            else:
                return {'error': 'Internal server error'}, 500
        
        @app.errorhandler(404)
        def handle_not_found(error):
            """Handle 404 errors."""
            self.log_error(
                message=f"404 Not Found: {request.url}",
                severity='WARNING',
                category='API_ERROR',
                context={
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'url': request.url
                }
            )
            return {'error': 'Not found'}, 404
        
        @app.errorhandler(500)
        def handle_internal_error(error):
            """Handle 500 errors."""
            self.log_error(
                message=f"Internal Server Error: {str(error)}",
                severity='FATAL',
                category='SYSTEM_ERROR',
                context={
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'url': request.url
                }
            )
            return {'error': 'Internal server error'}, 500
    
    def _setup_request_context(self, app: Flask):
        """Set up request context for error tracking.
        
        Args:
            app: Flask application instance
        """
        @app.before_request
        def before_request():
            """Set up request context for error tracking."""
            g.request_id = str(uuid.uuid4())
            g.request_start_time = time.time()
        
        @app.after_request
        def after_request(response):
            """Log request completion and performance metrics."""
            if hasattr(g, 'request_start_time'):
                request_duration = time.time() - g.request_start_time
                
                # Log slow requests as performance errors
                if request_duration > 5.0:  # 5 seconds threshold
                    self.log_error(
                        message=f"Slow request detected: {request_duration:.2f}s",
                        severity='WARNING',
                        category='PERFORMANCE_ERROR',
                        context={
                            'endpoint': request.endpoint,
                            'method': request.method,
                            'url': request.url,
                            'duration': request_duration,
                            'status_code': response.status_code
                        }
                    )
            
            return response
    
    def _start_background_processing(self):
        """Start background thread for processing errors."""
        if self._background_thread is None or not self._background_thread.is_alive():
            self._background_thread = threading.Thread(
                target=self._process_error_queue,
                daemon=True
            )
            self._background_thread.start()
            logger.info("Started background error processing thread")
    
    def _process_error_queue(self):
        """Process errors from the queue in background."""
        while not self._shutdown_event.is_set():
            try:
                # Get error from queue with timeout
                error_data = self._error_queue.get(timeout=1.0)
                
                # Send error to Firebase Crashlytics
                self._send_to_crashlytics(error_data)
                
                # Mark task as done
                self._error_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing error queue: {str(e)}")
    
    def _send_to_crashlytics(self, error_data: Dict[str, Any]):
        """Send error data to Firebase Crashlytics.
        
        Args:
            error_data: Error data dictionary
        """
        try:
            # This is a placeholder for actual Crashlytics SDK integration
            # In production, you would use the Firebase Crashlytics SDK
            # to send crash reports and custom errors
            
            # For now, we'll log the error data
            logger.info(f"Sending error to Crashlytics: {json.dumps(error_data, indent=2)}")
            
            # Update error statistics
            self._update_error_stats(error_data)
            
        except Exception as e:
            logger.error(f"Failed to send error to Crashlytics: {str(e)}")
    
    def _update_error_stats(self, error_data: Dict[str, Any]):
        """Update error tracking statistics.
        
        Args:
            error_data: Error data dictionary
        """
        self._error_stats['total_errors'] += 1
        self._error_stats['last_error_time'] = datetime.now().isoformat()
        
        # Update severity statistics
        severity = error_data.get('severity', 'ERROR')
        self._error_stats['errors_by_severity'][severity] = \
            self._error_stats['errors_by_severity'].get(severity, 0) + 1
        
        # Update category statistics
        category = error_data.get('category', 'SYSTEM_ERROR')
        self._error_stats['errors_by_category'][category] = \
            self._error_stats['errors_by_category'].get(category, 0) + 1
    
    def _teardown_handler(self, exception):
        """Handle Flask app teardown."""
        if exception:
            self.log_exception(
                exception,
                severity='ERROR',
                category='SYSTEM_ERROR',
                context={'teardown': True}
            )
    
    def log_exception(self, exception: Exception, 
                     severity: str = 'ERROR',
                     category: str = 'SYSTEM_ERROR',
                     context: Optional[Dict[str, Any]] = None,
                     user_id: Optional[str] = None) -> str:
        """Log an exception to Crashlytics.
        
        Args:
            exception: Exception to log
            severity: Error severity level
            category: Error category
            context: Additional context information
            user_id: User ID associated with the error
            
        Returns:
            Error ID for tracking
        """
        error_id = str(uuid.uuid4())
        
        # Extract exception information
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback is None:
            exc_traceback = exception.__traceback__
        
        # Create error data
        error_data = {
            'error_id': error_id,
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'category': category,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exception(type(exception), exception, exc_traceback),
            'context': context or {},
            'user_id': user_id,
            'request_id': getattr(g, 'request_id', None) if 'g' in globals() else None
        }
        
        # Add to error queue for background processing
        if self.enable_auto_collection:
            try:
                self._error_queue.put_nowait(error_data)
            except queue.Full:
                logger.warning("Error queue is full, dropping error")
        else:
            # Send immediately if auto collection is disabled
            self._send_to_crashlytics(error_data)
        
        logger.error(f"Exception logged to Crashlytics: {error_id}")
        return error_id
    
    def log_error(self, message: str,
                  severity: str = 'ERROR',
                  category: str = 'SYSTEM_ERROR',
                  context: Optional[Dict[str, Any]] = None,
                  user_id: Optional[str] = None) -> str:
        """Log a custom error message to Crashlytics.
        
        Args:
            message: Error message
            severity: Error severity level
            category: Error category
            context: Additional context information
            user_id: User ID associated with the error
            
        Returns:
            Error ID for tracking
        """
        error_id = str(uuid.uuid4())
        
        # Create error data
        error_data = {
            'error_id': error_id,
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'category': category,
            'message': message,
            'context': context or {},
            'user_id': user_id,
            'request_id': getattr(g, 'request_id', None) if 'g' in globals() else None
        }
        
        # Add to error queue for background processing
        if self.enable_auto_collection:
            try:
                self._error_queue.put_nowait(error_data)
            except queue.Full:
                logger.warning("Error queue is full, dropping error")
        else:
            # Send immediately if auto collection is disabled
            self._send_to_crashlytics(error_data)
        
        logger.error(f"Error logged to Crashlytics: {error_id}")
        return error_id
    
    def set_user_identifier(self, user_id: str, user_email: Optional[str] = None,
                           user_name: Optional[str] = None):
        """Set user identifier for crash reports.
        
        Args:
            user_id: Unique user identifier
            user_email: User email address
            user_name: User display name
        """
        try:
            # This would integrate with Firebase Crashlytics SDK
            # to set user identifier for crash reports
            logger.info(f"Set user identifier: {user_id}")
            
            # Store in Flask g object for request context
            if 'g' in globals():
                g.crashlytics_user_id = user_id
                g.crashlytics_user_email = user_email
                g.crashlytics_user_name = user_name
                
        except Exception as e:
            logger.error(f"Failed to set user identifier: {str(e)}")
    
    def set_custom_key(self, key: str, value: Any):
        """Set a custom key-value pair for crash reports.
        
        Args:
            key: Custom key name
            value: Custom value
        """
        try:
            # This would integrate with Firebase Crashlytics SDK
            # to set custom keys for crash reports
            logger.info(f"Set custom key: {key} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to set custom key: {str(e)}")
    
    def log_breadcrumb(self, message: str, category: str = 'general',
                      level: str = 'info', data: Optional[Dict[str, Any]] = None):
        """Log a breadcrumb for debugging context.
        
        Args:
            message: Breadcrumb message
            category: Breadcrumb category
            level: Log level
            data: Additional data
        """
        try:
            breadcrumb_data = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'category': category,
                'level': level,
                'data': data or {}
            }
            
            # This would integrate with Firebase Crashlytics SDK
            # to add breadcrumbs for crash reports
            logger.debug(f"Breadcrumb: {json.dumps(breadcrumb_data)}")
            
        except Exception as e:
            logger.error(f"Failed to log breadcrumb: {str(e)}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error tracking statistics.
        
        Returns:
            Error statistics dictionary
        """
        return {
            'total_errors': self._error_stats['total_errors'],
            'errors_by_severity': dict(self._error_stats['errors_by_severity']),
            'errors_by_category': dict(self._error_stats['errors_by_category']),
            'last_error_time': self._error_stats['last_error_time'],
            'queue_size': self._error_queue.qsize() if self.enable_auto_collection else 0,
            'background_thread_alive': self._background_thread.is_alive() if self._background_thread else False
        }
    
    def force_crash(self, message: str = "Test crash"):
        """Force a crash for testing purposes.
        
        Args:
            message: Crash message
        """
        logger.warning(f"Forcing crash for testing: {message}")
        raise Exception(f"Forced crash: {message}")
    
    def shutdown(self):
        """Shutdown the Crashlytics manager."""
        logger.info("Shutting down Firebase Crashlytics manager")
        
        # Signal shutdown to background thread
        self._shutdown_event.set()
        
        # Wait for error queue to be processed
        if self.enable_auto_collection:
            try:
                self._error_queue.join()
            except:
                pass
        
        # Wait for background thread to finish
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join(timeout=5.0)

# Decorator for automatic error logging
def crashlytics_monitor(severity: str = 'ERROR', 
                       category: str = 'SYSTEM_ERROR'):
    """Decorator to automatically monitor functions for errors.
    
    Args:
        severity: Error severity level
        category: Error category
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get crashlytics manager from Flask app
                if hasattr(g, 'crashlytics_manager'):
                    g.crashlytics_manager.log_exception(
                        e,
                        severity=severity,
                        category=category,
                        context={
                            'function': func.__name__,
                            'module': func.__module__,
                            'args': str(args)[:500],  # Limit size
                            'kwargs': str(kwargs)[:500]  # Limit size
                        }
                    )
                raise
        return wrapper
    return decorator

# Global instance for easy access
crashlytics_manager = None

def get_crashlytics_manager() -> FirebaseCrashlyticsManager:
    """Get the global crashlytics manager instance.
    
    Returns:
        FirebaseCrashlyticsManager instance
    """
    global crashlytics_manager
    
    if crashlytics_manager is None:
        crashlytics_manager = FirebaseCrashlyticsManager()
    
    return crashlytics_manager

def init_crashlytics(app: Flask, credentials_path: Optional[str] = None) -> FirebaseCrashlyticsManager:
    """Initialize Crashlytics with Flask app.
    
    Args:
        app: Flask application instance
        credentials_path: Path to Firebase service account credentials
        
    Returns:
        FirebaseCrashlyticsManager instance
    """
    global crashlytics_manager
    
    crashlytics_manager = FirebaseCrashlyticsManager(
        app=app,
        credentials_path=credentials_path
    )
    
    # Store in app context
    app.crashlytics_manager = crashlytics_manager
    
    return crashlytics_manager

