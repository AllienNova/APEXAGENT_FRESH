import abc
import logging
import inspect
from typing import Callable, Awaitable, Any, Dict, Optional, AsyncGenerator

from .exceptions import PluginError, PluginArgumentError, PluginNotImplementedError, PluginExecutionError, PluginStateError

# Type aliases for state management functions
SaveStateFunc = Callable[[str, Any], Awaitable[None]]
LoadStateFunc = Callable[[str, Optional[Any]], Awaitable[Any]]
DeleteStateFunc = Callable[[str], Awaitable[bool]]

class BaseEnhancedPlugin(abc.ABC):
    """
    Base class for ApexAgent enhanced plugins.

    This class provides a common structure, error handling framework, logging,
    asynchronous action support (including async generators for streaming output),
    progress reporting, and state persistence capabilities for all plugins. 
    Concrete plugins should inherit from this class and implement their specific actions as methods.

    Attributes:
        plugin_id (str): The unique identifier of the plugin.
        plugin_version (str): The version of the plugin.
        config (dict): Plugin-specific configuration.
        logger (logging.Logger): A logger instance for the plugin.
        progress_callback (Optional[Callable]): An optional callback for reporting progress.
        _save_state_func (Optional[SaveStateFunc]): Function to save plugin state.
        _load_state_func (Optional[LoadStateFunc]): Function to load plugin state.
        _delete_state_func (Optional[DeleteStateFunc]): Function to delete plugin state.
    """

    def __init__(self, 
                 plugin_id: str, 
                 plugin_version: str, 
                 config: Optional[Dict[str, Any]] = None, 
                 progress_callback: Optional[Callable[..., Awaitable[None] | None]] = None,
                 save_state_func: Optional[SaveStateFunc] = None,
                 load_state_func: Optional[LoadStateFunc] = None,
                 delete_state_func: Optional[DeleteStateFunc] = None):
        """
        Initializes the BaseEnhancedPlugin.

        Args:
            plugin_id (str): The unique identifier for this plugin instance.
            plugin_version (str): The version of this plugin.
            config (dict, optional): Plugin-specific configuration. Defaults to an empty dict.
            progress_callback (Callable, optional): An optional callback function for reporting progress.
            save_state_func (Callable, optional): An async function provided by PluginManager to save state.
                                                Signature: async def save(key: str, value: Any) -> None
            load_state_func (Callable, optional): An async function provided by PluginManager to load state.
                                                Signature: async def load(key: str, default: Optional[Any] = None) -> Any
            delete_state_func (Callable, optional): An async function provided by PluginManager to delete state.
                                                  Signature: async def delete(key: str) -> bool
        """
        self.plugin_id = plugin_id
        self.plugin_version = plugin_version
        self.config = config if config is not None else {}
        self.logger = logging.getLogger(f"apex_agent.plugin.{self.plugin_id}")
        self.progress_callback = progress_callback
        
        self._save_state_func = save_state_func
        self._load_state_func = load_state_func
        self._delete_state_func = delete_state_func
        
        self.logger.info(f"Plugin 
_id=\"{self.plugin_id}\" version 
_id=\"{self.plugin_version}\" initialized. State persistence: {"enabled" if self._save_state_func else "disabled"}.")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns basic metadata associated with this plugin instance.
        The definitive metadata is typically managed by PluginManager from the plugin"s metadata file.
        """
        return {
            "id": self.plugin_id,
            "version": self.plugin_version,
            "description": "BaseEnhancedPlugin - specific description should be in child class or metadata file.",
            "actions": [] 
        }

    async def execute_action(self, action_name: str, **kwargs: Any) -> Any:
        """
        Executes a specified action with given arguments.
        Handles synchronous, asynchronous coroutine, and asynchronous generator methods.
        """
        if not hasattr(self, action_name):
            self.logger.error(f"Action 
_id=\"{action_name}\" not found in plugin 
_id=\"{self.plugin_id}\".")
            raise PluginNotImplementedError(f"Action 
_id=\"{action_name}\" is not implemented in plugin 
_id=\"{self.plugin_id}\".")
        
        action_method = getattr(self, action_name)
        self.logger.info(f"Executing action 
_id=\"{action_name}\" in plugin 
_id=\"{self.plugin_id}\" with args: {kwargs}")
        try:
            if inspect.isasyncgenfunction(action_method):
                return action_method(**kwargs)
            elif inspect.iscoroutinefunction(action_method):
                 return await action_method(**kwargs)
            else:
                return action_method(**kwargs)
        except PluginArgumentError as pae:
            self.logger.error(f"Argument error in action 
_id=\"{action_name}\" of plugin 
_id=\"{self.plugin_id}\": {pae}")
            raise 
        except PluginExecutionError as pee:
            self.logger.error(f"Execution error in action 
_id=\"{action_name}\" of plugin 
_id=\"{self.plugin_id}\": {pee}")
            raise
        except PluginError as pe:
            self.logger.error(f"Plugin-specific error during action 
_id=\"{action_name}\" of plugin 
_id=\"{self.plugin_id}\": {pe}")
            raise 
        except Exception as e:
            self.logger.exception(f"Unexpected error during action 
_id=\"{action_name}\" of plugin 
_id=\"{self.plugin_id}\": {e}")
            raise PluginExecutionError(f"An unexpected error occurred in 
_id=\"{action_name}\" of plugin 
_id=\"{self.plugin_id}\": {str(e)}") from e

    async def _report_progress(self, 
                               action_name: str, 
                               current_step: int, 
                               total_steps: Optional[int], 
                               message: str, 
                               additional_data: Optional[Dict[str, Any]] = None):
        """Protected method for plugins to report progress on long-running tasks."""
        if self.progress_callback:
            try:
                callback_args = {
                    "plugin_id": self.plugin_id,
                    "action_name": action_name,
                    "current_step": current_step,
                    "total_steps": total_steps,
                    "message": message,
                    "additional_data": additional_data if additional_data is not None else {}
                }
                if inspect.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(**callback_args)
                else:
                    self.progress_callback(**callback_args)
            except Exception as e:
                self.logger.error(f"Error invoking progress callback for action 
_id=\"{action_name}\": {e}")
        else:
            progress_log_message = f"Progress ({self.plugin_id} - {action_name}): [{current_step}/{total_steps if total_steps is not None else "N/A"}] {message}"
            if additional_data:
                progress_log_message += f" Data: {additional_data}"
            self.logger.debug(progress_log_message)

    async def _save_plugin_state(self, key: str, value: Any) -> None:
        """
        Requests saving a key-value pair to the plugin"s persistent state.
        The value must be JSON-serializable.
        Delegates to a function provided by PluginManager.
        """
        if self._save_state_func:
            try:
                await self._save_state_func(key, value)
                self.logger.debug(f"Successfully requested to save state for key 
_id=\"{key}\".")
            except Exception as e:
                self.logger.error(f"Error requesting to save state for key 
_id=\"{key}\": {e}")
                raise PluginStateError(f"Failed to save state for key 
_id=\"{key}\" in plugin 
_id=\"{self.plugin_id}\".") from e
        else:
            self.logger.warning(f"State persistence (save) is not configured for plugin 
_id=\"{self.plugin_id}\". Key 
_id=\"{key}\" not saved.")
            raise PluginStateError("State persistence (save) not available for this plugin instance.")

    async def _load_plugin_state(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Requests loading a value from the plugin"s persistent state by key.
        Delegates to a function provided by PluginManager.
        Returns the default value if the key is not found or if state persistence is not configured.
        """
        if self._load_state_func:
            try:
                value = await self._load_state_func(key, default)
                self.logger.debug(f"Successfully requested to load state for key 
_id=\"{key}\".")
                return value
            except Exception as e:
                self.logger.error(f"Error requesting to load state for key 
_id=\"{key}\": {e}")
                raise PluginStateError(f"Failed to load state for key 
_id=\"{key}\" in plugin 
_id=\"{self.plugin_id}\".") from e
        else:
            self.logger.warning(f"State persistence (load) is not configured for plugin 
_id=\"{self.plugin_id}\". Returning default for key 
_id=\"{key}\".")
            return default

    async def _delete_plugin_state(self, key: str) -> bool:
        """
        Requests deleting a key-value pair from the plugin"s persistent state.
        Delegates to a function provided by PluginManager.
        Returns True if successful or key not found (if persistence is enabled).
        Raises PluginStateError if persistence is not configured or if deletion fails.
        """
        if self._delete_state_func:
            try:
                result = await self._delete_state_func(key)
                self.logger.debug(f"Successfully requested to delete state for key 
_id=\"{key}\". Result: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error requesting to delete state for key 
_id=\"{key}\": {e}")
                raise PluginStateError(f"Failed to delete state for key 
_id=\"{key}\" in plugin 
_id=\"{self.plugin_id}\".") from e
        else:
            self.logger.warning(f"State persistence (delete) is not configured for plugin 
_id=\"{self.plugin_id}\". Key 
_id=\"{key}\" not deleted.")
            # If not configured, it's as if the key wasn't there to delete from a persistent store.
            # However, to clearly indicate the feature isn't available, raising an error is better.
            raise PluginStateError("State persistence (delete) not available for this plugin instance.")

