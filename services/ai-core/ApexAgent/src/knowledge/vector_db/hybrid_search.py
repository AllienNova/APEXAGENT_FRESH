"""
Hybrid Search Interface for Aideon AI Lite Vector Database

This module provides interfaces and utilities for hybrid search functionality,
combining vector similarity search with keyword-based search for optimal results.

The hybrid search implementation supports multiple backends (FAISS, Milvus, Chroma)
and maintains enterprise-ready features including multi-tenant isolation,
comprehensive error handling, and high performance.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, TypeVar, Generic, Tuple

import numpy as np

from src.knowledge.vector_db.vector_database import (
    VectorDatabaseAdapter,
    VectorDocument,
    SearchResult,
    MetadataFilter,
    QueryError,
)

logger = logging.getLogger(__name__)

# Type variable for vector embeddings
T = TypeVar('T')


class HybridSearchResult(Generic[T]):
    """
    Result from a hybrid search operation.
    
    Contains the document, combined score, and component scores.
    """
    
    def __init__(self, 
                document: VectorDocument[T],
                combined_score: float,
                vector_score: float,
                keyword_score: float,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a hybrid search result.
        
        Args:
            document: The document.
            combined_score: The combined score (0.0 to 1.0).
            vector_score: The vector similarity score (0.0 to 1.0).
            keyword_score: The keyword match score (0.0 to 1.0).
            metadata: Optional metadata about the search result.
        """
        self.document = document
        self.combined_score = combined_score
        self.vector_score = vector_score
        self.keyword_score = keyword_score
        self.metadata = metadata or {}
    
    def __repr__(self) -> str:
        return (f"HybridSearchResult(id={self.document.id}, "
                f"combined_score={self.combined_score:.4f}, "
                f"vector_score={self.vector_score:.4f}, "
                f"keyword_score={self.keyword_score:.4f})")


class HybridSearchStrategy(ABC):
    """
    Abstract base class for hybrid search strategies.
    
    Defines how vector and keyword search results are combined.
    """
    
    @abstractmethod
    def combine_scores(self, vector_score: float, keyword_score: float) -> float:
        """
        Combine vector and keyword scores into a single score.
        
        Args:
            vector_score: The vector similarity score (0.0 to 1.0).
            keyword_score: The keyword match score (0.0 to 1.0).
            
        Returns:
            The combined score (0.0 to 1.0).
        """
        pass


class WeightedAverageStrategy(HybridSearchStrategy):
    """
    Weighted average strategy for combining vector and keyword scores.
    
    combined_score = (vector_weight * vector_score + keyword_weight * keyword_score) / (vector_weight + keyword_weight)
    """
    
    def __init__(self, vector_weight: float = 0.7, keyword_weight: float = 0.3):
        """
        Initialize a weighted average strategy.
        
        Args:
            vector_weight: The weight for vector scores (default: 0.7).
            keyword_weight: The weight for keyword scores (default: 0.3).
        """
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        
        # Normalize weights
        total_weight = self.vector_weight + self.keyword_weight
        if total_weight != 1.0:
            self.vector_weight /= total_weight
            self.keyword_weight /= total_weight
    
    def combine_scores(self, vector_score: float, keyword_score: float) -> float:
        """
        Combine vector and keyword scores using weighted average.
        
        Args:
            vector_score: The vector similarity score (0.0 to 1.0).
            keyword_score: The keyword match score (0.0 to 1.0).
            
        Returns:
            The combined score (0.0 to 1.0).
        """
        return (self.vector_weight * vector_score + self.keyword_weight * keyword_score)


class MaxScoreStrategy(HybridSearchStrategy):
    """
    Max score strategy for combining vector and keyword scores.
    
    combined_score = max(vector_score, keyword_score)
    """
    
    def combine_scores(self, vector_score: float, keyword_score: float) -> float:
        """
        Combine vector and keyword scores by taking the maximum.
        
        Args:
            vector_score: The vector similarity score (0.0 to 1.0).
            keyword_score: The keyword match score (0.0 to 1.0).
            
        Returns:
            The combined score (0.0 to 1.0).
        """
        return max(vector_score, keyword_score)


class MinScoreStrategy(HybridSearchStrategy):
    """
    Min score strategy for combining vector and keyword scores.
    
    combined_score = min(vector_score, keyword_score)
    """
    
    def combine_scores(self, vector_score: float, keyword_score: float) -> float:
        """
        Combine vector and keyword scores by taking the minimum.
        
        Args:
            vector_score: The vector similarity score (0.0 to 1.0).
            keyword_score: The keyword match score (0.0 to 1.0).
            
        Returns:
            The combined score (0.0 to 1.0).
        """
        return min(vector_score, keyword_score)


