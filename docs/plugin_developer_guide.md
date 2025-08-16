# ApexAgent Plugin Developer Guide

This guide provides instructions and best practices for developing plugins for the ApexAgent system. Plugins extend the agent's capabilities by providing new actions and functionalities.

## 1. Overview

Plugins in ApexAgent are discovered, loaded, and managed by the `PluginManager`. Each plugin must conform to a defined structure and interface to be compatible with the system.

## 2. Plugin Structure

Each plugin must reside in its own dedicated subdirectory within a designated plugins directory (e.g., `/home/ubuntu/agent_project/src/plugins/`). The structure for a single plugin should be as follows:

```
my_awesome_plugin/
|-- plugin.json            # Metadata file (Required)
|-- my_plugin_module.py    # Main plugin code containing the plugin class (Required)
|-- __init__.py            # Optional, if your plugin is a package
|-- other_modules/         # Optional, for additional plugin-specific code
|   |-- __init__.py
|   |-- utility.py
|-- bundled_dependencies/  # Optional, for any non-standard, bundled dependencies
|-- assets/                # Optional, for any assets like icons, templates
```

*   **`plugin.json`**: This mandatory file contains metadata about your plugin, such as its ID, name, version, entry point, and the actions it provides. It must conform to the `plugin_metadata_schema.json`.
*   **Main Plugin Module/Package**: This is where your main plugin class, inheriting from `BasePlugin`, will reside. The path to this class is specified in the `entry_point` field of `plugin.json` (e.g., `my_plugin_module.MyPluginClass`).

## 3. Plugin Metadata (`plugin.json`)

Refer to the `plugin_metadata_schema.json` and `plugin_metadata_schema_docs.md` for a detailed description of all available metadata fields. Key fields include:

*   `id`: A unique machine-readable string identifier for your plugin (e.g., "my_awesome_plugin_id").
*   `name`: A human-readable name (e.g., "My Awesome Plugin").
*   `version`: Semantic version (e.g., "1.0.2"). This is crucial for version management and dependency resolution. It MUST follow Semantic Versioning 2.0.0 (SemVer).
*   `description`: A brief description of what your plugin does.
*   `author`: Your name or organization.
*   `entry_point`: The fully qualified path to your main plugin class (e.g., `my_plugin_module.MyPluginClass` if your class `MyPluginClass` is in `my_plugin_module.py` at the root of your plugin directory).
*   `actions`: An array describing the actions your plugin provides.
*   `dependencies`: (Object, Optional) Specifies dependencies on other ApexAgent plugins and external Python libraries.
*   `default_enabled`: (Boolean, Optional, Default: `true`) Hint for initial activation state.
*   `checksum`: (Object, Optional) For integrity verification of your plugin directory.

## 4. Implementing the Plugin Class (`BasePlugin`)

Your main plugin class must inherit from `BasePlugin` (located in `agent_project.src.core.base_plugin`).

