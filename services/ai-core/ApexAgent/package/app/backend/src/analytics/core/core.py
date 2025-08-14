"""
Core module for the Advanced Analytics system.

This module provides the core functionality for the analytics system,
including configuration, initialization, and common utilities.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class SecurityClassification(Enum):
    """Security classification levels for analytics data."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"

class DataCategory(Enum):
    """Categories for analytics data."""
    SYSTEM = "system"
    USER = "user"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USAGE = "usage"
    DIAGNOSTIC = "diagnostic"
    CUSTOM = "custom"

class MetricType(Enum):
    """Types of metrics that can be tracked."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"
    CUSTOM = "custom"

class AnalyticsComponent(ABC):
    """
    Base class for all analytics components.
    
    This abstract class defines the common interface and functionality
    for all components in the analytics system.
    """
    
    def __init__(self, name: str):
        """
        Initialize the analytics component.
        
        Args:
            name: Name of the component
        """
        self.name = name
        self.enabled = False
        self.config: Dict[str, Any] = {}
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the component with the provided configuration.
        
        Args:
            config: Configuration dictionary for the component
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        self._logger.info(f"Initialized component: {self.name}")
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the component and release resources."""
        self.enabled = False
        self._logger.info(f"Shutdown component: {self.name}")
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the component.
        
        Returns:
            Dictionary containing health information
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "status": "healthy" if self.enabled else "disabled"
        }

class AnalyticsContext:
    """
    Context for analytics operations.
    
    This class provides context information for analytics operations,
    including user information, correlation IDs, and security context.
    """
    
    def __init__(self, user_id: Optional[str] = None, 
                correlation_id: Optional[str] = None,
                security_classification: Optional[SecurityClassification] = None):
        """
        Initialize the analytics context.
        
        Args:
            user_id: ID of the user associated with the context
            correlation_id: Correlation ID for tracking related operations
            security_classification: Security classification for the context
        """
        self.user_id = user_id
        self.correlation_id = correlation_id or self._generate_correlation_id()
        self.security_classification = security_classification or SecurityClassification.INTERNAL
        self.timestamp = datetime.now()
        self.attributes: Dict[str, Any] = {}
    
    def _generate_correlation_id(self) -> str:
        """
        Generate a unique correlation ID.
        
        Returns:
            Unique correlation ID
        """
        import uuid
        return str(uuid.uuid4())
    
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set a context attribute.
        
        Args:
            key: Attribute key
            value: Attribute value
        """
        self.attributes[key] = value
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get a context attribute.
        
        Args:
            key: Attribute key
            default: Default value if attribute is not found
            
        Returns:
            Attribute value or default
        """
        return self.attributes.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary.
        
        Returns:
            Dictionary representation of the context
        """
        return {
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "security_classification": self.security_classification.value if self.security_classification else None,
            "timestamp": self.timestamp.isoformat(),
            "attributes": self.attributes
        }

class MetricValue:
    """
    Value object for a metric.
    
    This class represents a single metric value with associated metadata.
    """
    
    def __init__(self, metric_name: str, value: Union[int, float], 
                dimensions: Optional[Dict[str, str]] = None,
                timestamp: Optional[datetime] = None):
        """
        Initialize the metric value.
        
        Args:
            metric_name: Name of the metric
            value: Numeric value of the metric
            dimensions: Optional dimensions for the metric
            timestamp: Optional timestamp for the metric
        """
        self.metric_name = metric_name
        self.value = value
        self.dimensions = dimensions or {}
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metric value to dictionary.
        
        Returns:
            Dictionary representation of the metric value
        """
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "dimensions": self.dimensions,
            "timestamp": self.timestamp.isoformat()
        }

class Event:
    """
    Event data structure.
    
    This class represents an event in the analytics system.
    """
    
    def __init__(self, event_type: str, data: Dict[str, Any],
                source: str, event_id: Optional[str] = None,
                correlation_id: Optional[str] = None,
                timestamp: Optional[datetime] = None,
                category: Optional[DataCategory] = None,
                security_classification: Optional[SecurityClassification] = None):
        """
        Initialize the event.
        
        Args:
            event_type: Type of the event
            data: Data associated with the event
            source: Source of the event
            event_id: Optional ID for the event
            correlation_id: Optional correlation ID for tracking related events
            timestamp: Optional timestamp for the event
            category: Optional category for the event
            security_classification: Optional security classification for the event
        """
        import uuid
        
        self.event_type = event_type
        self.data = data
        self.source = source
        self.event_id = event_id or str(uuid.uuid4())
        self.correlation_id = correlation_id
        self.timestamp = timestamp or datetime.now()
        self.category = category or DataCategory.SYSTEM
        self.security_classification = security_classification or SecurityClassification.INTERNAL
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category.value if self.category else None,
            "security_classification": self.security_classification.value if self.security_classification else None
        }

