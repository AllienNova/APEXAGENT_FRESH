"""
Unit tests for the ApexAgent event system.

This module contains tests for the event system components, including
Event, EventSubscriber, EventLogger, EventManager, and EventVisualizer.
"""

import asyncio
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import re
from typing import List, Set

from src.core.event_system.event import Event, EventPriority
from src.core.event_system.event_subscriber import EventSubscriber, CallbackEventSubscriber
from src.core.event_system.event_logger import EventLogger
from src.core.event_system.event_manager import EventManager
from src.core.event_system.event_visualizer import EventVisualizer


class TestEvent(unittest.TestCase):
    """Tests for the Event class."""
    
    def test_event_creation(self):
        """Test creating an event."""
        event = Event(
            event_type="test_event",
            source="test_source",
            data={"key": "value"},
            priority=EventPriority.HIGH
        )
        
        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.data, {"key": "value"})
        self.assertEqual(event.priority, EventPriority.HIGH)
        self.assertIsNotNone(event.timestamp)
        self.assertIsNotNone(event.id)
        self.assertIsNone(event.parent_id)
        self.assertEqual(event.metadata, {})
    
    def test_event_validation(self):
        """Test event validation."""
        with self.assertRaises(ValueError):
            Event(event_type="", source="test_source")
        
        with self.assertRaises(ValueError):
            Event(event_type="test_event", source="")
    
    def test_with_parent(self):
        """Test creating a child event."""
        parent = Event(
            event_type="parent_event",
            source="test_source"
        )
        
        child = Event(
            event_type="child_event",
            source="test_source"
        ).with_parent(parent)
        
        self.assertEqual(child.parent_id, parent.id)
    
    def test_with_metadata(self):
        """Test adding metadata to an event."""
        event = Event(
            event_type="test_event",
            source="test_source"
        )
        
        updated = event.with_metadata(key1="value1", key2="value2")
        
        self.assertEqual(updated.metadata, {"key1": "value1", "key2": "value2"})
    
    def test_to_dict(self):
        """Test converting an event to a dictionary."""
        event = Event(
            event_type="test_event",
            source="test_source",
            data={"key": "value"},
            priority=EventPriority.HIGH
        )
        
        event_dict = event.to_dict()
        
        self.assertEqual(event_dict["event_type"], "test_event")
        self.assertEqual(event_dict["source"], "test_source")
        self.assertEqual(event_dict["data"], {"key": "value"})
        self.assertEqual(event_dict["priority"], "HIGH")
        self.assertIsNotNone(event_dict["timestamp"])
        self.assertIsNotNone(event_dict["id"])
        self.assertIsNone(event_dict["parent_id"])
        self.assertEqual(event_dict["metadata"], {})
    
    def test_from_dict(self):
        """Test creating an event from a dictionary."""
        event_dict = {
            "event_type": "test_event",
            "source": "test_source",
            "data": {"key": "value"},
            "priority": "HIGH",
            "timestamp": datetime.now().isoformat(),
            "id": "test_id",
            "parent_id": "parent_id",
            "metadata": {"meta_key": "meta_value"}
        }
        
        event = Event.from_dict(event_dict)
        
        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.data, {"key": "value"})
        self.assertEqual(event.priority, EventPriority.HIGH)
        self.assertEqual(event.id, "test_id")
        self.assertEqual(event.parent_id, "parent_id")
        self.assertEqual(event.metadata, {"meta_key": "meta_value"})


