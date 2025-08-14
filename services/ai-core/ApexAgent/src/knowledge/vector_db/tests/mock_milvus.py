"""
Mock Milvus Client for Testing

This module provides a mock implementation of the Milvus client for testing
the Milvus adapter without requiring an actual Milvus server.
"""

import os
import json
import logging
import threading
import time
import uuid
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Set

# Define local classes instead of importing from src
class VectorDocument:
    def __init__(self, id, content, embedding, metadata=None, tenant_id=None):
        self.id = id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}
        self.tenant_id = tenant_id

class SearchResult:
    def __init__(self, document, score, metadata=None):
        self.document = document
        self.score = score
        self.metadata = metadata or {}

class QueryError(Exception):
    """Exception raised for query errors."""
    pass

class MetadataFilter:
    def __init__(self):
        self.equals = {}
        self.not_equals = {}
        self.greater_than = {}
        self.less_than = {}
        self.contains = {}

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global registry for collections to ensure singleton instances
_GLOBAL_COLLECTION_REGISTRY = {}

class MockMilvusDocumentObject:
    """Mock implementation of a Milvus document for testing."""
    
    def __init__(self, id: str, embedding: List[float], content: str, 
                 metadata_json: str, created_at: int, updated_at: int,
                 tenant_id: Optional[str] = None):
        """Initialize a mock Milvus document."""
        self.id = id
        self.embedding = embedding
        self.content = content
        self.metadata_json = metadata_json
        self.created_at = created_at
        self.updated_at = updated_at
        self.tenant_id = tenant_id
        
        # Parse metadata_json if it's a string
        if isinstance(metadata_json, str):
            try:
                self.metadata = json.loads(metadata_json)
            except json.JSONDecodeError:
                self.metadata = {}
        else:
            self.metadata = metadata_json or {}

