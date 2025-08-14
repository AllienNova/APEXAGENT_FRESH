#!/usr/bin/env python3
"""
Test suite for the Quality Assurance Framework.

This module provides comprehensive tests for the quality assurance framework
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

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from quality_assurance.quality_assurance_framework import (
    QualityAssuranceSystem, QAConfig, TestResult, TestSuite, TestCase,
    ValidationRule, ValidationResult, ValidationSeverity, CodeReview,
    PerformanceTest, SecurityTest, AccessibilityTest, CompatibilityTest
)

class TestQualityAssuranceSystem(unittest.TestCase):
    """Test cases for the QualityAssuranceSystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = QAConfig(
            enabled=True,
            results_directory=self.temp_dir,
            auto_test_on_commit=True,
            minimum_test_coverage=80.0,
            required_validations=["security", "performance"],
            notification_enabled=True
        )
        self.qa_system = QualityAssuranceSystem.get_instance()
        self.qa_system.initialize(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.qa_system.shutdown()
    
    def test_singleton_pattern(self):
        """Test that the QA system follows the singleton pattern."""
        instance1 = QualityAssuranceSystem.get_instance()
        instance2 = QualityAssuranceSystem.get_instance()
        self.assertIs(instance1, instance2)
    
    def test_test_suite_registration(self):
        """Test registering test suites."""
        suite = TestSuite("test_suite", "Test Suite")
        self.qa_system.register_test_suite(suite)
        
        # Verify suite was registered
        self.assertIn("test_suite", self.qa_system.get_test_suites())
        
        # Test unregistering
        self.qa_system.unregister_test_suite("test_suite")
        self.assertNotIn("test_suite", self.qa_system.get_test_suites())
    
    def test_validation_rule_registration(self):
        """Test registering validation rules."""
        rule = ValidationRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test validation rule",
            severity=ValidationSeverity.CRITICAL
        )
        self.qa_system.register_validation_rule(rule)
        
        # Verify rule was registered
        self.assertIn("test_rule", self.qa_system.get_validation_rules())
        
        # Test unregistering
        self.qa_system.unregister_validation_rule("test_rule")
        self.assertNotIn("test_rule", self.qa_system.get_validation_rules())
    
    @patch('quality_assurance.quality_assurance_framework.unittest.TextTestRunner')
    def test_run_test_suite(self, mock_runner):
        """Test running a test suite."""
        # Mock test runner
        mock_result = MagicMock()
        mock_result.wasSuccessful.return_value = True
        mock_result.testsRun = 5
        mock_result.failures = []
        mock_result.errors = []
        mock_runner.return_value.run.return_value = mock_result
        
        # Create test suite
        suite = TestSuite("test_suite", "Test Suite")
        test_case = TestCase("test_case", "Test Case")
        suite.add_test_case(test_case)
        self.qa_system.register_test_suite(suite)
        
        # Run the suite
        result = self.qa_system.run_test_suite("test_suite")
        
        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.total_tests, 5)
        self.assertEqual(result.passed_tests, 5)
        self.assertEqual(result.failed_tests, 0)
    
    def test_validate_code(self):
        """Test code validation."""
        # Create validation rule
        rule = ValidationRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test validation rule",
            severity=ValidationSeverity.CRITICAL,
            validate_func=lambda code: ValidationResult(
                rule_id="test_rule",
                success=True,
                message="Validation passed"
            )
        )
        self.qa_system.register_validation_rule(rule)
        
        # Validate code
        code = "def test_function():\n    return True"
        results = self.qa_system.validate_code(code)
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].rule_id, "test_rule")
    
    @patch('quality_assurance.quality_assurance_framework.coverage.Coverage')
    def test_measure_test_coverage(self, mock_coverage):
        """Test measuring test coverage."""
        # Mock coverage
        mock_cov = MagicMock()
        mock_cov.report.return_value = 85.5
        mock_coverage.return_value = mock_cov
        
        # Measure coverage
        coverage = self.qa_system.measure_test_coverage(["test_module"])
        
        # Verify coverage
        self.assertEqual(coverage, 85.5)
        mock_cov.start.assert_called_once()
        mock_cov.stop.assert_called_once()
        mock_cov.report.assert_called_once()
    
    def test_generate_qa_report(self):
        """Test generating QA report."""
        # Create test results
        test_results = [
            TestResult(
                suite_id="suite1",
                suite_name="Suite 1",
                success=True,
                total_tests=10,
                passed_tests=10,
                failed_tests=0,
                duration=1.5
            ),
            TestResult(
                suite_id="suite2",
                suite_name="Suite 2",
                success=False,
                total_tests=5,
                passed_tests=4,
                failed_tests=1,
                duration=0.8,
                failures=["Test case 3 failed"]
            )
        ]
        
        # Create validation results
        validation_results = [
            ValidationResult(
                rule_id="rule1",
                success=True,
                message="Validation passed"
            ),
            ValidationResult(
                rule_id="rule2",
                success=False,
                message="Validation failed",
                severity=ValidationSeverity.HIGH,
                line_number=42,
                code_snippet="def bad_function():"
            )
        ]
        
        # Generate report
        with patch('builtins.open', mock_open()) as mock_file:
            report_path = self.qa_system.generate_qa_report(
                test_results=test_results,
                validation_results=validation_results,
                test_coverage=85.5
            )
            
            # Verify report was written
            mock_file.assert_called_once()
            self.assertTrue(report_path.endswith(".json"))