if __name__ == "__main__":
    import asyncio

    # Example progress callback (can be async or sync)
    async def my_async_progress_handler(**kwargs: Any):
        print(f"ASYNC PROGRESS: Plugin 
_id=\"{kwargs.get("plugin_id")}\" Action 
_id=\"{kwargs.get("action_name")}\" - Step {kwargs.get("current_step")}/{kwargs.get("total_steps")}: {kwargs.get("message")}")

    # Dummy state functions for testing BaseEnhancedPlugin directly
    async def dummy_save_state(key: str, value: Any):
        print(f"[Dummy Save] Key: {key}, Value: {value}")
        # In a real scenario, this would write to a file or database
        # For testing, we can use a simple dictionary if needed for more complex tests
        # dummy_store.setdefault(plugin_id_bound_to_this_func, {})[key] = value

    async def dummy_load_state(key: str, default: Optional[Any] = None) -> Any:
        print(f"[Dummy Load] Key: {key}, Default: {default}")
        # return dummy_store.setdefault(plugin_id_bound_to_this_func, {}).get(key, default)
        return default # Simple dummy always returns default

    async def dummy_delete_state(key: str) -> bool:
        print(f"[Dummy Delete] Key: {key}")
        # if key in dummy_store.setdefault(plugin_id_bound_to_this_func, {}):
        #     del dummy_store[plugin_id_bound_to_this_func][key]
        #     return True
        return True # Simple dummy always returns true

    class MyTestPluginWithState(BaseEnhancedPlugin):
        def __init__(self, plugin_id: str, plugin_version: str, config: Optional[Dict[str, Any]] = None, 
                     progress_callback: Optional[Callable] = None, 
                     save_state_func: Optional[SaveStateFunc] = None,
                     load_state_func: Optional[LoadStateFunc] = None,
                     delete_state_func: Optional[DeleteStateFunc] = None):
            super().__init__(plugin_id, plugin_version, config, progress_callback, 
                             save_state_func, load_state_func, delete_state_func)
            self.counter = 0 # Internal, non-persistent state for this example

        async def increment_and_save(self, key_name: str):
            self.counter += 1
            await self._save_plugin_state(key_name, {"count": self.counter, "message": "Saved from plugin"})
            self.logger.info(f"Incremented counter to {self.counter} and saved to state key 
_id=\"{key_name}\".")
            return self.counter

        async def load_and_log(self, key_name: str):
            loaded_value = await self._load_plugin_state(key_name, default={"count": 0, "message": "Default"})
            self.logger.info(f"Loaded state for key 
_id=\"{key_name}\": {loaded_value}")
            if isinstance(loaded_value, dict) and "count" in loaded_value:
                self.counter = loaded_value["count"] # Sync internal counter if needed
            return loaded_value

        async def delete_counter_state(self, key_name: str):
            result = await self._delete_plugin_state(key_name)
            self.logger.info(f"Deletion of state key 
_id=\"{key_name}\" result: {result}")
            return result

    async def main():
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        print("--- Testing Plugin State Persistence (with dummy functions) ---")
        stateful_plugin = MyTestPluginWithState(
            plugin_id="com.example.stateful",
            plugin_version="0.1.0",
            save_state_func=dummy_save_state,
            load_state_func=dummy_load_state,
            delete_state_func=dummy_delete_state
        )

        # Test save
        await stateful_plugin.execute_action("increment_and_save", key_name="my_counter")
        await stateful_plugin.execute_action("increment_and_save", key_name="my_counter")

        # Test load
        loaded = await stateful_plugin.execute_action("load_and_log", key_name="my_counter")
        print(f"Value loaded by plugin: {loaded}") # Will be default due to dummy_load_state

        # Test delete
        delete_res = await stateful_plugin.execute_action("delete_counter_state", key_name="my_counter")
        print(f"Deletion result: {delete_res}")

        print("\n--- Testing Plugin State Persistence (NO functions provided) ---")
        stateful_plugin_no_funcs = MyTestPluginWithState(
            plugin_id="com.example.stateful.nofuncs",
            plugin_version="0.1.0"
        )
        try:
            await stateful_plugin_no_funcs.execute_action("increment_and_save", key_name="my_counter_nofunc")
        except PluginStateError as e:
            print(f"Caught expected PluginStateError for save: {e}")
        try:
            await stateful_plugin_no_funcs.execute_action("load_and_log", key_name="my_counter_nofunc")
        except PluginStateError as e: # Load will return default if no func, but _load_plugin_state itself won't raise if no func
            # Let's adjust the _load_plugin_state to be consistent with save/delete if no func
            print(f"Caught expected PluginStateError for load: {e}") # This might not be hit if load returns default
        # The current _load_plugin_state returns default if no func. Let's test that behavior.
        val_no_func = await stateful_plugin_no_funcs._load_plugin_state("my_key", default="test_default")
        print(f"Load with no func returned: {val_no_func}") # Should be "test_default"
        assert val_no_func == "test_default"

        try:
            await stateful_plugin_no_funcs.execute_action("delete_counter_state", key_name="my_counter_nofunc")
        except PluginStateError as e:
            print(f"Caught expected PluginStateError for delete: {e}")

    asyncio.run(main())

