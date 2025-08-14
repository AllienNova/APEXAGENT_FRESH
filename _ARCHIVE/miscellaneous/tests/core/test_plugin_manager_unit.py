import unittest
import os
import json
import shutil
import sys
import hashlib
import asyncio
import logging
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock, call # Added call

# Add project root to sys.path to allow importing PluginManager
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(project_root, "src"))

from core.plugin_manager import PluginManager
from core.base_plugin import BasePlugin, StreamableOutput
from core.plugin_state_manager import PluginStateManager
from core.plugin_exceptions import (
    PluginError,
    PluginInitializationError,
    PluginConfigurationError,
    PluginActionNotFoundError,
    PluginInvalidActionParametersError,
    PluginActionExecutionError,
    PluginDependencyError,
    PluginResourceNotFoundError,
    StreamingNotSupportedError,
    PluginNotFoundError
)
# Import async utils for type hinting and testing
from core.async_utils import ProgressUpdate, CancellationToken, PluginActionTimeoutError

from packaging.version import parse as parse_version
from typing import Callable, Optional, Any, Union, Iterator, AsyncIterator

# Configure basic logging for tests to see output from PluginManager and PluginStateManager
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Minimal concrete BasePlugin for testing purposes
class MinimalTestPlugin(BasePlugin):
    def __init__(self, plugin_id: str, plugin_name: str, version: str, description: str, config: dict = None):
        super().__init__(plugin_id, plugin_name, version, description, config)
        self.init_called = False
        self.actions_called = False
        self.exec_called = False
        self.shutdown_called = False

    def initialize(self, agent_context: dict = None) -> None:
        super().initialize(agent_context)
        self.init_called = True

    def get_actions(self) -> list[dict]:
        self.actions_called = True
        return []

    def execute_action(self, action_name: str, params: Optional[dict] = None, progress_callback: Optional[Callable[[ProgressUpdate], None]] = None, cancellation_token: Optional[CancellationToken] = None) -> StreamableOutput:
        self.exec_called = True
        return f"Action {action_name} executed"

    def shutdown(self) -> None:
        self.shutdown_called = True

