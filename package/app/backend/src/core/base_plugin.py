from abc import ABC, abstractmethod
from typing import Callable, Optional, Any, Union, Iterator, AsyncIterator, List, Dict, Type, TypeVar, Generic

# Import new async utility classes
from .async_utils import ProgressUpdate, CancellationToken 

from .plugin_exceptions import (
    PluginError, # Import base for type hinting if needed
    PluginInitializationError,
    PluginConfigurationError,
    PluginActionNotFoundError,
    PluginInvalidActionParametersError,
    PluginActionExecutionError,
    PluginDependencyError,
    PluginResourceNotFoundError,
    StreamingNotSupportedError, # Added for stream handling
    StreamTransformationError,  # New exception for stream transformation errors
    StreamCompositionError,     # New exception for stream composition errors
    StreamPersistenceError      # New exception for stream persistence errors
)

# Define type variables for generic stream types
T = TypeVar('T')
U = TypeVar('U')

# Define a type alias for streamable results
StreamableOutput = Union[Any, Iterator[Any], AsyncIterator[Any]]

class StreamMetadata:
    """
    Metadata for a stream, including information about its content, format, and capabilities.
    """
    def __init__(self, 
                 content_type: str = "application/json", 
                 item_schema: Optional[Dict] = None,
                 supports_transformation: bool = False,
                 supports_composition: bool = False,
                 supports_persistence: bool = False,
                 estimated_size: Optional[int] = None,
                 additional_info: Optional[Dict] = None):
        """
        Initialize stream metadata.
        
        Args:
            content_type (str): MIME type of the stream content. Defaults to "application/json".
            item_schema (Optional[Dict]): JSON schema describing the structure of items in the stream.
            supports_transformation (bool): Whether the stream supports transformation operations.
            supports_composition (bool): Whether the stream can be composed with other streams.
            supports_persistence (bool): Whether the stream supports persistence and resumption.
            estimated_size (Optional[int]): Estimated number of items in the stream, if known.
            additional_info (Optional[Dict]): Additional stream-specific metadata.
        """
        self.content_type = content_type
        self.item_schema = item_schema
        self.supports_transformation = supports_transformation
        self.supports_composition = supports_composition
        self.supports_persistence = supports_persistence
        self.estimated_size = estimated_size
        self.additional_info = additional_info or {}

class StreamCheckpoint:
    """
    Represents a checkpoint in a stream that can be used for persistence and resumption.
    """
    def __init__(self, 
                 stream_id: str,
                 position: int,
                 state: Dict[str, Any],
                 timestamp: float):
        """
        Initialize a stream checkpoint.
        
        Args:
            stream_id (str): Unique identifier for the stream.
            position (int): Position in the stream (e.g., item count).
            state (Dict[str, Any]): State information needed to resume the stream.
            timestamp (float): Unix timestamp when the checkpoint was created.
        """
        self.stream_id = stream_id
        self.position = position
        self.state = state
        self.timestamp = timestamp

