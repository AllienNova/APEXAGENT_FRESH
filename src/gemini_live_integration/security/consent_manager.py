"""
Consent Manager for Gemini Live API Integration.

This module implements a comprehensive consent management system that:
1. Tracks and enforces user consent for data processing
2. Provides granular controls for different data types and operations
3. Maintains an audit trail of consent changes
4. Supports consent revocation and data deletion

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


class ConsentScope(Enum):
    """Scopes for which consent can be granted."""
    DATA_COLLECTION = "data_collection"  # Collecting user data
    DATA_PROCESSING = "data_processing"  # Processing user data
    DATA_SHARING = "data_sharing"  # Sharing user data with third parties
    PERSONALIZATION = "personalization"  # Personalizing user experience
    MARKETING = "marketing"  # Marketing communications
    ANALYTICS = "analytics"  # Analytics and usage tracking
    SENSITIVE_DATA = "sensitive_data"  # Processing sensitive data
    THIRD_PARTY = "third_party"  # Third-party integrations
    LOCATION = "location"  # Location data
    BIOMETRIC = "biometric"  # Biometric data


class ConsentStatus(Enum):
    """Status of a consent record."""
    GRANTED = "granted"  # Consent explicitly granted
    DENIED = "denied"  # Consent explicitly denied
    WITHDRAWN = "withdrawn"  # Consent withdrawn after being granted
    EXPIRED = "expired"  # Consent expired
    PENDING = "pending"  # Consent request pending user action


@dataclass
class ConsentRecord:
    """Record of a user's consent for a specific scope."""
    consent_id: str
    user_id: str
    tenant_id: str
    scope: ConsentScope
    status: ConsentStatus
    timestamp: float
    expiration: Optional[float] = None
    data_categories: List[str] = field(default_factory=list)
    purposes: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    source: str = "user_explicit"  # How consent was obtained
    version: str = "1.0"  # Version of the consent record
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsentHistory:
    """History of consent changes for a user and scope."""
    user_id: str
    tenant_id: str
    scope: ConsentScope
    history: List[ConsentRecord] = field(default_factory=list)


class ConsentVerificationResult:
    """Result of a consent verification check."""
    
    def __init__(
        self,
        is_valid: bool,
        scope: ConsentScope,
        user_id: str,
        tenant_id: str,
        reason: str = "",
        record: Optional[ConsentRecord] = None
    ):
        self.is_valid = is_valid
        self.scope = scope
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.reason = reason
        self.record = record
        self.timestamp = time.time()
        self.verification_id = str(uuid.uuid4())
    
    def __bool__(self) -> bool:
        """Allow using the result in boolean context."""
        return self.is_valid


