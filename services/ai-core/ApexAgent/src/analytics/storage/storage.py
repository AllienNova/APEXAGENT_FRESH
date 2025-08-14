"""
Storage module for the Advanced Analytics system.

This module provides components for storing and retrieving analytics data,
including time series metrics, events, and aggregated statistics.
"""

import json
import logging
import os
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.core import (AnalyticsComponent, AnalyticsContext, DataCategory,
                        Event, MetricRegistry, MetricType, MetricValue,
                        SecurityClassification, metric_registry)

# Configure logging
logger = logging.getLogger(__name__)

# Global storage instance for module-level functions
_global_storage_instance: Optional['AnalyticsStorage'] = None

def initialize_storage(config: Dict[str, Any] = None) -> 'AnalyticsStorage':
    """
    Initialize the global storage instance.
    
    Args:
        config: Configuration dictionary for the storage
        
    Returns:
        Initialized storage instance
    """
    global _global_storage_instance
    
    if _global_storage_instance is None:
        _global_storage_instance = AnalyticsStorage("global_analytics_storage")
        _global_storage_instance.initialize(config or {})
        logger.info("Initialized global storage instance")
    
    return _global_storage_instance

def get_storage() -> 'AnalyticsStorage':
    """
    Get the global storage instance.
    
    Returns:
        Global storage instance
        
    Raises:
        RuntimeError: If global storage is not initialized
    """
    if _global_storage_instance is None:
        raise RuntimeError("Global storage instance is not initialized")
    
    return _global_storage_instance

