# ApexAgent Plugin: Knowledge Graph Manager

import os
import networkx as nx
import json
import matplotlib
matplotlib.use("Agg") # Use Agg backend for non-interactive plotting
import matplotlib.pyplot as plt
import logging # For more detailed logging

# Setup basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # Configure as needed

# Placeholder for BaseEnhancedPlugin if not available or for initial development
class BaseEnhancedPlugin:
    def __init__(self, agent_config=None, plugin_manager=None, api_key_manager=None):
        self.agent_config = agent_config
        self.plugin_manager = plugin_manager
        self.api_key_manager = api_key_manager
        logger.info(f"{self.__class__.__name__} initialized.")

    def get_metadata(self):
        return {
            "name": self.PLUGIN_NAME,
            "version": self.PLUGIN_VERSION,
            "description": self.PLUGIN_DESCRIPTION,
            "author": self.PLUGIN_AUTHOR,
            "actions": self.get_actions_metadata()
        }

    def get_actions_metadata(self):
        return []

    async def execute_action(self, action_name: str, parameters: dict):
        raise NotImplementedError("Subclasses must implement execute_action")

class KnowledgeGraphPlugin(BaseEnhancedPlugin):
    PLUGIN_NAME = "knowledge_graph_manager"
    PLUGIN_VERSION = "0.1.14" # Incremented for fixing None vs Falsey check in _save_graph
    PLUGIN_DESCRIPTION = "Manages, populates, and visualizes knowledge graphs. Fixed None vs Falsey check in _save_graph."
    PLUGIN_AUTHOR = "ApexAgent Team"

    def __init__(self, agent_config=None, plugin_manager=None, api_key_manager=None):
        super().__init__(agent_config, plugin_manager, api_key_manager)
        self.graphs = {} 
        self.default_graph_dir = os.path.join(os.path.expanduser("~"), "apex_agent_knowledge_graphs")
        self.visualization_dir = os.path.join(self.default_graph_dir, "visualizations")
        try:
            os.makedirs(self.default_graph_dir, exist_ok=True)
            os.makedirs(self.visualization_dir, exist_ok=True)
            logger.info(f"Knowledge graph directories ensured: {self.default_graph_dir}, {self.visualization_dir}")
        except OSError as e:
            logger.error(f"Error creating plugin directories: {e}")

    def _get_graph(self, graph_id: str, create_if_not_exists: bool = True) -> nx.MultiDiGraph | None:
        logger.info(f"_get_graph[ID:{id(self)}] called for graph_id: 	'{graph_id}'	, create_if_not_exists: {create_if_not_exists}. Current self.graphs keys: {list(self.graphs.keys())}")
        if graph_id in self.graphs:
            logger.info(f"_get_graph[ID:{id(self)}]: Graph 	'{graph_id}'	 found in self.graphs (in-memory cache). Returning instance {id(self.graphs[graph_id])}.")
            return self.graphs[graph_id]
        
        file_path = os.path.join(self.default_graph_dir, f"{graph_id}.graphml")
        logger.info(f"_get_graph[ID:{id(self)}]: Checking for graph file at: {file_path}")
        if os.path.exists(file_path):
            try:
                loaded_graph = nx.read_graphml(file_path)
                self.graphs[graph_id] = loaded_graph # Cache it
                logger.info(f"_get_graph[ID:{id(self)}]: Loaded graph 	'{graph_id}'	 from {file_path}. Cached instance {id(loaded_graph)}.")
                return loaded_graph
            except Exception as e:
                logger.error(f"_get_graph[ID:{id(self)}]: Error loading graph {graph_id} from {file_path}: {e}. Overwriting with new graph if create_if_not_exists is True.")
                if create_if_not_exists:
                    new_graph = nx.MultiDiGraph()
                    self.graphs[graph_id] = new_graph
                    logger.info(f"_get_graph[ID:{id(self)}]: Created new graph 	'{graph_id}'	 in memory (instance {id(new_graph)}) due to load error.")
                    return new_graph
                return None
        elif create_if_not_exists:
            new_graph = nx.MultiDiGraph()
            self.graphs[graph_id] = new_graph
            logger.info(f"_get_graph[ID:{id(self)}]: Created new in-memory graph: {graph_id} (instance {id(new_graph)}) because file did not exist and create_if_not_exists is True.")
            return new_graph
        else:
            logger.warning(f"_get_graph[ID:{id(self)}]: Graph 	'{graph_id}'	 not found in memory or on disk, and create_if_not_exists is False.")
            return None

    def _save_graph(self, graph_id: str) -> dict:
        logger.info(f"_save_graph[ID:{id(self)}] called for graph_id: '{graph_id}'. Current self.graphs keys: {list(self.graphs.keys())}")
        
        graph_to_save = None
        if graph_id in self.graphs:
            graph_to_save = self.graphs[graph_id]
            logger.info(f"_save_graph[ID:{id(self)}]: Graph '{graph_id}' (instance {id(graph_to_save)}) found by DIRECT KEY CHECK in self.graphs (in-memory cache) for saving. Type before check: {type(graph_to_save)}, Is None: {graph_to_save is None}")
        else:
            logger.info(f"_save_graph[ID:{id(self)}]: Graph '{graph_id}' NOT found by direct key check in self.graphs. Will attempt to load from disk.")
            graph_to_save = self._get_graph(graph_id, create_if_not_exists=False)
            if graph_to_save is not None: # Check if graph was loaded or is an empty graph object
                logger.info(f"_save_graph[ID:{id(self)}]: Graph '{graph_id}' (instance {id(graph_to_save)}) successfully loaded/retrieved from disk for saving. Type before check: {type(graph_to_save)}, Is None: {graph_to_save is None}")
            else:
                logger.warning(f"_save_graph[ID:{id(self)}]: Graph '{graph_id}' still not found after attempting disk load. Cannot save. graph_to_save is None: {graph_to_save is None}")

        # Corrected check: Use 'is None' to differentiate from empty but valid graph objects
        logger.info(f"_save_graph[ID:{id(self)}]: About to check 'if graph_to_save is None'. graph_to_save is None: {graph_to_save is None}. Type: {type(graph_to_save)}")
        if graph_to_save is None:
            logger.error(f"_save_graph[ID:{id(self)}]: Condition 'graph_to_save is None' is TRUE. graph_to_save is None: {graph_to_save is None}. Type: {type(graph_to_save)}. Returning 'not found' error.")
            return {"success": False, "error": f"Graph '{graph_id}' not found, cannot save."}
        else:
            logger.info(f"_save_graph[ID:{id(self)}]: Condition 'graph_to_save is None' is FALSE. Proceeding to actual save attempt. graph_to_save type: {type(graph_to_save)}")
        
        logger.info(f"_save_graph[ID:{id(self)}]: DIAGNOSTIC (post-check): Graph object type: {type(graph_to_save)}, Nodes: {graph_to_save.number_of_nodes()}, Edges: {graph_to_save.number_of_edges()}")

        file_path = os.path.join(self.default_graph_dir, f"{graph_id}.graphml")
        logger.info(f"_save_graph[ID:{id(self)}]: Attempting to save graph '{graph_id}' (instance {id(graph_to_save)}) to file: {file_path}")
        try:
            nx.write_graphml(graph_to_save, file_path)
            logger.info(f"_save_graph[ID:{id(self)}]: Successfully saved graph '{graph_id}' to {file_path}. Nodes: {graph_to_save.number_of_nodes()}, Edges: {graph_to_save.number_of_edges()}")
            return {"success": True, "message": f"Graph '{graph_id}' saved successfully to {file_path}."}
        except nx.NetworkXError as nxe:
            error_msg = f"_save_graph[ID:{id(self)}]: NetworkX specific error saving graph '{graph_id}' to {file_path}: {nxe}"
            logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"_save_graph[ID:{id(self)}]: General error saving graph '{graph_id}' to {file_path}: {e}"
            logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}

    def get_actions_metadata(self):
        return [
            {
                "action_name": "create_knowledge_graph",
                "description": "Creates a new, empty knowledge graph or loads an existing one. Auto-saves after creation.",
                "parameters": [
                    {"name": "graph_id", "type": "string", "required": True, "description": "Unique identifier for the knowledge graph."}
                ]
            },
            {
                "action_name": "add_node",
                "description": "Adds or updates a node in a specified knowledge graph. Auto-saves after modification.",
                "parameters": [
                    {"name": "graph_id", "type": "string", "required": True, "description": "Identifier of the target knowledge graph."},
                    {"name": "node_id", "type": "string", "required": True, "description": "Unique identifier for the node."},
                    {"name": "node_type", "type": "string", "required": False, "description": "Type of the node (e.g., PERSON, ORGANIZATION). Defaults to 'Unknown'."},
                    {"name": "properties", "type": "object", "required": False, "description": "Key-value pairs of additional properties for the node. 'label' property will be used for display."}
                ]
            },
            {
                "action_name": "add_edge",
                "description": "Adds a directed edge (relationship) between two nodes. Auto-saves after modification.",
                "parameters": [
                    {"name": "graph_id", "type": "string", "required": True, "description": "Identifier of the target knowledge graph."},
                    {"name": "source_node_id", "type": "string", "required": True, "description": "Identifier of the source node."},
                    {"name": "target_node_id", "type": "string", "required": True, "description": "Identifier of the target node."},
                    {"name": "relationship_type", "type": "string", "required": True, "description": "Type of the relationship (e.g., WORKS_AT, LOCATED_IN). Used as edge key."},
                    {"name": "properties", "type": "object", "required": False, "description": "Key-value pairs of additional properties for the edge."}
                ]
            },
            {
                "action_name": "populate_graph_from_extracted_data",
                "description": "Populates a knowledge graph using entities and relations. Auto-saves after population.",
                "parameters": [
                    {"name": "graph_id", "type": "string", "required": True, "description": "Identifier of the target knowledge graph."},
                    {"name": "extracted_data", "type": "object", "required": True, "description": "Structured data containing 'entities' and 'relations' lists."}
                ]
            },
            {
                "action_name": "query_knowledge_graph",
                "description": "Queries a knowledge graph for nodes, edges, or neighbors.",
                "parameters": [
                    {"name": "graph_id", "type": "string", "required": True, "description": "Identifier of the knowledge graph to query."},
                    {"name": "query_type", "type": "string", "required": True, "enum": ["get_node", "get_edges", "get_neighbors"], "description": "Type of query."},
                    {"name": "node_id", "type": "string", "required": False, "description": "Node ID required for 'get_node', 'get_edges', 'get_neighbors'."}
                ]
            },
            {
                "action_name": "save_graph_to_file",
                "description": "Saves the specified knowledge graph to a GraphML file.",
                "parameters": [
                    {"name": "graph_id", "type": "string", "required": True, "description": "Identifier of the knowledge graph to save."}
                ]
            },
            {
                "action_name": "visualize_graph",
                "description": "Generates a visualization of the specified knowledge graph and saves it as a PNG image.",
                "parameters": [
                    {"name": "graph_id", "type": "string", "required": True, "description": "Identifier of the knowledge graph to visualize."},
                    {"name": "save_path", "type": "string", "required": False, "description": "Optional. Absolute path to save the image (e.g., /path/to/graph.png). Defaults to a path in the plugin's visualization directory."}
                ]
            }
        ]

    async def execute_action(self, action_name: str, parameters: dict):
        graph_id = parameters.get("graph_id")
        if not graph_id:
             return {"success": False, "error": "Parameter 'graph_id' is required for this action."}

        try:
            if action_name == "create_knowledge_graph":
                graph = self._get_graph(graph_id, create_if_not_exists=True)
                if graph is None: # Check for None explicitly
                    return {"success": False, "error": f"Failed to create or load graph '{graph_id}'."}
                save_res = self._save_graph(graph_id)
                if not save_res.get("success"):
                    logger.warning(f"Auto-save after create_knowledge_graph for '{graph_id}' failed: {save_res.get('error')}")
                return {"success": True, "message": f"Knowledge graph '{graph_id}' ensured (created or loaded)."}
            
            if action_name == "save_graph_to_file":
                return self._save_graph(graph_id) 

            can_create_graph_for_action = (action_name == "populate_graph_from_extracted_data")
            graph = self._get_graph(graph_id, create_if_not_exists=can_create_graph_for_action)

            if graph is None: # Check for None explicitly
                 return {"success": False, "error": f"Knowledge graph '{graph_id}' not found and action '{action_name}' does not create it. Please create it first or ensure it can be loaded."}

            if action_name == "add_node":
                node_id = parameters.get("node_id")
                if not node_id:
                    return {"success": False, "error": "Parameter 'node_id' is required for adding a node."}
                node_type = parameters.get("node_type", "Unknown")
                properties = parameters.get("properties", {})
                serializable_props = {k: str(v) for k, v in properties.items()} if properties else {}
                serializable_props["label"] = properties.get("label", node_id)
                serializable_props["entity_type"] = node_type
                
                action_type = "updated" if graph.has_node(node_id) else "added"
                graph.add_node(node_id, **serializable_props)
                save_res = self._save_graph(graph_id)
                if not save_res.get("success"):
                    logger.warning(f"Auto-save after add_node for '{graph_id}' failed: {save_res.get('error')}")
                return {"success": True, "message": f"Node '{node_id}' {action_type} in graph '{graph_id}'."}

            elif action_name == "add_edge":
                source_node_id = parameters.get("source_node_id")
                target_node_id = parameters.get("target_node_id")
                relationship_type = parameters.get("relationship_type")
                if not all([source_node_id, target_node_id, relationship_type]):
                    return {"success": False, "error": "Parameters 'source_node_id', 'target_node_id', and 'relationship_type' are required."}
                
                if not graph.has_node(source_node_id):
                    return {"success": False, "error": f"Source node '{source_node_id}' not found in graph '{graph_id}'. Cannot add edge."}
                if not graph.has_node(target_node_id):
                    return {"success": False, "error": f"Target node '{target_node_id}' not found in graph '{graph_id}'. Cannot add edge."}
                
                properties = parameters.get("properties", {})
                serializable_props = {k: str(v) for k, v in properties.items()} if properties else {}
                graph.add_edge(source_node_id, target_node_id, key=relationship_type, **serializable_props, relation=relationship_type)
                save_res = self._save_graph(graph_id)
                if not save_res.get("success"):
                    logger.warning(f"Auto-save after add_edge for '{graph_id}' failed: {save_res.get('error')}")
                return {"success": True, "message": f"Edge '{relationship_type}' added between '{source_node_id}' and '{target_node_id}' in graph '{graph_id}'."}

            elif action_name == "populate_graph_from_extracted_data":
                extracted_data = parameters.get("extracted_data")
                if not extracted_data or not isinstance(extracted_data, dict):
                    return {"success": False, "error": "Parameter 'extracted_data' (object with entities and relations) is required."}
                
                entities = extracted_data.get("entities", [])
                relations = extracted_data.get("relations", [])
                if not isinstance(entities, list) or not isinstance(relations, list):
                    return {"success": False, "error": "'extracted_data' must contain 'entities' and 'relations' as lists."}

                nodes_processed = 0
                edges_added = 0
                for entity in entities:
                    if not isinstance(entity, dict):
                        logger.warning(f"Skipping invalid entity item (not a dict): {entity}")
                        continue
                    node_id = entity.get("id") or entity.get("text")
                    if not node_id:
                        logger.warning(f"Skipping entity due to missing 'id' or 'text': {entity}")
                        continue
                    node_type = entity.get("type", "Unknown")
                    node_props = entity.get("properties", {})
                    node_props["label"] = entity.get("text", node_id)
                    serializable_node_props = {k: str(v) for k, v in node_props.items()} if node_props else {}
                    serializable_node_props["entity_type"] = node_type
                    graph.add_node(node_id, **serializable_node_props)
                    nodes_processed += 1
                
                for relation in relations:
                    if not isinstance(relation, dict):
                        logger.warning(f"Skipping invalid relation item (not a dict): {relation}")
                        continue
                    subject_id = relation.get("subject_id")
                    object_id = relation.get("object_id")
                    relation_type = relation.get("relation_type") or relation.get("relation")
                    if not all([subject_id, object_id, relation_type]):
                        logger.warning(f"Skipping relation due to missing fields (subject_id, object_id, or relation_type): {relation}")
                        continue
                    if graph.has_node(subject_id) and graph.has_node(object_id):
                        edge_props = relation.get("properties", {})
                        serializable_edge_props = {k: str(v) for k, v in edge_props.items()} if edge_props else {}
                        graph.add_edge(subject_id, object_id, key=relation_type, **serializable_edge_props, relation=relation_type)
                        edges_added += 1
                    else:
                        logger.warning(f"Skipping edge due to missing subject ('{subject_id}') or object ('{object_id}') node in graph '{graph_id}'.")
                
                save_res = self._save_graph(graph_id)
                if not save_res.get("success"):
                    logger.warning(f"Auto-save after populate_graph_from_extracted_data for '{graph_id}' failed: {save_res.get('error')}")
                return {"success": True, "message": f"Graph '{graph_id}' populated. Nodes processed/updated: {nodes_processed} (total: {graph.number_of_nodes()}), Edges added: {edges_added} (total: {graph.number_of_edges()})."}

            elif action_name == "query_knowledge_graph":
                query_type = parameters.get("query_type")
                node_id_param = parameters.get("node_id")

                if not query_type:
                    return {"success": False, "error": "Parameter 'query_type' is required."}
                if query_type in ["get_node", "get_edges", "get_neighbors"] and not node_id_param:
                     return {"success": False, "error": f"Parameter 'node_id' is required for query type '{query_type}'."}

                if query_type == "get_node":
                    if not graph.has_node(node_id_param):
                        return {"success": False, "error": f"Node '{node_id_param}' not found in graph '{graph_id}'."}
                    return {"success": True, "node_data": graph.nodes[node_id_param]}
                elif query_type == "get_edges":
                    if not graph.has_node(node_id_param):
                        return {"success": False, "error": f"Node '{node_id_param}' not found for edge query in graph '{graph_id}'."}
                    edges_data = []
                    for u, v, data in graph.edges(node_id_param, data=True):
                        edges_data.append({"source": u, "target": v, "relation": data.get("relation", data.get("key")), "properties": data})
                    return {"success": True, "edges": edges_data, "message": f"Found {len(edges_data)} outgoing edges for node '{node_id_param}' in graph '{graph_id}'."}
                elif query_type == "get_neighbors":
                    if not graph.has_node(node_id_param):
                        return {"success": False, "error": f"Node '{node_id_param}' not found for neighbor query in graph '{graph_id}'."}
                    neighbors = list(nx.neighbors(graph, node_id_param))
                    return {"success": True, "neighbors": neighbors, "message": f"Found {len(neighbors)} neighbors for node '{node_id_param}' in graph '{graph_id}'."}
                else:
                    return {"success": False, "error": f"Unsupported 'query_type': '{query_type}'. Supported types are 'get_node', 'get_edges', 'get_neighbors'."}
            
            elif action_name == "visualize_graph":
                if graph.number_of_nodes() == 0:
                    return {"success": False, "error": f"Graph '{graph_id}' is empty. Cannot visualize an empty graph."}
                
                save_path_param = parameters.get("save_path")
                image_path = save_path_param or os.path.join(self.visualization_dir, f"{graph_id}_visualization.png")
                
                try:
                    img_dir = os.path.dirname(image_path)
                    if img_dir:
                        os.makedirs(img_dir, exist_ok=True)

                    plt.figure(figsize=(14, 12))
                    pos = nx.kamada_kawai_layout(graph) if graph.number_of_nodes() < 100 else nx.spring_layout(graph, k=0.5, iterations=30)
                    
                    node_labels = {node: data.get("label", node) for node, data in graph.nodes(data=True)}
                    nx.draw_networkx_nodes(graph, pos, node_size=2500, node_color="lightblue", alpha=0.9, linewidths=0.5, edgecolors="black")
                    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=8, font_weight="bold")
                    
                    edge_labels = {(u, v): data.get("relation", data.get("key", "")) for u, v, data in graph.edges(data=True)}
                    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), arrowstyle="->", arrowsize=15, edge_color="grey", alpha=0.6, width=1.5)
                    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=7, font_color="darkred", bbox={"alpha":0.1, "color":"white"})
                    
                    plt.title(f"Knowledge Graph Visualization: {graph_id}", fontsize=16)
                    plt.axis("off")
                    plt.tight_layout()
                    plt.savefig(image_path, format="png", dpi=200)
                    plt.close()
                    logger.info(f"Graph '{graph_id}' visualized and saved to {image_path}")
                    return {"success": True, "message": f"Graph '{graph_id}' visualized successfully and saved to {image_path}.", "image_path": image_path}
                except Exception as e:
                    error_msg = f"Error during graph visualization for '{graph_id}': {e}"
                    logger.error(error_msg, exc_info=True)
                    return {"success": False, "error": error_msg, "image_path": None}

            else:
                return {"success": False, "error": f"Action '{action_name}' is not supported by KnowledgeGraphPlugin."}

        except Exception as e:
            logger.error(f"Unexpected error executing action '{action_name}' for graph '{graph_id}': {e}", exc_info=True)
            return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

    def shutdown(self):
        logger.info("KnowledgeGraphPlugin shutting down. Saving all in-memory graphs.")
        for graph_id_key in list(self.graphs.keys()): # Use list() for safe iteration if keys change
            save_result = self._save_graph(graph_id_key)
            if not save_result["success"]:
                logger.error(f"Failed to save graph '{graph_id_key}' during shutdown: {save_result['error']}")
        logger.info("KnowledgeGraphPlugin shutdown complete.")

