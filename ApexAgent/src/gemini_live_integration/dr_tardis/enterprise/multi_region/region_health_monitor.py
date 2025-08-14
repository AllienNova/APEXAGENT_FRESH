"""
Region Health Monitoring for Gemini Live API Integration with Dr. TARDIS

This module implements health monitoring for multi-region deployments of the Gemini Live API
Integration with Dr. TARDIS in the Aideon AI Lite platform.

It provides:
1. Automated health checks for all regions
2. Latency and performance monitoring
3. Load monitoring and capacity planning
4. Alerting and notification for region health issues
5. Historical health data for trend analysis
"""

import json
import logging
import os
import time
import threading
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from .multi_region_deployment import Region, RegionHealth, MultiRegionDeployment

# Configure logging
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Severity levels for health alerts."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class HealthMetricType(Enum):
    """Types of health metrics that can be monitored."""
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    THROUGHPUT = "throughput"
    LOAD = "load"
    CAPACITY = "capacity"

class RegionHealthMonitor:
    """
    Monitors the health of all regions in a multi-region deployment.
    
    This class provides:
    - Automated health checks for all regions
    - Performance and latency monitoring
    - Load monitoring and capacity planning
    - Alerting for health issues
    - Historical health data collection
    """
    
    def __init__(self, deployment: MultiRegionDeployment, config_path: Optional[str] = None):
        """
        Initialize the region health monitor.
        
        Args:
            deployment: The multi-region deployment to monitor
            config_path: Path to the configuration file. If None, uses default config.
        """
        self.deployment = deployment
        self.check_interval = 60  # seconds
        self.alert_thresholds = {
            HealthMetricType.LATENCY: {
                AlertSeverity.WARNING: 500.0,  # ms
                AlertSeverity.CRITICAL: 1000.0  # ms
            },
            HealthMetricType.ERROR_RATE: {
                AlertSeverity.WARNING: 0.05,  # 5%
                AlertSeverity.CRITICAL: 0.10  # 10%
            },
            HealthMetricType.AVAILABILITY: {
                AlertSeverity.WARNING: 0.98,  # 98%
                AlertSeverity.CRITICAL: 0.95  # 95%
            },
            HealthMetricType.LOAD: {
                AlertSeverity.WARNING: 0.80,  # 80% of capacity
                AlertSeverity.CRITICAL: 0.95  # 95% of capacity
            }
        }
        self.history_retention = 86400  # 24 hours in seconds
        self.history = {}  # Historical health data
        self.alerts = []  # Recent alerts
        self.running = False
        self.monitor_thread = None
        
        # Load configuration
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file.
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Load check interval
            self.check_interval = config.get('check_interval', 60)
            
            # Load alert thresholds
            if 'alert_thresholds' in config:
                for metric_str, thresholds in config['alert_thresholds'].items():
                    try:
                        metric = HealthMetricType(metric_str)
                        self.alert_thresholds[metric] = {}
                        for severity_str, value in thresholds.items():
                            severity = AlertSeverity(severity_str)
                            self.alert_thresholds[metric][severity] = value
                    except ValueError:
                        logger.warning(f"Unknown metric type: {metric_str}")
            
            # Load history retention
            self.history_retention = config.get('history_retention', 86400)
            
            logger.info(f"Loaded health monitor configuration from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load health monitor configuration from {config_path}: {e}")
    
    def start(self) -> None:
        """Start the health monitoring thread."""
        if self.running:
            logger.warning("Health monitor is already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Started health monitoring thread")
    
    def stop(self) -> None:
        """Stop the health monitoring thread."""
        if not self.running:
            logger.warning("Health monitor is not running")
            return
        
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Stopped health monitoring thread")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop that runs in a separate thread."""
        while self.running:
            try:
                # Run health checks
                self._check_all_regions()
                
                # Clean up old history data
                self._clean_history()
                
                # Sleep until next check
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                time.sleep(5.0)  # Sleep briefly before retrying
    
    def _check_all_regions(self) -> None:
        """Check the health of all regions."""
        # Get all regions from the deployment
        regions = list(self.deployment.regions.keys())
        
        for region in regions:
            try:
                # Skip disabled regions
                if not self.deployment.regions[region].enabled:
                    continue
                
                # Check region health
                health = self._check_region_health(region)
                
                # Update deployment with health status
                self.deployment.update_region_health(region, health)
                
                # Record metrics
                self._record_metrics(region)
                
                # Check for alerts
                self._check_alerts(region)
            except Exception as e:
                logger.error(f"Error checking health for region {region}: {e}")
    
    def _check_region_health(self, region: Region) -> RegionHealth:
        """
        Check the health of a specific region.
        
        Args:
            region: The region to check
            
        Returns:
            The health status of the region
        """
        # In a real implementation, this would make actual API calls to check health
        # For this example, we'll use the deployment's simulate_health_check method
        return self.deployment._simulate_health_check(region)
    
    def _record_metrics(self, region: Region) -> None:
        """
        Record health metrics for a region.
        
        Args:
            region: The region to record metrics for
        """
        # Get current time
        now = time.time()
        
        # Initialize history for this region if it doesn't exist
        if region not in self.history:
            self.history[region] = []
        
        # Get current metrics
        latency = self.deployment.region_latencies.get(region, 0.0)
        load = self.deployment.region_loads.get(region, 0.0)
        max_capacity = self.deployment.regions[region].max_capacity
        health = self.deployment.region_health.get(region, RegionHealth.UNKNOWN)
        
        # Calculate derived metrics
        load_percentage = load / max_capacity if max_capacity > 0 else 0.0
        
        # Record metrics
        self.history[region].append({
            'timestamp': now,
            'latency': latency,
            'load': load,
            'load_percentage': load_percentage,
            'health': health.value,
            'max_capacity': max_capacity
        })
    
    def _clean_history(self) -> None:
        """Clean up old history data beyond the retention period."""
        now = time.time()
        cutoff = now - self.history_retention
        
        for region in self.history:
            # Filter out old entries
            self.history[region] = [entry for entry in self.history[region] 
                                   if entry['timestamp'] >= cutoff]
    
    def _check_alerts(self, region: Region) -> None:
        """
        Check for alert conditions for a region.
        
        Args:
            region: The region to check alerts for
        """
        # Get latest metrics
        if region not in self.history or not self.history[region]:
            return
        
        latest = self.history[region][-1]
        
        # Check latency alerts
        latency = latest['latency']
        latency_thresholds = self.alert_thresholds.get(HealthMetricType.LATENCY, {})
        
        if AlertSeverity.CRITICAL in latency_thresholds and latency >= latency_thresholds[AlertSeverity.CRITICAL]:
            self._create_alert(region, HealthMetricType.LATENCY, AlertSeverity.CRITICAL, 
                              f"Critical latency of {latency}ms exceeds threshold of {latency_thresholds[AlertSeverity.CRITICAL]}ms")
        elif AlertSeverity.WARNING in latency_thresholds and latency >= latency_thresholds[AlertSeverity.WARNING]:
            self._create_alert(region, HealthMetricType.LATENCY, AlertSeverity.WARNING, 
                              f"High latency of {latency}ms exceeds threshold of {latency_thresholds[AlertSeverity.WARNING]}ms")
        
        # Check load alerts
        load_percentage = latest['load_percentage']
        load_thresholds = self.alert_thresholds.get(HealthMetricType.LOAD, {})
        
        if AlertSeverity.CRITICAL in load_thresholds and load_percentage >= load_thresholds[AlertSeverity.CRITICAL]:
            self._create_alert(region, HealthMetricType.LOAD, AlertSeverity.CRITICAL, 
                              f"Critical load of {load_percentage:.1%} exceeds threshold of {load_thresholds[AlertSeverity.CRITICAL]:.1%}")
        elif AlertSeverity.WARNING in load_thresholds and load_percentage >= load_thresholds[AlertSeverity.WARNING]:
            self._create_alert(region, HealthMetricType.LOAD, AlertSeverity.WARNING, 
                              f"High load of {load_percentage:.1%} exceeds threshold of {load_thresholds[AlertSeverity.WARNING]:.1%}")
        
        # Check health status
        health = RegionHealth(latest['health'])
        if health == RegionHealth.UNHEALTHY:
            self._create_alert(region, HealthMetricType.AVAILABILITY, AlertSeverity.CRITICAL, 
                              f"Region {region} is unhealthy")
        elif health == RegionHealth.DEGRADED:
            self._create_alert(region, HealthMetricType.AVAILABILITY, AlertSeverity.WARNING, 
                              f"Region {region} is degraded")
    
    def _create_alert(self, region: Region, metric: HealthMetricType, severity: AlertSeverity, message: str) -> None:
        """
        Create a new alert.
        
        Args:
            region: The region the alert is for
            metric: The metric type that triggered the alert
            severity: The severity of the alert
            message: The alert message
        """
        alert = {
            'timestamp': time.time(),
            'region': region.value,
            'metric': metric.value,
            'severity': severity.value,
            'message': message
        }
        
        self.alerts.append(alert)
        
        # Log the alert
        if severity == AlertSeverity.CRITICAL:
            logger.error(f"ALERT: {message}")
        elif severity == AlertSeverity.WARNING:
            logger.warning(f"ALERT: {message}")
        else:
            logger.info(f"ALERT: {message}")
        
        # In a real implementation, this would also send notifications
        # via email, SMS, or integration with monitoring systems
    
    def get_recent_alerts(self, max_alerts: int = 100, min_severity: AlertSeverity = AlertSeverity.INFO) -> List[Dict]:
        """
        Get recent alerts.
        
        Args:
            max_alerts: Maximum number of alerts to return
            min_severity: Minimum severity level to include
            
        Returns:
            List of recent alerts
        """
        # Filter alerts by severity
        filtered_alerts = [alert for alert in self.alerts 
                          if AlertSeverity(alert['severity']) >= min_severity]
        
        # Sort by timestamp (newest first)
        sorted_alerts = sorted(filtered_alerts, key=lambda a: a['timestamp'], reverse=True)
        
        # Limit to max_alerts
        return sorted_alerts[:max_alerts]
    
    def get_region_health_summary(self, region: Region, time_range: int = 3600) -> Dict:
        """
        Get a health summary for a region over a time range.
        
        Args:
            region: The region to get the summary for
            time_range: Time range in seconds (default: 1 hour)
            
        Returns:
            Dictionary with health summary
        """
        if region not in self.history:
            return {
                'region': region.value,
                'data_points': 0,
                'current_health': RegionHealth.UNKNOWN.value,
                'avg_latency': 0.0,
                'max_latency': 0.0,
                'avg_load_percentage': 0.0,
                'max_load_percentage': 0.0,
                'availability': 0.0
            }
        
        # Filter history to the specified time range
        now = time.time()
        cutoff = now - time_range
        history = [entry for entry in self.history[region] if entry['timestamp'] >= cutoff]
        
        if not history:
            return {
                'region': region.value,
                'data_points': 0,
                'current_health': RegionHealth.UNKNOWN.value,
                'avg_latency': 0.0,
                'max_latency': 0.0,
                'avg_load_percentage': 0.0,
                'max_load_percentage': 0.0,
                'availability': 0.0
            }
        
        # Calculate metrics
        latencies = [entry['latency'] for entry in history]
        load_percentages = [entry['load_percentage'] for entry in history]
        health_statuses = [entry['health'] for entry in history]
        
        # Calculate availability (percentage of time the region was healthy)
        healthy_count = sum(1 for status in health_statuses if status == RegionHealth.HEALTHY.value)
        availability = healthy_count / len(health_statuses) if health_statuses else 0.0
        
        # Get current health
        current_health = history[-1]['health']
        
        return {
            'region': region.value,
            'data_points': len(history),
            'current_health': current_health,
            'avg_latency': sum(latencies) / len(latencies) if latencies else 0.0,
            'max_latency': max(latencies) if latencies else 0.0,
            'avg_load_percentage': sum(load_percentages) / len(load_percentages) if load_percentages else 0.0,
            'max_load_percentage': max(load_percentages) if load_percentages else 0.0,
            'availability': availability
        }
    
    def get_all_regions_health_summary(self, time_range: int = 3600) -> Dict[str, Dict]:
        """
        Get health summaries for all regions.
        
        Args:
            time_range: Time range in seconds (default: 1 hour)
            
        Returns:
            Dictionary mapping region names to health summaries
        """
        summaries = {}
        for region in self.deployment.regions:
            summaries[region.value] = self.get_region_health_summary(region, time_range)
        
        return summaries
    
    def export_health_data(self, output_path: str, time_range: int = 86400) -> bool:
        """
        Export health data to a file.
        
        Args:
            output_path: Path to save the data to
            time_range: Time range in seconds (default: 24 hours)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Filter history to the specified time range
            now = time.time()
            cutoff = now - time_range
            
            export_data = {
                'timestamp': now,
                'time_range': time_range,
                'regions': {}
            }
            
            for region in self.history:
                history = [entry for entry in self.history[region] if entry['timestamp'] >= cutoff]
                
                # Convert timestamps to ISO format for better readability
                formatted_history = []
                for entry in history:
                    formatted_entry = entry.copy()
                    formatted_entry['timestamp'] = datetime.fromtimestamp(entry['timestamp']).isoformat()
                    formatted_history.append(formatted_entry)
                
                export_data['regions'][region.value] = formatted_history
            
            # Add alerts
            export_data['alerts'] = []
            for alert in self.alerts:
                formatted_alert = alert.copy()
                formatted_alert['timestamp'] = datetime.fromtimestamp(alert['timestamp']).isoformat()
                export_data['alerts'].append(formatted_alert)
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported health data to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export health data to {output_path}: {e}")
            return False
