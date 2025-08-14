# Detailed Plan: Step 1.2.2 - Implement Asynchronous Execution, Progress Reporting, and Advanced Features

This document outlines the detailed steps to implement asynchronous action execution, progress reporting, and advanced operational capabilities within the ApexAgent plugin architecture, incorporating user feedback for a more robust system.

## 1. Goals

-   Enable plugins to perform long-running, I/O-bound operations without blocking the main agent thread.
-   Provide a standardized, structured mechanism for plugins to report progress, including hierarchical progress for complex tasks.
-   Implement cancellation support for long-running operations.
-   Introduce basic timeout mechanisms for asynchronous tasks.
-   Enhance error handling with retry policies for transient failures.
-   Ensure the `PluginManager` can correctly invoke and manage asynchronous actions, their progress, cancellation, and timeouts.
-   Provide clear documentation and examples for plugin developers.
-   Lay the groundwork for future enhancements like advanced resource management, monitoring, and state persistence for long-running operations.

## 2. Phased Implementation Approach

Given the scope of enhancements, a phased approach is recommended:

*   **Phase 1: Core Async, Progress, Cancellation, Timeout, and Basic Retries (Focus of this plan)**
    *   Structured `ProgressUpdate` class.
    *   `CancellationToken` mechanism.
    *   Basic timeout for actions.
    *   Simple retry policy integration.
    *   Updates to `BasePlugin` and `PluginManager`.
    *   Example plugin and documentation for Phase 1 features.
*   **Phase 2: Advanced Resource Management and Observability (Future Plan)**
    *   Task scheduler with concurrency limits.
    *   Advanced monitoring, metrics, and logging/tracing.
*   **Phase 3: State Persistence for Long-Running Operations (Future Plan)**
    *   Checkpointing and resuming interrupted operations.

**This document details the plan for Phase 1.**

## 3. Detailed Steps (Phase 1)

### Step 3.1: Design Core Asynchronous Infrastructure

*   **Task 3.1.1: Define `ProgressUpdate` Class:**
    *   Implement a `ProgressUpdate` class as suggested in user feedback:
        ```python
        class ProgressUpdate:
            def __init__(self, percentage: float, message: str, status: str, 
                         details: dict = None, sub_tasks: list = None): # sub_tasks for future hierarchical use
                self.percentage = percentage
                self.message = message
                self.status = status  # e.g., "running", "completed", "error", "milestone_reached"
                self.details = details or {}
                self.sub_tasks = sub_tasks or [] # Placeholder for future use
            
            def validate(self) -> bool:
                # Basic validation: percentage 0-100, status in allowed set, etc.
                if not (0.0 <= self.percentage <= 100.0):
                    return False
                # Add more validation as needed
                return True
        ```
    *   This class will be used for all progress reporting.
*   **Task 3.1.2: Define `CancellationToken` Class:**
    *   Implement a `CancellationToken` class:
        ```python
        class CancellationToken:
            def __init__(self):
                self._cancelled = False
            def cancel(self):
                self._cancelled = True
            @property
            def is_cancelled(self):
                return self._cancelled
        ```
*   **Task 3.1.3: Define `PluginActionTimeoutError` Exception:**
    *   Create a new custom exception `PluginActionTimeoutError(PluginActionExecutionError)`.

### Step 3.2: Refine `BasePlugin` for Asynchronous Operations

*   **Task 3.2.1: Update Asynchronous Action Signature:**
    *   Modify the `execute_action` signature in `BasePlugin.py`:
        `async def execute_action(self, action_name: str, params: dict = None, progress_callback: Optional[Callable[[ProgressUpdate], None]] = None, cancellation_token: Optional[CancellationToken] = None) -> Any:`
    *   The `progress_callback` will now accept a `ProgressUpdate` instance.
    *   The `cancellation_token` will be passed by the `PluginManager`.
*   **Task 3.2.2: Guidance for Plugins:**
    *   Plugins implementing async actions should periodically check `cancellation_token.is_cancelled` and gracefully terminate if true.
    *   Plugins should instantiate and use `ProgressUpdate` objects for reporting.

### Step 3.3: Modify `PluginManager` for Enhanced Async Support

*   **Task 3.3.1: Detect Asynchronous Actions:** (As per original plan)
    *   Use `inspect.iscoroutinefunction()`.
*   **Task 3.3.2: Instantiate and Pass `CancellationToken`:**
    *   `PluginManager.execute_plugin_action()` will create a `CancellationToken` instance and pass it to the plugin.
*   **Task 3.3.3: Implement Action Timeout Mechanism:**
    *   `PluginManager.execute_plugin_action()` will accept an optional `timeout` parameter (e.g., in seconds).
    *   Use `asyncio.wait_for()` to wrap the plugin action coroutine call. If a timeout occurs, catch `asyncio.TimeoutError` and raise `PluginActionTimeoutError`.
