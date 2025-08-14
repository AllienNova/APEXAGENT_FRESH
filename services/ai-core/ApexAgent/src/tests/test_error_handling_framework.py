#!/usr/bin/env python3
"""
Test suite for the Error Handling Framework.

This module provides comprehensive tests for the error handling framework
components of the ApexAgent system.
"""

import os
import sys
import unittest
import tempfile
import logging
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import threading
import time

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from error_handling.error_handling_framework import (
    ErrorHandlingSystem, ErrorConfig, ErrorSeverity, ErrorCategory,
    ErrorHandler, ErrorEvent, RetryStrategy, CircuitBreaker, FallbackStrategy
)

class TestErrorHandlingSystem(unittest.TestCase):
    """Test cases for the ErrorHandlingSystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ErrorConfig(
            enabled=True,
            log_directory=self.temp_dir,
            max_retries=3,
            retry_delay=0.1,
            circuit_breaker_enabled=True,
            circuit_breaker_threshold=5,
            circuit_breaker_reset_timeout=1.0
        )
        self.error_system = ErrorHandlingSystem.get_instance()
        self.error_system.initialize(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.error_system.shutdown()
    
    def test_singleton_pattern(self):
        """Test that the error handling system follows the singleton pattern."""
        instance1 = ErrorHandlingSystem.get_instance()
        instance2 = ErrorHandlingSystem.get_instance()
        self.assertIs(instance1, instance2)
    
    def test_error_registration(self):
        """Test registering error handlers."""
        handler = MagicMock()
        self.error_system.register_error_handler(ErrorCategory.NETWORK, handler)
        
        # Verify handler was registered
        self.assertIn(ErrorCategory.NETWORK, self.error_system._handlers)
        self.assertIn(handler, self.error_system._handlers[ErrorCategory.NETWORK])
        
        # Test unregistering
        self.error_system.unregister_error_handler(ErrorCategory.NETWORK, handler)
        self.assertNotIn(handler, self.error_system._handlers[ErrorCategory.NETWORK])
    
    def test_error_handling(self):
        """Test handling errors."""
        handler = MagicMock()
        self.error_system.register_error_handler(ErrorCategory.NETWORK, handler)
        
        error = Exception("Test network error")
        event = ErrorEvent(
            error=error,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            source="test_module",
            message="Test error message",
            context={"request_id": "123"}
        )
        
        self.error_system.handle_error(event)
        
        # Verify handler was called
        handler.assert_called_once_with(event)
    
    def test_error_logging(self):
        """Test error logging."""
        with patch('error_handling.error_handling_framework.logging.error') as mock_log:
            error = Exception("Test error")
            event = ErrorEvent(
                error=error,
                category=ErrorCategory.DATABASE,
                severity=ErrorSeverity.CRITICAL,
                source="test_module",
                message="Test error message",
                context={"request_id": "123"}
            )
            
            self.error_system.handle_error(event)
            
            # Verify error was logged
            mock_log.assert_called()
    
    @patch('error_handling.error_handling_framework.time.sleep')
    def test_retry_mechanism(self, mock_sleep):
        """Test retry mechanism."""
        # Create a function that fails twice then succeeds
        counter = [0]
        
        def test_function():
            counter[0] += 1
            if counter[0] <= 2:
                raise Exception("Temporary failure")
            return "Success"
        
        # Configure retry strategy
        retry_strategy = RetryStrategy(
            max_retries=3,
            delay=0.1,
            backoff_factor=2.0,
            exceptions=(Exception,)
        )
        
        # Execute with retry
        result = self.error_system.execute_with_retry(test_function, retry_strategy)
        
        # Verify function was called multiple times and eventually succeeded
        self.assertEqual(counter[0], 3)
        self.assertEqual(result, "Success")
        mock_sleep.assert_called()
    
    def test_circuit_breaker(self):
        """Test circuit breaker pattern."""
        # Create a circuit breaker
        breaker = CircuitBreaker(
            failure_threshold=2,
            reset_timeout=0.1
        )
        
        # Function that always fails
        def failing_function():
            raise Exception("Always fails")
        
        # First call - should try and fail
        with self.assertRaises(Exception):
            self.error_system.execute_with_circuit_breaker(failing_function, breaker)
        
        # Second call - should try and fail, then open circuit
        with self.assertRaises(Exception):
            self.error_system.execute_with_circuit_breaker(failing_function, breaker)
        
        # Third call - circuit should be open, so CircuitBreakerOpen exception
        with self.assertRaises(CircuitBreaker.CircuitBreakerOpen):
            self.error_system.execute_with_circuit_breaker(failing_function, breaker)
        
        # Wait for reset timeout
        time.sleep(0.2)
        
        # Circuit should be half-open now, so it should try again
        with self.assertRaises(Exception):
            self.error_system.execute_with_circuit_breaker(failing_function, breaker)
    
    def test_fallback_strategy(self):
        """Test fallback strategy."""
        # Create a fallback strategy
        fallback_value = "Fallback result"
        fallback = FallbackStrategy(lambda _: fallback_value)
        
        # Function that fails
        def failing_function():
            raise Exception("Always fails")
        
        # Execute with fallback
        result = self.error_system.execute_with_fallback(failing_function, fallback)
        
        # Verify fallback was used
        self.assertEqual(result, fallback_value)
    
    def test_graceful_degradation(self):
        """Test graceful degradation."""
        # Create component dependencies
        components = {
            "database": MagicMock(side_effect=Exception("Database unavailable")),
            "cache": MagicMock(return_value="Cached data"),
            "api": MagicMock(return_value="API data")
        }
        
        # Define degradation levels
        degradation_levels = [
            ["database", "cache", "api"],  # Try database first, then cache, then API
            ["cache", "api"],              # Skip database, try cache then API
            ["api"]                        # Last resort, just use API
        ]
        
        # Execute with graceful degradation
        result = self.error_system.execute_with_degradation(
            components, degradation_levels
        )
        
        # Verify components were called in order until success
        components["database"].assert_called_once()
        components["cache"].assert_called_once()
        self.assertEqual(result, "Cached data")
        components["api"].assert_not_called()

class TestErrorHandler(unittest.TestCase):
    """Test cases for the ErrorHandler class."""
    
    def test_error_handler_interface(self):
        """Test the ErrorHandler interface."""
        # Create a concrete implementation of ErrorHandler
        class ConcreteErrorHandler(ErrorHandler):
            def handle_error(self, event):
                return f"Handled: {event.message}"
        
        # Create an instance and test
        handler = ConcreteErrorHandler()
        event = ErrorEvent(
            error=Exception("Test"),
            category=ErrorCategory.GENERAL,
            severity=ErrorSeverity.MEDIUM,
            source="test",
            message="Test message"
        )
        
        result = handler.handle_error(event)
        self.assertEqual(result, "Handled: Test message")

class TestRetryStrategy(unittest.TestCase):
    """Test cases for the RetryStrategy class."""
    
    def test_retry_strategy_configuration(self):
        """Test configuring a retry strategy."""
        strategy = RetryStrategy(
            max_retries=5,
            delay=0.2,
            backoff_factor=1.5,
            exceptions=(ValueError, KeyError)
        )
        
        self.assertEqual(strategy.max_retries, 5)
        self.assertEqual(strategy.delay, 0.2)
        self.assertEqual(strategy.backoff_factor, 1.5)
        self.assertEqual(strategy.exceptions, (ValueError, KeyError))
    
    def test_calculate_delay(self):
        """Test calculating delay with backoff."""
        strategy = RetryStrategy(
            max_retries=3,
            delay=1.0,
            backoff_factor=2.0
        )
        
        # First retry: delay = 1.0
        self.assertEqual(strategy.calculate_delay(1), 1.0)
        
        # Second retry: delay = 1.0 * 2.0 = 2.0
        self.assertEqual(strategy.calculate_delay(2), 2.0)
        
        # Third retry: delay = 1.0 * 2.0^2 = 4.0
        self.assertEqual(strategy.calculate_delay(3), 4.0)

class TestCircuitBreaker(unittest.TestCase):
    """Test cases for the CircuitBreaker class."""
    
    def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions."""
        breaker = CircuitBreaker(
            failure_threshold=2,
            reset_timeout=0.1
        )
        
        # Initial state should be CLOSED
        self.assertEqual(breaker.state, CircuitBreaker.State.CLOSED)
        
        # Record failures
        breaker.record_failure()
        self.assertEqual(breaker.state, CircuitBreaker.State.CLOSED)
        
        breaker.record_failure()
        self.assertEqual(breaker.state, CircuitBreaker.State.OPEN)
        
        # Wait for reset timeout
        time.sleep(0.2)
        
        # State should be HALF_OPEN after timeout
        self.assertEqual(breaker.state, CircuitBreaker.State.HALF_OPEN)
        
        # Record success to close the circuit
        breaker.record_success()
        self.assertEqual(breaker.state, CircuitBreaker.State.CLOSED)

class TestFallbackStrategy(unittest.TestCase):
    """Test cases for the FallbackStrategy class."""
    
    def test_fallback_function(self):
        """Test fallback function execution."""
        # Create a fallback that returns the exception message
        fallback = FallbackStrategy(lambda e: f"Fallback: {str(e)}")
        
        # Test with an exception
        error = ValueError("Test error")
        result = fallback.execute(error)
        
        self.assertEqual(result, "Fallback: Test error")
    
    def test_fallback_chain(self):
        """Test chaining multiple fallbacks."""
        # Create a chain of fallbacks
        fallback1 = FallbackStrategy(lambda e: None if isinstance(e, ValueError) else "Fallback 1")
        fallback2 = FallbackStrategy(lambda e: "Fallback 2")
        
        # Chain them
        fallback1.set_next(fallback2)
        
        # Test with ValueError (fallback1 returns None, so fallback2 is used)
        result = fallback1.execute(ValueError("Test"))
        self.assertEqual(result, "Fallback 2")
        
        # Test with TypeError (fallback1 handles it)
        result = fallback1.execute(TypeError("Test"))
        self.assertEqual(result, "Fallback 1")

if __name__ == '__main__':
    unittest.main()
