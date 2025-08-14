"""
Vector Database Interface for Aideon AI Lite

This module provides a unified interface for vector database operations in the Aideon AI Lite platform.
It defines the core abstractions and interfaces for vector storage, retrieval, and management,
supporting multiple backend implementations through adapters.

Production-ready features:
- Abstract interface for vector database operations
- Support for multiple vector database backends
- Tenant-aware vector storage and retrieval
- Comprehensive error handling and logging
- Type hints for better IDE support and static analysis
"""

import abc
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union, Tuple, Set, TypeVar, Generic

logger = logging.getLogger(__name__)

# Type variable for vector embeddings
T = TypeVar('T')


class VectorDatabaseError(Exception):
    """Base exception class for vector database errors."""
    pass


class ConnectionError(VectorDatabaseError):
    """Exception raised when connection to vector database fails."""
    pass


class QueryError(VectorDatabaseError):
    """Exception raised when a query to the vector database fails."""
    pass


class IndexError(VectorDatabaseError):
    """Exception raised when an index operation fails."""
    pass


class DocumentError(VectorDatabaseError):
    """Exception raised when a document operation fails."""
    pass


class CollectionError(VectorDatabaseError):
    """Exception raised when a collection operation fails."""
    pass


class EmbeddingError(VectorDatabaseError):
    """Exception raised when embedding generation fails."""
    pass