class HybridSearchEngine(Generic[T]):
    """
    Engine for performing hybrid search operations.
    
    Combines vector similarity search with keyword-based search.
    """
    
    def __init__(self, 
                adapter: VectorDatabaseAdapter[T],
                strategy: Optional[HybridSearchStrategy] = None):
        """
        Initialize a hybrid search engine.
        
        Args:
            adapter: The vector database adapter.
            strategy: The strategy for combining scores (default: WeightedAverageStrategy).
        """
        self.adapter = adapter
        self.strategy = strategy or WeightedAverageStrategy()
    
    def search(self, 
              collection_name: str,
              query_text: str,
              query_vector: Optional[T] = None,
              limit: int = 10,
              filter: Optional[MetadataFilter] = None,
              tenant_id: Optional[str] = None,
              min_keyword_score: float = 0.0,
              min_vector_score: float = 0.0,
              min_combined_score: float = 0.0) -> List[HybridSearchResult[T]]:
        """
        Perform a hybrid search operation.
        
        Args:
            collection_name: The name of the collection.
            query_text: The query text for keyword search.
            query_vector: Optional query vector for vector search.
                If None, the adapter will generate a vector from the query text.
            limit: The maximum number of results to return.
            filter: Optional metadata filter.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            min_keyword_score: Minimum keyword score threshold (0.0 to 1.0).
            min_vector_score: Minimum vector score threshold (0.0 to 1.0).
            min_combined_score: Minimum combined score threshold (0.0 to 1.0).
            
        Returns:
            A list of hybrid search results.
            
        Raises:
            QueryError: If search fails.
        """
        try:
            # Perform vector search
            vector_results = []
            if query_vector is not None:
                vector_results = self.adapter.search_by_vector(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit * 2,  # Get more results for better hybrid matching
                    filter=filter,
                    tenant_id=tenant_id
                )
            else:
                # Use text-to-vector search
                vector_results = self.adapter.search_by_text(
                    collection_name=collection_name,
                    query_text=query_text,
                    limit=limit * 2,  # Get more results for better hybrid matching
                    filter=filter,
                    tenant_id=tenant_id
                )
            
            # Perform keyword search (implementation depends on adapter)
            keyword_results = self._perform_keyword_search(
                collection_name=collection_name,
                query_text=query_text,
                limit=limit * 2,  # Get more results for better hybrid matching
                filter=filter,
                tenant_id=tenant_id
            )
            
            # Combine results
            combined_results = self._combine_results(
                vector_results=vector_results,
                keyword_results=keyword_results,
                min_keyword_score=min_keyword_score,
                min_vector_score=min_vector_score,
                min_combined_score=min_combined_score
            )
            
            # Sort by combined score (descending)
            combined_results.sort(key=lambda x: x.combined_score, reverse=True)
            
            # Limit results
            return combined_results[:limit]
        except Exception as e:
            logger.error(f"Failed to perform hybrid search in collection {collection_name}: {str(e)}")
            raise QueryError(f"Failed to perform hybrid search in collection {collection_name}: {str(e)}")
    
    def _perform_keyword_search(self,
                              collection_name: str,
                              query_text: str,
                              limit: int = 10,
                              filter: Optional[MetadataFilter] = None,
                              tenant_id: Optional[str] = None) -> List[SearchResult[T]]:
        """
        Perform keyword-based search.
        
        This method should be overridden by adapter-specific implementations.
        
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
        # Default implementation uses text-to-vector search
        # This should be overridden by adapter-specific implementations
        return self.adapter.search_by_text(
            collection_name=collection_name,
            query_text=query_text,
            limit=limit,
            filter=filter,
            tenant_id=tenant_id
        )
    
    def _combine_results(self,
                        vector_results: List[SearchResult[T]],
                        keyword_results: List[SearchResult[T]],
                        min_keyword_score: float = 0.0,
                        min_vector_score: float = 0.0,
                        min_combined_score: float = 0.0) -> List[HybridSearchResult[T]]:
        """
        Combine vector and keyword search results.
        
        Args:
            vector_results: Results from vector search.
            keyword_results: Results from keyword search.
            min_keyword_score: Minimum keyword score threshold (0.0 to 1.0).
            min_vector_score: Minimum vector score threshold (0.0 to 1.0).
            min_combined_score: Minimum combined score threshold (0.0 to 1.0).
            
        Returns:
            A list of hybrid search results.
        """
        # Create a dictionary of document IDs to vector scores
        vector_scores = {result.document.id: result.score for result in vector_results}
        
        # Create a dictionary of document IDs to keyword scores
        keyword_scores = {result.document.id: result.score for result in keyword_results}
        
        # Create a dictionary of document IDs to documents
        documents = {}
        for result in vector_results:
            documents[result.document.id] = result.document
        for result in keyword_results:
            documents[result.document.id] = result.document
        
        # Combine scores
        combined_results = []
        
        # Process all unique document IDs
        all_doc_ids = set(vector_scores.keys()) | set(keyword_scores.keys())
        
        for doc_id in all_doc_ids:
            # Get scores (default to 0.0 if not found)
            vector_score = vector_scores.get(doc_id, 0.0)
            keyword_score = keyword_scores.get(doc_id, 0.0)
            
            # Apply thresholds
            if vector_score < min_vector_score or keyword_score < min_keyword_score:
                continue
            
            # Combine scores
            combined_score = self.strategy.combine_scores(vector_score, keyword_score)
            
            # Apply combined threshold
            if combined_score < min_combined_score:
                continue
            
            # Create hybrid search result
            hybrid_result = HybridSearchResult(
                document=documents[doc_id],
                combined_score=combined_score,
                vector_score=vector_score,
                keyword_score=keyword_score,
                metadata={
                    "vector_score": vector_score,
                    "keyword_score": keyword_score
                }
            )
            
            combined_results.append(hybrid_result)
        
        return combined_results
