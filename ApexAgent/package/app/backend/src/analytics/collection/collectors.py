"""
Collection module for the Advanced Analytics system.

This module provides data collection capabilities for tracking usage,
performance, events, and business metrics.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..core.core import AnalyticsComponent, DataCategory, MetricType, SecurityClassification

logger = logging.getLogger(__name__)

class BaseCollector:
    """
    Base class for all data collectors.
    
    This class provides common functionality for data collectors.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the base collector.
        
        Args:
            config: Configuration dictionary for the collector
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        logger.debug(f"Initialized {self.__class__.__name__} (enabled={self.enabled})")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize or reinitialize the collector with new configuration.
        
        Args:
            config: Configuration dictionary for the collector
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        logger.debug(f"Reinitialized {self.__class__.__name__} (enabled={self.enabled})")
    
    def _generate_id(self) -> str:
        """
        Generate a unique ID.
        
        Returns:
            Unique ID string
        """
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> int:
        """
        Get the current timestamp.
        
        Returns:
            Current timestamp in milliseconds
        """
        import time
        return int(time.time() * 1000)


class UsageCollector(BaseCollector):
    """
    Collector for resource usage data.
    
    This class provides methods for tracking resource usage across the system.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the usage collector.
        
        Args:
            config: Configuration dictionary for the collector
        """
        super().__init__(config)
        self.usage_records = []
        logger.info("Initialized UsageCollector")
    
    def record_usage(self, user_id: str, resource_type: str, quantity: Union[int, float],
                    metadata: Dict[str, Any] = None) -> str:
        """
        Record usage of a resource.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource being used
            quantity: Amount of resource consumed
            metadata: Additional metadata about the usage
            
        Returns:
            ID of the recorded usage event
        """
        if not self.enabled:
            logger.debug("UsageCollector is disabled, skipping record_usage")
            return self._generate_id()
        
        usage_id = self._generate_id()
        timestamp = self._get_timestamp()
        
        usage_record = {
            'id': usage_id,
            'user_id': user_id,
            'resource_type': resource_type,
            'quantity': quantity,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        
        self.usage_records.append(usage_record)
        logger.debug(f"Recorded usage: {resource_type}={quantity} for user {user_id}")
        
        return usage_id
    
    def get_usage_records(self, user_id: Optional[str] = None,
                         resource_type: Optional[str] = None,
                         start_time: Optional[int] = None,
                         end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get usage records matching the specified criteria.
        
        Args:
            user_id: Optional user ID to filter records
            resource_type: Optional resource type to filter records
            start_time: Optional start time (in milliseconds) to filter records
            end_time: Optional end time (in milliseconds) to filter records
            
        Returns:
            List of matching usage records
        """
        if not self.enabled:
            logger.debug("UsageCollector is disabled, returning empty list")
            return []
        
        filtered_records = self.usage_records
        
        if user_id is not None:
            filtered_records = [r for r in filtered_records if r['user_id'] == user_id]
        
        if resource_type is not None:
            filtered_records = [r for r in filtered_records if r['resource_type'] == resource_type]
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] <= end_time]
        
        return filtered_records


class PerformanceCollector(BaseCollector):
    """
    Collector for performance metrics.
    
    This class provides methods for tracking performance metrics across the system.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the performance collector.
        
        Args:
            config: Configuration dictionary for the collector
        """
        super().__init__(config)
        self.performance_records = []
        self.counter_records = {}
        logger.info("Initialized PerformanceCollector")
    
    def record_performance(self, component: str, operation: str, duration_ms: float,
                          success: bool, metadata: Dict[str, Any] = None) -> str:
        """
        Record a performance metric.
        
        Args:
            component: Name of the component
            operation: Name of the operation
            duration_ms: Duration of the operation in milliseconds
            success: Whether the operation was successful
            metadata: Additional metadata about the operation
            
        Returns:
            ID of the recorded performance metric
        """
        if not self.enabled:
            logger.debug("PerformanceCollector is disabled, skipping record_performance")
            return self._generate_id()
        
        perf_id = self._generate_id()
        timestamp = self._get_timestamp()
        
        perf_record = {
            'id': perf_id,
            'component': component,
            'operation': operation,
            'duration_ms': duration_ms,
            'success': success,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        
        self.performance_records.append(perf_record)
        logger.debug(f"Recorded performance: {component}.{operation}={duration_ms}ms (success={success})")
        
        return perf_id
    
    def increment_counter(self, counter_name: str, value: int = 1, dimensions: Dict[str, str] = None) -> None:
        """
        Increment a counter metric.
        
        Args:
            counter_name: Name of the counter
            value: Value to increment by (default: 1)
            dimensions: Dimensions for the counter (e.g., component, operation)
        """
        if not self.enabled:
            logger.debug("PerformanceCollector is disabled, skipping increment_counter")
            return
        
        # Create a key for the counter based on name and dimensions
        dimension_key = frozenset((dimensions or {}).items())
        counter_key = (counter_name, dimension_key)
        
        # Initialize counter if it doesn't exist
        if counter_key not in self.counter_records:
            self.counter_records[counter_key] = {
                'name': counter_name,
                'value': 0,
                'dimensions': dict(dimension_key),
                'last_updated': self._get_timestamp()
            }
        
        # Increment the counter
        self.counter_records[counter_key]['value'] += value
        self.counter_records[counter_key]['last_updated'] = self._get_timestamp()
        
        logger.debug(f"Incremented counter: {counter_name}+={value} with dimensions {dimensions}")
    
    def get_counter_value(self, counter_name: str, dimensions: Dict[str, str] = None) -> int:
        """
        Get the current value of a counter.
        
        Args:
            counter_name: Name of the counter
            dimensions: Dimensions for the counter
            
        Returns:
            Current value of the counter, or 0 if the counter doesn't exist
        """
        if not self.enabled:
            logger.debug("PerformanceCollector is disabled, returning 0")
            return 0
        
        # Create a key for the counter based on name and dimensions
        dimension_key = frozenset((dimensions or {}).items())
        counter_key = (counter_name, dimension_key)
        
        # Return the counter value if it exists, otherwise 0
        if counter_key in self.counter_records:
            return self.counter_records[counter_key]['value']
        
        return 0
    
    def get_all_counters(self) -> List[Dict[str, Any]]:
        """
        Get all counters.
        
        Returns:
            List of all counters
        """
        if not self.enabled:
            logger.debug("PerformanceCollector is disabled, returning empty list")
            return []
        
        return list(self.counter_records.values())
    
    def record_histogram(self, histogram_name: str, value: float, dimensions: Dict[str, str] = None) -> str:
        """
        Record a value in a histogram.
        
        Args:
            histogram_name: Name of the histogram
            value: Value to record
            dimensions: Dimensions for the histogram
            
        Returns:
            ID of the recorded histogram value
        """
        if not self.enabled:
            logger.debug("PerformanceCollector is disabled, skipping record_histogram")
            return self._generate_id()
        
        # For simplicity, we'll just record this as a performance record with a special type
        perf_id = self._generate_id()
        timestamp = self._get_timestamp()
        
        perf_record = {
            'id': perf_id,
            'type': 'histogram',
            'name': histogram_name,
            'value': value,
            'dimensions': dimensions or {},
            'timestamp': timestamp
        }
        
        self.performance_records.append(perf_record)
        logger.debug(f"Recorded histogram: {histogram_name}={value} with dimensions {dimensions}")
        
        return perf_id
    
    def get_performance_records(self, component: Optional[str] = None,
                              operation: Optional[str] = None,
                              success: Optional[bool] = None,
                              start_time: Optional[int] = None,
                              end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get performance records matching the specified criteria.
        
        Args:
            component: Optional component name to filter records
            operation: Optional operation name to filter records
            success: Optional success flag to filter records
            start_time: Optional start time (in milliseconds) to filter records
            end_time: Optional end time (in milliseconds) to filter records
            
        Returns:
            List of matching performance records
        """
        if not self.enabled:
            logger.debug("PerformanceCollector is disabled, returning empty list")
            return []
        
        filtered_records = self.performance_records
        
        if component is not None:
            filtered_records = [r for r in filtered_records if r.get('component') == component]
        
        if operation is not None:
            filtered_records = [r for r in filtered_records if r.get('operation') == operation]
        
        if success is not None:
            filtered_records = [r for r in filtered_records if r.get('success') == success]
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] <= end_time]
        
        return filtered_records


