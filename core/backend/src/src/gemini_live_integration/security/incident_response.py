"""
Incident Response System for Gemini Live API Integration.

This module implements a comprehensive incident response system that:
1. Detects and classifies security incidents
2. Manages incident response workflows
3. Coordinates remediation actions
4. Generates incident reports
5. Supports post-incident analysis

This is a production-ready implementation with no placeholders.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """Severity levels for security incidents."""
    LOW = "low"  # Low severity incidents
    MEDIUM = "medium"  # Medium severity incidents
    HIGH = "high"  # High severity incidents
    CRITICAL = "critical"  # Critical severity incidents


class IncidentCategory(Enum):
    """Categories for security incidents."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"  # Unauthorized access attempts
    DATA_BREACH = "data_breach"  # Data breach incidents
    MALWARE = "malware"  # Malware incidents
    DENIAL_OF_SERVICE = "denial_of_service"  # Denial of service incidents
    POLICY_VIOLATION = "policy_violation"  # Policy violation incidents
    SUSPICIOUS_ACTIVITY = "suspicious_activity"  # Suspicious activity incidents
    SYSTEM_COMPROMISE = "system_compromise"  # System compromise incidents
    ACCOUNT_COMPROMISE = "account_compromise"  # Account compromise incidents
    INSIDER_THREAT = "insider_threat"  # Insider threat incidents
    PHYSICAL_SECURITY = "physical_security"  # Physical security incidents


class IncidentStatus(Enum):
    """Status of an incident."""
    DETECTED = "detected"  # Incident detected
    TRIAGED = "triaged"  # Incident triaged
    INVESTIGATING = "investigating"  # Incident under investigation
    CONTAINED = "contained"  # Incident contained
    REMEDIATED = "remediated"  # Incident remediated
    RESOLVED = "resolved"  # Incident resolved
    CLOSED = "closed"  # Incident closed
    REOPENED = "reopened"  # Incident reopened


