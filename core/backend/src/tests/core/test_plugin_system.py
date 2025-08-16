"""
Test module for the ApexAgent plugin system.

This module contains comprehensive tests for the plugin system, including:
- Plugin loading and registration
- Plugin discovery
- Plugin lifecycle management
- Plugin API and event hooks
- Plugin security and isolation
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import logging
from unittest.mock import MagicMock, patch

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.plugin_loader import PluginLoader, PluginRegistry
from src.core.plugin_discovery import PluginDiscovery
from src.core.plugin_lifecycle import PluginLifecycleManager
from src.core.plugin_api import PluginAPI, PluginEventHooks
from src.core.plugin_security import PluginSecurityManager, PluginIsolationManager
from src.core.plugin_system import PluginSystem
from src.core.event_system.event_manager import EventManager
from src.core.event_system.event import Event
from src.core.plugin_exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginLoadError,
    PluginSecurityError,
    PluginPermissionError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestPluginLoader(unittest.TestCase):
    """Test cases for the PluginLoader class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_registry = PluginRegistry()
        self.plugin_loader = PluginLoader(self.plugin_registry)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_plugin_registry(self):
        """Test plugin registry functionality."""
        # Create mock plugin
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = "test_plugin"
        
        # Register plugin
        self.plugin_registry.register_plugin("test_plugin", mock_plugin)
        
        # Check if plugin is registered
        self.assertTrue(self.plugin_registry.is_registered("test_plugin"))
        self.assertEqual(self.plugin_registry.get_plugin("test_plugin"), mock_plugin)
        self.assertEqual(len(self.plugin_registry.get_all_plugins()), 1)
        
        # Unregister plugin
        self.plugin_registry.unregister_plugin("test_plugin")
        
        # Check if plugin is unregistered
        self.assertFalse(self.plugin_registry.is_registered("test_plugin"))
        with self.assertRaises(PluginNotFoundError):
            self.plugin_registry.get_plugin("test_plugin")
        self.assertEqual(len(self.plugin_registry.get_all_plugins()), 0)
    
    def test_load_plugin_module(self):
        """Test loading a plugin module."""
        # Create a simple plugin module
        plugin_dir = os.path.join(self.temp_dir, "test_plugin")
        os.makedirs(plugin_dir)
        
        with open(os.path.join(plugin_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(plugin_dir, "test_plugin.py"), "w") as f:
            f.write("""
class TestPlugin:
    def __init__(self, plugin_id, config):
        self.plugin_id = plugin_id
        self.config = config
    
    def get_id(self):
        return self.plugin_id

PLUGIN_MANIFEST = {
    "name": "Test Plugin",
    "version": "1.0.0",
    "description": "A test plugin",
    "main_class": "TestPlugin"
}
""")
        
        # Load plugin module
        module = self.plugin_loader._load_plugin_module(plugin_dir, "test_plugin")
        
        # Check if module is loaded correctly
        self.assertIsNotNone(module)
        self.assertTrue(hasattr(module, "TestPlugin"))
        self.assertTrue(hasattr(module, "PLUGIN_MANIFEST"))
        self.assertEqual(module.PLUGIN_MANIFEST["name"], "Test Plugin")
    
    def test_load_plugin_class(self):
        """Test loading a plugin class."""
        # Create a simple plugin module
        plugin_dir = os.path.join(self.temp_dir, "test_plugin")
        os.makedirs(plugin_dir)
        
        with open(os.path.join(plugin_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(plugin_dir, "test_plugin.py"), "w") as f:
            f.write("""
class TestPlugin:
    def __init__(self, plugin_id, config):
        self.plugin_id = plugin_id
        self.config = config
    
    def get_id(self):
        return self.plugin_id

PLUGIN_MANIFEST = {
    "name": "Test Plugin",
    "version": "1.0.0",
    "description": "A test plugin",
    "main_class": "TestPlugin"
}
""")
        
        # Load plugin module
        module = self.plugin_loader._load_plugin_module(plugin_dir, "test_plugin")
        
        # Load plugin class
        plugin_class = self.plugin_loader._load_plugin_class(module, "TestPlugin")
        
        # Check if class is loaded correctly
        self.assertIsNotNone(plugin_class)
        
        # Instantiate plugin
        plugin_instance = plugin_class("test_plugin_id", {"test": "config"})
        
        # Check if instance is created correctly
        self.assertEqual(plugin_instance.get_id(), "test_plugin_id")
    
    def test_load_plugin(self):
        """Test loading a plugin."""
        # Create a simple plugin module
        plugin_dir = os.path.join(self.temp_dir, "test_plugin")
        os.makedirs(plugin_dir)
        
        with open(os.path.join(plugin_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(plugin_dir, "test_plugin.py"), "w") as f:
            f.write("""
class TestPlugin:
    def __init__(self, plugin_id, config):
        self.plugin_id = plugin_id
        self.config = config
    
    def get_id(self):
        return self.plugin_id

PLUGIN_MANIFEST = {
    "name": "Test Plugin",
    "version": "1.0.0",
    "description": "A test plugin",
    "main_class": "TestPlugin"
}
""")
        
        # Load plugin
        plugin_id = "test_plugin"
        plugin_instance = self.plugin_loader.load_plugin(plugin_dir, plugin_id, {"test": "config"})
        
        # Check if plugin is loaded correctly
        self.assertIsNotNone(plugin_instance)
        self.assertEqual(plugin_instance.get_id(), plugin_id)
        
        # Check if plugin is registered
        self.assertTrue(self.plugin_registry.is_registered(plugin_id))
        self.assertEqual(self.plugin_registry.get_plugin(plugin_id), plugin_instance)


class TestPluginDiscovery(unittest.TestCase):
    """Test cases for the PluginDiscovery class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_registry = PluginRegistry()
        self.plugin_loader = PluginLoader(self.plugin_registry)
        self.plugin_discovery = PluginDiscovery(self.plugin_loader)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_discover_plugins(self):
        """Test discovering plugins in a directory."""
        # Create plugin directories
        plugin1_dir = os.path.join(self.temp_dir, "plugin1")
        plugin2_dir = os.path.join(self.temp_dir, "plugin2")
        os.makedirs(plugin1_dir)
        os.makedirs(plugin2_dir)
        
        # Create plugin1 files
        with open(os.path.join(plugin1_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(plugin1_dir, "plugin1.py"), "w") as f:
            f.write("""
class Plugin1:
    def __init__(self, plugin_id, config):
        self.plugin_id = plugin_id
        self.config = config

PLUGIN_MANIFEST = {
    "name": "Plugin 1",
    "version": "1.0.0",
    "description": "Test plugin 1",
    "main_class": "Plugin1"
}
""")
        
        # Create plugin2 files
        with open(os.path.join(plugin2_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(plugin2_dir, "plugin2.py"), "w") as f:
            f.write("""
class Plugin2:
    def __init__(self, plugin_id, config):
        self.plugin_id = plugin_id
        self.config = config

PLUGIN_MANIFEST = {
    "name": "Plugin 2",
    "version": "1.0.0",
    "description": "Test plugin 2",
    "main_class": "Plugin2"
}
""")
        
        # Create manifest files
        with open(os.path.join(plugin1_dir, "manifest.json"), "w") as f:
            json.dump({
                "name": "Plugin 1",
                "version": "1.0.0",
                "description": "Test plugin 1",
                "main_class": "Plugin1",
                "main_file": "plugin1.py"
            }, f)
        
        with open(os.path.join(plugin2_dir, "manifest.json"), "w") as f:
            json.dump({
                "name": "Plugin 2",
                "version": "1.0.0",
                "description": "Test plugin 2",
                "main_class": "Plugin2",
                "main_file": "plugin2.py"
            }, f)
        
        # Discover plugins
        discovered_plugins = self.plugin_discovery.discover_plugins(self.temp_dir)
        
        # Check if plugins are discovered correctly
        self.assertEqual(len(discovered_plugins), 2)
        self.assertIn("plugin1", discovered_plugins)
        self.assertIn("plugin2", discovered_plugins)
        
        # Check plugin metadata
        self.assertEqual(discovered_plugins["plugin1"]["name"], "Plugin 1")
        self.assertEqual(discovered_plugins["plugin2"]["name"], "Plugin 2")
    
    def test_load_discovered_plugins(self):
        """Test loading discovered plugins."""
        # Create plugin directories
        plugin1_dir = os.path.join(self.temp_dir, "plugin1")
        plugin2_dir = os.path.join(self.temp_dir, "plugin2")
        os.makedirs(plugin1_dir)
        os.makedirs(plugin2_dir)
        
        # Create plugin1 files
        with open(os.path.join(plugin1_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(plugin1_dir, "plugin1.py"), "w") as f:
            f.write("""
class Plugin1:
    def __init__(self, plugin_id, config):
        self.plugin_id = plugin_id
        self.config = config
    
    def get_name(self):
        return "Plugin 1"

PLUGIN_MANIFEST = {
    "name": "Plugin 1",
    "version": "1.0.0",
    "description": "Test plugin 1",
    "main_class": "Plugin1"
}
""")
        
        # Create plugin2 files
        with open(os.path.join(plugin2_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(plugin2_dir, "plugin2.py"), "w") as f:
            f.write("""
class Plugin2:
    def __init__(self, plugin_id, config):
        self.plugin_id = plugin_id
        self.config = config
    
    def get_name(self):
        return "Plugin 2"

PLUGIN_MANIFEST = {
    "name": "Plugin 2",
    "version": "1.0.0",
    "description": "Test plugin 2",
    "main_class": "Plugin2"
}
""")
        
        # Create manifest files
        with open(os.path.join(plugin1_dir, "manifest.json"), "w") as f:
            json.dump({
                "name": "Plugin 1",
                "version": "1.0.0",
                "description": "Test plugin 1",
                "main_class": "Plugin1",
                "main_file": "plugin1.py"
            }, f)
        
        with open(os.path.join(plugin2_dir, "manifest.json"), "w") as f:
            json.dump({
                "name": "Plugin 2",
                "version": "1.0.0",
                "description": "Test plugin 2",
                "main_class": "Plugin2",
                "main_file": "plugin2.py"
            }, f)
        
        # Discover plugins
        discovered_plugins = self.plugin_discovery.discover_plugins(self.temp_dir)
        
        # Load discovered plugins
        loaded_plugins = self.plugin_discovery.load_discovered_plugins(
            discovered_plugins,
            {"plugin1": {"config": "value1"}, "plugin2": {"config": "value2"}}
        )
        
        # Check if plugins are loaded correctly
        self.assertEqual(len(loaded_plugins), 2)
        self.assertIn("plugin1", loaded_plugins)
        self.assertIn("plugin2", loaded_plugins)
        
        # Check if plugins are registered
        self.assertTrue(self.plugin_registry.is_registered("plugin1"))
        self.assertTrue(self.plugin_registry.is_registered("plugin2"))
        
        # Check plugin instances
        plugin1 = self.plugin_registry.get_plugin("plugin1")
        plugin2 = self.plugin_registry.get_plugin("plugin2")
        
        self.assertEqual(plugin1.get_name(), "Plugin 1")
        self.assertEqual(plugin2.get_name(), "Plugin 2")


class TestPluginLifecycle(unittest.TestCase):
    """Test cases for the PluginLifecycleManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_registry = PluginRegistry()
        self.event_manager = EventManager()
        self.plugin_lifecycle = PluginLifecycleManager(self.plugin_registry, self.event_manager)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_plugin_lifecycle(self):
        """Test plugin lifecycle management."""
        # Create mock plugin with lifecycle methods
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = "test_plugin"
        mock_plugin.on_load = MagicMock()
        mock_plugin.on_start = MagicMock()
        mock_plugin.on_stop = MagicMock()
        mock_plugin.on_unload = MagicMock()
        
        # Register plugin
        self.plugin_registry.register_plugin("test_plugin", mock_plugin)
        
        # Test lifecycle methods
        self.plugin_lifecycle.load_plugin("test_plugin")
        mock_plugin.on_load.assert_called_once()
        
        self.plugin_lifecycle.start_plugin("test_plugin")
        mock_plugin.on_start.assert_called_once()
        
        self.plugin_lifecycle.stop_plugin("test_plugin")
        mock_plugin.on_stop.assert_called_once()
        
        self.plugin_lifecycle.unload_plugin("test_plugin")
        mock_plugin.on_unload.assert_called_once()
    
    def test_plugin_state_transitions(self):
        """Test plugin state transitions."""
        # Create mock plugin
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = "test_plugin"
        
        # Register plugin
        self.plugin_registry.register_plugin("test_plugin", mock_plugin)
        
        # Initial state should be REGISTERED
        self.assertEqual(self.plugin_lifecycle.get_plugin_state("test_plugin"), "REGISTERED")
        
        # Test state transitions
        self.plugin_lifecycle.load_plugin("test_plugin")
        self.assertEqual(self.plugin_lifecycle.get_plugin_state("test_plugin"), "LOADED")
        
        self.plugin_lifecycle.start_plugin("test_plugin")
        self.assertEqual(self.plugin_lifecycle.get_plugin_state("test_plugin"), "STARTED")
        
        self.plugin_lifecycle.stop_plugin("test_plugin")
        self.assertEqual(self.plugin_lifecycle.get_plugin_state("test_plugin"), "STOPPED")
        
        self.plugin_lifecycle.unload_plugin("test_plugin")
        self.assertEqual(self.plugin_lifecycle.get_plugin_state("test_plugin"), "UNLOADED")
    
    def test_plugin_events(self):
        """Test plugin lifecycle events."""
        # Create event listeners
        load_event = MagicMock()
        start_event = MagicMock()
        stop_event = MagicMock()
        unload_event = MagicMock()
        
        # Subscribe to events
        self.event_manager.subscribe("plugin.loaded", load_event)
        self.event_manager.subscribe("plugin.started", start_event)
        self.event_manager.subscribe("plugin.stopped", stop_event)
        self.event_manager.subscribe("plugin.unloaded", unload_event)
        
        # Create mock plugin
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = "test_plugin"
        
        # Register plugin
        self.plugin_registry.register_plugin("test_plugin", mock_plugin)
        
        # Test lifecycle events
        self.plugin_lifecycle.load_plugin("test_plugin")
        load_event.assert_called_once()
        self.assertEqual(load_event.call_args[0][0].data["plugin_id"], "test_plugin")
        
        self.plugin_lifecycle.start_plugin("test_plugin")
        start_event.assert_called_once()
        self.assertEqual(start_event.call_args[0][0].data["plugin_id"], "test_plugin")
        
        self.plugin_lifecycle.stop_plugin("test_plugin")
        stop_event.assert_called_once()
        self.assertEqual(stop_event.call_args[0][0].data["plugin_id"], "test_plugin")
        
        self.plugin_lifecycle.unload_plugin("test_plugin")
        unload_event.assert_called_once()
        self.assertEqual(unload_event.call_args[0][0].data["plugin_id"], "test_plugin")


class TestPluginAPI(unittest.TestCase):
    """Test cases for the PluginAPI class."""
    
    def setUp(self):
        """Set up test environment."""
        self.plugin_registry = PluginRegistry()
        self.event_manager = EventManager()
        self.plugin_system = MagicMock()
        self.plugin_system.get_plugin.return_value = MagicMock()
        self.plugin_api = PluginAPI(self.plugin_system, self.event_manager)
    
    def test_register_api_endpoint(self):
        """Test registering an API endpoint."""
        # Define a test handler function
        def test_handler(arg1, arg2=None):
            return f"{arg1}-{arg2}"
        
        # Register API endpoint
        self.plugin_api.register_api_endpoint(
            "test_plugin",
            "test_endpoint",
            test_handler,
            version="1.0.0",
            description="Test endpoint",
            params={"arg1": {"type": "str"}, "arg2": {"type": "str", "required": False}},
            returns={"type": "str"}
        )
        
        # Check if endpoint is registered
        self.assertIn("test_plugin.test_endpoint", self.plugin_api.api_endpoints)
        self.assertEqual(self.plugin_api.api_endpoints["test_plugin.test_endpoint"], test_handler)
        
        # Check documentation
        self.assertIn("test_plugin.test_endpoint", self.plugin_api.api_documentation)
        self.assertEqual(
            self.plugin_api.api_documentation["test_plugin.test_endpoint"]["description"],
            "Test endpoint"
        )
        
        # Check version
        self.assertIn("test_plugin.test_endpoint", self.plugin_api.api_versions)
        self.assertEqual(self.plugin_api.api_versions["test_plugin.test_endpoint"], "1.0.0")
    
    def test_call_api(self):
        """Test calling an API endpoint."""
        # Define a test handler function
        def test_handler(arg1, arg2=None):
            return f"{arg1}-{arg2}"
        
        # Register API endpoint
        self.plugin_api.register_api_endpoint(
            "test_plugin",
            "test_endpoint",
            test_handler
        )
        
        # Call API endpoint
        result = self.plugin_api.call_api("test_plugin", "test_endpoint", "value1", arg2="value2")
        
        # Check result
        self.assertEqual(result, "value1-value2")
    
    def test_unregister_api_endpoint(self):
        """Test unregistering an API endpoint."""
        # Define a test handler function
        def test_handler():
            return "test"
        
        # Register API endpoint
        self.plugin_api.register_api_endpoint(
            "test_plugin",
            "test_endpoint",
            test_handler
        )
        
        # Unregister API endpoint
        self.plugin_api.unregister_api_endpoint("test_plugin", "test_endpoint")
        
        # Check if endpoint is unregistered
        self.assertNotIn("test_plugin.test_endpoint", self.plugin_api.api_endpoints)
        self.assertNotIn("test_plugin.test_endpoint", self.plugin_api.api_documentation)
        self.assertNotIn("test_plugin.test_endpoint", self.plugin_api.api_versions)
    
    def test_api_documentation(self):
        """Test API documentation."""
        # Define test handler functions
        def test_handler1():
            return "test1"
        
        def test_handler2():
            return "test2"
        
        # Register API endpoints
        self.plugin_api.register_api_endpoint(
            "test_plugin1",
            "test_endpoint1",
            test_handler1,
            description="Test endpoint 1"
        )
        
        self.plugin_api.register_api_endpoint(
            "test_plugin2",
            "test_endpoint2",
            test_handler2,
            description="Test endpoint 2"
        )
        
        # Get all documentation
        docs = self.plugin_api.get_api_documentation()
        
        # Check documentation
        self.assertEqual(len(docs), 2)
        self.assertIn("test_plugin1.test_endpoint1", docs)
        self.assertIn("test_plugin2.test_endpoint2", docs)
        
        # Get documentation for specific plugin
        plugin1_docs = self.plugin_api.get_api_documentation("test_plugin1")
        
        # Check plugin-specific documentation
        self.assertEqual(len(plugin1_docs), 1)
        self.assertIn("test_plugin1.test_endpoint1", plugin1_docs)
        self.assertNotIn("test_plugin2.test_endpoint2", plugin1_docs)


class TestPluginEventHooks(unittest.TestCase):
    """Test cases for the PluginEventHooks class."""
    
    def setUp(self):
        """Set up test environment."""
        self.plugin_registry = PluginRegistry()
        self.event_manager = EventManager()
        self.plugin_system = MagicMock()
        self.plugin_system.get_plugin.return_value = MagicMock()
        self.plugin_event_hooks = PluginEventHooks(self.plugin_system, self.event_manager)
    
    def test_register_event_handler(self):
        """Test registering an event handler."""
        # Define a test handler function
        handler_mock = MagicMock()
        
        # Register event handler
        self.plugin_event_hooks.register_event_handler(
            "test_plugin",
            "test.event",
            handler_mock
        )
        
        # Check if handler is registered
        self.assertIn(("test_plugin", "test.event"), self.plugin_event_hooks.event_handlers)
        self.assertEqual(
            self.plugin_event_hooks.event_handlers[("test_plugin", "test.event")],
            handler_mock
        )
        
        # Check subscriptions
        self.assertIn("test_plugin", self.plugin_event_hooks.plugin_subscriptions)
        self.assertIn("test.event", self.plugin_event_hooks.plugin_subscriptions["test_plugin"])
    
    def test_event_routing(self):
        """Test event routing to handlers."""
        # Define a test handler function
        handler_mock = MagicMock()
        
        # Register event handler
        self.plugin_event_hooks.register_event_handler(
            "test_plugin",
            "test.event",
            handler_mock
        )
        
        # Create and emit test event
        test_event = Event("test.event", {"test": "data"})
        self.event_manager.emit_event(test_event)
        
        # Check if handler was called
        handler_mock.assert_called_once()
        self.assertEqual(handler_mock.call_args[0][0], test_event)
    
    def test_unregister_event_handler(self):
        """Test unregistering an event handler."""
        # Define a test handler function
        handler_mock = MagicMock()
        
        # Register event handler
        self.plugin_event_hooks.register_event_handler(
            "test_plugin",
            "test.event",
            handler_mock
        )
        
        # Unregister event handler
        self.plugin_event_hooks.unregister_event_handler("test_plugin", "test.event")
        
        # Check if handler is unregistered
        self.assertNotIn(("test_plugin", "test.event"), self.plugin_event_hooks.event_handlers)
        
        # Check subscriptions
        self.assertNotIn("test.event", self.plugin_event_hooks.plugin_subscriptions["test_plugin"])
    
    def test_get_plugin_subscriptions(self):
        """Test getting plugin subscriptions."""
        # Register event handlers
        self.plugin_event_hooks.register_event_handler(
            "test_plugin",
            "test.event1",
            MagicMock()
        )
        
        self.plugin_event_hooks.register_event_handler(
            "test_plugin",
            "test.event2",
            MagicMock()
        )
        
        # Get subscriptions
        subscriptions = self.plugin_event_hooks.get_plugin_subscriptions("test_plugin")
        
        # Check subscriptions
        self.assertEqual(len(subscriptions), 2)
        self.assertIn("test.event1", subscriptions)
        self.assertIn("test.event2", subscriptions)


class TestPluginSecurity(unittest.TestCase):
    """Test cases for the PluginSecurityManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.security_manager = PluginSecurityManager()
    
    def test_plugin_permissions(self):
        """Test plugin permission management."""
        # Register plugin
        self.security_manager.register_plugin("test_plugin", {
            "permissions": ["file.read", "api.access"]
        })
        
        # Check permissions
        self.assertTrue(self.security_manager.has_permission(
            "test_plugin",
            self.security_manager.PluginPermission.FILE_READ
        ))
        
        self.assertTrue(self.security_manager.has_permission(
            "test_plugin",
            self.security_manager.PluginPermission.API_ACCESS
        ))
        
        self.assertFalse(self.security_manager.has_permission(
            "test_plugin",
            self.security_manager.PluginPermission.FILE_WRITE
        ))
        
        # Grant permission
        self.security_manager.grant_permission(
            "test_plugin",
            self.security_manager.PluginPermission.FILE_WRITE
        )
        
        # Check granted permission
        self.assertTrue(self.security_manager.has_permission(
            "test_plugin",
            self.security_manager.PluginPermission.FILE_WRITE
        ))
        
        # Revoke permission
        self.security_manager.revoke_permission(
            "test_plugin",
            self.security_manager.PluginPermission.FILE_READ
        )
        
        # Check revoked permission
        self.assertFalse(self.security_manager.has_permission(
            "test_plugin",
            self.security_manager.PluginPermission.FILE_READ
        ))
    
    def test_trusted_plugins(self):
        """Test trusted plugin handling."""
        # Register trusted plugin
        self.security_manager.register_plugin("trusted_plugin", {
            "trusted": True
        })
        
        # Register non-trusted plugin
        self.security_manager.register_plugin("regular_plugin", {})
        
        # Check trusted status
        self.assertTrue(self.security_manager.is_trusted("trusted_plugin"))
        self.assertFalse(self.security_manager.is_trusted("regular_plugin"))
        
        # Check permissions (trusted plugins should have all permissions)
        for permission in self.security_manager.PluginPermission:
            self.assertTrue(self.security_manager.has_permission("trusted_plugin", permission))
    
    def test_sandbox_creation(self):
        """Test sandbox creation and management."""
        # Register plugin
        self.security_manager.register_plugin("test_plugin", {})
        
        # Create sandbox
        sandbox_info = self.security_manager.create_sandbox("test_plugin")
        
        # Check sandbox info
        self.assertEqual(sandbox_info["id"], "test_plugin")
        self.assertTrue(os.path.exists(sandbox_info["directory"]))
        
        # Get sandbox
        retrieved_sandbox = self.security_manager.get_sandbox("test_plugin")
        
        # Check retrieved sandbox
        self.assertEqual(retrieved_sandbox["id"], "test_plugin")
        self.assertEqual(retrieved_sandbox["directory"], sandbox_info["directory"])
        
        # Destroy sandbox
        self.security_manager.destroy_sandbox("test_plugin")
        
        # Check if sandbox is destroyed
        self.assertNotIn("test_plugin", self.security_manager.plugin_sandboxes)
    
    def test_execute_in_sandbox(self):
        """Test executing code in a sandbox."""
        # Register plugin
        self.security_manager.register_plugin("test_plugin", {})
        
        # Define a test function
        def test_func(a, b):
            return a + b
        
        # Execute in sandbox
        result = self.security_manager.execute_in_sandbox(
            "test_plugin",
            test_func,
            5,
            10
        )
        
        # Check result
        self.assertEqual(result, 15)


class TestPluginIsolation(unittest.TestCase):
    """Test cases for the PluginIsolationManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.security_manager = PluginSecurityManager()
        self.isolation_manager = PluginIsolationManager(self.security_manager)
    
    def test_secure_proxy(self):
        """Test secure plugin proxy."""
        # Register plugin
        self.security_manager.register_plugin("test_plugin", {})
        
        # Create mock plugin instance
        mock_plugin = MagicMock()
        mock_plugin.test_method = MagicMock(return_value="test_result")
        
        # Create secure proxy
        proxy = self.isolation_manager.create_secure_proxy("test_plugin", mock_plugin)
        
        # Call method through proxy
        result = proxy.test_method()
        
        # Check result
        self.assertEqual(result, "test_result")
        mock_plugin.test_method.assert_called_once()
    
    def test_isolated_namespace(self):
        """Test isolated namespace creation."""
        # Register plugin
        self.security_manager.register_plugin("test_plugin", {})
        
        # Create isolated namespace
        namespace = self.isolation_manager.create_isolated_namespace("test_plugin")
        
        # Check namespace
        self.assertEqual(namespace["__name__"], "plugin_test_plugin")
        self.assertEqual(namespace["__plugin_id__"], "test_plugin")
        self.assertIn("__builtins__", namespace)
        
        # Check if unsafe builtins are removed
        unsafe_builtins = [
            "open",
            "exec",
            "eval",
            "compile",
            "__import__"
        ]
        
        for builtin in unsafe_builtins:
            self.assertNotIn(builtin, namespace["__builtins__"])


class TestPluginSystem(unittest.TestCase):
    """Test cases for the PluginSystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_dirs = [
            os.path.join(self.temp_dir, "plugins"),
            os.path.join(self.temp_dir, "more_plugins")
        ]
        
        for plugin_dir in self.plugin_dirs:
            os.makedirs(plugin_dir)
        
        self.event_manager = EventManager()
        self.plugin_system = PluginSystem(self.event_manager)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_plugin_system_initialization(self):
        """Test plugin system initialization."""
        # Check if components are initialized
        self.assertIsNotNone(self.plugin_system.plugin_registry)
        self.assertIsNotNone(self.plugin_system.plugin_loader)
        self.assertIsNotNone(self.plugin_system.plugin_discovery)
        self.assertIsNotNone(self.plugin_system.plugin_lifecycle)
        self.assertIsNotNone(self.plugin_system.plugin_api)
        self.assertIsNotNone(self.plugin_system.plugin_event_hooks)
        self.assertIsNotNone(self.plugin_system.security_manager)
        self.assertIsNotNone(self.plugin_system.isolation_manager)
    
    def test_plugin_system_integration(self):
        """Test plugin system integration with a simple plugin."""
        # Create a simple plugin
        plugin_dir = os.path.join(self.plugin_dirs[0], "test_plugin")
        os.makedirs(plugin_dir)
        
        with open(os.path.join(plugin_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(plugin_dir, "test_plugin.py"), "w") as f:
            f.write("""
class TestPlugin:
    def __init__(self, plugin_id, config):
        self.plugin_id = plugin_id
        self.config = config
        self.started = False
    
    def on_load(self):
        pass
    
    def on_start(self):
        self.started = True
    
    def on_stop(self):
        self.started = False
    
    def on_unload(self):
        pass
    
    def is_started(self):
        return self.started

PLUGIN_MANIFEST = {
    "name": "Test Plugin",
    "version": "1.0.0",
    "description": "A test plugin",
    "main_class": "TestPlugin"
}
""")
        
        # Create manifest file
        with open(os.path.join(plugin_dir, "manifest.json"), "w") as f:
            json.dump({
                "name": "Test Plugin",
                "version": "1.0.0",
                "description": "A test plugin",
                "main_class": "TestPlugin",
                "main_file": "test_plugin.py"
            }, f)
        
        # Initialize plugin system with plugin directories
        self.plugin_system.initialize(self.plugin_dirs)
        
        # Check if plugin is discovered and registered
        self.assertTrue(self.plugin_system.has_plugin("test_plugin"))
        
        # Start plugin
        self.plugin_system.start_plugin("test_plugin")
        
        # Check if plugin is started
        plugin = self.plugin_system.get_plugin("test_plugin")
        self.assertTrue(plugin.is_started())
        
        # Stop plugin
        self.plugin_system.stop_plugin("test_plugin")
        
        # Check if plugin is stopped
        self.assertFalse(plugin.is_started())
        
        # Unload plugin
        self.plugin_system.unload_plugin("test_plugin")
        
        # Check if plugin is unloaded
        self.assertEqual(
            self.plugin_system.plugin_lifecycle.get_plugin_state("test_plugin"),
            "UNLOADED"
        )


if __name__ == "__main__":
    unittest.main()
