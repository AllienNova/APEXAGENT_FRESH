import asyncio
import logging
from typing import Callable, Awaitable, Any, Dict, Optional

from ..core.base_enhanced_plugin import BaseEnhancedPlugin
from ..core.exceptions import PluginArgumentError, PluginExecutionError

# It's good practice for plugins to have their own logger, 
# but BaseEnhancedPlugin already sets one up as self.logger
# logger = logging.getLogger(__name__) # This would create a logger named 'agent_project.src.plugins.example_long_running_plugin'

class ExampleLongRunningPlugin(BaseEnhancedPlugin):
    """
    An example plugin demonstrating asynchronous actions and progress reporting.
    """
    def __init__(self, 
                 plugin_id: str, 
                 plugin_version: str, 
                 config: Optional[Dict[str, Any]] = None, 
                 progress_callback: Optional[Callable[..., Awaitable[None] | None]] = None):
        super().__init__(plugin_id, plugin_version, config, progress_callback)
        self.logger.info(f"ExampleLongRunningPlugin (ID: {self.plugin_id}) initialized.")

    def synchronous_greet(self, name: str) -> str:
        """
        A simple synchronous action for demonstration.
        """
        if not isinstance(name, str) or not name:
            self.logger.warning("synchronous_greet called with invalid name.")
            raise PluginArgumentError("Argument 'name' must be a non-empty string.")
        self.logger.info(f"synchronous_greet action called with name: {name}")
        return f"Hello, {name}! From {self.plugin_id} v{self.plugin_version}. This is a synchronous action."

    async def long_computation_task(self, steps: int, task_id: str = "default_task"):
        """
        Simulates a long-running asynchronous computation that reports progress.

        Args:
            steps (int): The number of steps to simulate.
            task_id (str): An identifier for this task instance.
        """
        if not isinstance(steps, int) or steps <= 0:
            raise PluginArgumentError("Argument 'steps' must be a positive integer.")

        self.logger.info(f"Starting long_computation_task (ID: {task_id}) with {steps} steps.")
        await self._report_progress(action_name="long_computation_task",
                                    current_step=0,
                                    total_steps=steps,
                                    message=f"Task {task_id} initiated.",
                                    additional_data={"task_id": task_id, "status": "started"})
        
        for i in range(steps):
            await asyncio.sleep(0.05) # Simulate I/O-bound or async work
            current_progress_step = i + 1
            await self._report_progress(action_name="long_computation_task",
                                        current_step=current_progress_step,
                                        total_steps=steps,
                                        message=f"Processing step {current_progress_step} of {task_id}",
                                        additional_data={"task_id": task_id, "item_processed": i})
            
            # Simulate a potential failure point
            if task_id == "simulated_failure" and current_progress_step == steps // 2:
                self.logger.warning(f"Simulating failure in long_computation_task (ID: {task_id}) at step {current_progress_step}")
                raise PluginExecutionError(f"Simulated failure during {task_id} at step {current_progress_step}")

        await self._report_progress(action_name="long_computation_task",
                                    current_step=steps, # Final step reported as completed
                                    total_steps=steps,
                                    message=f"Task {task_id} completed successfully.",
                                    additional_data={"task_id": task_id, "status": "completed"})
        
        self.logger.info(f"Long_computation_task (ID: {task_id}) completed {steps} steps.")
        return f"Task {task_id} successfully finished after {steps} steps."

    async def another_async_action_no_progress(self, duration: float) -> str:
        """
        Another async action that does not report progress, just to show variety.
        """
        self.logger.info(f"Starting another_async_action_no_progress for {duration}s.")
        await asyncio.sleep(duration)
        self.logger.info("Finished another_async_action_no_progress.")
        return f"Slept for {duration} seconds."

# Example of how this plugin might be used (for direct testing or as a script)
# This would typically be orchestrated by the PluginManager
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    progress_updates = [] # To capture progress updates for verification

    async def demo_progress_callback(**kwargs):
        # A more sophisticated callback might filter by plugin_id or action_name
        print(f"[DEMO CALLBACK] Progress: {kwargs}")
        progress_updates.append(kwargs)

    async def run_plugin_demo():
        plugin_config = {"some_setting": "value"}
        example_plugin = ExampleLongRunningPlugin(
            plugin_id="com.example.longrunner",
            plugin_version="1.0.0",
            config=plugin_config,
            progress_callback=demo_progress_callback
        )

        # Test synchronous action via execute_action
        try:
            sync_result = await example_plugin.execute_action("synchronous_greet", name="Plugin User")
            print(f"Sync greet result: {sync_result}")
        except PluginError as e:
            print(f"Error in synchronous_greet: {e}")

        # Test async action with progress
        try:
            print("\nStarting long_computation_task (successful_run)...")
            result = await example_plugin.execute_action("long_computation_task", steps=4, task_id="successful_run")
            print(f"Result of successful_run: {result}")
        except PluginError as e:
            print(f"Error during successful_run: {e}")

        # Test async action designed to fail
        try:
            print("\nStarting long_computation_task (simulated_failure)...")
            await example_plugin.execute_action("long_computation_task", steps=5, task_id="simulated_failure")
        except PluginExecutionError as e:
            print(f"Caught expected failure in simulated_failure: {e}")
        except PluginError as e:
            print(f"Other error during simulated_failure: {e}")

        # Verify captured progress updates (basic check)
        print(f"\nCaptured {len(progress_updates)} progress updates during demo.")
        for update in progress_updates:
            if update.get("action_name") == "long_computation_task" and update.get("additional_data", {}).get("task_id") == "successful_run":
                assert update.get("plugin_id") == "com.example.longrunner"
        print("Basic progress update verification passed.")

    asyncio.run(run_plugin_demo())