class TestEventSubscriber(unittest.TestCase):
    """Tests for the EventSubscriber classes."""
    
    def test_callback_subscriber_creation(self):
        """Test creating a callback subscriber."""
        callback = lambda event: None
        subscriber = CallbackEventSubscriber(
            callback=callback,
            event_types={"test_event"},
            priority_filter={EventPriority.HIGH},
            source_filter={"test_source"}
        )
        
        self.assertEqual(subscriber.subscribed_event_types, {"test_event"})
        self.assertEqual(subscriber.priority_filter, {EventPriority.HIGH})
        self.assertEqual(subscriber.source_filter, {"test_source"})
    
    def test_callback_subscriber_string_event_type(self):
        """Test creating a callback subscriber with a string event type."""
        callback = lambda event: None
        subscriber = CallbackEventSubscriber(
            callback=callback,
            event_types="test_event"
        )
        
        self.assertEqual(subscriber.subscribed_event_types, {"test_event"})
    
    def test_callback_subscriber_list_event_types(self):
        """Test creating a callback subscriber with a list of event types."""
        callback = lambda event: None
        subscriber = CallbackEventSubscriber(
            callback=callback,
            event_types=["event1", "event2"]
        )
        
        self.assertEqual(subscriber.subscribed_event_types, {"event1", "event2"})
    
    def test_matches_event(self):
        """Test event matching."""
        callback = lambda event: None
        subscriber = CallbackEventSubscriber(
            callback=callback,
            event_types={"test_event"},
            priority_filter={EventPriority.HIGH},
            source_filter={"test_source"}
        )
        
        # Matching event
        event1 = Event(
            event_type="test_event",
            source="test_source",
            priority=EventPriority.HIGH
        )
        self.assertTrue(subscriber.matches_event(event1))
        
        # Non-matching event type
        event2 = Event(
            event_type="other_event",
            source="test_source",
            priority=EventPriority.HIGH
        )
        self.assertFalse(subscriber.matches_event(event2))
        
        # Non-matching source
        event3 = Event(
            event_type="test_event",
            source="other_source",
            priority=EventPriority.HIGH
        )
        self.assertFalse(subscriber.matches_event(event3))
        
        # Non-matching priority
        event4 = Event(
            event_type="test_event",
            source="test_source",
            priority=EventPriority.LOW
        )
        self.assertFalse(subscriber.matches_event(event4))
    
    def test_regex_matching(self):
        """Test regex pattern matching for event types and sources."""
        callback = lambda event: None
        subscriber = CallbackEventSubscriber(
            callback=callback,
            event_types=re.compile(r"test_.*"),
            source_filter=re.compile(r"source_.*")
        )
        
        # Matching event
        event1 = Event(
            event_type="test_event",
            source="source_1"
        )
        self.assertTrue(subscriber.matches_event(event1))
        
        # Another matching event
        event2 = Event(
            event_type="test_other",
            source="source_2"
        )
        self.assertTrue(subscriber.matches_event(event2))
        
        # Non-matching event type
        event3 = Event(
            event_type="other_event",
            source="source_1"
        )
        self.assertFalse(subscriber.matches_event(event3))
        
        # Non-matching source
        event4 = Event(
            event_type="test_event",
            source="other_source"
        )
        self.assertFalse(subscriber.matches_event(event4))


