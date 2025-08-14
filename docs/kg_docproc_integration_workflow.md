# Knowledge Graph and Document Processor Integration Workflow

This document outlines the workflow for integrating the `DocumentProcessor` plugin with the `KnowledgeGraphPlugin` to populate a knowledge graph using extracted entities and relations.

## 1. Overview

The primary goal is to enable ApexAgent to automatically build or augment a knowledge graph based on the content of processed documents. The `DocumentProcessor` will be responsible for extracting entities and their relationships from a given document. The `KnowledgeGraphPlugin` will then consume this structured information to create or update nodes and edges in a specified knowledge graph.

## 2. Workflow Steps

1.  **Document Processing and Extraction:**
    *   The user or an automated process initiates document processing via the `DocumentProcessor` plugin.
    *   The `DocumentProcessor.extract_entities_relations(file_path)` action is called.
    *   This action reads the document content (initially plain text, future enhancements could support various formats by leveraging other `DocumentProcessor` methods like `read_docx_text`, `extract_text_from_pdf`, etc., before passing text to an NLP pipeline).
    *   It performs entity recognition (e.g., identifying persons, organizations, locations) and relation extraction (e.g., identifying "works_at", "located_in", "is_a_competitor_of").
    *   The action returns a structured output, typically a JSON object, containing a list of identified entities and a list of identified relations. For example:
        ```json
        {
          "success": true,
          "entities": [
            {"text": "Alice Smith", "type": "PERSON", "id": "ent_person_alice_smith"},
            {"text": "Acme Corp", "type": "ORGANIZATION", "id": "ent_org_acme_corp"}
          ],
          "relations": [
            {"subject_id": "ent_person_alice_smith", "relation_type": "WORKS_AT", "object_id": "ent_org_acme_corp", "properties": {"role": "Engineer"}}
          ]
        }
        ```
        *Note: Entity IDs should be generated or normalized to ensure uniqueness and consistency within the graph. Relation properties can add more context.*

2.  **Knowledge Graph Population:**
    *   The output from `DocumentProcessor.extract_entities_relations` is passed to the `KnowledgeGraphPlugin`.
    *   A new action in `KnowledgeGraphPlugin`, such as `populate_graph_from_extracted_data(graph_id, extracted_data)`, will be responsible for this.
    *   **Node Creation/Update:**
        *   For each entity in `extracted_data.entities`:
            *   The plugin checks if a node with the given `entity.id` (or a normalized version of `entity.text` if ID is not robustly generated yet) already exists in the specified `graph_id`.
            *   If the node does not exist, it creates a new node using `KnowledgeGraphPlugin.add_node(graph_id, node_id=entity.id, node_type=entity.type, properties=entity.get("properties", {}))`. Entity text can be a primary property.
            *   If the node exists, the plugin might update its properties (e.g., add new aliases, update metadata). (Conflict resolution strategies might be needed for more advanced scenarios).
    *   **Edge Creation/Update:**
        *   For each relation in `extracted_data.relations`:
            *   The plugin ensures the subject and object nodes (identified by `relation.subject_id` and `relation.object_id`) exist in the graph (or creates them if a lenient mode is adopted, though ideally entities should be processed first).
            *   It then creates an edge (relationship) between the subject and object nodes using `KnowledgeGraphPlugin.add_edge(graph_id, source_node_id=relation.subject_id, target_node_id=relation.object_id, relationship_type=relation.relation_type, properties=relation.get("properties", {}))`. 
            *   The plugin should handle cases where the same relation might be extracted multiple times (e.g., avoid duplicate edges if properties are identical, or update properties of an existing edge).

3.  **User Feedback and Control:**
    *   The `KnowledgeGraphPlugin` should provide feedback on the population process (e.g., number of nodes/edges added or updated).
    *   Users might need options to control the population process, such as:
        *   Specifying the target graph.
        *   Dry-run mode to preview changes.
        *   Confirmation before applying changes.

## 3. Data Structures

*   **`DocumentProcessor` Output (for `extract_entities_relations`):**
    *   As defined in Step 2.1.
    *   Emphasis on clear `id` fields for entities to facilitate linking.
*   **`KnowledgeGraphPlugin` Input (for `populate_graph_from_extracted_data`):**
    *   The `graph_id` (string) specifying the target graph.
    *   The `extracted_data` (object) directly from `DocumentProcessor`.

## 4. Enhancements and Considerations

*   **Entity Disambiguation:** For robust graph building, simple text matching for entities is insufficient. Future enhancements should incorporate entity disambiguation techniques (e.g., linking "Acme Corp" to a canonical Acme Corporation entity).
*   **Relation Normalization:** Similar to entities, relation types might need normalization (e.g., "works for" and "employee of" could map to a canonical `WORKS_AT` relation).
*   **Confidence Scores:** The extraction process might yield confidence scores for entities and relations. The `KnowledgeGraphPlugin` could use these scores to filter or weight the information added to the graph.
*   **Scalability:** For large documents or many documents, the performance of both extraction and population needs to be considered. Batch processing might be necessary.
*   **Error Handling:** Robust error handling is crucial at each step (document access, extraction failures, graph update errors).
*   **Idempotency:** The population process should ideally be idempotent, meaning running it multiple times with the same input data does not produce different results or unwanted duplicates.

## 5. Next Steps (Implementation)

1.  Refine the `extract_entities_relations` method in `DocumentProcessor` to ensure it produces stable IDs and a clear structure for entities and relations.
2.  Implement the `populate_graph_from_extracted_data(graph_id, extracted_data)` action in `KnowledgeGraphPlugin.py`.
3.  Develop unit tests and integration tests for the end-to-end workflow.
4.  Create example usage scenarios.

