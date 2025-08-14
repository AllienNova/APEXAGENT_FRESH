"""
Security and Compliance Integration Tests for Gemini Live API Integration.

This module implements comprehensive tests for all security and compliance features:
1. Security Layer (Interceptor) tests
2. Encryption Service tests
3. Consent Manager tests
4. Audit Logger tests
5. Incident Response tests
6. Compliance Reporter tests

This is a production-ready implementation with no placeholders.
"""

import json
import time
import unittest
from unittest import mock
import uuid
from typing import Any, Dict, List, Optional

# Import security modules
from src.gemini_live_integration.security.security_layer import SecurityInterceptor, SecurityAction
from src.gemini_live_integration.security.encryption_service import EncryptionService, EncryptionAlgorithm
from src.gemini_live_integration.security.consent_manager import ConsentManager, ConsentScope, ConsentStatus
from src.gemini_live_integration.security.audit_logger import AuditLogger, AuditEventSeverity
from src.gemini_live_integration.security.incident_response import (
    IncidentResponseSystem, IncidentSeverity, IncidentCategory, IncidentStatus
)
from src.gemini_live_integration.security.compliance_reporter import (
    ComplianceReporter, ComplianceFramework, ComplianceStatus, ComplianceRiskLevel
)


class MockStorageProvider:
    """Mock storage provider for testing."""
    
    def __init__(self):
        self.data = {}
    
    def get_all(self, collection):
        return self.data.get(collection, [])
    
    def get(self, collection, id):
        items = self.data.get(collection, [])
        for item in items:
            if item.get("id") == id:
                return item
        return None
    
    def put(self, collection, id, data):
        if collection not in self.data:
            self.data[collection] = []
        
        # Update if exists
        for i, item in enumerate(self.data[collection]):
            if item.get("id") == id:
                self.data[collection][i] = data
                return
        
        # Add if not exists
        self.data[collection].append(data)


class MockNotificationHandler:
    """Mock notification handler for testing."""
    
    def __init__(self):
        self.notifications = []
    
    def __call__(self, notification):
        self.notifications.append(notification)


class TestSecurityLayer(unittest.TestCase):
    """Tests for the Security Layer (Interceptor)."""
    
    def setUp(self):
        """Set up test environment."""
        self.audit_logger = mock.MagicMock()
        self.security_layer = SecurityInterceptor(
            audit_logger=self.audit_logger,
            config={
                "blocked_keywords": ["password", "ssn", "credit_card"],
                "pii_detection_enabled": True,
                "max_token_count": 1000,
                "tenant_isolation_required": True
            }
        )
    
    def test_intercept_request_clean(self):
        """Test intercepting a clean request."""
        request = {
            "text": "Tell me about machine learning",
            "tenant_id": "tenant123",
            "user_id": "user456",
            "metadata": {"source": "web_app"}
        }
        
        result = self.security_layer.intercept_request(request)
        
        self.assertEqual(result.action, SecurityAction.ALLOW)
        self.assertEqual(result.modified_request, request)
        self.assertIsNone(result.reason)
    
    def test_intercept_request_blocked_keyword(self):
        """Test intercepting a request with blocked keywords."""
        request = {
            "text": "What is my password?",
            "tenant_id": "tenant123",
            "user_id": "user456",
            "metadata": {"source": "web_app"}
        }
        
        result = self.security_layer.intercept_request(request)
        
        self.assertEqual(result.action, SecurityAction.BLOCK)
        self.assertIsNotNone(result.reason)
        self.assertIn("blocked keyword", result.reason.lower())
    
    def test_intercept_request_missing_tenant(self):
        """Test intercepting a request with missing tenant ID."""
        request = {
            "text": "Tell me about machine learning",
            "user_id": "user456",
            "metadata": {"source": "web_app"}
        }
        
        result = self.security_layer.intercept_request(request)
        
        self.assertEqual(result.action, SecurityAction.BLOCK)
        self.assertIsNotNone(result.reason)
        self.assertIn("tenant_id", result.reason.lower())
    
    def test_intercept_response_clean(self):
        """Test intercepting a clean response."""
        request = {
            "text": "Tell me about machine learning",
            "tenant_id": "tenant123",
            "user_id": "user456"
        }
        
        response = {
            "text": "Machine learning is a field of artificial intelligence...",
            "metadata": {"model": "gemini-pro"}
        }
        
        result = self.security_layer.intercept_response(request, response)
        
        self.assertEqual(result.action, SecurityAction.ALLOW)
        self.assertEqual(result.modified_response, response)
        self.assertIsNone(result.reason)
    
    def test_intercept_response_pii_detected(self):
        """Test intercepting a response with PII."""
        request = {
            "text": "Tell me about myself",
            "tenant_id": "tenant123",
            "user_id": "user456"
        }
        
        response = {
            "text": "Your SSN is 123-45-6789 and your address is 123 Main St.",
            "metadata": {"model": "gemini-pro"}
        }
        
        result = self.security_layer.intercept_response(request, response)
        
        self.assertEqual(result.action, SecurityAction.REDACT)
        self.assertNotEqual(result.modified_response, response)
        self.assertNotIn("123-45-6789", result.modified_response["text"])
    
    def test_audit_logging(self):
        """Test that audit logging is performed."""
        request = {
            "text": "Tell me about machine learning",
            "tenant_id": "tenant123",
            "user_id": "user456"
        }
        
        self.security_layer.intercept_request(request)
        
        # Verify audit logger was called
        self.audit_logger.log_security_event.assert_called()


