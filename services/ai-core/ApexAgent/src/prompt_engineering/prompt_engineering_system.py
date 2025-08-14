"""
Integration module for the Aideon AI Lite prompt engineering system.
This module provides a unified API for seamless integration with the rest of the platform.
"""

from typing import Dict, Any, List, Optional, Union
import json
import os
import logging
import uuid
import datetime
from pathlib import Path

# Import prompt engineering components
from .enhanced_architecture import ModularPromptArchitecture
from .template_library import TemplateLibrary
from .prompt_construction import PromptConstructionEngine
from .conversation_starters import ConversationStarter
from .prompt_analytics import PromptAnalytics
from .user_template_manager import UserTemplateManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptEngineeringSystem:
    """
    Main integration module for the Aideon AI Lite prompt engineering system.
    Provides a unified API for seamless integration with the rest of the platform.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the prompt engineering system.
        
        Args:
            base_dir: Base directory for storing prompt engineering data
        """
        # Set base directory
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.join(os.path.dirname(__file__))
        
        # Initialize components
        self.architecture = ModularPromptArchitecture()
        self.template_library = TemplateLibrary()
        self.prompt_construction = PromptConstructionEngine(self.template_library)
        self.conversation_starter = ConversationStarter()
        
        # Set up analytics directory
        analytics_dir = os.path.join(self.base_dir, "analytics_data")
        self.analytics = PromptAnalytics(analytics_dir)
        
        # Set up user templates directory
        templates_dir = os.path.join(self.base_dir, "user_templates")
        self.user_template_manager = UserTemplateManager(templates_dir)
        
        logger.info("Prompt engineering system initialized")
    
    def generate_prompt(self,
                       task_type: str,
                       task_description: str,
                       user_id: Optional[str] = None,
                       template_id: Optional[str] = None,
                       parameters: Dict[str, Any] = None,
                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate an optimized prompt for a specific task.
        
        Args:
            task_type: Type of task (e.g., coding, data_analysis, content_creation)
            task_description: Description of the task
            user_id: Unique identifier for the user (optional)
            template_id: Specific template ID to use (optional)
            parameters: Additional parameters for prompt construction
            context: Additional context for prompt construction
            
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        # Default values
        parameters = parameters or {}
        context = context or {}
        
        # Generate prompt ID
        prompt_id = str(uuid.uuid4())
        
        # Start timing
        start_time = datetime.datetime.now()
        
        try:
            # If template_id provided, use that template
            if template_id:
                template = self.user_template_manager.get_template(template_id, user_id)
                if not template:
                    logger.warning(f"Template {template_id} not found, falling back to system templates")
                    template = None
                else:
                    # Record template usage
                    self.user_template_manager.record_template_usage(template_id, user_id)
            else:
                template = None
            
            # Generate prompt using construction engine
            prompt_result = self.prompt_construction.construct_prompt(
                task_type=task_type,
                task_description=task_description,
                template=template,
                parameters=parameters,
                context=context
            )
            
            # Get prompt text and metadata
            prompt_text = prompt_result["prompt"]
            template_name = prompt_result["template_name"]
            token_count = prompt_result["token_count"]
            
            # Record prompt usage in analytics
            self.analytics.record_prompt_usage(
                prompt_id=prompt_id,
                template_name=template_name,
                user_id=user_id,
                task_category=task_type,
                prompt_text=prompt_text,
                token_count=token_count,
                metadata={
                    "task_description": task_description,
                    "parameters": parameters
                }
            )
            
            # Calculate response time
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # Record prompt performance
            self.analytics.record_prompt_performance(
                prompt_id=prompt_id,
                success=True,
                response_time=response_time
            )
            
            # Return result
            return {
                "prompt_id": prompt_id,
                "prompt": prompt_text,
                "template_name": template_name,
                "token_count": token_count,
                "success": True,
                "response_time": response_time
            }
        
        except Exception as e:
            # Log error
            logger.error(f"Error generating prompt: {str(e)}")
            
            # Calculate response time
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # Record prompt performance
            self.analytics.record_prompt_performance(
                prompt_id=prompt_id,
                success=False,
                response_time=response_time,
                error_type=str(type(e).__name__)
            )
            
            # Return error
            return {
                "prompt_id": prompt_id,
                "success": False,
                "error": str(e),
                "error_type": str(type(e).__name__),
                "response_time": response_time
            }
    
    def generate_conversation_starter(self,
                                    scenario: str = "default",
                                    user_id: Optional[str] = None,
                                    task_category: Optional[str] = None,
                                    user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a standardized conversation starter.
        
        Args:
            scenario: Conversation scenario (default, coding, data_analysis, content_creation)
            user_id: Unique identifier for the user (optional)
            task_category: Category of the task (optional)
            user_preferences: User's preferences for conversation parameters (optional)
            
        Returns:
            Dictionary containing the generated conversation starter and metadata
        """
        # Default values
        user_preferences = user_preferences or {}
        
        # Generate prompt ID
        prompt_id = str(uuid.uuid4())
        
        # Start timing
        start_time = datetime.datetime.now()
        
        try:
            # Generate conversation starter
            starter = self.conversation_starter.generate_starter(
                scenario=scenario,
                user_id=user_id,
                task_category=task_category,
                user_preferences=user_preferences
            )
            
            # Estimate token count (rough estimate)
            token_count = len(starter.split()) * 1.3
            
            # Record prompt usage in analytics
            self.analytics.record_prompt_usage(
                prompt_id=prompt_id,
                template_name=f"conversation_starter_{scenario}",
                user_id=user_id,
                task_category=task_category or "general",
                prompt_text=starter,
                token_count=int(token_count),
                metadata={
                    "scenario": scenario,
                    "user_preferences": user_preferences
                }
            )
            
            # Calculate response time
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # Record prompt performance
            self.analytics.record_prompt_performance(
                prompt_id=prompt_id,
                success=True,
                response_time=response_time
            )
            
            # Return result
            return {
                "prompt_id": prompt_id,
                "starter": starter,
                "scenario": scenario,
                "token_count": int(token_count),
                "success": True,
                "response_time": response_time
            }
        
        except Exception as e:
            # Log error
            logger.error(f"Error generating conversation starter: {str(e)}")
            
            # Calculate response time
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # Record prompt performance
            self.analytics.record_prompt_performance(
                prompt_id=prompt_id,
                success=False,
                response_time=response_time,
                error_type=str(type(e).__name__)
            )
            
            # Return error
            return {
                "prompt_id": prompt_id,
                "success": False,
                "error": str(e),
                "error_type": str(type(e).__name__),
                "response_time": response_time
            }
    
    def record_prompt_feedback(self,
                             prompt_id: str,
                             success: bool,
                             completion_time: Optional[float] = None,
                             user_rating: Optional[int] = None,
                             error_type: Optional[str] = None,
                             metadata: Dict[str, Any] = None):
        """
        Record feedback for a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            success: Whether the prompt was successful
            completion_time: Time to complete the entire task in seconds (optional)
            user_rating: User satisfaction rating (1-5) (optional)
            error_type: Type of error if unsuccessful (optional)
            metadata: Additional metadata about the performance (optional)
        """
        # Default values
        metadata = metadata or {}
        
        # Record prompt performance
        self.analytics.record_prompt_performance(
            prompt_id=prompt_id,
            success=success,
            response_time=0.0,  # Not applicable for feedback
            completion_time=completion_time,
            user_rating=user_rating,
            error_type=error_type,
            metadata=metadata
        )
        
        logger.info(f"Recorded feedback for prompt {prompt_id}")
    
    def get_optimization_recommendations(self, template_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recommendations for optimizing prompts.
        
        Args:
            template_name: Name of the template to get recommendations for (optional)
            
        Returns:
            List of optimization recommendations
        """
        return self.analytics.get_optimization_recommendations(template_name)
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics report.
        
        Returns:
            Dictionary containing analytics report data
        """
        return self.analytics.generate_analytics_report()
    
    def create_user_template(self,
                           user_id: str,
                           template_name: str,
                           template_content: str,
                           description: str,
                           task_category: str,
                           variables: List[Dict[str, Any]],
                           is_public: bool = False,
                           metadata: Dict[str, Any] = None) -> str:
        """
        Create a new user template.
        
        Args:
            user_id: Unique identifier for the user
            template_name: Name of the template
            template_content: Content of the template with variable placeholders
            description: Description of the template
            task_category: Category of tasks the template is designed for
            variables: List of variable definitions with name, description, and default value
            is_public: Whether the template is publicly shared
            metadata: Additional metadata about the template
            
        Returns:
            Unique identifier for the created template
        """
        return self.user_template_manager.create_template(
            user_id=user_id,
            template_name=template_name,
            template_content=template_content,
            description=description,
            task_category=task_category,
            variables=variables,
            is_public=is_public,
            metadata=metadata
        )
    
    def list_user_templates(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all templates for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of template records
        """
        return self.user_template_manager.list_user_templates(user_id)
    
    def list_shared_templates(self, task_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all shared templates, optionally filtered by task category.
        
        Args:
            task_category: Category of tasks to filter by (optional)
            
        Returns:
            List of template records
        """
        return self.user_template_manager.list_shared_templates(task_category)
