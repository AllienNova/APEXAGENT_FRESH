"""
Chroma Hybrid Search Implementation for Aideon AI Lite Vector Database

This module provides a concrete implementation of the HybridSearchEngine
for the Chroma adapter, enabling combined vector and keyword search capabilities.

The implementation leverages Chroma's search capabilities while adding custom
keyword search functionality to maintain enterprise-ready features including
multi-tenant isolation, comprehensive error handling, and high performance.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Union, Tuple

import numpy as np

from src.knowledge.vector_db.vector_database import (
    VectorDocument,
    SearchResult,
    MetadataFilter,
    QueryError,
)
from src.knowledge.vector_db.adapters.chroma.chroma_adapter import ChromaAdapter
from src.knowledge.vector_db.hybrid_search import (
    HybridSearchEngine,
    HybridSearchResult,
    HybridSearchStrategy,
    WeightedAverageStrategy,
)

logger = logging.getLogger(__name__)


class ChromaHybridSearchEngine(HybridSearchEngine[np.ndarray]):
    """
    Chroma-specific implementation of the HybridSearchEngine.
    
    Extends Chroma's capabilities with custom keyword search functionality.
    """
    
    def __init__(self, 
                adapter: ChromaAdapter,
                strategy: Optional[HybridSearchStrategy] = None):
        """
        Initialize a Chroma hybrid search engine.
        
        Args:
            adapter: The Chroma adapter.
            strategy: The strategy for combining scores (default: WeightedAverageStrategy).
        """
        super().__init__(adapter, strategy or WeightedAverageStrategy())
        self.chroma_adapter = adapter
    
    def _perform_keyword_search(self,
                              collection_name: str,
                              query_text: str,
                              limit: int = 10,
                              filter: Optional[MetadataFilter] = None,
                              tenant_id: Optional[str] = None) -> List[SearchResult[np.ndarray]]:
        """
        Perform keyword-based search using Chroma.
        
        This implementation uses Chroma's where filtering capabilities to perform
        keyword search on document content.
        
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
        try:
            # Get tenant-prefixed collection name
            prefixed_collection_name = self.chroma_adapter.get_tenant_prefixed_collection_name(
                collection_name, tenant_id
            )
            
            # Get collection
            try:
                collection = self.chroma_adapter.client.get_collection(name=prefixed_collection_name)
            except Exception:
                raise QueryError(f"Collection {collection_name} does not exist")
            
            # Split query into terms
            query_terms = query_text.lower().split()
            
            if not query_terms:
                # If no terms, return empty results
                return []
            
            # Get all documents from collection
            # Note: Chroma doesn't support text search directly, so we need to get all documents
            # and filter them manually
            results = collection.get(
                include=["documents", "metadatas", "embeddings"],
                limit=limit * 5  # Get more documents to ensure we have enough after filtering
            )
            
            # Check if we have results
            if not results["ids"] or len(results["ids"]) == 0:
                return []
            
            # Process results
            search_results = []
            
            for i, doc_id in enumerate(results["ids"]):
                # Get document data
                content = ""
                if "documents" in results and results["documents"] is not None and i < len(results["documents"]):
                    content = results["documents"][i] or ""
                
                # Skip if content is empty
                if not content:
                    continue
                
                # Calculate keyword score
                content_lower = content.lower()
                term_matches = sum(1 for term in query_terms if term in content_lower)
                
                # Skip if no matches
                if term_matches == 0:
                    continue
                
                # Calculate score (0.0 to 1.0)
                score = min(1.0, term_matches / len(query_terms))
                
                # Get metadata
                metadata = {}
                if "metadatas" in results and results["metadatas"] is not None and i < len(results["metadatas"]):
                    metadata = results["metadatas"][i] or {}
                
                # Get embedding
                embedding = None
                if "embeddings" in results and results["embeddings"] is not None and i < len(results["embeddings"]):
                    embedding_data = results["embeddings"][i]
                    if embedding_data is not None:
                        embedding = np.array(embedding_data).astype(np.float32)
                
                # Create document
                document = VectorDocument(
                    id=doc_id,
                    content=content,
                    embedding=embedding,
                    metadata=metadata,
                    tenant_id=tenant_id
                )
                
                # Create search result
                search_result = SearchResult(
                    document=document,
                    score=score,
                    metadata={"keyword_matches": term_matches}
                )
                
                search_results.append(search_result)
            
            # Apply metadata filter if provided
            if filter:
                search_results = self._apply_metadata_filter(search_results, filter)
            
            # Sort by score (descending)
            search_results.sort(key=lambda x: x.score, reverse=True)
            
            # Limit results
            return search_results[:limit]
        except Exception as e:
            logger.error(f"Failed to perform keyword search in collection {collection_name}: {str(e)}")
            raise QueryError(f"Failed to perform keyword search in collection {collection_name}: {str(e)}")
    
    def _apply_metadata_filter(self, 
                              results: List[SearchResult[np.ndarray]], 
                              filter: MetadataFilter) -> List[SearchResult[np.ndarray]]:
        """
        Apply metadata filter to search results.
        
        Args:
            results: The search results to filter.
            filter: The metadata filter to apply.
            
        Returns:
            Filtered search results.
        """
        filtered_results = []
        
        for result in results:
            metadata = result.document.metadata or {}
            
            # Check equals filters
            equals_match = True
            for key, value in filter.equals.items():
                if key not in metadata or metadata[key] != value:
                    equals_match = False
                    break
            
            if not equals_match:
                continue
            
            # Check not equals filters
            not_equals_match = True
            for key, value in filter.not_equals.items():
                if key in metadata and metadata[key] == value:
                    not_equals_match = False
                    break
            
            if not not_equals_match:
                continue
            
            # Check greater than filters
            gt_match = True
            for key, value in filter.greater_than.items():
                if key not in metadata or metadata[key] <= value:
                    gt_match = False
                    break
            
            if not gt_match:
                continue
            
            # Check less than filters
            lt_match = True
            for key, value in filter.less_than.items():
                if key not in metadata or metadata[key] >= value:
                    lt_match = False
                    break
            
            if not lt_match:
                continue
            
            # Check in list filters
            in_list_match = True
            for key, values in filter.in_list.items():
                if key not in metadata or metadata[key] not in values:
                    in_list_match = False
                    break
            
            if not in_list_match:
                continue
            
            # Check not in list filters
            not_in_list_match = True
            for key, values in filter.not_in_list.items():
                if key in metadata and metadata[key] in values:
                    not_in_list_match = False
                    break
            
            if not not_in_list_match:
                continue
            
            # All filters passed, add to filtered results
            filtered_results.append(result)
        
        return filtered_results