```python
# In your plugin\'s main module (e.g., my_plugin_module.py)
from agent_project.src.core.base_plugin import BasePlugin
# Import custom exceptions for specific error reporting
from agent_project.src.core.plugin_exceptions import (
    PluginInitializationError,
    PluginConfigurationError,
    PluginActionNotFoundError,
    PluginInvalidActionParametersError,
    PluginActionExecutionError,
    PluginDependencyError,
    PluginResourceNotFoundError
)

class MyPluginClass(BasePlugin):
    def __init__(self, plugin_id: str, plugin_name: str, version: str, description: str, config: dict = None):
        super().__init__(plugin_id, plugin_name, version, description, config)
        # Your plugin-specific constructor logic here
        self.my_internal_state = None
        if self.config.get("api_key") is None:
            raise PluginConfigurationError("Missing required configuration: api_key")

    def initialize(self, agent_context: dict = None) -> None:
        super().initialize(agent_context)
        print(f"Plugin {self.plugin_id} ({self.name} v{self.version}) is initializing.")
        try:
            self.my_internal_state = "initialized"
        except FileNotFoundError as e:
            raise PluginResourceNotFoundError(f"Failed to load critical resource: {e}", original_exception=e)
        except Exception as e:
            raise PluginInitializationError(f"Unexpected error during initialization: {e}", original_exception=e)

    def get_actions(self) -> list[dict]:
        return [
            {
                "name": "my_action_one",
                "description": "Does something awesome.",
                "parameters_schema": { 
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "description": "First parameter"},
                        "count": {"type": "integer", "minimum": 1}
                    },
                    "required": ["param1", "count"]
                },
                "returns_schema": { 
                    "type": "object",
                    "properties": {
                        "result": {"type": "string"}
                    }
                }
            }
        ]

    # Example of a synchronous action
    # def execute_action(self, action_name: str, params: dict = None, progress_callback: Optional[Callable[[dict], None]] = None) -> any:
    # Example of an asynchronous action (see Section 8 for details)
    async def execute_action(self, action_name: str, params: dict = None, progress_callback: Optional[Callable[[dict], None]] = None) -> any:
        params = params or {}
        print(f"Plugin {self.plugin_id} executing action: {action_name} with params: {params}")

        if action_name == "my_action_one":
            if "param1" not in params or not isinstance(params["param1"], str):
                raise PluginInvalidActionParametersError("Parameter \\'param1\\' must be a string and is required.")
            if "count" not in params or not isinstance(params["count"], int) or params["count"] < 1:
                raise PluginInvalidActionParametersError("Parameter \\'count\\' must be an integer greater than 0 and is required.")
            
            try:
                # For async, you might await something here
                # await asyncio.sleep(1) 
                result_data = f"Action \\'my_action_one\\' executed with param1: {params["param1"]}, count: {params["count"]}. State: {self.my_internal_state}"
                if progress_callback:
                    progress_callback({"percentage": 100.0, "message": "Action completed"})
                return {"result": result_data}
            except Exception as e:
                raise PluginActionExecutionError(f"Error executing my_action_one: {e}", original_exception=e)
        else:
            raise PluginActionNotFoundError(f"Action \'{action_name}\' is not implemented by {self.plugin_id}.")

    def shutdown(self) -> None:
        print(f"Plugin {self.plugin_id} is shutting down.")
        self.my_internal_state = "shutdown"

```

**Key Methods to Implement/Override:**

*   **`__init__(self, plugin_id, plugin_name, version, description, config=None)`**: Your constructor. Always call `super().__init__(...)`. The `version` parameter is the string version from your `plugin.json`.
*   **`initialize(self, agent_context=None)`**: For setup logic. Raise `PluginInitializationError`, `PluginConfigurationError`, `PluginDependencyError`, or `PluginResourceNotFoundError` for critical setup failures.
*   **`get_actions(self)`**: Must return a list of dictionaries describing actions.
*   **`execute_action(self, action_name, params=None, progress_callback=None)`**: Core logic for actions. Can be synchronous or asynchronous (`async def`). Raise `PluginActionNotFoundError`, `PluginInvalidActionParametersError`, or `PluginActionExecutionError` as appropriate. See Section 8 for details on async and progress reporting.
*   **`shutdown(self)`**: Optional. For cleanup.

**Accessing Version Information**: Inside your plugin instance, you can access the plugin\'s version via `self.version` (string) or `self.parsed_version` (a `packaging.version.Version` object).

## 5. Plugin Loading and Execution Flow

