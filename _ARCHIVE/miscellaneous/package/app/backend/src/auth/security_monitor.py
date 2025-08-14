"""
Security Monitoring and Audit System for Aideon AI Lite

This module provides comprehensive security monitoring, threat detection,
and audit capabilities for the authentication system with real-time alerts
and anomaly detection.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import ipaddress
from collections import defaultdict, deque
import statistics
import threading
import time

from ..core.plugin_exceptions import (
    PluginError,
    PluginConfigurationError,
    PluginActionExecutionError
)

logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Types of security events."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    OAUTH_INITIATED = "oauth_initiated"
    OAUTH_COMPLETED = "oauth_completed"
    OAUTH_FAILED = "oauth_failed"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_REVOKED = "token_revoked"
    API_KEY_ADDED = "api_key_added"
    API_KEY_DELETED = "api_key_deleted"
    CREDENTIAL_ACCESS = "credential_access"
    ADMIN_ACCESS = "admin_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_TOKEN = "invalid_token"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class ThreatLevel(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventStatus(Enum):
    """Security event status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    INVESTIGATING = "investigating"
    FALSE_POSITIVE = "false_positive"


@dataclass
class SecurityEvent:
    """Security event record."""
    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    status: SecurityEventStatus
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        data['event_type'] = self.event_type.value
        data['threat_level'] = self.threat_level.value
        data['status'] = self.status.value
        return data


@dataclass
class SecurityMetrics:
    """Security metrics for monitoring."""
    total_events: int = 0
    events_by_type: Dict[str, int] = None
    events_by_threat_level: Dict[str, int] = None
    failed_logins_24h: int = 0
    successful_logins_24h: int = 0
    oauth_failures_24h: int = 0
    suspicious_activities_24h: int = 0
    unique_ips_24h: int = 0
    top_threat_ips: List[Tuple[str, int]] = None
    
    def __post_init__(self):
        if self.events_by_type is None:
            self.events_by_type = {}
        if self.events_by_threat_level is None:
            self.events_by_threat_level = {}
        if self.top_threat_ips is None:
            self.top_threat_ips = []


