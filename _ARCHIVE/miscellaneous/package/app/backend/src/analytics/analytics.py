"""
Main module for the Advanced Analytics system.

This module provides the primary entry point for the analytics system,
orchestrating the various components and providing a unified API for
analytics operations.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from .core.core import AnalyticsCore, SecurityClassification
from .collection.collectors import (
    UsageCollector,
    PerformanceCollector,
    BusinessMetricsCollector,
    EventCollector
)
from .processing.processors import (
    DataProcessor,
    AggregationProcessor,
    TrendAnalysisProcessor,
    AnomalyDetectionProcessor
)
from .storage.storage import (
    AnalyticsStorage,
    TimeSeriesStorage,
    EventStorage,
    MetricsStorage,
    StorageProvider,
    MemoryStorageProvider
)
from .presentation.visualization import (
    DashboardGenerator,
    ReportGenerator,
    ChartGenerator,
    AlertGenerator
)
from .integration.integration import (
    AuthIntegration,
    SubscriptionIntegration,
    LLMIntegration,
    DataProtectionIntegration
)

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """
    Main class for the Advanced Analytics system.
    
    This class orchestrates all analytics components and provides a unified
    interface for analytics operations throughout the ApexAgent platform.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Advanced Analytics system.
        
        Args:
            config: Configuration dictionary for the analytics system
        """
        self.config = config or {}
        logger.info("Initializing Advanced Analytics system")
        
        # Initialize core components
        self.core = AnalyticsCore(self.config.get('core', {}))
        
        # Initialize collectors
        self.usage_collector = UsageCollector(self.config.get('usage', {}))
        self.performance_collector = PerformanceCollector(self.config.get('performance', {}))
        self.business_metrics_collector = BusinessMetricsCollector(self.config.get('business', {}))
        self.event_collector = EventCollector(self.config.get('events', {}))
        
        # Initialize processors
        self.data_processor = DataProcessor(self.config.get('processing', {}))
        self.aggregation_processor = AggregationProcessor(self.config.get('aggregation', {}))
        self.trend_processor = TrendAnalysisProcessor(self.config.get('trends', {}))
        self.anomaly_processor = AnomalyDetectionProcessor(self.config.get('anomalies', {}))
        
        # Initialize storage
        # Create a default memory provider for storage components
        self.default_provider = MemoryStorageProvider("default_memory_provider")
        self.default_provider.initialize({"in_memory": True})
        
        # Initialize storage components with the provider
        self.storage = AnalyticsStorage(self.config.get('storage', {}))
        self.time_series_storage = TimeSeriesStorage("time_series_storage", self.default_provider)
        self.event_storage = EventStorage("event_storage", self.default_provider)
        self.metrics_storage = MetricsStorage("metrics_storage", self.default_provider)
        
        # Initialize visualization
        self.dashboard_generator = DashboardGenerator(self.config.get('dashboards', {}))
        self.report_generator = ReportGenerator(self.config.get('reports', {}))
        self.chart_generator = ChartGenerator(self.config.get('charts', {}))
        self.alert_generator = AlertGenerator(self.config.get('alerts', {}))
        
        # Initialize integrations
        self.auth_integration = AuthIntegration(self.config.get('auth_integration', {}))
        self.subscription_integration = SubscriptionIntegration(self.config.get('subscription_integration', {}))
        self.llm_integration = LLMIntegration(self.config.get('llm_integration', {}))
        self.data_protection_integration = DataProtectionIntegration(self.config.get('data_protection_integration', {}))
        
        logger.info("Advanced Analytics system initialized successfully")
    
    def track_usage(self, user_id: str, resource_type: str, quantity: Union[int, float], 
                   metadata: Dict[str, Any] = None) -> str:
        """
        Track usage of a resource by a user.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource being used
            quantity: Amount of resource consumed
            metadata: Additional metadata about the usage
            
        Returns:
            ID of the recorded usage event
        """
        # Verify user through auth integration
        self.auth_integration.verify_user(user_id)
        
        # Check subscription limits through subscription integration
        self.subscription_integration.check_usage_limits(user_id, resource_type, quantity)
        
        # Record the usage
        usage_id = self.usage_collector.record_usage(user_id, resource_type, quantity, metadata)
        
        # Process and store the usage data
        processed_data = self.data_processor.process_usage_data(
            user_id, resource_type, quantity, metadata
        )
        self.storage.store_usage_data(processed_data)
        
        return usage_id
    
    def track_performance(self, component: str, operation: str, duration_ms: float,
                         success: bool, metadata: Dict[str, Any] = None) -> str:
        """
        Track performance metrics for a component operation.
        
        Args:
            component: Name of the component
            operation: Name of the operation
            duration_ms: Duration of the operation in milliseconds
            success: Whether the operation was successful
            metadata: Additional metadata about the operation
            
        Returns:
            ID of the recorded performance event
        """
        # Record the performance metric
        perf_id = self.performance_collector.record_performance(
            component, operation, duration_ms, success, metadata
        )
        
        # Process and store the performance data
        processed_data = self.data_processor.process_performance_data(
            component, operation, duration_ms, success, metadata
        )
        self.time_series_storage.store_performance_data(processed_data)
        
        # Check for anomalies
        anomalies = self.anomaly_processor.detect_performance_anomalies(
            component, operation, duration_ms, success, metadata
        )
        
        if anomalies:
            self.alert_generator.generate_performance_alerts(anomalies)
        
        return perf_id
    
    def track_business_metric(self, metric_name: str, value: Union[int, float],
                             dimensions: Dict[str, str] = None) -> str:
        """
        Track a business metric.
        
        Args:
            metric_name: Name of the metric
            value: Value of the metric
            dimensions: Dimensions for the metric (e.g., region, product)
            
        Returns:
            ID of the recorded business metric
        """
        # Record the business metric
        metric_id = self.business_metrics_collector.record_metric(
            metric_name, value, dimensions
        )
        
        # Process and store the metric
        processed_data = self.data_processor.process_business_metric(
            metric_name, value, dimensions
        )
        self.metrics_storage.store_business_metric(processed_data)
        
        return metric_id
    
    def record_event(self, event_type: str, event_data: Dict[str, Any],
                    user_id: Optional[str] = None) -> str:
        """
        Record an application event.
        
        Args:
            event_type: Type of the event
            event_data: Data associated with the event
            user_id: ID of the user associated with the event (if applicable)
            
        Returns:
            ID of the recorded event
        """
        # If user_id is provided, verify through auth integration
        if user_id:
            self.auth_integration.verify_user(user_id)
        
        # Apply data protection to sensitive data before recording
        # This ensures PII and payment data are properly protected
        protected_event_data = self.data_protection_integration.protect_sensitive_data(
            event_data, 
            SecurityClassification.RESTRICTED
        )
        
        # Record the event with protected data
        event_id = self.event_collector.record_event(event_type, protected_event_data, user_id)
        
        # Process and store the event
        processed_event = self.data_processor.process_event(event_type, protected_event_data, user_id)
        self.event_storage.store_event(processed_event)
        
        return event_id
    
    def generate_dashboard(self, dashboard_id: str, user_id: str,
                          time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a dashboard for a user.
        
        Args:
            dashboard_id: ID of the dashboard to generate
            user_id: ID of the user requesting the dashboard
            time_range: Time range for the dashboard data
            
        Returns:
            Dashboard data structure
        """
        # Verify user through auth integration
        self.auth_integration.verify_user(user_id)
        
        # Check dashboard access through auth integration
        self.auth_integration.check_dashboard_access(user_id, dashboard_id)
        
        # Generate the dashboard
        dashboard = self.dashboard_generator.generate_dashboard(dashboard_id, user_id, time_range)
        
        return dashboard
    
    def generate_report(self, report_id: str, user_id: str, 
                       parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a report for a user.
        
        Args:
            report_id: ID of the report to generate
            user_id: ID of the user requesting the report
            parameters: Parameters for the report
            
        Returns:
            Report data structure
        """
        # Verify user through auth integration
        self.auth_integration.verify_user(user_id)
        
        # Check report access through auth integration
        self.auth_integration.check_report_access(user_id, report_id)
        
        # Generate the report
        report = self.report_generator.generate_report(report_id, user_id, parameters)
        
        return report
    
    def get_usage_trends(self, resource_type: str, time_range: Dict[str, Any],
                        granularity: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage trends for a resource type.
        
        Args:
            resource_type: Type of resource
            time_range: Time range for the trends
            granularity: Granularity of the trend data (hourly, daily, etc.)
            user_id: Optional user ID to filter trends for a specific user
            
        Returns:
            Trend data structure
        """
        # If user_id is provided, verify through auth integration
        if user_id:
            self.auth_integration.verify_user(user_id)
        
        # Get the trend data
        trend_data = self.trend_processor.analyze_usage_trends(
            resource_type, time_range, granularity, user_id
        )
        
        return trend_data
    
    def get_performance_metrics(self, component: str, operation: Optional[str] = None,
                              time_range: Dict[str, Any] = None,
                              aggregation: str = 'avg') -> Dict[str, Any]:
        """
        Get performance metrics for a component.
        
        Args:
            component: Name of the component
            operation: Optional operation to filter metrics
            time_range: Time range for the metrics
            aggregation: Aggregation method (avg, min, max, etc.)
            
        Returns:
            Performance metrics data structure
        """
        # Get the performance metrics
        metrics = self.aggregation_processor.aggregate_performance_metrics(
            component, operation, time_range, aggregation
        )
        
        return metrics
    
    def get_business_metrics(self, metric_names: List[str], 
                           dimensions: Dict[str, str] = None,
                           time_range: Dict[str, Any] = None,
                           aggregation: str = 'sum') -> Dict[str, Any]:
        """
        Get business metrics.
        
        Args:
            metric_names: Names of the metrics to retrieve
            dimensions: Dimensions to filter the metrics
            time_range: Time range for the metrics
            aggregation: Aggregation method (sum, avg, etc.)
            
        Returns:
            Business metrics data structure
        """
        # Get the business metrics
        metrics = self.aggregation_processor.aggregate_business_metrics(
            metric_names, dimensions, time_range, aggregation
        )
        
        return metrics
    
    def search_events(self, event_types: List[str] = None, 
                     user_id: Optional[str] = None,
                     time_range: Dict[str, Any] = None,
                     filters: Dict[str, Any] = None,
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
        # If user_id is provided, verify through auth integration
        if user_id:
            self.auth_integration.verify_user(user_id)
        
        # Search for events
        events = self.event_storage.search_events(
            event_types, user_id, time_range, filters, limit
        )
        
        # Ensure all returned events have proper data protection applied
        # This ensures PII and payment data remain protected when retrieved
        protected_events = []
        for event in events:
            if "event_data" in event:
                # Apply data protection again to ensure consistency
                event["event_data"] = self.data_protection_integration.protect_sensitive_data(
                    event["event_data"],
                    SecurityClassification.RESTRICTED
                )
            protected_events.append(event)
        
        return protected_events
    
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
        # Detect anomalies
        anomalies = self.anomaly_processor.detect_anomalies(
            metric_type, metric_name, time_range, sensitivity
        )
        
        return anomalies
    
    def configure_alerts(self, user_id: str, alert_config: Dict[str, Any]) -> str:
        """
        Configure alerts for a user.
        
        Args:
            user_id: ID of the user
            alert_config: Alert configuration
            
        Returns:
            ID of the configured alert
        """
        # Verify user through auth integration
        self.auth_integration.verify_user(user_id)
        
        # Configure the alert
        alert_id = self.alert_generator.configure_alert(user_id, alert_config)
        
        return alert_id
    
    def get_llm_usage_analytics(self, user_id: Optional[str] = None,
                              model_ids: List[str] = None,
                              time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get analytics for LLM usage.
        
        Args:
            user_id: Optional user ID to filter analytics
            model_ids: Optional list of model IDs to filter analytics
            time_range: Time range for the analytics
            
        Returns:
            LLM usage analytics data structure
        """
        # If user_id is provided, verify through auth integration
        if user_id:
            self.auth_integration.verify_user(user_id)
        
        # Get LLM usage analytics from the LLM integration
        analytics = self.llm_integration.get_usage_analytics(
            provider_id=None,
            model_id=model_ids,
            time_range=time_range
        )
        
        return analytics
    
    def get_subscription_analytics(self, user_id: Optional[str] = None,
                                 subscription_tier: str = None,
                                 time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get analytics for subscription usage.
        
        Args:
            user_id: Optional user ID to filter analytics
            subscription_tier: Optional subscription tier to filter analytics
            time_range: Time range for the analytics
            
        Returns:
            Subscription analytics data structure
        """
        # If user_id is provided, verify through auth integration
        if user_id:
            self.auth_integration.verify_user(user_id)
        
        # Get subscription analytics from the subscription integration
        analytics = self.subscription_integration.get_subscription_analytics(
            user_id=user_id,
            tier=subscription_tier,
            time_range=time_range
        )
        
        return analytics
    
    def verify_data_protection(self, data: Dict[str, Any], 
                              security_level: SecurityClassification = SecurityClassification.RESTRICTED) -> bool:
        """
        Verify that sensitive data is properly protected.
        
        Args:
            data: Data to verify
            security_level: Security classification level
            
        Returns:
            True if data is properly protected, False otherwise
        """
        # Use the data protection integration to verify data protection
        return self.data_protection_integration.verify_data_protection(data, security_level)
