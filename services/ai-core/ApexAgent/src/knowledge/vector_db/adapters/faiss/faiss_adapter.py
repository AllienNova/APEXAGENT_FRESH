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
                index.add(embed
(Content truncated due to size limit. Use line ranges to read in chunks)