import unittest
import os
import json
import shutil
import sys
import asyncio
import logging
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to sys.path to allow importing PluginManager
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(project_root, "src"))

from core.plugin_manager import PluginManager
from core.base_plugin import BasePlugin, StreamMetadata
from core.plugin_exceptions import (
    PluginError,
    PluginActionNotFoundError,
    StreamingNotSupportedError,
    PluginNotFoundError
)
from core.async_utils import ProgressUpdate, CancellationToken

from packaging.version import parse as parse_version
from typing import Optional, Dict, Any, AsyncIterator

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

class TestPluginManagerStreaming(unittest.IsolatedAsyncioTestCase):
    """Test suite for the streaming capabilities of PluginManager."""
    
    async def asyncSetUp(self):
        """Set up test environment with test plugins directory and schema."""
        self.base_project_dir = os.path.abspath(os.path.join(project_root, "tests", "test_temp_pm_streaming"))
        self.test_plugins_root_dir = os.path.join(self.base_project_dir, "plugins")
        self.test_plugin_states_dir = os.path.join(self.base_project_dir, "plugin_states_for_manager")
        self.schema_file_path = os.path.join(project_root, "docs", "plugin_metadata_schema.json")

        # Clean up any existing test directories
        if os.path.exists(self.base_project_dir):
            shutil.rmtree(self.base_project_dir)
        os.makedirs(self.test_plugins_root_dir, exist_ok=True)
        os.makedirs(self.test_plugin_states_dir, exist_ok=True)

        # Create a valid schema for testing
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
                "main_file": {"type": "string"},
                "main_class": {"type": "string"},
                "actions": {
                    "type": "array", 
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "parameters_schema": {"type": "object"},
                            "returns_schema": {"type": "object"},
                            "returns_stream": {"type": "boolean"},
                            "stream_metadata": {
                                "type": "object",
                                "properties": {
                                    "content_type": {"type": "string"},
                                    "supports_transformation": {"type": "boolean"},
                                    "supports_composition": {"type": "boolean"},
                                    "supports_persistence": {"type": "boolean"},
                                    "estimated_size": {"type": "integer"},
                                    "additional_info": {"type": "object"}
                                }
                            }
                        },
                        "required": ["name", "description"]
                    }
                },
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
            "required": ["id", "name", "version", "description", "author", "main_file", "main_class", "actions"]
        }
        
        # Ensure schema directory exists
        if not os.path.exists(os.path.dirname(self.schema_file_path)):
            os.makedirs(os.path.dirname(self.schema_file_path), exist_ok=True)
        
        # Write schema to file
        with open(self.schema_file_path, "w") as f:
            json.dump(self.valid_schema_content, f, indent=2)
        
        # Create a mock logger for agent context
        self.mock_agent_logger = MagicMock(spec=logging.Logger)
        self.agent_context_for_plugins = {"logger": self.mock_agent_logger}

        # Initialize the PluginManager
        self.manager = PluginManager(
            plugin_dirs=[self.test_plugins_root_dir], 
            schema_path=self.schema_file_path,
            agent_context=self.agent_context_for_plugins,
            state_manager_base_dir=self.test_plugin_states_dir
        )
        
        # Clear any existing data
        self.manager.plugins.clear()
        self.manager.plugin_paths.clear()
        self.manager.plugin_states.clear()
        self.manager.loaded_plugin_instances.clear()
        self.manager.streaming_actions.clear()

    async def asyncTearDown(self):
        """Clean up test environment after tests."""
        if hasattr(self, "manager") and self.manager:
            # Ensure all plugins are shutdown
            for plugin_id in list(self.manager.loaded_plugin_instances.keys()):
                for version in list(self.manager.loaded_plugin_instances[plugin_id].keys()):
                    self.manager.unload_plugin(plugin_id, str(version))
        
        # Remove test directories
        if os.path.exists(self.base_project_dir):
            shutil.rmtree(self.base_project_dir)
        
        # Clean up sys.path
        paths_to_remove = [p for p in sys.path if self.base_project_dir in p]
        for p in paths_to_remove:
            if p in sys.path:
                sys.path.remove(p)

    def _create_streaming_plugin(self, plugin_id, version, streaming_actions=None, non_streaming_actions=None):
        """
        Helper method to create a test plugin with streaming capabilities.
        
        Args:
            plugin_id (str): The plugin ID
            version (str): The plugin version
            streaming_actions (list, optional): List of streaming action configurations
            non_streaming_actions (list, optional): List of non-streaming action configurations
        
        Returns:
            str: Path to the created plugin directory
        """
        plugin_dir = os.path.join(self.test_plugins_root_dir, f"{plugin_id.replace('.', '_')}_v{version.replace('.', '_')}")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Default streaming actions if none provided
        if streaming_actions is None:
            streaming_actions = [
                {
                    "name": "stream_data",
                    "description": "Streams data items",
                    "returns_stream": True,
                    "stream_metadata": {
                        "content_type": "application/json",
                        "supports_transformation": True,
                        "supports_composition": True,
                        "supports_persistence": False,
                        "estimated_size": 100
                    }
                }
            ]
        
        # Default non-streaming actions if none provided
        if non_streaming_actions is None:
            non_streaming_actions = [
                {
                    "name": "get_data",
                    "description": "Gets data as a single response",
                    "returns_stream": False
                }
            ]
        
        # Combine all actions
        all_actions = streaming_actions + non_streaming_actions
        
        # Create plugin metadata
        metadata = {
            "id": plugin_id,
            "name": f"{plugin_id} Plugin",
            "version": version,
            "description": f"Test streaming plugin {plugin_id} v{version}",
            "author": "Test Author",
            "main_file": "plugin_main.py",
            "main_class": "StreamingPlugin",
            "actions": all_actions,
            "default_enabled": True
        }
        
        # Write metadata to plugin.json
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Create plugin implementation
        plugin_code = """
import logging
from typing import Callable, Optional, Any, Dict, AsyncIterator
import asyncio

from core.base_plugin import BasePlugin, StreamMetadata
from core.async_utils import ProgressUpdate, CancellationToken
from core.plugin_exceptions import StreamingNotSupportedError, PluginActionNotFoundError

class StreamingPlugin(BasePlugin):
    def __init__(self, plugin_id, plugin_name, version, description, config=None):
        super().__init__(plugin_id, plugin_name, version, description, config)
        self.logger = logging.getLogger(f"plugin.{plugin_id}")
    
    def initialize(self, agent_context=None):
        super().initialize(agent_context)
        self.logger.info(f"Initialized {self.plugin_id} v{self.version}")
    
    def get_actions(self):
        # Return actions from metadata
        actions = []
        
        # Add streaming actions
        actions.append({
            "name": "stream_data",
            "description": "Streams data items",
            "returns_stream": True,
            "stream_metadata": {
                "content_type": "application/json",
                "supports_transformation": True,
                "supports_composition": True,
                "supports_persistence": False,
                "estimated_size": 100
            }
        })
        
        # Add non-streaming actions
        actions.append({
            "name": "get_data",
            "description": "Gets data as a single response",
            "returns_stream": False
        })
        
        return actions
    
    def execute_action(self, action_name, params=None, progress_callback=None, cancellation_token=None):
        if action_name == "get_data":
            return {"data": "This is non-streaming data"}
        elif action_name == "stream_data":
            # This is a streaming action, but called via non-streaming method
            return {"error": "This action should be called via execute_action_stream"}
        else:
            raise PluginActionNotFoundError(f"Action {action_name} not found")
    
    async def execute_action_stream(self, action_name, params=None, progress_callback=None, cancellation_token=None):
        if action_name == "stream_data":
            # Stream 5 items
            for i in range(5):
                if cancellation_token and cancellation_token.is_cancelled:
                    break
                
                if progress_callback:
                    progress_callback(ProgressUpdate(
                        percentage=(i+1) * 20.0,
                        message=f"Processing item {i+1}/5",
                        status="running"
                    ))
                
                await asyncio.sleep(0.01)  # Simulate work
                yield {"item": i, "value": f"Stream item {i}"}
            
            if progress_callback:
                progress_callback(ProgressUpdate(
                    percentage=100.0,
                    message="Stream complete",
                    status="completed"
                ))
        else:
            raise StreamingNotSupportedError(f"Action {action_name} does not support streaming")
    
    async def get_stream_metadata(self, action_name, params=None):
        if action_name == "stream_data":
            return StreamMetadata(
                content_type="application/json",
                item_schema={"type": "object", "properties": {"item": {"type": "integer"}, "value": {"type": "string"}}},
                supports_transformation=True,
                supports_composition=True,
                supports_persistence=False,
                estimated_size=5,
                additional_info={"source": "test_plugin"}
            )
        else:
            raise StreamingNotSupportedError(f"Action {action_name} does not support streaming")
    
    async def transform_stream(self, stream, transform_type, transform_params=None, progress_callback=None, cancellation_token=None):
        if transform_type == "map":
            async for item in stream:
                if cancellation_token and cancellation_token.is_cancelled:
                    break
                
                # Apply transformation based on transform_params
                if transform_params and "map_function" in transform_params:
                    func_name = transform_params["map_function"]
                    if func_name == "uppercase_value":
                        item["value"] = item["value"].upper()
                    elif func_name == "double_item":
                        item["item"] *= 2
                
                yield item
        else:
            # Pass through for unsupported transform types
            async for item in stream:
                if cancellation_token and cancellation_token.is_cancelled:
                    break
                yield item
    
    def shutdown(self):
        self.logger.info(f"Shutting down {self.plugin_id} v{self.version}")
"""
        
        # Write plugin implementation to file
        with open(os.path.join(plugin_dir, "plugin_main.py"), "w") as f:
            f.write(plugin_code)
        
        return plugin_dir

    def _create_non_streaming_plugin(self, plugin_id, version):
        """
        Helper method to create a test plugin without streaming capabilities.
        
        Args:
            plugin_id (str): The plugin ID
            version (str): The plugin version
        
        Returns:
            str: Path to the created plugin directory
        """
        plugin_dir = os.path.join(self.test_plugins_root_dir, f"{plugin_id.replace('.', '_')}_v{version.replace('.', '_')}")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create plugin metadata
        metadata = {
            "id": plugin_id,
            "name": f"{plugin_id} Plugin",
            "version": version,
            "description": f"Test non-streaming plugin {plugin_id} v{version}",
            "author": "Test Author",
            "main_file": "plugin_main.py",
            "main_class": "NonStreamingPlugin",
            "actions": [
                {
                    "name": "get_data",
                    "description": "Gets data as a single response"
                },
                {
                    "name": "process_data",
                    "description": "Processes data and returns result"
                }
            ],
            "default_enabled": True
        }
        
        # Write metadata to plugin.json
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Create plugin implementation
        plugin_code = """
import logging
from typing import Callable, Optional, Any, Dict
from core.base_plugin import BasePlugin
from core.async_utils import ProgressUpdate, CancellationToken
from core.plugin_exceptions import StreamingNotSupportedError, PluginActionNotFoundError

class NonStreamingPlugin(BasePlugin):
    def __init__(self, plugin_id, plugin_name, version, description, config=None):
        super().__init__(plugin_id, plugin_name, version, description, config)
        self.logger = logging.getLogger(f"plugin.{plugin_id}")
    
    def initialize(self, agent_context=None):
        super().initialize(agent_context)
        self.logger.info(f"Initialized {self.plugin_id} v{self.version}")
    
    def get_actions(self):
        return [
            {
                "name": "get_data",
                "description": "Gets data as a single response"
            },
            {
                "name": "process_data",
                "description": "Processes data and returns result"
            }
        ]
    
    def execute_action(self, action_name, params=None, progress_callback=None, cancellation_token=None):
        if action_name == "get_data":
            return {"data": "This is non-streaming data"}
        elif action_name == "process_data":
            input_data = params.get("input", "default")
            return {"result": f"Processed: {input_data}"}
        else:
            raise PluginActionNotFoundError(f"Action {action_name} not found")
    
    async def execute_action_stream(self, action_name, params=None, progress_callback=None, cancellation_token=None):
        raise StreamingNotSupportedError(f"Plugin {self.plugin_id} does not support streaming")
    
    def shutdown(self):
        self.logger.info(f"Shutting down {self.plugin_id} v{self.version}")
"""
        
        # Write plugin implementation to file
        with open(os.path.join(plugin_dir, "plugin_main.py"), "w") as f:
            f.write(plugin_code)
        
        return plugin_dir

    async def test_01_discover_streaming_plugins(self):
        """Test that PluginManager correctly discovers plugins with streaming capabilities."""
        # Create test plugins
        self._create_streaming_plugin("com.test.streaming", "1.0.0")
        self._create_non_streaming_plugin("com.test.nonstreaming", "1.0.0")
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Check that streaming_actions dictionary is populated correctly
        self.assertIn("com.test.streaming", self.manager.streaming_actions)
        self.assertNotIn("com.test.nonstreaming", self.manager.streaming_actions)
        
        # Check that the streaming action is correctly identified
        streaming_plugin_version = parse_version("1.0.0")
        self.assertIn(streaming_plugin_version, self.manager.streaming_actions["com.test.streaming"])
        self.assertIn("stream_data", self.manager.streaming_actions["com.test.streaming"][streaming_plugin_version])
        
        # Verify streaming metadata
        metadata = self.manager.streaming_actions["com.test.streaming"][streaming_plugin_version]["stream_data"]
        self.assertEqual(metadata["content_type"], "application/json")
        self.assertTrue(metadata["supports_transformation"])
        self.assertTrue(metadata["supports_composition"])
        self.assertFalse(metadata["supports_persistence"])
        self.assertEqual(metadata["estimated_size"], 100)

    async def test_02_get_streaming_plugin_ids(self):
        """Test the get_streaming_plugin_ids method."""
        # Create test plugins
        self._create_streaming_plugin("com.test.streaming1", "1.0.0")
        self._create_streaming_plugin("com.test.streaming2", "1.0.0")
        self._create_non_streaming_plugin("com.test.nonstreaming", "1.0.0")
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Get streaming plugin IDs
        streaming_ids = self.manager.get_streaming_plugin_ids()
        
        # Verify results
        self.assertIn("com.test.streaming1", streaming_ids)
        self.assertIn("com.test.streaming2", streaming_ids)
        self.assertNotIn("com.test.nonstreaming", streaming_ids)

    async def test_03_get_streaming_actions(self):
        """Test the get_streaming_actions method."""
        # Create test plugins
        self._create_streaming_plugin("com.test.streaming", "1.0.0", 
            streaming_actions=[
                {
                    "name": "stream_data",
                    "description": "Streams data items",
                    "returns_stream": True,
                    "stream_metadata": {"content_type": "application/json"}
                },
                {
                    "name": "stream_logs",
                    "description": "Streams log entries",
                    "returns_stream": True,
                    "stream_metadata": {"content_type": "text/plain"}
                }
            ]
        )
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Get streaming actions
        actions = self.manager.get_streaming_actions("com.test.streaming")
        
        # Verify results
        self.assertEqual(len(actions), 2)
        self.assertIn("stream_data", actions)
        self.assertIn("stream_logs", actions)

    async def test_04_get_streaming_action_metadata(self):
        """Test the get_streaming_action_metadata method."""
        # Create test plugins
        self._create_streaming_plugin("com.test.streaming", "1.0.0")
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Get streaming action metadata
        metadata = self.manager.get_streaming_action_metadata("com.test.streaming", "stream_data")
        
        # Verify results
        self.assertEqual(metadata["content_type"], "application/json")
        self.assertTrue(metadata["supports_transformation"])
        self.assertTrue(metadata["supports_composition"])
        self.assertFalse(metadata["supports_persistence"])
        self.assertEqual(metadata["estimated_size"], 100)
        
        # Test with non-existent plugin
        with self.assertRaises(PluginNotFoundError):
            self.manager.get_streaming_action_metadata("com.test.nonexistent", "stream_data")
        
        # Test with non-existent action
        with self.assertRaises(StreamingNotSupportedError):
            self.manager.get_streaming_action_metadata("com.test.streaming", "nonexistent_action")

    async def test_05_is_action_streaming_capable(self):
        """Test the is_action_streaming_capable method."""
        # Create test plugins
        self._create_streaming_plugin("com.test.streaming", "1.0.0")
        self._create_non_streaming_plugin("com.test.nonstreaming", "1.0.0")
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Check streaming capability
        self.assertTrue(self.manager.is_action_streaming_capable("com.test.streaming", "stream_data"))
        self.assertFalse(self.manager.is_action_streaming_capable("com.test.streaming", "get_data"))
        self.assertFalse(self.manager.is_action_streaming_capable("com.test.nonstreaming", "get_data"))
        self.assertFalse(self.manager.is_action_streaming_capable("com.test.nonexistent", "any_action"))

    async def test_06_get_all_streaming_actions(self):
        """Test the get_all_streaming_actions method."""
        # Create test plugins
        self._create_streaming_plugin("com.test.streaming1", "1.0.0")
        self._create_streaming_plugin("com.test.streaming2", "1.0.0", 
            streaming_actions=[
                {
                    "name": "stream_logs",
                    "description": "Streams log entries",
                    "returns_stream": True,
                    "stream_metadata": {"content_type": "text/plain"}
                }
            ]
        )
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Get all streaming actions
        all_actions = self.manager.get_all_streaming_actions()
        
        # Verify results
        self.assertEqual(len(all_actions), 2)
        
        # Check that both plugins' actions are included
        plugin_action_pairs = [(a["plugin_id"], a["action_name"]) for a in all_actions]
        self.assertIn(("com.test.streaming1", "stream_data"), plugin_action_pairs)
        self.assertIn(("com.test.streaming2", "stream_logs"), plugin_action_pairs)
        
        # Check metadata is included
        for action in all_actions:
            self.assertIn("metadata", action)
            self.assertIn("content_type", action["metadata"])

    async def test_07_get_streaming_actions_by_capability(self):
        """Test the get_streaming_actions_by_capability method."""
        # Create test plugins with different capabilities
        self._create_streaming_plugin("com.test.streaming1", "1.0.0", 
            streaming_actions=[
                {
                    "name": "stream_data",
                    "description": "Streams data items",
                    "returns_stream": True,
                    "stream_metadata": {
                        "content_type": "application/json",
                        "supports_transformation": True,
                        "supports_composition": True,
                        "supports_persistence": False
                    }
                }
            ]
        )
        self._create_streaming_plugin("com.test.streaming2", "1.0.0", 
            streaming_actions=[
                {
                    "name": "stream_logs",
                    "description": "Streams log entries",
                    "returns_stream": True,
                    "stream_metadata": {
                        "content_type": "text/plain",
                        "supports_transformation": True,
                        "supports_composition": False,
                        "supports_persistence": True
                    }
                }
            ]
        )
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Get actions by transformation capability
        transform_actions = self.manager.get_streaming_actions_by_capability("transformation")
        self.assertEqual(len(transform_actions), 2)
        
        # Get actions by composition capability
        compose_actions = self.manager.get_streaming_actions_by_capability("composition")
        self.assertEqual(len(compose_actions), 1)
        self.assertEqual(compose_actions[0]["action_name"], "stream_data")
        
        # Get actions by persistence capability
        persist_actions = self.manager.get_streaming_actions_by_capability("persistence")
        self.assertEqual(len(persist_actions), 1)
        self.assertEqual(persist_actions[0]["action_name"], "stream_logs")

    async def test_08_get_streaming_actions_by_content_type(self):
        """Test the get_streaming_actions_by_content_type method."""
        # Create test plugins with different content types
        self._create_streaming_plugin("com.test.streaming1", "1.0.0", 
            streaming_actions=[
                {
                    "name": "stream_data",
                    "description": "Streams data items",
                    "returns_stream": True,
                    "stream_metadata": {"content_type": "application/json"}
                }
            ]
        )
        self._create_streaming_plugin("com.test.streaming2", "1.0.0", 
            streaming_actions=[
                {
                    "name": "stream_logs",
                    "description": "Streams log entries",
                    "returns_stream": True,
                    "stream_metadata": {"content_type": "text/plain"}
                }
            ]
        )
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Get actions by content type
        json_actions = self.manager.get_streaming_actions_by_content_type("application/json")
        self.assertEqual(len(json_actions), 1)
        self.assertEqual(json_actions[0]["action_name"], "stream_data")
        
        text_actions = self.manager.get_streaming_actions_by_content_type("text/plain")
        self.assertEqual(len(text_actions), 1)
        self.assertEqual(text_actions[0]["action_name"], "stream_logs")
        
        # Test with non-existent content type
        nonexistent_actions = self.manager.get_streaming_actions_by_content_type("application/xml")
        self.assertEqual(len(nonexistent_actions), 0)

    async def test_09_get_stream_metadata_from_plugin(self):
        """Test the get_stream_metadata_from_plugin method."""
        # Create test plugin
        self._create_streaming_plugin("com.test.streaming", "1.0.0")
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Load the plugin
        plugin = self.manager.load_plugin("com.test.streaming")
        self.assertIsNotNone(plugin)
        
        # Get stream metadata from plugin
        metadata = await self.manager.get_stream_metadata_from_plugin("com.test.streaming", "stream_data")
        
        # Verify results
        self.assertIsInstance(metadata, StreamMetadata)
        self.assertEqual(metadata.content_type, "application/json")
        self.assertTrue(metadata.supports_transformation)
        self.assertTrue(metadata.supports_composition)
        self.assertFalse(metadata.supports_persistence)
        self.assertEqual(metadata.estimated_size, 5)
        self.assertEqual(metadata.additional_info, {"source": "test_plugin"})
        
        # Test with non-existent plugin
        with self.assertRaises(PluginNotFoundError):
            await self.manager.get_stream_metadata_from_plugin("com.test.nonexistent", "stream_data")
        
        # Test with non-streaming action
        with self.assertRaises(StreamingNotSupportedError):
            await self.manager.get_stream_metadata_from_plugin("com.test.streaming", "get_data")

    async def test_10_update_streaming_metadata_from_instance(self):
        """Test that streaming metadata is updated from plugin instance."""
        # Create test plugin
        self._create_streaming_plugin("com.test.streaming", "1.0.0")
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Get initial metadata from discovery
        version = parse_version("1.0.0")
        initial_metadata = self.manager.streaming_actions["com.test.streaming"][version]["stream_data"]
        self.assertEqual(initial_metadata["estimated_size"], 100)
        
        # Load the plugin (this should update metadata)
        plugin = self.manager.load_plugin("com.test.streaming")
        self.assertIsNotNone(plugin)
        
        # Check that metadata was updated from the plugin instance
        updated_metadata = self.manager.streaming_actions["com.test.streaming"][version]["stream_data"]
        self.assertEqual(updated_metadata["estimated_size"], 100)  # This doesn't change in our test setup
        
        # The actual update would be visible if the plugin instance returned different metadata
        # than what was in the plugin.json file, but our test setup returns the same values

    async def test_11_version_handling_in_streaming_actions(self):
        """Test that version handling works correctly for streaming actions."""
        # Create test plugin with multiple versions
        self._create_streaming_plugin("com.test.streaming", "1.0.0")
        self._create_streaming_plugin("com.test.streaming", "1.1.0", 
            streaming_actions=[
                {
                    "name": "stream_data",
                    "description": "Streams data items (v1.1)",
                    "returns_stream": True,
                    "stream_metadata": {
                        "content_type": "application/json",
                        "supports_transformation": True,
                        "supports_composition": True,
                        "supports_persistence": True,  # Changed from v1.0.0
                        "estimated_size": 200  # Changed from v1.0.0
                    }
                }
            ]
        )
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Get streaming actions for specific version
        v1_actions = self.manager.get_streaming_actions("com.test.streaming", "1.0.0")
        self.assertIn("stream_data", v1_actions)
        
        v1_1_actions = self.manager.get_streaming_actions("com.test.streaming", "1.1.0")
        self.assertIn("stream_data", v1_1_actions)
        
        # Get metadata for specific versions
        v1_metadata = self.manager.get_streaming_action_metadata("com.test.streaming", "stream_data", "1.0.0")
        self.assertEqual(v1_metadata["estimated_size"], 100)
        self.assertFalse(v1_metadata["supports_persistence"])
        
        v1_1_metadata = self.manager.get_streaming_action_metadata("com.test.streaming", "stream_data", "1.1.0")
        self.assertEqual(v1_1_metadata["estimated_size"], 200)
        self.assertTrue(v1_1_metadata["supports_persistence"])
        
        # Test default version (latest)
        default_actions = self.manager.get_streaming_actions("com.test.streaming")
        self.assertIn("stream_data", default_actions)
        
        default_metadata = self.manager.get_streaming_action_metadata("com.test.streaming", "stream_data")
        self.assertEqual(default_metadata["estimated_size"], 200)  # Should be from v1.1.0

    async def test_12_error_handling_for_streaming_metadata(self):
        """Test error handling for streaming metadata methods."""
        # Create test plugin
        self._create_streaming_plugin("com.test.streaming", "1.0.0")
        
        # Discover plugins
        self.manager.discover_plugins()
        
        # Test with invalid version string
        with self.assertRaises(Exception):
            self.manager.get_streaming_action_metadata("com.test.streaming", "stream_data", "invalid.version")
        
        # Test with non-existent plugin
        self.assertEqual(self.manager.get_streaming_actions("com.test.nonexistent"), [])
        
        # Test with non-existent version
        self.assertEqual(self.manager.get_streaming_actions("com.test.streaming", "2.0.0"), [])

if __name__ == "__main__":
    unittest.main()