1.  **Discovery**: `PluginManager` scans for `plugin.json` files.
2.  **Validation**: Metadata is validated. Checksums/signatures verified.
3.  **Registration**: Valid plugins (including all their discovered versions) are registered. The `PluginManager` stores each version of a plugin separately, keyed by its `id` and parsed version object.
4.  **Loading (`load_plugin(plugin_id, version_specifier=None)`)**: 
    *   If a `version_specifier` (e.g., "==1.0.2", ">=1.1") is provided, `PluginManager` attempts to find the latest available version of the plugin that satisfies the specifier.
    *   If no `version_specifier` is given, the latest available version of the plugin is selected.
    *   If no matching version is found, loading fails.
    *   The module is imported, class instantiated, `initialize()` called, and instance cached (keyed by ID and specific version).
5.  **Action Execution (`execute_plugin_action(plugin_id, action_name, params=None, version_specifier=None, progress_callback=None)`)**:
    *   `PluginManager` loads the appropriate plugin version based on `plugin_id` and `version_specifier`.
    *   It inspects the plugin\'s `execute_action` method. If it\'s an `async def` method, it will be `await`ed. Otherwise, it\'s called synchronously.
    *   The `progress_callback` is passed to the plugin\'s `execute_action` method.
6.  **Unloading (`unload_plugin(plugin_id, version=None)`)**: 
    *   If a specific `version` string is provided, that version instance is targeted for shutdown and removal.
    *   If no `version` is provided, the latest loaded version of that `plugin_id` is targeted.
    *   `shutdown()` is called, instance removed from cache.

## 6. Versioning and Dependency Management

### 6.1. Plugin Versioning

Always use Semantic Versioning 2.0.0 for the `version` field in your `plugin.json`. This allows `PluginManager` and other plugins to reason about compatibility:

- **MAJOR** version increments for incompatible API changes
- **MINOR** version increments for backward-compatible functionality additions
- **PATCH** version increments for backward-compatible bug fixes

### 6.2. Dependency Declaration

The `dependencies` object in your `plugin.json` allows you to specify both plugin and library dependencies with version constraints:

```json
{
  "id": "my_awesome_plugin",
  "name": "My Awesome Plugin",
  "version": "1.2.0",
  "description": "A plugin that does amazing things",
  "author": "Your Name",
  "main_file": "plugin_main.py",
  "main_class": "Plugin",
  "dependencies": {
    "plugins": {
      "core_plugin": ">=1.0.0,<2.0.0",
      "utility_plugin": "^1.2.3"
    },
    "libraries": {
      "requests": ">=2.25.0",
      "numpy": "~=1.20.0"
    },
    "optional": {
      "plugins": {
        "optional_plugin": ">=1.0.0"
      },
      "libraries": {
        "pandas": ">=1.3.0"
      }
    }
  }
}
```

#### Plugin Dependencies

The `plugins` object specifies required ApexAgent plugins. Each key is a plugin ID, and each value is a version constraint string following the Python packaging specification format:

- `==1.0.0`: Exactly version 1.0.0
- `>=1.0.0`: Version 1.0.0 or higher
- `>=1.0.0,<2.0.0`: Version 1.0.0 or higher, but less than 2.0.0
- `~=1.2.3`: Version 1.2.3 or higher, but less than 1.3.0 (compatible release)
- `^1.2.3`: Version 1.2.3 or higher, but less than 2.0.0 (compatible release)

#### Library Dependencies

The `libraries` object specifies required Python libraries. Each key is a library name (as it would be imported), and each value is a version constraint string:

- `==1.0.0`: Exactly version 1.0.0
- `>=1.0.0`: Version 1.0.0 or higher
- `~=1.2.3`: Version 1.2.3 or higher, but less than 1.3.0 (compatible release)

#### Optional Dependencies

The `optional` object specifies dependencies that enhance functionality but aren't required for basic operation. These are structured the same way as required dependencies, with separate `plugins` and `libraries` objects.

### 6.3. Dependency Resolution Process

When a plugin is loaded, the `PluginManager` performs the following steps:

1. **Extract Dependencies**: Reads the `dependencies` object from the plugin's metadata
2. **Check Plugin Dependencies**: For each required plugin:
   - Verifies the plugin is available in the registry
   - Checks if any available version satisfies the version constraint
   - If not found or no compatible version exists, reports a dependency error
