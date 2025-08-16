"""
Presentation module for the Advanced Analytics system.

This module provides components for visualizing and reporting analytics data,
including dashboards, charts, and exportable reports.
"""

import base64
import io
import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from ..core.core import (AnalyticsComponent, AnalyticsContext, DataCategory,
                        Event, MetricRegistry, MetricType, MetricValue,
                        SecurityClassification, metric_registry)
from ..storage.storage import query_events, query_metrics

# Configure matplotlib to use non-interactive backend
matplotlib.use('Agg')

# Configure logging
logger = logging.getLogger(__name__)

class Visualizer(AnalyticsComponent, ABC):
    """Base class for all visualizers."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.enabled = False
        self.config: Dict[str, Any] = {}
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the visualizer with the provided configuration."""
        self.config = config
        self.enabled = config.get("enabled", True)
        self._logger.info(f"Initialized visualizer: {self.name}")
    
    def shutdown(self) -> None:
        """Shutdown the visualizer and release resources."""
        self.enabled = False
        self._logger.info(f"Shutdown visualizer: {self.name}")
    
    def get_health(self) -> Dict[str, Any]:
        """Get the health status of the visualizer."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "status": "healthy" if self.enabled else "disabled"
        }
    
    @abstractmethod
    def generate_visualization(self, data: Any, options: Dict[str, Any] = None) -> Any:
        """Generate a visualization from the provided data."""
        pass

class ChartVisualizer(Visualizer):
    """Visualizer for generating charts and graphs."""
    
    def __init__(self, name: str = "chart_visualizer"):
        super().__init__(name)
        self._default_width = 10
        self._default_height = 6
        self._default_dpi = 100
        self._default_format = "png"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the chart visualizer."""
        super().initialize(config)
        
        # Set default chart options
        self._default_width = config.get("default_width", 10)
        self._default_height = config.get("default_height", 6)
        self._default_dpi = config.get("default_dpi", 100)
        self._default_format = config.get("default_format", "png")
        
        # Set default style
        plt.style.use(config.get("style", "ggplot"))
    
    def generate_visualization(self, data: Any, options: Dict[str, Any] = None) -> Any:
        """Generate a chart visualization from the provided data."""
        if not self.enabled:
            return None
        
        options = options or {}
        
        # Extract chart options
        chart_type = options.get("chart_type", "line")
        title = options.get("title", "")
        x_label = options.get("x_label", "")
        y_label = options.get("y_label", "")
        width = options.get("width", self._default_width)
        height = options.get("height", self._default_height)
        dpi = options.get("dpi", self._default_dpi)
        output_format = options.get("format", self._default_format)
        
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
            
            # Generate chart based on type
            if chart_type == "line":
                self._generate_line_chart(data, ax, options)
            elif chart_type == "bar":
                self._generate_bar_chart(data, ax, options)
            elif chart_type == "pie":
                self._generate_pie_chart(data, ax, options)
            elif chart_type == "scatter":
                self._generate_scatter_chart(data, ax, options)
            elif chart_type == "histogram":
                self._generate_histogram_chart(data, ax, options)
            elif chart_type == "heatmap":
                self._generate_heatmap_chart(data, ax, options)
            else:
                self._logger.warning(f"Unknown chart type: {chart_type}, defaulting to line chart")
                self._generate_line_chart(data, ax, options)
            
            # Set title and labels
            ax.set_title(title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            
            # Add grid if requested
            if options.get("grid", True):
                ax.grid(True, linestyle="--", alpha=0.7)
            
            # Add legend if there are multiple series
            if options.get("legend", True) and hasattr(ax, "legend"):
                ax.legend()
            
            # Adjust layout
            fig.tight_layout()
            
            # Save to buffer
            buf = io.BytesIO()
            fig.savefig(buf, format=output_format)
            plt.close(fig)
            
            # Return as base64 encoded string
            buf.seek(0)
            image_data = base64.b64encode(buf.read()).decode("utf-8")
            
            return {
                "type": "image",
                "format": output_format,
                "data": image_data,
                "width": width * dpi,
                "height": height * dpi
            }
        
        except Exception as e:
            self._logger.error(f"Error generating chart: {e}")
            return None
    
    def _generate_line_chart(self, data: Any, ax: plt.Axes, options: Dict[str, Any]) -> None:
        """Generate a line chart."""
        # Convert data to DataFrame if it's a list of dictionaries
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError("Data must be a list of dictionaries or a pandas DataFrame")
        
        # Check if we have time series data
        if "timestamp" in df.columns:
            # Set timestamp as index
            df = df.set_index("timestamp")
            
            # Sort by timestamp
            df = df.sort_index()
            
            # Group by dimensions if present
            if "dimensions" in df.columns:
                # Extract dimension of interest
                dimension_key = options.get("dimension_key")
                if dimension_key:
                    # Create a new column for the dimension value
                    df["dimension_value"] = df["dimensions"].apply(
                        lambda d: d.get(dimension_key, "unknown") if isinstance(d, dict) else "unknown"
                    )
                    
                    # Group by dimension value
                    grouped = df.groupby("dimension_value")
                    
                    # Plot each group
                    for name, group in grouped:
                        group["value"].plot(ax=ax, label=name)
                else:
                    # No dimension specified, just plot the values
                    df["value"].plot(ax=ax)
            else:
                # No dimensions, just plot the values
                df["value"].plot(ax=ax)
        else:
            # Not time series data, plot as regular line chart
            df.plot(ax=ax)
    
    def _generate_bar_chart(self, data: Any, ax: plt.Axes, options: Dict[str, Any]) -> None:
        """Generate a bar chart."""
        # Implementation details omitted for brevity
        pass
    
    def _generate_pie_chart(self, data: Any, ax: plt.Axes, options: Dict[str, Any]) -> None:
        """Generate a pie chart."""
        # Implementation details omitted for brevity
        pass
    
    def _generate_scatter_chart(self, data: Any, ax: plt.Axes, options: Dict[str, Any]) -> None:
        """Generate a scatter chart."""
        # Implementation details omitted for brevity
        pass
    
    def _generate_histogram_chart(self, data: Any, ax: plt.Axes, options: Dict[str, Any]) -> None:
        """Generate a histogram chart."""
        # Implementation details omitted for brevity
        pass
    
    def _generate_heatmap_chart(self, data: Any, ax: plt.Axes, options: Dict[str, Any]) -> None:
        """Generate a heatmap chart."""
        # Implementation details omitted for brevity
        pass

class DashboardVisualizer(Visualizer):
    """
    Visualizer for generating interactive dashboards.
    
    This class provides methods for creating comprehensive dashboards
    with multiple charts, tables, and other visualizations.
    """
    
    def __init__(self, name: str = "dashboard_visualizer"):
        """Initialize the dashboard visualizer."""
        super().__init__(name)
        self._chart_visualizer = ChartVisualizer("chart_visualizer")
        self._default_width = 1200
        self._default_height = 800
        self._default_layout = "grid"
        self._default_theme = "light"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the dashboard visualizer with the provided configuration."""
        super().initialize(config)
        
        # Initialize chart visualizer
        self._chart_visualizer.initialize(config.get("chart_visualizer", {}))
        
        # Set default dashboard options
        self._default_width = config.get("default_width", 1200)
        self._default_height = config.get("default_height", 800)
        self._default_layout = config.get("default_layout", "grid")
        self._default_theme = config.get("default_theme", "light")
        
        self._logger.info(f"Initialized dashboard visualizer: {self.name}")
    
    def generate_visualization(self, data: Any, options: Dict[str, Any] = None) -> Any:
        """
        Generate a dashboard visualization from the provided data.
        
        Args:
            data: Dashboard data containing widgets
            options: Dashboard options
            
        Returns:
            Dictionary containing dashboard visualization data
        """
        # Implementation details omitted for brevity
        pass
    
    def _get_theme_color(self, theme: str, element: str) -> str:
        """
        Get a color for a theme element.
        
        Args:
            theme: Theme name
            element: Element name
            
        Returns:
            Color string
        """
        # Light theme colors
        light_colors = {
            "background": "#f5f5f5",
            "text": "#333333",
            "secondary_text": "#666666",
            "widget_background": "#ffffff",
            "border": "#dddddd",
            "header_background": "#eeeeee",
            "header_text": "#333333"
        }
        
        # Dark theme colors
        dark_colors = {
            "background": "#222222",
            "text": "#ffffff",
            "secondary_text": "#aaaaaa",
            "widget_background": "#333333",
            "border": "#444444",
            "header_background": "#444444",
            "header_text": "#ffffff"
        }
        
        # Get colors for theme
        colors = dark_colors if theme == "dark" else light_colors
        
        # Return color for element
        return colors.get(element, "#000000")

class DashboardGenerator:
    """
    Generator for creating dashboards.
    
    This class provides methods for creating and configuring dashboards
    based on analytics data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the dashboard generator.
        
        Args:
            config: Configuration dictionary for the dashboard generator
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self._visualizer = DashboardVisualizer("dashboard_visualizer")
        self._visualizer.initialize(self.config.get("visualizer", {}))
        self._logger = logging.getLogger(f"{__name__}.dashboard_generator")
        self._logger.info("Initialized DashboardGenerator")
    
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
        if not self.enabled:
            self._logger.debug(f"DashboardGenerator is disabled, returning empty dashboard")
            return {"error": "Dashboard generation is disabled"}
        
        try:
            # Get dashboard configuration
            dashboard_config = self._get_dashboard_config(dashboard_id)
            if not dashboard_config:
                return {"error": f"Dashboard not found: {dashboard_id}"}
            
            # Set default time range if not provided
            if not time_range:
                time_range = {
                    "start": datetime.now() - timedelta(days=7),
                    "end": datetime.now()
                }
            
            # Create dashboard data
            dashboard_data = {
                "id": dashboard_id,
                "title": dashboard_config.get("title", f"Dashboard {dashboard_id}"),
                "description": dashboard_config.get("description", ""),
                "user_id": user_id,
                "time_range": time_range,
                "widgets": []
            }
            
            # Generate widgets
            for widget_config in dashboard_config.get("widgets", []):
                widget = self._generate_widget(widget_config, user_id, time_range)
                if widget:
                    dashboard_data["widgets"].append(widget)
            
            return dashboard_data
        
        except Exception as e:
            self._logger.error(f"Error generating dashboard: {e}")
            return {"error": f"Error generating dashboard: {str(e)}"}
    
    def _get_dashboard_config(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Get the configuration for a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard
            
        Returns:
            Dashboard configuration
        """
        # Get dashboards from configuration
        dashboards = self.config.get("dashboards", {})
        
        # Return dashboard configuration if found
        return dashboards.get(dashboard_id, None)
    
    def _generate_widget(self, widget_config: Dict[str, Any], user_id: str,
                        time_range: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a widget for a dashboard.
        
        Args:
            widget_config: Widget configuration
            user_id: ID of the user
            time_range: Time range for the widget data
            
        Returns:
            Widget data
        """
        try:
            widget_type = widget_config.get("type", "chart")
            
            if widget_type == "chart":
                return self._generate_chart_widget(widget_config, user_id, time_range)
            elif widget_type == "text":
                return self._generate_text_widget(widget_config, user_id, time_range)
            elif widget_type == "table":
                return self._generate_table_widget(widget_config, user_id, time_range)
            elif widget_type == "metric":
                return self._generate_metric_widget(widget_config, user_id, time_range)
            else:
                self._logger.warning(f"Unknown widget type: {widget_type}")
                return None
        
        except Exception as e:
            self._logger.error(f"Error generating widget: {e}")
            return None
    
    def _generate_chart_widget(self, widget_config: Dict[str, Any], user_id: str,
                              time_range: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a chart widget.
        
        Args:
            widget_config: Widget configuration
            user_id: ID of the user
            time_range: Time range for the widget data
            
        Returns:
            Widget data
        """
        # Implementation details omitted for brevity
        return {
            "id": widget_config.get("id", "chart"),
            "type": "chart",
            "title": widget_config.get("title", "Chart"),
            "description": widget_config.get("description", ""),
            "chart": {
                "type": "line",
                "data": []
            }
        }
    
    def _generate_text_widget(self, widget_config: Dict[str, Any], user_id: str,
                             time_range: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a text widget.
        
        Args:
            widget_config: Widget configuration
            user_id: ID of the user
            time_range: Time range for the widget data
            
        Returns:
            Widget data
        """
        return {
            "id": widget_config.get("id", "text"),
            "type": "text",
            "title": widget_config.get("title", "Text"),
            "description": widget_config.get("description", ""),
            "content": widget_config.get("content", "")
        }
    
    def _generate_table_widget(self, widget_config: Dict[str, Any], user_id: str,
                              time_range: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a table widget.
        
        Args:
            widget_config: Widget configuration
            user_id: ID of the user
            time_range: Time range for the widget data
            
        Returns:
            Widget data
        """
        return {
            "id": widget_config.get("id", "table"),
            "type": "table",
            "title": widget_config.get("title", "Table"),
            "description": widget_config.get("description", ""),
            "columns": widget_config.get("columns", []),
            "data": []
        }
    
    def _generate_metric_widget(self, widget_config: Dict[str, Any], user_id: str,
                               time_range: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a metric widget.
        
        Args:
            widget_config: Widget configuration
            user_id: ID of the user
            time_range: Time range for the widget data
            
        Returns:
            Widget data
        """
        return {
            "id": widget_config.get("id", "metric"),
            "type": "metric",
            "title": widget_config.get("title", "Metric"),
            "description": widget_config.get("description", ""),
            "value": 0,
            "format": widget_config.get("format", "number"),
            "trend": None,
            "trend_value": None
        }

class ReportGenerator:
    """
    Generator for creating reports.
    
    This class provides methods for creating and configuring reports
    based on analytics data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the report generator.
        
        Args:
            config: Configuration dictionary for the report generator
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self._logger = logging.getLogger(f"{__name__}.report_generator")
        self._logger.info("Initialized ReportGenerator")
    
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
        if not self.enabled:
            self._logger.debug(f"ReportGenerator is disabled, returning empty report")
            return {"error": "Report generation is disabled"}
        
        try:
            # Get report configuration
            report_config = self._get_report_config(report_id)
            if not report_config:
                return {"error": f"Report not found: {report_id}"}
            
            # Create report data
            report_data = {
                "id": report_id,
                "title": report_config.get("title", f"Report {report_id}"),
                "description": report_config.get("description", ""),
                "user_id": user_id,
                "parameters": parameters or {},
                "sections": []
            }
            
            # Generate sections
            for section_config in report_config.get("sections", []):
                section = self._generate_section(section_config, user_id, parameters)
                if section:
                    report_data["sections"].append(section)
            
            return report_data
        
        except Exception as e:
            self._logger.error(f"Error generating report: {e}")
            return {"error": f"Error generating report: {str(e)}"}
    
    def _get_report_config(self, report_id: str) -> Dict[str, Any]:
        """
        Get the configuration for a report.
        
        Args:
            report_id: ID of the report
            
        Returns:
            Report configuration
        """
        # Get reports from configuration
        reports = self.config.get("reports", {})
        
        # Return report configuration if found
        return reports.get(report_id, None)
    
    def _generate_section(self, section_config: Dict[str, Any], user_id: str,
                         parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a section for a report.
        
        Args:
            section_config: Section configuration
            user_id: ID of the user
            parameters: Parameters for the report
            
        Returns:
            Section data
        """
        try:
            section_type = section_config.get("type", "text")
            
            if section_type == "text":
                return self._generate_text_section(section_config, user_id, parameters)
            elif section_type == "chart":
                return self._generate_chart_section(section_config, user_id, parameters)
            elif section_type == "table":
                return self._generate_table_section(section_config, user_id, parameters)
            else:
                self._logger.warning(f"Unknown section type: {section_type}")
                return None
        
        except Exception as e:
            self._logger.error(f"Error generating section: {e}")
            return None
    
    def _generate_text_section(self, section_config: Dict[str, Any], user_id: str,
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a text section.
        
        Args:
            section_config: Section configuration
            user_id: ID of the user
            parameters: Parameters for the report
            
        Returns:
            Section data
        """
        return {
            "id": section_config.get("id", "text"),
            "type": "text",
            "title": section_config.get("title", "Text"),
            "content": section_config.get("content", "")
        }
    
    def _generate_chart_section(self, section_config: Dict[str, Any], user_id: str,
                               parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a chart section.
        
        Args:
            section_config: Section configuration
            user_id: ID of the user
            parameters: Parameters for the report
            
        Returns:
            Section data
        """
        return {
            "id": section_config.get("id", "chart"),
            "type": "chart",
            "title": section_config.get("title", "Chart"),
            "chart": {
                "type": "line",
                "data": []
            }
        }
    
    def _generate_table_section(self, section_config: Dict[str, Any], user_id: str,
                               parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a table section.
        
        Args:
            section_config: Section configuration
            user_id: ID of the user
            parameters: Parameters for the report
            
        Returns:
            Section data
        """
        return {
            "id": section_config.get("id", "table"),
            "type": "table",
            "title": section_config.get("title", "Table"),
            "columns": section_config.get("columns", []),
            "data": []
        }

class ChartGenerator:
    """
    Generator for creating charts.
    
    This class provides methods for creating and configuring charts
    based on analytics data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the chart generator.
        
        Args:
            config: Configuration dictionary for the chart generator
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self._visualizer = ChartVisualizer("chart_visualizer")
        self._visualizer.initialize(self.config.get("visualizer", {}))
        self._logger = logging.getLogger(f"{__name__}.chart_generator")
        self._logger.info("Initialized ChartGenerator")
    
    def generate_chart(self, chart_type: str, data: Any, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a chart.
        
        Args:
            chart_type: Type of chart to generate
            data: Data for the chart
            options: Options for the chart
            
        Returns:
            Chart data structure
        """
        if not self.enabled:
            self._logger.debug(f"ChartGenerator is disabled, returning empty chart")
            return {"error": "Chart generation is disabled"}
        
        try:
            # Set chart type in options
            options = options or {}
            options["chart_type"] = chart_type
            
            # Generate chart
            chart = self._visualizer.generate_visualization(data, options)
            
            return chart
        
        except Exception as e:
            self._logger.error(f"Error generating chart: {e}")
            return {"error": f"Error generating chart: {str(e)}"}

class AlertGenerator:
    """
    Generator for creating alerts.
    
    This class provides methods for creating and configuring alerts
    based on analytics data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the alert generator.
        
        Args:
            config: Configuration dictionary for the alert generator
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self._logger = logging.getLogger(f"{__name__}.alert_generator")
        self._logger.info("Initialized AlertGenerator")
    
    def configure_alert(self, user_id: str, alert_config: Dict[str, Any]) -> str:
        """
        Configure an alert for a user.
        
        Args:
            user_id: ID of the user
            alert_config: Alert configuration
            
        Returns:
            ID of the configured alert
        """
        if not self.enabled:
            self._logger.debug(f"AlertGenerator is disabled, returning empty alert")
            return "alert_disabled"
        
        try:
            # Generate alert ID
            alert_id = f"alert_{user_id}_{int(datetime.now().timestamp())}"
            
            # Store alert configuration
            # In a real implementation, this would be stored in a database
            
            return alert_id
        
        except Exception as e:
            self._logger.error(f"Error configuring alert: {e}")
            return "alert_error"
    
    def generate_performance_alerts(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate performance alerts based on anomalies.
        
        Args:
            anomalies: List of anomalies
            
        Returns:
            List of generated alerts
        """
        if not self.enabled:
            self._logger.debug(f"AlertGenerator is disabled, returning empty alerts")
            return []
        
        try:
            alerts = []
            
            for anomaly in anomalies:
                alert = {
                    "id": f"alert_{int(datetime.now().timestamp())}_{len(alerts)}",
                    "type": "performance",
                    "severity": anomaly.get("severity", "medium"),
                    "component": anomaly.get("component", "unknown"),
                    "metric": anomaly.get("metric", "unknown"),
                    "value": anomaly.get("value", 0),
                    "threshold": anomaly.get("threshold", 0),
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Performance anomaly detected in {anomaly.get('component', 'unknown')}"
                }
                
                alerts.append(alert)
            
            return alerts
        
        except Exception as e:
            self._logger.error(f"Error generating performance alerts: {e}")
            return []

class PresentationManager(AnalyticsComponent):
    """
    Manager for presentation components.
    
    This class provides a unified interface for all presentation components,
    including dashboards, reports, charts, and alerts.
    """
    
    def __init__(self, name: str = "presentation_manager"):
        """
        Initialize the presentation manager.
        
        Args:
            name: Name of the presentation manager
        """
        super().__init__(name)
        self.enabled = False
        self.config: Dict[str, Any] = {}
        self._dashboard_generator = None
        self._report_generator = None
        self._chart_generator = None
        self._alert_generator = None
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the presentation manager with the provided configuration.
        
        Args:
            config: Configuration dictionary for the presentation manager
        """
        super().initialize(config)
        self.config = config
        self.enabled = config.get("enabled", True)
        
        # Initialize generators
        self._dashboard_generator = DashboardGenerator(config.get("dashboard_generator", {}))
        self._report_generator = ReportGenerator(config.get("report_generator", {}))
        self._chart_generator = ChartGenerator(config.get("chart_generator", {}))
        self._alert_generator = AlertGenerator(config.get("alert_generator", {}))
        
        self._logger.info(f"Initialized presentation manager: {self.name}")
    
    def shutdown(self) -> None:
        """Shutdown the presentation manager and release resources."""
        self.enabled = False
        self._logger.info(f"Shutdown presentation manager: {self.name}")
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the presentation manager.
        
        Returns:
            Dictionary containing health information
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "status": "healthy" if self.enabled else "disabled",
            "dashboard_generator": self._dashboard_generator.enabled if self._dashboard_generator else False,
            "report_generator": self._report_generator.enabled if self._report_generator else False,
            "chart_generator": self._chart_generator.enabled if self._chart_generator else False,
            "alert_generator": self._alert_generator.enabled if self._alert_generator else False
        }
    
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
        if not self.enabled:
            self._logger.debug(f"PresentationManager is disabled, returning empty dashboard")
            return {"error": "Presentation manager is disabled"}
        
        if not self._dashboard_generator:
            self._logger.error(f"Dashboard generator is not initialized")
            return {"error": "Dashboard generator is not initialized"}
        
        return self._dashboard_generator.generate_dashboard(dashboard_id, user_id, time_range)
    
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
        if not self.enabled:
            self._logger.debug(f"PresentationManager is disabled, returning empty report")
            return {"error": "Presentation manager is disabled"}
        
        if not self._report_generator:
            self._logger.error(f"Report generator is not initialized")
            return {"error": "Report generator is not initialized"}
        
        return self._report_generator.generate_report(report_id, user_id, parameters)
    
    def generate_chart(self, chart_type: str, data: Any, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a chart.
        
        Args:
            chart_type: Type of chart to generate
            data: Data for the chart
            options: Options for the chart
            
        Returns:
            Chart data structure
        """
        if not self.enabled:
            self._logger.debug(f"PresentationManager is disabled, returning empty chart")
            return {"error": "Presentation manager is disabled"}
        
        if not self._chart_generator:
            self._logger.error(f"Chart generator is not initialized")
            return {"error": "Chart generator is not initialized"}
        
        return self._chart_generator.generate_chart(chart_type, data, options)
    
    def configure_alert(self, user_id: str, alert_config: Dict[str, Any]) -> str:
        """
        Configure an alert for a user.
        
        Args:
            user_id: ID of the user
            alert_config: Alert configuration
            
        Returns:
            ID of the configured alert
        """
        if not self.enabled:
            self._logger.debug(f"PresentationManager is disabled, returning empty alert")
            return "alert_disabled"
        
        if not self._alert_generator:
            self._logger.error(f"Alert generator is not initialized")
            return "alert_error"
        
        return self._alert_generator.configure_alert(user_id, alert_config)
    
    def generate_performance_alerts(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate performance alerts based on anomalies.
        
        Args:
            anomalies: List of anomalies
            
        Returns:
            List of generated alerts
        """
        if not self.enabled:
            self._logger.debug(f"PresentationManager is disabled, returning empty alerts")
            return []
        
        if not self._alert_generator:
            self._logger.error(f"Alert generator is not initialized")
            return []
        
        return self._alert_generator.generate_performance_alerts(anomalies)

# Create global presentation manager instance
presentation_manager = PresentationManager()

def generate_visualization(data: Any, options: Dict[str, Any] = None) -> Any:
    """
    Generate a visualization from the provided data.
    
    Args:
        data: Data for the visualization
        options: Options for the visualization
        
    Returns:
        Visualization data structure
    """
    chart_type = options.get("chart_type", "line") if options else "line"
    return presentation_manager.generate_chart(chart_type, data, options)

def generate_report(report_id: str, user_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate a report for a user.
    
    Args:
        report_id: ID of the report to generate
        user_id: ID of the user requesting the report
        parameters: Parameters for the report
        
    Returns:
        Report data structure
    """
    return presentation_manager.generate_report(report_id, user_id, parameters)
