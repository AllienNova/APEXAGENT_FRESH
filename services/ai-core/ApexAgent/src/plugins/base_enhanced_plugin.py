# src/plugins/base_enhanced_plugin.py
import inspect
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Awaitable
from pydantic import BaseModel, ValidationError, create_model

from src.core.plugin_exceptions import InvalidInputError, PluginExecutionError, ApiKeyMissingError, ExternalServiceError
from src.core.api_key_manager import ApiKeyManager # Assuming ApiKeyManager is accessible

logger = logging.getLogger(__name__)

class BaseEnhancedPlugin(ABC):
    """
    Base class for enhanced plugins with metadata-driven actions, Pydantic validation,
    standardized error handling, and async support.
    """
    def __init__(self, api_key_manager: ApiKeyManager = None):
        self.plugin_name: str = self.__class__.__name__
        self.api_key_manager = api_key_manager if api_key_manager else ApiKeyManager() # Use a default if not provided
        # Metadata would typically be loaded by the PluginManager and passed or made accessible
        # For now, we assume action_specs are available to the plugin instance if needed for validation setup

    def _get_pydantic_model_for_action(self, action_name: str, parameters_spec: List[Dict[str, Any]]) -> Type[BaseModel]:
        """Dynamically creates a Pydantic model for an action's parameters."""
        fields = {}
        for param_spec in parameters_spec:
            param_name = param_spec["name"]
            param_type_str = param_spec["type"]
            is_required = param_spec.get("required", False)
            
            # Basic type mapping (can be expanded)
            type_map = {
                "string": str,
                "integer": int,
                "boolean": bool,
                "array": List,
                "object": Dict,
                "float": float,
                "datetime": str # Pydantic can parse ISO strings to datetime, or use datetime.datetime
            }
            field_type = type_map.get(param_type_str, Any) # Default to Any if type unknown

            if is_required:
                fields[param_name] = (field_type, ...)
            else:
                default_value = param_spec.get("default") # Pydantic needs a default for optional fields
                fields[param_name] = (field_type, default_value)
        
        # Create a unique model name to avoid Pydantic warnings/errors
        model_name = f"{self.plugin_name}_{action_name}_InputModel"
        return create_model(model_name, **fields)

    async def execute_action(self, action_name: str, action_params_spec: List[Dict[str, Any]], required_api_keys: List[str], **kwargs) -> Any:
        """
        Executes a plugin action with Pydantic validation and standardized error handling.
        `action_params_spec` is the 'parameters' list from the action's metadata.
        `required_api_keys` is the list of service names for API keys from plugin metadata.
        """
        logger.debug(f"Attempting to execute action 	'{action_name}	' in plugin 	'{self.plugin_name}	' with args: {kwargs}")

        # 1. Check for required API keys
        for key_service_name in required_api_keys:
            if not self.api_key_manager.get_api_key(key_service_name) and not self.api_key_manager.get_oauth_token(key_service_name):
                logger.error(f"API key/token for service 	'{key_service_name}	' missing for action 	'{action_name}	' in plugin 	'{self.plugin_name}	'.")
                raise ApiKeyMissingError(service_name=key_service_name)
            logger.debug(f"API key/token for service 	'{key_service_name}	' found.")

        # 2. Get and validate input using Pydantic model
        InputModel = self._get_pydantic_model_for_action(action_name, action_params_spec)
        try:
            validated_args = InputModel(**kwargs)
            logger.debug(f"Action 	'{action_name}	' arguments validated successfully.")
        except ValidationError as e:
            logger.error(f"Input validation failed for action 	'{action_name}	' in plugin 	'{self.plugin_name}	': {e.errors()}")
            raise InvalidInputError(errors=e.errors())

        # 3. Get the actual method to call
        action_method: Callable[..., Awaitable[Any]] = getattr(self, action_name, None)
        if not action_method or not callable(action_method):
            logger.error(f"Action method 	'{action_name}	' not found or not callable in plugin 	'{self.plugin_name}	'.")
            raise PluginExecutionError(action_name=action_name, plugin_name=self.plugin_name, message=f"Action method 	'{action_name}	' not implemented.")

        if not inspect.iscoroutinefunction(action_method):
            logger.warning(f"Action method 	'{action_name}	' in plugin 	'{self.plugin_name}	' is not async. Consider making it async for non-blocking IO.")
            # For now, we'll allow synchronous methods but the core might expect awaitables.
            # A more robust solution would be to run sync methods in a thread pool executor.

        # 4. Execute the action method
        try:
            logger.info(f"Executing action: {self.plugin_name}.{action_name}")
            # Pass validated arguments as keyword arguments
            result = await action_method(**validated_args.model_dump()) 
            logger.info(f"Action 	'{action_name}	' executed successfully by plugin 	'{self.plugin_name}	'.")
            return result
        except ApiKeyMissingError as e: # Re-raise if caught from within the action method itself
            raise e
        except InvalidInputError as e: # Re-raise
            raise e
        except ExternalServiceError as e: # Re-raise
            logger.error(f"External service error during action 	'{action_name}	' in plugin 	'{self.plugin_name}	': {e}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error during execution of action 	'{action_name}	' in plugin 	'{self.plugin_name}	': {e}")
            raise PluginExecutionError(action_name=action_name, plugin_name=self.plugin_name, original_exception=e)

    # Plugin developers will implement their specific actions as async methods
    # Example:
    # @abstractmethod
    # async def specific_action_name(self, param1: str, param2: int) -> Dict:
    #     pass

# Example of how a concrete plugin might use this:
# class MySamplePlugin(BaseEnhancedPlugin):
#     async def greet(self, name: str, enthusiasm: int = 1) -> str:
#         if name == "error":
#             raise ValueError("Simulated error in greet")
#         if name == "external_error":
#             raise ExternalServiceError(service_name="greeting_service", error_details="Service unavailable")
#         return f"Hello, {name}{'!' * enthusiasm}"

#     async def calculate_sum(self, a: int, b: int) -> int:
#         return a + b

# The PluginManager would call `plugin_instance.execute_action(...)`
# after loading the plugin and its metadata.