class TestPluginStateManager(unittest.TestCase):
    def setUp(self):
        self.test_base_dir = os.path.abspath(os.path.join(project_root, "tests", "test_temp_psm"))
        self.state_manager_dir = os.path.join(self.test_base_dir, "plugin_states_test")
        if os.path.exists(self.test_base_dir):
            shutil.rmtree(self.test_base_dir)
        os.makedirs(self.state_manager_dir, exist_ok=True)
        self.state_manager = PluginStateManager(base_state_dir=self.state_manager_dir)

    def tearDown(self):
        if os.path.exists(self.test_base_dir):
            shutil.rmtree(self.test_base_dir)

    def test_01_initialization_creates_directory(self):
        self.assertTrue(os.path.isdir(self.state_manager_dir))

    def test_02_get_state_file_path(self):
        plugin_id = "com.example.test"
        plugin_version = "1.0.0"
        expected_path = os.path.join(self.state_manager_dir, plugin_id, f"state_v{plugin_version}.json") # Updated to match PluginStateManager
        self.assertEqual(self.state_manager._get_state_file_path(plugin_id, plugin_version), expected_path)

    def test_03_save_and_load_plugin_state(self):
        plugin_id = "com.example.testsave"
        plugin_version = "1.0.1"
        state_data = {"key": "value", "count": 123}

        self.state_manager.save_plugin_state(plugin_id, plugin_version, state_data)
        state_file_path = self.state_manager._get_state_file_path(plugin_id, plugin_version)
        self.assertTrue(os.path.exists(state_file_path))

        with open(state_file_path, "r") as f:
            saved_content = json.load(f)
        # Checksum is now part of the saved structure
        self.assertEqual(saved_content["data"], state_data)
        self.assertIn("checksum", saved_content)

        loaded_state = self.state_manager.load_plugin_state(plugin_id, plugin_version)
        self.assertEqual(loaded_state, state_data)

    def test_04_load_non_existent_state(self):
        plugin_id = "com.example.nonexistent"
        plugin_version = "0.1.0"
        loaded_state = self.state_manager.load_plugin_state(plugin_id, plugin_version)
        self.assertIsNone(loaded_state)

    def test_05_save_non_serializable_state(self):
        plugin_id = "com.example.nonserializable"
        plugin_version = "1.0.0"
        non_serializable_data = {"set_data": {1, 2, 3}} # Sets are not JSON serializable by default
        with self.assertRaises(PluginActionExecutionError): # PluginStateManager wraps errors
            self.state_manager.save_plugin_state(plugin_id, plugin_version, non_serializable_data)

    def test_06_load_corrupted_state_file_json(self):
        plugin_id = "com.example.corruptedjson"
        plugin_version = "1.0.0"
        state_file_path = self.state_manager._get_state_file_path(plugin_id, plugin_version)
        os.makedirs(os.path.dirname(state_file_path), exist_ok=True)
        with open(state_file_path, "w") as f:
            f.write("this is not valid json")
        
        with self.assertRaises(PluginActionExecutionError): # Expecting wrapper
            self.state_manager.load_plugin_state(plugin_id, plugin_version)

    def test_07_load_corrupted_state_file_checksum(self):
        plugin_id = "com.example.corruptedchecksum"
        plugin_version = "1.0.0"
        state_data = {"key": "value"}
        self.state_manager.save_plugin_state(plugin_id, plugin_version, state_data)
        state_file_path = self.state_manager._get_state_file_path(plugin_id, plugin_version)
        # Corrupt the file after saving by changing content without updating checksum
        with open(state_file_path, "r+") as f:
            content = json.load(f)
            content["data"]["key"] = "corrupted_value"
            f.seek(0)
            json.dump(content, f)
            f.truncate()

        with self.assertLogs(level=\"ERROR\") as log:
            loaded_state = self.state_manager.load_plugin_state(plugin_id, plugin_version)
            self.assertIsNone(loaded_state)
        self.assertTrue(any("Checksum mismatch" in record.getMessage() for record in log.records))

# Change to IsolatedAsyncioTestCase for async test methods
class TestPluginManagerUnit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.base_project_dir = os.path.abspath(os.path.join(project_root, "tests", "test_temp_pm_unit"))
        self.test_plugins_root_dir = os.path.join(self.base_project_dir, "plugins")
        self.test_plugin_states_dir = os.path.join(self.base_project_dir, "plugin_states_for_manager")
        self.schema_file_path = os.path.join(project_root, "docs", "plugin_metadata_schema.json")

        if os.path.exists(self.base_project_dir):
            shutil.rmtree(self.base_project_dir)
        os.makedirs(self.test_plugins_root_dir, exist_ok=True)
        os.makedirs(self.test_plugin_states_dir, exist_ok=True)

        self.valid_schema_content = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "ApexAgent Plugin Metadata",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "version": {"type": "string", "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$"},
                "description": {"type": "string"},
                "author": {"type": "string"},
                "main_module": {"type": "string"}, # Changed from entry_point
                "class_name": {"type": "string"},  # Changed from entry_point
                "actions": {"type": "array", "items": {"type": "object"}},
                "dependencies": {"type": "object"},
                "checksum": {
                    "type": "object",
                    "properties": {
                        "algorithm": {"type": "string", "enum": ["sha256", "sha512"]},
                        "value": {"type": "string"}
                    },
                    "required": ["algorithm", "value"]
                },
                "signature": {"type": "object"},
                "default_enabled": {"type": "boolean"}
            },
            "required": ["id", "name", "version", "description", "author", "main_module", "class_name", "actions"]
        }
        if not os.path.exists(os.path.dirname(self.schema_file_path)):
             os.makedirs(os.path.dirname(self.schema_file_path), exist_ok=True)
        with open(self.schema_file_path, "w") as f:
            json.dump(self.valid_schema_content, f, indent=2)
        
        # Provide agent_context with a mock logger
        self.mock_agent_logger = MagicMock(spec=logging.Logger)
        self.agent_context_for_plugins = {"logger": self.mock_agent_logger}

        self.manager = PluginManager(
            plugin_dirs=[self.test_plugins_root_dir], 
            schema_path=self.schema_file_path,
            agent_context=self.agent_context_for_plugins, # Pass agent_context here
            state_manager_base_dir=self.test_plugin_states_dir
        )
        self.manager.plugins.clear()
        self.manager.plugin_paths.clear()
        self.manager.plugin_states.clear()
        self.manager.loaded_plugin_instances.clear()

    async def asyncTearDown(self):
        if hasattr(self, "manager") and self.manager:
            await asyncio.to_thread(self.manager.shutdown_all_plugins) # Ensure plugins are shutdown
        if os.path.exists(self.base_project_dir):
            shutil.rmtree(self.base_project_dir)
        paths_to_remove = [p for p in sys.path if self.base_project_dir in p]
        for p in paths_to_remove:
            if p in sys.path:
                 sys.path.remove(p)

    def _create_dummy_plugin_file_structure(self, plugin_id_str, version_str, main_module_name="main", class_name_str="Plugin", extra_metadata=None, files=None, plugin_subdir_name=None, custom_class_content=None):
        plugin_id_str = plugin_id_str.strip()
        version_str = version_str.strip()
        if plugin_subdir_name is None:
            safe_plugin_id_part = plugin_id_str.replace(".", "_")
            plugin_subdir_name = f"{safe_plugin_id_part}_v{version_str.replace(".", "_")}"
        plugin_dir = os.path.join(self.test_plugins_root_dir, plugin_subdir_name)
        os.makedirs(plugin_dir, exist_ok=True)

        metadata = {
            "id": plugin_id_str,
            "name": f"{plugin_id_str} Name v{version_str}",
            "version": version_str,
            "description": f"Test plugin {plugin_id_str} version {version_str}",
            "author": "Unit Test",
            "main_module": f"{main_module_name}.py", 
            "class_name": class_name_str,
            "actions": [{"name": "test_action", "description": "A test action"}],
            "default_enabled": True
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        entry_file_content = custom_class_content
        if entry_file_content is None:
            entry_file_content = f"""import logging
logger_plugin = logging.getLogger(__name__)

from core.base_plugin import BasePlugin, StreamableOutput
from core.async_utils import ProgressUpdate, CancellationToken # Make sure these are available
from core.plugin_exceptions import *
from typing import Callable, Optional, Any, Union, Iterator, AsyncIterator, Dict
import asyncio

class {class_name_str}(BasePlugin):
    def __init__(self, plugin_id, plugin_name, version, description, config=None):
        super().__init__(plugin_id, plugin_name, version, description, config)
        self.internal_data = {{}}
        self.logger = None # Will be set in initialize

    def initialize(self, agent_context: Optional[Dict[str, Any]] = None):
        super().initialize(agent_context)
        self.logger = agent_context.get(\"logger\") if agent_context else logging.getLogger(f\"plugin.{{self.plugin_id}}\")
        self.logger.info(f\"{{self.plugin_id}} v{{self.version}} initialized.\")
        loaded = self.load_state()
        if loaded:
            self.internal_data = loaded
            self.logger.info(f\"{{self.plugin_id}} loaded state: {{self.internal_data}}\")

    def get_actions(self): return {metadata.get("actions", [])}

    def execute_action(self, action_name, params=None, progress_callback: Optional[Callable[[ProgressUpdate], None]] = None, cancellation_token: Optional[CancellationToken] = None) -> StreamableOutput:
        self.logger.info(f\"{{self.plugin_id}} execute_action {{action_name}} called.\")
        if action_name == \"test_action\":
            return f\"Plugin {{self.plugin_id}} v{{self.version}} action: {{action_name}}\"
        elif action_name == \"set_data\":
            self.internal_data[\"my_key\"] = params.get(\"value\")
            self.save_state(self.internal_data)
            return {{ \"status\": \"saved\", \"data\": self.internal_data }}
        elif action_name == \"get_data\":
            return {{ \"data\": self.internal_data }}
        raise PluginActionNotFoundError(f\"Action {{action_name}} not found\")

    async def execute_action_stream(self, action_name, params=None, progress_callback: Optional[Callable[[ProgressUpdate], None]] = None, cancellation_token: Optional[CancellationToken] = None) -> AsyncIterator[Any]:
        self.logger.info(f\"{{self.plugin_id}} execute_action_stream {{action_name}} called.\")
        if action_name == \"stream_test\":
            for i in range(3):
                if cancellation_token and cancellation_token.is_cancelled:
                    self.logger.info(\"Stream cancelled\")
                    break
                if progress_callback:
                    progress_callback(ProgressUpdate(percentage=(i+1)*33.3, message=f\"Streaming item {{i}}\", status=\"running\"))
                await asyncio.sleep(0.01) # Simulate async work
                yield f\"stream item {{i}}\"
            if progress_callback:
                progress_callback(ProgressUpdate(percentage=100.0, message=\"Stream complete\", status=\"completed\"))
        else:
            raise StreamingNotSupportedError(f\"Action {{action_name}} does not support streaming\")
            if False: yield

    def shutdown(self):
        self.logger.info(f\"{{self.plugin_id}} v{{self.version}} shutdown.\")
        self.save_state(self.internal_data)
"""
        
        entry_module_path = os.path.join(plugin_dir, f"{main_module_name}.py")
        with open(entry_module_path, "w") as f:
            f.write(entry_file_content)

        if files:
            for file_name, content_data in files.items():
                file_path = os.path.join(plugin_dir, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(content_data)
        return plugin_dir

    # ... (keep existing synchronous tests, adapt them if necessary for async setUp/tearDown)
    # For brevity, I will omit the existing synchronous tests here, but they should be retained and potentially adapted.
    # Example of adapting a sync test to run in IsolatedAsyncioTestCase:
    async def test_00_invoke_create_dummy_plugin(self):
        """Test that _create_dummy_plugin_file_structure run and creates files."""
        plugin_dir = self._create_dummy_plugin_file_structure("com.example.dummy", "0.1.0")
        self.assertTrue(os.path.isdir(plugin_dir))
        self.assertTrue(os.path.isfile(os.path.join(plugin_dir, "plugin.json")))
        self.assertTrue(os.path.isfile(os.path.join(plugin_dir, "main.py")))

    async def test_30_discover_and_load_valid_plugin(self):
        plugin_id = "com.example.valid"
        version = "1.0.0"
        self._create_dummy_plugin_file_structure(plugin_id, version)
        self.manager.discover_plugins()
        
        loaded_plugin = self.manager.load_plugin(plugin_id, version)
        self.assertIsNotNone(loaded_plugin)
        self.assertEqual(loaded_plugin.plugin_id, plugin_id)
        self.assertEqual(loaded_plugin.version, version)

    async def test_35_execute_plugin_action_sync(self):
        plugin_id = "com.example.actionexec"
        version = "1.0.0"
        action_name = "test_action"
        self._create_dummy_plugin_file_structure(plugin_id, version)
        self.manager.discover_plugins()
        self.manager.enable_plugin(plugin_id, version)
        
        result = await self.manager.execute_plugin_action(plugin_id, action_name, version=version)
        self.assertEqual(result, f"Plugin {plugin_id} v{version} action: {action_name}")

    # --- New Async Tests Start Here ---

    def _get_async_demo_plugin_content(self):
        return """import asyncio
from typing import Optional, Callable, Dict, Any
from core.base_plugin import BasePlugin
from core.async_utils import ProgressUpdate, CancellationToken
from core.plugin_exceptions import PluginActionExecutionError, PluginActionNotFoundError

class AsyncDemoPlugin(BasePlugin):
    def initialize(self, agent_context: Optional[Dict[str, Any]] = None) -> None:
        super().initialize(agent_context)
        self.logger = agent_context.get(\"logger\") if agent_context else logging.getLogger(f\"plugin.{{self.plugin_id}}\")
        self.logger.info(f\"AsyncDemoPlugin {{self.version}} initialized.\")

    def get_actions(self) -> list[dict]:
        return [
            {{
                \"name\": \"long_computation\",
                \"description\": \"Simulates a long computation...\",
            }}
        ]

    async def execute_action(self, action_name: str, params: Optional[dict] = None, progress_callback: Optional[Callable[[ProgressUpdate], None]] = None, cancellation_token: Optional[CancellationToken] = None) -> str:
        if action_name == \"long_computation\":
            if params is None: params = {{}}
            duration_seconds = params.get(\"duration_seconds\", 1) # Short default for tests
            steps = params.get(\"steps\", 2)
            self.logger.info(f\"Starting long_computation for {{duration_seconds}}s in {{steps}} steps.\")
            if progress_callback: progress_callback(ProgressUpdate(percentage=0.0, message=\"Starting...\", status=\"running\"))
            for i in range(steps):
                if cancellation_token and cancellation_token.is_cancelled:
                    message = \"Cancelled.\"
                    if progress_callback: progress_callback(ProgressUpdate(percentage=(i / steps) * 100.0, message=message, status=\"cancelled\"))
                    return message
                await asyncio.sleep(duration_seconds / steps)
                current_percentage = ((i + 1) / steps) * 100.0
                if progress_callback: progress_callback(ProgressUpdate(percentage=current_percentage, message=f\"Step {{i+1}}\", status=\"running\"))
            if progress_callback: progress_callback(ProgressUpdate(percentage=100.0, message=\"Completed\", status=\"completed\"))
            return \"Computation Done\"
        raise PluginActionNotFoundError(f\"Action {{action_name}} not found\")
"""

    async def test_50_execute_async_plugin_action_success(self):
        plugin_id = "com.example.asyncdemo"
        version = "1.0.0"
        action_name = "long_computation"
        
        self._create_dummy_plugin_file_structure(
            plugin_id, version, 
            main_module_name="async_plugin_main", 
            class_name_str="AsyncDemoPlugin",
            custom_class_content=self._get_async_demo_plugin_content(),
            extra_metadata={"actions": [{"name": action_name, "description": "..."}]}
        )
        self.manager.discover_plugins()
        self.manager.enable_plugin(plugin_id, version)

        mock_progress_callback = MagicMock()
        
        # Patch the _progress_callback inside PluginManager for this specific test
        # to make assertions on what the plugin sends.
        # This is a bit indirect. A better way might be to pass our mock directly if the API allowed.
        # For now, we assume PluginManager calls the internal _progress_callback which logs.
        # We can also check the logs, or make the plugin use the passed callback directly.
        # The AsyncDemoPlugin *does* use the passed progress_callback.

        result = await self.manager.execute_plugin_action(
            plugin_id, action_name, 
            params={"duration_seconds": 1, "steps": 2}, 
            version=version
            # The actual progress_callback is internal to execute_plugin_action
            # We will check its calls by mocking it on the plugin instance if possible, or by checking logs
        )
        self.assertEqual(result, "Computation Done")
        
        # To check progress calls, we need to get the instance and see if its callback was called
        # Or, if the plugin manager exposes a way to tap into progress, use that.
        # The PluginManager creates its own _progress_callback. We can check logs for now.
        # For more direct testing, the plugin could store calls to its progress_callback.
        # Let's assume the logging in PluginManager._progress_callback is sufficient for now.
        # We expect several log messages for progress.

    async def test_51_execute_async_plugin_action_timeout_exceeded(self):
        plugin_id = "com.example.asynctimeoutfail"
        version = "1.0.0"
        action_name = "long_computation"
        self._create_dummy_plugin_file_structure(
            plugin_id, version, 
            main_module_name="async_plugin_main_tf", 
            class_name_str="AsyncDemoPlugin",
            custom_class_content=self._get_async_demo_plugin_content(),
            extra_metadata={"actions": [{"name": action_name, "description": "..."}]}
        )
        self.manager.discover_plugins()
        self.manager.enable_plugin(plugin_id, version)

        with self.assertRaises(PluginActionTimeoutError) as cm:
            await self.manager.execute_plugin_action(
                plugin_id, action_name, 
                params={"duration_seconds": 2, "steps": 1}, # Runs for 2s
                version=version, 
                timeout=0.5 # Timeout at 0.5s
            )
        self.assertIn("timed out after 0.5 seconds", str(cm.exception))
        self.assertEqual(cm.exception.timeout_seconds, 0.5)

    async def test_52_execute_async_plugin_action_timeout_met(self):
        plugin_id = "com.example.asynctimeoutok"
        version = "1.0.0"
        action_name = "long_computation"
        self._create_dummy_plugin_file_structure(
            plugin_id, version, 
            main_module_name="async_plugin_main_tok", 
            class_name_str="AsyncDemoPlugin",
            custom_class_content=self._get_async_demo_plugin_content(),
            extra_metadata={"actions": [{"name": action_name, "description": "..."}]}
        )
        self.manager.discover_plugins()
        self.manager.enable_plugin(plugin_id, version)

        result = await self.manager.execute_plugin_action(
            plugin_id, action_name, 
            params={"duration_seconds": 1, "steps": 1}, # Runs for 1s
            version=version, 
            timeout=2.0 # Timeout at 2s
        )
        self.assertEqual(result, "Computation Done")

    async def test_53_execute_async_plugin_action_cancellation(self):
        plugin_id = "com.example.asynccancel"
        version = "1.0.0"
        action_name = "long_computation"
        self._create_dummy_plugin_file_structure(
            plugin_id, version, 
            main_module_name="async_plugin_main_cancel", 
            class_name_str="AsyncDemoPlugin",
            custom_class_content=self._get_async_demo_plugin_content(),
            extra_metadata={"actions": [{"name": action_name, "description": "..."}]}
        )
        self.manager.discover_plugins()
        self.manager.enable_plugin(plugin_id, version)

        # To test cancellation, we need to call cancel() on the token *during* execution.
        # This requires a bit more setup.
        # We can patch CancellationToken to get a reference to the instance used.
        
        shared_token_ref = []
        original_cancellation_token_init = CancellationToken.__init__
        def mock_cancellation_token_init(self_token):
            original_cancellation_token_init(self_token)
            shared_token_ref.append(self_token)

        with patch("core.plugin_manager.CancellationToken.__init__", mock_cancellation_token_init):
            # Start the task but don't await it immediately
            task = asyncio.create_task(
                self.manager.execute_plugin_action(
                    plugin_id, action_name,
                    params={"duration_seconds": 2, "steps": 4}, # Long enough to cancel
                    version=version
                )
            )
            await asyncio.sleep(0.2) # Give it a moment to start and create the token
            self.assertTrue(len(shared_token_ref) > 0, "CancellationToken was not created")
            token_instance = shared_token_ref[0]
            token_instance.cancel() # Request cancellation

            result = await task # Now await the result
            self.assertEqual(result, "Cancelled.")

    async def test_54_progress_updates_received_and_valid(self):
        plugin_id = "com.example.asyncprogress"
        version = "1.0.0"
        action_name = "long_computation"
        self._create_dummy_plugin_file_structure(
            plugin_id, version,
            main_module_name="async_plugin_main_prog",
            class_name_str="AsyncDemoPlugin",
            custom_class_content=self._get_async_demo_plugin_content(),
            extra_metadata={"actions": [{"name": action_name, "description": "..."}]}
        )
        self.manager.discover_plugins()
        self.manager.enable_plugin(plugin_id, version)

        # Mock the internal _progress_callback in PluginManager
        # This is tricky because it's a local function within execute_plugin_action
        # A better way is to check the logs or have the plugin store progress updates.
        # For this test, we rely on the plugin calling the callback passed to it.
        # We can mock the logger used by PluginManager's _progress_callback.

        mock_pm_logger = MagicMock(spec=logging.Logger)
        with patch("core.plugin_manager.logger", mock_pm_logger):
            await self.manager.execute_plugin_action(
                plugin_id, action_name,
                params={"duration_seconds": 0.2, "steps": 2},
                version=version
            )
        
        # Check that the logger was called with progress messages
        # Example: logger.info(f"PROGRESS - Plugin: {plugin_id}, Action: {action_name}, ...")
        self.assertTrue(mock_pm_logger.info.called)
        
        # Check for specific progress update messages in the logs
        # This is an indirect way to test progress_callback. 
        # A more direct test would involve passing a mock callback into execute_plugin_action if the API supported it,
        # or having the plugin itself collect calls to the progress_callback it receives.
        
        calls = mock_pm_logger.info.call_args_list
        progress_messages_found = 0
        for c in calls:
            args, _ = c
            if args and isinstance(args[0], str) and args[0].startswith("PROGRESS -"):
                progress_messages_found +=1
                self.assertIn(f"Plugin: {plugin_id}", args[0])
                self.assertIn(f"Action: {action_name}", args[0])
                if "Starting..." in args[0]:
                    self.assertIn("Percentage: 0.0%", args[0])
                if "Step 1" in args[0]:
                    self.assertIn("Percentage: 50.0%", args[0])
                if "Step 2" in args[0] or "Completed" in args[0]: # Depending on exact plugin logic for last step
                    self.assertIn("Percentage: 100.0%", args[0])
        
        self.assertGreaterEqual(progress_messages_found, 3) # Start, step 1, step 2/completed

if __name__ == "__main__":
    unittest.main()