3. **Check Library Dependencies**: For each required library:
   - Attempts to import the library
   - If successful, checks if the installed version satisfies the constraint
   - If import fails or version is incompatible, reports a dependency error
4. **Optional Dependencies**: Checks optional dependencies but doesn't fail if they're missing
5. **Load or Fail**: If all required dependencies are satisfied, loads the plugin; otherwise, raises a specific dependency error

### 6.4. Dependency Error Types

The system provides specific error types for different dependency issues:

- **`PluginMissingDependencyError`**: Raised when a required dependency (plugin or library) is not found
- **`PluginIncompatibleDependencyError`**: Raised when a dependency is found but its version is incompatible
- **`PluginInvalidDependencySpecificationError`**: Raised when a dependency specification is invalid (e.g., malformed version constraint)
- **`PluginCircularDependencyError`**: Raised when a circular dependency chain is detected

### 6.5. Bypassing Dependency Checks

In some cases, you may want to load a plugin even if its dependencies aren't satisfied. The `PluginManager.load_plugin()` method accepts a `check_dependencies` parameter (default: `True`):

```python
# Load plugin without checking dependencies
plugin = plugin_manager.load_plugin("my_plugin", check_dependencies=False)
```

This is useful for testing or when you know the dependencies aren't needed for your specific use case.

## 7. Error Handling and Validation

A robust plugin system relies on clear and specific error reporting. ApexAgent provides a hierarchy of custom plugin exceptions to help developers signal issues accurately. These exceptions are defined in `agent_project.src.core.plugin_exceptions`.

### 7.1. Custom Plugin Exceptions

It is highly recommended to use these specific exceptions when appropriate, as `PluginManager` may use them for more detailed logging or differentiated error handling.

*   **`PluginError(Exception)`**: The base class for all plugin-related errors. You can catch this to handle any plugin-specific issue.
*   **`PluginInitializationError(PluginError)`**: Raise this during your plugin\'s `__init__` or `initialize` methods if a non-recoverable error occurs that prevents the plugin from becoming operational (e.g., failure to load essential resources, critical setup failure).
*   **`PluginConfigurationError(PluginError)`**: Raise this if the plugin\'s configuration (passed via `self.config`) is invalid, missing critical keys, or has values that prevent the plugin from operating correctly. This can be raised in `__init__` or `initialize`.
*   **`PluginActionError(PluginError)`**: Base class for errors specifically related to the execution of plugin actions.
    *   **`PluginActionNotFoundError(PluginActionError, AttributeError)`**: Raise this in `execute_action` if the provided `action_name` is not recognized or implemented by your plugin.
    *   **`PluginInvalidActionParametersError(PluginActionError, ValueError)`**: This is crucial for argument validation. Raise this in `execute_action` if the `params` dictionary is missing required parameters, contains parameters of the wrong type, or has values that are out of allowed ranges/formats.
    *   **`PluginActionExecutionError(PluginActionError)`**: Raise this for general, unexpected errors that occur *during* the internal logic of an action\'s execution, *after* parameters have been successfully validated. It\'s good practice to wrap unexpected internal exceptions (e.g., network errors, library-specific errors) in this custom exception to provide context.
*   **`PluginDependencyError(PluginError)`**: Base class for dependency-related errors.
    *   **`PluginMissingDependencyError(PluginDependencyError)`**: Raised when a required dependency is not found.
    *   **`PluginIncompatibleDependencyError(PluginDependencyError)`**: Raised when a dependency is found but its version is incompatible.
    *   **`PluginInvalidDependencySpecificationError(PluginDependencyError)`**: Raised when a dependency specification is invalid.
    *   **`PluginCircularDependencyError(PluginDependencyError)`**: Raised when a circular dependency chain is detected.
