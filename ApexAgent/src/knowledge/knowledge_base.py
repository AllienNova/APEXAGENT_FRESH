"""
Knowledge Base for Dr. TARDIS

This module provides knowledge base functionality for the Dr. TARDIS system,
including knowledge storage, retrieval, and connection to the ApexAgent
knowledge base.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import logging
import json
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class KnowledgeBase:
    """
    Provides knowledge base functionality for the Dr. TARDIS system.
    
    This class manages knowledge items, including storage, retrieval,
    and search capabilities.
    
    Attributes:
        logger (logging.Logger): Logger for knowledge base
        knowledge_items (Dict): Dictionary of knowledge items
        data_path (str): Path to the data directory
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the Knowledge Base.
        
        Args:
            data_path: Path to the data directory (default: None)
        """
        self.logger = logging.getLogger("KnowledgeBase")
        
        # Set default data path if not provided
        if data_path is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(module_dir, "data", "knowledge")
        else:
            self.data_path = data_path
            
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize knowledge items
        self.knowledge_items = self._load_knowledge_items()
        
        self.logger.info("KnowledgeBase initialized")
    
    def _load_knowledge_items(self) -> Dict[str, Any]:
        """
        Load knowledge items from data files.
        
        Returns:
            Dict: Dictionary of knowledge items
        """
        items = {}
        
        # Load from knowledge items directory if it exists
        items_dir = os.path.join(self.data_path, "items")
        os.makedirs(items_dir, exist_ok=True)
        
        for filename in os.listdir(items_dir):
            if filename.endswith(".json"):
                item_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(items_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        item_data = json.load(f)
                    items[item_id] = item_data
                except Exception as e:
                    self.logger.error(f"Error loading knowledge item {item_id}: {e}")
        
        self.logger.info(f"Loaded {len(items)} knowledge items")
        return items
    
    def _save_knowledge_item(self, item_id: str, item_data: Dict[str, Any]):
        """
        Save knowledge item to file.
        
        Args:
            item_id: Knowledge item ID
            item_data: Knowledge item data
        """
        items_dir = os.path.join(self.data_path, "items")
        os.makedirs(items_dir, exist_ok=True)
        
        file_path = os.path.join(items_dir, f"{item_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(item_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving knowledge item {item_id}: {e}")
    
    def add_knowledge_item(self, item: Dict[str, Any]):
        """
        Add a knowledge item to the knowledge base.
        
        Args:
            item: Knowledge item data
        """
        # Ensure item has an ID
        if "id" not in item:
            item_id = hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()
            item["id"] = item_id
        else:
            item_id = item["id"]
        
        # Add timestamp if not present
        if "timestamp" not in item:
            item["timestamp"] = datetime.now().isoformat()
        
        # Add item to knowledge items
        self.knowledge_items[item_id] = item
        
        # Save item to file
        self._save_knowledge_item(item_id, item)
        
        self.logger.info(f"Added knowledge item: {item_id}")
    
    def get_knowledge_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a knowledge item by ID.
        
        Args:
            item_id: Knowledge item ID
            
        Returns:
            Dict: Knowledge item data or None if not found
        """
        return self.knowledge_items.get(item_id)
    
    def update_knowledge_item(self, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a knowledge item.
        
        Args:
            item_id: Knowledge item ID
            item_data: Updated knowledge item data
            
        Returns:
            Dict: Updated knowledge item data or None if not found
        """
        if item_id not in self.knowledge_items:
            self.logger.warning(f"Knowledge item not found: {item_id}")
            return None
        
        # Update item
        item = self.knowledge_items[item_id]
        for key, value in item_data.items():
            if key != "id":  # Don't update ID
                item[key] = value
        
        # Update timestamp
        item["updated_at"] = datetime.now().isoformat()
        
        # Save updated item
        self._save_knowledge_item(item_id, item)
        
        self.logger.info(f"Updated knowledge item: {item_id}")
        return item
    
    def delete_knowledge_item(self, item_id: str) -> bool:
        """
        Delete a knowledge item.
        
        Args:
            item_id: Knowledge item ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        if item_id not in self.knowledge_items:
            self.logger.warning(f"Knowledge item not found: {item_id}")
            return False
        
        # Remove from knowledge items
        del self.knowledge_items[item_id]
        
        # Remove file if it exists
        file_path = os.path.join(self.data_path, "items", f"{item_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                self.logger.error(f"Error removing knowledge item file: {e}")
        
        self.logger.info(f"Deleted knowledge item: {item_id}")
        return True
    
    def search_knowledge(self, query: str, tags: List[str] = None, 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search knowledge items.
        
        Args:
            query: Search query
            tags: Optional list of tags to filter by
            limit: Maximum number of results to return
            
        Returns:
            List: List of matching knowledge items
        """
        results = []
        
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()
        
        # Search all knowledge items
        for item_id, item in self.knowledge_items.items():
            # Calculate relevance score
            relevance = 0
            
            # Check title
            title = item.get("title", "").lower()
            if query_lower in title:
                # Higher relevance for title matches
                relevance += 0.5
                # Even higher if it's an exact match
                if query_lower == title:
                    relevance += 0.3
            
            # Check content
            content = item.get("content", "").lower()
            if query_lower in content:
                # Lower relevance for content matches
                relevance += 0.3
            
            # Check tags
            item_tags = [tag.lower() for tag in item.get("tags", [])]
            for word in query_lower.split():
                if word in item_tags:
                    # Medium relevance for tag matches
                    relevance += 0.4
            
            # Filter by tags if provided
            if tags:
                # Convert tags to lowercase for case-insensitive comparison
                tags_lower = [tag.lower() for tag in tags]
                
                # Check if item has all required tags
                has_all_tags = all(tag in item_tags for tag in tags_lower)
                
                if not has_all_tags:
                    continue
            
            # Add to results if relevant
            if relevance > 0:
                # Add a copy of the item with relevance score
                result = item.copy()
                result["relevance"] = relevance
                results.append(result)
        
        # Sort by relevance
        sorted_results = sorted(results, key=lambda x: x["relevance"], reverse=True)
        
        # Limit results
        return sorted_results[:limit]
    
    def get_all_knowledge_items(self) -> List[Dict[str, Any]]:
        """
        Get all knowledge items.
        
        Returns:
            List: List of all knowledge items
        """
        return list(self.knowledge_items.values())
    
    def get_knowledge_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """
        Get knowledge items by tags.
        
        Args:
            tags: List of tags to filter by
            
        Returns:
            List: List of matching knowledge items
        """
        results = []
        
        # Convert tags to lowercase for case-insensitive comparison
        tags_lower = [tag.lower() for tag in tags]
        
        # Filter knowledge items by tags
        for item_id, item in self.knowledge_items.items():
            item_tags = [tag.lower() for tag in item.get("tags", [])]
            
            # Check if item has any of the required tags
            has_any_tag = any(tag in item_tags for tag in tags_lower)
            
            if has_any_tag:
                results.append(item)
        
        return results
    
    def get_recent_knowledge_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent knowledge items.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List: List of recent knowledge items
        """
        # Sort by timestamp
        sorted_items = sorted(
            self.knowledge_items.values(),
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        return sorted_items[:limit]


class ApexAgentKnowledgeConnector:
    """
    Connects to the ApexAgent knowledge base.
    
    This class provides methods to query and retrieve information from
    the ApexAgent knowledge base.
    
    Attributes:
        logger (logging.Logger): Logger for knowledge connector
        api_client: API client for ApexAgent
    """
    
    def __init__(self, api_client=None):
        """
        Initialize the ApexAgent Knowledge Connector.
        
        Args:
            api_client: API client for ApexAgent (default: None)
        """
        self.logger = logging.getLogger("ApexAgentKnowledgeConnector")
        self.api_client = api_client
        
        self.logger.info("ApexAgentKnowledgeConnector initialized")
    
    def query_knowledge_base(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query the ApexAgent knowledge base.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List: List of matching knowledge items
        """
        try:
            # If API client is available, use it to query
            if self.api_client:
                response = self.api_client.query_knowledge(query, limit=limit)
                return response.get("results", [])
            else:
                # Simulate response for testing
                self.logger.warning("API client not available, returning simulated results")
                return [
                    {
                        "id": f"simulated_{i}",
                        "title": f"Simulated Result {i} for '{query}'",
                        "content": f"This is a simulated result for the query '{query}'.",
                        "relevance": 0.9 - (i * 0.1)
                    }
                    for i in range(min(5, limit))
                ]
        except Exception as e:
            self.logger.error(f"Error querying knowledge base: {e}")
            return []
    
    def retrieve_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from the ApexAgent knowledge base.
        
        Args:
            document_id: Document ID
            
        Returns:
            Dict: Document data or None if not found
        """
        try:
            # If API client is available, use it to retrieve document
            if self.api_client:
                response = self.api_client.get_document(document_id)
                return response
            else:
                # Simulate response for testing
                self.logger.warning("API client not available, returning simulated document")
                return {
                    "id": document_id,
                    "title": f"Simulated Document {document_id}",
                    "content": f"This is a simulated document with ID {document_id}.",
                    "metadata": {
                        "author": "Simulated Author",
                        "created_at": datetime.now().isoformat()
                    }
                }
        except Exception as e:
            self.logger.error(f"Error retrieving document: {e}")
            return None
    
    def get_related_documents(self, document_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get documents related to a specific document.
        
        Args:
            document_id: Document ID
            limit: Maximum number of related documents to return
            
        Returns:
            List: List of related documents
        """
        try:
            # If API client is available, use it to get related documents
            if self.api_client:
                response = self.api_client.get_related_documents(document_id, limit=limit)
                return response.get("results", [])
            else:
                # Simulate response for testing
                self.logger.warning("API client not available, returning simulated related documents")
                return [
                    {
                        "id": f"related_{document_id}_{i}",
                        "title": f"Related Document {i} for {document_id}",
                        "content": f"This is a simulated related document for {document_id}.",
                        "relevance": 0.9 - (i * 0.1)
                    }
                    for i in range(min(3, limit))
                ]
        except Exception as e:
            self.logger.error(f"Error getting related documents: {e}")
            return []
    
    async def async_query_knowledge_base(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Asynchronously query the ApexAgent knowledge base.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List: List of matching knowledge items
        """
        try:
            # If API client is available and supports async, use it
            if self.api_client and hasattr(self.api_client, "async_query_knowledge"):
                response = await self.api_client.async_query_knowledge(query, limit=limit)
                return response.get("results", [])
            else:
                # Fall back to synchronous query
                return self.query_knowledge_base(query, limit)
        except Exception as e:
            self.logger.error(f"Error in async query of knowledge base: {e}")
            return []
    
    async def async_retrieve_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Asynchronously retrieve a document from the ApexAgent knowledge base.
        
        Args:
            document_id: Document ID
            
        Returns:
            Dict: Document data or None if not found
        """
        try:
            # If API client is available and supports async, use it
            if self.api_client and hasattr(self.api_client, "async_get_document"):
                response = await self.api_client.async_get_document(document_id)
                return response
            else:
                # Fall back to synchronous retrieval
                return self.retrieve_document(document_id)
        except Exception as e:
            self.logger.error(f"Error in async document retrieval: {e}")
            return None


# Example usage
def example_usage():
    # Create knowledge base
    kb = KnowledgeBase()
    
    # Add knowledge items
    kb.add_knowledge_item({
        "title": "Python Programming",
        "content": "Python is a high-level programming language.",
        "tags": ["python", "programming"]
    })
    
    kb.add_knowledge_item({
        "title": "Machine Learning",
        "content": "Machine learning is a subset of artificial intelligence.",
        "tags": ["ml", "ai", "data science"]
    })
    
    # Search knowledge
    results = kb.search_knowledge("python programming")
    print(f"Search results: {len(results)}")
    for result in results:
        print(f"- {result['title']} (relevance: {result['relevance']})")
    
    # Create ApexAgent knowledge connector
    connector = ApexAgentKnowledgeConnector()
    
    # Query knowledge base
    results = connector.query_knowledge_base("machine learning")
    print(f"ApexAgent query results: {len(results)}")
    for result in results:
        print(f"- {result['title']} (relevance: {result['relevance']})")

if __name__ == "__main__":
    example_usage()
