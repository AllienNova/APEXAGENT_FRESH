import asyncio
import os
import sys
import logging

# Add project root to Python path to allow importing modules from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.plugins.document_processor import DocumentProcessor
from src.plugins.knowledge_graph_plugin import KnowledgeGraphPlugin

# Setup basic logging for the test script
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def main():
    # 0. Setup - Create a sample document for testing
    sample_doc_content = "Dr. Alice Smith works at Acme Corp. Bob Johnson is a consultant for Zeta Inc. Acme Corp is located in New York. Zeta Inc. is a competitor of Acme Corp."
    sample_doc_path = "/home/ubuntu/test_integration_sample_doc.txt"
    with open(sample_doc_path, "w", encoding="utf-8") as f:
        f.write(sample_doc_content)
    logger.info(f"Sample document created at: {sample_doc_path}")

    # 1. Instantiate Plugins
    doc_processor = DocumentProcessor()
    kg_plugin = KnowledgeGraphPlugin()
    graph_id = "integration_test_graph_v2"
    empty_graph_id = "empty_test_graph_for_viz"
    non_existent_graph_id = "this_graph_does_not_exist"
    error_test_graph_id = "error_test_graph" # Define for clarity

    logger.info("--- Test Case 1: Full successful workflow (Extraction, Population, Query, Visualization) ---")
    # 1.1 Extract Entities and Relations
    extraction_result = doc_processor.extract_entities_relations(file_path=sample_doc_path)
    if not extraction_result or not extraction_result.get("success"):
        logger.error(f"Test Case 1 FAILED: Error extracting entities/relations: {extraction_result.get(	'error	', 	'Unknown error	')}")
        return
    logger.info(f"Extraction successful. Entities: {extraction_result.get(	'entities	')}, Relations: {extraction_result.get(	'relations	')}")
    extracted_data = {
        "entities": extraction_result.get("entities", []),
        "relations": extraction_result.get("relations", [])
    }

    # 1.2 Create and Populate Knowledge Graph
    await kg_plugin.execute_action("create_knowledge_graph", {"graph_id": graph_id})
    population_params = {"graph_id": graph_id, "extracted_data": extracted_data}
    population_result = await kg_plugin.execute_action("populate_graph_from_extracted_data", population_params)
    logger.info(f"Population Result: {population_result}")
    if not population_result or not population_result.get("success"):
        logger.error(f"Test Case 1 FAILED: Error populating graph: {population_result.get(	'error	', 	'Unknown error	')}")
        return

    # 1.3 Verify by Querying
    alice_node_query = {"graph_id": graph_id, "query_type": "get_node", "node_id": "alice_smith"}
    alice_node_result = await kg_plugin.execute_action("query_knowledge_graph", alice_node_query)
    logger.info(f"Query for Alice Smith	's node: {alice_node_result}")
    assert alice_node_result.get("success"), "Alice Smith node query failed"

    alice_edges_query = {"graph_id": graph_id, "query_type": "get_edges", "node_id": "alice_smith"}
    alice_edges_result = await kg_plugin.execute_action("query_knowledge_graph", alice_edges_query)
    logger.info(f"Query for Alice Smith	's outgoing edges: {alice_edges_result}")
    assert alice_edges_result.get("success"), "Alice Smith edges query failed"
    found_works_at = any(edge.get("target") == "acme_corp" and edge.get("relation") == "EMPLOYED_BY" for edge in alice_edges_result.get("edges", []))
    assert found_works_at, "Verification FAILED: Alice Smith WORKS_AT Acme Corp edge NOT found."
    logger.info("Verified: Alice Smith WORKS_AT Acme Corp edge found.")

    # 1.4 Visualize Graph
    logger.info("--- Testing Graph Visualization ---")
    viz_params = {"graph_id": graph_id}
    viz_result = await kg_plugin.execute_action("visualize_graph", viz_params)
    logger.info(f"Visualization Result: {viz_result}")
    assert viz_result.get("success"), "Graph visualization failed"
    assert viz_result.get("image_path") and os.path.exists(viz_result.get("image_path")), "Visualization image file not created or path missing"
    logger.info(f"Visualization successful. Image saved at: {viz_result.get(	'image_path	')}")

    # 1.5 Save the graph
    save_result = await kg_plugin.execute_action("save_graph_to_file", {"graph_id": graph_id})
    logger.info(f"Save graph result: {save_result}")
    assert save_result.get("success"), "Saving graph failed"

    logger.info("--- Test Case 1 PASSED ---")

    logger.info("\n--- Test Case 2: Error Handling Scenarios ---")
    # 2.1 Query non-existent graph
    query_non_existent_params = {"graph_id": non_existent_graph_id, "query_type": "get_node", "node_id": "any_node"}
    err_res_1 = await kg_plugin.execute_action("query_knowledge_graph", query_non_existent_params)
    logger.info(f"Query non-existent graph result: {err_res_1}")
    assert not err_res_1.get("success") and "not found" in err_res_1.get("error", "").lower(), "Error handling for query on non-existent graph failed"

    # 2.2 Visualize non-existent graph
    viz_non_existent_params = {"graph_id": non_existent_graph_id}
    err_res_2 = await kg_plugin.execute_action("visualize_graph", viz_non_existent_params)
    logger.info(f"Visualize non-existent graph result: {err_res_2}")
    assert not err_res_2.get("success") and "not found" in err_res_2.get("error", "").lower(), "Error handling for visualize non-existent graph failed"

    # 2.3 Visualize empty graph
    await kg_plugin.execute_action("create_knowledge_graph", {"graph_id": empty_graph_id})
    viz_empty_params = {"graph_id": empty_graph_id}
    err_res_3 = await kg_plugin.execute_action("visualize_graph", viz_empty_params)
    logger.info(f"Visualize empty graph result: {err_res_3}")
    assert not err_res_3.get("success") and "empty" in err_res_3.get("error", "").lower(), "Error handling for visualize empty graph failed"

    # 2.4 Add edge with non-existent source node
    await kg_plugin.execute_action("create_knowledge_graph", {"graph_id": error_test_graph_id})
    await kg_plugin.execute_action("add_node", {"graph_id": error_test_graph_id, "node_id": "target_node_for_error"})
    # Ensure graph is saved to disk so it can be loaded if not in memory for the add_edge call
    save_error_graph_result = await kg_plugin.execute_action("save_graph_to_file", {"graph_id": error_test_graph_id})
    logger.info(f"Save result for {error_test_graph_id}: {save_error_graph_result}")
    assert save_error_graph_result.get("success"), f"Failed to save {error_test_graph_id} before testing add_edge error"

    add_edge_err_params = {
        "graph_id": error_test_graph_id, 
        "source_node_id": "non_existent_source", 
        "target_node_id": "target_node_for_error", 
        "relationship_type": "LINKS_TO"
    }
    err_res_4 = await kg_plugin.execute_action("add_edge", add_edge_err_params)
    logger.info(f"Add edge with non-existent source node result: {err_res_4}")
    assert not err_res_4.get("success") and "source node" in err_res_4.get("error", "").lower() and "not found" in err_res_4.get("error", "").lower(), "Error handling for add edge with non-existent source failed"
    
    # 2.5 Populate with invalid data (e.g., entities not a list)
    populate_invalid_data_params = {"graph_id": graph_id, "extracted_data": {"entities": "not_a_list", "relations": []}}
    err_res_5 = await kg_plugin.execute_action("populate_graph_from_extracted_data", populate_invalid_data_params)
    logger.info(f"Populate with invalid data (entities not a list) result: {err_res_5}")
    assert not err_res_5.get("success") and "must contain" in err_res_5.get("error", "").lower() and "as lists" in err_res_5.get("error", "").lower(), "Error handling for populate with invalid entities type failed"

    logger.info("--- Test Case 2 PASSED (Error Handling Scenarios) ---")

    # Cleanup
    if os.path.exists(sample_doc_path):
        os.remove(sample_doc_path)
        logger.info(f"Cleaned up sample document: {sample_doc_path}")
    
    files_to_remove = [
        os.path.join(kg_plugin.default_graph_dir, f"{graph_id}.graphml"),
        os.path.join(kg_plugin.default_graph_dir, f"{empty_graph_id}.graphml"),
        os.path.join(kg_plugin.default_graph_dir, f"{error_test_graph_id}.graphml"),
    ]
    # Add the dynamically created image path if it exists
    if viz_result and viz_result.get("success") and viz_result.get("image_path") and os.path.exists(viz_result.get("image_path")):
        # files_to_remove.append(viz_result.get("image_path")) # Temporarily commented out to preserve for report
        pass # Added pass to fix IndentationError
    else: # Default path if dynamic one failed or not created but test might have created default
        default_image_path = os.path.join(kg_plugin.visualization_dir, f"{graph_id}_visualization.png")
        if os.path.exists(default_image_path):
             files_to_remove.append(default_image_path)

    for f_path in files_to_remove:
        if os.path.exists(f_path):
            try:
                os.remove(f_path)
                logger.info(f"Cleaned up: {f_path}")
            except OSError as e:
                logger.warning(f"Could not remove {f_path}: {e}")

    kg_plugin.shutdown()
    logger.info("--- All Test Cases Completed ---")

if __name__ == "__main__":
    asyncio.run(main())

