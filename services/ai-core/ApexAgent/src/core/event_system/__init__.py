"""
ApexAgent Event System

This package provides an extensible event system for the ApexAgent platform, enabling:
1. Event emission and subscription
2. Event logging and replay
3. Event-driven architecture for plugin communication
4. Event visualization for debugging

The event system is designed to be modular, extensible, and to support both synchronous
and asynchronous event handling.
"""

from .event_manager import EventManager
from .event import Event, EventPriority
from .event_subscriber import EventSubscriber
from .event_logger import EventLogger

__all__ = [
    'EventManager',
    'Event',
    'EventPriority',
    'EventSubscriber',
    'EventLogger',
]