class AnomalyDetector:
    """
    Anomaly detection system for identifying suspicious patterns.
    
    Uses statistical analysis and pattern recognition to detect
    unusual authentication behavior.
    """
    
    def __init__(self, window_size: int = 100):
        """
        Initialize anomaly detector.
        
        Args:
            window_size: Size of the sliding window for analysis
        """
        self.window_size = window_size
        self.login_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.ip_requests: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.user_agents: Dict[str, set] = defaultdict(set)
        self.failed_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        
        # Thresholds for anomaly detection
        self.max_failed_attempts = 5
        self.max_requests_per_minute = 60
        self.suspicious_user_agent_threshold = 10
        self.unusual_time_threshold = 2.0  # Standard deviations
    
    def analyze_login_pattern(
        self,
        user_id: str,
        timestamp: datetime,
        success: bool,
        ip_address: str,
        user_agent: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze login pattern for anomalies.
        
        Args:
            user_id: User ID
            timestamp: Login timestamp
            success: Whether login was successful
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Track login times
        self.login_times[user_id].append(timestamp)
        
        # Track IP requests
        self.ip_requests[ip_address].append(timestamp)
        
        # Track user agents
        self.user_agents[user_id].add(user_agent)
        
        # Track failed attempts
        if not success:
            self.failed_attempts[user_id].append(timestamp)
        
        # Check for anomalies
        anomalies.extend(self._check_failed_attempts(user_id))
        anomalies.extend(self._check_rate_limiting(ip_address))
        anomalies.extend(self._check_unusual_timing(user_id))
        anomalies.extend(self._check_suspicious_user_agents(user_id))
        anomalies.extend(self._check_geographic_anomalies(ip_address))
        
        return anomalies
    
    def _check_failed_attempts(self, user_id: str) -> List[Dict[str, Any]]:
        """Check for excessive failed login attempts."""
        anomalies = []
        
        recent_failures = [
            t for t in self.failed_attempts[user_id]
            if datetime.utcnow() - t < timedelta(minutes=15)
        ]
        
        if len(recent_failures) >= self.max_failed_attempts:
            anomalies.append({
                "type": "excessive_failed_attempts",
                "severity": "high",
                "details": {
                    "user_id": user_id,
                    "failed_attempts": len(recent_failures),
                    "threshold": self.max_failed_attempts,
                    "time_window": "15 minutes"
                }
            })
        
        return anomalies
    
    def _check_rate_limiting(self, ip_address: str) -> List[Dict[str, Any]]:
        """Check for rate limiting violations."""
        anomalies = []
        
        recent_requests = [
            t for t in self.ip_requests[ip_address]
            if datetime.utcnow() - t < timedelta(minutes=1)
        ]
        
        if len(recent_requests) > self.max_requests_per_minute:
            anomalies.append({
                "type": "rate_limit_exceeded",
                "severity": "medium",
                "details": {
                    "ip_address": ip_address,
                    "requests_per_minute": len(recent_requests),
                    "threshold": self.max_requests_per_minute
                }
            })
        
        return anomalies
    
    def _check_unusual_timing(self, user_id: str) -> List[Dict[str, Any]]:
        """Check for unusual login timing patterns."""
        anomalies = []
        
        if len(self.login_times[user_id]) < 10:
            return anomalies  # Not enough data
        
        # Calculate typical login hours
        login_hours = [t.hour for t in self.login_times[user_id]]
        
        if len(set(login_hours)) > 1:
            mean_hour = statistics.mean(login_hours)
            std_hour = statistics.stdev(login_hours)
            
            latest_hour = list(self.login_times[user_id])[-1].hour
            
            if abs(latest_hour - mean_hour) > self.unusual_time_threshold * std_hour:
                anomalies.append({
                    "type": "unusual_login_time",
                    "severity": "low",
                    "details": {
                        "user_id": user_id,
                        "login_hour": latest_hour,
                        "typical_range": f"{mean_hour - std_hour:.1f} - {mean_hour + std_hour:.1f}",
                        "deviation": abs(latest_hour - mean_hour) / std_hour
                    }
                })
        
        return anomalies
    
    def _check_suspicious_user_agents(self, user_id: str) -> List[Dict[str, Any]]:
        """Check for suspicious user agent patterns."""
        anomalies = []
        
        user_agent_count = len(self.user_agents[user_id])
        
        if user_agent_count > self.suspicious_user_agent_threshold:
            anomalies.append({
                "type": "multiple_user_agents",
                "severity": "medium",
                "details": {
                    "user_id": user_id,
                    "user_agent_count": user_agent_count,
                    "threshold": self.suspicious_user_agent_threshold
                }
            })
        
        return anomalies
    
    def _check_geographic_anomalies(self, ip_address: str) -> List[Dict[str, Any]]:
        """Check for geographic anomalies (simplified)."""
        anomalies = []
        
        # In a production system, this would use GeoIP databases
        # For now, just check for private vs public IPs
        try:
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                # Internal network access
                pass
            elif ip.is_loopback:
                # Localhost access
                pass
            else:
                # External access - could implement more sophisticated checks
                pass
        except ValueError:
            anomalies.append({
                "type": "invalid_ip_address",
                "severity": "medium",
                "details": {
                    "ip_address": ip_address
                }
            })
        
        return anomalies


class SecurityMonitor:
    """
    Comprehensive security monitoring system.
    
    Provides real-time security event tracking, threat detection,
    and automated response capabilities.
    """
    
    def __init__(self):
        """Initialize security monitor."""
        self.events: List[SecurityEvent] = []
        self.anomaly_detector = AnomalyDetector()
        self.alert_handlers: List[callable] = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Rate limiting tracking
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Threat intelligence (simplified)
        self.known_threat_ips = set()
        self.blocked_ips = set()
        
        # Metrics tracking
        self.metrics = SecurityMetrics()
        
        logger.info("Security monitor initialized")
    
    def start_monitoring(self):
        """Start security monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Security monitoring started")
    
    def stop_monitoring(self):
        """Stop security monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Security monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Perform periodic security checks
                self._check_for_threats()
                self._update_metrics()
                self._cleanup_old_events()
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Brief pause before retrying
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        threat_level: Optional[ThreatLevel] = None
    ) -> str:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            user_id: User ID (if applicable)
            ip_address: Client IP address
            user_agent: Client user agent
            endpoint: API endpoint accessed
            details: Additional event details
            threat_level: Threat level (auto-determined if not provided)
            
        Returns:
            Event ID
        """
        try:
            # Generate event ID
            event_id = self._generate_event_id()
            
            # Determine threat level if not provided
            if threat_level is None:
                threat_level = self._determine_threat_level(event_type, details)
            
            # Create security event
            event = SecurityEvent(
                event_id=event_id,
                event_type=event_type,
                threat_level=threat_level,
                status=SecurityEventStatus.ACTIVE,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                details=details or {}
            )
            
            # Store event
            self.events.append(event)
            
            # Perform anomaly detection for login events
            if event_type in [SecurityEventType.LOGIN_SUCCESS, SecurityEventType.LOGIN_FAILURE]:
                anomalies = self.anomaly_detector.analyze_login_pattern(
                    user_id=user_id or "unknown",
                    timestamp=event.timestamp,
                    success=event_type == SecurityEventType.LOGIN_SUCCESS,
                    ip_address=ip_address or "unknown",
                    user_agent=user_agent or "unknown"
                )
                
                # Create events for detected anomalies
                for anomaly in anomalies:
                    self._create_anomaly_event(anomaly, event)
            
            # Check for immediate threats
            self._check_immediate_threats(event)
            
            # Trigger alerts if necessary
            if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                self._trigger_alert(event)
            
            logger.info(f"Security event logged: {event_type.value} (ID: {event_id})")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            return ""
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        hash_input = f"{timestamp}_{len(self.events)}_{time.time()}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"sec_{timestamp}_{hash_value}"
    
    def _determine_threat_level(
        self,
        event_type: SecurityEventType,
        details: Optional[Dict[str, Any]]
    ) -> ThreatLevel:
        """Determine threat level based on event type and details."""
        
        # Critical threats
        if event_type in [
            SecurityEventType.UNAUTHORIZED_ACCESS,
            SecurityEventType.SUSPICIOUS_ACTIVITY
        ]:
            return ThreatLevel.CRITICAL
        
        # High threats
        if event_type in [
            SecurityEventType.RATE_LIMIT_EXCEEDED,
            SecurityEventType.INVALID_TOKEN
        ]:
            return ThreatLevel.HIGH
        
        # Medium threats
        if event_type in [
            SecurityEventType.LOGIN_FAILURE,
            SecurityEventType.OAUTH_FAILED
        ]:
            return ThreatLevel.MEDIUM
        
        # Low threats (normal operations)
        return ThreatLevel.LOW
    
    def _create_anomaly_event(self, anomaly: Dict[str, Any], parent_event: SecurityEvent):
        """Create security event for detected anomaly."""
        threat_level_map = {
            "low": ThreatLevel.LOW,
            "medium": ThreatLevel.MEDIUM,
            "high": ThreatLevel.HIGH,
            "critical": ThreatLevel.CRITICAL
        }
        
        anomaly_event = SecurityEvent(
            event_id=self._generate_event_id(),
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            threat_level=threat_level_map.get(anomaly["severity"], ThreatLevel.MEDIUM),
            status=SecurityEventStatus.ACTIVE,
            timestamp=datetime.utcnow(),
            user_id=parent_event.user_id,
            ip_address=parent_event.ip_address,
            user_agent=parent_event.user_agent,
            endpoint=parent_event.endpoint,
            details={
                "anomaly_type": anomaly["type"],
                "anomaly_details": anomaly["details"],
                "parent_event_id": parent_event.event_id
            }
        )
        
        self.events.append(anomaly_event)
        
        if anomaly_event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._trigger_alert(anomaly_event)
    
    def _check_immediate_threats(self, event: SecurityEvent):
        """Check for immediate threats requiring action."""
        
        # Check if IP is in known threat list
        if event.ip_address and event.ip_address in self.known_threat_ips:
            self._escalate_threat(event, "Known threat IP detected")
        
        # Check for brute force patterns
        if event.event_type == SecurityEventType.LOGIN_FAILURE:
            recent_failures = [
                e for e in self.events[-50:]  # Check last 50 events
                if (e.event_type == SecurityEventType.LOGIN_FAILURE and
                    e.ip_address == event.ip_address and
                    datetime.utcnow() - e.timestamp < timedelta(minutes=10))
            ]
            
            if len(recent_failures) >= 5:
                self._escalate_threat(event, "Brute force attack detected")
                self.blocked_ips.add(event.ip_address)
    
    def _escalate_threat(self, event: SecurityEvent, reason: str):
        """Escalate threat level and take action."""
        event.threat_level = ThreatLevel.CRITICAL
        event.details["escalation_reason"] = reason
        event.details["escalated_at"] = datetime.utcnow().isoformat()
        
        self._trigger_alert(event)
        logger.warning(f"Threat escalated: {reason} (Event ID: {event.event_id})")
    
    def _trigger_alert(self, event: SecurityEvent):
        """Trigger security alert."""
        for handler in self.alert_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.warning(f"Security alert triggered: {event.event_type.value} (Level: {event.threat_level.value})")
    
    def add_alert_handler(self, handler: callable):
        """Add alert handler function."""
        self.alert_handlers.append(handler)
    
    def _check_for_threats(self):
        """Perform periodic threat checks."""
        # Check for patterns in recent events
        recent_events = [
            e for e in self.events
            if datetime.utcnow() - e.timestamp < timedelta(hours=1)
        ]
        
        # Group by IP address
        ip_events = defaultdict(list)
        for event in recent_events:
            if event.ip_address:
                ip_events[event.ip_address].append(event)
        
        # Check for suspicious IP patterns
        for ip, events in ip_events.items():
            if len(events) > 100:  # High activity from single IP
                self._flag_suspicious_ip(ip, f"High activity: {len(events)} events in 1 hour")
    
    def _flag_suspicious_ip(self, ip_address: str, reason: str):
        """Flag IP address as suspicious."""
        if ip_address not in self.known_threat_ips:
            self.known_threat_ips.add(ip_address)
            
            # Create security event
            self.log_security_event(
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                ip_address=ip_address,
                threat_level=ThreatLevel.HIGH,
                details={
                    "reason": reason,
                    "action": "IP flagged as suspicious"
                }
            )
    
    def _update_metrics(self):
        """Update security metrics."""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Get events from last 24 hours
        recent_events = [e for e in self.events if e.timestamp >= last_24h]
        
        # Update metrics
        self.metrics.total_events = len(self.events)
        
        # Events by type
        self.metrics.events_by_type = {}
        for event_type in SecurityEventType:
            count = len([e for e in recent_events if e.event_type == event_type])
            if count > 0:
                self.metrics.events_by_type[event_type.value] = count
        
        # Events by threat level
        self.metrics.events_by_threat_level = {}
        for threat_level in ThreatLevel:
            count = len([e for e in recent_events if e.threat_level == threat_level])
            if count > 0:
                self.metrics.events_by_threat_level[threat_level.value] = count
        
        # Specific metrics
        self.metrics.failed_logins_24h = len([
            e for e in recent_events
            if e.event_type == SecurityEventType.LOGIN_FAILURE
        ])
        
        self.metrics.successful_logins_24h = len([
            e for e in recent_events
            if e.event_type == SecurityEventType.LOGIN_SUCCESS
        ])
        
        self.metrics.oauth_failures_24h = len([
            e for e in recent_events
            if e.event_type == SecurityEventType.OAUTH_FAILED
        ])
        
        self.metrics.suspicious_activities_24h = len([
            e for e in recent_events
            if e.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY
        ])
        
        # Unique IPs
        unique_ips = set(e.ip_address for e in recent_events if e.ip_address)
        self.metrics.unique_ips_24h = len(unique_ips)
        
        # Top threat IPs
        ip_threat_counts = defaultdict(int)
        for event in recent_events:
            if event.ip_address and event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                ip_threat_counts[event.ip_address] += 1
        
        self.metrics.top_threat_ips = sorted(
            ip_threat_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    
    def _cleanup_old_events(self):
        """Clean up old security events."""
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Keep only events from last 30 days
        self.events = [e for e in self.events if e.timestamp >= cutoff_date]
        
        logger.debug(f"Cleaned up old security events, {len(self.events)} events remaining")
    
    def get_security_events(
        self,
        event_type: Optional[SecurityEventType] = None,
        threat_level: Optional[ThreatLevel] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SecurityEvent]:
        """
        Get security events with filtering.
        
        Args:
            event_type: Filter by event type
            threat_level: Filter by threat level
            user_id: Filter by user ID
            ip_address: Filter by IP address
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of events to return
            
        Returns:
            List of security events
        """
        filtered_events = []
        
        for event in reversed(self.events):  # Most recent first
            # Apply filters
            if event_type and event.event_type != event_type:
                continue
            
            if threat_level and event.threat_level != threat_level:
                continue
            
            if user_id and event.user_id != user_id:
                continue
            
            if ip_address and event.ip_address != ip_address:
                continue
            
            if start_date and event.timestamp < start_date:
                continue
            
            if end_date and event.timestamp > end_date:
                continue
            
            filtered_events.append(event)
            
            if len(filtered_events) >= limit:
                break
        
        return filtered_events
    
    def get_security_metrics(self) -> SecurityMetrics:
        """Get current security metrics."""
        return self.metrics
    
    def resolve_security_event(
        self,
        event_id: str,
        resolved_by: str,
        resolution_notes: str = ""
    ) -> bool:
        """
        Resolve a security event.
        
        Args:
            event_id: Event ID to resolve
            resolved_by: User who resolved the event
            resolution_notes: Resolution notes
            
        Returns:
            True if successful
        """
        for event in self.events:
            if event.event_id == event_id:
                event.status = SecurityEventStatus.RESOLVED
                event.resolved_at = datetime.utcnow()
                event.resolved_by = resolved_by
                event.resolution_notes = resolution_notes
                
                logger.info(f"Security event resolved: {event_id} by {resolved_by}")
                return True
        
        return False
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked."""
        return ip_address in self.blocked_ips
    
    def block_ip(self, ip_address: str, reason: str = ""):
        """Block IP address."""
        self.blocked_ips.add(ip_address)
        
        self.log_security_event(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            ip_address=ip_address,
            threat_level=ThreatLevel.HIGH,
            details={
                "action": "IP blocked",
                "reason": reason
            }
        )
        
        logger.warning(f"IP address blocked: {ip_address} - {reason}")
    
    def unblock_ip(self, ip_address: str):
        """Unblock IP address."""
        self.blocked_ips.discard(ip_address)
        logger.info(f"IP address unblocked: {ip_address}")


# Global security monitor instance
security_monitor = SecurityMonitor()


def log_security_event(
    event_type: SecurityEventType,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    endpoint: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    threat_level: Optional[ThreatLevel] = None
) -> str:
    """
    Convenience function to log security events.
    
    Args:
        event_type: Type of security event
        user_id: User ID (if applicable)
        ip_address: Client IP address
        user_agent: Client user agent
        endpoint: API endpoint accessed
        details: Additional event details
        threat_level: Threat level (auto-determined if not provided)
        
    Returns:
        Event ID
    """
    return security_monitor.log_security_event(
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=endpoint,
        details=details,
        threat_level=threat_level
    )


def start_security_monitoring():
    """Start security monitoring."""
    security_monitor.start_monitoring()


def stop_security_monitoring():
    """Stop security monitoring."""
    security_monitor.stop_monitoring()


def get_security_monitor() -> SecurityMonitor:
    """Get the global security monitor instance."""
    return security_monitor

