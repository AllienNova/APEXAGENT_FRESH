"""
Compliance Reporter for Gemini Live API Integration.

This module implements a comprehensive compliance reporting system that:
1. Tracks compliance with regulatory requirements
2. Generates compliance reports for audits
3. Monitors compliance status in real-time
4. Provides alerts for compliance violations
5. Maintains compliance documentation

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


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"  # General Data Protection Regulation
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    SOC2 = "soc2"  # Service Organization Control 2
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    CCPA = "ccpa"  # California Consumer Privacy Act
    ISO27001 = "iso27001"  # ISO 27001
    NIST = "nist"  # National Institute of Standards and Technology
    FEDRAMP = "fedramp"  # Federal Risk and Authorization Management Program


class ComplianceStatus(Enum):
    """Status of compliance with a requirement."""
    COMPLIANT = "compliant"  # Fully compliant
    PARTIALLY_COMPLIANT = "partially_compliant"  # Partially compliant
    NON_COMPLIANT = "non_compliant"  # Non-compliant
    NOT_APPLICABLE = "not_applicable"  # Not applicable
    UNDER_REVIEW = "under_review"  # Under review


class ComplianceRiskLevel(Enum):
    """Risk level for compliance requirements."""
    LOW = "low"  # Low risk
    MEDIUM = "medium"  # Medium risk
    HIGH = "high"  # High risk
    CRITICAL = "critical"  # Critical risk


@dataclass
class ComplianceRequirement:
    """Compliance requirement definition."""
    requirement_id: str
    framework: ComplianceFramework
    title: str
    description: str
    risk_level: ComplianceRiskLevel
    controls: List[str]
    evidence_required: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceAssessment:
    """Assessment of compliance with a requirement."""
    assessment_id: str
    requirement_id: str
    tenant_id: str
    status: ComplianceStatus
    assessed_at: float
    assessed_by: str
    evidence: List[Dict[str, Any]]
    notes: str
    next_assessment_due: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceViolation:
    """Record of a compliance violation."""
    violation_id: str
    requirement_id: str
    tenant_id: str
    detected_at: float
    detected_by: str
    description: str
    severity: ComplianceRiskLevel
    status: str  # "open", "mitigated", "resolved", "false_positive"
    resolution: Optional[str] = None
    resolved_at: Optional[float] = None
    resolved_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceReporter:
    """
    Compliance Reporter for Gemini Live API Integration.
    
    This class manages compliance tracking, reporting, and alerting.
    """
    
    def __init__(
        self,
        storage_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        notification_handler: Optional[Any] = None,
        audit_logger: Optional[Any] = None
    ):
        """
        Initialize the compliance reporter.
        
        Args:
            storage_provider: Optional provider for persistent storage
            config: Configuration for the compliance reporter
            notification_handler: Optional handler for notifications
            audit_logger: Optional audit logger for compliance events
        """
        self.config = config or self._default_config()
        self.storage_provider = storage_provider
        self.notification_handler = notification_handler
        self.audit_logger = audit_logger
        
        # In-memory storage
        self._requirements: Dict[str, ComplianceRequirement] = {}
        self._assessments: Dict[str, ComplianceAssessment] = {}
        self._violations: Dict[str, ComplianceViolation] = {}
        
        # Load data if storage provider is available
        if self.storage_provider:
            self._load_data()
        else:
            # Load default requirements
            self._load_default_requirements()
        
        # Initialize metrics
        self.metrics = {
            "compliance_by_framework": {},
            "compliance_by_tenant": {},
            "open_violations_by_severity": {s.value: 0 for s in ComplianceRiskLevel},
            "assessments_due_in_30_days": 0
        }
        
        logger.info("Compliance Reporter initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Create default configuration for the compliance reporter."""
        return {
            "assessment_frequency_days": {  # How often to assess compliance
                ComplianceRiskLevel.LOW.value: 365,  # Annual
                ComplianceRiskLevel.MEDIUM.value: 180,  # Semi-annual
                ComplianceRiskLevel.HIGH.value: 90,  # Quarterly
                ComplianceRiskLevel.CRITICAL.value: 30  # Monthly
            },
            "notification_levels": {  # Notification levels by risk level
                ComplianceRiskLevel.LOW.value: ["email"],
                ComplianceRiskLevel.MEDIUM.value: ["email"],
                ComplianceRiskLevel.HIGH.value: ["email", "sms"],
                ComplianceRiskLevel.CRITICAL.value: ["email", "sms", "phone"]
            },
            "violation_escalation_thresholds": {  # Time thresholds for escalation in days
                ComplianceRiskLevel.LOW.value: 30,
                ComplianceRiskLevel.MEDIUM.value: 14,
                ComplianceRiskLevel.HIGH.value: 7,
                ComplianceRiskLevel.CRITICAL.value: 1
            },
            "retention_period_days": 2555,  # 7 years
            "compliance_threshold": 0.8  # 80% compliance threshold
        }
    
    def _load_data(self) -> None:
        """Load data from storage provider."""
        if not self.storage_provider:
            return
        
        try:
            # Load requirements
            requirements = self.storage_provider.get_all("compliance_requirements")
            for req_data in requirements:
                # Convert enum values from strings
                req_data["framework"] = ComplianceFramework(req_data["framework"])
                req_data["risk_level"] = ComplianceRiskLevel(req_data["risk_level"])
                
                # Create requirement object
                requirement = ComplianceRequirement(**req_data)
                self._requirements[requirement.requirement_id] = requirement
            
            # Load assessments
            assessments = self.storage_provider.get_all("compliance_assessments")
            for assessment_data in assessments:
                # Convert enum values from strings
                assessment_data["status"] = ComplianceStatus(assessment_data["status"])
                
                # Create assessment object
                assessment = ComplianceAssessment(**assessment_data)
                self._assessments[assessment.assessment_id] = assessment
            
            # Load violations
            violations = self.storage_provider.get_all("compliance_violations")
            for violation_data in violations:
                # Convert enum values from strings
                violation_data["severity"] = ComplianceRiskLevel(violation_data["severity"])
                
                # Create violation object
                violation = ComplianceViolation(**violation_data)
                self._violations[violation.violation_id] = violation
            
            logger.info("Loaded %d requirements, %d assessments, %d violations from storage",
                       len(self._requirements), len(self._assessments), len(self._violations))
        
        except Exception as e:
            logger.error("Failed to load compliance data: %s", str(e))
            # Load default requirements if loading from storage fails
            self._load_default_requirements()
    
    def _load_default_requirements(self) -> None:
        """Load default compliance requirements."""
        # GDPR requirements
        self._add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Data Processing Agreement",
            description="Ensure a Data Processing Agreement (DPA) is in place with the Gemini API provider.",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["legal_review", "contract_management"],
            evidence_required=["signed_dpa", "legal_review_documentation"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Data Subject Rights",
            description="Implement mechanisms to handle data subject rights requests for data processed through Gemini API.",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["dsr_process", "data_inventory"],
            evidence_required=["dsr_procedure_documentation", "request_handling_logs"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Data Minimization",
            description="Ensure only necessary data is sent to Gemini API and implement data retention policies.",
            risk_level=ComplianceRiskLevel.MEDIUM,
            controls=["data_filtering", "retention_policy"],
            evidence_required=["data_flow_diagrams", "retention_policy_documentation"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Lawful Basis for Processing",
            description="Establish and document lawful basis for processing data through Gemini API.",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["consent_management", "legal_basis_documentation"],
            evidence_required=["consent_records", "legal_basis_documentation"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Data Protection Impact Assessment",
            description="Conduct DPIA for high-risk processing activities using Gemini API.",
            risk_level=ComplianceRiskLevel.MEDIUM,
            controls=["dpia_process", "risk_assessment"],
            evidence_required=["completed_dpia", "risk_mitigation_plan"]
        )
        
        # HIPAA requirements
        self._add_requirement(
            framework=ComplianceFramework.HIPAA,
            title="Business Associate Agreement",
            description="Ensure a Business Associate Agreement (BAA) is in place with the Gemini API provider if PHI is processed.",
            risk_level=ComplianceRiskLevel.CRITICAL,
            controls=["legal_review", "contract_management"],
            evidence_required=["signed_baa", "legal_review_documentation"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.HIPAA,
            title="PHI Identification and Protection",
            description="Implement mechanisms to identify and protect PHI before sending to Gemini API.",
            risk_level=ComplianceRiskLevel.CRITICAL,
            controls=["phi_detection", "data_encryption"],
            evidence_required=["phi_detection_implementation", "encryption_documentation"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.HIPAA,
            title="Access Controls",
            description="Implement appropriate access controls for systems interacting with Gemini API.",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["access_management", "authentication"],
            evidence_required=["access_control_policy", "access_logs"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.HIPAA,
            title="Audit Controls",
            description="Implement audit controls to record and examine activity in systems interacting with Gemini API.",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["audit_logging", "log_review"],
            evidence_required=["audit_log_samples", "log_review_process"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.HIPAA,
            title="Transmission Security",
            description="Implement technical security measures to guard against unauthorized access to PHI being transmitted via Gemini API.",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["encryption", "secure_transmission"],
            evidence_required=["encryption_implementation", "network_security_documentation"]
        )
        
        # SOC2 requirements
        self._add_requirement(
            framework=ComplianceFramework.SOC2,
            title="Vendor Management",
            description="Establish vendor management process for Gemini API provider.",
            risk_level=ComplianceRiskLevel.MEDIUM,
            controls=["vendor_assessment", "contract_review"],
            evidence_required=["vendor_assessment_documentation", "contract_review_documentation"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.SOC2,
            title="Risk Management",
            description="Include Gemini API integration in risk assessment and management processes.",
            risk_level=ComplianceRiskLevel.MEDIUM,
            controls=["risk_assessment", "risk_mitigation"],
            evidence_required=["risk_assessment_documentation", "risk_mitigation_plan"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.SOC2,
            title="Change Management",
            description="Apply change management processes to Gemini API integration changes.",
            risk_level=ComplianceRiskLevel.MEDIUM,
            controls=["change_management", "testing"],
            evidence_required=["change_request_documentation", "test_results"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.SOC2,
            title="Logical Access",
            description="Implement logical access controls for Gemini API integration.",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["access_management", "authentication"],
            evidence_required=["access_control_policy", "access_review_documentation"]
        )
        
        self._add_requirement(
            framework=ComplianceFramework.SOC2,
            title="Monitoring",
            description="Implement monitoring for Gemini API integration.",
            risk_level=ComplianceRiskLevel.MEDIUM,
            controls=["monitoring", "alerting"],
            evidence_required=["monitoring_configuration", "alert_logs"]
        )
        
        logger.info("Loaded %d default compliance requirements", len(self._requirements))
    
    def _add_requirement(
        self,
        framework: ComplianceFramework,
        title: str,
        description: str,
        risk_level: ComplianceRiskLevel,
        controls: List[str],
        evidence_required: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ComplianceRequirement:
        """Add a compliance requirement."""
        # Generate a unique ID
        requirement_id = f"{framework.value}_{len(self._requirements) + 1}"
        
        # Create the requirement
        requirement = ComplianceRequirement(
            requirement_id=requirement_id,
            framework=framework,
            title=title,
            description=description,
            risk_level=risk_level,
            controls=controls,
            evidence_required=evidence_required,
            metadata=metadata or {}
        )
        
        # Store the requirement
        self._requirements[requirement_id] = requirement
        
        return requirement
    
    def _save_data(self, data_type: str, data_id: str, data: Any) -> None:
        """Save data to storage."""
        if not self.storage_provider:
            return
        
        try:
            # Convert enum values to strings for storage
            if data_type == "compliance_requirements":
                data_dict = {
                    **data.__dict__,
                    "framework": data.framework.value,
                    "risk_level": data.risk_level.value
                }
            elif data_type == "compliance_assessments":
                data_dict = {
                    **data.__dict__,
                    "status": data.status.value
                }
            elif data_type == "compliance_violations":
                data_dict = {
                    **data.__dict__,
                    "severity": data.severity.value
                }
            else:
                data_dict = data.__dict__
            
            # Save to storage
            self.storage_provider.put(
                data_type,
                data_id,
                data_dict
            )
            
            logger.debug("Saved %s %s", data_type, data_id)
        
        except Exception as e:
            logger.error("Failed to save %s: %s", data_type, str(e))
    
    def _log_compliance_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        tenant_id: Optional[str] = None,
        user_id: str = "system"
    ) -> None:
        """Log a compliance-related event."""
        if not self.audit_logger:
            return
        
        # Create audit event
        self.audit_logger.log_security_event(
            event_type=f"COMPLIANCE_{event_type}",
            source="compliance_reporter",
            details=details,
            severity="info",
            user_id=user_id,
            tenant_id=tenant_id or "system"
        )
    
    def _send_notification(
        self,
        notification_type: str,
        risk_level: ComplianceRiskLevel,
        message: str,
        recipients: List[str],
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send a notification about a compliance issue."""
        if not self.notification_handler:
            return
        
        try:
            # Get notification channels based on risk level
            channels = self.config["notification_levels"].get(risk_level.value, ["email"])
            
            # Prepare notification data
            notification = {
                "channels": channels,
                "notification_type": notification_type,
                "risk_level": risk_level.value,
                "message": message,
                "recipients": recipients,
                "details": details or {},
                "timestamp": time.time()
            }
            
            # Send notification
            self.notification_handler(notification)
            
            logger.debug("Sent %s notification with risk level %s to %s",
                        notification_type, risk_level.value, recipients)
        
        except Exception as e:
            logger.error("Failed to send notification: %s", str(e))
    
    def _update_metrics(self) -> None:
        """Update compliance metrics."""
        # Reset metrics
        self.metrics["compliance_by_framework"] = {}
        self.metrics["compliance_by_tenant"] = {}
        self.metrics["open_violations_by_severity"] = {s.value: 0 for s in ComplianceRiskLevel}
        self.metrics["assessments_due_in_30_days"] = 0
        
        # Count open violations by severity
        for violation in self._violations.values():
            if violation.status == "open":
                self.metrics["open_violations_by_severity"][violation.severity.value] += 1
        
        # Count assessments due in next 30 days
        now = time.time()
        thirty_days_from_now = now + (30 * 24 * 60 * 60)
        for assessment in self._assessments.values():
            if assessment.next_assessment_due and assessment.next_assessment_due <= thirty_days_from_now:
                self.metrics["assessments_due_in_30_days"] += 1
        
        # Calculate compliance by framework
        framework_requirements = {}
        framework_compliant = {}
        
        for req in self._requirements.values():
            framework = req.framework.value
            if framework not in framework_requirements:
                framework_requirements[framework] = 0
                framework_compliant[framework] = 0
            framework_requirements[framework] += 1
        
        # Find latest assessment for each requirement by tenant
        latest_assessments = {}
        for assessment in self._assessments.values():
            key = f"{assessment.requirement_id}_{assessment.tenant_id}"
            if key not in latest_assessments or assessment.assessed_at > latest_assessments[key].assessed_at:
                latest_assessments[key] = assessment
        
        # Count compliant requirements by framework and tenant
        tenant_requirements = {}
        tenant_compliant = {}
        
        for key, assessment in latest_assessments.items():
            requirement_id, tenant_id = key.split("_", 1)
            requirement = self._requirements.get(requirement_id)
            if not requirement:
                continue
            
            framework = requirement.framework.value
            
            # Initialize tenant counters if needed
            if tenant_id not in tenant_requirements:
                tenant_requirements[tenant_id] = 0
                tenant_compliant[tenant_id] = 0
            
            tenant_requirements[tenant_id] += 1
            
            # Count compliant assessments
            if assessment.status == ComplianceStatus.COMPLIANT:
                framework_compliant[framework] = framework_compliant.get(framework, 0) + 1
                tenant_compliant[tenant_id] += 1
        
        # Calculate compliance percentages by framework
        for framework, count in framework_requirements.items():
            if count > 0:
                compliance_rate = framework_compliant.get(framework, 0) / count
                self.metrics["compliance_by_framework"][framework] = compliance_rate
        
        # Calculate compliance percentages by tenant
        for tenant_id, count in tenant_requirements.items():
            if count > 0:
                compliance_rate = tenant_compliant.get(tenant_id, 0) / count
                self.metrics["compliance_by_tenant"][tenant_id] = compliance_rate
    
    def add_requirement(
        self,
        framework: ComplianceFramework,
        title: str,
        description: str,
        risk_level: ComplianceRiskLevel,
        controls: List[str],
        evidence_required: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "system"
    ) -> ComplianceRequirement:
        """
        Add a new compliance requirement.
        
        Args:
            framework: Compliance framework
            title: Title of the requirement
            description: Description of the requirement
            risk_level: Risk level of the requirement
            controls: List of controls for the requirement
            evidence_required: List of evidence required for the requirement
            metadata: Additional metadata for the requirement
            user_id: ID of the user adding the requirement
            
        Returns:
            The created requirement
        """
        # Create the requirement
        requirement = self._add_requirement(
            framework=framework,
            title=title,
            description=description,
            risk_level=risk_level,
            controls=controls,
            evidence_required=evidence_required,
            metadata=metadata
        )
        
        # Save to persistent storage
        self._save_data("compliance_requirements", requirement.requirement_id, requirement)
        
        # Log the event
        self._log_compliance_event(
            "REQUIREMENT_ADDED",
            {
                "requirement_id": requirement.requirement_id,
                "framework": framework.value,
                "title": title,
                "risk_level": risk_level.value,
                "added_by": user_id
            },
            user_id=user_id
        )
        
        return requirement
    
    def update_requirement(
        self,
        requirement_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        risk_level: Optional[ComplianceRiskLevel] = None,
        controls: Optional[List[str]] = None,
        evidence_required: Optional[List[str]] = None,
        metadata_updates: Optional[Dict[str, Any]] = None,
        user_id: str = "system"
    ) -> Optional[ComplianceRequirement]:
        """
        Update an existing compliance requirement.
        
        Args:
            requirement_id: ID of the requirement to update
            title: Optional new title
            description: Optional new description
            risk_level: Optional new risk level
            controls: Optional new controls
            evidence_required: Optional new evidence required
            metadata_updates: Optional metadata updates
            user_id: ID of the user updating the requirement
            
        Returns:
            The updated requirement, or None if not found
        """
        # Get the requirement
        requirement = self._requirements.get(requirement_id)
        if not requirement:
            logger.warning("Attempted to update non-existent requirement: %s", requirement_id)
            return None
        
        # Track changes for logging
        changes = {}
        
        # Update fields if provided
        if title and title != requirement.title:
            changes["title"] = {"old": requirement.title, "new": title}
            requirement.title = title
        
        if description and description != requirement.description:
            changes["description"] = {"old": requirement.description, "new": description}
            requirement.description = description
        
        if risk_level and risk_level != requirement.risk_level:
            changes["risk_level"] = {"old": requirement.risk_level.value, "new": risk_level.value}
            requirement.risk_level = risk_level
        
        if controls:
            changes["controls"] = {"old": requirement.controls, "new": controls}
            requirement.controls = controls
        
        if evidence_required:
            changes["evidence_required"] = {"old": requirement.evidence_required, "new": evidence_required}
            requirement.evidence_required = evidence_required
        
        # Update metadata if provided
        if metadata_updates:
            for key, value in metadata_updates.items():
                requirement.metadata[key] = value
            changes["metadata_updates"] = list(metadata_updates.keys())
        
        # If changes were made, save and log
        if changes:
            # Save to persistent storage
            self._save_data("compliance_requirements", requirement_id, requirement)
            
            # Log the update
            self._log_compliance_event(
                "REQUIREMENT_UPDATED",
                {
                    "requirement_id": requirement_id,
                    "framework": requirement.framework.value,
                    "changes": changes,
                    "updated_by": user_id
                },
                user_id=user_id
            )
        
        return requirement
    
    def create_assessment(
        self,
        requirement_id: str,
        tenant_id: str,
        status: ComplianceStatus,
        assessed_by: str,
        evidence: List[Dict[str, Any]],
        notes: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ComplianceAssessment]:
        """
        Create a new compliance assessment.
        
        Args:
            requirement_id: ID of the requirement being assessed
            tenant_id: ID of the tenant
            status: Compliance status
            assessed_by: ID of the user performing the assessment
            evidence: List of evidence for the assessment
            notes: Notes for the assessment
            metadata: Additional metadata for the assessment
            
        Returns:
            The created assessment, or None if requirement not found
        """
        # Check if requirement exists
        requirement = self._requirements.get(requirement_id)
        if not requirement:
            logger.warning("Attempted to create assessment for non-existent requirement: %s", requirement_id)
            return None
        
        # Generate a unique ID for the assessment
        assessment_id = str(uuid.uuid4())
        
        # Calculate next assessment due date based on risk level
        now = time.time()
        days = self.config["assessment_frequency_days"].get(requirement.risk_level.value, 365)
        next_assessment_due = now + (days * 24 * 60 * 60)
        
        # Create the assessment
        assessment = ComplianceAssessment(
            assessment_id=assessment_id,
            requirement_id=requirement_id,
            tenant_id=tenant_id,
            status=status,
            assessed_at=now,
            assessed_by=assessed_by,
            evidence=evidence,
            notes=notes,
            next_assessment_due=next_assessment_due,
            metadata=metadata or {}
        )
        
        # Store the assessment
        self._assessments[assessment_id] = assessment
        
        # Save to persistent storage
        self._save_data("compliance_assessments", assessment_id, assessment)
        
        # Log the assessment
        self._log_compliance_event(
            "ASSESSMENT_CREATED",
            {
                "assessment_id": assessment_id,
                "requirement_id": requirement_id,
                "framework": requirement.framework.value,
                "status": status.value,
                "assessed_by": assessed_by
            },
            tenant_id=tenant_id,
            user_id=assessed_by
        )
        
        # Send notification if non-compliant
        if status != ComplianceStatus.COMPLIANT and status != ComplianceStatus.NOT_APPLICABLE:
            self._send_notification(
                "non_compliant_assessment",
                requirement.risk_level,
                f"Non-compliant assessment for {requirement.title}",
                ["compliance_team"],
                {
                    "requirement_id": requirement_id,
                    "requirement_title": requirement.title,
                    "framework": requirement.framework.value,
                    "tenant_id": tenant_id,
                    "status": status.value,
                    "notes": notes
                }
            )
        
        # Update metrics
        self._update_metrics()
        
        return assessment
    
    def record_violation(
        self,
        requirement_id: str,
        tenant_id: str,
        description: str,
        detected_by: str,
        severity: Optional[ComplianceRiskLevel] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ComplianceViolation]:
        """
        Record a compliance violation.
        
        Args:
            requirement_id: ID of the requirement being violated
            tenant_id: ID of the tenant
            description: Description of the violation
            detected_by: ID of the user or system that detected the violation
            severity: Optional severity override (defaults to requirement's risk level)
            metadata: Additional metadata for the violation
            
        Returns:
            The created violation, or None if requirement not found
        """
        # Check if requirement exists
        requirement = self._requirements.get(requirement_id)
        if not requirement:
            logger.warning("Attempted to record violation for non-existent requirement: %s", requirement_id)
            return None
        
        # Use requirement's risk level if severity not provided
        if severity is None:
            severity = requirement.risk_level
        
        # Generate a unique ID for the violation
        violation_id = str(uuid.uuid4())
        
        # Create the violation
        violation = ComplianceViolation(
            violation_id=violation_id,
            requirement_id=requirement_id,
            tenant_id=tenant_id,
            detected_at=time.time(),
            detected_by=detected_by,
            description=description,
            severity=severity,
            status="open",
            metadata=metadata or {}
        )
        
        # Store the violation
        self._violations[violation_id] = violation
        
        # Save to persistent storage
        self._save_data("compliance_violations", violation_id, violation)
        
        # Log the violation
        self._log_compliance_event(
            "VIOLATION_RECORDED",
            {
                "violation_id": violation_id,
                "requirement_id": requirement_id,
                "framework": requirement.framework.value,
                "severity": severity.value,
                "detected_by": detected_by,
                "description": description
            },
            tenant_id=tenant_id,
            user_id=detected_by
        )
        
        # Send notification
        self._send_notification(
            "compliance_violation",
            severity,
            f"Compliance violation for {requirement.title}",
            ["compliance_team", "security_team"],
            {
                "violation_id": violation_id,
                "requirement_id": requirement_id,
                "requirement_title": requirement.title,
                "framework": requirement.framework.value,
                "tenant_id": tenant_id,
                "description": description
            }
        )
        
        # Update metrics
        self._update_metrics()
        
        return violation
    
    def update_violation(
        self,
        violation_id: str,
        status: Optional[str] = None,
        resolution: Optional[str] = None,
        resolved_by: Optional[str] = None,
        metadata_updates: Optional[Dict[str, Any]] = None,
        user_id: str = "system"
    ) -> Optional[ComplianceViolation]:
        """
        Update a compliance violation.
        
        Args:
            violation_id: ID of the violation to update
            status: Optional new status
            resolution: Optional resolution description
            resolved_by: Optional ID of the user resolving the violation
            metadata_updates: Optional metadata updates
            user_id: ID of the user updating the violation
            
        Returns:
            The updated violation, or None if not found
        """
        # Get the violation
        violation = self._violations.get(violation_id)
        if not violation:
            logger.warning("Attempted to update non-existent violation: %s", violation_id)
            return None
        
        # Track changes for logging
        changes = {}
        
        # Update status if provided
        if status and status != violation.status:
            changes["status"] = {"old": violation.status, "new": status}
            violation.status = status
            
            # If resolving the violation, set resolved_at
            if status in ["resolved", "mitigated", "false_positive"] and not violation.resolved_at:
                violation.resolved_at = time.time()
                changes["resolved_at"] = violation.resolved_at
        
        # Update resolution if provided
        if resolution and violation.resolution != resolution:
            changes["resolution"] = {"old": violation.resolution, "new": resolution}
            violation.resolution = resolution
        
        # Update resolved_by if provided
        if resolved_by and violation.resolved_by != resolved_by:
            changes["resolved_by"] = {"old": violation.resolved_by, "new": resolved_by}
            violation.resolved_by = resolved_by
        
        # Update metadata if provided
        if metadata_updates:
            for key, value in metadata_updates.items():
                violation.metadata[key] = value
            changes["metadata_updates"] = list(metadata_updates.keys())
        
        # If changes were made, save and log
        if changes:
            # Save to persistent storage
            self._save_data("compliance_violations", violation_id, violation)
            
            # Get the requirement for logging
            requirement = self._requirements.get(violation.requirement_id)
            framework = requirement.framework.value if requirement else "unknown"
            
            # Log the update
            self._log_compliance_event(
                "VIOLATION_UPDATED",
                {
                    "violation_id": violation_id,
                    "requirement_id": violation.requirement_id,
                    "framework": framework,
                    "changes": changes,
                    "updated_by": user_id
                },
                tenant_id=violation.tenant_id,
                user_id=user_id
            )
            
            # Send notification if resolved
            if "status" in changes and violation.status in ["resolved", "mitigated"]:
                severity = violation.severity
                self._send_notification(
                    "violation_resolved",
                    severity,
                    f"Compliance violation resolved: {violation.description}",
                    ["compliance_team"],
                    {
                        "violation_id": violation_id,
                        "requirement_id": violation.requirement_id,
                        "status": violation.status,
                        "resolution": violation.resolution,
                        "resolved_by": violation.resolved_by
                    }
                )
            
            # Update metrics
            self._update_metrics()
        
        return violation
    
    def get_requirement(self, requirement_id: str) -> Optional[ComplianceRequirement]:
        """
        Get a compliance requirement by ID.
        
        Args:
            requirement_id: ID of the requirement
            
        Returns:
            The requirement, or None if not found
        """
        return self._requirements.get(requirement_id)
    
    def get_requirements(
        self,
        framework: Optional[ComplianceFramework] = None,
        risk_level: Optional[ComplianceRiskLevel] = None
    ) -> List[ComplianceRequirement]:
        """
        Get compliance requirements matching the specified filters.
        
        Args:
            framework: Optional framework filter
            risk_level: Optional risk level filter
            
        Returns:
            List of matching requirements
        """
        # Start with all requirements
        requirements = list(self._requirements.values())
        
        # Apply filters
        if framework:
            requirements = [r for r in requirements if r.framework == framework]
        
        if risk_level:
            requirements = [r for r in requirements if r.risk_level == risk_level]
        
        # Sort by ID
        requirements.sort(key=lambda r: r.requirement_id)
        
        return requirements
    
    def get_assessment(self, assessment_id: str) -> Optional[ComplianceAssessment]:
        """
        Get a compliance assessment by ID.
        
        Args:
            assessment_id: ID of the assessment
            
        Returns:
            The assessment, or None if not found
        """
        return self._assessments.get(assessment_id)
    
    def get_assessments(
        self,
        requirement_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        status: Optional[ComplianceStatus] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[ComplianceAssessment]:
        """
        Get compliance assessments matching the specified filters.
        
        Args:
            requirement_id: Optional requirement ID filter
            tenant_id: Optional tenant ID filter
            status: Optional status filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of matching assessments
        """
        # Start with all assessments
        assessments = list(self._assessments.values())
        
        # Apply filters
        if requirement_id:
            assessments = [a for a in assessments if a.requirement_id == requirement_id]
        
        if tenant_id:
            assessments = [a for a in assessments if a.tenant_id == tenant_id]
        
        if status:
            assessments = [a for a in assessments if a.status == status]
        
        if start_time:
            assessments = [a for a in assessments if a.assessed_at >= start_time]
        
        if end_time:
            assessments = [a for a in assessments if a.assessed_at <= end_time]
        
        # Sort by assessed time (newest first)
        assessments.sort(key=lambda a: a.assessed_at, reverse=True)
        
        return assessments
    
    def get_latest_assessment(
        self,
        requirement_id: str,
        tenant_id: str
    ) -> Optional[ComplianceAssessment]:
        """
        Get the latest assessment for a requirement and tenant.
        
        Args:
            requirement_id: ID of the requirement
            tenant_id: ID of the tenant
            
        Returns:
            The latest assessment, or None if not found
        """
        # Get all assessments for this requirement and tenant
        assessments = self.get_assessments(requirement_id=requirement_id, tenant_id=tenant_id)
        
        # Return the first one (already sorted by assessed_at in descending order)
        return assessments[0] if assessments else None
    
    def get_violation(self, violation_id: str) -> Optional[ComplianceViolation]:
        """
        Get a compliance violation by ID.
        
        Args:
            violation_id: ID of the violation
            
        Returns:
            The violation, or None if not found
        """
        return self._violations.get(violation_id)
    
    def get_violations(
        self,
        requirement_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[ComplianceRiskLevel] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[ComplianceViolation]:
        """
        Get compliance violations matching the specified filters.
        
        Args:
            requirement_id: Optional requirement ID filter
            tenant_id: Optional tenant ID filter
            status: Optional status filter
            severity: Optional severity filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of matching violations
        """
        # Start with all violations
        violations = list(self._violations.values())
        
        # Apply filters
        if requirement_id:
            violations = [v for v in violations if v.requirement_id == requirement_id]
        
        if tenant_id:
            violations = [v for v in violations if v.tenant_id == tenant_id]
        
        if status:
            violations = [v for v in violations if v.status == status]
        
        if severity:
            violations = [v for v in violations if v.severity == severity]
        
        if start_time:
            violations = [v for v in violations if v.detected_at >= start_time]
        
        if end_time:
            violations = [v for v in violations if v.detected_at <= end_time]
        
        # Sort by detected time (newest first)
        violations.sort(key=lambda v: v.detected_at, reverse=True)
        
        return violations
    
    def generate_compliance_report(
        self,
        tenant_id: Optional[str] = None,
        framework: Optional[ComplianceFramework] = None,
        include_evidence: bool = False,
        include_violations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report.
        
        Args:
            tenant_id: Optional tenant ID to filter by
            framework: Optional framework to filter by
            include_evidence: Whether to include evidence details
            include_violations: Whether to include violations
            
        Returns:
            Compliance report
        """
        # Get requirements
        requirements = self.get_requirements(framework=framework)
        
        # Get latest assessment for each requirement
        requirement_assessments = {}
        for req in requirements:
            if tenant_id:
                # Get latest assessment for this tenant
                assessment = self.get_latest_assessment(req.requirement_id, tenant_id)
                if assessment:
                    requirement_assessments[req.requirement_id] = [assessment]
            else:
                # Get latest assessment for each tenant
                assessments = []
                tenant_ids = set(a.tenant_id for a in self._assessments.values() if a.requirement_id == req.requirement_id)
                for tid in tenant_ids:
                    assessment = self.get_latest_assessment(req.requirement_id, tid)
                    if assessment:
                        assessments.append(assessment)
                if assessments:
                    requirement_assessments[req.requirement_id] = assessments
        
        # Get violations
        violations_by_requirement = {}
        if include_violations:
            violations = self.get_violations(tenant_id=tenant_id)
            for violation in violations:
                if violation.requirement_id not in violations_by_requirement:
                    violations_by_requirement[violation.requirement_id] = []
                violations_by_requirement[violation.requirement_id].append({
                    "violation_id": violation.violation_id,
                    "description": violation.description,
                    "severity": violation.severity.value,
                    "status": violation.status,
                    "detected_at": violation.detected_at,
                    "resolved_at": violation.resolved_at,
                    "resolution": violation.resolution
                })
        
        # Calculate compliance status
        total_requirements = len(requirements)
        compliant_requirements = 0
        partially_compliant_requirements = 0
        non_compliant_requirements = 0
        not_applicable_requirements = 0
        under_review_requirements = 0
        
        # Prepare report data
        report_data = []
        for req in requirements:
            assessments = requirement_assessments.get(req.requirement_id, [])
            
            # Determine overall status
            if not assessments:
                status = "not_assessed"
            else:
                # Count statuses
                status_counts = {}
                for assessment in assessments:
                    status_counts[assessment.status.value] = status_counts.get(assessment.status.value, 0) + 1
                
                # Determine predominant status
                if status_counts.get(ComplianceStatus.COMPLIANT.value, 0) == len(assessments):
                    status = ComplianceStatus.COMPLIANT.value
                    compliant_requirements += 1
                elif status_counts.get(ComplianceStatus.NON_COMPLIANT.value, 0) > 0:
                    status = ComplianceStatus.NON_COMPLIANT.value
                    non_compliant_requirements += 1
                elif status_counts.get(ComplianceStatus.PARTIALLY_COMPLIANT.value, 0) > 0:
                    status = ComplianceStatus.PARTIALLY_COMPLIANT.value
                    partially_compliant_requirements += 1
                elif status_counts.get(ComplianceStatus.NOT_APPLICABLE.value, 0) == len(assessments):
                    status = ComplianceStatus.NOT_APPLICABLE.value
                    not_applicable_requirements += 1
                elif status_counts.get(ComplianceStatus.UNDER_REVIEW.value, 0) > 0:
                    status = ComplianceStatus.UNDER_REVIEW.value
                    under_review_requirements += 1
                else:
                    status = "mixed"
                    partially_compliant_requirements += 1
            
            # Prepare requirement data
            requirement_data = {
                "requirement_id": req.requirement_id,
                "framework": req.framework.value,
                "title": req.title,
                "description": req.description,
                "risk_level": req.risk_level.value,
                "controls": req.controls,
                "status": status,
                "assessments": []
            }
            
            # Add assessment data
            for assessment in assessments:
                assessment_data = {
                    "assessment_id": assessment.assessment_id,
                    "tenant_id": assessment.tenant_id,
                    "status": assessment.status.value,
                    "assessed_at": assessment.assessed_at,
                    "assessed_by": assessment.assessed_by,
                    "notes": assessment.notes,
                    "next_assessment_due": assessment.next_assessment_due
                }
                
                # Include evidence if requested
                if include_evidence:
                    assessment_data["evidence"] = assessment.evidence
                
                requirement_data["assessments"].append(assessment_data)
            
            # Add violations if requested
            if include_violations:
                requirement_data["violations"] = violations_by_requirement.get(req.requirement_id, [])
            
            report_data.append(requirement_data)
        
        # Calculate compliance rate
        assessed_requirements = compliant_requirements + partially_compliant_requirements + non_compliant_requirements
        compliance_rate = 0
        if assessed_requirements > 0:
            compliance_rate = (compliant_requirements + (partially_compliant_requirements * 0.5)) / assessed_requirements
        
        # Create the report
        report = {
            "generated_at": time.time(),
            "tenant_id": tenant_id,
            "framework": framework.value if framework else "all",
            "summary": {
                "total_requirements": total_requirements,
                "compliant_requirements": compliant_requirements,
                "partially_compliant_requirements": partially_compliant_requirements,
                "non_compliant_requirements": non_compliant_requirements,
                "not_applicable_requirements": not_applicable_requirements,
                "under_review_requirements": under_review_requirements,
                "compliance_rate": compliance_rate,
                "compliance_threshold": self.config["compliance_threshold"],
                "compliant": compliance_rate >= self.config["compliance_threshold"]
            },
            "requirements": report_data
        }
        
        # Log report generation
        self._log_compliance_event(
            "REPORT_GENERATED",
            {
                "tenant_id": tenant_id,
                "framework": framework.value if framework else "all",
                "compliance_rate": compliance_rate,
                "compliant": compliance_rate >= self.config["compliance_threshold"]
            },
            tenant_id=tenant_id
        )
        
        return report
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current compliance metrics."""
        # Update metrics before returning
        self._update_metrics()
        return self.metrics.copy()
    
    def check_assessments_due(self) -> List[Dict[str, Any]]:
        """
        Check for assessments that are due or overdue.
        
        Returns:
            List of due assessments
        """
        now = time.time()
        due_assessments = []
        
        # Find latest assessment for each requirement by tenant
        latest_assessments = {}
        for assessment in self._assessments.values():
            key = f"{assessment.requirement_id}_{assessment.tenant_id}"
            if key not in latest_assessments or assessment.assessed_at > latest_assessments[key].assessed_at:
                latest_assessments[key] = assessment
        
        # Check if any are due
        for key, assessment in latest_assessments.items():
            if assessment.next_assessment_due and assessment.next_assessment_due <= now:
                requirement = self._requirements.get(assessment.requirement_id)
                if not requirement:
                    continue
                
                days_overdue = (now - assessment.next_assessment_due) / (24 * 60 * 60)
                
                due_assessments.append({
                    "requirement_id": assessment.requirement_id,
                    "requirement_title": requirement.title,
                    "framework": requirement.framework.value,
                    "risk_level": requirement.risk_level.value,
                    "tenant_id": assessment.tenant_id,
                    "assessment_id": assessment.assessment_id,
                    "last_assessed_at": assessment.assessed_at,
                    "next_assessment_due": assessment.next_assessment_due,
                    "days_overdue": days_overdue
                })
        
        # Sort by days overdue (most overdue first)
        due_assessments.sort(key=lambda a: a["days_overdue"], reverse=True)
        
        return due_assessments
    
    def check_escalations_needed(self) -> List[Dict[str, Any]]:
        """
        Check for violations that need escalation.
        
        Returns:
            List of violations needing escalation
        """
        now = time.time()
        escalations_needed = []
        
        # Check open violations
        for violation in self._violations.values():
            if violation.status != "open":
                continue
            
            requirement = self._requirements.get(violation.requirement_id)
            if not requirement:
                continue
            
            # Calculate days open
            days_open = (now - violation.detected_at) / (24 * 60 * 60)
            
            # Check if escalation threshold exceeded
            threshold_days = self.config["violation_escalation_thresholds"].get(violation.severity.value, 30)
            if days_open > threshold_days:
                escalations_needed.append({
                    "violation_id": violation.violation_id,
                    "requirement_id": violation.requirement_id,
                    "requirement_title": requirement.title,
                    "framework": requirement.framework.value,
                    "severity": violation.severity.value,
                    "tenant_id": violation.tenant_id,
                    "detected_at": violation.detected_at,
                    "days_open": days_open,
                    "threshold_days": threshold_days,
                    "days_over_threshold": days_open - threshold_days
                })
        
        # Sort by days over threshold (most over first)
        escalations_needed.sort(key=lambda v: v["days_over_threshold"], reverse=True)
        
        return escalations_needed
