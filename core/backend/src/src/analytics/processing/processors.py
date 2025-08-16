"""
Processing module for the Advanced Analytics system.

This module provides data processing capabilities for analytics data,
including aggregation, trend analysis, and anomaly detection.
"""

import logging
import statistics
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple

from ..core.core import (AnalyticsComponent, AnalyticsContext, DataCategory,
                        Event, MetricRegistry, MetricType, MetricValue,
                        SecurityClassification, metric_registry)

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Base data processor for analytics data.
    
    This class provides methods for processing various types of analytics data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the data processor.
        
        Args:
            config: Configuration dictionary for the processor
        """
        self.config = config or {}
        logger.info("Initialized DataProcessor")
    
    def process_usage_data(self, user_id: str, resource_type: str, 
                          quantity: Union[int, float], 
                          metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process usage data.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource being used
            quantity: Amount of resource consumed
            metadata: Additional metadata about the usage
            
        Returns:
            Processed usage data
        """
        processed_data = {
            'user_id': user_id,
            'resource_type': resource_type,
            'quantity': quantity,
            'metadata': metadata or {},
            'processed': True,
            'timestamp': self._get_timestamp()
        }
        
        logger.debug(f"Processed usage data for {resource_type}")
        return processed_data
    
    def process_performance_data(self, component: str, operation: str, 
                               duration_ms: float, success: bool,
                               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process performance data.
        
        Args:
            component: Name of the component
            operation: Name of the operation
            duration_ms: Duration of the operation in milliseconds
            success: Whether the operation was successful
            metadata: Additional metadata about the operation
            
        Returns:
            Processed performance data
        """
        processed_data = {
            'component': component,
            'operation': operation,
            'duration_ms': duration_ms,
            'success': success,
            'metadata': metadata or {},
            'processed': True,
            'timestamp': self._get_timestamp()
        }
        
        logger.debug(f"Processed performance data for {component}.{operation}")
        return processed_data
    
    def process_business_metric(self, metric_name: str, value: Union[int, float],
                              dimensions: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Process business metric data.
        
        Args:
            metric_name: Name of the metric
            value: Value of the metric
            dimensions: Dimensions for the metric (e.g., region, product)
            
        Returns:
            Processed business metric data
        """
        processed_data = {
            'metric_name': metric_name,
            'value': value,
            'dimensions': dimensions or {},
            'processed': True,
            'timestamp': self._get_timestamp()
        }
        
        logger.debug(f"Processed business metric {metric_name}")
        return processed_data
    
    def process_event(self, event_type: str, event_data: Dict[str, Any],
                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process event data.
        
        Args:
            event_type: Type of the event
            event_data: Data associated with the event
            user_id: ID of the user associated with the event (if applicable)
            
        Returns:
            Processed event data
        """
        processed_data = {
            'event_type': event_type,
            'event_data': event_data,
            'user_id': user_id,
            'processed': True,
            'timestamp': self._get_timestamp()
        }
        
        logger.debug(f"Processed event {event_type}")
        return processed_data
    
    def _get_timestamp(self) -> int:
        """
        Get the current timestamp.
        
        Returns:
            Current timestamp in milliseconds
        """
        return int(time.time() * 1000)


class AggregationProcessor:
    """
    Processor for data aggregation.
    
    This class provides methods for aggregating various types of analytics data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the aggregation processor.
        
        Args:
            config: Configuration dictionary for the processor
        """
        self.config = config or {}
        logger.info("Initialized AggregationProcessor")
    
    def aggregate_performance_metrics(self, component: str, 
                                    operation: Optional[str] = None,
                                    time_range: Dict[str, Any] = None,
                                    aggregation: str = 'avg') -> Dict[str, Any]:
        """
        Aggregate performance metrics.
        
        Args:
            component: Name of the component
            operation: Optional operation to filter metrics
            time_range: Time range for the metrics
            aggregation: Aggregation method (avg, min, max, etc.)
            
        Returns:
            Aggregated performance metrics
        """
        # In a real implementation, this would query the database
        # For now, we'll return mock data
        
        if aggregation == 'avg':
            value = 45.7
        elif aggregation == 'min':
            value = 12.3
        elif aggregation == 'max':
            value = 98.6
        else:
            value = 45.7
        
        result = {
            'component': component,
            'operation': operation,
            'time_range': time_range,
            'aggregation': aggregation,
            'value': value,
            'sample_size': 100,
            'timestamp': self._get_timestamp()
        }
        
        logger.debug(f"Aggregated performance metrics for {component}")
        return result
    
    def aggregate_business_metrics(self, metric_names: List[str], 
                                 dimensions: Dict[str, str] = None,
                                 time_range: Dict[str, Any] = None,
                                 aggregation: str = 'sum') -> Dict[str, Any]:
        """
        Aggregate business metrics.
        
        Args:
            metric_names: Names of the metrics to aggregate
            dimensions: Dimensions to filter the metrics
            time_range: Time range for the metrics
            aggregation: Aggregation method (sum, avg, etc.)
            
        Returns:
            Aggregated business metrics
        """
        # In a real implementation, this would query the database
        # For now, we'll return mock data
        
        result = {
            'time_range': time_range,
            'dimensions': dimensions,
            'aggregation': aggregation,
            'timestamp': self._get_timestamp()
        }
        
        for metric_name in metric_names:
            if aggregation == 'sum':
                value = 1250.0
            elif aggregation == 'avg':
                value = 125.0
            elif aggregation == 'min':
                value = 50.0
            elif aggregation == 'max':
                value = 250.0
            else:
                value = 1250.0
            
            result[metric_name] = {
                'value': value,
                'sample_size': 10
            }
        
        logger.debug(f"Aggregated business metrics: {', '.join(metric_names)}")
        return result
    
    def _get_timestamp(self) -> int:
        """
        Get the current timestamp.
        
        Returns:
            Current timestamp in milliseconds
        """
        return int(time.time() * 1000)


class TrendAnalysisProcessor:
    """
    Processor for trend analysis.
    
    This class provides methods for analyzing trends in analytics data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the trend analysis processor.
        
        Args:
            config: Configuration dictionary for the processor
        """
        self.config = config or {}
        logger.info("Initialized TrendAnalysisProcessor")
    
    def analyze_usage_trends(self, resource_type: str, time_range: Dict[str, Any],
                           granularity: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze usage trends.
        
        Args:
            resource_type: Type of resource
            time_range: Time range for the trends
            granularity: Granularity of the trend data (hourly, daily, etc.)
            user_id: Optional user ID to filter trends for a specific user
            
        Returns:
            Usage trend data
        """
        # In a real implementation, this would query the database
        # For now, we'll return mock data
        
        data_points = []
        
        # Generate mock data points
        if granularity == 'hourly':
            for i in range(24):
                data_points.append({
                    'timestamp': self._get_timestamp() - (23 - i) * 3600 * 1000,
                    'value': 100 + i * 10 + (i % 3) * 5
                })
        elif granularity == 'daily':
            for i in range(7):
                data_points.append({
                    'timestamp': self._get_timestamp() - (6 - i) * 24 * 3600 * 1000,
                    'value': 1000 + i * 100 + (i % 3) * 50
                })
        else:  # Default to daily
            for i in range(7):
                data_points.append({
                    'timestamp': self._get_timestamp() - (6 - i) * 24 * 3600 * 1000,
                    'value': 1000 + i * 100 + (i % 3) * 50
                })
        
        result = {
            'resource_type': resource_type,
            'time_range': time_range,
            'granularity': granularity,
            'user_id': user_id,
            'data_points': data_points,
            'trend_direction': 'increasing',
            'trend_strength': 0.85,
            'timestamp': self._get_timestamp()
        }
        
        logger.debug(f"Analyzed usage trends for {resource_type}")
        return result
    
    def analyze_performance_trends(self, component: str, operation: Optional[str] = None,
                                 time_range: Dict[str, Any] = None,
                                 granularity: str = 'hourly') -> Dict[str, Any]:
        """
        Analyze performance trends.
        
        Args:
            component: Name of the component
            operation: Optional operation to filter trends
            time_range: Time range for the trends
            granularity: Granularity of the trend data (hourly, daily, etc.)
            
        Returns:
            Performance trend data
        """
        # In a real implementation, this would query the database
        # For now, we'll return mock data
        
        data_points = []
        
        # Generate mock data points
        if granularity == 'hourly':
            for i in range(24):
                data_points.append({
                    'timestamp': self._get_timestamp() - (23 - i) * 3600 * 1000,
                    'value': 50 - i * 0.5 + (i % 5) * 2
                })
        elif granularity == 'daily':
            for i in range(7):
                data_points.append({
                    'timestamp': self._get_timestamp() - (6 - i) * 24 * 3600 * 1000,
                    'value': 45 - i * 1.5 + (i % 3) * 3
                })
        else:  # Default to hourly
            for i in range(24):
                data_points.append({
                    'timestamp': self._get_timestamp() - (23 - i) * 3600 * 1000,
                    'value': 50 - i * 0.5 + (i % 5) * 2
                })
        
        result = {
            'component': component,
            'operation': operation,
            'time_range': time_range,
            'granularity': granularity,
            'data_points': data_points,
            'trend_direction': 'decreasing',
            'trend_strength': 0.72,
            'timestamp': self._get_timestamp()
        }
        
        logger.debug(f"Analyzed performance trends for {component}")
        return result
    
    def _get_timestamp(self) -> int:
        """
        Get the current timestamp.
        
        Returns:
            Current timestamp in milliseconds
        """
        return int(time.time() * 1000)


class AnomalyDetectionProcessor:
    """
    Processor for anomaly detection.
    
    This class provides methods for detecting anomalies in analytics data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the anomaly detection processor.
        
        Args:
            config: Configuration dictionary for the processor
        """
        self.config = config or {}
        logger.info("Initialized AnomalyDetectionProcessor")
    
    def detect_anomalies(self, metric_type: str, metric_name: str,
                        time_range: Dict[str, Any],
                        sensitivity: float = 0.05) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metrics.
        
        Args:
            metric_type: Type of metric (usage, performance, business)
            metric_name: Name of the metric
            time_range: Time range for anomaly detection
            sensitivity: Sensitivity threshold for anomaly detection
            
        Returns:
            List of detected anomalies
        """
        # In a real implementation, this would analyze historical data
        # For now, we'll return mock data
        
        anomalies = []
        
        # Generate a mock anomaly
        anomalies.append({
            'metric_type': metric_type,
            'metric_name': metric_name,
            'timestamp': self._get_timestamp() - 3600 * 1000,
            'expected_value': 100.0,
            'actual_value': 250.0,
            'deviation': 1.5,
            'severity': 'high',
            'description': f"Unexpected spike in {metric_name}"
        })
        
        logger.debug(f"Detected {len(anomalies)} anomalies in {metric_name}")
        return anomalies
    
    def detect_performance_anomalies(self, component: str, operation: str,
                                   duration_ms: float, success: bool,
                                   metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Detect anomalies in performance metrics.
        
        Args:
            component: Name of the component
            operation: Name of the operation
            duration_ms: Duration of the operation in milliseconds
            success: Whether the operation was successful
            metadata: Additional metadata about the operation
            
        Returns:
            List of detected anomalies
        """
        # In a real implementation, this would analyze historical data
        # For now, we'll return mock data based on the input
        
        anomalies = []
        
        # Check for duration anomalies
        if duration_ms > 100:
            anomalies.append({
                'metric_type': 'performance',
                'metric_name': f"{component}.{operation}.duration",
                'timestamp': self._get_timestamp(),
                'expected_value': 50.0,
                'actual_value': duration_ms,
                'deviation': (duration_ms - 50.0) / 50.0,
                'severity': 'medium',
                'description': f"Slow operation: {component}.{operation}"
            })
        
        # Check for failure anomalies
        if not success:
            anomalies.append({
                'metric_type': 'performance',
                'metric_name': f"{component}.{operation}.success",
                'timestamp': self._get_timestamp(),
                'expected_value': 1.0,
                'actual_value': 0.0,
                'deviation': 1.0,
                'severity': 'high',
                'description': f"Failed operation: {component}.{operation}"
            })
        
        logger.debug(f"Detected {len(anomalies)} performance anomalies for {component}.{operation}")
        return anomalies
    
    def _get_timestamp(self) -> int:
        """
        Get the current timestamp.
        
        Returns:
            Current timestamp in milliseconds
        """
        return int(time.time() * 1000)


class EventProcessor(AnalyticsComponent):
    """
    Processor for event data.
    
    This class provides methods for processing, analyzing, and correlating
    events from various sources in the system.
    """
    
    def __init__(self, name: str = "event_processor"):
        """
        Initialize the event processor.
        
        Args:
            name: Name of the processor component
        """
        super().__init__(name)
        self.event_buffer = []
        self.event_handlers = {}
        self.event_correlations = {}
        self.max_buffer_size = 1000
        self.retention_period_days = 7
        self._logger = logging.getLogger(f"{__name__}.{name}")
        self._logger.info(f"Initialized EventProcessor: {name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the event processor with the provided configuration.
        
        Args:
            config: Configuration dictionary for the processor
        """
        super().initialize(config)
        
        # Set buffer size
        self.max_buffer_size = config.get("max_buffer_size", 1000)
        
        # Set retention period
        self.retention_period_days = config.get("retention_period_days", 7)
        
        # Register default event handlers
        self._register_default_handlers()
        
        self._logger.info(f"Configured EventProcessor with buffer size {self.max_buffer_size} and retention period {self.retention_period_days} days")
    
    def shutdown(self) -> None:
        """Shutdown the event processor and release resources."""
        self.event_buffer = []
        self.event_handlers = {}
        self.event_correlations = {}
        self._logger.info(f"Shutdown EventProcessor: {self.name}")
        super().shutdown()
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the event processor.
        
        Returns:
            Dictionary containing health information
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "status": "healthy" if self.enabled else "disabled",
            "buffer_size": len(self.event_buffer),
            "buffer_capacity": self.max_buffer_size,
            "handler_count": len(self.event_handlers),
            "correlation_count": len(self.event_correlations)
        }
    
    def process_event(self, event: Event) -> Optional[str]:
        """
        Process an event.
        
        Args:
            event: Event to process
            
        Returns:
            ID of the processed event or None if processing failed
        """
        if not self.enabled:
            self._logger.debug(f"EventProcessor is disabled, skipping process_event: {event.event_type}")
            return None
        
        try:
            # Add event to buffer
            self._add_to_buffer(event)
            
            # Apply event handlers
            self._apply_handlers(event)
            
            # Check for correlations
            self._check_correlations(event)
            
            self._logger.debug(f"Processed event: {event.event_type}")
            return event.id
        
        except Exception as e:
            self._logger.error(f"Error processing event: {e}")
            return None
    
    def register_handler(self, event_type: str, handler_func: callable) -> None:
        """
        Register a handler function for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler_func: Function to call when event is processed
        """
        if not self.enabled:
            self._logger.debug(f"EventProcessor is disabled, skipping register_handler for {event_type}")
            return
        
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler_func)
        self._logger.debug(f"Registered handler for event type: {event_type}")
    
    def register_correlation(self, source_type: str, target_type: str, 
                           correlation_func: callable, 
                           time_window_seconds: int = 300) -> None:
        """
        Register a correlation between two event types.
        
        Args:
            source_type: Source event type
            target_type: Target event type
            correlation_func: Function to call when correlation is detected
            time_window_seconds: Time window for correlation in seconds
        """
        if not self.enabled:
            self._logger.debug(f"EventProcessor is disabled, skipping register_correlation for {source_type} -> {target_type}")
            return
        
        correlation_key = f"{source_type}:{target_type}"
        self.event_correlations[correlation_key] = {
            "source_type": source_type,
            "target_type": target_type,
            "correlation_func": correlation_func,
            "time_window_seconds": time_window_seconds
        }
        
        self._logger.debug(f"Registered correlation: {source_type} -> {target_type} (window: {time_window_seconds}s)")
    
    def query_events(self, event_types: List[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   filters: Dict[str, Any] = None,
                   limit: int = 100) -> List[Event]:
        """
        Query events matching the specified criteria.
        
        Args:
            event_types: Optional list of event types to filter
            start_time: Optional start time to filter events
            end_time: Optional end time to filter events
            filters: Optional additional filters for event properties
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        if not self.enabled:
            self._logger.debug(f"EventProcessor is disabled, returning empty list for query_events")
            return []
        
        # Use current time if end_time not provided
        if end_time is None:
            end_time = datetime.now()
        
        # Use 24 hours ago if start_time not provided
        if start_time is None:
            start_time = end_time - timedelta(days=1)
        
        # Convert to timestamps
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        # Filter events
        filtered_events = []
        for event in self.event_buffer:
            # Check timestamp
            if not (start_timestamp <= event.timestamp <= end_timestamp):
                continue
            
            # Check event type
            if event_types and event.event_type not in event_types:
                continue
            
            # Check additional filters
            if filters:
                match = True
                for key, value in filters.items():
                    if key == "user_id" and event.user_id != value:
                        match = False
                        break
                    elif key in event.properties and event.properties[key] != value:
                        match = False
                        break
                
                if not match:
                    continue
            
            filtered_events.append(event)
        
        # Sort by timestamp (newest first) and apply limit
        filtered_events.sort(key=lambda e: e.timestamp, reverse=True)
        return filtered_events[:limit]
    
    def get_event_counts(self, event_types: List[str] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       group_by: str = None) -> Dict[str, int]:
        """
        Get counts of events by type or other grouping.
        
        Args:
            event_types: Optional list of event types to filter
            start_time: Optional start time to filter events
            end_time: Optional end time to filter events
            group_by: Optional field to group counts by (default: event_type)
            
        Returns:
            Dictionary of event counts
        """
        if not self.enabled:
            self._logger.debug(f"EventProcessor is disabled, returning empty dict for get_event_counts")
            return {}
        
        # Query events
        events = self.query_events(
            event_types=event_types,
            start_time=start_time,
            end_time=end_time,
            limit=10000  # Use a high limit to get accurate counts
        )
        
        # Group by specified field or event_type by default
        group_field = group_by or "event_type"
        counts = {}
        
        for event in events:
            if group_field == "event_type":
                key = event.event_type
            elif group_field == "user_id":
                key = event.user_id or "unknown"
            elif group_field in event.properties:
                key = str(event.properties[group_field])
            else:
                key = "unknown"
            
            if key not in counts:
                counts[key] = 0
            
            counts[key] += 1
        
        return counts
    
    def analyze_event_sequence(self, event_types: List[str],
                             start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None,
                             user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze a sequence of events.
        
        Args:
            event_types: List of event types to analyze
            start_time: Optional start time to filter events
            end_time: Optional end time to filter events
            user_id: Optional user ID to filter events
            
        Returns:
            List of sequence analysis results
        """
        if not self.enabled:
            self._logger.debug(f"EventProcessor is disabled, returning empty list for analyze_event_sequence")
            return []
        
        # Query events
        filters = {"user_id": user_id} if user_id else None
        events = self.query_events(
            event_types=event_types,
            start_time=start_time,
            end_time=end_time,
            filters=filters,
            limit=10000  # Use a high limit to get accurate sequence
        )
        
        # Sort by timestamp (oldest first)
        events.sort(key=lambda e: e.timestamp)
        
        # Analyze sequence
        results = []
        prev_event = None
        
        for event in events:
            if prev_event:
                # Calculate time difference
                time_diff_ms = event.timestamp - prev_event.timestamp
                
                results.append({
                    "from_event": prev_event.event_type,
                    "to_event": event.event_type,
                    "from_timestamp": prev_event.timestamp,
                    "to_timestamp": event.timestamp,
                    "time_diff_ms": time_diff_ms,
                    "user_id": event.user_id
                })
            
            prev_event = event
        
        return results
    
    def _add_to_buffer(self, event: Event) -> None:
        """
        Add an event to the buffer.
        
        Args:
            event: Event to add
        """
        # Add to buffer
        self.event_buffer.append(event)
        
        # Trim buffer if needed
        if len(self.event_buffer) > self.max_buffer_size:
            # Remove oldest events
            self.event_buffer = self.event_buffer[-self.max_buffer_size:]
    
    def _apply_handlers(self, event: Event) -> None:
        """
        Apply registered handlers to an event.
        
        Args:
            event: Event to process
        """
        # Get handlers for this event type
        handlers = self.event_handlers.get(event.event_type, [])
        
        # Add handlers for wildcard event type
        handlers.extend(self.event_handlers.get("*", []))
        
        # Apply handlers
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self._logger.error(f"Error in event handler: {e}")
    
    def _check_correlations(self, event: Event) -> None:
        """
        Check for correlations with other events.
        
        Args:
            event: Event to check
        """
        # Get current time
        now = int(time.time() * 1000)
        
        # Check correlations where this event is the target
        for correlation_key, correlation in self.event_correlations.items():
            source_type, target_type = correlation_key.split(":")
            
            if event.event_type == target_type:
                # Look for source events in the buffer
                time_window_ms = correlation["time_window_seconds"] * 1000
                min_timestamp = now - time_window_ms
                
                for source_event in self.event_buffer:
                    if (source_event.event_type == source_type and 
                        source_event.timestamp >= min_timestamp and
                        source_event.timestamp <= event.timestamp):
                        
                        # Found a correlation, call the correlation function
                        try:
                            correlation["correlation_func"](source_event, event)
                        except Exception as e:
                            self._logger.error(f"Error in correlation function: {e}")
    
    def _register_default_handlers(self) -> None:
        """Register default event handlers."""
        # Register a handler for all events (logging)
        self.register_handler("*", self._log_event_handler)
    
    def _log_event_handler(self, event: Event) -> None:
        """
        Default handler for logging events.
        
        Args:
            event: Event to log
        """
        self._logger.debug(f"Event: {event.event_type} (id: {event.id}, user: {event.user_id})")


class MetricProcessor(AnalyticsComponent):
    """
    Processor for metric data.
    
    This class provides methods for processing, analyzing, and aggregating
    metrics from various sources in the system.
    """
    
    def __init__(self, name: str = "metric_processor"):
        """
        Initialize the metric processor.
        
        Args:
            name: Name of the processor component
        """
        super().__init__(name)
        self.metric_handlers = {}
        self.metric_thresholds = {}
        self.metric_aggregations = {}
        self.retention_period_days = 30
        self._logger = logging.getLogger(f"{__name__}.{name}")
        self._logger.info(f"Initialized MetricProcessor: {name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the metric processor with the provided configuration.
        
        Args:
            config: Configuration dictionary for the processor
        """
        super().initialize(config)
        
        # Set retention period
        self.retention_period_days = config.get("retention_period_days", 30)
        
        # Register default metric handlers
        self._register_default_handlers()
        
        # Register default thresholds if provided
        if "thresholds" in config:
            for threshold_config in config["thresholds"]:
                self.register_threshold(
                    metric_name=threshold_config["metric_name"],
                    threshold_value=threshold_config["value"],
                    comparison=threshold_config.get("comparison", "above"),
                    dimensions=threshold_config.get("dimensions"),
                    handler_func=self._default_threshold_handler
                )
        
        # Register default aggregations if provided
        if "aggregations" in config:
            for agg_config in config["aggregations"]:
                self.register_aggregation(
                    metric_name=agg_config["metric_name"],
                    aggregation_type=agg_config["type"],
                    interval_seconds=agg_config.get("interval_seconds", 300),
                    dimensions=agg_config.get("dimensions")
                )
        
        self._logger.info(f"Configured MetricProcessor with retention period {self.retention_period_days} days")
    
    def shutdown(self) -> None:
        """Shutdown the metric processor and release resources."""
        self.metric_handlers = {}
        self.metric_thresholds = {}
        self.metric_aggregations = {}
        self._logger.info(f"Shutdown MetricProcessor: {self.name}")
        super().shutdown()
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the metric processor.
        
        Returns:
            Dictionary containing health information
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "status": "healthy" if self.enabled else "disabled",
            "handler_count": len(self.metric_handlers),
            "threshold_count": len(self.metric_thresholds),
            "aggregation_count": len(self.metric_aggregations)
        }
    
    def process_metric(self, metric_name: str, value: Union[int, float, bool],
                      metric_type: MetricType = MetricType.GAUGE,
                      dimensions: Dict[str, str] = None,
                      timestamp: Optional[datetime] = None,
                      category: DataCategory = DataCategory.SYSTEM) -> bool:
        """
        Process a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Value of the metric
            metric_type: Type of the metric (gauge, counter, timer, etc.)
            dimensions: Dimensions for the metric (e.g., region, component)
            timestamp: Timestamp for the metric (defaults to current time)
            category: Category of the data
            
        Returns:
            True if processing succeeded, False otherwise
        """
        if not self.enabled:
            self._logger.debug(f"MetricProcessor is disabled, skipping process_metric: {metric_name}")
            return False
        
        try:
            # Use current time if timestamp not provided
            if timestamp is None:
                timestamp = datetime.now()
            
            # Convert boolean values to integers
            if isinstance(value, bool):
                value = 1 if value else 0
            
            # Create metric value object
            metric_value = MetricValue(
                name=metric_name,
                value=value,
                metric_type=metric_type,
                dimensions=dimensions or {},
                timestamp=int(timestamp.timestamp() * 1000),
                category=category
            )
            
            # Apply metric handlers
            self._apply_handlers(metric_value)
            
            # Check thresholds
            self._check_thresholds(metric_value)
            
            # Apply aggregations
            self._apply_aggregations(metric_value)
            
            # Store in registry
            metric_registry.register_metric(metric_value)
            
            self._logger.debug(f"Processed metric: {metric_name}={value}")
            return True
        
        except Exception as e:
            self._logger.error(f"Error processing metric: {e}")
            return False
    
    def register_handler(self, metric_name: str, handler_func: callable) -> None:
        """
        Register a handler function for a specific metric.
        
        Args:
            metric_name: Name of the metric to handle
            handler_func: Function to call when metric is processed
        """
        if not self.enabled:
            self._logger.debug(f"MetricProcessor is disabled, skipping register_handler for {metric_name}")
            return
        
        if metric_name not in self.metric_handlers:
            self.metric_handlers[metric_name] = []
        
        self.metric_handlers[metric_name].append(handler_func)
        self._logger.debug(f"Registered handler for metric: {metric_name}")
    
    def register_threshold(self, metric_name: str, threshold_value: float,
                         comparison: str = "above", dimensions: Dict[str, str] = None,
                         handler_func: callable = None) -> None:
        """
        Register a threshold for a metric.
        
        Args:
            metric_name: Name of the metric
            threshold_value: Threshold value
            comparison: Comparison type (above, below, equal)
            dimensions: Dimensions for the metric
            handler_func: Function to call when threshold is crossed
        """
        if not self.enabled:
            self._logger.debug(f"MetricProcessor is disabled, skipping register_threshold for {metric_name}")
            return
        
        # Create dimension key
        dimension_key = self._create_dimension_key(dimensions)
        
        # Create threshold key
        threshold_key = f"{metric_name}:{dimension_key}:{comparison}"
        
        # Register threshold
        self.metric_thresholds[threshold_key] = {
            "metric_name": metric_name,
            "dimensions": dimensions or {},
            "threshold_value": threshold_value,
            "comparison": comparison,
            "handler_func": handler_func or self._default_threshold_handler,
            "last_triggered": 0,
            "trigger_count": 0
        }
        
        self._logger.debug(f"Registered threshold for {metric_name}: {comparison} {threshold_value}")
    
    def register_aggregation(self, metric_name: str, aggregation_type: str,
                           interval_seconds: int = 300,
                           dimensions: Dict[str, str] = None) -> None:
        """
        Register an aggregation for a metric.
        
        Args:
            metric_name: Name of the metric
            aggregation_type: Type of aggregation (sum, avg, min, max)
            interval_seconds: Interval for aggregation in seconds
            dimensions: Dimensions for the metric
        """
        if not self.enabled:
            self._logger.debug(f"MetricProcessor is disabled, skipping register_aggregation for {metric_name}")
            return
        
        # Create dimension key
        dimension_key = self._create_dimension_key(dimensions)
        
        # Create aggregation key
        aggregation_key = f"{metric_name}:{dimension_key}:{aggregation_type}"
        
        # Register aggregation
        self.metric_aggregations[aggregation_key] = {
            "metric_name": metric_name,
            "dimensions": dimensions or {},
            "aggregation_type": aggregation_type,
            "interval_seconds": interval_seconds,
            "values": [],
            "last_aggregated": 0
        }
        
        self._logger.debug(f"Registered aggregation for {metric_name}: {aggregation_type} every {interval_seconds}s")
    
    def query_metrics(self, metric_name: str, start_time: datetime, end_time: datetime,
                    dimensions: Dict[str, str] = None, aggregation: str = None,
                    interval: str = None) -> List[Dict[str, Any]]:
        """
        Query metrics matching the specified criteria.
        
        Args:
            metric_name: Name of the metric
            start_time: Start time for the query
            end_time: End time for the query
            dimensions: Optional dimensions to filter by
            aggregation: Optional aggregation to apply (avg, sum, min, max)
            interval: Optional interval for aggregation (e.g., "1m", "5m", "1h")
            
        Returns:
            List of metric values
        """
        if not self.enabled:
            self._logger.debug(f"MetricProcessor is disabled, returning empty list for query_metrics")
            return []
        
        # Convert to timestamps
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        # Query metrics from registry
        metrics = metric_registry.query_metrics(
            metric_name=metric_name,
            dimensions=dimensions,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )
        
        # Apply aggregation if specified
        if aggregation and interval:
            metrics = self._aggregate_metrics(metrics, aggregation, interval)
        
        return metrics
    
    def get_metric_statistics(self, metric_name: str, start_time: datetime, end_time: datetime,
                            dimensions: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Get statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            start_time: Start time for the query
            end_time: End time for the query
            dimensions: Optional dimensions to filter by
            
        Returns:
            Dictionary containing metric statistics
        """
        if not self.enabled:
            self._logger.debug(f"MetricProcessor is disabled, returning empty dict for get_metric_statistics")
            return {}
        
        # Query metrics
        metrics = self.query_metrics(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            dimensions=dimensions
        )
        
        if not metrics:
            return {
                "metric_name": metric_name,
                "dimensions": dimensions or {},
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "sum": None,
                "std_dev": None,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        
        # Extract values
        values = [m["value"] for m in metrics]
        
        # Calculate statistics
        count = len(values)
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / count
        sum_val = sum(values)
        
        # Calculate standard deviation
        if count > 1:
            std_dev = statistics.stdev(values)
        else:
            std_dev = 0
        
        return {
            "metric_name": metric_name,
            "dimensions": dimensions or {},
            "count": count,
            "min": min_val,
            "max": max_val,
            "avg": avg_val,
            "sum": sum_val,
            "std_dev": std_dev,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    
    def detect_anomalies(self, metric_name: str, start_time: datetime, end_time: datetime,
                       dimensions: Dict[str, str] = None,
                       sensitivity: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a metric.
        
        Args:
            metric_name: Name of the metric
            start_time: Start time for the query
            end_time: End time for the query
            dimensions: Optional dimensions to filter by
            sensitivity: Sensitivity threshold for anomaly detection (standard deviations)
            
        Returns:
            List of detected anomalies
        """
        if not self.enabled:
            self._logger.debug(f"MetricProcessor is disabled, returning empty list for detect_anomalies")
            return []
        
        # Get statistics for baseline period (before start_time)
        baseline_end = start_time
        baseline_start = baseline_end - (end_time - start_time) * 2  # Use twice the query period for baseline
        
        baseline_stats = self.get_metric_statistics(
            metric_name=metric_name,
            start_time=baseline_start,
            end_time=baseline_end,
            dimensions=dimensions
        )
        
        if baseline_stats["count"] < 2:
            self._logger.debug(f"Not enough baseline data for anomaly detection: {metric_name}")
            return []
        
        # Query metrics for the target period
        metrics = self.query_metrics(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            dimensions=dimensions
        )
        
        # Detect anomalies
        anomalies = []
        baseline_avg = baseline_stats["avg"]
        baseline_std = baseline_stats["std_dev"]
        
        for metric in metrics:
            value = metric["value"]
            deviation = abs(value - baseline_avg) / baseline_std if baseline_std > 0 else 0
            
            if deviation >= sensitivity:
                # This is an anomaly
                anomalies.append({
                    "metric_name": metric_name,
                    "dimensions": dimensions or {},
                    "timestamp": metric["timestamp"],
                    "value": value,
                    "baseline_avg": baseline_avg,
                    "baseline_std": baseline_std,
                    "deviation": deviation,
                    "direction": "above" if value > baseline_avg else "below"
                })
        
        self._logger.debug(f"Detected {len(anomalies)} anomalies in {metric_name}")
        return anomalies
    
    def _apply_handlers(self, metric_value: MetricValue) -> None:
        """
        Apply registered handlers to a metric.
        
        Args:
            metric_value: Metric value to process
        """
        # Get handlers for this metric
        handlers = self.metric_handlers.get(metric_value.name, [])
        
        # Add handlers for wildcard metric
        handlers.extend(self.metric_handlers.get("*", []))
        
        # Apply handlers
        for handler in handlers:
            try:
                handler(metric_value)
            except Exception as e:
                self._logger.error(f"Error in metric handler: {e}")
    
    def _check_thresholds(self, metric_value: MetricValue) -> None:
        """
        Check if a metric crosses any registered thresholds.
        
        Args:
            metric_value: Metric value to check
        """
        # Create dimension key
        dimension_key = self._create_dimension_key(metric_value.dimensions)
        
        # Check all thresholds for this metric
        for comparison in ["above", "below", "equal"]:
            threshold_key = f"{metric_value.name}:{dimension_key}:{comparison}"
            
            if threshold_key in self.metric_thresholds:
                threshold = self.metric_thresholds[threshold_key]
                threshold_value = threshold["threshold_value"]
                
                # Check if threshold is crossed
                threshold_crossed = False
                
                if comparison == "above" and metric_value.value > threshold_value:
                    threshold_crossed = True
                elif comparison == "below" and metric_value.value < threshold_value:
                    threshold_crossed = True
                elif comparison == "equal" and metric_value.value == threshold_value:
                    threshold_crossed = True
                
                if threshold_crossed:
                    # Update threshold state
                    threshold["last_triggered"] = metric_value.timestamp
                    threshold["trigger_count"] += 1
                    
                    # Call threshold handler
                    try:
                        threshold["handler_func"](
                            metric_value=metric_value,
                            threshold_value=threshold_value,
                            comparison=comparison
                        )
                    except Exception as e:
                        self._logger.error(f"Error in threshold handler: {e}")
    
    def _apply_aggregations(self, metric_value: MetricValue) -> None:
        """
        Apply registered aggregations to a metric.
        
        Args:
            metric_value: Metric value to aggregate
        """
        # Create dimension key
        dimension_key = self._create_dimension_key(metric_value.dimensions)
        
        # Check all aggregations for this metric
        for aggregation_type in ["sum", "avg", "min", "max"]:
            aggregation_key = f"{metric_value.name}:{dimension_key}:{aggregation_type}"
            
            if aggregation_key in self.metric_aggregations:
                aggregation = self.metric_aggregations[aggregation_key]
                
                # Add value to aggregation
                aggregation["values"].append({
                    "value": metric_value.value,
                    "timestamp": metric_value.timestamp
                })
                
                # Check if it's time to aggregate
                now = int(time.time() * 1000)
                interval_ms = aggregation["interval_seconds"] * 1000
                
                if now - aggregation["last_aggregated"] >= interval_ms:
                    # Time to aggregate
                    self._perform_aggregation(aggregation_key)
    
    def _perform_aggregation(self, aggregation_key: str) -> None:
        """
        Perform an aggregation.
        
        Args:
            aggregation_key: Key of the aggregation to perform
        """
        if aggregation_key not in self.metric_aggregations:
            return
        
        aggregation = self.metric_aggregations[aggregation_key]
        values = aggregation["values"]
        
        if not values:
            return
        
        # Calculate aggregated value
        if aggregation["aggregation_type"] == "sum":
            agg_value = sum(v["value"] for v in values)
        elif aggregation["aggregation_type"] == "avg":
            agg_value = sum(v["value"] for v in values) / len(values)
        elif aggregation["aggregation_type"] == "min":
            agg_value = min(v["value"] for v in values)
        elif aggregation["aggregation_type"] == "max":
            agg_value = max(v["value"] for v in values)
        else:
            agg_value = sum(v["value"] for v in values)
        
        # Create aggregated metric name
        agg_metric_name = f"{aggregation['metric_name']}.{aggregation['aggregation_type']}.{aggregation['interval_seconds']}s"
        
        # Process aggregated metric
        now = int(time.time() * 1000)
        self.process_metric(
            metric_name=agg_metric_name,
            value=agg_value,
            metric_type=MetricType.GAUGE,
            dimensions=aggregation["dimensions"],
            timestamp=datetime.fromtimestamp(now / 1000)
        )
        
        # Update aggregation state
        aggregation["last_aggregated"] = now
        aggregation["values"] = []
    
    def _create_dimension_key(self, dimensions: Dict[str, str] = None) -> str:
        """
        Create a key string from dimensions.
        
        Args:
            dimensions: Dimensions dictionary
            
        Returns:
            String key for the dimensions
        """
        if not dimensions:
            return "default"
        
        # Sort dimensions by key to ensure consistent keys
        sorted_dimensions = sorted(dimensions.items())
        return ",".join(f"{k}={v}" for k, v in sorted_dimensions)
    
    def _register_default_handlers(self) -> None:
        """Register default metric handlers."""
        # Register a handler for all metrics (logging)
        self.register_handler("*", self._log_metric_handler)
    
    def _log_metric_handler(self, metric_value: MetricValue) -> None:
        """
        Default handler for logging metrics.
        
        Args:
            metric_value: Metric value to log
        """
        self._logger.debug(f"Metric: {metric_value.name}={metric_value.value} ({metric_value.metric_type.name})")
    
    def _default_threshold_handler(self, metric_value: MetricValue,
                                 threshold_value: float,
                                 comparison: str) -> None:
        """
        Default handler for threshold crossings.
        
        Args:
            metric_value: Metric value that crossed the threshold
            threshold_value: Threshold value
            comparison: Comparison type (above, below, equal)
        """
        self._logger.info(
            f"Threshold crossed: {metric_value.name}={metric_value.value} is {comparison} {threshold_value}"
        )
    
    def _aggregate_metrics(self, metrics: List[Dict[str, Any]], aggregation: str,
                         interval: str) -> List[Dict[str, Any]]:
        """
        Aggregate metrics by time interval.
        
        Args:
            metrics: List of metrics to aggregate
            aggregation: Aggregation type (avg, sum, min, max)
            interval: Interval for aggregation (e.g., "1m", "5m", "1h")
            
        Returns:
            List of aggregated metrics
        """
        # Parse interval
        interval_seconds = self._parse_interval(interval)
        if not interval_seconds:
            return metrics
        
        # Group metrics by interval
        intervals = {}
        for metric in metrics:
            # Calculate interval start time
            timestamp = metric["timestamp"]
            interval_start = timestamp - (timestamp % (interval_seconds * 1000))
            
            if interval_start not in intervals:
                intervals[interval_start] = []
            
            intervals[interval_start].append(metric)
        
        # Aggregate values in each interval
        result = []
        for interval_start, interval_metrics in sorted(intervals.items()):
            values = [m["value"] for m in interval_metrics]
            dimensions = interval_metrics[0]["dimensions"]  # Use dimensions from first metric
            
            # Calculate aggregated value
            if aggregation == "avg":
                agg_value = sum(values) / len(values)
            elif aggregation == "sum":
                agg_value = sum(values)
            elif aggregation == "min":
                agg_value = min(values)
            elif aggregation == "max":
                agg_value = max(values)
            else:
                agg_value = sum(values) / len(values)  # Default to avg
            
            result.append({
                "timestamp": interval_start,
                "value": agg_value,
                "dimensions": dimensions,
                "count": len(values)
            })
        
        return result
    
    def _parse_interval(self, interval: str) -> Optional[int]:
        """
        Parse an interval string to seconds.
        
        Args:
            interval: Interval string (e.g., "1m", "5m", "1h")
            
        Returns:
            Interval in seconds or None if invalid
        """
        if not interval:
            return None
        
        try:
            # Extract number and unit
            if interval.endswith("s"):
                return int(interval[:-1])
            elif interval.endswith("m"):
                return int(interval[:-1]) * 60
            elif interval.endswith("h"):
                return int(interval[:-1]) * 3600
            elif interval.endswith("d"):
                return int(interval[:-1]) * 86400
            else:
                return int(interval)
        except ValueError:
            return None
