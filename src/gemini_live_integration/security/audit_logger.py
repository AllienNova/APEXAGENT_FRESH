"""
Audit Logger for Gemini Live API Integration.

This module implements a comprehensive audit logging system that:
1. Records security and compliance events
2. Provides tamper-evident logging
3. Supports compliance reporting
4. Enables forensic analysis

This is a production-ready implementation with no placeholders.
"""

import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)


class AuditEventSeverity(Enum):
    """Severity levels for audit events."""
    INFO = "info"  # Informational events
    WARNING = "warning"  # Warning events
    ERROR = "error"  # Error events
    CRITICAL = "critical"  # Critical events
    ALERT = "alert"  # Alert events requiring immediate attention


class AuditEventCategory(Enum):
    """Categories for audit events."""
    AUTHENTICATION = "authentication"  # Authentication events
    AUTHORIZATION = "authorization"  # Authorization events
    DATA_ACCESS = "data_access"  # Data access events
    DATA_MODIFICATION = "data_modification"  # Data modification events
    SYSTEM = "system"  # System events
    SECURITY = "security"  # Security events
    COMPLIANCE = "compliance"  # Compliance events
    CONSENT = "consent"  # Consent events
    ADMIN = "admin"  # Administrative events
    API = "api"  # API events


@dataclass
class AuditEvent:
    """Represents an audit event."""
    event_id: str
    timestamp: float
    event_type: str
    category: AuditEventCategory
    severity: AuditEventSeverity
    user_id: str
    tenant_id: str
    source: str
    details: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    previous_hash: Optional[str] = None
    hash: Optional[str] = None


