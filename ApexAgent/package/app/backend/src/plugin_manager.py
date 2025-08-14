import os
import json
import importlib
import inspect
import functools
import asyncio # Required for async file operations if we use aiofiles, or for async helpers
from typing import Any, Dict, List, Optional, Callable, Awaitable, AsyncGenerator

from jsonschema import validate, RefResolver, Draft7Validator
import logging

# For dependency checking
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import parse as parse_version, InvalidVersion
import importlib.metadata # For checking installed package versions

from agent_project.src.core.base_enhanced_plugin import BaseEnhancedPlugin, SaveStateFunc, LoadStateFunc, DeleteStateFunc
from agent_project.src.core.exceptions import PluginInitializationError, PluginExecutionError, PluginNotImplementedError, PluginStateError, PluginDependencyError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PluginManager:
    def __init__(self, 
                 plugin_dirs: List[str], 
                 schema_path: str = "/home/ubuntu/agent_project/docs/plugin_metadata_schema.json",
                 plugin_states_root_dir: str = "/home/ubuntu/agent_project/plugin_states"):
        self.plugin_metadata_registry: Dict[str, Dict[str, Any]] = {} # Stores metadata and path
        self.plugin_instance_cache: Dict[str, BaseEnhancedPlugin] = {}
        self.plugin_status: Dict[str, str] = {} # Stores status like "loaded", "disabled_dependency_issue"
        self.schema_path = schema_path
        self.plugin_schema = self._load_schema()
        self.plugin_states_root_dir = plugin_states_root_dir
        os.makedirs(self.plugin_states_root_dir, exist_ok=True)
        
        if self.plugin_schema:
            self.discover_plugins(plugin_dirs)
        else:
            logging.error("Failed to load plugin metadata schema. Plugin discovery aborted.")

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        try:
            with open(self.schema_path, 'r') as f:
                schema = json.load(f)
            Draft7Validator.check_schema(schema) # Validate the schema itself
            logging.info(f"Successfully loaded plugin metadata schema from {self.schema_path}")
            return schema
        except FileNotFoundError:
            logging.error(f"Schema file not found: {self.schema_path}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON schema from {self.schema_path}: {e}")
        except Exception as e: # Catch other schema validation errors
            logging.error(f"An unexpected error occurred while loading or validating schema {self.schema_path}: {e}")
        return None

    def _check_plugin_dependencies(self, plugin_id: str, metadata: Dict[str, Any]) -> bool:
        """Checks dependencies for a given plugin. Returns True if all met, False otherwise."""
        dependencies = metadata.get("dependencies")
        if not dependencies:
            return True # No dependencies to check

        all_deps_met = True

        # Check plugin dependencies
        plugin_deps = dependencies.get("plugins", [])
        for dep in plugin_deps:
            dep_id = dep["id"]
            dep_version_spec = dep.get("version_specifier")
            
            if dep_id not in self.plugin_metadata_registry:
                logging.error(f"Dependency check failed for plugin '{plugin_id}': Required plugin '{dep_id}' not found.")
                all_deps_met = False
                continue
            
            if dep_version_spec:
                try:
                    required_spec = SpecifierSet(dep_version_spec)
                    actual_version_str = self.plugin_metadata_registry[dep_id]["metadata"].get("version")
                    if not actual_version_str:
                        logging.warning(f"Dependency check for plugin '{plugin_id}': Dependent plugin '{dep_id}' has no version. Cannot satisfy specifier '{dep_version_spec}'.")
                        all_deps_met = False
                        continue
                    actual_version = parse_version(actual_version_str)
                    if actual_version not in required_spec:
                        logging.error(f"Dependency check failed for plugin '{plugin_id}': Plugin '{dep_id}' version '{actual_version_str}' does not meet requirement '{dep_version_spec}'.")
                        all_deps_met = False
                except (InvalidSpecifier, InvalidVersion) as e:
                    logging.error(f"Dependency check failed for plugin '{plugin_id}': Invalid version specifier '{dep_version_spec}' or version for plugin '{dep_id}': {e}")
                    all_deps_met = False
        
        # Check Python library dependencies
        library_deps = dependencies.get("python_libraries", [])
        for lib_dep in library_deps:
            lib_name = lib_dep["name"]
            lib_version_spec = lib_dep.get("version_specifier")
            import_check_module = lib_dep.get("import_check_module", lib_name)
            
            try:
                importlib.import_module(import_check_module)
                if lib_version_spec:
                    try:
                        installed_version_str = importlib.metadata.version(lib_name) # Get version of the distribution package name
                        installed_version = parse_version(installed_version_str)
                        required_spec = SpecifierSet(lib_version_spec)
                        if installed_version not in required_spec:
                            logging.error(f"Dependency check failed for plugin '{plugin_id}': Library '{lib_name}' version '{installed_version_str}' does not meet requirement '{lib_version_spec}'.")
                            all_deps_met = False
                    except importlib.metadata.PackageNotFoundError:
                        logging.error(f"Dependency check failed for plugin '{plugin_id}': Library '{lib_name}' is importable as '{import_check_module}' but package metadata not found to check version '{lib_version_spec}'.")
                        all_deps_met = False # Cannot verify version
                    except (InvalidSpecifier, InvalidVersion) as e:
                        logging.error(f"Dependency check failed for plugin '{plugin_id}': Invalid version specifier '{lib_version_spec}' or version for library '{lib_name}': {e}")
                        all_deps_met = False
            except ImportError:
                logging.error(f"Dependency check failed for plugin '{plugin_id}': Required Python library '{import_check_module}' (for '{lib_name}') not found.")
                all_deps_met = False
        
        return all_deps_met

    def discover_plugins(self, plugin_dirs: List[str]):
        if not self.plugin_schema:
            logging.error("Plugin metadata schema not loaded. Cannot discover plugins.")
            return

        discovered_plugins_metadata = {} # Stage 1: Discover all metadata first

        for plugins_dir_path in plugin_dirs:
            if not os.path.isdir(plugins_dir_path):
                logging.warning(f"Plugin directory not found or not a directory: {plugins_dir_path}")
                continue
            
            logging.info(f"Scanning for plugins in: {plugins_dir_path}")
            for item_name in os.listdir(plugins_dir_path):
                plugin_path = os.path.join(plugins_dir_path, item_name)
                if os.path.isdir(plugin_path):
                    metadata_file_path = os.path.join(plugin_path, "plugin.json") 
                    if not os.path.isfile(metadata_file_path):
                        metadata_file_path_alt = os.path.join(plugin_path, "metadata.json")
                        if os.path.isfile(metadata_file_path_alt):
                            metadata_file_path = metadata_file_path_alt
                        else:
                            continue # No metadata file found
                    
                    logging.info(f"Found potential plugin metadata: {metadata_file_path}")
                    try:
                        with open(metadata_file_path, 'r') as f:
                            metadata = json.load(f)
                        
                        resolver = RefResolver.from_schema(self.plugin_schema)
                        validate(instance=metadata, schema=self.plugin_schema, resolver=resolver)
                        
                        plugin_id = metadata.get("id")
                        if not plugin_id:
                            logging.warning(f"Plugin metadata at {metadata_file_path} is missing 'id'. Skipping.")
                            continue

                        if plugin_id in discovered_plugins_metadata:
                            logging.warning(f"Duplicate plugin ID '{plugin_id}' found at {metadata_file_path}. Previous one at {discovered_plugins_metadata[plugin_id]['metadata_path']}. Skipping duplicate.")
                            continue
                        
                        discovered_plugins_metadata[plugin_id] = {
                            "metadata": metadata,
                            "path": plugin_path,
                            "metadata_path": metadata_file_path
                        }
                        logging.info(f"Successfully validated metadata for plugin '{metadata.get('name', plugin_id)}' (ID: {plugin_id})")
                    except Exception as e: 
                        logging.error(f"Error validating or processing metadata for plugin at {metadata_file_path}: {e}")
        
        # Stage 2: Register plugins and check dependencies
        # This order allows plugins to depend on each other regardless of scan order, as long as all metadata is valid.
        for plugin_id, plugin_data in discovered_plugins_metadata.items():
            self.plugin_metadata_registry[plugin_id] = plugin_data # Tentatively add to registry for dep checks
        
        for plugin_id, plugin_data in discovered_plugins_metadata.items():
            if self._check_plugin_dependencies(plugin_id, plugin_data["metadata"]):
                self.plugin_status[plugin_id] = "loaded"
                logging.info(f"Plugin '{plugin_data['metadata'].get('name', plugin_id)}' (ID: {plugin_id}) dependencies met. Status: loaded.")
            else:
                self.plugin_status[plugin_id] = "disabled_dependency_issue"
                # Keep in metadata_registry but mark as disabled
                logging.error(f"Plugin '{plugin_data['metadata'].get('name', plugin_id)}' (ID: {plugin_id}) has unmet dependencies. Status: disabled.")
                # Optionally, remove from registry if we don't want to list disabled plugins at all
                # del self.plugin_metadata_registry[plugin_id]

    def get_plugin_metadata(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        return self.plugin_metadata_registry.get(plugin_id, {}).get("metadata")

    def get_all_plugins_metadata(self, include_disabled: bool = False) -> Dict[str, Dict[str, Any]]:
        if include_disabled:
            return {pid: data["metadata"] for pid, data in self.plugin_metadata_registry.items()}
        else:
            return {
                pid: data["metadata"] 
                for pid, data in self.plugin_metadata_registry.items() 
                if self.plugin_status.get(pid) == "loaded"
            }

    def _load_plugin_class(self, entry_point_str: str) -> Optional[type[BaseEnhancedPlugin]]:
        try:
            module_name, class_name = entry_point_str.rsplit('.', 1)
            # Assuming entry_point is relative to a base like 'agent_project.src' or similar
            # For testing, this might need adjustment if plugins are in 'tests' package
            # Current assumption: entry_point is like "plugins.my_plugin_module.MyPluginClass"
            # and 'agent_project.src' is in PYTHONPATH.
            full_module_name = f"agent_project.src.{module_name}" 
            # If your plugins are directly under src (e.g. src.my_plugin_module), then it's fine.
            # If they are in src.plugins.my_plugin_module, then entry_point should be `plugins.my_plugin_module.MyPluginClass`
            # and full_module_name will be `agent_project.src.plugins.my_plugin_module`
            module = importlib.import_module(full_module_name)
            plugin_class = getattr(module, class_name)
            if not issubclass(plugin_class, BaseEnhancedPlugin):
                logging.error(f"Plugin class {entry_point_str} does not inherit from BaseEnhancedPlugin.")
                return None
            return plugin_class
        except ModuleNotFoundError as e:
            logging.error(f"Module not found for plugin class {entry_point_str}: {e}. Check PYTHONPATH and entry_point format.")
        except AttributeError as e:
            logging.error(f"Class not found in module for plugin class {entry_point_str}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error loading plugin class {entry_point_str}: {e}")
        return None

    async def _handle_plugin_progress(self, plugin_id: str, action_name: str, current_step: int, total_steps: Optional[int], message: str, additional_data: Optional[Dict[str, Any]]):
        log_message = f"PROGRESS: Plugin='{plugin_id}', Action='{action_name}', Step={current_step}/{total_steps if total_steps is not None else 'N/A'}"
        if message: log_message += f", Msg='{message}'"
        if additional_data: log_message += f", Data={additional_data}"
        logging.info(log_message)

    def _get_plugin_state_dir(self, plugin_id: str) -> str:
        state_dir = os.path.join(self.plugin_states_root_dir, plugin_id)
        os.makedirs(state_dir, exist_ok=True)
        return state_dir

    def _get_state_file_path(self, plugin_id: str, key: str) -> str:
        safe_key_filename = "".join(c if c.isalnum() else '_' for c in key) + ".json"
        return os.path.join(self._get_plugin_state_dir(plugin_id), safe_key_filename)

    async def _save_state_for_plugin(self, plugin_id: str, key: str, value: Any) -> None:
        file_path = self._get_state_file_path(plugin_id, key)
        try:
            await asyncio.to_thread(json.dump, value, open(file_path, 'w'), indent=2)
            logging.debug(f"State saved for plugin ID='{plugin_id}', key ID='{key}' to {file_path}")
        except TypeError as e:
            logging.error(f"Error serializing state for plugin ID='{plugin_id}', key ID='{key}': {e}")
            raise PluginStateError(f"Data for key ID='{key}' is not JSON serializable.") from e
        except IOError as e:
            logging.error(f"IOError saving state for plugin ID='{plugin_id}', key ID='{key}' to {file_path}: {e}")
            raise PluginStateError(f"Could not write state file for key ID='{key}'.") from e

    async def _load_state_for_plugin(self, plugin_id: str, key: str, default: Optional[Any] = None) -> Any:
        file_path = self._get_state_file_path(plugin_id, key)
        try:
            if not await asyncio.to_thread(os.path.exists, file_path):
                logging.debug(f"State file not found for plugin ID='{plugin_id}', key ID='{key}'. Returning default.")
                return default
            with await asyncio.to_thread(open, file_path, 'r') as f:
                value = await asyncio.to_thread(json.load, f)
            logging.debug(f"State loaded for plugin ID='{plugin_id}', key ID='{key}' from {file_path}")
            return value
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON state for plugin ID='{plugin_id}', key ID='{key}' from {file_path}: {e}")
            raise PluginStateError(f"Could not decode state file for key ID='{key}'. File may be corrupted.") from e
        except IOError as e:
            logging.error(f"IOError loading state for plugin ID='{plugin_id}', key ID='{key}' from {file_path}: {e}")
            raise PluginStateError(f"Could not read state file for key ID='{key}'.") from e

    async def _delete_state_for_plugin(self, plugin_id: str, key: str) -> bool:
        file_path = self._get_state_file_path(plugin_id, key)
        try:
            if await asyncio.to_thread(os.path.exists, file_path):
                await asyncio.to_thread(os.remove, file_path)
                logging.debug(f"State file deleted for plugin ID='{plugin_id}', key ID='{key}' at {file_path}")
                return True
            logging.debug(f"State file not found for deletion for plugin ID='{plugin_id}', key ID='{key}'. No action taken.")
            return True 
        except IOError as e:
            logging.error(f"IOError deleting state for plugin ID='{plugin_id}', key ID='{key}' at {file_path}: {e}")
            raise PluginStateError(f"Could not delete state file for key ID='{key}'.") from e

    def get_plugin_instance(self, plugin_id: str) -> Optional[BaseEnhancedPlugin]:
        if self.plugin_status.get(plugin_id) != "loaded":
            logging.error(f"Cannot get instance of plugin '{plugin_id}'. Status: {self.plugin_status.get(plugin_id, 'unknown')}. May have unmet dependencies or failed to load.")
            raise PluginDependencyError(f"Plugin '{plugin_id}' is not loaded or has unmet dependencies.")

        if plugin_id in self.plugin_instance_cache:
            return self.plugin_instance_cache[plugin_id]

        plugin_info = self.plugin_metadata_registry.get(plugin_id)
        if not plugin_info: # Should not happen if status is 'loaded'
            logging.error(f"Plugin with ID '{plugin_id}' not in metadata registry despite 'loaded' status. This is an internal error.")
            return None

        metadata = plugin_info["metadata"]
        entry_point = metadata.get("entry_point")
        if not entry_point:
            logging.error(f"No entry_point defined for plugin ID '{plugin_id}'.")
            return None

        plugin_class = self._load_plugin_class(entry_point)
        if not plugin_class:
            return None

        try:
            save_func = functools.partial(self._save_state_for_plugin, plugin_id)
            load_func = functools.partial(self._load_state_for_plugin, plugin_id)
            delete_func = functools.partial(self._delete_state_for_plugin, plugin_id)

            instance = plugin_class(
                plugin_id=plugin_id,
                plugin_version=metadata.get("version", "0.0.0"),
                config=metadata.get("configuration", {}),
                progress_callback=functools.partial(self._handle_plugin_progress, plugin_id),
                save_state_func=save_func,
                load_state_func=load_func,
                delete_state_func=delete_func
            )
            self.plugin_instance_cache[plugin_id] = instance
            logging.info(f"Successfully instantiated plugin '{plugin_id}'.")
            return instance
        except Exception as e:
            logging.error(f"Failed to instantiate plugin '{plugin_id}': {e}")
            # Potentially change status if instantiation fails post-dependency check
            self.plugin_status[plugin_id] = "disabled_instantiation_error"
            raise PluginInitializationError(f"Initialization failed for plugin '{plugin_id}': {e}") from e

    async def invoke_plugin_action(
        self, 
        plugin_id: str, 
        action_name: str, 
        **kwargs: Any
    ) -> Any:
        try:
            plugin_instance = self.get_plugin_instance(plugin_id) # This now raises PluginDependencyError if not loaded
        except PluginDependencyError:
            raise # Re-raise the specific error
        except Exception as e: # Catch other errors from get_plugin_instance, though less likely now
             raise PluginNotImplementedError(f"Plugin '{plugin_id}' could not be instantiated: {e}")
        
        if not plugin_instance: # Should be redundant due to checks in get_plugin_instance
            raise PluginNotImplementedError(f"Plugin '{plugin_id}' could not be instantiated or is not registered/loaded.")
        try:
            return await plugin_instance.execute_action(action_name, **kwargs)
        except PluginNotImplementedError:
            logging.error(f"Action '{action_name}' not implemented in plugin '{plugin_id}'.")
            raise
        except PluginExecutionError:
            logging.error(f"Execution error in action '{action_name}' of plugin '{plugin_id}'.")
            raise
        except Exception as e:
            logging.error(f"Unexpected error invoking action '{action_name}' on plugin '{plugin_id}': {e}")
            raise PluginExecutionError(f"Unexpected error during invoke_plugin_action for '{plugin_id}.{action_name}': {e}") from e

if __name__ == "__main__":
    # Test harness moved to a dedicated test file for clarity and robustness.
    pass

