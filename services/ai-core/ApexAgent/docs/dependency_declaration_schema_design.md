# Plugin Dependency Declaration - Schema Design

**Objective**: Enhance the `plugin_metadata_schema.json` to allow plugins to declare dependencies on other ApexAgent plugins and external Python libraries, including optional version constraints. This corresponds to Step 1.3.1 of the Core Plugin Architecture Refinement.

**Key Design Points & Features for `dependencies` object in `plugin_metadata_schema.json`**:

1.  **Top-Level `dependencies` Object (Optional)**:
    *   A new optional object named `dependencies` will be added to the root of the plugin metadata schema.
    *   If a plugin has no dependencies, this object can be omitted.

2.  **Structure within `dependencies`**:
    *   The `dependencies` object will contain two optional properties:
        *   `plugins`: An array of objects, each specifying a dependency on another ApexAgent plugin.
        *   `python_libraries`: An array of objects, each specifying a dependency on an external Python library.

3.  **Plugin Dependency Object Structure (`plugins` array items)**:
    *   Each object in the `plugins` array will have the following properties:
        *   `id` (string, required): The unique ID of the required ApexAgent plugin (e.g., "com.example.anotherplugin").
        *   `version_specifier` (string, optional): A version specifier string for the required plugin, following a simplified or standard convention (e.g., Semantic Versioning ranges like `>=1.2.0,<2.0.0`, `==1.5.3`, `~=2.1`). If omitted, any version is considered acceptable (though the `PluginManager` might default to requiring the latest available or a minimum compatible version based on its own logic if not specified).
            *   For initial implementation, we might support exact versions (`==1.0.0`) and minimum versions (`>=1.0.0`). Full SemVer range parsing can be added later using libraries like `packaging.specifiers`.
        *   `description` (string, optional): A brief reason why this plugin is needed.

4.  **Python Library Dependency Object Structure (`python_libraries` array items)**:
    *   Each object in the `python_libraries` array will have the following properties:
        *   `name` (string, required): The name of the Python library as it would be used with `pip` or `import` (e.g., "requests", "numpy").
        *   `version_specifier` (string, optional): A version specifier string for the library, ideally adhering to PEP 440 (e.g., `requests>=2.25.0,<3.0.0`, `numpy==1.20.3`). If omitted, any installed version is considered acceptable, or the `PluginManager` might just check for importability.
        *   `import_check_module` (string, optional): The module name to try importing to verify the library is installed (e.g., for a library named `beautifulsoup4`, the import check module might be `bs4`). If omitted, the `name` property will be used for the import check.
        *   `description` (string, optional): A brief reason why this library is needed.

**Example Snippet for `plugin_metadata.json`**:

```json
{
  "id": "com.example.myfeatureplugin",
  "name": "My Feature Plugin",
  "version": "0.5.0",
  // ... other metadata fields ...
  "dependencies": {
    "plugins": [
      {
        "id": "com.example.coreutilityplugin",
        "version_specifier": ">=1.2.0",
        "description": "Requires core utilities for data processing."
      },
      {
        "id": "com.example.anotherplugin",
        "version_specifier": "==2.1.0" // Exact version
      }
    ],
    "python_libraries": [
      {
        "name": "requests",
        "version_specifier": ">=2.25.0,<3.0.0",
        "description": "Needed for making HTTP requests to external APIs."
      },
      {
        "name": "pandas",
        "version_specifier": "~=1.3", // Compatible release with 1.3
        "import_check_module": "pandas"
      },
      {
        "name": "aioboto3", // No version specifier, just check if importable
        "import_check_module": "aioboto3"
      }
    ]
  }
}
```

**Schema Definition Updates (`plugin_metadata_schema.json`)**:

*   The main schema will be updated to include the `dependencies` object definition.
*   Definitions for `pluginDependency` and `pythonLibraryDependency` objects will be added to the schema's `definitions` section (or equivalent).

**Considerations for `PluginManager` (Step 1.3.2)**:

*   When parsing metadata, the `PluginManager` will need to validate this new `dependencies` section.
*   For plugin dependencies, it will check against its own registry of discovered plugins and their versions.
*   For Python library dependencies, it will attempt to import the specified module and, if a `version_specifier` is provided, use a library like `packaging.requirements` and `packaging.version` (or `importlib.metadata.version` for installed package versions) to check version compatibility.
*   Error reporting must be clear if dependencies are not met.
*   The initial scope does *not* include automatic installation of missing dependencies.

**Deliverables for Step 1.3.1**:

*   This design document (`dependency_declaration_schema_design.md`).
*   Updated `plugin_metadata_schema.json` file incorporating the new `dependencies` structure.
*   Updated `plugin_metadata_schema_docs.md` to document the new dependency fields and their usage.

**Next Steps after this Design**:

1.  Implement the changes in `plugin_metadata_schema.json`.
2.  Update `plugin_metadata_schema_docs.md`.
3.  Proceed to Step 1.3.2: Implement Dependency Checking in `PluginManager`.
