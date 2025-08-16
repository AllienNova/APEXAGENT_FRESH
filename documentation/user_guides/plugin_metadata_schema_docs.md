# ApexAgent Plugin Metadata Schema Documentation

This document provides a detailed explanation of the fields used in the `plugin_metadata_schema.json` for ApexAgent plugins. This schema is used to define the properties and capabilities of each plugin, enabling discovery, versioning, dependency management, and user understanding.

## Root Object

The metadata file is a single JSON object with the following properties:

### `name`
*   **Type**: `String`
*   **Required**: Yes
*   **Description**: A unique, human-readable name for the plugin. This is typically what users will see.
*   **Example**: `"Knowledge Graph Plugin"`, `"Advanced Document Processor"`

### `id`
*   **Type**: `String`
*   **Required**: Yes
*   **Description**: A machine-readable unique identifier for the plugin. It is recommended to use a reverse domain name style to ensure uniqueness.
*   **Pattern**: `^[a-zA-Z0-9_]+(\\.[a-zA-Z0-9_]+)+$` (e.g., `com.example.myplugin`)
*   **Example**: `"com.apexagent.knowledgegraph"`, `"com.apexagent.documentprocessor"`

### `version`
*   **Type**: `String`
*   **Required**: Yes
*   **Description**: The version of the plugin, following Semantic Versioning 2.0.0 (SemVer) conventions (e.g., MAJOR.MINOR.PATCH-prerelease+build).
*   **Pattern**: Matches SemVer format (e.g., `^ (0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$`).
*   **Example**: `"1.0.2"`, `"2.1.0-beta.1"`, `"0.3.0"`

### `description`
*   **Type**: `String`
*   **Required**: Yes
*   **Description**: A concise summary of the plugin's purpose and functionality. This helps users understand what the plugin does at a glance.
*   **Example**: `"Provides tools for creating, managing, and querying knowledge graphs."`

### `author`
*   **Type**: `String`
*   **Required**: Yes
*   **Description**: The name of the individual or organization that developed or maintains the plugin.
*   **Example**: `"ApexAgent Core Team"`, `"Jane Doe <jane.doe@example.com>"`

### `entry_point`
*   **Type**: `String`
*   **Required**: Yes
*   **Description**: The fully qualified Python path to the main class of the plugin. This class should typically inherit from `BasePlugin` or a similar base class provided by ApexAgent. The `PluginManager` uses this to instantiate the plugin.
*   **Example**: `"src.plugins.knowledge_graph_plugin.KnowledgeGraphPlugin"`

### `actions`
*   **Type**: Array of Objects
*   **Required**: Yes
*   **Description**: An array defining the actions (functions or methods) that the plugin exposes. Each action object has the following properties:
    *   **`name`** (String, Required): The programmatic name of the action. This is used to invoke the action.
        *   **Example**: `"create_knowledge_graph"`, `"extract_text_from_pdf"`
    *   **`description`** (String, Required): A human-readable description of what the action does.
        *   **Example**: `"Creates a new, empty knowledge graph with the specified ID."`
    *   **`parameters`** (Array of Objects, Optional): An array describing the parameters that the action accepts. Each parameter object has:
        *   **`name`** (String, Required): The name of the parameter.
        *   **`type`** (String, Required): The data type of the parameter. Allowed values: `"string"`, `"integer"`, `"boolean"`, `"number"`, `"object"`, `"array"`.
        *   **`description`** (String, Required): A description of the parameter and its purpose.
        *   **`required`** (Boolean, Default: `false`): Indicates if the parameter is mandatory for the action.
        *   **Example Parameter Object**:
            ```json
            {
              "name": "graph_id",
              "type": "string",
              "description": "The unique identifier for the graph to be created.",
              "required": true
            }
            ```
    *   **`returns`** (Object, Optional): An object describing the value returned by the action. It has:
        *   **`type`** (String, Required): The data type of the return value. Allowed values: `"string"`, `"integer"`, `"boolean"`, `"number"`, `"object"`, `"array"`, `"null"`.
        *   **`description`** (String, Required): A description of the returned value.
        *   **Example Returns Object**:
            ```json
            {
              "type": "object",
              "description": "A confirmation message and the ID of the created graph."
            }
            ```

### `dependencies`
*   **Type**: Object
*   **Required**: No (Optional)
*   **Description**: Specifies dependencies on other ApexAgent plugins and external Python libraries. If a plugin has no dependencies, this object can be omitted.
*   **Properties**:
    *   **`plugins`** (Array of Objects, Optional): A list of objects, each specifying a dependency on another ApexAgent plugin.
        *   Each plugin dependency object has:
            *   `id` (String, Required): The unique ID of the required ApexAgent plugin (e.g., "com.example.anotherplugin").
            *   `version_specifier` (String, Required): A PEP 440 version specifier string for the required plugin (e.g., ">=1.2.0", "==1.5.3", "~=1.0.0"). This is used by the `PluginManager` to select a compatible version of the dependency.
            *   `description` (String, Optional): A brief reason why this plugin is needed.
        *   **Example Plugin Dependency Object**:
            ```json
            {
              "id": "com.example.coreutilityplugin",
              "version_specifier": ">=1.2.0,<2.0.0",
              "description": "Requires core utilities for data processing, version 1.2.0 up to (but not including) 2.0.0."
            }
            ```
    *   **`python_libraries`** (Array of Objects, Optional): A list of objects, each specifying a dependency on an external Python library.
        *   Each Python library dependency object has:
            *   `name` (String, Required): The name of the Python library (e.g., "requests", "numpy").
            *   `version_specifier` (String, Optional): A PEP 440 version specifier string for the library (e.g., ">=2.25.0,<3.0.0", "~=1.3"). If omitted, any installed version is considered acceptable.
            *   `import_check_module` (String, Optional): The module name to try importing to verify installation (e.g., "bs4" for "beautifulsoup4"). Defaults to `name` if omitted.
            *   `description` (String, Optional): A brief reason why this library is needed.
        *   **Example Python Library Dependency Object**:
            ```json
            {
              "name": "requests",
              "version_specifier": ">=2.25.0,<3.0.0",
              "description": "Needed for making HTTP requests."
            }
            ```