def query_metrics(metric_name: str, start_time: datetime, end_time: datetime,
                 dimensions: Optional[Dict[str, str]] = None,
                 aggregation: Optional[str] = None,
                 interval: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Query metrics within a time range.
    
    Args:
        metric_name: Name of the metric
        start_time: Start time for the query
        end_time: End time for the query
        dimensions: Optional dimensions to filter by
        aggregation: Optional aggregation function (avg, sum, min, max, count)
        interval: Optional time interval for aggregation (e.g., "1h", "1d")
        
    Returns:
        List of metric values matching the query
    """
    storage = get_storage()
    metrics_storage = storage.get_metrics_storage()
    return metrics_storage.query_metrics(
        metric_name, start_time, end_time, dimensions, aggregation, interval
    )

def query_events(event_type: Optional[str] = None,
                start_time: Optional[datetime] = None,
                end_time: Optional[datetime] = None,
                source: Optional[str] = None,
                filters: Optional[Dict[str, Any]] = None,
                limit: int = 100) -> List[Dict[str, Any]]:
    """
    Query events within a time range.
    
    Args:
        event_type: Optional type of events to filter by
        start_time: Optional start time for the query
        end_time: Optional end time for the query
        source: Optional source to filter by
        filters: Optional filters for event data
        limit: Maximum number of events to return
        
    Returns:
        List of events matching the query
    """
    storage = get_storage()
    event_storage = storage.get_event_storage()
    return event_storage.query_events(
        event_type, start_time, end_time, source, filters, limit
    )

class StorageProvider(AnalyticsComponent, ABC):
    """Base class for all storage providers."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.enabled = False
        self.config: Dict[str, Any] = {}
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the storage provider with the provided configuration."""
        self.config = config
        self.enabled = config.get("enabled", True)
        self._logger.info(f"Initialized storage provider: {self.name}")
    
    def shutdown(self) -> None:
        """Shutdown the storage provider and release resources."""
        self.enabled = False
        self._logger.info(f"Shutdown storage provider: {self.name}")
    
    def get_health(self) -> Dict[str, Any]:
        """Get the health status of the storage provider."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "status": "healthy" if self.enabled else "disabled"
        }
    
    @abstractmethod
    def store_metric(self, metric: MetricValue) -> bool:
        """Store a metric value."""
        pass
    
    @abstractmethod
    def store_event(self, event: Event) -> bool:
        """Store an event."""
        pass
    
    @abstractmethod
    def query_metrics(self, metric_name: str, start_time: datetime, end_time: datetime,
                     dimensions: Dict[str, str] = None, aggregation: str = None,
                     interval: str = None) -> List[Dict[str, Any]]:
        """Query metrics within a time range."""
        pass
    
    @abstractmethod
    def query_events(self, event_type: str = None, start_time: datetime = None,
                    end_time: datetime = None, source: str = None,
                    filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query events within a time range."""
        pass

class SQLiteStorageProvider(StorageProvider):
    """Storage provider using SQLite database."""
    
    def __init__(self, name: str = "sqlite_storage_provider"):
        super().__init__(name)
        self._db_path = None
        self._connection = None
        self._lock = threading.RLock()
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the SQLite storage provider."""
        super().initialize(config)
        
        # Get database path from config
        self._db_path = config.get("db_path", "analytics.db")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self._db_path)), exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        
        self._logger.info(f"Initialized SQLite storage provider with database: {self._db_path}")
    
    def shutdown(self) -> None:
        """Shutdown the SQLite storage provider."""
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None
        
        super().shutdown()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        with self._lock:
            if self._connection is None:
                self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
                self._connection.row_factory = sqlite3.Row
            
            return self._connection
    
    def _initialize_database(self) -> None:
        """Initialize the database schema."""
        conn = self._get_connection()
        
        with self._lock:
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                dimensions TEXT
            )
            ''')
            
            # Create events table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                source TEXT NOT NULL,
                data TEXT NOT NULL,
                correlation_id TEXT,
                category TEXT,
                security_classification TEXT
            )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON metrics (metric_name, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type_time ON events (event_type, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_source ON events (source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_correlation ON events (correlation_id)')
            
            conn.commit()
    
    def store_metric(self, metric: MetricValue) -> bool:
        """Store a metric value in the database."""
        if not self.enabled:
            return False
        
        try:
            conn = self._get_connection()
            
            with self._lock:
                cursor = conn.cursor()
                
                # Convert dimensions to JSON string
                dimensions_json = json.dumps(metric.dimensions) if metric.dimensions else None
                
                # Insert metric
                cursor.execute(
                    'INSERT INTO metrics (metric_name, value, timestamp, dimensions) VALUES (?, ?, ?, ?)',
                    (metric.metric_name, float(metric.value), metric.timestamp.isoformat(), dimensions_json)
                )
                
                conn.commit()
                
                return True
        
        except Exception as e:
            self._logger.error(f"Error storing metric: {e}")
            return False
    
    def store_event(self, event: Event) -> bool:
        """Store an event in the database."""
        if not self.enabled:
            return False
        
        try:
            conn = self._get_connection()
            
            with self._lock:
                cursor = conn.cursor()
                
                # Convert data to JSON string
                data_json = json.dumps(event.data)
                
                # Convert category and security classification to strings
                category_str = event.category.value if event.category else None
                security_str = event.security_classification.value if event.security_classification else None
                
                # Insert event
                cursor.execute(
                    '''INSERT INTO events 
                       (event_id, event_type, timestamp, source, data, correlation_id, category, security_classification) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (event.event_id, event.event_type, event.timestamp.isoformat(), event.source,
                     data_json, event.correlation_id, category_str, security_str)
                )
                
                conn.commit()
                
                return True
        
        except Exception as e:
            self._logger.error(f"Error storing event: {e}")
            return False
    
    def query_metrics(self, metric_name: str, start_time: datetime, end_time: datetime,
                     dimensions: Dict[str, str] = None, aggregation: str = None,
                     interval: str = None) -> List[Dict[str, Any]]:
        """Query metrics within a time range."""
        if not self.enabled:
            return []
        
        try:
            conn = self._get_connection()
            
            with self._lock:
                cursor = conn.cursor()
                
                # Base query
                query = 'SELECT * FROM metrics WHERE metric_name = ? AND timestamp >= ? AND timestamp <= ?'
                params = [metric_name, start_time.isoformat(), end_time.isoformat()]
                
                # Add dimensions filter if provided
                if dimensions:
                    # This is a simple implementation that checks if the JSON string contains all key-value pairs
                    # A more robust implementation would use JSON functions if available in SQLite
                    for key, value in dimensions.items():
                        query += f" AND dimensions LIKE ?"
                        params.append(f'%"{key}": "{value}"%')
                
                # Add order by
                query += ' ORDER BY timestamp ASC'
                
                # Execute query
                cursor.execute(query, params)
                
                # Fetch results
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    dimensions_dict = json.loads(row['dimensions']) if row['dimensions'] else {}
                    
                    results.append({
                        'metric_name': row['metric_name'],
                        'value': row['value'],
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'dimensions': dimensions_dict
                    })
                
                # Apply aggregation if requested
                if aggregation and results:
                    if interval:
                        # Group by time interval and apply aggregation
                        interval_seconds = self._parse_interval(interval)
                        grouped_results = self._group_by_interval(results, interval_seconds)
                        
                        aggregated_results = []
                        for timestamp, group in grouped_results.items():
                            values = [item['value'] for item in group]
                            
                            if aggregation == 'avg':
                                agg_value = sum(values) / len(values)
                            elif aggregation == 'sum':
                                agg_value = sum(values)
                            elif aggregation == 'min':
                                agg_value = min(values)
                            elif aggregation == 'max':
                                agg_value = max(values)
                            elif aggregation == 'count':
                                agg_value = len(values)
                            else:
                                agg_value = sum(values) / len(values)  # Default to avg
                            
                            aggregated_results.append({
                                'metric_name': metric_name,
                                'value': agg_value,
                                'timestamp': timestamp,
                                'dimensions': dimensions or {}
                            })
                        
                        return sorted(aggregated_results, key=lambda x: x['timestamp'])
                    else:
                        # Apply aggregation to all results
                        values = [item['value'] for item in results]
                        
                        if aggregation == 'avg':
                            agg_value = sum(values) / len(values)
                        elif aggregation == 'sum':
                            agg_value = sum(values)
                        elif aggregation == 'min':
                            agg_value = min(values)
                        elif aggregation == 'max':
                            agg_value = max(values)
                        elif aggregation == 'count':
                            agg_value = len(values)
                        else:
                            agg_value = sum(values) / len(values)  # Default to avg
                        
                        return [{
                            'metric_name': metric_name,
                            'value': agg_value,
                            'timestamp': start_time,
                            'dimensions': dimensions or {}
                        }]
                
                return results
        
        except Exception as e:
            self._logger.error(f"Error querying metrics: {e}")
            return []
    
    def query_events(self, event_type: str = None, start_time: datetime = None,
                    end_time: datetime = None, source: str = None,
                    filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query events within a time range."""
        if not self.enabled:
            return []
        
        try:
            conn = self._get_connection()
            
            with self._lock:
                cursor = conn.cursor()
                
                # Base query
                query = 'SELECT * FROM events WHERE 1=1'
                params = []
                
                # Add filters
                if event_type:
                    query += ' AND event_type = ?'
                    params.append(event_type)
                
                if start_time:
                    query += ' AND timestamp >= ?'
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += ' AND timestamp <= ?'
                    params.append(end_time.isoformat())
                
                if source:
                    query += ' AND source = ?'
                    params.append(source)
                
                # Add order by and limit
                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                # Execute query
                cursor.execute(query, params)
                
                # Fetch results
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    data_dict = json.loads(row['data'])
                    
                    # Apply data filters if provided
                    if filters:
                        # Simple implementation that checks if all filter key-value pairs are in the data
                        if not all(data_dict.get(k) == v for k, v in filters.items()):
                            continue
                    
                    results.append({
                        'event_id': row['event_id'],
                        'event_type': row['event_type'],
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'source': row['source'],
                        'event_data': data_dict,
                        'correlation_id': row['correlation_id'],
                        'category': row['category'],
                        'security_classification': row['security_classification']
                    })
                
                return results
        
        except Exception as e:
            self._logger.error(f"Error querying events: {e}")
            return []
    
    def _parse_interval(self, interval: str) -> int:
        """
        Parse a time interval string into seconds.
        
        Args:
            interval: Interval string (e.g., "1h", "1d")
            
        Returns:
            Interval in seconds
        """
        if not interval:
            return 3600  # Default to 1 hour
        
        try:
            # Extract number and unit
            import re
            match = re.match(r'(\d+)([smhdw])', interval.lower())
            if not match:
                return 3600  # Default to 1 hour
            
            number, unit = match.groups()
            number = int(number)
            
            # Convert to seconds
            if unit == 's':
                return number
            elif unit == 'm':
                return number * 60
            elif unit == 'h':
                return number * 3600
            elif unit == 'd':
                return number * 86400
            elif unit == 'w':
                return number * 604800
            else:
                return 3600  # Default to 1 hour
        
        except Exception:
            return 3600  # Default to 1 hour
    
    def _group_by_interval(self, metrics: List[Dict[str, Any]], interval_seconds: int) -> Dict[datetime, List[Dict[str, Any]]]:
        """
        Group metrics by time interval.
        
        Args:
            metrics: List of metric dictionaries
            interval_seconds: Interval in seconds
            
        Returns:
            Dictionary mapping interval start times to lists of metrics
        """
        grouped = {}
        
        for metric in metrics:
            # Calculate the start of the interval for this metric
            timestamp = metric['timestamp']
            interval_start = timestamp.replace(
                microsecond=0,
                second=0,
                minute=(timestamp.minute // (interval_seconds // 60)) * (interval_seconds // 60)
            )
            
            if interval_seconds >= 3600:
                # For hourly intervals, round to the hour
                interval_start = interval_start.replace(minute=0)
            
            if interval_seconds >= 86400:
                # For daily intervals, round to the day
                interval_start = interval_start.replace(hour=0)
            
            # Add to the group
            if interval_start not in grouped:
                grouped[interval_start] = []
            
            grouped[interval_start].append(metric)
        
        return grouped

class MemoryStorageProvider(StorageProvider):
    """Storage provider using in-memory storage."""
    
    def __init__(self, name: str = "memory_storage_provider"):
        super().__init__(name)
        self._metrics = []
        self._events = []
        self._lock = threading.RLock()
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the memory storage provider."""
        super().initialize(config)
        self._logger.info("Initialized memory storage provider")
    
    def shutdown(self) -> None:
        """Shutdown the memory storage provider."""
        with self._lock:
            self._metrics = []
            self._events = []
        
        super().shutdown()
    
    def store_metric(self, metric: MetricValue) -> bool:
        """Store a metric value in memory."""
        if not self.enabled:
            return False
        
        with self._lock:
            self._metrics.append(metric)
        
        return True
    
    def store_event(self, event: Event) -> bool:
        """Store an event in memory."""
        if not self.enabled:
            return False
        
        with self._lock:
            self._events.append(event)
        
        return True
    
    def query_metrics(self, metric_name: str, start_time: datetime, end_time: datetime,
                     dimensions: Dict[str, str] = None, aggregation: str = None,
                     interval: str = None) -> List[Dict[str, Any]]:
        """Query metrics within a time range."""
        if not self.enabled:
            return []
        
        with self._lock:
            # Filter metrics
            filtered_metrics = [
                m for m in self._metrics
                if m.metric_name == metric_name
                and m.timestamp >= start_time
                and m.timestamp <= end_time
                and (not dimensions or all(m.dimensions.get(k) == v for k, v in dimensions.items()))
            ]
            
            # Convert to dictionaries
            results = [
                {
                    'metric_name': m.metric_name,
                    'value': m.value,
                    'timestamp': m.timestamp,
                    'dimensions': m.dimensions
                }
                for m in filtered_metrics
            ]
            
            # Apply aggregation if requested
            if aggregation and results:
                if interval:
                    # Group by time interval and apply aggregation
                    interval_seconds = self._parse_interval(interval)
                    grouped_results = self._group_by_interval(results, interval_seconds)
                    
                    aggregated_results = []
                    for timestamp, group in grouped_results.items():
                        values = [item['value'] for item in group]
                        
                        if aggregation == 'avg':
                            agg_value = sum(values) / len(values)
                        elif aggregation == 'sum':
                            agg_value = sum(values)
                        elif aggregation == 'min':
                            agg_value = min(values)
                        elif aggregation == 'max':
                            agg_value = max(values)
                        elif aggregation == 'count':
                            agg_value = len(values)
                        else:
                            agg_value = sum(values) / len(values)  # Default to avg
                        
                        aggregated_results.append({
                            'metric_name': metric_name,
                            'value': agg_value,
                            'timestamp': timestamp,
                            'dimensions': dimensions or {}
                        })
                    
                    return sorted(aggregated_results, key=lambda x: x['timestamp'])
                else:
                    # Apply aggregation to all results
                    values = [item['value'] for item in results]
                    
                    if aggregation == 'avg':
                        agg_value = sum(values) / len(values)
                    elif aggregation == 'sum':
                        agg_value = sum(values)
                    elif aggregation == 'min':
                        agg_value = min(values)
                    elif aggregation == 'max':
                        agg_value = max(values)
                    elif aggregation == 'count':
                        agg_value = len(values)
                    else:
                        agg_value = sum(values) / len(values)  # Default to avg
                    
                    return [{
                        'metric_name': metric_name,
                        'value': agg_value,
                        'timestamp': start_time,
                        'dimensions': dimensions or {}
                    }]
            
            return results
    
    def query_events(self, event_type: str = None, start_time: datetime = None,
                    end_time: datetime = None, source: str = None,
                    filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query events within a time range."""
        if not self.enabled:
            return []
        
        with self._lock:
            # Filter events
            filtered_events = self._events
            
            if event_type:
                filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
            if start_time:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
            
            if end_time:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
            
            if source:
                filtered_events = [e for e in filtered_events if e.source == source]
            
            # Apply data filters if provided
            if filters:
                filtered_events = [
                    e for e in filtered_events
                    if all(e.data.get(k) == v for k, v in filters.items())
                ]
            
            # Sort by timestamp (descending) and apply limit
            sorted_events = sorted(filtered_events, key=lambda e: e.timestamp, reverse=True)
            limited_events = sorted_events[:limit]
            
            # Convert to dictionaries
            results = [
                {
                    'event_id': e.event_id,
                    'event_type': e.event_type,
                    'timestamp': e.timestamp,
                    'source': e.source,
                    'event_data': e.data,
                    'correlation_id': e.correlation_id,
                    'category': e.category.value if e.category else None,
                    'security_classification': e.security_classification.value if e.security_classification else None
                }
                for e in limited_events
            ]
            
            return results
    
    def _parse_interval(self, interval: str) -> int:
        """
        Parse a time interval string into seconds.
        
        Args:
            interval: Interval string (e.g., "1h", "1d")
            
        Returns:
            Interval in seconds
        """
        if not interval:
            return 3600  # Default to 1 hour
        
        try:
            # Extract number and unit
            import re
            match = re.match(r'(\d+)([smhdw])', interval.lower())
            if not match:
                return 3600  # Default to 1 hour
            
            number, unit = match.groups()
            number = int(number)
            
            # Convert to seconds
            if unit == 's':
                return number
            elif unit == 'm':
                return number * 60
            elif unit == 'h':
                return number * 3600
            elif unit == 'd':
                return number * 86400
            elif unit == 'w':
                return number * 604800
            else:
                return 3600  # Default to 1 hour
        
        except Exception:
            return 3600  # Default to 1 hour
    
    def _group_by_interval(self, metrics: List[Dict[str, Any]], interval_seconds: int) -> Dict[datetime, List[Dict[str, Any]]]:
        """
        Group metrics by time interval.
        
        Args:
            metrics: List of metric dictionaries
            interval_seconds: Interval in seconds
            
        Returns:
            Dictionary mapping interval start times to lists of metrics
        """
        grouped = {}
        
        for metric in metrics:
            # Calculate the start of the interval for this metric
            timestamp = metric['timestamp']
            interval_start = timestamp.replace(
                microsecond=0,
                second=0,
                minute=(timestamp.minute // (interval_seconds // 60)) * (interval_seconds // 60)
            )
            
            if interval_seconds >= 3600:
                # For hourly intervals, round to the hour
                interval_start = interval_start.replace(minute=0)
            
            if interval_seconds >= 86400:
                # For daily intervals, round to the day
                interval_start = interval_start.replace(hour=0)
            
            # Add to the group
            if interval_start not in grouped:
                grouped[interval_start] = []
            
            grouped[interval_start].append(metric)
        
        return grouped

class AnalyticsStorage(AnalyticsComponent):
    """
    Main storage component for the analytics system.
    
    This class provides a unified interface for storing and retrieving
    analytics data across different storage types.
    """
    
    def __init__(self, name: str = "analytics_storage"):
        super().__init__(name)
        self.time_series_storage = None
        self.event_storage = None
        self.metrics_storage = None
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the analytics storage with the provided configuration."""
        super().initialize(config)
        
        # Create a default provider
        provider_config = config.get("provider", {})
        provider_type = provider_config.get("type", "memory")
        
        if provider_type == "sqlite":
            provider = SQLiteStorageProvider("default_sqlite_provider")
        else:
            provider = MemoryStorageProvider("default_memory_provider")
        
        provider.initialize(provider_config)
        
        # Initialize storage components
        self.time_series_storage = TimeSeriesStorage("time_series_storage", provider)
        self.event_storage = EventStorage("event_storage", provider)
        self.metrics_storage = MetricsStorage("metrics_storage", provider)
        
        self._logger.info(f"Initialized analytics storage with provider: {provider_type}")
    
    def shutdown(self) -> None:
        """Shutdown the analytics storage and release resources."""
        if self.time_series_storage:
            self.time_series_storage.shutdown()
        
        if self.event_storage:
            self.event_storage.shutdown()
        
        if self.metrics_storage:
            self.metrics_storage.shutdown()
        
        super().shutdown()
    
    def get_time_series_storage(self) -> 'TimeSeriesStorage':
        """Get the time series storage component."""
        return self.time_series_storage
    
    def get_event_storage(self) -> 'EventStorage':
        """Get the event storage component."""
        return self.event_storage
    
    def get_metrics_storage(self) -> 'MetricsStorage':
        """Get the metrics storage component."""
        return self.metrics_storage
    
    def store_usage_data(self, data: Dict[str, Any]) -> bool:
        """
        Store usage data.
        
        Args:
            data: Usage data to store
            
        Returns:
            True if the data was stored successfully, False otherwise
        """
        # Convert to metric value
        metric = MetricValue(
            metric_name=f"usage.{data.get('resource_type', 'unknown')}",
            value=data.get('quantity', 0),
            dimensions={
                'user_id': data.get('user_id'),
                'resource_type': data.get('resource_type', 'unknown')
            },
            timestamp=datetime.now()
        )
        
        return self.time_series_storage.store_metric(metric)
    
    def store_performance_data(self, data: Dict[str, Any]) -> bool:
        """
        Store performance data.
        
        Args:
            data: Performance data to store
            
        Returns:
            True if the data was stored successfully, False otherwise
        """
        # Convert to metric value
        metric = MetricValue(
            metric_name=f"performance.{data.get('component', 'unknown')}.{data.get('operation', 'unknown')}",
            value=data.get('duration_ms', 0),
            dimensions={
                'component': data.get('component', 'unknown'),
                'operation': data.get('operation', 'unknown'),
                'success': str(data.get('success', True))
            },
            timestamp=datetime.now()
        )
        
        return self.time_series_storage.store_metric(metric)
    
    def store_business_metric(self, data: Dict[str, Any]) -> bool:
        """
        Store a business metric.
        
        Args:
            data: Business metric data to store
            
        Returns:
            True if the data was stored successfully, False otherwise
        """
        # Convert to metric value
        metric = MetricValue(
            metric_name=data.get('metric_name', 'unknown'),
            value=data.get('value', 0),
            dimensions=data.get('dimensions', {}),
            timestamp=datetime.now()
        )
        
        return self.metrics_storage.store_metric(metric)
    
    def store_event(self, event: Event) -> bool:
        """
        Store an event.
        
        Args:
            event: Event to store
            
        Returns:
            True if the event was stored successfully, False otherwise
        """
        return self.event_storage.store_event(event)

class TimeSeriesStorage(AnalyticsComponent):
    """
    Storage component for time series data.
    
    This class provides methods for storing and retrieving time series data,
    such as performance metrics and usage statistics.
    """
    
    def __init__(self, name: str, provider: StorageProvider):
        super().__init__(name)
        self.provider = provider
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the time series storage with the provided configuration."""
        super().initialize(config)
        self._logger.info(f"Initialized time series storage: {self.name}")
    
    def shutdown(self) -> None:
        """Shutdown the time series storage and release resources."""
        super().shutdown()
    
    def store_metric(self, metric: MetricValue) -> bool:
        """
        Store a metric value.
        
        Args:
            metric: Metric value to store
            
        Returns:
            True if the metric was stored successfully, False otherwise
        """
        return self.provider.store_metric(metric)
    
    def store_performance_data(self, data: Dict[str, Any], metric: str = None, value: float = None) -> bool:
        """
        Store performance data.
        
        Args:
            data: Performance data to store
            metric: Optional metric name
            value: Optional metric value
            
        Returns:
            True if the data was stored successfully, False otherwise
        """
        # Convert to metric value
        metric_name = metric or f"performance.{data.get('component', 'unknown')}.{data.get('operation', 'unknown')}"
        metric_value = value if value is not None else data.get('duration_ms', 0)
        
        metric_obj = MetricValue(
            metric_name=metric_name,
            value=metric_value,
            dimensions={
                'component': data.get('component', 'unknown'),
                'operation': data.get('operation', 'unknown'),
                'success': str(data.get('success', True))
            },
            timestamp=datetime.now()
        )
        
        return self.store_metric(metric_obj)
    
    def query_metrics(self, metric_name: str, start_time: datetime, end_time: datetime,
                     dimensions: Dict[str, str] = None, aggregation: str = None,
                     interval: str = None) -> List[Dict[str, Any]]:
        """
        Query metrics within a time range.
        
        Args:
            metric_name: Name of the metric
            start_time: Start time for the query
            end_time: End time for the query
            dimensions: Optional dimensions to filter by
            aggregation: Optional aggregation function (avg, sum, min, max, count)
            interval: Optional time interval for aggregation (e.g., "1h", "1d")
            
        Returns:
            List of metric values matching the query
        """
        return self.provider.query_metrics(
            metric_name, start_time, end_time, dimensions, aggregation, interval
        )

class EventStorage(AnalyticsComponent):
    """
    Storage component for events.
    
    This class provides methods for storing and retrieving events,
    such as user actions, system events, and business events.
    """
    
    def __init__(self, name: str, provider: StorageProvider):
        super().__init__(name)
        self.provider = provider
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the event storage with the provided configuration."""
        super().initialize(config)
        self._logger.info(f"Initialized event storage: {self.name}")
    
    def shutdown(self) -> None:
        """Shutdown the event storage and release resources."""
        super().shutdown()
    
    def store_event(self, event: Event) -> bool:
        """
        Store an event.
        
        Args:
            event: Event to store
            
        Returns:
            True if the event was stored successfully, False otherwise
        """
        return self.provider.store_event(event)
    
    def search_events(self, event_types: List[str] = None, user_id: str = None,
                     time_range: Dict[str, Any] = None, filters: Dict[str, Any] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for events.
        
        Args:
            event_types: Types of events to search for
            user_id: Optional user ID to filter events
            time_range: Time range for the events
            filters: Additional filters for the search
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        # Convert event_types to single type for provider API
        event_type = event_types[0] if event_types and len(event_types) == 1 else None
        
        # Convert time_range to start_time and end_time
        start_time = None
        end_time = None
        
        if time_range:
            if 'start' in time_range:
                start_time = datetime.fromisoformat(time_range['start']) if isinstance(time_range['start'], str) else time_range['start']
            
            if 'end' in time_range:
                end_time = datetime.fromisoformat(time_range['end']) if isinstance(time_range['end'], str) else time_range['end']
        
        # Add user_id to filters if provided
        if user_id:
            if not filters:
                filters = {}
            
            filters['user_id'] = user_id
        
        # Query events
        events = self.provider.query_events(
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            filters=filters,
            limit=limit
        )
        
        # Filter by event_types if multiple types provided
        if event_types and len(event_types) > 1:
            events = [e for e in events if e['event_type'] in event_types]
        
        return events

class MetricsStorage(AnalyticsComponent):
    """
    Storage component for business metrics.
    
    This class provides methods for storing and retrieving business metrics,
    such as active users, revenue, and other KPIs.
    """
    
    def __init__(self, name: str, provider: StorageProvider):
        super().__init__(name)
        self.provider = provider
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the metrics storage with the provided configuration."""
        super().initialize(config)
        self._logger.info(f"Initialized metrics storage: {self.name}")
    
    def shutdown(self) -> None:
        """Shutdown the metrics storage and release resources."""
        super().shutdown()
    
    def store_metric(self, metric: MetricValue) -> bool:
        """
        Store a metric value.
        
        Args:
            metric: Metric value to store
            
        Returns:
            True if the metric was stored successfully, False otherwise
        """
        return self.provider.store_metric(metric)
    
    def store_business_metric(self, data: Dict[str, Any], value: float = None) -> bool:
        """
        Store a business metric.
        
        Args:
            data: Business metric data to store
            value: Optional metric value
            
        Returns:
            True if the metric was stored successfully, False otherwise
        """
        # Convert to metric value
        metric_value = value if value is not None else data.get('value', 0)
        
        metric_obj = MetricValue(
            metric_name=data.get('metric_name', 'unknown'),
            value=metric_value,
            dimensions=data.get('dimensions', {}),
            timestamp=datetime.now()
        )
        
        return self.store_metric(metric_obj)
    
    def query_metrics(self, metric_names: List[str], dimensions: Dict[str, str] = None,
                     time_range: Dict[str, Any] = None, aggregation: str = None) -> Dict[str, Any]:
        """
        Query metrics.
        
        Args:
            metric_names: Names of the metrics to query
            dimensions: Optional dimensions to filter by
            time_range: Optional time range for the query
            aggregation: Optional aggregation function (avg, sum, min, max, count)
            
        Returns:
            Dictionary mapping metric names to values
        """
        # Convert time_range to start_time and end_time
        start_time = datetime.now() - timedelta(days=30)  # Default to last 30 days
        end_time = datetime.now()
        
        if time_range:
            if 'start' in time_range:
                start_time = datetime.fromisoformat(time_range['start']) if isinstance(time_range['start'], str) else time_range['start']
            
            if 'end' in time_range:
                end_time = datetime.fromisoformat(time_range['end']) if isinstance(time_range['end'], str) else time_range['end']
        
        # Query each metric
        results = {}
        
        for metric_name in metric_names:
            metric_values = self.provider.query_metrics(
                metric_name, start_time, end_time, dimensions, aggregation
            )
            
            if metric_values:
                # Use the aggregated value if available
                if aggregation:
                    results[metric_name] = metric_values[0]['value']
                else:
                    # Otherwise, use the latest value
                    latest_value = max(metric_values, key=lambda x: x['timestamp'])
                    results[metric_name] = latest_value['value']
            else:
                results[metric_name] = 0
        
        return results