class MetadataFilter:
    """Class representing a filter for metadata in vector database queries."""
    
    def __init__(self):
        """Initialize a new metadata filter."""
        self.conditions = []
    
    def add_equals(self, field: str, value: Any) -> 'MetadataFilter':
        """
        Add an equals condition to the filter.
        
        Args:
            field: The field to filter on.
            value: The value to compare with.
            
        Returns:
            The filter instance for chaining.
        """
        self.conditions.append({"field": field, "op": "==", "value": value})
        return self
    
    def add_not_equals(self, field: str, value: Any) -> 'MetadataFilter':
        """
        Add a not equals condition to the filter.
        
        Args:
            field: The field to filter on.
            value: The value to compare with.
            
        Returns:
            The filter instance for chaining.
        """
        self.conditions.append({"field": field, "op": "!=", "value": value})
        return self
    
    def add_greater_than(self, field: str, value: Any) -> 'MetadataFilter':
        """
        Add a greater than condition to the filter.
        
        Args:
            field: The field to filter on.
            value: The value to compare with.
            
        Returns:
            The filter instance for chaining.
        """
        self.conditions.append({"field": field, "op": ">", "value": value})
        return self
    
    def add_less_than(self, field: str, value: Any) -> 'MetadataFilter':
        """
        Add a less than condition to the filter.
        
        Args:
            field: The field to filter on.
            value: The value to compare with.
            
        Returns:
            The filter instance for chaining.
        """
        self.conditions.append({"field": field, "op": "<", "value": value})
        return self
    
    def add_in(self, field: str, values: List[Any]) -> 'MetadataFilter':
        """
        Add an in condition to the filter.
        
        Args:
            field: The field to filter on.
            values: The list of values to check against.
            
        Returns:
            The filter instance for chaining.
        """
        self.conditions.append({"field": field, "op": "in", "value": values})
        return self
    
    def add_contains(self, field: str, value: Any) -> 'MetadataFilter':
        """
        Add a contains condition to the filter.
        
        Args:
            field: The field to filter on.
            value: The value to check for.
            
        Returns:
            The filter instance for chaining.
        """
        self.conditions.append({"field": field, "op": "contains", "value": value})
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the filter to a dictionary.
        
        Returns:
            A dictionary representation of the filter.
        """
        return {"conditions": self.conditions}


class VectorDocument(Generic[T]):
    """
    Class representing a document in the vector database.
    
    A vector document contains the original content, its vector embedding,
    and associated metadata.
    """
    
    def __init__(self, 
                 id: str,
                 content: str,
                 embedding: Optional[T] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 tenant_id: Optional[str] = None):
        """
        Initialize a new vector document.
        
        Args:
            id: The unique identifier for the document.
            content: The original content of the document.
            embedding: Optional vector embedding of the content.
            metadata: Optional metadata for the document.
            tenant_id: Optional tenant ID for multi-tenant isolation.
        """
        self.id = id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}
        self.tenant_id = tenant_id
        
        # Add creation timestamp if not present
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the document to a dictionary.
        
        Returns:
            A dictionary representation of the document.
        """
        result = {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
        }
        
        if self.tenant_id:
            result["tenant_id"] = self.tenant_id
        
        # Embedding is typically not included in the dict representation
        # as it may be large and not serializable
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorDocument':
        """
        Create a document from a dictionary.
        
        Args:
            data: The dictionary containing document data.
            
        Returns:
            A new VectorDocument instance.
        """
        return cls(
            id=data["id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            tenant_id=data.get("tenant_id")
        )


class SearchResult(Generic[T]):
    """
    Class representing a search result from the vector database.
    
    A search result contains the matched document, its similarity score,
    and any additional metadata.
    """
    
    def __init__(self, 
                 document: VectorDocument[T],
                 score: float,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a new search result.
        
        Args:
            document: The matched document.
            score: The similarity score (higher is better).
            metadata: Optional metadata for the search result.
        """
        self.document = document
        self.score = score
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the search result to a dictionary.
        
        Returns:
            A dictionary representation of the search result.
        """
        return {
            "document": self.document.to_dict(),
            "score": self.score,
            "metadata": self.metadata,
        }


class VectorDatabaseAdapter(abc.ABC, Generic[T]):
    """
    Abstract base class for vector database adapters.
    
    This class defines the interface that all vector database adapters must implement.
    """
    
    @abc.abstractmethod
    def connect(self, connection_params: Dict[str, Any]) -> bool:
        """
        Connect to the vector database.
        
        Args:
            connection_params: Connection parameters specific to the database.
            
        Returns:
            True if connection was successful, False otherwise.
            
        Raises:
            ConnectionError: If connection fails.
        """
        pass
    
    @abc.abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the vector database.
        
        Returns:
            True if disconnection was successful, False otherwise.
        """
        pass
    
    @abc.abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connected to the vector database.
        
        Returns:
            True if connected, False otherwise.
        """
        pass
    
    @abc.abstractmethod
    def create_collection(self, name: str, dimension: int, 
                         metadata: Optional[Dict[str, Any]] = None,
                         tenant_id: Optional[str] = None) -> bool:
        """
        Create a new collection in the vector database.
        
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
        pass
    
    @abc.abstractmethod
    def delete_collection(self, name: str, 
                         tenant_id: Optional[str] = None) -> bool:
        """
        Delete a collection from the vector database.
        
        Args:
            name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if collection was deleted successfully, False otherwise.
            
        Raises:
            CollectionError: If collection deletion fails.
        """
        pass
    
    @abc.abstractmethod
    def list_collections(self, tenant_id: Optional[str] = None) -> List[str]:
        """
        List all collections in the vector database.
        
        Args:
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of collection names.
            
        Raises:
            CollectionError: If listing collections fails.
        """
        pass
    
    @abc.abstractmethod
    def collection_exists(self, name: str, 
                         tenant_id: Optional[str] = None) -> bool:
        """
        Check if a collection exists in the vector database.
        
        Args:
            name: The name of the collection.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if collection exists, False otherwise.
        """
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
    def insert_document(self, collection_name: str, document: VectorDocument[T],
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
        pass
    
    @abc.abstractmethod
    def insert_documents(self, collection_name: str, documents: List[VectorDocument[T]],
                        tenant_id: Optional[str] = None) -> List[str]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection_name: The name of the collection.
            documents: The documents to insert.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A list of IDs of the inserted documents.
            
        Raises:
            DocumentError: If document insertion fails.
        """
        pass
    
    @abc.abstractmethod
    def get_document(self, collection_name: str, document_id: str,
                    tenant_id: Optional[str] = None) -> VectorDocument[T]:
        """
        Get a document from a collection.
        
        Args:
            collection_name: The name of the collection.
            document_id: The ID of the document to get.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            The document.
            
        Raises:
            DocumentError: If document retrieval fails.
        """
        pass
    
    @abc.abstractmethod
    def delete_document(self, collection_name: str, document_id: str,
                       tenant_id: Optional[str] = None) -> bool:
        """
        Delete a document from a collection.
        
        Args:
            collection_name: The name of the collection.
            document_id: The ID of the document to delete.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            True if document was deleted successfully, False otherwise.
            
        Raises:
            DocumentError: If document deletion fails.
        """
        pass
    
    @abc.abstractmethod
    def update_document(self, collection_name: str, document: VectorDocument[T],
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
        pass
    
    @abc.abstractmethod
    def search_by_vector(self, collection_name: str, query_vector: T,
                        limit: int = 10, filter: Optional[MetadataFilter] = None,
                        tenant_id: Optional[str] = None) -> List[SearchResult[T]]:
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
        pass
    
    @abc.abstractmethod
    d
(Content truncated due to size limit. Use line ranges to read in chunks)