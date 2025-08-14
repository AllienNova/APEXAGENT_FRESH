"""
Unit tests for the ApexAgent error handling framework.

This module contains tests for the error handling framework, including
error classification, error messages, error telemetry, and error events.
"""

import asyncio
import json
import logging
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.core.error_handling.errors import (
    ApexAgentError, ErrorSeverity, SystemError, InitializationError,
    ConfigurationError, ResourceError, PluginError, PluginLoadError,
    PluginExecutionError, PluginDependencyError, APIError, AuthenticationError,
    RateLimitError, ServiceUnavailableError, UserError, ValidationError,
    DataError, DataFormatError, DataStorageError, DataProcessingError
)
from src.core.error_handling.error_messages import (
    ErrorMessageTemplate, ErrorMessageManager, ErrorRecoveryManager,
    format_error_for_user
)
from src.core.error_handling.error_telemetry import (
    ErrorTelemetry, AsyncErrorTelemetry, telemetry, async_telemetry
)
from src.core.error_handling.error_events import (
    ErrorEventEmitter, ErrorEventSubscriber, ErrorEventHandler,
    format_error_for_user
)
from src.core.error_handling.error_recovery import ErrorRecoveryManager

from src.core.event_system.event import Event, EventPriority
from src.core.event_system.event_manager import EventManager
from src.core.event_system.event_subscriber import EventSubscriber


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


