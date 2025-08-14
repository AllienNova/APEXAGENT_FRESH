# ApexAgent - Master Todo Checklist

This checklist is derived from the `comprehensive_implementation_plan.md` and reflects the current project status.

## Foundational Architectural Enhancements

### 1. Core Plugin Architecture Refinement

#### 1.1. Plugin Registry and Discovery System

- [x] **Step 1.1.1: Design Detailed Plugin Metadata Schema**
    - [x] Define a JSON schema (or Pydantic model) for `plugin_metadata.json` files.
    - [x] Schema to include: `name`, `version`, `author`, `description`, `dependencies`, `actions`.
    - [x] Each action object to include: `action_name`, `description`, `parameters`, `return_type`.
    - [x] Incorporate API versioning fields for the plugin itself and potentially for individual actions.
    - [x] Reference insights from Manus `tools.json` for detail and clarity.
    - [x] **Deliverable:** `plugin_metadata_schema.json` (or Python Pydantic models), documentation for the schema.

- [x] **Step 1.1.2: Implement Auto-Discovery in `PluginManager`**
    - [x] Modify `PluginManager` to scan a designated `plugins` directory for `plugin_metadata.json` files.
    - [x] For each metadata file found, validate it against the schema from Step 1.1.1.
    - [x] Load and register valid plugins, making their actions available.
    - [x] Implement error handling for invalid metadata or plugin loading failures.
    - [x] **Deliverable:** Updated `PluginManager.py`, unit tests for plugin discovery and registration, error reporting for failed loads.

- [ ] **Step 1.1.3 (as per original plan doc): Implement API Versioning Support** (Note: We implemented Plugin Loading/Execution as our effective 1.1.3; this item from the plan is pending)
    - [ ] Modify `PluginManager` and the base plugin class to store and utilize version information from metadata.
    - [ ] Develop a strategy for how the agent/LLM requests a specific version of a plugin or action if multiple are available (or defaults to latest).
    - [ ] Ensure graceful handling if a requested version is not found.
    - [ ] **Deliverable:** Updated `PluginManager.py` and base plugin class, documentation on versioning strategy and usage.

#### 1.2. Enhanced Plugin Interface (`BaseEnhancedPlugin`)

- [ ] **Step 1.2.1: Design and Implement `BaseEnhancedPlugin`**
    - [x] Create a new `BasePlugin.py` (Note: Plan said `BaseEnhancedPlugin.py` or refactor `BaseToolPlugin.py`. We created `BasePlugin.py` as part of the loading framework, so this is partially complete).
    - [ ] Incorporate robust error handling: define custom plugin exceptions, establish patterns for argument validation within plugin actions, guide plugins to report errors clearly.
    - [ ] **Deliverable:** `BaseEnhancedPlugin.py` (or updated `BasePlugin.py`) with core structure and error handling framework.

- [x] **Step 1.2.2: Implement Asynchronous Execution and Progress Reporting**
    - [x] Add `async` support for action methods in `BaseEnhancedPlugin` for long-running tasks.
    - [x] Design and implement a mechanism for plugins to report progress.
    - [x] **Deliverable:** `BaseEnhancedPlugin.py` with async action support and progress reporting. Example plugin demonstrating async usage.

- [x] **Step 1.2.3: Implement Stream-Based Output Handling**
    - [x] Enable actions in `BaseEnhancedPlugin` to return data as a stream.
    - [x] Update `PluginManager` to handle streamed outputs.
    - [x] **Deliverable:** `BaseEnhancedPlugin.py` and `PluginManager.py` updated for streamed outputs. Example plugin demonstrating streamed output.

- [x] **Step 1.2.4: Implement Plugin State Persistence**
    - [x] Add methods to `BaseEnhancedPlugin` for plugins to request saving and loading of their internal state.
    - [x] Implement functionality in `PluginManager` to manage the storage and retrieval of this state.
    - [x] Ensure security considerations for persisted state.
    - [x] **Deliverable:** `BaseEnhancedPlugin.py` and `PluginManager.py` with state persistence. Documentation on usage and security.

#### 1.3. Dependency Resolution System

- [x] **Step 1.3.1: Enhance Metadata for Dependency Declaration**
    - [x] Ensure the `plugin_metadata_schema.json` has a well-defined section for declaring dependencies on:
        - [x] Other ApexAgent plugins (with optional version constraints).
        - [x] External Python libraries (with optional version constraints).
    - [x] **Deliverable:** Updated `plugin_metadata_schema.json`.

- [x] **Step 1.3.2: Implement Dependency Checking in `PluginManager`**
    - [x] During plugin loading, `PluginManager` reads dependency declarations.
    - [x] For plugin dependencies: check if the required plugin (and version) is already registered or available for loading.
    - [x] For library dependencies: check if the library (and version) is importable/available in the Python environment.
    - [x] Report clear errors if dependencies are not met.
    - [x] **Deliverable:** `PluginManager.py` with dependency checking logic. Comprehensive error reporting.

### 2. API Key Management Enhancements

#### 2.1. Harden Encryption at Rest for `ApiKeyManager`

