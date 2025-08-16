"""
Context-Aware Knowledge Retrieval for Dr. TARDIS

This module implements context-aware knowledge retrieval for the Dr. TARDIS
knowledge integration system, ensuring that queries and results are dynamically
adapted based on conversation and project context.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import logging
import json
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime
import hashlib
import uuid
import heapq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ContextAwareRetrieval:
    """
    Provides context-aware knowledge retrieval for the Dr. TARDIS system.
    
    This class enhances knowledge retrieval by incorporating conversation
    context, project memory, and user preferences to improve the relevance
    and personalization of results.
    
    Attributes:
        logger (logging.Logger): Logger for context-aware retrieval
        conversation_contexts (Dict): Dictionary of conversation contexts
        project_memories (Dict): Dictionary of project memories
        user_preferences (Dict): Dictionary of user preferences
        context_history (Dict): Dictionary of context history
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the Context-Aware Retrieval system.
        
        Args:
            data_path: Path to the data directory (default: None)
        """
        self.logger = logging.getLogger("ContextAwareRetrieval")
        
        # Set default data path if not provided
        if data_path is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(module_dir, "data", "context")
        else:
            self.data_path = data_path
            
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize conversation contexts
        self.conversation_contexts = self._load_conversation_contexts()
        
        # Initialize project memories
        self.project_memories = self._load_project_memories()
        
        # Initialize user preferences
        self.user_preferences = self._load_user_preferences()
        
        # Initialize context history
        self.context_history = {}
        
        self.logger.info("ContextAwareRetrieval initialized")
    
    def _load_conversation_contexts(self) -> Dict[str, Any]:
        """
        Load conversation contexts from data files.
        
        Returns:
            Dict: Dictionary of conversation contexts
        """
        contexts = {}
        
        # Load from conversation contexts directory if it exists
        contexts_dir = os.path.join(self.data_path, "conversations")
        os.makedirs(contexts_dir, exist_ok=True)
        
        for filename in os.listdir(contexts_dir):
            if filename.endswith(".json"):
                context_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(contexts_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        context_data = json.load(f)
                    contexts[context_id] = context_data
                except Exception as e:
                    self.logger.error(f"Error loading conversation context {context_id}: {e}")
        
        self.logger.info(f"Loaded {len(contexts)} conversation contexts")
        return contexts
    
    def _load_project_memories(self) -> Dict[str, Any]:
        """
        Load project memories from data files.
        
        Returns:
            Dict: Dictionary of project memories
        """
        memories = {}
        
        # Load from project memories directory if it exists
        memories_dir = os.path.join(self.data_path, "projects")
        os.makedirs(memories_dir, exist_ok=True)
        
        for filename in os.listdir(memories_dir):
            if filename.endswith(".json"):
                project_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(memories_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        memory_data = json.load(f)
                    memories[project_id] = memory_data
                except Exception as e:
                    self.logger.error(f"Error loading project memory {project_id}: {e}")
        
        self.logger.info(f"Loaded {len(memories)} project memories")
        return memories
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """
        Load user preferences from data files.
        
        Returns:
            Dict: Dictionary of user preferences
        """
        preferences = {}
        
        # Load from user preferences directory if it exists
        preferences_dir = os.path.join(self.data_path, "users")
        os.makedirs(preferences_dir, exist_ok=True)
        
        for filename in os.listdir(preferences_dir):
            if filename.endswith(".json"):
                user_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(preferences_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        preference_data = json.load(f)
                    preferences[user_id] = preference_data
                except Exception as e:
                    self.logger.error(f"Error loading user preferences {user_id}: {e}")
        
        self.logger.info(f"Loaded {len(preferences)} user preferences")
        return preferences
    
    def _save_conversation_context(self, context_id: str, context_data: Dict[str, Any]):
        """
        Save conversation context to file.
        
        Args:
            context_id: Conversation context ID
            context_data: Conversation context data
        """
        file_path = os.path.join(self.data_path, "conversations", f"{context_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(context_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving conversation context {context_id}: {e}")
    
    def _save_project_memory(self, project_id: str, memory_data: Dict[str, Any]):
        """
        Save project memory to file.
        
        Args:
            project_id: Project ID
            memory_data: Project memory data
        """
        file_path = os.path.join(self.data_path, "projects", f"{project_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving project memory {project_id}: {e}")
    
    def _save_user_preferences(self, user_id: str, preference_data: Dict[str, Any]):
        """
        Save user preferences to file.
        
        Args:
            user_id: User ID
            preference_data: User preference data
        """
        file_path = os.path.join(self.data_path, "users", f"{user_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(preference_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving user preferences {user_id}: {e}")
    
    async def enhance_query(self, query: str, context: Dict[str, Any]) -> str:
        """
        Enhance a query with context information.
        
        Args:
            query: Original query string
            context: Context information
            
        Returns:
            str: Enhanced query
        """
        # Extract context information
        conversation_id = context.get("conversation_id")
        project_id = context.get("project_id")
        user_id = context.get("user_id")
        
        # Initialize enhanced query with original query
        enhanced_query = query
        
        # Add context from conversation history if available
        if conversation_id and conversation_id in self.conversation_contexts:
            conversation = self.conversation_contexts[conversation_id]
            
            # Get recent topics from conversation
            recent_topics = self._extract_recent_topics(conversation)
            
            # Check if query is a follow-up question
            if self._is_followup_question(query):
                # Add context from previous messages
                recent_messages = conversation.get("messages", [])[-3:]
                context_additions = []
                
                for msg in recent_messages:
                    if msg.get("role") == "user":
                        context_additions.append(msg.get("content", ""))
                
                if context_additions:
                    # Add context to query
                    enhanced_query = f"{enhanced_query} [Context: {' '.join(context_additions)}]"
        
        # Add context from project memory if available
        if project_id and project_id in self.project_memories:
            project = self.project_memories[project_id]
            
            # Get key information from project memory
            key_info = project.get("key_information", {})
            
            # Check if query is related to project information
            project_related = False
            for key, value in key_info.items():
                if key.lower() in query.lower() or value.lower() in query.lower():
                    project_related = True
                    break
            
            if project_related:
                # Add project context to query
                project_context = f"Project: {project.get('name', project_id)}"
                if "description" in project:
                    project_context += f", {project['description']}"
                
                enhanced_query = f"{enhanced_query} [Project Context: {project_context}]"
        
        # Add context from user preferences if available
        if user_id and user_id in self.user_preferences:
            preferences = self.user_preferences[user_id]
            
            # Get relevant preferences
            relevant_prefs = {}
            for key, value in preferences.items():
                if key.lower() in query.lower():
                    relevant_prefs[key] = value
            
            if relevant_prefs:
                # Add user preference context to query
                pref_context = ", ".join([f"{k}: {v}" for k, v in relevant_prefs.items()])
                enhanced_query = f"{enhanced_query} [User Preferences: {pref_context}]"
        
        # Log the enhancement
        if enhanced_query != query:
            self.logger.debug(f"Enhanced query: {query} -> {enhanced_query}")
        
        return enhanced_query
    
    def _extract_recent_topics(self, conversation: Dict[str, Any]) -> List[str]:
        """
        Extract recent topics from a conversation.
        
        Args:
            conversation: Conversation data
            
        Returns:
            List: Recent topics
        """
        topics = []
        
        # Get recent messages
        messages = conversation.get("messages", [])[-5:]
        
        # Extract topics from messages
        for msg in messages:
            content = msg.get("content", "")
            
            # Simple topic extraction (could be enhanced with NLP)
            sentences = content.split(".")
            for sentence in sentences:
                words = sentence.strip().split()
                if len(words) > 2:
                    # Consider the first 3 words as a potential topic
                    topic = " ".join(words[:3])
                    topics.append(topic)
        
        return topics
    
    def _is_followup_question(self, query: str) -> bool:
        """
        Check if a query is a follow-up question.
        
        Args:
            query: Query string
            
        Returns:
            bool: True if query is a follow-up question
        """
        # Check for pronouns and other follow-up indicators
        followup_indicators = [
            "it", "this", "that", "they", "them", "these", "those",
            "he", "she", "his", "her", "their", "its",
            "what about", "how about", "what if", "and", "also", "too",
            "why", "how", "when", "where", "who"
        ]
        
        query_lower = query.lower()
        
        # Check if query starts with a follow-up indicator
        for indicator in followup_indicators:
            if query_lower.startswith(indicator + " ") or query_lower == indicator:
                return True
        
        # Check if query is very short (likely a follow-up)
        if len(query_lower.split()) <= 3:
            return True
        
        return False
    
    async def process_results(self, results: List[Dict[str, Any]], 
                            context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process results with context awareness.
        
        Args:
            results: List of result items
            context: Context information
            
        Returns:
            List: Processed results with context-based relevance
        """
        # Extract context information
        conversation_id = context.get("conversation_id")
        project_id = context.get("project_id")
        user_id = context.get("user_id")
        query = context.get("query", "")
        
        # If no results, return empty list
        if not results:
            return []
        
        # Apply context-based relevance scoring
        scored_results = []
        for result in results:
            # Start with the base relevance score
            relevance = result.get("relevance", 0.5)
            
            # Apply conversation context adjustments
            if conversation_id and conversation_id in self.conversation_contexts:
                conversation = self.conversation_contexts[conversation_id]
                
                # Boost relevance for items related to recent messages
                messages = conversation.get("messages", [])[-5:]
                for msg in messages:
                    content = msg.get("content", "")
                    if content and content.lower() in result.get("content", "").lower():
                        relevance += 0.1
                
                # Boost relevance for items related to conversation topics
                topics = conversation.get("topics", [])
                for topic in topics:
                    if topic.lower() in result.get("title", "").lower() or topic.lower() in result.get("content", "").lower():
                        relevance += 0.1
            
            # Apply project memory adjustments
            if project_id and project_id in self.project_memories:
                project = self.project_memories[project_id]
                
                # Boost relevance for items related to project key information
                key_info = project.get("key_information", {})
                for key, value in key_info.items():
                    if key.lower() in result.get("title", "").lower() or key.lower() in result.get("content", "").lower():
                        relevance += 0.1
                    if value.lower() in result.get("title", "").lower() or value.lower() in result.get("content", "").lower():
                        relevance += 0.1
                
                # Boost relevance for items related to project artifacts
                artifacts = project.get("artifacts", [])
                for artifact in artifacts:
                    if artifact.get("name", "").lower() in result.get("title", "").lower() or artifact.get("name", "").lower() in result.get("content", "").lower():
                        relevance += 0.1
            
            # Apply user preference adjustments
            if user_id and user_id in self.user_preferences:
                preferences = self.user_preferences[user_id]
                
                # Boost relevance for items related to preferred topics
                preferred_topics = preferences.get("preferred_topics", [])
                for topic in preferred_topics:
                    if topic.lower() in result.get("title", "").lower() or topic.lower() in result.get("content", "").lower():
                        relevance += 0.1
                
                # Adjust relevance based on preferred content types
                preferred_types = preferences.get("preferred_content_types", [])
                if result.get("type") in preferred_types:
                    relevance += 0.1
            
            # Cap relevance at 1.0
            result["relevance"] = min(1.0, relevance)
            scored_results.append(result)
        
        # Sort by relevance
        sorted_results = sorted(scored_results, key=lambda x: x["relevance"], reverse=True)
        
        # Apply diversity to results (avoid too many similar results)
        diverse_results = self._diversify_results(sorted_results, query)
        
        return diverse_results
    
    def _diversify_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Diversify results to avoid redundancy.
        
        Args:
            results: List of result items sorted by relevance
            query: Original query string
            
        Returns:
            List: Diversified results
        """
        if len(results) <= 3:
            return results
        
        diverse_results = []
        seen_types = set()
        
        # Always include the top result
        diverse_results.append(results[0])
        seen_types.add(results[0].get("type", "unknown"))
        
        # Add remaining results with diversity
        for result in results[1:]:
            result_type = result.get("type", "unknown")
            
            # Prioritize diverse types
            if result_type not in seen_types:
                diverse_results.append(result)
                seen_types.add(result_type)
                continue
            
            # Check content similarity with existing results
            is_similar = False
            for existing in diverse_results:
                similarity = self._calculate_similarity(existing, result)
                if similarity > 0.7:  # Threshold for similarity
                    is_similar = True
                    break
            
            if not is_similar:
                diverse_results.append(result)
        
        # Ensure we have enough results
        if len(diverse_results) < min(5, len(results)):
            # Add more results based on relevance
            for result in results:
                if result not in diverse_results and len(diverse_results) < min(5, len(results)):
                    diverse_results.append(result)
        
        return diverse_results
    
    def _calculate_similarity(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> float:
        """
        Calculate similarity between two items.
        
        Args:
            item1: First item
            item2: Second item
            
        Returns:
            float: Similarity score (0-1)
        """
        # Simple similarity calculation based on content overlap
        content1 = (item1.get("title", "") + " " + item1.get("content", "")).lower()
        content2 = (item2.get("title", "") + " " + item2.get("content", "")).lower()
        
        # Split into words
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0
        
        return intersection / union
    
    async def update_context(self, query: str, results: List[Dict[str, Any]], 
                           context: Dict[str, Any]):
        """
        Update context with query and results.
        
        Args:
            query: Query string
            results: Query results
            context: Context information
        """
        # Extract context information
        conversation_id = context.get("conversation_id")
        project_id = context.get("project_id")
        user_id = context.get("user_id")
        
        # Update conversation context
        if conversation_id:
            await self.update_conversation_context(conversation_id, query, results, context)
        
        # Update project memory
        if project_id:
            await self.update_project_memory(project_id, query, results, context)
        
        # Update user preferences
        if user_id:
            await self.update_user_preferences(user_id, query, results, context)
        
        # Update context history
        context_id = context.get("context_id", str(uuid.uuid4()))
        if context_id not in self.context_history:
            self.context_history[context_id] = []
        
        # Add to context history
        self.context_history[context_id].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results": [{"id": r.get("id"), "title": r.get("title"), "relevance": r.get("relevance")} for r in results[:3]]
        })
        
        # Trim history if it exceeds max size
        if len(self.context_history[context_id]) > 100:
            self.context_history[context_id] = self.context_history[context_id][-100:]
    
    async def update_conversation_context(self, conversation_id: str, query: str, 
                                        results: List[Dict[str, Any]], context: Dict[str, Any]):
        """
        Update conversation context with query and results.
        
        Args:
            conversation_id: Conversation ID
            query: Query string
            results: Query results
            context: Context information
        """
        # Initialize conversation context if not exists
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = {
                "id": conversation_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "topics": [],
                "entities": [],
                "last_updated": datetime.now().isoformat()
            }
        
        conversation = self.conversation_contexts[conversation_id]
        
        # Add query as user message
        conversation["messages"].append({
            "role": "user",
            "content": query,
            "timestamp": datetime.now().isoformat()
        })
        
        # Add results as assistant message
        if results:
            # Create a summary of the results
            result_summary = ""
            for result in results[:3]:
                result_summary += f"{result.get('title', 'Untitled')}: {result.get('content', '')[:100]}...\n"
            
            conversation["messages"].append({
                "role": "assistant",
                "content": result_summary,
                "timestamp": datetime.now().isoformat()
            })
        
        # Extract and update topics
        new_topics = self._extract_topics(query, results)
        for topic in new_topics:
            if topic not in conversation["topics"]:
                conversation["topics"].append(topic)
        
        # Extract and update entities
        new_entities = self._extract_entities(query, results)
        for entity in new_entities:
            if entity not in conversation["entities"]:
                conversation["entities"].append(entity)
        
        # Update last updated timestamp
        conversation["last_updated"] = datetime.now().isoformat()
        
        # Save conversation context
        self._save_conversation_context(conversation_id, conversation)
    
    async def update_project_memory(self, project_id: str, query: str, 
                                  results: List[Dict[str, Any]], context: Dict[str, Any]):
        """
        Update project memory with query and results.
        
        Args:
            project_id: Project ID
            query: Query string
            results: Query results
            context: Context information
        """
        # Initialize project memory if not exists
        if project_id not in self.project_memories:
            self.project_memories[project_id] = {
                "id": project_id,
                "created_at": datetime.now().isoformat(),
                "name": project_id,
                "queries": [],
                "key_information": {},
                "artifacts": [],
                "decisions": [],
                "last_updated": datetime.now().isoformat()
            }
        
        project = self.project_memories[project_id]
        
        # Add query to project memory
        project["queries"].append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "result_count": len(results)
        })
        
        # Trim queries if they exceed max size
        if len(project["queries"]) > 100:
            project["queries"] = project["queries"][-100:]
        
        # Extract key information from results
        for result in results[:5]:  # Consider top 5 results
            if result.get("type") == "key_information" and "key" in result and "value" in result:
                project["key_information"][result["key"]] = result["value"]
        
        # Check for artifacts in context
        if "artifacts" in context:
            for artifact in context["artifacts"]:
                # Check if artifact already exists
                exists = False
                for existing in project["artifacts"]:
                    if existing.get("id") == artifact.get("id"):
                        exists = True
                        # Update existing artifact
                        existing.update(artifact)
                        break
                
                if not exists:
                    # Add new artifact
                    project["artifacts"].append(artifact)
        
        # Check for decisions in context
        if "decision" in context:
            project["decisions"].append({
                "decision": context["decision"],
                "timestamp": datetime.now().isoformat(),
                "query": query
            })
        
        # Update last updated timestamp
        project["last_updated"] = datetime.now().isoformat()
        
        # Save project memory
        self._save_project_memory(project_id, project)
    
    async def update_user_preferences(self, user_id: str, query: str, 
                                    results: List[Dict[str, Any]], context: Dict[str, Any]):
        """
        Update user preferences with query and results.
        
        Args:
            user_id: User ID
            query: Query string
            results: Query results
            context: Context information
        """
        # Initialize user preferences if not exists
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "id": user_id,
                "created_at": datetime.now().isoformat(),
                "preferred_topics": [],
                "preferred_content_types": [],
                "interaction_history": [],
                "last_updated": datetime.now().isoformat()
            }
        
        preferences = self.user_preferences[user_id]
        
        # Add to interaction history
        preferences["interaction_history"].append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "result_count": len(results)
        })
        
        # Trim interaction history if it exceeds max size
        if len(preferences["interaction_history"]) > 100:
            preferences["interaction_history"] = preferences["interaction_history"][-100:]
        
        # Update preferred topics based on successful queries
        if results:
            # Extract topics from query and results
            topics = self._extract_topics(query, results)
            
            # Update preferred topics
            for topic in topics:
                if topic not in preferences["preferred_topics"]:
                    preferences["preferred_topics"].append(topic)
            
            # Limit preferred topics to top 20
            if len(preferences["preferred_topics"]) > 20:
                preferences["preferred_topics"] = preferences["preferred_topics"][-20:]
            
            # Update preferred content types
            for result in results[:3]:  # Consider top 3 results
                result_type = result.get("type")
                if result_type and result_type not in preferences["preferred_content_types"]:
                    preferences["preferred_content_types"].append(result_type)
        
        # Update last updated timestamp
        preferences["last_updated"] = datetime.now().isoformat()
        
        # Save user preferences
        self._save_user_preferences(user_id, preferences)
    
    def _extract_topics(self, query: str, results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract topics from query and results.
        
        Args:
            query: Query string
            results: Query results
            
        Returns:
            List: Extracted topics
        """
        topics = []
        
        # Extract from query (simple approach)
        query_words = query.lower().split()
        if len(query_words) >= 3:
            topics.append(" ".join(query_words[:3]))
        
        # Extract from results
        for result in results[:3]:  # Consider top 3 results
            # Add result title as a topic
            title = result.get("title", "").lower()
            if title and len(title.split()) <= 5:
                topics.append(title)
            
            # Extract from tags if available
            tags = result.get("tags", [])
            for tag in tags:
                if tag.lower() not in topics:
                    topics.append(tag.lower())
        
        return topics[:5]  # Limit to top 5 topics
    
    def _extract_entities(self, query: str, results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract entities from query and results.
        
        Args:
            query: Query string
            results: Query results
            
        Returns:
            List: Extracted entities
        """
        entities = []
        
        # Simple entity extraction (could be enhanced with NLP)
        # Look for capitalized words as potential entities
        words = query.split()
        for word in words:
            if word and len(word) > 1 and word[0].isupper():
                entities.append(word)
        
        # Extract from results
        for result in results[:3]:  # Consider top 3 results
            # Extract from title
            title_words = result.get("title", "").split()
            for word in title_words:
                if word and len(word) > 1 and word[0].isupper() and word not in entities:
                    entities.append(word)
            
            # Extract from content (simple approach)
            content = result.get("content", "")
            content_words = content.split()
            for word in content_words:
                if word and len(word) > 1 and word[0].isupper() and word not in entities:
                    entities.append(word)
        
        return entities[:10]  # Limit to top 10 entities
    
    async def get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation context.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict: Conversation context data
        """
        if conversation_id not in self.conversation_contexts:
            return None
        
        return self.conversation_contexts[conversation_id]
    
    async def get_project_memory(self, project_id: str) -> Dict[str, Any]:
        """
        Get project memory.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dict: Project memory data
        """
        if project_id not in self.project_memories:
            return None
        
        return self.project_memories[project_id]
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: User preferences data
        """
        if user_id not in self.user_preferences:
            return None
        
        return self.user_preferences[user_id]
    
    async def get_context_history(self, context_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get context history.
        
        Args:
            context_id: Context ID
            limit: Maximum number of history entries to return
            
        Returns:
            List: Context history entries
        """
        if context_id not in self.context_history:
            return []
        
        # Return the most recent entries up to the limit
        return self.context_history[context_id][-limit:]
    
    async def create_project(self, project_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project memory.
        
        Args:
            project_id: Project ID
            project_data: Project data
            
        Returns:
            Dict: Created project memory
        """
        # Initialize project memory
        self.project_memories[project_id] = {
            "id": project_id,
            "created_at": datetime.now().isoformat(),
            "name": project_data.get("name", project_id),
            "description": project_data.get("description", ""),
            "queries": [],
            "key_information": project_data.get("key_information", {}),
            "artifacts": project_data.get("artifacts", []),
            "decisions": [],
            "last_updated": datetime.now().isoformat()
        }
        
        # Save project memory
        self._save_project_memory(project_id, self.project_memories[project_id])
        
        return self.project_memories[project_id]
    
    async def create_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new conversation context.
        
        Args:
            conversation_id: Conversation ID
            conversation_data: Conversation data
            
        Returns:
            Dict: Created conversation context
        """
        # Initialize conversation context
        self.conversation_contexts[conversation_id] = {
            "id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "messages": conversation_data.get("messages", []),
            "topics": conversation_data.get("topics", []),
            "entities": conversation_data.get("entities", []),
            "last_updated": datetime.now().isoformat()
        }
        
        # Save conversation context
        self._save_conversation_context(conversation_id, self.conversation_contexts[conversation_id])
        
        return self.conversation_contexts[conversation_id]
    
    async def add_artifact(self, project_id: str, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an artifact to project memory.
        
        Args:
            project_id: Project ID
            artifact_data: Artifact data
            
        Returns:
            Dict: Updated project memory
        """
        # Initialize project memory if not exists
        if project_id not in self.project_memories:
            await self.create_project(project_id, {})
        
        project = self.project_memories[project_id]
        
        # Generate artifact ID if not provided
        if "id" not in artifact_data:
            artifact_data["id"] = str(uuid.uuid4())
        
        # Add timestamp if not provided
        if "created_at" not in artifact_data:
            artifact_data["created_at"] = datetime.now().isoformat()
        
        # Check if artifact already exists
        exists = False
        for i, existing in enumerate(project["artifacts"]):
            if existing.get("id") == artifact_data.get("id"):
                exists = True
                # Update existing artifact
                project["artifacts"][i] = artifact_data
                break
        
        if not exists:
            # Add new artifact
            project["artifacts"].append(artifact_data)
        
        # Update last updated timestamp
        project["last_updated"] = datetime.now().isoformat()
        
        # Save project memory
        self._save_project_memory(project_id, project)
        
        return project
    
    async def add_decision(self, project_id: str, decision: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a decision to project memory.
        
        Args:
            project_id: Project ID
            decision: Decision text
            context: Context information
            
        Returns:
            Dict: Updated project memory
        """
        # Initialize project memory if not exists
        if project_id not in self.project_memories:
            await self.create_project(project_id, {})
        
        project = self.project_memories[project_id]
        
        # Add decision
        project["decisions"].append({
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
            "query": context.get("query", ""),
            "context": {
                "conversation_id": context.get("conversation_id"),
                "user_id": context.get("user_id")
            }
        })
        
        # Update last updated timestamp
        project["last_updated"] = datetime.now().isoformat()
        
        # Save project memory
        self._save_project_memory(project_id, project)
        
        return project
    
    async def clear_conversation_context(self, conversation_id: str):
        """
        Clear conversation context.
        
        Args:
            conversation_id: Conversation ID
        """
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]
            
            # Remove file if it exists
            file_path = os.path.join(self.data_path, "conversations", f"{conversation_id}.json")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    self.logger.error(f"Error removing conversation context file: {e}")
            
            self.logger.info(f"Cleared conversation context: {conversation_id}")
    
    async def clear_project_memory(self, project_id: str):
        """
        Clear project memory.
        
        Args:
            project_id: Project ID
        """
        if project_id in self.project_memories:
            del self.project_memories[project_id]
            
            # Remove file if it exists
            file_path = os.path.join(self.data_path, "projects", f"{project_id}.json")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    self.logger.error(f"Error removing project memory file: {e}")
            
            self.logger.info(f"Cleared project memory: {project_id}")


class ProjectMemoryManager:
    """
    Manages project memory and artifacts with version control.
    
    This class provides comprehensive project memory management with
    artifact versioning, ensuring that project context is preserved
    across conversations and tasks.
    
    Attributes:
        logger (logging.Logger): Logger for project memory manager
        context_retrieval (ContextAwareRetrieval): Context-aware retrieval system
        projects (Dict): Dictionary of project data
        artifacts (Dict): Dictionary of artifact data with versions
    """
    
    def __init__(self, context_retrieval: ContextAwareRetrieval = None, data_path: str = None):
        """
        Initialize the Project Memory Manager.
        
        Args:
            context_retrieval: Context-aware retrieval system (default: create new)
            data_path: Path to the data directory (default: None)
        """
        self.logger = logging.getLogger("ProjectMemoryManager")
        
        # Use provided context retrieval or create new one
        self.context_retrieval = context_retrieval or ContextAwareRetrieval(data_path)
        
        # Set default data path if not provided
        if data_path is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(module_dir, "data", "projects")
        else:
            self.data_path = data_path
            
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize projects
        self.projects = {}
        
        # Initialize artifacts
        self.artifacts = {}
        
        self.logger.info("ProjectMemoryManager initialized")
    
    async def load_projects(self):
        """Load all projects from storage."""
        # Load projects from context retrieval
        for project_id in self.context_retrieval.project_memories:
            project = await self.context_retrieval.get_project_memory(project_id)
            if project:
                self.projects[project_id] = project
                
                # Load artifacts
                for artifact in project.get("artifacts", []):
                    artifact_id = artifact.get("id")
                    if artifact_id:
                        if artifact_id not in self.artifacts:
                            self.artifacts[artifact_id] = []
                        
                        # Add as a version if not already present
                        version_exists = False
                        for version in self.artifacts[artifact_id]:
                            if version.get("version") == artifact.get("version"):
                                version_exists = True
                                break
                        
                        if not version_exists:
                            self.artifacts[artifact_id].append(artifact)
        
        self.logger.info(f"Loaded {len(self.projects)} projects")
    
    async def create_project(self, project_id: str, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            project_id: Project ID
            name: Project name
            description: Project description
            
        Returns:
            Dict: Created project data
        """
        # Create project in context retrieval
        project = await self.context_retrieval.create_project(project_id, {
            "name": name,
            "description": description
        })
        
        # Store in local cache
        self.projects[project_id] = project
        
        self.logger.info(f"Created project: {project_id}")
        return project
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get project data.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dict: Project data
        """
        # Check local cache first
        if project_id in self.projects:
            return self.projects[project_id]
        
        # Try to load from context retrieval
        project = await self.context_retrieval.get_project_memory(project_id)
        if project:
            self.projects[project_id] = project
            return project
        
        return None
    
    async def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update project data.
        
        Args:
            project_id: Project ID
            project_data: Updated project data
            
        Returns:
            Dict: Updated project data
        """
        # Check if project exists
        if project_id not in self.projects and not await self.context_retrieval.get_project_memory(project_id):
            return None
        
        # Get existing project
        existing = await self.get_project(project_id)
        
        # Update fields
        for key, value in project_data.items():
            if key not in ["id", "created_at"]:
                existing[key] = value
        
        # Update last updated timestamp
        existing["last_updated"] = datetime.now().isoformat()
        
        # Save to context retrieval
        await self.context_retrieval._save_project_memory(project_id, existing)
        
        # Update local cache
        self.projects[project_id] = existing
        
        self.logger.info(f"Updated project: {project_id}")
        return existing
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if project exists
        if project_id not in self.projects and not await self.context_retrieval.get_project_memory(project_id):
            return False
        
        # Clear from context retrieval
        await self.context_retrieval.clear_project_memory(project_id)
        
        # Remove from local cache
        if project_id in self.projects:
            del self.projects[project_id]
        
        self.logger.info(f"Deleted project: {project_id}")
        return True
    
    async def add_artifact(self, project_id: str, name: str, content: str, 
                         artifact_type: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add an artifact to a project.
        
        Args:
            project_id: Project ID
            name: Artifact name
            content: Artifact content
            artifact_type: Artifact type (e.g., "document", "code", "image")
            metadata: Additional metadata
            
        Returns:
            Dict: Created artifact data
        """
        # Check if project exists
        project = await self.get_project(project_id)
        if not project:
            return None
        
        # Generate artifact ID
        artifact_id = str(uuid.uuid4())
        
        # Create artifact data
        artifact = {
            "id": artifact_id,
            "name": name,
            "content": content,
            "type": artifact_type,
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "project_id": project_id,
            "metadata": metadata or {}
        }
        
        # Add to context retrieval
        await self.context_retrieval.add_artifact(project_id, artifact)
        
        # Add to local artifacts cache
        if artifact_id not in self.artifacts:
            self.artifacts[artifact_id] = []
        self.artifacts[artifact_id].append(artifact)
        
        self.logger.info(f"Added artifact {artifact_id} to project {project_id}")
        return artifact
    
    async def update_artifact(self, artifact_id: str, content: str, 
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update an artifact, creating a new version.
        
        Args:
            artifact_id: Artifact ID
            content: Updated artifact content
            metadata: Updated metadata
            
        Returns:
            Dict: Updated artifact data
        """
        # Check if artifact exists
        if artifact_id not in self.artifacts:
            return None
        
        # Get latest version
        latest_version = max(self.artifacts[artifact_id], key=lambda x: x.get("version", 0))
        project_id = latest_version.get("project_id")
        
        # Create new version
        new_version = latest_version.get("version", 0) + 1
        
        # Create updated artifact
        updated_artifact = {
            "id": artifact_id,
            "name": latest_version.get("name"),
            "content": content,
            "type": latest_version.get("type"),
            "version": new_version,
            "created_at": latest_version.get("created_at"),
            "updated_at": datetime.now().isoformat(),
            "project_id": project_id,
            "metadata": metadata or latest_version.get("metadata", {})
        }
        
        # Add to context retrieval
        if project_id:
            await self.context_retrieval.add_artifact(project_id, updated_artifact)
        
        # Add to local artifacts cache
        self.artifacts[artifact_id].append(updated_artifact)
        
        self.logger.info(f"Updated artifact {artifact_id} to version {new_version}")
        return updated_artifact
    
    async def get_artifact(self, artifact_id: str, version: int = None) -> Dict[str, Any]:
        """
        Get an artifact.
        
        Args:
            artifact_id: Artifact ID
            version: Specific version to retrieve (default: latest)
            
        Returns:
            Dict: Artifact data
        """
        # Check if artifact exists
        if artifact_id not in self.artifacts:
            return None
        
        # Get requested version
        if version is not None:
            # Find specific version
            for artifact in self.artifacts[artifact_id]:
                if artifact.get("version") == version:
                    return artifact
            return None
        else:
            # Get latest version
            return max(self.artifacts[artifact_id], key=lambda x: x.get("version", 0))
    
    async def get_artifact_versions(self, artifact_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of an artifact.
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            List: List of artifact versions
        """
        # Check if artifact exists
        if artifact_id not in self.artifacts:
            return []
        
        # Sort by version
        return sorted(self.artifacts[artifact_id], key=lambda x: x.get("version", 0))
    
    async def get_project_artifacts(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all artifacts for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List: List of latest artifact versions for the project
        """
        project_artifacts = []
        
        # Find all artifacts for the project
        for artifact_id, versions in self.artifacts.items():
            # Check if any version belongs to the project
            project_versions = [v for v in versions if v.get("project_id") == project_id]
            if project_versions:
                # Add latest version
                latest = max(project_versions, key=lambda x: x.get("version", 0))
                project_artifacts.append(latest)
        
        return project_artifacts
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact and all its versions.
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if artifact exists
        if artifact_id not in self.artifacts:
            return False
        
        # Get project ID from latest version
        latest_version = max(self.artifacts[artifact_id], key=lambda x: x.get("version", 0))
        project_id = latest_version.get("project_id")
        
        # Remove from project if project exists
        if project_id and project_id in self.projects:
            project = self.projects[project_id]
            project["artifacts"] = [a for a in project.get("artifacts", []) if a.get("id") != artifact_id]
            
            # Save to context retrieval
            await self.context_retrieval._save_project_memory(project_id, project)
        
        # Remove from local cache
        del self.artifacts[artifact_id]
        
        self.logger.info(f"Deleted artifact: {artifact_id}")
        return True
    
    async def add_decision(self, project_id: str, decision: str, 
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a decision to project memory.
        
        Args:
            project_id: Project ID
            decision: Decision text
            context: Context information
            
        Returns:
            Dict: Updated project data
        """
        # Check if project exists
        project = await self.get_project(project_id)
        if not project:
            return None
        
        # Add decision through context retrieval
        updated_project = await self.context_retrieval.add_decision(
            project_id, decision, context or {}
        )
        
        # Update local cache
        self.projects[project_id] = updated_project
        
        self.logger.info(f"Added decision to project {project_id}")
        return updated_project
    
    async def get_project_decisions(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all decisions for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List: List of project decisions
        """
        # Check if project exists
        project = await self.get_project(project_id)
        if not project:
            return []
        
        return project.get("decisions", [])
    
    async def search_artifacts(self, query: str, project_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for artifacts.
        
        Args:
            query: Search query
            project_id: Optional project ID to limit search scope
            
        Returns:
            List: List of matching artifacts
        """
        results = []
        
        # Determine artifacts to search
        if project_id:
            # Get all artifacts for the project
            artifacts_to_search = await self.get_project_artifacts(project_id)
        else:
            # Get latest version of all artifacts
            artifacts_to_search = []
            for artifact_id, versions in self.artifacts.items():
                latest = max(versions, key=lambda x: x.get("version", 0))
                artifacts_to_search.append(latest)
        
        # Search artifacts
        query_lower = query.lower()
        for artifact in artifacts_to_search:
            relevance = 0
            
            # Check name
            if query_lower in artifact.get("name", "").lower():
                relevance += 0.5
            
            # Check content
            if query_lower in artifact.get("content", "").lower():
                relevance += 0.3
            
            # Check metadata
            metadata = artifact.get("metadata", {})
            for key, value in metadata.items():
                if isinstance(value, str) and query_lower in value.lower():
                    relevance += 0.2
                elif isinstance(key, str) and query_lower in key.lower():
                    relevance += 0.1
                # Fix: Check for tags in metadata and boost relevance if found
                elif key == "tags" and isinstance(value, list):
                    for tag in value:
                        if isinstance(tag, str) and query_lower in tag.lower():
                            relevance += 0.4
            
            # Fix: Also check for tags directly in the artifact
            tags = artifact.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str) and query_lower in tag.lower():
                        relevance += 0.4
            
            if relevance > 0:
                results.append({
                    "artifact": artifact,
                    "relevance": relevance
                })
        
        # Sort by relevance
        sorted_results = sorted(results, key=lambda x: x["relevance"], reverse=True)
        
        # Return artifacts only
        return [r["artifact"] for r in sorted_results]


# Example usage
async def example_usage():
    # Create context-aware retrieval
    car = ContextAwareRetrieval()
    
    # Create project memory manager
    pmm = ProjectMemoryManager(car)
    
    # Create a project
    project = await pmm.create_project(
        "example_project",
        "Example Project",
        "A project for testing context-aware retrieval"
    )
    
    # Add an artifact
    artifact = await pmm.add_artifact(
        "example_project",
        "Example Document",
        "This is an example document for testing.",
        "document",
        {"tags": ["example", "test"]}
    )
    
    # Update the artifact
    updated = await pmm.update_artifact(
        artifact["id"],
        "This is an updated example document for testing.",
        {"tags": ["example", "test", "updated"]}
    )
    
    # Add a decision
    await pmm.add_decision(
        "example_project",
        "Decided to use context-aware retrieval for knowledge integration",
        {"query": "How to integrate knowledge?"}
    )
    
    # Enhance a query with context
    enhanced = await car.enhance_query(
        "How to use this?",
        {"conversation_id": "example_conv", "project_id": "example_project"}
    )
    
    print(f"Enhanced query: {enhanced}")
    
    # Process results with context
    results = [
        {"id": "1", "title": "Usage Guide", "content": "How to use the system...", "relevance": 0.5},
        {"id": "2", "title": "Example Document", "content": "This is an example...", "relevance": 0.3}
    ]
    
    processed = await car.process_results(
        results,
        {"conversation_id": "example_conv", "project_id": "example_project", "query": "How to use this?"}
    )
    
    print(f"Processed results: {len(processed)}")
    
    # Update context with query and results
    await car.update_context(
        "How to use this?",
        processed,
        {"conversation_id": "example_conv", "project_id": "example_project"}
    )
    
    # Search artifacts
    search_results = await pmm.search_artifacts("example", "example_project")
    
    print(f"Search results: {len(search_results)}")

if __name__ == "__main__":
    asyncio.run(example_usage())