class TestErrorClassification(unittest.TestCase):
    """Test error classification and hierarchy."""
    
    def test_error_creation(self):
        """Test creating errors."""
        # Create a basic error
        error = ApexAgentError(
            message="Test error",
            component="test_component"
        )
        
        # Check properties
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.component, "test_component")
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertIsNotNone(error.error_code)
        self.assertIsNotNone(error.timestamp)
        self.assertIsNone(error.context)
        
        # Check string representation
        self.assertIn("Test error", str(error))
        self.assertIn("test_component", str(error))
    
    def test_error_with_context(self):
        """Test creating errors with context."""
        # Create an error with context
        error = ApexAgentError(
            message="Test error",
            component="test_component",
            context={"key": "value"}
        )
        
        # Check context
        self.assertEqual(error.context["key"], "value")
    
    def test_error_with_custom_severity(self):
        """Test creating errors with custom severity."""
        # Create an error with custom severity
        error = ApexAgentError(
            message="Test error",
            component="test_component",
            severity=ErrorSeverity.CRITICAL
        )
        
        # Check severity
        self.assertEqual(error.severity, ErrorSeverity.CRITICAL)
    
    def test_error_with_custom_code(self):
        """Test creating errors with custom error code."""
        # Create an error with custom error code
        error = ApexAgentError(
            message="Test error",
            component="test_component",
            error_code="TEST-001"
        )
        
        # Check error code
        self.assertEqual(error.error_code, "TEST-001")
    
    def test_error_to_dict(self):
        """Test converting errors to dictionaries."""
        # Create an error
        error = ApexAgentError(
            message="Test error",
            component="test_component",
            context={"key": "value"},
            severity=ErrorSeverity.WARNING,
            error_code="TEST-001"
        )
        
        # Convert to dictionary
        error_dict = error.to_dict()
        
        # Check dictionary
        self.assertEqual(error_dict["message"], "Test error")
        self.assertEqual(error_dict["component"], "test_component")
        self.assertEqual(error_dict["context"]["key"], "value")
        self.assertEqual(error_dict["severity"], ErrorSeverity.WARNING.name)
        self.assertEqual(error_dict["error_code"], "TEST-001")
        self.assertEqual(error_dict["error_type"], "ApexAgentError")
    
    def test_error_hierarchy(self):
        """Test error hierarchy."""
        # Create errors of different types
        system_error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        initialization_error = InitializationError(
            message="Initialization error",
            component="test_component"
        )
        configuration_error = ConfigurationError(
            message="Configuration error",
            component="test_component",
            config_key="test_key"
        )
        resource_error = ResourceError(
            message="Resource error",
            component="test_component",
            resource_type="test_resource"
        )
        plugin_error = PluginError(
            message="Plugin error",
            plugin_name="test_plugin"
        )
        plugin_load_error = PluginLoadError(
            message="Plugin load error",
            plugin_name="test_plugin",
            plugin_path="test_path"
        )
        plugin_execution_error = PluginExecutionError(
            message="Plugin execution error",
            plugin_name="test_plugin",
            operation="test_action"
        )
        plugin_dependency_error = PluginDependencyError(
            message="Plugin dependency error",
            plugin_name="test_plugin",
            dependency_id="test_dependency"
        )
        api_error = APIError(
            message="API error",
            component="test_component",
            api_name="test_api",
            operation="test_operation"
        )
        authentication_error = AuthenticationError(
            message="Authentication error",
            component="test_component",
            auth_method="test_service",  # Changed from service to auth_method to match constructor
            operation="authentication"
        )
        rate_limit_error = RateLimitError(
            message="Rate limit error",
            component="test_component",
            api_name="test_service",  # Changed from service to api_name to match constructor
            limit=100,
            reset_time=datetime.now() + timedelta(seconds=60),
            operation="api_request"
        )
        service_unavailable_error = ServiceUnavailableError(
            message="Service unavailable error",
            component="test_component",
            api_name="test_service",  # Changed from service to api_name to match constructor
            operation="service_request"
        )
        user_error = UserError(
            message="User error",
            component="test_component",
            user_id="test_user",
            operation="user_action"
        )
        validation_error = ValidationError(
            message="Validation error",
            component="test_component",
            field="test_field",
            reason="test_reason",
            operation="data_validation"
        )
        data_error = DataError(
            message="Data error",
            component="test_component",
            data_type="test_data",  # Added required data_type parameter
            data_source="test_source",
            operation="data_operation"
        )
        data_format_error = DataFormatError(
            message="Data format error",
            component="test_component",
            data_type="test_data",  # Added required data_type parameter
            data_source="test_source",
            expected_format="test_format",
            operation="data_parsing"
        )
        data_storage_error = DataStorageError(
            message="Data storage error",
            component="test_component",
            data_type="test_data",  # Added required data_type parameter
            storage_type="test_storage",  # Added required storage_type parameter
            data_source="test_source",
            operation="data_storage"
        )
        data_processing_error = DataProcessingError(
            message="Data processing error",
            component="test_component",
            data_type="test_data",  # Added required data_type parameter
            data_source="test_source",
            operation="data_processing"
        )
        
        # Check inheritance
        self.assertIsInstance(system_error, ApexAgentError)
        self.assertIsInstance(initialization_error, ApexAgentError)
        self.assertIsInstance(configuration_error, ApexAgentError)
        self.assertIsInstance(resource_error, ApexAgentError)
        self.assertIsInstance(plugin_error, ApexAgentError)
        self.assertIsInstance(plugin_load_error, PluginError)
        self.assertIsInstance(plugin_execution_error, PluginError)
        self.assertIsInstance(plugin_dependency_error, PluginError)
        self.assertIsInstance(api_error, ApexAgentError)
        self.assertIsInstance(authentication_error, ApexAgentError)
        self.assertIsInstance(rate_limit_error, APIError)
        self.assertIsInstance(service_unavailable_error, APIError)
        self.assertIsInstance(user_error, ApexAgentError)
        self.assertIsInstance(validation_error, UserError)
        self.assertIsInstance(data_error, ApexAgentError)
        self.assertIsInstance(data_format_error, DataError)
        self.assertIsInstance(data_storage_error, DataError)
        self.assertIsInstance(data_processing_error, DataError)
        
        # Check specific properties
        self.assertEqual(configuration_error.context["config_key"], "test_key")
        self.assertEqual(resource_error.context["resource_type"], "test_resource")
        self.assertEqual(plugin_error.context["plugin_name"], "test_plugin")
        self.assertEqual(plugin_load_error.context["plugin_path"], "test_path")
        self.assertEqual(plugin_execution_error.context["operation"], "test_action")
        self.assertEqual(plugin_dependency_error.context["dependency_id"], "test_dependency")
        self.assertEqual(api_error.context["api_name"], "test_api")
        self.assertEqual(authentication_error.context["service"], "test_service")
        self.assertEqual(rate_limit_error.context["limit"], 100)
        self.assertIsNotNone(rate_limit_error.context["reset_time"])
        self.assertEqual(service_unavailable_error.context["service"], "test_service")
        self.assertEqual(user_error.context["user_id"], "test_user")
        self.assertEqual(validation_error.context["field"], "test_field")
        self.assertEqual(validation_error.context["reason"], "test_reason")
        self.assertEqual(data_error.context["data_source"], "test_source")
        self.assertEqual(data_format_error.context["expected_format"], "test_format")
        self.assertEqual(data_storage_error.context["operation"], "data_storage")
        self.assertEqual(data_processing_error.context["operation"], "data_processing")