class ConsentManager:
    """
    Consent Manager for Gemini Live API Integration.
    
    This class manages user consent for various data processing activities,
    ensuring compliance with privacy regulations.
    """
    
    def __init__(
        self,
        storage_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        audit_logger: Optional[Any] = None
    ):
        """
        Initialize the consent manager.
        
        Args:
            storage_provider: Optional provider for persistent storage
            config: Configuration for the consent manager
            audit_logger: Optional audit logger for consent events
        """
        self.config = config or self._default_config()
        self.storage_provider = storage_provider
        self.audit_logger = audit_logger
        
        # In-memory storage for consent records
        self._consent_records: Dict[str, ConsentRecord] = {}
        self._consent_history: Dict[str, ConsentHistory] = {}
        
        # Load existing consent records if storage provider is available
        if self.storage_provider:
            self._load_consent_records()
        
        # Initialize metrics
        self.metrics = {
            "consent_granted": 0,
            "consent_denied": 0,
            "consent_withdrawn": 0,
            "consent_expired": 0,
            "consent_verified": 0,
            "verification_passed": 0,
            "verification_failed": 0,
        }
        
        logger.info("Consent Manager initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Create default configuration for the consent manager."""
        return {
            "default_expiration_days": 365,  # Default consent expiration in days
            "require_explicit_consent": True,  # Whether explicit consent is required
            "consent_reminder_days": 30,  # Days before expiration to remind users
            "store_consent_history": True,  # Whether to store consent history
            "max_history_records": 100,  # Maximum number of history records per user/scope
            "sensitive_data_categories": [
                "health", "biometric", "genetic", "religious", "political",
                "sexual_orientation", "racial_origin", "criminal_record"
            ],
            "default_purposes": [
                "service_provision", "feature_improvement", "personalization"
            ],
            "require_purpose_binding": True,  # Whether to require purpose binding
        }
    
    def _load_consent_records(self) -> None:
        """Load consent records from storage provider."""
        if not self.storage_provider:
            return
        
        try:
            # Load consent records
            records = self.storage_provider.get_all("consent_records")
            for record_data in records:
                record = ConsentRecord(**record_data)
                self._consent_records[f"{record.user_id}:{record.tenant_id}:{record.scope.value}"] = record
            
            # Load consent history if configured
            if self.config["store_consent_history"]:
                histories = self.storage_provider.get_all("consent_history")
                for history_data in histories:
                    history = ConsentHistory(**history_data)
                    self._consent_history[f"{history.user_id}:{history.tenant_id}:{history.scope.value}"] = history
            
            logger.info("Loaded %d consent records and %d history records from storage",
                       len(self._consent_records), len(self._consent_history))
        
        except Exception as e:
            logger.error("Failed to load consent records: %s", str(e))
    
    def _save_consent_record(self, record: ConsentRecord) -> None:
        """Save a consent record to storage."""
        if not self.storage_provider:
            return
        
        try:
            # Convert enum values to strings for storage
            record_data = {
                **record.__dict__,
                "scope": record.scope.value,
                "status": record.status.value
            }
            
            # Save to storage
            self.storage_provider.put(
                "consent_records",
                record.consent_id,
                record_data
            )
            
            logger.debug("Saved consent record %s for user %s, scope %s",
                        record.consent_id, record.user_id, record.scope.value)
        
        except Exception as e:
            logger.error("Failed to save consent record: %s", str(e))
    
    def _save_consent_history(self, history: ConsentHistory) -> None:
        """Save consent history to storage."""
        if not self.storage_provider or not self.config["store_consent_history"]:
            return
        
        try:
            # Convert enum values to strings for storage
            history_data = {
                **history.__dict__,
                "scope": history.scope.value,
                "history": [
                    {
                        **record.__dict__,
                        "scope": record.scope.value,
                        "status": record.status.value
                    }
                    for record in history.history
                ]
            }
            
            # Save to storage
            self.storage_provider.put(
                "consent_history",
                f"{history.user_id}:{history.tenant_id}:{history.scope.value}",
                history_data
            )
            
            logger.debug("Saved consent history for user %s, scope %s with %d records",
                        history.user_id, history.scope.value, len(history.history))
        
        except Exception as e:
            logger.error("Failed to save consent history: %s", str(e))
    
    def _log_consent_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        scope: ConsentScope,
        details: Dict[str, Any]
    ) -> None:
        """Log a consent-related event."""
        if not self.audit_logger:
            return
        
        event = {
            "event_type": f"CONSENT_{event_type}",
            "timestamp": time.time(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "scope": scope.value,
            "details": details
        }
        
        # Send to audit logger
        self.audit_logger(event)
        
        # Also log to application logs
        logger.info("Consent event: %s, User: %s, Scope: %s, Details: %s",
                   event_type, user_id, scope.value, json.dumps(details))
    
    def record_consent(
        self,
        user_id: str,
        tenant_id: str,
        scope: ConsentScope,
        status: ConsentStatus,
        data_categories: Optional[List[str]] = None,
        purposes: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        source: str = "user_explicit",
        expiration_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConsentRecord:
        """
        Record a user's consent decision.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            scope: Scope of the consent
            status: Status of the consent
            data_categories: Categories of data covered by the consent
            purposes: Purposes for which the data can be used
            conditions: Additional conditions for the consent
            source: Source of the consent (e.g., "user_explicit", "legal_basis")
            expiration_days: Days until the consent expires
            metadata: Additional metadata for the consent
            
        Returns:
            The created consent record
        """
        # Generate a unique ID for the consent record
        consent_id = str(uuid.uuid4())
        
        # Set expiration if provided, otherwise use default
        expiration = None
        if expiration_days is not None:
            expiration = time.time() + (expiration_days * 24 * 60 * 60)
        elif self.config["default_expiration_days"] > 0:
            expiration = time.time() + (self.config["default_expiration_days"] * 24 * 60 * 60)
        
        # Create the consent record
        record = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope,
            status=status,
            timestamp=time.time(),
            expiration=expiration,
            data_categories=data_categories or [],
            purposes=purposes or self.config["default_purposes"],
            conditions=conditions or {},
            source=source,
            metadata=metadata or {}
        )
        
        # Store the record
        key = f"{user_id}:{tenant_id}:{scope.value}"
        self._consent_records[key] = record
        
        # Save to persistent storage if available
        self._save_consent_record(record)
        
        # Update consent history if configured
        if self.config["store_consent_history"]:
            if key not in self._consent_history:
                self._consent_history[key] = ConsentHistory(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    scope=scope,
                    history=[]
                )
            
            # Add to history, respecting max history size
            history = self._consent_history[key]
            history.history.append(record)
            if len(history.history) > self.config["max_history_records"]:
                history.history = history.history[-self.config["max_history_records"]:]
            
            # Save history to persistent storage
            self._save_consent_history(history)
        
        # Log the consent event
        event_type = f"{status.value.upper()}"
        self._log_consent_event(
            event_type,
            user_id,
            tenant_id,
            scope,
            {
                "consent_id": consent_id,
                "data_categories": data_categories,
                "purposes": purposes,
                "source": source,
                "expiration": expiration
            }
        )
        
        # Update metrics
        if status == ConsentStatus.GRANTED:
            self.metrics["consent_granted"] += 1
        elif status == ConsentStatus.DENIED:
            self.metrics["consent_denied"] += 1
        elif status == ConsentStatus.WITHDRAWN:
            self.metrics["consent_withdrawn"] += 1
        
        return record
    
    def verify_consent(
        self,
        user_id: str,
        tenant_id: str,
        scope: ConsentScope,
        data_category: Optional[str] = None,
        purpose: Optional[str] = None
    ) -> ConsentVerificationResult:
        """
        Verify if a user has given consent for a specific scope.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            scope: Scope of the consent to verify
            data_category: Optional specific data category to check
            purpose: Optional specific purpose to check
            
        Returns:
            Result of the consent verification
        """
        # Update metrics
        self.metrics["consent_verified"] += 1
        
        # Get the consent record
        key = f"{user_id}:{tenant_id}:{scope.value}"
        record = self._consent_records.get(key)
        
        # If no record exists, consent is not granted
        if not record:
            self.metrics["verification_failed"] += 1
            return ConsentVerificationResult(
                is_valid=False,
                scope=scope,
                user_id=user_id,
                tenant_id=tenant_id,
                reason="No consent record found"
            )
        
        # Check if consent is granted
        if record.status != ConsentStatus.GRANTED:
            self.metrics["verification_failed"] += 1
            return ConsentVerificationResult(
                is_valid=False,
                scope=scope,
                user_id=user_id,
                tenant_id=tenant_id,
                reason=f"Consent status is {record.status.value}",
                record=record
            )
        
        # Check if consent has expired
        if record.expiration and time.time() > record.expiration:
            # Update the record to mark it as expired
            record.status = ConsentStatus.EXPIRED
            self._save_consent_record(record)
            
            self.metrics["consent_expired"] += 1
            self.metrics["verification_failed"] += 1
            
            return ConsentVerificationResult(
                is_valid=False,
                scope=scope,
                user_id=user_id,
                tenant_id=tenant_id,
                reason="Consent has expired",
                record=record
            )
        
        # Check data category if specified
        if data_category and record.data_categories:
            if data_category not in record.data_categories:
                self.metrics["verification_failed"] += 1
                return ConsentVerificationResult(
                    is_valid=False,
                    scope=scope,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    reason=f"Data category {data_category} not covered by consent",
                    record=record
                )
        
        # Check purpose if specified and purpose binding is required
        if purpose and self.config["require_purpose_binding"]:
            if not record.purposes or purpose not in record.purposes:
                self.metrics["verification_failed"] += 1
                return ConsentVerificationResult(
                    is_valid=False,
                    scope=scope,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    reason=f"Purpose {purpose} not covered by consent",
                    record=record
                )
        
        # All checks passed, consent is valid
        self.metrics["verification_passed"] += 1
        
        # Log the verification event
        self._log_consent_event(
            "VERIFIED",
            user_id,
            tenant_id,
            scope,
            {
                "consent_id": record.consent_id,
                "data_category": data_category,
                "purpose": purpose,
                "result": "valid"
            }
        )
        
        return ConsentVerificationResult(
            is_valid=True,
            scope=scope,
            user_id=user_id,
            tenant_id=tenant_id,
            reason="Consent is valid",
            record=record
        )
    
    def withdraw_consent(
        self,
        user_id: str,
        tenant_id: str,
        scope: ConsentScope,
        reason: str = "user_request"
    ) -> bool:
        """
        Withdraw a user's consent for a specific scope.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            scope: Scope of the consent to withdraw
            reason: Reason for withdrawal
            
        Returns:
            True if consent was withdrawn, False if no consent record exists
        """
        # Get the consent record
        key = f"{user_id}:{tenant_id}:{scope.value}"
        record = self._consent_records.get(key)
        
        # If no record exists, nothing to withdraw
        if not record:
            return False
        
        # Update the record
        record.status = ConsentStatus.WITHDRAWN
        record.metadata["withdrawal_reason"] = reason
        record.metadata["withdrawal_time"] = time.time()
        
        # Save the updated record
        self._save_consent_record(record)
        
        # Update consent history if configured
        if self.config["store_consent_history"] and key in self._consent_history:
            history = self._consent_history[key]
            history.history.append(record)
            if len(history.history) > self.config["max_history_records"]:
                history.history = history.history[-self.config["max_history_records"]:]
            
            # Save history to persistent storage
            self._save_consent_history(history)
        
        # Log the withdrawal event
        self._log_consent_event(
            "WITHDRAWN",
            user_id,
            tenant_id,
            scope,
            {
                "consent_id": record.consent_id,
                "reason": reason
            }
        )
        
        # Update metrics
        self.metrics["consent_withdrawn"] += 1
        
        return True
    
    def get_consent_status(
        self,
        user_id: str,
        tenant_id: str,
        scope: Optional[ConsentScope] = None
    ) -> Dict[str, Any]:
        """
        Get the consent status for a user.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            scope: Optional specific scope to check
            
        Returns:
            Dictionary with consent status information
        """
        result = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "timestamp": time.time(),
            "consents": {}
        }
        
        # If scope is specified, only check that scope
        if scope:
            key = f"{user_id}:{tenant_id}:{scope.value}"
            record = self._consent_records.get(key)
            if record:
                result["consents"][scope.value] = {
                    "status": record.status.value,
                    "timestamp": record.timestamp,
                    "expiration": record.expiration,
                    "data_categories": record.data_categories,
                    "purposes": record.purposes
                }
            else:
                result["consents"][scope.value] = {
                    "status": "not_recorded",
                    "timestamp": None,
                    "expiration": None,
                    "data_categories": [],
                    "purposes": []
                }
        
        # Otherwise, check all scopes
        else:
            for scope_value in ConsentScope:
                key = f"{user_id}:{tenant_id}:{scope_value.value}"
                record = self._consent_records.get(key)
                if record:
                    result["consents"][scope_value.value] = {
                        "status": record.status.value,
                        "timestamp": record.timestamp,
                        "expiration": record.expiration,
                        "data_categories": record.data_categories,
                        "purposes": record.purposes
                    }
                else:
                    result["consents"][scope_value.value] = {
                        "status": "not_recorded",
                        "timestamp": None,
                        "expiration": None,
                        "data_categories": [],
                        "purposes": []
                    }
        
        return result
    
    def get_consent_history(
        self,
        user_id: str,
        tenant_id: str,
        scope: ConsentScope
    ) -> List[Dict[str, Any]]:
        """
        Get the consent history for a user and scope.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            scope: Scope of the consent
            
        Returns:
            List of consent history records
        """
        if not self.config["store_consent_history"]:
            return []
        
        key = f"{user_id}:{tenant_id}:{scope.value}"
        history = self._consent_history.get(key)
        
        if not history:
            return []
        
        # Convert to dictionaries for API response
        return [
            {
                "consent_id": record.consent_id,
                "status": record.status.value,
                "timestamp": record.timestamp,
                "expiration": record.expiration,
                "data_categories": record.data_categories,
                "purposes": record.purposes,
                "source": record.source
            }
            for record in history.history
        ]
    
    def export_user_consents(
        self,
        user_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Export all consent information for a user.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            
        Returns:
            Dictionary with all consent information
        """
        result = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "export_timestamp": time.time(),
            "current_consents": {},
            "consent_history": {}
        }
        
        # Get current consents
        for scope_value in ConsentScope:
            key = f"{user_id}:{tenant_id}:{scope_value.value}"
            record = self._consent_records.get(key)
            if record:
                result["current_consents"][scope_value.value] = {
                    "consent_id": record.consent_id,
                    "status": record.status.value,
                    "timestamp": record.timestamp,
                    "expiration": record.expiration,
                    "data_categories": record.data_categories,
                    "purposes": record.purposes,
                    "conditions": record.conditions,
                    "source": record.source,
                    "version": record.version,
                    "metadata": record.metadata
                }
        
        # Get consent history if configured
        if self.config["store_consent_history"]:
            for scope_value in ConsentScope:
                key = f"{user_id}:{tenant_id}:{scope_value.value}"
                history = self._consent_history.get(key)
                if history:
                    result["consent_history"][scope_value.value] = [
                        {
                            "consent_id": record.consent_id,
                            "status": record.status.value,
                            "timestamp": record.timestamp,
                            "expiration": record.expiration,
                            "data_categories": record.data_categories,
                            "purposes": record.purposes,
                            "conditions": record.conditions,
                            "source": record.source,
                            "version": record.version,
                            "metadata": record.metadata
                        }
                        for record in history.history
                    ]
        
        # Log the export event
        self._log_consent_event(
            "EXPORTED",
            user_id,
            tenant_id,
            ConsentScope.DATA_COLLECTION,  # Use a generic scope for the export event
            {
                "export_timestamp": result["export_timestamp"],
                "num_consents": len(result["current_consents"]),
                "num_history_records": sum(len(h) for h in result["consent_history"].values())
            }
        )
        
        return result
    
    def delete_user_consents(
        self,
        user_id: str,
        tenant_id: str
    ) -> int:
        """
        Delete all consent information for a user.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            
        Returns:
            Number of consent records deleted
        """
        deleted_count = 0
        
        # Delete current consents
        for scope_value in ConsentScope:
            key = f"{user_id}:{tenant_id}:{scope_value.value}"
            if key in self._consent_records:
                # Get the record for logging
                record = self._consent_records[key]
                
                # Delete from in-memory storage
                del self._consent_records[key]
                
                # Delete from persistent storage if available
                if self.storage_provider:
                    try:
                        self.storage_provider.delete(
                            "consent_records",
                            record.consent_id
                        )
                    except Exception as e:
                        logger.error("Failed to delete consent record from storage: %s", str(e))
                
                deleted_count += 1
        
        # Delete consent history if configured
        if self.config["store_consent_history"]:
            for scope_value in ConsentScope:
                key = f"{user_id}:{tenant_id}:{scope_value.value}"
                if key in self._consent_history:
                    # Delete from in-memory storage
                    del self._consent_history[key]
                    
                    # Delete from persistent storage if available
                    if self.storage_provider:
                        try:
                            self.storage_provider.delete(
                                "consent_history",
                                key
                            )
                        except Exception as e:
                            logger.error("Failed to delete consent history from storage: %s", str(e))
        
        # Log the deletion event
        self._log_consent_event(
            "DELETED",
            user_id,
            tenant_id,
            ConsentScope.DATA_COLLECTION,  # Use a generic scope for the deletion event
            {
                "deleted_count": deleted_count,
                "deletion_timestamp": time.time()
            }
        )
        
        return deleted_count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current consent metrics."""
        return self.metrics.copy()
