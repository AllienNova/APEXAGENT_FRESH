#!/usr/bin/env python3
"""
Test suite for the Accessibility Framework.

This module provides comprehensive tests for the accessibility framework
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
from accessibility.accessibility_framework import (
    AccessibilitySystem, AccessibilityConfig, AccessibilityStandard,
    AccessibilityRule, AccessibilityViolation, AccessibilitySeverity,
    AccessibilityReport, AccessibilityScanner, ColorContrastChecker,
    KeyboardNavigationChecker, ScreenReaderCompatibilityChecker,
    AccessibilityOverlay
)

class TestAccessibilitySystem(unittest.TestCase):
    """Test cases for the AccessibilitySystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AccessibilityConfig(
            enabled=True,
            data_directory=self.temp_dir,
            standards=[
                AccessibilityStandard.WCAG_2_1_AA,
                AccessibilityStandard.SECTION_508
            ],
            auto_scan_enabled=True,
            overlay_enabled=True,
            report_generation_enabled=True
        )
        self.accessibility_system = AccessibilitySystem.get_instance()
        self.accessibility_system.initialize(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.accessibility_system.shutdown()
    
    def test_singleton_pattern(self):
        """Test that the accessibility system follows the singleton pattern."""
        instance1 = AccessibilitySystem.get_instance()
        instance2 = AccessibilitySystem.get_instance()
        self.assertIs(instance1, instance2)
    
    def test_register_accessibility_rule(self):
        """Test registering an accessibility rule."""
        # Create a rule
        rule = AccessibilityRule(
            rule_id="color-contrast",
            name="Color Contrast",
            description="Ensure sufficient contrast between text and background",
            standard=AccessibilityStandard.WCAG_2_1_AA,
            severity=AccessibilitySeverity.CRITICAL
        )
        
        # Register the rule
        self.accessibility_system.register_accessibility_rule(rule)
        
        # Verify rule was registered
        registered_rule = self.accessibility_system.get_accessibility_rule("color-contrast")
        self.assertEqual(registered_rule, rule)
    
    def test_get_rules_by_standard(self):
        """Test getting rules by standard."""
        # Register rules for different standards
        rule1 = AccessibilityRule(
            rule_id="color-contrast",
            name="Color Contrast",
            standard=AccessibilityStandard.WCAG_2_1_AA
        )
        rule2 = AccessibilityRule(
            rule_id="keyboard-navigation",
            name="Keyboard Navigation",
            standard=AccessibilityStandard.WCAG_2_1_AA
        )
        rule3 = AccessibilityRule(
            rule_id="section-508-compliance",
            name="Section 508 Compliance",
            standard=AccessibilityStandard.SECTION_508
        )
        
        self.accessibility_system.register_accessibility_rule(rule1)
        self.accessibility_system.register_accessibility_rule(rule2)
        self.accessibility_system.register_accessibility_rule(rule3)
        
        # Get WCAG rules
        wcag_rules = self.accessibility_system.get_rules_by_standard(AccessibilityStandard.WCAG_2_1_AA)
        self.assertEqual(len(wcag_rules), 2)
        self.assertIn(rule1, wcag_rules)
        self.assertIn(rule2, wcag_rules)
        
        # Get Section 508 rules
        section_508_rules = self.accessibility_system.get_rules_by_standard(AccessibilityStandard.SECTION_508)
        self.assertEqual(len(section_508_rules), 1)
        self.assertIn(rule3, section_508_rules)
    
    def test_scan_element(self):
        """Test scanning an element for accessibility violations."""
        # Register rules
        rule1 = AccessibilityRule(
            rule_id="color-contrast",
            name="Color Contrast",
            standard=AccessibilityStandard.WCAG_2_1_AA,
            check_func=lambda element: [
                AccessibilityViolation(
                    rule_id="color-contrast",
                    element=element,
                    message="Insufficient contrast ratio"
                )
            ] if element.get("color") == "light-gray" else []
        )
        
        rule2 = AccessibilityRule(
            rule_id="alt-text",
            name="Alt Text",
            standard=AccessibilityStandard.WCAG_2_1_AA,
            check_func=lambda element: [
                AccessibilityViolation(
                    rule_id="alt-text",
                    element=element,
                    message="Missing alt text"
                )
            ] if element.get("type") == "image" and not element.get("alt") else []
        )
        
        self.accessibility_system.register_accessibility_rule(rule1)
        self.accessibility_system.register_accessibility_rule(rule2)
        
        # Create test elements
        element1 = {
            "id": "header",
            "type": "text",
            "color": "light-gray"
        }
        
        element2 = {
            "id": "logo",
            "type": "image",
            "alt": "Company Logo"
        }
        
        element3 = {
            "id": "banner",
            "type": "image"
        }
        
        # Scan elements
        violations1 = self.accessibility_system.scan_element(element1)
        violations2 = self.accessibility_system.scan_element(element2)
        violations3 = self.accessibility_system.scan_element(element3)
        
        # Verify violations
        self.assertEqual(len(violations1), 1)
        self.assertEqual(violations1[0].rule_id, "color-contrast")
        
        self.assertEqual(len(violations2), 0)
        
        self.assertEqual(len(violations3), 1)
        self.assertEqual(violations3[0].rule_id, "alt-text")
    
    def test_scan_page(self):
        """Test scanning a page for accessibility violations."""
        # Register rules
        rule = AccessibilityRule(
            rule_id="color-contrast",
            name="Color Contrast",
            standard=AccessibilityStandard.WCAG_2_1_AA,
            check_func=lambda element: [
                AccessibilityViolation(
                    rule_id="color-contrast",
                    element=element,
                    message="Insufficient contrast ratio"
                )
            ] if element.get("color") == "light-gray" else []
        )
        
        self.accessibility_system.register_accessibility_rule(rule)
        
        # Create test page
        page = {
            "url": "https://example.com",
            "elements": [
                {
                    "id": "header",
                    "type": "text",
                    "color": "light-gray"
                },
                {
                    "id": "content",
                    "type": "text",
                    "color": "black"
                },
                {
                    "id": "footer",
                    "type": "text",
                    "color": "light-gray"
                }
            ]
        }
        
        # Scan page
        with patch.object(self.accessibility_system, '_track_scan') as mock_track:
            violations = self.accessibility_system.scan_page(page)
            
            # Verify violations
            self.assertEqual(len(violations), 2)
            self.assertEqual(violations[0].rule_id, "color-contrast")
            self.assertEqual(violations[1].rule_id, "color-contrast")
            
            # Verify scan was tracked
            mock_track.assert_called_once()
    
    @patch('accessibility.accessibility_framework.datetime')
    def test_generate_accessibility_report(self, mock_datetime):
        """Test generating an accessibility report."""
        # Mock datetime
        mock_now = datetime.datetime(2023, 1, 1, 12, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        # Register rules
        rule1 = AccessibilityRule(
            rule_id="color-contrast",
            name="Color Contrast",
            standard=AccessibilityStandard.WCAG_2_1_AA
        )
        
        rule2 = AccessibilityRule(
            rule_id="alt-text",
            name="Alt Text",
            standard=AccessibilityStandard.WCAG_2_1_AA
        )
        
        self.accessibility_system.register_accessibility_rule(rule1)
        self.accessibility_system.register_accessibility_rule(rule2)
        
        # Create violations
        violations = [
            AccessibilityViolation(
                rule_id="color-contrast",
                element={"id": "header"},
                message="Insufficient contrast ratio"
            ),
            AccessibilityViolation(
                rule_id="alt-text",
                element={"id": "logo"},
                message="Missing alt text"
            )
        ]
        
        # Generate report
        with patch.object(self.accessibility_system, '_store_report') as mock_store:
            report = self.accessibility_system.generate_accessibility_report(
                url="https://example.com",
                violations=violations
            )
            
            # Verify report
            self.assertEqual(report.url, "https://example.com")
            self.assertEqual(report.timestamp, mock_now)
            self.assertEqual(len(report.violations), 2)
            self.assertEqual(report.violations[0].rule_id, "color-contrast")
            self.assertEqual(report.violations[1].rule_id, "alt-text")
            
            # Verify report was stored
            mock_store.assert_called_once_with(report)
    
    @patch('accessibility.accessibility_framework.os.path.exists')
    @patch('accessibility.accessibility_framework.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_report(self, mock_file, mock_makedirs, mock_exists):
        """Test exporting an accessibility report."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Create report
        report = AccessibilityReport(
            report_id="report-123",
            url="https://example.com",
            timestamp=datetime.datetime(2023, 1, 1, 12, 0),
            violations=[
                AccessibilityViolation(
                    rule_id="color-contrast",
                    element={"id": "header"},
                    message="Insufficient contrast ratio"
                )
            ]
        )
        
        # Export report
        export_path = self.accessibility_system.export_report(
            report=report,
            format="json",
            output_path=os.path.join(self.temp_dir, "report.json")
        )
        
        # Verify export
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        self.assertTrue(export_path.endswith("report.json"))
    
    def test_get_accessibility_score(self):
        """Test calculating accessibility score."""
        # Create violations with different severities
        violations = [
            AccessibilityViolation(
                rule_id="rule1",
                element={"id": "elem1"},
                severity=AccessibilitySeverity.CRITICAL
            ),
            AccessibilityViolation(
                rule_id="rule2",
                element={"id": "elem2"},
                severity=AccessibilitySeverity.HIGH
            ),
            AccessibilityViolation(
                rule_id="rule3",
                element={"id": "elem3"},
                severity=AccessibilitySeverity.MEDIUM
            ),
            AccessibilityViolation(
                rule_id="rule4",
                element={"id": "elem4"},
                severity=AccessibilitySeverity.LOW
            )
        ]
        
        # Calculate score
        score = self.accessibility_system.get_accessibility_score(violations)
        
        # Verify score (lower is worse)
        self.assertLess(score, 100)
        self.assertGreaterEqual(score, 0)
    
    def test_get_remediation_suggestions(self):
        """Test getting remediation suggestions for violations."""
        # Register rules with remediation suggestions
        rule = AccessibilityRule(
            rule_id="color-contrast",
            name="Color Contrast",
            standard=AccessibilityStandard.WCAG_2_1_AA,
            remediation="Increase contrast ratio to at least 4.5:1 for normal text"
        )
        
        self.accessibility_system.register_accessibility_rule(rule)
        
        # Create violation
        violation = AccessibilityViolation(
            rule_id="color-contrast",
            element={"id": "header", "color": "light-gray"},
            message="Insufficient contrast ratio"
        )
        
        # Get remediation suggestion
        suggestion = self.accessibility_system.get_remediation_suggestion(violation)
        
        # Verify suggestion
        self.assertEqual(suggestion, "Increase contrast ratio to at least 4.5:1 for normal text")

class TestAccessibilityRule(unittest.TestCase):
    """Test cases for the AccessibilityRule class."""
    
    def test_rule_creation(self):
        """Test creating an accessibility rule."""
        rule = AccessibilityRule(
            rule_id="color-contrast",
            name="Color Contrast",
            description="Ensure sufficient contrast between text and background",
            standard=AccessibilityStandard.WCAG_2_1_AA,
            severity=AccessibilitySeverity.CRITICAL,
            remediation="Increase contrast ratio to at least 4.5:1 for normal text"
        )
        
        self.assertEqual(rule.rule_id, "color-contrast")
        self.assertEqual(rule.name, "Color Contrast")
        self.assertEqual(rule.description, "Ensure sufficient contrast between text and background")
        self.assertEqual(rule.standard, AccessibilityStandard.WCAG_2_1_AA)
        self.assertEqual(rule.severity, AccessibilitySeverity.CRITICAL)
        self.assertEqual(rule.remediation, "Increase contrast ratio to at least 4.5:1 for normal text")
    
    def test_check_element(self):
        """Test checking an element against a rule."""
        # Create rule with check function
        def check_func(element):
            if element.get("type") == "image" and not element.get("alt"):
                return [
                    AccessibilityViolation(
                        rule_id="alt-text",
                        element=element,
                        message="Missing alt text"
                    )
                ]
            return []
        
        rule = AccessibilityRule(
            rule_id="alt-text",
            name="Alt Text",
            standard=AccessibilityStandard.WCAG_2_1_AA,
            check_func=check_func
        )
        
        # Check valid element
        element1 = {
            "id": "logo",
            "type": "image",
            "alt": "Company Logo"
        }
        
        violations1 = rule.check_element(element1)
        self.assertEqual(len(violations1), 0)
        
        # Check invalid element
        element2 = {
            "id": "banner",
            "type": "image"
        }
        
        violations2 = rule.check_element(element2)
        self.assertEqual(len(violations2), 1)
        self.assertEqual(violations2[0].rule_id, "alt-text")
        self.assertEqual(violations2[0].message, "Missing alt text")
    
    def test_to_dict(self):
        """Test converting rule to dictionary."""
        rule = AccessibilityRule(
            rule_id="color-contrast",
            name="Color Contrast",
            description="Ensure sufficient contrast between text and background",
            standard=AccessibilityStandard.WCAG_2_1_AA,
            severity=AccessibilitySeverity.CRITICAL,
            remediation="Increase contrast ratio to at least 4.5:1 for normal text"
        )
        
        rule_dict = rule.to_dict()
        
        self.assertEqual(rule_dict["rule_id"], "color-contrast")
        self.assertEqual(rule_dict["name"], "Color Contrast")
        self.assertEqual(rule_dict["description"], "Ensure sufficient contrast between text and background")
        self.assertEqual(rule_dict["standard"], "wcag_2_1_aa")
        self.assertEqual(rule_dict["severity"], "critical")
        self.assertEqual(rule_dict["remediation"], "Increase contrast ratio to at least 4.5:1 for normal text")
    
    def test_from_dict(self):
        """Test creating rule from dictionary."""
        rule_dict = {
            "rule_id": "color-contrast",
            "name": "Color Contrast",
            "description": "Ensure sufficient contrast between text and background",
            "standard": "wcag_2_1_aa",
            "severity": "critical",
            "remediation": "Increase contrast ratio to at least 4.5:1 for normal text"
        }
        
        rule = AccessibilityRule.from_dict(rule_dict)
        
        self.assertEqual(rule.rule_id, "color-contrast")
        self.assertEqual(rule.name, "Color Contrast")
        self.assertEqual(rule.description, "Ensure sufficient contrast between text and background")
        self.assertEqual(rule.standard, AccessibilityStandard.WCAG_2_1_AA)
        self.assertEqual(rule.severity, AccessibilitySeverity.CRITICAL)
        self.assertEqual(rule.remediation, "Increase contrast ratio to at least 4.5:1 for normal text")

class TestAccessibilityViolation(unittest.TestCase):
    """Test cases for the AccessibilityViolation class."""
    
    def test_violation_creation(self):
        """Test creating an accessibility violation."""
        violation = AccessibilityViolation(
            rule_id="color-contrast",
            element={"id": "header", "color": "light-gray"},
            message="Insufficient contrast ratio",
            severity=AccessibilitySeverity.CRITICAL,
            details={"contrast_ratio": 2.5, "required_ratio": 4.5}
        )
        
        self.assertEqual(violation.rule_id, "color-contrast")
        self.assertEqual(violation.element["id"], "header")
        self.assertEqual(violation.message, "Insufficient contrast ratio")
        self.assertEqual(violation.severity, AccessibilitySeverity.CRITICAL)
        self.assertEqual(violation.details["contrast_ratio"], 2.5)
        self.assertEqual(violation.details["required_ratio"], 4.5)
    
    def test_to_dict(self):
        """Test converting violation to dictionary."""
        violation = AccessibilityViolation(
            rule_id="color-contrast",
            element={"id": "header", "color": "light-gray"},
            message="Insufficient contrast ratio",
            severity=AccessibilitySeverity.CRITICAL,
            details={"contrast_ratio": 2.5, "required_ratio": 4.5}
        )
        
        violation_dict = violation.to_dict()
        
        self.assertEqual(violation_dict["rule_id"], "color-contrast")
        self.assertEqual(violation_dict["element"]["id"], "header")
        self.assertEqual(violation_dict["message"], "Insufficient contrast ratio")
        self.assertEqual(violation_dict["severity"], "critical")
        self.assertEqual(violation_dict["details"]["contrast_ratio"], 2.5)
        self.assertEqual(violation_dict["details"]["required_ratio"], 4.5)
    
    def test_from_dict(self):
        """Test creating violation from dictionary."""
        violation_dict = {
            "rule_id": "color-contrast",
            "element": {"id": "header", "color": "light-gray"},
            "message": "Insufficient contrast ratio",
            "severity": "critical",
            "details": {"contrast_ratio": 2.5, "required_ratio": 4.5}
        }
        
        violation = AccessibilityViolation.from_dict(violation_dict)
        
        self.assertEqual(violation.rule_id, "color-contrast")
        self.assertEqual(violation.element["id"], "header")
        self.assertEqual(violation.message, "Insufficient contrast ratio")
        self.assertEqual(violation.severity, AccessibilitySeverity.CRITICAL)
        self.assertEqual(violation.details["contrast_ratio"], 2.5)
        self.assertEqual(violation.details["required_ratio"], 4.5)

class TestAccessibilityReport(unittest.TestCase):
    """Test cases for the AccessibilityReport class."""
    
    def test_report_creation(self):
        """Test creating an accessibility report."""
        report = AccessibilityReport(
            report_id="report-123",
            url="https://example.com",
            timestamp=datetime.datetime(2023, 1, 1, 12, 0),
            violations=[
                AccessibilityViolation(
                    rule_id="color-contrast",
                    element={"id": "header"},
                    message="Insufficient contrast ratio"
                ),
                AccessibilityViolation(
                    rule_id="alt-text",
                    element={"id": "logo"},
                    message="Missing alt text"
                )
            ],
            standards=[AccessibilityStandard.WCAG_2_1_AA]
        )
        
        self.assertEqual(report.report_id, "report-123")
        self.assertEqual(report.url, "https://example.com")
        self.assertEqual(report.timestamp, datetime.datetime(2023, 1, 1, 12, 0))
        self.assertEqual(len(report.violations), 2)
        self.assertEqual(report.violations[0].rule_id, "color-contrast")
        self.assertEqual(report.violations[1].rule_id, "alt-text")
        self.assertEqual(report.standards, [AccessibilityStandard.WCAG_2_1_AA])
    
    def test_get_violation_count(self):
        """Test getting violation count by severity."""
        report = AccessibilityReport(
            report_id="report-123",
            url="https://example.com",
            violations=[
                AccessibilityViolation(
                    rule_id="rule1",
                    element={"id": "elem1"},
                    severity=AccessibilitySeverity.CRITICAL
                ),
                AccessibilityViolation(
                    rule_id="rule2",
                    element={"id": "elem2"},
                    severity=AccessibilitySeverity.HIGH
                ),
                AccessibilityViolation(
                    rule_id="rule3",
                    element={"id": "elem3"},
                    severity=AccessibilitySeverity.CRITICAL
                )
            ]
        )
        
        # Get counts
        critical_count = report.get_violation_count(AccessibilitySeverity.CRITICAL)
        high_count = report.get_violation_count(AccessibilitySeverity.HIGH)
        medium_count = report.get_violation_count(AccessibilitySeverity.MEDIUM)
        
        # Verify counts
        self.assertEqual(critical_count, 2)
        self.assertEqual(high_count, 1)
        self.assertEqual(medium_count, 0)
    
    def test_get_violations_by_rule(self):
        """Test getting violations by rule ID."""
        report = AccessibilityReport(
            report_id="report-123",
            url="https://example.com",
            violations=[
                AccessibilityViolation(
                    rule_id="color-contrast",
                    element={"id": "header"},
                    message="Insufficient contrast ratio"
                ),
                AccessibilityViolation(
                    rule_id="color-contrast",
                    element={"id": "footer"},
                    message="Insufficient contrast ratio"
                ),
                AccessibilityViolation(
                    rule_id="alt-text",
                    element={"id": "logo"},
                    message="Missing alt text"
                )
            ]
        )
        
        # Get violations by rule
        contrast_violations = report.get_violations_by_rule("color-contrast")
        alt_text_violations = report.get_violations_by_rule("alt-text")
        
        # Verify violations
        self.assertEqual(len(contrast_violations), 2)
        self.assertEqual(contrast_violations[0].element["id"], "header")
        self.assertEqual(contrast_violations[1].element["id"], "footer")
        
        self.assertEqual(len(alt_text_violations), 1)
        self.assertEqual(alt_text_violations[0].element["id"], "logo")
    
    def test_to_dict(self):
        """Test converting report to dictionary."""
        report = AccessibilityReport(
            report_id="report-123",
            url="https://example.com",
            timestamp=datetime.datetime(2023, 1, 1, 12, 0),
            violations=[
                AccessibilityViolation(
                    rule_id="color-contrast",
                    element={"id": "header"},
                    message="Insufficient contrast ratio"
                )
            ],
            standards=[AccessibilityStandard.WCAG_2_1_AA]
        )
        
        report_dict = report.to_dict()
        
        self.assertEqual(report_dict["report_id"], "report-123")
        self.assertEqual(report_dict["url"], "https://example.com")
        self.assertEqual(report_dict["timestamp"], "2023-01-01T12:00:00")
        self.assertEqual(len(report_dict["violations"]), 1)
        self.assertEqual(report_dict["violations"][0]["rule_id"], "color-contrast")
        self.assertEqual(report_dict["standards"], ["wcag_2_1_aa"])

class TestColorContrastChecker(unittest.TestCase):
    """Test cases for the ColorContrastChecker class."""
    
    def setUp(self):
        """Set up test environment."""
        self.checker = ColorContrastChecker()
    
    def test_calculate_contrast_ratio(self):
        """Test calculating contrast ratio between colors."""
        # Test black on white (high contrast)
        ratio1 = self.checker.calculate_contrast_ratio("#000000", "#FFFFFF")
        self.assertGreaterEqual(ratio1, 21.0)  # Maximum contrast
        
        # Test light gray on white (low contrast)
        ratio2 = self.checker.calculate_contrast_ratio("#CCCCCC", "#FFFFFF")
        self.assertLess(ratio2, 2.0)  # Low contrast
        
        # Test blue on white (medium contrast)
        ratio3 = self.checker.calculate_contrast_ratio("#0000FF", "#FFFFFF")
        self.assertGreaterEqual(ratio3, 4.5)  # Meets WCAG AA for normal text
    
    def test_check_text_contrast(self):
        """Test checking text contrast against WCAG standards."""
        # Test passing contrast for normal text (AA requires 4.5:1)
        result1 = self.checker.check_text_contrast(
            foreground="#000000",
            background="#FFFFFF",
            text_size=16,
            is_bold=False,
            level="AA"
        )
        self.assertTrue(result1["passes"])
        
        # Test failing contrast for normal text
        result2 = self.checker.check_text_contrast(
            foreground="#CCCCCC",
            background="#FFFFFF",
            text_size=16,
            is_bold=False,
            level="AA"
        )
        self.assertFalse(result2["passes"])
        
        # Test passing contrast for large text (AA requires 3:1)
        result3 = self.checker.check_text_contrast(
            foreground="#777777",
            background="#FFFFFF",
            text_size=24,  # Large text
            is_bold=False,
            level="AA"
        )
        self.assertTrue(result3["passes"])
    
    def test_check_element(self):
        """Test checking an element for contrast issues."""
        # Create element with contrast issue
        element = {
            "id": "header",
            "type": "text",
            "foreground_color": "#CCCCCC",
            "background_color": "#FFFFFF",
            "text_size": 16
        }
        
        # Check element
        violations = self.checker.check_element(element)
        
        # Verify violations
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "color-contrast")
        self.assertIn("contrast ratio", violations[0].message.lower())

class TestKeyboardNavigationChecker(unittest.TestCase):
    """Test cases for the KeyboardNavigationChecker class."""
    
    def setUp(self):
        """Set up test environment."""
        self.checker = KeyboardNavigationChecker()
    
    def test_check_focusable_elements(self):
        """Test checking if interactive elements are focusable."""
        # Create elements
        elements = [
            {
                "id": "button1",
                "type": "button",
                "tabindex": 0  # Focusable
            },
            {
                "id": "button2",
                "type": "button",
                "tabindex": -1  # Not focusable
            },
            {
                "id": "div1",
                "type": "div",
                "onclick": "handleClick()"  # Interactive but not focusable
            }
        ]
        
        # Check elements
        violations = self.checker.check_focusable_elements(elements)
        
        # Verify violations
        self.assertEqual(len(violations), 2)
        self.assertEqual(violations[0].element["id"], "button2")
        self.assertEqual(violations[1].element["id"], "div1")
    
    def test_check_tab_order(self):
        """Test checking tab order of focusable elements."""
        # Create elements with non-sequential tab order
        elements = [
            {
                "id": "elem1",
                "tabindex": 1
            },
            {
                "id": "elem2",
                "tabindex": 3  # Out of order
            },
            {
                "id": "elem3",
                "tabindex": 2  # Out of order
            }
        ]
        
        # Check tab order
        violations = self.checker.check_tab_order(elements)
        
        # Verify violations
        self.assertEqual(len(violations), 1)
        self.assertIn("tab order", violations[0].message.lower())
    
    def test_check_keyboard_traps(self):
        """Test checking for keyboard traps."""
        # Create elements with potential keyboard trap
        elements = [
            {
                "id": "modal",
                "type": "div",
                "role": "dialog",
                "children": [
                    {
                        "id": "close-button",
                        "type": "button",
                        "tabindex": -1  # Can't be focused to close modal
                    }
                ]
            }
        ]
        
        # Check for keyboard traps
        violations = self.checker.check_keyboard_traps(elements)
        
        # Verify violations
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].element["id"], "modal")
        self.assertIn("keyboard trap", violations[0].message.lower())

class TestScreenReaderCompatibilityChecker(unittest.TestCase):
    """Test cases for the ScreenReaderCompatibilityChecker class."""
    
    def setUp(self):
        """Set up test environment."""
        self.checker = ScreenReaderCompatibilityChecker()
    
    def test_check_image_alt_text(self):
        """Test checking images for alt text."""
        # Create elements
        elements = [
            {
                "id": "logo",
                "type": "image",
                "alt": "Company Logo"  # Has alt text
            },
            {
                "id": "banner",
                "type": "image"  # Missing alt text
            },
            {
                "id": "decorative",
                "type": "image",
                "alt": "",  # Empty alt text for decorative image
                "role": "presentation"
            }
        ]
        
        # Check elements
        violations = self.checker.check_image_alt_text(elements)
        
        # Verify violations
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].element["id"], "banner")
        self.assertIn("alt text", violations[0].message.lower())
    
    def test_check_form_labels(self):
        """Test checking form fields for labels."""
        # Create elements
        elements = [
            {
                "id": "name-field",
                "type": "input",
                "label": "Name"  # Has label
            },
            {
                "id": "email-field",
                "type": "input"  # Missing label
            },
            {
                "id": "submit-button",
                "type": "button",
                "value": "Submit"  # Button with value
            }
        ]
        
        # Check elements
        violations = self.checker.check_form_labels(elements)
        
        # Verify violations
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].element["id"], "email-field")
        self.assertIn("label", violations[0].message.lower())
    
    def test_check_aria_attributes(self):
        """Test checking ARIA attributes for proper usage."""
        # Create elements
        elements = [
            {
                "id": "menu",
                "role": "menu",
                "aria-expanded": "true"  # Valid ARIA usage
            },
            {
                "id": "button",
                "role": "button",
                "aria-selected": "true"  # Invalid ARIA combination
            },
            {
                "id": "heading",
                "role": "heading",
                "aria-level": "invalid"  # Invalid ARIA value
            }
        ]
        
        # Check elements
        violations = self.checker.check_aria_attributes(elements)
        
        # Verify violations
        self.assertEqual(len(violations), 2)
        self.assertEqual(violations[0].element["id"], "button")
        self.assertEqual(violations[1].element["id"], "heading")

class TestAccessibilityOverlay(unittest.TestCase):
    """Test cases for the AccessibilityOverlay class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = AccessibilityConfig(
            enabled=True,
            overlay_enabled=True
        )
        self.overlay = AccessibilityOverlay(self.config)
    
    def test_generate_overlay_code(self):
        """Test generating overlay code."""
        # Generate overlay code
        code = self.overlay.generate_overlay_code()
        
        # Verify code
        self.assertIsInstance(code, str)
        self.assertIn("<script", code)
        self.assertIn("accessibility", code.lower())
    
    def test_apply_text_adjustments(self):
        """Test applying text adjustments."""
        # Create page content
        content = "<div>Sample text</div>"
        
        # Apply adjustments
        adjusted = self.overlay.apply_text_adjustments(
            content=content,
            font_size_increase=2,
            line_spacing=1.5,
            letter_spacing=0.1
        )
        
        # Verify adjustments
        self.assertIn("font-size", adjusted)
        self.assertIn("line-height", adjusted)
        self.assertIn("letter-spacing", adjusted)
    
    def test_apply_color_adjustments(self):
        """Test applying color adjustments."""
        # Create page content
        content = "<div style='color: #333; background-color: #FFF;'>Sample text</div>"
        
        # Apply adjustments for high contrast
        adjusted = self.overlay.apply_color_adjustments(
            content=content,
            high_contrast=True
        )
        
        # Verify adjustments
        self.assertIn("color: #FFFFFF", adjusted)
        self.assertIn("background-color: #000000", adjusted)
    
    def test_generate_accessibility_statement(self):
        """Test generating accessibility statement."""
        # Generate statement
        statement = self.overlay.generate_accessibility_statement(
            organization_name="Example Corp",
            contact_email="accessibility@example.com",
            standards=[AccessibilityStandard.WCAG_2_1_AA]
        )
        
        # Verify statement
        self.assertIn("Example Corp", statement)
        self.assertIn("accessibility@example.com", statement)
        self.assertIn("WCAG", statement)

if __name__ == '__main__':
    unittest.main()
