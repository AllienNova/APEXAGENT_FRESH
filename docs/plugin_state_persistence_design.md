# Plugin State Persistence - Design Plan

**Objective**: Implement functionality for plugins (via `BaseEnhancedPlugin`) to save and load their internal state, with `PluginManager` managing the storage and retrieval. This corresponds to Step 1.2.4 of the Core Plugin Architecture Refinement.

**Key Design Points & Features**:

1.  **`BaseEnhancedPlugin` API for State Management**:
    *   New `async` methods will be added to `BaseEnhancedPlugin`:
        *   `async def _save_plugin_state(self, key: str, value: Any) -> None`:
            *   Allows the plugin to request saving a serializable `value` associated with a `key`.
            *   The plugin itself does not know *how* or *where* it's saved, only that it requests it.
            *   This method will delegate the actual saving mechanism to the `PluginManager` via a callback or a direct call if the `PluginManager` instance is accessible.
        *   `async def _load_plugin_state(self, key: str, default: Optional[Any] = None) -> Any`:
            *   Allows the plugin to request loading a previously saved value associated with a `key`.
            *   If the key is not found, it returns the `default` value.
            *   Delegates to `PluginManager` for actual loading.
        *   `async def _delete_plugin_state(self, key: str) -> bool`:
            *   Allows the plugin to request deletion of a state entry by `key`.
            *   Returns `True` if deletion was successful or key didn't exist, `False` on error.
            *   Delegates to `PluginManager`.
    *   These methods will be prefixed with an underscore to indicate they are intended for internal use by the plugin and rely on the managing system (`PluginManager`).

2.  **`PluginManager` Responsibilities for State Persistence**:
    *   **Storage Location**: `PluginManager` will define a root directory for storing plugin states (e.g., `/home/ubuntu/agent_project/plugin_states/`).
    *   **Per-Plugin State Storage**: Within the root directory, each plugin instance will have its own subdirectory, named by its unique `plugin_id` (e.g., `/home/ubuntu/agent_project/plugin_states/com.example.myplugin/`). This isolates plugin states.
    *   **State File Format**: Each state `key` for a plugin will be stored as a separate JSON file within the plugin's state directory (e.g., `/home/ubuntu/agent_project/plugin_states/com.example.myplugin/my_state_key.json`).
        *   JSON is chosen for its human-readability and wide support. Data must be JSON-serializable.
        *   The file will contain the `value` associated with the `key`.
    *   **State Management Callbacks/Methods**: `PluginManager` will need to provide the actual implementation for saving, loading, and deleting state. This can be achieved by passing callback functions to `BaseEnhancedPlugin` upon instantiation, or by `BaseEnhancedPlugin` having a reference to its managing `PluginManager` (less ideal due to tight coupling).
        *   **Preferred Approach**: Pass state management functions (e.g., `save_state_func`, `load_state_func`, `delete_state_func`) from `PluginManager` to `BaseEnhancedPlugin` during its initialization. These functions will be bound to the specific `plugin_id`.
            *   `BaseEnhancedPlugin.__init__` will accept these optional callbacks.
            *   The `_save_plugin_state`, `_load_plugin_state`, `_delete_plugin_state` methods in `BaseEnhancedPlugin` will then call these provided functions.
    *   **Serialization/Deserialization**: `PluginManager`'s state functions will handle JSON serialization (on save) and deserialization (on load).
    *   **Error Handling**: Robust error handling for file I/O operations (file not found, permissions, disk full, serialization errors) is crucial. Custom exceptions like `PluginStateError` (already defined) should be used.
    *   **Security**: 
        *   The state directory should have appropriate permissions.
        *   Sensitive data stored by plugins is the plugin developer's responsibility to encrypt *before* passing to `_save_plugin_state` if needed. The framework provides persistence, not encryption of arbitrary plugin data by default.
        *   Documentation must clearly state that plugins should not store unencrypted sensitive information using this mechanism unless the underlying storage is appropriately secured.