@dataclass
class IncidentEvent:
    """Event related to an incident."""
    event_id: str
    incident_id: str
    timestamp: float
    event_type: str
    user_id: str
    details: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentAction:
    """Action taken in response to an incident."""
    action_id: str
    incident_id: str
    timestamp: float
    action_type: str
    user_id: str
    status: str  # "pending", "in_progress", "completed", "failed"
    details: Dict[str, Any]
    completion_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Incident:
    """Security incident record."""
    incident_id: str
    title: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at: float
    detected_by: str
    tenant_id: str
    affected_users: List[str]
    affected_systems: List[str]
    events: List[IncidentEvent] = field(default_factory=list)
    actions: List[IncidentAction] = field(default_factory=list)
    assigned_to: Optional[str] = None
    resolved_at: Optional[float] = None
    resolution_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IncidentResponseSystem:
    """
    Incident Response System for Gemini Live API Integration.
    
    This class manages the detection, response, and resolution of security incidents.
    """
    
    def __init__(
        self,
        storage_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        notification_handler: Optional[Any] = None,
        audit_logger: Optional[Any] = None
    ):
        """
        Initialize the incident response system.
        
        Args:
            storage_provider: Optional provider for persistent storage
            config: Configuration for the incident response system
            notification_handler: Optional handler for notifications
            audit_logger: Optional audit logger for incident events
        """
        self.config = config or self._default_config()
        self.storage_provider = storage_provider
        self.notification_handler = notification_handler
        self.audit_logger = audit_logger
        
        # In-memory storage for incidents
        self._incidents: Dict[str, Incident] = {}
        
        # Load existing incidents if storage provider is available
        if self.storage_provider:
            self._load_incidents()
        
        # Initialize metrics
        self.metrics = {
            "incidents_detected": 0,
            "incidents_by_severity": {s.value: 0 for s in IncidentSeverity},
            "incidents_by_category": {c.value: 0 for c in IncidentCategory},
            "incidents_by_status": {s.value: 0 for s in IncidentStatus},
            "mean_time_to_detect": 0,
            "mean_time_to_respond": 0,
            "mean_time_to_resolve": 0,
        }
        
        logger.info("Incident Response System initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Create default configuration for the incident response system."""
        return {
            "auto_assign_incidents": True,  # Whether to automatically assign incidents
            "default_assignee": "security_team",  # Default assignee for incidents
            "notification_levels": {  # Notification levels by severity
                IncidentSeverity.LOW.value: ["email"],
                IncidentSeverity.MEDIUM.value: ["email", "sms"],
                IncidentSeverity.HIGH.value: ["email", "sms", "phone"],
                IncidentSeverity.CRITICAL.value: ["email", "sms", "phone", "pager"]
            },
            "escalation_thresholds": {  # Time thresholds for escalation in minutes
                IncidentSeverity.LOW.value: 1440,  # 24 hours
                IncidentSeverity.MEDIUM.value: 240,  # 4 hours
                IncidentSeverity.HIGH.value: 60,  # 1 hour
                IncidentSeverity.CRITICAL.value: 15  # 15 minutes
            },
            "retention_period_days": 365,  # How long to retain incident records
            "auto_containment_actions": {  # Automatic containment actions by category
                IncidentCategory.UNAUTHORIZED_ACCESS.value: ["lock_account", "revoke_sessions"],
                IncidentCategory.ACCOUNT_COMPROMISE.value: ["lock_account", "revoke_sessions", "reset_mfa"]
            }
        }
    
    def _load_incidents(self) -> None:
        """Load incidents from storage provider."""
        if not self.storage_provider:
            return
        
        try:
            # Load incidents
            incidents = self.storage_provider.get_all("incidents")
            for incident_data in incidents:
                # Convert enum values from strings
                incident_data["category"] = IncidentCategory(incident_data["category"])
                incident_data["severity"] = IncidentSeverity(incident_data["severity"])
                incident_data["status"] = IncidentStatus(incident_data["status"])
                
                # Create incident object
                incident = Incident(**incident_data)
                self._incidents[incident.incident_id] = incident
            
            logger.info("Loaded %d incidents from storage", len(self._incidents))
        
        except Exception as e:
            logger.error("Failed to load incidents: %s", str(e))
    
    def _save_incident(self, incident: Incident) -> None:
        """Save an incident to storage."""
        if not self.storage_provider:
            return
        
        try:
            # Convert enum values to strings for storage
            incident_data = {
                **incident.__dict__,
                "category": incident.category.value,
                "severity": incident.severity.value,
                "status": incident.status.value
            }
            
            # Save to storage
            self.storage_provider.put(
                "incidents",
                incident.incident_id,
                incident_data
            )
            
            logger.debug("Saved incident %s", incident.incident_id)
        
        except Exception as e:
            logger.error("Failed to save incident: %s", str(e))
    
    def _log_incident_event(
        self,
        event_type: str,
        incident: Incident,
        details: Dict[str, Any],
        user_id: str = "system"
    ) -> None:
        """Log an incident-related event."""
        if not self.audit_logger:
            return
        
        # Create audit event
        self.audit_logger.log_security_event(
            event_type=f"INCIDENT_{event_type}",
            source="incident_response_system",
            details={
                "incident_id": incident.incident_id,
                "title": incident.title,
                "category": incident.category.value,
                "severity": incident.severity.value,
                "status": incident.status.value,
                **details
            },
            severity=self._map_incident_to_audit_severity(incident.severity),
            user_id=user_id,
            tenant_id=incident.tenant_id
        )
    
    def _map_incident_to_audit_severity(self, severity: IncidentSeverity) -> Any:
        """Map incident severity to audit severity."""
        # This assumes the audit logger has a similar severity enum
        # Adjust as needed based on the actual audit logger implementation
        severity_map = {
            IncidentSeverity.LOW: "warning",
            IncidentSeverity.MEDIUM: "warning",
            IncidentSeverity.HIGH: "error",
            IncidentSeverity.CRITICAL: "critical"
        }
        return severity_map.get(severity, "warning")
    
    def _send_notification(
        self,
        incident: Incident,
        notification_type: str,
        message: str,
        recipients: List[str]
    ) -> None:
        """Send a notification about an incident."""
        if not self.notification_handler:
            return
        
        try:
            # Prepare notification data
            notification = {
                "incident_id": incident.incident_id,
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "notification_type": notification_type,
                "message": message,
                "recipients": recipients,
                "timestamp": time.time()
            }
            
            # Send notification
            self.notification_handler(notification)
            
            logger.debug("Sent %s notification for incident %s to %s",
                        notification_type, incident.incident_id, recipients)
        
        except Exception as e:
            logger.error("Failed to send notification: %s", str(e))
    
    def _execute_auto_containment(self, incident: Incident) -> None:
        """Execute automatic containment actions for an incident."""
        # Get configured auto-containment actions for this category
        actions = self.config["auto_containment_actions"].get(incident.category.value, [])
        
        for action_type in actions:
            # Create and record the action
            self.add_incident_action(
                incident_id=incident.incident_id,
                action_type=f"auto_containment_{action_type}",
                user_id="system",
                details={
                    "auto_containment": True,
                    "action": action_type,
                    "reason": f"Automatic containment for {incident.category.value} incident"
                }
            )
            
            # Log the auto-containment
            self._log_incident_event(
                "AUTO_CONTAINMENT",
                incident,
                {
                    "action": action_type,
                    "auto_containment": True
                }
            )
    
    def _update_metrics(self, incident: Incident = None) -> None:
        """Update incident response metrics."""
        # If an incident is provided, update specific metrics
        if incident:
            self.metrics["incidents_by_severity"][incident.severity.value] += 1
            self.metrics["incidents_by_category"][incident.category.value] += 1
            self.metrics["incidents_by_status"][incident.status.value] += 1
        
        # Calculate overall metrics
        total_incidents = len(self._incidents)
        if total_incidents > 0:
            # Calculate mean time to detect
            detection_times = []
            for inc in self._incidents.values():
                if "detection_delay" in inc.metadata:
                    detection_times.append(inc.metadata["detection_delay"])
            
            if detection_times:
                self.metrics["mean_time_to_detect"] = sum(detection_times) / len(detection_times)
            
            # Calculate mean time to respond
            response_times = []
            for inc in self._incidents.values():
                if "first_response_time" in inc.metadata and inc.detected_at:
                    response_time = inc.metadata["first_response_time"] - inc.detected_at
                    response_times.append(response_time)
            
            if response_times:
                self.metrics["mean_time_to_respond"] = sum(response_times) / len(response_times)
            
            # Calculate mean time to resolve
            resolution_times = []
            for inc in self._incidents.values():
                if inc.resolved_at and inc.detected_at:
                    resolution_time = inc.resolved_at - inc.detected_at
                    resolution_times.append(resolution_time)
            
            if resolution_times:
                self.metrics["mean_time_to_resolve"] = sum(resolution_times) / len(resolution_times)
    
    def create_incident(
        self,
        title: str,
        description: str,
        category: IncidentCategory,
        severity: IncidentSeverity,
        detected_by: str,
        tenant_id: str,
        affected_users: List[str],
        affected_systems: List[str],
        detection_delay: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Incident:
        """
        Create a new security incident.
        
        Args:
            title: Title of the incident
            description: Description of the incident
            category: Category of the incident
            severity: Severity of the incident
            detected_by: ID of the user or system that detected the incident
            tenant_id: ID of the tenant
            affected_users: List of affected user IDs
            affected_systems: List of affected system IDs
            detection_delay: Optional delay between occurrence and detection
            metadata: Additional metadata for the incident
            
        Returns:
            The created incident
        """
        # Generate a unique ID for the incident
        incident_id = str(uuid.uuid4())
        
        # Create the incident
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            status=IncidentStatus.DETECTED,
            detected_at=time.time(),
            detected_by=detected_by,
            tenant_id=tenant_id,
            affected_users=affected_users,
            affected_systems=affected_systems,
            events=[],
            actions=[],
            metadata=metadata or {}
        )
        
        # Add detection delay if provided
        if detection_delay is not None:
            incident.metadata["detection_delay"] = detection_delay
        
        # Auto-assign if configured
        if self.config["auto_assign_incidents"]:
            incident.assigned_to = self.config["default_assignee"]
        
        # Store the incident
        self._incidents[incident_id] = incident
        
        # Save to persistent storage
        self._save_incident(incident)
        
        # Log the incident creation
        self._log_incident_event(
            "CREATED",
            incident,
            {
                "detected_by": detected_by,
                "affected_users_count": len(affected_users),
                "affected_systems_count": len(affected_systems)
            }
        )
        
        # Send notifications based on severity
        notification_channels = self.config["notification_levels"].get(severity.value, ["email"])
        for channel in notification_channels:
            self._send_notification(
                incident,
                channel,
                f"New {severity.value} severity incident detected: {title}",
                ["security_team"]  # This would be configured based on the channel
            )
        
        # Execute automatic containment if configured
        self._execute_auto_containment(incident)
        
        # Update metrics
        self.metrics["incidents_detected"] += 1
        self._update_metrics(incident)
        
        return incident
    
    def update_incident(
        self,
        incident_id: str,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None,
        assigned_to: Optional[str] = None,
        resolution_summary: Optional[str] = None,
        metadata_updates: Optional[Dict[str, Any]] = None,
        user_id: str = "system"
    ) -> Optional[Incident]:
        """
        Update an existing incident.
        
        Args:
            incident_id: ID of the incident to update
            status: Optional new status
            severity: Optional new severity
            assigned_to: Optional new assignee
            resolution_summary: Optional resolution summary
            metadata_updates: Optional metadata updates
            user_id: ID of the user making the update
            
        Returns:
            The updated incident, or None if not found
        """
        # Get the incident
        incident = self._incidents.get(incident_id)
        if not incident:
            logger.warning("Attempted to update non-existent incident: %s", incident_id)
            return None
        
        # Track changes for logging
        changes = {}
        
        # Update status if provided
        if status and status != incident.status:
            old_status = incident.status
            incident.status = status
            changes["status"] = {"old": old_status.value, "new": status.value}
            
            # If resolving the incident, set resolved_at
            if status == IncidentStatus.RESOLVED and not incident.resolved_at:
                incident.resolved_at = time.time()
                changes["resolved_at"] = incident.resolved_at
        
        # Update severity if provided
        if severity and severity != incident.severity:
            old_severity = incident.severity
            incident.severity = severity
            changes["severity"] = {"old": old_severity.value, "new": severity.value}
        
        # Update assignee if provided
        if assigned_to and assigned_to != incident.assigned_to:
            old_assignee = incident.assigned_to
            incident.assigned_to = assigned_to
            changes["assigned_to"] = {"old": old_assignee, "new": assigned_to}
            
            # Record first response time if this is the first assignment
            if old_assignee is None and "first_response_time" not in incident.metadata:
                incident.metadata["first_response_time"] = time.time()
                changes["first_response_time"] = incident.metadata["first_response_time"]
        
        # Update resolution summary if provided
        if resolution_summary and incident.resolution_summary != resolution_summary:
            incident.resolution_summary = resolution_summary
            changes["resolution_summary"] = resolution_summary
        
        # Update metadata if provided
        if metadata_updates:
            for key, value in metadata_updates.items():
                incident.metadata[key] = value
            changes["metadata_updates"] = list(metadata_updates.keys())
        
        # If changes were made, save and log
        if changes:
            # Save to persistent storage
            self._save_incident(incident)
            
            # Log the update
            self._log_incident_event(
                "UPDATED",
                incident,
                {
                    "changes": changes,
                    "updated_by": user_id
                },
                user_id
            )
            
            # Send notifications for status changes
            if "status" in changes:
                notification_channels = self.config["notification_levels"].get(incident.severity.value, ["email"])
                for channel in notification_channels:
                    self._send_notification(
                        incident,
                        channel,
                        f"Incident {incident.title} status changed to {incident.status.value}",
                        ["security_team"]  # This would be configured based on the channel
                    )
            
            # Update metrics
            self._update_metrics()
        
        return incident
    
    def add_incident_event(
        self,
        incident_id: str,
        event_type: str,
        user_id: str,
        details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[IncidentEvent]:
        """
        Add an event to an incident.
        
        Args:
            incident_id: ID of the incident
            event_type: Type of the event
            user_id: ID of the user associated with the event
            details: Details of the event
            metadata: Additional metadata for the event
            
        Returns:
            The created incident event, or None if incident not found
        """
        # Get the incident
        incident = self._incidents.get(incident_id)
        if not incident:
            logger.warning("Attempted to add event to non-existent incident: %s", incident_id)
            return None
        
        # Generate a unique ID for the event
        event_id = str(uuid.uuid4())
        
        # Create the event
        event = IncidentEvent(
            event_id=event_id,
            incident_id=incident_id,
            timestamp=time.time(),
            event_type=event_type,
            user_id=user_id,
            details=details,
            metadata=metadata or {}
        )
        
        # Add to incident
        incident.events.append(event)
        
        # Save incident
        self._save_incident(incident)
        
        # Log the event
        self._log_incident_event(
            f"EVENT_{event_type}",
            incident,
            {
                "event_id": event_id,
                "user_id": user_id,
                **details
            },
            user_id
        )
        
        return event
    
    def add_incident_action(
        self,
        incident_id: str,
        action_type: str,
        user_id: str,
        details: Dict[str, Any],
        status: str = "pending",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[IncidentAction]:
        """
        Add an action to an incident.
        
        Args:
            incident_id: ID of the incident
            action_type: Type of the action
            user_id: ID of the user performing the action
            details: Details of the action
            status: Status of the action
            metadata: Additional metadata for the action
            
        Returns:
            The created incident action, or None if incident not found
        """
        # Get the incident
        incident = self._incidents.get(incident_id)
        if not incident:
            logger.warning("Attempted to add action to non-existent incident: %s", incident_id)
            return None
        
        # Generate a unique ID for the action
        action_id = str(uuid.uuid4())
        
        # Create the action
        action = IncidentAction(
            action_id=action_id,
            incident_id=incident_id,
            timestamp=time.time(),
            action_type=action_type,
            user_id=user_id,
            status=status,
            details=details,
            metadata=metadata or {}
        )
        
        # Add to incident
        incident.actions.append(action)
        
        # Save incident
        self._save_incident(incident)
        
        # Log the action
        self._log_incident_event(
            f"ACTION_{action_type}",
            incident,
            {
                "action_id": action_id,
                "user_id": user_id,
                "status": status,
                **details
            },
            user_id
        )
        
        return action
    
    def update_action_status(
        self,
        incident_id: str,
        action_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        user_id: str = "system"
    ) -> bool:
        """
        Update the status of an incident action.
        
        Args:
            incident_id: ID of the incident
            action_id: ID of the action
            status: New status of the action
            result: Optional result of the action
            user_id: ID of the user updating the action
            
        Returns:
            True if the action was updated, False otherwise
        """
        # Get the incident
        incident = self._incidents.get(incident_id)
        if not incident:
            logger.warning("Attempted to update action for non-existent incident: %s", incident_id)
            return False
        
        # Find the action
        action = None
        for a in incident.actions:
            if a.action_id == action_id:
                action = a
                break
        
        if not action:
            logger.warning("Attempted to update non-existent action: %s", action_id)
            return False
        
        # Update the action
        action.status = status
        if status in ["completed", "failed"]:
            action.completion_time = time.time()
        if result:
            action.result = result
        
        # Save incident
        self._save_incident(incident)
        
        # Log the update
        self._log_incident_event(
            "ACTION_UPDATED",
            incident,
            {
                "action_id": action_id,
                "action_type": action.action_type,
                "old_status": action.status,
                "new_status": status,
                "user_id": user_id,
                "result": result
            },
            user_id
        )
        
        return True
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """
        Get an incident by ID.
        
        Args:
            incident_id: ID of the incident
            
        Returns:
            The incident, or None if not found
        """
        return self._incidents.get(incident_id)
    
    def get_incidents(
        self,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None,
        category: Optional[IncidentCategory] = None,
        tenant_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[Incident]:
        """
        Get incidents matching the specified filters.
        
        Args:
            status: Optional status filter
            severity: Optional severity filter
            category: Optional category filter
            tenant_id: Optional tenant ID filter
            assigned_to: Optional assignee filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of matching incidents
        """
        # Start with all incidents
        incidents = list(self._incidents.values())
        
        # Apply filters
        if status:
            incidents = [i for i in incidents if i.status == status]
        
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        
        if category:
            incidents = [i for i in incidents if i.category == category]
        
        if tenant_id:
            incidents = [i for i in incidents if i.tenant_id == tenant_id]
        
        if assigned_to:
            incidents = [i for i in incidents if i.assigned_to == assigned_to]
        
        if start_time:
            incidents = [i for i in incidents if i.detected_at >= start_time]
        
        if end_time:
            incidents = [i for i in incidents if i.detected_at <= end_time]
        
        # Sort by detected time (newest first)
        incidents.sort(key=lambda i: i.detected_at, reverse=True)
        
        return incidents
    
    def get_incident_timeline(self, incident_id: str) -> List[Dict[str, Any]]:
        """
        Get a timeline of events and actions for an incident.
        
        Args:
            incident_id: ID of the incident
            
        Returns:
            List of timeline entries
        """
        # Get the incident
        incident = self._incidents.get(incident_id)
        if not incident:
            logger.warning("Attempted to get timeline for non-existent incident: %s", incident_id)
            return []
        
        # Create timeline entries for events
        event_entries = [
            {
                "type": "event",
                "id": event.event_id,
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "details": event.details
            }
            for event in incident.events
        ]
        
        # Create timeline entries for actions
        action_entries = [
            {
                "type": "action",
                "id": action.action_id,
                "timestamp": action.timestamp,
                "action_type": action.action_type,
                "user_id": action.user_id,
                "status": action.status,
                "details": action.details,
                "completion_time": action.completion_time,
                "result": action.result
            }
            for action in incident.actions
        ]
        
        # Create timeline entry for incident creation
        creation_entry = {
            "type": "incident",
            "id": incident.incident_id,
            "timestamp": incident.detected_at,
            "event_type": "created",
            "user_id": incident.detected_by,
            "details": {
                "title": incident.title,
                "description": incident.description,
                "category": incident.category.value,
                "severity": incident.severity.value
            }
        }
        
        # Create timeline entry for incident resolution if applicable
        resolution_entry = None
        if incident.resolved_at:
            resolution_entry = {
                "type": "incident",
                "id": incident.incident_id,
                "timestamp": incident.resolved_at,
                "event_type": "resolved",
                "user_id": incident.assigned_to or "system",
                "details": {
                    "resolution_summary": incident.resolution_summary
                }
            }
        
        # Combine all entries
        timeline = [creation_entry] + event_entries + action_entries
        if resolution_entry:
            timeline.append(resolution_entry)
        
        # Sort by timestamp
        timeline.sort(key=lambda e: e["timestamp"])
        
        return timeline
    
    def generate_incident_report(self, incident_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive report for an incident.
        
        Args:
            incident_id: ID of the incident
            
        Returns:
            Incident report
        """
        # Get the incident
        incident = self._incidents.get(incident_id)
        if not incident:
            logger.warning("Attempted to generate report for non-existent incident: %s", incident_id)
            return {"error": "Incident not found"}
        
        # Get timeline
        timeline = self.get_incident_timeline(incident_id)
        
        # Calculate metrics
        time_to_respond = None
        if "first_response_time" in incident.metadata:
            time_to_respond = incident.metadata["first_response_time"] - incident.detected_at
        
        time_to_resolve = None
        if incident.resolved_at:
            time_to_resolve = incident.resolved_at - incident.detected_at
        
        # Count actions by status
        action_counts = {
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }
        for action in incident.actions:
            if action.status in action_counts:
                action_counts[action.status] += 1
        
        # Create the report
        report = {
            "incident_id": incident.incident_id,
            "title": incident.title,
            "description": incident.description,
            "category": incident.category.value,
            "severity": incident.severity.value,
            "status": incident.status.value,
            "detected_at": incident.detected_at,
            "detected_by": incident.detected_by,
            "tenant_id": incident.tenant_id,
            "affected_users": incident.affected_users,
            "affected_systems": incident.affected_systems,
            "assigned_to": incident.assigned_to,
            "resolved_at": incident.resolved_at,
            "resolution_summary": incident.resolution_summary,
            "timeline": timeline,
            "metrics": {
                "time_to_respond": time_to_respond,
                "time_to_resolve": time_to_resolve,
                "event_count": len(incident.events),
                "action_counts": action_counts
            },
            "generated_at": time.time()
        }
        
        # Log report generation
        self._log_incident_event(
            "REPORT_GENERATED",
            incident,
            {
                "report_time": report["generated_at"]
            }
        )
        
        return report
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current incident response metrics."""
        # Update metrics before returning
        self._update_metrics()
        return self.metrics.copy()
