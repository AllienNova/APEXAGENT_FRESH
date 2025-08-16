import asyncio
import logging
from typing import Dict, Optional, Any, Callable, Awaitable

from ..core.base_enhanced_plugin import BaseEnhancedPlugin, SaveStateFunc, LoadStateFunc, DeleteStateFunc
from ..core.exceptions import PluginArgumentError, PluginExecutionError

class ExampleStatefulPlugin(BaseEnhancedPlugin):
    """
    An example plugin demonstrating the use of state persistence features.
    It simulates managing a simple counter and a user preference.
    """
    def __init__(self, 
                 plugin_id: str, 
                 plugin_version: str, 
                 config: Optional[Dict[str, Any]] = None, 
                 progress_callback: Optional[Callable[..., Awaitable[None] | None]] = None,
                 save_state_func: Optional[SaveStateFunc] = None,
                 load_state_func: Optional[LoadStateFunc] = None,
                 delete_state_func: Optional[DeleteStateFunc] = None):
        super().__init__(plugin_id, plugin_version, config, progress_callback, 
                         save_state_func, load_state_func, delete_state_func)
        self.logger.info(f"ExampleStatefulPlugin (ID: {self.plugin_id}) initialized.")
        self._internal_counter = 0 # In-memory counter, might be synced with persistent state

    async def initialize_counter_from_state(self, counter_key: str = "session_counter"):
        """Loads the counter from persistent state during plugin initialization or on demand."""
        try:
            state_data = await self._load_plugin_state(counter_key, default={"value": 0})
            if isinstance(state_data, dict) and "value" in state_data:
                self._internal_counter = int(state_data["value"])
                self.logger.info(f"Counter initialized from state key 
_id=\"{counter_key}\" to: {self._internal_counter}")
            else:
                self.logger.warning(f"Could not initialize counter from state key 
_id=\"{counter_key}\", using default 0. Loaded: {state_data}")
                self._internal_counter = 0
                # Optionally save the default state if it wasn_t there
                await self._save_plugin_state(counter_key, {"value": self._internal_counter})
        except Exception as e:
            self.logger.error(f"Error initializing counter from state: {e}")
            self._internal_counter = 0 # Fallback to default
        return self._internal_counter

    async def increment_counter(self, counter_key: str = "session_counter", increment_by: int = 1) -> int:
        """Increments an internal counter and saves it to persistent state."""
        if not isinstance(increment_by, int):
            raise PluginArgumentError("Argument \"increment_by\" must be an integer.")
        
        # Load current state to ensure we are not overwriting if multiple instances or for resilience
        # For a simple counter, this might be overkill if only one agent instance uses it,
        # but good practice for more complex shared state.
        # Alternatively, assume _internal_counter is the source of truth if initialized correctly.
        current_state = await self._load_plugin_state(counter_key, default={"value": self._internal_counter})
        self._internal_counter = current_state.get("value", self._internal_counter) + increment_by
        
        await self._save_plugin_state(counter_key, {"value": self._internal_counter})
        self.logger.info(f"Counter incremented to {self._internal_counter} and saved to state key 
_id=\"{counter_key}\".")
        return self._internal_counter

    async def get_counter(self, counter_key: str = "session_counter") -> int:
        """Retrieves the counter value from persistent state."""
        state_data = await self._load_plugin_state(counter_key, default={"value": 0})
        return state_data.get("value", 0)

    async def set_preference(self, pref_key: str, pref_value: Any) -> None:
        """Saves a user preference to persistent state."""
        if not isinstance(pref_key, str) or not pref_key:
            raise PluginArgumentError("Argument \"pref_key\" must be a non-empty string.")
        await self._save_plugin_state(pref_key, {"preference": pref_value})
        self.logger.info(f"Preference 
_id=\"{pref_key}\" set to 
_id=\"{pref_value}\" and saved.")

    async def get_preference(self, pref_key: str, default_value: Optional[Any] = None) -> Any:
        """Retrieves a user preference from persistent state."""
        state_data = await self._load_plugin_state(pref_key, default={"preference": default_value})
        return state_data.get("preference", default_value)

    async def delete_preference(self, pref_key: str) -> bool:
        """Deletes a user preference from persistent state."""
        result = await self._delete_plugin_state(pref_key)
        self.logger.info(f"Deletion of preference key 
_id=\"{pref_key}\" result: {result}")
        return result

    async def try_save_non_serializable(self, key: str = "bad_data"):
        """Attempts to save non-JSON-serializable data to test error handling."""
        # A set is not directly JSON serializable by default json.dump
        bad_value = {1, 2, 3}
        self.logger.info(f"Attempting to save non-serializable data for key 
_id=\"{key}\".")
        await self._save_plugin_state(key, bad_value)
        # This line should not be reached if error handling is correct in PluginManager/BaseEnhancedPlugin
        self.logger.warning("Non-serializable data was unexpectedly saved without error.") 

