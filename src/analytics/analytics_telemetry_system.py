#!/usr/bin/env python3
"""
Analytics and Telemetry System for ApexAgent

This module provides a comprehensive analytics and telemetry system
for tracking usage, performance, and behavior of the ApexAgent platform.
It includes data collection, processing, storage, and visualization capabilities.
"""

import os
import sys
import time
import json
import uuid
import logging
import threading
import queue
import random
import hashlib
import socket
import platform
import psutil
import requests
import numpy as np
import pandas as pd
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, TypeVar, cast, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analytics.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("analytics")

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')

class EventType(Enum):
    """Enumeration of event types."""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    USER_ACTION = "user_action"
    SYSTEM_ACTION = "system_action"
    ERROR = "error"
    WARNING = "warning"
    PERFORMANCE = "performance"
    RESOURCE_USAGE = "resource_usage"
    FEATURE_USAGE = "feature_usage"
    TASK_START = "task_start"
    TASK_END = "task_end"
    TASK_PROGRESS = "task_progress"
    CUSTOM = "custom"

class EventCategory(Enum):
    """Enumeration of event categories."""
    USER = "user"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    ERROR = "error"
    FEATURE = "feature"
    TASK = "task"
    SECURITY = "security"
    NETWORK = "network"
    RESOURCE = "resource"
    CUSTOM = "custom"

