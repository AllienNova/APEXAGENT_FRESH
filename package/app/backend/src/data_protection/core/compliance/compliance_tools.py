"""
Compliance Tools module for the Data Protection Framework.

This module provides comprehensive compliance capabilities including regulatory
compliance management, audit logging, data retention policies, and compliance reporting
for standards such as GDPR, SOC 2, HIPAA, and PCI DSS.
"""

import os
import json
import time
import uuid
import logging
import datetime
import hashlib
import base64
import re
import csv
import io
from typing import Dict, List, Optional, Tuple, Union, Any, Set, Callable
from enum import Enum
import concurrent.futures

from ..crypto import CryptoCore, HashAlgorithm
from ..key_management import KeyManagementService
from ..storage import StorageManager, StorageType
from ..anonymization import DataAnonymizationService

# Configure logging
logger = logging.getLogger(__name__)

class ComplianceStandard(Enum):
    """Supported compliance standards."""
    GDPR = "gdpr"           # General Data Protection Regulation
    SOC2 = "soc2"           # Service Organization Control 2
    HIPAA = "hipaa"         # Health Insurance Portability and Accountability Act
    PCI_DSS = "pci_dss"     # Payment Card Industry Data Security Standard
    ISO_27001 = "iso_27001" # ISO 27001 Information Security Management
    CCPA = "ccpa"           # California Consumer Privacy Act
    NIST = "nist"           # NIST Cybersecurity Framework

