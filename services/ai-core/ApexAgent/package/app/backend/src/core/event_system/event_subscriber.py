"""
EventSubscriber interface for the ApexAgent event system.

This module defines the EventSubscriber protocol and related functionality
for subscribing to and handling events.
"""

from abc import ABC, abstractmethod
import asyncio
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Union
import re

from .event import Event, EventPriority


class EventSubscriber(ABC):
    """
    Abstract base class for event subscribers.
    
    Event subscribers receive events from the EventManager when events matching
    their subscription criteria are emitted.
    """
    
    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        """
        Handle an event that matches this subscriber's criteria.
        
        Args:
            event: The event to handle
        """
        pass
    
    @property
    @abstractmethod
    def subscribed_event_types(self) -> Union[Set[str], List[str], Pattern]:
        """
        Get the event types this subscriber is interested in.
        
        Returns:
            A set of event type strings, a list of event type strings, or a regex pattern
            that matches event types
        """
        pass
    
    @property
    def priority_filter(self) -> Optional[Set[EventPriority]]:
        """
        Get the event priorities this subscriber is interested in.
        
        Returns:
            A set of EventPriority values, or None to accept all priorities
        """
        return None
    
    @property
    def source_filter(self) -> Optional[Union[Set[str], Pattern]]:
        """
        Get the event sources this subscriber is interested in.
        
        Returns:
            A set of source strings, a regex pattern that matches sources,
            or None to accept all sources
        """
        return None
    
    def matches_event(self, event: Event) -> bool:
        """
        Check if an event matches this subscriber's criteria.
        
        Args:
            event: The event to check
            
        Returns:
            True if the event matches, False otherwise
        """
        # Check event type
        event_types = self.subscribed_event_types
        if isinstance(event_types, (set, list)):
            # Check for exact match
            if event.event_type in event_types:
                return self._check_filters(event)
                
            # Check for wildcard match
            for event_type in event_types:
                if event_type.endswith(".*") and event.event_type.startswith(event_type[:-1]):
                    return self._check_filters(event)
                    
            return False
        elif isinstance(event_types, Pattern):
            if not event_types.match(event.event_type):
                return False
        
        return self._check_filters(event)
    
    def _check_filters(self, event: Event) -> bool:
        """
        Check if an event matches this subscriber's priority and source filters.
        
        Args:
            event: The event to check
            
        Returns:
            True if the event matches, False otherwise
        """
        # Check priority if filter is set
        priority_filter = self.priority_filter
        if priority_filter is not None and event.priority not in priority_filter:
            return False
        
        # Check source if filter is set
        source_filter = self.source_filter
        if source_filter is not None:
            if isinstance(source_filter, set):
                if event.source not in source_filter:
                    return False
            elif isinstance(source_filter, Pattern):
                if not source_filter.match(event.source):
                    return False
        
        return True


class CallbackEventSubscriber(EventSubscriber):
    """
    A simple event subscriber that calls a function when an event is received.
    
    This class provides a convenient way to subscribe to events without creating
    a full EventSubscriber subclass.
    """
    
    def __init__(
        self, 
        callback: Callable[[Event], Any],
        event_types: Union[str, List[str], Set[str], Pattern],
        priority_filter: Optional[Set[EventPriority]] = None,
        source_filter: Optional[Union[Set[str], Pattern]] = None
    ):
        """
        Initialize a new CallbackEventSubscriber.
        
        Args:
            callback: Function to call when an event is received
            event_types: Event type(s) to subscribe to
            priority_filter: Optional set of priorities to filter by
            source_filter: Optional set of sources or pattern to filter by
        """
        self._callback = callback
        
        # Convert single string to set
        if isinstance(event_types, str):
            self._event_types = {event_types}
        # Convert list to set for faster lookups
        elif isinstance(event_types, list):
            self._event_types = set(event_types)
        else:
            self._event_types = event_types
            
        self._priority_filter = priority_filter
        self._source_filter = source_filter
    
    async def handle_event(self, event: Event) -> None:
        """
        Handle an event by calling the callback function.
        
        Args:
            event: The event to handle
        """
        # Handle both async and sync callbacks
        if asyncio.iscoroutinefunction(self._callback):
            await self._callback(event)
        else:
            self._callback(event)
    
    @property
    def subscribed_event_types(self) -> Union[Set[str], Pattern]:
        """
        Get the event types this subscriber is interested in.
        
        Returns:
            A set of event type strings or a regex pattern
        """
        return self._event_types
    
    @property
    def priority_filter(self) -> Optional[Set[EventPriority]]:
        """
        Get the event priorities this subscriber is interested in.
        
        Returns:
            A set of EventPriority values, or None to accept all priorities
        """
        return self._priority_filter
    
    @property
    def source_filter(self) -> Optional[Union[Set[str], Pattern]]:
        """
        Get the event sources this subscriber is interested in.
        
        Returns:
            A set of source strings, a regex pattern, or None to accept all sources
        """
        return self._source_filter
