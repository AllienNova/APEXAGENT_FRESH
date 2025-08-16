"""
Compliance Tools module for Dr. TARDIS Gemini Live API integration.

This module provides comprehensive compliance management capabilities including:
- Compliance standards and requirements management
- Compliance assessment and reporting
- Audit logging and evidence collection
- Retention policy enforcement
- Data subject request handling
"""

import re
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Import required modules
from src.data_protection.core.storage import StorageManager


class ComplianceStandard(Enum):
    """Compliance standards supported by the system."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    CCPA = "ccpa"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    NIST_800_53 = "nist_800_53"
    FERPA = "ferpa"
    GLBA = "glba"
    COPPA = "coppa"
    CUSTOM = "custom"


class DataClassification(Enum):
    """Data classification levels for sensitivity categorization."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    PERSONAL = "personal"
    SENSITIVE_PERSONAL = "sensitive_personal"
    HEALTH = "health"
    FINANCIAL = "financial"
    PROPRIETARY = "proprietary"
    CUSTOM = "custom"


class ConsentLevel(Enum):
    """Consent levels for data processing."""
    NONE = "none"
    IMPLIED = "implied"
    INFORMED = "informed"
    EXPLICIT = "explicit"
    PARENTAL = "parental"
    WITHDRAWN = "withdrawn"
    CUSTOM = "custom"


class AuditEventType(Enum):
    """Types of audit events."""
    ACCESS = "access"
    MODIFICATION = "modification"
    DELETION = "deletion"
    CREATION = "creation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SYSTEM = "system"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    CUSTOM = "custom"


class AuditEventSeverity(Enum):
    """Severity levels for audit events."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    WARNING = "warning"  # Added missing WARNING severity level


class CompliancePolicy:
    """Represents a compliance policy."""
    
    def __init__(
        self,
        policy_id: str,
        name: str,
        description: str,
        standard: ComplianceStandard,
        version: str,
        rules: List[str],
        owner: str,
        effective_date: int,
        review_date: Optional[int] = None,
        status: str = "active",
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a compliance policy.
        
        Args:
            policy_id: Unique identifier for the policy
            name: Name of the policy
            description: Detailed description
            standard: Compliance standard this policy implements
            version: Version of the policy
            rules: List of rule IDs this policy enforces
            owner: Owner responsible for the policy
            effective_date: Date when policy becomes effective (Unix time)
            review_date: Date when policy should be reviewed (Unix time)
            status: Status of the policy (active, draft, archived)
            tags: Additional metadata tags
        """
        self.policy_id = policy_id
        self.name = name
        self.description = description
        self.standard = standard
        self.version = version
        self.rules = rules
        self.owner = owner
        self.effective_date = effective_date
        self.review_date = review_date
        self.status = status
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'standard': self.standard.value,
            'version': self.version,
            'rules': self.rules,
            'owner': self.owner,
            'effective_date': self.effective_date,
            'review_date': self.review_date,
            'status': self.status,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompliancePolicy':
        """Create from dictionary."""
        return cls(
            policy_id=data['policy_id'],
            name=data['name'],
            description=data['description'],
            standard=ComplianceStandard(data['standard']),
            version=data['version'],
            rules=data['rules'],
            owner=data['owner'],
            effective_date=data['effective_date'],
            review_date=data.get('review_date'),
            status=data.get('status', 'active'),
            tags=data.get('tags')
        )