class MockMilvusCollectionObject:
    """Mock implementation of a Milvus collection for testing."""
    
    def __init__(self, name: str, schema=None, using: str = None, **kwargs):
        """Initialize a mock Milvus collection."""
        self.name = name
        self.schema = schema
        self.using = using
        self.dimension = 128  # Default dimension
        
        # Extract dimension from schema if provided
        if schema and hasattr(schema, 'fields'):
            for field in schema.fields:
                if hasattr(field, 'dim') and field.dim is not None:
                    self.dimension = field.dim
                    break
        
        self.description = kwargs.get('description', '')
        self.documents = {}  # id -> document object
        self.lock = threading.RLock()
        self.has_index = False
        self.index_params = None
        self.loaded = False
        
        # Register collection in global registry
        _GLOBAL_COLLECTION_REGISTRY[name] = self
        mock_utility.collections[name] = self
        
        logger.info(f"Created collection {name} with dimension {self.dimension}")
        logger.info(f"Global registry now contains: {list(_GLOBAL_COLLECTION_REGISTRY.keys())}")
    
    def insert(self, data: List[List[Any]]) -> Dict[str, Any]:
        """Insert data into the collection."""
        with self.lock:
            ids = data[0]
            embeddings = data[1]
            contents = data[2]
            metadata_jsons = data[3]
            created_ats = data[4]
            updated_ats = data[5]
            
            logger.debug(f"[INSERT] Collection: {self.name}, Inserting document IDs: {ids}")
            
            for i, doc_id in enumerate(ids):
                # Create document object with attribute access
                self.documents[doc_id] = MockMilvusDocumentObject(
                    id=doc_id,
                    embedding=embeddings[i],
                    content=contents[i],
                    metadata_json=metadata_jsons[i],
                    created_at=created_ats[i],
                    updated_at=updated_ats[i]
                )
                logger.debug(f"[INSERT] Added document with ID: '{doc_id}' to collection {self.name}")
            
            logger.info(f"Inserted {len(ids)} documents into collection {self.name}. Total documents: {len(self.documents)}")
            logger.info(f"Document IDs in collection {self.name}: {list(self.documents.keys())}")
            return {"insert_count": len(ids)}
    
    def delete(self, expr: str) -> Dict[str, Any]:
        """Delete documents matching the expression."""
        with self.lock:
            logger.debug(f"[DELETE] Collection: {self.name}, Expression: '{expr}'")
            logger.debug(f"[DELETE] Current document IDs: {list(self.documents.keys())}")
            
            # Simple expression parsing for testing
            if expr.startswith("id == "):
                # Extract ID from "id == 'doc_id'" or "id == \"doc_id\""
                if "'" in expr:
                    doc_id = expr.split("'")[1]
                elif '"' in expr:
                    doc_id = expr.split('"')[1]
                else:
                    doc_id = expr[6:].strip()
                
                logger.debug(f"[DELETE] Extracted document ID: '{doc_id}'")
                
                if doc_id in self.documents:
                    del self.documents[doc_id]
                    logger.info(f"Deleted document '{doc_id}' from collection {self.name}")
                    return {"delete_count": 1}
                else:
                    logger.info(f"Document '{doc_id}' not found in collection {self.name} for deletion")
            
            return {"delete_count": 0}
    
    def query(self, expr: str = None, output_fields: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """Query documents matching the expression."""
        with self.lock:
            results = []
            
            logger.debug(f"[QUERY] Collection: {self.name}, Expression: '{expr}'")
            logger.debug(f"[QUERY] Output fields: {output_fields}")
            logger.debug(f"[QUERY] Collection {self.name} has documents: {list(self.documents.keys())}")
            
            # If no expression, return all documents
            if not expr:
                for doc_id, doc in self.documents.items():
                    result = {}
                    for field in output_fields:
                        result[field] = getattr(doc, field, None)
                    results.append(result)
                return results
            
            # Simple expression parsing for testing
            if expr.startswith("id == "):
                # Extract ID from "id == 'doc_id'" or "id == \"doc_id\""
                if "'" in expr:
                    doc_id = expr.split("'")[1]
                elif '"' in expr:
                    doc_id = expr.split('"')[1]
                else:
                    doc_id = expr[6:].strip()
                
                logger.debug(f"[QUERY] Extracted document ID: '{doc_id}'")
                
                if doc_id in self.documents:
                    doc = self.documents[doc_id]
                    result = {}
                    for field in output_fields:
                        result[field] = getattr(doc, field, None)
                    results.append(result)
                    logger.info(f"Found document '{doc_id}' in collection {self.name}")
                else:
                    logger.info(f"Document '{doc_id}' not found in collection {self.name}")
                    logger.debug(f"[QUERY] Available document IDs: {list(self.documents.keys())}")
            
            return results
    
    def search(self, data: List[List[float]], anns_field: str, param: Dict[str, Any],
              limit: int, expr: str = None, output_fields: List[str] = None, **kwargs) -> List[List[Dict[str, Any]]]:
        """Search for similar vectors."""
        with self.lock:
            query_vector = np.array(data[0])
            results = []
            hits = []
            
            logger.debug(f"[SEARCH] Collection: {self.name}, Expression: '{expr}'")
            logger.debug(f"[SEARCH] Collection {self.name} has documents: {list(self.documents.keys())}")
            
            # Calculate distances for all documents
            distances = []
            doc_ids = []
            
            for doc_id, doc in self.documents.items():
                embedding = np.array(doc.embedding)
                distance = np.linalg.norm(query_vector - embedding)
                distances.append(distance)
                doc_ids.append(doc_id)
            
            # Sort by distance
            sorted_indices = np.argsort(distances)
            
            # Get top k results
            for i in range(min(limit, len(sorted_indices))):
                idx = sorted_indices[i]
                doc_id = doc_ids[idx]
                distance = distances[idx]
                doc = self.documents[doc_id]
                
                # Create entity dictionary with attribute access
                entity = {}
                for field in output_fields:
                    entity[field] = getattr(doc, field, None)
                
                # Create hit object
                hit = MockMilvusHit(
                    id=doc_id,
                    distance=distance,
                    entity=entity
                )
                hits.append(hit)
            
            results.append(hits)
            return results
    
    def get_stats(self) -> List[Dict[str, str]]:
        """Get collection statistics."""
        with self.lock:
            return [
                {"key": "row_count", "value": str(len(self.documents))},
                {"key": "data_size", "value": "0"}
            ]
    
    def load(self) -> None:
        """Load the collection into memory."""
        with self.lock:
            self.loaded = True
    
    def release(self) -> None:
        """Release the collection from memory."""
        with self.lock:
            self.loaded = False
    
    def create_index(self, field_name: str, index_params: Dict[str, Any]) -> None:
        """Create an index on the specified field."""
        with self.lock:
            self.has_index = True
            self.index_params = index_params
    
    def drop_index(self) -> None:
        """Drop the index."""
        with self.lock:
            self.has_index = False
            self.index_params = None
    
    def has_index(self) -> bool:
        """Check if the collection has an index."""
        with self.lock:
            return self.has_index
    
    def index(self) -> List[Any]:
        """Get index information."""
        with self.lock:
            if not self.has_index:
                return []
            
            return [MockMilvusIndex(field_name="embedding", index_params=self.index_params)]
    
    def flush(self) -> Dict[str, Any]:
        """Flush the collection."""
        return {"flush_count": len(self.documents)}
    
    def compact(self) -> Dict[str, Any]:
        """Compact the collection."""
        return {"compact_count": len(self.documents)}


class MockMilvusHit:
    """Mock implementation of a Milvus search hit."""
    
    def __init__(self, id: str, distance: float, entity: Dict[str, Any]):
        """Initialize a mock Milvus hit."""
        self.id = id
        self.distance = distance
        self.entity = entity


class MockMilvusIndex:
    """Mock implementation of a Milvus index."""
    
    def __init__(self, field_name: str, index_params: Dict[str, Any]):
        """Initialize a mock Milvus index."""
        self.field_name = field_name
        self.params = index_params


class MockMilvusConnections:
    """Mock implementation of Milvus connections."""
    
    def __init__(self):
        """Initialize mock Milvus connections."""
        self.connections = {}
    
    def connect(self, alias: str, host: str, port: str, user: str = "", password: str = "", **kwargs) -> Dict[str, Any]:
        """Connect to a mock Milvus server."""
        self.connections[alias] = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "connected": True
        }
        return {"status": "connected"}
    
    def disconnect(self, alias: str) -> Dict[str, Any]:
        """Disconnect from a mock Milvus server."""
        if alias in self.connections:
            self.connections[alias]["connected"] = False
            return {"status": "disconnected"}
        return {"status": "not_connected"}
    
    def has_connection(self, alias: str) -> bool:
        """Check if a connection exists."""
        return alias in self.connections and self.connections[alias]["connected"]
    
    def list_connections(self) -> List[str]:
        """List all connections."""
        return [alias for alias, conn in self.connections.items() if conn["connected"]]
    
    def get_connection_addr(self, alias: str) -> Dict[str, Any]:
        """Get connection address."""
        if alias in self.connections:
            conn = self.connections[alias]
            return {
                "host": conn["host"],
                "port": conn["port"]
            }
        return {}


