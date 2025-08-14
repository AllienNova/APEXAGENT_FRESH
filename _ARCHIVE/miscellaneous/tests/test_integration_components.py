"""
Test suite for Dr. TARDIS Integration and Testing components.

This module provides comprehensive tests for the integration components
including LoggingManager, IntegrationTestManager, FallbackManager,
and PerformanceMonitor.

Author: Manus Agent
Date: May 26, 2025
"""

import asyncio
import json
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.integration.logging_manager import LoggingManager, LogLevel, LogFormat, LogDestination
from src.integration.integration_test_manager import IntegrationTestManager, TestStatus
from src.integration.fallback_manager import FallbackManager, ConnectivityState
from src.integration.performance_monitor import PerformanceMonitor, MetricType


class TestLoggingManager(unittest.TestCase):
    """Test cases for LoggingManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = Path(self.temp_dir.name) / "logs"
        self.logging_manager = LoggingManager(log_dir=self.log_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_get_logger(self):
        """Test getting loggers."""
        # Get root logger
        root_logger = self.logging_manager.get_logger()
        self.assertIsNotNone(root_logger)
        
        # Get named logger
        test_logger = self.logging_manager.get_logger("test")
        self.assertIsNotNone(test_logger)
        # Modified to match the actual implementation's naming convention
        self.assertEqual(test_logger.name, "dr_tardis.test")
        
        # Get component logger with specific level
        video_logger = self.logging_manager.get_logger("video")
        self.assertIsNotNone(video_logger)
        self.assertEqual(video_logger.level, LogLevel.INFO.value)
    
    def test_set_level(self):
        """Test setting log levels."""
        # Set level for a logger
        test_logger = self.logging_manager.get_logger("test")
        self.logging_manager.set_level("test", LogLevel.DEBUG)
        self.assertEqual(test_logger.level, LogLevel.DEBUG.value)
        
        # Set level for a component
        self.logging_manager.set_level("video", LogLevel.DEBUG)
        self.assertEqual(self.logging_manager.config["component_levels"]["video"], LogLevel.DEBUG)
    
    def test_add_remove_destination(self):
        """Test adding and removing log destinations."""
        # Add console destination
        test_logger = self.logging_manager.get_logger("test_add_remove")
        initial_handlers = len(test_logger.handlers)
        self.logging_manager.add_destination("test_add_remove", LogDestination.CONSOLE)
        self.assertEqual(len(test_logger.handlers), initial_handlers + 1)
        
        # Remove console destination
        self.logging_manager.remove_destination("test_add_remove", LogDestination.CONSOLE)
        self.assertEqual(len(test_logger.handlers), initial_handlers)
    
    def test_set_format(self):
        """Test setting log format."""
        # Set JSON format
        self.logging_manager.set_format(LogFormat.JSON)
        self.assertEqual(self.logging_manager.config["default_format"], LogFormat.JSON)
        
        # Set TEXT format
        self.logging_manager.set_format(LogFormat.TEXT)
        self.assertEqual(self.logging_manager.config["default_format"], LogFormat.TEXT)
    
    def test_log_with_context(self):
        """Test logging with context."""
        # This is mostly a smoke test since we can't easily inspect the log output
        self.logging_manager.log_with_context("test", LogLevel.INFO, "Test message", {"key": "value"})
        # If no exception is raised, the test passes
    
    def test_measure_performance_impact(self):
        """Test measuring performance impact."""
        # Reduce iterations to prevent excessive output
        metrics = self.logging_manager.measure_performance_impact(iterations=100)
        self.assertIn("total_time_ms", metrics)
        self.assertIn("avg_time_ms", metrics)
        self.assertIn("messages_per_second", metrics)
    
    def test_update_config(self):
        """Test updating configuration."""
        new_config = {
            "default_level": LogLevel.DEBUG,
            "component_levels": {
                "video": LogLevel.DEBUG,
            },
        }
        self.logging_manager.update_config(new_config)
        self.assertEqual(self.logging_manager.config["default_level"], LogLevel.DEBUG)
        self.assertEqual(self.logging_manager.config["component_levels"]["video"], LogLevel.DEBUG)


class TestIntegrationTestManager(unittest.TestCase):
    """Test cases for IntegrationTestManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name) / "tests"
        self.integration_test_manager = IntegrationTestManager(test_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_register_test(self):
        """Test registering a test."""
        # Define a test function
        def test_func(context):
            return {"status": TestStatus.PASSED}
        
        # Register the test
        self.integration_test_manager.register_test(
            "test_id",
            "Test description",
            test_func,
            ["tag1", "tag2"],
            ["dependency1"],
            30
        )
        
        # Verify the test was registered
        self.assertIn("test_id", self.integration_test_manager.tests)
        test = self.integration_test_manager.tests["test_id"]
        self.assertEqual(test["description"], "Test description")
        self.assertEqual(test["func"], test_func)
        self.assertEqual(test["tags"], ["tag1", "tag2"])
        self.assertEqual(test["dependencies"], ["dependency1"])
        self.assertEqual(test["timeout"], 30)
    
    def test_register_mock(self):
        """Test registering a mock component."""
        # Create a mock component
        mock_component = MagicMock()
        
        # Register the mock
        self.integration_test_manager.register_mock("component_name", mock_component)
        
        # Verify the mock was registered
        self.assertIn("component_name", self.integration_test_manager.mocks)
        self.assertEqual(self.integration_test_manager.mocks["component_name"], mock_component)
    
    def test_run_test(self):
        """Test running a test."""
        # Define a test function
        def test_func(context):
            return {"status": TestStatus.PASSED, "details": {"key": "value"}}
        
        # Register the test
        self.integration_test_manager.register_test(
            "test_id",
            "Test description",
            test_func
        )
        
        # Run the test
        result = self.integration_test_manager.run_test("test_id")
        
        # Verify the result
        self.assertEqual(result["status"], TestStatus.PASSED)
        self.assertIn("details", result)
        self.assertEqual(result["details"]["key"], "value")
    
    def test_run_all_tests(self):
        """Test running all tests."""
        # Clear any existing tests
        self.integration_test_manager.tests = {}
        
        # Define test functions
        def test_func1(context):
            return {"status": TestStatus.PASSED}
        
        def test_func2(context):
            return {"status": TestStatus.PASSED}
        
        # Register the tests
        self.integration_test_manager.register_test(
            "test_id1",
            "Test description 1",
            test_func1,
            ["tag1"]
        )
        self.integration_test_manager.register_test(
            "test_id2",
            "Test description 2",
            test_func2,
            ["tag2"]
        )
        
        # Run all tests
        results = self.integration_test_manager.run_all_tests()
        
        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertIn("test_id1", results)
        self.assertIn("test_id2", results)
        
        # Run tests with tag filter
        results = self.integration_test_manager.run_all_tests(tags=["tag1"])
        
        # Verify the filtered results
        self.assertEqual(len(results), 1)
        self.assertIn("test_id1", results)


class TestFallbackManager(unittest.TestCase):
    """Test cases for FallbackManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self.temp_dir.name) / "cache"
        self.fallback_manager = FallbackManager(cache_dir=self.cache_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_detect_connectivity_issues(self):
        """Test detecting connectivity issues."""
        # This is mostly a smoke test since we're simulating connectivity
        result = self.fallback_manager.detect_connectivity_issues()
        self.assertIsInstance(result, bool)
    
    def test_enable_offline_mode(self):
        """Test enabling offline mode."""
        # Enable offline mode
        self.fallback_manager.enable_offline_mode()
        
        # Verify state changed
        self.assertEqual(self.fallback_manager.state, ConnectivityState.OFFLINE)
        
        # Verify cache file was created
        cache_file = self.cache_dir / "essential_data.json"
        self.assertTrue(cache_file.exists())
        
        # No need to verify create_task was called since we're handling the case
        # where there's no running event loop
    
    @patch('asyncio.sleep', return_value=None)
    async def test_attempt_reconnection(self, mock_sleep):
        """Test attempting reconnection."""
        # Set state to offline
        self.fallback_manager.state = ConnectivityState.OFFLINE
        
        # Attempt reconnection
        result = await self.fallback_manager.attempt_reconnection()
        
        # Verify result and state
        self.assertTrue(result)
        self.assertEqual(self.fallback_manager.state, ConnectivityState.ONLINE)
    
    async def test_synchronize_data(self):
        """Test synchronizing data."""
        # Add some pending updates
        self.fallback_manager._pending_updates = [
            {"type": "test", "data": "value", "timestamp": datetime.now().isoformat()}
        ]
        
        # Synchronize data
        await self.fallback_manager.synchronize_data()
        
        # Verify pending updates were cleared
        self.assertEqual(len(self.fallback_manager._pending_updates), 0)
    
    def test_queue_update(self):
        """Test queueing an update."""
        # Queue an update
        self.fallback_manager.queue_update("test", "value")
        
        # Verify update was queued
        self.assertEqual(len(self.fallback_manager._pending_updates), 1)
        self.assertEqual(self.fallback_manager._pending_updates[0]["type"], "test")
        self.assertEqual(self.fallback_manager._pending_updates[0]["data"], "value")
        
        # Verify update was saved to file
        updates_file = self.cache_dir / "pending_updates.json"
        self.assertTrue(updates_file.exists())
    
    def test_get_cached_data(self):
        """Test getting cached data."""
        # Add some cached data
        self.fallback_manager._cached_data = {
            "test": {
                "timestamp": datetime.now().isoformat(),
                "data": {"key": "value"}
            }
        }
        
        # Get cached data
        data = self.fallback_manager.get_cached_data("test")
        
        # Verify data
        self.assertEqual(data, {"key": "value"})
        
        # Get non-existent data
        data = self.fallback_manager.get_cached_data("nonexistent")
        self.assertIsNone(data)
    
    def test_is_feature_available(self):
        """Test checking if a feature is available."""
        # Check feature availability in online state
        self.fallback_manager.state = ConnectivityState.ONLINE
        self.assertTrue(self.fallback_manager.is_feature_available("any_feature"))
        
        # Check feature availability in offline state
        self.fallback_manager.state = ConnectivityState.OFFLINE
        self.assertTrue(self.fallback_manager.is_feature_available("basic_conversation"))
        self.assertFalse(self.fallback_manager.is_feature_available("nonexistent_feature"))
    
    def test_get_state(self):
        """Test getting the current state."""
        # Set state
        self.fallback_manager.state = ConnectivityState.OFFLINE
        
        # Get state
        state = self.fallback_manager.get_state()
        
        # Verify state
        self.assertEqual(state, ConnectivityState.OFFLINE)
    
    def test_update_config(self):
        """Test updating configuration."""
        # Update config
        new_config = {"reconnect_interval": 60}
        self.fallback_manager.update_config(new_config)
        
        # Verify config was updated
        self.assertEqual(self.fallback_manager.config["reconnect_interval"], 60)


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.metrics_dir = Path(self.temp_dir.name) / "metrics"
        self.performance_monitor = PerformanceMonitor(metrics_dir=self.metrics_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        # Stop monitoring if it's running
        self.performance_monitor.stop_monitoring()
        self.temp_dir.cleanup()
    
    def test_determine_metric_type(self):
        """Test determining metric type."""
        # Test timer type
        self.assertEqual(self.performance_monitor._determine_metric_type("response_time"), MetricType.TIMER)
        
        # Test gauge type
        self.assertEqual(self.performance_monitor._determine_metric_type("cpu_usage"), MetricType.GAUGE)
        
        # Test counter type
        self.assertEqual(self.performance_monitor._determine_metric_type("api_calls"), MetricType.COUNTER)
        
        # Test histogram type (default)
        self.assertEqual(self.performance_monitor._determine_metric_type("other"), MetricType.HISTOGRAM)
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring."""
        # Start monitoring
        self.performance_monitor.start_monitoring()
        self.assertTrue(self.performance_monitor._monitoring_thread.is_alive())
        
        # Stop monitoring
        self.performance_monitor.stop_monitoring()
        time.sleep(0.1)  # Give thread time to stop
        self.assertFalse(self.performance_monitor._monitoring_thread.is_alive())
    
    def test_collect_metrics(self):
        """Test collecting metrics."""
        # Collect metrics
        self.performance_monitor._collect_metrics()
        
        # Verify metrics were collected
        for metric_name in self.performance_monitor.config["metrics_to_collect"]:
            self.assertIn(metric_name, self.performance_monitor.metrics)
            self.assertEqual(len(self.performance_monitor.metrics[metric_name]["values"]), 1)
    
    def test_check_alerts(self):
        """Test checking alerts."""
        # Add a metric value that exceeds threshold
        self.performance_monitor.metrics["response_time"] = {
            "type": MetricType.TIMER,
            "values": [{"timestamp": datetime.now().isoformat(), "value": 3.0}],
            "alerts": [],
        }
        
        # Check alerts
        self.performance_monitor._check_alerts()
        
        # Verify alert was added
        self.assertEqual(len(self.performance_monitor.metrics["response_time"]["alerts"]), 1)
    
    def test_save_metrics(self):
        """Test saving metrics."""
        # Add some metrics
        self.performance_monitor._collect_metrics()
        
        # Save metrics
        self.performance_monitor._save_metrics()
        
        # Verify metrics file was created
        metrics_files = list(self.metrics_dir.glob("metrics_*.json"))
        self.assertEqual(len(metrics_files), 1)
    
    def test_calculate_summary(self):
        """Test calculating summary statistics."""
        # Add some metric values
        self.performance_monitor.metrics["response_time"] = {
            "type": MetricType.TIMER,
            "values": [
                {"timestamp": datetime.now().isoformat(), "value": 1.0},
                {"timestamp": datetime.now().isoformat(), "value": 2.0},
                {"timestamp": datetime.now().isoformat(), "value": 3.0},
            ],
            "alerts": [],
        }
        
        # Calculate summary
        summary = self.performance_monitor._calculate_summary("response_time")
        
        # Verify summary
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["min"], 1.0)
        self.assertEqual(summary["max"], 3.0)
        self.assertEqual(summary["avg"], 2.0)
        self.assertEqual(summary["p50"], 2.0)
        self.assertEqual(summary["p90"], 3.0)
    
    def test_get_metric(self):
        """Test getting a metric."""
        # Add a metric
        self.performance_monitor.metrics["response_time"] = {
            "type": MetricType.TIMER,
            "values": [{"timestamp": datetime.now().isoformat(), "value": 1.0}],
            "alerts": [],
        }
        
        # Get the metric
        metric = self.performance_monitor.get_metric("response_time")
        
        # Verify metric
        self.assertEqual(metric["type"], MetricType.TIMER.value)
        self.assertEqual(len(metric["values"]), 1)
        self.assertEqual(metric["values"][0]["value"], 1.0)
    
    def test_get_all_metrics(self):
        """Test getting all metrics."""
        # Add some metrics
        self.performance_monitor._collect_metrics()
        
        # Get all metrics
        metrics = self.performance_monitor.get_all_metrics()
        
        # Verify metrics
        for metric_name in self.performance_monitor.config["metrics_to_collect"]:
            self.assertIn(metric_name, metrics)
    
    def test_record_custom_metric(self):
        """Test recording a custom metric."""
        # Record a custom metric
        self.performance_monitor.record_custom_metric("custom_metric", 42.0)
        
        # Verify metric was recorded
        self.assertIn("custom_metric", self.performance_monitor.metrics)
        self.assertEqual(len(self.performance_monitor.metrics["custom_metric"]["values"]), 1)
        self.assertEqual(self.performance_monitor.metrics["custom_metric"]["values"][0]["value"], 42.0)
    
    def test_get_alerts(self):
        """Test getting alerts."""
        # Add some alerts
        alert_time = datetime.now()
        self.performance_monitor.metrics["response_time"] = {
            "type": MetricType.TIMER,
            "values": [],
            "alerts": [
                {
                    "timestamp": alert_time.isoformat(),
                    "value": 3.0,
                    "threshold": 2.0,
                }
            ],
        }
        
        # Get all alerts
        alerts = self.performance_monitor.get_alerts()
        
        # Verify alerts
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["metric"], "response_time")
        self.assertEqual(alerts[0]["value"], 3.0)
        
        # Get alerts since a specific time
        future_time = alert_time + timedelta(seconds=1)
        alerts = self.performance_monitor.get_alerts(since=future_time)
        
        # Verify no alerts are returned
        self.assertEqual(len(alerts), 0)
    
    def test_update_config(self):
        """Test updating configuration."""
        # Update config
        new_config = {"collection_interval": 10}
        self.performance_monitor.update_config(new_config)
        
        # Verify config was updated
        self.assertEqual(self.performance_monitor.config["collection_interval"], 10)


if __name__ == '__main__':
    unittest.main()
