"""
FAISS Adapter for Aideon AI Lite Vector Database

This module provides a concrete implementation of the VectorDatabaseAdapter
interface using FAISS (Facebook AI Similarity Search) as the backend.

FAISS is a library for efficient similarity search and clustering of dense vectors.
It contains algorithms that search in sets of vectors of any size, up to ones that
possibly do not fit in RAM. It also contains supporting code for evaluation and
parameter tuning.

Production-ready features:
- Thread-safe operations
- Efficient batch processing
- Comprehensive error handling
- Performance optimizations
- Multi-tenant isolation
"""

import os
import json
import logging
import threading
import numpy as np
import faiss
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union, cast
from pathlib import Path

from ..vector_database import (
    VectorDatabaseAdapter,
    VectorDocument,
    SearchResult,
    MetadataFilter,
    ConnectionError,
    QueryError,
    IndexError,
    DocumentError,
    CollectionError,
    EmbeddingError,
)

logger = logging.getLogger(__name__)


class FAISSAdapter(VectorDatabaseAdapter[np.ndarray]):
    """
    FAISS implementation of the VectorDatabaseAdapter interface.
    
    This adapter uses FAISS for efficient similarity search and clustering
    of dense vectors, with support for multi-tenant isolation and comprehensive
    error handling.
    """
    
    def __init__(self, 
                 storage_path: Optional[str] = None,
                 index_type: str = "Flat",
                 metric_type: str = "L2"):
        """
        Initialize the FAISS adapter.
        
        Args:
            storage_path: Path to store FAISS indices and metadata.
                          If None, uses a temporary directory.
            index_type: Type of FAISS index to use (e.g., "Flat", "IVF", "HNSW").
            metric_type: Distance metric to use ("L2" or "IP" for inner product).
        """
        self.storage_path = storage_path or os.path.join(os.getcwd(), "faiss_storage")
        self.index_type = index_type
        self.metric_type = metric_type
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Dictionary to store FAISS indices in memory
        self.indices: Dict[str, faiss.Index] = {}
        
        # Dictionary to store document metadata
        self.metadata: Dict[str, Dict[str, Dict[str, Any]]] = {}
        
        # Lock for thread safety
        self.lock = threading.RLock()
        
        # Connection status
        self._connected = False
    
    def connect(self, connection_params: Dict[str, Any]) -> bool:
        """
        Connect to the FAISS database.
        
        For FAISS, this primarily involves setting up the storage directory
        and loading any existing indices.
        
        Args:
            connection_params: Connection parameters.
                storage_path: Optional override for storage path.
                
        Returns:
            True if connection was successful, False otherwise.
            
        Raises:
            ConnectionError: If connection fails.
        """
        try:
            # Update storage path if provided
            if "storage_path" in connection_params:
                self.storage_path = connection_params["storage_path"]
                os.makedirs(self.storage_path, exist_ok=True)
            
            # Load existing indices
            self._load_indices()
            
            self._connected = True
            logger.info(f"Connected to FAISS database at {self.storage_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to FAISS database: {str(e)}")
            raise ConnectionError(f"Failed to connect to FAISS database: {str(e)}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from the FAISS database.
        
        For FAISS, this involves saving all indices to disk and clearing
        in-memory data structures.
        
        Returns:
            True if disconnection was successful, False otherwise.
        """
        if not self._connected:
            return True
        
        try:
            # Save all indices to disk
            self._save_indices()
            
            # Clear in-memory data structures
            with self.lock:
                self.indices.clear()
                self.metadata.clear()
            
            self._connected = False
            logger.info("Disconnected from FAISS database")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect from FAISS database: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if connected to the FAISS database.
        
        Returns:
            True if connected, False otherwise.
        """
        return self._connected
    
    def create_collection(self, name: str, dimension: int, 
                         metadata: Optional[Dict[str, Any]] = None,
                         tenant_id: Optional[str] = None) -> bool:
        """
        Create a new collection in the FAISS database.
        
        Args:
            name: The name of the collection.
            dimension: The dimension of vectors in the collection.
            metadata: Optional metadata for the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if collection was created successfully, False otherwise.
            
        Raises:
            CollectionError: If collection creation fails.
        """
        self._ensure_connected()
        
        try:
            with self.lock:
                # Check if collection already exists
                if self._collection_exists_internal(name, tenant_id):
                    logger.warning(f"Collection {name} already exists")
                    return False
                
                # Create FAISS index
                if self.metric_type == "L2":
                    index = faiss.IndexFlatL2(dimension)
                elif self.metric_type == "IP":
                    index = faiss.IndexFlatIP(dimension)
                else:
                    raise CollectionError(f"Unsupported metric type: {self.metric_type}")
                
                # Store index in memory
                collection_key = self._get_collection_key(name, tenant_id)
                self.indices[collection_key] = index
                
                # Initialize metadata storage for this collection
                self.metadata[collection_key] = {}
                
                # Store collection metadata
                collection_metadata = metadata or {}
                collection_metadata.update({
                    "dimension": dimension,
                    "created_at": datetime.utcnow().isoformat(),
                    "index_type": self.index_type,
                    "metric_type": self.metric_type,
                    "document_count": 0,
                })
                
                if tenant_id:
                    collection_metadata["tenant_id"] = tenant_id
                
                # Save collection metadata
                self._save_collection_metadata(collection_key, collection_metadata)
                
                # Save index to disk
                self._save_index(collection_key)
                
                logger.info(f"Created collection {name} with dimension {dimension}")
                return True
        except Exception as e:
            logger.error(f"Failed to create collection {name}: {str(e)}")
            raise CollectionError(f"Failed to create collection {name}: {str(e)}")
    
    def delete_collection(self, name: str, 
                         tenant_id: Optional[str] = None) -> bool:
        """
        Delete a collection from the FAISS database.
        
        Args:
            name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if collection was deleted successfully, False otherwise.
            
        Raises:
            CollectionError: If collection deletion fails.
        """
        self._ensure_connected()
        
        try:
            with self.lock:
                collection_key = self._get_collection_key(name, tenant_id)
                
                # Check if collection exists
                if not self._collection_exists_internal(name, tenant_id):
                    logger.warning(f"Collection {name} does not exist")
                    return False
                
                # Remove index from memory
                if collection_key in self.indices:
                    del self.indices[collection_key]
                
                # Remove metadata from memory
                if collection_key in self.metadata:
                    del self.metadata[collection_key]
                
                # Remove files from disk
                index_path = os.path.join(self.storage_path, f"{collection_key}.index")
                metadata_path = os.path.join(self.storage_path, f"{collection_key}.metadata.json")
                documents_path = os.path.join(self.storage_path, f"{collection_key}.documents.json")
                
                if os.path.exists(index_path):
                    os.remove(index_path)
                
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                
                if os.path.exists(documents_path):
                    os.remove(documents_path)
                
                logger.info(f"Deleted collection {name}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete collection {name}: {str(e)}")
            raise CollectionError(f"Failed to delete collection {name}: {str(e)}")
    
    def list_collections(self, tenant_id: Optional[str] = None) -> List[str]:
        """
        List all collections in the FAISS database.
        
        Args:
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of collection names.
            
        Raises:
            CollectionError: If listing collections fails.
        """
        self._ensure_connected()
        
        try:
            collections = []
            
            # List all metadata files in the storage directory
            for filename in os.listdir(self.storage_path):
                if filename.endswith(".metadata.json"):
                    collection_key = filename.replace(".metadata.json", "")
                    
                    # If tenant_id is provided, filter collections by tenant
                    if tenant_id:
                        tenant_prefix = f"{tenant_id}_"
                        if collection_key.startswith(tenant_prefix):
                            # Remove tenant prefix
                            collection_name = collection_key[len(tenant_prefix):]
                            collections.append(collection_name)
                    else:
                        # If no tenant filtering, include all collections
                        # but strip tenant prefix if present
                        parts = collection_key.split("_", 1)
                        if len(parts) > 1:
                            collections.append(parts[1])
                        else:
                            collections.append(collection_key)
            
            return collections
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise CollectionError(f"Failed to list collections: {str(e)}")
    
    def collection_exists(self, name: str, 
                         tenant_id: Optional[str] = None) -> bool:
        """
        Check if a collection exists in the FAISS database.
        
        Args:
            name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if collection exists, False otherwise.
        """
        self._ensure_connected()
        
        try:
            return self._collection_exists_internal(name, tenant_id)
        except Exception as e:
            logger.error(f"Failed to check if collection {name} exists: {str(e)}")
            return False
    
    def get_collection_info(self, name: str, 
                           tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A dictionary containing collection information.
            
        Raises:
            CollectionError: If getting collection information fails.
        """
        self._ensure_connected()
        
        try:
            collection_key = self._get_collection_key(name, tenant_id)
            
            # Check if collection exists
            if not self._collection_exists_internal(name, tenant_id):
                raise CollectionError(f"Collection {name} does not exist")
            
            # Load collection metadata
            metadata_path = os.path.join(self.storage_path, f"{collection_key}.metadata.json")
            
            if not os.path.exists(metadata_path):
                raise CollectionError(f"Metadata for collection {name} not found")
            
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            # Add current document count
            if collection_key in self.indices:
                metadata["document_count"] = self.indices[collection_key].ntotal
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to get information for collection {name}: {str(e)}")
            raise CollectionError(f"Failed to get information for collection {name}: {str(e)}")
    
    def insert_document(self, collection_name: str, document: VectorDocument[np.ndarray],
                       tenant_id: Optional[str] = None) -> str:
        """
        Insert a document into a collection.
        
        Args:
            collection_name: The name of the collection.
            document: The document to insert.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            The ID of the inserted document.
            
        Raises:
            DocumentError: If document insertion fails.
        """
        self._ensure_connected()
        
        try:
            with self.lock:
                collection_key = self._get_collection_key(collection_name, tenant_id)
                
                # Check if collection exists
                if not self._collection_exists_internal(collection_name, tenant_id):
                    raise DocumentError(f"Collection {collection_name} does not exist")
                
                # Ensure document has an embedding
                if document.embedding is None:
                    raise DocumentError("Document must have an embedding")
                
                # Ensure embedding is a numpy array
                embedding = np.array(document.embedding).astype(np.float32)
                
                # Reshape embedding to ensure it's 2D (required by FAISS)
                if embedding.ndim == 1:
                    embedding = embedding.reshape(1, -1)
                
                # Get index
                index = self._get_index(collection_key)
                
                # Add embedding to index
                index.add(embedding)
                
                # Get FAISS ID (index of the added vector)
                faiss_id = index.ntotal - 1
                
                # Load document metadata if not already loaded
                if collection_key not in self.metadata:
                    self.metadata[collection_key] = {}
                
                # Store document metadata
                self.metadata[collection_key][document.id] = {
                    "content": document.content,
                    "metadata": document.metadata,
                    "faiss_id": faiss_id,
                    "added_at": datetime.utcnow().isoformat(),
                }
                
                # Add tenant_id to metadata if provided
                if tenant_id:
                    self.metadata[collection_key][document.id]["tenant_id"] = tenant_id
                
                # Save metadata to disk
                self._save_documents(collection_key)
                
                # Save index to disk
                self._save_index(collection_key)
                
                logger.info(f"Inserted document {document.id} into collection {collection_name}")
                return document.id
        except Exception as e:
            logger.error(f"Failed to insert document into collection {collection_name}: {str(e)}")
            raise DocumentError(f"Failed to insert document into collection {collection_name}: {str(e)}")
    
    def insert_documents(self, collection_name: str, documents: List[VectorDocument[np.ndarray]],
                        tenant_id: Optional[str] = None) -> List[str]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection_name: The name of the collection.
            documents: The documents to insert.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of inserted document IDs.
            
        Raises:
            DocumentError: If document insertion fails.
        """
        self._ensure_connected()
        
        try:
            with self.lock:
                collection_key = self._get_collection_key(collection_name, tenant_id)
                
                # Check if collection exists
                if not self._collection_exists_internal(collection_name, tenant_id):
                    raise DocumentError(f"Collection {collection_name} does not exist")
                
                # Get index
                index = self._get_index(collection_key)
                
                # Load document metadata if not already loaded
                if collection_key not in self.metadata:
                    self.metadata[collection_key] = {}
                
                # Prepare embeddings
                embeddings = []
                for document in documents:
                    # Ensure document has an embedding
                    if document.embedding is None:
                        raise DocumentError(f"Document {document.id} must have an embedding")
                    
                    # Ensure embedding is a numpy array
                    embedding = np.array(document.embedding).astype(np.float32)
                    
                    # Reshape embedding to ensure it's 2D (required by FAISS)
                    if embedding.ndim == 1:
                        embedding = embedding.reshape(1, -1)
                    
                    embeddings.append(embedding)
                
                # Concatenate embeddings
                if embeddings:
                    embeddings_array = np.vstack(embeddings)
                    
                    # Add embeddings to index
                    index.add(embeddings_array)
                    
                    # Get FAISS IDs (indices of the added vectors)
                    start_id = index.ntotal - len(documents)
                    
                    # Store document metadata
                    for i, document in enumerate(documents):
                        faiss_id = start_id + i
                        
                        self.metadata[collection_key][document.id] = {
                            "content": document.content,
                            "metadata": document.metadata,
                            "faiss_id": faiss_id,
                            "added_at": datetime.utcnow().isoformat(),
                        }
                        
                        # Add tenant_id to metadata if provided
                        if tenant_id:
                            self.metadata[collection_key][document.id]["tenant_id"] = tenant_id
                
                # Save metadata to disk
                self._save_documents(collection_key)
                
                # Save index to disk
                self._save_index(collection_key)
                
                logger.info(f"Inserted {len(documents)} documents into collection {collection_name}")
                return [document.id for document in documents]
        except Exception as e:
            logger.error(f"Failed to insert documents into collection {collection_name}: {str(e)}")
            raise DocumentError(f"Failed to insert documents into collection {collection_name}: {str(e)}")
    
    def get_document(self, collection_name: str, document_id: str,
                    tenant_id: Optional[str] = None) -> VectorDocument[np.ndarray]:
        """
        Get a document from a collection.
        
        Args:
            collection_name: The name of the collection.
            document_id: The ID of the document.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            The document.
            
        Raises:
            DocumentError: If document does not exist.
        """
        self._ensure_connected()
        
        try:
            collection_key = self._get_collection_key(collection_name, tenant_id)
            
            # Check if collection exists
            if not self._collection_exists_internal(collection_name, tenant_id):
                raise DocumentError(f"Collection {collection_name} does not exist")
            
            # Load document metadata if not already loaded
            if collection_key not in self.metadata or not self.metadata[collection_key]:
                self._load_documents(collection_key)
            
            # Check if document exists
            if document_id not in self.metadata[collection_key]:
                raise DocumentError(f"Document {document_id} not found in collection {collection_name}")
            
            # Get document metadata
            doc_metadata = self.metadata[collection_key][document_id]
            
            # Get index
            index = self._get_index(collection_key)
            
            # Get embedding
            embedding = None
            if hasattr(index, "reconstruct"):
                try:
                    faiss_id = doc_metadata["faiss_id"]
                    embedding = index.reconstruct(int(faiss_id))
                except Exception as e:
                    logger.warning(f"Failed to reconstruct embedding for document {document_id}: {str(e)}")
            
            # Create document
            document = VectorDocument(
                id=document_id,
                content=doc_metadata["content"],
                embedding=embedding,
                metadata=doc_metadata["metadata"],
                tenant_id=doc_metadata.get("tenant_id")
            )
            
            return document
        except Exception as e:
            logger.error(f"Failed to get document {document_id} from collection {collection_name}: {str(e)}")
            raise DocumentError(f"Failed to get document {document_id} from collection {collection_name}: {str(e)}")
    
    def delete_document(self, collection_name: str, document_id: str,
                       tenant_id: Optional[str] = None) -> bool:
        """
        Delete a document from a collection.
        
        Args:
            collection_name: The name of the collection.
            document_id: The ID of the document.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if document was deleted successfully, False otherwise.
            
        Raises:
            DocumentError: If document deletion fails.
        """
        self._ensure_connected()
        
        try:
            with self.lock:
                collection_key = self._get_collection_key(collection_name, tenant_id)
                
                # Check if collection exists
                if not self._collection_exists_internal(collection_name, tenant_id):
                    raise DocumentError(f"Collection {collection_name} does not exist")
                
                # Load document metadata if not already loaded
                if collection_key not in self.metadata or not self.metadata[collection_key]:
                    self._load_documents(collection_key)
                
                # Check if document exists
                if document_id not in self.metadata[collection_key]:
                    logger.warning(f"Document {document_id} not found in collection {collection_name}")
                    return False
                
                # FAISS does not support direct deletion of vectors
                # We need to rebuild the index without the deleted vector
                
                # Get index
                index = self._get_index(collection_key)
                
                # Get FAISS ID of document to delete
                faiss_id_to_delete = self.metadata[collection_key][document_id]["faiss_id"]
                
                # Remove document from metadata
                del self.metadata[collection_key][document_id]
                
                # Update FAISS IDs for documents with higher IDs
                for doc_id, metadata in self.metadata[collection_key].items():
                    if metadata["faiss_id"] > faiss_id_to_delete:
                        metadata["faiss_id"] -= 1
                
                # Save metadata to disk
                self._save_documents(collection_key)
                
                # Rebuild index
                self._rebuild_index(collection_key)
                
                logger.info(f"Deleted document {document_id} from collection {collection_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete document {document_id} from collection {collection_name}: {str(e)}")
            raise DocumentError(f"Failed to delete document {document_id} from collection {collection_name}: {str(e)}")
    
    def update_document(self, collection_name: str, document: VectorDocument[np.ndarray],
                       tenant_id: Optional[str] = None) -> bool:
        """
        Update a document in a collection.
        
        Args:
            collection_name: The name of the collection.
            document: The document to update.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if document was updated successfully, False otherwise.
            
        Raises:
            DocumentError: If document update fails.
        """
        self._ensure_connected()
        
        try:
            with self.lock:
                collection_key = self._get_collection_key(collection_name, tenant_id)
                
                # Check if collection exists
                if not self._collection_exists_internal(collection_name, tenant_id):
                    raise DocumentError(f"Collection {collection_name} does not exist")
                
                # Load document metadata if not already loaded
                if collection_key not in self.metadata or not self.metadata[collection_key]:
                    self._load_documents(collection_key)
                
                # Check if document exists
                if document.id not in self.metadata[collection_key]:
                    logger.warning(f"Document {document.id} not found in collection {collection_name}")
                    return False
                
                # Get index
                index = self._get_index(collection_key)
                
                # Get FAISS ID of document to update
                faiss_id = self.metadata[collection_key][document.id]["faiss_id"]
                
                # FAISS does not support direct update of vectors
                # We need to rebuild the index with the updated vector
                
                # Update document metadata
                self.metadata[collection_key][document.id] = {
                    "content": document.content,
                    "metadata": document.metadata,
                    "faiss_id": faiss_id,
                    "updated_at": datetime.utcnow().isoformat(),
                    "added_at": self.metadata[collection_key][document.id].get("added_at", datetime.utcnow().isoformat()),
                }
                
                # Add tenant_id to metadata if provided
                if tenant_id:
                    self.metadata[collection_key][document.id]["tenant_id"] = tenant_id
                
                # Save metadata to disk
                self._save_documents(collection_key)
                
                # Rebuild index
                self._rebuild_index(collection_key)
                
                logger.info(f"Updated document {document.id} in collection {collection_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to update document {document.id} in collection {collection_name}: {str(e)}")
            raise DocumentError(f"Failed to update document {document.id} in collection {collection_name}: {str(e)}")
    
    def search_by_vector(self, collection_name: str, query_vector: np.ndarray,
                        limit: int = 10, filter: Optional[MetadataFilter] = None,
                        tenant_id: Optional[str] = None) -> List[SearchResult[np.ndarray]]:
        """
        Search for similar vectors in a collection.
        
        Args:
            collection_name: The name of the collection.
            query_vector: The query vector.
            limit: The maximum number of results to return.
            filter: Optional metadata filter.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of search results.
            
        Raises:
            QueryError: If search fails.
        """
        self._ensure_connected()
        
        try:
            collection_key = self._get_collection_key(collection_name, tenant_id)
            
            # Check if collection exists
            if not self._collection_exists_internal(collection_name, tenant_id):
                raise QueryError(f"Collection {collection_name} does not exist")
            
            # Get index
            index = self._get_index(collection_key)
            
            # Ensure query vector is a numpy array
            query = np.array(query_vector).astype(np.float32)
            
            # Reshape query to ensure it's 2D (required by FAISS)
            if query.ndim == 1:
                query = query.reshape(1, -1)
            
            # Search for similar vectors
            k = min(limit, index.ntotal)
            if k == 0:
                return []
            
            distances, indices = index.search(query, k)
            
            # Load documents if not already loaded
            if collection_key not in self.metadata or not self.metadata[collection_key]:
                self._load_documents(collection_key)
            
            # Create search results
            results = []
            
            # Map FAISS IDs to document IDs
            faiss_id_to_doc_id = {}
            for doc_id, metadata in self.metadata[collection_key].items():
                faiss_id_to_doc_id[metadata["faiss_id"]] = doc_id
            
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                # Skip invalid indices
                if idx < 0 or idx >= index.ntotal:
                    continue
                
                # Get document ID
                if idx not in faiss_id_to_doc_id:
                    logger.warning(f"FAISS ID {idx} not found in metadata")
                    continue
                
                doc_id = faiss_id_to_doc_id[idx]
                
                # Get document metadata
                doc_metadata = self.metadata[collection_key][doc_id]
                
                # Apply metadata filter if provided
                if filter and not self._apply_filter(doc_metadata["metadata"], filter):
                    continue
                
                # Get embedding
                embedding = None
                try:
                    if hasattr(index, "reconstruct"):
                        embedding = index.reconstruct(int(idx))
                except Exception as e:
                    logger.warning(f"Failed to reconstruct embedding for document {doc_id}: {str(e)}")
                
                # Create document
                document = VectorDocument(
                    id=doc_id,
                    content=doc_metadata["content"],
                    embedding=embedding,
                    metadata=doc_metadata["metadata"],
                    tenant_id=doc_metadata.get("tenant_id")
                )
                
                # Calculate score (convert distance to similarity score)
                # For L2 distance, smaller is better, so we negate it
                # For IP (inner product), larger is better
                score = -distance if self.metric_type == "L2" else distance
                
                # Create search result
                result = SearchResult(
                    document=document,
                    score=float(score)
                )
                
                results.append(result)
            
            logger.info(f"Found {len(results)} results for vector search in collection {collection_name}")
            return results
        except Exception as e:
            logger.error(f"Failed to search by vector in collection {collection_name}: {str(e)}")
            raise QueryError(f"Failed to search by vector in collection {collection_name}: {str(e)}")
    
    def search_by_text(self, collection_name: str, query_text: str,
                      limit: int = 10, filter: Optional[MetadataFilter] = None,
                      tenant_id: Optional[str] = None) -> List[SearchResult[np.ndarray]]:
        """
        Search for similar documents by text in a collection.
        
        This method is not directly supported by FAISS and requires an external
        embedding model to convert text to vectors. This implementation raises
        an error to indicate that it's not supported.
        
        Args:
            collection_name: The name of the collection.
            query_text: The query text.
            limit: The maximum number of results to return.
            filter: Optional metadata filter.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of search results.
            
        Raises:
            QueryError: If search fails.
        """
        raise QueryError("Text search not supported by FAISS adapter. Use an embedding model to convert text to vectors and then use search_by_vector.")
    
    def search_by_id(self, collection_name: str, document_id: str,
                    limit: int = 10, filter: Optional[MetadataFilter] = None,
                    tenant_id: Optional[str] = None) -> List[SearchResult[np.ndarray]]:
        """
        Search for similar documents to a document in a collection.
        
        Args:
            collection_name: The name of the collection.
            document_id: The ID of the document to search for.
            limit: The maximum number of results to return.
            filter: Optional metadata filter.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of search results.
            
        Raises:
            QueryError: If search fails.
        """
        self._ensure_connected()
        
        try:
            # Get document
            document = self.get_document(collection_name, document_id, tenant_id)
            
            # Search by vector
            return self.search_by_vector(collection_name, document.embedding, limit, filter, tenant_id)
        except Exception as e:
            logger.error(f"Failed to search by ID in collection {collection_name}: {str(e)}")
            raise QueryError(f"Failed to search by ID in collection {collection_name}: {str(e)}")
    
    def count_documents(self, collection_name: str, filter: Optional[MetadataFilter] = None,
                       tenant_id: Optional[str] = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection_name: The name of the collection.
            filter: Optional metadata filter.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            The number of documents.
            
        Raises:
            CollectionError: If collection does not exist.
        """
        self._ensure_connected()
        
        try:
            collection_key = self._get_collection_key(collection_name, tenant_id)
            
            # Check if collection exists
            if not self._collection_exists_internal(collection_name, tenant_id):
                raise CollectionError(f"Collection {collection_name} does not exist")
            
            # Get index
            index = self._get_index(collection_key)
            
            # If no filter, return total count
            if not filter:
                return index.ntotal
            
            # Load document metadata if not already loaded
            if collection_key not in self.metadata or not self.metadata[collection_key]:
                self._load_documents(collection_key)
            
            # Count documents that match filter
            count = 0
            for doc_id, metadata in self.metadata[collection_key].items():
                if self._apply_filter(metadata["metadata"], filter):
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"Failed to count documents in collection {collection_name}: {str(e)}")
            raise CollectionError(f"Failed to count documents in collection {collection_name}: {str(e)}")
    
    def create_index(self, collection_name: str, tenant_id: Optional[str] = None) -> bool:
        """
        Create an index for a collection.
        
        For FAISS, this is a no-op since the index is created when the collection is created.
        
        Args:
            collection_name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if index creation is successful, False otherwise.
            
        Raises:
            CollectionError: If collection does not exist.
        """
        self._ensure_connected()
        
        try:
            # Check if collection exists
            if not self._collection_exists_internal(collection_name, tenant_id):
                raise CollectionError(f"Collection {collection_name} does not exist")
            
            # Index is already created when collection is created
            return True
        except Exception as e:
            logger.error(f"Failed to create index for collection {collection_name}: {str(e)}")
            raise IndexError(f"Failed to create index for collection {collection_name}: {str(e)}")
    
    def get_nearest_neighbors(self, collection_name: str, query_vector: np.ndarray,
                             k: int = 10, filter: Optional[MetadataFilter] = None,
                             tenant_id: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        Get the nearest neighbors to a query vector.
        
        Args:
            collection_name: The name of the collection.
            query_vector: The query vector.
            k: The number of neighbors to return.
            filter: Optional metadata filter.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of tuples with document IDs and distances.
            
        Raises:
            QueryError: If query fails.
        """
        self._ensure_connected()
        
        try:
            # Search by vector
            results = self.search_by_vector(collection_name, query_vector, k, filter, tenant_id)
            
            # Convert to list of tuples
            return [(result.document.id, result.score) for result in results]
        except Exception as e:
            logger.error(f"Failed to get nearest neighbors in collection {collection_name}: {str(e)}")
            raise QueryError(f"Failed to get nearest neighbors in collection {collection_name}: {str(e)}")
    
    def _ensure_connected(self):
        """
        Ensure that the adapter is connected.
        
        Raises:
            ConnectionError: If not connected.
        """
        if not self._connected:
            raise ConnectionError("Not connected to FAISS database")
    
    def _get_collection_key(self, name: str, tenant_id: Optional[str] = None) -> str:
        """
        Get the key for a collection.
        
        Args:
            name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            The collection key.
        """
        return self.get_tenant_prefixed_collection_name(name, tenant_id)
    
    def _collection_exists_internal(self, name: str, tenant_id: Optional[str] = None) -> bool:
        """
        Check if a collection exists internally.
        
        Args:
            name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if collection exists, False otherwise.
        """
        collection_key = self._get_collection_key(name, tenant_id)
        
        # Check if index is loaded in memory
        if collection_key in self.indices:
            return True
        
        # Check if index exists on disk
        index_path = os.path.join(self.storage_path, f"{collection_key}.index")
        metadata_path = os.path.join(self.storage_path, f"{collection_key}.metadata.json")
        
        return os.path.exists(index_path) and os.path.exists(metadata_path)
    
    def _get_index(self, collection_key: str) -> faiss.Index:
        """
        Get the FAISS index for a collection.
        
        Args:
            collection_key: The key of the collection.
            
        Returns:
            The FAISS index.
            
        Raises:
            CollectionError: If collection does not exist.
        """
        # Check if index is loaded in memory
        if collection_key in self.indices:
            return self.indices[collection_key]
        
        # Check if index exists on disk
        index_path = os.path.join(self.storage_path, f"{collection_key}.index")
        
        if not os.path.exists(index_path):
            raise CollectionError(f"Index for collection {collection_key} not found")
        
        # Load index from disk
        try:
            index = faiss.read_index(index_path)
            self.indices[collection_key] = index
            return index
        except Exception as e:
            raise CollectionError(f"Failed to load index for collection {collection_key}: {str(e)}")
    
    def _load_indices(self):
        """
        Load all indices from disk.
        
        This method is called during connection to load existing indices.
        """
        # List all index files in the storage directory
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".index"):
                collection_key = filename.replace(".index", "")
                
                try:
                    # Load index
                    index_path = os.path.join(self.storage_path, filename)
                    index = faiss.read_index(index_path)
                    self.indices[collection_key] = index
                    
                    # Load documents
                    self._load_documents(collection_key)
                    
                    logger.info(f"Loaded index for collection {collection_key}")
                except Exception as e:
                    logger.error(f"Failed to load index for collection {collection_key}: {str(e)}")
    
    def _save_indices(self):
        """
        Save all indices to disk.
        
        This method is called during disconnection to save indices.
        """
        for collection_key, index in self.indices.items():
            try:
                self._save_index(collection_key)
                logger.info(f"Saved index for collection {collection_key}")
            except Exception as e:
                logger.error(f"Failed to save index for collection {collection_key}: {str(e)}")
    
    def _save_index(self, collection_key: str):
        """
        Save an index to disk.
        
        Args:
            collection_key: The key of the collection.
            
        Raises:
            CollectionError: If saving index fails.
        """
        if collection_key not in self.indices:
            raise CollectionError(f"Index for collection {collection_key} not found in memory")
        
        index_path = os.path.join(self.storage_path, f"{collection_key}.index")
        
        try:
            faiss.write_index(self.indices[collection_key], index_path)
        except Exception as e:
            raise CollectionError(f"Failed to save index for collection {collection_key}: {str(e)}")
    
    def _save_collection_metadata(self, collection_key: str, metadata: Dict[str, Any]):
        """
        Save collection metadata to disk.
        
        Args:
            collection_key: The key of the collection.
            metadata: The metadata to save.
            
        Raises:
            CollectionError: If saving metadata fails.
        """
        metadata_path = os.path.join(self.storage_path, f"{collection_key}.metadata.json")
        
        try:
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            raise CollectionError(f"Failed to save metadata for collection {collection_key}: {str(e)}")
    
    def _load_documents(self, collection_key: str):
        """
        Load document metadata from disk.
        
        Args:
            collection_key: The key of the collection.
            
        Raises:
            DocumentError: If loading documents fails.
        """
        documents_path = os.path.join(self.storage_path, f"{collection_key}.documents.json")
        
        if not os.path.exists(documents_path):
            # No documents yet
            self.metadata[collection_key] = {}
            return
        
        try:
            with open(documents_path, "r") as f:
                self.metadata[collection_key] = json.load(f)
        except Exception as e:
            raise DocumentError(f"Failed to load documents for collection {collection_key}: {str(e)}")
    
    def _save_documents(self, collection_key: str):
        """
        Save document metadata to disk.
        
        Args:
            collection_key: The key of the collection.
            
        Raises:
            DocumentError: If saving documents fails.
        """
        if collection_key not in self.metadata:
            raise DocumentError(f"Documents for collection {collection_key} not found in memory")
        
        documents_path = os.path.join(self.storage_path, f"{collection_key}.documents.json")
        
        try:
            with open(documents_path, "w") as f:
                json.dump(self.metadata[collection_key], f, indent=2)
        except Exception as e:
            raise DocumentError(f"Failed to save documents for collection {collection_key}: {str(e)}")
    
    def _rebuild_index(self, collection_key: str):
        """
        Rebuild the index for a collection.
        
        This method is called when documents are deleted or updated.
        
        Args:
            collection_key: The key of the collection.
            
        Raises:
            CollectionError: If rebuilding index fails.
        """
        if collection_key not in self.indices:
            raise CollectionError(f"Index for collection {collection_key} not found in memory")
        
        if collection_key not in self.metadata:
            raise CollectionError(f"Documents for collection {collection_key} not found in memory")
        
        try:
            # Get current index
            index = self.indices[collection_key]
            
            # Get dimension
            dimension = index.d
            
            # Create new index
            if self.metric_type == "L2":
                new_index = faiss.IndexFlatL2(dimension)
            elif self.metric_type == "IP":
                new_index = faiss.IndexFlatIP(dimension)
            else:
                raise CollectionError(f"Unsupported metric type: {self.metric_type}")
            
            # Collect embeddings
            embeddings = []
            doc_ids = []
            
            for doc_id, metadata in self.metadata[collection_key].items():
                # Get embedding
                faiss_id = metadata["faiss_id"]
                
                try:
                    embedding = index.reconstruct(faiss_id)
                    embeddings.append(embedding)
                    doc_ids.append(doc_id)
                except Exception as e:
                    logger.warning(f"Failed to reconstruct embedding for document {doc_id}: {str(e)}")
            
            # Add embeddings to new index
            if embeddings:
                embeddings_array = np.vstack(embeddings)
                new_index.add(embeddings_array)
                
                # Update FAISS IDs
                for i, doc_id in enumerate(doc_ids):
                    self.metadata[collection_key][doc_id]["faiss_id"] = i
            
            # Replace index
            self.indices[collection_key] = new_index
            
            # Save index to disk
            self._save_index(collection_key)
            
            # Save documents to disk
            self._save_documents(collection_key)
            
            logger.info(f"Rebuilt index for collection {collection_key}")
        except Exception as e:
            raise CollectionError(f"Failed to rebuild index for collection {collection_key}: {str(e)}")
    
    def _apply_filter(self, metadata: Dict[str, Any], filter: MetadataFilter) -> bool:
        """
        Apply a metadata filter to document metadata.
        
        Args:
            metadata: The document metadata.
            filter: The metadata filter.
            
        Returns:
            True if the document matches the filter, False otherwise.
        """
        # Convert filter to dict
        filter_dict = filter.to_dict()
        
        # Apply filter conditions
        for condition in filter_dict.get("conditions", []):
            condition_type = condition.get("type")
            
            if condition_type == "equals":
                field = condition.get("field")
                value = condition.get("value")
                
                if field not in metadata or metadata[field] != value:
                    return False
            
            elif condition_type == "not_equals":
                field = condition.get("field")
                value = condition.get("value")
                
                if field in metadata and metadata[field] == value:
                    return False
            
            elif condition_type == "greater_than":
                field = condition.get("field")
                value = condition.get("value")
                
                if field not in metadata or metadata[field] <= value:
                    return False
            
            elif condition_type == "less_than":
                field = condition.get("field")
                value = condition.get("value")
                
                if field not in metadata or metadata[field] >= value:
                    return False
            
            elif condition_type == "greater_than_or_equal":
                field = condition.get("field")
                value = condition.get("value")
                
                if field not in metadata or metadata[field] < value:
                    return False
            
            elif condition_type == "less_than_or_equal":
                field = condition.get("field")
                value = condition.get("value")
                
                if field not in metadata or metadata[field] > value:
                    return False
            
            elif condition_type == "in":
                field = condition.get("field")
                values = condition.get("value")
                
                if field not in metadata or metadata[field] not in values:
                    return False
            
            elif condition_type == "not_in":
                field = condition.get("field")
                values = condition.get("value")
                
                if field in metadata and metadata[field] in values:
                    return False
            
            elif condition_type == "contains":
                field = condition.get("field")
                value = condition.get("value")
                
                if field not in metadata or not isinstance(metadata[field], str) or value not in metadata[field]:
                    return False
            
            elif condition_type == "not_contains":
                field = condition.get("field")
                value = condition.get("value")
                
                if field in metadata and isinstance(metadata[field], str) and value in metadata[field]:
                    return False
            
            elif condition_type == "starts_with":
                field = condition.get("field")
                value = condition.get("value")
                
                if field not in metadata or not isinstance(metadata[field], str) or not metadata[field].startswith(value):
                    return False
            
            elif condition_type == "ends_with":
                field = condition.get("field")
                value = condition.get("value")
                
                if field not in metadata or not isinstance(metadata[field], str) or not metadata[field].endswith(value):
                    return False
            
            elif condition_type == "exists":
                field = condition.get("field")
                
                if field not in metadata:
                    return False
            
            elif condition_type == "not_exists":
                field = condition.get("field")
                
                if field in metadata:
                    return False
            
            elif condition_type == "and":
                filters = condition.get("filters", [])
                
                for sub_filter in filters:
                    sub_filter_obj = MetadataFilter.from_dict(sub_filter)
                    if not self._apply_filter(metadata, sub_filter_obj):
                        return False
            
            elif condition_type == "or":
                filters = condition.get("filters", [])
                
                if not filters:
                    return False
                
                match = False
                for sub_filter in filters:
                    sub_filter_obj = MetadataFilter.from_dict(sub_filter)
                    if self._apply_filter(metadata, sub_filter_obj):
                        match = True
                        break
                
                if not match:
                    return False
        
        return True
