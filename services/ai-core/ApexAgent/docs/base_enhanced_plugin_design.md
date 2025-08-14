# BaseEnhancedPlugin - Design Plan

**Objective**: Design and implement `BaseEnhancedPlugin.py`, a new base class for ApexAgent plugins. This class will incorporate robust error handling, define patterns for argument validation, and serve as a foundation for future enhancements like asynchronous execution, progress reporting, stream-based output, and state persistence. This corresponds to Step 1.2.1 of the Core Plugin Architecture Refinement.

**Key Design Points & Features for `BaseEnhancedPlugin` (Step 1.2.1 Focus)**:

1.  **Core Structure**:
    *   The class will be named `BaseEnhancedPlugin`.
    *   It will reside in `src/base_enhanced_plugin.py` (or a similar appropriate location like `src/core/base_enhanced_plugin.py` if a `core` module is established).
    *   It should be an abstract base class (using `abc.ABC` and `abc.abstractmethod`) if it defines methods that all concrete plugins *must* implement (e.g., a method to return plugin metadata or a primary execution method if standardized).
    *   It will likely take plugin-specific configuration or context during initialization (e.g., `__init__(self, config=None, plugin_id=None, plugin_version=None)`).
    *   It should provide access to a logger instance for consistent logging within plugins.

2.  **Robust Error Handling Framework**:
    *   **Custom Plugin Exceptions**: Define a hierarchy of custom exceptions specific to plugin operations. This allows for more granular error catching and reporting by the `PluginManager` and the agent core.
        *   `PluginError(Exception)`: Base exception for all plugin-related errors.
        *   `PluginInitializationError(PluginError)`: For errors during plugin setup.
        *   `PluginExecutionError(PluginError)`: For errors during an action's execution.
        *   `PluginConfigurationError(PluginError)`: For errors related to invalid or missing plugin configuration.
        *   `PluginArgumentError(PluginExecutionError, ValueError)`: For invalid arguments passed to a plugin action.
        *   `PluginDependencyError(PluginError)`: For issues with plugin dependencies (though primarily checked by `PluginManager`).
        *   `PluginStateError(PluginError)`: For errors related to plugin state persistence (relevant for Step 1.2.4).
    *   These exceptions should be defined within the same file or a dedicated `src/core/exceptions.py` module and imported.
    *   **Guidance for Plugins**: The base class or its documentation should guide plugin developers to raise these specific exceptions appropriately.

3.  **Argument Validation Patterns**:
    *   While full validation logic for every action resides within the concrete plugin, `BaseEnhancedPlugin` can provide utility methods or promote patterns.
    *   **Option 1 (Decorators - more advanced)**: Could explore decorators for common validation tasks (e.g., `@require_type(param_name, expected_type)`), but this might be overly complex for an initial base class.
    *   **Option 2 (Helper Methods - simpler)**: Provide helper methods like `self._validate_argument(value, expected_type, choices=None, required=True, arg_name="")` that plugins can call at the beginning of their actions. These helpers would raise `PluginArgumentError`.
    *   **Option 3 (Documentation and Convention)**: Primarily rely on clear documentation and conventions, encouraging plugins to perform validation and raise `PluginArgumentError` themselves. This is the most straightforward initial approach.
    *   **Decision for Step 1.2.1**: Start with Option 3 (Documentation and Convention) for raising `PluginArgumentError`. Helper methods can be added later if a strong need arises.
    *   The metadata for each action (from `plugin.json`) already defines parameter types and whether they are required. The `PluginManager` or a wrapper layer could potentially perform initial validation based on this metadata *before* calling the plugin action, reducing boilerplate in the plugin itself. This is a consideration for `PluginManager` evolution.

4.  **Action Definition and Execution**:
    *   Plugins will define their actions as methods.
    *   The `PluginManager` will discover these actions based on the `actions` list in the plugin metadata.
    *   The `BaseEnhancedPlugin` itself might not need to be overly prescriptive about how actions are named or structured beyond being methods, as the metadata drives discovery.
    *   However, it could provide a standard way to invoke an action if the `PluginManager` calls a generic `execute_action(self, action_name, **kwargs)` method on the plugin instance, which then dispatches to the actual method. This allows the base class to wrap action execution with common logic (e.g., error handling, logging) if needed.

5.  **Logging Integration**:
    *   `BaseEnhancedPlugin` should initialize a logger instance (e.g., `self.logger = logging.getLogger(f"plugin.{self.plugin_id or 'unknown_plugin'}")`) that plugins can use for consistent logging.
    *   This logger can be pre-configured to include plugin ID in log messages.

6.  **Future Extensibility Hooks (Placeholders/Considerations for Steps 1.2.2 - 1.2.4)**:
    *   **Asynchronous Execution (Step 1.2.2)**: Design methods to be `async def` if asynchronous operations are anticipated as a common case. The base class might define an `async execute_action(...)`.
    *   **Progress Reporting (Step 1.2.2)**: Consider a `_report_progress(self, current_step, total_steps, message)` method that plugins can call. The base class could then emit this progress via a callback or event system provided by the `PluginManager`.
    *   **Stream-Based Output (Step 1.2.3)**: Actions might need to be `async def` and use `yield` to stream results. The base class structure should not hinder this.
    *   **State Persistence (Step 1.2.4)**: Define abstract methods like `async save_state(self, data_key, data_value)` and `async load_state(self, data_key)` that the `PluginManager` would implement or facilitate.

**Deliverables for Step 1.2.1**:

*   **`BaseEnhancedPlugin.py`**: The Python file containing the `BaseEnhancedPlugin` class and associated custom plugin exceptions.
*   **Documentation**: Comments within the code and potentially a separate Markdown document explaining how to use `BaseEnhancedPlugin`, its error handling features, and conventions for plugin developers.
*   **Unit Tests**: Basic unit tests for the `BaseEnhancedPlugin` itself (e.g., initialization, logger availability, and if any helper methods are added).

**Implementation Steps for 1.2.1**:

1.  **Create `src/core/exceptions.py` (or similar)**: Define the custom plugin exception hierarchy.
2.  **Create `src/core/base_enhanced_plugin.py`**: Implement the `BaseEnhancedPlugin` class.
    *   Include `__init__` with config, plugin_id, plugin_version parameters.
    *   Set up the logger.
    *   Define any abstract methods if necessary (though initially, it might be a concrete class that plugins inherit from, with conventions for action methods).
3.  **Write Documentation**: Document the base class, exceptions, and usage patterns for plugin developers.
4.  **Write Unit Tests**: Test the instantiation and basic properties of `BaseEnhancedPlugin`.
5.  **Refactor an Existing Simple Plugin (Optional but Recommended)**: If a very simple plugin exists (or create a dummy one), refactor it to inherit from `BaseEnhancedPlugin` to test the integration and ergonomics.

**Self-Correction/Refinement during Design**:
*   Initially considered making `BaseEnhancedPlugin` responsible for parsing its own metadata. Corrected: Metadata parsing and validation are responsibilities of the `PluginManager`. The `PluginManager` can pass relevant metadata (like plugin ID, version) to the plugin instance during initialization.
*   Debated whether action methods should be explicitly declared as abstract. Decided against it for now to maintain flexibility; actions are methods whose names match the metadata. A generic `execute_action` wrapper in the base class could be a good compromise for centralized pre/post processing of action calls.

This design focuses on establishing a solid, error-aware foundation for plugins. Subsequent steps (1.2.2-1.2.4) will build upon this base to add more advanced capabilities.