*   **`PluginResourceNotFoundError(PluginError, FileNotFoundError)`**: Raise this when your plugin cannot find an essential internal resource it needs to operate (e.g., a template file, a data file it expects to be bundled with it).

**Chaining Exceptions**: When wrapping an original exception, pass it to the `original_exception` parameter of the custom plugin exception for better debugging: 
`raise PluginActionExecutionError("Failed to call external API", original_exception=e)`

### 7.2. Argument Validation Best Practices

Robust argument validation within your `execute_action` method is critical for plugin stability and security.

1.  **Always Validate**: Do not assume parameters will be correct. Explicitly check for presence, type, and constraints.
2.  **Fail Fast**: Perform validation at the beginning of your `execute_action` method before performing significant work.
3.  **Use `PluginInvalidActionParametersError`**: When validation fails, raise `PluginInvalidActionParametersError` with a clear, descriptive message indicating which parameter failed validation and why.
4.  **Leverage Schemas (Optional but Recommended)**: While `BasePlugin` doesn\'t enforce it, consider using a library like Pydantic within your plugin to define data models for your action parameters. This can simplify validation logic significantly.

## 8. Asynchronous Actions and Progress Reporting

To handle long-running tasks without blocking the main agent thread and to provide feedback on their progress, plugins can implement asynchronous actions and utilize a progress reporting mechanism.

### 8.1. Asynchronous `execute_action`

If your plugin action involves I/O-bound operations (e.g., network requests, file operations) or any task that might take a significant amount of time, you should define your `execute_action` method as an `async def` coroutine.

```python
import asyncio
from typing import Callable, Optional, Any

# ... (other imports and BasePlugin definition)

class MyAsyncPlugin(BasePlugin):
    # ... (other methods: __init__, initialize, get_actions)

    async def execute_action(self, action_name: str, params: dict = None, 
                            progress_callback: Optional[Callable[[dict], None]] = None,
                            cancellation_token: Optional[CancellationToken] = None) -> Any:
        params = params or {}
        
        if action_name == "fetch_data":
            # Validate parameters
            if "url" not in params:
                raise PluginInvalidActionParametersError("Missing required parameter: url")
            
            # Report initial progress
            if progress_callback:
                progress_callback({"percentage": 0, "message": "Starting data fetch"})
            
            try:
                # Simulate a network request
                await asyncio.sleep(2)  # In a real plugin, this would be an actual async HTTP request
                
                # Check for cancellation
                if cancellation_token and cancellation_token.is_cancelled:
                    return {"status": "cancelled"}
                
                # Report progress
                if progress_callback:
                    progress_callback({"percentage": 50, "message": "Data received, processing"})
                
                # More async work
                await asyncio.sleep(1)
                
                # Final progress report
                if progress_callback:
                    progress_callback({"percentage": 100, "message": "Fetch complete"})
                
                return {"status": "success", "data": f"Data from {params['url']}"}
            except Exception as e:
                raise PluginActionExecutionError(f"Error fetching data: {e}")
        else:
            raise PluginActionNotFoundError(f"Action '{action_name}' not found")
```

The `PluginManager` will automatically detect if your `execute_action` method is a coroutine and will handle it appropriately.

### 8.2. Progress Reporting

For long-running actions, it's important to provide feedback on their progress. The `progress_callback` parameter allows your plugin to report progress updates.

```python
# Example progress update
progress_data = {
    "percentage": 75,  # 0-100 indicating completion percentage
    "message": "Processing data...",  # Human-readable status message
    "status": "running",  # Optional status indicator (e.g., "running", "paused", "error")
    "details": {  # Optional detailed information
        "items_processed": 150,
        "total_items": 200,
        "current_stage": "validation"
    }
}

# Call the progress callback
if progress_callback:
    progress_callback(progress_data)
```

### 8.3. Cancellation Support

The `cancellation_token` parameter allows your plugin to check if the operation should be cancelled.

