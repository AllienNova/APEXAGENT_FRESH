# Plugin Registry and Discovery System - Detailed Implementation Plan

This document outlines the detailed implementation steps for creating the Plugin Registry and Discovery System for ApexAgent, corresponding to Section 1.1 of the comprehensive implementation plan. This plan incorporates feedback regarding security, lifecycle management, performance, testing, and update strategies.

## 1. Step 1.1.1: Design Detailed Plugin Metadata Schema

**Objective**: Define a comprehensive and flexible metadata schema for plugins that will facilitate discovery, versioning, dependency management, security, lifecycle hints, and user understanding.

**Deliverables**:
*   A JSON schema file (`plugin_metadata_schema.json`) defining the structure.
*   Documentation (`plugin_metadata_schema_docs.md`) explaining each field in the schema and its purpose.

**Detailed Steps**:

1.  **Identify Core and Enhanced Metadata Fields**:
    *   `name`: (String, Required) Unique, human-readable name.
    *   `id`: (String, Required, Unique) Machine-readable unique identifier.
    *   `version`: (String, Required) Semantic versioning (e.g., "1.2.3").
    *   `description`: (String, Required) Brief description.
    *   `author`: (String, Required) Name or organization.
    *   `entry_point`: (String, Required) Fully qualified name of the main plugin class.
    *   `actions`: (Array of Objects, Required) List of actions the plugin provides (with name, description, parameters, returns).
    *   `dependencies`: (Object, Optional) Specifies dependencies on other ApexAgent plugins and external Python libraries.
        *   `plugins`: (Array of Objects, Optional) List of ApexAgent plugin dependencies (id, version_specifier, description). The `version_specifier` should follow PEP 440 (e.g., "==1.2.3", ">=1.2,<2.0", "~=1.2.3").
        *   `python_libraries`: (Array of Objects, Optional) List of external Python library dependencies (name, version_specifier, import_check_module, description).
    *   `tags`: (Array of Strings, Optional) Keywords for categorization.
    *   `icon`: (String, Optional) Path or URL to an icon.
    *   `homepage`: (String, Optional) URL to homepage/documentation.
    *   `license`: (String, Optional) SPDX license identifier.
    *   `permissions_required`: (Array of Strings, Optional) System permissions needed.
    *   `configuration_schema`: (Object, Optional) JSON schema for plugin-specific configuration.
    *   **`checksum`**: (Object, Optional) Checksum for integrity verification (algorithm, value).
    *   **`signature`**: (Object, Optional) Digital signature for authenticity (method, key_id, value).
    *   **`default_enabled`**: (Boolean, Optional, Default: `true`) Hint for initial activation state.

2.  **Draft JSON Schema (`plugin_metadata_schema.json`)**:
    *   Create/Update the JSON schema file incorporating all identified fields with appropriate types, descriptions, and validation rules. This step has been completed, incorporating the enhanced `dependencies`, `checksum`, `signature`, and `default_enabled` structures.

3.  **Write/Update Documentation for the Schema (`plugin_metadata_schema_docs.md`)**:
    *   Create/Update a Markdown file detailing each field, its purpose, data type, constraints, and examples. This step has been completed, with new fields and structures documented.

4.  **Review and Iterate on Schema and Documentation**:
    *   Ensure clarity, completeness, correctness, and consideration for edge cases and future extensibility. This review has been performed.

## 2. Step 1.1.2: Implement Auto-Discovery and Enhanced `PluginManager` Capabilities

**Objective**: Enhance `PluginManager` to automatically discover plugins, validate their integrity and authenticity, manage their initial lifecycle state, and optimize discovery performance.

**Deliverables**:
*   Updated `PluginManager.py` with auto-discovery, security validation, initial lifecycle handling, and performance considerations.
*   Unit and Integration tests for the discovery and validation mechanisms.
*   Robust error reporting.

**Detailed Steps**:

1.  **Define Plugin Directory Structure**:
    *   **Standard Structure**: Plugins will be organized within a main `plugins` directory located at `/home/ubuntu/agent_project/src/plugins/`. 
    *   **Individual Plugin Directories**: Each plugin must reside in its own dedicated subdirectory within this main `plugins` directory. The name of this subdirectory should ideally be descriptive and match or relate to the plugin's `id` or `name` (e.g., `/home/ubuntu/agent_project/src/plugins/knowledge_graph_plugin/`).
    *   **Metadata File**: Each individual plugin directory must contain a metadata file named `plugin.json`. This file must conform to the `plugin_metadata_schema.json` defined in Step 1.1.1.
    *   **Plugin Code**: The plugin's source code and any other necessary resources (e.g., assets, templates) should be contained within its dedicated subdirectory.
    *   **Rationale**: This structure promotes modularity, simplifies discovery (as the `PluginManager` can scan a known root directory), prevents naming conflicts between plugin resources, and aligns with common practices for plugin-based architectures, supporting long-term maintainability.

2.  **Implement Core Auto-Discovery Logic**:
    *   Modify `PluginManager` to scan specified directories for metadata files.
    *   Parse and validate metadata against `plugin_metadata_schema.json` using a library like `jsonschema`.
    *   Register valid plugins in an internal registry (keyed by `plugin_id`), storing metadata and path.