class TestTestSuite(unittest.TestCase):
    """Test cases for the TestSuite class."""
    
    def test_test_suite_creation(self):
        """Test creating a test suite."""
        suite = TestSuite("test_suite", "Test Suite")
        self.assertEqual(suite.suite_id, "test_suite")
        self.assertEqual(suite.name, "Test Suite")
        self.assertEqual(len(suite.test_cases), 0)
    
    def test_add_test_case(self):
        """Test adding a test case to a suite."""
        suite = TestSuite("test_suite", "Test Suite")
        test_case = TestCase("test_case", "Test Case")
        suite.add_test_case(test_case)
        
        self.assertEqual(len(suite.test_cases), 1)
        self.assertEqual(suite.test_cases[0], test_case)
    
    def test_remove_test_case(self):
        """Test removing a test case from a suite."""
        suite = TestSuite("test_suite", "Test Suite")
        test_case = TestCase("test_case", "Test Case")
        suite.add_test_case(test_case)
        
        suite.remove_test_case("test_case")
        self.assertEqual(len(suite.test_cases), 0)
    
    def test_get_test_case(self):
        """Test getting a test case by ID."""
        suite = TestSuite("test_suite", "Test Suite")
        test_case = TestCase("test_case", "Test Case")
        suite.add_test_case(test_case)
        
        retrieved_case = suite.get_test_case("test_case")
        self.assertEqual(retrieved_case, test_case)
        
        # Test non-existent case
        self.assertIsNone(suite.get_test_case("non_existent"))
    
    def test_to_unittest_suite(self):
        """Test converting to unittest TestSuite."""
        suite = TestSuite("test_suite", "Test Suite")
        
        # Add a test case with a test method
        class SampleTest(unittest.TestCase):
            def test_sample(self):
                self.assertTrue(True)
        
        test_case = TestCase("test_case", "Test Case")
        test_case.test_class = SampleTest
        suite.add_test_case(test_case)
        
        # Convert to unittest suite
        unittest_suite = suite.to_unittest_suite()
        
        # Verify it's a unittest.TestSuite
        self.assertIsInstance(unittest_suite, unittest.TestSuite)
        
        # Verify it contains our test
        self.assertEqual(unittest_suite.countTestCases(), 1)

class TestTestCase(unittest.TestCase):
    """Test cases for the TestCase class."""
    
    def test_test_case_creation(self):
        """Test creating a test case."""
        case = TestCase("test_case", "Test Case")
        self.assertEqual(case.case_id, "test_case")
        self.assertEqual(case.name, "Test Case")
        self.assertIsNone(case.test_class)
    
    def test_set_test_class(self):
        """Test setting the test class."""
        case = TestCase("test_case", "Test Case")
        
        class SampleTest(unittest.TestCase):
            def test_sample(self):
                pass
        
        case.test_class = SampleTest
        self.assertEqual(case.test_class, SampleTest)
    
    def test_to_unittest_suite(self):
        """Test converting to unittest TestSuite."""
        case = TestCase("test_case", "Test Case")
        
        class SampleTest(unittest.TestCase):
            def test_sample1(self):
                pass
            
            def test_sample2(self):
                pass
        
        case.test_class = SampleTest
        
        # Convert to unittest suite
        unittest_suite = case.to_unittest_suite()
        
        # Verify it's a unittest.TestSuite
        self.assertIsInstance(unittest_suite, unittest.TestSuite)
        
        # Verify it contains our tests
        self.assertEqual(unittest_suite.countTestCases(), 2)

