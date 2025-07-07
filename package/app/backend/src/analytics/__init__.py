"""
Aideon AI Lite - Analytics Module
Enterprise-grade analytics system with real-time processing and visualization

This module provides comprehensive analytics capabilities including:
- Real-time performance monitoring
- Business intelligence and reporting
- Advanced data visualization
- Anomaly detection and insights
- Enterprise-grade integration and orchestration

All mock data has been eliminated and replaced with production-ready
GCP services including Cloud Monitoring, BigQuery, and Firestore.
"""

from .integration_service import (
    AnalyticsIntegrationService,
    AnalyticsConfig,
    AnalyticsMetrics,
    ComponentHealth
)

from .cloud_monitoring_service import CloudMonitoringService

from .presentation.visualization import (
    RealTimeVisualizationService,
    DashboardConfig,
    VisualizationData
)

# Version information
__version__ = "2.0.0"
__status__ = "Production Ready"

# Export main integration service instance
__all__ = [
    # Main integration service
    "AnalyticsIntegrationService",
    
    # Configuration and data classes
    "AnalyticsConfig",
    "AnalyticsMetrics", 
    "ComponentHealth",
    "DashboardConfig",
    "VisualizationData",
    
    # Individual services
    "CloudMonitoringService",
    "RealTimeVisualizationService",
    
    # Module metadata
    "__version__",
    "__status__"
]

# Module-level convenience functions
async def get_analytics_overview(time_range: str = "1h"):
    """
    Get comprehensive analytics overview
    
    Args:
        time_range: Time range for analytics (1h, 24h, 7d, 30d)
        
    Returns:
        Comprehensive analytics metrics
    """
    from .integration_service import analytics_integration
    return await analytics_integration.get_comprehensive_analytics(time_range)

async def get_dashboard_data(dashboard_type: str = "overview"):
    """
    Get real-time dashboard data
    
    Args:
        dashboard_type: Type of dashboard (overview, performance, business)
        
    Returns:
        Real-time dashboard data
    """
    from .integration_service import analytics_integration
    return await analytics_integration.get_real_time_dashboard_data(dashboard_type)

async def check_system_health():
    """
    Check health of all analytics components
    
    Returns:
        System health status
    """
    from .integration_service import analytics_integration
    return await analytics_integration.perform_health_check()

async def initialize_analytics():
    """
    Initialize the analytics system
    
    Returns:
        Initialization status
    """
    from .integration_service import analytics_integration
    return await analytics_integration.initialize()

# Module initialization message
import logging
logger = logging.getLogger(__name__)
logger.info(f"Aideon Analytics Module v{__version__} - {__status__}")
logger.info("Enterprise-grade analytics with GCP integration loaded successfully")


