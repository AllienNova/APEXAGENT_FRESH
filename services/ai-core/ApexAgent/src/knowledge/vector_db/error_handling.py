"""
Error Handling and Logging for Aideon AI Lite Vector Database

This module provides comprehensive error handling and logging utilities
for the vector database integration in the Aideon AI Lite platform.

Production-ready features:
- Structured logging with context
- Error tracking and monitoring
- Graceful degradation strategies
- Detailed error reporting
- Performance metrics collection
"""

import os
import json
import logging
import time
import traceback
import threading
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union, Type
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

# Performance metrics
_metrics = {
    "operation_counts": {},
    "error_counts": {},
    "latencies": {},
    "start_time": time.time()
}

# Lock for thread safety
_metrics_lock = threading.RLock()


class ErrorTracker:
    """
    Utility for tracking and reporting errors.
    
    This class provides methods for tracking errors, generating reports,
    and implementing graceful degradation strategies.
    """
    
    def __init__(self, max_errors: int = 1000):
        """
        Initialize the error tracker.
        
        Args:
            max_errors: Maximum number of errors to track.
        """
        self.errors: List[Dict[str, Any]] = []
        self.max_errors = max_errors
        self.lock = threading.RLock()
    
    def track_error(self, error: Exception, context: Dict[str, Any] = None):
        """
        Track an error with context.
        
        Args:
            error: The error to track.
            context: Optional context information.
        """
        with self.lock:
            # Create error entry
            error_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {}
            }
            
            # Add to errors list
            self.errors.append(error_entry)
            
            # Trim errors list if needed
            if len(self.errors) > self.max_errors:
                self.errors = self.errors[-self.max_errors:]
            
            # Update error counts
            error_type = type(error).__name__
            with _metrics_lock:
                if error_type not in _metrics["error_counts"]:
                    _metrics["error_counts"][error_type] = 0
                _metrics["error_counts"][error_type] += 1
    
    def get_error_report(self) -> Dict[str, Any]:
        """
        Generate an error report.
        
        Returns:
            A dictionary containing error statistics and recent errors.
        """
        with self.lock:
            # Count errors by type
            error_counts = {}
            for error in self.errors:
                error_type = error["error_type"]
                if error_type not in error_counts:
                    error_counts[error_type] = 0
                error_counts[error_type] += 1
            
            # Generate report
            return {
                "total_errors": len(self.errors),
                "error_counts": error_counts,
                "recent_errors": self.errors[-10:] if self.errors else []
            }
    
    def clear_errors(self):
        """Clear all tracked errors."""
        with self.lock:
            self.errors = []


# Global error tracker instance
_error_tracker = ErrorTracker()


def get_error_tracker() -> ErrorTracker:
    """
    Get the global error tracker instance.
    
    Returns:
        The global error tracker instance.
    """
    return _error_tracker


def track_operation(operation_name: str):
    """
    Decorator for tracking operation metrics.
    
    This decorator tracks operation counts and latencies for monitoring
    and performance analysis.
    
    Args:
        operation_name: The name of the operation to track.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Call the original function
                result = func(*args, **kwargs)
                
                # Track successful operation
                with _metrics_lock:
                    if operation_name not in _metrics["operation_counts"]:
                        _metrics["operation_counts"][operation_name] = 0
                    _metrics["operation_counts"][operation_name] += 1
                    
                    # Track latency
                    latency = time.time() - start_time
                    if operation_name not in _metrics["latencies"]:
                        _metrics["latencies"][operation_name] = []
                    _metrics["latencies"][operation_name].append(latency)
                    
                    # Keep only the last 100 latencies
                    if len(_metrics["latencies"][operation_name]) > 100:
                        _metrics["latencies"][operation_name] = _metrics["latencies"][operation_name][-100:]
                
                return result
            except Exception as e:
                # Track error
                _error_tracker.track_error(e, {
                    "operation": operation_name,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                
                # Re-raise the exception
                raise
        
        return wrapper
    
    return decorator


def with_retry(max_retries: int = 3, retry_delay: float = 1.0, 
              exponential_backoff: bool = True, 
              retryable_exceptions: Optional[List[Type[Exception]]] = None):
    """
    Decorator for retrying operations on failure.
    
    This decorator automatically retries operations that fail with
    specified exceptions, with configurable retry behavior.
    
    Args:
        max_retries: Maximum number of retry attempts.
        retry_delay: Delay in seconds between retries.
        exponential_backoff: Whether to use exponential backoff for retries.
        retryable_exceptions: List of exception types to retry on.
                             If None, retries on all exceptions.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = retry_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Check if we should retry
                    if retryable_exceptions and not any(isinstance(e, ex) for ex in retryable_exceptions):
                        raise
                    
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                        raise
                    
                    # Log retry attempt
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after error: {str(e)}")
                    
                    # Wait before retrying
                    time.sleep(delay)
                    
                    # Increase delay if using exponential backoff
                    if exponential_backoff:
                        delay *= 2
        
        return wrapper
    
    return decorator


