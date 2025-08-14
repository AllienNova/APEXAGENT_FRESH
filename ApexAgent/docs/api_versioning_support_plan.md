# API Versioning Support for PluginManager - Design Plan

**Objective**: Enable the `PluginManager` and plugins to support API versioning, allowing for backward compatibility and graceful evolution of plugin interfaces. This corresponds to Step 1.1.3 of the Plugin Registry and Discovery System.

**Key Considerations & Design Points**:

1.  **Leverage `version` field in Metadata**:
    *   The `version` field (e.g., "1.2.3") in `plugin_metadata_schema.json` is the primary source for a plugin's own version. This is already captured during discovery.
    *   The `PluginManager` will store this version alongside other metadata for each registered plugin.

2.  **`PluginManager` Version Awareness & Storage**:
    *   The `plugin_registry` in `PluginManager` currently stores:
        ```python
        self.plugin_registry[plugin_id] = {
            "metadata": metadata,
            "path": plugin_path,
            "metadata_path": metadata_file_path
        }
        ```
    *   The `metadata` object already contains the `version` string.
    *   No change is immediately needed for storage, as the version is part of the stored metadata.

3.  **Handling Multiple Versions of the Same Plugin (Conceptual - Future Enhancement)**:
    *   Currently, the `discover_plugins` method handles duplicate `plugin_id`s by keeping the first one encountered and logging a warning. This implicitly means only one version of a plugin (by ID) is active.
    *   For true multi-version support (e.g., `com.example.foo v1.0.0` and `com.example.foo v1.1.0` both available), the `plugin_registry` keying would need to change, perhaps to a tuple of `(plugin_id, version)` or the value for a `plugin_id` would be a list/dict of versions.
    *   **For this initial implementation (Step 1.1.3), we will assume that only one version of a plugin (per `plugin_id`) is loaded/active at a time, typically the one found in its specific plugin directory.** The `version` field is primarily for informational purposes and for future dependency resolution (Step 1.3).

4.  **Retrieving Plugin by Version (Future Enhancement)**:
    *   A method like `get_plugin_instance(plugin_id, version_specifier=None)` could be envisioned.
    *   If `version_specifier` is provided (e.g., "~1.0", ">=1.0,<2.0"), the `PluginManager` would need a mechanism to parse this specifier and compare it against the semantic versions of available plugins (if multiple versions were supported).
    *   Libraries like `semantic_version` (Python package) can be used for parsing and comparing SemVer strings and specifiers.
    *   **For this initial implementation (Step 1.1.3), `get_plugin_instance` will not yet support a `version_specifier`. It will load the single discovered version of the plugin.** The groundwork is laid by storing the version string.

5.  **API Versioning vs. Plugin Versioning**:
    *   The `version` in `plugin.json` refers to the plugin's own version (features, bugfixes).
    *   If ApexAgent itself has a versioned core API that plugins interact with, plugins might need to declare compatibility with a specific core API version. This is a more advanced topic.
    *   **For Step 1.1.3, the focus is on the plugin's own version.** The `dependencies` field in the metadata already allows specifying version ranges for *other plugin* dependencies.

6.  **Modifications to `PluginManager.py`**:
    *   Ensure the `version` from metadata is accessible. (Already done as it's part of `metadata`).
    *   No significant changes to loading logic are required for this initial step, as we are not yet implementing selection of specific versions from multiple available versions of the *same* plugin ID.
    *   The primary change will be in documentation and laying the conceptual groundwork for future version-aware operations.

7.  **Base Plugin Structure (`BaseEnhancedPlugin`)**:
    *   No immediate changes are required to a base plugin class *for this specific step* regarding its own version declaration, as it's handled by the external metadata file.
    *   If a plugin needed to declare compatibility with a *core agent API version*, that might be a property on the base class in the future.

8.  **Documentation for Developers**:
    *   Create/update documentation explaining:
        *   How to specify their plugin's version in `plugin.json` using Semantic Versioning.
        *   How the `PluginManager` currently uses this version (primarily for information and future dependency checks).
        *   Best practices for versioning (e.g., when to increment MAJOR, MINOR, PATCH).
        *   How to specify version ranges for dependencies on other plugins (using the existing `dependencies` field).

**Deliverables for Step 1.1.3**:

*   **Updated `PluginManager.py`**: While major functional changes for version selection are deferred, ensure the code is clean and comments reflect the awareness of the stored version information for future use. Potentially add a helper method to parse/compare semantic versions if any internal logic starts needing it (though likely not for this specific step if we defer advanced selection).
*   **Documentation (`plugin_versioning_guide.md`)**: A new document explaining plugin versioning for developers, covering the points in item 8 above.
*   **Unit Tests**: Tests to verify that the version string is correctly read and stored as part of the plugin's metadata in the registry. (This is implicitly covered by existing tests that check the full metadata object, but can be made more explicit if desired).

**Implementation Steps for 1.1.3**:

1.  **Review `PluginManager.py`**: Confirm that the `version` field from plugin metadata is correctly stored and accessible. Add comments if needed to highlight its role for versioning.
2.  **Install `semantic_version` library**: Although full version-specifier logic is deferred, installing it now prepares for future dependency resolution steps and allows for easy version validation/comparison if any simple checks are added. `pip3 install semantic_version`.
3.  **Draft `plugin_versioning_guide.md`**: Write the documentation for plugin developers.
4.  **Update/Add Unit Tests (Minor)**: Ensure at least one test explicitly checks that the `version` field is correctly retrieved from a test plugin's metadata by the `PluginManager`.
5.  **Review and Refine**: Ensure documentation is clear and accurate.

**Self-Correction/Refinement during Design**:
*   Initial thought: Implement full version selection logic in `PluginManager` now.
*   Correction: The detailed plan (Step 1.1.3) focuses on *awareness* and *documentation* for the plugin's own version. Full, complex version selection (especially with multiple versions of the same plugin ID active) and dependency resolution are larger efforts (Step 1.3). This step lays the foundation by ensuring versions are captured and developers know how to declare them.
*   The `dependencies` field in `plugin_metadata_schema.json` already provides a way for plugins to declare versioned dependencies on *other* plugins. The `PluginManager` will eventually need to use this for resolution (Step 1.3.2).

This design focuses on fulfilling the immediate requirements of Step 1.1.3 while setting the stage for more advanced versioning features later.
