"""
__init__.py for the error handling package.

This module initializes the error handling framework and exports
the main components for easy access.
"""

from .errors import (
    ApexAgentError, ErrorSeverity, SystemError, InitializationError,
    ConfigurationError, ResourceError, PluginError, PluginLoadError,
    PluginExecutionError, PluginDependencyError, APIError, AuthenticationError,
    RateLimitError, ServiceUnavailableError, UserError, ValidationError,
    PermissionError, DataError, DataFormatError, DataStorageError, DataProcessingError
)
from .error_messages import (
    ErrorMessageTemplate, ErrorMessageManager, ErrorRecoveryManager,
    format_error_for_user
)
from .error_telemetry import (
    ErrorTelemetry, AsyncErrorTelemetry, telemetry, async_telemetry,
    log_error, get_error_report
)
from .error_events import (
    ErrorEventEmitter, ErrorEventSubscriber, ErrorEventHandler,
    format_error_for_user
)

# Create global instances for easy access
message_manager = ErrorMessageManager()
recovery_manager = ErrorRecoveryManager()

__all__ = [
    # Error classes
    'ApexAgentError', 'ErrorSeverity', 'SystemError', 'InitializationError',
    'ConfigurationError', 'ResourceError', 'PluginError', 'PluginLoadError',
    'PluginExecutionError', 'PluginDependencyError', 'APIError', 'AuthenticationError',
    'RateLimitError', 'ServiceUnavailableError', 'UserError', 'ValidationError',
    'PermissionError', 'DataError', 'DataFormatError', 'DataStorageError', 'DataProcessingError',
    
    # Error messages
    'ErrorMessageTemplate', 'ErrorMessageManager', 'ErrorRecoveryManager',
    'format_error_for_user', 'message_manager', 'recovery_manager',
    
    # Error telemetry
    'ErrorTelemetry', 'AsyncErrorTelemetry', 'telemetry', 'async_telemetry',
    'log_error', 'get_error_report',
    
    # Error events
    'ErrorEventEmitter', 'ErrorEventSubscriber', 'ErrorEventHandler'
]