class TestErrorMessages(unittest.TestCase):
    """Test error messages."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a message manager
        self.message_manager = ErrorMessageManager()
        
        # Register message templates
        self.message_manager.register_message_template(
            "system_error",
            "A system error occurred in {component}: {message}",
            "Please check system logs for more information."
        )
        self.message_manager.register_message_template(
            "initialization_error",
            "Failed to initialize {component}: {message}",
            "Please restart the application."
        )
        self.message_manager.register_message_template(
            "configuration_error",
            "Invalid configuration for {component}: {message}",
            "Please check the configuration file."
        )
        self.message_manager.register_message_template(
            "plugin_error",
            "Plugin error in {plugin_name}: {message}",
            "Please check the plugin configuration."
        )
        self.message_manager.register_message_template(
            "api_error",
            "API error in {api_name}: {message}",
            "Please check your internet connection."
        )
        self.message_manager.register_message_template(
            "authentication_error",
            "Authentication failed for {service}: {message}",
            "Please check your credentials."
        )
        self.message_manager.register_message_template(
            "user_error",
            "User error: {message}",
            "Please check your input."
        )
        self.message_manager.register_message_template(
            "data_error",
            "Data error in {data_source}: {message}",
            "Please check the data source."
        )
    
    def test_message_template_registration(self):
        """Test registering message templates."""
        # Check that templates were registered
        self.assertIn("system_error", self.message_manager.message_templates)
        self.assertIn("initialization_error", self.message_manager.message_templates)
        self.assertIn("configuration_error", self.message_manager.message_templates)
        self.assertIn("plugin_error", self.message_manager.message_templates)
        self.assertIn("api_error", self.message_manager.message_templates)
        self.assertIn("authentication_error", self.message_manager.message_templates)
        self.assertIn("user_error", self.message_manager.message_templates)
        self.assertIn("data_error", self.message_manager.message_templates)
    
    def test_format_error_message(self):
        """Test formatting error messages."""
        # Create an error
        error = SystemError(
            message="Test error",
            component="test_component",
            operation="test_operation"
        )
        
        # Format the message
        message = self.message_manager.format_error_message(error)
        
        # Check the message
        self.assertIn("system error", message.lower())
        self.assertIn("test_component", message)
        self.assertIn("Test error", message)
    
    def test_format_error_message_with_recovery(self):
        """Test formatting error messages with recovery suggestions."""
        # Create an error
        error = SystemError(
            message="Test error",
            component="test_component",
            operation="test_operation"
        )
        
        # Format the message with recovery suggestion
        message = self.message_manager.format_error_message(
            error, include_recovery=True
        )
        
        # Check the message
        self.assertIn("system error", message.lower())
        self.assertIn("test_component", message)
        self.assertIn("Test error", message)
        self.assertIn("system logs", message.lower())
    
    def test_format_error_message_with_custom_template(self):
        """Test formatting error messages with custom templates."""
        # Create an error
        error = SystemError(
            message="Test error",
            component="test_component",
            operation="test_operation"
        )
        
        # Format the message with a custom template
        message = self.message_manager.format_error_message(
            error,
            message_template="Custom message: {message}",
            recovery_template="Custom recovery: {component}"
        )
        
        # Check the message
        self.assertIn("Custom message", message)
        self.assertIn("Test error", message)
        self.assertNotIn("Custom recovery", message)
        
        # Format the message with a custom template and recovery
        message = self.message_manager.format_error_message(
            error,
            message_template="Custom message: $message",
            recovery_template="Custom recovery: $component",
            include_recovery=True
        )
        
        # Check the message
        self.assertIn("Custom message", message)
        self.assertIn("Test error", message)
        self.assertIn("Custom recovery", message)
        self.assertIn("test_component", message)
    
    def test_format_error_for_user(self):
        """Test formatting errors for user display."""
        # Create an error
        error = SystemError(
            message="Test error",
            component="test_component",
            operation="test_operation"
        )
        
        # Set user message and recovery suggestion
        error.user_message = "User-friendly error message"
        error.recovery_suggestion = "User-friendly recovery suggestion"
        
        # Format the error for user display
        message = format_error_for_user(error)
        
        # Check the message
        self.assertIn("User-friendly error message", message)
        self.assertIn("User-friendly recovery suggestion", message)
        self.assertIn(error.error_code, message)


class TestErrorTelemetry(unittest.TestCase):
    """Test error telemetry."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a telemetry instance
        self.telemetry = ErrorTelemetry()
        
        # Create an async telemetry instance
        self.async_telemetry = AsyncErrorTelemetry()
    
    def test_log_error(self):
        """Test logging errors."""
        # Create an error
        error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        
        # Log the error
        self.telemetry.log_error(error)
        
        # Check that the error was logged
        errors = self.telemetry.get_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["error_type"], "SystemError")
        self.assertEqual(errors[0]["message"], "System error")
        self.assertEqual(errors[0]["component"], "test_component")
    
    def test_log_multiple_errors(self):
        """Test logging multiple errors."""
        # Create errors
        system_error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        api_error = APIError(
            message="API error",
            component="test_component",
            api_name="test_api",
            operation="test_operation"
        )
        
        # Log the errors
        self.telemetry.log_error(system_error)
        self.telemetry.log_error(api_error)
        
        # Check that the errors were logged
        errors = self.telemetry.get_errors()
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]["error_type"], "SystemError")
        self.assertEqual(errors[1]["error_type"], "APIError")
    
    def test_get_errors_by_type(self):
        """Test getting errors by type."""
        # Create errors
        system_error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        api_error_1 = APIError(
            message="API error 1",
            component="test_component",
            api_name="test_api",
            operation="test_operation"
        )
        api_error_2 = APIError(
            message="API error 2",
            component="test_component",
            api_name="test_api",
            operation="test_operation"
        )
        
        # Log the errors
        self.telemetry.log_error(system_error)
        self.telemetry.log_error(api_error_1)
        self.telemetry.log_error(api_error_2)
        
        # Get errors by type
        system_errors = self.telemetry.get_errors_by_type("SystemError")
        api_errors = self.telemetry.get_errors_by_type("APIError")
        
        # Check the errors
        self.assertEqual(len(system_errors), 1)
        self.assertEqual(system_errors[0]["message"], "System error")
        
        self.assertEqual(len(api_errors), 2)
        self.assertEqual(api_errors[0]["message"], "API error 1")
        self.assertEqual(api_errors[1]["message"], "API error 2")
    
    def test_get_errors_by_component(self):
        """Test getting errors by component."""
        # Create errors
        system_error = SystemError(
            message="System error",
            component="component_1",
            operation="test_operation"
        )
        api_error = APIError(
            message="API error",
            component="component_2",
            api_name="test_api",
            operation="test_operation"
        )
        
        # Log the errors
        self.telemetry.log_error(system_error)
        self.telemetry.log_error(api_error)
        
        # Get errors by component
        component_1_errors = self.telemetry.get_errors_by_component("component_1")
        component_2_errors = self.telemetry.get_errors_by_component("component_2")
        
        # Check the errors
        self.assertEqual(len(component_1_errors), 1)
        self.assertEqual(component_1_errors[0]["message"], "System error")
        
        self.assertEqual(len(component_2_errors), 1)
        self.assertEqual(component_2_errors[0]["message"], "API error")
    
    def test_get_errors_by_severity(self):
        """Test getting errors by severity."""
        # Create errors
        system_error = SystemError(
            message="System error",
            component="test_component",
            severity=ErrorSeverity.CRITICAL,
            operation="test_operation"
        )
        api_error = APIError(
            message="API error",
            component="test_component",
            api_name="test_api",
            severity=ErrorSeverity.WARNING,
            operation="test_operation"
        )
        
        # Log the errors
        self.telemetry.log_error(system_error)
        self.telemetry.log_error(api_error)
        
        # Get errors by severity
        critical_errors = self.telemetry.get_errors_by_severity(ErrorSeverity.CRITICAL)
        warning_errors = self.telemetry.get_errors_by_severity(ErrorSeverity.WARNING)
        
        # Check the errors
        self.assertEqual(len(critical_errors), 1)
        self.assertEqual(critical_errors[0]["message"], "System error")
        
        self.assertEqual(len(warning_errors), 1)
        self.assertEqual(warning_errors[0]["message"], "API error")
    
    def test_get_error_count(self):
        """Test getting error count."""
        # Create errors
        system_error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        api_error = APIError(
            message="API error",
            component="test_component",
            api_name="test_api",
            operation="test_operation"
        )
        
        # Log the errors
        self.telemetry.log_error(system_error)
        self.telemetry.log_error(api_error)
        
        # Get error count
        count = self.telemetry.get_error_count()
        system_count = self.telemetry.get_error_count("SystemError")
        api_count = self.telemetry.get_error_count("APIError")
        
        # Check the counts
        self.assertEqual(count, 2)
        self.assertEqual(system_count, 1)
        self.assertEqual(api_count, 1)
    
    def test_get_error_frequency(self):
        """Test getting error frequency."""
        # Create errors
        system_error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        api_error = APIError(
            message="API error",
            component="test_component",
            api_name="test_api",
            operation="test_operation"
        )
        
        # Log the errors multiple times
        self.telemetry.log_error(system_error)
        self.telemetry.log_error(api_error)
        self.telemetry.log_error(system_error)
        
        # Get error frequency
        frequency = self.telemetry.get_error_frequency()
        
        # Check the frequency
        self.assertEqual(len(frequency), 2)
        self.assertEqual(frequency["SystemError"], 2)
        self.assertEqual(frequency["APIError"], 1)
    
    def test_clear_errors(self):
        """Test clearing errors."""
        # Create an error
        error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        
        # Log the error
        self.telemetry.log_error(error)
        
        # Check that the error was logged
        self.assertEqual(len(self.telemetry.get_errors()), 1)
        
        # Clear the errors
        self.telemetry.clear_errors()
        
        # Check that the errors were cleared
        self.assertEqual(len(self.telemetry.get_errors()), 0)
    
    async def test_async_log_error(self):
        """Test logging errors asynchronously."""
        # Create an error
        error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        
        # Log the error asynchronously
        await self.async_telemetry.log_error(error)
        
        # Check that the error was logged
        errors = await self.async_telemetry.get_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["error_type"], "SystemError")
    
    async def test_async_get_error_report(self):
        """Test getting error reports asynchronously."""
        # Create errors
        system_error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        api_error = APIError(
            message="API error",
            component="test_component",
            api_name="test_api",
            operation="test_operation"
        )
        
        # Log the errors asynchronously
        await self.async_telemetry.log_error(system_error)
        await self.async_telemetry.log_error(api_error)
        
        # Get error report
        report = await self.async_telemetry.get_error_report()
        
        # Check the report
        self.assertEqual(report["total_errors"], 2)
        self.assertEqual(report["error_types"]["SystemError"], 1)
        self.assertEqual(report["error_types"]["APIError"], 1)
        self.assertEqual(report["components"]["test_component"], 2)