*   **Task 3.3.4: Implement Progress Callback Handling:** (Revised)
    *   The `progress_callback` function defined within `PluginManager.execute_plugin_action()` will now expect a `ProgressUpdate` object.
    *   It should validate the `ProgressUpdate` object using its `validate()` method before processing.
    *   Initial processing: Log the structured progress.
*   **Task 3.3.5: Basic Retry Mechanism (Conceptual - for future integration with a RetryPolicy class):**
    *   For now, `PluginManager` will not implement a full retry policy. However, the design should acknowledge that plugins themselves might implement retries for certain operations, or a future `AsyncOperationManager` could handle this.
    *   The focus for Phase 1 is on the plugin being able to execute robustly with cancellation and timeouts.
*   **Task 3.3.6: Error Handling for Async Actions:** (As per original plan, ensure `PluginActionTimeoutError` is handled).

### Step 3.4: Develop an Example Plugin for Phase 1 Features

*   **Task 3.4.1: Create/Update `ExampleAsyncPlugin`:**
    *   Demonstrate an asynchronous action that takes time.
    *   Show periodic checks for `cancellation_token.is_cancelled`.
    *   Implement progress reporting using `ProgressUpdate` objects.
    *   Show how it might react to a timeout (though the timeout is enforced by `PluginManager`).

### Step 3.5: Implement Unit and Integration Tests for Phase 1

*   **Task 3.5.1: Test `ProgressUpdate` and `CancellationToken` classes.**
*   **Task 3.5.2: Test `PluginManager` Async Handling, Cancellation, and Timeout:**
    *   Verify correct invocation of async actions.
    *   Test that cancellation requests are propagated (plugin mock checks token).
    *   Test that timeouts are enforced and `PluginActionTimeoutError` is raised.
*   **Task 3.5.3: Test Progress Callback with `ProgressUpdate` objects.**
*   **Task 3.5.4: Test `ExampleAsyncPlugin` functionality.**

### Step 3.6: Update Developer Documentation for Phase 1

*   **Task 3.6.1: Update `plugin_developer_guide.md`:**
    *   Revise sections on asynchronous actions.
    *   Detail the `ProgressUpdate` class, its fields, and validation.
    *   Explain how to use the `cancellation_token`.
    *   Mention the timeout mechanism enforced by `PluginManager`.
    *   Provide updated code examples based on the `ExampleAsyncPlugin`.
*   **Task 3.6.2: Update `BasePlugin.py` and other relevant docstrings.**

## 4. Deliverables (Phase 1)

*   `ProgressUpdate` and `CancellationToken` class implementations.
*   `PluginActionTimeoutError` custom exception.
*   Updated `BasePlugin.py` with revised `execute_action` signature.
*   Updated `PluginManager.py` to support async actions, cancellation tokens, timeouts, and structured progress reporting.
*   An `ExampleAsyncPlugin` demonstrating Phase 1 features.
*   Comprehensive unit and integration tests.
*   Updated `plugin_developer_guide.md`.
*   This updated plan document (`async_progress_reporting_plan.md`).

## 5. Timeline (Estimate for Phase 1)

*   Step 3.1 (Design Core Async Infrastructure): 2-3 hours
*   Step 3.2 (Refine `BasePlugin`): 1-2 hours
*   Step 3.3 (Modify `PluginManager` - Async, Cancel, Timeout, Progress): 4-6 hours
*   Step 3.4 (Develop Example Plugin): 2-3 hours
*   Step 3.5 (Implement Tests): 5-7 hours
*   Step 3.6 (Update Documentation): 3-4 hours
*   **Total Estimated Time for Phase 1:** 17-25 hours (spread over multiple work sessions)

## 6. Future Phases Considerations (Post Phase 1)

*   **Resource Management (Phase 2):** Introduce `TaskScheduler` for concurrency control.
*   **Enhanced Error Handling & Recovery (Phase 2/3):** Implement `RetryPolicy` class and integrate it, support partial results.
*   **Advanced Monitoring & Observability (Phase 2/3):** `OperationMetrics`, logging/tracing integration.
*   **State Persistence for Long-Running Operations (Phase 3):** Checkpointing and resuming.
*   **Hierarchical Progress Reporting (Phase 2/3):** Fully utilize `sub_tasks` in `ProgressUpdate`.
*   **Dedicated `AsyncOperationManager` (Phase 2):** To centralize handling of scheduling, cancellation, monitoring, etc., as suggested in user feedback.

This phased approach allows for incremental delivery of a robust asynchronous execution framework, prioritizing critical features first.

