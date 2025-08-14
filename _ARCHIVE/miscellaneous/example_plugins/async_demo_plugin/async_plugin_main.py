import asyncio
from typing import Optional, Callable, Dict, Any

# Assuming these are in the python path when the plugin is loaded by PluginManager
# For standalone testing, you might need to adjust sys.path or place them appropriately.
from core.base_plugin import BasePlugin
from core.async_utils import ProgressUpdate, CancellationToken
from core.plugin_exceptions import PluginActionExecutionError

class AsyncDemoPlugin(BasePlugin):
    """A plugin demonstrating asynchronous actions, progress reporting, and cancellation."""

    def initialize(self, agent_context: Optional[Dict[str, Any]] = None) -> None:
        super().initialize(agent_context)
        # No specific initialization needed for this demo plugin
        self.logger = agent_context.get("logger") if agent_context else None
        if self.logger:
            self.logger.info(f"AsyncDemoPlugin {self.version} initialized.")
        else:
            print(f"AsyncDemoPlugin {self.version} initialized (logger not available).")

    def get_actions(self) -> list[dict]:
        """Returns the actions this plugin can perform, matching plugin.json."""
        return [
            {
                "name": "long_computation",
                "description": "Simulates a long computation that reports progress and can be cancelled.",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "duration_seconds": {
                            "type": "integer",
                            "description": "The number of seconds the task should simulate running for.",
                            "default": 5
                        },
                        "steps": {
                            "type": "integer",
                            "description": "The number of steps to divide the duration into for progress reporting.",
                            "default": 5
                        }
                    }
                },
                "returns_schema": {
                    "type": "string",
                    "description": "A message indicating the result of the computation."
                }
            }
        ]

    async def execute_action(
        self, 
        action_name: str, 
        params: Optional[dict] = None, 
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
        cancellation_token: Optional[CancellationToken] = None
    ) -> str:
        """Executes the specified asynchronous action."""
        if action_name == "long_computation":
            if params is None:
                params = {}
            duration_seconds = params.get("duration_seconds", 5)
            steps = params.get("steps", 5)

            if not isinstance(duration_seconds, int) or duration_seconds <= 0:
                raise PluginActionExecutionError("duration_seconds must be a positive integer.")
            if not isinstance(steps, int) or steps <= 0:
                raise PluginActionExecutionError("steps must be a positive integer.")

            if self.logger:
                self.logger.info(f"Starting long_computation for {duration_seconds}s in {steps} steps.")
            else:
                print(f"Starting long_computation for {duration_seconds}s in {steps} steps.")

            if progress_callback:
                progress_callback(ProgressUpdate(
                    percentage=0.0, 
                    message="Starting long computation...", 
                    status="running"
                ))

            for i in range(steps):
                if cancellation_token and cancellation_token.is_cancelled:
                    message = "Long computation cancelled by request."
                    if self.logger:
                        self.logger.info(message)
                    else:
                        print(message)
                    if progress_callback:
                        progress_callback(ProgressUpdate(
                            percentage=(i / steps) * 100.0, 
                            message=message, 
                            status="cancelled"
                        ))
                    return message

                # Simulate work for one step
                await asyncio.sleep(duration_seconds / steps)
                
                current_percentage = ((i + 1) / steps) * 100.0
                progress_message = f"Step {i + 1} of {steps} completed."
                
                if self.logger:
                    self.logger.debug(f"Progress: {current_percentage}% - {progress_message}")

                if progress_callback:
                    progress_callback(ProgressUpdate(
                        percentage=current_percentage, 
                        message=progress_message, 
                        status="running"
                    ))
            
            final_message = "Long computation completed successfully."
            if self.logger:
                self.logger.info(final_message)
            else:
                print(final_message)

            if progress_callback:
                progress_callback(ProgressUpdate(
                    percentage=100.0, 
                    message=final_message, 
                    status="completed"
                ))
            return final_message
        else:
            raise PluginActionNotFoundError(f"Action 	\"{action_name}\" not found in AsyncDemoPlugin.")

    def shutdown(self) -> None:
        if self.logger:
            self.logger.info("AsyncDemoPlugin shutdown.")
        else:
            print("AsyncDemoPlugin shutdown.")