class TestErrorEvents(unittest.IsolatedAsyncioTestCase):
    """Test error events."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Create an event manager
        self.event_manager = EventManager()
        
        # Create an error event emitter
        self.emitter = ErrorEventEmitter(self.event_manager)
    
    async def test_error_to_event(self):
        """Test converting errors to events."""
        # Create an error
        error = SystemError(
            message="System error",
            component="test_component",
            severity=ErrorSeverity.CRITICAL,
            operation="test_operation"
        )
        
        # Convert to event
        event = self.emitter.error_to_event(error)
        
        # Check event
        self.assertEqual(event.event_type, "error.SystemError")
        self.assertEqual(event.source, "error_handler")
        self.assertEqual(event.data["message"], "System error")
        self.assertEqual(event.data["component"], "test_component")
        self.assertEqual(event.data["severity"], "CRITICAL")
        self.assertEqual(event.priority, EventPriority.CRITICAL)
    
    async def test_emit_error(self):
        """Test emitting errors as events."""
        # Create a subscriber to receive events
        events_received = []
        
        class TestSubscriber(EventSubscriber):
            @property
            def subscribed_event_types(self):
                return {"error.*"}
            
            def matches_event(self, event):
                return event.event_type.startswith("error.")
            
            async def handle_event(self, event):
                events_received.append(event)
        
        # Register the subscriber
        subscriber = TestSubscriber()
        await self.event_manager.register_subscriber(subscriber)
        
        # Create an error
        error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        
        # Emit the error as an event
        event = await self.emitter.emit_error(error)
        
        # Check that the event was emitted
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].event_type, "error.SystemError")
    
    async def test_error_event_subscriber(self):
        """Test subscribing to error events."""
        # Create a list to store received events
        events_received = []
        
        # Create a callback function
        async def handle_event(event):
            events_received.append(event)
        
        # Create a subscriber
        subscriber = ErrorEventSubscriber(
            error_types=["SystemError"],
            callback=handle_event
        )
        
        # Register the subscriber
        await self.event_manager.register_subscriber(subscriber)
        
        # Create and emit an error event
        system_error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        api_error = APIError(
            message="API error",
            component="test_component",
            api_name="test_api",
            operation="test_operation"
        )
        
        # Emit the errors as events
        await self.emitter.emit_error(system_error)
        await self.emitter.emit_error(api_error)
        
        # Check that only the system error event was received
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].event_type, "error.SystemError")
    
    async def test_error_event_handler(self):
        """Test handling error events."""
        handler = ErrorEventHandler(self.event_manager)
        
        # Wait for handler initialization to complete
        await asyncio.sleep(0.1)
        
        # Register a handler
        events_handled = []
        
        async def handle_system_error(event):
            events_handled.append(event)
        
        handler.register_handler("SystemError", handle_system_error)
        
        # Create and emit an error event
        event = Event(
            event_type="error.SystemError",
            source="test",
            data={"error_type": "SystemError", "message": "System error"}
        )
        
        await self.event_manager.emit(event)
        await asyncio.sleep(0.1)
        
        # Check that the event was handled
        self.assertEqual(len(events_handled), 1)
        self.assertEqual(events_handled[0].event_type, "error.SystemError")


class TestErrorRecovery(unittest.IsolatedAsyncioTestCase):
    """Test error recovery."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a recovery manager
        self.recovery_manager = ErrorRecoveryManager()
    
    def test_register_recovery_strategy(self):
        """Test registering recovery strategies."""
        # Register a recovery strategy
        def recover_config_error(error, **kwargs):
            return True
        
        self.recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        
        # Check that the strategy was registered
        self.assertIn("ConfigurationError", self.recovery_manager.strategies)
        self.assertEqual(
            self.recovery_manager.strategies["ConfigurationError"]["function"],
            recover_config_error
        )
        self.assertEqual(
            self.recovery_manager.strategies["ConfigurationError"]["description"],
            "Loads default configuration values"
        )
    
    def test_get_recovery_strategy(self):
        """Test getting recovery strategies."""
        # Register a recovery strategy
        def recover_config_error(error, **kwargs):
            return True
        
        self.recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        
        # Get the strategy
        strategy = self.recovery_manager.get_strategy("ConfigurationError")
        
        # Check the strategy
        self.assertEqual(strategy["function"], recover_config_error)
        self.assertEqual(strategy["description"], "Loads default configuration values")
    
    def test_get_recovery_strategies(self):
        """Test getting all recovery strategies."""
        # Register recovery strategies
        def recover_config_error(error, **kwargs):
            return True
        
        def recover_api_error(error, **kwargs):
            return True
        
        self.recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        self.recovery_manager.register_strategy(
            "APIError",
            recover_api_error,
            "Retries the API request"
        )
        
        # Get all strategies
        strategies = self.recovery_manager.get_strategies()
        
        # Check the strategies
        self.assertEqual(len(strategies), 2)
        self.assertIn("ConfigurationError", strategies)
        self.assertIn("APIError", strategies)
    
    def test_has_recovery_strategy(self):
        """Test checking if a recovery strategy exists."""
        # Register a recovery strategy
        def recover_config_error(error, **kwargs):
            return True
        
        self.recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        
        # Check if strategies exist
        self.assertTrue(self.recovery_manager.has_strategy("ConfigurationError"))
        self.assertFalse(self.recovery_manager.has_strategy("APIError"))
    
    def test_unregister_recovery_strategy(self):
        """Test unregistering recovery strategies."""
        # Register a recovery strategy
        def recover_config_error(error, **kwargs):
            return True
        
        self.recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        
        # Check that the strategy was registered
        self.assertTrue(self.recovery_manager.has_strategy("ConfigurationError"))
        
        # Unregister the strategy
        self.recovery_manager.unregister_strategy("ConfigurationError")
        
        # Check that the strategy was unregistered
        self.assertFalse(self.recovery_manager.has_strategy("ConfigurationError"))
    
    def test_attempt_recovery(self):
        """Test attempting recovery."""
        # Register a recovery strategy
        recovery_attempted = False
        
        def recover_config_error(error, **kwargs):
            nonlocal recovery_attempted
            recovery_attempted = True
            return True
        
        self.recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        
        # Create an error
        error = ConfigurationError(
            message="Configuration error",
            component="test_component",
            config_key="test_key"
        )
        
        # Attempt recovery
        result = self.recovery_manager.attempt_recovery(error)
        
        # Check the result
        self.assertTrue(result)
        self.assertTrue(recovery_attempted)
    
    def test_attempt_recovery_with_kwargs(self):
        """Test attempting recovery with additional arguments."""
        # Register a recovery strategy
        received_kwargs = {}
        
        def recover_config_error(error, **kwargs):
            nonlocal received_kwargs
            received_kwargs = kwargs
            return True
        
        self.recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        
        # Create an error
        error = ConfigurationError(
            message="Configuration error",
            component="test_component",
            config_key="test_key"
        )
        
        # Attempt recovery with additional arguments
        result = self.recovery_manager.attempt_recovery(
            error, key1="value1", key2="value2"
        )
        
        # Check the result
        self.assertTrue(result)
        self.assertEqual(received_kwargs["key1"], "value1")
        self.assertEqual(received_kwargs["key2"], "value2")
    
    def test_attempt_recovery_no_strategy(self):
        """Test attempting recovery with no strategy."""
        # Create an error
        error = ConfigurationError(
            message="Configuration error",
            component="test_component",
            config_key="test_key"
        )
        
        # Attempt recovery
        result = self.recovery_manager.attempt_recovery(error)
        
        # Check the result
        self.assertFalse(result)
    
    def test_attempt_recovery_failed(self):
        """Test attempting recovery that fails."""
        # Register a recovery strategy
        def recover_config_error(error, **kwargs):
            return False
        
        self.recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        
        # Create an error
        error = ConfigurationError(
            message="Configuration error",
            component="test_component",
            config_key="test_key"
        )
        
        # Attempt recovery
        result = self.recovery_manager.attempt_recovery(error)
        
        # Check the result
        self.assertFalse(result)