if __name__ == "__main__":
    import asyncio
    plugin = KnowledgeGraphPlugin()
    
    async def test_full_workflow_enhanced():
        graph_id = "enhanced_test_graph"
        logger.info(f"--- Testing Full Workflow (Enhanced) for Graph: {graph_id} ---")
        
        logger.info(await plugin.execute_action("create_knowledge_graph", {"graph_id": graph_id}))
        
        simulated_extracted_data = {
            "entities": [
                {"id": "person_001", "text": "Dr. Evelyn Reed", "type": "PERSON", "properties": {"specialty": "AI Research"}},
                {"id": "org_alpha", "text": "Alpha Innovations", "type": "ORGANIZATION"},
                {"id": "project_x", "text": "Project Chimera", "type": "PROJECT"}
            ],
            "relations": [
                {"subject_id": "person_001", "relation_type": "WORKS_FOR", "object_id": "org_alpha", "properties": {"role": "Chief Scientist"}},
                {"subject_id": "person_001", "relation_type": "LEADS", "object_id": "project_x"},
                {"subject_id": "org_alpha", "relation_type": "FUNDS", "object_id": "project_x"}
            ]
        }
        
        logger.info(await plugin.execute_action("populate_graph_from_extracted_data", 
                                       {"graph_id": graph_id, "extracted_data": simulated_extracted_data}))
        
        logger.info(await plugin.execute_action("query_knowledge_graph", 
                                       {"graph_id": graph_id, "query_type": "get_node", "node_id": "person_001"}))
        
        logger.info(await plugin.execute_action("query_knowledge_graph", 
                                       {"graph_id": graph_id, "query_type": "get_edges", "node_id": "org_alpha"}))
        
        viz_result = await plugin.execute_action("visualize_graph", {"graph_id": graph_id})
        logger.info(viz_result)
        if viz_result.get("success"):
            logger.info(f"Visualization saved to: {viz_result.get('image_path')}")

        logger.info("--- Testing visualization of non-existent graph ---")
        non_existent_graph_id = "non_existent_graph_for_viz"
        viz_error_result = await plugin.execute_action("visualize_graph", {"graph_id": non_existent_graph_id})
        logger.info(viz_error_result)

        logger.info("--- Testing query of non-existent node ---")
        query_error_result = await plugin.execute_action("query_knowledge_graph", 
                                       {"graph_id": graph_id, "query_type": "get_node", "node_id": "non_existent_node"})
        logger.info(query_error_result)

        # Explicit save_graph_to_file is still available if needed, but auto-save should handle most cases.
        # logger.info(await plugin.execute_action("save_graph_to_file", {"graph_id": graph_id}))
        
        plugin.shutdown()

    asyncio.run(test_full_workflow_enhanced())

