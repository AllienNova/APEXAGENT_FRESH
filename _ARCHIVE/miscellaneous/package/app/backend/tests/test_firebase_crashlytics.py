"""
Test suite for Firebase Crashlytics integration.

This module provides comprehensive tests for the Firebase Crashlytics
functionality in Aideon AI Lite.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import threading
import time
import queue
from datetime import datetime

# Import the modules to test
from ..firebase_crashlytics import FirebaseCrashlyticsManager, crashlytics_monitor, get_crashlytics_manager
from ..api.crashlytics_endpoints import crashlytics_bp

class TestFirebaseCrashlyticsManager(unittest.TestCase):
    """Test cases for FirebaseCrashlyticsManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FirebaseCrashlyticsManager(enable_auto_collection=False)
        self.manager._initialized = True  # Skip Firebase initialization for tests
    
    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin._apps', [])
    def test_initialize_firebase_success(self, mock_init_app):
        """Test successful Firebase initialization."""
        mock_app = Mock()
        mock_init_app.return_value = mock_app
        
        manager = FirebaseCrashlyticsManager()
        self.assertTrue(manager._initialized)
    
    def test_log_error_success(self):
        """Test successful error logging."""
        message = "Test error message"
        severity = "ERROR"
        category = "SYSTEM_ERROR"
        context = {"test": "context"}
        user_id = "test_user"
        
        error_id = self.manager.log_error(
            message=message,
            severity=severity,
            category=category,
            context=context,
            user_id=user_id
        )
        
        self.assertIsInstance(error_id, str)
        self.assertEqual(len(error_id), 36)  # UUID length
        
        # Check error stats
        stats = self.manager.get_error_stats()
        self.assertEqual(stats['total_errors'], 1)
        self.assertEqual(stats['errors_by_severity']['ERROR'], 1)
        self.assertEqual(stats['errors_by_category']['SYSTEM_ERROR'], 1)
    
    def test_log_exception_success(self):
        """Test successful exception logging."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            error_id = self.manager.log_exception(
                exception=e,
                severity="FATAL",
                category="VALIDATION_ERROR",
                context={"test": "context"},
                user_id="test_user"
            )
            
            self.assertIsInstance(error_id, str)
            self.assertEqual(len(error_id), 36)  # UUID length
            
            # Check error stats
            stats = self.manager.get_error_stats()
            self.assertEqual(stats['total_errors'], 1)
            self.assertEqual(stats['errors_by_severity']['FATAL'], 1)
            self.assertEqual(stats['errors_by_category']['VALIDATION_ERROR'], 1)
    
    def test_set_user_identifier(self):
        """Test setting user identifier."""
        user_id = "test_user_123"
        user_email = "test@example.com"
        user_name = "Test User"
        
        # Should not raise any exceptions
        self.manager.set_user_identifier(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name
        )
    
    def test_set_custom_key(self):
        """Test setting custom key."""
        key = "test_key"
        value = "test_value"
        
        # Should not raise any exceptions
        self.manager.set_custom_key(key, value)
    
    def test_log_breadcrumb(self):
        """Test logging breadcrumb."""
        message = "Test breadcrumb"
        category = "test"
        level = "info"
        data = {"test": "data"}
        
        # Should not raise any exceptions
        self.manager.log_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data
        )
    
    def test_error_stats_tracking(self):
        """Test error statistics tracking."""
        # Log multiple errors
        self.manager.log_error("Error 1", severity="ERROR", category="API_ERROR")
        self.manager.log_error("Error 2", severity="WARNING", category="API_ERROR")
        self.manager.log_error("Error 3", severity="FATAL", category="SYSTEM_ERROR")
        
        stats = self.manager.get_error_stats()
        
        self.assertEqual(stats['total_errors'], 3)
        self.assertEqual(stats['errors_by_severity']['ERROR'], 1)
        self.assertEqual(stats['errors_by_severity']['WARNING'], 1)
        self.assertEqual(stats['errors_by_severity']['FATAL'], 1)
        self.assertEqual(stats['errors_by_category']['API_ERROR'], 2)
        self.assertEqual(stats['errors_by_category']['SYSTEM_ERROR'], 1)
        self.assertIsNotNone(stats['last_error_time'])
    
    def test_force_crash(self):
        """Test force crash functionality."""
        with self.assertRaises(Exception) as context:
            self.manager.force_crash("Test crash message")
        
        self.assertIn("Forced crash: Test crash message", str(context.exception))
    
    def test_background_processing_disabled(self):
        """Test behavior when background processing is disabled."""
        manager = FirebaseCrashlyticsManager(enable_auto_collection=False)
        manager._initialized = True
        
        # Log an error
        error_id = manager.log_error("Test error")
        
        # Should process immediately, not queue
        self.assertEqual(manager._error_queue.qsize(), 0)
        self.assertIsInstance(error_id, str)
    
    @patch('threading.Thread')
    def test_background_processing_enabled(self, mock_thread):
        """Test behavior when background processing is enabled."""
        manager = FirebaseCrashlyticsManager(enable_auto_collection=True)
        manager._initialized = True
        
        # Mock thread
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # Start background processing
        manager._start_background_processing()
        
        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
    
    def test_shutdown(self):
        """Test manager shutdown."""
        manager = FirebaseCrashlyticsManager(enable_auto_collection=False)
        manager._initialized = True
        
        # Should not raise any exceptions
        manager.shutdown()
        
        # Check shutdown event is set
        self.assertTrue(manager._shutdown_event.is_set())

class TestCrashlyticsDecorator(unittest.TestCase):
    """Test cases for crashlytics_monitor decorator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FirebaseCrashlyticsManager(enable_auto_collection=False)
        self.manager._initialized = True
        
        # Mock Flask g object
        self.mock_g = Mock()
        self.mock_g.crashlytics_manager = self.manager
    
    @patch('src.firebase_crashlytics.g')
    def test_decorator_success(self, mock_g):
        """Test decorator with successful function execution."""
        mock_g.crashlytics_manager = self.manager
        
        @crashlytics_monitor(severity='ERROR', category='API_ERROR')
        def test_function():
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        
        # No errors should be logged
        stats = self.manager.get_error_stats()
        self.assertEqual(stats['total_errors'], 0)
    
    @patch('src.firebase_crashlytics.g')
    def test_decorator_exception(self, mock_g):
        """Test decorator with function that raises exception."""
        mock_g.crashlytics_manager = self.manager
        
        @crashlytics_monitor(severity='FATAL', category='SYSTEM_ERROR')
        def test_function():
            raise ValueError("Test exception")
        
        with self.assertRaises(ValueError):
            test_function()
        
        # Error should be logged
        stats = self.manager.get_error_stats()
        self.assertEqual(stats['total_errors'], 1)
        self.assertEqual(stats['errors_by_severity']['FATAL'], 1)
        self.assertEqual(stats['errors_by_category']['SYSTEM_ERROR'], 1)