class TestEncryptionService(unittest.TestCase):
    """Tests for the Encryption Service."""
    
    def setUp(self):
        """Set up test environment."""
        self.encryption_service = EncryptionService()
    
    def test_encrypt_decrypt_text(self):
        """Test encrypting and decrypting text."""
        original_text = "This is sensitive information"
        tenant_id = "tenant123"
        
        # Encrypt
        encrypted_data = self.encryption_service.encrypt_text(
            text=original_text,
            tenant_id=tenant_id
        )
        
        self.assertNotEqual(encrypted_data.ciphertext, original_text)
        self.assertIsNotNone(encrypted_data.key_id)
        
        # Decrypt
        decrypted_text = self.encryption_service.decrypt_text(
            ciphertext=encrypted_data.ciphertext,
            key_id=encrypted_data.key_id,
            tenant_id=tenant_id
        )
        
        self.assertEqual(decrypted_text, original_text)
    
    def test_encrypt_decrypt_document(self):
        """Test encrypting and decrypting a document."""
        original_document = {
            "title": "Confidential Report",
            "content": "This is sensitive information",
            "metadata": {"author": "John Doe"}
        }
        tenant_id = "tenant123"
        
        # Encrypt
        encrypted_data = self.encryption_service.encrypt_document(
            document=original_document,
            tenant_id=tenant_id,
            fields_to_encrypt=["content"]
        )
        
        self.assertEqual(encrypted_data.document["title"], original_document["title"])
        self.assertNotEqual(encrypted_data.document["content"], original_document["content"])
        self.assertEqual(encrypted_data.document["metadata"], original_document["metadata"])
        
        # Decrypt
        decrypted_document = self.encryption_service.decrypt_document(
            document=encrypted_data.document,
            key_mappings=encrypted_data.key_mappings,
            tenant_id=tenant_id
        )
        
        self.assertEqual(decrypted_document, original_document)
    
    def test_tenant_isolation(self):
        """Test that encryption maintains tenant isolation."""
        text = "This is sensitive information"
        tenant1_id = "tenant1"
        tenant2_id = "tenant2"
        
        # Encrypt with tenant1
        encrypted_data = self.encryption_service.encrypt_text(
            text=text,
            tenant_id=tenant1_id
        )
        
        # Try to decrypt with tenant2
        with self.assertRaises(Exception):
            self.encryption_service.decrypt_text(
                ciphertext=encrypted_data.ciphertext,
                key_id=encrypted_data.key_id,
                tenant_id=tenant2_id
            )
    
    def test_key_rotation(self):
        """Test key rotation."""
        text = "This is sensitive information"
        tenant_id = "tenant123"
        
        # Encrypt with current key
        encrypted_data = self.encryption_service.encrypt_text(
            text=text,
            tenant_id=tenant_id
        )
        
        # Rotate keys
        self.encryption_service.rotate_keys(tenant_id)
        
        # Should still be able to decrypt with old key
        decrypted_text = self.encryption_service.decrypt_text(
            ciphertext=encrypted_data.ciphertext,
            key_id=encrypted_data.key_id,
            tenant_id=tenant_id
        )
        
        self.assertEqual(decrypted_text, text)
        
        # New encryption should use new key
        new_encrypted_data = self.encryption_service.encrypt_text(
            text=text,
            tenant_id=tenant_id
        )
        
        self.assertNotEqual(new_encrypted_data.key_id, encrypted_data.key_id)