class MockMilvusUtility:
    """Mock implementation of Milvus utility functions."""
    
    def __init__(self):
        """Initialize mock Milvus utility."""
        self.collections = {}
    
    def has_collection(self, collection_name: str, using: str = None) -> bool:
        """Check if a collection exists."""
        exists = collection_name in self.collections or collection_name in _GLOBAL_COLLECTION_REGISTRY
        logger.info(f"Checking if collection {collection_name} exists: {exists}")
        return exists
    
    def list_collections(self, using: str = None) -> List[str]:
        """List all collections."""
        # Use the global registry for consistent collection listing
        collections = list(_GLOBAL_COLLECTION_REGISTRY.keys())
        logger.info(f"Listing collections: {collections}")
        return collections
    
    def drop_collection(self, collection_name: str, using: str = None) -> bool:
        """Drop a collection."""
        if collection_name in _GLOBAL_COLLECTION_REGISTRY:
            del _GLOBAL_COLLECTION_REGISTRY[collection_name]
            if collection_name in self.collections:
                del self.collections[collection_name]
            logger.info(f"Dropped collection {collection_name}")
            return True
        logger.info(f"Collection {collection_name} not found for dropping")
        return False
    
    def get_collection_stats(self, collection_name: str, using: str = None) -> Dict[str, Any]:
        """Get collection statistics."""
        if collection_name in _GLOBAL_COLLECTION_REGISTRY:
            collection = _GLOBAL_COLLECTION_REGISTRY[collection_name]
            return {
                "row_count": len(collection.documents),
                "data_size": 0
            }
        return {}


# Create global mock objects
mock_connections = MockMilvusConnections()
mock_utility = MockMilvusUtility()


