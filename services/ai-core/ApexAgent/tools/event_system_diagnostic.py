#!/usr/bin/env python3
"""
Minimal diagnostic script for event emission and subscription.

This script provides a minimal, standalone example of event emission and
subscription to diagnose issues with the event system outside of unittest.
"""

import asyncio
import logging
import sys
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Union

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)

logger = logging.getLogger("event_diagnostic")

# Import event system components
sys.path.append('/home/ubuntu/agent_project')
from src.core.event_system.event import Event, EventPriority
from src.core.event_system.event_manager import EventManager
from src.core.event_system.event_subscriber import EventSubscriber, CallbackEventSubscriber


async def test_direct_callback():
    """Test registering a callback directly."""
    logger.info("=== Testing direct callback registration ===")
    
    # Create event manager
    event_manager = EventManager()
    
    # Create a list to store received events
    events_received = []
    
    # Define a callback function
    async def handle_event(event):
        logger.info(f"Callback received event: {event.event_type}")
        events_received.append(event)
    
    # Register the callback
    logger.info("Registering callback")
    await event_manager.register_callback(
        handle_event,
        event_types="test.event"
    )
    
    # Log registered subscribers
    subscribers_str = ", ".join([
        f"{s.__class__.__name__}({s.subscribed_event_types})" 
        for s in event_manager._subscribers
    ])
    logger.info(f"Registered subscribers: {subscribers_str}")
    
    # Create and emit an event
    event = Event(
        event_type="test.event",
        source="test",
        data={"message": "Test message"}
    )
    
    logger.info(f"Emitting event: {event.event_type}")
    delivery_count = await event_manager.emit(event)
    logger.info(f"Event delivered to {delivery_count} subscribers")
    
    # Wait for event processing to complete
    await asyncio.sleep(0.5)
    
    # Check that the event was received
    logger.info(f"Events received: {len(events_received)}")
    if len(events_received) > 0:
        logger.info(f"Event type: {events_received[0].event_type}")
    else:
        logger.error("No events received!")


async def test_sync_callback():
    """Test registering a synchronous callback."""
    logger.info("=== Testing synchronous callback registration ===")
    
    # Create event manager
    event_manager = EventManager()
    
    # Create a list to store received events
    events_received = []
    
    # Define a synchronous callback function
    def handle_event(event):
        logger.info(f"Sync callback received event: {event.event_type}")
        events_received.append(event)
    
    # Register the callback
    logger.info("Registering sync callback")
    await event_manager.register_callback(
        handle_event,
        event_types="test.event"
    )
    
    # Log registered subscribers
    subscribers_str = ", ".join([
        f"{s.__class__.__name__}({s.subscribed_event_types})" 
        for s in event_manager._subscribers
    ])
    logger.info(f"Registered subscribers: {subscribers_str}")
    
    # Create and emit an event
    event = Event(
        event_type="test.event",
        source="test",
        data={"message": "Test message"}
    )
    
    logger.info(f"Emitting event: {event.event_type}")
    delivery_count = await event_manager.emit(event)
    logger.info(f"Event delivered to {delivery_count} subscribers")
    
    # Wait for event processing to complete
    await asyncio.sleep(0.5)
    
    # Check that the event was received
    logger.info(f"Events received: {len(events_received)}")
    if len(events_received) > 0:
        logger.info(f"Event type: {events_received[0].event_type}")
    else:
        logger.error("No events received!")


async def test_wildcard_subscription():
    """Test subscribing to events with wildcards."""
    logger.info("=== Testing wildcard subscription ===")
    
    # Create event manager
    event_manager = EventManager()
    
    # Create a list to store received events
    events_received = []
    
    # Define a callback function
    async def handle_event(event):
        logger.info(f"Wildcard callback received event: {event.event_type}")
        events_received.append(event)
    
    # Register the callback with a wildcard
    logger.info("Registering callback with wildcard")
    await event_manager.register_callback(
        handle_event,
        event_types="test.*"
    )
    
    # Log registered subscribers
    subscribers_str = ", ".join([
        f"{s.__class__.__name__}({s.subscribed_event_types})" 
        for s in event_manager._subscribers
    ])
    logger.info(f"Registered subscribers: {subscribers_str}")
    
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
    
    logger.info(f"Emitting event: {event1.event_type}")
    delivery_count = await event_manager.emit(event1)
    logger.info(f"Event delivered to {delivery_count} subscribers")
    
    logger.info(f"Emitting event: {event2.event_type}")
    delivery_count = await event_manager.emit(event2)
    logger.info(f"Event delivered to {delivery_count} subscribers")
    
    logger.info(f"Emitting event: {event3.event_type}")
    delivery_count = await event_manager.emit(event3)
    logger.info(f"Event delivered to {delivery_count} subscribers")
    
    # Wait for event processing to complete
    await asyncio.sleep(0.5)
    
    # Check that the events were received
    logger.info(f"Events received: {len(events_received)}")
    for i, event in enumerate(events_received):
        logger.info(f"Event {i+1} type: {event.event_type}")


async def test_custom_subscriber():
    """Test registering a custom subscriber class."""
    logger.info("=== Testing custom subscriber class ===")
    
    # Create event manager
    event_manager = EventManager()
    
    # Create a list to store received events
    events_received = []
    
    # Define a subscriber class
    class TestSubscriber(EventSubscriber):
        @property
        def subscribed_event_types(self):
            return {"test.event"}
        
        def matches_event(self, event):
            logger.info(f"Checking if event {event.event_type} matches subscribed types {self.subscribed_event_types}")
            return event.event_type in self.subscribed_event_types
        
        async def handle_event(self, event):
            logger.info(f"Subscriber received event: {event.event_type}")
            events_received.append(event)
    
    # Create and register the subscriber
    subscriber = TestSubscriber()
    
    logger.info("Registering subscriber")
    await event_manager.register_subscriber(subscriber)
    
    # Log registered subscribers
    subscribers_str = ", ".join([
        f"{s.__class__.__name__}({s.subscribed_event_types})" 
        for s in event_manager._subscribers
    ])
    logger.info(f"Registered subscribers: {subscribers_str}")
    
    # Create and emit an event
    event = Event(
        event_type="test.event",
        source="test",
        data={"message": "Test message"}
    )
    
    logger.info(f"Emitting event: {event.event_type}")
    delivery_count = await event_manager.emit(event)
    logger.info(f"Event delivered to {delivery_count} subscribers")
    
    # Wait for event processing to complete
    await asyncio.sleep(0.5)
    
    # Check that the event was received
    logger.info(f"Events received: {len(events_received)}")
    if len(events_received) > 0:
        logger.info(f"Event type: {events_received[0].event_type}")
    else:
        logger.error("No events received!")


async def main():
    """Run all tests."""
    logger.info("Starting event system diagnostic tests")
    
    await test_direct_callback()
    await test_sync_callback()
    await test_wildcard_subscription()
    await test_custom_subscriber()
    
    logger.info("All tests completed")


if __name__ == "__main__":
    asyncio.run(main())
