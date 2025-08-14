#!/usr/bin/env python3
"""
Quality Assurance Framework for ApexAgent

This module provides a comprehensive quality assurance framework
with automated testing, validation, verification, and quality metrics
for ensuring high-quality software delivery.
"""

import os
import sys
import time
import json
import logging
import threading
import queue
import random
import functools
import inspect
import unittest
import doctest
import coverage
import pytest
import re
import ast
import pylint.lint
import mypy.api
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, TypeVar, cast, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quality_assurance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("quality_assurance")

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')

class QualityLevel(Enum):
    """Enumeration of quality levels."""
    MINIMAL = "minimal"      # Basic quality checks
    STANDARD = "standard"    # Standard quality checks
    HIGH = "high"            # High quality checks
    ENTERPRISE = "enterprise"  # Enterprise-grade quality checks

class TestType(Enum):
    """Enumeration of test types."""
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    COMPATIBILITY = "compatibility"
    LOCALIZATION = "localization"
    REGRESSION = "regression"
    SMOKE = "smoke"
    ACCEPTANCE = "acceptance"

class ValidationLevel(Enum):
    """Enumeration of validation levels."""
    BASIC = "basic"          # Basic validation
    STANDARD = "standard"    # Standard validation
    STRICT = "strict"        # Strict validation
    CUSTOM = "custom"        # Custom validation rules

class CodeQualityMetric(Enum):
    """Enumeration of code quality metrics."""
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    TEST_COVERAGE = "test_coverage"
    STYLE_COMPLIANCE = "style_compliance"
    TYPE_SAFETY = "type_safety"
    DUPLICATION = "duplication"

@dataclass
class TestResult:
    """Result of a test execution."""
    test_id: str
    test_type: TestType
    component: str
    passed: bool
    execution_time: float  # in seconds
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the test result to a dictionary."""
        return {
            "test_id": self.test_id,
            "test_type": self.test_type.value,
            "component": self.component,
            "passed": self.passed,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "additional_info": self.additional_info
        }

@dataclass
class ValidationResult:
    """Result of a validation check."""
    validation_id: str
    component: str
    valid: bool
    level: ValidationLevel
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation result to a dictionary."""
        return {
            "validation_id": self.validation_id,
            "component": self.component,
            "valid": self.valid,
            "level": self.level.value,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message,
            "details": self.details
        }