class BasePlugin(ABC):
    """
    Abstract Base Class for all ApexAgent plugins.

    Plugins must inherit from this class and implement all abstract methods.
    The PluginManager will expect plugins to conform to this interface for loading,
    action execution, and lifecycle management.
    """

    def __init__(self, plugin_id: str, plugin_name: str, version: str, description: str, config: dict = None):
        """
        Initializes the base plugin attributes.
        This constructor can be called by subclasses using super().__init__(...).

        Args:
            plugin_id (str): The unique ID of the plugin (from metadata).
            plugin_name (str): The human-readable name of the plugin (from metadata).
            version (str): The version of the plugin (from metadata).
            description (str): The description of the plugin (from metadata).
            config (dict, optional): Plugin-specific configuration. Defaults to None.
        
        Raises:
            PluginConfigurationError: If the provided config is invalid during basic setup by the plugin.
        """
        self._plugin_id = plugin_id
        self._plugin_name = plugin_name
        self._version = version
        self._description = description
        self.config = config if config is not None else {}
        self.agent_context = None # To be set by the PluginManager during initialization

    @property
    def plugin_id(self) -> str:
        """Returns the unique identifier of the plugin."""
        return self._plugin_id

    @property
    def name(self) -> str:
        """Returns the human-readable name of the plugin."""
        return self._plugin_name

    @property
    def version(self) -> str:
        """Returns the version of the plugin."""
        return self._version

    @property
    def description(self) -> str:
        """Returns the description of the plugin."""
        return self._description

    @abstractmethod
    def initialize(self, agent_context: dict = None) -> None:
        """
        Called by the PluginManager after the plugin instance is created and loaded.
        Plugins should perform any necessary setup or initialization here, such as
        loading resources, validating essential configuration, or establishing connections.

        Args:
            agent_context (dict, optional): A dictionary containing references to core agent
                                          services or context information that the plugin might need.
                                          The exact structure of this context is TBD.
        Raises:
            PluginInitializationError: If a non-recoverable error occurs during initialization
                                       that prevents the plugin from becoming operational.
            PluginConfigurationError: If plugin-specific configuration passed via `self.config`
                                      is found to be invalid or missing critical values during initialization.
            PluginDependencyError: If a critical runtime dependency (e.g., another service, external library)
                                   cannot be met during initialization.
            PluginResourceNotFoundError: If an essential resource file for the plugin cannot be found.
        """
        self.agent_context = agent_context
        pass

    @abstractmethod
    def get_actions(self) -> list[dict]:
        """
        Returns a list of actions that this plugin can perform.
        Each action should be a dictionary, potentially including:
        - "name": (str) The unique name of the action within this plugin.
        - "description": (str) A human-readable description of what the action does.
        - "parameters_schema": (dict, optional) A JSON schema describing the expected parameters for this action.
        - "returns_schema": (dict, optional) A JSON schema describing the expected return value of this action.
        - "returns_stream": (bool, optional) Indicates if the action returns a stream (iterator/generator). Defaults to False.
        - "stream_metadata": (dict, optional) Additional metadata about the stream capabilities if returns_stream is True.
        
        This information should align with the "actions" field in the plugin.json metadata,
        but this method allows the plugin to dynamically generate or confirm its actions if needed.
        """
        pass

    @abstractmethod
    def execute_action(self, 
                       action_name: str, 
                       params: Optional[dict] = None, 
                       progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
                       cancellation_token: Optional[CancellationToken] = None
                       ) -> StreamableOutput:
        """
        Executes a specific action provided by the plugin.
        This method can be defined as a regular synchronous method or an asynchronous (async def) method by the plugin developer.
        The PluginManager will inspect it and call/await it appropriately.
        The action can return a single value, an iterator/generator for synchronous streams, or an async iterator/generator for asynchronous streams.

        Args:
            action_name (str): The name of the action to execute.
                               This must match one of the action names returned by get_actions().
            params (Optional[dict]): A dictionary of parameters for the action.
                                     The structure should conform to the action's parameters_schema. Defaults to None.
            progress_callback (Optional[Callable[[ProgressUpdate], None]]):
                A callback function that the plugin can use to report progress during execution.
                The callback expects a ProgressUpdate object. Defaults to None.
            cancellation_token (Optional[CancellationToken]): 
                A token that the plugin can check to see if cancellation has been requested.
                Plugins performing long-running operations should periodically check `cancellation_token.is_cancelled`.
                Defaults to None.

        Returns:
            StreamableOutput: The result of the action execution. This can be a single value, an iterator, or an async iterator.
                              If this method is defined as `async def`, it will return an Awaitable that resolves to one of these types.

        Raises:
            PluginActionNotFoundError: If the `action_name` is not supported or recognized by this plugin.
            PluginInvalidActionParametersError: If the provided `params` are invalid for the specified action
                                                (e.g., missing required parameters, incorrect types, values out of range).
            PluginActionExecutionError: For general, unexpected errors that occur during the internal logic
                                        of an action's execution, after parameters have been validated.
                                        It's recommended to wrap internal exceptions in this for clarity.
            PluginDependencyError: If the action relies on a runtime dependency that is unavailable.
            PluginResourceNotFoundError: If the action requires a resource that cannot be found.
        """
        pass

    async def execute_action_stream(self, 
                                    action_name: str, 
                                    params: Optional[dict] = None, 
                                    progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
                                    cancellation_token: Optional[CancellationToken] = None
                                    ) -> AsyncIterator[Any]:
        """
        Executes a specific action that provides an asynchronous stream of results.
        Plugins that support streaming output for an action should override this method.
        The method should `yield` data chunks as they become available.

        Args:
            action_name (str): The name of the action to execute.
            params (Optional[dict]): A dictionary of parameters for the action. Defaults to None.
            progress_callback (Optional[Callable[[ProgressUpdate], None]]):
                A callback function for out-of-band progress updates, expecting a ProgressUpdate object.
                Defaults to None.
            cancellation_token (Optional[CancellationToken]): 
                A token for checking cancellation status. Defaults to None.

        Yields:
            Any: Data chunks from the stream.

        Raises:
            StreamingNotSupportedError: If this plugin or specific action does not support streaming output via this method.
            PluginActionNotFoundError: If the `action_name` is not supported or recognized by this plugin.
            PluginInvalidActionParametersError: If the provided `params` are invalid for the specified action.
            PluginActionExecutionError: For general, unexpected errors that occur during the stream generation.
            PluginDependencyError: If the action relies on a runtime dependency that is unavailable.
            PluginResourceNotFoundError: If the action requires a resource that cannot be found.
        """
        raise StreamingNotSupportedError(f"Action '{action_name}' on plugin '{self.plugin_id}' does not support asynchronous streaming via execute_action_stream.")
        if False: # pragma: no cover
            yield

    async def get_stream_metadata(self, 
                                 action_name: str, 
                                 params: Optional[dict] = None
                                 ) -> StreamMetadata:
        """
        Returns metadata about a stream that would be produced by the specified action.
        This allows consumers to understand the stream's capabilities before execution.

        Args:
            action_name (str): The name of the action that would produce the stream.
            params (Optional[dict]): Parameters that would be passed to the action. Defaults to None.

        Returns:
            StreamMetadata: Metadata about the stream.

        Raises:
            StreamingNotSupportedError: If the action does not support streaming.
            PluginActionNotFoundError: If the action is not found.
            PluginInvalidActionParametersError: If the parameters are invalid.
        """
        # Default implementation returns basic metadata
        # Plugins should override this to provide more specific information
        actions = self.get_actions()
        action_info = next((a for a in actions if a["name"] == action_name), None)
        
        if not action_info:
            raise PluginActionNotFoundError(f"Action '{action_name}' not found in plugin '{self.plugin_id}'")
            
        if not action_info.get("returns_stream", False):
            raise StreamingNotSupportedError(f"Action '{action_name}' does not support streaming")
            
        # Return basic metadata
        return StreamMetadata(
            content_type="application/json",
            item_schema=action_info.get("returns_schema"),
            supports_transformation=False,
            supports_composition=False,
            supports_persistence=False
        )

    async def transform_stream(self, 
                              stream: AsyncIterator[T], 
                              transform_type: str,
                              transform_params: Optional[dict] = None,
                              progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
                              cancellation_token: Optional[CancellationToken] = None
                              ) -> AsyncIterator[U]:
        """
        Applies a transformation to a stream.
        
        Args:
            stream (AsyncIterator[T]): The input stream to transform.
            transform_type (str): The type of transformation to apply (e.g., "map", "filter", "batch").
            transform_params (Optional[dict]): Parameters for the transformation. Defaults to None.
            progress_callback (Optional[Callable[[ProgressUpdate], None]]): Callback for progress updates.
            cancellation_token (Optional[CancellationToken]): Token for cancellation checks.
            
        Yields:
            U: Transformed items.
            
        Raises:
            StreamTransformationError: If the transformation fails or is not supported.
        """
        # Default implementation just passes through the stream
        # Plugins should override this to provide actual transformations
        raise StreamTransformationError(f"Stream transformation '{transform_type}' is not supported by plugin '{self.plugin_id}'")
        if False: # pragma: no cover
            async for item in stream:
                yield item

    async def compose_streams(self, 
                             streams: List[AsyncIterator[Any]], 
                             composition_type: str,
                             composition_params: Optional[dict] = None,
                             progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
                             cancellation_token: Optional[CancellationToken] = None
                             ) -> AsyncIterator[Any]:
        """
        Composes multiple streams into a single stream.
        
        Args:
            streams (List[AsyncIterator[Any]]): The input streams to compose.
            composition_type (str): The type of composition to apply (e.g., "merge", "zip", "concat").
            composition_params (Optional[dict]): Parameters for the composition. Defaults to None.
            progress_callback (Optional[Callable[[ProgressUpdate], None]]): Callback for progress updates.
            cancellation_token (Optional[CancellationToken]): Token for cancellation checks.
            
        Yields:
            Any: Items from the composed stream.
            
        Raises:
            StreamCompositionError: If the composition fails or is not supported.
        """
        # Default implementation raises an error
        # Plugins should override this to provide actual composition
        raise StreamCompositionError(f"Stream composition '{composition_type}' is not supported by plugin '{self.plugin_id}'")
        if False: # pragma: no cover
            yield None

    async def create_stream_checkpoint(self, 
                                      stream_id: str,
                                      position: int,
                                      state: Dict[str, Any]
                                      ) -> StreamCheckpoint:
        """
        Creates a checkpoint for a stream that can be used for persistence and resumption.
        
        Args:
            stream_id (str): Unique identifier for the stream.
            position (int): Position in the stream (e.g., item count).
            state (Dict[str, Any]): State information needed to resume the stream.
            
        Returns:
            StreamCheckpoint: A checkpoint object.
            
        Raises:
            StreamPersistenceError: If checkpoint creation fails.
        """
        # Default implementation creates a basic checkpoint
        # Plugins should override this to provide more sophisticated checkpointing
        import time
        return StreamCheckpoint(
            stream_id=stream_id,
            position=position,
            state=state,
            timestamp=time.time()
        )

    async def resume_stream_from_checkpoint(self, 
                                           action_name: str,
                                           checkpoint: StreamCheckpoint,
                                           params: Optional[dict] = None,
                                           progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
                                           cancellation_token: Optional[CancellationToken] = None
                                           ) -> AsyncIterator[Any]:
        """
        Resumes a stream from a checkpoint.
        
        Args:
            action_name (str): The name of the action that produced the original stream.
            checkpoint (StreamCheckpoint): The checkpoint to resume from.
            params (Optional[dict]): Additional parameters for the resumption. Defaults to None.
            progress_callback (Optional[Callable[[ProgressUpdate], None]]): Callback for progress updates.
            cancellation_token (Optional[CancellationToken]): Token for cancellation checks.
            
        Yields:
            Any: Items from the resumed stream.
            
        Raises:
            StreamPersistenceError: If resumption fails.
            StreamingNotSupportedError: If the action does not support streaming.
            PluginActionNotFoundError: If the action is not found.
        """
        # Default implementation raises an error
        # Plugins should override this to provide actual resumption
        raise StreamPersistenceError(f"Stream resumption is not supported by plugin '{self.plugin_id}'")
        if False: # pragma: no cover
            yield None

    def shutdown(self) -> None:
        """
        Called by the PluginManager when the plugin is being unloaded or the agent is shutting down.
        Plugins should perform any necessary cleanup here (e.g., releasing resources, saving state).
        This method is optional for plugins to implement if no specific shutdown logic is needed.
        """
        pass

    def save_state(self, state_data: dict) -> None:
        """
        Requests the PluginManager to save the current state of the plugin.

        The plugin provides its state as a dictionary, which should be JSON-serializable.
        The PluginManager will handle the actual storage.

        Args:
            state_data (dict): A dictionary representing the plugin's state to be saved.

        Raises:
            PluginError: If the agent_context or state manager is not available.
            PluginActionExecutionError: If saving the state fails for reasons like I/O errors
                                        or serialization problems (raised by the state manager).
        """
        if not self.agent_context or "plugin_state_manager" not in self.agent_context:
            raise PluginError("Plugin state manager is not available in agent_context. Cannot save state.")
        try:
            self.agent_context["plugin_state_manager"].save_plugin_state(self.plugin_id, self.version, state_data)
        except Exception as e:
            raise PluginActionExecutionError(f"Failed to save state for plugin {self.plugin_id}: {e}", original_exception=e)

    def load_state(self) -> dict | None:
        """
        Requests the PluginManager to load the previously saved state for the plugin.

        Returns:
            dict | None: The loaded state as a dictionary, or None if no state was found
                         or if an error occurred during loading.

        Raises:
            PluginError: If the agent_context or state manager is not available.
            PluginActionExecutionError: If loading the state fails for reasons like I/O errors
                                        or deserialization problems (raised by the state manager).
        """
        if not self.agent_context or "plugin_state_manager" not in self.agent_context:
            raise PluginError("Plugin state manager is not available in agent_context. Cannot load state.")
        try:
            return self.agent_context["plugin_state_manager"].load_plugin_state(self.plugin_id, self.version)
        except Exception as e:
            raise PluginActionExecutionError(f"Failed to load state for plugin {self.plugin_id}: {e}", original_exception=e)