# Example of how this plugin might be used (for direct testing or as a script)
# This would typically be orchestrated by the PluginManager
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, 
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Dummy state functions for direct testing of ExampleStatefulPlugin
    # In a real scenario, these are provided by PluginManager
    _plugin_store: Dict[str, Dict[str, Any]] = {}

    async def _dummy_save_state(plugin_id_bound: str, key: str, value: Any):
        _plugin_store.setdefault(plugin_id_bound, {})[key] = value
        print(f"[DUMMY SAVE] Plugin 
_id=\"{plugin_id_bound}\", Key: {key}, Value: {value}")

    async def _dummy_load_state(plugin_id_bound: str, key: str, default: Optional[Any] = None) -> Any:
        val = _plugin_store.get(plugin_id_bound, {}).get(key, default)
        print(f"[DUMMY LOAD] Plugin 
_id=\"{plugin_id_bound}\", Key: {key}, Loaded: {val}")
        return val

    async def _dummy_delete_state(plugin_id_bound: str, key: str) -> bool:
        if plugin_id_bound in _plugin_store and key in _plugin_store[plugin_id_bound]:
            del _plugin_store[plugin_id_bound][key]
            print(f"[DUMMY DELETE] Plugin 
_id=\"{plugin_id_bound}\", Key: {key} - Deleted")
            return True
        print(f"[DUMMY DELETE] Plugin 
_id=\"{plugin_id_bound}\", Key: {key} - Not found")
        return False # Or True if key not found is also considered success

    async def run_stateful_plugin_demo():
        plugin_id_for_demo = "com.example.stateful.demo"
        
        # Bind dummy functions to a specific plugin ID for this demo
        bound_save = lambda k, v: _dummy_save_state(plugin_id_for_demo, k, v)
        bound_load = lambda k, d=None: _dummy_load_state(plugin_id_for_demo, k, d)
        bound_delete = lambda k: _dummy_delete_state(plugin_id_for_demo, k)

        stateful_plugin = ExampleStatefulPlugin(
            plugin_id=plugin_id_for_demo,
            plugin_version="1.0.0",
            save_state_func=bound_save,
            load_state_func=bound_load,
            delete_state_func=bound_delete
        )

        print("\n--- Testing Stateful Plugin Demo ---")
        
        # Initialize counter
        await stateful_plugin.execute_action("initialize_counter_from_state", counter_key="demo_counter")
        
        # Increment counter a few times
        await stateful_plugin.execute_action("increment_counter", counter_key="demo_counter", increment_by=5)
        count = await stateful_plugin.execute_action("increment_counter", counter_key="demo_counter")
        print(f"Counter after increments: {count}")
        assert count == 6 # 0 (init) + 5 + 1

        # Get counter directly
        retrieved_count = await stateful_plugin.execute_action("get_counter", counter_key="demo_counter")
        print(f"Retrieved counter: {retrieved_count}")
        assert retrieved_count == 6

        # Set and get a preference
        await stateful_plugin.execute_action("set_preference", pref_key="user_theme", pref_value="dark")
        theme = await stateful_plugin.execute_action("get_preference", pref_key="user_theme")
        print(f"User theme: {theme}")
        assert theme == "dark"

        # Get a non-existent preference with default
        font = await stateful_plugin.execute_action("get_preference", pref_key="user_font", default_value="Arial")
        print(f"User font (defaulted): {font}")
        assert font == "Arial"

        # Delete preference
        del_result = await stateful_plugin.execute_action("delete_preference", pref_key="user_theme")
        print(f"Deletion of theme preference result: {del_result}")
        assert del_result is True
        theme_after_delete = await stateful_plugin.execute_action("get_preference", pref_key="user_theme", default_value="light")
        print(f"Theme after delete (defaulted): {theme_after_delete}")
        assert theme_after_delete == "light"

        print("\n--- Stateful Plugin Demo Complete ---")

    asyncio.run(run_stateful_plugin_demo())

