"""
Gemini Incident Response Manager for Dr. TARDIS.

This module provides incident response management for the Gemini Live API integration,
including incident detection, notification, and response coordination.

Author: Manus Agent
Date: May 26, 2025
"""

import json
import logging
import time
import uuid
import os
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

from src.security.gemini_audit_manager import GeminiAuditManager, GeminiAuditCategory, AuditEventSeverity
from src.plugins.notification_service import NotificationService

class IncidentSeverity(Enum):
    """Severity levels for security incidents."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IncidentStatus(Enum):
    """Status values for security incidents."""
    NEW = "new"
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"

class IncidentCategory(Enum):
    """Categories for security incidents."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MALWARE = "malware"
    DENIAL_OF_SERVICE = "denial_of_service"
    POLICY_VIOLATION = "policy_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    API_ABUSE = "api_abuse"
    CONFIGURATION_ERROR = "configuration_error"

class GeminiIncidentResponseManager:
    """
    Manages security incident response for the Gemini Live API integration.
    
    Provides incident detection, notification, and response coordination.
    """
    
    def __init__(
        self,
        audit_manager: GeminiAuditManager,
        notification_service: Optional[NotificationService] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Gemini Incident Response Manager.
        
        Args:
            audit_manager: Instance of GeminiAuditManager for audit logging
            notification_service: Optional notification service for alerts
            config: Configuration options for incident response
        """
        self.audit_manager = audit_manager
        self.notification_service = notification_service
        
        # Default configuration
        self.config = {
            "incident_retention_days": 365,  # 1 year retention for incidents
            "auto_escalation": True,  # Automatically escalate critical incidents
            "notification_enabled": True,  # Enable incident notifications
            "evidence_retention_days": 730,  # 2 years retention for evidence
            "max_incidents_per_report": 3,  # Maximum incidents to include in reports
            "log_level": logging.INFO
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        # Initialize logger
        self.logger = logging.getLogger("dr_tardis.security.incident_response")
        try:
            self.logger.setLevel(self.config["log_level"])
        except (TypeError, ValueError):
            # Handle case where log_level might be a MagicMock or invalid
            self.logger.setLevel(logging.INFO)
        
        # Initialize incident store
        self.incidents = {}
        
        # Initialize notification handlers
        self.notification_handlers = {}
        
        # Initialize incident actions store
        self.incident_actions = {}
        
        # Register default notification handler if notification service is provided
        if notification_service and self.config["notification_enabled"]:
            self.register_notification_handler("default", self._default_notification_handler)
    
    def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        source: str,
        affected_components: Optional[List[str]] = None,
        reported_by: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        category: IncidentCategory = IncidentCategory.SUSPICIOUS_ACTIVITY
    ) -> str:
        """
        Create a new security incident.
        
        Args:
            title: Title for the incident
            description: Description of the incident
            severity: Severity level of the incident
            source: Source of the incident detection
            affected_components: List of affected system components
            reported_by: Person or system that reported the incident
            details: Additional details about the incident
            user_id: ID of the user associated with the incident
            category: Category of the incident (default: SUSPICIOUS_ACTIVITY)
            
        Returns:
            ID of the created incident
        """
        # Generate incident ID
        incident_id = str(uuid.uuid4())
        
        # Create incident record
        incident = {
            "incident_id": incident_id,
            "title": title,
            "category": category.value,
            "severity": severity.value,
            "status": IncidentStatus.OPEN.value,
            "description": description,
            "source": source,
            "details": details or {},
            "user_id": user_id,
            "affected_components": affected_components or [],
            "reported_by": reported_by or source,
            "created_at": int(time.time()),
            "updated_at": int(time.time()),
            "assigned_to": None,
            "resolution": None,
            "evidence": [],
            "timeline": [
                {
                    "timestamp": int(time.time()),
                    "action": "created",
                    "details": "Incident created",
                    "actor": reported_by or source
                }
            ]
        }
        
        # Store incident
        self.incidents[incident_id] = incident
        
        # Log incident creation
        self.audit_manager.log_security_event(
            event_type=GeminiAuditCategory.INCIDENT,
            severity=AuditEventSeverity.WARNING,
            details={
                "action": "incident_created",
                "incident_id": incident_id,
                "category": category.value,
                "severity": severity.value,
                "source": source,
                "reported_by": reported_by or source
            },
            user_id=user_id,
            source="incident_response"
        )
        
        # Send notifications
        if self.config["notification_enabled"]:
            self._notify_incident(incident)
        
        # Auto-escalate critical incidents
        if severity == IncidentSeverity.CRITICAL and self.config["auto_escalation"]:
            self._escalate_incident(incident_id)
        
        return incident_id
    
    def update_incident(
        self,
        incident_id: str,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None,
        assigned_to: Optional[str] = None,
        notes: Optional[str] = None,
        resolution: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        resolution_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update an existing incident.
        
        Args:
            incident_id: ID of the incident to update
            status: New status for the incident
            severity: New severity level for the incident
            assigned_to: User the incident is assigned to
            notes: Additional notes about the incident
            resolution: Resolution information
            details: Updated incident details
            resolution_time: Time of resolution (Unix timestamp)
            
        Returns:
            Updated incident record
        """
        # Check if incident exists
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Get incident
        incident = self.incidents[incident_id]
        
        # Track changes for timeline
        changes = []
        
        # Update status if provided
        if status:
            old_status = incident["status"]
            incident["status"] = status.value
            changes.append(f"Status changed from {old_status} to {status.value}")
        
        # Update severity if provided
        if severity:
            old_severity = incident["severity"]
            incident["severity"] = severity.value
            changes.append(f"Severity changed from {old_severity} to {severity.value}")
        
        # Update assignment if provided
        if assigned_to is not None:
            old_assigned = incident.get("assigned_to", "unassigned")
            incident["assigned_to"] = assigned_to
            changes.append(f"Assignment changed from {old_assigned} to {assigned_to}")
        
        # Update notes if provided
        if notes:
            if "notes" not in incident:
                incident["notes"] = []
            incident["notes"].append({
                "timestamp": int(time.time()),
                "content": notes,
                "author": "incident_response_manager"
            })
            changes.append("Notes added")
        
        # Update resolution if provided
        if resolution:
            incident["resolution"] = resolution
            changes.append(f"Resolution updated: {resolution}")
            
            # Add resolution time if provided
            if resolution_time:
                incident["resolution_time"] = resolution_time
                changes.append(f"Resolution time set: {datetime.fromtimestamp(resolution_time).isoformat()}")
        
        # Update details if provided
        if details:
            # Merge with existing details
            incident["details"].update(details)
            changes.append("Details updated")
        
        # Update timestamp
        incident["updated_at"] = int(time.time())
        
        # Add timeline entry
        incident["timeline"].append({
            "timestamp": int(time.time()),
            "action": "updated",
            "details": "; ".join(changes),
            "actor": "incident_response_manager"
        })
        
        # Store updated incident
        self.incidents[incident_id] = incident
        
        # Log incident update
        self.audit_manager.log_security_event(
            event_type=GeminiAuditCategory.INCIDENT,
            severity=AuditEventSeverity.INFO,
            details={
                "action": "incident_updated",
                "incident_id": incident_id,
                "changes": changes
            },
            user_id=incident.get("user_id"),
            source="incident_response"
        )
        
        # Send notifications for significant changes
        if status or severity == IncidentSeverity.CRITICAL:
            self._notify_incident(incident, "updated")
        
        return incident
    
    def get_incident(self, incident_id: str) -> Dict[str, Any]:
        """
        Get an incident by ID.
        
        Args:
            incident_id: ID of the incident to retrieve
            
        Returns:
            Incident record
        """
        # Check if incident exists
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")
        
        return self.incidents[incident_id]
    
    def list_incidents(
        self,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None,
        category: Optional[IncidentCategory] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        user_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List incidents matching criteria.
        
        Args:
            status: Filter by status
            severity: Filter by severity
            category: Filter by category
            start_time: Filter by start time (Unix timestamp)
            end_time: Filter by end time (Unix timestamp)
            user_id: Filter by user ID
            limit: Maximum number of incidents to return
            
        Returns:
            List of matching incidents
        """
        # Set default time range if not specified
        if not end_time:
            end_time = int(time.time())
        if not start_time:
            start_time = end_time - (30 * 24 * 60 * 60)  # 30 days
        
        # Filter incidents
        filtered_incidents = []
        for incident in self.incidents.values():
            # Apply time filter
            created_at = incident["created_at"]
            if created_at < start_time or created_at > end_time:
                continue
            
            # Apply status filter
            if status and incident["status"] != status.value:
                continue
            
            # Apply severity filter
            if severity and incident["severity"] != severity.value:
                continue
            
            # Apply category filter
            if category and incident["category"] != category.value:
                continue
            
            # Apply user filter
            if user_id and incident.get("user_id") != user_id:
                continue
            
            filtered_incidents.append(incident)
        
        # Sort by created_at (newest first)
        filtered_incidents.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply limit
        if limit and len(filtered_incidents) > limit:
            filtered_incidents = filtered_incidents[:limit]
        
        return filtered_incidents
    
    def add_incident_evidence(
        self,
        incident_id: str,
        evidence_type: str,
        content: Any,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add evidence to an incident.
        
        Args:
            incident_id: ID of the incident
            evidence_type: Type of evidence
            content: Evidence content
            description: Description of the evidence
            metadata: Additional metadata about the evidence
            
        Returns:
            ID of the added evidence
        """
        # Check if incident exists
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Generate evidence ID
        evidence_id = str(uuid.uuid4())
        
        # Create evidence record
        evidence = {
            "evidence_id": evidence_id,
            "evidence_type": evidence_type,
            "type": evidence_type,  # Keep original for backward compatibility
            "content": content,
            "description": description or "",
            "metadata": metadata or {},
            "added_at": int(time.time())
        }
        
        # Add evidence to incident
        self.incidents[incident_id]["evidence"].append(evidence)
        
        # Add timeline entry
        self.incidents[incident_id]["timeline"].append({
            "timestamp": int(time.time()),
            "action": "evidence_added",
            "details": f"Evidence added: {description or evidence_type}",
            "actor": "incident_response_manager"
        })
        
        # Update incident timestamp
        self.incidents[incident_id]["updated_at"] = int(time.time())
        
        # Log evidence addition
        self.audit_manager.log_security_event(
            event_type=GeminiAuditCategory.INCIDENT,
            severity=AuditEventSeverity.INFO,
            details={
                "action": "evidence_added",
                "incident_id": incident_id,
                "evidence_id": evidence_id,
                "evidence_type": evidence_type
            },
            user_id=self.incidents[incident_id].get("user_id"),
            source="incident_response"
        )
        
        return evidence_id
    
    def get_incident_evidence(self, incident_id: str, evidence_id: str) -> Dict[str, Any]:
        """
        Get evidence for an incident by ID.
        
        Args:
            incident_id: ID of the incident
            evidence_id: ID of the evidence to retrieve
            
        Returns:
            Evidence record
        """
        # Check if incident exists
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Find evidence by ID
        for evidence in self.incidents[incident_id]["evidence"]:
            if evidence["evidence_id"] == evidence_id:
                return evidence
        
        # Evidence not found
        raise ValueError(f"Evidence {evidence_id} not found for incident {incident_id}")
    
    def add_incident_action(
        self,
        incident_id: str,
        action_type: str,
        description: str,
        assigned_to: Optional[str] = None,
        status: str = "pending",
        due_date: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an action to an incident.
        
        Args:
            incident_id: ID of the incident
            action_type: Type of action (containment, eradication, etc.)
            description: Description of the action
            assigned_to: Person or team assigned to the action
            status: Status of the action
            due_date: Due date for the action (Unix timestamp)
            details: Additional details about the action
            
        Returns:
            ID of the added action
        """
        # Check if incident exists
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Generate action ID
        action_id = str(uuid.uuid4())
        
        # Create action record
        action = {
            "action_id": action_id,
            "incident_id": incident_id,
            "action_type": action_type,
            "description": description,
            "assigned_to": assigned_to,
            "status": status,
            "due_date": due_date,
            "details": details or {},
            "created_at": int(time.time()),
            "updated_at": int(time.time()),
            "completed_at": None
        }
        
        # Initialize actions for this incident if not exists
        if incident_id not in self.incident_actions:
            self.incident_actions[incident_id] = []
        
        # Add action to incident actions
        self.incident_actions[incident_id].append(action)
        
        # Add timeline entry
        self.incidents[incident_id]["timeline"].append({
            "timestamp": int(time.time()),
            "action": "action_added",
            "details": f"Action added: {description}",
            "actor": "incident_response_manager"
        })
        
        # Update incident timestamp
        self.incidents[incident_id]["updated_at"] = int(time.time())
        
        # Log action addition
        self.audit_manager.log_security_event(
            event_type=GeminiAuditCategory.INCIDENT,
            severity=AuditEventSeverity.INFO,
            details={
                "action": "incident_action_added",
                "incident_id": incident_id,
                "action_id": action_id,
                "action_type": action_type,
                "assigned_to": assigned_to
            },
            user_id=self.incidents[incident_id].get("user_id"),
            source="incident_response"
        )
        
        return action_id
    
    def get_incident_actions(self, incident_id: str) -> List[Dict[str, Any]]:
        """
        Get actions for an incident.
        
        Args:
            incident_id: ID of the incident
            
        Returns:
            List of action records
        """
        # Check if incident exists
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Return actions for this incident
        return self.incident_actions.get(incident_id, [])
    
    def generate_incident_report(
        self,
        incident_id: Optional[str] = None,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None,
        time_range: Optional[Tuple[int, int]] = None,
        include_evidence: bool = False,
        include_resolved: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a report for one or more incidents.
        
        Args:
            incident_id: ID of a specific incident to report on
            status: Filter by status
            severity: Filter by severity
            time_range: Time range for the report (start_time, end_time)
            include_evidence: Whether to include evidence in the report
            include_resolved: Whether to include resolved incidents
            
        Returns:
            Incident report
        """
        # Handle single incident case
        if incident_id:
            if incident_id not in self.incidents:
                raise ValueError(f"Incident {incident_id} not found")
            
            incidents = [self.incidents[incident_id]]
        else:
            # Get incidents matching criteria
            if time_range:
                start_time, end_time = time_range
            else:
                end_time = int(time.time())
                start_time = end_time - (7 * 24 * 60 * 60)  # 7 days
            
            incidents = self.list_incidents(
                status=status,
                severity=severity,
                start_time=start_time,
                end_time=end_time,
                limit=self.config["max_incidents_per_report"]
            )
            
            # Filter out resolved incidents if not included
            if not include_resolved:
                incidents = [i for i in incidents if i["status"] != IncidentStatus.RESOLVED.value]
        
        # Generate report
        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": int(time.time()),
            "generated_at_str": datetime.now().isoformat(),
            "time_range": {
                "start": start_time if 'start_time' in locals() else incidents[0]["created_at"] if incidents else int(time.time()),
                "end": end_time if 'end_time' in locals() else int(time.time()),
                "start_date": datetime.fromtimestamp(start_time if 'start_time' in locals() else incidents[0]["created_at"] if incidents else int(time.time())).isoformat(),
                "end_date": datetime.fromtimestamp(end_time if 'end_time' in locals() else int(time.time())).isoformat()
            },
            "total_incidents": len(incidents),
            "incidents": [],
            "severity_counts": {}  # Initialize severity_counts directly in the report
        }
        
        # Add incident details
        for incident in incidents:
            incident_details = {
                "incident_id": incident["incident_id"],
                "title": incident["title"],
                "category": incident["category"],
                "severity": incident["severity"],
                "status": incident["status"],
                "description": incident["description"],
                "created_at": incident["created_at"],
                "created_at_str": datetime.fromtimestamp(incident["created_at"]).isoformat(),
                "updated_at": incident["updated_at"],
                "updated_at_str": datetime.fromtimestamp(incident["updated_at"]).isoformat(),
                "timeline": incident["timeline"]
            }
            
            # Include evidence if requested
            if include_evidence:
                incident_details["evidence"] = incident["evidence"]
            
            report["incidents"].append(incident_details)
        
        # Add summary statistics
        severity_counts = {}
        category_counts = {}
        status_counts = {}
        
        for incident in incidents:
            # Count by severity
            severity = incident["severity"]
            if severity not in severity_counts:
                severity_counts[severity] = 0
            severity_counts[severity] += 1
            
            # Count by category
            category = incident["category"]
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
            
            # Count by status
            status = incident["status"]
            if status not in status_counts:
                status_counts[status] = 0
            status_counts[status] += 1
        
        # Ensure severity_counts has all expected keys
        if "low" not in severity_counts:
            severity_counts["low"] = 0
        if "medium" not in severity_counts:
            severity_counts["medium"] = 0
        if "high" not in severity_counts:
            severity_counts["high"] = 0
        if "critical" not in severity_counts:
            severity_counts["critical"] = 0
            
        report["summary"] = {
            "severity_counts": severity_counts,
            "category_counts": category_counts,
            "status_counts": status_counts
        }
        
        # Also update the report's direct severity_counts field
        report["severity_counts"] = severity_counts
        
        return report
    
    def register_notification_handler(self, handler_id: str, handler: Callable) -> None:
        """
        Register a handler for incident notifications.
        
        Args:
            handler_id: Unique identifier for the handler
            handler: Function to call with incident details when notification is needed
        """
        self.notification_handlers[handler_id] = handler
    
    def _notify_incident(self, incident: Dict[str, Any], action: str = "created") -> None:
        """
        Send notifications for an incident.
        
        Args:
            incident: Incident details
            action: Action that triggered the notification
        """
        if not self.notification_handlers:
            return
        
        # Call all registered notification handlers
        for handler_id, handler in self.notification_handlers.items():
            try:
                handler(incident, action)
            except Exception as e:
                self.logger.error(f"Error in notification handler {handler_id}: {e}")
    
    def _default_notification_handler(self, incident: Dict[str, Any], action: str) -> None:
        """
        Default handler for incident notifications.
        
        Args:
            incident: Incident details
            action: Action that triggered the notification
        """
        if not self.notification_service:
            return
        
        # Determine notification priority based on severity
        severity = incident["severity"]
        if severity == IncidentSeverity.CRITICAL.value:
            priority = "high"
        elif severity == IncidentSeverity.HIGH.value:
            priority = "high"
        elif severity == IncidentSeverity.MEDIUM.value:
            priority = "medium"
        else:
            priority = "low"
        
        # Create notification message
        if action == "created":
            subject = f"New {severity} incident: {incident['title']}"
            message = f"A new security incident has been detected:\n\n" \
                     f"ID: {incident['incident_id']}\n" \
                     f"Title: {incident['title']}\n" \
                     f"Category: {incident['category']}\n" \
                     f"Severity: {incident['severity']}\n" \
                     f"Description: {incident['description']}\n" \
                     f"Created: {datetime.fromtimestamp(incident['created_at']).isoformat()}"
        else:
            subject = f"Updated {severity} incident: {incident['title']}"
            message = f"A security incident has been updated:\n\n" \
                     f"ID: {incident['incident_id']}\n" \
                     f"Title: {incident['title']}\n" \
                     f"Category: {incident['category']}\n" \
                     f"Severity: {incident['severity']}\n" \
                     f"Status: {incident['status']}\n" \
                     f"Description: {incident['description']}\n" \
                     f"Updated: {datetime.fromtimestamp(incident['updated_at']).isoformat()}"
        
        # Send notification
        try:
            self.notification_service.send_notification(
                subject=subject,
                message=message,
                priority=priority,
                recipients=["security_team"],
                incident_id=incident["incident_id"]
            )
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
    
    def _escalate_incident(self, incident_id: str) -> None:
        """
        Escalate a critical incident.
        
        Args:
            incident_id: ID of the incident to escalate
        """
        # Get incident
        incident = self.incidents[incident_id]
        
        # Add timeline entry
        incident["timeline"].append({
            "timestamp": int(time.time()),
            "action": "escalated",
            "details": "Incident automatically escalated due to critical severity",
            "actor": "incident_response_manager"
        })
        
        # Update incident
        incident["updated_at"] = int(time.time())
        self.incidents[incident_id] = incident
        
        # Log escalation
        self.audit_manager.log_security_event(
            event_type=GeminiAuditCategory.INCIDENT,
            severity=AuditEventSeverity.WARNING,
            details={
                "action": "incident_escalated",
                "incident_id": incident_id,
                "reason": "critical_severity"
            },
            user_id=incident.get("user_id"),
            source="incident_response"
        )
        
        # Send high-priority notification
        if self.notification_service:
            try:
                self.notification_service.send_notification(
                    subject=f"ESCALATED: Critical incident {incident['title']}",
                    message=f"A critical security incident has been escalated:\n\n" \
                           f"ID: {incident['incident_id']}\n" \
                           f"Title: {incident['title']}\n" \
                           f"Category: {incident['category']}\n" \
                           f"Description: {incident['description']}\n" \
                           f"Created: {datetime.fromtimestamp(incident['created_at']).isoformat()}\n\n" \
                           f"IMMEDIATE ATTENTION REQUIRED",
                    priority="critical",
                    recipients=["security_team", "incident_response_team", "management"],
                    incident_id=incident["incident_id"]
                )
            except Exception as e:
                self.logger.error(f"Failed to send escalation notification: {e}")