```python
# Check for cancellation periodically in long-running operations
if cancellation_token and cancellation_token.is_cancelled:
    # Clean up resources
    return {"status": "cancelled"}
```

## 9. State Persistence

Plugins can save and load state data to maintain information between sessions. This is useful for caching, storing user preferences, or maintaining any other persistent data.

### 9.1. Saving State

To save state, use the `save_state` method:

```python
def save_state(self, state_data: dict):
    """
    Save plugin state data.
    
    Args:
        state_data (dict): The state data to save
    """
    # This method is implemented in BasePlugin and handles the actual storage
    # You just need to provide a dictionary of data to save
    super().save_state(state_data)
```

### 9.2. Loading State

To load previously saved state, use the `load_state` method:

```python
def load_state(self) -> dict:
    """
    Load plugin state data.
    
    Returns:
        dict: The loaded state data, or None if no state exists
    """
    # This method is implemented in BasePlugin and handles the actual retrieval
    return super().load_state()
```

### 9.3. Using State in Your Plugin

Here's an example of how to use state persistence in a plugin:

```python
def initialize(self, agent_context=None):
    super().initialize(agent_context)
    
    # Load saved state or initialize default state
    saved_state = self.load_state()
    if saved_state:
        self.counter = saved_state.get("counter", 0)
        self.cache = saved_state.get("cache", {})
    else:
        self.counter = 0
        self.cache = {}

def execute_action(self, action_name, params=None, progress_callback=None):
    if action_name == "increment_counter":
        self.counter += 1
        
        # Save the updated state
        self.save_state({
            "counter": self.counter,
            "cache": self.cache
        })
        
        return {"counter": self.counter}
    # ... other actions
```

## 10. Best Practices

### 10.1. Plugin Design

1. **Single Responsibility**: Each plugin should have a clear, focused purpose.
2. **Minimal Dependencies**: Minimize dependencies on other plugins to reduce coupling.
3. **Graceful Degradation**: When optional dependencies are missing, provide reduced functionality rather than failing completely.
4. **Comprehensive Documentation**: Document your plugin's purpose, actions, parameters, and dependencies.

### 10.2. Version Management

1. **Follow SemVer**: Strictly adhere to Semantic Versioning 2.0.0 principles.
2. **Changelog**: Maintain a changelog documenting changes between versions.
3. **Version Compatibility**: Clearly document compatibility with other plugins and the core system.

### 10.3. Error Handling

1. **Specific Exceptions**: Use the most specific exception type for each error condition.
2. **Informative Messages**: Provide clear, actionable error messages.
3. **Graceful Recovery**: Attempt to recover from non-critical errors when possible.
4. **Log Appropriately**: Use logging to record errors and important events.

### 10.4. Performance

1. **Async for I/O**: Use async methods for I/O-bound operations.
2. **Progress Reporting**: Provide regular progress updates for long-running operations.
3. **Resource Management**: Clean up resources in the `shutdown` method.
4. **Cancellation Support**: Check the cancellation token regularly in long-running operations.

## 11. Troubleshooting

### 11.1. Common Issues

1. **Plugin Not Discovered**: Ensure your `plugin.json` is valid and in the correct location.
2. **Dependency Errors**: Check that all required plugins and libraries are available and have compatible versions.
3. **Import Errors**: Verify that your plugin's module structure matches what's declared in `plugin.json`.
4. **Version Conflicts**: Use specific version constraints to avoid conflicts with other plugins.

### 11.2. Debugging Tips

1. **Enable Debug Logging**: Set the logging level to DEBUG to see detailed information.
2. **Inspect Plugin Registry**: Use `PluginManager.get_plugin_ids()` and `PluginManager.get_plugin_metadata()` to inspect the discovered plugins.
3. **Check Dependencies**: Use `PluginManager.check_plugin_dependencies()` to verify dependency resolution.
4. **Test in Isolation**: Test your plugin in isolation before integrating it with other plugins.
