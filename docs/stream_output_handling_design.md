# Stream-Based Output Handling in Plugins - Design Plan

**Objective**: Enable actions in `BaseEnhancedPlugin` to return data as a stream (e.g., using async generators) and update `PluginManager` to handle these streamed outputs, making them available to the agent core. This corresponds to Step 1.2.3 of the Core Plugin Architecture Refinement.

**Key Design Points & Features**:

1.  **Plugin Action Definition for Streaming Output**:
    *   Actions that need to stream output will be defined as `async def` methods in the plugin (inheriting from `BaseEnhancedPlugin`).
    *   These methods will use `yield` to produce chunks of data, effectively making them asynchronous generators.
    *   Example:
        ```python
        # In a concrete plugin class
        async def stream_generated_text(self, prompt: str):
            # Simulate generating text chunk by chunk
            for i in range(5):
                await asyncio.sleep(0.1)
                chunk = f"Text chunk {i+1} for prompt 
{prompt}
"
                yield chunk
            yield "END_OF_STREAM" # Optional: A special marker for end, or just let the generator exhaust.
        ```
    *   The type of data yielded can be anything (e.g., strings, dictionaries, custom objects), but consistency per action is important.

2.  **`BaseEnhancedPlugin` Support**:
    *   The existing `BaseEnhancedPlugin.execute_action` method already uses `inspect.iscoroutinefunction` and `await` for async methods. If an `async def` method uses `yield`, it returns an async generator.
    *   The `execute_action` method will, therefore, return an `AsyncGenerator` if the underlying action method is an async generator.
    *   No significant changes are needed in `BaseEnhancedPlugin` itself to *enable* returning async generators, but its documentation should clarify this capability.

3.  **`PluginManager` Handling of Streamed Outputs**:
    *   When `PluginManager` invokes a plugin action (e.g., via a method like `async call_plugin_action(self, plugin_id, action_name, **kwargs)`), it needs to check the return type.
    *   If the return value is an `AsyncGenerator` (which can be checked using `inspect.isasyncgen`), the `PluginManager` (or the entity calling `PluginManager`) must iterate over it asynchronously to consume the stream.
    *   **Option A: `PluginManager` returns the async generator directly.**
        *   The `PluginManager.call_plugin_action` method would return the async generator to its caller (e.g., the agent core).
        *   The agent core would then be responsible for `async for chunk in result_stream:`.
        *   This is simpler for `PluginManager` but puts more responsibility on the caller.
    *   **Option B: `PluginManager` consumes the stream and uses a callback.**
        *   The `PluginManager.call_plugin_action` could accept an optional `stream_callback` function.
        *   If an async generator is returned by the plugin and `stream_callback` is provided, `PluginManager` iterates and calls the callback for each chunk.
        *   `async def call_plugin_action(self, plugin_id, action_name, stream_callback=None, **kwargs)`
        *   This is more complex for `PluginManager` but provides a consistent interface for the caller, regardless of whether the output is streamed or a single value.
    *   **Decision**: Option A is generally more flexible and Pythonic for handling async generators. The `PluginManager`'s primary role is to execute the action; the consumption of the stream is better handled by the component that needs the data. The `PluginManager` should clearly document when an action is expected to return a stream (perhaps based on plugin metadata).
    *   The `PluginManager`'s method that executes the plugin action (let's assume it's an enhanced version of `BaseEnhancedPlugin.execute_action` or a new method in `PluginManager` that wraps it) will return the result. If the result is an `AsyncGenerator`, the caller is responsible for iterating through it.

4.  **Metadata Indication for Streaming Actions (Optional Enhancement)**:
    *   To help the `PluginManager` or agent core know in advance if an action streams output, the plugin metadata schema (`plugin_metadata_schema.json`) could be enhanced.
    *   Add an optional boolean field `"streams_output": true` to the action definition in the metadata.
    *   This allows the system to prepare for stream handling without needing to inspect the function signature at runtime every time, or to present streaming UIs more effectively.
    *   If not present, the system could default to `false` or inspect the return type annotation if available (e.g., `AsyncGenerator[str, None]`).

5.  **Error Handling in Streams**:
    *   If an exception occurs within the plugin's async generator action *during streaming*, the `async for` loop in the consumer will raise that exception.
    *   The `PluginManager` or the agent core consuming the stream must be prepared to handle exceptions during stream iteration.
    *   `BaseEnhancedPlugin.execute_action` already has a `try...except` block. If the action method (the async generator function itself) raises an error *before yielding anything*, `execute_action` would catch it. If an error occurs *while the generator is yielding*, the consumer of the generator handles it.

6.  **Example Plugin**:
    *   A new example plugin (e.g., `ExampleStreamingPlugin`) will be created.
    *   It will feature at least one `async def` action that uses `yield` to stream data (e.g., chunks of text, or a sequence of numbers).

7.  **Documentation**:
    *   Update developer documentation for `BaseEnhancedPlugin` to explain how to create actions that stream output using `async def` and `yield`.
    *   Update `PluginManager` documentation to explain how it returns async generators and how callers should consume them.

**Deliverables for Step 1.2.3**:

*   **Updated `BaseEnhancedPlugin.py`**: Minor updates or primarily documentation clarifying support for `async def` actions that `yield` (returning `AsyncGenerator`).
*   **Updated `PluginManager.py`**: Modifications to its action execution logic to correctly return `AsyncGenerator` instances to the caller. Documentation on how the caller should handle these.
*   **Example Plugin (`example_streaming_plugin.py`)**: Demonstrating an action that streams output.
*   **Unit Tests**: For the `PluginManager`'s handling of streaming actions and for the example streaming plugin.
*   **Documentation**: Updated developer guides.
*   **(Optional) Updated `plugin_metadata_schema.json`**: If adding the `streams_output` field.

**Implementation Steps for 1.2.3**:

1.  **(Optional) Update `plugin_metadata_schema.json`**: Add `streams_output: boolean` to the action definition and update its documentation.
2.  **Review/Update `BaseEnhancedPlugin.execute_action`**: Ensure it correctly returns the `AsyncGenerator` produced by an `async def ... yield` action. Add documentation.
3.  **Update `PluginManager` Action Invocation**: Ensure the method in `PluginManager` that calls plugin actions (e.g., a hypothetical `PluginManager.invoke_action(plugin_instance, action_name, **kwargs)`) correctly returns the `AsyncGenerator` to its own caller (e.g., the agent core).
4.  **Create `ExampleStreamingPlugin`**: Implement a plugin with an `async def ... yield` action.
5.  **Write Unit Tests**:
    *   Test that `PluginManager` (or its action invocation part) returns an `AsyncGenerator` when a streaming action is called.
    *   Test consumption of the stream from the example plugin, verifying yielded chunks.
    *   Test error handling if the generator raises an exception during iteration.
6.  **Update Developer Documentation**: Explain how to create and consume streaming plugin actions.
7.  **Review and Refine**: Ensure the streaming mechanism is intuitive and robust.

**Self-Correction/Refinement during Design**:
*   The `PluginManager` should not consume the stream itself unless it has a specific role like multiplexing or transforming streams. Returning the raw `AsyncGenerator` is cleaner for the direct consumer.
*   Clear documentation and possibly metadata flags are important for the caller to know when to expect a stream versus a single return value.

This design focuses on leveraging Python's native async generator capabilities for efficient stream handling.
