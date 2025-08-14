"""
EventManager for the ApexAgent event system.

This module provides the central event management functionality, including
event emission, subscription management, and event distribution.
"""

import asyncio
import logging
import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Union
import weakref

from .event import Event, EventPriority
from .event_subscriber import EventSubscriber, CallbackEventSubscriber
from .event_logger import EventLogger


class EventManager:
    """
    Central manager for the event system.
    
    The EventManager is responsible for:
    - Registering and unregistering event subscribers
    - Emitting events to appropriate subscribers
    - Managing event loggers
    - Providing utilities for working with events
    
    It supports both synchronous and asynchronous event handling.
    """
    
    def __init__(self):
        """Initialize a new EventManager."""
        self._subscribers: List[EventSubscriber] = []
        self._loggers: List[EventLogger] = []
        self._logger = logging.getLogger("apex_agent.event_manager")
        
        # Event statistics
        self._stats = {
            "events_emitted": 0,
            "events_delivered": 0,
            "subscribers_notified": 0
        }
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def register_subscriber(self, subscriber: EventSubscriber) -> None:
        """
        Register an event subscriber.
        
        Args:
            subscriber: The subscriber to register
        """
        async with self._lock:
            if subscriber not in self._subscribers:
                self._subscribers.append(subscriber)
                self._logger.debug(
                    f"Registered subscriber for event types: {subscriber.subscribed_event_types}"
                )
    
    async def unregister_subscriber(self, subscriber: EventSubscriber) -> bool:
        """
        Unregister an event subscriber.
        
        Args:
            subscriber: The subscriber to unregister
            
        Returns:
            True if the subscriber was found and removed, False otherwise
        """
        async with self._lock:
            if subscriber in self._subscribers:
                self._subscribers.remove(subscriber)
                self._logger.debug(
                    f"Unregistered subscriber for event types: {subscriber.subscribed_event_types}"
                )
                return True
            return False
    
    async def register_callback(
        self,
        callback: Callable[[Event], Any],
        event_types: Union[str, List[str], Set[str], Pattern],
        priority_filter: Optional[Set[EventPriority]] = None,
        source_filter: Optional[Union[Set[str], Pattern]] = None
    ) -> CallbackEventSubscriber:
        """
        Register a callback function as an event subscriber.
        
        This is a convenience method that creates a CallbackEventSubscriber
        and registers it.
        
        Args:
            callback: Function to call when an event is received
            event_types: Event type(s) to subscribe to
            priority_filter: Optional set of priorities to filter by
            source_filter: Optional set of sources or pattern to filter by
            
        Returns:
            The created CallbackEventSubscriber
        """
        subscriber = CallbackEventSubscriber(
            callback=callback,
            event_types=event_types,
            priority_filter=priority_filter,
            source_filter=source_filter
        )
        await self.register_subscriber(subscriber)
        return subscriber
    
    async def register_logger(self, logger: EventLogger) -> None:
        """
        Register an event logger.
        
        Args:
            logger: The logger to register
        """
        async with self._lock:
            if logger not in self._loggers:
                self._loggers.append(logger)
                self._logger.debug("Registered event logger")
    
    async def unregister_logger(self, logger: EventLogger) -> bool:
        """
        Unregister an event logger.
        
        Args:
            logger: The logger to unregister
            
        Returns:
            True if the logger was found and removed, False otherwise
        """
        async with self._lock:
            if logger in self._loggers:
                self._loggers.remove(logger)
                self._logger.debug("Unregistered event logger")
                return True
            return False
    
    def _matches_wildcard(self, event_type: str, pattern: str) -> bool:
        """
        Check if an event type matches a wildcard pattern.
        
        Args:
            event_type: The event type to check
            pattern: The wildcard pattern (e.g., "event.*")
            
        Returns:
            True if the event type matches the pattern, False otherwise
        """
        if pattern.endswith(".*"):
            # Check if event_type starts with the prefix before the wildcard
            prefix = pattern[:-1]  # Remove the '*'
            return event_type.startswith(prefix)
        return event_type == pattern
    
    async def emit(self, event: Event) -> int:
        """
        Emit an event to all matching subscribers.
        
        Args:
            event: The event to emit
            
        Returns:
            Number of subscribers the event was delivered to
        """
        async with self._lock:
            self._stats["events_emitted"] += 1
            
            # Log the event with all registered loggers
            for logger in self._loggers:
                try:
                    await logger.log_event(event)
                except Exception as e:
                    self._logger.error(f"Error logging event: {e}")
            
            # Find matching subscribers
            matching_subscribers = []
            for subscriber in self._subscribers:
                try:
                    if subscriber.matches_event(event):
                        matching_subscribers.append(subscriber)
                except Exception as e:
                    self._logger.error(f"Error checking if subscriber matches event: {e}")
            
            self._logger.debug(f"Found {len(matching_subscribers)} matching subscribers for event {event.event_type}")
            
            # Deliver the event to each matching subscriber
            delivery_count = 0
            for subscriber in matching_subscribers:
                try:
                    # Handle both async and sync callbacks
                    result = subscriber.handle_event(event)
                    if asyncio.iscoroutine(result):
                        await result
                    delivery_count += 1
                    self._logger.debug(f"Successfully delivered event {event.event_type} to subscriber")
                except Exception as e:
                    self._logger.error(f"Error delivering event to subscriber: {e}")
            
            self._stats["events_delivered"] += 1
            self._stats["subscribers_notified"] += delivery_count
            
            return delivery_count
    
    def create_event(
        self,
        event_type: str,
        source: str,
        data: Optional[Dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        Create a new event.
        
        This is a convenience method for creating events with the current timestamp.
        
        Args:
            event_type: String identifier for the event type
            source: Identifier of the component emitting the event
            data: Dictionary containing event-specific data
            priority: Priority level of the event
            parent_id: Optional ID of a parent event
            metadata: Optional dictionary for additional metadata
            
        Returns:
            A new Event instance
        """
        return Event(
            event_type=event_type,
            source=source,
            data=data or {},
            priority=priority,
            parent_id=parent_id,
            metadata=metadata or {}
        )
    
    async def emit_new(
        self,
        event_type: str,
        source: str,
        data: Optional[Dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        Create and emit a new event.
        
        This is a convenience method that combines create_event and emit.
        
        Args:
            event_type: String identifier for the event type
            source: Identifier of the component emitting the event
            data: Dictionary containing event-specific data
            priority: Priority level of the event
            parent_id: Optional ID of a parent event
            metadata: Optional dictionary for additional metadata
            
        Returns:
            The emitted Event instance
        """
        event = self.create_event(
            event_type=event_type,
            source=source,
            data=data,
            priority=priority,
            parent_id=parent_id,
            metadata=metadata
        )
        await self.emit(event)
        return event
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about event processing.
        
        Returns:
            Dictionary of statistics
        """
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset event statistics."""
        self._stats = {
            "events_emitted": 0,
            "events_delivered": 0,
            "subscribers_notified": 0
        }
    
    async def shutdown(self) -> None:
        """
        Shut down the event manager.
        
        This closes all loggers and clears subscribers.
        """
        async with self._lock:
            # Close all loggers
            for logger in self._loggers:
                logger.close()
            
            # Clear subscribers and loggers
            self._subscribers.clear()
            self._loggers.clear()
            
            self._logger.info("Event manager shut down")
            
    # Adding compatibility methods for plugin system
    
    def emit_event(self, event: Event) -> int:
        """
        Synchronous wrapper for emit method to maintain compatibility with plugin system.
        
        Args:
            event: The event to emit
            
        Returns:
            Number of subscribers the event was delivered to
        """
        # Create a new event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Run the async emit method in the event loop
        if loop.is_running():
            # If the loop is already running, create a future and run it
            future = asyncio.run_coroutine_threadsafe(self.emit(event), loop)
            return future.result()
        else:
            # If the loop is not running, run the coroutine directly
            return loop.run_until_complete(self.emit(event))
    
    def subscribe(
        self,
        event_type: Union[str, List[str], Set[str], Pattern],
        callback: Callable[[Event], Any],
        priority_filter: Optional[Set[EventPriority]] = None,
        source_filter: Optional[Union[Set[str], Pattern]] = None,
        priority: Optional[int] = None  # Added priority parameter for test compatibility
    ) -> CallbackEventSubscriber:
        """
        Synchronous wrapper for register_callback method to maintain compatibility with plugin system.
        
        Args:
            event_type: Event type(s) to subscribe to
            callback: Function to call when an event is received
            priority_filter: Optional set of priorities to filter by
            source_filter: Optional set of sources or pattern to filter by
            priority: Optional priority value for subscription (ignored, kept for compatibility)
            
        Returns:
            The created CallbackEventSubscriber
        """
        # Create a new event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Run the async register_callback method in the event loop
        if loop.is_running():
            # If the loop is already running, create a future and run it
            future = asyncio.run_coroutine_threadsafe(
                self.register_callback(callback, event_type, priority_filter, source_filter),
                loop
            )
            return future.result()
        else:
            # If the loop is not running, run the coroutine directly
            return loop.run_until_complete(
                self.register_callback(callback, event_type, priority_filter, source_filter)
            )
    
    def unsubscribe(self, subscriber: EventSubscriber) -> bool:
        """
        Synchronous wrapper for unregister_subscriber method to maintain compatibility with plugin system.
        
        Args:
            subscriber: The subscriber to unregister
            
        Returns:
            True if the subscriber was found and removed, False otherwise
        """
        # Create a new event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Run the async unregister_subscriber method in the event loop
        if loop.is_running():
            # If the loop is already running, create a future and run it
            future = asyncio.run_coroutine_threadsafe(
                self.unregister_subscriber(subscriber),
                loop
            )
            return future.result()
        else:
            # If the loop is not running, run the coroutine directly
            return loop.run_until_complete(self.unregister_subscriber(subscriber))
