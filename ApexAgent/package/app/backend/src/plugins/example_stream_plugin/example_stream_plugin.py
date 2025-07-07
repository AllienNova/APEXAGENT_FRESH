import asyncio
from typing import Callable, Optional, Any, AsyncIterator

# Assuming BasePlugin and exceptions are in a discoverable path or handled by PluginManager's sys.path manipulation
# For local testing, you might need to adjust imports if core is not in PYTHONPATH
try:
    from core.base_plugin import BasePlugin
    from core.plugin_exceptions import PluginActionExecutionError, StreamingNotSupportedError
except ImportError:
    # Fallback for scenarios where core might not be directly in PYTHONPATH during isolated testing
    # This is a simplified placeholder for development; production packaging should handle this.
    class BasePlugin: # type: ignore
        def __init__(self, plugin_id, plugin_name, version, description, config=None):
            self._plugin_id = plugin_id
            self._plugin_name = plugin_name
            self._version = version
            self._description = description
            self.config = config or {}
            self.agent_context = None
        @property
        def plugin_id(self) -> str: return self._plugin_id
        @property
        def name(self) -> str: return self._plugin_name
        @property
        def version(self) -> str: return self._version
        @property
        def description(self) -> str: return self._description
        def initialize(self, agent_context=None): self.agent_context = agent_context
        def get_actions(self): return []
        def execute_action(self, action_name, params=None, progress_callback=None): raise NotImplementedError
        async def execute_action_stream(self, action_name: str, params: dict = None, progress_callback: Optional[Callable[[dict], None]] = None) -> AsyncIterator[Any]:
            raise NotImplementedError
            if False: yield
        def shutdown(self): pass
    class PluginActionExecutionError(Exception): pass # type: ignore
    class StreamingNotSupportedError(Exception): pass # type: ignore


class ExampleStreamPlugin(BasePlugin):
    def initialize(self, agent_context: dict = None) -> None:
        super().initialize(agent_context)
        # No specific initialization needed for this example
        print(f"ExampleStreamPlugin 	'{self.plugin_id}	' initialized.")

    def get_actions(self) -> list[dict]:
        # This could be dynamically generated or read from metadata again
        # For simplicity, returning what's defined in plugin.json
        return [
            {
                "name": "generate_numbers_stream",
                "description": "Streams a sequence of numbers with a delay.",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Number of items to stream.", "default": 5},
                        "delay": {"type": "number", "description": "Delay in seconds between items.", "default": 0.5}
                    }
                },
                "returns_stream": True
            },
            {
                "name": "echo_message",
                "description": "Returns a simple echo message (non-streaming).",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Message to echo."}
                    },
                    "required": ["message"]
                },
                "returns_stream": False
            }
        ]

    async def execute_action_stream(self, action_name: str, params: dict = None, progress_callback: Optional[Callable[[dict], None]] = None) -> AsyncIterator[Any]:
        if action_name == "generate_numbers_stream":
            count = params.get("count", 5) if params else 5
            delay = params.get("delay", 0.5) if params else 0.5

            if not isinstance(count, int) or count < 0:
                raise PluginActionExecutionError("Parameter 'count' must be a non-negative integer.")
            if not isinstance(delay, (int, float)) or delay < 0:
                raise PluginActionExecutionError("Parameter 'delay' must be a non-negative number.")

            for i in range(count):
                if progress_callback:
                    progress_callback({
                        "status": "streaming", 
                        "current_item": i + 1, 
                        "total_items": count,
                        "message": f"Streaming item {i+1} of {count}"
                    })
                yield {"number": i, "message": f"Streamed number {i}"}
                await asyncio.sleep(delay)
            
            if progress_callback:
                progress_callback({"status": "completed", "total_items_streamed": count})
        else:
            # This specific method is for streaming actions. 
            # If called for a non-streaming action, or an unknown one, raise StreamingNotSupportedError.
            raise StreamingNotSupportedError(f"Action 	'{action_name}	' on plugin 	'{self.plugin_id}	' does not support asynchronous streaming via execute_action_stream or is not found.")

    def execute_action(self, action_name: str, params: dict = None, progress_callback: Optional[Callable[[dict], None]] = None) -> Any:
        if action_name == "echo_message":
            message = params.get("message", "No message provided") if params else "No message provided"
            if progress_callback:
                progress_callback({"status": "processing", "message": "Echoing message"})
            result = f"Echo from ExampleStreamPlugin: {message}"
            if progress_callback:
                progress_callback({"status": "completed", "result_length": len(result)})
            return result
        elif action_name == "generate_numbers_stream":
            # This action is designed for execute_action_stream.
            # A plugin could choose to also offer a non-streaming version here (e.g., returning a list),
            # or explicitly state it's only streamable.
            raise StreamingNotSupportedError(f"Action 	'{action_name}	' is designed for streaming and should be called via execute_action_stream.")
        else:
            raise PluginActionExecutionError(f"Action 	'{action_name}	' not found in ExampleStreamPlugin.")

    def shutdown(self) -> None:
        print(f"ExampleStreamPlugin 	'{self.plugin_id}	' shutting down.")

