#!/usr/bin/env python3
"""
Test suite for the Compliance Framework.

This module provides comprehensive tests for the compliance framework
components of the ApexAgent system.
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import threading
import time
import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from compliance.compliance_framework import (
    ComplianceSystem, ComplianceConfig, ComplianceStandard, ComplianceControl,
    ComplianceRequirement, ComplianceAudit, ComplianceReport, ComplianceStatus,
    ComplianceSeverity, DataProcessor, ConsentManager, AuditLogger
)

class TestComplianceSystem(unittest.TestCase):
    """Test cases for the ComplianceSystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ComplianceConfig(
            enabled=True,
            data_directory=self.temp_dir,
            active_standards=[
                ComplianceStandard.GDPR,
                ComplianceStandard.HIPAA,
                ComplianceStandard.SOC2
            ],
            audit_logging_enabled=True,
            consent_management_enabled=True,
            data_retention_days=90,
            auto_remediation_enabled=True
        )
        self.compliance_system = ComplianceSystem.get_instance()
        self.compliance_system.initialize(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.compliance_system.shutdown()
    
    def test_singleton_pattern(self):
        """Test that the compliance system follows the singleton pattern."""
        instance1 = ComplianceSystem.get_instance()
        instance2 = ComplianceSystem.get_instance()
        self.assertIs(instance1, instance2)
    
    def test_register_compliance_control(self):
        """Test registering a compliance control."""
        control = ComplianceControl(
            control_id="access-control-1",
            name="Access Control Policy",
            description="Defines access control requirements",
            standards=[ComplianceStandard.GDPR, ComplianceStandard.SOC2],
            requirements=[
                ComplianceRequirement(
                    req_id="req-1",
                    description="All access must be authenticated",
                    severity=ComplianceSeverity.HIGH
                )
            ]
        )
        self.compliance_system.register_compliance_control(control)
        
        # Verify control was registered
        registered_control = self.compliance_system.get_compliance_control("access-control-1")
        self.assertEqual(registered_control, control)
    
    def test_get_controls_by_standard(self):
        """Test getting controls by standard."""
        # Register controls for different standards
        control1 = ComplianceControl(
            control_id="gdpr-control-1",
            name="GDPR Control 1",
            standards=[ComplianceStandard.GDPR]
        )
        control2 = ComplianceControl(
            control_id="hipaa-control-1",
            name="HIPAA Control 1",
            standards=[ComplianceStandard.HIPAA]
        )
        control3 = ComplianceControl(
            control_id="shared-control-1",
            name="Shared Control 1",
            standards=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA]
        )
        
        self.compliance_system.register_compliance_control(control1)
        self.compliance_system.register_compliance_control(control2)
        self.compliance_system.register_compliance_control(control3)
        
        # Get GDPR controls
        gdpr_controls = self.compliance_system.get_controls_by_standard(ComplianceStandard.GDPR)
        self.assertEqual(len(gdpr_controls), 2)
        self.assertIn(control1, gdpr_controls)
        self.assertIn(control3, gdpr_controls)
        
        # Get HIPAA controls
        hipaa_controls = self.compliance_system.get_controls_by_standard(ComplianceStandard.HIPAA)
        self.assertEqual(len(hipaa_controls), 2)
        self.assertIn(control2, hipaa_controls)
        self.assertIn(control3, hipaa_controls)
    
    def test_evaluate_compliance(self):
        """Test evaluating compliance for a control."""
        # Register a control
        control = ComplianceControl(
            control_id="data-encryption",
            name="Data Encryption",
            description="Ensures data is encrypted at rest and in transit",
            standards=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA],
            requirements=[
                ComplianceRequirement(
                    req_id="req-1",
                    description="Data must be encrypted at rest",
                    severity=ComplianceSeverity.HIGH
                ),
                ComplianceRequirement(
                    req_id="req-2",
                    description="Data must be encrypted in transit",
                    severity=ComplianceSeverity.HIGH
                )
            ]
        )
        self.compliance_system.register_compliance_control(control)
        
        # Mock evaluation function
        def evaluate_func(control):
            results = {}
            for req in control.requirements:
                # Simulate req-1 passing and req-2 failing
                if req.req_id == "req-1":
                    results[req.req_id] = (True, "Encryption at rest is enabled")
                else:
                    results[req.req_id] = (False, "TLS is not configured")
            return results
        
        # Evaluate compliance
        status, results = self.compliance_system.evaluate_compliance(
            "data-encryption", evaluate_func
        )
        
        # Verify results
        self.assertEqual(status, ComplianceStatus.PARTIAL)
        self.assertTrue(results["req-1"][0])
        self.assertFalse(results["req-2"][0])
    
    @patch('compliance.compliance_framework.datetime')
    def test_run_compliance_audit(self, mock_datetime):
        """Test running a compliance audit."""
        # Mock datetime
        mock_now = datetime.datetime(2023, 1, 1, 12, 0)
        mock_datetime.now.return_value = mock_now
        
        # Register controls
        control1 = ComplianceControl(
            control_id="control-1",
            name="Control 1",
            standards=[ComplianceStandard.GDPR]
        )
        control2 = ComplianceControl(
            control_id="control-2",
            name="Control 2",
            standards=[ComplianceStandard.GDPR]
        )
        
        self.compliance_system.register_compliance_control(control1)
        self.compliance_system.register_compliance_control(control2)
        
        # Mock evaluation function
        def evaluate_func(control):
            # Simulate control-1 passing and control-2 failing
            if control.control_id == "control-1":
                return {req.req_id: (True, "Passed") for req in control.requirements}
            else:
                return {req.req_id: (False, "Failed") for req in control.requirements}
        
        # Run audit
        with patch.object(self.compliance_system, '_store_audit_report') as mock_store:
            audit_report = self.compliance_system.run_compliance_audit(
                standard=ComplianceStandard.GDPR,
                evaluate_func=evaluate_func
            )
            
            # Verify audit report
            self.assertEqual(audit_report.standard, ComplianceStandard.GDPR)
            self.assertEqual(audit_report.timestamp, mock_now)
            self.assertEqual(len(audit_report.control_results), 2)
            self.assertEqual(audit_report.control_results["control-1"].status, ComplianceStatus.COMPLIANT)
            self.assertEqual(audit_report.control_results["control-2"].status, ComplianceStatus.NON_COMPLIANT)
            
            # Verify report was stored
            mock_store.assert_called_once_with(audit_report)
    
    @patch('compliance.compliance_framework.os.path.exists')
    @patch('compliance.compliance_framework.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_compliance_report(self, mock_file, mock_makedirs, mock_exists):
        """Test generating a compliance report."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Create audit report
        audit_report = ComplianceAudit(
            audit_id="audit-123",
            standard=ComplianceStandard.GDPR,
            timestamp=datetime.datetime(2023, 1, 1, 12, 0),
            control_results={
                "control-1": MagicMock(status=ComplianceStatus.COMPLIANT),
                "control-2": MagicMock(status=ComplianceStatus.NON_COMPLIANT)
            }
        )
        
        # Generate report
        with patch.object(self.compliance_system, 'get_latest_audit') as mock_get_audit:
            mock_get_audit.return_value = audit_report
            
            report_path = self.compliance_system.generate_compliance_report(
                standard=ComplianceStandard.GDPR,
                format="pdf",
                output_path=os.path.join(self.temp_dir, "report.pdf")
            )
            
            # Verify report generation
            mock_makedirs.assert_called_once()
            mock_file.assert_called_once()
            self.assertTrue(report_path.endswith("report.pdf"))

class TestComplianceControl(unittest.TestCase):
    """Test cases for the ComplianceControl class."""
    
    def test_control_creation(self):
        """Test creating a compliance control."""
        control = ComplianceControl(
            control_id="access-control-1",
            name="Access Control Policy",
            description="Defines access control requirements",
            standards=[ComplianceStandard.GDPR, ComplianceStandard.SOC2],
            requirements=[
                ComplianceRequirement(
                    req_id="req-1",
                    description="All access must be authenticated",
                    severity=ComplianceSeverity.HIGH
                )
            ]
        )
        
        self.assertEqual(control.control_id, "access-control-1")
        self.assertEqual(control.name, "Access Control Policy")
        self.assertEqual(control.description, "Defines access control requirements")
        self.assertEqual(len(control.standards), 2)
        self.assertIn(ComplianceStandard.GDPR, control.standards)
        self.assertIn(ComplianceStandard.SOC2, control.standards)
        self.assertEqual(len(control.requirements), 1)
        self.assertEqual(control.requirements[0].req_id, "req-1")
    
    def test_add_requirement(self):
        """Test adding a requirement to a control."""
        control = ComplianceControl(
            control_id="access-control-1",
            name="Access Control Policy"
        )
        
        requirement = ComplianceRequirement(
            req_id="req-1",
            description="All access must be authenticated",
            severity=ComplianceSeverity.HIGH
        )
        
        control.add_requirement(requirement)
        
        self.assertEqual(len(control.requirements), 1)
        self.assertEqual(control.requirements[0], requirement)
    
    def test_to_dict(self):
        """Test converting control to dictionary."""
        control = ComplianceControl(
            control_id="access-control-1",
            name="Access Control Policy",
            description="Defines access control requirements",
            standards=[ComplianceStandard.GDPR],
            requirements=[
                ComplianceRequirement(
                    req_id="req-1",
                    description="All access must be authenticated",
                    severity=ComplianceSeverity.HIGH
                )
            ]
        )
        
        control_dict = control.to_dict()
        
        self.assertEqual(control_dict["control_id"], "access-control-1")
        self.assertEqual(control_dict["name"], "Access Control Policy")
        self.assertEqual(control_dict["description"], "Defines access control requirements")
        self.assertEqual(control_dict["standards"], ["gdpr"])
        self.assertEqual(len(control_dict["requirements"]), 1)
        self.assertEqual(control_dict["requirements"][0]["req_id"], "req-1")
    
    def test_from_dict(self):
        """Test creating control from dictionary."""
        control_dict = {
            "control_id": "access-control-1",
            "name": "Access Control Policy",
            "description": "Defines access control requirements",
            "standards": ["gdpr", "soc2"],
            "requirements": [
                {
                    "req_id": "req-1",
                    "description": "All access must be authenticated",
                    "severity": "high"
                }
            ]
        }
        
        control = ComplianceControl.from_dict(control_dict)
        
        self.assertEqual(control.control_id, "access-control-1")
        self.assertEqual(control.name, "Access Control Policy")
        self.assertEqual(control.description, "Defines access control requirements")
        self.assertEqual(len(control.standards), 2)
        self.assertIn(ComplianceStandard.GDPR, control.standards)
        self.assertIn(ComplianceStandard.SOC2, control.standards)
        self.assertEqual(len(control.requirements), 1)
        self.assertEqual(control.requirements[0].req_id, "req-1")
        self.assertEqual(control.requirements[0].severity, ComplianceSeverity.HIGH)

class TestComplianceRequirement(unittest.TestCase):
    """Test cases for the ComplianceRequirement class."""
    
    def test_requirement_creation(self):
        """Test creating a compliance requirement."""
        requirement = ComplianceRequirement(
            req_id="req-1",
            description="All access must be authenticated",
            severity=ComplianceSeverity.HIGH,
            implementation_notes="Use OAuth 2.0 for authentication"
        )
        
        self.assertEqual(requirement.req_id, "req-1")
        self.assertEqual(requirement.description, "All access must be authenticated")
        self.assertEqual(requirement.severity, ComplianceSeverity.HIGH)
        self.assertEqual(requirement.implementation_notes, "Use OAuth 2.0 for authentication")
    
    def test_to_dict(self):
        """Test converting requirement to dictionary."""
        requirement = ComplianceRequirement(
            req_id="req-1",
            description="All access must be authenticated",
            severity=ComplianceSeverity.HIGH,
            implementation_notes="Use OAuth 2.0 for authentication"
        )
        
        req_dict = requirement.to_dict()
        
        self.assertEqual(req_dict["req_id"], "req-1")
        self.assertEqual(req_dict["description"], "All access must be authenticated")
        self.assertEqual(req_dict["severity"], "high")
        self.assertEqual(req_dict["implementation_notes"], "Use OAuth 2.0 for authentication")
    
    def test_from_dict(self):
        """Test creating requirement from dictionary."""
        req_dict = {
            "req_id": "req-1",
            "description": "All access must be authenticated",
            "severity": "high",
            "implementation_notes": "Use OAuth 2.0 for authentication"
        }
        
        requirement = ComplianceRequirement.from_dict(req_dict)
        
        self.assertEqual(requirement.req_id, "req-1")
        self.assertEqual(requirement.description, "All access must be authenticated")
        self.assertEqual(requirement.severity, ComplianceSeverity.HIGH)
        self.assertEqual(requirement.implementation_notes, "Use OAuth 2.0 for authentication")

class TestComplianceAudit(unittest.TestCase):
    """Test cases for the ComplianceAudit class."""
    
    def test_audit_creation(self):
        """Test creating a compliance audit."""
        audit = ComplianceAudit(
            audit_id="audit-123",
            standard=ComplianceStandard.GDPR,
            timestamp=datetime.datetime(2023, 1, 1, 12, 0),
            control_results={
                "control-1": MagicMock(status=ComplianceStatus.COMPLIANT),
                "control-2": MagicMock(status=ComplianceStatus.NON_COMPLIANT)
            }
        )
        
        self.assertEqual(audit.audit_id, "audit-123")
        self.assertEqual(audit.standard, ComplianceStandard.GDPR)
        self.assertEqual(audit.timestamp, datetime.datetime(2023, 1, 1, 12, 0))
        self.assertEqual(len(audit.control_results), 2)
    
    def test_get_overall_status(self):
        """Test getting overall compliance status."""
        # All compliant
        audit1 = ComplianceAudit(
            audit_id="audit-1",
            standard=ComplianceStandard.GDPR,
            control_results={
                "control-1": MagicMock(status=ComplianceStatus.COMPLIANT),
                "control-2": MagicMock(status=ComplianceStatus.COMPLIANT)
            }
        )
        self.assertEqual(audit1.get_overall_status(), ComplianceStatus.COMPLIANT)
        
        # Mixed status
        audit2 = ComplianceAudit(
            audit_id="audit-2",
            standard=ComplianceStandard.GDPR,
            control_results={
                "control-1": MagicMock(status=ComplianceStatus.COMPLIANT),
                "control-2": MagicMock(status=ComplianceStatus.NON_COMPLIANT)
            }
        )
        self.assertEqual(audit2.get_overall_status(), ComplianceStatus.PARTIAL)
        
        # All non-compliant
        audit3 = ComplianceAudit(
            audit_id="audit-3",
            standard=ComplianceStandard.GDPR,
            control_results={
                "control-1": MagicMock(status=ComplianceStatus.NON_COMPLIANT),
                "control-2": MagicMock(status=ComplianceStatus.NON_COMPLIANT)
            }
        )
        self.assertEqual(audit3.get_overall_status(), ComplianceStatus.NON_COMPLIANT)
    
    def test_to_dict(self):
        """Test converting audit to dictionary."""
        # Create mock control results
        control_result1 = MagicMock()
        control_result1.to_dict.return_value = {"status": "compliant"}
        
        control_result2 = MagicMock()
        control_result2.to_dict.return_value = {"status": "non_compliant"}
        
        audit = ComplianceAudit(
            audit_id="audit-123",
            standard=ComplianceStandard.GDPR,
            timestamp=datetime.datetime(2023, 1, 1, 12, 0),
            control_results={
                "control-1": control_result1,
                "control-2": control_result2
            }
        )
        
        audit_dict = audit.to_dict()
        
        self.assertEqual(audit_dict["audit_id"], "audit-123")
        self.assertEqual(audit_dict["standard"], "gdpr")
        self.assertEqual(audit_dict["timestamp"], "2023-01-01T12:00:00")
        self.assertEqual(len(audit_dict["control_results"]), 2)
        self.assertEqual(audit_dict["control_results"]["control-1"]["status"], "compliant")
        self.assertEqual(audit_dict["control_results"]["control-2"]["status"], "non_compliant")

class TestDataProcessor(unittest.TestCase):
    """Test cases for the DataProcessor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = ComplianceConfig(
            enabled=True,
            data_retention_days=90
        )
        self.processor = DataProcessor(self.config)
    
    def test_process_personal_data(self):
        """Test processing personal data."""
        # Create test data
        personal_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "address": "123 Main St",
            "phone": "555-1234",
            "preferences": {
                "marketing": True,
                "notifications": False
            }
        }
        
        # Process data with anonymization
        processed_data = self.processor.process_personal_data(
            personal_data, anonymize=True
        )
        
        # Verify sensitive fields are anonymized
        self.assertNotEqual(processed_data["name"], "John Doe")
        self.assertNotEqual(processed_data["email"], "john@example.com")
        self.assertNotEqual(processed_data["address"], "123 Main St")
        self.assertNotEqual(processed_data["phone"], "555-1234")
        
        # Non-sensitive fields should remain
        self.assertEqual(processed_data["preferences"]["marketing"], True)
        self.assertEqual(processed_data["preferences"]["notifications"], False)
    
    def test_validate_data_processing(self):
        """Test validating data processing."""
        # Valid processing with consent
        result1 = self.processor.validate_data_processing(
            data_type="personal",
            purpose="marketing",
            has_consent=True,
            retention_period=30
        )
        self.assertTrue(result1)
        
        # Invalid processing without consent
        result2 = self.processor.validate_data_processing(
            data_type="personal",
            purpose="marketing",
            has_consent=False,
            retention_period=30
        )
        self.assertFalse(result2)
        
        # Invalid processing with excessive retention
        result3 = self.processor.validate_data_processing(
            data_type="personal",
            purpose="marketing",
            has_consent=True,
            retention_period=365  # Exceeds config.data_retention_days
        )
        self.assertFalse(result3)
    
    def test_apply_data_retention_policy(self):
        """Test applying data retention policy."""
        # Create test data with timestamps
        data_records = [
            {"id": 1, "created_at": datetime.datetime.now() - datetime.timedelta(days=100)},
            {"id": 2, "created_at": datetime.datetime.now() - datetime.timedelta(days=50)},
            {"id": 3, "created_at": datetime.datetime.now() - datetime.timedelta(days=10)}
        ]
        
        # Apply retention policy (90 days)
        retained_records = self.processor.apply_data_retention_policy(data_records)
        
        # Verify old records are removed
        self.assertEqual(len(retained_records), 2)
        self.assertEqual(retained_records[0]["id"], 2)
        self.assertEqual(retained_records[1]["id"], 3)