class TestEventLogger(unittest.IsolatedAsyncioTestCase):
    """Tests for the EventLogger class."""
    
    async def test_memory_logging(self):
        """Test logging events to memory."""
        logger = EventLogger(log_to_memory=True, log_to_file=False, log_to_logger=False)
        
        event1 = Event(event_type="test_event_1", source="test_source")
        event2 = Event(event_type="test_event_2", source="test_source")
        
        await logger.log_event(event1)
        await logger.log_event(event2)
        
        events = logger.get_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, "test_event_1")
        self.assertEqual(events[1].event_type, "test_event_2")
    
    async def test_file_logging(self):
        """Test logging events to a file."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create logger with file logging
            logger = EventLogger(
                log_to_memory=False,
                log_to_file=True,
                log_file_path=temp_path,
                log_to_logger=False
            )
            
            event = Event(event_type="test_event", source="test_source", data={"key": "value"})
            await logger.log_event(event)
            
            # Close the logger to ensure file is written
            logger.close()
            
            # Check file contents
            with open(temp_path, "r") as f:
                lines = f.readlines()
                
                # First line should be the header
                self.assertIn("event_log_header", lines[0])
                
                # Second line should contain the event
                self.assertIn("test_event", lines[1])
                self.assertIn("test_source", lines[1])
                self.assertIn("key", lines[1])
                self.assertIn("value", lines[1])
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    async def test_event_filtering(self):
        """Test filtering events by type."""
        logger = EventLogger(
            log_to_memory=True,
            log_to_file=False,
            log_to_logger=False,
            event_types_to_log={"included_event"}
        )
        
        event1 = Event(event_type="included_event", source="test_source")
        event2 = Event(event_type="excluded_event", source="test_source")
        
        await logger.log_event(event1)
        await logger.log_event(event2)
        
        events = logger.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "included_event")
    
    async def test_memory_limit(self):
        """Test memory limit for stored events."""
        logger = EventLogger(
            log_to_memory=True,
            log_to_file=False,
            log_to_logger=False,
            memory_limit=2
        )
        
        event1 = Event(event_type="event1", source="test_source")
        event2 = Event(event_type="event2", source="test_source")
        event3 = Event(event_type="event3", source="test_source")
        
        await logger.log_event(event1)
        await logger.log_event(event2)
        await logger.log_event(event3)
        
        events = logger.get_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, "event2")
        self.assertEqual(events[1].event_type, "event3")
    
    async def test_clear_memory(self):
        """Test clearing events from memory."""
        logger = EventLogger(log_to_memory=True, log_to_file=False, log_to_logger=False)
        
        event = Event(event_type="test_event", source="test_source")
        await logger.log_event(event)
        
        self.assertEqual(len(logger.get_events()), 1)
        
        logger.clear_memory()
        self.assertEqual(len(logger.get_events()), 0)


class TestEventManager(unittest.IsolatedAsyncioTestCase):
    """Tests for the EventManager class."""
    
    async def test_register_subscriber(self):
        """Test registering a subscriber."""
        manager = EventManager()
        
        # Create a mock subscriber
        class MockSubscriber(EventSubscriber):
            def __init__(self):
                self.events_received = []
            
            async def handle_event(self, event):
                self.events_received.append(event)
            
            @property
            def subscribed_event_types(self):
                return {"test_event"}
        
        subscriber = MockSubscriber()
        await manager.register_subscriber(subscriber)
        
        # Emit an event
        event = Event(event_type="test_event", source="test_source")
        delivery_count = await manager.emit(event)
        
        self.assertEqual(delivery_count, 1)
        self.assertEqual(len(subscriber.events_received), 1)
        self.assertEqual(subscriber.events_received[0].event_type, "test_event")
    
    async def test_unregister_subscriber(self):
        """Test unregistering a subscriber."""
        manager = EventManager()
        
        # Create a mock subscriber
        class MockSubscriber(EventSubscriber):
            def __init__(self):
                self.events_received = []
            
            async def handle_event(self, event):
                self.events_received.append(event)
            
            @property
            def subscribed_event_types(self):
                return {"test_event"}
        
        subscriber = MockSubscriber()
        await manager.register_subscriber(subscriber)
        
        # Unregister the subscriber
        result = await manager.unregister_subscriber(subscriber)
        self.assertTrue(result)
        
        # Emit an event
        event = Event(event_type="test_event", source="test_source")
        delivery_count = await manager.emit(event)
        
        self.assertEqual(delivery_count, 0)
        self.assertEqual(len(subscriber.events_received), 0)
    
    async def test_register_callback(self):
        """Test registering a callback function."""
        manager = EventManager()
        
        # Create a callback function
        events_received = []
        async def callback(event):
            events_received.append(event)
        
        # Register the callback
        await manager.register_callback(
            callback=callback,
            event_types="test_event"
        )
        
        # Emit an event
        event = Event(event_type="test_event", source="test_source")
        delivery_count = await manager.emit(event)
        
        self.assertEqual(delivery_count, 1)
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].event_type, "test_event")
    
    async def test_register_logger(self):
        """Test registering a logger."""
        manager = EventManager()
        
        # Create a logger
        logger = EventLogger(log_to_memory=True, log_to_file=False, log_to_logger=False)
        await manager.register_logger(logger)
        
        # Emit an event
        event = Event(event_type="test_event", source="test_source")
        await manager.emit(event)
        
        # Check that the event was logged
        logged_events = logger.get_events()
        self.assertEqual(len(logged_events), 1)
        self.assertEqual(logged_events[0].event_type, "test_event")
    
    async def test_unregister_logger(self):
        """Test unregistering a logger."""
        manager = EventManager()
        
        # Create a logger
        logger = EventLogger(log_to_memory=True, log_to_file=False, log_to_logger=False)
        await manager.register_logger(logger)
        
        # Unregister the logger
        result = await manager.unregister_logger(logger)
        self.assertTrue(result)
        
        # Emit an event
        event = Event(event_type="test_event", source="test_source")
        await manager.emit(event)
        
        # Check that the event was not logged
        logged_events = logger.get_events()
        self.assertEqual(len(logged_events), 0)
    
    async def test_create_and_emit_event(self):
        """Test creating and emitting an event in one step."""
        manager = EventManager()
        
        # Create a mock subscriber
        class MockSubscriber(EventSubscriber):
            def __init__(self):
                self.events_received = []
            
            async def handle_event(self, event):
                self.events_received.append(event)
            
            @property
            def subscribed_event_types(self):
                return {"test_event"}
        
        subscriber = MockSubscriber()
        await manager.register_subscriber(subscriber)
        
        # Create and emit an event
        event = await manager.emit_new(
            event_type="test_event",
            source="test_source",
            data={"key": "value"}
        )
        
        self.assertEqual(len(subscriber.events_received), 1)
        self.assertEqual(subscriber.events_received[0].event_type, "test_event")
        self.assertEqual(subscriber.events_received[0].data, {"key": "value"})
    
    async def test_stats(self):
        """Test event statistics."""
        manager = EventManager()
        
        # Create a mock subscriber
        class MockSubscriber(EventSubscriber):
            def __init__(self):
                self.events_received = []
            
            async def handle_event(self, event):
                self.events_received.append(event)
            
            @property
            def subscribed_event_types(self):
                return {"test_event"}
        
        subscriber = MockSubscriber()
        await manager.register_subscriber(subscriber)
        
        # Emit an event
        event = Event(event_type="test_event", source="test_source")
        await manager.emit(event)
        
        # Check stats
        stats = manager.get_stats()
        self.assertEqual(stats["events_emitted"], 1)
        self.assertEqual(stats["events_delivered"], 1)
        self.assertEqual(stats["subscribers_notified"], 1)
        
        # Reset stats
        manager.reset_stats()
        stats = manager.get_stats()
        self.assertEqual(stats["events_emitted"], 0)
        self.assertEqual(stats["events_delivered"], 0)
        self.assertEqual(stats["subscribers_notified"], 0)
    
    async def test_shutdown(self):
        """Test shutting down the event manager."""
        manager = EventManager()
        
        # Create a mock subscriber
        class MockSubscriber(EventSubscriber):
            def __init__(self):
                self.events_received = []
            
            async def handle_event(self, event):
                self.events_received.append(event)
            
            @property
            def subscribed_event_types(self):
                return {"test_event"}
        
        subscriber = MockSubscriber()
        await manager.register_subscriber(subscriber)
        
        # Create a logger
        logger = EventLogger(log_to_memory=True, log_to_file=False, log_to_logger=False)
        await manager.register_logger(logger)
        
        # Shut down the manager
        await manager.shutdown()
        
        # Emit an event (should not be delivered)
        event = Event(event_type="test_event", source="test_source")
        delivery_count = await manager.emit(event)
        
        self.assertEqual(delivery_count, 0)
        self.assertEqual(len(subscriber.events_received), 0)


class TestEventVisualizer(unittest.IsolatedAsyncioTestCase):
    """Tests for the EventVisualizer class."""
    
    async def test_process_event(self):
        """Test processing an event for visualization."""
        visualizer = EventVisualizer()
        
        event = Event(event_type="test_event", source="test_source")
        await visualizer.process_event(event)
        
        data = visualizer.get_visualization_data()
        self.assertEqual(len(data["events"]), 1)
        self.assertEqual(data["events"][0]["type"], "test_event")
        self.assertEqual(data["events"][0]["source"], "test_source")
    
    async def test_parent_child_relationship(self):
        """Test visualizing parent-child relationships."""
        visualizer = EventVisualizer()
        
        parent = Event(event_type="parent_event", source="test_source")
        child = Event(
            event_type="child_event",
            source="test_source",
            parent_id=parent.id
        )
        
        await visualizer.process_event(parent)
        await visualizer.process_event(child)
        
        data = visualizer.get_visualization_data()
        self.assertEqual(len(data["events"]), 2)
        self.assertEqual(len(data["relationships"]), 1)
        self.assertEqual(data["relationships"][0]["from"], parent.id)
        self.assertEqual(data["relationships"][0]["to"], child.id)
    
    async def test_generate_mermaid_diagram(self):
        """Test generating a Mermaid diagram."""
        visualizer = EventVisualizer()
        
        parent = Event(event_type="parent_event", source="test_source")
        child = Event(
            event_type="child_event",
            source="test_source",
            parent_id=parent.id
        )
        
        await visualizer.process_event(parent)
        await visualizer.process_event(child)
        
        diagram = visualizer.generate_event_flow_diagram(format="mermaid")
        self.assertIn("graph TD;", diagram)
        self.assertIn("parent_event", diagram)
        self.assertIn("child_event", diagram)
        self.assertIn("-->", diagram)
    
    async def test_generate_dot_diagram(self):
        """Test generating a DOT diagram."""
        visualizer = EventVisualizer()
        
        parent = Event(event_type="parent_event", source="test_source")
        child = Event(
            event_type="child_event",
            source="test_source",
            parent_id=parent.id
        )
        
        await visualizer.process_event(parent)
        await visualizer.process_event(child)
        
        diagram = visualizer.generate_event_flow_diagram(format="dot")
        self.assertIn("digraph EventFlow {", diagram)
        self.assertIn("parent_event", diagram)
        self.assertIn("child_event", diagram)
        self.assertIn("->", diagram)
    
    async def test_generate_timeline(self):
        """Test generating an event timeline."""
        visualizer = EventVisualizer()
        
        event1 = Event(event_type="event1", source="test_source")
        # Wait a bit to ensure different timestamps
        await asyncio.sleep(0.01)
        event2 = Event(event_type="event2", source="test_source")
        
        await visualizer.process_event(event1)
        await visualizer.process_event(event2)
        
        timeline = visualizer.generate_event_timeline()
        self.assertIn("Event Timeline:", timeline)
        self.assertIn("event1", timeline)
        self.assertIn("event2", timeline)
    
    async def test_generate_statistics(self):
        """Test generating event statistics."""
        visualizer = EventVisualizer()
        
        event1 = Event(event_type="type1", source="source1", priority=EventPriority.LOW)
        event2 = Event(event_type="type2", source="source2", priority=EventPriority.HIGH)
        event3 = Event(event_type="type1", source="source1", priority=EventPriority.NORMAL)
        
        await visualizer.process_event(event1)
        await visualizer.process_event(event2)
        await visualizer.process_event(event3)
        
        stats = visualizer.generate_event_statistics()
        self.assertIn("Event Statistics:", stats)
        self.assertIn("Total Events: 3", stats)
        self.assertIn("Unique Event Types: 2", stats)
        self.assertIn("Unique Sources: 2", stats)
        self.assertIn("type1: 2", stats)
        self.assertIn("type2: 1", stats)
        self.assertIn("source1: 2", stats)
        self.assertIn("source2: 1", stats)
    
    async def test_clear_visualization_data(self):
        """Test clearing visualization data."""
        visualizer = EventVisualizer()
        
        event = Event(event_type="test_event", source="test_source")
        await visualizer.process_event(event)
        
        data = visualizer.get_visualization_data()
        self.assertEqual(len(data["events"]), 1)
        
        visualizer.clear_visualization_data()
        
        data = visualizer.get_visualization_data()
        self.assertEqual(len(data["events"]), 0)


if __name__ == "__main__":
    unittest.main()