class TestValidationRule(unittest.TestCase):
    """Test cases for the ValidationRule class."""
    
    def test_validation_rule_creation(self):
        """Test creating a validation rule."""
        rule = ValidationRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test validation rule",
            severity=ValidationSeverity.CRITICAL
        )
        
        self.assertEqual(rule.rule_id, "test_rule")
        self.assertEqual(rule.name, "Test Rule")
        self.assertEqual(rule.description, "A test validation rule")
        self.assertEqual(rule.severity, ValidationSeverity.CRITICAL)
    
    def test_validate_with_function(self):
        """Test validating with a custom function."""
        # Create a validation function
        def validate_func(code):
            if "import os" in code:
                return ValidationResult(
                    rule_id="test_rule",
                    success=False,
                    message="Direct OS import not allowed",
                    severity=ValidationSeverity.HIGH,
                    line_number=1
                )
            return ValidationResult(
                rule_id="test_rule",
                success=True,
                message="Validation passed"
            )
        
        # Create rule with the function
        rule = ValidationRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test validation rule",
            severity=ValidationSeverity.HIGH,
            validate_func=validate_func
        )
        
        # Test with valid code
        result = rule.validate("def test_function():\n    return True")
        self.assertTrue(result.success)
        
        # Test with invalid code
        result = rule.validate("import os\ndef test_function():\n    return True")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Direct OS import not allowed")
        self.assertEqual(result.line_number, 1)
    
    def test_validate_with_regex(self):
        """Test validating with a regex pattern."""
        # Create rule with regex
        rule = ValidationRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test validation rule",
            severity=ValidationSeverity.MEDIUM,
            regex_pattern=r"print\s*\(",
            regex_message="Use of print() is discouraged"
        )
        
        # Test with valid code
        result = rule.validate("def test_function():\n    return True")
        self.assertTrue(result.success)
        
        # Test with invalid code
        result = rule.validate("def test_function():\n    print('Hello')\n    return True")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Use of print() is discouraged")
        self.assertEqual(result.line_number, 2)

