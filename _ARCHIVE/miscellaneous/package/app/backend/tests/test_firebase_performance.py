"""
Test suite for Firebase Performance Monitoring integration.

This module provides comprehensive tests for the Firebase Performance
Monitoring functionality in Aideon AI Lite.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import threading
import time
from datetime import datetime

# Import the modules to test
from ..firebase_performance import FirebasePerformanceManager, PerformanceTrace, performance_monitor, get_performance_manager
from ..api.performance_endpoints import performance_bp

class TestFirebasePerformanceManager(unittest.TestCase):
    """Test cases for FirebasePerformanceManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FirebasePerformanceManager(enable_auto_collection=False)
        self.manager._initialized = True  # Skip Firebase initialization for tests
    
    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin._apps', [])
    def test_initialize_firebase_success(self, mock_init_app):
        """Test successful Firebase initialization."""
        mock_app = Mock()
        mock_init_app.return_value = mock_app
        
        manager = FirebasePerformanceManager()
        self.assertTrue(manager._initialized)
    
    def test_start_trace_success(self):
        """Test successful trace creation."""
        name = "test_trace"
        trace_type = "CUSTOM_TRACE"
        attributes = {"test": "attribute"}
        
        trace = self.manager.start_trace(
            name=name,
            trace_type=trace_type,
            attributes=attributes
        )
        
        self.assertIsInstance(trace, PerformanceTrace)
        self.assertEqual(trace.name, name)
        self.assertEqual(trace.trace_type, trace_type)
        self.assertEqual(trace.attributes["test"], "attribute")
        self.assertIn(trace.trace_id, self.manager._active_traces)
    
    def test_stop_trace_success(self):
        """Test successful trace stopping."""
        trace = self.manager.start_trace("test_trace", "CUSTOM_TRACE")
        trace_id = trace.trace_id
        
        # Wait a bit to ensure duration > 0
        time.sleep(0.01)
        
        self.manager.stop_trace(trace)
        
        self.assertTrue(trace._stopped)
        self.assertIsNotNone(trace.duration)
        self.assertGreater(trace.duration, 0)
        self.assertNotIn(trace_id, self.manager._active_traces)
        
        # Check statistics update
        stats = self.manager.get_performance_stats()
        self.assertEqual(stats['total_traces'], 1)
        self.assertEqual(stats['traces_by_type']['CUSTOM_TRACE'], 1)
    
    def test_performance_stats_tracking(self):
        """Test performance statistics tracking."""
        # Create and stop multiple traces
        trace1 = self.manager.start_trace("trace1", "HTTP_REQUEST")
        time.sleep(0.01)
        self.manager.stop_trace(trace1)
        
        trace2 = self.manager.start_trace("trace2", "DATABASE_QUERY")
        time.sleep(0.01)
        self.manager.stop_trace(trace2)
        
        trace3 = self.manager.start_trace("trace3", "HTTP_REQUEST")
        time.sleep(0.01)
        self.manager.stop_trace(trace3)
        
        stats = self.manager.get_performance_stats()
        
        self.assertEqual(stats['total_traces'], 3)
        self.assertEqual(stats['traces_by_type']['HTTP_REQUEST'], 2)
        self.assertEqual(stats['traces_by_type']['DATABASE_QUERY'], 1)
        self.assertIn('HTTP_REQUEST', stats['average_durations'])
        self.assertIn('DATABASE_QUERY', stats['average_durations'])
    
    def test_trace_summary(self):
        """Test trace summary statistics."""
        # Create traces with known durations
        trace1 = self.manager.start_trace("trace1", "HTTP_REQUEST")
        time.sleep(0.01)
        self.manager.stop_trace(trace1)
        
        trace2 = self.manager.start_trace("trace2", "HTTP_REQUEST")
        time.sleep(0.02)
        self.manager.stop_trace(trace2)
        
        # Get summary for HTTP_REQUEST
        summary = self.manager.get_trace_summary("HTTP_REQUEST")
        
        self.assertEqual(summary['count'], 2)
        self.assertGreater(summary['average_duration'], 0)
        self.assertGreater(summary['max_duration'], summary['min_duration'])
        self.assertGreaterEqual(summary['p95_duration'], summary['average_duration'])
        self.assertGreaterEqual(summary['p99_duration'], summary['p95_duration'])
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.Process')
    def test_collect_system_metrics(self, mock_process, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection."""
        # Mock system metrics
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, available=1000000, total=2000000)
        mock_disk.return_value = Mock(percent=70.0, free=500000, total=1000000)
        mock_process.return_value = Mock(
            memory_info=Mock(return_value=Mock(rss=100000)),
            cpu_percent=Mock(return_value=25.0)
        )
        
        metrics = self.manager._collect_system_metrics()
        
        self.assertEqual(metrics['cpu']['percent'], 50.0)
        self.assertEqual(metrics['memory']['percent'], 60.0)
        self.assertEqual(metrics['disk']['percent'], 70.0)
        self.assertEqual(metrics['process']['memory_bytes'], 100000)
        self.assertEqual(metrics['process']['cpu_percent'], 25.0)
    
    def test_slow_operation_detection(self):
        """Test slow operation detection."""
        # Create a trace that should be flagged as slow
        trace = PerformanceTrace(
            name="slow_operation",
            trace_type="HTTP_REQUEST",
            manager=self.manager
        )
        trace.duration = 10.0  # 10 seconds - should be flagged as slow
        
        self.manager._check_slow_operation(trace)
        
        stats = self.manager.get_performance_stats()
        self.assertGreater(len(stats['recent_slow_operations']), 0)
        
        slow_op = stats['recent_slow_operations'][-1]
        self.assertIn("slow_operation", slow_op['message'])
        self.assertEqual(slow_op['type'], 'HTTP_REQUEST')
    
    def test_shutdown(self):
        """Test manager shutdown."""
        manager = FirebasePerformanceManager(enable_auto_collection=False)
        manager._initialized = True
        
        # Create some active traces
        trace1 = manager.start_trace("trace1", "CUSTOM_TRACE")
        trace2 = manager.start_trace("trace2", "CUSTOM_TRACE")
        
        # Should not raise any exceptions
        manager.shutdown()
        
        # Check that traces are stopped
        self.assertTrue(trace1._stopped)
        self.assertTrue(trace2._stopped)
        self.assertEqual(len(manager._active_traces), 0)
        self.assertTrue(manager._shutdown_event.is_set())

class TestPerformanceTrace(unittest.TestCase):
    """Test cases for PerformanceTrace."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = Mock()
        self.trace = PerformanceTrace(
            name="test_trace",
            trace_type="CUSTOM_TRACE",
            manager=self.manager,
            attributes={"initial": "attribute"}
        )
    
    def test_trace_initialization(self):
        """Test trace initialization."""
        self.assertEqual(self.trace.name, "test_trace")
        self.assertEqual(self.trace.trace_type, "CUSTOM_TRACE")
        self.assertEqual(self.trace.attributes["initial"], "attribute")
        self.assertIsNotNone(self.trace.trace_id)
        self.assertIsNotNone(self.trace.start_time)
        self.assertIsNone(self.trace.end_time)
        self.assertFalse(self.trace._stopped)
    
    def test_add_attribute(self):
        """Test adding attributes to trace."""
        self.trace.add_attribute("new_key", "new_value")
        self.assertEqual(self.trace.attributes["new_key"], "new_value")
    
    def test_add_metric(self):
        """Test adding metrics to trace."""
        self.trace.add_metric("response_time", 1.5)
        self.trace.add_metric("request_count", 10)
        
        self.assertIn("metrics", self.trace.attributes)
        self.assertEqual(self.trace.attributes["metrics"]["response_time"], 1.5)
        self.assertEqual(self.trace.attributes["metrics"]["request_count"], 10)
    
    def test_stop_trace(self):
        """Test stopping a trace."""
        start_time = self.trace.start_time
        time.sleep(0.01)
        
        self.trace.stop()
        
        self.assertTrue(self.trace._stopped)
        self.assertIsNotNone(self.trace.end_time)
        self.assertIsNotNone(self.trace.duration)
        self.assertGreater(self.trace.end_time, start_time)
        self.assertGreater(self.trace.duration, 0)
        self.assertEqual(self.trace.attributes["duration"], self.trace.duration)
    
    def test_context_manager_success(self):
        """Test trace as context manager with success."""
        with self.trace as trace:
            self.assertIs(trace, self.trace)
            time.sleep(0.01)
        
        self.assertTrue(self.trace._stopped)
        self.assertGreater(self.trace.duration, 0)
    
    def test_context_manager_exception(self):
        """Test trace as context manager with exception."""
        try:
            with self.trace as trace:
                time.sleep(0.01)
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        self.assertTrue(self.trace._stopped)
        self.assertEqual(self.trace.attributes["exception_type"], "ValueError")
        self.assertEqual(self.trace.attributes["exception_message"], "Test exception")

class TestPerformanceDecorator(unittest.TestCase):
    """Test cases for performance_monitor decorator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FirebasePerformanceManager(enable_auto_collection=False)
        self.manager._initialized = True
        
        # Patch the get_performance_manager function
        self.patcher = patch('src.firebase_performance.get_performance_manager')
        self.mock_get_manager = self.patcher.start()
        self.mock_get_manager.return_value = self.manager
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.patcher.stop()
    
    def test_decorator_success(self):
        """Test decorator with successful function execution."""
        @performance_monitor(name="test_function", trace_type="CUSTOM_TRACE")
        def test_function():
            time.sleep(0.01)
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        
        # Check that trace was created and completed
        stats = self.manager.get_performance_stats()
        self.assertEqual(stats['total_traces'], 1)
        self.assertEqual(stats['traces_by_type']['CUSTOM_TRACE'], 1)
    
    def test_decorator_exception(self):
        """Test decorator with function that raises exception."""
        @performance_monitor(name="failing_function", trace_type="CUSTOM_TRACE")
        def failing_function():
            time.sleep(0.01)
            raise ValueError("Test exception")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        # Check that trace was created and completed with error info
        stats = self.manager.get_performance_stats()
        self.assertEqual(stats['total_traces'], 1)

class TestPerformanceEndpoints(unittest.TestCase):
    """Test cases for performance API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        from flask import Flask
        
        self.app = Flask(__name__)
        self.app.register_blueprint(performance_bp)
        self.client = self.app.test_client()
        
        # Mock performance manager
        self.mock_manager = Mock()
        
        # Patch the get_performance_manager function
        self.patcher = patch('src.api.performance_endpoints.get_performance_manager')
        self.mock_get_manager = self.patcher.start()
        self.mock_get_manager.return_value = self.mock_manager
        
        # Mock metric types and thresholds
        self.mock_manager.METRIC_TYPES = {
            'HTTP_REQUEST': 'http_request',
            'DATABASE_QUERY': 'database_query',
            'CUSTOM_TRACE': 'custom_trace'
        }
        self.mock_manager.PERFORMANCE_THRESHOLDS = {
            'HTTP_REQUEST': {'good': 1.0, 'acceptable': 3.0, 'poor': 5.0}
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.patcher.stop()
    
    def test_start_trace_success(self):
        """Test successful trace start via API."""
        mock_trace = Mock()
        mock_trace.trace_id = "trace_123"
        self.mock_manager.start_trace.return_value = mock_trace
        
        response = self.client.post(
            '/api/v1/performance/start-trace',
            json={
                'name': 'test_trace',
                'trace_type': 'HTTP_REQUEST',
                'attributes': {'test': 'attribute'}
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['trace_id'], 'trace_123')
        
        # Verify manager was called correctly
        self.mock_manager.start_trace.assert_called_once()
    
    def test_start_trace_missing_name(self):
        """Test trace start with missing name."""
        response = self.client.post(
            '/api/v1/performance/start-trace',
            json={'trace_type': 'HTTP_REQUEST'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'MISSING_NAME')
    
    def test_start_trace_invalid_type(self):
        """Test trace start with invalid trace type."""
        response = self.client.post(
            '/api/v1/performance/start-trace',
            json={
                'name': 'test_trace',
                'trace_type': 'INVALID_TYPE'
            }
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'INVALID_TRACE_TYPE')
    
    def test_get_performance_stats_success(self):
        """Test successful performance stats retrieval via API."""
        mock_stats = {
            'total_traces': 100,
            'traces_by_type': {'HTTP_REQUEST': 60, 'DATABASE_QUERY': 40},
            'average_durations': {'HTTP_REQUEST': 1.5, 'DATABASE_QUERY': 0.3},
            'active_traces': 5,
            'slow_operations_count': 3,
            'system_metrics': {'cpu': {'percent': 45.0}}
        }
        self.mock_manager.get_performance_stats.return_value = mock_stats
        
        response = self.client.get('/api/v1/performance/stats')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['stats'], mock_stats)
    
    def test_get_trace_summary_success(self):
        """Test successful trace summary retrieval via API."""
        mock_summary = {
            'count': 50,
            'average_duration': 1.2,
            'min_duration': 0.1,
            'max_duration': 5.0,
            'p95_duration': 3.0,
            'p99_duration': 4.5
        }
        self.mock_manager.get_trace_summary.return_value = mock_summary
        
        response = self.client.get('/api/v1/performance/trace-summary?trace_type=HTTP_REQUEST')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['summary'], mock_summary)
        self.assertEqual(data['trace_type'], 'HTTP_REQUEST')
    
    def test_health_check_healthy(self):
        """Test health check with healthy status."""
        mock_stats = {
            'monitoring_thread_alive': True,
            'system_metrics': {
                'cpu': {'percent': 50.0},
                'memory': {'percent': 60.0},
                'disk': {'percent': 70.0}
            },
            'slow_operations_count': 2
        }
        self.mock_manager.get_performance_stats.return_value = mock_stats
        
        response = self.client.get('/api/v1/performance/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['health']['status'], 'healthy')
        self.assertEqual(len(data['health']['issues']), 0)
    
    def test_health_check_warning(self):
        """Test health check with warning status."""
        mock_stats = {
            'monitoring_thread_alive': True,
            'system_metrics': {
                'cpu': {'percent': 85.0},  # High CPU
                'memory': {'percent': 90.0},  # High memory
                'disk': {'percent': 70.0}
            },
            'slow_operations_count': 15  # High slow operations
        }
        self.mock_manager.get_performance_stats.return_value = mock_stats
        
        response = self.client.get('/api/v1/performance/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['health']['status'], 'warning')
        self.assertGreater(len(data['health']['issues']), 0)
    
    def test_health_check_error(self):
        """Test health check with error status."""
        mock_stats = {
            'monitoring_thread_alive': False,  # Thread not running
            'system_metrics': {},
            'slow_operations_count': 5
        }
        self.mock_manager.get_performance_stats.return_value = mock_stats
        
        response = self.client.get('/api/v1/performance/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['health']['status'], 'error')
        self.assertIn('Background monitoring thread not running', data['health']['issues'])
    
    def test_get_metric_types(self):
        """Test getting metric types via API."""
        response = self.client.get('/api/v1/performance/metric-types')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('metric_types', data)
        self.assertIn('type_mapping', data)
    
    def test_get_thresholds(self):
        """Test getting performance thresholds via API."""
        response = self.client.get('/api/v1/performance/thresholds')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('thresholds', data)
    
    def test_benchmark_cpu(self):
        """Test CPU benchmark via API."""
        response = self.client.post(
            '/api/v1/performance/benchmark',
            json={
                'test_type': 'cpu',
                'duration': 0.1
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['benchmark']['test_type'], 'cpu')
        self.assertGreater(data['benchmark']['result'], 0)
    
    def test_benchmark_memory(self):
        """Test memory benchmark via API."""
        response = self.client.post(
            '/api/v1/performance/benchmark',
            json={
                'test_type': 'memory',
                'duration': 0.1
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['benchmark']['test_type'], 'memory')
        self.assertGreater(data['benchmark']['result'], 0)
    
    def test_benchmark_invalid_duration(self):
        """Test benchmark with invalid duration."""
        response = self.client.post(
            '/api/v1/performance/benchmark',
            json={
                'test_type': 'cpu',
                'duration': 15.0  # Too long
            }
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'DURATION_TOO_LONG')

if __name__ == '__main__':
    unittest.main()

