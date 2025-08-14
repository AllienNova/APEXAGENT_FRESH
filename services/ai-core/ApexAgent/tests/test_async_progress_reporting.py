import unittest
import asyncio
from unittest.mock import Mock, AsyncMock, call # AsyncMock for async callbacks

from agent_project.src.core.base_enhanced_plugin import BaseEnhancedPlugin
from agent_project.src.core.exceptions import PluginArgumentError, PluginExecutionError
from agent_project.src.plugins.example_long_running_plugin import ExampleLongRunningPlugin

class TestAsyncProgressReporting(unittest.IsolatedAsyncioTestCase):

    async def test_plugin_initialization_with_progress_callback(self):
        mock_progress_callback = AsyncMock()
        plugin = ExampleLongRunningPlugin(
            plugin_id="test.init_plugin",
            plugin_version="0.1.0",
            progress_callback=mock_progress_callback
        )
        self.assertEqual(plugin.plugin_id, "test.init_plugin")
        self.assertEqual(plugin.progress_callback, mock_progress_callback)

    async def test_async_action_calls_progress_callback(self):
        mock_progress_callback = AsyncMock() # Use AsyncMock for awaitable callbacks
        plugin = ExampleLongRunningPlugin(
            plugin_id="test.progress_plugin",
            plugin_version="0.1.0",
            progress_callback=mock_progress_callback
        )

        steps = 3
        task_id = "test_task_123"
        await plugin.execute_action("long_computation_task", steps=steps, task_id=task_id)

        # Check if callback was called (steps + 2 times: 1 for start, steps for each step, 1 for end)
        self.assertEqual(mock_progress_callback.call_count, steps + 2)

        # Check the first call (task initiated)
        first_call_args = mock_progress_callback.call_args_list[0][1] # kwargs of the first call
        self.assertEqual(first_call_args["plugin_id"], "test.progress_plugin")
        self.assertEqual(first_call_args["action_name"], "long_computation_task")
        self.assertEqual(first_call_args["current_step"], 0)
        self.assertEqual(first_call_args["total_steps"], steps)
        self.assertEqual(first_call_args["message"], f"Task {task_id} initiated.")
        self.assertEqual(first_call_args["additional_data"], {"task_id": task_id, "status": "started"})
        
        # Check one intermediate call
        intermediate_call_args = mock_progress_callback.call_args_list[1][1]
        self.assertEqual(intermediate_call_args["current_step"], 1)
        self.assertEqual(intermediate_call_args["message"], f"Processing step 1 of {task_id}")

        # Check the last call (task completed)
        last_call_args = mock_progress_callback.call_args_list[steps + 1][1]
        self.assertEqual(last_call_args["current_step"], steps)
        self.assertEqual(last_call_args["total_steps"], steps)
        self.assertEqual(last_call_args["message"], f"Task {task_id} completed successfully.")
        self.assertEqual(last_call_args["additional_data"], {"task_id": task_id, "status": "completed"})

    async def test_async_action_without_progress_callback_logs_instead(self):
        # To test logging, we might need to capture log output
        # For simplicity, we ensure it runs without error if no callback is provided
        plugin = ExampleLongRunningPlugin(
            plugin_id="test.no_callback_plugin",
            plugin_version="0.1.0",
            progress_callback=None # Explicitly None
        )
        steps = 2
        try:
            # We expect this to log to self.logger.debug, not raise an error
            await plugin.execute_action("long_computation_task", steps=steps, task_id="no_cb_test")
        except Exception as e:
            self.fail(f"Task with no callback failed unexpectedly: {e}")

    async def test_sync_action_in_plugin(self):
        plugin = ExampleLongRunningPlugin(
            plugin_id="test.sync_action_plugin",
            plugin_version="0.1.0"
        )
        result = await plugin.execute_action("synchronous_greet", name="Tester")
        self.assertEqual(result, "Hello, Tester! From test.sync_action_plugin v0.1.0. This is a synchronous action.")

    async def test_invalid_argument_in_async_action(self):
        plugin = ExampleLongRunningPlugin(
            plugin_id="test.arg_error_plugin",
            plugin_version="0.1.0"
        )
        with self.assertRaises(PluginArgumentError):
            await plugin.execute_action("long_computation_task", steps=-1, task_id="invalid_steps")

    async def test_execution_error_in_async_action(self):
        mock_progress_callback = AsyncMock()
        plugin = ExampleLongRunningPlugin(
            plugin_id="test.exec_error_plugin",
            plugin_version="0.1.0",
            progress_callback=mock_progress_callback
        )
        steps = 4
        with self.assertRaises(PluginExecutionError) as cm:
            await plugin.execute_action("long_computation_task", steps=steps, task_id="simulated_failure")
        
        self.assertIn("Simulated failure during simulated_failure at step 2", str(cm.exception))
        # Check that progress was reported up to the failure point
        # Failure at step 2 (0-indexed loop, so i=1, current_progress_step=2)
        # Calls: start (1), step 1 (1), step 2 (1) = 3 calls
        self.assertEqual(mock_progress_callback.call_count, 1 + steps // 2)

    async def test_non_existent_action_call(self):
        plugin = ExampleLongRunningPlugin(
            plugin_id="test.no_action_plugin",
            plugin_version="0.1.0"
        )
        from agent_project.src.core.exceptions import PluginNotImplementedError
        with self.assertRaises(PluginNotImplementedError):
            await plugin.execute_action("action_that_does_not_exist")

if __name__ == "__main__":
    unittest.main()
