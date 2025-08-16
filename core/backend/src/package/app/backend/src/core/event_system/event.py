"""
Event class for the ApexAgent event system.

This module defines the Event class and related enumerations used throughout
the event system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional, Union
import uuid


class EventPriority(Enum):
    """Priority levels for events."""
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class Event:
    """
    Base class for all events in the ApexAgent system.
    
    Events are immutable data objects that represent something that happened
    in the system. They contain information about what happened, when it happened,
    and any relevant data.
    
    Attributes:
        event_type: String identifier for the event type
        source: Identifier of the component that emitted the event
        timestamp: When the event was created
        priority: Priority level of the event
        data: Dictionary containing event-specific data
        id: Unique identifier for this event instance
        parent_id: Optional ID of a parent event that caused this event
        metadata: Optional dictionary for additional metadata
    """
    event_type: str
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the event after initialization."""
        if not self.event_type:
            raise ValueError("Event type cannot be empty")
        if not self.source:
            raise ValueError("Event source cannot be empty")
    
    def with_parent(self, parent_event: Union['Event', str]) -> 'Event':
        """
        Create a new event with this event as a child of the specified parent.
        
        Args:
            parent_event: Either an Event object or a string event ID
            
        Returns:
            A new Event instance with the parent_id set
        """
        parent_id = parent_event.id if isinstance(parent_event, Event) else parent_event
        return Event(
            event_type=self.event_type,
            source=self.source,
            data=self.data.copy(),
            priority=self.priority,
            timestamp=self.timestamp,
            parent_id=parent_id,
            metadata=self.metadata.copy()
        )
    
    def with_metadata(self, **kwargs) -> 'Event':
        """
        Create a new event with additional metadata.
        
        Args:
            **kwargs: Key-value pairs to add to metadata
            
        Returns:
            A new Event instance with updated metadata
        """
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return Event(
            event_type=self.event_type,
            source=self.source,
            data=self.data.copy(),
            priority=self.priority,
            timestamp=self.timestamp,
            parent_id=self.parent_id,
            metadata=new_metadata
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "id": self.id,
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.name,
            "data": self.data,
            "parent_id": self.parent_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """
        Create an Event instance from a dictionary.
        
        Args:
            data: Dictionary containing event data
            
        Returns:
            New Event instance
        """
        # Convert string priority back to enum
        priority_str = data.pop("priority", EventPriority.NORMAL.name)
        priority = EventPriority[priority_str] if isinstance(priority_str, str) else priority_str
        
        # Convert ISO timestamp string back to datetime
        timestamp_str = data.pop("timestamp", datetime.now().isoformat())
        timestamp = datetime.fromisoformat(timestamp_str) if isinstance(timestamp_str, str) else timestamp_str
        
        return cls(
            **{k: v for k, v in data.items() if k in cls.__annotations__},
            priority=priority,
            timestamp=timestamp
        )