# Mock Milvus client for testing
class MockMilvusClient:
    """Mock implementation of a Milvus client for testing."""
    
    def __init__(self):
        """Initialize a mock Milvus client."""
        self.collections = {}
    
    def create_collection(self, collection_name: str, dimension: int, 
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new collection."""
        if collection_name in self.collections:
            logger.warning(f"Collection {collection_name} already exists")
            return False
        
        # Create collection object with attribute access
        self.collections[collection_name] = MockMilvusCollectionObject(
            name=collection_name,
            dimension=dimension
        )
        
        logger.info(f"Created collection {collection_name} with dimension {dimension}")
        return True
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        if collection_name in self.collections:
            del self.collections[collection_name]
            logger.info(f"Deleted collection {collection_name}")
            
            # Also remove from global registry
            if collection_name in _GLOBAL_COLLECTION_REGISTRY:
                del _GLOBAL_COLLECTION_REGISTRY[collection_name]
            
            return True
        
        logger.warning(f"Collection {collection_name} does not exist")
        return False
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        exists = collection_name in self.collections or collection_name in _GLOBAL_COLLECTION_REGISTRY
        logger.info(f"Checking if collection {collection_name} exists: {exists}")
        return exists
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information."""
        if collection_name in self.collections:
            collection = self.collections[collection_name]
            return {
                "name": collection_name,
                "dimension": collection.dimension,
                "document_count": len(collection.documents),
                "description": collection.description
            }
        
        if collection_name in _GLOBAL_COLLECTION_REGISTRY:
            collection = _GLOBAL_COLLECTION_REGISTRY[collection_name]
            return {
                "name": collection_name,
                "dimension": collection.dimension,
                "document_count": len(collection.documents),
                "description": collection.description
            }
        
        logger.warning(f"Collection {collection_name} does not exist")
        return {}
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        # Use the global registry for consistent collection listing
        collections = list(_GLOBAL_COLLECTION_REGISTRY.keys())
        logger.info(f"Listing collections: {collections}")
        return collections
    
    def insert_document(self, collection_name: str, document: VectorDocument) -> bool:
        """Insert a document into a collection."""
        if collection_name not in self.collections and collection_name not in _GLOBAL_COLLECTION_REGISTRY:
            logger.warning(f"Collection {collection_name} does not exist")
            return False
        
        # Get collection from registry or local collections
        collection = self.collections.get(collection_name, _GLOBAL_COLLECTION_REGISTRY.get(collection_name))
        
        if not collection:
            logger.warning(f"Collection {collection_name} not found in registry")
            return False
        
        # Convert metadata to JSON string
        metadata_json = json.dumps(document.metadata) if document.metadata else "{}"
        
        # Get current time
        current_time = int(time.time())
        
        # Insert document
        collection.insert([
            [document.id],  # id
            [document.embedding.tolist() if hasattr(document.embedding, 'tolist') else document.embedding],  # embedding
            [document.content],  # content
            [metadata_json],  # metadata_json
            [current_time],  # created_at
            [current_time]   # updated_at
        ])
        
        logger.info(f"Inserted document {document.id} into collection {collection_name}")
        return True
    
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document from a collection."""
        if collection_name not in self.collections and collection_name not in _GLOBAL_COLLECTION_REGISTRY:
            logger.warning(f"Collection {collection_name} does not exist")
            return False
        
        # Get collection from registry or local collections
        collection = self.collections.get(collection_name, _GLOBAL_COLLECTION_REGISTRY.get(collection_name))
        
        if not collection:
            logger.warning(f"Collection {collection_name} not found in registry")
            return False
        
        # Delete document
        expr = f'id == "{document_id}"'
        result = collection.delete(expr)
        
        logger.info(f"Deleted document {document_id} from collection {collection_name}")
        return result["delete_count"] > 0
    
    def search(self, collection_name: str, query_vector: np.ndarray,
              limit: int = 10, filter: Optional[MetadataFilter] = None) -> List[SearchResult]:
        """Search for similar vectors in a collection."""
        if collection_name not in self.collections and collection_name not in _GLOBAL_COLLECTION_REGISTRY:
            logger.warning(f"Collection {collection_name} does not exist")
            return []
        
        # Get collection from registry or local collections
        collection = self.collections.get(collection_name, _GLOBAL_COLLECTION_REGISTRY.get(collection_name))
        
        if not collection:
            logger.warning(f"Collection {collection_name} not found in registry")
            return []
        
        # Convert filter to expression if provided
        expr = None
        if filter:
            # Simple implementation for testing
            if filter.equals:
                conditions = []
                for key, value in filter.equals.items():
                    if isinstance(value, str):
                        conditions.append(f'metadata_json like "%{key}%:{value}%"')
                    else:
                        conditions.append(f'metadata_json like "%{key}%:{value}%"')
                
                if conditions:
                    expr = " and ".join(conditions)
        
        # Perform search
        search_results = collection.search(
            data=[query_vector.tolist() if hasattr(query_vector, 'tolist') else query_vector],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"ef": 64}},
            limit=limit,
            expr=expr,
            output_fields=["id", "content", "metadata_json", "created_at", "updated_at"]
        )
        
        # Convert to SearchResult objects
        results = []
        for hits in search_results:
            for hit in hits:
                # Get document data
                doc_id = hit.id
                distance = hit.distance
                entity = hit.entity
                
                # Parse metadata JSON
                metadata_json = entity.get("metadata_json", "{}")
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    metadata = {}
                
                # Convert distance to similarity score (1.0 - normalized distance)
                # Assuming dimension is 128 for testing
                dimension = 128
                max_distance = np.sqrt(dimension)  # Maximum possible L2 distance
                similarity = 1.0 - (distance / max_distance)
                
                # Create document
                document = VectorDocument(
                    id=doc_id,
                    content=entity.get("content", ""),
                    embedding=query_vector,  # Use query vector as placeholder
                    metadata=metadata
                )
                
                # Create search result
                result = SearchResult(
                    document=document,
                    score=similarity,
                    metadata={
                        "distance": distance,
                        "similarity": similarity
                    }
                )
                
                results.append(result)
        
        return results