- [x] **Step 2.1.1: Review Current `ApiKeyManager` Storage**
    - [x] Analyze the existing mechanism in `ApiKeyManager.py`.
    - [x] Identify current encryption methods and potential weaknesses.
    - [x] **Deliverable:** Internal review document/notes.

- [x] **Step 2.1.2: Implement Stronger Encryption**
    - [x] Select a robust encryption library (PyNaCl/libsodium).
    - [x] Implement a secure method for deriving/managing the encryption key.
    - [x] Update `ApiKeyManager.py` with hierarchical key management.
    - [x] Create a migration path for existing encrypted keys.
    - [x] **Deliverable:** Enhanced `ApiKeyManager.py`, documentation, security considerations, and migration steps.

- [x] **Step 2.1.3: Implement Secure Storage for Master Key**
    - [x] Move master key from environment variables to system keyring.
    - [x] Implement fallback mechanisms for headless environments.
    - [x] **Deliverable:** Updated `ApiKeyManager.py` with secure key storage.

- [x] **Step 2.1.4: Add Access Control and Audit Logging**
    - [x] Implement plugin-level permissions for credential access.
    - [x] Add comprehensive audit logging of all credential access.
    - [x] **Deliverable:** Enhanced `ApiKeyManager.py` with access control features.

- [x] **Step 2.1.5: Implement Key Rotation**
    - [x] Support rotating all levels of keys (master, KEK, DEK).
    - [x] Add configurable rotation intervals and status checking.
    - [x] **Deliverable:** Enhanced `ApiKeyManager.py` with key rotation capabilities.

- [x] **Step 2.1.6: Validate Security Enhancements**
    - [x] Develop comprehensive validation tests.
    - [x] Ensure backward compatibility with existing encrypted data.
    - [x] Test fallback mechanisms for different environments.
    - [x] **Deliverable:** Validation script and test results.

### 3. Document Processing and Knowledge Management

#### 3.1. Document Understanding Plugin (Further Enhancements)

- [ ] **Step 3.1.1: Implement Semantic Search within Documents**
    - [ ] Research and select libraries for sentence embeddings and vector similarity search.
    - [ ] Modify `DocumentProcessor` to generate and store embeddings.
    - [ ] Add a new action `search_document_semantically(document_path, query_text, top_k_results)`.
    - [ ] **Deliverable:** Updated `DocumentProcessor.py` with semantic search action, example usage, documentation.

- [ ] **Step 3.1.2: Implement Semantic Search across Multiple Documents**
    - [ ] Design a strategy for managing a collection of processed documents and their embeddings.
    - [ ] Add new actions like `add_document_to_search_index(document_path)` and `search_collection_semantically(query_text, top_k_results)`.
    - [ ] **Deliverable:** Enhancements to `DocumentProcessor` or a new `KnowledgeBaseManager` plugin, indexing mechanism, cross-document search action.

- [ ] **Step 3.1.3: Design Document Version Tracking (Conceptual)**
    - [ ] Research approaches for version tracking.
    - [ ] Define how `DocumentProcessor` or other plugins would interact with versioned documents.
    - [ ] **Deliverable:** Design document outlining version tracking strategies.

#### 3.2. Knowledge Graph Plugin

- [x] **Step 3.2.1: Research Knowledge Graph Technologies** (Partially done)
    - [ ] Explore Python libraries for creating and managing knowledge graphs.
    - [ ] Investigate techniques for extracting entities and relationships from text.
    - [ ] **Deliverable:** Research summary and technology selection report.

- [x] **Step 3.2.2: Design `KnowledgeGraphPlugin` Core Functionality** (Partially done)
    - [ ] Define actions for the plugin (create, add_node, add_edge, query, visualize).
    - [ ] **Deliverable:** Detailed design specification for `KnowledgeGraphPlugin.py`.

- [x] **Step 3.2.3: Implement `KnowledgeGraphPlugin` (Initial Version)** (Partially done)
    - [ ] Implement the core actions using selected libraries.
    - [ ] Focus on basic node/edge creation and simple querying.
    - [ ] **Deliverable:** `KnowledgeGraphPlugin.py` implementation, unit tests, example usage.

- [x] **Step 3.2.4: Integrate with `DocumentProcessor` for Entity/Relation Extraction**
    - [x] Develop a workflow where `DocumentProcessor` can extract entities and potential relationships.
    - [x] Add an action to `DocumentProcessor` like `extract_entities_relations(text)`.
    - [x] `KnowledgeGraphPlugin` can then use this output to populate a graph.
    - [x] **Deliverable:** Enhanced `DocumentProcessor` or new methods in `KnowledgeGraphPlugin`, integration workflow example.

### 4. Plugin Loading and Execution Framework (Completed as effective Step 1.1.3)
(Note: This section is numbered as '4. Step 1.1.3' in the source plan, but corresponds to the work we just completed)

- [x] **Step 4.1 (was 001): Design Plugin Loading Mechanism**
    - [x] Outline Core Design Considerations (Execution Context, Dependency Management, Resource Allocation, Security).
    - [x] Update Implementation Plan Document.