3.  **Integration between `BaseEnhancedPlugin` and `PluginManager`**:
    *   `PluginManager.get_plugin_instance()` will be updated to pass the state management functions to the `BaseEnhancedPlugin` constructor.
    *   These functions will be closures or partial functions that already know the `plugin_id` and the base state path, so `BaseEnhancedPlugin` only needs to pass the `key` and `value`.
    *   Example of functions `PluginManager` would create and pass:
        ```python
        # Inside PluginManager, when creating a plugin instance:
        plugin_id = "com.example.myplugin"
        state_dir = os.path.join(self.root_state_dir, plugin_id)
        os.makedirs(state_dir, exist_ok=True)

        async def save_state_for_plugin(key: str, value: Any):
            # ... logic to save value to state_dir/key.json ...
        
        async def load_state_for_plugin(key: str, default: Optional[Any] = None) -> Any:
            # ... logic to load value from state_dir/key.json ...

        async def delete_state_for_plugin(key: str) -> bool:
            # ... logic to delete state_dir/key.json ...

        instance = plugin_class(
            ...,
            save_state_func=save_state_for_plugin,
            load_state_func=load_state_for_plugin,
            delete_state_func=delete_state_for_plugin
        )
        ```

4.  **Example Plugin**:
    *   A new example plugin (e.g., `ExampleStatefulPlugin`) will be created.
    *   It will demonstrate using `_save_plugin_state` to store some data (e.g., a counter, user preference) and `_load_plugin_state` to retrieve it upon next execution or initialization.

5.  **Documentation**:
    *   Update `BaseEnhancedPlugin` documentation for the new state management methods.
    *   Update `PluginManager` documentation regarding state storage strategy and security considerations.
    *   Provide guidance for plugin developers on how to use state persistence and when it's appropriate.

**Deliverables for Step 1.2.4**:

*   **Updated `BaseEnhancedPlugin.py`**: With `_save_plugin_state`, `_load_plugin_state`, `_delete_plugin_state` methods and updated `__init__` to accept state management functions.
*   **Updated `PluginManager.py`**: With logic to manage plugin state storage (directory creation, file I/O, serialization) and to pass state management functions to plugin instances.
*   **Example Plugin (`example_stateful_plugin.py`)**: Demonstrating usage of state persistence.
*   **Unit Tests**: For `PluginManager`'s state management logic and for the example stateful plugin.
*   **Documentation**: Updated developer guides and security notes.

**Implementation Steps for 1.2.4**:

1.  **Update `BaseEnhancedPlugin`**:
    *   Modify `__init__` to accept `save_state_func`, `load_state_func`, `delete_state_func` (optional, typed with `Callable`).
    *   Implement `async def _save_plugin_state(self, key, value)`, `async def _load_plugin_state(self, key, default=None)`, and `async def _delete_plugin_state(self, key)` that call these functions if available, logging a warning or raising an error if not.
2.  **Update `PluginManager`**:
    *   Define `self.root_plugin_states_dir` in `__init__`.
    *   Implement the actual state persistence helper methods (e.g., `_save_state_to_file`, `_load_state_from_file`, `_delete_state_file`) that take `plugin_id`, `key`, `value`.
    *   In `get_plugin_instance`, create and pass the bound state management functions (e.g., using `functools.partial` or lambdas) to the plugin constructor.
    *   Ensure directory creation for plugin states (`os.makedirs(..., exist_ok=True)`).
    *   Implement robust error handling (file I/O, JSON errors) using `PluginStateError`.
3.  **Create `ExampleStatefulPlugin`**: Implement a plugin that uses the new state methods.
4.  **Write Unit Tests**:
    *   Test saving state via `PluginManager` (indirectly by calling plugin's method).
    *   Test loading existing state.
    *   Test loading non-existent state (should return default).
    *   Test deleting state.
    *   Test error conditions (e.g., non-serializable data, permission issues if mockable).
5.  **Update Developer Documentation**: Explain the feature, usage, and security implications.
6.  **Review and Refine**: Ensure the mechanism is secure, robust, and developer-friendly.

**Security Considerations (Reiteration)**:
*   Plugin state is stored per-plugin ID, providing isolation.
*   Data is stored as JSON files. If plugins need to store sensitive data, they are responsible for encrypting it *before* calling `_save_plugin_state`.
*   The root state directory must be secured by the system administrator.
*   Documentation must clearly warn developers about storing sensitive data unencrypted.

This design provides a clear separation of concerns: `BaseEnhancedPlugin` defines the interface for plugins to request state operations, and `PluginManager` implements the actual storage mechanism.
