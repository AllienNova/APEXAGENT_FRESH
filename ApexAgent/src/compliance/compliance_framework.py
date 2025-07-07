#!/usr/bin/env python3
"""
Compliance and Regulatory Framework for ApexAgent

This module provides a comprehensive framework for managing compliance
requirements, data privacy, consent, and audit logging to meet
regulatory standards like GDPR, HIPAA, and SOC2.
"""

import os
import sys
import time
import json
import uuid
import logging
import threading
import hashlib
import hmac
import base64
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, TypeVar, cast, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("compliance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("compliance")

# Type variables for generic functions
T = TypeVar("T")
R = TypeVar("R")

class ComplianceStandard(Enum):
    """Enumeration of compliance standards."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    CCPA = "ccpa"
    ISO27001 = "iso27001"
    CUSTOM = "custom"

class DataClassification(Enum):
    """Enumeration of data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SENSITIVE = "sensitive"
    PHI = "phi"  # Protected Health Information (HIPAA)
    PII = "pii"  # Personally Identifiable Information (GDPR/CCPA)

class ConsentStatus(Enum):
    """Enumeration of consent statuses."""
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"
    PENDING = "pending"
    EXPIRED = "expired"

class AuditAction(Enum):
    """Enumeration of audit actions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS = "access"
    CONSENT_CHANGE = "consent_change"
    POLICY_CHANGE = "policy_change"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    CUSTOM = "custom"

@dataclass
class CompliancePolicy:
    """Compliance policy data structure."""
    policy_id: str
    standard: ComplianceStandard
    version: str
    description: str
    rules: Dict[str, Any]
    effective_date: datetime
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class ConsentRecord:
    """Consent record data structure."""
    consent_id: str
    user_id: str
    purpose: str
    status: ConsentStatus
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuditLog:
    """Audit log entry data structure."""
    log_id: str
    timestamp: datetime
    user_id: Optional[str]
    action: AuditAction
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = "success"  # success, failure
    signature: Optional[str] = None  # For integrity verification

@dataclass
class ComplianceConfig:
    """Configuration for the compliance framework."""
    enabled_standards: Set[ComplianceStandard] = field(default_factory=set)
    data_retention_policy: Dict[DataClassification, int] = field(default_factory=dict)  # days
    audit_log_retention: int = 365  # days
    consent_required_purposes: List[str] = field(default_factory=list)
    audit_log_storage_path: str = "audit_logs"
    consent_storage_path: str = "consent_records"
    policy_storage_path: str = "policies"
    encryption_key: Optional[str] = None  # For encrypting sensitive data
    audit_log_signing_key: Optional[str] = None  # For signing audit logs
    anonymization_salt: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {
            "enabled_standards": [std.value for std in self.enabled_standards],
            "data_retention_policy": {cls.value: days for cls, days in self.data_retention_policy.items()},
            "audit_log_retention": self.audit_log_retention,
            "consent_required_purposes": self.consent_required_purposes,
            "audit_log_storage_path": self.audit_log_storage_path,
            "consent_storage_path": self.consent_storage_path,
            "policy_storage_path": self.policy_storage_path,
            "anonymization_salt": self.anonymization_salt
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComplianceConfig":
        """Create a configuration from a dictionary."""
        return cls(
            enabled_standards={ComplianceStandard(std) for std in data.get("enabled_standards", [])},
            data_retention_policy={DataClassification(cls): days for cls, days in data.get("data_retention_policy", {}).items()},
            audit_log_retention=data.get("audit_log_retention", 365),
            consent_required_purposes=data.get("consent_required_purposes", []),
            audit_log_storage_path=data.get("audit_log_storage_path", "audit_logs"),
            consent_storage_path=data.get("consent_storage_path", "consent_records"),
            policy_storage_path=data.get("policy_storage_path", "policies"),
            encryption_key=data.get("encryption_key"),
            audit_log_signing_key=data.get("audit_log_signing_key"),
            anonymization_salt=data.get("anonymization_salt")
        )

class PolicyManager:
    """Manages compliance policies."""
    
    def __init__(self, config: ComplianceConfig):
        """Initialize the policy manager."""
        self.config = config
        self.policies: Dict[str, CompliancePolicy] = {}
        self._lock = threading.RLock()
        self._load_policies()
    
    def _load_policies(self) -> None:
        """Load policies from storage."""
        with self._lock:
            self.policies = {}
            policy_dir = Path(self.config.policy_storage_path)
            policy_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in policy_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        policy_data = json.load(f)
                    
                    policy = CompliancePolicy(
                        policy_id=policy_data["policy_id"],
                        standard=ComplianceStandard(policy_data["standard"]),
                        version=policy_data["version"],
                        description=policy_data["description"],
                        rules=policy_data["rules"],
                        effective_date=datetime.fromisoformat(policy_data["effective_date"]),
                        last_updated=datetime.fromisoformat(policy_data["last_updated"]),
                        is_active=policy_data["is_active"]
                    )
                    self.policies[policy.policy_id] = policy
                except Exception as e:
                    logger.error(f"Failed to load policy from {file_path}: {str(e)}")
    
    def _save_policy(self, policy: CompliancePolicy) -> None:
        """Save a policy to storage."""
        policy_dir = Path(self.config.policy_storage_path)
        policy_dir.mkdir(parents=True, exist_ok=True)
        file_path = policy_dir / f"{policy.policy_id}.json"
        
        try:
            policy_data = {
                "policy_id": policy.policy_id,
                "standard": policy.standard.value,
                "version": policy.version,
                "description": policy.description,
                "rules": policy.rules,
                "effective_date": policy.effective_date.isoformat(),
                "last_updated": policy.last_updated.isoformat(),
                "is_active": policy.is_active
            }
            with open(file_path, "w") as f:
                json.dump(policy_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save policy {policy.policy_id}: {str(e)}")
    
    def add_policy(self, standard: ComplianceStandard, version: str, description: str,
                  rules: Dict[str, Any], effective_date: datetime) -> CompliancePolicy:
        """Add a new compliance policy."""
        with self._lock:
            policy_id = str(uuid.uuid4())
            policy = CompliancePolicy(
                policy_id=policy_id,
                standard=standard,
                version=version,
                description=description,
                rules=rules,
                effective_date=effective_date
            )
            self.policies[policy_id] = policy
            self._save_policy(policy)
            logger.info(f"Added new policy: {policy_id} ({standard.value} v{version})")
            return policy
    
    def update_policy(self, policy_id: str, **kwargs) -> Optional[CompliancePolicy]:
        """Update an existing policy."""
        with self._lock:
            if policy_id not in self.policies:
                logger.error(f"Policy not found: {policy_id}")
                return None
            
            policy = self.policies[policy_id]
            updated = False
            for key, value in kwargs.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
                    updated = True
            
            if updated:
                policy.last_updated = datetime.now()
                self._save_policy(policy)
                logger.info(f"Updated policy: {policy_id}")
            
            return policy
    
    def get_policy(self, policy_id: str) -> Optional[CompliancePolicy]:
        """Get a policy by ID."""
        with self._lock:
            return self.policies.get(policy_id)
    
    def get_active_policies(self, standard: Optional[ComplianceStandard] = None) -> List[CompliancePolicy]:
        """Get all active policies, optionally filtered by standard."""
        with self._lock:
            active_policies = [p for p in self.policies.values() if p.is_active]
            if standard:
                active_policies = [p for p in active_policies if p.standard == standard]
            return active_policies
    
    def check_compliance(self, data: Any, data_classification: DataClassification) -> bool:
        """Check if data handling complies with active policies."""
        # This is a placeholder. Real implementation would involve complex rule evaluation.
        active_policies = self.get_active_policies()
        for policy in active_policies:
            if policy.standard in self.config.enabled_standards:
                # Apply policy rules based on data_classification and policy.rules
                # Example: Check if PII is encrypted according to GDPR rules
                if policy.standard == ComplianceStandard.GDPR and data_classification == DataClassification.PII:
                    # Placeholder check
                    if not self._is_encrypted(data):
                        logger.warning(f"Data classified as PII is not encrypted, violating GDPR policy {policy.policy_id}")
                        # return False # Uncomment to enforce
                    pass
                elif policy.standard == ComplianceStandard.HIPAA and data_classification == DataClassification.PHI:
                    # Placeholder check
                    if not self._is_access_logged(data):
                        logger.warning(f"Access to PHI is not logged, violating HIPAA policy {policy.policy_id}")
                        # return False # Uncomment to enforce
                    pass
        return True # Assume compliant for now

    def _is_encrypted(self, data: Any) -> bool:
        # Placeholder for encryption check
        return True

    def _is_access_logged(self, data: Any) -> bool:
        # Placeholder for access logging check
        return True

class ConsentManager:
    """Manages user consent."""
    
    def __init__(self, config: ComplianceConfig):
        """Initialize the consent manager."""
        self.config = config
        self.consent_records: Dict[str, Dict[str, ConsentRecord]] = {}
        self._lock = threading.RLock()
        self._load_consent_records()
    
    def _load_consent_records(self) -> None:
        """Load consent records from storage."""
        with self._lock:
            self.consent_records = {}
            consent_dir = Path(self.config.consent_storage_path)
            consent_dir.mkdir(parents=True, exist_ok=True)
            
            for user_dir in consent_dir.iterdir():
                if user_dir.is_dir():
                    user_id = user_dir.name
                    self.consent_records[user_id] = {}
                    for file_path in user_dir.glob("*.json"):
                        try:
                            with open(file_path, "r") as f:
                                consent_data = json.load(f)
                            
                            record = ConsentRecord(
                                consent_id=consent_data["consent_id"],
                                user_id=consent_data["user_id"],
                                purpose=consent_data["purpose"],
                                status=ConsentStatus(consent_data["status"]),
                                granted_at=datetime.fromisoformat(consent_data["granted_at"]) if consent_data.get("granted_at") else None,
                                revoked_at=datetime.fromisoformat(consent_data["revoked_at"]) if consent_data.get("revoked_at") else None,
                                expires_at=datetime.fromisoformat(consent_data["expires_at"]) if consent_data.get("expires_at") else None,
                                version=consent_data.get("version", "1.0"),
                                metadata=consent_data.get("metadata", {})
                            )
                            self.consent_records[user_id][record.purpose] = record
                        except Exception as e:
                            logger.error(f"Failed to load consent record from {file_path}: {str(e)}")
    
    def _save_consent_record(self, record: ConsentRecord) -> None:
        """Save a consent record to storage."""
        user_dir = Path(self.config.consent_storage_path) / record.user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_dir / f"{record.purpose}.json"
        
        try:
            consent_data = {
                "consent_id": record.consent_id,
                "user_id": record.user_id,
                "purpose": record.purpose,
                "status": record.status.value,
                "granted_at": record.granted_at.isoformat() if record.granted_at else None,
                "revoked_at": record.revoked_at.isoformat() if record.revoked_at else None,
                "expires_at": record.expires_at.isoformat() if record.expires_at else None,
                "version": record.version,
                "metadata": record.metadata
            }
            with open(file_path, "w") as f:
                json.dump(consent_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save consent record {record.consent_id}: {str(e)}")
    
    def record_consent(self, user_id: str, purpose: str, status: ConsentStatus,
                      version: str = "1.0", expires_at: Optional[datetime] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> ConsentRecord:
        """Record or update user consent."""
        with self._lock:
            if user_id not in self.consent_records:
                self.consent_records[user_id] = {}
            
            consent_id = str(uuid.uuid4())
            now = datetime.now()
            
            record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                purpose=purpose,
                status=status,
                granted_at=now if status == ConsentStatus.GRANTED else None,
                revoked_at=now if status == ConsentStatus.REVOKED else None,
                expires_at=expires_at,
                version=version,
                metadata=metadata or {}
            )
            
            self.consent_records[user_id][purpose] = record
            self._save_consent_record(record)
            logger.info(f"Recorded consent for user {user_id}, purpose {purpose}: {status.value}")
            # Log consent change
            audit_logger.log_audit(
                user_id=user_id,
                action=AuditAction.CONSENT_CHANGE,
                resource_type="consent",
                resource_id=purpose,
                details=record.to_dict()
            )
            return record
    
    def get_consent_status(self, user_id: str, purpose: str) -> ConsentStatus:
        """Get the current consent status for a user and purpose."""
        with self._lock:
            if user_id not in self.consent_records or purpose not in self.consent_records[user_id]:
                return ConsentStatus.PENDING
            
            record = self.consent_records[user_id][purpose]
            
            # Check for expiration
            if record.expires_at and record.expires_at < datetime.now():
                record.status = ConsentStatus.EXPIRED
                self._save_consent_record(record) # Update status in storage
                return ConsentStatus.EXPIRED
            
            return record.status
    
    def check_consent(self, user_id: str, purpose: str) -> bool:
        """Check if consent is granted for a specific purpose."""
        return self.get_consent_status(user_id, purpose) == ConsentStatus.GRANTED
    
    def get_user_consents(self, user_id: str) -> Dict[str, ConsentStatus]:
        """Get all consent statuses for a user."""
        with self._lock:
            if user_id not in self.consent_records:
                return {}
            
            statuses = {}
            for purpose, record in self.consent_records[user_id].items():
                # Check for expiration
                if record.expires_at and record.expires_at < datetime.now():
                    record.status = ConsentStatus.EXPIRED
                    self._save_consent_record(record)
                statuses[purpose] = record.status
            return statuses
    
    def revoke_consent(self, user_id: str, purpose: str) -> Optional[ConsentRecord]:
        """Revoke consent for a user and purpose."""
        return self.record_consent(user_id, purpose, ConsentStatus.REVOKED)

class AuditLogger:
    """Logs audit trails for compliance."""
    
    def __init__(self, config: ComplianceConfig):
        """Initialize the audit logger."""
        self.config = config
        self.log_queue = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._ensure_storage_path()
    
    def _ensure_storage_path(self) -> None:
        """Ensure the audit log storage path exists."""
        Path(self.config.audit_log_storage_path).mkdir(parents=True, exist_ok=True)
    
    def start(self) -> None:
        """Start the audit logger thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._process_logs, daemon=True)
            self._thread.start()
            logger.info("Audit logger started")
    
    def stop(self) -> None:
        """Stop the audit logger thread."""
        with self._lock:
            if not self._running:
                return
            self._running = False
            if self._thread:
                self._thread.join(timeout=5.0)
                self._thread = None
            # Process any remaining logs in the queue
            self._process_queue_sync()
            logger.info("Audit logger stopped")
    
    def log_audit(self, action: AuditAction, details: Dict[str, Any],
                 user_id: Optional[str] = None, resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None, ip_address: Optional[str] = None,
                 user_agent: Optional[str] = None, status: str = "success") -> str:
        """Log an audit event."""
        log_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        log_entry = AuditLog(
            log_id=log_id,
            timestamp=timestamp,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        
        # Sign the log entry if key is provided
        if self.config.audit_log_signing_key:
            log_entry.signature = self._sign_log(log_entry)
        
        self.log_queue.put(log_entry)
        return log_id
    
    def _sign_log(self, log_entry: AuditLog) -> str:
        """Sign an audit log entry for integrity."""
        if not self.config.audit_log_signing_key:
            return ""
        
        # Create canonical representation
        log_data = log_entry.to_dict()
        log_data.pop("signature", None) # Remove signature field itself
        canonical_log = json.dumps(log_data, sort_keys=True, separators=(",", ":"))
        
        # Sign using HMAC-SHA256
        signature = hmac.new(
            self.config.audit_log_signing_key.encode(),
            canonical_log.encode(),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode()
    
    def verify_log_signature(self, log_entry: AuditLog) -> bool:
        """Verify the signature of an audit log entry."""
        if not self.config.audit_log_signing_key or not log_entry.signature:
            logger.warning(f"Cannot verify log {log_entry.log_id}: No signing key or signature.")
            return False
        
        expected_signature = self._sign_log(log_entry)
        return hmac.compare_digest(log_entry.signature, expected_signature)
    
    def _process_logs(self) -> None:
        """Process logs from the queue and write to storage."""
        while self._running:
            try:
                log_entry = self.log_queue.get(timeout=1.0)
                self._write_log(log_entry)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing audit log: {str(e)}")
    
    def _process_queue_sync(self) -> None:
        """Process remaining logs in the queue synchronously."""
        while not self.log_queue.empty():
            try:
                log_entry = self.log_queue.get_nowait()
                self._write_log(log_entry)
                self.log_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing remaining audit log: {str(e)}")
    
    def _write_log(self, log_entry: AuditLog) -> None:
        """Write a single log entry to the appropriate file."""
        try:
            date_str = log_entry.timestamp.strftime("%Y-%m-%d")
            log_dir = Path(self.config.audit_log_storage_path) / date_str
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "audit.log"
            
            log_line = json.dumps(log_entry.to_dict()) + "\n"
            
            with open(log_file, "a") as f:
                f.write(log_line)
        except Exception as e:
            logger.error(f"Failed to write audit log {log_entry.log_id}: {str(e)}")
    
    def query_logs(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                  user_id: Optional[str] = None, action: Optional[AuditAction] = None,
                  resource_type: Optional[str] = None, resource_id: Optional[str] = None,
                  limit: int = 1000) -> List[AuditLog]:
        """Query audit logs."""
        logs = []
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=7)
            if not end_date:
                end_date = datetime.now()
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                log_file = Path(self.config.audit_log_storage_path) / date_str / "audit.log"
                
                if log_file.exists():
                    with open(log_file, "r") as f:
                        for line in f:
                            if len(logs) >= limit:
                                break
                            try:
                                log_data = json.loads(line)
                                log_entry = AuditLog(
                                    log_id=log_data["log_id"],
                                    timestamp=datetime.fromisoformat(log_data["timestamp"]),
                                    user_id=log_data.get("user_id"),
                                    action=AuditAction(log_data["action"]),
                                    resource_type=log_data.get("resource_type"),
                                    resource_id=log_data.get("resource_id"),
                                    details=log_data["details"],
                                    ip_address=log_data.get("ip_address"),
                                    user_agent=log_data.get("user_agent"),
                                    status=log_data.get("status", "success"),
                                    signature=log_data.get("signature")
                                )
                                
                                # Apply filters
                                if user_id and log_entry.user_id != user_id:
                                    continue
                                if action and log_entry.action != action:
                                    continue
                                if resource_type and log_entry.resource_type != resource_type:
                                    continue
                                if resource_id and log_entry.resource_id != resource_id:
                                    continue
                                
                                # Verify signature if needed
                                # if self.config.audit_log_signing_key and not self.verify_log_signature(log_entry):
                                #     logger.warning(f"Audit log signature verification failed: {log_entry.log_id}")
                                #     continue # Optionally skip invalid logs
                                
                                logs.append(log_entry)
                            except Exception as e:
                                logger.error(f"Failed to parse audit log line: {line.strip()} - {str(e)}")
                
                if len(logs) >= limit:
                    break
                current_date += timedelta(days=1)
            
            # Sort logs by timestamp (descending)
            logs.sort(key=lambda x: x.timestamp, reverse=True)
            
            return logs[:limit]
        except Exception as e:
            logger.error(f"Error querying audit logs: {str(e)}")
            return []
    
    def cleanup_old_logs(self) -> None:
        """Clean up old audit logs based on retention policy."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.audit_log_retention)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
            log_root_dir = Path(self.config.audit_log_storage_path)
            
            if log_root_dir.exists():
                for date_dir in log_root_dir.iterdir():
                    if date_dir.is_dir() and date_dir.name < cutoff_date_str:
                        log_file = date_dir / "audit.log"
                        if log_file.exists():
                            log_file.unlink()
                        try:
                            date_dir.rmdir() # Remove dir only if empty
                        except OSError:
                            logger.warning(f"Could not remove non-empty directory: {date_dir}")
                logger.info(f"Cleaned up audit logs older than {cutoff_date_str}")
        except Exception as e:
            logger.error(f"Error cleaning up old audit logs: {str(e)}")

class DataPrivacyManager:
    """Manages data privacy functions like anonymization and deletion."""
    
    def __init__(self, config: ComplianceConfig):
        """Initialize the data privacy manager."""
        self.config = config
    
    def anonymize_data(self, data: Any, data_classification: DataClassification) -> Any:
        """Anonymize data based on its classification."""
        if not self.config.anonymization_salt:
            logger.warning("Anonymization salt not configured. Cannot anonymize.")
            return data
        
        if data_classification in [DataClassification.PII, DataClassification.PHI, DataClassification.SENSITIVE]:
            if isinstance(data, str):
                # Use salted hash for anonymization
                hashed_value = hashlib.sha256((data + self.config.anonymization_salt).encode()).hexdigest()
                return f"anon_{hashed_value[:16]}"
            elif isinstance(data, dict):
                return {key: self.anonymize_data(value, data_classification) for key, value in data.items()}
            elif isinstance(data, list):
                return [self.anonymize_data(item, data_classification) for item in data]
            else:
                # For non-string types, return a generic placeholder
                return f"[anonymized_{data_classification.value}]"
        return data
    
    def handle_data_subject_request(self, user_id: str, request_type: str) -> bool:
        """Handle data subject requests (e.g., access, deletion)."""
        # This requires integration with data storage systems.
        logger.info(f"Handling data subject request for user {user_id}: {request_type}")
        if request_type == "access":
            # Retrieve user data from all relevant systems
            # Provide data in a portable format
            pass
        elif request_type == "deletion":
            # Delete user data from all relevant systems, respecting retention policies
            # Anonymize data where deletion is not possible (e.g., audit logs)
            pass
        else:
            logger.error(f"Unsupported data subject request type: {request_type}")
            return False
        return True # Placeholder
    
    def apply_retention_policy(self, data: Any, data_classification: DataClassification, timestamp: datetime) -> bool:
        """Check if data should be retained based on policy."""
        retention_days = self.config.data_retention_policy.get(data_classification)
        if retention_days is None:
            return True # No specific policy, retain indefinitely (or based on default)
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        return timestamp >= cutoff_date

class ComplianceFramework:
    """Main compliance framework class."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> "ComplianceFramework":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = ComplianceFramework()
        return cls._instance
    
    def __init__(self):
        """Initialize the compliance framework."""
        self.config = ComplianceConfig()
        self.policy_manager = PolicyManager(self.config)
        self.consent_manager = ConsentManager(self.config)
        self.audit_logger = AuditLogger(self.config)
        self.privacy_manager = DataPrivacyManager(self.config)
        self._initialized = False
        self._lock = threading.RLock()
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """Initialize the framework with configuration."""
        with self._lock:
            if self._initialized:
                return
            
            if config_path and Path(config_path).exists():
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                    self.config = ComplianceConfig.from_dict(config_data)
                except Exception as e:
                    logger.error(f"Failed to load compliance config from {config_path}: {str(e)}. Using defaults.")
                    self.config = ComplianceConfig()
            else:
                logger.warning("Compliance config file not found. Using defaults.")
                self.config = ComplianceConfig()
            
            # Re-initialize managers with the loaded config
            self.policy_manager = PolicyManager(self.config)
            self.consent_manager = ConsentManager(self.config)
            self.audit_logger = AuditLogger(self.config)
            self.privacy_manager = DataPrivacyManager(self.config)
            
            # Start audit logger
            self.audit_logger.start()
            
            self._initialized = True
            logger.info("Compliance framework initialized")
    
    def shutdown(self) -> None:
        """Shutdown the framework."""
        with self._lock:
            if not self._initialized:
                return
            self.audit_logger.stop()
            self._initialized = False
            logger.info("Compliance framework shutdown")
    
    def ensure_initialized(self) -> None:
        """Ensure the framework is initialized."""
        if not self._initialized:
            self.initialize()
    
    # --- Expose Manager Methods --- #
    
    # Policy Manager Methods
    def add_policy(self, *args, **kwargs) -> CompliancePolicy:
        self.ensure_initialized()
        return self.policy_manager.add_policy(*args, **kwargs)
    
    def update_policy(self, *args, **kwargs) -> Optional[CompliancePolicy]:
        self.ensure_initialized()
        return self.policy_manager.update_policy(*args, **kwargs)
    
    def get_policy(self, *args, **kwargs) -> Optional[CompliancePolicy]:
        self.ensure_initialized()
        return self.policy_manager.get_policy(*args, **kwargs)
    
    def get_active_policies(self, *args, **kwargs) -> List[CompliancePolicy]:
        self.ensure_initialized()
        return self.policy_manager.get_active_policies(*args, **kwargs)
    
    def check_compliance(self, *args, **kwargs) -> bool:
        self.ensure_initialized()
        return self.policy_manager.check_compliance(*args, **kwargs)
    
    # Consent Manager Methods
    def record_consent(self, *args, **kwargs) -> ConsentRecord:
        self.ensure_initialized()
        return self.consent_manager.record_consent(*args, **kwargs)
    
    def get_consent_status(self, *args, **kwargs) -> ConsentStatus:
        self.ensure_initialized()
        return self.consent_manager.get_consent_status(*args, **kwargs)
    
    def check_consent(self, *args, **kwargs) -> bool:
        self.ensure_initialized()
        return self.consent_manager.check_consent(*args, **kwargs)
    
    def get_user_consents(self, *args, **kwargs) -> Dict[str, ConsentStatus]:
        self.ensure_initialized()
        return self.consent_manager.get_user_consents(*args, **kwargs)
    
    def revoke_consent(self, *args, **kwargs) -> Optional[ConsentRecord]:
        self.ensure_initialized()
        return self.consent_manager.revoke_consent(*args, **kwargs)
    
    # Audit Logger Methods
    def log_audit(self, *args, **kwargs) -> str:
        self.ensure_initialized()
        return self.audit_logger.log_audit(*args, **kwargs)
    
    def query_logs(self, *args, **kwargs) -> List[AuditLog]:
        self.ensure_initialized()
        return self.audit_logger.query_logs(*args, **kwargs)
    
    def verify_log_signature(self, *args, **kwargs) -> bool:
        self.ensure_initialized()
        return self.audit_logger.verify_log_signature(*args, **kwargs)
    
    def cleanup_old_logs(self) -> None:
        self.ensure_initialized()
        self.audit_logger.cleanup_old_logs()
    
    # Data Privacy Manager Methods
    def anonymize_data(self, *args, **kwargs) -> Any:
        self.ensure_initialized()
        return self.privacy_manager.anonymize_data(*args, **kwargs)
    
    def handle_data_subject_request(self, *args, **kwargs) -> bool:
        self.ensure_initialized()
        return self.privacy_manager.handle_data_subject_request(*args, **kwargs)
    
    def apply_retention_policy(self, *args, **kwargs) -> bool:
        self.ensure_initialized()
        return self.privacy_manager.apply_retention_policy(*args, **kwargs)

# Global instance for easy access
compliance_framework = ComplianceFramework.get_instance()
audit_logger = compliance_framework.audit_logger # Expose audit logger directly

# --- Helper Functions --- #

def initialize_compliance(config_path: Optional[str] = None) -> None:
    """Initialize the compliance framework."""
    compliance_framework.initialize(config_path)

def shutdown_compliance() -> None:
    """Shutdown the compliance framework."""
    compliance_framework.shutdown()

# Example usage
if __name__ == "__main__":
    # Initialize
    initialize_compliance()
    
    # Example: Record consent
    user_id = "user_abc_123"
    consent_purpose = "marketing_emails"
    
    compliance_framework.record_consent(user_id, consent_purpose, ConsentStatus.GRANTED)
    
    # Check consent
    has_consent = compliance_framework.check_consent(user_id, consent_purpose)
    print(f"User {user_id} consent for {consent_purpose}: {has_consent}")
    
    # Log an audit event
    compliance_framework.log_audit(
        user_id=user_id,
        action=AuditAction.READ,
        resource_type="profile",
        resource_id=user_id,
        details={"fields": ["email", "name"]}
    )
    
    # Anonymize data
    email = "test@example.com"
    anonymized_email = compliance_framework.anonymize_data(email, DataClassification.PII)
    print(f"Original email: {email}, Anonymized: {anonymized_email}")
    
    # Query logs
    logs = compliance_framework.query_logs(user_id=user_id, limit=10)
    print(f"Found {len(logs)} audit logs for user {user_id}")
    for log in logs:
        print(f"- {log.timestamp} {log.action.value} {log.resource_type}/{log.resource_id}")
    
    # Shutdown
    shutdown_compliance()