- [x] **Step 4.2 (was 002): Define Standard Plugin Interface/Base Class**
    - [x] Design Plugin Interface (`initialize`, `execute_action`, `get_actions`, `shutdown`).
    - [x] Create Base Class (`BasePlugin.py`).
    - [x] Document the Interface.
- [x] **Step 4.3 (was 003): Implement Core Plugin Loading Logic**
    - [x] Enhance `PluginManager` (dynamic import, instantiation, instance management).
    - [x] Integrate with Execution Context Design.
- [x] **Step 4.4 (was 004): Implement Action Invocation Mechanism**
    - [x] Develop Action Dispatcher in `PluginManager`.
    - [x] Define Parameter Passing and Result Handling.
    - [x] Define Contextual Information availability.
- [x] **Step 4.5 (was 005): Implement Error Handling for Loading and Execution**
    - [x] Handle Loading Errors (module not found, class not found, instantiation errors).
    - [x] Handle Execution Errors (exceptions from plugin actions, prevent agent crash).
    - [x] Ensure Clear Logging and Reporting.
- [x] **(Implicit Step, was 006): Update Documentation and Tests for Plugin Loading**
    - [x] Update Main Plan document.
    - [x] Create Developer Documentation (`plugin_developer_guide.md`).
    - [x] Ensure comprehensive Unit and Integration Tests.

### 5. Stream-Based Output and Metadata Enhancements

- [x] **Step 5.1: Enhance PluginManager with Stream Discovery**
    - [x] Add streaming_actions dictionary to store metadata about streaming-capable actions
    - [x] Modify discovery process to extract and store streaming metadata
    - [x] Implement version-aware handling of streaming metadata
    - [x] **Deliverable:** Enhanced PluginManager.py with streaming discovery capabilities

- [x] **Step 5.2: Implement Stream Capability Query Methods**
    - [x] Add methods to query which plugins and actions support streaming
    - [x] Implement metadata retrieval for streaming actions
    - [x] Add filtering by capabilities and content types
    - [x] **Deliverable:** PluginManager.py with comprehensive query methods

- [x] **Step 5.3: Develop Comprehensive Unit Tests**
    - [x] Create test suite for streaming discovery and metadata
    - [x] Test version handling and error cases
    - [x] Validate filtering and capability detection
    - [x] **Deliverable:** test_plugin_manager_streaming.py with comprehensive test cases

### 6. Plugin Marketplace (Conceptual Design)

- [ ] **Step 6.1 (was 4.1.1): Define Scope and Goals of Plugin Marketplace**
    - [ ] Clarify objectives.
    - [ ] **Deliverable:** Scope document.

- [ ] **Step 6.2 (was 4.1.2): Research Existing Plugin Marketplace Architectures**
    - [ ] Look at examples.
    - [ ] Identify common features.
    - [ ] **Deliverable:** Research summary.

- [ ] **Step 6.3 (was 4.1.3): Design Core Marketplace Infrastructure (Conceptual)**
    - [ ] Outline components (web interface, backend API, packaging, metadata).
    - [ ] Consider security implications.
    - [ ] **Deliverable:** High-level architectural design document.

### 7. LLM Provider Expansion

#### 7.1. AWS Bedrock Provider

- [ ] **Step 7.1.1 (was 5.1.1): Research AWS Bedrock API and SDK**
    - [ ] Understand authentication, models, API endpoints, SDK.
    - [ ] **Deliverable:** Research notes.

- [ ] **Step 7.1.2 (was 5.1.2): Design `BedrockProvider` Plugin**
    - [ ] Define configuration parameters.
    - [ ] Implement methods adhering to `BaseLlmProvider` interface.
    - [ ] Handle API errors and rate limits.
    - [ ] **Deliverable:** Design specification.

- [ ] **Step 7.1.3 (was 5.1.3): Implement and Test `BedrockProvider`**
    - [ ] Write Python code using `boto3`.
    - [ ] Integrate with `ApiKeyManager`.
    - [ ] Create test scripts.
    - [ ] **Deliverable:** `BedrockProvider.py`, test scripts, documentation.

#### 7.2. Azure OpenAI Service Provider

- [ ] **Step 7.2.1 (was 5.2.1): Research Azure OpenAI Service API and SDK**
    - [ ] Understand authentication, deployment types, API endpoints, SDK.
    - [ ] **Deliverable:** Research notes.

- [ ] **Step 7.2.2 (was 5.2.2): Design `AzureOpenAIProvider` Plugin**
    - [ ] Define configuration parameters.
    - [ ] Implement methods compatible with `BaseLlmProvider`.
    - [ ] **Deliverable:** Design specification.

- [ ] **Step 7.2.3 (was 5.2.3): Implement and Test `AzureOpenAIProvider`**
    - [ ] Write Python code.
    - [ ] Integrate with `ApiKeyManager`.
    - [ ] Create test scripts.
    - [ ] **Deliverable:** `AzureOpenAIProvider.py`, test scripts, documentation.
