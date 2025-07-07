"""
Performance Monitor for Dr. TARDIS Gemini Live API Integration.

This module provides comprehensive monitoring and analytics for tracking
system performance and resource utilization.

Classes:
    PerformanceMonitor: Tracks and analyzes system performance metrics

Author: Manus Agent
Date: May 26, 2025
"""

import json
import logging
import os
import time
import threading
from collections import deque
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable, Deque

class MetricType(Enum):
    """Enumeration of metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class PerformanceMonitor:
    """
    Tracks and analyzes system performance metrics.
    
    Features:
    - Real-time performance monitoring
    - Resource utilization tracking
    - Response time measurement
    - Bottleneck identification
    - Performance trend analysis
    - Configurable alerting thresholds
    
    Attributes:
        metrics (Dict): Dictionary of collected metrics
        config (Dict): Configuration settings
        logger: Logger instance
    """
    
    def __init__(
        self,
        metrics_dir: Optional[Union[str, Path]] = None,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the PerformanceMonitor.
        
        Args:
            metrics_dir: Directory for metrics data, defaults to 'metrics' in current directory
            config: Configuration settings
            logger: Logger instance, if None a new logger will be created
        """
        # Set up basic configuration
        self.metrics_dir = Path(metrics_dir) if metrics_dir else Path("metrics")
        self.config = config or {
            "collection_interval": 5,  # seconds
            "retention_period": 86400,  # 24 hours in seconds
            "alert_thresholds": {
                "response_time": 2.0,  # seconds
                "cpu_usage": 80.0,  # percent
                "memory_usage": 80.0,  # percent
            },
            "metrics_to_collect": ["response_time", "cpu_usage", "memory_usage", "api_calls"],
        }
        
        # Create metrics directory if it doesn't exist
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        # Set up logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("performance_monitor")
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Initialize metrics storage
        self.metrics = {}
        for metric_name in self.config["metrics_to_collect"]:
            self.metrics[metric_name] = {
                "type": self._determine_metric_type(metric_name),
                "values": deque(maxlen=int(self.config["retention_period"] / self.config["collection_interval"])),
                "alerts": [],
            }
        
        # Initialize monitoring thread
        self._stop_monitoring = threading.Event()
        self._monitoring_thread = None
        
        self.logger.info(f"PerformanceMonitor initialized at {datetime.now().isoformat()}")
        self.logger.info(f"Metrics directory: {self.metrics_dir}")
    
    def _determine_metric_type(self, metric_name: str) -> MetricType:
        """Determine the type of a metric based on its name."""
        if metric_name.endswith("_time"):
            return MetricType.TIMER
        elif metric_name.endswith("_usage"):
            return MetricType.GAUGE
        elif metric_name.endswith("_calls"):
            return MetricType.COUNTER
        else:
            return MetricType.HISTOGRAM
    
    def start_monitoring(self) -> None:
        """Start collecting performance metrics."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self.logger.info("Monitoring already started")
            return
        
        self.logger.info("Starting performance monitoring")
        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop collecting performance metrics."""
        if not self._monitoring_thread or not self._monitoring_thread.is_alive():
            self.logger.info("Monitoring not running")
            return
        
        self.logger.info("Stopping performance monitoring")
        self._stop_monitoring.set()
        self._monitoring_thread.join(timeout=5.0)
        
        if self._monitoring_thread.is_alive():
            self.logger.warning("Monitoring thread did not stop gracefully")
        else:
            self.logger.info("Monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Continuously collect performance metrics."""
        interval = self.config["collection_interval"]
        
        while not self._stop_monitoring.is_set():
            start_time = time.time()
            
            try:
                # Collect metrics
                self._collect_metrics()
                
                # Check for alerts
                self._check_alerts()
                
                # Save metrics periodically
                if int(start_time) % 60 == 0:  # Save every minute
                    self._save_metrics()
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
            
            # Sleep for the remaining time in the interval
            elapsed = time.time() - start_time
            sleep_time = max(0.1, interval - elapsed)
            time.sleep(sleep_time)
    
    def _collect_metrics(self) -> None:
        """Collect current performance metrics."""
        timestamp = datetime.now().isoformat()
        
        # In a real implementation, these would collect actual system metrics
        # For this implementation, we'll simulate metric collection
        
        if "response_time" in self.metrics:
            # Simulate response time measurement
            response_time = self._measure_response_time()
            self.metrics["response_time"]["values"].append({
                "timestamp": timestamp,
                "value": response_time,
            })
        
        if "cpu_usage" in self.metrics:
            # Simulate CPU usage measurement
            cpu_usage = self._measure_cpu_usage()
            self.metrics["cpu_usage"]["values"].append({
                "timestamp": timestamp,
                "value": cpu_usage,
            })
        
        if "memory_usage" in self.metrics:
            # Simulate memory usage measurement
            memory_usage = self._measure_memory_usage()
            self.metrics["memory_usage"]["values"].append({
                "timestamp": timestamp,
                "value": memory_usage,
            })
        
        if "api_calls" in self.metrics:
            # Simulate API call counting
            api_calls = self._count_api_calls()
            self.metrics["api_calls"]["values"].append({
                "timestamp": timestamp,
                "value": api_calls,
            })
    
    def _measure_response_time(self) -> float:
        """Measure response time for API calls."""
        # In a real implementation, this would measure actual response times
        # For this implementation, we'll simulate response time measurement
        
        # Simulate a response time between 0.1 and 3.0 seconds
        # Usually around 0.5 seconds, but occasionally higher
        import random
        base_time = 0.5
        variation = random.random() * 0.4  # 0.0 to 0.4
        spike = random.random() > 0.95  # 5% chance of a spike
        
        if spike:
            return base_time + variation + random.random() * 2.0  # Add up to 2.0 seconds for a spike
        else:
            return base_time + variation
    
    def _measure_cpu_usage(self) -> float:
        """Measure CPU usage."""
        # In a real implementation, this would measure actual CPU usage
        # For this implementation, we'll simulate CPU usage measurement
        
        # Simulate CPU usage between 10% and 90%
        import random
        base_usage = 30.0
        variation = random.random() * 20.0  # 0.0 to 20.0
        spike = random.random() > 0.9  # 10% chance of a spike
        
        if spike:
            return min(100.0, base_usage + variation + random.random() * 40.0)  # Add up to 40% for a spike
        else:
            return base_usage + variation
    
    def _measure_memory_usage(self) -> float:
        """Measure memory usage."""
        # In a real implementation, this would measure actual memory usage
        # For this implementation, we'll simulate memory usage measurement
        
        # Simulate memory usage between 20% and 70%
        import random
        base_usage = 40.0
        variation = random.random() * 10.0  # 0.0 to 10.0
        
        return base_usage + variation
    
    def _count_api_calls(self) -> int:
        """Count API calls."""
        # In a real implementation, this would count actual API calls
        # For this implementation, we'll simulate API call counting
        
        # Simulate between 10 and 100 API calls per interval
        import random
        base_calls = 30
        variation = int(random.random() * 20)  # 0 to 20
        
        return base_calls + variation
    
    def _check_alerts(self) -> None:
        """Check for metrics exceeding alert thresholds."""
        thresholds = self.config["alert_thresholds"]
        
        for metric_name, threshold in thresholds.items():
            if metric_name not in self.metrics:
                continue
            
            metric = self.metrics[metric_name]
            if not metric["values"]:
                continue
            
            latest = metric["values"][-1]
            value = latest["value"]
            
            if value > threshold:
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "metric": metric_name,
                    "value": value,
                    "threshold": threshold,
                }
                
                metric["alerts"].append(alert)
                self.logger.warning(f"Alert: {metric_name} = {value} exceeds threshold {threshold}")
    
    def _save_metrics(self) -> None:
        """Save collected metrics to disk."""
        try:
            # Create a snapshot of current metrics
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "metrics": {},
            }
            
            for metric_name, metric in self.metrics.items():
                snapshot["metrics"][metric_name] = {
                    "type": metric["type"].value,
                    "values": list(metric["values"]),
                    "alerts": metric["alerts"],
                    "summary": self._calculate_summary(metric_name),
                }
            
            # Save snapshot to file
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.metrics_dir / filename
            
            with open(filepath, "w") as f:
                json.dump(snapshot, f, indent=2)
            
            self.logger.info(f"Metrics saved to {filepath}")
            
            # Clean up old metric files
            self._cleanup_old_files()
        except Exception as e:
            self.logger.error(f"Error saving metrics: {str(e)}")
    
    def _cleanup_old_files(self) -> None:
        """Clean up old metric files."""
        try:
            retention_days = self.config["retention_period"] / 86400  # Convert seconds to days
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for file_path in self.metrics_dir.glob("metrics_*.json"):
                try:
                    # Extract date from filename
                    date_str = file_path.stem.split("_")[1]
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        self.logger.info(f"Removed old metrics file: {file_path}")
                except (ValueError, IndexError):
                    self.logger.warning(f"Could not parse date from filename: {file_path}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old files: {str(e)}")
    
    def _calculate_summary(self, metric_name: str) -> Dict[str, Any]:
        """Calculate summary statistics for a metric."""
        metric = self.metrics[metric_name]
        values = [item["value"] for item in metric["values"]]
        
        if not values:
            return {}
        
        summary = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
        }
        
        # Add percentiles for histograms and timers
        if metric["type"] in [MetricType.HISTOGRAM, MetricType.TIMER]:
            sorted_values = sorted(values)
            summary["p50"] = sorted_values[int(len(sorted_values) * 0.5)]
            summary["p90"] = sorted_values[int(len(sorted_values) * 0.9)]
            summary["p95"] = sorted_values[int(len(sorted_values) * 0.95)]
            summary["p99"] = sorted_values[int(len(sorted_values) * 0.99)]
        
        return summary
    
    def get_metric(self, metric_name: str) -> Dict[str, Any]:
        """
        Get the current value and history of a metric.
        
        Args:
            metric_name: Name of the metric to retrieve
            
        Returns:
            Dictionary with metric data or empty dict if metric not found
        """
        if metric_name not in self.metrics:
            self.logger.warning(f"Metric {metric_name} not found")
            return {}
        
        metric = self.metrics[metric_name]
        
        return {
            "type": metric["type"].value,
            "values": list(metric["values"]),
            "alerts": metric["alerts"],
            "summary": self._calculate_summary(metric_name),
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary of all metrics
        """
        result = {}
        
        for metric_name in self.metrics:
            result[metric_name] = self.get_metric(metric_name)
        
        return result
    
    def record_custom_metric(self, metric_name: str, value: Any, metric_type: Optional[MetricType] = None) -> None:
        """
        Record a custom metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            metric_type: Type of the metric, if None will be determined automatically
        """
        if metric_name not in self.metrics:
            # Create new metric
            self.metrics[metric_name] = {
                "type": metric_type or self._determine_metric_type(metric_name),
                "values": deque(maxlen=int(self.config["retention_period"] / self.config["collection_interval"])),
                "alerts": [],
            }
        
        # Record value
        self.metrics[metric_name]["values"].append({
            "timestamp": datetime.now().isoformat(),
            "value": value,
        })
        
        self.logger.debug(f"Recorded custom metric: {metric_name} = {value}")
    
    def get_alerts(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get alerts that have occurred.
        
        Args:
            since: Only return alerts since this time, if None returns all alerts
            
        Returns:
            List of alerts
        """
        all_alerts = []
        
        for metric_name, metric in self.metrics.items():
            for alert in metric["alerts"]:
                if since is None or datetime.fromisoformat(alert["timestamp"]) >= since:
                    all_alerts.append({
                        **alert,
                        "metric": metric_name,
                    })
        
        # Sort by timestamp
        all_alerts.sort(key=lambda a: a["timestamp"])
        
        return all_alerts
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update the configuration settings.
        
        Args:
            config: New configuration settings
        """
        self.config.update(config)
        self.logger.info(f"Configuration updated: {config}")
        
        # Update metric storage if retention period changed
        if "retention_period" in config and "collection_interval" in self.config:
            new_maxlen = int(self.config["retention_period"] / self.config["collection_interval"])
            for metric_name, metric in self.metrics.items():
                new_values = deque(list(metric["values"]), maxlen=new_maxlen)
                metric["values"] = new_values
