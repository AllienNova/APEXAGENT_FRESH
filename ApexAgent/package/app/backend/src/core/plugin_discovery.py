"""
Plugin Discovery Module for ApexAgent

This module provides functionality for discovering plugins in the ApexAgent system.
It handles scanning directories for plugins, parsing manifests, and validating plugin structures.
"""

import os
import json
import logging
import glob
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple

from src.core.plugin_exceptions import (
    PluginError,
    PluginConfigurationError
)

# Configure logging
logger = logging.getLogger(__name__)

class PluginDiscovery:
    """
    Handles the discovery of plugins in specified directories.
    
    The PluginDiscovery is responsible for:
    1. Scanning directories for potential plugins
    2. Parsing and validating plugin manifests
    3. Tracking plugin versions and updates
    4. Providing metadata about discovered plugins
    """
    
    def __init__(self, schema_validator=None, plugin_loader=None):
        """
        Initialize the PluginDiscovery.
        
        Args:
            schema_validator: Optional validator for plugin manifests
            plugin_loader: Optional plugin loader for loading discovered plugins
        """
        self.schema_validator = schema_validator
        self.plugin_loader = plugin_loader
        self.discovered_plugins = {}  # Maps plugin_id to plugin metadata
        self.plugin_paths = {}  # Maps plugin_id to plugin directory path
        self.plugin_checksums = {}  # Maps plugin_id to checksum for change detection
    
    def discover_plugins(self, plugin_dirs: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Discover plugins in the specified directories.
        
        Args:
            plugin_dirs: List of directories to scan for plugins
            
        Returns:
            Dictionary mapping plugin IDs to plugin metadata
            
        Raises:
            PluginError: If a plugin directory cannot be accessed
        """
        # Reset discovery results
        self.discovered_plugins = {}
        self.plugin_paths = {}
        self.plugin_checksums = {}
        
        # Track all plugin IDs to detect duplicates
        all_plugin_ids = set()
        duplicate_plugin_ids = set()
        
        # Scan each directory
        for plugin_dir in plugin_dirs:
            if not os.path.exists(plugin_dir):
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
                
            if not os.path.isdir(plugin_dir):
                logger.warning(f"Plugin path is not a directory: {plugin_dir}")
                continue
                
            try:
                # Look for potential plugin directories (containing manifest.json)
                for item in os.listdir(plugin_dir):
                    item_path = os.path.join(plugin_dir, item)
                    
                    # Skip non-directories
                    if not os.path.isdir(item_path):
                        continue
                    
                    # Check for manifest file
                    manifest_path = self._find_manifest_file(item_path)
                    if not manifest_path:
                        continue
                    
                    # Parse and validate manifest
                    try:
                        metadata = self._parse_manifest(manifest_path)
                        plugin_id = metadata.get('id')
                        
                        if not plugin_id:
                            logger.warning(f"Plugin manifest missing 'id' field: {manifest_path}")
                            continue
                        
                        # Check for duplicate plugin IDs
                        if plugin_id in all_plugin_ids:
                            duplicate_plugin_ids.add(plugin_id)
                            logger.warning(f"Duplicate plugin ID found: {plugin_id}")
                            continue
                        
                        all_plugin_ids.add(plugin_id)
                        
                        # Store plugin metadata and path
                        self.discovered_plugins[plugin_id] = metadata
                        self.plugin_paths[plugin_id] = item_path
                        
                        # Calculate plugin checksum for change detection
                        self.plugin_checksums[plugin_id] = self._calculate_plugin_checksum(item_path)
                        
                        logger.info(f"Discovered plugin: {plugin_id} (version {metadata.get('version', 'unknown')})")
                    
                    except Exception as e:
                        logger.warning(f"Error processing plugin manifest {manifest_path}: {e}")
            
            except Exception as e:
                raise PluginError(f"Error scanning plugin directory {plugin_dir}: {e}")
        
        # Log warning for duplicate plugin IDs
        if duplicate_plugin_ids:
            logger.warning(f"Found {len(duplicate_plugin_ids)} duplicate plugin IDs: {', '.join(duplicate_plugin_ids)}")
        
        return self.discovered_plugins
    
    def load_discovered_plugins(self, plugin_config: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load all discovered plugins using the plugin loader.
        
        Args:
            plugin_config: Optional dictionary mapping plugin IDs to configuration dictionaries
            
        Returns:
            Dictionary mapping plugin IDs to loaded plugin instances
            
        Raises:
            PluginError: If the plugin loader is not set or if loading fails
        """
        if not self.plugin_loader:
            raise PluginError("Plugin loader not set, cannot load plugins")
        
        loaded_plugins = {}
        plugin_config = plugin_config or {}
        
        for plugin_id, metadata in self.discovered_plugins.items():
            try:
                plugin_path = self.plugin_paths[plugin_id]
                config = plugin_config.get(plugin_id, {})
                
                # Load the plugin
                plugin_instance = self.plugin_loader.load_plugin(plugin_path, plugin_id, config)
                loaded_plugins[plugin_id] = plugin_instance
                
                logger.info(f"Loaded plugin: {plugin_id}")
                
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")
                # Continue loading other plugins even if one fails
        
        return loaded_plugins
    
    def _find_manifest_file(self, plugin_dir: str) -> Optional[str]:
        """
        Find the manifest file in a plugin directory.
        
        Looks for manifest.json, plugin.json, or *.manifest.json files.
        
        Args:
            plugin_dir: Directory to search for manifest file
            
        Returns:
            Path to manifest file if found, None otherwise
        """
        # Check for common manifest file names
        manifest_candidates = [
            os.path.join(plugin_dir, 'manifest.json'),
            os.path.join(plugin_dir, 'plugin.json')
        ]
        
        for candidate in manifest_candidates:
            if os.path.isfile(candidate):
                return candidate
        
        # Look for *.manifest.json files
        manifest_pattern = os.path.join(plugin_dir, '*.manifest.json')
        manifest_files = glob.glob(manifest_pattern)
        
        if manifest_files:
            return manifest_files[0]
        
        return None
    
    def _parse_manifest(self, manifest_path: str) -> Dict[str, Any]:
        """
        Parse and validate a plugin manifest file.
        
        Args:
            manifest_path: Path to the manifest file
            
        Returns:
            Parsed manifest as a dictionary
            
        Raises:
            PluginConfigurationError: If the manifest is invalid
        """
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Validate required fields
            required_fields = ['id', 'name', 'version', 'description', 'main_module', 'class_name']
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                raise PluginConfigurationError(
                    f"Plugin manifest missing required fields: {', '.join(missing_fields)}"
                )
            
            # Validate with schema if available
            if self.schema_validator:
                self.schema_validator.validate(manifest)
            
            return manifest
            
        except json.JSONDecodeError as e:
            raise PluginConfigurationError(f"Invalid JSON in plugin manifest: {e}")
        except Exception as e:
            if isinstance(e, PluginConfigurationError):
                raise
            raise PluginConfigurationError(f"Error parsing plugin manifest: {e}")
    
    def _calculate_plugin_checksum(self, plugin_dir: str) -> str:
        """
        Calculate a checksum for a plugin directory to detect changes.
        
        Args:
            plugin_dir: Path to the plugin directory
            
        Returns:
            Checksum string
        """
        hasher = hashlib.md5()
        
        # Get list of all files in the plugin directory
        for root, _, files in os.walk(plugin_dir):
            for file in sorted(files):  # Sort for consistent order
                file_path = os.path.join(root, file)
                
                # Skip __pycache__ and other non-source files
                if '__pycache__' in file_path or file.endswith('.pyc'):
                    continue
                
                # Update hash with file path and content
                rel_path = os.path.relpath(file_path, plugin_dir)
                hasher.update(rel_path.encode('utf-8'))
                
                try:
                    with open(file_path, 'rb') as f:
                        # Read in chunks to handle large files
                        for chunk in iter(lambda: f.read(4096), b''):
                            hasher.update(chunk)
                except Exception as e:
                    logger.warning(f"Error reading file for checksum: {file_path}: {e}")
        
        return hasher.hexdigest()
    
    def get_plugin_path(self, plugin_id: str) -> str:
        """
        Get the directory path for a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Path to the plugin directory
            
        Raises:
            PluginError: If the plugin is not found
        """
        if plugin_id not in self.plugin_paths:
            raise PluginError(f"Plugin not found: {plugin_id}")
        
        return self.plugin_paths[plugin_id]
    
    def get_plugin_metadata(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin metadata
            
        Raises:
            PluginError: If the plugin is not found
        """
        if plugin_id not in self.discovered_plugins:
            raise PluginError(f"Plugin not found: {plugin_id}")
        
        return self.discovered_plugins[plugin_id]
    
    def get_all_plugin_ids(self) -> List[str]:
        """
        Get a list of all discovered plugin IDs.
        
        Returns:
            List of plugin IDs
        """
        return list(self.discovered_plugins.keys())
    
    def has_plugin_changed(self, plugin_id: str) -> bool:
        """
        Check if a plugin has changed since it was discovered.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            True if the plugin has changed, False otherwise
            
        Raises:
            PluginError: If the plugin is not found
        """
        if plugin_id not in self.plugin_paths:
            raise PluginError(f"Plugin not found: {plugin_id}")
        
        if plugin_id not in self.plugin_checksums:
            return True
        
        old_checksum = self.plugin_checksums[plugin_id]
        new_checksum = self._calculate_plugin_checksum(self.plugin_paths[plugin_id])
        
        return old_checksum != new_checksum
    
    def get_plugins_by_capability(self, capability: str) -> List[str]:
        """
        Get plugins that declare a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of plugin IDs with the specified capability
        """
        matching_plugins = []
        
        for plugin_id, metadata in self.discovered_plugins.items():
            capabilities = metadata.get('capabilities', [])
            if capability in capabilities:
                matching_plugins.append(plugin_id)
        
        return matching_plugins
    
    def get_plugins_with_dependencies(self) -> Dict[str, List[str]]:
        """
        Get a mapping of plugins to their dependencies.
        
        Returns:
            Dictionary mapping plugin IDs to lists of dependency plugin IDs
        """
        dependency_map = {}
        
        for plugin_id, metadata in self.discovered_plugins.items():
            dependencies = metadata.get('dependencies', {}).get('plugins', {})
            if dependencies:
                dependency_map[plugin_id] = list(dependencies.keys())
        
        return dependency_map
    
    def get_dependent_plugins(self, plugin_id: str) -> List[str]:
        """
        Get plugins that depend on a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            List of plugin IDs that depend on the specified plugin
        """
        dependent_plugins = []
        
        for dep_id, metadata in self.discovered_plugins.items():
            if dep_id == plugin_id:
                continue
                
            dependencies = metadata.get('dependencies', {}).get('plugins', {})
            if plugin_id in dependencies:
                dependent_plugins.append(dep_id)
        
        return dependent_plugins
    
    def set_plugin_loader(self, plugin_loader) -> None:
        """
        Set the plugin loader to use for loading discovered plugins.
        
        Args:
            plugin_loader: The plugin loader instance
        """
        self.plugin_loader = plugin_loader


class ManifestSchemaValidator:
    """
    Validates plugin manifests against a JSON schema.
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the schema validator.
        
        Args:
            schema_path: Path to the JSON schema file
            
        Raises:
            PluginConfigurationError: If the schema cannot be loaded
        """
        self.schema = None
        
        if schema_path:
            try:
                with open(schema_path, 'r') as f:
                    self.schema = json.load(f)
            except Exception as e:
                raise PluginConfigurationError(f"Failed to load schema from {schema_path}: {e}")
    
    def validate(self, manifest: Dict[str, Any]) -> None:
        """
        Validate a manifest against the schema.
        
        Args:
            manifest: The manifest to validate
            
        Raises:
            PluginConfigurationError: If validation fails
        """
        if not self.schema:
            return
        
        try:
            import jsonschema
            jsonschema.validate(instance=manifest, schema=self.schema)
        except ImportError:
            logger.warning("jsonschema package not available, skipping schema validation")
        except jsonschema.exceptions.ValidationError as e:
            raise PluginConfigurationError(f"Plugin manifest validation failed: {e}")