class BusinessMetricsCollector(BaseCollector):
    """
    Collector for business metrics.
    
    This class provides methods for tracking business metrics across the system.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the business metrics collector.
        
        Args:
            config: Configuration dictionary for the collector
        """
        super().__init__(config)
        self.metric_records = []
        logger.info("Initialized BusinessMetricsCollector")
    
    def record_metric(self, metric_name: str, value: Union[int, float],
                     dimensions: Dict[str, str] = None) -> str:
        """
        Record a business metric.
        
        Args:
            metric_name: Name of the metric
            value: Value of the metric
            dimensions: Dimensions for the metric (e.g., region, product)
            
        Returns:
            ID of the recorded metric
        """
        if not self.enabled:
            logger.debug("BusinessMetricsCollector is disabled, skipping record_metric")
            return self._generate_id()
        
        metric_id = self._generate_id()
        timestamp = self._get_timestamp()
        
        metric_record = {
            'id': metric_id,
            'metric_name': metric_name,
            'value': value,
            'dimensions': dimensions or {},
            'timestamp': timestamp
        }
        
        self.metric_records.append(metric_record)
        logger.debug(f"Recorded business metric: {metric_name}={value}")
        
        return metric_id
    
    def get_metric_records(self, metric_name: Optional[str] = None,
                          dimensions: Dict[str, str] = None,
                          start_time: Optional[int] = None,
                          end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get metric records matching the specified criteria.
        
        Args:
            metric_name: Optional metric name to filter records
            dimensions: Optional dimensions to filter records
            start_time: Optional start time (in milliseconds) to filter records
            end_time: Optional end time (in milliseconds) to filter records
            
        Returns:
            List of matching metric records
        """
        if not self.enabled:
            logger.debug("BusinessMetricsCollector is disabled, returning empty list")
            return []
        
        filtered_records = self.metric_records
        
        if metric_name is not None:
            filtered_records = [r for r in filtered_records if r['metric_name'] == metric_name]
        
        if dimensions is not None:
            filtered_records = [
                r for r in filtered_records if all(
                    r['dimensions'].get(k) == v for k, v in dimensions.items()
                )
            ]
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] <= end_time]
        
        return filtered_records


class EventCollector(BaseCollector):
    """
    Collector for application events.
    
    This class provides methods for tracking events across the system.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the event collector.
        
        Args:
            config: Configuration dictionary for the collector
        """
        super().__init__(config)
        self.event_records = []
        logger.info("Initialized EventCollector")
    
    def record_event(self, event_type: str, event_data: Dict[str, Any],
                    source: str, user_id: Optional[str] = None) -> str:
        """
        Record an application event.
        
        Args:
            event_type: Type of the event
            event_data: Data associated with the event
            source: Source of the event
            user_id: Optional ID of the user associated with the event
            
        Returns:
            ID of the recorded event
        """
        if not self.enabled:
            logger.debug("EventCollector is disabled, skipping record_event")
            return self._generate_id()
        
        event_id = self._generate_id()
        timestamp = self._get_timestamp()
        
        event_record = {
            'id': event_id,
            'event_type': event_type,
            'event_data': event_data or {},
            'source': source,
            'user_id': user_id,
            'timestamp': timestamp
        }
        
        self.event_records.append(event_record)
        logger.debug(f"Recorded event: {event_type} from {source}")
        
        return event_id
    
    def get_event_records(self, event_type: Optional[str] = None,
                         user_id: Optional[str] = None,
                         source: Optional[str] = None,
                         start_time: Optional[int] = None,
                         end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get event records matching the specified criteria.
        
        Args:
            event_type: Optional event type to filter records
            user_id: Optional user ID to filter records
            source: Optional source to filter records
            start_time: Optional start time (in milliseconds) to filter records
            end_time: Optional end time (in milliseconds) to filter records
            
        Returns:
            List of matching event records
        """
        if not self.enabled:
            logger.debug("EventCollector is disabled, returning empty list")
            return []
        
        filtered_records = self.event_records
        
        if event_type is not None:
            filtered_records = [r for r in filtered_records if r['event_type'] == event_type]
        
        if user_id is not None:
            filtered_records = [r for r in filtered_records if r['user_id'] == user_id]
        
        if source is not None:
            filtered_records = [r for r in filtered_records if r['source'] == source]
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] <= end_time]
        
        return filtered_records
