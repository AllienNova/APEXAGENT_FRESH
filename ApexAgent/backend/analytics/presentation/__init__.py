"""
Presentation module initialization for the Advanced Analytics system.

This module provides components for visualizing and reporting analytics data.
"""

from .visualization import (
    ChartVisualizer,
    DashboardVisualizer,
    ReportGenerator,
    PresentationManager,
    presentation_manager,
    generate_visualization,
    generate_report
)

__all__ = [
    'ChartVisualizer',
    'DashboardVisualizer',
    'ReportGenerator',
    'PresentationManager',
    'presentation_manager',
    'generate_visualization',
    'generate_report'
]