class TestConsentManager(unittest.TestCase):
    """Tests for the Consent Manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.storage_provider = MockStorageProvider()
        self.audit_logger = mock.MagicMock()
        self.consent_manager = ConsentManager(
            storage_provider=self.storage_provider,
            audit_logger=self.audit_logger
        )
    
    def test_record_consent(self):
        """Test recording consent."""
        user_id = "user123"
        tenant_id = "tenant456"
        scope = ConsentScope.DATA_PROCESSING
        
        # Record consent
        consent = self.consent_manager.record_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope,
            status=ConsentStatus.GRANTED,
            context={"source": "web_form"}
        )
        
        self.assertEqual(consent.user_id, user_id)
        self.assertEqual(consent.tenant_id, tenant_id)
        self.assertEqual(consent.scope, scope)
        self.assertEqual(consent.status, ConsentStatus.GRANTED)
        
        # Verify audit logging
        self.audit_logger.log_security_event.assert_called()
    
    def test_check_consent(self):
        """Test checking consent."""
        user_id = "user123"
        tenant_id = "tenant456"
        scope = ConsentScope.DATA_PROCESSING
        
        # No consent initially
        has_consent = self.consent_manager.check_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope
        )
        
        self.assertFalse(has_consent)
        
        # Record consent
        self.consent_manager.record_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope,
            status=ConsentStatus.GRANTED,
            context={"source": "web_form"}
        )
        
        # Check again
        has_consent = self.consent_manager.check_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope
        )
        
        self.assertTrue(has_consent)
    
    def test_revoke_consent(self):
        """Test revoking consent."""
        user_id = "user123"
        tenant_id = "tenant456"
        scope = ConsentScope.DATA_PROCESSING
        
        # Record consent
        self.consent_manager.record_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope,
            status=ConsentStatus.GRANTED,
            context={"source": "web_form"}
        )
        
        # Revoke consent
        self.consent_manager.record_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope,
            status=ConsentStatus.REVOKED,
            context={"source": "web_form"}
        )
        
        # Check again
        has_consent = self.consent_manager.check_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope
        )
        
        self.assertFalse(has_consent)
    
    def test_get_consent_history(self):
        """Test getting consent history."""
        user_id = "user123"
        tenant_id = "tenant456"
        scope = ConsentScope.DATA_PROCESSING
        
        # Record consent multiple times
        self.consent_manager.record_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope,
            status=ConsentStatus.GRANTED,
            context={"source": "web_form"}
        )
        
        time.sleep(0.1)  # Ensure different timestamps
        
        self.consent_manager.record_consent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope,
            status=ConsentStatus.REVOKED,
            context={"source": "web_form"}
        )
        
        # Get history
        history = self.consent_manager.get_consent_history(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope
        )
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].status, ConsentStatus.REVOKED)  # Most recent first
        self.assertEqual(history[1].status, ConsentStatus.GRANTED)


class TestAuditLogger(unittest.TestCase):
    """Tests for the Audit Logger."""
    
    def setUp(self):
        """Set up test environment."""
        self.storage_provider = MockStorageProvider()
        self.audit_logger = AuditLogger(
            storage_provider=self.storage_provider
        )
    
    def test_log_security_event(self):
        """Test logging a security event."""
        # Log an event
        event = self.audit_logger.log_security_event(
            event_type="USER_LOGIN",
            source="auth_service",
            details={"ip_address": "192.168.1.1"},
            severity=AuditEventSeverity.INFO,
            user_id="user123",
            tenant_id="tenant456"
        )
        
        self.assertEqual(event.event_type, "USER_LOGIN")
        self.assertEqual(event.source, "auth_service")
        self.assertEqual(event.severity, AuditEventSeverity.INFO)
        self.assertEqual(event.user_id, "user123")
        self.assertEqual(event.tenant_id, "tenant456")
        self.assertEqual(event.details["ip_address"], "192.168.1.1")
    
    def test_get_events(self):
        """Test getting events."""
        # Log multiple events
        self.audit_logger.log_security_event(
            event_type="USER_LOGIN",
            source="auth_service",
            details={"ip_address": "192.168.1.1"},
            severity=AuditEventSeverity.INFO,
            user_id="user123",
            tenant_id="tenant456"
        )
        
        self.audit_logger.log_security_event(
            event_type="DATA_ACCESS",
            source="data_service",
            details={"resource_id": "doc789"},
            severity=AuditEventSeverity.WARNING,
            user_id="user123",
            tenant_id="tenant456"
        )
        
        # Get events by type
        events = self.audit_logger.get_events(
            event_type="USER_LOGIN"
        )
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "USER_LOGIN")
        
        # Get events by user
        events = self.audit_logger.get_events(
            user_id="user123"
        )
        
        self.assertEqual(len(events), 2)
    
    def test_search_events(self):
        """Test searching events."""
        # Log events
        self.audit_logger.log_security_event(
            event_type="DATA_ACCESS",
            source="data_service",
            details={"resource_id": "doc123", "action": "read"},
            severity=AuditEventSeverity.INFO,
            user_id="user123",
            tenant_id="tenant456"
        )
        
        self.audit_logger.log_security_event(
            event_type="DATA_ACCESS",
            source="data_service",
            details={"resource_id": "doc456", "action": "write"},
            severity=AuditEventSeverity.WARNING,
            user_id="user789",
            tenant_id="tenant456"
        )
        
        # Search by detail field
        events = self.audit_logger.search_events(
            detail_filters={"action": "read"}
        )
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].details["action"], "read")
    
    def test_event_retention(self):
        """Test event retention."""
        # Override retention period for testing
        self.audit_logger.config["retention_period_days"] = 0  # Immediate expiration
        
        # Log an event
        event = self.audit_logger.log_security_event(
            event_type="TEST_EVENT",
            source="test",
            details={},
            severity=AuditEventSeverity.INFO,
            user_id="user123",
            tenant_id="tenant456"
        )
        
        # Run retention cleanup
        deleted_count = self.audit_logger.cleanup_expired_events()
        
        # Check that event was deleted
        self.assertGreaterEqual(deleted_count, 1)
        
        events = self.audit_logger.get_events(event_type="TEST_EVENT")
        self.assertEqual(len(events), 0)


class TestIncidentResponseSystem(unittest.TestCase):
    """Tests for the Incident Response System."""
    
    def setUp(self):
        """Set up test environment."""
        self.storage_provider = MockStorageProvider()
        self.notification_handler = MockNotificationHandler()
        self.audit_logger = mock.MagicMock()
        self.incident_response = IncidentResponseSystem(
            storage_provider=self.storage_provider,
            notification_handler=self.notification_handler,
            audit_logger=self.audit_logger
        )
    
    def test_create_incident(self):
        """Test creating an incident."""
        # Create an incident
        incident = self.incident_response.create_incident(
            title="Unauthorized Access Attempt",
            description="Multiple failed login attempts from unknown IP",
            category=IncidentCategory.UNAUTHORIZED_ACCESS,
            severity=IncidentSeverity.HIGH,
            detected_by="security_system",
            tenant_id="tenant123",
            affected_users=["user456"],
            affected_systems=["auth_system"]
        )
        
        self.assertEqual(incident.title, "Unauthorized Access Attempt")
        self.assertEqual(incident.category, IncidentCategory.UNAUTHORIZED_ACCESS)
        self.assertEqual(incident.severity, IncidentSeverity.HIGH)
        self.assertEqual(incident.status, IncidentStatus.DETECTED)
        self.assertEqual(incident.tenant_id, "tenant123")
        
        # Verify audit logging
        self.audit_logger.log_security_event.assert_called()
        
        # Verify notification
        self.assertGreaterEqual(len(self.notification_handler.notifications), 1)
    
    def test_update_incident(self):
        """Test updating an incident."""
        # Create an incident
        incident = self.incident_response.create_incident(
            title="Unauthorized Access Attempt",
            description="Multiple failed login attempts from unknown IP",
            category=IncidentCategory.UNAUTHORIZED_ACCESS,
            severity=IncidentSeverity.HIGH,
            detected_by="security_system",
            tenant_id="tenant123",
            affected_users=["user456"],
            affected_systems=["auth_system"]
        )
        
        # Update the incident
        updated_incident = self.incident_response.update_incident(
            incident_id=incident.incident_id,
            status=IncidentStatus.INVESTIGATING,
            assigned_to="security_analyst",
            user_id="admin"
        )
        
        self.assertEqual(updated_incident.status, IncidentStatus.INVESTIGATING)
        self.assertEqual(updated_incident.assigned_to, "security_analyst")
        
        # Verify audit logging for update
        self.audit_logger.log_security_event.assert_called()
    
    def test_add_incident_event(self):
        """Test adding an event to an incident."""
        # Create an incident
        incident = self.incident_response.create_incident(
            title="Unauthorized Access Attempt",
            description="Multiple failed login attempts from unknown IP",
            category=IncidentCategory.UNAUTHORIZED_ACCESS,
            severity=IncidentSeverity.HIGH,
            detected_by="security_system",
            tenant_id="tenant123",
            affected_users=["user456"],
            affected_systems=["auth_system"]
        )
        
        # Add an event
        event = self.incident_response.add_incident_event(
            incident_id=incident.incident_id,
            event_type="INVESTIGATION",
            user_id="security_analyst",
            details={"findings": "IP address traced to known malicious source"}
        )
        
        self.assertEqual(event.event_type, "INVESTIGATION")
        self.assertEqual(event.user_id, "security_analyst")
        self.assertEqual(event.details["findings"], "IP address traced to known malicious source")
        
        # Verify the event was added to the incident
        updated_incident = self.incident_response.get_incident(incident.incident_id)
        self.assertEqual(len(updated_incident.events), 1)
    
    def test_generate_incident_report(self):
        """Test generating an incident report."""
        # Create an incident
        incident = self.incident_response.create_incident(
            title="Unauthorized Access Attempt",
            description="Multiple failed login attempts from unknown IP",
            category=IncidentCategory.UNAUTHORIZED_ACCESS,
            severity=IncidentSeverity.HIGH,
            detected_by="security_system",
            tenant_id="tenant123",
            affected_users=["user456"],
            affected_systems=["auth_system"]
        )
        
        # Add events and actions
        self.incident_response.add_incident_event(
            incident_id=incident.incident_id,
            event_type="INVESTIGATION",
            user_id="security_analyst",
            details={"findings": "IP address traced to known malicious source"}
        )
        
        self.incident_response.add_incident_action(
            incident_id=incident.incident_id,
            action_type="BLOCK_IP",
            user_id="security_analyst",
            details={"ip_address": "192.168.1.1"},
            status="completed"
        )
        
        # Generate report
        report = self.incident_response.generate_incident_report(incident.incident_id)
        
        self.assertEqual(report["incident_id"], incident.incident_id)
        self.assertEqual(report["title"], incident.title)
        self.assertEqual(report["status"], incident.status.value)
        self.assertGreaterEqual(len(report["timeline"]), 3)  # Creation, event, action


class TestComplianceReporter(unittest.TestCase):
    """Tests for the Compliance Reporter."""
    
    def setUp(self):
        """Set up test environment."""
        self.storage_provider = MockStorageProvider()
        self.notification_handler = MockNotificationHandler()
        self.audit_logger = mock.MagicMock()
        self.compliance_reporter = ComplianceReporter(
            storage_provider=self.storage_provider,
            notification_handler=self.notification_handler,
            audit_logger=self.audit_logger
        )
    
    def test_add_requirement(self):
        """Test adding a compliance requirement."""
        # Add a requirement
        requirement = self.compliance_reporter.add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Data Processing Agreement",
            description="Ensure a DPA is in place with the Gemini API provider",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["legal_review", "contract_management"],
            evidence_required=["signed_dpa", "legal_review_documentation"],
            user_id="compliance_officer"
        )
        
        self.assertEqual(requirement.framework, ComplianceFramework.GDPR)
        self.assertEqual(requirement.title, "Data Processing Agreement")
        self.assertEqual(requirement.risk_level, ComplianceRiskLevel.HIGH)
        
        # Verify audit logging
        self.audit_logger.log_security_event.assert_called()
    
    def test_create_assessment(self):
        """Test creating a compliance assessment."""
        # Add a requirement
        requirement = self.compliance_reporter.add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Data Processing Agreement",
            description="Ensure a DPA is in place with the Gemini API provider",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["legal_review", "contract_management"],
            evidence_required=["signed_dpa", "legal_review_documentation"],
            user_id="compliance_officer"
        )
        
        # Create an assessment
        assessment = self.compliance_reporter.create_assessment(
            requirement_id=requirement.requirement_id,
            tenant_id="tenant123",
            status=ComplianceStatus.COMPLIANT,
            assessed_by="compliance_officer",
            evidence=[
                {"type": "document", "id": "dpa_123", "name": "Signed DPA"},
                {"type": "document", "id": "review_456", "name": "Legal Review"}
            ],
            notes="DPA signed and reviewed by legal team"
        )
        
        self.assertEqual(assessment.requirement_id, requirement.requirement_id)
        self.assertEqual(assessment.tenant_id, "tenant123")
        self.assertEqual(assessment.status, ComplianceStatus.COMPLIANT)
        self.assertEqual(len(assessment.evidence), 2)
        
        # Verify audit logging
        self.audit_logger.log_security_event.assert_called()
    
    def test_record_violation(self):
        """Test recording a compliance violation."""
        # Add a requirement
        requirement = self.compliance_reporter.add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Data Processing Agreement",
            description="Ensure a DPA is in place with the Gemini API provider",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["legal_review", "contract_management"],
            evidence_required=["signed_dpa", "legal_review_documentation"],
            user_id="compliance_officer"
        )
        
        # Record a violation
        violation = self.compliance_reporter.record_violation(
            requirement_id=requirement.requirement_id,
            tenant_id="tenant123",
            description="DPA expired and not renewed",
            detected_by="compliance_system"
        )
        
        self.assertEqual(violation.requirement_id, requirement.requirement_id)
        self.assertEqual(violation.tenant_id, "tenant123")
        self.assertEqual(violation.status, "open")
        self.assertEqual(violation.severity, ComplianceRiskLevel.HIGH)  # Inherited from requirement
        
        # Verify audit logging
        self.audit_logger.log_security_event.assert_called()
        
        # Verify notification
        self.assertGreaterEqual(len(self.notification_handler.notifications), 1)
    
    def test_generate_compliance_report(self):
        """Test generating a compliance report."""
        # Add requirements
        gdpr_req = self.compliance_reporter.add_requirement(
            framework=ComplianceFramework.GDPR,
            title="Data Processing Agreement",
            description="Ensure a DPA is in place with the Gemini API provider",
            risk_level=ComplianceRiskLevel.HIGH,
            controls=["legal_review", "contract_management"],
            evidence_required=["signed_dpa", "legal_review_documentation"]
        )
        
        hipaa_req = self.compliance_reporter.add_requirement(
            framework=ComplianceFramework.HIPAA,
            title="Business Associate Agreement",
            description="Ensure a BAA is in place with the Gemini API provider",
            risk_level=ComplianceRiskLevel.CRITICAL,
            controls=["legal_review", "contract_management"],
            evidence_required=["signed_baa", "legal_review_documentation"]
        )
        
        # Create assessments
        self.compliance_reporter.create_assessment(
            requirement_id=gdpr_req.requirement_id,
            tenant_id="tenant123",
            status=ComplianceStatus.COMPLIANT,
            assessed_by="compliance_officer",
            evidence=[{"type": "document", "id": "dpa_123", "name": "Signed DPA"}],
            notes="DPA signed and reviewed"
        )
        
        self.compliance_reporter.create_assessment(
            requirement_id=hipaa_req.requirement_id,
            tenant_id="tenant123",
            status=ComplianceStatus.NON_COMPLIANT,
            assessed_by="compliance_officer",
            evidence=[],
            notes="BAA not yet signed"
        )
        
        # Generate report
        report = self.compliance_reporter.generate_compliance_report(
            tenant_id="tenant123",
            include_evidence=True
        )
        
        self.assertEqual(report["tenant_id"], "tenant123")
        self.assertEqual(report["summary"]["total_requirements"], 2)
        self.assertEqual(report["summary"]["compliant_requirements"], 1)
        self.assertEqual(report["summary"]["non_compliant_requirements"], 1)
        self.assertEqual(len(report["requirements"]), 2)
        
        # Verify audit logging
        self.audit_logger.log_security_event.assert_called()


if __name__ == "__main__":
    unittest.main()