class TestErrorHandlingIntegration(unittest.IsolatedAsyncioTestCase):
    """Test error handling integration."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Create components
        self.event_manager = EventManager()
        self.emitter = ErrorEventEmitter(self.event_manager)
        self.telemetry = ErrorTelemetry()
        
        # Create a subscriber to receive events
        self.events_received = []
        
        class TestSubscriber(EventSubscriber):
            def __init__(self, events_received):
                self.events_received = events_received
            
            @property
            def subscribed_event_types(self):
                return {"error.*"}
            
            def matches_event(self, event):
                return event.event_type.startswith("error.")
            
            async def handle_event(self, event):
                self.events_received.append(event)
        
        # Register the subscriber
        self.subscriber = TestSubscriber(self.events_received)
        await self.event_manager.register_subscriber(self.subscriber)
    
    async def test_end_to_end_error_flow(self):
        """Test the complete error handling flow."""
        # Create an error
        error = SystemError(
            message="System error",
            component="test_component",
            operation="test_operation"
        )
        
        # Emit the error as an event and log to telemetry
        await self.emitter.emit_error(error)
        self.telemetry.log_error(error)
        
        # Wait a moment to ensure event processing is complete
        await asyncio.sleep(0.1)
        
        # Check that the event was emitted
        self.assertEqual(len(self.events_received), 1)
        self.assertEqual(self.events_received[0].event_type, "error.SystemError")
        
        # Check that the error was logged to telemetry
        errors = self.telemetry.get_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["error_type"], "SystemError")
        
        # Format the error for user display
        message = format_error_for_user(error)
        self.assertIn("test_component", message)
        self.assertIn("system logs", message)
    
    async def test_error_recovery_flow(self):
        """Test the error recovery flow."""
        # Initialize components
        recovery_manager = ErrorRecoveryManager()
        
        # Register a recovery strategy
        recovery_attempted = False
        
        def recover_config_error(error, **kwargs):
            nonlocal recovery_attempted
            recovery_attempted = True
            return True
        
        recovery_manager.register_strategy(
            "ConfigurationError",
            recover_config_error,
            "Loads default configuration values"
        )
        
        # Create an error with recovery capability
        error = ConfigurationError(
            message="Configuration error",
            component="test_component",
            config_key="test_key",
            can_recover=True,
            recovery_func=recover_config_error
        )
        
        # Emit the error as an event
        event = await self.emitter.emit_error(error)
        
        # Attempt recovery
        result = recovery_manager.attempt_recovery(error)
        
        # Check the result
        self.assertTrue(result)
        self.assertTrue(recovery_attempted)
        
        # Check that the event was emitted
        self.assertEqual(len(self.events_received), 1)
        self.assertEqual(self.events_received[0].event_type, "error.ConfigurationError")


if __name__ == "__main__":
    unittest.main()