class TestCodeReview(unittest.TestCase):
    """Test cases for the CodeReview class."""
    
    def test_code_review_creation(self):
        """Test creating a code review."""
        review = CodeReview(
            review_id="review1",
            reviewer="Test Reviewer",
            file_path="/path/to/file.py",
            commit_id="abc123"
        )
        
        self.assertEqual(review.review_id, "review1")
        self.assertEqual(review.reviewer, "Test Reviewer")
        self.assertEqual(review.file_path, "/path/to/file.py")
        self.assertEqual(review.commit_id, "abc123")
        self.assertEqual(len(review.comments), 0)
    
    def test_add_comment(self):
        """Test adding a comment to a code review."""
        review = CodeReview(
            review_id="review1",
            reviewer="Test Reviewer",
            file_path="/path/to/file.py"
        )
        
        review.add_comment(
            line_number=42,
            comment="This code needs improvement",
            severity=ValidationSeverity.MEDIUM
        )
        
        self.assertEqual(len(review.comments), 1)
        self.assertEqual(review.comments[0].line_number, 42)
        self.assertEqual(review.comments[0].comment, "This code needs improvement")
        self.assertEqual(review.comments[0].severity, ValidationSeverity.MEDIUM)
    
    def test_get_comments_by_severity(self):
        """Test getting comments by severity."""
        review = CodeReview(
            review_id="review1",
            reviewer="Test Reviewer",
            file_path="/path/to/file.py"
        )
        
        review.add_comment(line_number=10, comment="Critical issue", severity=ValidationSeverity.CRITICAL)
        review.add_comment(line_number=20, comment="High issue", severity=ValidationSeverity.HIGH)
        review.add_comment(line_number=30, comment="Medium issue", severity=ValidationSeverity.MEDIUM)
        review.add_comment(line_number=40, comment="Low issue", severity=ValidationSeverity.LOW)
        review.add_comment(line_number=50, comment="Another high issue", severity=ValidationSeverity.HIGH)
        
        # Get critical comments
        critical_comments = review.get_comments_by_severity(ValidationSeverity.CRITICAL)
        self.assertEqual(len(critical_comments), 1)
        self.assertEqual(critical_comments[0].comment, "Critical issue")
        
        # Get high comments
        high_comments = review.get_comments_by_severity(ValidationSeverity.HIGH)
        self.assertEqual(len(high_comments), 2)
        
        # Get all comments
        all_comments = review.get_comments()
        self.assertEqual(len(all_comments), 5)
    
    def test_to_dict(self):
        """Test converting a code review to dictionary."""
        review = CodeReview(
            review_id="review1",
            reviewer="Test Reviewer",
            file_path="/path/to/file.py",
            commit_id="abc123"
        )
        
        review.add_comment(line_number=10, comment="Test comment", severity=ValidationSeverity.MEDIUM)
        
        review_dict = review.to_dict()
        
        self.assertEqual(review_dict["review_id"], "review1")
        self.assertEqual(review_dict["reviewer"], "Test Reviewer")
        self.assertEqual(review_dict["file_path"], "/path/to/file.py")
        self.assertEqual(review_dict["commit_id"], "abc123")
        self.assertEqual(len(review_dict["comments"]), 1)
        self.assertEqual(review_dict["comments"][0]["line_number"], 10)
        self.assertEqual(review_dict["comments"][0]["comment"], "Test comment")
        self.assertEqual(review_dict["comments"][0]["severity"], "medium")
    
    def test_from_dict(self):
        """Test creating a code review from dictionary."""
        review_dict = {
            "review_id": "review1",
            "reviewer": "Test Reviewer",
            "file_path": "/path/to/file.py",
            "commit_id": "abc123",
            "comments": [
                {
                    "line_number": 10,
                    "comment": "Test comment",
                    "severity": "medium"
                }
            ]
        }
        
        review = CodeReview.from_dict(review_dict)
        
        self.assertEqual(review.review_id, "review1")
        self.assertEqual(review.reviewer, "Test Reviewer")
        self.assertEqual(review.file_path, "/path/to/file.py")
        self.assertEqual(review.commit_id, "abc123")
        self.assertEqual(len(review.comments), 1)
        self.assertEqual(review.comments[0].line_number, 10)
        self.assertEqual(review.comments[0].comment, "Test comment")
        self.assertEqual(review.comments[0].severity, ValidationSeverity.MEDIUM)

class TestPerformanceTest(unittest.TestCase):
    """Test cases for the PerformanceTest class."""
    
    def test_performance_test_creation(self):
        """Test creating a performance test."""
        test = PerformanceTest(
            test_id="perf_test",
            name="Performance Test",
            description="A performance test"
        )
        
        self.assertEqual(test.test_id, "perf_test")
        self.assertEqual(test.name, "Performance Test")
        self.assertEqual(test.description, "A performance test")
    
    def test_measure_execution_time(self):
        """Test measuring execution time."""
        test = PerformanceTest(
            test_id="perf_test",
            name="Performance Test"
        )
        
        # Function to measure
        def test_function():
            time.sleep(0.1)
            return True
        
        # Measure execution time
        result = test.measure_execution_time(test_function)
        
        # Verify result
        self.assertGreaterEqual(result, 0.1)
        self.assertLess(result, 0.2)  # Allow some overhead
    
    def test_run_benchmark(self):
        """Test running a benchmark."""
        test = PerformanceTest(
            test_id="perf_test",
            name="Performance Test"
        )
        
        # Function to benchmark
        def test_function():
            time.sleep(0.01)
            return True
        
        # Run benchmark
        result = test.run_benchmark(test_function, iterations=5)
        
        # Verify result
        self.assertEqual(result.iterations, 5)
        self.assertGreaterEqual(result.min_time, 0.01)
        self.assertGreaterEqual(result.max_time, 0.01)
        self.assertGreaterEqual(result.avg_time, 0.01)
        self.assertGreaterEqual(result.total_time, 0.05)
    
    def test_check_performance_threshold(self):
        """Test checking performance against threshold."""
        test = PerformanceTest(
            test_id="perf_test",
            name="Performance Test"
        )
        
        # Function to test
        def fast_function():
            return True
        
        def slow_function():
            time.sleep(0.2)
            return True
        
        # Check fast function against threshold
        result = test.check_performance_threshold(fast_function, max_time=0.1)
        self.assertTrue(result.success)
        
        # Check slow function against threshold
        result = test.check_performance_threshold(slow_function, max_time=0.1)
        self.assertFalse(result.success)

if __name__ == '__main__':
    unittest.main()