class MetricRegistry:
    """
    Registry for metrics.
    
    This class provides a registry for tracking and managing metrics.
    """
    
    def __init__(self):
        """Initialize the metric registry."""
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.values: List[MetricValue] = []
        self._logger = logging.getLogger(f"{__name__}.MetricRegistry")
    
    def register_metric(self, name: str, description: Optional[str] = None,
                       metric_type: Union[str, MetricType] = MetricType.GAUGE,
                       category: Optional[str] = None,
                       security_classification: Optional[str] = None,
                       default_dimensions: Optional[Dict[str, str]] = None) -> None:
        """
        Register a metric in the registry.
        
        Args:
            name: Name of the metric
            description: Optional description of the metric
            metric_type: Type of the metric (string or MetricType enum)
            category: Optional category for the metric
            security_classification: Optional security classification for the metric
            default_dimensions: Optional default dimensions for the metric
        """
        if name in self.metrics:
            self._logger.warning(f"Metric already registered: {name}")
            return
        
        # Convert string metric_type to enum if needed
        if isinstance(metric_type, str):
            try:
                metric_type = MetricType(metric_type)
            except ValueError:
                # Default to CUSTOM if not a valid enum value
                self._logger.warning(f"Invalid metric type: {metric_type}, using CUSTOM")
                metric_type = MetricType.CUSTOM
        
        self.metrics[name] = {
            "name": name,
            "type": metric_type,
            "description": description,
            "category": category,
            "security_classification": security_classification,
            "default_dimensions": default_dimensions or {},
            "created_at": datetime.now()
        }
        
        self._logger.debug(f"Registered metric: {name} ({metric_type.value})")
    
    def record_value(self, metric_name: str, value: Union[int, float],
                    dimensions: Optional[Dict[str, str]] = None) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Value to record
            dimensions: Optional dimensions for the metric
        """
        if metric_name not in self.metrics:
            # Auto-register the metric
            self.register_metric(name=metric_name, metric_type=MetricType.GAUGE)
        
        # Merge with default dimensions
        merged_dimensions = dict(self.metrics[metric_name].get("default_dimensions", {}))
        if dimensions:
            merged_dimensions.update(dimensions)
        
        # Create and store the metric value
        metric_value = MetricValue(metric_name, value, merged_dimensions)
        self.values.append(metric_value)
        
        self._logger.debug(f"Recorded metric: {metric_name}={value}")
    
    def get_values(self, metric_name: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 dimensions: Optional[Dict[str, str]] = None) -> List[MetricValue]:
        """
        Get metric values from the registry.
        
        Args:
            metric_name: Optional name of the metric to filter by
            start_time: Optional start time to filter by
            end_time: Optional end time to filter by
            dimensions: Optional dimensions to filter by
            
        Returns:
            List of matching metric values
        """
        filtered_values = self.values
        
        # Apply filters
        if metric_name:
            filtered_values = [v for v in filtered_values if v.metric_name == metric_name]
        
        if start_time:
            filtered_values = [v for v in filtered_values if v.timestamp >= start_time]
        
        if end_time:
            filtered_values = [v for v in filtered_values if v.timestamp <= end_time]
        
        if dimensions:
            filtered_values = [
                v for v in filtered_values
                if all(v.dimensions.get(k) == dimensions[k] for k in dimensions)
            ]
        
        return filtered_values
    
    def clear(self) -> None:
        """Clear all metric values from the registry."""
        self.values = []
        self._logger.debug("Cleared all metric values")

# Create a global metric registry instance
metric_registry = MetricRegistry()

class AnalyticsCore:
    """
    Core class for the Advanced Analytics system.
    
    This class provides the foundation for the analytics system, including
    configuration management, initialization, and common utilities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the analytics core.
        
        Args:
            config: Configuration dictionary for the core
        """
        self.config = config or {}
        self.test_mode = self.config.get('test_mode', False)
        logger.info(f"Initializing AnalyticsCore (test_mode={self.test_mode})")
        
        # Initialize core components
        self._initialize_components()
    
    def _initialize_components(self):
        """
        Initialize core components based on configuration.
        """
        # Set up core utilities
        self.utilities = {}
        
        # Initialize event bus if enabled
        if self.config.get('enable_event_bus', True):
            self.event_bus = self._create_event_bus()
        
        # Initialize metrics registry if enabled
        if self.config.get('enable_metrics_registry', True):
            self.metrics_registry = self._create_metrics_registry()
        
        logger.info("Core components initialized")
    
    def _create_event_bus(self) -> Dict[str, Any]:
        """
        Create and configure the event bus.
        
        Returns:
            Configured event bus
        """
        return {
            'subscribers': {},
            'enabled': True,
            'buffer_size': self.config.get('event_buffer_size', 1000)
        }
    
    def _create_metrics_registry(self) -> Dict[str, Any]:
        """
        Create and configure the metrics registry.
        
        Returns:
            Configured metrics registry
        """
        return {
            'metrics': {},
            'enabled': True,
            'default_aggregation': self.config.get('default_aggregation', 'avg')
        }
    
    def register_utility(self, name: str, utility: Any) -> None:
        """
        Register a utility function or object.
        
        Args:
            name: Name of the utility
            utility: Utility function or object
        """
        self.utilities[name] = utility
        logger.debug(f"Registered utility: {name}")
    
    def get_utility(self, name: str) -> Optional[Any]:
        """
        Get a registered utility.
        
        Args:
            name: Name of the utility
            
        Returns:
            Registered utility or None if not found
        """
        return self.utilities.get(name)
    
    def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event_type: Type of the event
            event_data: Data associated with the event
        """
        if hasattr(self, 'event_bus') and self.event_bus['enabled']:
            subscribers = self.event_bus['subscribers'].get(event_type, [])
            for subscriber in subscribers:
                try:
                    subscriber(event_type, event_data)
                except Exception as e:
                    logger.error(f"Error in event subscriber: {str(e)}")
            
            logger.debug(f"Published event: {event_type}")
    
    def subscribe_to_event(self, event_type: str, callback: callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of the event to subscribe to
            callback: Callback function to invoke when event occurs
        """
        if hasattr(self, 'event_bus'):
            if event_type not in self.event_bus['subscribers']:
                self.event_bus['subscribers'][event_type] = []
            
            self.event_bus['subscribers'][event_type].append(callback)
            logger.debug(f"Subscribed to event: {event_type}")