class TestConsentManager(unittest.TestCase):
    """Test cases for the ConsentManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ComplianceConfig(
            enabled=True,
            data_directory=self.temp_dir,
            consent_management_enabled=True
        )
        self.consent_manager = ConsentManager(self.config)
    
    def test_record_consent(self):
        """Test recording user consent."""
        # Record consent
        with patch.object(self.consent_manager, '_store_consent') as mock_store:
            consent_id = self.consent_manager.record_consent(
                user_id="user-123",
                purpose="marketing",
                granted=True,
                timestamp=datetime.datetime(2023, 1, 1, 12, 0)
            )
            
            # Verify consent was stored
            mock_store.assert_called_once()
            args, _ = mock_store.call_args
            consent_record = args[0]
            
            self.assertEqual(consent_record.user_id, "user-123")
            self.assertEqual(consent_record.purpose, "marketing")
            self.assertTrue(consent_record.granted)
            self.assertEqual(consent_record.timestamp, datetime.datetime(2023, 1, 1, 12, 0))
            self.assertIsNotNone(consent_id)
    
    @patch('compliance.compliance_framework.ConsentManager._load_consent')
    def test_check_consent(self, mock_load):
        """Test checking user consent."""
        # Mock loaded consent
        mock_load.return_value = MagicMock(
            user_id="user-123",
            purpose="marketing",
            granted=True,
            timestamp=datetime.datetime(2023, 1, 1, 12, 0)
        )
        
        # Check consent
        has_consent = self.consent_manager.check_consent(
            user_id="user-123",
            purpose="marketing"
        )
        
        # Verify consent check
        self.assertTrue(has_consent)
        mock_load.assert_called_once()
    
    @patch('compliance.compliance_framework.ConsentManager._load_consent')
    def test_revoke_consent(self, mock_load):
        """Test revoking user consent."""
        # Mock loaded consent
        mock_consent = MagicMock(
            user_id="user-123",
            purpose="marketing",
            granted=True,
            timestamp=datetime.datetime(2023, 1, 1, 12, 0)
        )
        mock_load.return_value = mock_consent
        
        # Revoke consent
        with patch.object(self.consent_manager, '_store_consent') as mock_store:
            success = self.consent_manager.revoke_consent(
                user_id="user-123",
                purpose="marketing"
            )
            
            # Verify consent was revoked
            self.assertTrue(success)
            mock_store.assert_called_once()
            args, _ = mock_store.call_args
            consent_record = args[0]
            
            self.assertEqual(consent_record.user_id, "user-123")
            self.assertEqual(consent_record.purpose, "marketing")
            self.assertFalse(consent_record.granted)
    
    def test_get_consent_history(self):
        """Test getting consent history for a user."""
        # Mock consent records
        self.consent_manager._consent_records = {
            "user-123": {
                "marketing": [
                    MagicMock(
                        consent_id="consent-1",
                        user_id="user-123",
                        purpose="marketing",
                        granted=True,
                        timestamp=datetime.datetime(2023, 1, 1, 12, 0)
                    ),
                    MagicMock(
                        consent_id="consent-2",
                        user_id="user-123",
                        purpose="marketing",
                        granted=False,
                        timestamp=datetime.datetime(2023, 1, 2, 12, 0)
                    )
                ],
                "analytics": [
                    MagicMock(
                        consent_id="consent-3",
                        user_id="user-123",
                        purpose="analytics",
                        granted=True,
                        timestamp=datetime.datetime(2023, 1, 1, 12, 0)
                    )
                ]
            }
        }
        
        # Get consent history
        history = self.consent_manager.get_consent_history(
            user_id="user-123",
            purpose="marketing"
        )
        
        # Verify history
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].consent_id, "consent-1")
        self.assertEqual(history[1].consent_id, "consent-2")
        
        # Get all consent history
        all_history = self.consent_manager.get_consent_history(
            user_id="user-123"
        )
        
        # Verify all history
        self.assertEqual(len(all_history), 3)

class TestAuditLogger(unittest.TestCase):
    """Test cases for the AuditLogger class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ComplianceConfig(
            enabled=True,
            data_directory=self.temp_dir,
            audit_logging_enabled=True
        )
        self.audit_logger = AuditLogger(self.config)
    
    @patch('compliance.compliance_framework.os.path.exists')
    @patch('compliance.compliance_framework.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_log_event(self, mock_file, mock_makedirs, mock_exists):
        """Test logging an audit event."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Log event
        event_id = self.audit_logger.log_event(
            event_type="data_access",
            user_id="user-123",
            resource="customer_data",
            action="read",
            status="success",
            details={"record_id": "record-456"}
        )
        
        # Verify event was logged
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        mock_file().write.assert_called_once()
        self.assertIsNotNone(event_id)
    
    @patch('compliance.compliance_framework.glob.glob')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_audit_logs(self, mock_file, mock_glob):
        """Test getting audit logs."""
        # Mock glob to return file paths
        mock_glob.return_value = [
            os.path.join(self.temp_dir, "audit_logs", "2023-01-01", "log1.json"),
            os.path.join(self.temp_dir, "audit_logs", "2023-01-01", "log2.json")
        ]
        
        # Mock file content
        mock_file.return_value.__enter__.return_value.read.side_effect = [
            json.dumps({
                "event_id": "event-1",
                "event_type": "data_access",
                "timestamp": "2023-01-01T12:00:00",
                "user_id": "user-123",
                "resource": "customer_data",
                "action": "read",
                "status": "success"
            }),
            json.dumps({
                "event_id": "event-2",
                "event_type": "authentication",
                "timestamp": "2023-01-01T12:05:00",
                "user_id": "user-123",
                "resource": "login",
                "action": "login",
                "status": "success"
            })
        ]
        
        # Get audit logs
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime(2023, 1, 2)
        logs = self.audit_logger.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            event_type="data_access"
        )
        
        # Verify logs
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].event_id, "event-1")
        self.assertEqual(logs[0].event_type, "data_access")
        
        # Get all logs
        all_logs = self.audit_logger.get_audit_logs(
            start_date=start_date,
            end_date=end_date
        )
        
        # Verify all logs
        self.assertEqual(len(all_logs), 2)
    
    @patch('compliance.compliance_framework.os.path.exists')
    @patch('compliance.compliance_framework.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_audit_logs(self, mock_file, mock_makedirs, mock_exists):
        """Test exporting audit logs."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Mock get_audit_logs
        with patch.object(self.audit_logger, 'get_audit_logs') as mock_get_logs:
            mock_get_logs.return_value = [
                MagicMock(
                    event_id="event-1",
                    event_type="data_access",
                    to_dict=lambda: {"event_id": "event-1", "event_type": "data_access"}
                ),
                MagicMock(
                    event_id="event-2",
                    event_type="authentication",
                    to_dict=lambda: {"event_id": "event-2", "event_type": "authentication"}
                )
            ]
            
            # Export logs
            export_path = self.audit_logger.export_audit_logs(
                start_date=datetime.datetime(2023, 1, 1),
                end_date=datetime.datetime(2023, 1, 2),
                format="json",
                output_path=os.path.join(self.temp_dir, "export.json")
            )
            
            # Verify export
            mock_makedirs.assert_called_once()
            mock_file.assert_called_once()
            self.assertTrue(export_path.endswith("export.json"))

if __name__ == '__main__':
    unittest.main()
