"""
Chroma Adapter for Aideon AI Lite Vector Database

This module provides a concrete implementation of the VectorDatabaseAdapter
interface using Chroma as the backend.

Chroma is an open-source embedding database designed for storing, managing,
and searching vector embeddings for AI applications.

Production-ready features:
- Connection management for both in-memory and persistent deployments
- Collection handling with tenant isolation
- Embedding integration with multiple models
- Comprehensive error handling
- Performance optimizations
"""

import os
import json
import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union, cast

import numpy as np
import chromadb
from chromadb.config import Settings
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions

# Fix import path for vector_database
from ...vector_database import (
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


class ChromaAdapter(VectorDatabaseAdapter[np.ndarray]):
    """
    Chroma implementation of the VectorDatabaseAdapter interface.
    
    This adapter uses Chroma for efficient similarity search and management
    of vector embeddings, with support for multi-tenant isolation and
    comprehensive error handling.
    """
    
    def __init__(self, 
                 persist_directory: Optional[str] = None,
                 host: Optional[str] = None,
                 port: Optional[str] = None,
                 ssl: bool = False,
                 headers: Optional[Dict[str, str]] = None):
        """
        Initialize the Chroma adapter.
        
        Args:
            persist_directory: Optional directory for persistent storage.
                If None, an in-memory database will be used.
            host: Optional host for client connection.
            port: Optional port for client connection.
            ssl: Whether to use SSL for client connection.
            headers: Optional headers for client connection.
        """
        self.persist_directory = persist_directory
        self.host = host
        self.port = port
        self.ssl = ssl
        self.headers = headers or {}
        
        # Create storage directory if it doesn't exist
        if self.persist_directory:
            os.makedirs(self.persist_directory, exist_ok=True)
        
        # Dictionary to store collection metadata
        self.metadata: Dict[str, Dict[str, Any]] = {}
        
        # Lock for thread safety
        self.lock = threading.RLock()
        
        # Connection status
        self._connected = False
        
        # Chroma client
        self.client = None
        
        # Default embedding function
        self.default_embedding_function = None
    
    def connect(self, connection_params: Dict[str, Any]) -> bool:
        """
        Connect to the Chroma database.
        
        Args:
            connection_params: Connection parameters.
                persist_directory: Optional override for persist directory.
                host: Optional override for host.
                port: Optional override for port.
                ssl: Optional override for SSL.
                headers: Optional override for headers.
                
        Returns:
            True if connection was successful, False otherwise.
            
        Raises:
            ConnectionError: If connection fails.
        """
        try:
            # Update connection parameters if provided
            persist_directory = connection_params.get("persist_directory", self.persist_directory)
            host = connection_params.get("host", self.host)
            port = connection_params.get("port", self.port)
            ssl = connection_params.get("ssl", self.ssl)
            headers = connection_params.get("headers", self.headers)
            
            # Configure settings
            settings = Settings()
            
            if host and port:
                # HTTP client
                self.client = chromadb.HttpClient(
                    host=host,
                    port=port,
                    ssl=ssl,
                    headers=headers
                )
            else:
                # Persistent or in-memory client
                self.client = chromadb.PersistentClient(
                    path=persist_directory
                ) if persist_directory else chromadb.Client(settings)
            
            # Initialize default embedding function
            self.default_embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Update instance variables
            self.persist_directory = persist_directory
            self.host = host
            self.port = port
            self.ssl = ssl
            self.headers = headers
            
            self._connected = True
            logger.info(f"Connected to Chroma database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Chroma database: {str(e)}")
            raise ConnectionError(f"Failed to connect to Chroma database: {str(e)}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from the Chroma database.
        
        Returns:
            True if disconnection was successful, False otherwise.
        """
        if not self._connected:
            return True
        
        try:
            # Clear in-memory data structures
            with self.lock:
                self.metadata.clear()
            
            # Reset client
            self.client = None
            self.default_embedding_function = None
            
            self._connected = False
            logger.info("Disconnected from Chroma database")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect from Chroma database: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if connected to the Chroma database.
        
        Returns:
            True if connected, False otherwise.
        """
        return self._connected and self.client is not None
    
    def create_collection(self, name: str, dimension: int, 
                         metadata: Optional[Dict[str, Any]] = None,
                         tenant_id: Optional[str] = None) -> bool:
        """
        Create a new collection in the Chroma database.
        
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
                # Get tenant-prefixed collection name
                collection_name = self.get_tenant_prefixed_collection_name(name, tenant_id)
                
                # Check if collection already exists
                try:
                    self.client.get_collection(name=collection_name)
                    logger.warning(f"Collection {collection_name} already exists")
                    return False
                except Exception:
                    # Collection doesn't exist, proceed with creation
                    pass
                
                # Prepare collection metadata
                collection_metadata = metadata or {}
                collection_metadata.update({
                    "dimension": dimension,
                    "created_at": datetime.utcnow().isoformat(),
                    "document_count": 0,
                })
                
                if tenant_id:
                    collection_metadata["tenant_id"] = tenant_id
                
                # Create collection
                self.client.create_collection(
                    name=collection_name,
                    metadata=collection_metadata,
                    embedding_function=self.default_embedding_function
                )
                
                # Store collection metadata
                self.metadata[collection_name] = collection_metadata
                
                logger.info(f"Created collection {collection_name} with dimension {dimension}")
                return True
        except Exception as e:
            logger.error(f"Failed to create collection {name}: {str(e)}")
            raise CollectionError(f"Failed to create collection {name}: {str(e)}")
    
    def delete_collection(self, name: str, 
                         tenant_id: Optional[str] = None) -> bool:
        """
        Delete a collection from the Chroma database.
        
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
                # Get tenant-prefixed collection name
                collection_name = self.get_tenant_prefixed_collection_name(name, tenant_id)
                
                # Check if collection exists
                try:
                    self.client.get_collection(name=collection_name)
                except Exception:
                    logger.warning(f"Collection {collection_name} does not exist")
                    return False
                
                # Delete collection
                self.client.delete_collection(name=collection_name)
                
                # Remove metadata
                if collection_name in self.metadata:
                    del self.metadata[collection_name]
                
                logger.info(f"Deleted collection {collection_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete collection {name}: {str(e)}")
            raise CollectionError(f"Failed to delete collection {name}: {str(e)}")
    
    def list_collections(self, tenant_id: Optional[str] = None) -> List[str]:
        """
        List all collections in the Chroma database.
        
        Args:
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of collection names.
            
        Raises:
            CollectionError: If listing collections fails.
        """
        self._ensure_connected()
        
        try:
            # Get all collections
            all_collections = self.client.list_collections()
            
            # Extract collection names
            collection_names = [collection.name for collection in all_collections]
            
            # Filter by tenant if provided
            if tenant_id:
                tenant_prefix = f"{tenant_id}_"
                filtered_collections = []
                
                for collection_name in collection_names:
                    if collection_name.startswith(tenant_prefix):
                        # Remove tenant prefix
                        name = collection_name[len(tenant_prefix):]
                        filtered_collections.append(name)
                
                return filtered_collections
            else:
                # If no tenant filtering, return all collections
                # but strip tenant prefix if present
                result_collections = []
                
                for collection_name in collection_names:
                    parts = collection_name.split("_", 1)
                    if len(parts) > 1:
                        result_collections.append(parts[1])
                    else:
                        result_collections.append(collection_name)
                
                return result_collections
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise CollectionError(f"Failed to list collections: {str(e)}")
    
    def collection_exists(self, name: str, 
                         tenant_id: Optional[str] = None) -> bool:
        """
        Check if a collection exists in the Chroma database.
        
        Args:
            name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if collection exists, False otherwise.
        """
        self._ensure_connected()
        
        try:
            # Get tenant-prefixed collection name
            collection_name = self.get_tenant_prefixed_collection_name(name, tenant_id)
            
            # Check if collection exists
            try:
                self.client.get_collection(name=collection_name)
                return True
            except Exception:
                return False
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
            # Get tenant-prefixed collection name
            collection_name = self.get_tenant_prefixed_collection_name(name, tenant_id)
            
            # Get collection
            try:
                collection = self.client.get_collection(name=collection_name)
            except Exception:
                raise CollectionError(f"Collection {name} does not exist")
            
            # Get collection metadata
            metadata = collection.metadata or {}
            
            # Count documents
            count = collection.count()
            
            # Update metadata with count
            metadata["document_count"] = count
            
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
                # Get tenant-prefixed collection name
                prefixed_collection_name = self.get_tenant_prefixed_collection_name(collection_name, tenant_id)
                
                # Get collection
                try:
             
(Content truncated due to size limit. Use line ranges to read in chunks)