3.  **Implement Security Validation during Discovery**:
    *   If `checksum` object is present in metadata, calculate checksum of the plugin's package/directory using the specified `algorithm` and compare with `value`. Log error/warning or prevent loading on mismatch, based on security policy.
    *   If `signature` object is present, implement verification logic using the specified `method` and `key_id` (if applicable) against the `value`. Log error/warning or prevent loading on failed verification.
    *   Define clear policies for handling plugins that fail these checks.

4.  **Implement Initial Lifecycle State Management**:
    *   Use the `default_enabled` field from metadata to set the initial state of a plugin upon discovery. Discovered plugins might be registered but not immediately activated if `default_enabled` is `false`.
    *   Provide a mechanism within `PluginManager` to query the intended initial enabled state of a plugin.

5.  **Address Performance Optimization for Discovery (Planning Phase)**:
    *   **Caching Strategy (Plan)**:
        *   **Objective**: Reduce redundant parsing and validation of `plugin.json` files on subsequent agent starts.
        *   **Mechanism**: After successful discovery, validation, and security checks, the `PluginManager` could serialize key plugin metadata (ID, version, path, entry point, validated status, checksum, initial enabled state) to a cache file (e.g., `plugin_cache.json` or a lightweight database like SQLite).
        *   **Cache Key**: The primary key could be the plugin directory path or a combination of path and plugin ID.
        *   **Invalidation**: 
            *   On startup, for each cached entry, compare the modification timestamp of the `plugin.json` file and its containing directory against stored timestamps in the cache. 
            *   If timestamps differ, or if the plugin directory is no longer found, invalidate that cache entry and re-discover/re-validate the plugin from scratch.
            *   Consider invalidating the entire cache if the `plugin_metadata_schema.json` itself changes, as this might alter validation rules.
        *   **Benefits**: Significantly speeds up startup if many plugins are present and unchanged.
        *   **Considerations**: Cache file location, format, and potential for corruption.
    *   **Incremental Discovery Strategy (Plan)**:
        *   **Objective**: For very large plugin repositories or frequently changing environments, avoid re-scanning all known plugin directories if only a few have changed.
        *   **Mechanism**: 
            *   Maintain a persistent list of known plugin directories and their last scan status/timestamp.
            *   Use filesystem event monitoring (e.g., libraries like `watchdog` if feasible and appropriate for the agent's environment) to detect additions, removals, or modifications in the main plugin directories.
            *   Alternatively, on startup, quickly scan only for new subdirectories in the main plugin roots or check modification times of known plugin subdirectories against a stored manifest.
        *   **Integration with Caching**: Incremental discovery would work well with caching. If a new plugin is detected, it's processed fully. If a known plugin directory is modified, its cache entry is invalidated, and it's re-processed.
        *   **Benefits**: Reduces I/O and processing for large, mostly static plugin sets.
        *   **Considerations**: Complexity of filesystem event monitoring, reliability across different OS, and potential overhead of monitoring itself. A simpler timestamp-based check on plugin directories might be a more pragmatic first step.
    *   **Documentation**: These planned strategies should be documented as potential future enhancements to the `PluginManager` once the core functionality is stable.

6.  **Implement Robust Error Handling and Reporting**:
    *   Handle non-existent directories, unreadable files, invalid JSON, schema validation failures, duplicate plugin IDs, checksum mismatches, signature failures.
    *   Provide clear, actionable error messages and logging.

7.  **Update `PluginManager` Core Methods**:
    *   Ensure methods like `load_plugin`, `get_plugin_actions` use the information from the internal registry, considering the plugin's discovered state and version.
    *   `load_plugin` will use `entry_point` for dynamic import and instantiation, only if the plugin passes security checks and is (or can be) enabled.

## 3. Step 1.1.3: Implement Plugin Versioning Support

**Objective**: Enable `PluginManager` and plugins to support API versioning, allowing for backward compatibility and graceful evolution of plugin interfaces.

**Deliverables**:
*   Updated `PluginManager.py` to handle plugin versions effectively.
*   Documentation on plugin versioning for developers.
*   Unit and integration tests for versioning capabilities.

**Detailed Strategy and Design**:

1.  **Version Declaration and Storage**:
    *   **Plugin Metadata**: The `version` field in `plugin.json` (e.g., "1.2.3") is the canonical source for a plugin's version. It MUST adhere to Semantic Versioning 2.0.0 (SemVer).
    *   **`PluginManager` Storage**: During discovery, `PluginManager` will parse this version. If multiple versions of the same plugin (identical `id`) are found in different directories or through different discovery paths, all valid versions will be registered. The internal registry will store plugins keyed by their `id`, and then by their parsed `packaging.version.Version` object to allow for easy sorting and comparison.

2.  **Requesting Specific Plugin Versions**:
    *   **`load_plugin` Enhancement**: The `PluginManager.load_plugin(plugin_id: str, version_specifier: str = None)` method will be enhanced. The `version_specifier` parameter will accept a string representing a PEP 440 version specifier (e.g., "==1.2.3", ">=1.2.0,<2.0.0", "~=1.2.3").
    *   **Dependency Resolution**: The `dependencies.plugins.version_specifier` field in `plugin.json` will also use PEP 440 specifiers for requesting dependent plugins.

3.  **Version Selection and Resolution Strategy**:
    *   **No Specifier**: If `version_specifier` is `None` when calling `load_plugin`, the `PluginManager` will load the latest available (highest) version of the plugin that meets all other criteria (e.g., security checks, enabled state).
    *   **With Specifier**: If a `version_specifier` is provided, `PluginManager` will iterate through all registered versions of the plugin with the given `plugin_id`.
        *   It will use the `packaging.specifiers.SpecifierSet` class to parse the `version_specifier` string.
        *   It will use `packaging.version.Version` to parse each available plugin version.
        *   The `SpecifierSet.filter()` method will be used to find all available versions that satisfy the specifier.
        *   From the filtered list of satisfying versions, the latest (highest) version will be chosen.
    *   **Pre-release Versions**: By default, pre-release versions (e.g., "1.0.0-alpha.1", "2.0.0b3") will be considered for selection if they satisfy the specifier and no stable version does, or if the specifier explicitly includes pre-releases. The `packaging` library handles this behavior correctly.

4.  **Conflict and Missing Version Handling**:
    *   **Missing Version**: If `load_plugin` is called with a `version_specifier` and no registered version of the plugin satisfies it, `PluginManager` will log a clear error and return `None` (or raise a specific `PluginVersionNotFound` exception).
    *   **Dependency Conflicts**: During the (future) implementation of full dependency resolution (Step 1.3.2), if multiple plugins require incompatible versions of a shared dependency plugin, this will be flagged as an error. The current versioning support focuses on direct loading requests; full transitive dependency conflict resolution is a more complex step.
    *   **Error Reporting**: All version-related issues (parsing errors, no matching version, etc.) will be logged with detailed information, including the requested `plugin_id`, `version_specifier`, and available versions.

5.  **API Versioning vs. Plugin Versioning**:
    *   The `version` field in `plugin.json` refers to the version of the plugin package itself (its code and metadata).
    *   While this often correlates with the stability of the plugin's API (actions, parameters), it's distinct from any versioning of the core ApexAgent API that plugins might interact with. For now, we assume a single, stable core agent API for plugins. If the core agent API becomes versioned in the future, plugins might need to declare compatibility with specific core API versions in their metadata.

6.  **Documentation and Examples**:
    *   The `plugin_developer_guide.md` will be updated to explain SemVer usage for the `version` field, how to specify `version_specifier` in dependencies, and how `PluginManager` resolves versions.
    *   Examples in `plugin_metadata_schema_docs.md` will be updated to show version specifiers.

## 4. Step 1.1.4: Implement Strategies for Plugin Updates and Migrations

**Objective**: Define and implement basic strategies for handling plugin updates and managing potential breaking changes.

**Deliverables**:
*   Logic in `PluginManager` to support update checks.
*   Documentation for users and developers on the update process.

**Detailed Steps**:

1.  **Leverage Versioning for Update Detection**:
    *   The `PluginManager` can compare the version of a currently loaded/known plugin with a newly discovered version.

2.  **Define Update Policy**: 
    *   Determine how updates are applied (e.g., automatic on next restart, manual trigger).
    *   Consider how to handle updates for plugins that are currently in use.

3.  **Handling Breaking Changes (Major Version Updates)**:
    *   The system should clearly indicate when a plugin update involves a major version change.
    *   Provide warnings or require confirmation before applying major updates.

4.  **User Notification and Management Interface (Conceptual)**:
    *   Consider how the `PluginManager` might provide information for a UI to inform users about updates.

5.  **Documentation on Updates and Migrations**:
    *   Provide guidance to plugin developers on managing updates and communicating breaking changes.
    *   Inform users on how the system handles plugin updates.

## 5. Step 1.1.5: Implement Expanded Testing Strategy

**Objective**: Ensure the robustness and reliability of the Plugin Registry and Discovery system through comprehensive testing.

**Deliverables**:
*   A suite of unit and integration tests covering all aspects of the system.

**Detailed Steps**:

1.  **Unit Tests for `PluginManager` Components**:
    *   Test metadata parsing and validation logic.
    *   Test checksum and signature verification utilities.
    *   Test individual aspects of the discovery process.

2.  **Integration Tests for Plugin Discovery and Loading Lifecycle**:
    *   Create test scenarios with various plugin setups (valid, invalid, failing security checks, duplicate IDs, different `default_enabled` states, multiple source directories).
    *   Verify `PluginManager` correctly discovers, validates, registers, and loads plugins.
    *   Test version information retrieval and dependency information parsing.

3.  **Tests for Performance Optimization Features**:
    *   If caching is implemented, test cache creation, hit/miss scenarios, and invalidation.

4.  **Tests for Update Handling (Basic)**:
    *   Simulate plugin update scenarios and verify `PluginManager`'s behavior.

## 6. Step 1.1.6: Develop Comprehensive Documentation

**Objective**: Provide clear, comprehensive documentation for both plugin developers and users of the ApexAgent plugin system.

**Deliverables**:
*   Developer documentation for creating and managing plugins.
*   User documentation for understanding and interacting with the plugin system.

**Detailed Steps**:

1.  **Developer Documentation**:
    *   Consolidate and expand `plugin_metadata_schema_docs.md`.
    *   Provide a guide on creating a new plugin: directory structure, `plugin.json` creation, implementing the plugin class, versioning, security (checksums/signatures).
    *   Explain `PluginManager` discovery, validation, and loading processes.
    *   Document APIs or base classes.

2.  **User/Administrator Documentation (High-Level)**:
    *   Explain plugins in ApexAgent.
    *   Describe plugin management (file-based for now).
    *   Explain security implications.
    *   How to interpret plugin information.

**Integration Notes for Overall Plugin System (Section 1.1)**:
*   The `plugin_metadata_schema.json` is central.
*   `PluginManager` is the core controller.
*   Security and error reporting are critical.
*   This work supports future advanced lifecycle management and dependency resolution.




## 4. Step 1.1.3 (Effective - was Section 4 in previous plan structure): Implement Plugin Loading and Execution Framework

**Objective**: Develop a robust framework for dynamically loading plugin code, executing plugin actions, and managing the plugin lifecycle within the ApexAgent environment.

**Deliverables**:
*   Updated `PluginManager.py` with plugin loading and execution capabilities.
*   A defined plugin interface or base class for developers.
*   Unit and integration tests for the loading and execution framework.
*   Documentation for plugin developers on creating and integrating plugins with the new framework.

**Detailed Steps**:

### 4.1. Design Plugin Loading Mechanism (Corresponds to Plan Step 001)

**Objective**:
(Content truncated due to size limit. Use line ranges to read in chunks)



## 5. Step 1.2.1: Design and Implement BaseEnhancedPlugin (Error Handling and Validation)

**Objective**: Enhance the plugin base class (`BasePlugin.py`) to provide robust error handling mechanisms, including a hierarchy of custom plugin exceptions and standardized patterns for argument validation. This aims to improve plugin reliability, maintainability, and the developer experience by making error reporting more specific and consistent.

**Deliverables**:
*   Definition and implementation of custom plugin exception classes (e.g., in `src/core/plugin_exceptions.py`).
*   Updated `BasePlugin.py` to guide or facilitate the use of these custom exceptions.
*   Updated `PluginManager.py` to appropriately catch and log these custom exceptions.
*   Updated `plugin_developer_guide.md` with a new section on error handling, custom exceptions, and argument validation best practices.
*   Unit tests for the new exception classes and any modifications to `BasePlugin` or `PluginManager` related to error handling.

**Detailed Design Considerations and Strategy**:

1.  **Custom Plugin Exception Hierarchy**:
    *   A base exception class `PluginError(Exception)` will be defined. This will serve as the parent for all plugin-specific exceptions.
    *   Specific subclasses will be created for common error scenarios:
        *   `PluginInitializationError(PluginError)`: Raised for errors occurring during a plugin's `__init__` or `initialize` methods (e.g., failure to load essential resources, invalid initial configuration).
        *   `PluginConfigurationError(PluginError)`: Raised specifically when a plugin encounters issues with its provided configuration (e.g., missing required config keys, invalid config values) that prevent it from operating correctly.
        *   `PluginActionError(PluginError)`: A base class for errors related to the execution of plugin actions.
            *   `PluginActionNotFoundError(PluginActionError, AttributeError)`: Raised if `execute_action` is called with an `action_name` that the plugin does not implement or recognize.
            *   `PluginInvalidActionParametersError(PluginActionError, ValueError)`: Raised when the parameters provided to an action are invalid (e.g., wrong type, missing required parameters, value out of range). This is the primary exception for argument validation failures.
            *   `PluginActionExecutionError(PluginActionError)`: Raised for general, unexpected errors that occur during the internal logic of an action's execution, after parameters have been validated.
        *   `PluginDependencyError(PluginError)`: Raised if a plugin detects that a critical dependency (another plugin or an external library) is missing or incompatible during its operation (distinct from discovery-time checks by `PluginManager`).
        *   `PluginResourceNotFoundError(PluginError, FileNotFoundError)`: Raised when a plugin cannot find an essential internal resource it needs to operate (e.g., a template file, a data file).
    *   Each custom exception will be designed to accept a descriptive message and optionally, the original causing exception (for chained exceptions) to aid in debugging.
    *   These exceptions will be located in a new file, e.g., `src/core/plugin_exceptions.py`.

2.  **Argument Validation Patterns for Plugins**:
    *   **Guidance in Developer Guide**: The `plugin_developer_guide.md` will strongly recommend that plugins perform explicit validation of parameters at the beginning of their `execute_action` methods.
    *   **Raising Specific Exceptions**: Plugins should be instructed to raise `PluginInvalidActionParametersError` when parameter validation fails, providing a clear message about the nature of the validation error.
    *   **Tools for Validation**: While `BasePlugin` will not enforce a specific validation library, the guide will suggest:
        *   Using Python's built-in `isinstance()` for basic type checks.
        *   For more complex validation (e.g., data structures, formats, ranges), developers can use libraries like Pydantic within their plugin logic. The `BasePlugin` itself will remain agnostic to these libraries to maintain flexibility.
    *   No new helper methods for validation will be added to `BasePlugin` at this stage to keep it lightweight; the focus is on providing the right exceptions to raise.

3.  **Modifications to `BasePlugin.py`**:
    *   The existing `BasePlugin.py` will be retained and enhanced. No new `BaseEnhancedPlugin.py` will be created for this step to avoid unnecessary class hierarchy proliferation for now.
    *   Docstrings within `BasePlugin.py` (especially for `execute_action`) will be updated to guide developers on using the new custom exceptions for error reporting.
    *   The `BasePlugin` itself will not automatically wrap all errors in these custom exceptions; it remains the plugin developer's responsibility to catch their internal errors and raise the appropriate `PluginError` subclass when it provides more specific and useful context to the `PluginManager` and the system.

4.  **Integration with `PluginManager.py`**:
    *   The `PluginManager`'s `load_plugin` and `execute_plugin_action` methods will be updated to include `try...except` blocks that specifically catch `PluginError` (and its subclasses).
    *   When a `PluginError` is caught, `PluginManager` will log it with more specific details (e.g., distinguishing between an `PluginInitializationError` and a `PluginActionExecutionError`). This allows for better diagnostics and potentially different system responses based on the error type.
    *   Generic exceptions originating from plugins might still be caught by a general `Exception` handler in `PluginManager` but will be logged with less specific plugin-related context.

5.  **Documentation Updates**:
    *   A new section titled "Error Handling and Validation" will be added to `plugin_developer_guide.md`. This section will detail:
        *   The hierarchy and purpose of each custom `PluginError` subclass.
        *   Guidance on when and how plugins should raise these exceptions.
        *   Best practices for validating action parameters and reporting failures using `PluginInvalidActionParametersError`.
    *   Docstrings in `BasePlugin.py` and `PluginManager.py` will be updated to reflect the new error handling mechanisms and expectations.




## 6. Step 1.2.2: Implement Asynchronous Execution and Progress Reporting

**Objective**: Enhance `BasePlugin` and `PluginManager` to support asynchronous execution of plugin actions for long-running tasks and provide a standardized mechanism for plugins to report progress.

**Deliverables**:
*   Updated `BasePlugin.py` with support for `async def execute_action`.
*   Updated `PluginManager.py` to handle asynchronous actions and process progress reports.
*   An example plugin demonstrating asynchronous actions and progress reporting.
*   Updated documentation (`plugin_developer_guide.md` and `plugin_registry_discovery_implementation_plan.md`).
*   Unit and integration tests for these new features.

**Detailed Design and Strategy**:

### 6.1. Asynchronous Action Support

1.  **`BasePlugin.py` Modification**:
    *   The `execute_action` method in `BasePlugin.py` will remain as is to support existing synchronous plugins.
    *   A new method, `async_execute_action(self, action_name: str, **kwargs)`, will be added to `BasePlugin.py`. Plugin developers can override this method if their action needs to be asynchronous.
    *   Alternatively, and preferably for cleaner separation and to avoid forcing all plugins to implement both, we can inspect the `execute_action` method of the loaded plugin instance. If `inspect.iscoroutinefunction(plugin_instance.execute_action)` is true, then `PluginManager` will `await` it. This allows plugin developers to simply define `async def execute_action(...)` if they need it, without a separate method name. This approach is more Pythonic and flexible.
    *   The `PluginManager` will be responsible for checking if the `execute_action` method of a plugin instance is an async function (coroutine) and `await` it accordingly. If it's a regular synchronous function, it will be called directly.

2.  **`PluginManager.py` Enhancement**:
    *   The `execute_plugin_action` method in `PluginManager` will be modified.
    *   Before calling `plugin_instance.execute_action(action_name, **action_args)`, it will use `inspect.iscoroutinefunction()` to check the type of the method.
    *   If it is a coroutine function, `PluginManager` will `await plugin_instance.execute_action(...)`.
    *   If it is a regular function, it will be called as `result = plugin_instance.execute_action(...)`.
    *   This ensures that the agent's main loop (or the calling context of `PluginManager`) can correctly handle both synchronous and asynchronous plugin actions without blocking, assuming the caller of `PluginManager.execute_plugin_action` is itself running in an async context or handles the awaitable appropriately.

3.  **Agent Main Loop Considerations**:
    *   The part of the agent that invokes `PluginManager.execute_plugin_action` must be designed to handle awaitables. If the agent's core loop is synchronous, it might need to run the async plugin actions in a separate event loop or use `asyncio.run()` if appropriate for the context. For an agent architecture, it's highly likely the core processing loop will be asynchronous to manage multiple I/O bound tasks (like LLM calls, tool executions, etc.).

### 6.2. Progress Reporting Mechanism

1.  **Callback-Based Approach**:
    *   A `progress_callback` function will be passed by the `PluginManager` to the plugin's `execute_action` (or `async_execute_action`) method if the plugin indicates it supports progress reporting (e.g., via a metadata flag or by accepting the kwarg).
    *   The `progress_callback` will be an optional parameter in the `execute_action` signature: `def execute_action(self, action_name: str, progress_callback: Optional[Callable] = None, **kwargs)`.
    *   The plugin can then call `progress_callback(progress_data)` at various points during its execution.

2.  **Progress Data Structure**:
    *   `progress_data` will be a dictionary with a standardized structure, for example:
        ```json
        {
          "percentage": float,  // Optional: 0.0 to 100.0
          "message": str,     // Optional: Current status message
          "details": dict     // Optional: Any other structured data
        }
        ```
    *   This allows flexibility while providing common fields.

3.  **`PluginManager` Handling of Progress Reports**:
    *   When `PluginManager` calls a plugin action, it will generate a simple default `progress_callback` function.
    *   This default callback could, for instance, log the progress updates using the agent's standard logging mechanism.
    *   In the future, the calling context (e.g., a UI or a higher-level agent process) could provide its own `progress_callback` to `PluginManager` to display progress to the user or react to specific progress messages.

4.  **Plugin Implementation**:
    *   Plugin developers will check if `progress_callback` is provided and call it with the defined data structure.
    *   Example within a plugin action:
        ```python
        if progress_callback:
            progress_callback({"percentage": 10.0, "message": "Starting task..."})
        # ... perform work ...
        if progress_callback:
            progress_callback({"percentage": 50.0, "message": "Halfway done!"})
        ```

### 6.3. Metadata Indication (Optional Enhancement)

*   Consider adding an optional field in `plugin.json` within each action's definition, like `"supports_progress_reporting": true`, to explicitly declare that an action can provide progress updates. This would allow `PluginManager` to know in advance if it should prepare/pass a callback, though simply passing it as an optional kwarg is also viable and simpler.

This design aims for flexibility, allowing both synchronous and asynchronous plugins, and provides a clear way for long-running tasks to communicate progress without tightly coupling them to a specific UI or logging implementation.



## 7. Step 1.2.3: Implement Stream-Based Output Handling

**Objective**: Enable plugins to return data as a stream, allowing for efficient handling of large outputs or continuous data flows, and enhance `PluginManager` to manage these streams.

**Deliverables**:
*   Updated `BasePlugin.py` and `PluginManager.py` with stream handling capabilities.
*   An example plugin demonstrating stream-based output.
*   Updated documentation for developers.
*   Unit and integration tests for stream functionality.

**Detailed Design and Strategy**:

1.  **Indicating Streamable Output**:
    *   **Mechanism**: A plugin action can indicate it returns a stream by its return type annotation and potentially a flag in its action metadata within `plugin.json`.
    *   **Return Type Annotation**: If an action is intended to return a stream, its `execute_action` method in the plugin should be type-hinted to return `Iterator[Any]`, `AsyncIterator[Any]`, `Generator[Any, None, None]`, or `AsyncGenerator[Any, None]` (or more specific types if known).
    *   **Action Metadata (Optional Flag)**: We can add an optional boolean field, e.g., `"returns_stream": true`, to the action definition in `plugin.json`. While type hints are primary for Python, this metadata flag can be useful for external tools or if the agent needs to know about streamability without loading the plugin code.
    *   **`PluginManager` Detection**: `PluginManager` will primarily rely on inspecting the returned object from `execute_action`. If the object is an iterator or an async iterator (using `isinstance` checks with `collections.abc.Iterator`, `collections.abc.AsyncIterator`), it will be treated as a stream.

2.  **Stream Interface Representation**:
    *   **Synchronous Streams**: For synchronous actions, the stream will be a standard Python iterator/generator (implementing `__iter__` and `__next__`).
    *   **Asynchronous Streams**: For asynchronous actions (`async def execute_action`), the stream will be an async iterator/generator (implementing `__aiter__` and `__anext__`).
    *   **Data Chunks**: Each item yielded by the iterator/generator will represent a chunk of the streamed data. The nature of these chunks (e.g., bytes, strings, structured dictionaries) will be defined by the plugin action itself and should be documented in its action metadata.

3.  **`PluginManager` Handling of Streams**:
    *   **`execute_plugin_action` Modification**: The `PluginManager.execute_plugin_action` method will not attempt to fully consume the stream. Instead, it will return the iterator/async iterator object directly to its caller (e.g., the agent core).
    *   **No Buffering by Default**: `PluginManager` will not buffer the stream unless explicitly designed for a specific caching or intermediary purpose, which is not part of this initial stream implementation.
    *   **Error Handling**: If an error occurs within the plugin while generating the stream (i.e., an exception is raised from `__next__` or `__anext__`), this exception will propagate to the consumer of the stream. `PluginManager` itself won't wrap these iteration-time exceptions unless necessary for context.

4.  **Agent Core Consumption of Streams**:
    *   The component of the agent that invokes `execute_plugin_action` will be responsible for iterating over the returned stream.
    *   **Synchronous Consumption**: `for chunk in stream_object:`
    *   **Asynchronous Consumption**: `async for chunk in async_stream_object:`
    *   **Resource Management**: The consuming component must ensure that streams are properly consumed or closed if necessary, especially if they involve underlying resources (though typical Python generators handle this well).

5.  **Updating `BasePlugin.py`**:
    *   No explicit changes are strictly required in `BasePlugin.py` for a plugin to *return* an iterator/generator. Python functions/methods can already do this.
    *   However, the documentation and examples for `BasePlugin` will be updated to show how to implement actions that yield data.

6.  **Updating `PluginManager.py`**:
    *   The primary change in `PluginManager.execute_plugin_action` is to ensure it correctly identifies and returns iterators/async iterators without attempting to convert them to a list or single value.
    *   The logic that handles `async def` methods in `execute_plugin_action` will already correctly return an async generator if the plugin's `execute_action` is an `async def` that `yields`.

7.  **Documentation Updates**:
    *   `plugin_developer_guide.md` will receive a new section explaining how to create actions that return streams (both sync and async), with examples.
    *   This section in `plugin_registry_discovery_implementation_plan.md` will serve as the design documentation.

**Example (Conceptual Plugin Action)**:

```python
# In a plugin's execute_action method
async def execute_action(self, action_name: str, params: dict = None, progress_callback = None):
    if action_name == "stream_large_data":
        # This is now an async generator function
        for i in range(params.get("chunks", 10)):
            await asyncio.sleep(0.1) # Simulate async work to get data
            yield {"chunk_index": i, "data": f"Data part {i}"}
            if progress_callback:
                progress_callback({"percentage": (i+1)*10, "message": f"Sent chunk {i+1}"})
```

This design prioritizes simplicity and leverages Python's built-in iterator and generator protocols. The `PluginManager` acts as a passthrough for stream objects, leaving consumption to the caller.



## 5. Step 1.2.3: Implement Stream-Based Output Handling

**Objective**: Enable plugins to return data as a stream, suitable for large outputs, continuous data flows, or real-time updates, without blocking the agent or requiring the entire dataset to be in memory at once.

**Deliverables**:
*   Updated `BasePlugin.py` with support for stream-based action execution.
*   Updated `PluginManager.py` to invoke and manage streamed outputs.
*   An example plugin demonstrating stream-based output (`example_stream_plugin`).
*   Updated documentation (`plugin_developer_guide.md`).
*   Unit and integration tests for stream handling.

**Detailed Steps**:

1.  **Enhance `BasePlugin.py` for Streamable Actions**:
    *   A new method `async def execute_action_stream(self, action_name: str, parameters: dict, progress_callback: Callable = None) -> AsyncIterator[Any]:` will be added to `BasePlugin.py`.
    *   Plugins wishing to provide streamed output for an action must implement this method.
    *   The method should `yield` data chunks as they become available.
    *   If a plugin is called via `execute_action_stream` for an action not designed for streaming, it should raise a `NotImplementedError` or a custom `StreamingNotSupportedError` (from `plugin_exceptions.py`).
    *   The `progress_callback` can be used for out-of-band progress updates, separate from the data chunks yielded by the stream.

2.  **Update `PluginManager.py` to Handle Streamed Outputs**:
    *   A new method `async def invoke_action_stream(self, plugin_id: str, action_name: str, parameters: dict, version_specifier: str = None, progress_callback: Callable = None) -> AsyncIterator[Any]:` will be added to `PluginManager.py`.
    *   This method will perform plugin loading, validation, and version resolution similar to `invoke_action`.
    *   It will then call the plugin instance's `execute_action_stream` method.
    *   The `AsyncIterator` returned by the plugin will be returned to the caller, allowing direct iteration over the streamed data.
    *   **Error Handling**: 
        *   Appropriate exceptions (e.g., `PluginNotFoundError`, `PluginActionNotFoundError`, `PluginVersionError`, `StreamingNotSupportedError`) will be raised if the plugin/action cannot be invoked or does not support streaming.
        *   Exceptions occurring within the plugin's stream generator during iteration will propagate to the consumer of the stream.

3.  **Define Data Chunk Guidance (Documentation)**:
    *   The `plugin_developer_guide.md` will provide guidance that yielded data chunks can be any Python object (e.g., strings, dictionaries, custom objects).
    *   Plugins should maintain consistency in the type and structure of data yielded for a particular stream.
    *   Error reporting within a stream (after it has started) should primarily be done by raising exceptions from the generator.

4.  **Create an Example Streaming Plugin (`example_stream_plugin`)**:
    *   A new plugin will be created under `/home/ubuntu/agent_project/src/plugins/example_stream_plugin/`.
    *   It will include a `plugin.json` metadata file.
    *   Its Python code (`example_stream_plugin.py`) will implement `BasePlugin` and provide an action that uses `execute_action_stream` to `yield` a sequence of data (e.g., a series of messages or numbers with small delays to simulate a stream).

5.  **Update Documentation**:
    *   **`plugin_developer_guide.md`**: A new section will be added detailing how to implement streamable actions using `execute_action_stream` and `yield`. Best practices for stream design and error handling will be included.
    *   **`plugin_registry_discovery_implementation_plan.md`**: This current step fulfills this documentation requirement.

6.  **Implement Unit and Integration Tests**:
    *   **Unit Tests (`test_plugin_manager_unit.py`)**:
        *   Test `PluginManager.invoke_action_stream` for successful invocation of a streaming action.
        *   Test scenarios where a plugin or action does not support streaming (e.g., `execute_action_stream` is not implemented or raises `NotImplementedError`).
        *   Test error conditions like plugin not found, action not found, or version mismatches when attempting to invoke a stream.
    *   **Integration Tests (`test_plugin_manager_integration.py`)**:
        *   Utilize the `example_stream_plugin` to test the end-to-end streaming pipeline.
        *   Verify that the consumer of the stream receives all yielded data chunks correctly and in order.
        *   Test the propagation of exceptions raised by the plugin during stream generation.



## 6. Step 1.2.4: Implement Plugin State Persistence

**Objective**: Enable plugins to save and load their internal state across agent sessions, allowing them to remember user preferences, learned data, or progress on long-running tasks.

**Deliverables**:
*   Updated `BasePlugin.py` with methods for state saving and loading.
*   Updated `PluginManager.py` to manage and facilitate state storage and retrieval for plugins.
*   An example plugin demonstrating state persistence.
*   Updated documentation (`plugin_developer_guide.md`).
*   Unit and integration tests for state persistence.

**Detailed Design and Implementation Steps**:

1.  **Design Plugin State Persistence Mechanism**:
    *   **Storage Location**: A dedicated directory, e.g., `/home/ubuntu/agent_project/plugin_states/`, will be used. Within this, each plugin will have its own subdirectory named after its `plugin_id`. Each specific version of a plugin will have its own state file within its plugin ID directory, named, for example, `state_v<version>.json` (e.g., `state_v1.0.2.json`). This allows different versions of the same plugin to maintain separate states if necessary.
    *   **Data Format**: JSON will be used as the primary serialization format for plugin state. This is human-readable, widely supported, and suitable for structured data. Plugins will be responsible for ensuring their state is JSON-serializable. For complex binary data, plugins would need to encode it (e.g., base64) before including it in the JSON state.
    *   **Security**: 
        *   **Sensitivity**: Plugins should be designed to avoid storing highly sensitive information (like raw API keys or PII) directly in their state if possible. If sensitive data must be stored, the plugin itself should handle its encryption/decryption before passing it to the `save_state` method or after receiving it from `load_state`. The `PluginManager` will not provide automatic encryption for all plugin states by default to keep the core mechanism simpler, but this could be a future enhancement or a utility provided to plugins.
        *   **Access Control**: The `plugin_states` directory will be managed by the agent. Direct access by plugins to other plugins' state files will not be permitted through the `PluginManager`'s state management API. Each plugin instance will only be given access to its own state data.
    *   **API in `BasePlugin`**:
        *   `save_state(self, state_data: dict) -> None`: A method for the plugin to request its current state (provided as a dictionary) to be saved.
        *   `load_state(self) -> dict | None`: A method for the plugin to request its previously saved state. Returns the state as a dictionary or `None` if no state is found or an error occurs.
    *   **`PluginManager` Role**:
        *   The `PluginManager` will construct the specific state file path for a given plugin instance (based on its ID and version).
        *   It will handle the file I/O (reading and writing the JSON state file) on behalf of the plugin.
        *   It will pass the loaded state dictionary to the plugin or take the state dictionary from the plugin to save it.
        *   Error handling for file operations (e.g., file not found, permission issues, JSON decoding errors) will be managed by `PluginManager`, which will then communicate success/failure or the loaded state to the plugin.

2.  **Document Design in `plugin_registry_discovery_implementation_plan.md`**: This current section fulfills this step.

3.  **Add State Management Methods to `BasePlugin.py`**:
    *   Implement `save_state(self, state_data: dict)`: This method will likely call a method on `PluginManager` (passed via `agent_context` or a dedicated interface) to perform the actual saving, e.g., `self.agent_context.plugin_state_manager.save_plugin_state(self.plugin_id, self.version, state_data)`.
    *   Implement `load_state(self) -> dict | None`: Similarly, this will call a `PluginManager` method, e.g., `self.agent_context.plugin_state_manager.load_plugin_state(self.plugin_id, self.version)`.
    *   Plugins will call these methods, typically during their `initialize` (to load state) or `shutdown` (to save state), or at other appropriate times during their lifecycle.

4.  **Implement State Management in `PluginManager.py` (or a new `PluginStateManager` class)**:
    *   Create a dedicated directory for plugin states if it doesn't exist (e.g., `/home/ubuntu/agent_project/plugin_states/`).
    *   Implement `save_plugin_state(plugin_id: str, plugin_version: str, state_data: dict)`:
        *   Construct file path: `plugin_states/<plugin_id>/state_v<plugin_version>.json`.
        *   Ensure the plugin-specific subdirectory exists.
        *   Serialize `state_data` to JSON and write to the file, overwriting previous state.
        *   Handle file I/O errors.
    *   Implement `load_plugin_state(plugin_id: str, plugin_version: str) -> dict | None`:
        *   Construct file path.
        *   If file exists, read and deserialize JSON.
        *   Return the dictionary, or `None` if file not found or on JSON error.
        *   Handle file I/O errors.
    *   This functionality might be part of `PluginManager` directly or delegated to a new helper class like `PluginStateManager` accessible via `agent_context`.

5.  **Address Security Considerations (Implementation Details)**:
    *   Documentation will strongly advise plugin developers against storing unencrypted sensitive data.
    *   File permissions for the `plugin_states` directory and its contents should be set to restrict access as much as possible (e.g., only accessible by the agent user).

6.  **Create/Update Example Plugin for State Persistence (`example_stateful_plugin`)**:
    *   Develop a new plugin or modify an existing one.
    *   Demonstrate calling `load_state()` in `initialize()` and `save_state()` in `shutdown()` or during an action.
    *   Example: A counter plugin that increments a value and persists it.

7.  **Update `plugin_developer_guide.md`**: Add a new section explaining how plugins can save and load their state, best practices, and security advice.

8.  **Implement Unit and Integration Tests**: 
    *   Test `BasePlugin` methods (if they contain logic beyond calling `PluginManager`).
    *   Test `PluginManager`'s state saving and loading logic (file creation, data integrity, error handling for file ops, handling of missing states).
    *   Integration tests using the `example_stateful_plugin` to ensure end-to-end persistence works.

9.  **Validate Functionality and Robustness**: Thoroughly test various scenarios.

