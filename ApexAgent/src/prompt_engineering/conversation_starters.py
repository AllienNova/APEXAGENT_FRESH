"""
Optimized conversation starters for the Aideon AI Lite platform.
This module provides standardized conversation initiators that establish
clear parameters for effective and efficient interactions.
"""

from typing import Dict, Any, List, Optional, Union
import json
import os
import logging
from pathlib import Path
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationStarter:
    """
    Manages standardized conversation starters that establish clear parameters
    for effective and efficient interactions.
    """
    
    def __init__(self):
        """Initialize the conversation starter with default templates."""
        # Default conversation starter template
        self.default_template = """
SYSTEM: Initializing Aideon AI Lite with optimized parameters.
- Intelligence Level: {intelligence_level}
- Verbosity: {verbosity}
- Creativity: {creativity}
- Format Preference: {format_preference}
- Domain Expertise: {domain_expertise}

USER CONTEXT:
- Project: {project}
- Previous context: {previous_context}
- Priority: {priority}

How can I assist you today?
"""
        
        # Intelligence level options
        self.intelligence_levels = ["Adaptive", "Standard", "Advanced", "Expert"]
        
        # Verbosity options
        self.verbosity_options = ["Concise", "Balanced", "Detailed"]
        
        # Creativity options
        self.creativity_options = ["Practical", "Balanced", "Creative"]
        
        # Format preference options
        self.format_preferences = ["Default", "Structured", "Conversational"]
        
        # Domain expertise options
        self.domain_expertise_options = [
            "General",
            "Specialized in: Software Development",
            "Specialized in: Data Analysis",
            "Specialized in: Content Creation",
            "Specialized in: Business Operations",
            "Specialized in: System Administration"
        ]
        
        # Priority options
        self.priority_options = ["Speed", "Quality", "Efficiency", "Balance"]
        
        # Custom templates for specific scenarios
        self.scenario_templates = {
            "coding": """
SYSTEM: Initializing Aideon AI Lite with coding-optimized parameters.
- Intelligence Level: {intelligence_level}
- Code Style: Clean, maintainable, and well-documented
- Error Handling: Comprehensive with graceful degradation
- Testing Approach: {testing_approach}
- Language Expertise: {language_expertise}

PROJECT CONTEXT:
- Repository: {project}
- Previous work: {previous_context}
- Priority: {priority}

How can I assist with your coding task today?
""",
            "data_analysis": """
SYSTEM: Initializing Aideon AI Lite with data analysis parameters.
- Intelligence Level: {intelligence_level}
- Analysis Depth: {analysis_depth}
- Visualization Style: {visualization_style}
- Statistical Rigor: {statistical_rigor}
- Domain Knowledge: {domain_expertise}

DATA CONTEXT:
- Dataset: {project}
- Previous analysis: {previous_context}
- Priority: {priority}

What data analysis task would you like me to perform?
""",
            "content_creation": """
SYSTEM: Initializing Aideon AI Lite with content creation parameters.
- Intelligence Level: {intelligence_level}
- Tone: {tone}
- Style: {style}
- Audience Level: {audience_level}
- Domain Knowledge: {domain_expertise}

CONTENT CONTEXT:
- Project: {project}
- Previous content: {previous_context}
- Priority: {priority}

What content would you like me to create today?
"""
        }
        
        # User preference storage
        self.user_preferences = {}
    
    def generate_starter(self, 
                         scenario: str = "default", 
                         user_id: str = None,
                         task_category: str = None,
                         user_preferences: Dict[str, Any] = None) -> str:
        """
        Generate a standardized conversation starter based on scenario and user preferences.
        
        Args:
            scenario: Conversation scenario (default, coding, data_analysis, content_creation)
            user_id: Unique identifier for the user
            task_category: Category of the task
            user_preferences: User's preferences for conversation parameters
            
        Returns:
            Formatted conversation starter
        """
        # Default values
        user_preferences = user_preferences or {}
        
        # Load saved user preferences if available
        if user_id and user_id in self.user_preferences:
            saved_preferences = self.user_preferences[user_id]
            # Merge with provided preferences (provided take precedence)
            for key, value in saved_preferences.items():
                if key not in user_preferences:
                    user_preferences[key] = value
        
        # Select template based on scenario
        if scenario in self.scenario_templates:
            template = self.scenario_templates[scenario]
        else:
            template = self.default_template
            scenario = "default"
        
        # Prepare parameters based on scenario
        params = self._prepare_parameters(scenario, task_category, user_preferences)
        
        # Format template with parameters
        starter = template.format(**params)
        
        # Save user preferences if user_id provided
        if user_id:
            self.user_preferences[user_id] = params
        
        logger.info(f"Generated {scenario} conversation starter")
        return starter
    
    def _prepare_parameters(self, 
                           scenario: str, 
                           task_category: str, 
                           user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare parameters for the conversation starter template.
        
        Args:
            scenario: Conversation scenario
            task_category: Category of the task
            user_preferences: User's preferences
            
        Returns:
            Dictionary of parameters for template formatting
        """
        # Common parameters
        params = {
            "intelligence_level": user_preferences.get("intelligence_level", self._select_intelligence_level(task_category)),
            "project": user_preferences.get("project", "New project"),
            "previous_context": user_preferences.get("previous_context", "None"),
            "priority": user_preferences.get("priority", "Balance")
        }
        
        # Scenario-specific parameters
        if scenario == "default":
            params.update({
                "verbosity": user_preferences.get("verbosity", self._select_verbosity(task_category)),
                "creativity": user_preferences.get("creativity", self._select_creativity(task_category)),
                "format_preference": user_preferences.get("format_preference", "Default"),
                "domain_expertise": user_preferences.get("domain_expertise", self._select_domain_expertise(task_category))
            })
        
        elif scenario == "coding":
            params.update({
                "testing_approach": user_preferences.get("testing_approach", "Comprehensive with unit and integration tests"),
                "language_expertise": user_preferences.get("language_expertise", "Python, JavaScript, and other languages as needed")
            })
        
        elif scenario == "data_analysis":
            params.update({
                "analysis_depth": user_preferences.get("analysis_depth", "Comprehensive with exploratory and confirmatory analysis"),
                "visualization_style": user_preferences.get("visualization_style", "Clear, informative, and publication-ready"),
                "statistical_rigor": user_preferences.get("statistical_rigor", "Thorough with appropriate significance testing")
            })
        
        elif scenario == "content_creation":
            params.update({
                "tone": user_preferences.get("tone", "Professional"),
                "style": user_preferences.get("style", "Engaging and informative"),
                "audience_level": user_preferences.get("audience_level", "Knowledgeable general audience")
            })
        
        return params
    
    def _select_intelligence_level(self, task_category: str) -> str:
        """
        Select appropriate intelligence level based on task category.
        
        Args:
            task_category: Category of the task
            
        Returns:
            Selected intelligence level
        """
        if not task_category:
            return "Adaptive"
        
        # Map task categories to intelligence levels
        category_to_level = {
            "software_development": "Expert",
            "data_analysis": "Expert",
            "content_creation": "Advanced",
            "business_operations": "Advanced",
            "system_administration": "Expert"
        }
        
        return category_to_level.get(task_category, "Adaptive")
    
    def _select_verbosity(self, task_category: str) -> str:
        """
        Select appropriate verbosity based on task category.
        
        Args:
            task_category: Category of the task
            
        Returns:
            Selected verbosity
        """
        if not task_category:
            return "Balanced"
        
        # Map task categories to verbosity
        category_to_verbosity = {
            "software_development": "Concise",
            "data_analysis": "Detailed",
            "content_creation": "Balanced",
            "business_operations": "Concise",
            "system_administration": "Concise"
        }
        
        return category_to_verbosity.get(task_category, "Balanced")
    
    def _select_creativity(self, task_category: str) -> str:
        """
        Select appropriate creativity level based on task category.
        
        Args:
            task_category: Category of the task
            
        Returns:
            Selected creativity level
        """
        if not task_category:
            return "Balanced"
        
        # Map task categories to creativity
        category_to_creativity = {
            "software_development": "Practical",
            "data_analysis": "Practical",
            "content_creation": "Creative",
            "business_operations": "Balanced",
            "system_administration": "Practical"
        }
        
        return category_to_creativity.get(task_category, "Balanced")
    
    def _select_domain_expertise(self, task_category: str) -> str:
        """
        Select appropriate domain expertise based on task category.
        
        Args:
            task_category: Category of the task
            
        Returns:
            Selected domain expertise
        """
        if not task_category:
            return "General"
        
        # Map task categories to domain expertise
        category_to_expertise = {
            "software_development": "Specialized in: Software Development",
            "data_analysis": "Specialized in: Data Analysis",
            "content_creation": "Specialized in: Content Creation",
            "business_operations": "Specialized in: Business Operations",
            "system_administration": "Specialized in: System Administration"
        }
        
        return category_to_expertise.get(task_category, "General")
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """
        Save user preferences for future conversations.
        
        Args:
            user_id: Unique identifier for the user
            preferences: User's preferences
        """
        self.user_preferences[user_id] = preferences
        logger.info(f"Saved preferences for user {user_id}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get saved user preferences.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            User's saved preferences or empty dict if not found
        """
        return self.user_preferences.get(user_id, {})
    
    def clear_user_preferences(self, user_id: str):
        """
        Clear saved user preferences.
        
        Args:
            user_id: Unique identifier for the user
        """
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]
            logger.info(f"Cleared preferences for user {user_id}")
