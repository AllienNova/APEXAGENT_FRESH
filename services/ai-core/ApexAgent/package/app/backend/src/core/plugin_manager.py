import os
import json
import hashlib
import importlib
import logging
import sys
import inspect
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from packaging.version import Version
import packaging.version
from packaging.specifiers import SpecifierSet
import jsonschema

# Import exceptions from plugin_exceptions.py to ensure consistent module identity
from core.plugin_exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginDependencyError,
    PluginMissingDependencyError,
    PluginIncompatibleDependencyError,
    PluginInvalidDependencySpecificationError,
    PluginCircularDependencyError
)

# Configure logging
logger = logging.getLogger(__name__)

class PluginManager:
    """
    Manages the discovery, loading, and lifecycle of plugins.
    
    The PluginManager is responsible for:
    1. Discovering plugins in the specified directory
    2. Validating plugin metadata
    3. Loading and initializing plugins
    4. Managing plugin state and configuration
    5. Handling plugin dependencies
    6. Providing access to plugin functionality
    """
    
    def __init__(self, plugin_dir: str, schema_path: Optional[str] = None):
        """
        Initialize the PluginManager.
        
        Args:
            plugin_dir: Directory containing plugins
            schema_path: Path to the JSON schema for plugin metadata validation
        """
        self.plugin_dir = os.path.abspath(plugin_dir)
        self.plugins = {}  # Stores loaded plugin instances
        self.plugin_metadata = {}  # Stores plugin metadata
        self.plugin_paths = {}  # Stores paths to plugin directories
        self.plugin_modules = {}  # Stores loaded plugin modules
        self.plugin_enabled = {}  # Stores enabled/disabled state of plugins
        self.plugin_dependencies = {}  # Stores plugin dependencies
        self.streaming_actions = {}  # Stores streaming-capable actions metadata
        
        # Load schema for plugin metadata validation
        if schema_path:
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)
        else:
            schema_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
            schema_path = os.path.join(schema_dir, 'plugin_metadata_schema.json')
            try:
                with open(schema_path, 'r') as f:
                    self.schema = json.load(f)
            except FileNotFoundError:
                logger.warning(f"Plugin metadata schema not found at {schema_path}. Schema validation will be skipped.")
                self.schema = None
    
    def discover_plugins(self) -> int:
        """
        Discover plugins in the plugin directory.
        
        Returns:
            Number of plugins discovered
        """
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory {self.plugin_dir} does not exist.")
            return 0
        
        # Reset plugin metadata and paths
        self.plugin_metadata = {}
        self.plugin_paths = {}
        self.plugin_dependencies = {}
        self.streaming_actions = {}
        
        count = 0
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            if not os.path.isdir(plugin_path):
                continue
            
            metadata_path = os.path.join(plugin_path, 'plugin.json')
            if not os.path.exists(metadata_path):
                continue
            
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Validate metadata against schema
                if self.schema:
                    try:
                        jsonschema.validate(instance=metadata, schema=self.schema)
                    except jsonschema.exceptions.ValidationError as e:
                        logger.warning(f"Plugin metadata validation failed for {item}: {e}")
                        continue
                
                # Check required fields
                required_fields = ['id', 'name', 'version', 'description', 'main_file', 'main_class']
                if not all(field in metadata for field in required_fields):
                    logger.warning(f"Plugin metadata missing required fields for {item}")
                    continue
                
                # Store plugin metadata and path
                plugin_id = metadata['id']
                self.plugin_metadata[plugin_id] = metadata
                self.plugin_paths[plugin_id] = plugin_path
                
                # Store plugin dependencies if present
                if 'dependencies' in metadata:
                    self.plugin_dependencies[plugin_id] = metadata['dependencies']
                
                # Store streaming actions metadata if present
                if 'actions' in metadata:
                    streaming_actions = {}
                    for action_id, action_metadata in metadata['actions'].items():
                        if 'streaming' in action_metadata and action_metadata['streaming']:
                            streaming_actions[action_id] = action_metadata.get('stream_metadata', {})
                    
                    if streaming_actions:
                        self.streaming_actions[plugin_id] = streaming_actions
                
                # Set plugin as enabled by default
                self.plugin_enabled[plugin_id] = True
                
                count += 1
                logger.info(f"Discovered plugin: {plugin_id} (version {metadata['version']})")
            
            except Exception as e:
                logger.warning(f"Error loading plugin metadata from {metadata_path}: {e}")
        
        return count
    
    def get_plugin_ids(self) -> List[str]:
        """
        Get a list of all discovered plugin IDs.
        
        Returns:
            List of plugin IDs
        """
        return list(self.plugin_metadata.keys())
    
    def get_plugin_metadata(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            Plugin metadata dictionary
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        return self.plugin_metadata[plugin_id]
    
    def get_plugin_path(self, plugin_id: str) -> str:
        """
        Get the directory path for a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            Absolute path to the plugin directory
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_paths:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        return self.plugin_paths[plugin_id]
    
    def enable_plugin(self, plugin_id: str) -> None:
        """
        Enable a plugin.
        
        Args:
            plugin_id: ID of the plugin to enable
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        self.plugin_enabled[plugin_id] = True
        logger.info(f"Enabled plugin: {plugin_id}")
    
    def disable_plugin(self, plugin_id: str) -> None:
        """
        Disable a plugin.
        
        Args:
            plugin_id: ID of the plugin to disable
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        self.plugin_enabled[plugin_id] = False
        logger.info(f"Disabled plugin: {plugin_id}")
    
    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """
        Check if a plugin is enabled.
        
        Args:
            plugin_id: ID of the plugin to check
        
        Returns:
            True if the plugin is enabled, False otherwise
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        return self.plugin_enabled.get(plugin_id, False)
    
    def _load_plugin_module(self, plugin_id: str) -> Any:
        """
        Load the module for a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            Loaded plugin module
        
        Raises:
            PluginNotFoundError: If the plugin is not found
            ImportError: If the plugin module cannot be imported
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        if plugin_id in self.plugin_modules:
            return self.plugin_modules[plugin_id]
        
        metadata = self.plugin_metadata[plugin_id]
        plugin_path = self.plugin_paths[plugin_id]
        main_file = metadata['main_file']
        
        # Check if main file exists
        main_file_path = os.path.join(plugin_path, main_file)
        if not os.path.exists(main_file_path):
            raise ImportError(f"Plugin main file not found: {main_file_path}")
        
        # Add plugin directory to sys.path temporarily
        original_sys_path = sys.path.copy()
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)
        
        try:
            # Import the module
            module_name = os.path.splitext(main_file)[0]
            module = importlib.import_module(module_name)
            
            # Store the module
            self.plugin_modules[plugin_id] = module
            
            return module
        
        except Exception as e:
            raise ImportError(f"Failed to import plugin module: {e}")
        
        finally:
            # Restore original sys.path
            sys.path = original_sys_path
    
    def load_plugin(self, plugin_id: str, check_dependencies: bool = True) -> Any:
        """
        Load and initialize a plugin.
        
        Args:
            plugin_id: ID of the plugin to load
            check_dependencies: Whether to check plugin dependencies before loading
        
        Returns:
            Initialized plugin instance
        
        Raises:
            PluginNotFoundError: If the plugin is not found
            PluginDependencyError: If plugin dependencies are not satisfied
            ImportError: If the plugin module cannot be imported
            AttributeError: If the plugin class is not found in the module
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        if not self.is_plugin_enabled(plugin_id):
            logger.warning(f"Attempted to load disabled plugin: {plugin_id}")
            return None
        
        # Check if plugin is already loaded
        if plugin_id in self.plugins:
            return self.plugins[plugin_id]
        
        # Check dependencies if required
        if check_dependencies:
            is_satisfied, missing, incompatible = self.check_plugin_dependencies(plugin_id)
            
            if not is_satisfied:
                metadata = self.plugin_metadata[plugin_id]
                version = metadata['version']
                
                # Handle missing dependencies
                if missing['plugins'] or missing['libraries']:
                    missing_plugins = missing['plugins']
                    missing_libraries = missing['libraries']
                    error_msg = f"Plugin {plugin_id} version {version} has missing dependencies\n"
                    
                    if missing_plugins:
                        error_msg += f"  Missing plugins: {missing_plugins}\n"
                    
                    if missing_libraries:
                        error_msg += f"  Missing libraries: {missing_libraries}"
                    
                    # Create exception with all required attributes
                    raise PluginMissingDependencyError(
                        plugin_id=plugin_id,
                        version=version,
                        missing_plugins=missing_plugins,
                        missing_libraries=missing_libraries,
                        message=error_msg
                    )
                
                # Handle incompatible dependencies
                if incompatible['plugins'] or incompatible['libraries']:
                    incompatible_plugins = incompatible['plugins']
                    incompatible_libraries = incompatible['libraries']
                    error_msg = f"Plugin {plugin_id} version {version} has incompatible dependencies\n"
                    
                    if incompatible_plugins:
                        error_msg += f"  Incompatible plugins: {incompatible_plugins}\n"
                    
                    if incompatible_libraries:
                        error_msg += f"  Incompatible libraries: {incompatible_libraries}"
                    
                    # Create exception with all required attributes
                    raise PluginIncompatibleDependencyError(
                        plugin_id=plugin_id,
                        version=version,
                        incompatible_plugins=incompatible_plugins,
                        incompatible_libraries=incompatible_libraries,
                        message=error_msg
                    )
                
                # Generic dependency error if we get here
                error_msg = f"Plugin {plugin_id} version {version} has unsatisfied dependencies"
                raise PluginDependencyError(error_msg)
        
        try:
            # Load the plugin module
            module = self._load_plugin_module(plugin_id)
            
            # Get plugin metadata
            metadata = self.plugin_metadata[plugin_id]
            main_class = metadata['main_class']
            
            # Get the plugin class
            if not hasattr(module, main_class):
                raise AttributeError(f"Plugin class {main_class} not found in module")
            
            plugin_class = getattr(module, main_class)
            
            # Initialize the plugin
            plugin = plugin_class(
                plugin_id=metadata['id'],
                plugin_name=metadata['name'],
                version=metadata['version'],
                description=metadata['description'],
                config=metadata.get('config', {})
            )
            
            # Store the plugin instance
            self.plugins[plugin_id] = plugin
            
            # Update streaming metadata if the plugin has streaming capabilities
            if hasattr(plugin, 'get_streaming_actions'):
                streaming_actions = plugin.get_streaming_actions()
                if streaming_actions:
                    self.streaming_actions[plugin_id] = streaming_actions
            
            logger.info(f"Loaded plugin: {plugin_id} (version {metadata['version']})")
            
            return plugin
        
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            raise
    
    def unload_plugin(self, plugin_id: str) -> None:
        """
        Unload a plugin.
        
        Args:
            plugin_id: ID of the plugin to unload
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Remove plugin instance
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
        
        # Remove plugin module
        if plugin_id in self.plugin_modules:
            del self.plugin_modules[plugin_id]
        
        logger.info(f"Unloaded plugin: {plugin_id}")
    
    def get_plugin(self, plugin_id: str) -> Any:
        """
        Get a loaded plugin instance.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            Plugin instance if loaded, None otherwise
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        return self.plugins.get(plugin_id)
    
    def is_plugin_loaded(self, plugin_id: str) -> bool:
        """
        Check if a plugin is loaded.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            True if the plugin is loaded, False otherwise
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        return plugin_id in self.plugins
    
    def get_plugin_version(self, plugin_id: str) -> str:
        """
        Get the version of a plugin.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            Plugin version string
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        return self.plugin_metadata[plugin_id]['version']
    
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
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Check if plugin is loaded
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            # Try to load the plugin
            plugin = self.load_plugin(plugin_id)
        
        # Get actions from plugin
        if hasattr(plugin, 'get_actions'):
            return plugin.get_actions()
        
        # Fall back to metadata
        metadata = self.plugin_metadata[plugin_id]
        if 'actions' in metadata:
            return list(metadata['actions'].keys())
        
        return []
    
    def execute_action(self, plugin_id: str, action: str, *args, **kwargs) -> Any:
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
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Check if plugin is loaded
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            # Try to load the plugin
            plugin = self.load_plugin(plugin_id)
        
        # Check if action exists
        if not hasattr(plugin, action):
            raise AttributeError(f"Action {action} not found in plugin {plugin_id}")
        
        # Execute the action
        action_method = getattr(plugin, action)
        return action_method(*args, **kwargs)
    
    def check_plugin_dependencies(self, plugin_id: str) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
        """
        Check if all dependencies for a plugin are satisfied.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            Tuple of (is_satisfied, missing_dependencies, incompatible_dependencies)
            
            is_satisfied: True if all dependencies are satisfied, False otherwise
            missing_dependencies: Dictionary of missing dependencies
            incompatible_dependencies: Dictionary of incompatible dependencies
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Get plugin dependencies
        dependencies = self.get_plugin_dependencies(plugin_id)
        
        # Initialize result dictionaries
        missing = {
            "plugins": {},
            "libraries": {}
        }
        
        incompatible = {
            "plugins": {},
            "libraries": {}
        }
        
        # Check plugin dependencies
        if "plugins" in dependencies:
            for dep_id, constraint in dependencies["plugins"].items():
                # Check if plugin exists
                if dep_id not in self.plugin_metadata:
                    missing["plugins"][dep_id] = constraint
                    continue
                
                # Check version constraint
                try:
                    dep_version = self.get_plugin_version(dep_id)
                    spec = SpecifierSet(constraint)
                    
                    if packaging.version.parse(dep_version) not in spec:
                        incompatible["plugins"][dep_id] = {
                            "constraint": constraint,
                            "available": [dep_version]
                        }
                except Exception as e:
                    # Invalid version constraint
                    logger.warning(f"Invalid version constraint for plugin dependency {dep_id}: {e}")
                    incompatible["plugins"][dep_id] = {
                        "constraint": constraint,
                        "error": "Invalid version constraint"
                    }
        
        # Check library dependencies
        if "libraries" in dependencies:
            for lib_name, constraint in dependencies["libraries"].items():
                # Check if library exists
                try:
                    lib_module = importlib.import_module(lib_name)
                except ImportError:
                    missing["libraries"][lib_name] = constraint
                    continue
                
                # Check version constraint
                try:
                    lib_version = getattr(lib_module, "__version__", "0.0.0")
                    spec = SpecifierSet(constraint)
                    
                    if packaging.version.parse(lib_version) not in spec:
                        incompatible["libraries"][lib_name] = {
                            "constraint": constraint,
                            "installed": lib_version
                        }
                except Exception as e:
                    # Invalid version constraint
                    logger.warning(f"Invalid version constraint for library dependency {lib_name}: {e}")
                    incompatible["libraries"][lib_name] = {
                        "constraint": constraint,
                        "error": "Invalid version constraint"
                    }
        
        # Check if all dependencies are satisfied
        is_satisfied = (
            len(missing["plugins"]) == 0 and
            len(missing["libraries"]) == 0 and
            len(incompatible["plugins"]) == 0 and
            len(incompatible["libraries"]) == 0
        )
        
        return is_satisfied, missing, incompatible
    
    def get_plugin_dependencies(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get dependencies for a plugin.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            Dictionary of dependencies
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Get dependencies from plugin_dependencies
        if plugin_id in self.plugin_dependencies:
            return self.plugin_dependencies[plugin_id]
        
        # Fall back to metadata
        metadata = self.plugin_metadata[plugin_id]
        if 'dependencies' in metadata:
            return metadata['dependencies']
        
        # No dependencies
        return {}
    
    def get_streaming_plugin_ids(self) -> List[str]:
        """
        Get a list of plugin IDs that support streaming.
        
        Returns:
            List of plugin IDs with streaming capabilities
        """
        return list(self.streaming_actions.keys())
    
    def get_streaming_actions(self, plugin_id: str) -> List[str]:
        """
        Get a list of streaming-capable actions for a plugin.
        
        Args:
            plugin_id: ID of the plugin
        
        Returns:
            List of action names that support streaming
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        if plugin_id not in self.streaming_actions:
            return []
        
        return list(self.streaming_actions[plugin_id].keys())
    
    def get_streaming_action_metadata(self, plugin_id: str, action: str) -> Dict[str, Any]:
        """
        Get streaming metadata for a specific action.
        
        Args:
            plugin_id: ID of the plugin
            action: Name of the action
        
        Returns:
            Dictionary of streaming metadata
        
        Raises:
            PluginNotFoundError: If the plugin is not found
            KeyError: If the action does not support streaming
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        if plugin_id not in self.streaming_actions:
            raise KeyError(f"Plugin {plugin_id} does not support streaming")
        
        if action not in self.streaming_actions[plugin_id]:
            raise KeyError(f"Action {action} in plugin {plugin_id} does not support streaming")
        
        return self.streaming_actions[plugin_id][action]
    
    def get_stream_metadata_from_plugin(self, plugin_id: str, action: str) -> Dict[str, Any]:
        """
        Get streaming metadata directly from a plugin instance.
        
        Args:
            plugin_id: ID of the plugin
            action: Name of the action
        
        Returns:
            Dictionary of streaming metadata
        
        Raises:
            PluginNotFoundError: If the plugin is not found
            AttributeError: If the plugin does not support streaming
            KeyError: If the action does not support streaming
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Check if plugin is loaded
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            # Try to load the plugin
            plugin = self.load_plugin(plugin_id)
        
        # Check if plugin supports streaming
        if not hasattr(plugin, 'get_streaming_metadata'):
            raise AttributeError(f"Plugin {plugin_id} does not support streaming")
        
        # Get streaming metadata for the action
        metadata = plugin.get_streaming_metadata(action)
        if not metadata:
            raise KeyError(f"Action {action} in plugin {plugin_id} does not support streaming")
        
        return metadata
    
    def is_action_streaming_capable(self, plugin_id: str, action: str) -> bool:
        """
        Check if an action supports streaming.
        
        Args:
            plugin_id: ID of the plugin
            action: Name of the action
        
        Returns:
            True if the action supports streaming, False otherwise
        
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        if plugin_id not in self.plugin_metadata:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        if plugin_id not in self.streaming_actions:
            return False
        
        return action in self.streaming_actions[plugin_id]
    
    def get_all_streaming_actions(self) -> Dict[str, List[str]]:
        """
        Get all streaming-capable actions across all plugins.
        
        Returns:
            Dictionary mapping plugin IDs to lists of streaming-capable action names
        """
        result = {}
        for plugin_id in self.streaming_actions:
            result[plugin_id] = list(self.streaming_actions[plugin_id].keys())
        return result
    
    def get_streaming_actions_by_capability(self, capability: str) -> Dict[str, List[str]]:
        """
        Get streaming-capable actions that support a specific capability.
        
        Args:
            capability: Streaming capability to filter by
        
        Returns:
            Dictionary mapping plugin IDs to lists of action names
        """
        result = {}
        for plugin_id, actions in self.streaming_actions.items():
            matching_actions = []
            for action_id, metadata in actions.items():
                if 'capabilities' in metadata and capability in metadata['capabilities']:
                    matching_actions.append(action_id)
            
            if matching_actions:
                result[plugin_id] = matching_actions
        
        return result
    
    def get_streaming_actions_by_content_type(self, content_type: str) -> Dict[str, List[str]]:
        """
        Get streaming-capable actions that support a specific content type.
        
        Args:
            content_type: Content type to filter by
        
        Returns:
            Dictionary mapping plugin IDs to lists of action names
        """
        result = {}
        for plugin_id, actions in self.streaming_actions.items():
            matching_actions = []
            for action_id, metadata in actions.items():
                if 'content_types' in metadata and content_type in metadata['content_types']:
                    matching_actions.append(action_id)
            
            if matching_actions:
                result[plugin_id] = matching_actions
        
        return result
    
    def transform_stream(self, stream, transformation, **kwargs):
        """
        Apply a transformation to a stream.
        
        Args:
            stream: The stream to transform
            transformation: The transformation to apply
            **kwargs: Additional parameters for the transformation
        
        Returns:
            Transformed stream
        
        Raises:
            NotImplementedError: This method is not yet implemented
        """
        # This is a placeholder for future implementation
        raise NotImplementedError("Stream transformation is not yet implemented")
