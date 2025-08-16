#!/usr/bin/env python3
"""
Error Handling and Resilience Framework for ApexAgent

This module provides a comprehensive error handling and resilience framework
with automatic retry mechanisms, fallback strategies, circuit breakers,
and graceful degradation capabilities.
"""

import os
import sys
import time
import json
import logging
import traceback
import functools
import threading
import queue
import random
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, TypeVar, cast
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("error_handling.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("error_handling")

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')

class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    CRITICAL = "critical"  # System cannot continue, requires immediate attention
    HIGH = "high"          # Major functionality is impacted, requires prompt attention
    MEDIUM = "medium"      # Some functionality is impacted, should be addressed soon
    LOW = "low"            # Minor issue, can be addressed in regular maintenance
    INFO = "info"          # Informational only, no action required

class ErrorCategory(Enum):
    """Enumeration of error categories."""
    SYSTEM = "system"              # Operating system, hardware, or environment errors
    NETWORK = "network"            # Network connectivity or communication errors
    DATABASE = "database"          # Database access or query errors
    API = "api"                    # API call or response errors
    AUTHENTICATION = "auth"        # Authentication or authorization errors
    VALIDATION = "validation"      # Input validation errors
    BUSINESS_LOGIC = "business"    # Business logic or rule violations
    RESOURCE = "resource"          # Resource availability or capacity errors
    CONFIGURATION = "config"       # Configuration or setup errors
    DEPENDENCY = "dependency"      # External dependency errors
    UNKNOWN = "unknown"            # Unclassified errors

class CircuitState(Enum):
    """Enumeration of circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests are allowed
    OPEN = "open"          # Failure threshold exceeded, requests are blocked
    HALF_OPEN = "half_open"  # Testing if service has recovered

@dataclass
class ErrorContext:
    """Context information for an error."""
    timestamp: datetime = field(default_factory=datetime.now)
    component: str = ""
    operation: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    error: Exception
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    traceback: str
    handled: bool = False
    resolution_steps: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error record to a dictionary."""
        return {
            "error_type": self.error.__class__.__name__,
            "error_message": str(self.error),
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.context.timestamp.isoformat(),
            "component": self.context.component,
            "operation": self.context.operation,
            "user_id": self.context.user_id,
            "session_id": self.context.session_id,
            "request_id": self.context.request_id,
            "input_data": self.context.input_data,
            "additional_info": self.context.additional_info,
            "traceback": self.traceback,
            "handled": self.handled,
            "resolution_steps": self.resolution_steps
        }

class RetryStrategy(Enum):
    """Enumeration of retry strategies."""
    FIXED = "fixed"                # Fixed delay between retries
    EXPONENTIAL = "exponential"    # Exponential backoff
    FIBONACCI = "fibonacci"        # Fibonacci sequence delay
    RANDOM = "random"              # Random delay within a range

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    jitter: bool = True  # Add randomness to avoid thundering herd
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate the delay for a retry attempt.
        
        Args:
            attempt: The current retry attempt (1-based)
            
        Returns:
            float: The delay in seconds
        """
        if attempt <= 0:
            return 0
        
        if self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (2 ** (attempt - 1))
        elif self.strategy == RetryStrategy.FIBONACCI:
            # Calculate Fibonacci number
            a, b = 1, 1
            for _ in range(attempt - 1):
                a, b = b, a + b
            delay = self.base_delay * a
        elif self.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(self.base_delay, self.base_delay * attempt)
        else:
            delay = self.base_delay
        
        # Apply maximum delay
        delay = min(delay, self.max_delay)
        
        # Add jitter if enabled (±10%)
        if self.jitter:
            jitter_factor = random.uniform(0.9, 1.1)
            delay *= jitter_factor
        
        return delay

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5  # Number of failures before opening circuit
    recovery_timeout: float = 30.0  # Seconds to wait before testing recovery
    success_threshold: int = 2  # Number of successes needed to close circuit
    timeout: float = 10.0  # Seconds to wait for a response before considering it a failure
    include_exceptions: List[Type[Exception]] = field(default_factory=list)  # Exception types to count as failures
    exclude_exceptions: List[Type[Exception]] = field(default_factory=list)  # Exception types to ignore

@dataclass
class FallbackConfig:
    """Configuration for fallback behavior."""
    enabled: bool = True
    strategies: List[str] = field(default_factory=list)  # List of fallback strategy names
    max_fallbacks: int = 3  # Maximum number of fallbacks to attempt

class ErrorHandlingConfig:
    """Configuration for the error handling framework."""
    
    def __init__(self):
        """Initialize the error handling configuration."""
        self.retry_configs: Dict[str, RetryConfig] = {}
        self.circuit_breaker_configs: Dict[str, CircuitBreakerConfig] = {}
        self.fallback_configs: Dict[str, FallbackConfig] = {}
        self.global_retry_config = RetryConfig()
        self.global_circuit_breaker_config = CircuitBreakerConfig()
        self.global_fallback_config = FallbackConfig()
        self.error_handlers: Dict[Type[Exception], List[Callable[[ErrorRecord], None]]] = {}
        self.error_queue_size: int = 1000
        self.error_processors: int = 2
        self.log_all_errors: bool = True
        self.telemetry_enabled: bool = True
        self.alert_on_severity: List[ErrorSeverity] = [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]
    
    def get_retry_config(self, operation: str) -> RetryConfig:
        """
        Get the retry configuration for an operation.
        
        Args:
            operation: The operation name
            
        Returns:
            RetryConfig: The retry configuration
        """
        return self.retry_configs.get(operation, self.global_retry_config)
    
    def get_circuit_breaker_config(self, operation: str) -> CircuitBreakerConfig:
        """
        Get the circuit breaker configuration for an operation.
        
        Args:
            operation: The operation name
            
        Returns:
            CircuitBreakerConfig: The circuit breaker configuration
        """
        return self.circuit_breaker_configs.get(operation, self.global_circuit_breaker_config)
    
    def get_fallback_config(self, operation: str) -> FallbackConfig:
        """
        Get the fallback configuration for an operation.
        
        Args:
            operation: The operation name
            
        Returns:
            FallbackConfig: The fallback configuration
        """
        return self.fallback_configs.get(operation, self.global_fallback_config)
    
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
            
            # Load global retry config
            if "global_retry" in config_data:
                retry_data = config_data["global_retry"]
                self.global_retry_config = RetryConfig(
                    max_retries=retry_data.get("max_retries", 3),
                    strategy=RetryStrategy(retry_data.get("strategy", "exponential")),
                    base_delay=retry_data.get("base_delay", 1.0),
                    max_delay=retry_data.get("max_delay", 60.0),
                    jitter=retry_data.get("jitter", True)
                )
            
            # Load global circuit breaker config
            if "global_circuit_breaker" in config_data:
                cb_data = config_data["global_circuit_breaker"]
                self.global_circuit_breaker_config = CircuitBreakerConfig(
                    failure_threshold=cb_data.get("failure_threshold", 5),
                    recovery_timeout=cb_data.get("recovery_timeout", 30.0),
                    success_threshold=cb_data.get("success_threshold", 2),
                    timeout=cb_data.get("timeout", 10.0)
                )
            
            # Load global fallback config
            if "global_fallback" in config_data:
                fb_data = config_data["global_fallback"]
                self.global_fallback_config = FallbackConfig(
                    enabled=fb_data.get("enabled", True),
                    strategies=fb_data.get("strategies", []),
                    max_fallbacks=fb_data.get("max_fallbacks", 3)
                )
            
            # Load operation-specific configs
            if "operations" in config_data:
                for op_name, op_config in config_data["operations"].items():
                    # Load retry config
                    if "retry" in op_config:
                        retry_data = op_config["retry"]
                        self.retry_configs[op_name] = RetryConfig(
                            max_retries=retry_data.get("max_retries", 3),
                            strategy=RetryStrategy(retry_data.get("strategy", "exponential")),
                            base_delay=retry_data.get("base_delay", 1.0),
                            max_delay=retry_data.get("max_delay", 60.0),
                            jitter=retry_data.get("jitter", True)
                        )
                    
                    # Load circuit breaker config
                    if "circuit_breaker" in op_config:
                        cb_data = op_config["circuit_breaker"]
                        self.circuit_breaker_configs[op_name] = CircuitBreakerConfig(
                            failure_threshold=cb_data.get("failure_threshold", 5),
                            recovery_timeout=cb_data.get("recovery_timeout", 30.0),
                            success_threshold=cb_data.get("success_threshold", 2),
                            timeout=cb_data.get("timeout", 10.0)
                        )
                    
                    # Load fallback config
                    if "fallback" in op_config:
                        fb_data = op_config["fallback"]
                        self.fallback_configs[op_name] = FallbackConfig(
                            enabled=fb_data.get("enabled", True),
                            strategies=fb_data.get("strategies", []),
                            max_fallbacks=fb_data.get("max_fallbacks", 3)
                        )
            
            # Load framework settings
            if "framework" in config_data:
                framework = config_data["framework"]
                self.error_queue_size = framework.get("error_queue_size", 1000)
                self.error_processors = framework.get("error_processors", 2)
                self.log_all_errors = framework.get("log_all_errors", True)
                self.telemetry_enabled = framework.get("telemetry_enabled", True)
                
                # Load alert severity levels
                if "alert_on_severity" in framework:
                    self.alert_on_severity = [
                        ErrorSeverity(sev) for sev in framework["alert_on_severity"]
                    ]
            
            logger.info(f"Configuration loaded successfully from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {str(e)}")
            return False

class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascading failures.
    
    The circuit breaker monitors for failures and temporarily blocks requests
    when a failure threshold is reached, allowing the system to recover.
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        """
        Initialize the circuit breaker.
        
        Args:
            name: Name of the circuit breaker
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = datetime.min
        self.last_success_time = datetime.min
        self.last_state_change_time = datetime.now()
        self._lock = threading.RLock()
    
    def allow_request(self) -> bool:
        """
        Check if a request is allowed to proceed.
        
        Returns:
            bool: True if the request is allowed, False otherwise
        """
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has elapsed
                now = datetime.now()
                if (now - self.last_state_change_time).total_seconds() >= self.config.recovery_timeout:
                    logger.info(f"Circuit {self.name} transitioning from OPEN to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.last_state_change_time = now
                    self.success_count = 0
                    return True
                return False
            
            # HALF_OPEN state: allow limited requests to test recovery
            return True
    
    def record_success(self) -> None:
        """Record a successful operation."""
        with self._lock:
            self.last_success_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    logger.info(f"Circuit {self.name} transitioning from HALF_OPEN to CLOSED")
                    self.state = CircuitState.CLOSED
                    self.last_state_change_time = datetime.now()
                    self.failure_count = 0
            elif self.state == CircuitState.CLOSED:
                # Reset failure count after a success in closed state
                self.failure_count = 0
    
    def record_failure(self, exception: Optional[Exception] = None) -> None:
        """
        Record a failed operation.
        
        Args:
            exception: The exception that caused the failure
        """
        with self._lock:
            # Check if this exception should be counted
            if exception is not None:
                # Skip if exception is in exclude list
                if any(isinstance(exception, exc_type) for exc_type in self.config.exclude_exceptions):
                    return
                
                # Skip if include list is not empty and exception is not in it
                if (self.config.include_exceptions and 
                    not any(isinstance(exception, exc_type) for exc_type in self.config.include_exceptions)):
                    return
            
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.config.failure_threshold:
                    logger.warning(f"Circuit {self.name} transitioning from CLOSED to OPEN after {self.failure_count} failures")
                    self.state = CircuitState.OPEN
                    self.last_state_change_time = datetime.now()
            elif self.state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit {self.name} transitioning from HALF_OPEN to OPEN after a failure")
                self.state = CircuitState.OPEN
                self.last_state_change_time = datetime.now()
                self.success_count = 0
    
    def get_state(self) -> CircuitState:
        """
        Get the current state of the circuit breaker.
        
        Returns:
            CircuitState: The current state
        """
        with self._lock:
            return self.state
    
    def reset(self) -> None:
        """Reset the circuit breaker to its initial state."""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_state_change_time = datetime.now()
            logger.info(f"Circuit {self.name} has been reset")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the circuit breaker.
        
        Returns:
            Dict: Metrics about the circuit breaker
        """
        with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time > datetime.min else None,
                "last_success_time": self.last_success_time.isoformat() if self.last_success_time > datetime.min else None,
                "last_state_change_time": self.last_state_change_time.isoformat(),
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "success_threshold": self.config.success_threshold,
                    "timeout": self.config.timeout
                }
            }

class ErrorHandler:
    """
    Error handling framework for ApexAgent.
    
    This class provides comprehensive error handling capabilities including:
    - Error categorization and severity assessment
    - Automatic retry with configurable strategies
    - Circuit breakers to prevent cascading failures
    - Fallback mechanisms for graceful degradation
    - Error logging, monitoring, and alerting
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'ErrorHandler':
        """
        Get the singleton instance of the error handler.
        
        Returns:
            ErrorHandler: The singleton instance
        """
        if cls._instance is None:
            cls._instance = ErrorHandler()
        return cls._instance
    
    def __init__(self):
        """Initialize the error handler."""
        self.config = ErrorHandlingConfig()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.fallback_strategies: Dict[str, Callable] = {}
        self.error_queue: queue.Queue = queue.Queue(maxsize=self.config.error_queue_size)
        self.error_processors_threads: List[threading.Thread] = []
        self.running = False
        self._lock = threading.RLock()
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the error handler.
        
        Args:
            config_path: Optional path to configuration file
        """
        if config_path and os.path.exists(config_path):
            self.config.load_from_file(config_path)
        
        # Start error processor threads
        self.running = True
        for i in range(self.config.error_processors):
            thread = threading.Thread(
                target=self._process_error_queue,
                name=f"ErrorProcessor-{i}",
                daemon=True
            )
            thread.start()
            self.error_processors_threads.append(thread)
        
        logger.info("Error handler initialized")
    
    def shutdown(self) -> None:
        """Shutdown the error handler."""
        self.running = False
        
        # Wait for error processors to finish
        for thread in self.error_processors_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)
        
        logger.info("Error handler shut down")
    
    def _process_error_queue(self) -> None:
        """Process errors from the error queue."""
        while self.running:
            try:
                # Get error record from queue with timeout
                try:
                    error_record = self.error_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process the error
                self._handle_error(error_record)
                
                # Mark task as done
                self.error_queue.task_done()
            except Exception as e:
                logger.error(f"Error in error processor: {str(e)}")
    
    def _handle_error(self, error_record: ErrorRecord) -> None:
        """
        Handle an error record.
        
        Args:
            error_record: The error record to handle
        """
        # Log the error
        if self.config.log_all_errors:
            self._log_error(error_record)
        
        # Send telemetry
        if self.config.telemetry_enabled:
            self._send_telemetry(error_record)
        
        # Send alerts for high severity errors
        if error_record.severity in self.config.alert_on_severity:
            self._send_alert(error_record)
        
        # Call registered error handlers
        self._call_error_handlers(error_record)
        
        # Mark as handled
        error_record.handled = True
    
    def _log_error(self, error_record: ErrorRecord) -> None:
        """
        Log an error record.
        
        Args:
            error_record: The error record to log
        """
        error_dict = error_record.to_dict()
        
        # Log with appropriate level based on severity
        if error_record.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR: {error_dict}")
        elif error_record.severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH SEVERITY ERROR: {error_dict}")
        elif error_record.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY ERROR: {error_dict}")
        elif error_record.severity == ErrorSeverity.LOW:
            logger.info(f"LOW SEVERITY ERROR: {error_dict}")
        else:
            logger.debug(f"INFO LEVEL ERROR: {error_dict}")
    
    def _send_telemetry(self, error_record: ErrorRecord) -> None:
        """
        Send telemetry for an error record.
        
        Args:
            error_record: The error record to send telemetry for
        """
        # In a real implementation, this would send telemetry to a monitoring system
        # For this example, we'll just log it
        logger.debug(f"Sending telemetry for error: {error_record.error.__class__.__name__}")
    
    def _send_alert(self, error_record: ErrorRecord) -> None:
        """
        Send an alert for an error record.
        
        Args:
            error_record: The error record to send an alert for
        """
        # In a real implementation, this would send alerts via email, SMS, etc.
        # For this example, we'll just log it
        logger.warning(f"ALERT: {error_record.severity.value} severity error in {error_record.context.component}: {str(error_record.error)}")
    
    def _call_error_handlers(self, error_record: ErrorRecord) -> None:
        """
        Call registered error handlers for an error record.
        
        Args:
            error_record: The error record to handle
        """
        error_type = type(error_record.error)
        
        # Call handlers for this specific error type
        for handler in self.config.error_handlers.get(error_type, []):
            try:
                handler(error_record)
            except Exception as e:
                logger.error(f"Error in error handler: {str(e)}")
        
        # Call handlers for parent error types
        for error_class, handlers in self.config.error_handlers.items():
            if issubclass(error_type, error_class) and error_class != error_type:
                for handler in handlers:
                    try:
                        handler(error_record)
                    except Exception as e:
                        logger.error(f"Error in error handler: {str(e)}")
    
    def register_error_handler(self, error_type: Type[Exception], handler: Callable[[ErrorRecord], None]) -> None:
        """
        Register a handler for a specific error type.
        
        Args:
            error_type: The error type to handle
            handler: The handler function
        """
        with self._lock:
            if error_type not in self.config.error_handlers:
                self.config.error_handlers[error_type] = []
            self.config.error_handlers[error_type].append(handler)
    
    def register_fallback_strategy(self, name: str, strategy: Callable) -> None:
        """
        Register a fallback strategy.
        
        Args:
            name: The name of the strategy
            strategy: The strategy function
        """
        with self._lock:
            self.fallback_strategies[name] = strategy
    
    def get_circuit_breaker(self, operation: str) -> CircuitBreaker:
        """
        Get or create a circuit breaker for an operation.
        
        Args:
            operation: The operation name
            
        Returns:
            CircuitBreaker: The circuit breaker
        """
        with self._lock:
            if operation not in self.circuit_breakers:
                config = self.config.get_circuit_breaker_config(operation)
                self.circuit_breakers[operation] = CircuitBreaker(operation, config)
            return self.circuit_breakers[operation]
    
    def categorize_error(self, error: Exception) -> Tuple[ErrorSeverity, ErrorCategory]:
        """
        Categorize an error by severity and category.
        
        Args:
            error: The error to categorize
            
        Returns:
            Tuple[ErrorSeverity, ErrorCategory]: The severity and category
        """
        # In a real implementation, this would use more sophisticated logic
        # based on error type, message, and context
        
        # Default categorization
        severity = ErrorSeverity.MEDIUM
        category = ErrorCategory.UNKNOWN
        
        # Categorize by error type
        error_type = type(error)
        error_name = error_type.__name__
        error_message = str(error).lower()
        
        # Network errors
        if (
            "connection" in error_name.lower() or
            "timeout" in error_name.lower() or
            "network" in error_name.lower() or
            "socket" in error_name.lower() or
            "connection" in error_message or
            "timeout" in error_message or
            "network" in error_message
        ):
            category = ErrorCategory.NETWORK
            severity = ErrorSeverity.MEDIUM
        
        # Database errors
        elif (
            "database" in error_name.lower() or
            "db" in error_name.lower() or
            "sql" in error_name.lower() or
            "query" in error_name.lower() or
            "database" in error_message or
            "sql" in error_message
        ):
            category = ErrorCategory.DATABASE
            severity = ErrorSeverity.HIGH
        
        # API errors
        elif (
            "api" in error_name.lower() or
            "http" in error_name.lower() or
            "request" in error_name.lower() or
            "response" in error_name.lower() or
            "api" in error_message or
            "http" in error_message
        ):
            category = ErrorCategory.API
            severity = ErrorSeverity.MEDIUM
        
        # Authentication errors
        elif (
            "auth" in error_name.lower() or
            "permission" in error_name.lower() or
            "access" in error_name.lower() or
            "unauthorized" in error_message or
            "permission" in error_message or
            "access denied" in error_message
        ):
            category = ErrorCategory.AUTHENTICATION
            severity = ErrorSeverity.HIGH
        
        # Validation errors
        elif (
            "validation" in error_name.lower() or
            "invalid" in error_name.lower() or
            "validation" in error_message or
            "invalid" in error_message
        ):
            category = ErrorCategory.VALIDATION
            severity = ErrorSeverity.LOW
        
        # Resource errors
        elif (
            "resource" in error_name.lower() or
            "memory" in error_name.lower() or
            "capacity" in error_name.lower() or
            "disk" in error_name.lower() or
            "out of memory" in error_message or
            "disk full" in error_message or
            "resource" in error_message
        ):
            category = ErrorCategory.RESOURCE
            severity = ErrorSeverity.HIGH
        
        # Configuration errors
        elif (
            "config" in error_name.lower() or
            "setting" in error_name.lower() or
            "configuration" in error_message or
            "setting" in error_message
        ):
            category = ErrorCategory.CONFIGURATION
            severity = ErrorSeverity.MEDIUM
        
        # System errors
        elif (
            "system" in error_name.lower() or
            "os" in error_name.lower() or
            "io" in error_name.lower() or
            "file" in error_name.lower() or
            "system" in error_message or
            "os" in error_message
        ):
            category = ErrorCategory.SYSTEM
            severity = ErrorSeverity.HIGH
        
        # Dependency errors
        elif (
            "dependency" in error_name.lower() or
            "import" in error_name.lower() or
            "module" in error_name.lower() or
            "dependency" in error_message or
            "import" in error_message or
            "module" in error_message
        ):
            category = ErrorCategory.DEPENDENCY
            severity = ErrorSeverity.MEDIUM
        
        # Adjust severity based on error message
        if (
            "critical" in error_message or
            "fatal" in error_message or
            "emergency" in error_message
        ):
            severity = ErrorSeverity.CRITICAL
        elif (
            "severe" in error_message or
            "major" in error_message or
            "high" in error_message
        ):
            severity = ErrorSeverity.HIGH
        elif (
            "minor" in error_message or
            "low" in error_message
        ):
            severity = ErrorSeverity.LOW
        
        return severity, category
    
    def record_error(self, error: Exception, context: ErrorContext) -> ErrorRecord:
        """
        Record an error occurrence.
        
        Args:
            error: The error that occurred
            context: The context in which the error occurred
            
        Returns:
            ErrorRecord: The error record
        """
        # Categorize the error
        severity, category = self.categorize_error(error)
        
        # Get traceback
        tb_str = traceback.format_exc()
        
        # Create error record
        error_record = ErrorRecord(
            error=error,
            severity=severity,
            category=category,
            context=context,
            traceback=tb_str
        )
        
        # Add to error queue for processing
        try:
            self.error_queue.put(error_record, block=False)
        except queue.Full:
            logger.warning("Error queue is full, dropping error record")
        
        return error_record
    
    def with_retry(self, operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Decorator for automatic retry of operations.
        
        Args:
            operation: The operation name
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> R:
                # Get retry configuration
                retry_config = self.config.get_retry_config(operation)
                
                # Initialize variables
                attempt = 0
                last_error = None
                
                # Try the operation with retries
                while attempt <= retry_config.max_retries:
                    try:
                        # First attempt or retry
                        if attempt > 0:
                            # Calculate delay
                            delay = retry_config.get_delay(attempt)
                            logger.info(f"Retrying {operation} (attempt {attempt}/{retry_config.max_retries}) after {delay:.2f}s delay")
                            time.sleep(delay)
                        
                        # Execute the function
                        return func(*args, **kwargs)
                    except Exception as e:
                        # Record the error
                        last_error = e
                        
                        # Create error context
                        context = ErrorContext(
                            component=func.__module__,
                            operation=operation
                        )
                        
                        # Record the error
                        self.record_error(e, context)
                        
                        # Increment attempt counter
                        attempt += 1
                        
                        # Log the retry attempt
                        if attempt <= retry_config.max_retries:
                            logger.warning(f"Error in {operation} (attempt {attempt}): {str(e)}")
                        else:
                            logger.error(f"Error in {operation} after {retry_config.max_retries} retries: {str(e)}")
                
                # If we get here, all retries failed
                if last_error:
                    raise last_error
                
                # This should never happen
                raise RuntimeError(f"Unexpected error in retry logic for {operation}")
            
            return wrapper
        
        return decorator
    
    def with_circuit_breaker(self, operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Decorator for circuit breaker pattern.
        
        Args:
            operation: The operation name
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> R:
                # Get or create circuit breaker
                circuit_breaker = self.get_circuit_breaker(operation)
                
                # Check if request is allowed
                if not circuit_breaker.allow_request():
                    raise RuntimeError(f"Circuit breaker open for {operation}")
                
                try:
                    # Execute the function with timeout
                    result = func(*args, **kwargs)
                    
                    # Record success
                    circuit_breaker.record_success()
                    
                    return result
                except Exception as e:
                    # Record failure
                    circuit_breaker.record_failure(e)
                    
                    # Re-raise the exception
                    raise
            
            return wrapper
        
        return decorator
    
    def with_fallback(self, operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Decorator for fallback pattern.
        
        Args:
            operation: The operation name
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> R:
                # Get fallback configuration
                fallback_config = self.config.get_fallback_config(operation)
                
                # If fallbacks are disabled, just execute the function
                if not fallback_config.enabled:
                    return func(*args, **kwargs)
                
                try:
                    # Try the primary function
                    return func(*args, **kwargs)
                except Exception as primary_error:
                    # Create error context
                    context = ErrorContext(
                        component=func.__module__,
                        operation=operation
                    )
                    
                    # Record the primary error
                    self.record_error(primary_error, context)
                    
                    # Try fallback strategies
                    last_error = primary_error
                    fallback_count = 0
                    
                    for strategy_name in fallback_config.strategies:
                        # Check if we've reached the maximum number of fallbacks
                        if fallback_count >= fallback_config.max_fallbacks:
                            break
                        
                        # Get the fallback strategy
                        if strategy_name not in self.fallback_strategies:
                            logger.warning(f"Fallback strategy {strategy_name} not found for {operation}")
                            continue
                        
                        strategy = self.fallback_strategies[strategy_name]
                        
                        try:
                            # Try the fallback strategy
                            logger.info(f"Trying fallback strategy {strategy_name} for {operation}")
                            return strategy(*args, **kwargs)
                        except Exception as fallback_error:
                            # Record the fallback error
                            fallback_context = ErrorContext(
                                component=func.__module__,
                                operation=f"{operation}.fallback.{strategy_name}"
                            )
                            self.record_error(fallback_error, fallback_context)
                            
                            # Update last error
                            last_error = fallback_error
                            
                            # Increment fallback counter
                            fallback_count += 1
                    
                    # If we get here, all fallbacks failed
                    logger.error(f"All fallbacks failed for {operation}")
                    raise last_error
            
            return wrapper
        
        return decorator
    
    def with_resilience(self, operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Combined decorator for retry, circuit breaker, and fallback patterns.
        
        Args:
            operation: The operation name
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            # Apply decorators in reverse order (innermost first)
            # Fallback -> Circuit Breaker -> Retry
            func_with_fallback = self.with_fallback(operation)(func)
            func_with_circuit_breaker = self.with_circuit_breaker(operation)(func_with_fallback)
            func_with_retry = self.with_retry(operation)(func_with_circuit_breaker)
            
            return func_with_retry
        
        return decorator
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the error handler.
        
        Returns:
            Dict: Metrics about the error handler
        """
        with self._lock:
            metrics = {
                "error_queue_size": self.error_queue.qsize(),
                "error_queue_capacity": self.error_queue.maxsize,
                "error_processors": len(self.error_processors_threads),
                "circuit_breakers": {
                    name: cb.get_metrics() for name, cb in self.circuit_breakers.items()
                },
                "fallback_strategies": list(self.fallback_strategies.keys())
            }
            
            return metrics


# Global instance for easy access
error_handler = ErrorHandler.get_instance()


def initialize_error_handling(config_path: Optional[str] = None) -> None:
    """
    Initialize the error handling framework.
    
    Args:
        config_path: Optional path to configuration file
    """
    error_handler.initialize(config_path)


def shutdown_error_handling() -> None:
    """Shutdown the error handling framework."""
    error_handler.shutdown()


def with_retry(operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for automatic retry of operations.
    
    Args:
        operation: The operation name
        
    Returns:
        Callable: Decorator function
    """
    return error_handler.with_retry(operation)


def with_circuit_breaker(operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for circuit breaker pattern.
    
    Args:
        operation: The operation name
        
    Returns:
        Callable: Decorator function
    """
    return error_handler.with_circuit_breaker(operation)


def with_fallback(operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for fallback pattern.
    
    Args:
        operation: The operation name
        
    Returns:
        Callable: Decorator function
    """
    return error_handler.with_fallback(operation)


def with_resilience(operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Combined decorator for retry, circuit breaker, and fallback patterns.
    
    Args:
        operation: The operation name
        
    Returns:
        Callable: Decorator function
    """
    return error_handler.with_resilience(operation)


def register_error_handler(error_type: Type[Exception], handler: Callable[[ErrorRecord], None]) -> None:
    """
    Register a handler for a specific error type.
    
    Args:
        error_type: The error type to handle
        handler: The handler function
    """
    error_handler.register_error_handler(error_type, handler)


def register_fallback_strategy(name: str, strategy: Callable) -> None:
    """
    Register a fallback strategy.
    
    Args:
        name: The name of the strategy
        strategy: The strategy function
    """
    error_handler.register_fallback_strategy(name, strategy)


def record_error(error: Exception, component: str, operation: str, **context_kwargs: Any) -> ErrorRecord:
    """
    Record an error occurrence.
    
    Args:
        error: The error that occurred
        component: The component where the error occurred
        operation: The operation where the error occurred
        **context_kwargs: Additional context information
        
    Returns:
        ErrorRecord: The error record
    """
    context = ErrorContext(
        component=component,
        operation=operation,
        **context_kwargs
    )
    
    return error_handler.record_error(error, context)


def get_metrics() -> Dict[str, Any]:
    """
    Get metrics about the error handler.
    
    Returns:
        Dict: Metrics about the error handler
    """
    return error_handler.get_metrics()


# Example usage
if __name__ == "__main__":
    # Initialize error handling
    initialize_error_handling()
    
    # Register a fallback strategy
    def cached_data_fallback(*args, **kwargs):
        return {"status": "cached", "data": "Cached data"}
    
    register_fallback_strategy("cached_data", cached_data_fallback)
    
    # Define a function with resilience
    @with_resilience("fetch_data")
    def fetch_data(url):
        # Simulate a network request
        if random.random() < 0.7:
            raise ConnectionError("Failed to connect to server")
        return {"status": "success", "data": "Real data"}
    
    # Try the function
    try:
        for i in range(5):
            try:
                result = fetch_data("https://example.com/api/data")
                print(f"Attempt {i+1}: Success - {result}")
            except Exception as e:
                print(f"Attempt {i+1}: Error - {str(e)}")
            time.sleep(1)
    finally:
        # Shutdown error handling
        shutdown_error_handling()