class ComplianceRule:
    """Represents a compliance rule."""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        standard: ComplianceStandard,
        requirement_id: str,
        validation_function: str,
        severity: str,
        remediation: str,
        automated: bool = True,
        parameters: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a compliance rule.
        
        Args:
            rule_id: Unique identifier for the rule
            name: Name of the rule
            description: Detailed description
            standard: Compliance standard this rule implements
            requirement_id: ID of the requirement this rule satisfies
            validation_function: Name of function to validate compliance
            severity: Severity if rule is violated
            remediation: Remediation steps if rule is violated
            automated: Whether rule can be automatically validated
            parameters: Parameters for validation function
            tags: Additional metadata tags
        """
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.standard = standard
        self.requirement_id = requirement_id
        self.validation_function = validation_function
        self.severity = severity
        self.remediation = remediation
        self.automated = automated
        self.parameters = parameters or {}
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'standard': self.standard.value,
            'requirement_id': self.requirement_id,
            'validation_function': self.validation_function,
            'severity': self.severity,
            'remediation': self.remediation,
            'automated': self.automated,
            'parameters': self.parameters,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceRule':
        """Create from dictionary."""
        return cls(
            rule_id=data['rule_id'],
            name=data['name'],
            description=data['description'],
            standard=ComplianceStandard(data['standard']),
            requirement_id=data['requirement_id'],
            validation_function=data['validation_function'],
            severity=data['severity'],
            remediation=data['remediation'],
            automated=data.get('automated', True),
            parameters=data.get('parameters'),
            tags=data.get('tags')
        )
    
    def validate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate compliance with this rule.
        
        Args:
            context: Context data for validation
            
        Returns:
            Tuple of (is_compliant, reason)
        """
        # This is a simplified implementation
        # In a real implementation, this would dynamically call the validation function
        if not self.automated:
            return False, "Manual validation required"
        
        # Simple validation based on context
        if self.rule_id in context.get('compliant_rules', []):
            return True, "Rule validated successfully"
        elif self.rule_id in context.get('non_compliant_rules', []):
            return False, f"Rule validation failed: {context.get('reasons', {}).get(self.rule_id, 'Unknown reason')}"
        else:
            return False, "Rule not evaluated"


class ComplianceRequirement:
    """Represents a compliance requirement."""
    
    def __init__(
        self,
        requirement_id: str,
        standard: ComplianceStandard,
        title: str = None,
        description: str = None,
        section: str = None,
        controls: List[str] = None,
        tags: Optional[Dict[str, str]] = None,
        verification_method: str = None,
        verification_frequency: str = None,
        owner: str = None,
        verification_status: Optional[str] = None,
        name: str = None
    ):
        """
        Initialize a compliance requirement.
        
        Args:
            requirement_id: Unique identifier for the requirement
            standard: Compliance standard this requirement belongs to
            title: Title of the requirement (preferred over name)
            description: Detailed description
            section: Section in the standard
            controls: List of control IDs that satisfy this requirement
            tags: Additional metadata tags
            verification_method: Method to verify compliance
            verification_frequency: How often to verify
            owner: Owner responsible for the requirement
            verification_status: Current verification status
            name: Name of the requirement (deprecated, use title instead)
        """
        self.requirement_id = requirement_id
        self.name = name
        self.description = description
        self.standard = standard
        self.section = section
        self.controls = controls
        self.verification_method = verification_method
        self.verification_frequency = verification_frequency
        self.owner = owner
        self.verification_status = verification_status
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'requirement_id': self.requirement_id,
            'name': self.name,
            'description': self.description,
            'standard': self.standard.value,
            'section': self.section,
            'controls': self.controls,
            'verification_method': self.verification_method,
            'verification_frequency': self.verification_frequency,
            'owner': self.owner,
            'verification_status': self.verification_status,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceRequirement':
        """Create from dictionary."""
        return cls(
            requirement_id=data['requirement_id'],
            name=data['name'],
            description=data['description'],
            standard=ComplianceStandard(data['standard']),
            section=data['section'],
            controls=data['controls'],
            verification_method=data['verification_method'],
            verification_frequency=data['verification_frequency'],
            owner=data['owner'],
            verification_status=data.get('verification_status'),
            tags=data.get('tags')
        )


