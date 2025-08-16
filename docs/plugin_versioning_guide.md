# ApexAgent Plugin Versioning Guide

This guide explains how to version your ApexAgent plugins and how the `PluginManager` utilizes this version information. Proper versioning is crucial for managing updates, dependencies, and ensuring a stable plugin ecosystem.

## 1. Declaring Your Plugin's Version

Each ApexAgent plugin **must** declare its version in its metadata file (e.g., `plugin.json` or `metadata.json`). This is done using the `version` field.

*   **Field**: `version`
*   **Type**: String
*   **Format**: Semantic Versioning 2.0.0 (SemVer). Examples: `"1.0.0"`, `"0.2.1"`, `"1.3.0-beta.1"`.

**Example `plugin.json` snippet**:
```json
{
  "name": "My Awesome Plugin",
  "id": "com.example.myawesomeplugin",
  "version": "1.0.0",
  "description": "Does awesome things.",
  "author": "Plugin Developer",
  "entry_point": "my_awesome_plugin.main.MyAwesomePlugin",
  "actions": [
    // ... actions ...
  ]
}
```

## 2. Semantic Versioning (SemVer) Basics

Semantic Versioning is a formal convention for determining the version number of new software releases. The version number is typically in the format `MAJOR.MINOR.PATCH`.

*   **MAJOR** version: Increment when you make incompatible API changes.
*   **MINOR** version: Increment when you add functionality in a backward-compatible manner.
*   **PATCH** version: Increment when you make backward-compatible bug fixes.

Additional labels for pre-release (e.g., `1.0.0-alpha`, `1.0.0-beta.2`) and build metadata (e.g., `1.0.0+build.123`) are also allowed.

Adhering to SemVer helps users and other plugins understand the nature of changes between releases.

## 3. How `PluginManager` Uses Version Information

Currently, the `PluginManager` uses the plugin's `version` for the following purposes:

*   **Information & Display**: The version is stored as part of the plugin's registered metadata and can be displayed to users or used in logs.
*   **Duplicate Plugin ID Handling**: When discovering plugins, if multiple plugins with the same `id` are found, the `PluginManager` logs the versions of the conflicting plugins to help diagnose the situation. It currently keeps the first one encountered.
*   **Foundation for Dependency Resolution**: The stored version information is crucial for the planned dependency resolution system (Step 1.3 of the Core Plugin Architecture Refinement). When a plugin declares a dependency on another plugin, it will specify a version range (e.g., `"^1.2.0"`, `">=2.0.0 <3.0.0"`). The `PluginManager` will eventually use the registered versions to find a compatible dependency.

**Future Enhancements**:
*   The `PluginManager` may in the future support loading specific versions of a plugin if multiple versions are available and the system is configured to manage them.
*   More sophisticated dependency resolution will rely heavily on accurate SemVer in plugin metadata.

## 4. Versioning Dependencies on Other Plugins

If your plugin depends on another ApexAgent plugin, you should declare this dependency, including the compatible version range, in the `dependencies` section of your plugin's metadata file.

**Example `dependencies` snippet**:
```json
{
  // ... other metadata ...
  "dependencies": [
    {
      "plugin_id": "com.apexagent.documentprocessor",
      "version_range": "^1.2.0" // Requires DocumentProcessor version 1.2.0 or any later 1.x version
    },
    {
      "plugin_id": "com.apexagent.anotherplugin",
      "version_range": ">=2.1.0 <3.0.0" // Requires AnotherPlugin version >= 2.1.0 but less than 3.0.0
    }
  ]
}
```

*   **`plugin_id`**: The unique ID of the plugin your plugin depends on.
*   **`version_range`**: A string specifying the compatible version range. Common conventions (like those used by npm or pip) are recommended. The `semantic_version` Python library can parse many common specifier formats.

## 5. Best Practices for Plugin Versioning

*   **Start with `0.1.0`**: For initial development, you can start with a `0.x.y` version.
*   **Increment `MAJOR` for Breaking Changes**: If you change your plugin's API or functionality in a way that is not backward-compatible, increment the `MAJOR` version (e.g., `1.5.2` -> `2.0.0`).
*   **Increment `MINOR` for New Features**: If you add new features but maintain backward compatibility, increment the `MINOR` version (e.g., `1.5.2` -> `1.6.0`).
*   **Increment `PATCH` for Bug Fixes**: For backward-compatible bug fixes, increment the `PATCH` version (e.g., `1.5.2` -> `1.5.3`).
*   **Be Clear in Changelogs**: Maintain a changelog for your plugin that details changes in each version.
*   **Test Thoroughly**: Before releasing a new version, especially a `MAJOR` or `MINOR` update, test it thoroughly, including its interaction with potential dependent plugins or core agent features.

By following these guidelines, you contribute to a more stable, manageable, and understandable plugin ecosystem for ApexAgent.