def with_fallback(fallback_function: Callable):
    """
    Decorator for providing fallback behavior on failure.
    
    This decorator calls a fallback function when the original function fails,
    implementing graceful degradation.
    
    Args:
        fallback_function: The function to call on failure.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error
                logger.error(f"Function {func.__name__} failed, using fallback: {str(e)}")
                
                # Track the error
                _error_tracker.track_error(e, {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "using_fallback": True
                })
                
                # Call fallback function
                return fallback_function(*args, **kwargs)
        
        return wrapper
    
    return decorator


def with_timeout(timeout_seconds: float):
    """
    Decorator for applying a timeout to a function.
    
    This decorator raises a TimeoutError if the function takes longer
    than the specified timeout to complete.
    
    Args:
        timeout_seconds: The timeout in seconds.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
            
            # Set timeout
            original_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout_seconds))
            
            try:
                return func(*args, **kwargs)
            finally:
                # Reset timeout
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)
        
        return wrapper
    
    return decorator


def log_context(level: int = logging.INFO, include_args: bool = True):
    """
    Decorator for logging function calls with context.
    
    This decorator logs function calls with context information,
    including arguments and return values.
    
    Args:
        level: The logging level to use.
        include_args: Whether to include function arguments in the log.
        
    Returns:
        A decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique ID for this call
            call_id = str(uuid.uuid4())
            
            # Prepare context information
            context = {
                "function": func.__name__,
                "call_id": call_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add arguments if requested
            if include_args:
                # Convert args to string representations
                arg_strs = [str(arg) for arg in args]
                kwarg_strs = {k: str(v) for k, v in kwargs.items()}
                
                context["args"] = arg_strs
                context["kwargs"] = kwarg_strs
            
            # Log function call
            logger.log(level, f"Calling {func.__name__}", extra={"context": context})
            
            start_time = time.time()
            
            try:
                # Call the original function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Log successful completion
                logger.log(level, f"Completed {func.__name__} in {duration:.3f}s", 
                          extra={"context": {**context, "duration": duration}})
                
                return result
            except Exception as e:
                # Calculate duration
                duration = time.time() - start_time
                
                # Log error
                logger.error(f"Error in {func.__name__}: {str(e)}", 
                            extra={"context": {**context, "duration": duration, "error": str(e)}})
                
                # Re-raise the exception
                raise
        
        return wrapper
    
    return decorator


def get_performance_metrics() -> Dict[str, Any]:
    """
    Get performance metrics for monitoring.
    
    Returns:
        A dictionary containing performance metrics.
    """
    with _metrics_lock:
        # Calculate uptime
        uptime = time.time() - _metrics["start_time"]
        
        # Calculate average latencies
        avg_latencies = {}
        for operation, latencies in _metrics["latencies"].items():
            if latencies:
                avg_latencies[operation] = sum(latencies) / len(latencies)
        
        # Generate metrics report
        return {
            "uptime": uptime,
            "operation_counts": _metrics["operation_counts"].copy(),
            "error_counts": _metrics["error_counts"].copy(),
            "average_latencies": avg_latencies
        }


def reset_performance_metrics():
    """Reset all performance metrics."""
    with _metrics_lock:
        _metrics["operation_counts"] = {}
        _metrics["error_counts"] = {}
        _metrics["latencies"] = {}
        _metrics["start_time"] = time.time()


class StructuredLogger:
    """
    Logger for structured logging with context.
    
    This class provides methods for logging structured messages with
    context information for better traceability and analysis.
    """
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        """
        Initialize the structured logger.
        
        Args:
            name: The name of the logger.
            log_file: Optional file to log to.
        """
        self.logger = logging.getLogger(name)
        self.context = {}
        
        # Configure file handler if log_file is provided
        if log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def set_context(self, **kwargs):
        """
        Set context for subsequent log messages.
        
        Args:
            **kwargs: Context key-value pairs.
        """
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context."""
        self.context = {}
    
    def _log(self, level: int, message: str, context: Dict[str, Any] = None):
        """
        Log a message with context.
        
        Args:
            level: The logging level.
            message: The message to log.
            context: Additional context for this message.
        """
        # Merge context
        merged_context = self.context.copy()
        if context:
            merged_context.update(context)
        
        # Add timestamp
        merged_context["timestamp"] = datetime.utcnow().isoformat()
        
        # Log the message with context
        self.logger.log(level, message, extra={"context": merged_context})
    
    def debug(self, message: str, **context):
        """
        Log a debug message.
        
        Args:
            message: The message to log.
            **context: Additional context for this message.
        """
        self._log(logging.DEBUG, message, context)
    
    def info(self, message: str, **context):
        """
        Log an info message.
        
        Args:
            message: The message to log.
            **context: Additional context for this message.
        """
        self._log(logging.INFO, message, context)
    
    def warning(self, message: str, **context):
        """
        Log a warning message.
        
        Args:
            message: The message to log.
            **context: Additional context for this message.
        """
        self._log(logging.WARNING, message, context)
    
    def error(self, message: str, **context):
        """
        Log an error message.
        
        Args:
            message: The message to log.
            **context: Additional context for this message.
        """
        self._log(logging.ERROR, message, context)
    
    def critical(self, message: str, **context):
        """
        Log a critical message.
        
        Args:
            message: The message to log.
            **context: Additional context for this message.
        """
        self._log(logging.CRITICAL, message, context)


