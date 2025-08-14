"""
Plugin Lifecycle Management Module for ApexAgent

This module provides functionality for managing the lifecycle of plugins in the ApexAgent system.
It handles plugin state transitions, dependency management, and lifecycle events.
"""

import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple, Callable

from src.core.plugin_exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginStateError,
    PluginDependencyError
)

# Configure logging
logger = logging.getLogger(__name__)

class PluginState(Enum):
    """Enum representing the possible states of a plugin."""
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    UNLOADED = "unloaded"


class PluginLifecycleManager:
    """
    Manages the lifecycle of plugins in the ApexAgent system.
    
    The PluginLifecycleManager is responsible for:
    1. Managing plugin state transitions
    2. Handling plugin dependencies during lifecycle operations
    3. Executing lifecycle hooks
    4. Providing lifecycle event notifications
    """
    
    def __init__(self, plugin_registry, plugin_discovery):
        """
        Initialize the PluginLifecycleManager.
        
        Args:
            plugin_registry: Registry for accessing plugin instances
            plugin_discovery: Discovery system for plugin metadata
        """
        self.registry = plugin_registry
        self.discovery = plugin_discovery
        self.plugin_states = {}  # Maps plugin_id to PluginState
        self.lifecycle_hooks = {
            "pre_start": {},
            "post_start": {},
            "pre_stop": {},
            "post_stop": {},
            "pre_reload": {},
            "post_reload": {}
        }
    
    def register_lifecycle_hook(self, hook_type: str, plugin_id: str, hook_fn: Callable) -> None:
        """
        Register a lifecycle hook for a plugin.
        
        Args:
            hook_type: Type of hook (pre_start, post_start, etc.)
            plugin_id: ID of the plugin
            hook_fn: Function to call when the hook is triggered
            
        Raises:
            ValueError: If the hook type is invalid
        """
        if hook_type not in self.lifecycle_hooks:
            raise ValueError(f"Invalid hook type: {hook_type}")
        
        if plugin_id not in self.lifecycle_hooks[hook_type]:
            self.lifecycle_hooks[hook_type][plugin_id] = []
        
        self.lifecycle_hooks[hook_type][plugin_id].append(hook_fn)
        logger.debug(f"Registered {hook_type} hook for plugin {plugin_id}")
    
    def _execute_hooks(self, hook_type: str, plugin_id: str, **kwargs) -> None:
        """
        Execute all hooks of a specific type for a plugin.
        
        Args:
            hook_type: Type of hook to execute
            plugin_id: ID of the plugin
            **kwargs: Additional arguments to pass to the hook functions
        """
        if hook_type not in self.lifecycle_hooks:
            return
        
        if plugin_id not in self.lifecycle_hooks[hook_type]:
            return
        
        for hook_fn in self.lifecycle_hooks[hook_type][plugin_id]:
            try:
                hook_fn(plugin_id=plugin_id, **kwargs)
            except Exception as e:
                logger.error(f"Error executing {hook_type} hook for plugin {plugin_id}: {e}")
    
    def get_plugin_state(self, plugin_id: str) -> PluginState:
        """
        Get the current state of a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Current state of the plugin
            
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_states:
            # Check if plugin exists in registry or discovery
            try:
                self.registry.get_plugin(plugin_id)
                self.plugin_states[plugin_id] = PluginState.REGISTERED
            except PluginNotFoundError:
                try:
                    self.discovery.get_plugin_metadata(plugin_id)
                    self.plugin_states[plugin_id] = PluginState.DISCOVERED
                except Exception:
                    raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        return self.plugin_states[plugin_id]
    
    def set_plugin_state(self, plugin_id: str, state: PluginState) -> None:
        """
        Set the state of a plugin.
        
        Args:
            plugin_id: ID of the plugin
            state: New state for the plugin
            
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        # Verify plugin exists
        try:
            self.registry.get_plugin(plugin_id)
        except PluginNotFoundError:
            try:
                self.discovery.get_plugin_metadata(plugin_id)
            except Exception:
                raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Update state
        old_state = self.plugin_states.get(plugin_id)
        self.plugin_states[plugin_id] = state
        
        logger.info(f"Plugin {plugin_id} state changed: {old_state} -> {state}")
    
    def start_plugin(self, plugin_id: str, force: bool = False) -> None:
        """
        Start a plugin.
        
        Args:
            plugin_id: ID of the plugin to start
            force: If True, start even if dependencies are not satisfied
            
        Raises:
            PluginNotFoundError: If the plugin is not found
            PluginStateError: If the plugin is in an invalid state
            PluginDependencyError: If plugin dependencies are not satisfied
        """
        # Check if plugin exists
        try:
            plugin = self.registry.get_plugin(plugin_id)
        except PluginNotFoundError:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found or not loaded")
        
        # Check current state
        current_state = self.get_plugin_state(plugin_id)
        if current_state == PluginState.ACTIVE:
            logger.debug(f"Plugin {plugin_id} is already active")
            return
        
        if current_state not in [PluginState.REGISTERED, PluginState.INITIALIZED, PluginState.INACTIVE]:
            raise PluginStateError(
                f"Cannot start plugin {plugin_id} in state {current_state}"
            )
        
        # Check dependencies if not forcing
        if not force:
            self._check_start_dependencies(plugin_id)
        
        try:
            # Execute pre-start hooks
            self._execute_hooks("pre_start", plugin_id)
            
            # Call start method if available
            if hasattr(plugin, 'start') and callable(getattr(plugin, 'start')):
                plugin.start()
            
            # Update state
            self.set_plugin_state(plugin_id, PluginState.ACTIVE)
            
            # Execute post-start hooks
            self._execute_hooks("post_start", plugin_id)
            
            logger.info(f"Started plugin: {plugin_id}")
            
        except Exception as e:
            self.set_plugin_state(plugin_id, PluginState.FAILED)
            logger.error(f"Failed to start plugin {plugin_id}: {e}")
            raise PluginStateError(f"Failed to start plugin {plugin_id}: {e}")
    
    def stop_plugin(self, plugin_id: str, force: bool = False) -> None:
        """
        Stop a plugin.
        
        Args:
            plugin_id: ID of the plugin to stop
            force: If True, stop even if dependent plugins are active
            
        Raises:
            PluginNotFoundError: If the plugin is not found
            PluginStateError: If the plugin is in an invalid state
            PluginDependencyError: If other plugins depend on this plugin
        """
        # Check if plugin exists
        try:
            plugin = self.registry.get_plugin(plugin_id)
        except PluginNotFoundError:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found or not loaded")
        
        # Check current state
        current_state = self.get_plugin_state(plugin_id)
        if current_state == PluginState.INACTIVE:
            logger.debug(f"Plugin {plugin_id} is already inactive")
            return
        
        if current_state != PluginState.ACTIVE:
            raise PluginStateError(
                f"Cannot stop plugin {plugin_id} in state {current_state}"
            )
        
        # Check for dependent plugins if not forcing
        if not force:
            self._check_stop_dependencies(plugin_id)
        
        try:
            # Execute pre-stop hooks
            self._execute_hooks("pre_stop", plugin_id)
            
            # Call stop method if available
            if hasattr(plugin, 'stop') and callable(getattr(plugin, 'stop')):
                plugin.stop()
            
            # Update state
            self.set_plugin_state(plugin_id, PluginState.INACTIVE)
            
            # Execute post-stop hooks
            self._execute_hooks("post_stop", plugin_id)
            
            logger.info(f"Stopped plugin: {plugin_id}")
            
        except Exception as e:
            self.set_plugin_state(plugin_id, PluginState.FAILED)
            logger.error(f"Failed to stop plugin {plugin_id}: {e}")
            raise PluginStateError(f"Failed to stop plugin {plugin_id}: {e}")
    
    def reload_plugin(self, plugin_id: str, force: bool = False) -> None:
        """
        Reload a plugin.
        
        Args:
            plugin_id: ID of the plugin to reload
            force: If True, reload even if dependencies are not satisfied
            
        Raises:
            PluginNotFoundError: If the plugin is not found
            PluginStateError: If the plugin is in an invalid state
            PluginDependencyError: If plugin dependencies are not satisfied
        """
        # Check if plugin exists
        try:
            plugin = self.registry.get_plugin(plugin_id)
        except PluginNotFoundError:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found or not loaded")
        
        # Check current state
        current_state = self.get_plugin_state(plugin_id)
        was_active = (current_state == PluginState.ACTIVE)
        
        try:
            # Execute pre-reload hooks
            self._execute_hooks("pre_reload", plugin_id)
            
            # Stop the plugin if it's active
            if was_active:
                self.stop_plugin(plugin_id, force=force)
            
            # Call reload method if available
            if hasattr(plugin, 'reload') and callable(getattr(plugin, 'reload')):
                plugin.reload()
            
            # Update state
            self.set_plugin_state(plugin_id, PluginState.INITIALIZED)
            
            # Restart the plugin if it was active
            if was_active:
                self.start_plugin(plugin_id, force=force)
            
            # Execute post-reload hooks
            self._execute_hooks("post_reload", plugin_id)
            
            logger.info(f"Reloaded plugin: {plugin_id}")
            
        except Exception as e:
            self.set_plugin_state(plugin_id, PluginState.FAILED)
            logger.error(f"Failed to reload plugin {plugin_id}: {e}")
            raise PluginStateError(f"Failed to reload plugin {plugin_id}: {e}")
    
    def _check_start_dependencies(self, plugin_id: str) -> None:
        """
        Check if all dependencies are satisfied before starting a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Raises:
            PluginDependencyError: If dependencies are not satisfied
        """
        # Get plugin metadata
        try:
            metadata = self.registry.get_metadata(plugin_id)
        except PluginNotFoundError:
            try:
                metadata = self.discovery.get_plugin_metadata(plugin_id)
            except Exception:
                raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Check plugin dependencies
        dependencies = metadata.get('dependencies', {}).get('plugins', {})
        unsatisfied = []
        
        for dep_id in dependencies:
            try:
                dep_state = self.get_plugin_state(dep_id)
                if dep_state != PluginState.ACTIVE:
                    unsatisfied.append(dep_id)
            except PluginNotFoundError:
                unsatisfied.append(dep_id)
        
        if unsatisfied:
            raise PluginDependencyError(
                f"Cannot start plugin {plugin_id}: unsatisfied dependencies: {', '.join(unsatisfied)}"
            )
    
    def _check_stop_dependencies(self, plugin_id: str) -> None:
        """
        Check if any active plugins depend on this plugin before stopping it.
        
        Args:
            plugin_id: ID of the plugin
            
        Raises:
            PluginDependencyError: If other plugins depend on this plugin
        """
        dependent_plugins = []
        
        # Check all active plugins
        for pid, state in self.plugin_states.items():
            if pid == plugin_id or state != PluginState.ACTIVE:
                continue
            
            try:
                metadata = self.registry.get_metadata(pid)
                dependencies = metadata.get('dependencies', {}).get('plugins', {})
                
                if plugin_id in dependencies:
                    dependent_plugins.append(pid)
            except Exception:
                continue
        
        if dependent_plugins:
            raise PluginDependencyError(
                f"Cannot stop plugin {plugin_id}: active plugins depend on it: {', '.join(dependent_plugins)}"
            )
    
    def start_all_plugins(self, ignore_failures: bool = False) -> Dict[str, Any]:
        """
        Start all registered plugins.
        
        Args:
            ignore_failures: If True, continue starting plugins even if some fail
            
        Returns:
            Dictionary with 'success' and 'failed' lists
        """
        success = []
        failed = {}
        
        # Get all registered plugins
        plugins = self.registry.get_all_plugins()
        
        # Start each plugin
        for plugin_id in plugins:
            try:
                self.start_plugin(plugin_id)
                success.append(plugin_id)
            except Exception as e:
                failed[plugin_id] = str(e)
                if not ignore_failures:
                    break
        
        return {
            'success': success,
            'failed': failed
        }
    
    def stop_all_plugins(self, ignore_failures: bool = False) -> Dict[str, Any]:
        """
        Stop all active plugins.
        
        Args:
            ignore_failures: If True, continue stopping plugins even if some fail
            
        Returns:
            Dictionary with 'success' and 'failed' lists
        """
        success = []
        failed = {}
        
        # Get all active plugins
        active_plugins = [
            pid for pid, state in self.plugin_states.items()
            if state == PluginState.ACTIVE
        ]
        
        # Stop each plugin
        for plugin_id in active_plugins:
            try:
                self.stop_plugin(plugin_id, force=True)
                success.append(plugin_id)
            except Exception as e:
                failed[plugin_id] = str(e)
                if not ignore_failures:
                    break
        
        return {
            'success': success,
            'failed': failed
        }
    
    def get_plugin_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get a dependency graph of all plugins.
        
        Returns:
            Dictionary mapping plugin IDs to lists of dependency plugin IDs
        """
        dependency_graph = {}
        
        # Get all plugins
        all_plugins = set(self.registry.get_all_plugins().keys())
        all_plugins.update(self.discovery.get_all_plugin_ids())
        
        # Build dependency graph
        for plugin_id in all_plugins:
            try:
                # Try to get metadata from registry first
                try:
                    metadata = self.registry.get_metadata(plugin_id)
                except PluginNotFoundError:
                    metadata = self.discovery.get_plugin_metadata(plugin_id)
                
                dependencies = metadata.get('dependencies', {}).get('plugins', {})
                dependency_graph[plugin_id] = list(dependencies.keys())
            except Exception:
                dependency_graph[plugin_id] = []
        
        return dependency_graph
    
    def get_plugin_dependents(self, plugin_id: str) -> List[str]:
        """
        Get a list of plugins that depend on a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            List of plugin IDs that depend on the specified plugin
        """
        dependents = []
        
        # Get dependency graph
        dependency_graph = self.get_plugin_dependency_graph()
        
        # Find plugins that depend on the specified plugin
        for pid, deps in dependency_graph.items():
            if plugin_id in deps:
                dependents.append(pid)
        
        return dependents
    
    def get_plugin_startup_order(self) -> List[str]:
        """
        Get the correct order to start plugins based on dependencies.
        
        Returns:
            List of plugin IDs in the order they should be started
        """
        # Get dependency graph
        dependency_graph = self.get_plugin_dependency_graph()
        
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(plugin_id):
            if plugin_id in temp_visited:
                # Cyclic dependency detected
                return
            
            if plugin_id in visited:
                return
            
            temp_visited.add(plugin_id)
            
            # Visit dependencies first
            for dep_id in dependency_graph.get(plugin_id, []):
                visit(dep_id)
            
            temp_visited.remove(plugin_id)
            visited.add(plugin_id)
            order.append(plugin_id)
        
        # Visit all plugins
        for plugin_id in dependency_graph:
            if plugin_id not in visited:
                visit(plugin_id)
        
        # Reverse to get correct order
        return list(reversed(order))
    
    def get_plugin_shutdown_order(self) -> List[str]:
        """
        Get the correct order to stop plugins based on dependencies.
        
        Returns:
            List of plugin IDs in the order they should be stopped
        """
        # Get startup order and reverse it
        return list(reversed(self.get_plugin_startup_order()))
    
    def start_plugins_in_order(self, ignore_failures: bool = False) -> Dict[str, Any]:
        """
        Start plugins in the correct dependency order.
        
        Args:
            ignore_failures: If True, continue starting plugins even if some fail
            
        Returns:
            Dictionary with 'success' and 'failed' lists
        """
        success = []
        failed = {}
        
        # Get startup order
        startup_order = self.get_plugin_startup_order()
        
        # Start each plugin in order
        for plugin_id in startup_order:
            try:
                # Skip plugins that are not registered
                if plugin_id not in self.registry.get_all_plugins():
                    continue
                
                self.start_plugin(plugin_id)
                success.append(plugin_id)
            except Exception as e:
                failed[plugin_id] = str(e)
                if not ignore_failures:
                    break
        
        return {
            'success': success,
            'failed': failed
        }
    
    def stop_plugins_in_order(self, ignore_failures: bool = False) -> Dict[str, Any]:
        """
        Stop plugins in the correct dependency order.
        
        Args:
            ignore_failures: If True, continue stopping plugins even if some fail
            
        Returns:
            Dictionary with 'success' and 'failed' lists
        """
        success = []
        failed = {}
        
        # Get shutdown order
        shutdown_order = self.get_plugin_shutdown_order()
        
        # Stop each plugin in order
        for plugin_id in shutdown_order:
            try:
                # Skip plugins that are not active
                if self.get_plugin_state(plugin_id) != PluginState.ACTIVE:
                    continue
                
                self.stop_plugin(plugin_id, force=True)
                success.append(plugin_id)
            except Exception as e:
                failed[plugin_id] = str(e)
                if not ignore_failures:
                    break
        
        return {
            'success': success,
            'failed': failed
        }