class ComplianceControl:
    """Represents a compliance control."""
    
    def __init__(
        self,
        control_id: str,
        name: str,
        description: str,
        type: str,
        implementation_status: str,
        owner: str,
        effectiveness: Optional[float] = None,
        last_assessment: Optional[int] = None,
        documentation_url: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a compliance control.
        
        Args:
            control_id: Unique identifier for the control
            name: Name of the control
            description: Detailed description
            type: Type of control (preventive, detective, corrective)
            implementation_status: Status of implementation
            effectiveness: Effectiveness score (0.0-1.0)
            last_assessment: Timestamp of last assessment (Unix time)
            owner: Owner responsible for the control
            documentation_url: URL to control documentation
            tags: Additional metadata tags
        """
        self.control_id = control_id
        self.name = name
        self.description = description
        self.type = type
        self.implementation_status = implementation_status
        self.effectiveness = effectiveness
        self.last_assessment = last_assessment
        self.owner = owner
        self.documentation_url = documentation_url
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'control_id': self.control_id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'implementation_status': self.implementation_status,
            'effectiveness': self.effectiveness,
            'last_assessment': self.last_assessment,
            'owner': self.owner,
            'documentation_url': self.documentation_url,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceControl':
        """Create from dictionary."""
        return cls(
            control_id=data['control_id'],
            name=data['name'],
            description=data['description'],
            type=data['type'],
            implementation_status=data['implementation_status'],
            owner=data['owner'],
            effectiveness=data.get('effectiveness'),
            last_assessment=data.get('last_assessment'),
            documentation_url=data.get('documentation_url'),
            tags=data.get('tags')
        )


class AuditEvent:
    """Represents an audit event."""
    
    def __init__(
        self,
        event_id: str,
        timestamp: int,
        event_type: AuditEventType,
        severity: AuditEventSeverity,
        source: str,
        actor: str,
        resource: str,
        action: str,
        outcome: str,
        details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Initialize an audit event.
        
        Args:
            event_id: Unique identifier for the event
            timestamp: Event timestamp (Unix time)
            event_type: Type of event
            severity: Severity level
            source: Source of the event
            actor: Actor who performed the action
            resource: Resource that was acted upon
            action: Action that was performed
            outcome: Outcome of the action
            details: Detailed information about the event
            metadata: Additional metadata
            session_id: Session identifier
            tags: Additional metadata tags
            source_ip: Source IP address
            user_agent: User agent string
        """
        self.event_id = event_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.severity = severity
        self.source = source
        self.actor = actor
        self.resource = resource
        self.action = action
        self.outcome = outcome
        self.details = details
        self.metadata = metadata or {}
        self.session_id = session_id
        self.tags = tags or {}
        self.source_ip = source_ip
        self.user_agent = user_agent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'source': self.source,
            'actor': self.actor,
            'resource': self.resource,
            'action': self.action,
            'outcome': self.outcome,
            'details': self.details,
            'metadata': self.metadata,
            'session_id': self.session_id,
            'tags': self.tags,
            'source_ip': self.source_ip,
            'user_agent': self.user_agent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create from dictionary."""
        return cls(
            event_id=data['event_id'],
            timestamp=data['timestamp'],
            event_type=AuditEventType(data['event_type']),
            severity=AuditEventSeverity(data['severity']),
            source=data['source'],
            actor=data['actor'],
            resource=data['resource'],
            action=data['action'],
            outcome=data['outcome'],
            details=data['details'],
            metadata=data.get('metadata'),
            session_id=data.get('session_id'),
            tags=data.get('tags'),
            source_ip=data.get('source_ip'),
            user_agent=data.get('user_agent')
        )


class DataRetentionPolicy:
    """Represents a data retention policy."""
    
    def __init__(
        self,
        policy_id: str,
        name: str,
        description: str,
        data_types: List[str],
        retention_period: int,
        deletion_method: str,
        legal_basis: str,
        exceptions: Optional[List[str]] = None,
        owner: str = None,
        effective_date: Optional[int] = None,
        review_date: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a data retention policy.
        
        Args:
            policy_id: Unique identifier for the policy
            name: Name of the policy
            description: Detailed description
            data_types: Types of data this policy applies to
            retention_period: Retention period in days
            deletion_method: Method for deleting data
            legal_basis: Legal basis for retention
            exceptions: Exceptions to the policy
            owner: Owner responsible for the policy
            effective_date: Date when policy becomes effective (Unix time)
            review_date: Date when policy should be reviewed (Unix time)
            tags: Additional metadata tags
        """
        self.policy_id = policy_id
        self.name = name
        self.description = description
        self.data_types = data_types
        self.retention_period = retention_period
        self.deletion_method = deletion_method
        self.legal_basis = legal_basis
        self.exceptions = exceptions or []
        self.owner = owner
        self.effective_date = effective_date or int(time.time())
        self.review_date = review_date
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'data_types': self.data_types,
            'retention_period': self.retention_period,
            'deletion_method': self.deletion_method,
            'legal_basis': self.legal_basis,
            'exceptions': self.exceptions,
            'owner': self.owner,
            'effective_date': self.effective_date,
            'review_date': self.review_date,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataRetentionPolicy':
        """Create from dictionary."""
        return cls(
            policy_id=data['policy_id'],
            name=data['name'],
            description=data['description'],
            data_types=data['data_types'],
            retention_period=data['retention_period'],
            deletion_method=data['deletion_method'],
            legal_basis=data['legal_basis'],
            exceptions=data.get('exceptions'),
            owner=data.get('owner'),
            effective_date=data.get('effective_date'),
            review_date=data.get('review_date'),
            tags=data.get('tags')
        )
    
    def should_retain(self, data_type: str, creation_time: int) -> bool:
        """
        Check if data should be retained based on this policy.
        
        Args:
            data_type: Type of data
            creation_time: Creation time of the data (Unix time)
            
        Returns:
            True if data should be retained, False if it should be deleted
        """
        # Check if data type is covered by this policy
        if data_type not in self.data_types:
            return True  # Not covered by this policy, retain by default
        
        # Check if data type is in exceptions
        if data_type in self.exceptions:
            return True  # Exception to the policy, retain
        
        # Check if retention period has expired
        current_time = int(time.time())
        age_days = (current_time - creation_time) / (24 * 60 * 60)
        
        return age_days <= self.retention_period


class ComplianceReport:
    """Represents a compliance report."""
    
    def __init__(
        self,
        report_id: str,
        title: str,
        description: str,
        standards: List[ComplianceStandard],
        timestamp: int,
        results: Dict[str, Any],
        summary: Dict[str, Any],
        generated_by: str,
        report_period: Dict[str, int],
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a compliance report.
        
        Args:
            report_id: Unique identifier for the report
            title: Title of the report
            description: Detailed description
            standards: Compliance standards covered in the report
            timestamp: Report generation timestamp (Unix time)
            results: Detailed compliance results
            summary: Summary of compliance status
            generated_by: Entity that generated the report
            report_period: Start and end time of the report period
            tags: Additional metadata tags
        """
        self.report_id = report_id
        self.title = title
        self.description = description
        self.standards = standards
        self.timestamp = timestamp
        self.results = results
        self.summary = summary
        self.generated_by = generated_by
        self.report_period = report_period
        self.tags = tags or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'report_id': self.report_id,
            'title': self.title,
            'description': self.description,
            'standards': [s.value for s in self.standards],
            'timestamp': self.timestamp,
            'results': self.results,
            'summary': self.summary,
            'generated_by': self.generated_by,
            'report_period': self.report_period,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplianceReport':
        """Create from dictionary."""
        return cls(
            report_id=data['report_id'],
            title=data['title'],
            description=data['description'],
            standards=[ComplianceStandard(s) for s in data['standards']],
            timestamp=data['timestamp'],
            results=data['results'],
            summary=data['summary'],
            generated_by=data['generated_by'],
            report_period=data['report_period'],
            tags=data.get('tags')
        )


class ComplianceAuditor:
    """Audits compliance with various standards and requirements."""
    
    def __init__(
        self,
        storage_manager: Optional[StorageManager] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the compliance auditor.
        
        Args:
            storage_manager: Storage manager for persistence
            config: Configuration options
        """
        self.storage_manager = storage_manager
        
        # Default configuration
        self.config = {
            'audit_frequency': 'daily',
            'standards': [s.value for s in ComplianceStandard],
            'evidence_retention_days': 365,
            'report_format': 'json',
            'notification_enabled': True,
            'auto_remediation_enabled': False
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        # Load compliance requirements
        self.requirements = {}
        self.rules = {}
        
        # Initialize audit log
        self.audit_log = []
    
    def audit_compliance(
        self,
        standard: Union[ComplianceStandard, str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Audit compliance with a specific standard.
        
        Args:
            standard: Compliance standard to audit
            context: Context data for the audit
            
        Returns:
            Audit results
        """
        # Convert string standard to enum if needed
        if isinstance(standard, str):
            try:
                standard = ComplianceStandard(standard)
            except ValueError:
                return {
                    'status': 'error',
                    'message': f"Invalid compliance standard: {standard}",
                    'timestamp': int(time.time())
                }
        
        # Get requirements for the standard
        requirements = self.get_requirements(standard)
        if not requirements:
            return {
                'status': 'error',
                'message': f"No requirements found for standard: {standard.value}",
                'timestamp': int(time.time())
            }
        
        # Audit each requirement
        results = {
            'standard': standard.value,
            'timestamp': int(time.time()),
            'requirements': {},
            'summary': {
                'total': len(requirements),
                'compliant': 0,
                'non_compliant': 0,
                'not_applicable': 0,
                'not_evaluated': 0
            }
        }
        
        for req in requirements:
            req_result = self.audit_requirement(req, context)
            results['requirements'][req.requirement_id] = req_result
            
            # Update summary
            if req_result['status'] == 'compliant':
                results['summary']['compliant'] += 1
            elif req_result['status'] == 'non_compliant':
                results['summary']['non_compliant'] += 1
            elif req_result['status'] == 'not_applicable':
                results['summary']['not_applicable'] += 1
            else:
                results['summary']['not_evaluated'] += 1
        
        # Calculate overall compliance status
        if results['summary']['non_compliant'] > 0:
            results['status'] = 'non_compliant'
        elif results['summary']['not_evaluated'] > 0:
            results['status'] = 'partially_compliant'
        else:
            results['status'] = 'compliant'
        
        # Log the audit
        self.log_audit(standard, results)
        
        return results
    
    def audit_requirement(
        self,
        requirement: ComplianceRequirement,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Audit compliance with a specific requirement.
        
        Args:
            requirement: Compliance requirement to audit
            context: Context data for the audit
            
        Returns:
            Audit results for the requirement
        """
        # Get rules for the requirement
        rules = self.get_rules(requirement.requirement_id)
        
        # If no rules, mark as not evaluated
        if not rules:
            return {
                'status': 'not_evaluated',
                'message': f"No rules defined for requirement: {requirement.requirement_id}",
                'timestamp': int(time.time())
            }
        
        # Evaluate each rule
        rule_results = {}
        compliant_count = 0
        
        for rule in rules:
            is_compliant, reason = rule.validate(context)
            rule_results[rule.rule_id] = {
                'status': 'compliant' if is_compliant else 'non_compliant',
                'message': reason
            }
            
            if is_compliant:
                compliant_count += 1
        
        # Determine overall requirement status
        if compliant_count == len(rules):
            status = 'compliant'
            message = f"All {len(rules)} rules passed"
        elif compliant_count == 0:
            status = 'non_compliant'
            message = f"All {len(rules)} rules failed"
        else:
            status = 'partially_compliant'
            message = f"{compliant_count} of {len(rules)} rules passed"
        
        return {
            'status': status,
            'message': message,
            'timestamp': int(time.time()),
            'rules': rule_results
        }
    
    def get_requirements(self, standard: ComplianceStandard) -> List[ComplianceRequirement]:
        """
        Get requirements for a specific standard.
        
        Args:
            standard: Compliance standard
            
        Returns:
            List of compliance requirements
        """
        # In a real implementation, this would load from a database or configuration
        # For this implementation, return a minimal set of requirements
        return self.requirements.get(standard.value, [])
    
    def get_rules(self, requirement_id: str) -> List[ComplianceRule]:
        """
        Get rules for a specific requirement.
        
        Args:
            requirement_id: Requirement ID
            
        Returns:
            List of compliance rules
        """
        # In a real implementation, this would load from a database or configuration
        # For this implementation, return a minimal set of rules
        return self.rules.get(requirement_id, [])
    
    def log_audit(self, standard: ComplianceStandard, results: Dict[str, Any]) -> None:
        """
        Log an audit event.
        
        Args:
            standard: Compliance standard that was audited
            results: Audit results
        """
        audit_event = {
            'event_id': str(uuid.uuid4()),
            'timestamp': int(time.time()),
            'standard': standard.value,
            'status': results['status'],
            'summary': results['summary']
        }
        
        self.audit_log.append(audit_event)
        
        # In a real implementation, this would persist to storage
        if self.storage_manager:
            pass  # Store audit event
    
    def generate_report(
        self,
        standards: Optional[List[ComplianceStandard]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> ComplianceReport:
        """
        Generate a compliance report.
        
        Args:
            standards: List of standards to include in the report
            start_time: Start time for the report period (Unix time)
            end_time: End time for the report period (Unix time)
            
        Returns:
            Compliance report
        """
        # Default to all standards if none specified
        if not standards:
            standards = [ComplianceStandard(s) for s in self.config['standards']]
        
        # Default time range to last 30 days if not specified
        current_time = int(time.time())
        if not end_time:
            end_time = current_time
        if not start_time:
            start_time = end_time - (30 * 24 * 60 * 60)  # 30 days
        
        # Filter audit log by time range and standards
        filtered_log = [
            event for event in self.audit_log
            if start_time <= event['timestamp'] <= end_time
            and event['standard'] in [s.value for s in standards]
        ]
        
        # Aggregate results by standard
        results = {}
        summary = {
            'total_standards': len(standards),
            'compliant_standards': 0,
            'non_compliant_standards': 0,
            'partially_compliant_standards': 0
        }
        
        for standard in standards:
            standard_events = [
                event for event in filtered_log
                if event['standard'] == standard.value
            ]
            
            if not standard_events:
                results[standard.value] = {
                    'status': 'not_evaluated',
                    'message': 'No audit events found for this standard'
                }
                continue
            
            # Get the most recent event for this standard
            latest_event = max(standard_events, key=lambda e: e['timestamp'])
            
            results[standard.value] = {
                'status': latest_event['status'],
                'timestamp': latest_event['timestamp'],
                'summary': latest_event['summary']
            }
            
            # Update summary
            if latest_event['status'] == 'compliant':
                summary['compliant_standards'] += 1
            elif latest_event['status'] == 'non_compliant':
                summary['non_compliant_standards'] += 1
            else:
                summary['partially_compliant_standards'] += 1
        
        # Create report
        report = ComplianceReport(
            report_id=str(uuid.uuid4()),
            title=f"Compliance Report {time.strftime('%Y-%m-%d', time.localtime(start_time))} to {time.strftime('%Y-%m-%d', time.localtime(end_time))}",
            description=f"Compliance report for {len(standards)} standards",
            standards=standards,
            timestamp=current_time,
            results=results,
            summary=summary,
            generated_by="ComplianceAuditor",
            report_period={
                'start_time': start_time,
                'end_time': end_time
            }
        )
        
        return report


# Add ConsentStatus enum for validation
class ConsentStatus(Enum):
    """Status of user consent."""
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    UNKNOWN = "unknown"
    NO_CONSENT = "no_consent"  # Added missing NO_CONSENT status


class ComplianceManager:
    """
    Manages compliance operations for the system.
    
    This class provides a centralized interface for compliance management,
    including policy enforcement, audit coordination, and reporting.
    """
    
    def __init__(
        self,
        storage_manager: Optional[StorageManager] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the compliance manager.
        
        Args:
            storage_manager: Storage manager for persistence
            config: Configuration options
        """
        self.storage_manager = storage_manager
        
        # Default configuration
        self.config = {
            'enabled_standards': [s.value for s in ComplianceStandard],
            'audit_schedule': 'daily',
            'report_schedule': 'weekly',
            'notification_enabled': True,
            'auto_remediation_enabled': False,
            'retention_policy_enforcement': True
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        # Initialize components
        self.auditor = ComplianceAuditor(storage_manager, config)
        self.policies = {}
        self.retention_policies = {}
        
        # Load policies
        self._load_policies()
    
    def _load_policies(self) -> None:
        """Load compliance policies from storage."""
        # In a real implementation, this would load from a database or configuration
        # For this implementation, we'll create some default policies
        
        # Example compliance policy
        gdpr_policy = CompliancePolicy(
            policy_id="gdpr-default",
            name="GDPR Default Policy",
            description="Default policy for GDPR compliance",
            standard=ComplianceStandard.GDPR,
            version="1.0",
            rules=["gdpr-consent", "gdpr-data-minimization", "gdpr-retention"],
            owner="compliance_team",
            effective_date=int(time.time())
        )
        
        # Example retention policy
        user_data_retention = DataRetentionPolicy(
            policy_id="user-data-retention",
            name="User Data Retention Policy",
            description="Retention policy for user data",
            data_types=["user_profile", "user_preferences", "user_activity"],
            retention_period=365 * 2,  # 2 years
            deletion_method="secure_delete",
            legal_basis="legitimate_interest",
            owner="data_protection_officer"
        )
        
        # Store policies
        self.policies[gdpr_policy.policy_id] = gdpr_policy
        self.retention_policies[user_data_retention.policy_id] = user_data_retention
    
    def get_applicable_policies(
        self,
        data_type: str,
        operation: str,
        context: Dict[str, Any]
    ) -> List[CompliancePolicy]:
        """
        Get applicable compliance policies for a given operation.
        
        Args:
            data_type: Type of data being processed
            operation: Operation being performed
            context: Additional context for policy evaluation
            
        Returns:
            List of applicable compliance policies
        """
        # In a real implementation, this would use more sophisticated matching logic
        # For this implementation, return all policies
        return list(self.policies.values())
    
    def check_compliance(
        self,
        data_type: str,
        operation: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check compliance for a given operation.
        
        Args:
            data_type: Type of data being processed
            operation: Operation being performed
            context: Additional context for compliance check
            
        Returns:
            Compliance check results
        """
        # Get applicable policies
        policies = self.get_applicable_policies(data_type, operation, context)
        
        # Check compliance with each policy
        results = {
            'timestamp': int(time.time()),
            'data_type': data_type,
            'operation': operation,
            'policies': {}
        }
        
        for policy in policies:
            # In a real implementation, this would evaluate each rule in the policy
            # For this implementation, use a simplified approach
            if policy.policy_id in context.get('compliant_policies', []):
                status = 'compliant'
                message = "Policy requirements satisfied"
            elif policy.policy_id in context.get('non_compliant_policies', []):
                status = 'non_compliant'
                message = context.get('reasons', {}).get(policy.policy_id, "Policy requirements not satisfied")
            else:
                status = 'unknown'
                message = "Compliance status unknown"
            
            results['policies'][policy.policy_id] = {
                'status': status,
                'message': message,
                'standard': policy.standard.value
            }
        
        # Determine overall compliance status
        if not policies:
            results['status'] = 'not_applicable'
            results['message'] = "No applicable policies"
        elif all(p['status'] == 'compliant' for p in results['policies'].values()):
            results['status'] = 'compliant'
            results['message'] = "All policy requirements satisfied"
        elif any(p['status'] == 'non_compliant' for p in results['policies'].values()):
            results['status'] = 'non_compliant'
            results['message'] = "One or more policy requirements not satisfied"
        else:
            results['status'] = 'unknown'
            results['message'] = "Compliance status unknown"
        
        return results
    
    def check_retention(self, data_type: str, creation_time: int) -> bool:
        """
        Check if data should be retained based on retention policies.
        
        Args:
            data_type: Type of data
            creation_time: Creation time of the data (Unix time)
            
        Returns:
            True if data should be retained, False if it should be deleted
        """
        if not self.config['retention_policy_enforcement']:
            return True
        
        # Check each retention policy
        for policy in self.retention_policies.values():
            if data_type in policy.data_types:
                return policy.should_retain(data_type, creation_time)
        
        # No applicable policy, retain by default
        return True
    
    def generate_compliance_report(
        self,
        standards: Optional[List[ComplianceStandard]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> ComplianceReport:
        """
        Generate a compliance report.
        
        Args:
            standards: List of standards to include in the report
            start_time: Start time for the report period (Unix time)
            end_time: End time for the report period (Unix time)
            
        Returns:
            Compliance report
        """
        return self.auditor.generate_report(standards, start_time, end_time)
    
    def audit_standard(
        self,
        standard: Union[ComplianceStandard, str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Audit compliance with a specific standard.
        
        Args:
            standard: Compliance standard to audit
            context: Context data for the audit
            
        Returns:
            Audit results
        """
        return self.auditor.audit_compliance(standard, context)
    
    def get_policy(self, policy_id: str) -> Optional[CompliancePolicy]:
        """
        Get a compliance policy by ID.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Compliance policy, or None if not found
        """
        return self.policies.get(policy_id)
    
    def get_retention_policy(self, policy_id: str) -> Optional[DataRetentionPolicy]:
        """
        Get a data retention policy by ID.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Data retention policy, or None if not found
        """
        return self.retention_policies.get(policy_id)
    
    def add_policy(self, policy: CompliancePolicy) -> None:
        """
        Add a compliance policy.
        
        Args:
            policy: Compliance policy to add
        """
        self.policies[policy.policy_id] = policy
        
        # In a real implementation, this would persist to storage
        if self.storage_manager:
            pass  # Store policy
    
    def add_retention_policy(self, policy: DataRetentionPolicy) -> None:
        """
        Add a data retention policy.
        
        Args:
            policy: Data retention policy to add
        """
        self.retention_policies[policy.policy_id] = policy
        
        # In a real implementation, this would persist to storage
        if self.storage_manager:
            pass  # Store policy
    
    def update_policy(self, policy: CompliancePolicy) -> None:
        """
        Update a compliance policy.
        
        Args:
            policy: Updated compliance policy
        """
        if policy.policy_id not in self.policies:
            raise ValueError(f"Policy not found: {policy.policy_id}")
        
        self.policies[policy.policy_id] = policy
        
        # In a real implementation, this would persist to storage
        if self.storage_manager:
            pass  # Store policy
    
    def update_retention_policy(self, policy: DataRetentionPolicy) -> None:
        """
        Update a data retention policy.
        
        Args:
            policy: Updated data retention policy
        """
        if policy.policy_id not in self.retention_policies:
            raise ValueError(f"Retention policy not found: {policy.policy_id}")
        
        self.retention_policies[policy.policy_id] = policy
        
        # In a real implementation, this would persist to storage
        if self.storage_manager:
            pass  # Store policy
    
    def delete_policy(self, policy_id: str) -> None:
        """
        Delete a compliance policy.
        
        Args:
            policy_id: ID of the policy to delete
        """
        if policy_id not in self.policies:
            raise ValueError(f"Policy not found: {policy_id}")
        
        del self.policies[policy_id]
        
        # In a real implementation, this would persist to storage
        if self.storage_manager:
            pass  # Delete policy
    
    def delete_retention_policy(self, policy_id: str) -> None:
        """
        Delete a data retention policy.
        
        Args:
            policy_id: ID of the policy to delete
        """
        if policy_id not in self.retention_policies:
            raise ValueError(f"Retention policy not found: {policy_id}")
        
        del self.retention_policies[policy_id]
        
        # In a real implementation, this would persist to storage
        if self.storage_manager:
            pass  # Delete policy
