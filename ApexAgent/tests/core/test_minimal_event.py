"""
Minimal test for event emission and subscription.

This module provides a minimal test case for isolating event emission
and subscription issues in the event system.
"""

import asyncio
import logging
import sys
import unittest

from src.core.event_system.event import Event, EventPriority
from src.core.event_system.event_manager import EventManager
from src.core.event_system.event_subscriber import EventSubscriber, CallbackEventSubscriber

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)


class MinimalEventTest(unittest.IsolatedAsyncioTestCase):
    """Minimal test for event emission and subscription."""
    
    async def asyncSetUp(self):
        """Set up the test."""
        self.event_manager = EventManager()
        self.logger = logging.getLogger("minimal_event_test")
        self.logger.debug("Test setup complete")
    
    async def test_direct_callback_registration(self):
        """Test registering a callback directly."""
        # Create a list to store received events
        events_received = []
        
        # Define a callback function
        async def handle_event(event):
            self.logger.debug(f"Callback received event: {event.event_type}")
            events_received.append(event)
        
        # Register the callback
        self.logger.debug("Registering callback")
        await self.event_manager.register_callback(
            handle_event,
            event_types="test.event"
        )
        
        # Log registered subscribers
        subscribers_str = ", ".join([
            f"{s.__class__.__name__}({s.subscribed_event_types})" 
            for s in self.event_manager._subscribers
        ])
        self.logger.debug(f"Registered subscribers: {subscribers_str}")
        
        # Create and emit an event
        event = Event(
            event_type="test.event",
            source="test",
            data={"message": "Test message"}
        )
        
        self.logger.debug(f"Emitting event: {event.event_type}")
        delivery_count = await self.event_manager.emit(event)
        self.logger.debug(f"Event delivered to {delivery_count} subscribers")
        
        # Wait for event processing to complete
        await asyncio.sleep(0.5)
        
        # Check that the event was received
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].event_type, "test.event")
    
    async def test_subscriber_class_registration(self):
        """Test registering a subscriber class."""
        # Create a list to store received events
        events_received = []
        
        # Define a subscriber class
        class TestSubscriber(EventSubscriber):
            @property
            def subscribed_event_types(self):
                return {"test.event"}
            
            def matches_event(self, event):
                return event.event_type in self.subscribed_event_types
            
            async def handle_event(self, event):
                self.logger.debug(f"Subscriber received event: {event.event_type}")
                events_received.append(event)
        
        # Create and register the subscriber
        subscriber = TestSubscriber()
        subscriber.logger = self.logger
        
        self.logger.debug("Registering subscriber")
        await self.event_manager.register_subscriber(subscriber)
        
        # Log registered subscribers
        subscribers_str = ", ".join([
            f"{s.__class__.__name__}({s.subscribed_event_types})" 
            for s in self.event_manager._subscribers
        ])
        self.logger.debug(f"Registered subscribers: {subscribers_str}")
        
        # Create and emit an event
        event = Event(
            event_type="test.event",
            source="test",
            data={"message": "Test message"}
        )
        
        self.logger.debug(f"Emitting event: {event.event_type}")
        delivery_count = await self.event_manager.emit(event)
        self.logger.debug(f"Event delivered to {delivery_count} subscribers")
        
        # Wait for event processing to complete
        await asyncio.sleep(0.5)
        
        # Check that the event was received
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].event_type, "test.event")
    
    async def test_sync_callback_registration(self):
        """Test registering a synchronous callback."""
        # Create a list to store received events
        events_received = []
        
        # Define a synchronous callback function
        def handle_event(event):
            self.logger.debug(f"Sync callback received event: {event.event_type}")
            events_received.append(event)
        
        # Register the callback
        self.logger.debug("Registering sync callback")
        await self.event_manager.register_callback(
            handle_event,
            event_types="test.event"
        )
        
        # Log registered subscribers
        subscribers_str = ", ".join([
            f"{s.__class__.__name__}({s.subscribed_event_types})" 
            for s in self.event_manager._subscribers
        ])
        self.logger.debug(f"Registered subscribers: {subscribers_str}")
        
        # Create and emit an event
        event = Event(
            event_type="test.event",
            source="test",
            data={"message": "Test message"}
        )
        
        self.logger.debug(f"Emitting event: {event.event_type}")
        delivery_count = await self.event_manager.emit(event)
        self.logger.debug(f"Event delivered to {delivery_count} subscribers")
        
        # Wait for event processing to complete
        await asyncio.sleep(0.5)
        
        # Check that the event was received
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].event_type, "test.event")
    
    async def test_multiple_subscribers(self):
        """Test registering multiple subscribers."""
        # Create lists to store received events
        events_received_1 = []
        events_received_2 = []
        
        # Define callback functions
        async def handle_event_1(event):
            self.logger.debug(f"Callback 1 received event: {event.event_type}")
            events_received_1.append(event)
        
        async def handle_event_2(event):
            self.logger.debug(f"Callback 2 received event: {event.event_type}")
            events_received_2.append(event)
        
        # Register the callbacks
        self.logger.debug("Registering callbacks")
        await self.event_manager.register_callback(
            handle_event_1,
            event_types="test.event"
        )
        await self.event_manager.register_callback(
            handle_event_2,
            event_types="test.event"
        )
        
        # Log registered subscribers
        subscribers_str = ", ".join([
            f"{s.__class__.__name__}({s.subscribed_event_types})" 
            for s in self.event_manager._subscribers
        ])
        self.logger.debug(f"Registered subscribers: {subscribers_str}")
        
        # Create and emit an event
        event = Event(
            event_type="test.event",
            source="test",
            data={"message": "Test message"}
        )
        
        self.logger.debug(f"Emitting event: {event.event_type}")
        delivery_count = await self.event_manager.emit(event)
        self.logger.debug(f"Event delivered to {delivery_count} subscribers")
        
        # Wait for event processing to complete
        await asyncio.sleep(0.5)
        
        # Check that the event was received by both subscribers
        self.assertEqual(len(events_received_1), 1)
        self.assertEqual(events_received_1[0].event_type, "test.event")
        self.assertEqual(len(events_received_2), 1)
        self.assertEqual(events_received_2[0].event_type, "test.event")
    
    async def test_wildcard_subscription(self):
        """Test subscribing to events with wildcards."""
        # Create a list to store received events
        events_received = []
        
        # Define a callback function
        async def handle_event(event):
            self.logger.debug(f"Callback received event: {event.event_type}")
            events_received.append(event)
        
        # Register the callback with a wildcard
        self.logger.debug("Registering callback with wildcard")
        await self.event_manager.register_callback(
            handle_event,
            event_types="test.*"
        )
        
        # Log registered subscribers
        subscribers_str = ", ".join([
            f"{s.__class__.__name__}({s.subscribed_event_types})" 
            for s in self.event_manager._subscribers
        ])
        self.logger.debug(f"Registered subscribers: {subscribers_str}")
        
        # Create and emit events
        event1 = Event(
            event_type="test.event1",
            source="test",
            data={"message": "Test message 1"}
        )
        
        event2 = Event(
            event_type="test.event2",
            source="test",
            data={"message": "Test message 2"}
        )
        
        event3 = Event(
            event_type="other.event",
            source="test",
            data={"message": "Test message 3"}
        )
        
        self.logger.debug(f"Emitting event: {event1.event_type}")
        delivery_count = await self.event_manager.emit(event1)
        self.logger.debug(f"Event delivered to {delivery_count} subscribers")
        
        self.logger.debug(f"Emitting event: {event2.event_type}")
        delivery_count = await self.event_manager.emit(event2)
        self.logger.debug(f"Event delivered to {delivery_count} subscribers")
        
        self.logger.debug(f"Emitting event: {event3.event_type}")
        delivery_count = await self.event_manager.emit(event3)
        self.logger.debug(f"Event delivered to {delivery_count} subscribers")
        
        # Wait for event processing to complete
        await asyncio.sleep(0.5)
        
        # Check that only the matching events were received
        self.assertEqual(len(events_received), 2)
        self.assertEqual(events_received[0].event_type, "test.event1")
        self.assertEqual(events_received[1].event_type, "test.event2")


if __name__ == "__main__":
    unittest.main()
