"""
User-customizable template system for the Aideon AI Lite platform.
This module provides tools for users to create, modify, and share custom prompt templates.
"""

from typing import Dict, Any, List, Optional, Union
import json
import os
import logging
import uuid
from pathlib import Path
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserTemplateManager:
    """
    Manages user-customizable prompt templates for the Aideon AI Lite platform.
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the user template manager.
        
        Args:
            templates_dir: Directory to store user templates
        """
        # Set templates directory
        if templates_dir:
            self.templates_dir = templates_dir
        else:
            self.templates_dir = os.path.join(os.path.dirname(__file__), "user_templates")
        
        # Create directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize template storage
        self.user_templates = {}
        self.shared_templates = {}
        
        # Load existing templates
        self._load_templates()
    
    def create_template(self, 
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
        # Default values
        metadata = metadata or {}
        
        # Generate template ID
        template_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Create template record
        template_record = {
            "template_id": template_id,
            "user_id": user_id,
            "template_name": template_name,
            "template_content": template_content,
            "description": description,
            "task_category": task_category,
            "variables": variables,
            "is_public": is_public,
            "created_at": timestamp,
            "updated_at": timestamp,
            "usage_count": 0,
            "metadata": metadata
        }
        
        # Store in user templates
        if user_id not in self.user_templates:
            self.user_templates[user_id] = {}
        
        self.user_templates[user_id][template_id] = template_record
        
        # Store in shared templates if public
        if is_public:
            self.shared_templates[template_id] = template_record
        
        # Save templates
        self._save_templates()
        
        logger.info(f"Created template {template_id} for user {user_id}")
        return template_id
    
    def update_template(self,
                       template_id: str,
                       user_id: str,
                       template_name: Optional[str] = None,
                       template_content: Optional[str] = None,
                       description: Optional[str] = None,
                       task_category: Optional[str] = None,
                       variables: Optional[List[Dict[str, Any]]] = None,
                       is_public: Optional[bool] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing user template.
        
        Args:
            template_id: Unique identifier for the template
            user_id: Unique identifier for the user
            template_name: New name of the template (optional)
            template_content: New content of the template (optional)
            description: New description of the template (optional)
            task_category: New category of tasks (optional)
            variables: New list of variable definitions (optional)
            is_public: New public sharing status (optional)
            metadata: New additional metadata (optional)
            
        Returns:
            Whether the update was successful
        """
        # Check if user exists
        if user_id not in self.user_templates:
            logger.warning(f"User {user_id} not found in templates")
            return False
        
        # Check if template exists
        if template_id not in self.user_templates[user_id]:
            logger.warning(f"Template {template_id} not found for user {user_id}")
            return False
        
        # Get template record
        template_record = self.user_templates[user_id][template_id]
        
        # Update timestamp
        template_record["updated_at"] = datetime.datetime.now().isoformat()
        
        # Update fields if provided
        if template_name is not None:
            template_record["template_name"] = template_name
        
        if template_content is not None:
            template_record["template_content"] = template_content
        
        if description is not None:
            template_record["description"] = description
        
        if task_category is not None:
            template_record["task_category"] = task_category
        
        if variables is not None:
            template_record["variables"] = variables
        
        if is_public is not None:
            template_record["is_public"] = is_public
            
            # Update shared templates
            if is_public:
                self.shared_templates[template_id] = template_record
            elif template_id in self.shared_templates:
                del self.shared_templates[template_id]
        
        if metadata is not None:
            template_record["metadata"].update(metadata)
        
        # Save templates
        self._save_templates()
        
        logger.info(f"Updated template {template_id} for user {user_id}")
        return True
    
    def delete_template(self, template_id: str, user_id: str) -> bool:
        """
        Delete a user template.
        
        Args:
            template_id: Unique identifier for the template
            user_id: Unique identifier for the user
            
        Returns:
            Whether the deletion was successful
        """
        # Check if user exists
        if user_id not in self.user_templates:
            logger.warning(f"User {user_id} not found in templates")
            return False
        
        # Check if template exists
        if template_id not in self.user_templates[user_id]:
            logger.warning(f"Template {template_id} not found for user {user_id}")
            return False
        
        # Delete from user templates
        del self.user_templates[user_id][template_id]
        
        # Delete from shared templates if public
        if template_id in self.shared_templates:
            del self.shared_templates[template_id]
        
        # Save templates
        self._save_templates()
        
        logger.info(f"Deleted template {template_id} for user {user_id}")
        return True
    
    def get_template(self, template_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a template by ID.
        
        Args:
            template_id: Unique identifier for the template
            user_id: Unique identifier for the user (optional)
            
        Returns:
            Template record or empty dict if not found
        """
        # If user_id provided, check user templates
        if user_id:
            if user_id in self.user_templates and template_id in self.user_templates[user_id]:
                return self.user_templates[user_id][template_id]
        
        # Check shared templates
        if template_id in self.shared_templates:
            return self.shared_templates[template_id]
        
        logger.warning(f"Template {template_id} not found")
        return {}
    
    def list_user_templates(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all templates for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of template records
        """
        if user_id not in self.user_templates:
            logger.warning(f"User {user_id} not found in templates")
            return []
        
        return list(self.user_templates[user_id].values())
    
    def list_shared_templates(self, task_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all shared templates, optionally filtered by task category.
        
        Args:
            task_category: Category of tasks to filter by (optional)
            
        Returns:
            List of template records
        """
        templates = list(self.shared_templates.values())
        
        # Filter by task category if provided
        if task_category:
            templates = [t for t in templates if t["task_category"] == task_category]
        
        return templates
    
    def record_template_usage(self, template_id: str, user_id: Optional[str] = None):
        """
        Record usage of a template.
        
        Args:
            template_id: Unique identifier for the template
            user_id: Unique identifier for the user (optional)
        """
        # Update usage count in user templates if user_id provided
        if user_id and user_id in self.user_templates and template_id in self.user_templates[user_id]:
            self.user_templates[user_id][template_id]["usage_count"] += 1
        
        # Update usage count in shared templates
        if template_id in self.shared_templates:
            self.shared_templates[template_id]["usage_count"] += 1
        
        # Save templates
        self._save_templates()
        
        logger.info(f"Recorded usage of template {template_id}")
    
    def _load_templates(self):
        """Load templates from disk."""
        # Load user templates
        user_templates_path = os.path.join(self.templates_dir, "user_templates.json")
        if os.path.exists(user_templates_path):
            try:
                with open(user_templates_path, 'r') as f:
                    self.user_templates = json.load(f)
                logger.info(f"Loaded user templates for {len(self.user_templates)} users")
            except Exception as e:
                logger.error(f"Error loading user templates: {str(e)}")
        
        # Load shared templates
        shared_templates_path = os.path.join(self.templates_dir, "shared_templates.json")
        if os.path.exists(shared_templates_path):
            try:
                with open(shared_templates_path, 'r') as f:
                    self.shared_templates = json.load(f)
                logger.info(f"Loaded {len(self.shared_templates)} shared templates")
            except Exception as e:
                logger.error(f"Error loading shared templates: {str(e)}")
    
    def _save_templates(self):
        """Save templates to disk."""
        # Save user templates
        user_templates_path = os.path.join(self.templates_dir, "user_templates.json")
        try:
            with open(user_templates_path, 'w') as f:
                json.dump(self.user_templates, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user templates: {str(e)}")
        
        # Save shared templates
        shared_templates_path = os.path.join(self.templates_dir, "shared_templates.json")
        try:
            with open(shared_templates_path, 'w') as f:
                json.dump(self.shared_templates, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving shared templates: {str(e)}")
