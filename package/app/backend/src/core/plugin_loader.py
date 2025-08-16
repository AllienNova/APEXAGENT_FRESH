"""
Plugin Loader Module for ApexAgent

This module provides functionality for loading and registering plugins in the ApexAgent system.
It handles dynamic loading of plugin modules, class instantiation, and plugin registration.
"""

import os
import sys
import json
import importlib
import importlib.util
import inspect
import logging
from typing import Dict, Any, Optional, List, Tuple, Type, Union

from src.core.plugin_exceptions import (
    PluginError,
    PluginInitializationError,
    PluginNotFoundError,
    PluginConfigurationError
)

# Configure logging
logger = logging.getLogger(__name__)

class PluginLoader:
    """
    Handles the loading and registration of plugins.
    
    The PluginLoader is responsible for:
    1. Loading plugin modules dynamically
    2. Instantiating plugin classes
    3. Validating plugin interfaces
    4. Registering plugins with the plugin registry
    """
    
    def __init__(self, plugin_registry):
        """
        Initialize the PluginLoader.
        
        Args:
            plugin_registry: The registry where plugins will be registered
        """
        self.plugin_registry = plugin_registry
        self.loaded_modules = {}
    
    def load_plugin_from_path(self, plugin_path: str, manifest_path: str) -> Dict[str, Any]:
        """
        Load a plugin from a specified path using its manifest file.
        
        Args:
            plugin_path: Path to the plugin directory
            manifest_path: Path to the plugin manifest file
            
        Returns:
            Dictionary containing the loaded plugin instance and metadata
            
        Raises:
            PluginConfigurationError: If the manifest is invalid
            PluginInitializationError: If the plugin fails to initialize
            PluginNotFoundError: If the plugin module or class cannot be found
        """
        try:
            # Load and validate manifest
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Validate required fields
            required_fields = ['id', 'name', 'version', 'description', 'main_module', 'class_name']
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                raise PluginConfigurationError(
                    f"Plugin manifest missing required fields: {', '.join(missing_fields)}"
                )
            
            # Extract plugin information
            plugin_id = manifest['id']
            plugin_name = manifest['name']
            version = manifest['version']
            description = manifest['description']
            main_module = manifest['main_module']
            class_name = manifest['class_name']
            
            # Load the plugin module
            plugin_module = self._load_module(plugin_path, main_module)
            
            # Get the plugin class
            if not hasattr(plugin_module, class_name):
                raise PluginNotFoundError(
                    f"Plugin class '{class_name}' not found in module '{main_module}'"
                )
            
            plugin_class = getattr(plugin_module, class_name)
            
            # Create plugin instance
            plugin_instance = self._instantiate_plugin(
                plugin_class,
                plugin_id,
                plugin_name,
                version,
                description,
                manifest.get('config', {})
            )
            
            # Register the plugin
            self.plugin_registry.register_plugin(plugin_id, plugin_instance, manifest)
            
            return {
                'id': plugin_id,
                'instance': plugin_instance,
                'metadata': manifest,
                'module': plugin_module
            }
            
        except json.JSONDecodeError as e:
            raise PluginConfigurationError(f"Invalid plugin manifest: {e}")
        except Exception as e:
            if isinstance(e, (PluginConfigurationError, PluginInitializationError, PluginNotFoundError)):
                raise
            raise PluginInitializationError(f"Failed to load plugin: {e}")
    
    def _load_module(self, plugin_path: str, module_name: str) -> Any:
        """
        Load a Python module dynamically.
        
        Args:
            plugin_path: Path to the plugin directory
            module_name: Name of the module to load
            
        Returns:
            Loaded module object
            
        Raises:
            PluginNotFoundError: If the module file cannot be found
            ImportError: If the module cannot be imported
        """
        # Check if module has already been loaded
        cache_key = f"{plugin_path}:{module_name}"
        if cache_key in self.loaded_modules:
            return self.loaded_modules[cache_key]
        
        # Handle both .py and module name formats
        if module_name.endswith('.py'):
            module_file = module_name
            module_name = os.path.splitext(module_name)[0]
        else:
            module_file = f"{module_name}.py"
        
        # Check if module file exists
        module_path = os.path.join(plugin_path, module_file)
        if not os.path.exists(module_path):
            raise PluginNotFoundError(f"Plugin module file not found: {module_path}")
        
        # Add plugin directory to sys.path temporarily
        original_sys_path = sys.path.copy()
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)
        
        try:
            # Try to import using importlib.util for better control
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None:
                raise ImportError(f"Failed to create module spec for {module_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Cache the loaded module
            self.loaded_modules[cache_key] = module
            
            return module
            
        except Exception as e:
            if module_name in sys.modules:
                del sys.modules[module_name]
            raise ImportError(f"Failed to import plugin module: {e}")
        
        finally:
            # Restore original sys.path
            sys.path = original_sys_path
    
    def _instantiate_plugin(
        self,
        plugin_class: Type,
        plugin_id: str,
        plugin_name: str,
        version: str,
        description: str,
        config: Dict[str, Any]
    ) -> Any:
        """
        Instantiate a plugin class.
        
        Args:
            plugin_class: The plugin class to instantiate
            plugin_id: ID of the plugin
            plugin_name: Name of the plugin
            version: Version of the plugin
            description: Description of the plugin
            config: Configuration for the plugin
            
        Returns:
            Instantiated plugin object
            
        Raises:
            PluginInitializationError: If the plugin fails to initialize
        """
        try:
            # Check constructor signature to determine how to instantiate
            sig = inspect.signature(plugin_class.__init__)
            params = sig.parameters
            
            # Prepare kwargs based on available parameters
            kwargs = {}
            if 'plugin_id' in params:
                kwargs['plugin_id'] = plugin_id
            if 'plugin_name' in params:
                kwargs['plugin_name'] = plugin_name
            if 'version' in params:
                kwargs['version'] = version
            if 'description' in params:
                kwargs['description'] = description
            if 'config' in params:
                kwargs['config'] = config
            
            # Instantiate the plugin
            plugin_instance = plugin_class(**kwargs)
            
            # Validate plugin interface
            self._validate_plugin_interface(plugin_instance)
            
            return plugin_instance
            
        except Exception as e:
            raise PluginInitializationError(f"Failed to instantiate plugin {plugin_id}: {e}")
    
    def _validate_plugin_interface(self, plugin_instance: Any) -> None:
        """
        Validate that a plugin instance implements the required interface.
        
        Args:
            plugin_instance: The plugin instance to validate
            
        Raises:
            PluginInitializationError: If the plugin does not implement the required interface
        """
        # Required methods for all plugins
        required_methods = [
            'initialize',
            'get_metadata',
            'get_actions',
            'execute_action',
            'shutdown'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(plugin_instance, method) or not callable(getattr(plugin_instance, method)):
                missing_methods.append(method)
        
        if missing_methods:
            raise PluginInitializationError(
                f"Plugin does not implement required methods: {', '.join(missing_methods)}"
            )
    
    # Adding missing methods required by tests
    
    def load_plugin(self, plugin_dir: str, plugin_id: str, config: Dict[str, Any] = None) -> Any:
        """
        Load a plugin from a directory.
        
        Args:
            plugin_dir: Path to the plugin directory
            plugin_id: ID to assign to the plugin
            config: Optional configuration for the plugin
            
        Returns:
            Instantiated plugin object
            
        Raises:
            PluginNotFoundError: If the plugin cannot be found
            PluginInitializationError: If the plugin fails to initialize
        """
        # Look for manifest file
        manifest_path = os.path.join(plugin_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            raise PluginNotFoundError(f"Plugin manifest not found at {manifest_path}")
        
        # Load plugin from manifest
        plugin_data = self.load_plugin_from_path(plugin_dir, manifest_path)
        
        # Update config if provided
        if config:
            plugin_instance = plugin_data['instance']
            if hasattr(plugin_instance, 'update_config') and callable(getattr(plugin_instance, 'update_config')):
                plugin_instance.update_config(config)
        
        return plugin_data['instance']
    
    def _load_plugin_module(self, plugin_dir: str, plugin_id: str) -> Any:
        """
        Load a plugin module from a directory.
        
        Args:
            plugin_dir: Path to the plugin directory
            plugin_id: ID of the plugin
            
        Returns:
            Loaded module object
            
        Raises:
            PluginNotFoundError: If the plugin module cannot be found
        """
        # Look for main module file
        module_path = None
        for file_name in os.listdir(plugin_dir):
            if file_name.endswith('.py'):
                # Check if this is the main module
                module_path = os.path.join(plugin_dir, file_name)
                break
        
        if not module_path:
            raise PluginNotFoundError(f"No Python module found in plugin directory: {plugin_dir}")
        
        # Load the module
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        return self._load_module(plugin_dir, module_name)
    
    def _load_plugin_class(self, module: Any, class_name: str) -> Type:
        """
        Load a plugin class from a module.
        
        Args:
            module: Module object containing the plugin class
            class_name: Name of the plugin class
            
        Returns:
            Plugin class
            
        Raises:
            PluginNotFoundError: If the plugin class cannot be found
        """
        if not hasattr(module, class_name):
            raise PluginNotFoundError(f"Plugin class '{class_name}' not found in module")
        
        plugin_class = getattr(module, class_name)
        
        # Verify that it's a class
        if not inspect.isclass(plugin_class):
            raise PluginNotFoundError(f"'{class_name}' is not a class")
        
        return plugin_class


class PluginRegistry:
    """
    Registry for managing plugin registrations.
    
    The PluginRegistry is responsible for:
    1. Storing plugin instances and metadata
    2. Providing access to registered plugins
    3. Managing plugin lifecycle state
    """
    
    def __init__(self):
        """Initialize the PluginRegistry."""
        self.plugins = {}  # Stores plugin instances by ID
        self.metadata = {}  # Stores plugin metadata by ID
        self.plugin_states = {}  # Stores plugin lifecycle states
    
    def register_plugin(self, plugin_id: str, plugin_instance: Any, metadata: Dict[str, Any] = None) -> None:
        """
        Register a plugin with the registry.
        
        Args:
            plugin_id: ID of the plugin
            plugin_instance: Instance of the plugin
            metadata: Metadata for the plugin (optional for test compatibility)
            
        Raises:
            PluginError: If a plugin with the same ID is already registered
        """
        if plugin_id in self.plugins:
            raise PluginError(f"Plugin with ID '{plugin_id}' is already registered")
        
        self.plugins[plugin_id] = plugin_instance
        
        # Use provided metadata or create a minimal default
        if metadata is None:
            metadata = {
                "id": plugin_id,
                "name": getattr(plugin_instance, "name", plugin_id),
                "version": getattr(plugin_instance, "version", "0.0.0"),
                "description": getattr(plugin_instance, "description", "No description provided")
            }
        
        self.metadata[plugin_id] = metadata
        self.plugin_states[plugin_id] = 'registered'
        
        logger.info(f"Registered plugin: {plugin_id} (version {metadata.get('version', 'unknown')})")
    
    def unregister_plugin(self, plugin_id: str) -> None:
        """
        Unregister a plugin from the registry.
        
        Args:
            plugin_id: ID of the plugin to unregister
            
        Raises:
            PluginNotFoundError: If the plugin is not registered
        """
        if plugin_id not in self.plugins:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not registered")
        
        # Remove plugin from registry
        del self.plugins[plugin_id]
        del self.metadata[plugin_id]
        del self.plugin_states[plugin_id]
        
        logger.info(f"Unregistered plugin: {plugin_id}")
    
    def get_plugin(self, plugin_id: str) -> Any:
        """
        Get a plugin instance by ID.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin instance
            
        Raises:
            PluginNotFoundError: If the plugin is not registered
        """
        if plugin_id not in self.plugins:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not registered")
        
        return self.plugins[plugin_id]
    
    def get_metadata(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get metadata for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin metadata
            
        Raises:
            PluginNotFoundError: If the plugin is not registered
        """
        if plugin_id not in self.metadata:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not registered")
        
        return self.metadata[plugin_id]
    
    def get_plugin_state(self, plugin_id: str) -> str:
        """
        Get the current state of a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Current state of the plugin
            
        Raises:
            PluginNotFoundError: If the plugin is not registered
        """
        if plugin_id not in self.plugin_states:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not registered")
        
        return self.plugin_states[plugin_id]
    
    def set_plugin_state(self, plugin_id: str, state: str) -> None:
        """
        Set the state of a plugin.
        
        Args:
            plugin_id: ID of the plugin
            state: New state for the plugin
            
        Raises:
            PluginNotFoundError: If the plugin is not registered
        """
        if plugin_id not in self.plugin_states:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not registered")
        
        self.plugin_states[plugin_id] = state
        logger.debug(f"Plugin '{plugin_id}' state changed to '{state}'")
    
    def get_all_plugins(self) -> Dict[str, Any]:
        """
        Get all registered plugins.
        
        Returns:
            Dictionary mapping plugin IDs to plugin instances
        """
        return self.plugins.copy()
    
    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all registered plugins.
        
        Returns:
            Dictionary mapping plugin IDs to plugin metadata
        """
        return self.metadata.copy()
    
    def get_all_plugin_states(self) -> Dict[str, str]:
        """
        Get states for all registered plugins.
        
        Returns:
            Dictionary mapping plugin IDs to plugin states
        """
        return self.plugin_states.copy()
    
    def get_plugins_by_state(self, state: str) -> Dict[str, Any]:
        """
        Get all plugins in a specific state.
        
        Args:
            state: State to filter by
            
        Returns:
            Dictionary mapping plugin IDs to plugin instances
        """
        result = {}
        for plugin_id, plugin_state in self.plugin_states.items():
            if plugin_state == state:
                result[plugin_id] = self.plugins[plugin_id]
        return result
