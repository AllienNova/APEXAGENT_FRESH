#!/usr/bin/env python3
"""
Test suite for the Analytics and Telemetry System.

This module provides comprehensive tests for the analytics and telemetry
components of the ApexAgent system.
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import threading
import time
import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from analytics.analytics_telemetry_system import (
    AnalyticsTelemetrySystem, AnalyticsConfig, EventType, EventPriority,
    AnalyticsEvent, MetricsCollector, EventProcessor, DataAggregator,
    VisualizationEngine, ExportFormat, PrivacyLevel
)

class TestAnalyticsTelemetrySystem(unittest.TestCase):
    """Test cases for the AnalyticsTelemetrySystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalyticsConfig(
            enabled=True,
            data_directory=self.temp_dir,
            privacy_level=PrivacyLevel.ANONYMIZED,
            collection_interval=60,
            batch_size=100,
            retention_days=30,
            auto_export_enabled=False
        )
        self.analytics_system = AnalyticsTelemetrySystem.get_instance()
        self.analytics_system.initialize(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.analytics_system.shutdown()
    
    def test_singleton_pattern(self):
        """Test that the analytics system follows the singleton pattern."""
        instance1 = AnalyticsTelemetrySystem.get_instance()
        instance2 = AnalyticsTelemetrySystem.get_instance()
        self.assertIs(instance1, instance2)
    
    def test_track_event(self):
        """Test tracking an event."""
        # Mock event processor
        mock_processor = MagicMock()
        self.analytics_system._event_processor = mock_processor
        
        # Track event
        event = AnalyticsEvent(
            event_type=EventType.USER_ACTION,
            name="button_click",
            properties={"button_id": "submit", "page": "checkout"},
            priority=EventPriority.NORMAL
        )
        self.analytics_system.track_event(event)
        
        # Verify event was processed
        mock_processor.process_event.assert_called_once_with(event)
    
    def test_track_event_with_dict(self):
        """Test tracking an event using a dictionary."""
        # Mock event processor
        mock_processor = MagicMock()
        self.analytics_system._event_processor = mock_processor
        
        # Track event with dictionary
        self.analytics_system.track_event_dict(
            event_type=EventType.USER_ACTION,
            name="button_click",
            properties={"button_id": "submit", "page": "checkout"}
        )
        
        # Verify event was processed
        mock_processor.process_event.assert_called_once()
        args, _ = mock_processor.process_event.call_args
        event = args[0]
        self.assertEqual(event.event_type, EventType.USER_ACTION)
        self.assertEqual(event.name, "button_click")
        self.assertEqual(event.properties["button_id"], "submit")
    
    def test_get_metrics(self):
        """Test getting metrics."""
        # Mock metrics collector
        mock_collector = MagicMock()
        mock_collector.get_metrics.return_value = {
            "cpu_usage": 25.5,
            "memory_usage": 512.0,
            "active_users": 10
        }
        self.analytics_system._metrics_collector = mock_collector
        
        # Get metrics
        metrics = self.analytics_system.get_metrics()
        
        # Verify metrics
        self.assertEqual(metrics["cpu_usage"], 25.5)
        self.assertEqual(metrics["memory_usage"], 512.0)
        self.assertEqual(metrics["active_users"], 10)
    
    def test_get_aggregated_data(self):
        """Test getting aggregated data."""
        # Mock data aggregator
        mock_aggregator = MagicMock()
        mock_aggregator.get_aggregated_data.return_value = {
            "daily_active_users": [5, 8, 10, 12, 15],
            "average_session_time": 120.5
        }
        self.analytics_system._data_aggregator = mock_aggregator
        
        # Get aggregated data
        data = self.analytics_system.get_aggregated_data(
            metrics=["daily_active_users", "average_session_time"],
            start_date=datetime.datetime.now() - datetime.timedelta(days=5),
            end_date=datetime.datetime.now()
        )
        
        # Verify data
        self.assertEqual(data["daily_active_users"], [5, 8, 10, 12, 15])
        self.assertEqual(data["average_session_time"], 120.5)
    
    @patch('analytics.analytics_telemetry_system.os.path.exists')
    @patch('analytics.analytics_telemetry_system.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_data(self, mock_file, mock_makedirs, mock_exists):
        """Test exporting data."""
        # Mock data aggregator
        mock_aggregator = MagicMock()
        mock_aggregator.get_aggregated_data.return_value = {
            "daily_active_users": [5, 8, 10, 12, 15],
            "average_session_time": 120.5
        }
        self.analytics_system._data_aggregator = mock_aggregator
        
        # Mock path exists
        mock_exists.return_value = False
        
        # Export data
        export_path = self.analytics_system.export_data(
            metrics=["daily_active_users", "average_session_time"],
            start_date=datetime.datetime.now() - datetime.timedelta(days=5),
            end_date=datetime.datetime.now(),
            format=ExportFormat.JSON,
            output_path=os.path.join(self.temp_dir, "export.json")
        )
        
        # Verify export
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        self.assertTrue(export_path.endswith("export.json"))
    
    def test_generate_visualization(self):
        """Test generating visualization."""
        # Mock visualization engine
        mock_engine = MagicMock()
        mock_engine.generate_visualization.return_value = "/path/to/chart.png"
        self.analytics_system._visualization_engine = mock_engine
        
        # Mock data aggregator
        mock_aggregator = MagicMock()
        mock_aggregator.get_aggregated_data.return_value = {
            "daily_active_users": [5, 8, 10, 12, 15]
        }
        self.analytics_system._data_aggregator = mock_aggregator
        
        # Generate visualization
        chart_path = self.analytics_system.generate_visualization(
            metric="daily_active_users",
            chart_type="line",
            title="Daily Active Users",
            start_date=datetime.datetime.now() - datetime.timedelta(days=5),
            end_date=datetime.datetime.now()
        )
        
        # Verify visualization
        self.assertEqual(chart_path, "/path/to/chart.png")
        mock_engine.generate_visualization.assert_called_once()

class TestAnalyticsEvent(unittest.TestCase):
    """Test cases for the AnalyticsEvent class."""
    
    def test_event_creation(self):
        """Test creating an analytics event."""
        event = AnalyticsEvent(
            event_type=EventType.USER_ACTION,
            name="button_click",
            properties={"button_id": "submit", "page": "checkout"},
            priority=EventPriority.HIGH
        )
        
        self.assertEqual(event.event_type, EventType.USER_ACTION)
        self.assertEqual(event.name, "button_click")
        self.assertEqual(event.properties["button_id"], "submit")
        self.assertEqual(event.priority, EventPriority.HIGH)
        self.assertIsNotNone(event.timestamp)
        self.assertIsNotNone(event.event_id)
    
    def test_to_dict(self):
        """Test converting event to dictionary."""
        event = AnalyticsEvent(
            event_type=EventType.USER_ACTION,
            name="button_click",
            properties={"button_id": "submit"},
            priority=EventPriority.NORMAL
        )
        
        event_dict = event.to_dict()
        
        self.assertEqual(event_dict["event_type"], "user_action")
        self.assertEqual(event_dict["name"], "button_click")
        self.assertEqual(event_dict["properties"]["button_id"], "submit")
        self.assertEqual(event_dict["priority"], "normal")
        self.assertIn("timestamp", event_dict)
        self.assertIn("event_id", event_dict)
    
    def test_from_dict(self):
        """Test creating event from dictionary."""
        event_dict = {
            "event_type": "user_action",
            "name": "button_click",
            "properties": {"button_id": "submit"},
            "priority": "high",
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": "test-id-123"
        }
        
        event = AnalyticsEvent.from_dict(event_dict)
        
        self.assertEqual(event.event_type, EventType.USER_ACTION)
        self.assertEqual(event.name, "button_click")
        self.assertEqual(event.properties["button_id"], "submit")
        self.assertEqual(event.priority, EventPriority.HIGH)
        self.assertEqual(event.event_id, "test-id-123")
    
    def test_anonymize(self):
        """Test anonymizing an event."""
        event = AnalyticsEvent(
            event_type=EventType.USER_ACTION,
            name="login",
            properties={
                "username": "john_doe",
                "email": "john@example.com",
                "ip_address": "192.168.1.1",
                "button_id": "login_button"
            }
        )
        
        anonymized = event.anonymize()
        
        # Verify sensitive data is anonymized
        self.assertNotEqual(anonymized.properties["username"], "john_doe")
        self.assertNotEqual(anonymized.properties["email"], "john@example.com")
        self.assertNotEqual(anonymized.properties["ip_address"], "192.168.1.1")
        
        # Non-sensitive data should remain
        self.assertEqual(anonymized.properties["button_id"], "login_button")
        
        # Event type and name should remain
        self.assertEqual(anonymized.event_type, EventType.USER_ACTION)
        self.assertEqual(anonymized.name, "login")

class TestMetricsCollector(unittest.TestCase):
    """Test cases for the MetricsCollector class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = AnalyticsConfig(
            enabled=True,
            collection_interval=60
        )
        self.collector = MetricsCollector(self.config)
    
    def test_collect_system_metrics(self):
        """Test collecting system metrics."""
        with patch('analytics.analytics_telemetry_system.psutil') as mock_psutil:
            # Mock psutil functions
            mock_psutil.cpu_percent.return_value = 25.5
            mock_psutil.virtual_memory.return_value.percent = 40.0
            mock_psutil.disk_usage.return_value.percent = 60.0
            
            # Collect metrics
            metrics = self.collector.collect_system_metrics()
            
            # Verify metrics
            self.assertEqual(metrics["cpu_usage"], 25.5)
            self.assertEqual(metrics["memory_usage"], 40.0)
            self.assertEqual(metrics["disk_usage"], 60.0)
    
    def test_collect_application_metrics(self):
        """Test collecting application metrics."""
        # Mock application metrics
        self.collector._app_metrics = {
            "active_users": 10,
            "active_sessions": 5,
            "requests_per_minute": 120
        }
        
        # Collect metrics
        metrics = self.collector.collect_application_metrics()
        
        # Verify metrics
        self.assertEqual(metrics["active_users"], 10)
        self.assertEqual(metrics["active_sessions"], 5)
        self.assertEqual(metrics["requests_per_minute"], 120)
    
    def test_get_metrics(self):
        """Test getting all metrics."""
        # Mock system and application metrics
        with patch.object(self.collector, 'collect_system_metrics') as mock_system:
            with patch.object(self.collector, 'collect_application_metrics') as mock_app:
                mock_system.return_value = {
                    "cpu_usage": 25.5,
                    "memory_usage": 40.0
                }
                mock_app.return_value = {
                    "active_users": 10,
                    "requests_per_minute": 120
                }
                
                # Get all metrics
                metrics = self.collector.get_metrics()
                
                # Verify metrics
                self.assertEqual(metrics["cpu_usage"], 25.5)
                self.assertEqual(metrics["memory_usage"], 40.0)
                self.assertEqual(metrics["active_users"], 10)
                self.assertEqual(metrics["requests_per_minute"], 120)
    
    def test_update_application_metric(self):
        """Test updating an application metric."""
        # Update metric
        self.collector.update_application_metric("active_users", 15)
        
        # Verify metric was updated
        metrics = self.collector.collect_application_metrics()
        self.assertEqual(metrics["active_users"], 15)
    
    def test_increment_application_metric(self):
        """Test incrementing an application metric."""
        # Set initial value
        self.collector.update_application_metric("request_count", 10)
        
        # Increment metric
        self.collector.increment_application_metric("request_count")
        
        # Verify metric was incremented
        metrics = self.collector.collect_application_metrics()
        self.assertEqual(metrics["request_count"], 11)
    
    def test_decrement_application_metric(self):
        """Test decrementing an application metric."""
        # Set initial value
        self.collector.update_application_metric("active_sessions", 5)
        
        # Decrement metric
        self.collector.decrement_application_metric("active_sessions")
        
        # Verify metric was decremented
        metrics = self.collector.collect_application_metrics()
        self.assertEqual(metrics["active_sessions"], 4)

class TestEventProcessor(unittest.TestCase):
    """Test cases for the EventProcessor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalyticsConfig(
            enabled=True,
            data_directory=self.temp_dir,
            privacy_level=PrivacyLevel.ANONYMIZED,
            batch_size=10
        )
        self.processor = EventProcessor(self.config)
    
    def test_process_event(self):
        """Test processing an event."""
        # Create event
        event = AnalyticsEvent(
            event_type=EventType.USER_ACTION,
            name="button_click",
            properties={"button_id": "submit"}
        )
        
        # Process event
        with patch.object(self.processor, '_store_event') as mock_store:
            self.processor.process_event(event)
            
            # Verify event was stored
            mock_store.assert_called_once()
            args, _ = mock_store.call_args
            stored_event = args[0]
            
            # Verify event was anonymized (since privacy level is ANONYMIZED)
            self.assertIsNot(stored_event, event)
    
    def test_process_batch(self):
        """Test processing a batch of events."""
        # Create events
        events = [
            AnalyticsEvent(
                event_type=EventType.USER_ACTION,
                name=f"event_{i}",
                properties={"index": i}
            )
            for i in range(5)
        ]
        
        # Process batch
        with patch.object(self.processor, '_store_events') as mock_store:
            self.processor.process_batch(events)
            
            # Verify batch was stored
            mock_store.assert_called_once()
            args, _ = mock_store.call_args
            stored_events = args[0]
            self.assertEqual(len(stored_events), 5)
    
    @patch('analytics.analytics_telemetry_system.os.path.exists')
    @patch('analytics.analytics_telemetry_system.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_store_event(self, mock_file, mock_makedirs, mock_exists):
        """Test storing an event."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Create event
        event = AnalyticsEvent(
            event_type=EventType.USER_ACTION,
            name="button_click",
            properties={"button_id": "submit"}
        )
        
        # Store event
        self.processor._store_event(event)
        
        # Verify event was stored
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        mock_file().write.assert_called_once()
    
    def test_batch_processing(self):
        """Test automatic batch processing."""
        # Mock _store_events
        with patch.object(self.processor, '_store_events') as mock_store:
            # Set batch size to 3
            self.processor._batch_size = 3
            
            # Process 2 events (not enough for a batch)
            for i in range(2):
                event = AnalyticsEvent(
                    event_type=EventType.USER_ACTION,
                    name=f"event_{i}",
                    properties={"index": i}
                )
                self.processor.process_event(event)
            
            # Verify batch was not stored yet
            mock_store.assert_not_called()
            self.assertEqual(len(self.processor._event_queue), 2)
            
            # Process 1 more event (completes the batch)
            event = AnalyticsEvent(
                event_type=EventType.USER_ACTION,
                name="event_2",
                properties={"index": 2}
            )
            self.processor.process_event(event)
            
            # Verify batch was stored
            mock_store.assert_called_once()
            self.assertEqual(len(self.processor._event_queue), 0)

class TestDataAggregator(unittest.TestCase):
    """Test cases for the DataAggregator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalyticsConfig(
            enabled=True,
            data_directory=self.temp_dir
        )
        self.aggregator = DataAggregator(self.config)
    
    @patch('analytics.analytics_telemetry_system.glob.glob')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_events(self, mock_file, mock_glob):
        """Test loading events from storage."""
        # Mock glob to return file paths
        mock_glob.return_value = [
            os.path.join(self.temp_dir, "events", "2023-01-01", "event1.json"),
            os.path.join(self.temp_dir, "events", "2023-01-01", "event2.json")
        ]
        
        # Mock file content
        mock_file.return_value.__enter__.return_value.read.side_effect = [
            json.dumps({
                "event_type": "user_action",
                "name": "button_click",
                "properties": {"button_id": "submit"},
                "timestamp": "2023-01-01T12:00:00"
            }),
            json.dumps({
                "event_type": "system",
                "name": "app_start",
                "properties": {},
                "timestamp": "2023-01-01T12:05:00"
            })
        ]
        
        # Load events
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime(2023, 1, 2)
        events = self.aggregator._load_events(start_date, end_date)
        
        # Verify events
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].name, "button_click")
        self.assertEqual(events[1].name, "app_start")
    
    def test_aggregate_events(self):
        """Test aggregating events."""
        # Create test events
        events = [
            AnalyticsEvent(
                event_type=EventType.USER_ACTION,
                name="page_view",
                properties={"page": "home"},
                timestamp=datetime.datetime(2023, 1, 1, 12, 0)
            ),
            AnalyticsEvent(
                event_type=EventType.USER_ACTION,
                name="page_view",
                properties={"page": "products"},
                timestamp=datetime.datetime(2023, 1, 1, 12, 5)
            ),
            AnalyticsEvent(
                event_type=EventType.USER_ACTION,
                name="button_click",
                properties={"button_id": "add_to_cart"},
                timestamp=datetime.datetime(2023, 1, 1, 12, 10)
            ),
            AnalyticsEvent(
                event_type=EventType.USER_ACTION,
                name="page_view",
                properties={"page": "cart"},
                timestamp=datetime.datetime(2023, 1, 1, 12, 15)
            )
        ]
        
        # Aggregate events
        aggregated = self.aggregator._aggregate_events(events)
        
        # Verify aggregation
        self.assertEqual(aggregated["event_counts"]["page_view"], 3)
        self.assertEqual(aggregated["event_counts"]["button_click"], 1)
        self.assertEqual(aggregated["page_views"]["home"], 1)
        self.assertEqual(aggregated["page_views"]["products"], 1)
        self.assertEqual(aggregated["page_views"]["cart"], 1)
    
    @patch('analytics.analytics_telemetry_system.DataAggregator._load_events')
    def test_get_aggregated_data(self, mock_load):
        """Test getting aggregated data."""
        # Mock loaded events
        mock_load.return_value = [
            AnalyticsEvent(
                event_type=EventType.USER_ACTION,
                name="page_view",
                properties={"page": "home"},
                timestamp=datetime.datetime(2023, 1, 1, 12, 0)
            ),
            AnalyticsEvent(
                event_type=EventType.USER_ACTION,
                name="button_click",
                properties={"button_id": "submit"},
                timestamp=datetime.datetime(2023, 1, 1, 12, 5)
            )
        ]
        
        # Get aggregated data
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime(2023, 1, 2)
        data = self.aggregator.get_aggregated_data(
            metrics=["event_counts", "page_views"],
            start_date=start_date,
            end_date=end_date
        )
        
        # Verify data
        self.assertIn("event_counts", data)
        self.assertIn("page_views", data)
        self.assertEqual(data["event_counts"]["page_view"], 1)
        self.assertEqual(data["event_counts"]["button_click"], 1)
        self.assertEqual(data["page_views"]["home"], 1)

class TestVisualizationEngine(unittest.TestCase):
    """Test cases for the VisualizationEngine class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AnalyticsConfig(
            enabled=True,
            data_directory=self.temp_dir
        )
        self.engine = VisualizationEngine(self.config)
    
    @patch('analytics.analytics_telemetry_system.plt')
    @patch('analytics.analytics_telemetry_system.os.path.exists')
    @patch('analytics.analytics_telemetry_system.os.makedirs')
    def test_generate_line_chart(self, mock_makedirs, mock_exists, mock_plt):
        """Test generating a line chart."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Mock matplotlib
        mock_plt.figure.return_value = MagicMock()
        mock_plt.savefig.return_value = None
        
        # Generate chart
        data = {
            "dates": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
            "values": [10, 15, 12, 18, 20]
        }
        chart_path = self.engine.generate_line_chart(
            data=data,
            title="Test Chart",
            x_label="Date",
            y_label="Value",
            output_path=os.path.join(self.temp_dir, "chart.png")
        )
        
        # Verify chart generation
        mock_makedirs.assert_called_once()
        mock_plt.figure.assert_called_once()
        mock_plt.plot.assert_called_once()
        mock_plt.title.assert_called_once_with("Test Chart")
        mock_plt.xlabel.assert_called_once_with("Date")
        mock_plt.ylabel.assert_called_once_with("Value")
        mock_plt.savefig.assert_called_once()
        self.assertTrue(chart_path.endswith("chart.png"))
    
    @patch('analytics.analytics_telemetry_system.plt')
    @patch('analytics.analytics_telemetry_system.os.path.exists')
    @patch('analytics.analytics_telemetry_system.os.makedirs')
    def test_generate_bar_chart(self, mock_makedirs, mock_exists, mock_plt):
        """Test generating a bar chart."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Mock matplotlib
        mock_plt.figure.return_value = MagicMock()
        mock_plt.savefig.return_value = None
        
        # Generate chart
        data = {
            "categories": ["Category A", "Category B", "Category C", "Category D"],
            "values": [10, 15, 12, 18]
        }
        chart_path = self.engine.generate_bar_chart(
            data=data,
            title="Test Bar Chart",
            x_label="Category",
            y_label="Value",
            output_path=os.path.join(self.temp_dir, "bar_chart.png")
        )
        
        # Verify chart generation
        mock_makedirs.assert_called_once()
        mock_plt.figure.assert_called_once()
        mock_plt.bar.assert_called_once()
        mock_plt.title.assert_called_once_with("Test Bar Chart")
        mock_plt.xlabel.assert_called_once_with("Category")
        mock_plt.ylabel.assert_called_once_with("Value")
        mock_plt.savefig.assert_called_once()
        self.assertTrue(chart_path.endswith("bar_chart.png"))
    
    @patch('analytics.analytics_telemetry_system.plt')
    @patch('analytics.analytics_telemetry_system.os.path.exists')
    @patch('analytics.analytics_telemetry_system.os.makedirs')
    def test_generate_pie_chart(self, mock_makedirs, mock_exists, mock_plt):
        """Test generating a pie chart."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Mock matplotlib
        mock_plt.figure.return_value = MagicMock()
        mock_plt.savefig.return_value = None
        
        # Generate chart
        data = {
            "labels": ["Category A", "Category B", "Category C", "Category D"],
            "values": [10, 15, 12, 18]
        }
        chart_path = self.engine.generate_pie_chart(
            data=data,
            title="Test Pie Chart",
            output_path=os.path.join(self.temp_dir, "pie_chart.png")
        )
        
        # Verify chart generation
        mock_makedirs.assert_called_once()
        mock_plt.figure.assert_called_once()
        mock_plt.pie.assert_called_once()
        mock_plt.title.assert_called_once_with("Test Pie Chart")
        mock_plt.savefig.assert_called_once()
        self.assertTrue(chart_path.endswith("pie_chart.png"))
    
    @patch('analytics.analytics_telemetry_system.VisualizationEngine.generate_line_chart')
    @patch('analytics.analytics_telemetry_system.VisualizationEngine.generate_bar_chart')
    @patch('analytics.analytics_telemetry_system.VisualizationEngine.generate_pie_chart')
    def test_generate_visualization(self, mock_pie, mock_bar, mock_line):
        """Test generating visualization based on chart type."""
        # Mock chart generation methods
        mock_line.return_value = "/path/to/line_chart.png"
        mock_bar.return_value = "/path/to/bar_chart.png"
        mock_pie.return_value = "/path/to/pie_chart.png"
        
        # Test line chart
        data = {"dates": ["2023-01-01"], "values": [10]}
        chart_path = self.engine.generate_visualization(
            data=data,
            chart_type="line",
            title="Test Chart",
            output_path="/path/to/chart.png"
        )
        mock_line.assert_called_once()
        self.assertEqual(chart_path, "/path/to/line_chart.png")
        
        # Test bar chart
        data = {"categories": ["Category A"], "values": [10]}
        chart_path = self.engine.generate_visualization(
            data=data,
            chart_type="bar",
            title="Test Chart",
            output_path="/path/to/chart.png"
        )
        mock_bar.assert_called_once()
        self.assertEqual(chart_path, "/path/to/bar_chart.png")
        
        # Test pie chart
        data = {"labels": ["Category A"], "values": [10]}
        chart_path = self.engine.generate_visualization(
            data=data,
            chart_type="pie",
            title="Test Chart",
            output_path="/path/to/chart.png"
        )
        mock_pie.assert_called_once()
        self.assertEqual(chart_path, "/path/to/pie_chart.png")

if __name__ == '__main__':
    unittest.main()