class ComplianceRequirement:
    """Represents a specific compliance requirement."""
    
    def __init__(
        self,
        requirement_id: str,
        standard: ComplianceStandard,
        title: str,
        description: str,
        section: str,
        controls: List[str],
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a compliance requirement.
        
        Args:
            requirement_id: Unique identifier for the requirement
            standard: Compliance standard
            title: Short title of the requirement
            description: Detailed description
            section: Section or article in the standard
            controls: List of control identifiers
            tags: Additional metadata tags
        """
        self.requirement_id = requirement_id
        self.standard = standard
        self.title = title
        self.description = description
        self.section = section
        self.controls = controls
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'requirement_id': self.requirement_id,
            'standard': self.standard.value,
            'title': self.title,
            'description': self.description,
            'section': self.section,
            'controls': self.controls,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceRequirement':
        """Create from dictionary."""
        return cls(
            requirement_id=data['requirement_id'],
            standard=ComplianceStandard(data['standard']),
            title=data['title'],
            description=data['description'],
            section=data['section'],
            controls=data['controls'],
            tags=data.get('tags')
        )

class ComplianceControl:
    """Represents a specific control that implements compliance requirements."""
    
    def __init__(
        self,
        control_id: str,
        name: str,
        description: str,
        implementation_status: str,
        verification_method: str,
        owner: str,
        requirements: List[str],
        evidence: Optional[List[str]] = None,
        last_verified: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a compliance control.
        
        Args:
            control_id: Unique identifier for the control
            name: Name of the control
            description: Detailed description
            implementation_status: Status of implementation
            verification_method: Method used to verify the control
            owner: Owner responsible for the control
            requirements: List of requirement IDs this control addresses
            evidence: List of evidence identifiers
            last_verified: Timestamp of last verification
            tags: Additional metadata tags
        """
        self.control_id = control_id
        self.name = name
        self.description = description
        self.implementation_status = implementation_status
        self.verification_method = verification_method
        self.owner = owner
        self.requirements = requirements
        self.evidence = evidence or []
        self.last_verified = last_verified
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'control_id': self.control_id,
            'name': self.name,
            'description': self.description,
            'implementation_status': self.implementation_status,
            'verification_method': self.verification_method,
            'owner': self.owner,
            'requirements': self.requirements,
            'evidence': self.evidence,
            'last_verified': self.last_verified,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceControl':
        """Create from dictionary."""
        return cls(
            control_id=data['control_id'],
            name=data['name'],
            description=data['description'],
            implementation_status=data['implementation_status'],
            verification_method=data['verification_method'],
            owner=data['owner'],
            requirements=data['requirements'],
            evidence=data.get('evidence'),
            last_verified=data.get('last_verified'),
            tags=data.get('tags')
        )

class AuditEventType(Enum):
    """Types of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    SYSTEM = "system"
    USER_MANAGEMENT = "user_management"
    PLUGIN = "plugin"

class AuditEventSeverity(Enum):
    """Severity levels for audit events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditEvent:
    """Represents an audit event for compliance and security monitoring."""
    
    def __init__(
        self,
        event_id: str,
        timestamp: int,
        event_type: AuditEventType,
        severity: AuditEventSeverity,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        details: Optional[Dict[str, Any]] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize an audit event.
        
        Args:
            event_id: Unique identifier for the event
            timestamp: Event timestamp (Unix time)
            event_type: Type of event
            severity: Severity level
            actor: Actor who performed the action
            action: Action performed
            resource: Resource affected
            outcome: Outcome of the action
            details: Additional details
            source_ip: Source IP address
            user_agent: User agent string
            session_id: Session identifier
            tags: Additional metadata tags
        """
        self.event_id = event_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.severity = severity
        self.actor = actor
        self.action = action
        self.resource = resource
        self.outcome = outcome
        self.details = details or {}
        self.source_ip = source_ip
        self.user_agent = user_agent
        self.session_id = session_id
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'actor': self.actor,
            'action': self.action,
            'resource': self.resource,
            'outcome': self.outcome,
            'details': self.details,
            'source_ip': self.source_ip,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create from dictionary."""
        return cls(
            event_id=data['event_id'],
            timestamp=data['timestamp'],
            event_type=AuditEventType(data['event_type']),
            severity=AuditEventSeverity(data['severity']),
            actor=data['actor'],
            action=data['action'],
            resource=data['resource'],
            outcome=data['outcome'],
            details=data.get('details'),
            source_ip=data.get('source_ip'),
            user_agent=data.get('user_agent'),
            session_id=data.get('session_id'),
            tags=data.get('tags')
        )

class RetentionPolicy:
    """Represents a data retention policy."""
    
    def __init__(
        self,
        policy_id: str,
        name: str,
        description: str,
        data_category: str,
        retention_period: int,
        legal_basis: str,
        action_after_retention: str,
        owner: str,
        applies_to: List[str],
        exceptions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a retention policy.
        
        Args:
            policy_id: Unique identifier for the policy
            name: Name of the policy
            description: Detailed description
            data_category: Category of data this policy applies to
            retention_period: Retention period in seconds
            legal_basis: Legal basis for the retention period
            action_after_retention: Action to take after retention period
            owner: Owner responsible for the policy
            applies_to: List of resource patterns this policy applies to
            exceptions: List of exception patterns
            tags: Additional metadata tags
        """
        self.policy_id = policy_id
        self.name = name
        self.description = description
        self.data_category = data_category
        self.retention_period = retention_period
        self.legal_basis = legal_basis
        self.action_after_retention = action_after_retention
        self.owner = owner
        self.applies_to = applies_to
        self.exceptions = exceptions or []
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'data_category': self.data_category,
            'retention_period': self.retention_period,
            'legal_basis': self.legal_basis,
            'action_after_retention': self.action_after_retention,
            'owner': self.owner,
            'applies_to': self.applies_to,
            'exceptions': self.exceptions,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetentionPolicy':
        """Create from dictionary."""
        return cls(
            policy_id=data['policy_id'],
            name=data['name'],
            description=data['description'],
            data_category=data['data_category'],
            retention_period=data['retention_period'],
            legal_basis=data['legal_basis'],
            action_after_retention=data['action_after_retention'],
            owner=data['owner'],
            applies_to=data['applies_to'],
            exceptions=data.get('exceptions'),
            tags=data.get('tags')
        )

class DataSubjectRequest:
    """Represents a data subject request (e.g., GDPR right to access, erasure)."""
    
    class RequestType(Enum):
        """Types of data subject requests."""
        ACCESS = "access"
        ERASURE = "erasure"
        RECTIFICATION = "rectification"
        RESTRICTION = "restriction"
        PORTABILITY = "portability"
        OBJECTION = "objection"
        AUTOMATED_DECISION = "automated_decision"
    
    class RequestStatus(Enum):
        """Status of data subject requests."""
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        DENIED = "denied"
        CANCELLED = "cancelled"
    
    def __init__(
        self,
        request_id: str,
        request_type: RequestType,
        subject_id: str,
        created_at: int,
        status: RequestStatus,
        details: str,
        assigned_to: Optional[str] = None,
        completed_at: Optional[int] = None,
        response_details: Optional[str] = None,
        verification_method: Optional[str] = None,
        verification_status: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a data subject request.
        
        Args:
            request_id: Unique identifier for the request
            request_type: Type of request
            subject_id: Identifier for the data subject
            created_at: Creation timestamp (Unix time)
            status: Status of the request
            details: Request details
            assigned_to: Person assigned to handle the request
            completed_at: Completion timestamp (Unix time)
            response_details: Details of the response
            verification_method: Method used to verify the subject's identity
            verification_status: Status of identity verification
            tags: Additional metadata tags
        """
        self.request_id = request_id
        self.request_type = request_type
        self.subject_id = subject_id
        self.created_at = created_at
        self.status = status
        self.details = details
        self.assigned_to = assigned_to
        self.completed_at = completed_at
        self.response_details = response_details
        self.verification_method = verification_method
        self.verification_status = verification_status
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'request_id': self.request_id,
            'request_type': self.request_type.value,
            'subject_id': self.subject_id,
            'created_at': self.created_at,
            'status': self.status.value,
            'details': self.details,
            'assigned_to': self.assigned_to,
            'completed_at': self.completed_at,
            'response_details': self.response_details,
            'verification_method': self.verification_method,
            'verification_status': self.verification_status,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataSubjectRequest':
        """Create from dictionary."""
        return cls(
            request_id=data['request_id'],
            request_type=cls.RequestType(data['request_type']),
            subject_id=data['subject_id'],
            created_at=data['created_at'],
            status=cls.RequestStatus(data['status']),
            details=data['details'],
            assigned_to=data.get('assigned_to'),
            completed_at=data.get('completed_at'),
            response_details=data.get('response_details'),
            verification_method=data.get('verification_method'),
            verification_status=data.get('verification_status'),
            tags=data.get('tags')
        )

class ComplianceError(Exception):
    """Base exception for compliance operations."""
    pass

class AuditError(Exception):
    """Base exception for audit operations."""
    pass

class RetentionError(Exception):
    """Base exception for retention operations."""
    pass

class DataSubjectRequestError(Exception):
    """Base exception for data subject request operations."""
    pass

class AuditLogger:
    """
    Service for logging and querying audit events.
    
    This class provides methods for recording audit events and querying
    the audit log for compliance and security monitoring.
    """
    
    def __init__(
        self,
        storage_manager: StorageManager,
        audit_storage_path: str,
        crypto_core: Optional[CryptoCore] = None,
        max_concurrent_operations: int = 5
    ):
        """
        Initialize the audit logger.
        
        Args:
            storage_manager: Storage manager
            audit_storage_path: Path for storing audit logs
            crypto_core: Cryptographic core
            max_concurrent_operations: Maximum number of concurrent operations
        """
        self._storage_manager = storage_manager
        self._audit_storage_path = os.path.abspath(audit_storage_path)
        self._crypto = crypto_core or CryptoCore()
        self._max_concurrent_operations = max_concurrent_operations
        
        # Create audit storage directory
        os.makedirs(self._audit_storage_path, exist_ok=True)
        
        # Thread pool for concurrent operations
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_operations)
        
        # Current log file
        self._current_log_file = None
        self._current_log_date = None
        
        logger.info(f"Audit Logger initialized with storage path {self._audit_storage_path}")
    
    def _get_log_file_path(self, date_str: str) -> str:
        """Get the path for a log file by date."""
        return os.path.join(self._audit_storage_path, f"audit_{date_str}.jsonl")
    
    def _get_current_log_file(self) -> str:
        """Get the current log file path."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if self._current_log_date != today:
            self._current_log_date = today
            self._current_log_file = self._get_log_file_path(today)
        
        return self._current_log_file
    
    def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditEventSeverity,
        actor: str,
        action: str,
        resource: str,
        outcome: str,
        details: Optional[Dict[str, Any]] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        async_operation: bool = True
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            severity: Severity level
            actor: Actor who performed the action
            action: Action performed
            resource: Resource affected
            outcome: Outcome of the action
            details: Additional details
            source_ip: Source IP address
            user_agent: User agent string
            session_id: Session identifier
            tags: Additional metadata tags
            async_operation: Whether to perform logging asynchronously
        
        Returns:
            AuditEvent: The logged event
        
        Raises:
            AuditError: If logging fails
        """
        try:
            # Generate event ID
            event_id = str(uuid.uuid4())
            
            # Create event
            now = int(time.time())
            event = AuditEvent(
                event_id=event_id,
                timestamp=now,
                event_type=event_type,
                severity=severity,
                actor=actor,
                action=action,
                resource=resource,
                outcome=outcome,
                details=details,
                source_ip=source_ip,
                user_agent=user_agent,
                session_id=session_id,
                tags=tags
            )
            
            # Log event
            if async_operation:
                self._executor.submit(self._write_event, event)
            else:
                self._write_event(event)
            
            return event
        
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
            raise AuditError(f"Failed to log audit event: {str(e)}")
    
    def _write_event(self, event: AuditEvent) -> None:
        """
        Write an event to the audit log.
        
        Args:
            event: Audit event
        """
        try:
            # Get current log file
            log_file = self._get_current_log_file()
            
            # Convert event to JSON
            event_json = json.dumps(event.to_dict())
            
            # Append to log file
            with open(log_file, 'a') as f:
                f.write(event_json + '\n')
            
            logger.debug(f"Audit event {event.event_id} logged successfully")
        
        except Exception as e:
            logger.error(f"Failed to write audit event: {str(e)}")
    
    def query_events(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        event_types: Optional[List[AuditEventType]] = None,
        severities: Optional[List[AuditEventSeverity]] = None,
        actors: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
        resources: Optional[List[str]] = None,
        outcomes: Optional[List[str]] = None,
        source_ips: Optional[List[str]] = None,
        session_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> Tuple[List[AuditEvent], int]:
        """
        Query audit events with filtering.
        
        Args:
            start_time: Filter by start time (Unix time)
            end_time: Filter by end time (Unix time)
            event_types: Filter by event types
            severities: Filter by severities
            actors: Filter by actors
            actions: Filter by actions
            resources: Filter by resources
            outcomes: Filter by outcomes
            source_ips: Filter by source IPs
            session_ids: Filter by session IDs
            tags: Filter by tags
            limit: Maximum number of events to return
            offset: Offset for pagination
        
        Returns:
            Tuple[List[AuditEvent], int]: List of events and total count
        
        Raises:
            AuditError: If query fails
        """
        try:
            results = []
            total_count = 0
            
            # Determine date range
            if start_time is None:
                # Default to last 30 days
                start_time = int(time.time()) - (30 * 24 * 60 * 60)
            
            if end_time is None:
                end_time = int(time.time())
            
            # Convert to datetime for file filtering
            start_date = datetime.datetime.fromtimestamp(start_time)
            end_date = datetime.datetime.fromtimestamp(end_time)
            
            # Generate list of dates in range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date.strftime("%Y-%m-%d"))
                current_date += datetime.timedelta(days=1)
            
            # Process each log file
            for date_str in date_range:
                log_file = self._get_log_file_path(date_str)
                
                if not os.path.exists(log_file):
                    continue
                
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            # Parse event
                            event_dict = json.loads(line.strip())
                            event = AuditEvent.from_dict(event_dict)
                            
                            # Apply filters
                            if start_time and event.timestamp < start_time:
                                continue
                            
                            if end_time and event.timestamp > end_time:
                                continue
                            
                            if event_types and event.event_type not in event_types:
                                continue
                            
                            if severities and event.severity not in severities:
                                continue
                            
                            if actors and event.actor not in actors:
                                continue
                            
                            if actions and event.action not in actions:
                                continue
                            
                            if resources and not any(re.search(r, event.resource) for r in resources):
                                continue
                            
                            if outcomes and event.outcome not in outcomes:
                                continue
                            
                            if source_ips and event.source_ip not in source_ips:
                                continue
                            
                            if session_ids and event.session_id not in session_ids:
                                continue
                            
                            if tags:
                                match = True
                                for key, value in tags.items():
                                    if key not in event.tags or event.tags[key] != value:
                                        match = False
                                        break
                                
                                if not match:
                                    continue
                            
                            # Increment count
                            total_count += 1
                            
                            # Add to results if within pagination range
                            if total_count > offset and len(results) < limit:
                                results.append(event)
                        
                        except Exception as e:
                            logger.error(f"Error processing audit event: {str(e)}")
                            # Continue with next event
            
            # Sort by timestamp (newest first)
            results.sort(key=lambda x: x.timestamp, reverse=True)
            
            return results, total_count
        
        except Exception as e:
            logger.error(f"Failed to query audit events: {str(e)}")
            raise AuditError(f"Failed to query audit events: {str(e)}")
    
    def export_events(
        self,
        format: str,
        query_params: Dict[str, Any]
    ) -> Tuple[bytes, str]:
        """
        Export audit events in various formats.
        
        Args:
            format: Export format (json, csv)
            query_params: Query parameters for filtering events
        
        Returns:
            Tuple[bytes, str]: Exported data and content type
        
        Raises:
            AuditError: If export fails
        """
        try:
            # Query events
            events, _ = self.query_events(**query_params)
            
            if format.lower() == 'json':
                # Export as JSON
                data = json.dumps([e.to_dict() for e in events], indent=2)
                content_type = 'application/json'
                return data.encode('utf-8'), content_type
            
            elif format.lower() == 'csv':
                # Export as CSV
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'Event ID', 'Timestamp', 'Event Type', 'Severity',
                    'Actor', 'Action', 'Resource', 'Outcome',
                    'Source IP', 'User Agent', 'Session ID'
                ])
                
                # Write events
                for event in events:
                    timestamp_str = datetime.datetime.fromtimestamp(event.timestamp).isoformat()
                    writer.writerow([
                        event.event_id,
                        timestamp_str,
                        event.event_type.value,
                        event.severity.value,
                        event.actor,
                        event.action,
                        event.resource,
                        event.outcome,
                        event.source_ip or '',
                        event.user_agent or '',
                        event.session_id or ''
                    ])
                
                content_type = 'text/csv'
                return output.getvalue().encode('utf-8'), content_type
            
            else:
                raise AuditError(f"Unsupported export format: {format}")
        
        except Exception as e:
            logger.error(f"Failed to export audit events: {str(e)}")
            raise AuditError(f"Failed to export audit events: {str(e)}")

class RetentionManager:
    """
    Service for managing data retention policies.
    
    This class provides methods for creating, managing, and enforcing
    data retention policies for compliance with regulations.
    """
    
    def __init__(
        self,
        storage_manager: StorageManager,
        policy_storage_path: str,
        max_concurrent_operations: int = 5
    ):
        """
        Initialize the retention manager.
        
        Args:
            storage_manager: Storage manager
            policy_storage_path: Path for storing retention policies
            max_concurrent_operations: Maximum number of concurrent operations
        """
        self._storage_manager = storage_manager
        self._policy_storage_path = os.path.abspath(policy_storage_path)
        self._max_concurrent_operations = max_concurrent_operations
        
        # Create policy storage directory
        os.makedirs(self._policy_storage_path, exist_ok=True)
        
        # Thread pool for concurrent operations
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_operations)
        
        logger.info(f"Retention Manager initialized with policy path {self._policy_storage_path}")
    
    def _get_policy_path(self, policy_id: str) -> str:
        """Get the path for a policy file."""
        return os.path.join(self._policy_storage_path, f"{policy_id}.json")
    
    def create_policy(
        self,
        name: str,
        description: str,
        data_category: str,
        retention_period: int,
        legal_basis: str,
        action_after_retention: str,
        owner: str,
        applies_to: List[str],
        exceptions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RetentionPolicy:
        """
        Create a retention policy.
        
        Args:
            name: Name of the policy
            description: Detailed description
            data_category: Category of data this policy applies to
            retention_period: Retention period in seconds
            legal_basis: Legal basis for the retention period
            action_after_retention: Action to take after retention period
            owner: Owner responsible for the policy
            applies_to: List of resource patterns this policy applies to
            exceptions: List of exception patterns
            tags: Additional metadata tags
        
        Returns:
            RetentionPolicy: The created policy
        
        Raises:
            RetentionError: If policy creation fails
        """
        try:
            # Generate policy ID
            policy_id = str(uuid.uuid4())
            
            # Create policy
            policy = RetentionPolicy(
                policy_id=policy_id,
                name=name,
                description=description,
                data_category=data_category,
                retention_period=retention_period,
                legal_basis=legal_basis,
                action_after_retention=action_after_retention,
                owner=owner,
                applies_to=applies_to,
                exceptions=exceptions,
                tags=tags
            )
            
            # Save policy
            self._save_policy(policy)
            
            logger.info(f"Retention policy {policy_id} created successfully")
            return policy
        
        except Exception as e:
            logger.error(f"Failed to create retention policy: {str(e)}")
            raise RetentionError(f"Failed to create retention policy: {str(e)}")
    
    def _save_policy(self, policy: RetentionPolicy) -> None:
        """
        Save a retention policy to disk.
        
        Args:
            policy: Retention policy
        """
        policy_path = self._get_policy_path(policy.policy_id)
        with open(policy_path, 'w') as f:
            json.dump(policy.to_dict(), f)
    
    def get_policy(self, policy_id: str) -> RetentionPolicy:
        """
        Get a retention policy.
        
        Args:
            policy_id: Policy ID
        
        Returns:
            RetentionPolicy: The policy
        
        Raises:
            RetentionError: If policy retrieval fails
        """
        try:
            policy_path = self._get_policy_path(policy_id)
            
            if not os.path.exists(policy_path):
                raise RetentionError(f"Retention policy {policy_id} not found")
            
            with open(policy_path, 'r') as f:
                policy_dict = json.load(f)
            
            return RetentionPolicy.from_dict(policy_dict)
        
        except Exception as e:
            logger.error(f"Failed to get retention policy: {str(e)}")
            raise RetentionError(f"Failed to get retention policy: {str(e)}")
    
    def list_policies(
        self,
        owner: Optional[str] = None,
        data_category: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[RetentionPolicy]:
        """
        List retention policies with optional filtering.
        
        Args:
            owner: Filter by owner
            data_category: Filter by data category
            tags: Filter by tags
        
        Returns:
            List[RetentionPolicy]: List of policies
        
        Raises:
            RetentionError: If listing fails
        """
        try:
            results = []
            
            # List all policy files
            for filename in os.listdir(self._policy_storage_path):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    # Read policy
                    with open(os.path.join(self._policy_storage_path, filename), 'r') as f:
                        policy_dict = json.load(f)
                    
                    policy = RetentionPolicy.from_dict(policy_dict)
                    
                    # Apply filters
                    if owner and policy.owner != owner:
                        continue
                    
                    if data_category and policy.data_category != data_category:
                        continue
                    
                    if tags:
                        match = True
                        for key, value in tags.items():
                            if key not in policy.tags or policy.tags[key] != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    results.append(policy)
                
                except Exception as e:
                    logger.error(f"Error processing policy file {filename}: {str(e)}")
                    # Continue with next file
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to list retention policies: {str(e)}")
            raise RetentionError(f"Failed to list retention policies: {str(e)}")
    
    def update_policy(
        self,
        policy_id: str,
        owner: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        retention_period: Optional[int] = None,
        legal_basis: Optional[str] = None,
        action_after_retention: Optional[str] = None,
        applies_to: Optional[List[str]] = None,
        exceptions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RetentionPolicy:
        """
        Update a retention policy.
        
        Args:
            policy_id: Policy ID
            owner: Owner requesting update
            name: Name of the policy
            description: Detailed description
            retention_period: Retention period in seconds
            legal_basis: Legal basis for the retention period
            action_after_retention: Action to take after retention period
            applies_to: List of resource patterns this policy applies to
            exceptions: List of exception patterns
            tags: Additional metadata tags
        
        Returns:
            RetentionPolicy: The updated policy
        
        Raises:
            RetentionError: If update fails
        """
        try:
            # Get policy
            policy = self.get_policy(policy_id)
            
            # Check ownership
            if policy.owner != owner and owner != "system":
                raise RetentionError(f"Access denied: {owner} is not the owner of policy {policy_id}")
            
            # Update fields
            if name is not None:
                policy.name = name
            
            if description is not None:
                policy.description = description
            
            if retention_period is not None:
                policy.retention_period = retention_period
            
            if legal_basis is not None:
                policy.legal_basis = legal_basis
            
            if action_after_retention is not None:
                policy.action_after_retention = action_after_retention
            
            if applies_to is not None:
                policy.applies_to = applies_to
            
            if exceptions is not None:
                policy.exceptions = exceptions
            
            if tags is not None:
                policy.tags = tags
            
            # Save updated policy
            self._save_policy(policy)
            
            logger.info(f"Retention policy {policy_id} updated successfully")
            return policy
        
        except Exception as e:
            logger.error(f"Failed to update retention policy: {str(e)}")
            raise RetentionError(f"Failed to update retention policy: {str(e)}")
    
    def delete_policy(self, policy_id: str, owner: str) -> None:
        """
        Delete a retention policy.
        
        Args:
            policy_id: Policy ID
            owner: Owner requesting deletion
        
        Raises:
            RetentionError: If deletion fails
        """
        try:
            # Get policy
            policy = self.get_policy(policy_id)
            
            # Check ownership
            if policy.owner != owner and owner != "system":
                raise RetentionError(f"Access denied: {owner} is not the owner of policy {policy_id}")
            
            # Delete policy
            policy_path = self._get_policy_path(policy_id)
            if os.path.exists(policy_path):
                os.remove(policy_path)
            
            logger.info(f"Retention policy {policy_id} deleted successfully")
        
        except Exception as e:
            logger.error(f"Failed to delete retention policy: {str(e)}")
            raise RetentionError(f"Failed to delete retention policy: {str(e)}")
    
    def enforce_policies(
        self,
        storage_type: Optional[StorageType] = None,
        async_operation: bool = True
    ) -> Dict[str, Any]:
        """
        Enforce all retention policies.
        
        Args:
            storage_type: Limit enforcement to specific storage type
            async_operation: Whether to perform enforcement asynchronously
        
        Returns:
            Dict[str, Any]: Enforcement results
        
        Raises:
            RetentionError: If enforcement fails
        """
        try:
            # Get all policies
            policies = self.list_policies()
            
            if async_operation:
                future = self._executor.submit(
                    self._enforce_policies_internal, policies, storage_type
                )
                return {'status': 'started', 'message': 'Retention policy enforcement started'}
            else:
                results = self._enforce_policies_internal(policies, storage_type)
                return results
        
        except Exception as e:
            logger.error(f"Failed to enforce retention policies: {str(e)}")
            raise RetentionError(f"Failed to enforce retention policies: {str(e)}")
    
    def _enforce_policies_internal(
        self,
        policies: List[RetentionPolicy],
        storage_type: Optional[StorageType] = None
    ) -> Dict[str, Any]:
        """
        Internal method to enforce retention policies.
        
        Args:
            policies: List of policies to enforce
            storage_type: Limit enforcement to specific storage type
        
        Returns:
            Dict[str, Any]: Enforcement results
        """
        try:
            now = int(time.time())
            results = {
                'total_objects': 0,
                'expired_objects': 0,
                'deleted_objects': 0,
                'anonymized_objects': 0,
                'archived_objects': 0,
                'errors': 0,
                'policy_results': {}
            }
            
            # Get storage types to process
            storage_types = [storage_type] if storage_type else [
                StorageType.OBJECT,
                StorageType.FILE,
                StorageType.DATABASE,
                StorageType.CACHE
            ]
            
            # Process each storage type
            for st in storage_types:
                try:
                    storage = self._storage_manager.get_storage(st)
                    
                    # List all objects
                    objects, _ = storage.list_objects(requester="system")
                    results['total_objects'] += len(objects)
                    
                    # Process each object
                    for obj_metadata in objects:
                        try:
                            # Find applicable policies
                            applicable_policies = self._find_applicable_policies(
                                obj_metadata, policies
                            )
                            
                            if not applicable_policies:
                                continue
                            
                            # Get most restrictive policy
                            policy = min(
                                applicable_policies,
                                key=lambda p: p.retention_period
                            )
                            
                            # Check if object has expired
                            if obj_metadata.created_at + policy.retention_period <= now:
                                # Object has expired
                                results['expired_objects'] += 1
                                
                                # Perform action based on policy
                                if policy.action_after_retention == 'delete':
                                    # Delete object
                                    storage.delete_object(
                                        obj_metadata.object_id,
                                        requester="system"
                                    )
                                    results['deleted_objects'] += 1
                                
                                elif policy.action_after_retention == 'anonymize':
                                    # Anonymize object
                                    self._anonymize_object(obj_metadata, storage)
                                    results['anonymized_objects'] += 1
                                
                                elif policy.action_after_retention == 'archive':
                                    # Archive object
                                    self._archive_object(obj_metadata, storage)
                                    results['archived_objects'] += 1
                                
                                # Update policy results
                                if policy.policy_id not in results['policy_results']:
                                    results['policy_results'][policy.policy_id] = {
                                        'name': policy.name,
                                        'expired_objects': 0,
                                        'actions': {}
                                    }
                                
                                results['policy_results'][policy.policy_id]['expired_objects'] += 1
                                
                                action = policy.action_after_retention
                                if action not in results['policy_results'][policy.policy_id]['actions']:
                                    results['policy_results'][policy.policy_id]['actions'][action] = 0
                                
                                results['policy_results'][policy.policy_id]['actions'][action] += 1
                        
                        except Exception as e:
                            logger.error(f"Error processing object {obj_metadata.object_id}: {str(e)}")
                            results['errors'] += 1
                
                except Exception as e:
                    logger.error(f"Error processing storage type {st.value}: {str(e)}")
                    results['errors'] += 1
            
            logger.info(f"Retention policy enforcement completed: {results['expired_objects']} expired objects processed")
            return results
        
        except Exception as e:
            logger.error(f"Failed to enforce retention policies: {str(e)}")
            return {
                'status': 'error',
                'message': f"Failed to enforce retention policies: {str(e)}"
            }
    
    def _find_applicable_policies(
        self,
        obj_metadata: Any,
        policies: List[RetentionPolicy]
    ) -> List[RetentionPolicy]:
        """
        Find policies that apply to an object.
        
        Args:
            obj_metadata: Object metadata
            policies: List of policies
        
        Returns:
            List[RetentionPolicy]: List of applicable policies
        """
        applicable = []
        
        for policy in policies:
            # Check if policy applies to this object
            for pattern in policy.applies_to:
                if re.search(pattern, obj_metadata.object_id):
                    # Check exceptions
                    excepted = False
                    for exception in policy.exceptions:
                        if re.search(exception, obj_metadata.object_id):
                            excepted = True
                            break
                    
                    if not excepted:
                        applicable.append(policy)
                        break
        
        return applicable
    
    def _anonymize_object(self, obj_metadata: Any, storage: Any) -> None:
        """
        Anonymize an object.
        
        Args:
            obj_metadata: Object metadata
            storage: Storage service
        """
        try:
            # Retrieve object
            data_stream, _ = storage.retrieve_object(
                obj_metadata.object_id,
                requester="system"
            )
            
            # Read data
            data = data_stream.read()
            data_stream.close()
            
            # Create anonymization service
            anonymization = DataAnonymizationService()
            
            # Anonymize data
            anonymized_data = anonymization.anonymize_data(
                data=data,
                content_type=obj_metadata.content_type
            )
            
            # Store anonymized data
            storage.store_object(
                data=anonymized_data,
                content_type=obj_metadata.content_type,
                owner=obj_metadata.owner,
                object_id=obj_metadata.object_id,
                encrypt=True,
                verify_integrity=True
            )
            
            logger.info(f"Object {obj_metadata.object_id} anonymized successfully")
        
        except Exception as e:
            logger.error(f"Failed to anonymize object {obj_metadata.object_id}: {str(e)}")
            raise RetentionError(f"Failed to anonymize object: {str(e)}")
    
    def _archive_object(self, obj_metadata: Any, storage: Any) -> None:
        """
        Archive an object.
        
        Args:
            obj_metadata: Object metadata
            storage: Storage service
        """
        try:
            # Retrieve object
            data_stream, _ = storage.retrieve_object(
                obj_metadata.object_id,
                requester="system"
            )
            
            # Read data
            data = data_stream.read()
            data_stream.close()
            
            # Create archive storage
            archive_storage = self._storage_manager.get_storage(StorageType.ARCHIVE)
            
            # Store in archive
            archive_storage.store_object(
                data=data,
                content_type=obj_metadata.content_type,
                owner=obj_metadata.owner,
                object_id=f"archive/{obj_metadata.object_id}",
                encrypt=True,
                verify_integrity=True
            )
            
            # Delete original
            storage.delete_object(
                obj_metadata.object_id,
                requester="system"
            )
            
            logger.info(f"Object {obj_metadata.object_id} archived successfully")
        
        except Exception as e:
            logger.error(f"Failed to archive object {obj_metadata.object_id}: {str(e)}")
            raise RetentionError(f"Failed to archive object: {str(e)}")

class DataSubjectRequestManager:
    """
    Service for managing data subject requests.
    
    This class provides methods for creating, managing, and processing
    data subject requests for compliance with regulations like GDPR.
    """
    
    def __init__(
        self,
        storage_manager: StorageManager,
        request_storage_path: str,
        anonymization_service: Optional[Any] = None,
        max_concurrent_operations: int = 5
    ):
        """
        Initialize the data subject request manager.
        
        Args:
            storage_manager: Storage manager
            request_storage_path: Path for storing requests
            anonymization_service: Data anonymization service
            max_concurrent_operations: Maximum number of concurrent operations
        """
        self._storage_manager = storage_manager
        self._request_storage_path = os.path.abspath(request_storage_path)
        self._anonymization = anonymization_service or DataAnonymizationService()
        self._max_concurrent_operations = max_concurrent_operations
        
        # Create request storage directory
        os.makedirs(self._request_storage_path, exist_ok=True)
        
        # Thread pool for concurrent operations
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_operations)
        
        # Active operations
        self._active_requests = {}
        
        logger.info(f"Data Subject Request Manager initialized with storage path {self._request_storage_path}")
    
    def _get_request_path(self, request_id: str) -> str:
        """Get the path for a request file."""
        return os.path.join(self._request_storage_path, f"{request_id}.json")
    
    def create_request(
        self,
        request_type: DataSubjectRequest.RequestType,
        subject_id: str,
        details: str,
        verification_method: Optional[str] = None,
        verification_status: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> DataSubjectRequest:
        """
        Create a data subject request.
        
        Args:
            request_type: Type of request
            subject_id: Identifier for the data subject
            details: Request details
            verification_method: Method used to verify the subject's identity
            verification_status: Status of identity verification
            tags: Additional metadata tags
        
        Returns:
            DataSubjectRequest: The created request
        
        Raises:
            DataSubjectRequestError: If request creation fails
        """
        try:
            # Generate request ID
            request_id = str(uuid.uuid4())
            
            # Create request
            now = int(time.time())
            request = DataSubjectRequest(
                request_id=request_id,
                request_type=request_type,
                subject_id=subject_id,
                created_at=now,
                status=DataSubjectRequest.RequestStatus.PENDING,
                details=details,
                verification_method=verification_method,
                verification_status=verification_status,
                tags=tags
            )
            
            # Save request
            self._save_request(request)
            
            logger.info(f"Data subject request {request_id} created successfully")
            return request
        
        except Exception as e:
            logger.error(f"Failed to create data subject request: {str(e)}")
            raise DataSubjectRequestError(f"Failed to create data subject request: {str(e)}")
    
    def _save_request(self, request: DataSubjectRequest) -> None:
        """
        Save a data subject request to disk.
        
        Args:
            request: Data subject request
        """
        request_path = self._get_request_path(request.request_id)
        with open(request_path, 'w') as f:
            json.dump(request.to_dict(), f)
    
    def get_request(self, request_id: str) -> DataSubjectRequest:
        """
        Get a data subject request.
        
        Args:
            request_id: Request ID
        
        Returns:
            DataSubjectRequest: The request
        
        Raises:
            DataSubjectRequestError: If request retrieval fails
        """
        try:
            request_path = self._get_request_path(request_id)
            
            if not os.path.exists(request_path):
                raise DataSubjectRequestError(f"Data subject request {request_id} not found")
            
            with open(request_path, 'r') as f:
                request_dict = json.load(f)
            
            return DataSubjectRequest.from_dict(request_dict)
        
        except Exception as e:
            logger.error(f"Failed to get data subject request: {str(e)}")
            raise DataSubjectRequestError(f"Failed to get data subject request: {str(e)}")
    
    def list_requests(
        self,
        subject_id: Optional[str] = None,
        request_type: Optional[DataSubjectRequest.RequestType] = None,
        status: Optional[DataSubjectRequest.RequestStatus] = None,
        assigned_to: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[DataSubjectRequest]:
        """
        List data subject requests with optional filtering.
        
        Args:
            subject_id: Filter by subject ID
            request_type: Filter by request type
            status: Filter by status
            assigned_to: Filter by assignee
            start_time: Filter by start time (Unix time)
            end_time: Filter by end time (Unix time)
            tags: Filter by tags
        
        Returns:
            List[DataSubjectRequest]: List of requests
        
        Raises:
            DataSubjectRequestError: If listing fails
        """
        try:
            results = []
            
            # List all request files
            for filename in os.listdir(self._request_storage_path):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    # Read request
                    with open(os.path.join(self._request_storage_path, filename), 'r') as f:
                        request_dict = json.load(f)
                    
                    request = DataSubjectRequest.from_dict(request_dict)
                    
                    # Apply filters
                    if subject_id and request.subject_id != subject_id:
                        continue
                    
                    if request_type and request.request_type != request_type:
                        continue
                    
                    if status and request.status != status:
                        continue
                    
                    if assigned_to and request.assigned_to != assigned_to:
                        continue
                    
                    if start_time and request.created_at < start_time:
                        continue
                    
                    if end_time and request.created_at > end_time:
                        continue
                    
                    if tags:
                        match = True
                        for key, value in tags.items():
                            if key not in request.tags or request.tags[key] != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    results.append(request)
                
                except Exception as e:
                    logger.error(f"Error processing request file {filename}: {str(e)}")
                    # Continue with next file
            
            # Sort by creation time (newest first)
            results.sort(key=lambda x: x.created_at, reverse=True)
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to list data subject requests: {str(e)}")
            raise DataSubjectRequestError(f"Failed to list data subject requests: {str(e)}")
    
    def update_request(
        self,
        request_id: str,
        status: Optional[DataSubjectRequest.RequestStatus] = None,
        assigned_to: Optional[str] = None,
        response_details: Optional[str] = None,
        verification_status: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> DataSubjectRequest:
        """
        Update a data subject request.
        
        Args:
            request_id: Request ID
            status: Status of the request
            assigned_to: Person assigned to handle the request
            response_details: Details of the response
            verification_status: Status of identity verification
            tags: Additional metadata tags
        
        Returns:
            DataSubjectRequest: The updated request
        
        Raises:
            DataSubjectRequestError: If update fails
        """
        try:
            # Get request
            request = self.get_request(request_id)
            
            # Update fields
            if status is not None:
                request.status = status
                
                if status == DataSubjectRequest.RequestStatus.COMPLETED:
                    request.completed_at = int(time.time())
            
            if assigned_to is not None:
                request.assigned_to = assigned_to
            
            if response_details is not None:
                request.response_details = response_details
            
            if verification_status is not None:
                request.verification_status = verification_status
            
            if tags is not None:
                request.tags = tags
            
            # Save updated request
            self._save_request(request)
            
            logger.info(f"Data subject request {request_id} updated successfully")
            return request
        
        except Exception as e:
            logger.error(f"Failed to update data subject request: {str(e)}")
            raise DataSubjectRequestError(f"Failed to update data subject request: {str(e)}")
    
    def process_request(
        self,
        request_id: str,
        assigned_to: str,
        async_operation: bool = True
    ) -> DataSubjectRequest:
        """
        Process a data subject request.
        
        Args:
            request_id: Request ID
            assigned_to: Person processing the request
            async_operation: Whether to process asynchronously
        
        Returns:
            DataSubjectRequest: The updated request
        
        Raises:
            DataSubjectRequestError: If processing fails
        """
        try:
            # Get request
            request = self.get_request(request_id)
            
            # Check if request can be processed
            if request.status != DataSubjectRequest.RequestStatus.PENDING:
                raise DataSubjectRequestError(f"Request {request_id} cannot be processed because it is not pending")
            
            # Update request
            request.status = DataSubjectRequest.RequestStatus.IN_PROGRESS
            request.assigned_to = assigned_to
            self._save_request(request)
            
            # Process request
            if async_operation:
                self._active_requests[request_id] = self._executor.submit(
                    self._process_request_internal, request
                )
            else:
                request = self._process_request_internal(request)
            
            return request
        
        except Exception as e:
            logger.error(f"Failed to process data subject request: {str(e)}")
            raise DataSubjectRequestError(f"Failed to process data subject request: {str(e)}")
    
    def _process_request_internal(self, request: DataSubjectRequest) -> DataSubjectRequest:
        """
        Internal method to process a data subject request.
        
        Args:
            request: Data subject request
        
        Returns:
            DataSubjectRequest: The updated request
        """
        try:
            # Process based on request type
            if request.request_type == DataSubjectRequest.RequestType.ACCESS:
                result = self._process_access_request(request)
            
            elif request.request_type == DataSubjectRequest.RequestType.ERASURE:
                result = self._process_erasure_request(request)
            
            elif request.request_type == DataSubjectRequest.RequestType.RECTIFICATION:
                result = self._process_rectification_request(request)
            
            elif request.request_type == DataSubjectRequest.RequestType.RESTRICTION:
                result = self._process_restriction_request(request)
            
            elif request.request_type == DataSubjectRequest.RequestType.PORTABILITY:
                result = self._process_portability_request(request)
            
            elif request.request_type == DataSubjectRequest.RequestType.OBJECTION:
                result = self._process_objection_request(request)
            
            elif request.request_type == DataSubjectRequest.RequestType.AUTOMATED_DECISION:
                result = self._process_automated_decision_request(request)
            
            else:
                raise DataSubjectRequestError(f"Unsupported request type: {request.request_type}")
            
            # Update request
            request.status = DataSubjectRequest.RequestStatus.COMPLETED
            request.completed_at = int(time.time())
            request.response_details = result
            self._save_request(request)
            
            logger.info(f"Data subject request {request.request_id} processed successfully")
            return request
        
        except Exception as e:
            logger.error(f"Failed to process data subject request: {str(e)}")
            
            # Update request
            request.status = DataSubjectRequest.RequestStatus.FAILED
            request.response_details = f"Error: {str(e)}"
            self._save_request(request)
            
            return request
    
    def _process_access_request(self, request: DataSubjectRequest) -> str:
        """
        Process an access request.
        
        Args:
            request: Data subject request
        
        Returns:
            str: Result details
        """
        # Find all data for the subject
        data = self._find_subject_data(request.subject_id)
        
        # Format result
        result = f"Access request processed. Found {len(data)} data items.\n\n"
        
        for item in data:
            result += f"- {item['storage_type']}: {item['object_id']}\n"
            result += f"  Created: {datetime.datetime.fromtimestamp(item['created_at']).isoformat()}\n"
            result += f"  Size: {item['size']} bytes\n"
            result += f"  Content Type: {item['content_type']}\n\n"
        
        return result
    
    def _process_erasure_request(self, request: DataSubjectRequest) -> str:
        """
        Process an erasure request.
        
        Args:
            request: Data subject request
        
        Returns:
            str: Result details
        """
        # Find all data for the subject
        data = self._find_subject_data(request.subject_id)
        
        # Delete or anonymize each item
        deleted_count = 0
        anonymized_count = 0
        error_count = 0
        
        for item in data:
            try:
                storage_type = StorageType(item['storage_type'])
                storage = self._storage_manager.get_storage(storage_type)
                
                # Determine if data should be deleted or anonymized
                if self._can_delete_data(item):
                    # Delete data
                    storage.delete_object(
                        item['object_id'],
                        requester="system"
                    )
                    deleted_count += 1
                else:
                    # Anonymize data
                    self._anonymize_object(item, storage)
                    anonymized_count += 1
            
            except Exception as e:
                logger.error(f"Error processing item {item['object_id']}: {str(e)}")
                error_count += 1
        
        # Format result
        result = f"Erasure request processed.\n\n"
        result += f"- Total items: {len(data)}\n"
        result += f"- Deleted: {deleted_count}\n"
        result += f"- Anonymized: {anonymized_count}\n"
        result += f"- Errors: {error_count}\n"
        
        return result
    
    def _process_rectification_request(self, request: DataSubjectRequest) -> str:
        """
        Process a rectification request.
        
        Args:
            request: Data subject request
        
        Returns:
            str: Result details
        """
        # This would typically involve updating specific data fields
        # For this implementation, we'll just return a placeholder
        return "Rectification request processed. Data has been updated."
    
    def _process_restriction_request(self, request: DataSubjectRequest) -> str:
        """
        Process a restriction request.
        
        Args:
            request: Data subject request
        
        Returns:
            str: Result details
        """
        # This would typically involve marking data as restricted
        # For this implementation, we'll just return a placeholder
        return "Restriction request processed. Data processing has been restricted."
    
    def _process_portability_request(self, request: DataSubjectRequest) -> str:
        """
        Process a portability request.
        
        Args:
            request: Data subject request
        
        Returns:
            str: Result details
        """
        # Find all data for the subject
        data = self._find_subject_data(request.subject_id)
        
        # Export data in portable format
        export_data = []
        
        for item in data:
            try:
                storage_type = StorageType(item['storage_type'])
                storage = self._storage_manager.get_storage(storage_type)
                
                # Retrieve data
                data_stream, _ = storage.retrieve_object(
                    item['object_id'],
                    requester="system"
                )
                
                # Read data
                raw_data = data_stream.read()
                data_stream.close()
                
                # Add to export
                export_data.append({
                    'object_id': item['object_id'],
                    'content_type': item['content_type'],
                    'created_at': item['created_at'],
                    'data': base64.b64encode(raw_data).decode('utf-8')
                })
            
            except Exception as e:
                logger.error(f"Error exporting item {item['object_id']}: {str(e)}")
        
        # Format result
        result = f"Portability request processed. Exported {len(export_data)} data items.\n\n"
        result += "Data has been exported in a portable format."
        
        return result
    
    def _process_objection_request(self, request: DataSubjectRequest) -> str:
        """
        Process an objection request.
        
        Args:
            request: Data subject request
        
        Returns:
            str: Result details
        """
        # This would typically involve marking data as objected to
        # For this implementation, we'll just return a placeholder
        return "Objection request processed. Data processing has been adjusted."
    
    def _process_automated_decision_request(self, request: DataSubjectRequest) -> str:
        """
        Process an automated decision request.
        
        Args:
            request: Data subject request
        
        Returns:
            str: Result details
        """
        # This would typically involve reviewing automated decisions
        # For this implementation, we'll just return a placeholder
        return "Automated decision request processed. Decisions have been reviewed."
    
    def _find_subject_data(self, subject_id: str) -> List[Dict[str, Any]]:
        """
        Find all data for a subject.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            List[Dict[str, Any]]: List of data items
        """
        results = []
        
        # Process each storage type
        for storage_type in [
            StorageType.OBJECT,
            StorageType.FILE,
            StorageType.DATABASE,
            StorageType.CACHE
        ]:
            try:
                storage = self._storage_manager.get_storage(storage_type)
                
                # List all objects
                objects, _ = storage.list_objects(requester="system")
                
                # Filter objects for this subject
                for obj_metadata in objects:
                    # Check if object belongs to subject
                    if self._is_subject_data(obj_metadata, subject_id):
                        results.append({
                            'storage_type': storage_type.value,
                            'object_id': obj_metadata.object_id,
                            'content_type': obj_metadata.content_type,
                            'size': obj_metadata.size,
                            'created_at': obj_metadata.created_at,
                            'modified_at': obj_metadata.modified_at
                        })
            
            except Exception as e:
                logger.error(f"Error searching storage type {storage_type.value}: {str(e)}")
        
        return results
    
    def _is_subject_data(self, obj_metadata: Any, subject_id: str) -> bool:
        """
        Determine if an object contains data for a subject.
        
        Args:
            obj_metadata: Object metadata
            subject_id: Subject ID
        
        Returns:
            bool: Whether the object contains data for the subject
        """
        # Check object ID
        if subject_id in obj_metadata.object_id:
            return True
        
        # Check owner
        if hasattr(obj_metadata, 'owner') and obj_metadata.owner == subject_id:
            return True
        
        # Check metadata
        if hasattr(obj_metadata, 'metadata') and obj_metadata.metadata:
            if 'subject_id' in obj_metadata.metadata and obj_metadata.metadata['subject_id'] == subject_id:
                return True
        
        # More sophisticated checks would be implemented here
        # For example, retrieving and scanning the content
        
        return False
    
    def _can_delete_data(self, item: Dict[str, Any]) -> bool:
        """
        Determine if data can be deleted or should be anonymized.
        
        Args:
            item: Data item
        
        Returns:
            bool: Whether the data can be deleted
        """
        # This would typically involve checking legal requirements
        # For this implementation, we'll use a simple heuristic
        
        # Don't delete database records, anonymize them
        if item['storage_type'] == StorageType.DATABASE.value:
            return False
        
        # Don't delete items needed for legal compliance
        if 'legal' in item['object_id'].lower():
            return False
        
        # Don't delete items needed for financial records
        if 'financial' in item['object_id'].lower() or 'finance' in item['object_id'].lower():
            return False
        
        # Default to allowing deletion
        return True
    
    def _anonymize_object(self, item: Dict[str, Any], storage: Any) -> None:
        """
        Anonymize an object.
        
        Args:
            item: Data item
            storage: Storage service
        """
        try:
            # Retrieve object
            data_stream, _ = storage.retrieve_object(
                item['object_id'],
                requester="system"
            )
            
            # Read data
            data = data_stream.read()
            data_stream.close()
            
            # Anonymize data
            anonymized_data = self._anonymization.anonymize_data(
                data=data,
                content_type=item['content_type']
            )
            
            # Store anonymized data
            storage.store_object(
                data=anonymized_data,
                content_type=item['content_type'],
                owner="anonymized",
                object_id=item['object_id'],
                encrypt=True,
                verify_integrity=True
            )
            
            logger.info(f"Object {item['object_id']} anonymized successfully")
        
        except Exception as e:
            logger.error(f"Failed to anonymize object {item['object_id']}: {str(e)}")
            raise DataSubjectRequestError(f"Failed to anonymize object: {str(e)}")

class ComplianceManager:
    """
    Service for managing compliance requirements and controls.
    
    This class provides methods for creating, managing, and validating
    compliance requirements and controls for various standards.
    """
    
    def __init__(
        self,
        storage_path: str,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the compliance manager.
        
        Args:
            storage_path: Path for storing compliance data
            audit_logger: Audit logger
        """
        self._storage_path = os.path.abspath(storage_path)
        self._audit_logger = audit_logger
        
        # Create storage directories
        self._requirements_path = os.path.join(self._storage_path, "requirements")
        os.makedirs(self._requirements_path, exist_ok=True)
        
        self._controls_path = os.path.join(self._storage_path, "controls")
        os.makedirs(self._controls_path, exist_ok=True)
        
        self._evidence_path = os.path.join(self._storage_path, "evidence")
        os.makedirs(self._evidence_path, exist_ok=True)
        
        logger.info(f"Compliance Manager initialized with storage path {self._storage_path}")
    
    def _get_requirement_path(self, requirement_id: str) -> str:
        """Get the path for a requirement file."""
        return os.path.join(self._requirements_path, f"{requirement_id}.json")
    
    def _get_control_path(self, control_id: str) -> str:
        """Get the path for a control file."""
        return os.path.join(self._controls_path, f"{control_id}.json")
    
    def create_requirement(
        self,
        standard: ComplianceStandard,
        title: str,
        description: str,
        section: str,
        controls: List[str],
        tags: Optional[Dict[str, str]] = None
    ) -> ComplianceRequirement:
        """
        Create a compliance requirement.
        
        Args:
            standard: Compliance standard
            title: Short title of the requirement
            description: Detailed description
            section: Section or article in the standard
            controls: List of control identifiers
            tags: Additional metadata tags
        
        Returns:
            ComplianceRequirement: The created requirement
        
        Raises:
            ComplianceError: If requirement creation fails
        """
        try:
            # Generate requirement ID
            requirement_id = f"{standard.value}_{section.replace('.', '_')}"
            
            # Create requirement
            requirement = ComplianceRequirement(
                requirement_id=requirement_id,
                standard=standard,
                title=title,
                description=description,
                section=section,
                controls=controls,
                tags=tags
            )
            
            # Save requirement
            self._save_requirement(requirement)
            
            # Log event
            if self._audit_logger:
                self._audit_logger.log_event(
                    event_type=AuditEventType.COMPLIANCE,
                    severity=AuditEventSeverity.INFO,
                    actor="system",
                    action="create_requirement",
                    resource=f"requirement/{requirement_id}",
                    outcome="success",
                    details={
                        'standard': standard.value,
                        'title': title,
                        'section': section
                    }
                )
            
            logger.info(f"Compliance requirement {requirement_id} created successfully")
            return requirement
        
        except Exception as e:
            logger.error(f"Failed to create compliance requirement: {str(e)}")
            raise ComplianceError(f"Failed to create compliance requirement: {str(e)}")
    
    def _save_requirement(self, requirement: ComplianceRequirement) -> None:
        """
        Save a compliance requirement to disk.
        
        Args:
            requirement: Compliance requirement
        """
        requirement_path = self._get_requirement_path(requirement.requirement_id)
        with open(requirement_path, 'w') as f:
            json.dump(requirement.to_dict(), f)
    
    def get_requirement(self, requirement_id: str) -> ComplianceRequirement:
        """
        Get a compliance requirement.
        
        Args:
            requirement_id: Requirement ID
        
        Returns:
            ComplianceRequirement: The requirement
        
        Raises:
            ComplianceError: If requirement retrieval fails
        """
        try:
            requirement_path = self._get_requirement_path(requirement_id)
            
            if not os.path.exists(requirement_path):
                raise ComplianceError(f"Compliance requirement {requirement_id} not found")
            
            with open(requirement_path, 'r') as f:
                requirement_dict = json.load(f)
            
            return ComplianceRequirement.from_dict(requirement_dict)
        
        except Exception as e:
            logger.error(f"Failed to get compliance requirement: {str(e)}")
            raise ComplianceError(f"Failed to get compliance requirement: {str(e)}")
    
    def list_requirements(
        self,
        standard: Optional[ComplianceStandard] = None,
        section: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[ComplianceRequirement]:
        """
        List compliance requirements with optional filtering.
        
        Args:
            standard: Filter by standard
            section: Filter by section
            tags: Filter by tags
        
        Returns:
            List[ComplianceRequirement]: List of requirements
        
        Raises:
            ComplianceError: If listing fails
        """
        try:
            results = []
            
            # List all requirement files
            for filename in os.listdir(self._requirements_path):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    # Read requirement
                    with open(os.path.join(self._requirements_path, filename), 'r') as f:
                        requirement_dict = json.load(f)
                    
                    requirement = ComplianceRequirement.from_dict(requirement_dict)
                    
                    # Apply filters
                    if standard and requirement.standard != standard:
                        continue
                    
                    if section and requirement.section != section:
                        continue
                    
                    if tags:
                        match = True
                        for key, value in tags.items():
                            if key not in requirement.tags or requirement.tags[key] != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    results.append(requirement)
                
                except Exception as e:
                    logger.error(f"Error processing requirement file {filename}: {str(e)}")
                    # Continue with next file
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to list compliance requirements: {str(e)}")
            raise ComplianceError(f"Failed to list compliance requirements: {str(e)}")
    
    def create_control(
        self,
        name: str,
        description: str,
        implementation_status: str,
        verification_method: str,
        owner: str,
        requirements: List[str],
        evidence: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> ComplianceControl:
        """
        Create a compliance control.
        
        Args:
            name: Name of the control
            description: Detailed description
            implementation_status: Status of implementation
            verification_method: Method used to verify the control
            owner: Owner responsible for the control
            requirements: List of requirement IDs this control addresses
            evidence: List of evidence identifiers
            tags: Additional metadata tags
        
        Returns:
            ComplianceControl: The created control
        
        Raises:
            ComplianceError: If control creation fails
        """
        try:
            # Generate control ID
            control_id = f"control_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            
            # Create control
            control = ComplianceControl(
                control_id=control_id,
                name=name,
                description=description,
                implementation_status=implementation_status,
                verification_method=verification_method,
                owner=owner,
                requirements=requirements,
                evidence=evidence,
                tags=tags
            )
            
            # Save control
            self._save_control(control)
            
            # Log event
            if self._audit_logger:
                self._audit_logger.log_event(
                    event_type=AuditEventType.COMPLIANCE,
                    severity=AuditEventSeverity.INFO,
                    actor=owner,
                    action="create_control",
                    resource=f"control/{control_id}",
                    outcome="success",
                    details={
                        'name': name,
                        'implementation_status': implementation_status,
                        'requirements': requirements
                    }
                )
            
            logger.info(f"Compliance control {control_id} created successfully")
            return control
        
        except Exception as e:
            logger.error(f"Failed to create compliance control: {str(e)}")
            raise ComplianceError(f"Failed to create compliance control: {str(e)}")
    
    def _save_control(self, control: ComplianceControl) -> None:
        """
        Save a compliance control to disk.
        
        Args:
            control: Compliance control
        """
        control_path = self._get_control_path(control.control_id)
        with open(control_path, 'w') as f:
            json.dump(control.to_dict(), f)
    
    def get_control(self, control_id: str) -> ComplianceControl:
        """
        Get a compliance control.
        
        Args:
            control_id: Control ID
        
        Returns:
            ComplianceControl: The control
        
        Raises:
            ComplianceError: If control retrieval fails
        """
        try:
            control_path = self._get_control_path(control_id)
            
            if not os.path.exists(control_path):
                raise ComplianceError(f"Compliance control {control_id} not found")
            
            with open(control_path, 'r') as f:
                control_dict = json.load(f)
            
            return ComplianceControl.from_dict(control_dict)
        
        except Exception as e:
            logger.error(f"Failed to get compliance control: {str(e)}")
            raise ComplianceError(f"Failed to get compliance control: {str(e)}")
    
    def list_controls(
        self,
        owner: Optional[str] = None,
        implementation_status: Optional[str] = None,
        requirement: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[ComplianceControl]:
        """
        List compliance controls with optional filtering.
        
        Args:
            owner: Filter by owner
            implementation_status: Filter by implementation status
            requirement: Filter by requirement ID
            tags: Filter by tags
        
        Returns:
            List[ComplianceControl]: List of controls
        
        Raises:
            ComplianceError: If listing fails
        """
        try:
            results = []
            
            # List all control files
            for filename in os.listdir(self._controls_path):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    # Read control
                    with open(os.path.join(self._controls_path, filename), 'r') as f:
                        control_dict = json.load(f)
                    
                    control = ComplianceControl.from_dict(control_dict)
                    
                    # Apply filters
                    if owner and control.owner != owner:
                        continue
                    
                    if implementation_status and control.implementation_status != implementation_status:
                        continue
                    
                    if requirement and requirement not in control.requirements:
                        continue
                    
                    if tags:
                        match = True
                        for key, value in tags.items():
                            if key not in control.tags or control.tags[key] != value:
                                match = False
                                break
                        
                        if not match:
                            continue
                    
                    results.append(control)
                
                except Exception as e:
                    logger.error(f"Error processing control file {filename}: {str(e)}")
                    # Continue with next file
            
            return results
        
        except Exception as e:
            logger.error(f"Failed to list compliance controls: {str(e)}")
            raise ComplianceError(f"Failed to list compliance controls: {str(e)}")
    
    def update_control(
        self,
        control_id: str,
        owner: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        implementation_status: Optional[str] = None,
        verification_method: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        evidence: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> ComplianceControl:
        """
        Update a compliance control.
        
        Args:
            control_id: Control ID
            owner: Owner requesting update
            name: Name of the control
            description: Detailed description
            implementation_status: Status of implementation
            verification_method: Method used to verify the control
            requirements: List of requirement IDs this control addresses
            evidence: List of evidence identifiers
            tags: Additional metadata tags
        
        Returns:
            ComplianceControl: The updated control
        
        Raises:
            ComplianceError: If update fails
        """
        try:
            # Get control
            control = self.get_control(control_id)
            
            # Check ownership
            if control.owner != owner and owner != "system":
                raise ComplianceError(f"Access denied: {owner} is not the owner of control {control_id}")
            
            # Update fields
            if name is not None:
                control.name = name
            
            if description is not None:
                control.description = description
            
            if implementation_status is not None:
                control.implementation_status = implementation_status
            
            if verification_method is not None:
                control.verification_method = verification_method
            
            if requirements is not None:
                control.requirements = requirements
            
            if evidence is not None:
                control.evidence = evidence
            
            if tags is not None:
                control.tags = tags
            
            # Save updated control
            self._save_control(control)
            
            # Log event
            if self._audit_logger:
                self._audit_logger.log_event(
                    event_type=AuditEventType.COMPLIANCE,
                    severity=AuditEventSeverity.INFO,
                    actor=owner,
                    action="update_control",
                    resource=f"control/{control_id}",
                    outcome="success",
                    details={
                        'name': control.name,
                        'implementation_status': control.implementation_status
                    }
                )
            
            logger.info(f"Compliance control {control_id} updated successfully")
            return control
        
        except Exception as e:
            logger.error(f"Failed to update compliance control: {str(e)}")
            raise ComplianceError(f"Failed to update compliance control: {str(e)}")
    
    def verify_control(
        self,
        control_id: str,
        verifier: str,
        verification_result: str,
        evidence: Optional[List[str]] = None
    ) -> ComplianceControl:
        """
        Verify a compliance control.
        
        Args:
            control_id: Control ID
            verifier: Person performing verification
            verification_result: Result of verification
            evidence: List of evidence identifiers
        
        Returns:
            ComplianceControl: The updated control
        
        Raises:
            ComplianceError: If verification fails
        """
        try:
            # Get control
            control = self.get_control(control_id)
            
            # Update control
            control.last_verified = int(time.time())
            
            if evidence:
                control.evidence = evidence
            
            # Save updated control
            self._save_control(control)
            
            # Log event
            if self._audit_logger:
                self._audit_logger.log_event(
                    event_type=AuditEventType.COMPLIANCE,
                    severity=AuditEventSeverity.INFO,
                    actor=verifier,
                    action="verify_control",
                    resource=f"control/{control_id}",
                    outcome="success",
                    details={
                        'verification_result': verification_result,
                        'evidence': evidence
                    }
                )
            
            logger.info(f"Compliance control {control_id} verified successfully")
            return control
        
        except Exception as e:
            logger.error(f"Failed to verify compliance control: {str(e)}")
            raise ComplianceError(f"Failed to verify compliance control: {str(e)}")
    
    def generate_compliance_report(
        self,
        standard: ComplianceStandard,
        format: str = 'json'
    ) -> Tuple[bytes, str]:
        """
        Generate a compliance report for a standard.
        
        Args:
            standard: Compliance standard
            format: Report format (json, csv)
        
        Returns:
            Tuple[bytes, str]: Report data and content type
        
        Raises:
            ComplianceError: If report generation fails
        """
        try:
            # Get requirements for standard
            requirements = self.list_requirements(standard=standard)
            
            # Get controls
            controls = self.list_controls()
            
            # Build report data
            report_data = {
                'standard': standard.value,
                'generated_at': int(time.time()),
                'requirements': [],
                'summary': {
                    'total_requirements': len(requirements),
                    'total_controls': 0,
                    'implemented_controls': 0,
                    'verified_controls': 0,
                    'compliance_percentage': 0
                }
            }
            
            # Process each requirement
            for req in requirements:
                req_data = req.to_dict()
                req_data['controls'] = []
                
                # Find controls for this requirement
                for control in controls:
                    if req.requirement_id in control.requirements:
                        req_data['controls'].append(control.to_dict())
                
                report_data['requirements'].append(req_data)
                
                # Update summary
                report_data['summary']['total_controls'] += len(req_data['controls'])
                
                for control in req_data['controls']:
                    if control['implementation_status'] == 'implemented':
                        report_data['summary']['implemented_controls'] += 1
                    
                    if control['last_verified']:
                        report_data['summary']['verified_controls'] += 1
            
            # Calculate compliance percentage
            if report_data['summary']['total_controls'] > 0:
                report_data['summary']['compliance_percentage'] = (
                    report_data['summary']['implemented_controls'] /
                    report_data['summary']['total_controls'] * 100
                )
            
            # Generate report in requested format
            if format.lower() == 'json':
                # Export as JSON
                data = json.dumps(report_data, indent=2)
                content_type = 'application/json'
                return data.encode('utf-8'), content_type
            
            elif format.lower() == 'csv':
                # Export as CSV
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'Requirement ID', 'Section', 'Title',
                    'Control ID', 'Control Name', 'Implementation Status',
                    'Last Verified', 'Owner'
                ])
                
                # Write data
                for req in report_data['requirements']:
                    if not req['controls']:
                        # Write requirement with no controls
                        writer.writerow([
                            req['requirement_id'],
                            req['section'],
                            req['title'],
                            '', '', '', '', ''
                        ])
                    else:
                        # Write requirement with each control
                        for control in req['controls']:
                            last_verified = ''
                            if control['last_verified']:
                                last_verified = datetime.datetime.fromtimestamp(
                                    control['last_verified']
                                ).isoformat()
                            
                            writer.writerow([
                                req['requirement_id'],
                                req['section'],
                                req['title'],
                                control['control_id'],
                                control['name'],
                                control['implementation_status'],
                                last_verified,
                                control['owner']
                            ])
                
                content_type = 'text/csv'
                return output.getvalue().encode('utf-8'), content_type
            
            else:
                raise ComplianceError(f"Unsupported report format: {format}")
        
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {str(e)}")
            raise ComplianceError(f"Failed to generate compliance report: {str(e)}")

class ComplianceToolsService:
    """
    Main service for compliance tools.
    
    This class provides a unified interface to all compliance tools,
    including audit logging, retention management, data subject requests,
    and compliance management.
    """
    
    def __init__(
        self,
        storage_manager: StorageManager,
        base_path: str,
        crypto_core: Optional[CryptoCore] = None,
        anonymization_service: Optional[Any] = None
    ):
        """
        Initialize the compliance tools service.
        
        Args:
            storage_manager: Storage manager
            base_path: Base path for storing compliance data
            crypto_core: Cryptographic core
            anonymization_service: Data anonymization service
        """
        self._storage_manager = storage_manager
        self._base_path = os.path.abspath(base_path)
        self._crypto = crypto_core or CryptoCore()
        self._anonymization = anonymization_service
        
        # Create base directory
        os.makedirs(self._base_path, exist_ok=True)
        
        # Initialize audit logger
        audit_path = os.path.join(self._base_path, "audit")
        self._audit_logger = AuditLogger(
            storage_manager=storage_manager,
            audit_storage_path=audit_path,
            crypto_core=self._crypto
        )
        
        # Initialize retention manager
        retention_path = os.path.join(self._base_path, "retention")
        self._retention_manager = RetentionManager(
            storage_manager=storage_manager,
            policy_storage_path=retention_path
        )
        
        # Initialize data subject request manager
        dsr_path = os.path.join(self._base_path, "dsr")
        self._dsr_manager = DataSubjectRequestManager(
            storage_manager=storage_manager,
            request_storage_path=dsr_path,
            anonymization_service=self._anonymization
        )
        
        # Initialize compliance manager
        compliance_path = os.path.join(self._base_path, "compliance")
        self._compliance_manager = ComplianceManager(
            storage_path=compliance_path,
            audit_logger=self._audit_logger
        )
        
        logger.info(f"Compliance Tools Service initialized with base path {self._base_path}")
    
    @property
    def audit_logger(self) -> AuditLogger:
        """Get the audit logger."""
        return self._audit_logger
    
    @property
    def retention_manager(self) -> RetentionManager:
        """Get the retention manager."""
        return self._retention_manager
    
    @property
    def dsr_manager(self) -> DataSubjectRequestManager:
        """Get the data subject request manager."""
        return self._dsr_manager
    
    @property
    def compliance_manager(self) -> ComplianceManager:
        """Get the compliance manager."""
        return self._compliance_manager
    
    def initialize_gdpr_requirements(self) -> List[ComplianceRequirement]:
        """
        Initialize GDPR compliance requirements.
        
        Returns:
            List[ComplianceRequirement]: Created requirements
        """
        requirements = []
        
        # Create GDPR requirements
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Lawfulness, fairness and transparency",
            description="Personal data shall be processed lawfully, fairly and in a transparent manner in relation to the data subject.",
            section="5.1.a",
            controls=[],
            tags={'category': 'principles'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Purpose limitation",
            description="Personal data shall be collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes.",
            section="5.1.b",
            controls=[],
            tags={'category': 'principles'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Data minimisation",
            description="Personal data shall be adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed.",
            section="5.1.c",
            controls=[],
            tags={'category': 'principles'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Accuracy",
            description="Personal data shall be accurate and, where necessary, kept up to date.",
            section="5.1.d",
            controls=[],
            tags={'category': 'principles'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Storage limitation",
            description="Personal data shall be kept in a form which permits identification of data subjects for no longer than is necessary for the purposes for which the personal data are processed.",
            section="5.1.e",
            controls=[],
            tags={'category': 'principles'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Integrity and confidentiality",
            description="Personal data shall be processed in a manner that ensures appropriate security of the personal data, including protection against unauthorised or unlawful processing and against accidental loss, destruction or damage, using appropriate technical or organisational measures.",
            section="5.1.f",
            controls=[],
            tags={'category': 'principles'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Right of access",
            description="The data subject shall have the right to obtain from the controller confirmation as to whether or not personal data concerning him or her are being processed, and, where that is the case, access to the personal data.",
            section="15",
            controls=[],
            tags={'category': 'rights'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Right to rectification",
            description="The data subject shall have the right to obtain from the controller without undue delay the rectification of inaccurate personal data concerning him or her.",
            section="16",
            controls=[],
            tags={'category': 'rights'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Right to erasure",
            description="The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay.",
            section="17",
            controls=[],
            tags={'category': 'rights'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.GDPR,
            title="Data protection by design and by default",
            description="The controller shall implement appropriate technical and organisational measures for ensuring that, by default, only personal data which are necessary for each specific purpose of the processing are processed.",
            section="25",
            controls=[],
            tags={'category': 'controller_obligations'}
        ))
        
        return requirements
    
    def initialize_hipaa_requirements(self) -> List[ComplianceRequirement]:
        """
        Initialize HIPAA compliance requirements.
        
        Returns:
            List[ComplianceRequirement]: Created requirements
        """
        requirements = []
        
        # Create HIPAA requirements
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.HIPAA,
            title="Privacy Rule - Notice of Privacy Practices",
            description="Covered entities must provide a notice of their privacy practices.",
            section="164.520",
            controls=[],
            tags={'category': 'privacy'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.HIPAA,
            title="Privacy Rule - Access of Individuals to PHI",
            description="Individuals have the right to access their protected health information.",
            section="164.524",
            controls=[],
            tags={'category': 'privacy'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.HIPAA,
            title="Security Rule - Administrative Safeguards",
            description="Covered entities must implement administrative safeguards to protect electronic PHI.",
            section="164.308",
            controls=[],
            tags={'category': 'security'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.HIPAA,
            title="Security Rule - Physical Safeguards",
            description="Covered entities must implement physical safeguards to protect electronic PHI.",
            section="164.310",
            controls=[],
            tags={'category': 'security'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.HIPAA,
            title="Security Rule - Technical Safeguards",
            description="Covered entities must implement technical safeguards to protect electronic PHI.",
            section="164.312",
            controls=[],
            tags={'category': 'security'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.HIPAA,
            title="Breach Notification Rule",
            description="Covered entities must provide notification following a breach of unsecured PHI.",
            section="164.400-414",
            controls=[],
            tags={'category': 'breach'}
        ))
        
        return requirements
    
    def initialize_pci_dss_requirements(self) -> List[ComplianceRequirement]:
        """
        Initialize PCI DSS compliance requirements.
        
        Returns:
            List[ComplianceRequirement]: Created requirements
        """
        requirements = []
        
        # Create PCI DSS requirements
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.PCI_DSS,
            title="Install and maintain a firewall configuration",
            description="Install and maintain a firewall configuration to protect cardholder data.",
            section="1",
            controls=[],
            tags={'category': 'network_security'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.PCI_DSS,
            title="Do not use vendor-supplied defaults",
            description="Do not use vendor-supplied defaults for system passwords and other security parameters.",
            section="2",
            controls=[],
            tags={'category': 'configuration'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.PCI_DSS,
            title="Protect stored cardholder data",
            description="Protect stored cardholder data.",
            section="3",
            controls=[],
            tags={'category': 'data_protection'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.PCI_DSS,
            title="Encrypt transmission of cardholder data",
            description="Encrypt transmission of cardholder data across open, public networks.",
            section="4",
            controls=[],
            tags={'category': 'data_protection'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.PCI_DSS,
            title="Use and regularly update anti-virus software",
            description="Use and regularly update anti-virus software or programs.",
            section="5",
            controls=[],
            tags={'category': 'malware_protection'}
        ))
        
        requirements.append(self._compliance_manager.create_requirement(
            standard=ComplianceStandard.PCI_DSS,
            title="Develop and maintain secure systems and applications",
            description="Develop and maintain secure systems and applications.",
            section="6",
            controls=[],
            tags={'category': 'secure_development'}
        ))
        
        return requirements
    
    def initialize_default_retention_policies(self) -> List[RetentionPolicy]:
        """
        Initialize default retention policies.
        
        Returns:
            List[RetentionPolicy]: Created policies
        """
        policies = []
        
        # Create default retention policies
        policies.append(self._retention_manager.create_policy(
            name="Personal Data Retention",
            description="Retention policy for personal data",
            data_category="personal_data",
            retention_period=60 * 60 * 24 * 365 * 2,  # 2 years
            legal_basis="GDPR Article 5(1)(e)",
            action_after_retention="anonymize",
            owner="system",
            applies_to=[".*personal.*", ".*user.*"],
            exceptions=[".*legal.*", ".*compliance.*"]
        ))
        
        policies.append(self._retention_manager.create_policy(
            name="Financial Data Retention",
            description="Retention policy for financial data",
            data_category="financial_data",
            retention_period=60 * 60 * 24 * 365 * 7,  # 7 years
            legal_basis="Tax regulations",
            action_after_retention="archive",
            owner="system",
            applies_to=[".*financial.*", ".*payment.*", ".*invoice.*"],
            exceptions=[]
        ))
        
        policies.append(self._retention_manager.create_policy(
            name="Log Data Retention",
            description="Retention policy for log data",
            data_category="log_data",
            retention_period=60 * 60 * 24 * 90,  # 90 days
            legal_basis="Security best practices",
            action_after_retention="delete",
            owner="system",
            applies_to=[".*log.*", ".*audit.*"],
            exceptions=[".*security.*", ".*incident.*"]
        ))
        
        policies.append(self._retention_manager.create_policy(
            name="Health Data Retention",
            description="Retention policy for health data",
            data_category="health_data",
            retention_period=60 * 60 * 24 * 365 * 6,  # 6 years
            legal_basis="HIPAA",
            action_after_retention="anonymize",
            owner="system",
            applies_to=[".*health.*", ".*medical.*"],
            exceptions=[]
        ))
        
        return policies
