import unittest
import asyncio
import os
import json
import shutil
import logging
from typing import Dict, Any, Optional

from agent_project.src.plugin_manager import PluginManager
from agent_project.src.plugins.example_stateful_plugin import ExampleStatefulPlugin # Assuming it exists
from agent_project.src.core.exceptions import PluginStateError, PluginArgumentError

# Configure basic logging for tests (optional, can be helpful for debugging)
logging.basicConfig(level=logging.DEBUG, format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\
)

# Define temporary directories for test plugins and their states
TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS = "/home/ubuntu/agent_project/tests/temp_state_plugins_root"
TEST_PLUGIN_STATES_DIR = "/home/ubuntu/agent_project/tests/temp_plugin_states_storage"
PLUGIN_SCHEMA_PATH_FOR_STATE_TESTS = "/home/ubuntu/agent_project/docs/plugin_metadata_schema.json"

# Define the specific directory for our ExampleStatefulPlugin code and metadata within the root
EXAMPLE_STATEFUL_PLUGIN_CODE_DIR_NAME = "example_stateful_plugin_code"
EXAMPLE_STATEFUL_PLUGIN_ID = "com.example.stateful.test"

class TestPluginStatePersistence(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the global schema exists (it should from previous steps)
        if not os.path.exists(PLUGIN_SCHEMA_PATH_FOR_STATE_TESTS):
            raise FileNotFoundError(f"CRITICAL: Plugin schema not found at {PLUGIN_SCHEMA_PATH_FOR_STATE_TESTS} for tests.")

        # Clean up and create temporary directories
        for dir_path in [TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS, TEST_PLUGIN_STATES_DIR]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            os.makedirs(dir_path, exist_ok=True)

        # Setup the ExampleStatefulPlugin for discovery by PluginManager
        # This involves creating a directory structure and metadata file.
        plugin_code_source_path = "/home/ubuntu/agent_project/src/plugins/example_stateful_plugin.py"
        if not os.path.exists(plugin_code_source_path):
            raise FileNotFoundError(f"ExampleStatefulPlugin source code not found at {plugin_code_source_path}")

        # The PluginManager scans plugin_dirs. Each item in plugin_dirs is a directory containing plugin folders.
        # So, TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS will contain EXAMPLE_STATEFUL_PLUGIN_CODE_DIR_NAME
        cls.plugin_dir_for_discovery = os.path.join(TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS, EXAMPLE_STATEFUL_PLUGIN_CODE_DIR_NAME)
        os.makedirs(cls.plugin_dir_for_discovery, exist_ok=True)

        # Copy the plugin code into this directory. It needs to be importable.
        # The entry_point will be relative to agent_project.src.
        # Let_s place it such that the entry_point can be, e.g., 
        # `tests.temp_state_plugins_root.example_stateful_plugin_code.example_stateful_plugin.ExampleStatefulPlugin`
        # This requires `tests.temp_state_plugins_root` to be part of the module path for PluginManager_s import logic.
        # PluginManager uses `agent_project.src.{module_name_from_entry_point}`.
        # So, entry_point should be `plugins.{EXAMPLE_STATEFUL_PLUGIN_CODE_DIR_NAME}.example_stateful_plugin.ExampleStatefulPlugin`
        # if we copy `example_stateful_plugin.py` into a structure like:
        # `/home/ubuntu/agent_project/src/plugins/{EXAMPLE_STATEFUL_PLUGIN_CODE_DIR_NAME}/example_stateful_plugin.py`
        # For testing, it_s easier to adjust the PluginManager_s base path or use a more direct way if possible.
        # Given the current PluginManager import logic, we_ll simulate the structure under `agent_project/src/plugins`
        # by making our TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS act as that `plugins` directory.

        shutil.copy(plugin_code_source_path, os.path.join(cls.plugin_dir_for_discovery, "example_stateful_plugin.py"))
        # Create an __init__.py to make it a package
        with open(os.path.join(cls.plugin_dir_for_discovery, "__init__.py"), "w") as f:
            f.write("") # Empty __init__.py is fine

        # Create metadata for ExampleStatefulPlugin
        metadata = {
            "name": "Test Example Stateful Plugin",
            "id": EXAMPLE_STATEFUL_PLUGIN_ID,
            "version": "1.0.0",
            "description": "A test plugin demonstrating state persistence.",
            "author": "Test Framework",
            # Entry point relative to agent_project.src
            # The plugin file is example_stateful_plugin.py inside the EXAMPLE_STATEFUL_PLUGIN_CODE_DIR_NAME directory
            # which is itself inside TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS (which acts as the `plugins` folder for the test manager)
            "entry_point": f"tests.temp_state_plugins_root.{EXAMPLE_STATEFUL_PLUGIN_CODE_DIR_NAME}.example_stateful_plugin.ExampleStatefulPlugin",
            "actions": [
                {"name": "initialize_counter_from_state", "description": "Initializes counter."},
                {"name": "increment_counter", "description": "Increments and saves counter."},
                {"name": "get_counter", "description": "Gets counter from state."},
                {"name": "set_preference", "description": "Sets a preference."},
                {"name": "get_preference", "description": "Gets a preference."},
                {"name": "delete_preference", "description": "Deletes a preference."},
                {"name": "try_save_non_serializable", "description": "Tests saving bad data."}
            ]
        }
        with open(os.path.join(cls.plugin_dir_for_discovery, "plugin.json"), "w") as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary directories
        for dir_path in [TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS, TEST_PLUGIN_STATES_DIR]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)

    async def asyncSetUp(self):
        # PluginManager needs plugin_dirs to be a list of directories *containing* plugin folders.
        # Here, TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS contains EXAMPLE_STATEFUL_PLUGIN_CODE_DIR_NAME.
        # However, the entry point is constructed as `agent_project.src.{entry_point_module}`.
        # This means the test plugin directory needs to be locatable via that path.
        # A workaround for testing is to ensure `agent_project.src.tests.temp_state_plugins_root...` is importable.
        # This usually means `agent_project/src` must be in PYTHONPATH, and `tests` must be a package.
        # For simplicity, we assume the test execution environment handles Python path correctly.
        self.manager = PluginManager(
            plugin_dirs=[TEST_PLUGINS_ROOT_DIR_FOR_STATE_TESTS], # Scan the directory containing our test plugin package
            schema_path=PLUGIN_SCHEMA_PATH_FOR_STATE_TESTS,
            plugin_states_root_dir=TEST_PLUGIN_STATES_DIR
        )
        # Ensure the test plugin is discovered
        self.assertIn(EXAMPLE_STATEFUL_PLUGIN_ID, self.manager.plugin_metadata_registry, 
                      f"Test plugin {EXAMPLE_STATEFUL_PLUGIN_ID} not discovered. Registry: {self.manager.plugin_metadata_registry.keys()}")
        self.plugin_instance = self.manager.get_plugin_instance(EXAMPLE_STATEFUL_PLUGIN_ID)
        self.assertIsNotNone(self.plugin_instance, f"Failed to get instance of {EXAMPLE_STATEFUL_PLUGIN_ID}")

    def _get_expected_state_file_path(self, plugin_id: str, key: str) -> str:
        # Helper to get the path where PluginManager should store the state file
        safe_key_filename = "".join(c if c.isalnum() else \"_\" for c in key) + ".json"
        return os.path.join(TEST_PLUGIN_STATES_DIR, plugin_id, safe_key_filename)

    async def test_save_and_load_state(self):
        counter_key = "my_test_counter"
        pref_key = "my_test_preference"

        # Initialize counter (should load default 0 and save it)
        await self.plugin_instance.execute_action("initialize_counter_from_state", counter_key=counter_key)
        counter_state_file = self._get_expected_state_file_path(EXAMPLE_STATEFUL_PLUGIN_ID, counter_key)
        self.assertTrue(os.path.exists(counter_state_file))
        with open(counter_state_file, \"r\") as f:
            data = json.load(f)
        self.assertEqual(data, {"value": 0})

        # Increment counter
        incremented_value = await self.plugin_instance.execute_action("increment_counter", counter_key=counter_key, increment_by=5)
        self.assertEqual(incremented_value, 5)
        with open(counter_state_file, \"r\") as f:
            data = json.load(f)
        self.assertEqual(data, {"value": 5})

        # Get counter
        retrieved_counter = await self.plugin_instance.execute_action("get_counter", counter_key=counter_key)
        self.assertEqual(retrieved_counter, 5)

        # Set preference
        pref_value = {"theme": "dark", "notifications": True}
        await self.plugin_instance.execute_action("set_preference", pref_key=pref_key, pref_value=pref_value)
        pref_state_file = self._get_expected_state_file_path(EXAMPLE_STATEFUL_PLUGIN_ID, pref_key)
        self.assertTrue(os.path.exists(pref_state_file))
        with open(pref_state_file, \"r\") as f:
            data = json.load(f)
        self.assertEqual(data, {"preference": pref_value})

        # Get preference
        retrieved_pref = await self.plugin_instance.execute_action("get_preference", pref_key=pref_key)
        self.assertEqual(retrieved_pref, pref_value)

    async def test_load_non_existent_state_with_default(self):
        non_existent_key = "this_key_does_not_exist"
        default_val = {"message": "I am a default"}
        loaded_value = await self.plugin_instance.execute_action("get_preference", pref_key=non_existent_key, default_value=default_val)
        self.assertEqual(loaded_value, default_val)
        # Ensure no file was created for a non-existent key on load
        state_file = self._get_expected_state_file_path(EXAMPLE_STATEFUL_PLUGIN_ID, non_existent_key)
        self.assertFalse(os.path.exists(state_file))

    async def test_delete_state(self):
        key_to_delete = "to_be_deleted_pref"
        initial_value = "temporary_value"

        # Save something first
        await self.plugin_instance.execute_action("set_preference", pref_key=key_to_delete, pref_value=initial_value)
        state_file = self._get_expected_state_file_path(EXAMPLE_STATEFUL_PLUGIN_ID, key_to_delete)
        self.assertTrue(os.path.exists(state_file), "State file should exist before deletion.")

        # Delete it
        delete_result = await self.plugin_instance.execute_action("delete_preference", pref_key=key_to_delete)
        self.assertTrue(delete_result, "Deletion should be reported as successful.")
        self.assertFalse(os.path.exists(state_file), "State file should not exist after deletion.")

        # Try deleting again (should still be successful, idempotent-like)
        delete_again_result = await self.plugin_instance.execute_action("delete_preference", pref_key=key_to_delete)
        self.assertTrue(delete_again_result)

    async def test_save_non_serializable_data(self):
        # The ExampleStatefulPlugin has a specific action for this
        with self.assertRaises(PluginStateError) as cm:
            await self.plugin_instance.execute_action("try_save_non_serializable", key="bad_data_key")
        self.assertIn("not JSON serializable", str(cm.exception).lower())
        # Ensure no corrupted file was left (or an empty one)
        bad_data_file = self._get_expected_state_file_path(EXAMPLE_STATEFUL_PLUGIN_ID, "bad_data_key")
        self.assertFalse(os.path.exists(bad_data_file), "File for non-serializable data should not exist or be cleaned up.")

    async def test_state_persistence_without_configured_functions(self):
        # Create a plugin instance directly, without state functions
        plugin_no_state = ExampleStatefulPlugin(
            plugin_id="com.example.nostate",
            plugin_version="1.0.0"
            # No save_state_func, load_state_func, delete_state_func provided
        )

        with self.assertRaises(PluginStateError) as cm_save:
            await plugin_no_state._save_plugin_state("some_key", "some_value")
        self.assertIn("not available", str(cm_save.exception))

        # Load should return default if not configured
        loaded_val = await plugin_no_state._load_plugin_state("some_key", default="is_default")
        self.assertEqual(loaded_val, "is_default")

        with self.assertRaises(PluginStateError) as cm_delete:
            await plugin_no_state._delete_plugin_state("some_key")
        self.assertIn("not available", str(cm_delete.exception))

if __name__ == "__main__":
    unittest.main()
