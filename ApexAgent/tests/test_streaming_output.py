import unittest
import asyncio
import inspect
import os
import json
import shutil
from typing import List, Dict, Any, Optional, AsyncGenerator
from unittest.mock import AsyncMock

from agent_project.src.plugin_manager import PluginManager
from agent_project.src.plugins.example_streaming_plugin import ExampleStreamingPlugin # Assuming it's here
from agent_project.src.core.exceptions import PluginArgumentError, PluginExecutionError, PluginNotImplementedError

# Define a temporary directory for test plugins
TEST_PLUGINS_TEMP_DIR = "/home/ubuntu/agent_project/tests/temp_streaming_plugins"
PLUGIN_SCHEMA_PATH = "/home/ubuntu/agent_project/docs/plugin_metadata_schema.json"

class TestStreamingOutputHandling(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the schema exists (it should from previous steps)
        if not os.path.exists(PLUGIN_SCHEMA_PATH):
            raise FileNotFoundError(f"CRITICAL: Plugin schema not found at {PLUGIN_SCHEMA_PATH} for tests.")
        
        # Create a temporary directory for our test plugin
        if os.path.exists(TEST_PLUGINS_TEMP_DIR):
            shutil.rmtree(TEST_PLUGINS_TEMP_DIR)
        os.makedirs(TEST_PLUGINS_TEMP_DIR)

        # Create the ExampleStreamingPlugin structure for discovery
        plugin_name = "example_streaming_plugin"
        plugin_dir = os.path.join(TEST_PLUGINS_TEMP_DIR, plugin_name)
        os.makedirs(plugin_dir)

        # Create metadata for ExampleStreamingPlugin
        metadata = {
            "name": "Example Streaming Plugin",
            "id": "com.example.streamer",
            "version": "1.0.0",
            "description": "A plugin demonstrating streaming output.",
            "author": "Test Framework",
            "entry_point": f"plugins.{plugin_name}.example_streaming_plugin.ExampleStreamingPlugin",
            "actions": [
                {
                    "name": "generate_text_stream", 
                    "description": "Streams text chunks.",
                    "streams_output": True # Explicitly mark as streaming
                },
                {
                    "name": "stream_with_error", 
                    "description": "Streams items then errors.",
                    "streams_output": True
                },
                {
                    "name": "non_streaming_action", 
                    "description": "A regular non-streaming action."
                }
            ]
        }
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Copy the actual plugin code to the temp directory to make it discoverable
        # This assumes the ExampleStreamingPlugin is in agent_project.src.plugins.example_streaming_plugin.py
        # Adjust path if necessary
        source_plugin_file = "/home/ubuntu/agent_project/src/plugins/example_streaming_plugin.py"
        # The entry point implies plugins.example_streaming_plugin.example_streaming_plugin.ExampleStreamingPlugin
        # So the file should be plugins/example_streaming_plugin/example_streaming_plugin.py relative to src
        # Let's adjust the temp structure to match this expectation for importlib
        # The PluginManager's current _load_plugin_class uses f"agent_project.src.{module_name}"
        # So, if entry_point is "plugins.example_streaming_plugin.example_streaming_plugin.ExampleStreamingPlugin",
        # module_name becomes "plugins.example_streaming_plugin.example_streaming_plugin"
        # This means the file needs to be at: TEST_PLUGINS_TEMP_DIR/example_streaming_plugin/example_streaming_plugin.py
        # And TEST_PLUGINS_TEMP_DIR needs to be seen as `agent_project.src.plugins` effectively for the test manager
        # This is getting complicated. For unit testing PluginManager's invoke, it's easier if we can mock plugin loading
        # or directly provide an instance. However, to test the full invoke_plugin_action path, discovery is involved.

        # Let's simplify: The PluginManager expects plugin_dirs to be a list of dirs *containing* plugin folders.
        # The entry_point in metadata should be relative to `agent_project.src`
        # So, if `ExampleStreamingPlugin` is at `agent_project/src/plugins/example_streaming_plugin.py`
        # and its class is `ExampleStreamingPlugin`, the entry point in metadata should be
        # `plugins.example_streaming_plugin.ExampleStreamingPlugin`
        # The metadata above uses `plugins.example_streaming_plugin.example_streaming_plugin.ExampleStreamingPlugin`
        # This implies a file structure like: `plugins_dir/example_streaming_plugin/example_streaming_plugin.py`
        # Let's ensure our temp setup matches this for the test.

        target_plugin_file_dir = os.path.join(TEST_PLUGINS_TEMP_DIR, "example_streaming_plugin") # This is the dir for `com.example.streamer`
        # The entry point is plugins.example_streaming_plugin.example_streaming_plugin.ExampleStreamingPlugin
        # This means the file `example_streaming_plugin.py` should be inside `target_plugin_file_dir`
        # And the module path for importlib will be based on how `plugin_dirs` is structured relative to `sys.path`
        # The current PluginManager constructs module_name = f"agent_project.src.{module_name_from_entry_point}"
        # If entry_point is "plugins.mypluginmodule.MyPluginClass", then it tries to import "agent_project.src.plugins.mypluginmodule"
        # This means the test plugin directory (TEST_PLUGINS_TEMP_DIR) should be structured as if it's `agent_project/src/plugins`
        # So, TEST_PLUGINS_TEMP_DIR will contain `example_streaming_plugin` (folder), which contains `example_streaming_plugin.py` (file)
        # And the plugin_dirs for PluginManager init should be `[TEST_PLUGINS_TEMP_DIR]`
        # And the entry point in metadata should be `example_streaming_plugin.example_streaming_plugin.ExampleStreamingPlugin`
        # if TEST_PLUGINS_TEMP_DIR is treated as the `plugins` folder itself.

        # Let's adjust metadata and file path for clarity and current PluginManager behavior.
        # We'll make TEST_PLUGINS_TEMP_DIR the directory *containing* the plugin folder `example_streaming_plugin_code`
        plugin_code_dir_name = "example_streaming_plugin_code"
        plugin_actual_code_dir = os.path.join(TEST_PLUGINS_TEMP_DIR, plugin_code_dir_name)
        os.makedirs(plugin_actual_code_dir, exist_ok=True)
        shutil.copy(source_plugin_file, os.path.join(plugin_actual_code_dir, "example_streaming_plugin.py"))
        # Create an __init__.py in plugin_code_dir_name to make it a package
        with open(os.path.join(plugin_actual_code_dir, "__init__.py"), "w") as f:
            f.write("")

        metadata["entry_point"] = f"{plugin_code_dir_name}.example_streaming_plugin.ExampleStreamingPlugin"
        # This means PluginManager will try to import agent_project.src.plugins_test_temp_streaming.example_streaming_plugin_code.example_streaming_plugin
        # This requires TEST_PLUGINS_TEMP_DIR to be effectively `agent_project.src.plugins_test_temp_streaming`
        # This is still a bit off. The PluginManager assumes `plugin_dirs` are scanned, and entry points are relative to `agent_project.src`
        # Let's assume `plugin_dirs` for PluginManager is `["/home/ubuntu/agent_project/src/plugins"]` for real use.
        # For testing, we need to replicate a similar structure or mock parts of PluginManager.

        # Given the complexity of perfectly mimicking the import structure for dynamic loading in tests,
        # we will focus on testing the streaming logic assuming the plugin instance is correctly obtained.
        # We can directly instantiate ExampleStreamingPlugin for some tests and mock get_plugin_instance for others.
        # However, the request is to test PluginManager's invoke_plugin_action.

        # Let's try to make the discovery work for the test by placing the temp dir correctly in the hierarchy for imports.
        # The PluginManager does: module = importlib.import_module(f"agent_project.src.{module_name}")
        # If entry_point is "my_plugin_module.MyPluginClass", it imports "agent_project.src.my_plugin_module"
        # So, `my_plugin_module.py` (or `my_plugin_module/__init__.py`) must be in `agent_project/src/`
        # This is not how plugins are typically structured in subdirs.

        # Re-evaluating PluginManager's _load_plugin_class and discover_plugins:
        # discover_plugins creates `module_path` like `plugins_test_temp_manager.dummy_manager_plugin_one` if plugin_dir is `.../src/plugins_test_temp_manager/dummy_manager_plugin_one`
        # entry_point is `plugins.dummy_manager_plugin_one.main.DummyManagerPluginOne`
        # _load_plugin_class uses `full_module_name = f"agent_project.src.{module_name_from_entry_point}"`
        # This means entry_point in metadata *must* be relative to `agent_project.src`
        # So, for `ExampleStreamingPlugin` at `/home/ubuntu/agent_project/src/plugins/example_streaming_plugin.py`,
        # the entry_point should be `plugins.example_streaming_plugin.ExampleStreamingPlugin`.

        # Let's use the real plugin path for the ExampleStreamingPlugin for the test PluginManager
        # and ensure its metadata is correctly placed for discovery.
        # We'll create a temporary metadata file in the actual plugin's directory if it doesn't exist.
        cls.example_plugin_dir = "/home/ubuntu/agent_project/src/plugins/example_streaming_plugin_for_test"
        os.makedirs(cls.example_plugin_dir, exist_ok=True)
        shutil.copy("/home/ubuntu/agent_project/src/plugins/example_streaming_plugin.py", os.path.join(cls.example_plugin_dir, "__init__.py")) # Make it a package
        # or copy it as example_streaming_plugin.py and adjust entry point
        # shutil.copy("/home/ubuntu/agent_project/src/plugins/example_streaming_plugin.py", os.path.join(cls.example_plugin_dir, "actual_plugin_file.py"))

        test_metadata = {
            "name": "Test Example Streaming Plugin",
            "id": "com.example.streamer.test", # Unique ID for test
            "version": "1.0.1",
            "description": "A test instance of the streaming plugin.",
            "author": "Test Framework",
            "entry_point": "plugins.example_streaming_plugin_for_test.ExampleStreamingPlugin", # Assumes __init__.py has the class
            "actions": metadata["actions"] # Reuse actions from above
        }
        with open(os.path.join(cls.example_plugin_dir, "plugin.json"), "w") as f:
            json.dump(test_metadata, f, indent=2)
        
        # The PluginManager will scan a directory *containing* cls.example_plugin_dir
        # So, if cls.example_plugin_dir is .../src/plugins/example_streaming_plugin_for_test
        # then plugin_dirs for PluginManager should be ["/home/ubuntu/agent_project/src/plugins"]
        cls.test_plugin_root_scan_dir = "/home/ubuntu/agent_project/src/plugins"

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.example_plugin_dir):
             shutil.rmtree(cls.example_plugin_dir)
        # if os.path.exists(TEST_PLUGINS_TEMP_DIR):
        #     shutil.rmtree(TEST_PLUGINS_TEMP_DIR)

    async def asyncSetUp(self):
        self.manager = PluginManager(plugin_dirs=[self.test_plugin_root_scan_dir], schema_path=PLUGIN_SCHEMA_PATH)
        # Ensure the test plugin is discovered
        self.assertIn("com.example.streamer.test", self.manager.plugin_metadata_registry)

    async def test_invoke_streaming_action_successful(self):
        plugin_id = "com.example.streamer.test"
        action_name = "generate_text_stream"
        num_chunks = 3
        
        result_stream = await self.manager.invoke_plugin_action(plugin_id, action_name, prompt="Test Stream", num_chunks=num_chunks)
        
        self.assertTrue(inspect.isasyncgen(result_stream), "Action did not return an async generator")
        
        consumed_chunks = []
        async for chunk in result_stream:
            consumed_chunks.append(chunk)
            self.assertIsInstance(chunk, str)
        
        self.assertEqual(len(consumed_chunks), num_chunks, "Incorrect number of chunks received")
        self.assertTrue(all(f"Chunk {i+1}/{num_chunks}" in consumed_chunks[i] for i in range(num_chunks)))

    async def test_invoke_streaming_action_with_error_during_stream(self):
        plugin_id = "com.example.streamer.test"
        action_name = "stream_with_error"
        total_items = 5
        error_at = 3

        result_stream = await self.manager.invoke_plugin_action(plugin_id, action_name, total_items=total_items, error_at_item=error_at)
        self.assertTrue(inspect.isasyncgen(result_stream))

        consumed_items_before_error = []
        with self.assertRaises(PluginExecutionError) as cm:
            async for item in result_stream:
                consumed_items_before_error.append(item)
        
        self.assertEqual(len(consumed_items_before_error), error_at - 1, "Incorrect number of items received before error")
        self.assertIn(f"Simulated error at item {error_at}", str(cm.exception))

    async def test_invoke_non_streaming_action(self):
        plugin_id = "com.example.streamer.test"
        action_name = "non_streaming_action"
        test_value = 20
        
        result = await self.manager.invoke_plugin_action(plugin_id, action_name, value=test_value)
        
        self.assertFalse(inspect.isasyncgen(result), "Non-streaming action unexpectedly returned a generator")
        self.assertEqual(result, test_value * 2)

    async def test_invoke_action_with_argument_error(self):
        plugin_id = "com.example.streamer.test"
        action_name = "generate_text_stream"
        with self.assertRaises(PluginArgumentError):
            await self.manager.invoke_plugin_action(plugin_id, action_name, prompt="Valid", num_chunks=-1) # Invalid num_chunks

    async def test_invoke_non_existent_action(self):
        plugin_id = "com.example.streamer.test"
        with self.assertRaises(PluginNotImplementedError):
            await self.manager.invoke_plugin_action(plugin_id, "this_action_does_not_exist")

    async def test_invoke_action_on_non_existent_plugin(self):
        with self.assertRaises(PluginNotImplementedError): # PluginManager raises this if plugin can't be instanced
            await self.manager.invoke_plugin_action("com.example.nonexistentplugin", "any_action")

if __name__ == "__main__":
    unittest.main()