class EventPriority(Enum):
    """Enumeration of event priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class StorageType(Enum):
    """Enumeration of storage types."""
    LOCAL = "local"
    REMOTE = "remote"
    BOTH = "both"
    NONE = "none"

class PrivacyLevel(Enum):
    """Enumeration of privacy levels."""
    PUBLIC = "public"           # No sensitive data
    INTERNAL = "internal"       # Internal use only
    RESTRICTED = "restricted"   # Restricted access
    SENSITIVE = "sensitive"     # Sensitive data
    CONFIDENTIAL = "confidential"  # Confidential data

@dataclass
class Event:
    """Event data structure."""
    event_id: str
    event_type: EventType
    category: EventCategory
    timestamp: datetime
    data: Dict[str, Any]
    session_id: str
    user_id: Optional[str] = None
    component: Optional[str] = None
    priority: EventPriority = EventPriority.MEDIUM
    privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "category": self.category.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "component": self.component,
            "priority": self.priority.value,
            "privacy_level": self.privacy_level.value,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create an event from a dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            category=EventCategory(data["category"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=data["data"],
            session_id=data["session_id"],
            user_id=data.get("user_id"),
            component=data.get("component"),
            priority=EventPriority(data.get("priority", "medium")),
            privacy_level=PrivacyLevel(data.get("privacy_level", "internal")),
            tags=data.get("tags", [])
        )

@dataclass
class Session:
    """Session data structure."""
    session_id: str
    start_time: datetime
    user_id: Optional[str] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    events: List[Event] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the session to a dictionary."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "user_id": self.user_id,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metadata": self.metadata,
            "events": [event.to_dict() for event in self.events]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create a session from a dictionary."""
        session = cls(
            session_id=data["session_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            user_id=data.get("user_id"),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            metadata=data.get("metadata", {})
        )
        
        if "events" in data:
            session.events = [Event.from_dict(event_data) for event_data in data["events"]]
        
        return session

@dataclass
class Metric:
    """Metric data structure."""
    metric_id: str
    name: str
    value: float
    timestamp: datetime
    unit: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    dimensions: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metric to a dictionary."""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "unit": self.unit,
            "tags": self.tags,
            "dimensions": self.dimensions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metric':
        """Create a metric from a dictionary."""
        return cls(
            metric_id=data["metric_id"],
            name=data["name"],
            value=data["value"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            unit=data.get("unit"),
            tags=data.get("tags", {}),
            dimensions=data.get("dimensions", {})
        )

@dataclass
class AnalyticsConfig:
    """Configuration for the analytics system."""
    enabled: bool = True
    storage_type: StorageType = StorageType.LOCAL
    local_storage_path: str = "analytics"
    remote_endpoint: Optional[str] = None
    remote_api_key: Optional[str] = None
    batch_size: int = 100
    flush_interval: int = 60  # seconds
    sampling_rate: float = 1.0  # 1.0 = 100%
    privacy_filter: Dict[str, List[str]] = field(default_factory=dict)
    include_system_info: bool = True
    include_performance_metrics: bool = True
    anonymize_user_data: bool = True
    max_event_age: int = 30  # days
    max_storage_size: int = 1024  # MB
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {
            "enabled": self.enabled,
            "storage_type": self.storage_type.value,
            "local_storage_path": self.local_storage_path,
            "remote_endpoint": self.remote_endpoint,
            "batch_size": self.batch_size,
            "flush_interval": self.flush_interval,
            "sampling_rate": self.sampling_rate,
            "privacy_filter": self.privacy_filter,
            "include_system_info": self.include_system_info,
            "include_performance_metrics": self.include_performance_metrics,
            "anonymize_user_data": self.anonymize_user_data,
            "max_event_age": self.max_event_age,
            "max_storage_size": self.max_storage_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalyticsConfig':
        """Create a configuration from a dictionary."""
        return cls(
            enabled=data.get("enabled", True),
            storage_type=StorageType(data.get("storage_type", "local")),
            local_storage_path=data.get("local_storage_path", "analytics"),
            remote_endpoint=data.get("remote_endpoint"),
            remote_api_key=data.get("remote_api_key"),
            batch_size=data.get("batch_size", 100),
            flush_interval=data.get("flush_interval", 60),
            sampling_rate=data.get("sampling_rate", 1.0),
            privacy_filter=data.get("privacy_filter", {}),
            include_system_info=data.get("include_system_info", True),
            include_performance_metrics=data.get("include_performance_metrics", True),
            anonymize_user_data=data.get("anonymize_user_data", True),
            max_event_age=data.get("max_event_age", 30),
            max_storage_size=data.get("max_storage_size", 1024)
        )

class EventCollector:
    """
    Event collector for collecting and processing events.
    
    This class provides functionality for collecting events from various
    sources and processing them before storage.
    """
    
    def __init__(self, config: AnalyticsConfig):
        """
        Initialize the event collector.
        
        Args:
            config: Analytics configuration
        """
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        self.event_queue = queue.Queue()
        self.event_processors: List[Callable[[Event], Optional[Event]]] = []
        self.event_filters: List[Callable[[Event], bool]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
    
    def start(self) -> None:
        """Start the event collector."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._thread = threading.Thread(target=self._process_events, daemon=True)
            self._thread.start()
            
            # Record session start event
            self.collect_event(
                event_type=EventType.SESSION_START,
                category=EventCategory.SYSTEM,
                data=self._get_system_info() if self.config.include_system_info else {}
            )
            
            logger.info("Event collector started")
    
    def stop(self) -> None:
        """Stop the event collector."""
        with self._lock:
            if not self._running:
                return
            
            # Record session end event
            self.collect_event(
                event_type=EventType.SESSION_END,
                category=EventCategory.SYSTEM,
                data={"duration": (datetime.now() - self.session_start_time).total_seconds()}
            )
            
            self._running = False
            if self._thread:
                self._thread.join(timeout=5.0)
                self._thread = None
            
            logger.info("Event collector stopped")
    
    def collect_event(self, event_type: EventType, category: EventCategory, data: Dict[str, Any],
                     user_id: Optional[str] = None, component: Optional[str] = None,
                     priority: EventPriority = EventPriority.MEDIUM,
                     privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL,
                     tags: Optional[List[str]] = None) -> str:
        """
        Collect an event.
        
        Args:
            event_type: Event type
            category: Event category
            data: Event data
            user_id: Optional user ID
            component: Optional component name
            priority: Event priority
            privacy_level: Privacy level
            tags: Optional tags
            
        Returns:
            str: Event ID
        """
        if not self.config.enabled:
            return ""
        
        # Apply sampling
        if self.config.sampling_rate < 1.0 and random.random() > self.config.sampling_rate:
            return ""
        
        # Create event
        event_id = str(uuid.uuid4())
        event = Event(
            event_id=event_id,
            event_type=event_type,
            category=category,
            timestamp=datetime.now(),
            data=data,
            session_id=self.session_id,
            user_id=self._anonymize_user_id(user_id) if self.config.anonymize_user_data and user_id else user_id,
            component=component,
            priority=priority,
            privacy_level=privacy_level,
            tags=tags or []
        )
        
        # Apply privacy filter
        event = self._apply_privacy_filter(event)
        
        # Add to queue
        self.event_queue.put(event)
        
        return event_id
    
    def add_event_processor(self, processor: Callable[[Event], Optional[Event]]) -> None:
        """
        Add an event processor.
        
        Args:
            processor: Event processor function
        """
        with self._lock:
            self.event_processors.append(processor)
    
    def add_event_filter(self, filter_func: Callable[[Event], bool]) -> None:
        """
        Add an event filter.
        
        Args:
            filter_func: Event filter function
        """
        with self._lock:
            self.event_filters.append(filter_func)
    
    def _process_events(self) -> None:
        """Process events from the queue."""
        while self._running:
            try:
                # Get event from queue with timeout
                try:
                    event = self.event_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Apply filters
                if not self._apply_filters(event):
                    self.event_queue.task_done()
                    continue
                
                # Apply processors
                processed_event = self._apply_processors(event)
                if not processed_event:
                    self.event_queue.task_done()
                    continue
                
                # Pass to storage manager
                # In a real implementation, this would pass the event to a storage manager
                # For this example, we'll just log it
                logger.debug(f"Processed event: {processed_event.event_id}")
                
                self.event_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing event: {str(e)}")
    
    def _apply_filters(self, event: Event) -> bool:
        """
        Apply filters to an event.
        
        Args:
            event: The event
            
        Returns:
            bool: True if the event passes all filters, False otherwise
        """
        for filter_func in self.event_filters:
            try:
                if not filter_func(event):
                    return False
            except Exception as e:
                logger.error(f"Error applying filter: {str(e)}")
        
        return True
    
    def _apply_processors(self, event: Event) -> Optional[Event]:
        """
        Apply processors to an event.
        
        Args:
            event: The event
            
        Returns:
            Optional[Event]: The processed event, or None if it should be dropped
        """
        processed_event = event
        
        for processor in self.event_processors:
            try:
                processed_event = processor(processed_event)
                if not processed_event:
                    return None
            except Exception as e:
                logger.error(f"Error applying processor: {str(e)}")
        
        return processed_event
    
    def _apply_privacy_filter(self, event: Event) -> Event:
        """
        Apply privacy filter to an event.
        
        Args:
            event: The event
            
        Returns:
            Event: The filtered event
        """
        # Clone the event data
        filtered_data = event.data.copy()
        
        # Apply privacy filter
        for field, patterns in self.config.privacy_filter.items():
            if field in filtered_data:
                value = filtered_data[field]
                if isinstance(value, str):
                    for pattern in patterns:
                        # Replace pattern with asterisks
                        filtered_data[field] = value.replace(pattern, '*' * len(pattern))
        
        # Create new event with filtered data
        return Event(
            event_id=event.event_id,
            event_type=event.event_type,
            category=event.category,
            timestamp=event.timestamp,
            data=filtered_data,
            session_id=event.session_id,
            user_id=event.user_id,
            component=event.component,
            priority=event.priority,
            privacy_level=event.privacy_level,
            tags=event.tags
        )
    
    def _anonymize_user_id(self, user_id: str) -> str:
        """
        Anonymize a user ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            str: The anonymized user ID
        """
        # Hash the user ID
        return hashlib.sha256(user_id.encode()).hexdigest()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dict[str, Any]: System information
        """
        try:
            info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "hostname": socket.gethostname(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage('/').total
            }
            
            return info
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}

class MetricCollector:
    """
    Metric collector for collecting and processing metrics.
    
    This class provides functionality for collecting metrics from various
    sources and processing them before storage.
    """
    
    def __init__(self, config: AnalyticsConfig):
        """
        Initialize the metric collector.
        
        Args:
            config: Analytics configuration
        """
        self.config = config
        self.metric_queue = queue.Queue()
        self.metric_processors: List[Callable[[Metric], Optional[Metric]]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._performance_monitor: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start the metric collector."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._thread = threading.Thread(target=self._process_metrics, daemon=True)
            self._thread.start()
            
            # Start performance monitoring if enabled
            if self.config.include_performance_metrics:
                self._performance_monitor = threading.Thread(target=self._monitor_performance, daemon=True)
                self._performance_monitor.start()
            
            logger.info("Metric collector started")
    
    def stop(self) -> None:
        """Stop the metric collector."""
        with self._lock:
            if not self._running:
                return
            
            self._running = False
            if self._thread:
                self._thread.join(timeout=5.0)
                self._thread = None
            
            if self._performance_monitor:
                self._performance_monitor.join(timeout=5.0)
                self._performance_monitor = None
            
            logger.info("Metric collector stopped")
    
    def collect_metric(self, name: str, value: float, unit: Optional[str] = None,
                      tags: Optional[Dict[str, str]] = None,
                      dimensions: Optional[Dict[str, str]] = None) -> str:
        """
        Collect a metric.
        
        Args:
            name: Metric name
            value: Metric value
            unit: Optional unit
            tags: Optional tags
            dimensions: Optional dimensions
            
        Returns:
            str: Metric ID
        """
        if not self.config.enabled:
            return ""
        
        # Create metric
        metric_id = str(uuid.uuid4())
        metric = Metric(
            metric_id=metric_id,
            name=name,
            value=value,
            timestamp=datetime.now(),
            unit=unit,
            tags=tags or {},
            dimensions=dimensions or {}
        )
        
        # Add to queue
        self.metric_queue.put(metric)
        
        return metric_id
    
    def add_metric_processor(self, processor: Callable[[Metric], Optional[Metric]]) -> None:
        """
        Add a metric processor.
        
        Args:
            processor: Metric processor function
        """
        with self._lock:
            self.metric_processors.append(processor)
    
    def _process_metrics(self) -> None:
        """Process metrics from the queue."""
        while self._running:
            try:
                # Get metric from queue with timeout
                try:
                    metric = self.metric_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Apply processors
                processed_metric = self._apply_processors(metric)
                if not processed_metric:
                    self.metric_queue.task_done()
                    continue
                
                # Pass to storage manager
                # In a real implementation, this would pass the metric to a storage manager
                # For this example, we'll just log it
                logger.debug(f"Processed metric: {processed_metric.metric_id}")
                
                self.metric_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing metric: {str(e)}")
    
    def _apply_processors(self, metric: Metric) -> Optional[Metric]:
        """
        Apply processors to a metric.
        
        Args:
            metric: The metric
            
        Returns:
            Optional[Metric]: The processed metric, or None if it should be dropped
        """
        processed_metric = metric
        
        for processor in self.metric_processors:
            try:
                processed_metric = processor(processed_metric)
                if not processed_metric:
                    return None
            except Exception as e:
                logger.error(f"Error applying processor: {str(e)}")
        
        return processed_metric
    
    def _monitor_performance(self) -> None:
        """Monitor system performance."""
        while self._running:
            try:
                # Collect CPU usage
                cpu_percent = psutil.cpu_percent(interval=1.0)
                self.collect_metric(
                    name="cpu_usage",
                    value=cpu_percent,
                    unit="percent",
                    tags={"type": "system"}
                )
                
                # Collect memory usage
                memory = psutil.virtual_memory()
                self.collect_metric(
                    name="memory_usage",
                    value=memory.percent,
                    unit="percent",
                    tags={"type": "system"}
                )
                
                # Collect disk usage
                disk = psutil.disk_usage('/')
                self.collect_metric(
                    name="disk_usage",
                    value=disk.percent,
                    unit="percent",
                    tags={"type": "system"}
                )
                
                # Collect network usage
                net_io = psutil.net_io_counters()
                self.collect_metric(
                    name="network_bytes_sent",
                    value=net_io.bytes_sent,
                    unit="bytes",
                    tags={"type": "system"}
                )
                self.collect_metric(
                    name="network_bytes_recv",
                    value=net_io.bytes_recv,
                    unit="bytes",
                    tags={"type": "system"}
                )
                
                # Sleep for a while
                time.sleep(60.0)
            except Exception as e:
                logger.error(f"Error monitoring performance: {str(e)}")
                time.sleep(60.0)

class StorageManager:
    """
    Storage manager for storing events and metrics.
    
    This class provides functionality for storing events and metrics
    in local or remote storage.
    """
    
    def __init__(self, config: AnalyticsConfig):
        """
        Initialize the storage manager.
        
        Args:
            config: Analytics configuration
        """
        self.config = config
        self.event_batch: List[Event] = []
        self.metric_batch: List[Metric] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._last_flush_time = datetime.now()
    
    def start(self) -> None:
        """Start the storage manager."""
        with self._lock:
            if self._running:
                return
            
            # Create storage directory if it doesn't exist
            if self.config.storage_type in [StorageType.LOCAL, StorageType.BOTH]:
                os.makedirs(self.config.local_storage_path, exist_ok=True)
            
            self._running = True
            self._thread = threading.Thread(target=self._flush_loop, daemon=True)
            self._thread.start()
            
            logger.info("Storage manager started")
    
    def stop(self) -> None:
        """Stop the storage manager."""
        with self._lock:
            if not self._running:
                return
            
            self._running = False
            if self._thread:
                self._thread.join(timeout=5.0)
                self._thread = None
            
            # Flush any remaining data
            self._flush()
            
            logger.info("Storage manager stopped")
    
    def store_event(self, event: Event) -> None:
        """
        Store an event.
        
        Args:
            event: The event
        """
        with self._lock:
            self.event_batch.append(event)
            
            # Flush if batch size reached
            if len(self.event_batch) >= self.config.batch_size:
                self._flush_events()
    
    def store_metric(self, metric: Metric) -> None:
        """
        Store a metric.
        
        Args:
            metric: The metric
        """
        with self._lock:
            self.metric_batch.append(metric)
            
            # Flush if batch size reached
            if len(self.metric_batch) >= self.config.batch_size:
                self._flush_metrics()
    
    def _flush_loop(self) -> None:
        """Flush data periodically."""
        while self._running:
            try:
                # Check if flush interval reached
                now = datetime.now()
                if (now - self._last_flush_time).total_seconds() >= self.config.flush_interval:
                    self._flush()
                    self._last_flush_time = now
                
                # Sleep for a while
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Error in flush loop: {str(e)}")
    
    def _flush(self) -> None:
        """Flush all data."""
        with self._lock:
            self._flush_events()
            self._flush_metrics()
    
    def _flush_events(self) -> None:
        """Flush events."""
        if not self.event_batch:
            return
        
        try:
            # Store locally if configured
            if self.config.storage_type in [StorageType.LOCAL, StorageType.BOTH]:
                self._store_events_locally(self.event_batch)
            
            # Store remotely if configured
            if self.config.storage_type in [StorageType.REMOTE, StorageType.BOTH]:
                self._store_events_remotely(self.event_batch)
            
            # Clear batch
            self.event_batch = []
            
            logger.debug(f"Flushed events")
        except Exception as e:
            logger.error(f"Error flushing events: {str(e)}")
    
    def _flush_metrics(self) -> None:
        """Flush metrics."""
        if not self.metric_batch:
            return
        
        try:
            # Store locally if configured
            if self.config.storage_type in [StorageType.LOCAL, StorageType.BOTH]:
                self._store_metrics_locally(self.metric_batch)
            
            # Store remotely if configured
            if self.config.storage_type in [StorageType.REMOTE, StorageType.BOTH]:
                self._store_metrics_remotely(self.metric_batch)
            
            # Clear batch
            self.metric_batch = []
            
            logger.debug(f"Flushed metrics")
        except Exception as e:
            logger.error(f"Error flushing metrics: {str(e)}")
    
    def _store_events_locally(self, events: List[Event]) -> None:
        """
        Store events locally.
        
        Args:
            events: The events
        """
        try:
            # Create events directory if it doesn't exist
            events_dir = os.path.join(self.config.local_storage_path, "events")
            os.makedirs(events_dir, exist_ok=True)
            
            # Group events by date
            events_by_date: Dict[str, List[Event]] = {}
            for event in events:
                date_str = event.timestamp.strftime("%Y-%m-%d")
                if date_str not in events_by_date:
                    events_by_date[date_str] = []
                events_by_date[date_str].append(event)
            
            # Store events by date
            for date_str, date_events in events_by_date.items():
                # Create date directory if it doesn't exist
                date_dir = os.path.join(events_dir, date_str)
                os.makedirs(date_dir, exist_ok=True)
                
                # Create file path
                file_path = os.path.join(date_dir, f"{uuid.uuid4()}.json")
                
                # Write events to file
                with open(file_path, 'w') as f:
                    json.dump([event.to_dict() for event in date_events], f)
        except Exception as e:
            logger.error(f"Error storing events locally: {str(e)}")
            raise
    
    def _store_metrics_locally(self, metrics: List[Metric]) -> None:
        """
        Store metrics locally.
        
        Args:
            metrics: The metrics
        """
        try:
            # Create metrics directory if it doesn't exist
            metrics_dir = os.path.join(self.config.local_storage_path, "metrics")
            os.makedirs(metrics_dir, exist_ok=True)
            
            # Group metrics by date
            metrics_by_date: Dict[str, List[Metric]] = {}
            for metric in metrics:
                date_str = metric.timestamp.strftime("%Y-%m-%d")
                if date_str not in metrics_by_date:
                    metrics_by_date[date_str] = []
                metrics_by_date[date_str].append(metric)
            
            # Store metrics by date
            for date_str, date_metrics in metrics_by_date.items():
                # Create date directory if it doesn't exist
                date_dir = os.path.join(metrics_dir, date_str)
                os.makedirs(date_dir, exist_ok=True)
                
                # Create file path
                file_path = os.path.join(date_dir, f"{uuid.uuid4()}.json")
                
                # Write metrics to file
                with open(file_path, 'w') as f:
                    json.dump([metric.to_dict() for metric in date_metrics], f)
        except Exception as e:
            logger.error(f"Error storing metrics locally: {str(e)}")
            raise
    
    def _store_events_remotely(self, events: List[Event]) -> None:
        """
        Store events remotely.
        
        Args:
            events: The events
        """
        if not self.config.remote_endpoint:
            return
        
        try:
            # Prepare request
            url = f"{self.config.remote_endpoint}/events"
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.config.remote_api_key:
                headers["X-API-Key"] = self.config.remote_api_key
            
            data = [event.to_dict() for event in events]
            
            # Send request
            response = requests.post(url, headers=headers, json=data)
            
            # Check response
            if response.status_code != 200:
                logger.error(f"Error storing events remotely: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error storing events remotely: {str(e)}")
            raise
    
    def _store_metrics_remotely(self, metrics: List[Metric]) -> None:
        """
        Store metrics remotely.
        
        Args:
            metrics: The metrics
        """
        if not self.config.remote_endpoint:
            return
        
        try:
            # Prepare request
            url = f"{self.config.remote_endpoint}/metrics"
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.config.remote_api_key:
                headers["X-API-Key"] = self.config.remote_api_key
            
            data = [metric.to_dict() for metric in metrics]
            
            # Send request
            response = requests.post(url, headers=headers, json=data)
            
            # Check response
            if response.status_code != 200:
                logger.error(f"Error storing metrics remotely: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error storing metrics remotely: {str(e)}")
            raise
    
    def cleanup_old_data(self) -> None:
        """Clean up old data."""
        if self.config.storage_type not in [StorageType.LOCAL, StorageType.BOTH]:
            return
        
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.config.max_event_age)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
            
            # Clean up events
            events_dir = os.path.join(self.config.local_storage_path, "events")
            if os.path.exists(events_dir):
                for date_dir in os.listdir(events_dir):
                    if date_dir < cutoff_date_str:
                        date_path = os.path.join(events_dir, date_dir)
                        if os.path.isdir(date_path):
                            for file_name in os.listdir(date_path):
                                file_path = os.path.join(date_path, file_name)
                                os.remove(file_path)
                            os.rmdir(date_path)
            
            # Clean up metrics
            metrics_dir = os.path.join(self.config.local_storage_path, "metrics")
            if os.path.exists(metrics_dir):
                for date_dir in os.listdir(metrics_dir):
                    if date_dir < cutoff_date_str:
                        date_path = os.path.join(metrics_dir, date_dir)
                        if os.path.isdir(date_path):
                            for file_name in os.listdir(date_path):
                                file_path = os.path.join(date_path, file_name)
                                os.remove(file_path)
                            os.rmdir(date_path)
            
            logger.info(f"Cleaned up data older than {cutoff_date_str}")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
    
    def check_storage_size(self) -> None:
        """Check storage size and clean up if necessary."""
        if self.config.storage_type not in [StorageType.LOCAL, StorageType.BOTH]:
            return
        
        try:
            # Get storage size
            storage_size = 0
            for root, _, files in os.walk(self.config.local_storage_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    storage_size += os.path.getsize(file_path)
            
            # Convert to MB
            storage_size_mb = storage_size / (1024 * 1024)
            
            # Check if size exceeds limit
            if storage_size_mb > self.config.max_storage_size:
                logger.warning(f"Storage size ({storage_size_mb:.2f} MB) exceeds limit ({self.config.max_storage_size} MB)")
                
                # Clean up old data
                self.cleanup_old_data()
                
                # If still too large, delete oldest data
                if storage_size_mb > self.config.max_storage_size:
                    self._delete_oldest_data()
        except Exception as e:
            logger.error(f"Error checking storage size: {str(e)}")
    
    def _delete_oldest_data(self) -> None:
        """Delete oldest data."""
        try:
            # Find oldest event date
            events_dir = os.path.join(self.config.local_storage_path, "events")
            oldest_event_date = None
            if os.path.exists(events_dir):
                for date_dir in os.listdir(events_dir):
                    date_path = os.path.join(events_dir, date_dir)
                    if os.path.isdir(date_path):
                        if oldest_event_date is None or date_dir < oldest_event_date:
                            oldest_event_date = date_dir
            
            # Find oldest metric date
            metrics_dir = os.path.join(self.config.local_storage_path, "metrics")
            oldest_metric_date = None
            if os.path.exists(metrics_dir):
                for date_dir in os.listdir(metrics_dir):
                    date_path = os.path.join(metrics_dir, date_dir)
                    if os.path.isdir(date_path):
                        if oldest_metric_date is None or date_dir < oldest_metric_date:
                            oldest_metric_date = date_dir
            
            # Delete oldest data
            if oldest_event_date and (not oldest_metric_date or oldest_event_date <= oldest_metric_date):
                date_path = os.path.join(events_dir, oldest_event_date)
                if os.path.isdir(date_path):
                    for file_name in os.listdir(date_path):
                        file_path = os.path.join(date_path, file_name)
                        os.remove(file_path)
                    os.rmdir(date_path)
                    logger.info(f"Deleted oldest event data: {oldest_event_date}")
            elif oldest_metric_date:
                date_path = os.path.join(metrics_dir, oldest_metric_date)
                if os.path.isdir(date_path):
                    for file_name in os.listdir(date_path):
                        file_path = os.path.join(date_path, file_name)
                        os.remove(file_path)
                    os.rmdir(date_path)
                    logger.info(f"Deleted oldest metric data: {oldest_metric_date}")
        except Exception as e:
            logger.error(f"Error deleting oldest data: {str(e)}")

class AnalyticsQuery:
    """
    Analytics query for querying and analyzing data.
    
    This class provides functionality for querying and analyzing
    events and metrics.
    """
    
    def __init__(self, config: AnalyticsConfig):
        """
        Initialize the analytics query.
        
        Args:
            config: Analytics configuration
        """
        self.config = config
    
    def query_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                    event_types: Optional[List[EventType]] = None, categories: Optional[List[EventCategory]] = None,
                    user_id: Optional[str] = None, component: Optional[str] = None,
                    tags: Optional[List[str]] = None, limit: int = 1000) -> List[Event]:
        """
        Query events.
        
        Args:
            start_date: Optional start date
            end_date: Optional end date
            event_types: Optional event types
            categories: Optional categories
            user_id: Optional user ID
            component: Optional component
            tags: Optional tags
            limit: Maximum number of events to return
            
        Returns:
            List[Event]: Matching events
        """
        if self.config.storage_type not in [StorageType.LOCAL, StorageType.BOTH]:
            return []
        
        events = []
        
        try:
            # Set default dates
            if not start_date:
                start_date = datetime.now() - timedelta(days=7)
            if not end_date:
                end_date = datetime.now()
            
            # Convert dates to strings
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Get date range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
            
            # Query events
            events_dir = os.path.join(self.config.local_storage_path, "events")
            if os.path.exists(events_dir):
                for date_str in date_range:
                    date_dir = os.path.join(events_dir, date_str)
                    if os.path.exists(date_dir) and os.path.isdir(date_dir):
                        for file_name in os.listdir(date_dir):
                            if len(events) >= limit:
                                break
                            
                            file_path = os.path.join(date_dir, file_name)
                            if os.path.isfile(file_path) and file_name.endswith('.json'):
                                with open(file_path, 'r') as f:
                                    file_events = json.load(f)
                                    for event_data in file_events:
                                        # Create event
                                        event = Event.from_dict(event_data)
                                        
                                        # Apply filters
                                        if event_types and event.event_type not in event_types:
                                            continue
                                        if categories and event.category not in categories:
                                            continue
                                        if user_id and event.user_id != user_id:
                                            continue
                                        if component and event.component != component:
                                            continue
                                        if tags and not any(tag in event.tags for tag in tags):
                                            continue
                                        
                                        events.append(event)
                                        
                                        if len(events) >= limit:
                                            break
            
            return events
        except Exception as e:
            logger.error(f"Error querying events: {str(e)}")
            return []
    
    def query_metrics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                     names: Optional[List[str]] = None, tags: Optional[Dict[str, str]] = None,
                     dimensions: Optional[Dict[str, str]] = None, limit: int = 1000) -> List[Metric]:
        """
        Query metrics.
        
        Args:
            start_date: Optional start date
            end_date: Optional end date
            names: Optional metric names
            tags: Optional tags
            dimensions: Optional dimensions
            limit: Maximum number of metrics to return
            
        Returns:
            List[Metric]: Matching metrics
        """
        if self.config.storage_type not in [StorageType.LOCAL, StorageType.BOTH]:
            return []
        
        metrics = []
        
        try:
            # Set default dates
            if not start_date:
                start_date = datetime.now() - timedelta(days=7)
            if not end_date:
                end_date = datetime.now()
            
            # Convert dates to strings
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Get date range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
            
            # Query metrics
            metrics_dir = os.path.join(self.config.local_storage_path, "metrics")
            if os.path.exists(metrics_dir):
                for date_str in date_range:
                    date_dir = os.path.join(metrics_dir, date_str)
                    if os.path.exists(date_dir) and os.path.isdir(date_dir):
                        for file_name in os.listdir(date_dir):
                            if len(metrics) >= limit:
                                break
                            
                            file_path = os.path.join(date_dir, file_name)
                            if os.path.isfile(file_path) and file_name.endswith('.json'):
                                with open(file_path, 'r') as f:
                                    file_metrics = json.load(f)
                                    for metric_data in file_metrics:
                                        # Create metric
                                        metric = Metric.from_dict(metric_data)
                                        
                                        # Apply filters
                                        if names and metric.name not in names:
                                            continue
                                        if tags and not all(metric.tags.get(k) == v for k, v in tags.items()):
                                            continue
                                        if dimensions and not all(metric.dimensions.get(k) == v for k, v in dimensions.items()):
                                            continue
                                        
                                        metrics.append(metric)
                                        
                                        if len(metrics) >= limit:
                                            break
            
            return metrics
        except Exception as e:
            logger.error(f"Error querying metrics: {str(e)}")
            return []
    
    def aggregate_metrics(self, metrics: List[Metric], aggregation: str = 'avg',
                         group_by: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Aggregate metrics.
        
        Args:
            metrics: The metrics
            aggregation: Aggregation function ('avg', 'sum', 'min', 'max', 'count')
            group_by: Optional fields to group by
            
        Returns:
            Dict[str, float]: Aggregated metrics
        """
        if not metrics:
            return {}
        
        try:
            # Convert metrics to DataFrame
            data = []
            for metric in metrics:
                row = {
                    'name': metric.name,
                    'value': metric.value,
                    'timestamp': metric.timestamp
                }
                
                # Add tags
                for k, v in metric.tags.items():
                    row[f'tag_{k}'] = v
                
                # Add dimensions
                for k, v in metric.dimensions.items():
                    row[f'dim_{k}'] = v
                
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Group by fields
            if group_by:
                group_cols = []
                for field in group_by:
                    if field == 'name':
                        group_cols.append('name')
                    elif field.startswith('tag_'):
                        tag_name = field[4:]
                        group_cols.append(f'tag_{tag_name}')
                    elif field.startswith('dim_'):
                        dim_name = field[4:]
                        group_cols.append(f'dim_{dim_name}')
                
                if not group_cols:
                    group_cols = ['name']
                
                # Group and aggregate
                if aggregation == 'avg':
                    result_df = df.groupby(group_cols)['value'].mean().reset_index()
                elif aggregation == 'sum':
                    result_df = df.groupby(group_cols)['value'].sum().reset_index()
                elif aggregation == 'min':
                    result_df = df.groupby(group_cols)['value'].min().reset_index()
                elif aggregation == 'max':
                    result_df = df.groupby(group_cols)['value'].max().reset_index()
                elif aggregation == 'count':
                    result_df = df.groupby(group_cols)['value'].count().reset_index()
                else:
                    result_df = df.groupby(group_cols)['value'].mean().reset_index()
                
                # Convert to dictionary
                result = {}
                for _, row in result_df.iterrows():
                    key = '_'.join(str(row[col]) for col in group_cols)
                    result[key] = row['value']
                
                return result
            else:
                # Aggregate all metrics
                if aggregation == 'avg':
                    return {'all': df['value'].mean()}
                elif aggregation == 'sum':
                    return {'all': df['value'].sum()}
                elif aggregation == 'min':
                    return {'all': df['value'].min()}
                elif aggregation == 'max':
                    return {'all': df['value'].max()}
                elif aggregation == 'count':
                    return {'all': df['value'].count()}
                else:
                    return {'all': df['value'].mean()}
        except Exception as e:
            logger.error(f"Error aggregating metrics: {str(e)}")
            return {}
    
    def get_event_statistics(self, events: List[Event]) -> Dict[str, Any]:
        """
        Get statistics for events.
        
        Args:
            events: The events
            
        Returns:
            Dict[str, Any]: Event statistics
        """
        if not events:
            return {}
        
        try:
            # Count events by type
            events_by_type = {}
            for event in events:
                event_type = event.event_type.value
                if event_type not in events_by_type:
                    events_by_type[event_type] = 0
                events_by_type[event_type] += 1
            
            # Count events by category
            events_by_category = {}
            for event in events:
                category = event.category.value
                if category not in events_by_category:
                    events_by_category[category] = 0
                events_by_category[category] += 1
            
            # Count events by component
            events_by_component = {}
            for event in events:
                if event.component:
                    if event.component not in events_by_component:
                        events_by_component[event.component] = 0
                    events_by_component[event.component] += 1
            
            # Count events by user
            events_by_user = {}
            for event in events:
                if event.user_id:
                    if event.user_id not in events_by_user:
                        events_by_user[event.user_id] = 0
                    events_by_user[event.user_id] += 1
            
            # Count events by day
            events_by_day = {}
            for event in events:
                day = event.timestamp.strftime("%Y-%m-%d")
                if day not in events_by_day:
                    events_by_day[day] = 0
                events_by_day[day] += 1
            
            # Count events by hour
            events_by_hour = {}
            for event in events:
                hour = event.timestamp.hour
                if hour not in events_by_hour:
                    events_by_hour[hour] = 0
                events_by_hour[hour] += 1
            
            # Return statistics
            return {
                "total_events": len(events),
                "events_by_type": events_by_type,
                "events_by_category": events_by_category,
                "events_by_component": events_by_component,
                "events_by_user": events_by_user,
                "events_by_day": events_by_day,
                "events_by_hour": events_by_hour
            }
        except Exception as e:
            logger.error(f"Error getting event statistics: {str(e)}")
            return {}
    
    def get_metric_statistics(self, metrics: List[Metric]) -> Dict[str, Any]:
        """
        Get statistics for metrics.
        
        Args:
            metrics: The metrics
            
        Returns:
            Dict[str, Any]: Metric statistics
        """
        if not metrics:
            return {}
        
        try:
            # Group metrics by name
            metrics_by_name = {}
            for metric in metrics:
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append(metric.value)
            
            # Calculate statistics for each metric
            metric_stats = {}
            for name, values in metrics_by_name.items():
                values_array = np.array(values)
                metric_stats[name] = {
                    "count": len(values),
                    "min": float(np.min(values_array)),
                    "max": float(np.max(values_array)),
                    "mean": float(np.mean(values_array)),
                    "median": float(np.median(values_array)),
                    "std": float(np.std(values_array)),
                    "p25": float(np.percentile(values_array, 25)),
                    "p75": float(np.percentile(values_array, 75)),
                    "p90": float(np.percentile(values_array, 90)),
                    "p95": float(np.percentile(values_array, 95)),
                    "p99": float(np.percentile(values_array, 99))
                }
            
            # Return statistics
            return {
                "total_metrics": len(metrics),
                "unique_metrics": len(metrics_by_name),
                "metric_stats": metric_stats
            }
        except Exception as e:
            logger.error(f"Error getting metric statistics: {str(e)}")
            return {}

class Analytics:
    """
    Analytics system for ApexAgent.
    
    This class provides comprehensive analytics capabilities including:
    - Event tracking
    - Metric collection
    - Data storage
    - Data querying and analysis
    - Visualization
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'Analytics':
        """
        Get the singleton instance of the analytics system.
        
        Returns:
            Analytics: The singleton instance
        """
        if cls._instance is None:
            cls._instance = Analytics()
        return cls._instance
    
    def __init__(self):
        """Initialize the analytics system."""
        self.config = AnalyticsConfig()
        self.event_collector = EventCollector(self.config)
        self.metric_collector = MetricCollector(self.config)
        self.storage_manager = StorageManager(self.config)
        self.query = AnalyticsQuery(self.config)
        self._initialized = False
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the analytics system.
        
        Args:
            config_path: Optional path to configuration file
        """
        if self._initialized:
            return
        
        # Load configuration
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                self.config = AnalyticsConfig.from_dict(config_data)
        
        # Initialize components
        self.event_collector = EventCollector(self.config)
        self.metric_collector = MetricCollector(self.config)
        self.storage_manager = StorageManager(self.config)
        self.query = AnalyticsQuery(self.config)
        
        # Connect components
        self.event_collector.add_event_processor(self.storage_manager.store_event)
        self.metric_collector.add_metric_processor(self.storage_manager.store_metric)
        
        # Start components
        if self.config.enabled:
            self.storage_manager.start()
            self.event_collector.start()
            self.metric_collector.start()
        
        self._initialized = True
        logger.info("Analytics system initialized")
    
    def shutdown(self) -> None:
        """Shutdown the analytics system."""
        if not self._initialized:
            return
        
        # Stop components
        self.event_collector.stop()
        self.metric_collector.stop()
        self.storage_manager.stop()
        
        self._initialized = False
        logger.info("Analytics system shutdown")
    
    def track_event(self, event_type: EventType, category: EventCategory, data: Dict[str, Any],
                   user_id: Optional[str] = None, component: Optional[str] = None,
                   priority: EventPriority = EventPriority.MEDIUM,
                   privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL,
                   tags: Optional[List[str]] = None) -> str:
        """
        Track an event.
        
        Args:
            event_type: Event type
            category: Event category
            data: Event data
            user_id: Optional user ID
            component: Optional component name
            priority: Event priority
            privacy_level: Privacy level
            tags: Optional tags
            
        Returns:
            str: Event ID
        """
        if not self._initialized:
            self.initialize()
        
        return self.event_collector.collect_event(
            event_type=event_type,
            category=category,
            data=data,
            user_id=user_id,
            component=component,
            priority=priority,
            privacy_level=privacy_level,
            tags=tags
        )
    
    def track_metric(self, name: str, value: float, unit: Optional[str] = None,
                    tags: Optional[Dict[str, str]] = None,
                    dimensions: Optional[Dict[str, str]] = None) -> str:
        """
        Track a metric.
        
        Args:
            name: Metric name
            value: Metric value
            unit: Optional unit
            tags: Optional tags
            dimensions: Optional dimensions
            
        Returns:
            str: Metric ID
        """
        if not self._initialized:
            self.initialize()
        
        return self.metric_collector.collect_metric(
            name=name,
            value=value,
            unit=unit,
            tags=tags,
            dimensions=dimensions
        )
    
    def track_error(self, error: Exception, component: Optional[str] = None,
                   user_id: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Track an error.
        
        Args:
            error: The error
            component: Optional component name
            user_id: Optional user ID
            additional_data: Optional additional data
            
        Returns:
            str: Event ID
        """
        if not self._initialized:
            self.initialize()
        
        # Prepare data
        data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc()
        }
        
        if additional_data:
            data.update(additional_data)
        
        return self.event_collector.collect_event(
            event_type=EventType.ERROR,
            category=EventCategory.ERROR,
            data=data,
            user_id=user_id,
            component=component,
            priority=EventPriority.HIGH
        )
    
    def track_user_action(self, action: str, user_id: Optional[str] = None,
                         component: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Track a user action.
        
        Args:
            action: The action
            user_id: Optional user ID
            component: Optional component name
            data: Optional data
            
        Returns:
            str: Event ID
        """
        if not self._initialized:
            self.initialize()
        
        return self.event_collector.collect_event(
            event_type=EventType.USER_ACTION,
            category=EventCategory.USER,
            data={"action": action, **(data or {})},
            user_id=user_id,
            component=component
        )
    
    def track_feature_usage(self, feature: str, user_id: Optional[str] = None,
                           component: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Track feature usage.
        
        Args:
            feature: The feature
            user_id: Optional user ID
            component: Optional component name
            data: Optional data
            
        Returns:
            str: Event ID
        """
        if not self._initialized:
            self.initialize()
        
        return self.event_collector.collect_event(
            event_type=EventType.FEATURE_USAGE,
            category=EventCategory.FEATURE,
            data={"feature": feature, **(data or {})},
            user_id=user_id,
            component=component
        )
    
    def track_task(self, task_id: str, status: str, user_id: Optional[str] = None,
                  component: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Track a task.
        
        Args:
            task_id: The task ID
            status: The task status
            user_id: Optional user ID
            component: Optional component name
            data: Optional data
            
        Returns:
            str: Event ID
        """
        if not self._initialized:
            self.initialize()
        
        if status.lower() == "start":
            event_type = EventType.TASK_START
        elif status.lower() == "end":
            event_type = EventType.TASK_END
        else:
            event_type = EventType.TASK_PROGRESS
        
        return self.event_collector.collect_event(
            event_type=event_type,
            category=EventCategory.TASK,
            data={"task_id": task_id, "status": status, **(data or {})},
            user_id=user_id,
            component=component
        )
    
    def track_performance(self, metric_name: str, value: float, unit: Optional[str] = None,
                         component: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> str:
        """
        Track a performance metric.
        
        Args:
            metric_name: The metric name
            value: The metric value
            unit: Optional unit
            component: Optional component name
            tags: Optional tags
            
        Returns:
            str: Metric ID
        """
        if not self._initialized:
            self.initialize()
        
        return self.metric_collector.collect_metric(
            name=metric_name,
            value=value,
            unit=unit,
            tags={"type": "performance", "component": component, **(tags or {})}
        )
    
    def query_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                    event_types: Optional[List[EventType]] = None, categories: Optional[List[EventCategory]] = None,
                    user_id: Optional[str] = None, component: Optional[str] = None,
                    tags: Optional[List[str]] = None, limit: int = 1000) -> List[Event]:
        """
        Query events.
        
        Args:
            start_date: Optional start date
            end_date: Optional end date
            event_types: Optional event types
            categories: Optional categories
            user_id: Optional user ID
            component: Optional component name
            tags: Optional tags
            limit: Maximum number of events to return
            
        Returns:
            List[Event]: Matching events
        """
        if not self._initialized:
            self.initialize()
        
        return self.query.query_events(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types,
            categories=categories,
            user_id=user_id,
            component=component,
            tags=tags,
            limit=limit
        )
    
    def query_metrics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                     names: Optional[List[str]] = None, tags: Optional[Dict[str, str]] = None,
                     dimensions: Optional[Dict[str, str]] = None, limit: int = 1000) -> List[Metric]:
        """
        Query metrics.
        
        Args:
            start_date: Optional start date
            end_date: Optional end date
            names: Optional metric names
            tags: Optional tags
            dimensions: Optional dimensions
            limit: Maximum number of metrics to return
            
        Returns:
            List[Metric]: Matching metrics
        """
        if not self._initialized:
            self.initialize()
        
        return self.query.query_metrics(
            start_date=start_date,
            end_date=end_date,
            names=names,
            tags=tags,
            dimensions=dimensions,
            limit=limit
        )
    
    def get_event_statistics(self, events: Optional[List[Event]] = None,
                            start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                            event_types: Optional[List[EventType]] = None,
                            categories: Optional[List[EventCategory]] = None,
                            user_id: Optional[str] = None, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Get event statistics.
        
        Args:
            events: Optional list of events (if not provided, will query events)
            start_date: Optional start date (for querying events)
            end_date: Optional end date (for querying events)
            event_types: Optional event types (for querying events)
            categories: Optional categories (for querying events)
            user_id: Optional user ID (for querying events)
            component: Optional component name (for querying events)
            
        Returns:
            Dict[str, Any]: Event statistics
        """
        if not self._initialized:
            self.initialize()
        
        # Query events if not provided
        if events is None:
            events = self.query_events(
                start_date=start_date,
                end_date=end_date,
                event_types=event_types,
                categories=categories,
                user_id=user_id,
                component=component
            )
        
        return self.query.get_event_statistics(events)
    
    def get_metric_statistics(self, metrics: Optional[List[Metric]] = None,
                             start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                             names: Optional[List[str]] = None, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Get metric statistics.
        
        Args:
            metrics: Optional list of metrics (if not provided, will query metrics)
            start_date: Optional start date (for querying metrics)
            end_date: Optional end date (for querying metrics)
            names: Optional metric names (for querying metrics)
            tags: Optional tags (for querying metrics)
            
        Returns:
            Dict[str, Any]: Metric statistics
        """
        if not self._initialized:
            self.initialize()
        
        # Query metrics if not provided
        if metrics is None:
            metrics = self.query_metrics(
                start_date=start_date,
                end_date=end_date,
                names=names,
                tags=tags
            )
        
        return self.query.get_metric_statistics(metrics)
    
    def aggregate_metrics(self, metrics: Optional[List[Metric]] = None,
                         start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                         names: Optional[List[str]] = None, tags: Optional[Dict[str, str]] = None,
                         aggregation: str = 'avg', group_by: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Aggregate metrics.
        
        Args:
            metrics: Optional list of metrics (if not provided, will query metrics)
            start_date: Optional start date (for querying metrics)
            end_date: Optional end date (for querying metrics)
            names: Optional metric names (for querying metrics)
            tags: Optional tags (for querying metrics)
            aggregation: Aggregation function ('avg', 'sum', 'min', 'max', 'count')
            group_by: Optional fields to group by
            
        Returns:
            Dict[str, float]: Aggregated metrics
        """
        if not self._initialized:
            self.initialize()
        
        # Query metrics if not provided
        if metrics is None:
            metrics = self.query_metrics(
                start_date=start_date,
                end_date=end_date,
                names=names,
                tags=tags
            )
        
        return self.query.aggregate_metrics(metrics, aggregation, group_by)
    
    def cleanup_old_data(self) -> None:
        """Clean up old data."""
        if not self._initialized:
            self.initialize()
        
        self.storage_manager.cleanup_old_data()
    
    def check_storage_size(self) -> None:
        """Check storage size and clean up if necessary."""
        if not self._initialized:
            self.initialize()
        
        self.storage_manager.check_storage_size()
    
    def get_config(self) -> AnalyticsConfig:
        """
        Get the analytics configuration.
        
        Returns:
            AnalyticsConfig: The configuration
        """
        return self.config
    
    def set_config(self, config: AnalyticsConfig) -> None:
        """
        Set the analytics configuration.
        
        Args:
            config: The configuration
        """
        # Shutdown with old config
        self.shutdown()
        
        # Set new config
        self.config = config
        
        # Initialize with new config
        self.initialize()


# Global instance for easy access
analytics = Analytics.get_instance()


def initialize_analytics(config_path: Optional[str] = None) -> None:
    """
    Initialize the analytics system.
    
    Args:
        config_path: Optional path to configuration file
    """
    analytics.initialize(config_path)


def track_event(event_type: EventType, category: EventCategory, data: Dict[str, Any],
               user_id: Optional[str] = None, component: Optional[str] = None,
               priority: EventPriority = EventPriority.MEDIUM,
               privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL,
               tags: Optional[List[str]] = None) -> str:
    """
    Track an event.
    
    Args:
        event_type: Event type
        category: Event category
        data: Event data
        user_id: Optional user ID
        component: Optional component name
        priority: Event priority
        privacy_level: Privacy level
        tags: Optional tags
        
    Returns:
        str: Event ID
    """
    return analytics.track_event(
        event_type=event_type,
        category=category,
        data=data,
        user_id=user_id,
        component=component,
        priority=priority,
        privacy_level=privacy_level,
        tags=tags
    )


def track_metric(name: str, value: float, unit: Optional[str] = None,
                tags: Optional[Dict[str, str]] = None,
                dimensions: Optional[Dict[str, str]] = None) -> str:
    """
    Track a metric.
    
    Args:
        name: Metric name
        value: Metric value
        unit: Optional unit
        tags: Optional tags
        dimensions: Optional dimensions
        
    Returns:
        str: Metric ID
    """
    return analytics.track_metric(
        name=name,
        value=value,
        unit=unit,
        tags=tags,
        dimensions=dimensions
    )


def track_error(error: Exception, component: Optional[str] = None,
               user_id: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Track an error.
    
    Args:
        error: The error
        component: Optional component name
        user_id: Optional user ID
        additional_data: Optional additional data
        
    Returns:
        str: Event ID
    """
    return analytics.track_error(
        error=error,
        component=component,
        user_id=user_id,
        additional_data=additional_data
    )


def track_user_action(action: str, user_id: Optional[str] = None,
                     component: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
    """
    Track a user action.
    
    Args:
        action: The action
        user_id: Optional user ID
        component: Optional component name
        data: Optional data
        
    Returns:
        str: Event ID
    """
    return analytics.track_user_action(
        action=action,
        user_id=user_id,
        component=component,
        data=data
    )


def track_feature_usage(feature: str, user_id: Optional[str] = None,
                       component: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
    """
    Track feature usage.
    
    Args:
        feature: The feature
        user_id: Optional user ID
        component: Optional component name
        data: Optional data
        
    Returns:
        str: Event ID
    """
    return analytics.track_feature_usage(
        feature=feature,
        user_id=user_id,
        component=component,
        data=data
    )


def track_task(task_id: str, status: str, user_id: Optional[str] = None,
              component: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
    """
    Track a task.
    
    Args:
        task_id: The task ID
        status: The task status
        user_id: Optional user ID
        component: Optional component name
        data: Optional data
        
    Returns:
        str: Event ID
    """
    return analytics.track_task(
        task_id=task_id,
        status=status,
        user_id=user_id,
        component=component,
        data=data
    )


def track_performance(metric_name: str, value: float, unit: Optional[str] = None,
                     component: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> str:
    """
    Track a performance metric.
    
    Args:
        metric_name: The metric name
        value: The metric value
        unit: Optional unit
        component: Optional component name
        tags: Optional tags
        
    Returns:
        str: Metric ID
    """
    return analytics.track_performance(
        metric_name=metric_name,
        value=value,
        unit=unit,
        component=component,
        tags=tags
    )


def query_events(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                event_types: Optional[List[EventType]] = None, categories: Optional[List[EventCategory]] = None,
                user_id: Optional[str] = None, component: Optional[str] = None,
                tags: Optional[List[str]] = None, limit: int = 1000) -> List[Event]:
    """
    Query events.
    
    Args:
        start_date: Optional start date
        end_date: Optional end date
        event_types: Optional event types
        categories: Optional categories
        user_id: Optional user ID
        component: Optional component name
        tags: Optional tags
        limit: Maximum number of events to return
        
    Returns:
        List[Event]: Matching events
    """
    return analytics.query_events(
        start_date=start_date,
        end_date=end_date,
        event_types=event_types,
        categories=categories,
        user_id=user_id,
        component=component,
        tags=tags,
        limit=limit
    )


def query_metrics(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                 names: Optional[List[str]] = None, tags: Optional[Dict[str, str]] = None,
                 dimensions: Optional[Dict[str, str]] = None, limit: int = 1000) -> List[Metric]:
    """
    Query metrics.
    
    Args:
        start_date: Optional start date
        end_date: Optional end date
        names: Optional metric names
        tags: Optional tags
        dimensions: Optional dimensions
        limit: Maximum number of metrics to return
        
    Returns:
        List[Metric]: Matching metrics
    """
    return analytics.query_metrics(
        start_date=start_date,
        end_date=end_date,
        names=names,
        tags=tags,
        dimensions=dimensions,
        limit=limit
    )


def get_event_statistics(events: Optional[List[Event]] = None,
                        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                        event_types: Optional[List[EventType]] = None,
                        categories: Optional[List[EventCategory]] = None,
                        user_id: Optional[str] = None, component: Optional[str] = None) -> Dict[str, Any]:
    """
    Get event statistics.
    
    Args:
        events: Optional list of events (if not provided, will query events)
        start_date: Optional start date (for querying events)
        end_date: Optional end date (for querying events)
        event_types: Optional event types (for querying events)
        categories: Optional categories (for querying events)
        user_id: Optional user ID (for querying events)
        component: Optional component name (for querying events)
        
    Returns:
        Dict[str, Any]: Event statistics
    """
    return analytics.get_event_statistics(
        events=events,
        start_date=start_date,
        end_date=end_date,
        event_types=event_types,
        categories=categories,
        user_id=user_id,
        component=component
    )


def get_metric_statistics(metrics: Optional[List[Metric]] = None,
                         start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                         names: Optional[List[str]] = None, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Get metric statistics.
    
    Args:
        metrics: Optional list of metrics (if not provided, will query metrics)
        start_date: Optional start date (for querying metrics)
        end_date: Optional end date (for querying metrics)
        names: Optional metric names (for querying metrics)
        tags: Optional tags (for querying metrics)
        
    Returns:
        Dict[str, Any]: Metric statistics
    """
    return analytics.get_metric_statistics(
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        names=names,
        tags=tags
    )


def aggregate_metrics(metrics: Optional[List[Metric]] = None,
                     start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                     names: Optional[List[str]] = None, tags: Optional[Dict[str, str]] = None,
                     aggregation: str = 'avg', group_by: Optional[List[str]] = None) -> Dict[str, float]:
    """
    Aggregate metrics.
    
    Args:
        metrics: Optional list of metrics (if not provided, will query metrics)
        start_date: Optional start date (for querying metrics)
        end_date: Optional end date (for querying metrics)
        names: Optional metric names (for querying metrics)
        tags: Optional tags (for querying metrics)
        aggregation: Aggregation function ('avg', 'sum', 'min', 'max', 'count')
        group_by: Optional fields to group by
        
    Returns:
        Dict[str, float]: Aggregated metrics
    """
    return analytics.aggregate_metrics(
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        names=names,
        tags=tags,
        aggregation=aggregation,
        group_by=group_by
    )


def cleanup_old_data() -> None:
    """Clean up old data."""
    analytics.cleanup_old_data()


def check_storage_size() -> None:
    """Check storage size and clean up if necessary."""
    analytics.check_storage_size()


def shutdown_analytics() -> None:
    """Shutdown the analytics system."""
    analytics.shutdown()


# Example usage
if __name__ == "__main__":
    # Initialize analytics
    initialize_analytics()
    
    # Track events
    track_event(
        event_type=EventType.USER_ACTION,
        category=EventCategory.USER,
        data={"action": "login", "success": True},
        user_id="user123",
        component="auth"
    )
    
    track_feature_usage(
        feature="search",
        user_id="user123",
        component="search",
        data={"query": "example", "results": 10}
    )
    
    # Track metrics
    track_metric(
        name="response_time",
        value=0.5,
        unit="seconds",
        tags={"endpoint": "/api/search"}
    )
    
    track_performance(
        metric_name="cpu_usage",
        value=25.0,
        unit="percent",
        component="server"
    )
    
    # Query events
    events = query_events(
        event_types=[EventType.USER_ACTION],
        categories=[EventCategory.USER],
        user_id="user123"
    )
    
    # Get event statistics
    event_stats = get_event_statistics(events)
    print(f"Event statistics: {event_stats}")
    
    # Query metrics
    metrics = query_metrics(
        names=["response_time"],
        tags={"endpoint": "/api/search"}
    )
    
    # Get metric statistics
    metric_stats = get_metric_statistics(metrics)
    print(f"Metric statistics: {metric_stats}")
    
    # Aggregate metrics
    aggregated = aggregate_metrics(
        metrics=metrics,
        aggregation="avg",
        group_by=["name"]
    )
    print(f"Aggregated metrics: {aggregated}")
    
    # Shutdown analytics
    shutdown_analytics()