@dataclass
class CodeQualityResult:
    """Result of a code quality check."""
    file_path: str
    metrics: Dict[CodeQualityMetric, float]
    issues: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the code quality result to a dictionary."""
        return {
            "file_path": self.file_path,
            "metrics": {metric.value: value for metric, value in self.metrics.items()},
            "issues": self.issues,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class QualityReport:
    """Comprehensive quality report."""
    report_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    test_results: List[TestResult] = field(default_factory=list)
    validation_results: List[ValidationResult] = field(default_factory=list)
    code_quality_results: List[CodeQualityResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the quality report to a dictionary."""
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp.isoformat(),
            "test_results": [result.to_dict() for result in self.test_results],
            "validation_results": [result.to_dict() for result in self.validation_results],
            "code_quality_results": [result.to_dict() for result in self.code_quality_results],
            "summary": self.summary
        }
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save the quality report to a file.
        
        Args:
            file_path: Path to save the report
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save quality report: {str(e)}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['QualityReport']:
        """
        Load a quality report from a file.
        
        Args:
            file_path: Path to the report file
            
        Returns:
            Optional[QualityReport]: The loaded report, or None if loading failed
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            report = QualityReport(
                report_id=data["report_id"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                summary=data["summary"]
            )
            
            # Load test results
            for result_data in data["test_results"]:
                report.test_results.append(TestResult(
                    test_id=result_data["test_id"],
                    test_type=TestType(result_data["test_type"]),
                    component=result_data["component"],
                    passed=result_data["passed"],
                    execution_time=result_data["execution_time"],
                    timestamp=datetime.fromisoformat(result_data["timestamp"]),
                    error_message=result_data["error_message"],
                    stack_trace=result_data["stack_trace"],
                    additional_info=result_data["additional_info"]
                ))
            
            # Load validation results
            for result_data in data["validation_results"]:
                report.validation_results.append(ValidationResult(
                    validation_id=result_data["validation_id"],
                    component=result_data["component"],
                    valid=result_data["valid"],
                    level=ValidationLevel(result_data["level"]),
                    timestamp=datetime.fromisoformat(result_data["timestamp"]),
                    error_message=result_data["error_message"],
                    details=result_data["details"]
                ))
            
            # Load code quality results
            for result_data in data["code_quality_results"]:
                report.code_quality_results.append(CodeQualityResult(
                    file_path=result_data["file_path"],
                    metrics={CodeQualityMetric(k): v for k, v in result_data["metrics"].items()},
                    issues=result_data["issues"],
                    timestamp=datetime.fromisoformat(result_data["timestamp"])
                ))
            
            return report
        except Exception as e:
            logger.error(f"Failed to load quality report: {str(e)}")
            return None

@dataclass
class TestConfig:
    """Configuration for test execution."""
    enabled_test_types: Set[TestType] = field(default_factory=set)
    disabled_test_types: Set[TestType] = field(default_factory=set)
    timeout: float = 60.0  # seconds
    parallel: bool = True
    max_workers: int = 4
    fail_fast: bool = False
    retry_count: int = 0
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    
    def is_test_type_enabled(self, test_type: TestType) -> bool:
        """
        Check if a test type is enabled.
        
        Args:
            test_type: The test type to check
            
        Returns:
            bool: True if the test type is enabled, False otherwise
        """
        return (
            (not self.enabled_test_types or test_type in self.enabled_test_types) and
            test_type not in self.disabled_test_types
        )

@dataclass
class ValidationConfig:
    """Configuration for validation checks."""
    level: ValidationLevel = ValidationLevel.STANDARD
    custom_validators: Dict[str, Callable] = field(default_factory=dict)
    schema_paths: Dict[str, str] = field(default_factory=dict)
    validation_rules: Dict[str, Dict[str, Any]] = field(default_factory=dict)

@dataclass
class CodeQualityConfig:
    """Configuration for code quality checks."""
    enabled_metrics: Set[CodeQualityMetric] = field(default_factory=set)
    thresholds: Dict[CodeQualityMetric, float] = field(default_factory=dict)
    style_guide: str = "pep8"
    max_complexity: int = 10
    min_test_coverage: float = 80.0  # percentage
    type_checking: bool = True
    lint_config_path: Optional[str] = None

class QualityAssuranceConfig:
    """Configuration for the quality assurance framework."""
    
    def __init__(self):
        """Initialize the quality assurance configuration."""
        self.quality_level = QualityLevel.STANDARD
        self.test_configs: Dict[str, TestConfig] = {}
        self.validation_configs: Dict[str, ValidationConfig] = {}
        self.code_quality_configs: Dict[str, CodeQualityConfig] = {}
        self.global_test_config = TestConfig()
        self.global_validation_config = ValidationConfig()
        self.global_code_quality_config = CodeQualityConfig()
        self.report_dir: str = "reports"
        self.notification_enabled: bool = True
        self.notification_threshold: float = 80.0  # percentage
        self.auto_fix: bool = False
        self.continuous_testing: bool = False
        self.test_result_history: int = 10  # number of reports to keep
    
    def get_test_config(self, component: str) -> TestConfig:
        """
        Get the test configuration for a component.
        
        Args:
            component: The component name
            
        Returns:
            TestConfig: The test configuration
        """
        return self.test_configs.get(component, self.global_test_config)
    
    def get_validation_config(self, component: str) -> ValidationConfig:
        """
        Get the validation configuration for a component.
        
        Args:
            component: The component name
            
        Returns:
            ValidationConfig: The validation configuration
        """
        return self.validation_configs.get(component, self.global_validation_config)
    
    def get_code_quality_config(self, component: str) -> CodeQualityConfig:
        """
        Get the code quality configuration for a component.
        
        Args:
            component: The component name
            
        Returns:
            CodeQualityConfig: The code quality configuration
        """
        return self.code_quality_configs.get(component, self.global_code_quality_config)
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Load quality level
            if "quality_level" in config_data:
                self.quality_level = QualityLevel(config_data["quality_level"])
            
            # Load global test config
            if "global_test" in config_data:
                test_data = config_data["global_test"]
                self.global_test_config = TestConfig(
                    timeout=test_data.get("timeout", 60.0),
                    parallel=test_data.get("parallel", True),
                    max_workers=test_data.get("max_workers", 4),
                    fail_fast=test_data.get("fail_fast", False),
                    retry_count=test_data.get("retry_count", 0),
                    include_patterns=test_data.get("include_patterns", []),
                    exclude_patterns=test_data.get("exclude_patterns", [])
                )
                
                # Load enabled test types
                if "enabled_test_types" in test_data:
                    self.global_test_config.enabled_test_types = {
                        TestType(test_type) for test_type in test_data["enabled_test_types"]
                    }
                
                # Load disabled test types
                if "disabled_test_types" in test_data:
                    self.global_test_config.disabled_test_types = {
                        TestType(test_type) for test_type in test_data["disabled_test_types"]
                    }
            
            # Load global validation config
            if "global_validation" in config_data:
                validation_data = config_data["global_validation"]
                self.global_validation_config = ValidationConfig(
                    level=ValidationLevel(validation_data.get("level", "standard")),
                    schema_paths=validation_data.get("schema_paths", {}),
                    validation_rules=validation_data.get("validation_rules", {})
                )
            
            # Load global code quality config
            if "global_code_quality" in config_data:
                quality_data = config_data["global_code_quality"]
                self.global_code_quality_config = CodeQualityConfig(
                    style_guide=quality_data.get("style_guide", "pep8"),
                    max_complexity=quality_data.get("max_complexity", 10),
                    min_test_coverage=quality_data.get("min_test_coverage", 80.0),
                    type_checking=quality_data.get("type_checking", True),
                    lint_config_path=quality_data.get("lint_config_path")
                )
                
                # Load enabled metrics
                if "enabled_metrics" in quality_data:
                    self.global_code_quality_config.enabled_metrics = {
                        CodeQualityMetric(metric) for metric in quality_data["enabled_metrics"]
                    }
                
                # Load thresholds
                if "thresholds" in quality_data:
                    self.global_code_quality_config.thresholds = {
                        CodeQualityMetric(metric): value
                        for metric, value in quality_data["thresholds"].items()
                    }
            
            # Load component-specific configs
            if "components" in config_data:
                for component_name, component_config in config_data["components"].items():
                    # Load test config
                    if "test" in component_config:
                        test_data = component_config["test"]
                        self.test_configs[component_name] = TestConfig(
                            timeout=test_data.get("timeout", 60.0),
                            parallel=test_data.get("parallel", True),
                            max_workers=test_data.get("max_workers", 4),
                            fail_fast=test_data.get("fail_fast", False),
                            retry_count=test_data.get("retry_count", 0),
                            include_patterns=test_data.get("include_patterns", []),
                            exclude_patterns=test_data.get("exclude_patterns", [])
                        )
                        
                        # Load enabled test types
                        if "enabled_test_types" in test_data:
                            self.test_configs[component_name].enabled_test_types = {
                                TestType(test_type) for test_type in test_data["enabled_test_types"]
                            }
                        
                        # Load disabled test types
                        if "disabled_test_types" in test_data:
                            self.test_configs[component_name].disabled_test_types = {
                                TestType(test_type) for test_type in test_data["disabled_test_types"]
                            }
                    
                    # Load validation config
                    if "validation" in component_config:
                        validation_data = component_config["validation"]
                        self.validation_configs[component_name] = ValidationConfig(
                            level=ValidationLevel(validation_data.get("level", "standard")),
                            schema_paths=validation_data.get("schema_paths", {}),
                            validation_rules=validation_data.get("validation_rules", {})
                        )
                    
                    # Load code quality config
                    if "code_quality" in component_config:
                        quality_data = component_config["code_quality"]
                        self.code_quality_configs[component_name] = CodeQualityConfig(
                            style_guide=quality_data.get("style_guide", "pep8"),
                            max_complexity=quality_data.get("max_complexity", 10),
                            min_test_coverage=quality_data.get("min_test_coverage", 80.0),
                            type_checking=quality_data.get("type_checking", True),
                            lint_config_path=quality_data.get("lint_config_path")
                        )
                        
                        # Load enabled metrics
                        if "enabled_metrics" in quality_data:
                            self.code_quality_configs[component_name].enabled_metrics = {
                                CodeQualityMetric(metric) for metric in quality_data["enabled_metrics"]
                            }
                        
                        # Load thresholds
                        if "thresholds" in quality_data:
                            self.code_quality_configs[component_name].thresholds = {
                                CodeQualityMetric(metric): value
                                for metric, value in quality_data["thresholds"].items()
                            }
            
            # Load framework settings
            if "framework" in config_data:
                framework = config_data["framework"]
                self.report_dir = framework.get("report_dir", "reports")
                self.notification_enabled = framework.get("notification_enabled", True)
                self.notification_threshold = framework.get("notification_threshold", 80.0)
                self.auto_fix = framework.get("auto_fix", False)
                self.continuous_testing = framework.get("continuous_testing", False)
                self.test_result_history = framework.get("test_result_history", 10)
            
            logger.info(f"Configuration loaded successfully from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {str(e)}")
            return False

class TestRunner:
    """
    Test runner for executing tests.
    
    This class provides functionality for running different types of tests
    and collecting test results.
    """
    
    def __init__(self, config: TestConfig):
        """
        Initialize the test runner.
        
        Args:
            config: Test configuration
        """
        self.config = config
        self.results: List[TestResult] = []
    
    def run_unittest(self, test_path: str, component: str) -> List[TestResult]:
        """
        Run unittest tests.
        
        Args:
            test_path: Path to the test file or directory
            component: Component name
            
        Returns:
            List[TestResult]: Test results
        """
        results = []
        
        try:
            # Create test loader
            loader = unittest.TestLoader()
            
            # Discover tests
            if os.path.isdir(test_path):
                suite = loader.discover(test_path, pattern="test_*.py")
            else:
                suite = loader.loadTestsFromName(test_path)
            
            # Create test runner
            runner = unittest.TextTestRunner(verbosity=2)
            
            # Run tests
            for test in list(suite):
                test_name = test.id()
                
                # Check if test should be included/excluded
                if not self._should_run_test(test_name):
                    continue
                
                # Run the test
                start_time = time.time()
                test_result = runner.run(test)
                end_time = time.time()
                
                # Create test result
                result = TestResult(
                    test_id=test_name,
                    test_type=TestType.UNIT,
                    component=component,
                    passed=test_result.wasSuccessful(),
                    execution_time=end_time - start_time
                )
                
                # Add error information if test failed
                if not test_result.wasSuccessful():
                    if test_result.errors:
                        result.error_message = str(test_result.errors[0][1])
                        result.stack_trace = test_result.errors[0][1].__traceback__.format_exc()
                    elif test_result.failures:
                        result.error_message = str(test_result.failures[0][1])
                        result.stack_trace = test_result.failures[0][1].__traceback__.format_exc()
                
                results.append(result)
                
                # Stop if fail fast is enabled and test failed
                if self.config.fail_fast and not result.passed:
                    break
        except Exception as e:
            logger.error(f"Error running unittest tests: {str(e)}")
            # Create error result
            results.append(TestResult(
                test_id=f"{test_path}:error",
                test_type=TestType.UNIT,
                component=component,
                passed=False,
                execution_time=0.0,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            ))
        
        return results
    
    def run_pytest(self, test_path: str, component: str) -> List[TestResult]:
        """
        Run pytest tests.
        
        Args:
            test_path: Path to the test file or directory
            component: Component name
            
        Returns:
            List[TestResult]: Test results
        """
        results = []
        
        try:
            # Build pytest arguments
            pytest_args = [test_path, "-v"]
            
            # Add timeout if configured
            if self.config.timeout > 0:
                pytest_args.extend(["--timeout", str(self.config.timeout)])
            
            # Run pytest
            start_time = time.time()
            pytest_result = pytest.main(pytest_args)
            end_time = time.time()
            
            # Create test result
            result = TestResult(
                test_id=test_path,
                test_type=TestType.UNIT,
                component=component,
                passed=pytest_result == 0,
                execution_time=end_time - start_time
            )
            
            # Add error information if test failed
            if pytest_result != 0:
                result.error_message = f"Pytest failed with exit code {pytest_result}"
            
            results.append(result)
        except Exception as e:
            logger.error(f"Error running pytest tests: {str(e)}")
            # Create error result
            results.append(TestResult(
                test_id=f"{test_path}:error",
                test_type=TestType.UNIT,
                component=component,
                passed=False,
                execution_time=0.0,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            ))
        
        return results
    
    def run_doctest(self, module_path: str, component: str) -> List[TestResult]:
        """
        Run doctests.
        
        Args:
            module_path: Path to the module
            component: Component name
            
        Returns:
            List[TestResult]: Test results
        """
        results = []
        
        try:
            # Run doctest
            start_time = time.time()
            doctest_result = doctest.testfile(module_path, verbose=True)
            end_time = time.time()
            
            # Create test result
            result = TestResult(
                test_id=f"{module_path}:doctest",
                test_type=TestType.UNIT,
                component=component,
                passed=doctest_result.failed == 0,
                execution_time=end_time - start_time,
                additional_info={
                    "attempted": doctest_result.attempted,
                    "passed": doctest_result.attempted - doctest_result.failed,
                    "failed": doctest_result.failed
                }
            )
            
            results.append(result)
        except Exception as e:
            logger.error(f"Error running doctests: {str(e)}")
            # Create error result
            results.append(TestResult(
                test_id=f"{module_path}:doctest:error",
                test_type=TestType.UNIT,
                component=component,
                passed=False,
                execution_time=0.0,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            ))
        
        return results
    
    def run_integration_test(self, test_path: str, component: str) -> List[TestResult]:
        """
        Run integration tests.
        
        Args:
            test_path: Path to the test file or directory
            component: Component name
            
        Returns:
            List[TestResult]: Test results
        """
        # In a real implementation, this would run integration tests
        # For this example, we'll use pytest with a different test type
        results = []
        
        try:
            # Build pytest arguments
            pytest_args = [test_path, "-v"]
            
            # Add timeout if configured
            if self.config.timeout > 0:
                pytest_args.extend(["--timeout", str(self.config.timeout)])
            
            # Run pytest
            start_time = time.time()
            pytest_result = pytest.main(pytest_args)
            end_time = time.time()
            
            # Create test result
            result = TestResult(
                test_id=test_path,
                test_type=TestType.INTEGRATION,
                component=component,
                passed=pytest_result == 0,
                execution_time=end_time - start_time
            )
            
            # Add error information if test failed
            if pytest_result != 0:
                result.error_message = f"Integration test failed with exit code {pytest_result}"
            
            results.append(result)
        except Exception as e:
            logger.error(f"Error running integration tests: {str(e)}")
            # Create error result
            results.append(TestResult(
                test_id=f"{test_path}:error",
                test_type=TestType.INTEGRATION,
                component=component,
                passed=False,
                execution_time=0.0,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            ))
        
        return results
    
    def run_functional_test(self, test_path: str, component: str) -> List[TestResult]:
        """
        Run functional tests.
        
        Args:
            test_path: Path to the test file or directory
            component: Component name
            
        Returns:
            List[TestResult]: Test results
        """
        # In a real implementation, this would run functional tests
        # For this example, we'll use pytest with a different test type
        results = []
        
        try:
            # Build pytest arguments
            pytest_args = [test_path, "-v"]
            
            # Add timeout if configured
            if self.config.timeout > 0:
                pytest_args.extend(["--timeout", str(self.config.timeout)])
            
            # Run pytest
            start_time = time.time()
            pytest_result = pytest.main(pytest_args)
            end_time = time.time()
            
            # Create test result
            result = TestResult(
                test_id=test_path,
                test_type=TestType.FUNCTIONAL,
                component=component,
                passed=pytest_result == 0,
                execution_time=end_time - start_time
            )
            
            # Add error information if test failed
            if pytest_result != 0:
                result.error_message = f"Functional test failed with exit code {pytest_result}"
            
            results.append(result)
        except Exception as e:
            logger.error(f"Error running functional tests: {str(e)}")
            # Create error result
            results.append(TestResult(
                test_id=f"{test_path}:error",
                test_type=TestType.FUNCTIONAL,
                component=component,
                passed=False,
                execution_time=0.0,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            ))
        
        return results
    
    def run_performance_test(self, test_path: str, component: str) -> List[TestResult]:
        """
        Run performance tests.
        
        Args:
            test_path: Path to the test file or directory
            component: Component name
            
        Returns:
            List[TestResult]: Test results
        """
        # In a real implementation, this would run performance tests
        # For this example, we'll simulate a performance test
        results = []
        
        try:
            # Simulate performance test
            start_time = time.time()
            time.sleep(0.5)  # Simulate test execution
            end_time = time.time()
            
            # Create test result
            result = TestResult(
                test_id=f"{test_path}:performance",
                test_type=TestType.PERFORMANCE,
                component=component,
                passed=True,
                execution_time=end_time - start_time,
                additional_info={
                    "throughput": 1000,  # requests per second
                    "latency": 10,  # milliseconds
                    "memory_usage": 100  # MB
                }
            )
            
            results.append(result)
        except Exception as e:
            logger.error(f"Error running performance tests: {str(e)}")
            # Create error result
            results.append(TestResult(
                test_id=f"{test_path}:performance:error",
                test_type=TestType.PERFORMANCE,
                component=component,
                passed=False,
                execution_time=0.0,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            ))
        
        return results
    
    def run_security_test(self, test_path: str, component: str) -> List[TestResult]:
        """
        Run security tests.
        
        Args:
            test_path: Path to the test file or directory
            component: Component name
            
        Returns:
            List[TestResult]: Test results
        """
        # In a real implementation, this would run security tests
        # For this example, we'll simulate a security test
        results = []
        
        try:
            # Simulate security test
            start_time = time.time()
            time.sleep(0.5)  # Simulate test execution
            end_time = time.time()
            
            # Create test result
            result = TestResult(
                test_id=f"{test_path}:security",
                test_type=TestType.SECURITY,
                component=component,
                passed=True,
                execution_time=end_time - start_time,
                additional_info={
                    "vulnerabilities": 0,
                    "severity": "low"
                }
            )
            
            results.append(result)
        except Exception as e:
            logger.error(f"Error running security tests: {str(e)}")
            # Create error result
            results.append(TestResult(
                test_id=f"{test_path}:security:error",
                test_type=TestType.SECURITY,
                component=component,
                passed=False,
                execution_time=0.0,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            ))
        
        return results
    
    def _should_run_test(self, test_name: str) -> bool:
        """
        Check if a test should be run based on include/exclude patterns.
        
        Args:
            test_name: The test name
            
        Returns:
            bool: True if the test should be run, False otherwise
        """
        # Check include patterns
        if self.config.include_patterns:
            included = False
            for pattern in self.config.include_patterns:
                if re.search(pattern, test_name):
                    included = True
                    break
            if not included:
                return False
        
        # Check exclude patterns
        for pattern in self.config.exclude_patterns:
            if re.search(pattern, test_name):
                return False
        
        return True

class Validator:
    """
    Validator for validating data and components.
    
    This class provides functionality for validating data against schemas
    and custom validation rules.
    """
    
    def __init__(self, config: ValidationConfig):
        """
        Initialize the validator.
        
        Args:
            config: Validation configuration
        """
        self.config = config
        self.results: List[ValidationResult] = []
    
    def validate_json_schema(self, data: Dict[str, Any], schema_name: str, component: str) -> ValidationResult:
        """
        Validate JSON data against a schema.
        
        Args:
            data: The data to validate
            schema_name: The schema name
            component: Component name
            
        Returns:
            ValidationResult: Validation result
        """
        try:
            import jsonschema
            
            # Get schema path
            schema_path = self.config.schema_paths.get(schema_name)
            if not schema_path:
                return ValidationResult(
                    validation_id=f"{component}:{schema_name}",
                    component=component,
                    valid=False,
                    level=self.config.level,
                    error_message=f"Schema not found: {schema_name}"
                )
            
            # Load schema
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            # Validate data
            start_time = time.time()
            jsonschema.validate(data, schema)
            end_time = time.time()
            
            # Create validation result
            result = ValidationResult(
                validation_id=f"{component}:{schema_name}",
                component=component,
                valid=True,
                level=self.config.level,
                details={
                    "execution_time": end_time - start_time
                }
            )
            
            return result
        except jsonschema.exceptions.ValidationError as e:
            # Validation failed
            return ValidationResult(
                validation_id=f"{component}:{schema_name}",
                component=component,
                valid=False,
                level=self.config.level,
                error_message=str(e),
                details={
                    "path": list(e.path),
                    "schema_path": list(e.schema_path)
                }
            )
        except Exception as e:
            # Other error
            logger.error(f"Error validating JSON schema: {str(e)}")
            return ValidationResult(
                validation_id=f"{component}:{schema_name}",
                component=component,
                valid=False,
                level=self.config.level,
                error_message=str(e)
            )
    
    def validate_custom(self, data: Any, validator_name: str, component: str) -> ValidationResult:
        """
        Validate data using a custom validator.
        
        Args:
            data: The data to validate
            validator_name: The validator name
            component: Component name
            
        Returns:
            ValidationResult: Validation result
        """
        try:
            # Get validator function
            validator = self.config.custom_validators.get(validator_name)
            if not validator:
                return ValidationResult(
                    validation_id=f"{component}:{validator_name}",
                    component=component,
                    valid=False,
                    level=self.config.level,
                    error_message=f"Validator not found: {validator_name}"
                )
            
            # Run validator
            start_time = time.time()
            valid, error_message, details = validator(data)
            end_time = time.time()
            
            # Create validation result
            result = ValidationResult(
                validation_id=f"{component}:{validator_name}",
                component=component,
                valid=valid,
                level=self.config.level,
                error_message=error_message,
                details=details or {
                    "execution_time": end_time - start_time
                }
            )
            
            return result
        except Exception as e:
            # Other error
            logger.error(f"Error running custom validator: {str(e)}")
            return ValidationResult(
                validation_id=f"{component}:{validator_name}",
                component=component,
                valid=False,
                level=self.config.level,
                error_message=str(e)
            )
    
    def validate_rules(self, data: Dict[str, Any], rule_set: str, component: str) -> List[ValidationResult]:
        """
        Validate data against a set of rules.
        
        Args:
            data: The data to validate
            rule_set: The rule set name
            component: Component name
            
        Returns:
            List[ValidationResult]: Validation results
        """
        results = []
        
        try:
            # Get rule set
            rule_set_config = self.config.validation_rules.get(rule_set)
            if not rule_set_config:
                results.append(ValidationResult(
                    validation_id=f"{component}:{rule_set}",
                    component=component,
                    valid=False,
                    level=self.config.level,
                    error_message=f"Rule set not found: {rule_set}"
                ))
                return results
            
            # Validate each rule
            for rule_name, rule_config in rule_set_config.items():
                try:
                    # Get rule type
                    rule_type = rule_config.get("type", "required")
                    
                    # Get field path
                    field_path = rule_config.get("field", "")
                    
                    # Get field value
                    field_value = self._get_field_value(data, field_path)
                    
                    # Validate based on rule type
                    valid = True
                    error_message = None
                    
                    if rule_type == "required":
                        valid = field_value is not None
                        if not valid:
                            error_message = f"Field is required: {field_path}"
                    
                    elif rule_type == "type":
                        expected_type = rule_config.get("expected", "string")
                        if expected_type == "string":
                            valid = isinstance(field_value, str)
                        elif expected_type == "number":
                            valid = isinstance(field_value, (int, float))
                        elif expected_type == "boolean":
                            valid = isinstance(field_value, bool)
                        elif expected_type == "array":
                            valid = isinstance(field_value, list)
                        elif expected_type == "object":
                            valid = isinstance(field_value, dict)
                        
                        if not valid:
                            error_message = f"Field has wrong type: {field_path}, expected {expected_type}"
                    
                    elif rule_type == "min_length":
                        min_length = rule_config.get("value", 0)
                        valid = isinstance(field_value, (str, list)) and len(field_value) >= min_length
                        if not valid:
                            error_message = f"Field length is too short: {field_path}, min {min_length}"
                    
                    elif rule_type == "max_length":
                        max_length = rule_config.get("value", 100)
                        valid = isinstance(field_value, (str, list)) and len(field_value) <= max_length
                        if not valid:
                            error_message = f"Field length is too long: {field_path}, max {max_length}"
                    
                    elif rule_type == "pattern":
                        pattern = rule_config.get("value", "")
                        valid = isinstance(field_value, str) and re.match(pattern, field_value) is not None
                        if not valid:
                            error_message = f"Field does not match pattern: {field_path}, pattern {pattern}"
                    
                    elif rule_type == "min_value":
                        min_value = rule_config.get("value", 0)
                        valid = isinstance(field_value, (int, float)) and field_value >= min_value
                        if not valid:
                            error_message = f"Field value is too small: {field_path}, min {min_value}"
                    
                    elif rule_type == "max_value":
                        max_value = rule_config.get("value", 0)
                        valid = isinstance(field_value, (int, float)) and field_value <= max_value
                        if not valid:
                            error_message = f"Field value is too large: {field_path}, max {max_value}"
                    
                    elif rule_type == "enum":
                        allowed_values = rule_config.get("values", [])
                        valid = field_value in allowed_values
                        if not valid:
                            error_message = f"Field value not in allowed values: {field_path}, allowed {allowed_values}"
                    
                    # Create validation result
                    results.append(ValidationResult(
                        validation_id=f"{component}:{rule_set}:{rule_name}",
                        component=component,
                        valid=valid,
                        level=self.config.level,
                        error_message=error_message,
                        details={
                            "rule_type": rule_type,
                            "field_path": field_path,
                            "field_value": field_value
                        }
                    ))
                except Exception as e:
                    # Rule validation error
                    logger.error(f"Error validating rule {rule_name}: {str(e)}")
                    results.append(ValidationResult(
                        validation_id=f"{component}:{rule_set}:{rule_name}",
                        component=component,
                        valid=False,
                        level=self.config.level,
                        error_message=str(e)
                    ))
        except Exception as e:
            # Other error
            logger.error(f"Error validating rules: {str(e)}")
            results.append(ValidationResult(
                validation_id=f"{component}:{rule_set}",
                component=component,
                valid=False,
                level=self.config.level,
                error_message=str(e)
            ))
        
        return results
    
    def _get_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Get a field value from nested data.
        
        Args:
            data: The data
            field_path: The field path (dot notation)
            
        Returns:
            Any: The field value, or None if not found
        """
        if not field_path:
            return data
        
        parts = field_path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif isinstance(value, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    return None
            else:
                return None
        
        return value

class CodeQualityAnalyzer:
    """
    Code quality analyzer for checking code quality.
    
    This class provides functionality for analyzing code quality,
    including complexity, style, and test coverage.
    """
    
    def __init__(self, config: CodeQualityConfig):
        """
        Initialize the code quality analyzer.
        
        Args:
            config: Code quality configuration
        """
        self.config = config
        self.results: List[CodeQualityResult] = []
    
    def analyze_file(self, file_path: str) -> CodeQualityResult:
        """
        Analyze a file for code quality.
        
        Args:
            file_path: Path to the file
            
        Returns:
            CodeQualityResult: Code quality result
        """
        metrics = {}
        issues = []
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return CodeQualityResult(
                    file_path=file_path,
                    metrics={},
                    issues=[{
                        "message": f"File not found: {file_path}",
                        "line": 0,
                        "column": 0,
                        "severity": "error"
                    }]
                )
            
            # Check file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() != '.py':
                return CodeQualityResult(
                    file_path=file_path,
                    metrics={},
                    issues=[{
                        "message": f"Unsupported file type: {ext}",
                        "line": 0,
                        "column": 0,
                        "severity": "warning"
                    }]
                )
            
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Analyze complexity
            if CodeQualityMetric.COMPLEXITY in self.config.enabled_metrics:
                complexity_metric, complexity_issues = self._analyze_complexity(file_path, content)
                metrics[CodeQualityMetric.COMPLEXITY] = complexity_metric
                issues.extend(complexity_issues)
            
            # Analyze style compliance
            if CodeQualityMetric.STYLE_COMPLIANCE in self.config.enabled_metrics:
                style_metric, style_issues = self._analyze_style(file_path)
                metrics[CodeQualityMetric.STYLE_COMPLIANCE] = style_metric
                issues.extend(style_issues)
            
            # Analyze type safety
            if CodeQualityMetric.TYPE_SAFETY in self.config.enabled_metrics and self.config.type_checking:
                type_metric, type_issues = self._analyze_types(file_path)
                metrics[CodeQualityMetric.TYPE_SAFETY] = type_metric
                issues.extend(type_issues)
            
            # Analyze documentation
            if CodeQualityMetric.DOCUMENTATION in self.config.enabled_metrics:
                doc_metric, doc_issues = self._analyze_documentation(file_path, content)
                metrics[CodeQualityMetric.DOCUMENTATION] = doc_metric
                issues.extend(doc_issues)
            
            # Create code quality result
            result = CodeQualityResult(
                file_path=file_path,
                metrics=metrics,
                issues=issues
            )
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return CodeQualityResult(
                file_path=file_path,
                metrics={},
                issues=[{
                    "message": f"Analysis error: {str(e)}",
                    "line": 0,
                    "column": 0,
                    "severity": "error"
                }]
            )
    
    def analyze_directory(self, directory_path: str, recursive: bool = True) -> List[CodeQualityResult]:
        """
        Analyze a directory for code quality.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to analyze subdirectories
            
        Returns:
            List[CodeQualityResult]: Code quality results
        """
        results = []
        
        try:
            # Check if directory exists
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                logger.error(f"Directory not found: {directory_path}")
                return results
            
            # Get Python files
            if recursive:
                for root, _, files in os.walk(directory_path):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            results.append(self.analyze_file(file_path))
            else:
                for file in os.listdir(directory_path):
                    if file.endswith('.py'):
                        file_path = os.path.join(directory_path, file)
                        results.append(self.analyze_file(file_path))
            
            return results
        except Exception as e:
            logger.error(f"Error analyzing directory {directory_path}: {str(e)}")
            return results
    
    def analyze_test_coverage(self, directory_path: str) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Analyze test coverage for a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Tuple[float, List[Dict[str, Any]]]: Coverage percentage and issues
        """
        try:
            # Create coverage object
            cov = coverage.Coverage()
            
            # Start coverage
            cov.start()
            
            # Run tests
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        test_path = os.path.join(root, file)
                        try:
                            # Run test
                            pytest.main([test_path, "-q"])
                        except Exception as e:
                            logger.error(f"Error running test {test_path}: {str(e)}")
            
            # Stop coverage
            cov.stop()
            
            # Get coverage data
            cov.save()
            
            # Create coverage report
            report = cov.report(show_missing=True)
            
            # Get coverage percentage
            coverage_percent = report
            
            # Get missing lines
            issues = []
            for file in cov.get_data().measured_files():
                analysis = cov._analyze(file)
                missing_lines = analysis.missing
                if missing_lines:
                    issues.append({
                        "file": file,
                        "missing_lines": list(missing_lines),
                        "severity": "warning"
                    })
            
            return coverage_percent, issues
        except Exception as e:
            logger.error(f"Error analyzing test coverage: {str(e)}")
            return 0.0, [{
                "message": f"Coverage analysis error: {str(e)}",
                "severity": "error"
            }]
    
    def _analyze_complexity(self, file_path: str, content: str) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Analyze code complexity.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Tuple[float, List[Dict[str, Any]]]: Complexity metric and issues
        """
        try:
            import radon.complexity
            import radon.metrics
            
            # Parse AST
            tree = ast.parse(content)
            
            # Calculate complexity
            complexity_visitor = radon.complexity.ComplexityVisitor.from_ast(tree)
            complexity_results = complexity_visitor.results
            
            # Calculate average complexity
            if complexity_results:
                avg_complexity = sum(result.complexity for result in complexity_results) / len(complexity_results)
            else:
                avg_complexity = 0.0
            
            # Create issues for high complexity
            issues = []
            for result in complexity_results:
                if result.complexity > self.config.max_complexity:
                    issues.append({
                        "message": f"High complexity ({result.complexity}) in {result.name}",
                        "line": result.lineno,
                        "column": 0,
                        "severity": "warning"
                    })
            
            return avg_complexity, issues
        except Exception as e:
            logger.error(f"Error analyzing complexity: {str(e)}")
            return 0.0, [{
                "message": f"Complexity analysis error: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "error"
            }]
    
    def _analyze_style(self, file_path: str) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Analyze code style compliance.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple[float, List[Dict[str, Any]]]: Style compliance metric and issues
        """
        try:
            # Create a custom reporter to capture pylint output
            class Reporter:
                def __init__(self):
                    self.issues = []
                
                def handle_message(self, msg):
                    self.issues.append({
                        "message": msg.msg,
                        "line": msg.line,
                        "column": msg.column,
                        "severity": msg.category
                    })
                
                def on_set_current_module(self, *args, **kwargs):
                    pass
                
                def on_close(self, *args, **kwargs):
                    pass
            
            reporter = Reporter()
            
            # Run pylint
            args = [file_path]
            if self.config.lint_config_path:
                args.extend(["--rcfile", self.config.lint_config_path])
            
            pylint.lint.Run(args, reporter=reporter, exit=False)
            
            # Calculate style compliance metric
            if reporter.issues:
                # Lower is better (0 = perfect)
                style_metric = 10.0 - min(10.0, len(reporter.issues))
            else:
                style_metric = 10.0
            
            return style_metric, reporter.issues
        except Exception as e:
            logger.error(f"Error analyzing style: {str(e)}")
            return 0.0, [{
                "message": f"Style analysis error: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "error"
            }]
    
    def _analyze_types(self, file_path: str) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Analyze type safety.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple[float, List[Dict[str, Any]]]: Type safety metric and issues
        """
        try:
            # Run mypy
            result, error_messages, _ = mypy.api.run([file_path])
            
            # Parse error messages
            issues = []
            for message in error_messages:
                parts = message.split(":", 3)
                if len(parts) >= 3:
                    try:
                        line = int(parts[1])
                        issues.append({
                            "message": parts[3].strip() if len(parts) > 3 else "Type error",
                            "line": line,
                            "column": 0,
                            "severity": "error"
                        })
                    except ValueError:
                        issues.append({
                            "message": message,
                            "line": 0,
                            "column": 0,
                            "severity": "error"
                        })
                else:
                    issues.append({
                        "message": message,
                        "line": 0,
                        "column": 0,
                        "severity": "error"
                    })
            
            # Calculate type safety metric
            if issues:
                # Lower is better (0 = perfect)
                type_metric = 10.0 - min(10.0, len(issues))
            else:
                type_metric = 10.0
            
            return type_metric, issues
        except Exception as e:
            logger.error(f"Error analyzing types: {str(e)}")
            return 0.0, [{
                "message": f"Type analysis error: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "error"
            }]
    
    def _analyze_documentation(self, file_path: str, content: str) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Analyze documentation quality.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Tuple[float, List[Dict[str, Any]]]: Documentation metric and issues
        """
        try:
            # Parse AST
            tree = ast.parse(content)
            
            # Find all functions and classes
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node)
            
            # Check for docstrings
            missing_docs = []
            
            for func in functions:
                if not ast.get_docstring(func):
                    missing_docs.append({
                        "message": f"Missing docstring for function {func.name}",
                        "line": func.lineno,
                        "column": func.col_offset,
                        "severity": "warning"
                    })
            
            for cls in classes:
                if not ast.get_docstring(cls):
                    missing_docs.append({
                        "message": f"Missing docstring for class {cls.name}",
                        "line": cls.lineno,
                        "column": cls.col_offset,
                        "severity": "warning"
                    })
            
            # Calculate documentation metric
            total_items = len(functions) + len(classes)
            if total_items > 0:
                documented_items = total_items - len(missing_docs)
                doc_metric = (documented_items / total_items) * 10.0
            else:
                doc_metric = 10.0
            
            return doc_metric, missing_docs
        except Exception as e:
            logger.error(f"Error analyzing documentation: {str(e)}")
            return 0.0, [{
                "message": f"Documentation analysis error: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "error"
            }]

class QualityAssurance:
    """
    Quality assurance framework for ApexAgent.
    
    This class provides comprehensive quality assurance capabilities including:
    - Automated testing
    - Data validation
    - Code quality analysis
    - Test coverage analysis
    - Quality reporting
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'QualityAssurance':
        """
        Get the singleton instance of the quality assurance framework.
        
        Returns:
            QualityAssurance: The singleton instance
        """
        if cls._instance is None:
            cls._instance = QualityAssurance()
        return cls._instance
    
    def __init__(self):
        """Initialize the quality assurance framework."""
        self.config = QualityAssuranceConfig()
        self.test_runners: Dict[str, TestRunner] = {}
        self.validators: Dict[str, Validator] = {}
        self.code_quality_analyzers: Dict[str, CodeQualityAnalyzer] = {}
        self.reports: List[QualityReport] = []
        self._lock = threading.RLock()
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the quality assurance framework.
        
        Args:
            config_path: Optional path to configuration file
        """
        if config_path and os.path.exists(config_path):
            self.config.load_from_file(config_path)
        
        # Create report directory if it doesn't exist
        os.makedirs(self.config.report_dir, exist_ok=True)
        
        logger.info("Quality assurance framework initialized")
    
    def get_test_runner(self, component: str) -> TestRunner:
        """
        Get or create a test runner for a component.
        
        Args:
            component: Component name
            
        Returns:
            TestRunner: The test runner
        """
        with self._lock:
            if component not in self.test_runners:
                config = self.config.get_test_config(component)
                self.test_runners[component] = TestRunner(config)
            return self.test_runners[component]
    
    def get_validator(self, component: str) -> Validator:
        """
        Get or create a validator for a component.
        
        Args:
            component: Component name
            
        Returns:
            Validator: The validator
        """
        with self._lock:
            if component not in self.validators:
                config = self.config.get_validation_config(component)
                self.validators[component] = Validator(config)
            return self.validators[component]
    
    def get_code_quality_analyzer(self, component: str) -> CodeQualityAnalyzer:
        """
        Get or create a code quality analyzer for a component.
        
        Args:
            component: Component name
            
        Returns:
            CodeQualityAnalyzer: The code quality analyzer
        """
        with self._lock:
            if component not in self.code_quality_analyzers:
                config = self.config.get_code_quality_config(component)
                self.code_quality_analyzers[component] = CodeQualityAnalyzer(config)
            return self.code_quality_analyzers[component]
    
    def run_tests(self, component: str, test_paths: List[str]) -> List[TestResult]:
        """
        Run tests for a component.
        
        Args:
            component: Component name
            test_paths: Paths to test files or directories
            
        Returns:
            List[TestResult]: Test results
        """
        results = []
        
        try:
            # Get test runner
            test_runner = self.get_test_runner(component)
            
            # Run tests for each path
            for test_path in test_paths:
                # Check if path exists
                if not os.path.exists(test_path):
                    logger.warning(f"Test path not found: {test_path}")
                    continue
                
                # Determine test type based on path
                if "unit" in test_path.lower():
                    test_type = TestType.UNIT
                elif "integration" in test_path.lower():
                    test_type = TestType.INTEGRATION
                elif "functional" in test_path.lower():
                    test_type = TestType.FUNCTIONAL
                elif "performance" in test_path.lower():
                    test_type = TestType.PERFORMANCE
                elif "security" in test_path.lower():
                    test_type = TestType.SECURITY
                else:
                    test_type = TestType.UNIT
                
                # Check if test type is enabled
                if not test_runner.config.is_test_type_enabled(test_type):
                    logger.info(f"Skipping disabled test type: {test_type.value}")
                    continue
                
                # Run tests based on type
                if test_type == TestType.UNIT:
                    if test_path.endswith('.py'):
                        # Run unittest for single file
                        path_results = test_runner.run_unittest(test_path, component)
                    else:
                        # Run pytest for directory
                        path_results = test_runner.run_pytest(test_path, component)
                elif test_type == TestType.INTEGRATION:
                    path_results = test_runner.run_integration_test(test_path, component)
                elif test_type == TestType.FUNCTIONAL:
                    path_results = test_runner.run_functional_test(test_path, component)
                elif test_type == TestType.PERFORMANCE:
                    path_results = test_runner.run_performance_test(test_path, component)
                elif test_type == TestType.SECURITY:
                    path_results = test_runner.run_security_test(test_path, component)
                else:
                    logger.warning(f"Unsupported test type: {test_type.value}")
                    continue
                
                # Add results
                results.extend(path_results)
                
                # Stop if fail fast is enabled and any test failed
                if test_runner.config.fail_fast and any(not result.passed for result in path_results):
                    logger.warning("Stopping tests due to fail fast")
                    break
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
        
        return results
    
    def validate_data(self, component: str, data: Dict[str, Any], schema_name: str) -> ValidationResult:
        """
        Validate data against a schema.
        
        Args:
            component: Component name
            data: The data to validate
            schema_name: The schema name
            
        Returns:
            ValidationResult: Validation result
        """
        try:
            # Get validator
            validator = self.get_validator(component)
            
            # Validate data
            result = validator.validate_json_schema(data, schema_name, component)
            
            return result
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return ValidationResult(
                validation_id=f"{component}:{schema_name}",
                component=component,
                valid=False,
                level=validator.config.level,
                error_message=str(e)
            )
    
    def validate_custom(self, component: str, data: Any, validator_name: str) -> ValidationResult:
        """
        Validate data using a custom validator.
        
        Args:
            component: Component name
            data: The data to validate
            validator_name: The validator name
            
        Returns:
            ValidationResult: Validation result
        """
        try:
            # Get validator
            validator = self.get_validator(component)
            
            # Validate data
            result = validator.validate_custom(data, validator_name, component)
            
            return result
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return ValidationResult(
                validation_id=f"{component}:{validator_name}",
                component=component,
                valid=False,
                level=validator.config.level,
                error_message=str(e)
            )
    
    def validate_rules(self, component: str, data: Dict[str, Any], rule_set: str) -> List[ValidationResult]:
        """
        Validate data against a set of rules.
        
        Args:
            component: Component name
            data: The data to validate
            rule_set: The rule set name
            
        Returns:
            List[ValidationResult]: Validation results
        """
        try:
            # Get validator
            validator = self.get_validator(component)
            
            # Validate data
            results = validator.validate_rules(data, rule_set, component)
            
            return results
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return [ValidationResult(
                validation_id=f"{component}:{rule_set}",
                component=component,
                valid=False,
                level=validator.config.level,
                error_message=str(e)
            )]
    
    def analyze_code_quality(self, component: str, file_path: str) -> CodeQualityResult:
        """
        Analyze code quality for a file.
        
        Args:
            component: Component name
            file_path: Path to the file
            
        Returns:
            CodeQualityResult: Code quality result
        """
        try:
            # Get code quality analyzer
            analyzer = self.get_code_quality_analyzer(component)
            
            # Analyze file
            result = analyzer.analyze_file(file_path)
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing code quality: {str(e)}")
            return CodeQualityResult(
                file_path=file_path,
                metrics={},
                issues=[{
                    "message": f"Analysis error: {str(e)}",
                    "line": 0,
                    "column": 0,
                    "severity": "error"
                }]
            )
    
    def analyze_directory_quality(self, component: str, directory_path: str, recursive: bool = True) -> List[CodeQualityResult]:
        """
        Analyze code quality for a directory.
        
        Args:
            component: Component name
            directory_path: Path to the directory
            recursive: Whether to analyze subdirectories
            
        Returns:
            List[CodeQualityResult]: Code quality results
        """
        try:
            # Get code quality analyzer
            analyzer = self.get_code_quality_analyzer(component)
            
            # Analyze directory
            results = analyzer.analyze_directory(directory_path, recursive)
            
            return results
        except Exception as e:
            logger.error(f"Error analyzing directory quality: {str(e)}")
            return []
    
    def analyze_test_coverage(self, component: str, directory_path: str) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Analyze test coverage for a directory.
        
        Args:
            component: Component name
            directory_path: Path to the directory
            
        Returns:
            Tuple[float, List[Dict[str, Any]]]: Coverage percentage and issues
        """
        try:
            # Get code quality analyzer
            analyzer = self.get_code_quality_analyzer(component)
            
            # Analyze test coverage
            coverage_percent, issues = analyzer.analyze_test_coverage(directory_path)
            
            return coverage_percent, issues
        except Exception as e:
            logger.error(f"Error analyzing test coverage: {str(e)}")
            return 0.0, [{
                "message": f"Coverage analysis error: {str(e)}",
                "severity": "error"
            }]
    
    def create_quality_report(self, report_id: Optional[str] = None) -> QualityReport:
        """
        Create a quality report.
        
        Args:
            report_id: Optional report ID
            
        Returns:
            QualityReport: The quality report
        """
        # Generate report ID if not provided
        if not report_id:
            report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create report
        report = QualityReport(report_id=report_id)
        
        # Add test results
        for test_runner in self.test_runners.values():
            report.test_results.extend(test_runner.results)
        
        # Add validation results
        for validator in self.validators.values():
            report.validation_results.extend(validator.results)
        
        # Add code quality results
        for analyzer in self.code_quality_analyzers.values():
            report.code_quality_results.extend(analyzer.results)
        
        # Calculate summary
        summary = self._calculate_summary(report)
        report.summary = summary
        
        # Add to reports list
        with self._lock:
            self.reports.append(report)
            
            # Limit number of reports
            if len(self.reports) > self.config.test_result_history:
                self.reports = self.reports[-self.config.test_result_history:]
        
        # Save report
        report_path = os.path.join(self.config.report_dir, f"{report_id}.json")
        report.save_to_file(report_path)
        
        # Send notification if enabled
        if self.config.notification_enabled:
            self._send_notification(report)
        
        return report
    
    def _calculate_summary(self, report: QualityReport) -> Dict[str, Any]:
        """
        Calculate summary for a quality report.
        
        Args:
            report: The quality report
            
        Returns:
            Dict[str, Any]: The summary
        """
        summary = {
            "total_tests": len(report.test_results),
            "passed_tests": sum(1 for result in report.test_results if result.passed),
            "failed_tests": sum(1 for result in report.test_results if not result.passed),
            "total_validations": len(report.validation_results),
            "passed_validations": sum(1 for result in report.validation_results if result.valid),
            "failed_validations": sum(1 for result in report.validation_results if not result.valid),
            "total_files_analyzed": len(report.code_quality_results),
            "quality_metrics": {},
            "components": {}
        }
        
        # Calculate test pass rate
        if summary["total_tests"] > 0:
            summary["test_pass_rate"] = (summary["passed_tests"] / summary["total_tests"]) * 100.0
        else:
            summary["test_pass_rate"] = 0.0
        
        # Calculate validation pass rate
        if summary["total_validations"] > 0:
            summary["validation_pass_rate"] = (summary["passed_validations"] / summary["total_validations"]) * 100.0
        else:
            summary["validation_pass_rate"] = 0.0
        
        # Calculate average quality metrics
        metrics_count = {}
        metrics_sum = {}
        
        for result in report.code_quality_results:
            for metric, value in result.metrics.items():
                if metric not in metrics_sum:
                    metrics_sum[metric] = 0.0
                    metrics_count[metric] = 0
                
                metrics_sum[metric] += value
                metrics_count[metric] += 1
        
        for metric, total in metrics_sum.items():
            count = metrics_count[metric]
            if count > 0:
                summary["quality_metrics"][metric.value] = total / count
        
        # Calculate component-specific summaries
        component_tests = {}
        component_validations = {}
        component_quality = {}
        
        for result in report.test_results:
            if result.component not in component_tests:
                component_tests[result.component] = {"total": 0, "passed": 0}
            
            component_tests[result.component]["total"] += 1
            if result.passed:
                component_tests[result.component]["passed"] += 1
        
        for result in report.validation_results:
            if result.component not in component_validations:
                component_validations[result.component] = {"total": 0, "passed": 0}
            
            component_validations[result.component]["total"] += 1
            if result.valid:
                component_validations[result.component]["passed"] += 1
        
        for result in report.code_quality_results:
            # Extract component from file path
            path_parts = result.file_path.split(os.path.sep)
            component = path_parts[-2] if len(path_parts) > 1 else "unknown"
            
            if component not in component_quality:
                component_quality[component] = {"total": 0, "metrics": {}}
            
            component_quality[component]["total"] += 1
            
            for metric, value in result.metrics.items():
                if metric not in component_quality[component]["metrics"]:
                    component_quality[component]["metrics"][metric.value] = {"sum": 0.0, "count": 0}
                
                component_quality[component]["metrics"][metric.value]["sum"] += value
                component_quality[component]["metrics"][metric.value]["count"] += 1
        
        # Combine component summaries
        all_components = set(list(component_tests.keys()) + list(component_validations.keys()) + list(component_quality.keys()))
        
        for component in all_components:
            summary["components"][component] = {
                "tests": component_tests.get(component, {"total": 0, "passed": 0}),
                "validations": component_validations.get(component, {"total": 0, "passed": 0}),
                "quality": {"metrics": {}}
            }
            
            # Calculate test pass rate
            tests = summary["components"][component]["tests"]
            if tests["total"] > 0:
                tests["pass_rate"] = (tests["passed"] / tests["total"]) * 100.0
            else:
                tests["pass_rate"] = 0.0
            
            # Calculate validation pass rate
            validations = summary["components"][component]["validations"]
            if validations["total"] > 0:
                validations["pass_rate"] = (validations["passed"] / validations["total"]) * 100.0
            else:
                validations["pass_rate"] = 0.0
            
            # Calculate average quality metrics
            if component in component_quality:
                for metric_name, data in component_quality[component]["metrics"].items():
                    if data["count"] > 0:
                        summary["components"][component]["quality"]["metrics"][metric_name] = data["sum"] / data["count"]
        
        # Calculate overall quality score
        quality_score = 0.0
        quality_factors = 0
        
        if summary["total_tests"] > 0:
            quality_score += summary["test_pass_rate"]
            quality_factors += 1
        
        if summary["total_validations"] > 0:
            quality_score += summary["validation_pass_rate"]
            quality_factors += 1
        
        for metric, value in summary["quality_metrics"].items():
            quality_score += value * 10.0  # Scale to 0-100
            quality_factors += 1
        
        if quality_factors > 0:
            summary["quality_score"] = quality_score / quality_factors
        else:
            summary["quality_score"] = 0.0
        
        return summary
    
    def _send_notification(self, report: QualityReport) -> None:
        """
        Send notification for a quality report.
        
        Args:
            report: The quality report
        """
        try:
            # Check if notification should be sent
            if report.summary.get("quality_score", 0.0) < self.config.notification_threshold:
                logger.warning(
                    f"Quality score ({report.summary.get('quality_score', 0.0):.2f}) "
                    f"below threshold ({self.config.notification_threshold:.2f})"
                )
                
                # In a real implementation, this would send a notification
                # via email, Slack, etc.
                
                # For this example, we'll just log it
                logger.info(f"Notification sent for report: {report.report_id}")
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def get_latest_report(self) -> Optional[QualityReport]:
        """
        Get the latest quality report.
        
        Returns:
            Optional[QualityReport]: The latest report, or None if no reports exist
        """
        with self._lock:
            if self.reports:
                return self.reports[-1]
            return None
    
    def get_report(self, report_id: str) -> Optional[QualityReport]:
        """
        Get a quality report by ID.
        
        Args:
            report_id: The report ID
            
        Returns:
            Optional[QualityReport]: The report, or None if not found
        """
        with self._lock:
            for report in self.reports:
                if report.report_id == report_id:
                    return report
            
            # Try to load from file
            report_path = os.path.join(self.config.report_dir, f"{report_id}.json")
            if os.path.exists(report_path):
                return QualityReport.load_from_file(report_path)
            
            return None
    
    def register_custom_validator(self, component: str, validator_name: str, validator_func: Callable) -> None:
        """
        Register a custom validator.
        
        Args:
            component: Component name
            validator_name: The validator name
            validator_func: The validator function
        """
        try:
            # Get validator
            validator = self.get_validator(component)
            
            # Register custom validator
            validator.config.custom_validators[validator_name] = validator_func
            
            logger.info(f"Registered custom validator: {validator_name} for component {component}")
        except Exception as e:
            logger.error(f"Error registering custom validator: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the quality assurance framework.
        
        Returns:
            Dict: Metrics about the quality assurance framework
        """
        with self._lock:
            metrics = {
                "test_runners": len(self.test_runners),
                "validators": len(self.validators),
                "code_quality_analyzers": len(self.code_quality_analyzers),
                "reports": len(self.reports),
                "latest_report": None
            }
            
            # Add latest report summary
            latest_report = self.get_latest_report()
            if latest_report:
                metrics["latest_report"] = {
                    "report_id": latest_report.report_id,
                    "timestamp": latest_report.timestamp.isoformat(),
                    "quality_score": latest_report.summary.get("quality_score", 0.0),
                    "test_pass_rate": latest_report.summary.get("test_pass_rate", 0.0),
                    "validation_pass_rate": latest_report.summary.get("validation_pass_rate", 0.0)
                }
            
            return metrics


# Global instance for easy access
quality_assurance = QualityAssurance.get_instance()


def initialize_quality_assurance(config_path: Optional[str] = None) -> None:
    """
    Initialize the quality assurance framework.
    
    Args:
        config_path: Optional path to configuration file
    """
    quality_assurance.initialize(config_path)


def run_tests(component: str, test_paths: List[str]) -> List[TestResult]:
    """
    Run tests for a component.
    
    Args:
        component: Component name
        test_paths: Paths to test files or directories
        
    Returns:
        List[TestResult]: Test results
    """
    return quality_assurance.run_tests(component, test_paths)


def validate_data(component: str, data: Dict[str, Any], schema_name: str) -> ValidationResult:
    """
    Validate data against a schema.
    
    Args:
        component: Component name
        data: The data to validate
        schema_name: The schema name
        
    Returns:
        ValidationResult: Validation result
    """
    return quality_assurance.validate_data(component, data, schema_name)


def validate_custom(component: str, data: Any, validator_name: str) -> ValidationResult:
    """
    Validate data using a custom validator.
    
    Args:
        component: Component name
        data: The data to validate
        validator_name: The validator name
        
    Returns:
        ValidationResult: Validation result
    """
    return quality_assurance.validate_custom(component, data, validator_name)


def validate_rules(component: str, data: Dict[str, Any], rule_set: str) -> List[ValidationResult]:
    """
    Validate data against a set of rules.
    
    Args:
        component: Component name
        data: The data to validate
        rule_set: The rule set name
        
    Returns:
        List[ValidationResult]: Validation results
    """
    return quality_assurance.validate_rules(component, data, rule_set)


def analyze_code_quality(component: str, file_path: str) -> CodeQualityResult:
    """
    Analyze code quality for a file.
    
    Args:
        component: Component name
        file_path: Path to the file
        
    Returns:
        CodeQualityResult: Code quality result
    """
    return quality_assurance.analyze_code_quality(component, file_path)


def analyze_directory_quality(component: str, directory_path: str, recursive: bool = True) -> List[CodeQualityResult]:
    """
    Analyze code quality for a directory.
    
    Args:
        component: Component name
        directory_path: Path to the directory
        recursive: Whether to analyze subdirectories
        
    Returns:
        List[CodeQualityResult]: Code quality results
    """
    return quality_assurance.analyze_directory_quality(component, directory_path, recursive)


def analyze_test_coverage(component: str, directory_path: str) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Analyze test coverage for a directory.
    
    Args:
        component: Component name
        directory_path: Path to the directory
        
    Returns:
        Tuple[float, List[Dict[str, Any]]]: Coverage percentage and issues
    """
    return quality_assurance.analyze_test_coverage(component, directory_path)


def create_quality_report(report_id: Optional[str] = None) -> QualityReport:
    """
    Create a quality report.
    
    Args:
        report_id: Optional report ID
        
    Returns:
        QualityReport: The quality report
    """
    return quality_assurance.create_quality_report(report_id)


def get_latest_report() -> Optional[QualityReport]:
    """
    Get the latest quality report.
    
    Returns:
        Optional[QualityReport]: The latest report, or None if no reports exist
    """
    return quality_assurance.get_latest_report()


def get_report(report_id: str) -> Optional[QualityReport]:
    """
    Get a quality report by ID.
    
    Args:
        report_id: The report ID
        
    Returns:
        Optional[QualityReport]: The report, or None if not found
    """
    return quality_assurance.get_report(report_id)


def register_custom_validator(component: str, validator_name: str, validator_func: Callable) -> None:
    """
    Register a custom validator.
    
    Args:
        component: Component name
        validator_name: The validator name
        validator_func: The validator function
    """
    quality_assurance.register_custom_validator(component, validator_name, validator_func)


def get_metrics() -> Dict[str, Any]:
    """
    Get metrics about the quality assurance framework.
    
    Returns:
        Dict: Metrics about the quality assurance framework
    """
    return quality_assurance.get_metrics()


# Example usage
if __name__ == "__main__":
    # Initialize quality assurance
    initialize_quality_assurance()
    
    # Define a custom validator
    def validate_user_data(data):
        valid = True
        error_message = None
        details = {}
        
        # Check required fields
        if "username" not in data:
            valid = False
            error_message = "Username is required"
        elif len(data["username"]) < 3:
            valid = False
            error_message = "Username must be at least 3 characters"
        
        if "email" not in data:
            valid = False
            error_message = "Email is required"
        elif "@" not in data["email"]:
            valid = False
            error_message = "Invalid email format"
        
        return valid, error_message, details
    
    # Register custom validator
    register_custom_validator("user", "user_data", validate_user_data)
    
    # Validate data
    user_data = {
        "username": "john",
        "email": "john@example.com"
    }
    
    result = validate_custom("user", user_data, "user_data")
    print(f"Validation result: {result.valid}")
    
    # Create quality report
    report = create_quality_report()
    print(f"Report ID: {report.report_id}")
    
    # Get metrics
    metrics = get_metrics()
    print(f"Metrics: {metrics}")
