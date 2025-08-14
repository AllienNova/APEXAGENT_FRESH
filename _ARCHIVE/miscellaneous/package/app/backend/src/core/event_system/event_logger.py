"""
EventLogger for the ApexAgent event system.

This module provides functionality for logging, storing, and replaying events
for debugging, testing, and analysis purposes.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TextIO, Union

from .event import Event


class EventLogger:
    """
    Logger for events in the ApexAgent system.
    
    The EventLogger subscribes to events and logs them to various outputs,
    including files, memory, and standard logging. It also provides functionality
    for replaying logged events.
    """
    
    def __init__(
        self,
        log_to_file: bool = False,
        log_file_path: Optional[Union[str, Path]] = None,
        log_to_memory: bool = True,
        memory_limit: int = 1000,
        log_to_logger: bool = True,
        logger_name: str = "apex_agent.events",
        event_types_to_log: Optional[Set[str]] = None
    ):
        """
        Initialize a new EventLogger.
        
        Args:
            log_to_file: Whether to log events to a file
            log_file_path: Path to the log file (if log_to_file is True)
            log_to_memory: Whether to keep events in memory
            memory_limit: Maximum number of events to keep in memory
            log_to_logger: Whether to log events to a Python logger
            logger_name: Name of the Python logger to use
            event_types_to_log: Set of event types to log (None for all)
        """
        self._log_to_file = log_to_file
        self._log_file_path = Path(log_file_path) if log_file_path else None
        self._log_to_memory = log_to_memory
        self._memory_limit = memory_limit
        self._log_to_logger = log_to_logger
        self._logger = logging.getLogger(logger_name) if log_to_logger else None
        self._event_types_to_log = event_types_to_log
        
        # Memory storage for events
        self._events: List[Event] = []
        
        # File handle for log file
        self._log_file: Optional[TextIO] = None
        
        # Initialize log file if needed
        if self._log_to_file:
            self._initialize_log_file()
    
    def _initialize_log_file(self) -> None:
        """Initialize the log file with a header."""
        if not self._log_file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._log_file_path = Path(f"event_log_{timestamp}.jsonl")
        
        # Create parent directories if they don't exist
        self._log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file in append mode
        self._log_file = open(self._log_file_path, "a", encoding="utf-8")
        
        # Write a header with metadata
        header = {
            "type": "event_log_header",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
        self._log_file.write(json.dumps(header) + "\n")
        self._log_file.flush()
    
    async def log_event(self, event: Event) -> None:
        """
        Log an event.
        
        Args:
            event: The event to log
        """
        # Check if we should log this event type
        if self._event_types_to_log is not None and event.event_type not in self._event_types_to_log:
            return
        
        # Log to memory if enabled
        if self._log_to_memory:
            self._events.append(event)
            # Trim if we exceed the memory limit
            if len(self._events) > self._memory_limit:
                self._events = self._events[-self._memory_limit:]
        
        # Log to file if enabled
        if self._log_to_file and self._log_file:
            event_dict = event.to_dict()
            self._log_file.write(json.dumps(event_dict) + "\n")
            self._log_file.flush()
        
        # Log to Python logger if enabled
        if self._log_to_logger and self._logger:
            log_level = self._get_log_level_for_priority(event.priority)
            self._logger.log(
                log_level,
                f"Event: {event.event_type} from {event.source} - {json.dumps(event.data)}"
            )
    
    def _get_log_level_for_priority(self, priority) -> int:
        """
        Map event priority to Python logging level.
        
        Args:
            priority: Event priority
            
        Returns:
            Python logging level
        """
        from .event import EventPriority
        
        priority_to_level = {
            EventPriority.LOW: logging.DEBUG,
            EventPriority.NORMAL: logging.INFO,
            EventPriority.HIGH: logging.WARNING,
            EventPriority.CRITICAL: logging.ERROR
        }
        return priority_to_level.get(priority, logging.INFO)
    
    def get_events(self, limit: Optional[int] = None) -> List[Event]:
        """
        Get events from memory.
        
        Args:
            limit: Maximum number of events to return (None for all)
            
        Returns:
            List of events
        """
        if limit is None:
            return self._events.copy()
        return self._events[-limit:]
    
    def clear_memory(self) -> None:
        """Clear events from memory."""
        self._events = []
    
    async def replay_events(
        self, 
        events: Optional[List[Event]] = None, 
        callback: Optional[callable] = None,
        delay_factor: float = 1.0
    ) -> None:
        """
        Replay a sequence of events with their original timing.
        
        Args:
            events: List of events to replay (None to use stored events)
            callback: Function to call for each event
            delay_factor: Factor to apply to delays between events (1.0 = real time)
        """
        if events is None:
            events = self._events
        
        if not events:
            return
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        # Replay events with delays
        prev_time = sorted_events[0].timestamp
        for event in sorted_events:
            # Calculate delay based on time difference
            time_diff = (event.timestamp - prev_time).total_seconds()
            if time_diff > 0 and delay_factor > 0:
                await asyncio.sleep(time_diff * delay_factor)
            
            # Call the callback with the event
            if callback:
                await callback(event)
            
            prev_time = event.timestamp
    
    def close(self) -> None:
        """Close the logger and any open resources."""
        if self._log_file:
            self._log_file.close()
            self._log_file = None
    
    def __del__(self) -> None:
        """Ensure resources are closed when the object is garbage collected."""
        self.close()