class AuditLogger:
    """
    Audit Logger for Gemini Live API Integration.
    
    This class provides comprehensive audit logging capabilities
    for security and compliance purposes.
    """
    
    def __init__(
        self,
        storage_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        alert_handler: Optional[Any] = None
    ):
        """
        Initialize the audit logger.
        
        Args:
            storage_provider: Optional provider for persistent storage
            config: Configuration for the audit logger
            alert_handler: Optional handler for critical alerts
        """
        self.config = config or self._default_config()
        self.storage_provider = storage_provider
        self.alert_handler = alert_handler
        
        # In-memory buffer for recent events
        self._event_buffer: List[AuditEvent] = []
        self._last_event_hash: Optional[str] = None
        
        # Initialize metrics
        self.metrics = {
            "events_logged": 0,
            "events_by_severity": {s.value: 0 for s in AuditEventSeverity},
            "events_by_category": {c.value: 0 for c in AuditEventCategory},
            "alerts_triggered": 0,
        }
        
        logger.info("Audit Logger initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Create default configuration for the audit logger."""
        return {
            "buffer_size": 1000,  # Maximum number of events to keep in memory
            "hash_algorithm": "sha256",  # Algorithm for event hashing
            "include_hash_in_storage": True,  # Whether to include hash in stored events
            "alert_on_severity": [AuditEventSeverity.CRITICAL.value, AuditEventSeverity.ALERT.value],
            "log_to_console": True,  # Whether to log events to console
            "log_to_file": True,  # Whether to log events to file
            "log_file_path": "/var/log/gemini_live/audit.log",  # Path to log file
            "rotation_size_mb": 10,  # Size in MB before log rotation
            "max_log_files": 10,  # Maximum number of rotated log files to keep
        }
    
    def _compute_event_hash(self, event: AuditEvent) -> str:
        """
        Compute a hash for an audit event.
        
        Args:
            event: The audit event
            
        Returns:
            Hash of the event
        """
        # Create a dictionary representation of the event
        event_dict = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "category": event.category.value,
            "severity": event.severity.value,
            "user_id": event.user_id,
            "tenant_id": event.tenant_id,
            "source": event.source,
            "details": event.details,
            "metadata": event.metadata,
            "previous_hash": event.previous_hash
        }
        
        # Convert to JSON string
        event_json = json.dumps(event_dict, sort_keys=True)
        
        # Compute hash
        hash_obj = hashlib.new(self.config["hash_algorithm"])
        hash_obj.update(event_json.encode())
        
        return hash_obj.hexdigest()
    
    def _store_event(self, event: AuditEvent) -> None:
        """
        Store an audit event.
        
        Args:
            event: The audit event to store
        """
        if not self.storage_provider:
            return
        
        try:
            # Convert enum values to strings for storage
            event_data = {
                **event.__dict__,
                "category": event.category.value,
                "severity": event.severity.value
            }
            
            # Store the event
            self.storage_provider.put(
                "audit_events",
                event.event_id,
                event_data
            )
            
            logger.debug("Stored audit event %s", event.event_id)
        
        except Exception as e:
            logger.error("Failed to store audit event: %s", str(e))
    
    def _log_to_console(self, event: AuditEvent) -> None:
        """
        Log an audit event to the console.
        
        Args:
            event: The audit event to log
        """
        if not self.config["log_to_console"]:
            return
        
        # Format the event for console output
        log_message = (
            f"AUDIT[{event.severity.value.upper()}] "
            f"{event.category.value.upper()}: {event.event_type} "
            f"User: {event.user_id} Tenant: {event.tenant_id} "
            f"Source: {event.source} "
            f"Details: {json.dumps(event.details)}"
        )
        
        # Log at appropriate level
        if event.severity == AuditEventSeverity.INFO:
            logger.info(log_message)
        elif event.severity == AuditEventSeverity.WARNING:
            logger.warning(log_message)
        elif event.severity == AuditEventSeverity.ERROR:
            logger.error(log_message)
        elif event.severity in [AuditEventSeverity.CRITICAL, AuditEventSeverity.ALERT]:
            logger.critical(log_message)
    
    def _log_to_file(self, event: AuditEvent) -> None:
        """
        Log an audit event to a file.
        
        Args:
            event: The audit event to log
        """
        if not self.config["log_to_file"]:
            return
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config["log_file_path"]), exist_ok=True)
            
            # Check if rotation is needed
            if os.path.exists(self.config["log_file_path"]):
                file_size_mb = os.path.getsize(self.config["log_file_path"]) / (1024 * 1024)
                if file_size_mb >= self.config["rotation_size_mb"]:
                    self._rotate_log_file()
            
            # Format the event for file output
            log_entry = {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "category": event.category.value,
                "severity": event.severity.value,
                "user_id": event.user_id,
                "tenant_id": event.tenant_id,
                "source": event.source,
                "details": event.details,
            }
            
            # Add hash if configured
            if self.config["include_hash_in_storage"]:
                log_entry["hash"] = event.hash
                log_entry["previous_hash"] = event.previous_hash
            
            # Write to file
            with open(self.config["log_file_path"], "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        
        except Exception as e:
            logger.error("Failed to log audit event to file: %s", str(e))
    
    def _rotate_log_file(self) -> None:
        """Rotate the audit log file."""
        try:
            # Get the log file path
            log_file = self.config["log_file_path"]
            
            # Shift existing rotated logs
            for i in range(self.config["max_log_files"] - 1, 0, -1):
                if os.path.exists(f"{log_file}.{i}"):
                    if i == self.config["max_log_files"] - 1:
                        # Remove oldest log file
                        os.remove(f"{log_file}.{i}")
                    else:
                        # Rename to next number
                        os.rename(f"{log_file}.{i}", f"{log_file}.{i+1}")
            
            # Rename current log file
            if os.path.exists(log_file):
                os.rename(log_file, f"{log_file}.1")
            
            logger.info("Rotated audit log file")
        
        except Exception as e:
            logger.error("Failed to rotate audit log file: %s", str(e))
    
    def _check_for_alerts(self, event: AuditEvent) -> None:
        """
        Check if an event should trigger an alert.
        
        Args:
            event: The audit event to check
        """
        if not self.alert_handler:
            return
        
        # Check if severity requires an alert
        if event.severity.value in self.config["alert_on_severity"]:
            try:
                # Send alert
                self.alert_handler({
                    "event_id": event.event_id,
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "category": event.category.value,
                    "severity": event.severity.value,
                    "user_id": event.user_id,
                    "tenant_id": event.tenant_id,
                    "source": event.source,
                    "details": event.details,
                })
                
                # Update metrics
                self.metrics["alerts_triggered"] += 1
                
                logger.info("Triggered alert for event %s", event.event_id)
            
            except Exception as e:
                logger.error("Failed to send alert: %s", str(e))
    
    def log_event(
        self,
        event_type: str,
        category: AuditEventCategory,
        severity: AuditEventSeverity,
        user_id: str,
        tenant_id: str,
        source: str,
        details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of the event
            category: Category of the event
            severity: Severity of the event
            user_id: ID of the user associated with the event
            tenant_id: ID of the tenant associated with the event
            source: Source of the event
            details: Details of the event
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Generate a unique ID for the event
        event_id = str(uuid.uuid4())
        
        # Create the audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=time.time(),
            event_type=event_type,
            category=category,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=details,
            metadata=metadata or {},
            previous_hash=self._last_event_hash
        )
        
        # Compute hash for the event
        event.hash = self._compute_event_hash(event)
        self._last_event_hash = event.hash
        
        # Add to buffer, respecting buffer size
        self._event_buffer.append(event)
        if len(self._event_buffer) > self.config["buffer_size"]:
            self._event_buffer.pop(0)
        
        # Store the event
        self._store_event(event)
        
        # Log to console and file
        self._log_to_console(event)
        self._log_to_file(event)
        
        # Check for alerts
        self._check_for_alerts(event)
        
        # Update metrics
        self.metrics["events_logged"] += 1
        self.metrics["events_by_severity"][event.severity.value] += 1
        self.metrics["events_by_category"][event.category.value] += 1
        
        return event
    
    def log_authentication_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        source: str,
        success: bool,
        details: Dict[str, Any],
        severity: Optional[AuditEventSeverity] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log an authentication event.
        
        Args:
            event_type: Type of the authentication event
            user_id: ID of the user
            tenant_id: ID of the tenant
            source: Source of the event
            success: Whether authentication was successful
            details: Details of the event
            severity: Optional severity override
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Determine severity based on success
        if severity is None:
            severity = AuditEventSeverity.INFO if success else AuditEventSeverity.WARNING
        
        # Add success flag to details
        event_details = {
            "success": success,
            **details
        }
        
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.AUTHENTICATION,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=event_details,
            metadata=metadata
        )
    
    def log_authorization_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        source: str,
        resource: str,
        action: str,
        allowed: bool,
        details: Dict[str, Any],
        severity: Optional[AuditEventSeverity] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log an authorization event.
        
        Args:
            event_type: Type of the authorization event
            user_id: ID of the user
            tenant_id: ID of the tenant
            source: Source of the event
            resource: Resource being accessed
            action: Action being performed
            allowed: Whether the action was allowed
            details: Details of the event
            severity: Optional severity override
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Determine severity based on allowed
        if severity is None:
            severity = AuditEventSeverity.INFO if allowed else AuditEventSeverity.WARNING
        
        # Add authorization details
        event_details = {
            "resource": resource,
            "action": action,
            "allowed": allowed,
            **details
        }
        
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.AUTHORIZATION,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=event_details,
            metadata=metadata
        )
    
    def log_data_access_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        source: str,
        data_type: str,
        data_id: str,
        operation: str,
        details: Dict[str, Any],
        severity: AuditEventSeverity = AuditEventSeverity.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log a data access event.
        
        Args:
            event_type: Type of the data access event
            user_id: ID of the user
            tenant_id: ID of the tenant
            source: Source of the event
            data_type: Type of data being accessed
            data_id: ID of the data being accessed
            operation: Operation being performed
            details: Details of the event
            severity: Severity of the event
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Add data access details
        event_details = {
            "data_type": data_type,
            "data_id": data_id,
            "operation": operation,
            **details
        }
        
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.DATA_ACCESS,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=event_details,
            metadata=metadata
        )
    
    def log_system_event(
        self,
        event_type: str,
        source: str,
        component: str,
        details: Dict[str, Any],
        severity: AuditEventSeverity = AuditEventSeverity.INFO,
        user_id: str = "system",
        tenant_id: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log a system event.
        
        Args:
            event_type: Type of the system event
            source: Source of the event
            component: System component
            details: Details of the event
            severity: Severity of the event
            user_id: ID of the user (defaults to "system")
            tenant_id: ID of the tenant (defaults to "system")
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Add system details
        event_details = {
            "component": component,
            **details
        }
        
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.SYSTEM,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=event_details,
            metadata=metadata
        )
    
    def log_security_event(
        self,
        event_type: str,
        source: str,
        details: Dict[str, Any],
        severity: AuditEventSeverity,
        user_id: str,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log a security event.
        
        Args:
            event_type: Type of the security event
            source: Source of the event
            details: Details of the event
            severity: Severity of the event
            user_id: ID of the user
            tenant_id: ID of the tenant
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.SECURITY,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=details,
            metadata=metadata
        )
    
    def log_compliance_event(
        self,
        event_type: str,
        source: str,
        regulation: str,
        details: Dict[str, Any],
        severity: AuditEventSeverity = AuditEventSeverity.INFO,
        user_id: str = "system",
        tenant_id: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log a compliance event.
        
        Args:
            event_type: Type of the compliance event
            source: Source of the event
            regulation: Regulation related to the event
            details: Details of the event
            severity: Severity of the event
            user_id: ID of the user (defaults to "system")
            tenant_id: ID of the tenant (defaults to "system")
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Add compliance details
        event_details = {
            "regulation": regulation,
            **details
        }
        
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.COMPLIANCE,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=event_details,
            metadata=metadata
        )
    
    def log_consent_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        source: str,
        consent_id: str,
        scope: str,
        status: str,
        details: Dict[str, Any],
        severity: AuditEventSeverity = AuditEventSeverity.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log a consent event.
        
        Args:
            event_type: Type of the consent event
            user_id: ID of the user
            tenant_id: ID of the tenant
            source: Source of the event
            consent_id: ID of the consent record
            scope: Scope of the consent
            status: Status of the consent
            details: Details of the event
            severity: Severity of the event
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Add consent details
        event_details = {
            "consent_id": consent_id,
            "scope": scope,
            "status": status,
            **details
        }
        
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.CONSENT,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=event_details,
            metadata=metadata
        )
    
    def log_admin_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        source: str,
        target_user_id: Optional[str],
        target_resource: str,
        action: str,
        details: Dict[str, Any],
        severity: AuditEventSeverity = AuditEventSeverity.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log an administrative event.
        
        Args:
            event_type: Type of the administrative event
            user_id: ID of the user performing the action
            tenant_id: ID of the tenant
            source: Source of the event
            target_user_id: Optional ID of the target user
            target_resource: Resource being administered
            action: Action being performed
            details: Details of the event
            severity: Severity of the event
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Add admin details
        event_details = {
            "target_resource": target_resource,
            "action": action,
            **details
        }
        
        if target_user_id:
            event_details["target_user_id"] = target_user_id
        
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.ADMIN,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=event_details,
            metadata=metadata
        )
    
    def log_api_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        source: str,
        api_endpoint: str,
        method: str,
        status_code: int,
        details: Dict[str, Any],
        severity: Optional[AuditEventSeverity] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Log an API event.
        
        Args:
            event_type: Type of the API event
            user_id: ID of the user
            tenant_id: ID of the tenant
            source: Source of the event
            api_endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            details: Details of the event
            severity: Optional severity override
            metadata: Additional metadata for the event
            
        Returns:
            The created audit event
        """
        # Determine severity based on status code
        if severity is None:
            if 200 <= status_code < 300:
                severity = AuditEventSeverity.INFO
            elif 400 <= status_code < 500:
                severity = AuditEventSeverity.WARNING
            elif 500 <= status_code < 600:
                severity = AuditEventSeverity.ERROR
            else:
                severity = AuditEventSeverity.INFO
        
        # Add API details
        event_details = {
            "api_endpoint": api_endpoint,
            "method": method,
            "status_code": status_code,
            **details
        }
        
        # Log the event
        return self.log_event(
            event_type=event_type,
            category=AuditEventCategory.API,
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            source=source,
            details=event_details,
            metadata=metadata
        )
    
    def get_recent_events(
        self,
        count: int = 10,
        category: Optional[AuditEventCategory] = None,
        severity: Optional[AuditEventSeverity] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> List[AuditEvent]:
        """
        Get recent audit events.
        
        Args:
            count: Maximum number of events to return
            category: Optional category filter
            severity: Optional severity filter
            user_id: Optional user ID filter
            tenant_id: Optional tenant ID filter
            
        Returns:
            List of recent audit events
        """
        # Start with all events in buffer
        events = self._event_buffer.copy()
        
        # Apply filters
        if category:
            events = [e for e in events if e.category == category]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Limit to requested count
        return events[:count]
    
    def verify_event_chain(self, start_index: int = 0, count: int = 100) -> Tuple[bool, Optional[str]]:
        """
        Verify the integrity of the event chain.
        
        Args:
            start_index: Index to start verification from
            count: Maximum number of events to verify
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self._event_buffer:
            return True, None
        
        # Get events to verify
        events = self._event_buffer[start_index:start_index + count]
        
        # Verify each event's hash chain
        for i, event in enumerate(events[1:], 1):
            previous_event = events[i - 1]
            
            # Verify previous hash reference
            if event.previous_hash != previous_event.hash:
                return False, f"Hash chain broken between events {previous_event.event_id} and {event.event_id}"
            
            # Verify event hash
            computed_hash = self._compute_event_hash(event)
            if computed_hash != event.hash:
                return False, f"Event hash mismatch for event {event.event_id}"
        
        return True, None
    
    def export_events(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        category: Optional[AuditEventCategory] = None,
        severity: Optional[AuditEventSeverity] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        include_hash: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Export audit events for compliance reporting.
        
        Args:
            start_time: Optional start time filter
            end_time: Optional end time filter
            category: Optional category filter
            severity: Optional severity filter
            user_id: Optional user ID filter
            tenant_id: Optional tenant ID filter
            include_hash: Whether to include hash information
            
        Returns:
            List of audit events as dictionaries
        """
        # Start with events in buffer
        events = self._event_buffer.copy()
        
        # Apply time filters
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # Apply other filters
        if category:
            events = [e for e in events if e.category == category]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        
        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)
        
        # Convert to dictionaries
        result = []
        for event in events:
            event_dict = {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "category": event.category.value,
                "severity": event.severity.value,
                "user_id": event.user_id,
                "tenant_id": event.tenant_id,
                "source": event.source,
                "details": event.details,
            }
            
            # Include hash information if requested
            if include_hash:
                event_dict["hash"] = event.hash
                event_dict["previous_hash"] = event.previous_hash
            
            result.append(event_dict)
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current audit metrics."""
        return self.metrics.copy()