*   **Example `dependencies` Block**:
    ```json
    "dependencies": {
      "plugins": [
        {
          "id": "com.example.coreutilityplugin",
          "version_specifier": ">=1.2.0,<2.0.0"
        }
      ],
      "python_libraries": [
        {
          "name": "requests",
          "version_specifier": ">=2.25.0"
        }
      ]
    }
    ```

### `tags`
*   **Type**: Array of Strings
*   **Required**: No (Optional)
*   **Description**: A list of keywords or tags associated with the plugin. This helps in categorizing and searching for plugins.
*   **Example**: `["knowledge management", "text processing", "ai", "data visualization"]`

### `icon`
*   **Type**: `String` (URI Reference)
*   **Required**: No (Optional)
*   **Description**: A path (relative to the plugin's root or an absolute path within the agent's known asset paths) or a full URL to an icon representing the plugin. This can be used in user interfaces.
*   **Example**: `"assets/icon.png"`, `"https://example.com/plugin_icon.svg"`

### `homepage`
*   **Type**: `String` (URI)
*   **Required**: No (Optional)
*   **Description**: A URL pointing to the plugin's official homepage, documentation, or source repository.
*   **Example**: `"https://github.com/user/my-apexagent-plugin"`

### `license`
*   **Type**: `String`
*   **Required**: No (Optional)
*   **Description**: The SPDX license identifier for the plugin's code (e.g., "MIT", "Apache-2.0"). This helps users understand the licensing terms.
*   **Example**: `"MIT"`

### `permissions_required`
*   **Type**: Array of Strings
*   **Required**: No (Optional)
*   **Description**: A list of specific system permissions or capabilities that the plugin requires to operate. This can be used by the `PluginManager` or the agent environment to grant or deny access, or to inform the user.
*   **Example**: `["file_system_read_all", "network_access_external", "execute_shell_commands"]`

### `configuration_schema`
*   **Type**: `Object` (JSON Schema)
*   **Required**: No (Optional)
*   **Description**: A JSON schema object that defines the structure and validation rules for any configuration settings that the plugin accepts. This allows for plugin-specific settings (e.g., API keys, default behaviors) to be managed and validated by the agent.
*   **Example**:
    ```json
    {
      "type": "object",
      "properties": {
        "api_key": {
          "type": "string",
          "description": "API key for accessing the external service."
        },
        "default_model": {
          "type": "string",
          "enum": ["model-a", "model-b"],
          "default": "model-a"
        }
      },
      "required": ["api_key"]
    }
    ```

### `checksum`
*   **Type**: `Object`
*   **Required**: No (Optional)
*   **Description**: An object containing checksum information for the plugin package or directory. This can be used to verify the integrity of the plugin files. The `PluginManager` might use this to ensure the plugin hasn't been tampered with.
*   **Properties**:
    *   **`algorithm`** (String, Required): The algorithm used to generate the checksum (e.g., `"sha256"`, `"md5"`).
    *   **`value`** (String, Required): The actual checksum value.
*   **Example**:
    ```json
    "checksum": {
      "algorithm": "sha256",
      "value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    ```

### `signature`
*   **Type**: `Object`
*   **Required**: No (Optional)
*   **Description**: An object containing digital signature information for the plugin package or its metadata. This helps in verifying the authenticity and integrity of the plugin, ensuring it comes from a trusted source and hasn't been altered.
*   **Properties**:
    *   **`method`** (String, Required): The signing method used (e.g., `"gpg"`, `"rsa-sha256"`).
    *   **`key_id`** (String, Optional): An identifier for the public key that can be used to verify the signature (e.g., a GPG key ID, a URL to a public key).
    *   **`value`** (String, Required): The digital signature value itself, typically base64 encoded.
*   **Example**:
    ```json
    "signature": {
      "method": "gpg",
      "key_id": "0xABC123DEF456GHI7",
      "value": "-----BEGIN PGP SIGNATURE-----\n...\n-----END PGP SIGNATURE-----"
    }
    ```

### `default_enabled`
*   **Type**: `Boolean`
*   **Required**: No (Optional)
*   **Default**: `true`
*   **Description**: A flag indicating whether the plugin should be enabled by default when it is discovered and loaded by the `PluginManager`. If `false`, the plugin will be registered but will require explicit activation by the user or system administrator. If this field is omitted, it defaults to `true`.
*   **Example**: `"default_enabled": false`

## Required Fields

The following top-level fields **must** be present in every plugin metadata file:
*   `name`
*   `id`
*   `version`
*   `description`
*   `author`
*   `entry_point`
*   `actions`

This schema provides a robust foundation for managing plugins within the ApexAgent ecosystem. Developers should ensure their plugin metadata files conform to this specification.

