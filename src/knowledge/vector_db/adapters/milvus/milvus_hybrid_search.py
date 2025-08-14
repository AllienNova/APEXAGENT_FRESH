"""
Milvus Hybrid Search Implementation for Aideon AI Lite Vector Database

This module provides a concrete implementation of the HybridSearchEngine
for the Milvus adapter, enabling combined vector and keyword search capabilities.

The implementation leverages Milvus's built-in hybrid search functionality
while maintaining enterprise-ready features including multi-tenant isolation,
comprehensive error handling, and high performance.
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
from src.knowledge.vector_db.adapters.milvus.milvus_adapter import MilvusAdapter
from src.knowledge.vector_db.hybrid_search import (
    HybridSearchEngine,
    HybridSearchResult,
    HybridSearchStrategy,
    WeightedAverageStrategy,
)

logger = logging.getLogger(__name__)


class MilvusHybridSearchEngine(HybridSearchEngine[np.ndarray]):
    """
    Milvus-specific implementation of the HybridSearchEngine.
    
    Leverages Milvus's built-in hybrid search capabilities for optimal performance.
    """
    
    def __init__(self, 
                adapter: MilvusAdapter,
                strategy: Optional[HybridSearchStrategy] = None):
        """
        Initialize a Milvus hybrid search engine.
        
        Args:
            adapter: The Milvus adapter.
            strategy: The strategy for combining scores (default: WeightedAverageStrategy).
        """
        super().__init__(adapter, strategy or WeightedAverageStrategy())
        self.milvus_adapter = adapter
    
    def _perform_keyword_search(self,
                              collection_name: str,
                              query_text: str,
                              limit: int = 10,
                              filter: Optional[MetadataFilter] = None,
                              tenant_id: Optional[str] = None) -> List[SearchResult[np.ndarray]]:
        """
        Perform keyword-based search using Milvus.
        
        This implementation uses Milvus's scalar filtering capabilities to perform
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
            prefixed_collection_name = self.milvus_adapter.get_tenant_prefixed_collection_name(
                collection_name, tenant_id
            )
            
            # Prepare query expression for keyword search
            # Split query into terms and create OR conditions for each term
            query_terms = [term.lower() for term in re.findall(r'\b\w+\b', query_text)]
            
            if not query_terms:
                # If no terms, return empty results
                return []
            
            # Create expression for keyword search
            # Format: "content like '%term1%' or content like '%term2%' or ..."
            keyword_expressions = []
            for term in query_terms:
                # Escape single quotes in term
                escaped_term = term.replace("'", "\\'")
                keyword_expressions.append(f"content like '%{escaped_term}%'")
            
            keyword_expression = " or ".join(keyword_expressions)
            
            # Combine with existing filter if provided
            expression = keyword_expression
            if filter:
                filter_expression = self.milvus_adapter._convert_metadata_filter(filter)
                if filter_expression:
                    expression = f"({keyword_expression}) and ({filter_expression})"
            
            # Execute search
            results = self.milvus_adapter._search_by_expression(
                collection_name=collection_name,
                expression=expression,
                limit=limit,
                tenant_id=tenant_id
            )
            
            # Calculate keyword scores based on term frequency and position
            for result in results:
                content = result.document.content.lower()
                
                # Initialize metrics for scoring
                term_matches = 0
                term_positions = []
                exact_phrase_bonus = 0
                
                # Calculate term frequency
                for term in query_terms:
                    # Count occurrences of the term
                    term_count = content.count(term)
                    if term_count > 0:
                        term_matches += term_count
                        
                        # Find positions of term occurrences
                        pos = 0
                        while True:
                            pos = content.find(term, pos)
                            if pos == -1:
                                break
                            term_positions.append(pos)
                            pos += len(term)
                
                # Check for exact phrase matches (terms appearing consecutively)
                if len(query_terms) > 1 and query_text.lower() in content:
                    exact_phrase_bonus = 0.2  # Bonus for exact phrase match
                
                # Calculate proximity score (how close terms appear to each other)
                proximity_score = 0
                if len(term_positions) > 1:
                    # Sort positions
                    term_positions.sort()
                    
                    # Calculate average distance between consecutive terms
                    avg_distance = sum(term_positions[i+1] - term_positions[i] 
                                      for i in range(len(term_positions)-1)) / (len(term_positions)-1)
                    
                    # Normalize: closer terms = higher score
                    proximity_score = max(0, min(0.1, 50 / (avg_distance + 10)))
                
                # Calculate base score from term frequency
                # Ensure at least a minimum score for any match
                base_score = 0.1 + 0.7 * min(1.0, term_matches / (len(query_terms) * 2))
                
                # Combine scores with bonuses
                score = min(1.0, base_score + exact_phrase_bonus + proximity_score)
                
                # Ensure score is never zero for matched documents
                # (they wouldn't be in results if they didn't match)
                score = max(0.1, score)
                
                # Set the score
                result.score = score
                
                # Add scoring details to metadata for debugging and transparency
                result.metadata["keyword_match_details"] = {
                    "term_matches": term_matches,
                    "total_terms": len(query_terms),
                    "exact_phrase_bonus": exact_phrase_bonus,
                    "proximity_score": proximity_score,
                    "base_score": base_score,
                    "final_score": score
                }
            
            # Sort by score (descending)
            results.sort(key=lambda x: x.score, reverse=True)
            
            return results
        except Exception as e:
            logger.error(f"Failed to perform keyword search in collection {collection_name}: {str(e)}")
            raise QueryError(f"Failed to perform keyword search in collection {collection_name}: {str(e)}")
