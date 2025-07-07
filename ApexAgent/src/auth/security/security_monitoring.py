"""
Security Monitoring and Compliance module for ApexAgent.

This module provides comprehensive audit logging, compliance reporting,
and security analytics with anomaly detection capabilities.
"""

import os
import json
import uuid
import logging
import hashlib
import secrets
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Union

from src.core.error_handling.errors import SecurityError, ConfigurationError
from src.core.event_system.event_manager import EventManager

logger = logging.getLogger(__name__)

class AuditLog:
    """
    Represents an audit log entry.
    """
    def __init__(
        self,
        log_id: str,
        action: str,
        actor_id: str,
        actor_type: str,  # "user", "system", "plugin", "admin"
        resource_type: str,
        resource_id: Optional[str],
        result: str,  # "success", "failure", "error", "warning"
        description: str,
        timestamp: datetime = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.log_id = log_id or str(uuid.uuid4())
        self.action = action
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.result = result
        self.description = description
        self.timestamp = timestamp or datetime.now()
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.session_id = session_id
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert log entry to dictionary representation.
        
        Returns:
            Dictionary representation of the log entry
        """
        return {
            "log_id": self.log_id,
            "action": self.action,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "result": self.result,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, log_dict: Dict[str, Any]) -> 'AuditLog':
        """
        Create a log entry from dictionary representation.
        
        Args:
            log_dict: Dictionary representation of the log entry
            
        Returns:
            AuditLog object
        """
        timestamp = log_dict.get("timestamp")
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
            
        return cls(
            log_id=log_dict.get("log_id"),
            action=log_dict["action"],
            actor_id=log_dict["actor_id"],
            actor_type=log_dict["actor_type"],
            resource_type=log_dict["resource_type"],
            resource_id=log_dict.get("resource_id"),
            result=log_dict["result"],
            description=log_dict["description"],
            timestamp=timestamp,
            ip_address=log_dict.get("ip_address"),
            user_agent=log_dict.get("user_agent"),
            session_id=log_dict.get("session_id"),
            metadata=log_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"AuditLog(id={self.log_id}, action={self.action}, result={self.result})"


class ComplianceRequirement:
    """
    Represents a compliance requirement.
    """
    def __init__(
        self,
        requirement_id: str,
        name: str,
        description: str,
        standard: str,  # "GDPR", "SOC2", "HIPAA", "PCI-DSS", etc.
        category: str,
        verification_method: str,  # "automated", "manual", "hybrid"
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.requirement_id = requirement_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.standard = standard
        self.category = category
        self.verification_method = verification_method
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert requirement to dictionary representation.
        
        Returns:
            Dictionary representation of the requirement
        """
        return {
            "requirement_id": self.requirement_id,
            "name": self.name,
            "description": self.description,
            "standard": self.standard,
            "category": self.category,
            "verification_method": self.verification_method,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, requirement_dict: Dict[str, Any]) -> 'ComplianceRequirement':
        """
        Create a requirement from dictionary representation.
        
        Args:
            requirement_dict: Dictionary representation of the requirement
            
        Returns:
            ComplianceRequirement object
        """
        return cls(
            requirement_id=requirement_dict.get("requirement_id"),
            name=requirement_dict["name"],
            description=requirement_dict["description"],
            standard=requirement_dict["standard"],
            category=requirement_dict["category"],
            verification_method=requirement_dict["verification_method"],
            is_active=requirement_dict.get("is_active", True),
            metadata=requirement_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"ComplianceRequirement(id={self.requirement_id}, name={self.name}, standard={self.standard})"


class ComplianceCheck:
    """
    Represents a compliance check.
    """
    def __init__(
        self,
        check_id: str,
        requirement_id: str,
        name: str,
        description: str,
        check_type: str,  # "log_analysis", "configuration", "policy", "test"
        check_function: Callable[[], Tuple[bool, str, Dict[str, Any]]],
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.check_id = check_id or str(uuid.uuid4())
        self.requirement_id = requirement_id
        self.name = name
        self.description = description
        self.check_type = check_type
        self.check_function = check_function
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert check to dictionary representation.
        
        Returns:
            Dictionary representation of the check
        """
        return {
            "check_id": self.check_id,
            "requirement_id": self.requirement_id,
            "name": self.name,
            "description": self.description,
            "check_type": self.check_type,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    def run(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Run the compliance check.
        
        Returns:
            Tuple of (passed, details, additional_data)
        """
        try:
            return self.check_function()
        except Exception as e:
            logger.error(f"Error running compliance check {self.check_id}: {e}")
            return False, f"Error: {str(e)}", {"error": str(e)}
    
    def __str__(self) -> str:
        return f"ComplianceCheck(id={self.check_id}, name={self.name}, requirement={self.requirement_id})"


class ComplianceReport:
    """
    Represents a compliance report.
    """
    def __init__(
        self,
        report_id: str,
        name: str,
        description: str,
        standards: List[str],
        generated_at: datetime = None,
        generated_by: Optional[str] = None,
        results: Dict[str, Dict[str, Any]] = None,
        summary: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ):
        self.report_id = report_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.standards = standards
        self.generated_at = generated_at or datetime.now()
        self.generated_by = generated_by
        self.results = results or {}
        self.summary = summary or {}
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary representation.
        
        Returns:
            Dictionary representation of the report
        """
        return {
            "report_id": self.report_id,
            "name": self.name,
            "description": self.description,
            "standards": self.standards,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "generated_by": self.generated_by,
            "results": self.results,
            "summary": self.summary,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, report_dict: Dict[str, Any]) -> 'ComplianceReport':
        """
        Create a report from dictionary representation.
        
        Args:
            report_dict: Dictionary representation of the report
            
        Returns:
            ComplianceReport object
        """
        generated_at = report_dict.get("generated_at")
        if generated_at and isinstance(generated_at, str):
            generated_at = datetime.fromisoformat(generated_at)
            
        return cls(
            report_id=report_dict.get("report_id"),
            name=report_dict["name"],
            description=report_dict["description"],
            standards=report_dict["standards"],
            generated_at=generated_at,
            generated_by=report_dict.get("generated_by"),
            results=report_dict.get("results", {}),
            summary=report_dict.get("summary", {}),
            metadata=report_dict.get("metadata", {})
        )
    
    def add_result(self, check_id: str, result: Dict[str, Any]) -> None:
        """
        Add a check result to the report.
        
        Args:
            check_id: ID of the check
            result: Result data
        """
        self.results[check_id] = result
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the report.
        
        Returns:
            Summary data
        """
        total_checks = len(self.results)
        passed_checks = sum(1 for result in self.results.values() if result.get("passed", False))
        failed_checks = total_checks - passed_checks
        
        # Group by standard
        standard_results = {}
        for check_id, result in self.results.items():
            standard = result.get("standard")
            if standard:
                if standard not in standard_results:
                    standard_results[standard] = {"total": 0, "passed": 0, "failed": 0}
                standard_results[standard]["total"] += 1
                if result.get("passed", False):
                    standard_results[standard]["passed"] += 1
                else:
                    standard_results[standard]["failed"] += 1
        
        # Calculate compliance percentage
        compliance_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        summary = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "compliance_percentage": compliance_percentage,
            "standard_results": standard_results
        }
        
        self.summary = summary
        return summary
    
    def __str__(self) -> str:
        return f"ComplianceReport(id={self.report_id}, name={self.name}, standards={self.standards})"


class AnomalyDetector:
    """
    Base class for anomaly detection.
    """
    def __init__(
        self,
        detector_id: str,
        name: str,
        description: str,
        data_source: str,
        sensitivity: float = 1.0,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.detector_id = detector_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.data_source = data_source
        self.sensitivity = sensitivity
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert detector to dictionary representation.
        
        Returns:
            Dictionary representation of the detector
        """
        return {
            "detector_id": self.detector_id,
            "name": self.name,
            "description": self.description,
            "data_source": self.data_source,
            "sensitivity": self.sensitivity,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    def detect(self, data: Any) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Detect anomalies in data.
        
        Args:
            data: Data to analyze
            
        Returns:
            Tuple of (is_anomaly, anomaly_score, details)
        """
        raise NotImplementedError("Subclasses must implement detect method")
    
    def __str__(self) -> str:
        return f"AnomalyDetector(id={self.detector_id}, name={self.name})"


class StatisticalAnomalyDetector(AnomalyDetector):
    """
    Statistical anomaly detector using z-scores.
    """
    def __init__(
        self,
        detector_id: str,
        name: str,
        description: str,
        data_source: str,
        baseline_data: List[float] = None,
        threshold: float = 3.0,
        sensitivity: float = 1.0,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            detector_id=detector_id,
            name=name,
            description=description,
            data_source=data_source,
            sensitivity=sensitivity,
            is_active=is_active,
            metadata=metadata
        )
        self.baseline_data = baseline_data or []
        self.threshold = threshold
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert detector to dictionary representation.
        
        Returns:
            Dictionary representation of the detector
        """
        base_dict = super().to_dict()
        base_dict.update({
            "baseline_data": self.baseline_data,
            "threshold": self.threshold
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, detector_dict: Dict[str, Any]) -> 'StatisticalAnomalyDetector':
        """
        Create a detector from dictionary representation.
        
        Args:
            detector_dict: Dictionary representation of the detector
            
        Returns:
            StatisticalAnomalyDetector object
        """
        return cls(
            detector_id=detector_dict.get("detector_id"),
            name=detector_dict["name"],
            description=detector_dict["description"],
            data_source=detector_dict["data_source"],
            baseline_data=detector_dict.get("baseline_data", []),
            threshold=detector_dict.get("threshold", 3.0),
            sensitivity=detector_dict.get("sensitivity", 1.0),
            is_active=detector_dict.get("is_active", True),
            metadata=detector_dict.get("metadata", {})
        )
    
    def add_baseline_data(self, data: Union[float, List[float]]) -> None:
        """
        Add data to the baseline.
        
        Args:
            data: Data point or list of data points to add
        """
        if isinstance(data, list):
            self.baseline_data.extend(data)
        else:
            self.baseline_data.append(data)
    
    def detect(self, data: float) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Detect anomalies using z-score.
        
        Args:
            data: Data point to analyze
            
        Returns:
            Tuple of (is_anomaly, anomaly_score, details)
        """
        if not self.baseline_data:
            return False, 0.0, {"error": "No baseline data available"}
            
        try:
            # Calculate z-score
            mean = statistics.mean(self.baseline_data)
            stdev = statistics.stdev(self.baseline_data) if len(self.baseline_data) > 1 else 1.0
            
            if stdev == 0:
                z_score = 0.0 if data == mean else float('inf')
            else:
                z_score = abs(data - mean) / stdev
                
            # Apply sensitivity
            adjusted_score = z_score * self.sensitivity
            
            # Determine if anomaly
            is_anomaly = adjusted_score > self.threshold
            
            return is_anomaly, adjusted_score, {
                "mean": mean,
                "stdev": stdev,
                "z_score": z_score,
                "adjusted_score": adjusted_score,
                "threshold": self.threshold
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return False, 0.0, {"error": str(e)}


class BehavioralAnomalyDetector(AnomalyDetector):
    """
    Behavioral anomaly detector for user actions.
    """
    def __init__(
        self,
        detector_id: str,
        name: str,
        description: str,
        data_source: str,
        user_profiles: Dict[str, Dict[str, Any]] = None,
        sensitivity: float = 1.0,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            detector_id=detector_id,
            name=name,
            description=description,
            data_source=data_source,
            sensitivity=sensitivity,
            is_active=is_active,
            metadata=metadata
        )
        self.user_profiles = user_profiles or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert detector to dictionary representation.
        
        Returns:
            Dictionary representation of the detector
        """
        base_dict = super().to_dict()
        base_dict.update({
            "user_profiles": self.user_profiles
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, detector_dict: Dict[str, Any]) -> 'BehavioralAnomalyDetector':
        """
        Create a detector from dictionary representation.
        
        Args:
            detector_dict: Dictionary representation of the detector
            
        Returns:
            BehavioralAnomalyDetector object
        """
        return cls(
            detector_id=detector_dict.get("detector_id"),
            name=detector_dict["name"],
            description=detector_dict["description"],
            data_source=detector_dict["data_source"],
            user_profiles=detector_dict.get("user_profiles", {}),
            sensitivity=detector_dict.get("sensitivity", 1.0),
            is_active=detector_dict.get("is_active", True),
            metadata=detector_dict.get("metadata", {})
        )
    
    def update_user_profile(self, user_id: str, behavior_data: Dict[str, Any]) -> None:
        """
        Update a user's behavioral profile.
        
        Args:
            user_id: User ID to update
            behavior_data: Behavioral data to update
        """
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
            
        # Update profile with new data
        for key, value in behavior_data.items():
            if key not in self.user_profiles[user_id]:
                self.user_profiles[user_id][key] = {
                    "values": [],
                    "last_updated": datetime.now().isoformat()
                }
                
            profile_entry = self.user_profiles[user_id][key]
            
            # Add new value
            if isinstance(value, (int, float)):
                if "values" not in profile_entry:
                    profile_entry["values"] = []
                profile_entry["values"].append(value)
                
                # Keep only the last 100 values
                if len(profile_entry["values"]) > 100:
                    profile_entry["values"] = profile_entry["values"][-100:]
                    
                # Update statistics
                profile_entry["mean"] = statistics.mean(profile_entry["values"])
                if len(profile_entry["values"]) > 1:
                    profile_entry["stdev"] = statistics.stdev(profile_entry["values"])
                else:
                    profile_entry["stdev"] = 0.0
            else:
                # For non-numeric values, store frequency
                if "frequency" not in profile_entry:
                    profile_entry["frequency"] = {}
                    
                str_value = str(value)
                if str_value not in profile_entry["frequency"]:
                    profile_entry["frequency"][str_value] = 0
                profile_entry["frequency"][str_value] += 1
                
            # Update timestamp
            profile_entry["last_updated"] = datetime.now().isoformat()
    
    def detect(self, user_id: str, behavior_data: Dict[str, Any]) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Detect behavioral anomalies.
        
        Args:
            user_id: User ID to check
            behavior_data: Behavioral data to analyze
            
        Returns:
            Tuple of (is_anomaly, anomaly_score, details)
        """
        if user_id not in self.user_profiles:
            # No profile yet, not enough data to detect anomalies
            return False, 0.0, {"error": "No user profile available"}
            
        anomaly_scores = []
        anomaly_details = {}
        
        for key, value in behavior_data.items():
            if key not in self.user_profiles[user_id]:
                # No data for this behavior yet
                continue
                
            profile_entry = self.user_profiles[user_id][key]
            
            if isinstance(value, (int, float)) and "mean" in profile_entry and "stdev" in profile_entry:
                # Numeric value, use z-score
                mean = profile_entry["mean"]
                stdev = profile_entry["stdev"]
                
                if stdev == 0:
                    z_score = 0.0 if value == mean else float('inf')
                else:
                    z_score = abs(value - mean) / stdev
                    
                # Apply sensitivity
                adjusted_score = z_score * self.sensitivity
                
                anomaly_scores.append(adjusted_score)
                anomaly_details[key] = {
                    "type": "numeric",
                    "value": value,
                    "mean": mean,
                    "stdev": stdev,
                    "z_score": z_score,
                    "adjusted_score": adjusted_score
                }
                
            elif "frequency" in profile_entry:
                # Categorical value, use frequency
                str_value = str(value)
                total_occurrences = sum(profile_entry["frequency"].values())
                value_occurrences = profile_entry["frequency"].get(str_value, 0)
                
                if total_occurrences > 0:
                    frequency = value_occurrences / total_occurrences
                    rarity_score = 1.0 - frequency
                    
                    # Apply sensitivity
                    adjusted_score = rarity_score * self.sensitivity
                    
                    anomaly_scores.append(adjusted_score)
                    anomaly_details[key] = {
                        "type": "categorical",
                        "value": value,
                        "frequency": frequency,
                        "rarity_score": rarity_score,
                        "adjusted_score": adjusted_score
                    }
        
        if not anomaly_scores:
            return False, 0.0, {"error": "No matching behavior data for analysis"}
            
        # Calculate overall anomaly score
        overall_score = max(anomaly_scores)
        
        # Determine if anomaly (threshold of 0.8)
        is_anomaly = overall_score > 0.8
        
        return is_anomaly, overall_score, {
            "scores": anomaly_scores,
            "overall_score": overall_score,
            "details": anomaly_details
        }


class SecurityMonitoringManager:
    """
    Manages security monitoring and compliance.
    """
    def __init__(
        self,
        event_manager: EventManager = None
    ):
        self.event_manager = event_manager or EventManager()
        
        # Audit logs
        self.audit_logs: List[AuditLog] = []
        
        # Compliance requirements
        self.compliance_requirements: Dict[str, ComplianceRequirement] = {}
        self.standard_requirements: Dict[str, List[str]] = {}  # standard -> [requirement_id]
        
        # Compliance checks
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.requirement_checks: Dict[str, List[str]] = {}  # requirement_id -> [check_id]
        
        # Compliance reports
        self.compliance_reports: Dict[str, ComplianceReport] = {}
        
        # Anomaly detectors
        self.anomaly_detectors: Dict[str, AnomalyDetector] = {}
        self.data_source_detectors: Dict[str, List[str]] = {}  # data_source -> [detector_id]
        
        # Register default compliance requirements
        self._register_default_requirements()
        
        # Register default anomaly detectors
        self._register_default_detectors()
        
    def _register_default_requirements(self) -> None:
        """
        Register default compliance requirements.
        """
        # GDPR requirements
        self.register_compliance_requirement(ComplianceRequirement(
            requirement_id="gdpr-consent",
            name="User Consent",
            description="Obtain and manage user consent for data processing",
            standard="GDPR",
            category="data_processing",
            verification_method="automated"
        ))
        
        self.register_compliance_requirement(ComplianceRequirement(
            requirement_id="gdpr-data-access",
            name="Data Access Rights",
            description="Provide users with access to their personal data",
            standard="GDPR",
            category="data_rights",
            verification_method="automated"
        ))
        
        self.register_compliance_requirement(ComplianceRequirement(
            requirement_id="gdpr-data-deletion",
            name="Right to be Forgotten",
            description="Allow users to request deletion of their personal data",
            standard="GDPR",
            category="data_rights",
            verification_method="automated"
        ))
        
        # SOC 2 requirements
        self.register_compliance_requirement(ComplianceRequirement(
            requirement_id="soc2-access-control",
            name="Access Control",
            description="Implement and maintain access controls",
            standard="SOC2",
            category="security",
            verification_method="automated"
        ))
        
        self.register_compliance_requirement(ComplianceRequirement(
            requirement_id="soc2-audit-logging",
            name="Audit Logging",
            description="Maintain comprehensive audit logs",
            standard="SOC2",
            category="monitoring",
            verification_method="automated"
        ))
        
        # HIPAA requirements
        self.register_compliance_requirement(ComplianceRequirement(
            requirement_id="hipaa-data-encryption",
            name="Data Encryption",
            description="Encrypt sensitive health information",
            standard="HIPAA",
            category="security",
            verification_method="automated"
        ))
        
        # PCI DSS requirements
        self.register_compliance_requirement(ComplianceRequirement(
            requirement_id="pci-dss-access-control",
            name="Access Control",
            description="Restrict access to cardholder data",
            standard="PCI-DSS",
            category="security",
            verification_method="automated"
        ))
    
    def _register_default_detectors(self) -> None:
        """
        Register default anomaly detectors.
        """
        # Login frequency detector
        self.register_anomaly_detector(StatisticalAnomalyDetector(
            detector_id="login-frequency",
            name="Login Frequency",
            description="Detect unusual login frequency",
            data_source="login_events",
            threshold=2.5,
            sensitivity=1.0
        ))
        
        # Failed login detector
        self.register_anomaly_detector(StatisticalAnomalyDetector(
            detector_id="failed-login",
            name="Failed Login Attempts",
            description="Detect unusual number of failed login attempts",
            data_source="failed_login_events",
            threshold=2.0,
            sensitivity=1.2
        ))
        
        # User behavior detector
        self.register_anomaly_detector(BehavioralAnomalyDetector(
            detector_id="user-behavior",
            name="User Behavior",
            description="Detect unusual user behavior patterns",
            data_source="user_actions",
            sensitivity=1.0
        ))
    
    def record_audit_log(
        self,
        action: str,
        actor_id: str,
        actor_type: str,
        resource_type: str,
        resource_id: Optional[str],
        result: str,
        description: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> AuditLog:
        """
        Record an audit log entry.
        
        Args:
            action: Action performed
            actor_id: ID of the actor performing the action
            actor_type: Type of actor
            resource_type: Type of resource
            resource_id: ID of the resource
            result: Result of the action
            description: Description of the action
            ip_address: Optional IP address
            user_agent: Optional user agent
            session_id: Optional session ID
            metadata: Optional additional metadata
            
        Returns:
            Recorded AuditLog
        """
        # Create log entry
        log_id = str(uuid.uuid4())
        log_entry = AuditLog(
            log_id=log_id,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            metadata=metadata
        )
        
        # Store log entry
        self.audit_logs.append(log_entry)
        
        # Emit event
        self.event_manager.emit_event("security.audit_log_recorded", {
            "log_id": log_id,
            "action": action,
            "actor_id": actor_id,
            "resource_type": resource_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return log_entry
    
    def get_audit_logs(
        self,
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        result: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs with optional filtering.
        
        Args:
            action: Optional action to filter by
            actor_id: Optional actor ID to filter by
            actor_type: Optional actor type to filter by
            resource_type: Optional resource type to filter by
            resource_id: Optional resource ID to filter by
            result: Optional result to filter by
            start_time: Optional start time to filter by
            end_time: Optional end time to filter by
            limit: Maximum number of logs to return
            
        Returns:
            List of AuditLog instances
        """
        # Apply filters
        filtered_logs = self.audit_logs
        
        if action:
            filtered_logs = [log for log in filtered_logs if log.action == action]
            
        if actor_id:
            filtered_logs = [log for log in filtered_logs if log.actor_id == actor_id]
            
        if actor_type:
            filtered_logs = [log for log in filtered_logs if log.actor_type == actor_type]
            
        if resource_type:
            filtered_logs = [log for log in filtered_logs if log.resource_type == resource_type]
            
        if resource_id:
            filtered_logs = [log for log in filtered_logs if log.resource_id == resource_id]
            
        if result:
            filtered_logs = [log for log in filtered_logs if log.result == result]
            
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
            
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
            
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda log: log.timestamp, reverse=True)
        
        # Apply limit
        return filtered_logs[:limit]
    
    def register_compliance_requirement(
        self,
        requirement: ComplianceRequirement
    ) -> ComplianceRequirement:
        """
        Register a compliance requirement.
        
        Args:
            requirement: ComplianceRequirement instance
            
        Returns:
            Registered ComplianceRequirement
            
        Raises:
            ConfigurationError: If requirement ID already exists
        """
        if requirement.requirement_id in self.compliance_requirements:
            raise ConfigurationError(f"Compliance requirement '{requirement.requirement_id}' already registered")
            
        # Store requirement
        self.compliance_requirements[requirement.requirement_id] = requirement
        
        # Update standard index
        if requirement.standard not in self.standard_requirements:
            self.standard_requirements[requirement.standard] = []
        self.standard_requirements[requirement.standard].append(requirement.requirement_id)
        
        # Emit event
        self.event_manager.emit_event("compliance.requirement_registered", {
            "requirement_id": requirement.requirement_id,
            "name": requirement.name,
            "standard": requirement.standard,
            "timestamp": datetime.now().isoformat()
        })
        
        return requirement
    
    def get_compliance_requirement(
        self,
        requirement_id: str
    ) -> Optional[ComplianceRequirement]:
        """
        Get a compliance requirement by ID.
        
        Args:
            requirement_id: Requirement ID to get
            
        Returns:
            ComplianceRequirement instance or None if not found
        """
        return self.compliance_requirements.get(requirement_id)
    
    def get_requirements_by_standard(
        self,
        standard: str
    ) -> List[ComplianceRequirement]:
        """
        Get all compliance requirements for a standard.
        
        Args:
            standard: Standard to filter by
            
        Returns:
            List of ComplianceRequirement instances
        """
        if standard not in self.standard_requirements:
            return []
            
        return [self.compliance_requirements[req_id] for req_id in self.standard_requirements[standard]
                if req_id in self.compliance_requirements]
    
    def register_compliance_check(
        self,
        check: ComplianceCheck
    ) -> ComplianceCheck:
        """
        Register a compliance check.
        
        Args:
            check: ComplianceCheck instance
            
        Returns:
            Registered ComplianceCheck
            
        Raises:
            ConfigurationError: If check ID already exists
        """
        if check.check_id in self.compliance_checks:
            raise ConfigurationError(f"Compliance check '{check.check_id}' already registered")
            
        # Verify requirement exists
        if check.requirement_id not in self.compliance_requirements:
            raise ConfigurationError(f"Compliance requirement '{check.requirement_id}' not found")
            
        # Store check
        self.compliance_checks[check.check_id] = check
        
        # Update requirement index
        if check.requirement_id not in self.requirement_checks:
            self.requirement_checks[check.requirement_id] = []
        self.requirement_checks[check.requirement_id].append(check.check_id)
        
        # Emit event
        self.event_manager.emit_event("compliance.check_registered", {
            "check_id": check.check_id,
            "name": check.name,
            "requirement_id": check.requirement_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return check
    
    def get_compliance_check(
        self,
        check_id: str
    ) -> Optional[ComplianceCheck]:
        """
        Get a compliance check by ID.
        
        Args:
            check_id: Check ID to get
            
        Returns:
            ComplianceCheck instance or None if not found
        """
        return self.compliance_checks.get(check_id)
    
    def get_checks_by_requirement(
        self,
        requirement_id: str
    ) -> List[ComplianceCheck]:
        """
        Get all compliance checks for a requirement.
        
        Args:
            requirement_id: Requirement ID to filter by
            
        Returns:
            List of ComplianceCheck instances
        """
        if requirement_id not in self.requirement_checks:
            return []
            
        return [self.compliance_checks[check_id] for check_id in self.requirement_checks[requirement_id]
                if check_id in self.compliance_checks]
    
    def run_compliance_check(
        self,
        check_id: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Run a compliance check.
        
        Args:
            check_id: Check ID to run
            
        Returns:
            Tuple of (passed, details, additional_data)
            
        Raises:
            ConfigurationError: If check does not exist
        """
        check = self.get_compliance_check(check_id)
        if not check:
            raise ConfigurationError(f"Compliance check '{check_id}' not found")
            
        # Run check
        result = check.run()
        
        # Emit event
        self.event_manager.emit_event("compliance.check_run", {
            "check_id": check_id,
            "name": check.name,
            "requirement_id": check.requirement_id,
            "passed": result[0],
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def generate_compliance_report(
        self,
        name: str,
        description: str,
        standards: List[str],
        generated_by: Optional[str] = None
    ) -> ComplianceReport:
        """
        Generate a compliance report.
        
        Args:
            name: Report name
            description: Report description
            standards: List of standards to include
            generated_by: Optional ID of the user generating the report
            
        Returns:
            Generated ComplianceReport
        """
        # Create report
        report_id = str(uuid.uuid4())
        report = ComplianceReport(
            report_id=report_id,
            name=name,
            description=description,
            standards=standards,
            generated_by=generated_by
        )
        
        # Get all requirements for the specified standards
        requirements = []
        for standard in standards:
            requirements.extend(self.get_requirements_by_standard(standard))
            
        # Run checks for each requirement
        for requirement in requirements:
            checks = self.get_checks_by_requirement(requirement.requirement_id)
            
            for check in checks:
                if not check.is_active:
                    continue
                    
                # Run check
                passed, details, additional_data = check.run()
                
                # Add result to report
                report.add_result(check.check_id, {
                    "check_id": check.check_id,
                    "name": check.name,
                    "requirement_id": requirement.requirement_id,
                    "requirement_name": requirement.name,
                    "standard": requirement.standard,
                    "passed": passed,
                    "details": details,
                    "additional_data": additional_data
                })
        
        # Generate summary
        report.generate_summary()
        
        # Store report
        self.compliance_reports[report_id] = report
        
        # Emit event
        self.event_manager.emit_event("compliance.report_generated", {
            "report_id": report_id,
            "name": name,
            "standards": standards,
            "timestamp": datetime.now().isoformat()
        })
        
        return report
    
    def get_compliance_report(
        self,
        report_id: str
    ) -> Optional[ComplianceReport]:
        """
        Get a compliance report by ID.
        
        Args:
            report_id: Report ID to get
            
        Returns:
            ComplianceReport instance or None if not found
        """
        return self.compliance_reports.get(report_id)
    
    def register_anomaly_detector(
        self,
        detector: AnomalyDetector
    ) -> AnomalyDetector:
        """
        Register an anomaly detector.
        
        Args:
            detector: AnomalyDetector instance
            
        Returns:
            Registered AnomalyDetector
            
        Raises:
            ConfigurationError: If detector ID already exists
        """
        if detector.detector_id in self.anomaly_detectors:
            raise ConfigurationError(f"Anomaly detector '{detector.detector_id}' already registered")
            
        # Store detector
        self.anomaly_detectors[detector.detector_id] = detector
        
        # Update data source index
        if detector.data_source not in self.data_source_detectors:
            self.data_source_detectors[detector.data_source] = []
        self.data_source_detectors[detector.data_source].append(detector.detector_id)
        
        # Emit event
        self.event_manager.emit_event("security.detector_registered", {
            "detector_id": detector.detector_id,
            "name": detector.name,
            "data_source": detector.data_source,
            "timestamp": datetime.now().isoformat()
        })
        
        return detector
    
    def get_anomaly_detector(
        self,
        detector_id: str
    ) -> Optional[AnomalyDetector]:
        """
        Get an anomaly detector by ID.
        
        Args:
            detector_id: Detector ID to get
            
        Returns:
            AnomalyDetector instance or None if not found
        """
        return self.anomaly_detectors.get(detector_id)
    
    def get_detectors_by_data_source(
        self,
        data_source: str
    ) -> List[AnomalyDetector]:
        """
        Get all anomaly detectors for a data source.
        
        Args:
            data_source: Data source to filter by
            
        Returns:
            List of AnomalyDetector instances
        """
        if data_source not in self.data_source_detectors:
            return []
            
        return [self.anomaly_detectors[detector_id] for detector_id in self.data_source_detectors[data_source]
                if detector_id in self.anomaly_detectors]
    
    def detect_anomalies(
        self,
        data_source: str,
        data: Any,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in data.
        
        Args:
            data_source: Data source of the data
            data: Data to analyze
            user_id: Optional user ID the data is associated with
            
        Returns:
            List of anomaly detection results
        """
        # Get detectors for this data source
        detectors = self.get_detectors_by_data_source(data_source)
        
        # Run detectors
        results = []
        
        for detector in detectors:
            if not detector.is_active:
                continue
                
            try:
                # Run detector
                if isinstance(detector, BehavioralAnomalyDetector) and user_id:
                    # For behavioral detectors, we need user ID
                    is_anomaly, score, details = detector.detect(user_id, data)
                else:
                    # For other detectors
                    is_anomaly, score, details = detector.detect(data)
                    
                # Add result
                results.append({
                    "detector_id": detector.detector_id,
                    "name": detector.name,
                    "is_anomaly": is_anomaly,
                    "score": score,
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                })
                
                # If anomaly detected, emit event
                if is_anomaly:
                    self.event_manager.emit_event("security.anomaly_detected", {
                        "detector_id": detector.detector_id,
                        "name": detector.name,
                        "data_source": data_source,
                        "score": score,
                        "user_id": user_id,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"Error detecting anomalies with detector {detector.detector_id}: {e}")
                
        return results
    
    def update_behavioral_profile(
        self,
        user_id: str,
        data_source: str,
        behavior_data: Dict[str, Any]
    ) -> None:
        """
        Update a user's behavioral profile.
        
        Args:
            user_id: User ID to update
            data_source: Data source of the behavior data
            behavior_data: Behavioral data to update
        """
        # Get behavioral detectors for this data source
        detectors = [d for d in self.get_detectors_by_data_source(data_source)
                    if isinstance(d, BehavioralAnomalyDetector)]
        
        # Update profiles
        for detector in detectors:
            if not detector.is_active:
                continue
                
            try:
                detector.update_user_profile(user_id, behavior_data)
            except Exception as e:
                logger.error(f"Error updating behavioral profile with detector {detector.detector_id}: {e}")
    
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for a security dashboard.
        
        Returns:
            Dashboard data
        """
        # Get recent audit logs
        recent_logs = self.get_audit_logs(limit=10)
        
        # Get recent anomalies
        # In a real implementation, you would store and retrieve anomalies
        # For this example, we'll return an empty list
        recent_anomalies = []
        
        # Get compliance summary
        compliance_summary = {}
        for standard, requirement_ids in self.standard_requirements.items():
            total_requirements = len(requirement_ids)
            total_checks = 0
            passed_checks = 0
            
            for req_id in requirement_ids:
                if req_id in self.requirement_checks:
                    req_checks = self.requirement_checks[req_id]
                    total_checks += len(req_checks)
                    
                    for check_id in req_checks:
                        if check_id in self.compliance_checks:
                            check = self.compliance_checks[check_id]
                            if check.is_active:
                                passed, _, _ = check.run()
                                if passed:
                                    passed_checks += 1
            
            compliance_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            
            compliance_summary[standard] = {
                "total_requirements": total_requirements,
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "compliance_percentage": compliance_percentage
            }
        
        # Return dashboard data
        return {
            "recent_logs": [log.to_dict() for log in recent_logs],
            "recent_anomalies": recent_anomalies,
            "compliance_summary": compliance_summary,
            "timestamp": datetime.now().isoformat()
        }
