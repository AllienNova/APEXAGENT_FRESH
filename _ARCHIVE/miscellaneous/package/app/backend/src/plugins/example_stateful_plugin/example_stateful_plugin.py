import logging
from core.base_plugin import BasePlugin
from core.plugin_exceptions import PluginActionNotFoundError, PluginActionExecutionError

logger = logging.getLogger(__name__)

class StatefulPlugin(BasePlugin):
    """
    An example plugin that demonstrates saving and loading its internal state.
    It maintains a simple counter that persists across sessions.
    """
    def __init__(self, plugin_id: str, plugin_name: str, version: str, description: str, config: dict = None):
        super().__init__(plugin_id, plugin_name, version, description, config)
        self.counter = 0 # Default initial state for the counter
        logger.info(f"StatefulPlugin 	'{self.plugin_id}	' (v{self.version}) __init__ called. Initial counter: {self.counter}")

    def initialize(self, agent_context: dict = None) -> None:
        super().initialize(agent_context)
        logger.info(f"StatefulPlugin 	'{self.plugin_id}	' (v{self.version}) initializing...")
        
        # Load persisted state
        try:
            loaded_state = self.load_state()
            if loaded_state is not None and isinstance(loaded_state, dict):
                self.counter = loaded_state.get("counter", 0)
                logger.info(f"StatefulPlugin 	'{self.plugin_id}	' loaded state. Counter set to: {self.counter}")
            else:
                logger.info(f"StatefulPlugin 	'{self.plugin_id}	' no prior state found or state was invalid. Using default counter: {self.counter}")
        except Exception as e:
            # Log the error but don't let it prevent initialization; use default state.
            logger.error(f"StatefulPlugin 	'{self.plugin_id}	' error loading state during initialize: {e}. Using default counter: {self.counter}", exc_info=True)
            # self.counter remains at its default value
        
        logger.info(f"StatefulPlugin 	'{self.plugin_id}	' (v{self.version}) initialized. Current counter: {self.counter}")

    def get_actions(self) -> list[dict]:
        return [
            {
                "name": "get_counter",
                "description": "Gets the current value of the persistent counter.",
                "parameters_schema": {},
                "returns_schema": {
                    "type": "object",
                    "properties": {
                        "counter": {"type": "integer"}
                    }
                }
            },
            {
                "name": "increment_counter",
                "description": "Increments the persistent counter by a given amount and saves the new state.",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "integer", "default": 1}
                    }
                },
                "returns_schema": {
                    "type": "object",
                    "properties": {
                        "new_counter": {"type": "integer"}
                    }
                }
            }
        ]

    def execute_action(self, action_name: str, params: dict = None, progress_callback: callable = None) -> any:
        params = params or {}
        logger.info(f"StatefulPlugin 	'{self.plugin_id}	' executing action: {action_name} with params: {params}")

        if action_name == "get_counter":
            return {"counter": self.counter}
        
        elif action_name == "increment_counter":
            amount = params.get("amount", 1)
            if not isinstance(amount, int):
                raise PluginActionExecutionError("Parameter 'amount' must be an integer.")
            
            self.counter += amount
            logger.info(f"StatefulPlugin 	'{self.plugin_id}	' counter incremented to: {self.counter}")
            
            # Save the new state
            try:
                self.save_state({"counter": self.counter})
                logger.info(f"StatefulPlugin 	'{self.plugin_id}	' state saved successfully. Counter: {self.counter}")
            except Exception as e:
                # Log error but action can still return the new counter value
                logger.error(f"StatefulPlugin 	'{self.plugin_id}	' error saving state after increment: {e}", exc_info=True)
                # Optionally, re-raise if saving state is critical for this action's success
                # raise PluginActionExecutionError(f"Failed to save state after increment: {e}", original_exception=e)
            
            return {"new_counter": self.counter}
        
        else:
            raise PluginActionNotFoundError(f"Action 	'{action_name}	' is not implemented by {self.plugin_id}.")

    def shutdown(self) -> None:
        logger.info(f"StatefulPlugin 	'{self.plugin_id}	' (v{self.version}) shutting down. Current counter: {self.counter}")
        # Save the final state on shutdown
        try:
            self.save_state({"counter": self.counter})
            logger.info(f"StatefulPlugin 	'{self.plugin_id}	' final state saved successfully during shutdown. Counter: {self.counter}")
        except Exception as e:
            logger.error(f"StatefulPlugin 	'{self.plugin_id}	' error saving state during shutdown: {e}", exc_info=True)
        logger.info(f"StatefulPlugin 	'{self.plugin_id}	' (v{self.version}) shutdown complete.")

