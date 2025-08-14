import asyncio
from typing import Callable, Optional, Any, Dict, List

# Assuming BasePlugin and exceptions are in agent_project.src.core
# Adjust path if necessary based on actual project structure and PYTHONPATH
from ....core.base_plugin import BasePlugin
from ....core.plugin_exceptions import PluginActionExecutionError

class ExampleAsyncPlugin(BasePlugin):
    """
    An example plugin demonstrating asynchronous actions and progress reporting.
    """

    def __init__(self, plugin_id: str, plugin_name: str, version: str, description: str, config: dict = None):
        super().__init__(plugin_id, plugin_name, version, description, config)
        # No specific initialization needed for this example beyond base class

    def initialize(self, agent_context: dict = None) -> None:
        """Initializes the plugin with agent context."""
        super().initialize(agent_context)
        # Example: self.logger = agent_context.get("logger") if agent_context else print
        # self.logger(f"ExampleAsyncPlugin 	'{self.plugin_id}	' initialized.")
        print(f"ExampleAsyncPlugin 	'{self.plugin_id}	' initialized.")

    def get_actions(self) -> List[Dict[str, Any]]:
        """Returns the actions this plugin can perform, matching plugin.json."""
        return [
            {
                "name": "long_running_task",
                "description": "Simulates a long-running task that reports progress asynchronously.",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "duration_seconds": {"type": "integer", "description": "Total task duration in seconds.", "default": 5},
                        "steps": {"type": "integer", "description": "Number of progress steps.", "default": 10}
                    }
                },
                "returns_schema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "message": {"type": "string"}
                    }
                }
            }
        ]

    async def execute_action(self, action_name: str, params: dict = None, progress_callback: Optional[Callable[[dict], None]] = None) -> Any:
        """Executes a specific action, handling asynchronous tasks and progress reporting."""
        if action_name == "long_running_task":
            return await self._handle_long_running_task(params, progress_callback)
        else:
            raise PluginActionNotFoundError(f"Action 	'{action_name}	' not found in ExampleAsyncPlugin.")

    async def _handle_long_running_task(self, params: dict, progress_callback: Optional[Callable[[dict], None]]) -> Dict[str, str]:
        """Handles the simulation of a long-running task with progress reporting."""
        params = params or {}
        duration_seconds = params.get("duration_seconds", 5)
        steps = params.get("steps", 10)

        if not isinstance(duration_seconds, int) or duration_seconds <= 0:
            duration_seconds = 5
        if not isinstance(steps, int) or steps <= 0:
            steps = 10

        print(f"Starting long_running_task for {duration_seconds} seconds with {steps} steps.")

        for i in range(steps):
            await asyncio.sleep(duration_seconds / steps)  # Simulate work
            progress_percentage = ((i + 1) / steps) * 100
            progress_message = f"Step {i + 1} of {steps} completed."
            
            if progress_callback:
                try:
                    # If progress_callback is an async function, await it
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback({"percentage": round(progress_percentage, 2), "message": progress_message})
                    else: # Otherwise, call it directly (assuming it's synchronous)
                        progress_callback({"percentage": round(progress_percentage, 2), "message": progress_message})
                except Exception as e:
                    # Log error but continue the task, as progress reporting is secondary
                    print(f"Error in progress_callback: {e}")
            
            print(f"Progress: {progress_percentage:.2f}% - {progress_message}")

        final_message = f"Long-running task completed after {duration_seconds} seconds."
        print(final_message)
        return {"status": "completed", "message": final_message}

    def shutdown(self) -> None:
        """Performs cleanup when the plugin is shut down."""
        # self.logger(f"ExampleAsyncPlugin 	'{self.plugin_id}	' shutting down.")
        print(f"ExampleAsyncPlugin 	'{self.plugin_id}	' shutting down.")
        pass

# Example of how the PluginManager might load and use this (for testing purposes):
# async def main():
#     plugin = ExampleAsyncPlugin(
#         plugin_id="example_async", 
#         plugin_name="Async Example", 
#         version="1.0.0", 
#         description="Test async plugin"
#     )
#     plugin.initialize()
# 
#     def my_progress_callback(progress_data):
#         print(f"[CALLBACK] Progress: {progress_data}")
# 
#     result = await plugin.execute_action(
#         action_name="long_running_task", 
#         params={"duration_seconds": 3, "steps": 6},
#         progress_callback=my_progress_callback
#     )
#     print(f"Final result: {result}")
#     plugin.shutdown()
# 
# if __name__ == "__main__":
#     asyncio.run(main())

