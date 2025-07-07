"""
Core module initialization for the Advanced Analytics system.

This module provides the core functionality for the analytics system.
"""

from .core import (
    AnalyticsCore,
    AnalyticsComponent,
    AnalyticsContext,
    DataCategory,
    Event,
    MetricRegistry,
    MetricType,
    MetricValue,
    SecurityClassification,
    metric_registry
)

__all__ = [
    'AnalyticsCore',
    'AnalyticsComponent',
    'AnalyticsContext',
    'DataCategory',
    'Event',
    'MetricRegistry',
    'MetricType',
    'MetricValue',
    'SecurityClassification',
    'metric_registry'
]