class TestCrashlyticsEndpoints(unittest.TestCase):
    """Test cases for crashlytics API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        from flask import Flask
        
        self.app = Flask(__name__)
        self.app.register_blueprint(crashlytics_bp)
        self.client = self.app.test_client()
        
        # Mock crashlytics manager
        self.mock_manager = Mock()
        
        # Patch the get_crashlytics_manager function
        self.patcher = patch('src.api.crashlytics_endpoints.get_crashlytics_manager')
        self.mock_get_manager = self.patcher.start()
        self.mock_get_manager.return_value = self.mock_manager
        
        # Mock severity levels and categories
        self.mock_manager.SEVERITY_LEVELS = {
            'FATAL': 'fatal',
            'ERROR': 'error',
            'WARNING': 'warning',
            'INFO': 'info',
            'DEBUG': 'debug'
        }
        self.mock_manager.ERROR_CATEGORIES = {
            'API_ERROR': 'api_error',
            'SYSTEM_ERROR': 'system_error',
            'USER_ERROR': 'user_error'
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.patcher.stop()
    
    def test_report_error_success(self):
        """Test successful error reporting via API."""
        self.mock_manager.log_error.return_value = "error_123"
        
        response = self.client.post(
            '/api/v1/crashlytics/report-error',
            json={
                'message': 'Test error message',
                'severity': 'ERROR',
                'category': 'API_ERROR',
                'context': {'test': 'context'},
                'user_id': 'user_123'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['error_id'], 'error_123')
        
        # Verify manager was called correctly
        self.mock_manager.log_error.assert_called_once()
    
    def test_report_error_missing_message(self):
        """Test error reporting with missing message."""
        response = self.client.post(
            '/api/v1/crashlytics/report-error',
            json={'severity': 'ERROR'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'MISSING_MESSAGE')
    
    def test_report_error_invalid_severity(self):
        """Test error reporting with invalid severity."""
        response = self.client.post(
            '/api/v1/crashlytics/report-error',
            json={
                'message': 'Test error',
                'severity': 'INVALID_SEVERITY'
            }
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'INVALID_SEVERITY')
    
    def test_report_exception_success(self):
        """Test successful exception reporting via API."""
        self.mock_manager.log_exception.return_value = "exception_123"
        
        response = self.client.post(
            '/api/v1/crashlytics/report-exception',
            json={
                'exception_type': 'ValueError',
                'exception_message': 'Test exception',
                'stack_trace': ['line 1', 'line 2'],
                'severity': 'FATAL',
                'category': 'SYSTEM_ERROR'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['error_id'], 'exception_123')
    
    def test_set_user_success(self):
        """Test successful user setting via API."""
        response = self.client.post(
            '/api/v1/crashlytics/set-user',
            json={
                'user_id': 'user_123',
                'user_email': 'test@example.com',
                'user_name': 'Test User'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify manager was called correctly
        self.mock_manager.set_user_identifier.assert_called_once_with(
            user_id='user_123',
            user_email='test@example.com',
            user_name='Test User'
        )
    
    def test_set_custom_key_success(self):
        """Test successful custom key setting via API."""
        response = self.client.post(
            '/api/v1/crashlytics/set-custom-key',
            json={
                'key': 'test_key',
                'value': 'test_value'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify manager was called correctly
        self.mock_manager.set_custom_key.assert_called_once_with('test_key', 'test_value')
    
    def test_log_breadcrumb_success(self):
        """Test successful breadcrumb logging via API."""
        response = self.client.post(
            '/api/v1/crashlytics/breadcrumb',
            json={
                'message': 'Test breadcrumb',
                'category': 'test',
                'level': 'info',
                'data': {'test': 'data'}
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify manager was called correctly
        self.mock_manager.log_breadcrumb.assert_called_once()
    
    def test_get_error_stats_success(self):
        """Test successful error stats retrieval via API."""
        mock_stats = {
            'total_errors': 10,
            'errors_by_severity': {'ERROR': 5, 'WARNING': 3, 'FATAL': 2},
            'errors_by_category': {'API_ERROR': 6, 'SYSTEM_ERROR': 4},
            'last_error_time': datetime.now().isoformat(),
            'queue_size': 0,
            'background_thread_alive': True
        }
        self.mock_manager.get_error_stats.return_value = mock_stats
        
        response = self.client.get('/api/v1/crashlytics/stats')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['stats'], mock_stats)
    
    def test_health_check_healthy(self):
        """Test health check with healthy status."""
        mock_stats = {
            'total_errors': 10,
            'background_thread_alive': True,
            'queue_size': 5
        }
        self.mock_manager.get_error_stats.return_value = mock_stats
        
        response = self.client.get('/api/v1/crashlytics/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['health']['status'], 'healthy')
        self.assertEqual(len(data['health']['issues']), 0)
    
    def test_health_check_warning(self):
        """Test health check with warning status."""
        mock_stats = {
            'total_errors': 150,  # High error count
            'background_thread_alive': True,
            'queue_size': 60  # High queue size
        }
        self.mock_manager.get_error_stats.return_value = mock_stats
        
        response = self.client.get('/api/v1/crashlytics/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['health']['status'], 'warning')
        self.assertGreater(len(data['health']['issues']), 0)
    
    def test_health_check_error(self):
        """Test health check with error status."""
        mock_stats = {
            'total_errors': 50,
            'background_thread_alive': False,  # Thread not running
            'queue_size': 10
        }
        self.mock_manager.get_error_stats.return_value = mock_stats
        
        response = self.client.get('/api/v1/crashlytics/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['health']['status'], 'error')
        self.assertIn('Background processing thread not running', data['health']['issues'])
    
    def test_test_crash_endpoint(self):
        """Test crash testing endpoint."""
        self.mock_manager.force_crash.side_effect = Exception("Forced crash")
        
        with self.assertRaises(Exception):
            self.client.post('/api/v1/crashlytics/test-crash')
        
        # Verify force_crash was called
        self.mock_manager.force_crash.assert_called_once()
    
    def test_get_severity_levels(self):
        """Test getting severity levels via API."""
        response = self.client.get('/api/v1/crashlytics/severity-levels')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('severity_levels', data)
        self.assertIn('severity_mapping', data)
    
    def test_get_error_categories(self):
        """Test getting error categories via API."""
        response = self.client.get('/api/v1/crashlytics/error-categories')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('error_categories', data)
        self.assertIn('category_mapping', data)

class TestFlaskIntegration(unittest.TestCase):
    """Test cases for Flask integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        from flask import Flask
        
        self.app = Flask(__name__)
        self.manager = FirebaseCrashlyticsManager(enable_auto_collection=False)
        self.manager._initialized = True
        
        # Initialize with app
        self.manager.init_app(self.app)
        
        self.client = self.app.test_client()
    
    def test_error_handler_registration(self):
        """Test that error handlers are properly registered."""
        # Create a route that raises an exception
        @self.app.route('/test-error')
        def test_error():
            raise ValueError("Test error")
        
        response = self.client.get('/test-error')
        
        # Should return 500 error
        self.assertEqual(response.status_code, 500)
        
        # Error should be logged
        stats = self.manager.get_error_stats()
        self.assertGreater(stats['total_errors'], 0)
    
    def test_404_handler(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent-endpoint')
        
        self.assertEqual(response.status_code, 404)
        
        # Error should be logged
        stats = self.manager.get_error_stats()
        self.assertGreater(stats['total_errors'], 0)

if __name__ == '__main__':
    unittest.main()