def get_structured_logger(name: str, log_file: Optional[str] = None) -> StructuredLogger:
    """
    Get a structured logger.
    
    Args:
        name: The name of the logger.
        log_file: Optional file to log to.
        
    Returns:
        A structured logger instance.
    """
    return StructuredLogger(name, log_file)


class GracefulDegradation:
    """
    Utility for implementing graceful degradation strategies.
    
    This class provides methods for detecting system health issues
    and implementing appropriate degradation strategies.
    """
    
    def __init__(self):
        """Initialize the graceful degradation utility."""
        self.strategies = {
            "read_only_mode": False,
            "reduced_results": False,
            "simplified_search": False,
            "cache_only_mode": False
        }
        self.health_checks = {
            "database_connection": True,
            "embedding_generation": True,
            "search_performance": True,
            "memory_usage": True
        }
        self.lock = threading.RLock()
    
    def update_health_status(self, check_name: str, status: bool):
        """
        Update the status of a health check.
        
        Args:
            check_name: The name of the health check.
            status: The status (True for healthy, False for unhealthy).
        """
        with self.lock:
            if check_name in self.health_checks:
                self.health_checks[check_name] = status
                self._update_strategies()
    
    def _update_strategies(self):
        """Update degradation strategies based on health status."""
        with self.lock:
            # Reset strategies
            self.strategies = {
                "read_only_mode": False,
                "reduced_results": False,
                "simplified_search": False,
                "cache_only_mode": False
            }
            
            # Apply strategies based on health status
            if not self.health_checks["database_connection"]:
                self.strategies["read_only_mode"] = True
                self.strategies["cache_only_mode"] = True
            
            if not self.health_checks["embedding_generation"]:
                self.strategies["cache_only_mode"] = True
            
            if not self.health_checks["search_performance"]:
                self.strategies["reduced_results"] = True
                self.strategies["simplified_search"] = True
            
            if not self.health_checks["memory_usage"]:
                self.strategies["reduced_results"] = True
    
    def is_strategy_active(self, strategy_name: str) -> bool:
        """
        Check if a degradation strategy is active.
        
        Args:
            strategy_name: The name of the strategy to check.
            
        Returns:
            True if the strategy is active, False otherwise.
        """
        with self.lock:
            return self.strategies.get(strategy_name, False)
    
    def get_active_strategies(self) -> List[str]:
        """
        Get a list of active degradation strategies.
        
        Returns:
            A list of active strategy names.
        """
        with self.lock:
            return [name for name, active in self.strategies.items() if active]
    
    def get_health_status(self) -> Dict[str, bool]:
        """
        Get the current health status.
        
        Returns:
            A dictionary mapping health check names to their status.
        """
        with self.lock:
            return self.health_checks.copy()


# Global graceful degradation instance
_graceful_degradation = GracefulDegradation()


def get_graceful_degradation() -> GracefulDegradation:
    """
    Get the global graceful degradation instance.
    
    Returns:
        The global graceful degradation instance.
    """
    return _graceful_degradation
