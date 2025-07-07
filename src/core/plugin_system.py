"""
Plugin System Module for ApexAgent

This module integrates the plugin loader, registry, and discovery components
into a cohesive plugin system for the ApexAgent platform.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

from src.core.plugin_loader import PluginLoader, PluginRegistry
from src.core.plugin_discovery import PluginDiscovery, ManifestSchemaValidator
from src.core.plugin_exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginInitializationError,
    PluginConfigurationError
)

# Configure logging
logger = logging.getLogger(__name__)

class PluginSystem:
    """
    Main entry point for the ApexAgent plugin system.
    
    The PluginSystem integrates discovery, loading, and management of plugins
    into a cohesive interface for the rest of the application.
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None, schema_path: Optional[str] = None):
        """
        Initialize the plugin system.
        
        Args:
            plugin_dirs: List of directories to scan for plugins
            schema_path: Path to the JSON schema for validating plugin manifests
        """
        self.plugin_dirs = plugin_dirs or []
        
        # Initialize components
        self.registry = PluginRegistry()
        self.schema_validator = ManifestSchemaValidator(schema_path) if schema_path else None
        self.discovery = PluginDiscovery(self.schema_validator)
        self.loader = PluginLoader(self.registry)
        
        # Track loaded plugins
        self.loaded_plugins = set()
        
        logger.info("Plugin system initialized")
    
    def add_plugin_directory(self, plugin_dir: str) -> None:
        """
        Add a directory to scan for plugins.
        
        Args:
            plugin_dir: Directory path to add
        """
        if plugin_dir not in self.plugin_dirs:
            self.plugin_dirs.append(plugin_dir)
            logger.debug(f"Added plugin directory: {plugin_dir}")
    
    def discover_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover plugins in all configured directories.
        
        Returns:
            Dictionary mapping plugin IDs to plugin metadata
        """
        discovered = self.discovery.discover_plugins(self.plugin_dirs)
        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
    
    def load_plugin(self, plugin_id: str) -> Any:
        """
        Load a specific plugin by ID.
        
        Args:
            plugin_id: ID of the plugin to load
            
        Returns:
            Plugin instance
            
        Raises:
            PluginNotFoundError: If the plugin is not found
            PluginInitializationError: If the plugin fails to initialize
        """
        # Check if plugin is already loaded
        try:
            plugin = self.registry.get_plugin(plugin_id)
            return plugin
        except PluginNotFoundError:
            pass
        
        # Get plugin path from discovery
        try:
            plugin_path = self.discovery.get_plugin_path(plugin_id)
            manifest_path = os.path.join(plugin_path, 'manifest.json')
            
            # Try alternative manifest paths if the default doesn't exist
            if not os.path.exists(manifest_path):
                alt_paths = [
                    os.path.join(plugin_path, 'plugin.json'),
                    *[f for f in os.listdir(plugin_path) if f.endswith('.manifest.json')]
                ]
                
                for alt_path in alt_paths:
                    full_path = os.path.join(plugin_path, alt_path)
                    if os.path.exists(full_path):
                        manifest_path = full_path
                        break
            
            # Load the plugin
            result = self.loader.load_plugin_from_path(plugin_path, manifest_path)
            
            # Mark as loaded
            self.loaded_plugins.add(plugin_id)
            
            # Initialize the plugin
            plugin_instance = result['instance']
            if hasattr(plugin_instance, 'initialize') and callable(getattr(plugin_instance, 'initialize')):
                plugin_instance.initialize()
                self.registry.set_plugin_state(plugin_id, 'initialized')
            
            logger.info(f"Loaded and initialized plugin: {plugin_id}")
            return plugin_instance
            
        except Exception as e:
            if isinstance(e, (PluginNotFoundError, PluginInitializationError)):
                raise
            raise PluginInitializationError(f"Failed to load plugin {plugin_id}: {e}")
    
    def load_all_plugins(self) -> Dict[str, Any]:
        """
        Load all discovered plugins.
        
        Returns:
            Dictionary mapping plugin IDs to plugin instances
        """
        # Discover plugins if not already done
        if not self.discovery.discovered_plugins:
            self.discover_plugins()
        
        # Track successfully loaded plugins
        loaded = {}
        failed = {}
        
        # Load each plugin
        for plugin_id in self.discovery.get_all_plugin_ids():
            try:
                plugin = self.load_plugin(plugin_id)
                loaded[plugin_id] = plugin
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")
                failed[plugin_id] = str(e)
        
        if failed:
            logger.warning(f"Failed to load {len(failed)} plugins: {', '.join(failed.keys())}")
        
        logger.info(f"Successfully loaded {len(loaded)} plugins")
        return loaded
    
    def load_plugins_with_capability(self, capability: str) -> Dict[str, Any]:
        """
        Load all plugins with a specific capability.
        
        Args:
            capability: Capability to filter by
            
        Returns:
            Dictionary mapping plugin IDs to plugin instances
        """
        # Discover plugins if not already done
        if not self.discovery.discovered_plugins:
            self.discover_plugins()
        
        # Get plugins with the capability
        plugin_ids = self.discovery.get_plugins_by_capability(capability)
        
        # Load each plugin
        loaded = {}
        for plugin_id in plugin_ids:
            try:
                plugin = self.load_plugin(plugin_id)
                loaded[plugin_id] = plugin
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")
        
        logger.info(f"Loaded {len(loaded)} plugins with capability '{capability}'")
        return loaded
    
    def get_plugin(self, plugin_id: str) -> Any:
        """
        Get a plugin instance by ID.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin instance
            
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        try:
            return self.registry.get_plugin(plugin_id)
        except PluginNotFoundError:
            # Try to load the plugin if it's not in the registry
            return self.load_plugin(plugin_id)
    
    def get_plugin_metadata(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get metadata for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin metadata
            
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        try:
            return self.registry.get_metadata(plugin_id)
        except PluginNotFoundError:
            # Try to get metadata from discovery
            try:
                return self.discovery.get_plugin_metadata(plugin_id)
            except PluginError:
                raise PluginNotFoundError(f"Plugin {plugin_id} not found")
    
    def get_all_plugins(self) -> Dict[str, Any]:
        """
        Get all loaded plugin instances.
        
        Returns:
            Dictionary mapping plugin IDs to plugin instances
        """
        return self.registry.get_all_plugins()
    
    def get_all_plugin_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all discovered plugins.
        
        Returns:
            Dictionary mapping plugin IDs to plugin metadata
        """
        # Combine metadata from registry and discovery
        metadata = {}
        
        # Add metadata from registry
        metadata.update(self.registry.get_all_metadata())
        
        # Add metadata from discovery for plugins not in registry
        for plugin_id, plugin_metadata in self.discovery.discovered_plugins.items():
            if plugin_id not in metadata:
                metadata[plugin_id] = plugin_metadata
        
        return metadata
    
    def execute_plugin_action(self, plugin_id: str, action: str, *args, **kwargs) -> Any:
        """
        Execute an action on a plugin.
        
        Args:
            plugin_id: ID of the plugin
            action: Name of the action to execute
            *args: Positional arguments to pass to the action
            **kwargs: Keyword arguments to pass to the action
            
        Returns:
            Result of the action
            
        Raises:
            PluginNotFoundError: If the plugin is not found
            AttributeError: If the action is not found
        """
        # Get the plugin instance
        plugin = self.get_plugin(plugin_id)
        
        # Check if action exists
        if not hasattr(plugin, action) or not callable(getattr(plugin, action)):
            raise AttributeError(f"Action '{action}' not found in plugin '{plugin_id}'")
        
        # Execute the action
        action_method = getattr(plugin, action)
        return action_method(*args, **kwargs)
    
    def get_plugin_actions(self, plugin_id: str) -> List[str]:
        """
        Get a list of available actions for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            List of action names
            
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        # Get the plugin instance
        plugin = self.get_plugin(plugin_id)
        
        # Get actions from plugin
        if hasattr(plugin, 'get_actions') and callable(getattr(plugin, 'get_actions')):
            return plugin.get_actions()
        
        # Fall back to introspection
        actions = []
        for attr_name in dir(plugin):
            # Skip private methods and attributes
            if attr_name.startswith('_'):
                continue
            
            attr = getattr(plugin, attr_name)
            if callable(attr):
                actions.append(attr_name)
        
        return actions
    
    def reload_plugin(self, plugin_id: str) -> Any:
        """
        Reload a plugin.
        
        Args:
            plugin_id: ID of the plugin to reload
            
        Returns:
            Reloaded plugin instance
            
        Raises:
            PluginNotFoundError: If the plugin is not found
            PluginInitializationError: If the plugin fails to reload
        """
        # Check if plugin is loaded
        if plugin_id not in self.loaded_plugins:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not loaded")
        
        try:
            # Get plugin path
            plugin_path = self.discovery.get_plugin_path(plugin_id)
            
            # Unload the plugin
            self.unload_plugin(plugin_id)
            
            # Reload the plugin
            return self.load_plugin(plugin_id)
            
        except Exception as e:
            if isinstance(e, (PluginNotFoundError, PluginInitializationError)):
                raise
            raise PluginInitializationError(f"Failed to reload plugin {plugin_id}: {e}")
    
    def unload_plugin(self, plugin_id: str) -> None:
        """
        Unload a plugin.
        
        Args:
            plugin_id: ID of the plugin to unload
            
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        # Check if plugin is loaded
        if plugin_id not in self.loaded_plugins:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' is not loaded")
        
        try:
            # Get the plugin instance
            plugin = self.registry.get_plugin(plugin_id)
            
            # Call shutdown method if available
            if hasattr(plugin, 'shutdown') and callable(getattr(plugin, 'shutdown')):
                plugin.shutdown()
            
            # Unregister the plugin
            self.registry.unregister_plugin(plugin_id)
            
            # Remove from loaded plugins
            self.loaded_plugins.remove(plugin_id)
            
            logger.info(f"Unloaded plugin: {plugin_id}")
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}")
            raise
    
    def check_for_updates(self) -> Dict[str, bool]:
        """
        Check for updates to loaded plugins.
        
        Returns:
            Dictionary mapping plugin IDs to boolean indicating if an update is available
        """
        updates = {}
        
        for plugin_id in self.loaded_plugins:
            try:
                updates[plugin_id] = self.discovery.has_plugin_changed(plugin_id)
            except Exception as e:
                logger.warning(f"Error checking for updates to plugin {plugin_id}: {e}")
                updates[plugin_id] = False
        
        return updates
    
    def shutdown(self) -> None:
        """
        Shutdown the plugin system and all loaded plugins.
        """
        # Get a copy of loaded plugins to avoid modification during iteration
        loaded_plugins = list(self.loaded_plugins)
        
        # Unload each plugin
        for plugin_id in loaded_plugins:
            try:
                self.unload_plugin(plugin_id)
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin_id}: {e}")
        
        logger.info("Plugin system shutdown complete")
