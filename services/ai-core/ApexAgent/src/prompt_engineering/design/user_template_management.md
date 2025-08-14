# User Template Management System Design

## Overview

This document outlines the design for a comprehensive user template management system for the Aideon AI Lite platform. Building upon the enhanced modular prompt architecture and prompt analytics system, this component provides sophisticated tools for users to create, customize, share, and manage prompt templates.

## Design Goals

1. **Intuitive Template Creation** - Enable users to create templates without deep technical knowledge
2. **Powerful Customization** - Provide advanced options for technical users
3. **Version Control** - Track template changes with full history
4. **Sharing and Collaboration** - Allow teams to share and collaborate on templates
5. **Performance Insights** - Provide analytics on template performance
6. **Cross-Project Compatibility** - Ensure templates work across different projects
7. **Enterprise Integration** - Support enterprise governance and compliance
8. **Adaptive Learning** - Improve templates based on usage patterns

## Core Architecture

### UserTemplateManager Class

The `UserTemplateManager` class serves as the central component for user template management:

```python
class UserTemplateManager:
    """
    Comprehensive system for managing user-created prompt templates.
    """
    
    def __init__(self, 
                storage_dir: str = None, 
                analytics: PromptAnalytics = None,
                db_connection: Any = None):
        """Initialize the user template manager"""
        # Set storage directory
        if storage_dir:
            self.storage_dir = storage_dir
        else:
            self.storage_dir = os.path.join(os.path.dirname(__file__), "user_templates")
        
        # Create directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize database connection
        self.db = db_connection or self._initialize_database()
        
        # Initialize analytics
        self.analytics = analytics
        
        # Initialize components
        self.template_registry = UserTemplateRegistry(self.db)
        self.template_editor = TemplateEditor(self.template_registry)
        self.version_control = TemplateVersionControl(self.db)
        self.sharing_manager = TemplateSharingManager(self.db)
        self.import_export = TemplateImportExport(self.template_registry, self.storage_dir)
        self.validator = TemplateValidator()
        self.recommendation_engine = TemplateRecommendationEngine(self.analytics, self.template_registry)
    
    def create_template(self, 
                       name: str,
                       description: str,
                       content: str,
                       task_category: str = None,
                       task_domain: str = None,
                       tags: List[str] = None,
                       user_id: str = None,
                       organization_id: str = None,
                       is_public: bool = False) -> Dict[str, Any]:
        """
        Create a new template.
        
        Args:
            name: Name of the template
            description: Description of the template
            content: Template content
            task_category: Category of tasks the template is for (optional)
            task_domain: Domain of tasks the template is for (optional)
            tags: Tags for the template (optional)
            user_id: ID of the user creating the template (optional)
            organization_id: ID of the organization (optional)
            is_public: Whether the template is public (optional)
            
        Returns:
            Dictionary with template information
        """
        # Validate template
        validation_result = self.validator.validate_template(content)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": "Invalid template",
                "validation_errors": validation_result["errors"]
            }
        
        # Create template
        template_id = str(uuid.uuid4())
        
        template = {
            "id": template_id,
            "name": name,
            "description": description,
            "content": content,
            "task_category": task_category,
            "task_domain": task_domain,
            "tags": tags or [],
            "user_id": user_id,
            "organization_id": organization_id,
            "is_public": is_public,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "version": 1,
            "usage_count": 0,
            "rating": None
        }
        
        # Add to registry
        success = self.template_registry.add_template(template)
        
        if success:
            # Add to version control
            self.version_control.create_version(template_id, template, "Initial version")
            
            return {
                "success": True,
                "template_id": template_id,
                "template": template
            }
        else:
            return {
                "success": False,
                "error": "Failed to add template to registry"
            }
    
    def update_template(self, 
                       template_id: str,
                       name: str = None,
                       description: str = None,
                       content: str = None,
                       task_category: str = None,
                       task_domain: str = None,
                       tags: List[str] = None,
                       is_public: bool = None,
                       commit_message: str = "Updated template") -> Dict[str, Any]:
        """
        Update an existing template.
        
        Args:
            template_id: ID of the template to update
            name: New name of the template (optional)
            description: New description of the template (optional)
            content: New template content (optional)
            task_category: New category of tasks the template is for (optional)
            task_domain: New domain of tasks the template is for (optional)
            tags: New tags for the template (optional)
            is_public: New public status (optional)
            commit_message: Message describing the update (optional)
            
        Returns:
            Dictionary with template information
        """
        # Get existing template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Validate new content if provided
        if content:
            validation_result = self.validator.validate_template(content)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Invalid template content",
                    "validation_errors": validation_result["errors"]
                }
        
        # Update template
        updated_template = template.copy()
        
        if name:
            updated_template["name"] = name
        
        if description:
            updated_template["description"] = description
        
        if content:
            updated_template["content"] = content
        
        if task_category:
            updated_template["task_category"] = task_category
        
        if task_domain:
            updated_template["task_domain"] = task_domain
        
        if tags:
            updated_template["tags"] = tags
        
        if is_public is not None:
            updated_template["is_public"] = is_public
        
        updated_template["updated_at"] = datetime.datetime.now().isoformat()
        updated_template["version"] += 1
        
        # Update in registry
        success = self.template_registry.update_template(template_id, updated_template)
        
        if success:
            # Add to version control
            self.version_control.create_version(template_id, updated_template, commit_message)
            
            return {
                "success": True,
                "template_id": template_id,
                "template": updated_template
            }
        else:
            return {
                "success": False,
                "error": "Failed to update template in registry"
            }
    
    def delete_template(self, template_id: str) -> Dict[str, Any]:
        """
        Delete a template.
        
        Args:
            template_id: ID of the template to delete
            
        Returns:
            Dictionary with result information
        """
        # Get existing template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Delete from registry
        success = self.template_registry.delete_template(template_id)
        
        if success:
            return {
                "success": True,
                "template_id": template_id
            }
        else:
            return {
                "success": False,
                "error": "Failed to delete template from registry"
            }
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """
        Get a template.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            Dictionary with template information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        
        if template:
            return {
                "success": True,
                "template": template
            }
        else:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
    
    def search_templates(self, 
                        query: str = None,
                        task_category: str = None,
                        task_domain: str = None,
                        tags: List[str] = None,
                        user_id: str = None,
                        organization_id: str = None,
                        include_public: bool = True,
                        sort_by: str = "updated_at",
                        sort_order: str = "desc",
                        limit: int = 100,
                        offset: int = 0) -> Dict[str, Any]:
        """
        Search for templates.
        
        Args:
            query: Search query (optional)
            task_category: Filter by task category (optional)
            task_domain: Filter by task domain (optional)
            tags: Filter by tags (optional)
            user_id: Filter by user ID (optional)
            organization_id: Filter by organization ID (optional)
            include_public: Whether to include public templates (optional)
            sort_by: Field to sort by (optional)
            sort_order: Sort order (asc or desc) (optional)
            limit: Maximum number of results (optional)
            offset: Offset for pagination (optional)
            
        Returns:
            Dictionary with search results
        """
        # Search templates
        results = self.template_registry.search_templates(
            query=query,
            task_category=task_category,
            task_domain=task_domain,
            tags=tags,
            user_id=user_id,
            organization_id=organization_id,
            include_public=include_public,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "total": results["total"],
            "templates": results["templates"]
        }
    
    def get_template_versions(self, template_id: str) -> Dict[str, Any]:
        """
        Get versions of a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with version information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Get versions
        versions = self.version_control.get_versions(template_id)
        
        return {
            "success": True,
            "template_id": template_id,
            "versions": versions
        }
    
    def get_template_version(self, template_id: str, version: int) -> Dict[str, Any]:
        """
        Get a specific version of a template.
        
        Args:
            template_id: ID of the template
            version: Version number
            
        Returns:
            Dictionary with template version information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Get version
        template_version = self.version_control.get_version(template_id, version)
        
        if template_version:
            return {
                "success": True,
                "template_id": template_id,
                "version": version,
                "template": template_version
            }
        else:
            return {
                "success": False,
                "error": f"Version not found: {version}"
            }
    
    def revert_to_version(self, template_id: str, version: int) -> Dict[str, Any]:
        """
        Revert a template to a previous version.
        
        Args:
            template_id: ID of the template
            version: Version number to revert to
            
        Returns:
            Dictionary with result information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Get version
        template_version = self.version_control.get_version(template_id, version)
        
        if not template_version:
            return {
                "success": False,
                "error": f"Version not found: {version}"
            }
        
        # Update template with version data
        updated_template = template.copy()
        
        # Copy relevant fields from version
        for field in ["name", "description", "content", "task_category", "task_domain", "tags", "is_public"]:
            if field in template_version:
                updated_template[field] = template_version[field]
        
        updated_template["updated_at"] = datetime.datetime.now().isoformat()
        updated_template["version"] += 1
        
        # Update in registry
        success = self.template_registry.update_template(template_id, updated_template)
        
        if success:
            # Add to version control
            self.version_control.create_version(
                template_id, 
                updated_template, 
                f"Reverted to version {version}"
            )
            
            return {
                "success": True,
                "template_id": template_id,
                "template": updated_template
            }
        else:
            return {
                "success": False,
                "error": "Failed to update template in registry"
            }
    
    def share_template(self, 
                      template_id: str,
                      user_ids: List[str] = None,
                      organization_id: str = None,
                      permission: str = "view") -> Dict[str, Any]:
        """
        Share a template with users or an organization.
        
        Args:
            template_id: ID of the template to share
            user_ids: IDs of users to share with (optional)
            organization_id: ID of organization to share with (optional)
            permission: Permission level (view, edit, admin) (optional)
            
        Returns:
            Dictionary with result information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Share template
        if user_ids:
            for user_id in user_ids:
                self.sharing_manager.share_with_user(template_id, user_id, permission)
        
        if organization_id:
            self.sharing_manager.share_with_organization(template_id, organization_id, permission)
        
        return {
            "success": True,
            "template_id": template_id
        }
    
    def unshare_template(self, 
                        template_id: str,
                        user_ids: List[str] = None,
                        organization_id: str = None) -> Dict[str, Any]:
        """
        Unshare a template with users or an organization.
        
        Args:
            template_id: ID of the template to unshare
            user_ids: IDs of users to unshare with (optional)
            organization_id: ID of organization to unshare with (optional)
            
        Returns:
            Dictionary with result information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Unshare template
        if user_ids:
            for user_id in user_ids:
                self.sharing_manager.unshare_with_user(template_id, user_id)
        
        if organization_id:
            self.sharing_manager.unshare_with_organization(template_id, organization_id)
        
        return {
            "success": True,
            "template_id": template_id
        }
    
    def get_template_permissions(self, template_id: str) -> Dict[str, Any]:
        """
        Get permissions for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with permission information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Get permissions
        permissions = self.sharing_manager.get_permissions(template_id)
        
        return {
            "success": True,
            "template_id": template_id,
            "permissions": permissions
        }
    
    def export_template(self, template_id: str, format: str = "json") -> Dict[str, Any]:
        """
        Export a template.
        
        Args:
            template_id: ID of the template to export
            format: Export format (json, yaml, xml) (optional)
            
        Returns:
            Dictionary with export information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Export template
        export_result = self.import_export.export_template(template_id, format)
        
        if export_result["success"]:
            return {
                "success": True,
                "template_id": template_id,
                "format": format,
                "file_path": export_result["file_path"],
                "content": export_result["content"]
            }
        else:
            return {
                "success": False,
                "error": export_result["error"]
            }
    
    def import_template(self, 
                       file_path: str = None,
                       content: str = None,
                       format: str = "json",
                       user_id: str = None,
                       organization_id: str = None) -> Dict[str, Any]:
        """
        Import a template.
        
        Args:
            file_path: Path to template file (optional)
            content: Template content (optional)
            format: Import format (json, yaml, xml) (optional)
            user_id: ID of the user importing the template (optional)
            organization_id: ID of the organization (optional)
            
        Returns:
            Dictionary with import information
        """
        # Import template
        import_result = self.import_export.import_template(
            file_path=file_path,
            content=content,
            format=format
        )
        
        if import_result["success"]:
            # Create template
            template_data = import_result["template"]
            
            # Override user and organization
            if user_id:
                template_data["user_id"] = user_id
            
            if organization_id:
                template_data["organization_id"] = organization_id
            
            # Create template
            create_result = self.create_template(
                name=template_data["name"],
                description=template_data["description"],
                content=template_data["content"],
                task_category=template_data.get("task_category"),
                task_domain=template_data.get("task_domain"),
                tags=template_data.get("tags"),
                user_id=template_data.get("user_id"),
                organization_id=template_data.get("organization_id"),
                is_public=template_data.get("is_public", False)
            )
            
            if create_result["success"]:
                return {
                    "success": True,
                    "template_id": create_result["template_id"],
                    "template": create_result["template"]
                }
            else:
                return {
                    "success": False,
                    "error": create_result["error"]
                }
        else:
            return {
                "success": False,
                "error": import_result["error"]
            }
    
    def get_template_recommendations(self, 
                                   task_category: str = None,
                                   task_domain: str = None,
                                   user_id: str = None,
                                   organization_id: str = None,
                                   limit: int = 5) -> Dict[str, Any]:
        """
        Get template recommendations.
        
        Args:
            task_category: Category of tasks (optional)
            task_domain: Domain of tasks (optional)
            user_id: ID of the user (optional)
            organization_id: ID of the organization (optional)
            limit: Maximum number of recommendations (optional)
            
        Returns:
            Dictionary with recommendation information
        """
        # Get recommendations
        recommendations = self.recommendation_engine.get_recommendations(
            task_category=task_category,
            task_domain=task_domain,
            user_id=user_id,
            organization_id=organization_id,
            limit=limit
        )
        
        return {
            "success": True,
            "recommendations": recommendations
        }
    
    def rate_template(self, 
                     template_id: str,
                     rating: int,
                     feedback: str = None,
                     user_id: str = None) -> Dict[str, Any]:
        """
        Rate a template.
        
        Args:
            template_id: ID of the template to rate
            rating: Rating (1-5)
            feedback: Feedback text (optional)
            user_id: ID of the user rating the template (optional)
            
        Returns:
            Dictionary with result information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Validate rating
        if rating < 1 or rating > 5:
            return {
                "success": False,
                "error": "Rating must be between 1 and 5"
            }
        
        # Add rating
        rating_data = {
            "template_id": template_id,
            "rating": rating,
            "feedback": feedback,
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.db["ratings"].append(rating_data)
        
        # Update template rating
        template_ratings = [r["rating"] for r in self.db["ratings"] if r["template_id"] == template_id]
        avg_rating = sum(template_ratings) / len(template_ratings) if template_ratings else None
        
        updated_template = template.copy()
        updated_template["rating"] = avg_rating
        
        self.template_registry.update_template(template_id, updated_template)
        
        # Record in analytics if available
        if self.analytics:
            self.analytics.record_user_feedback(
                prompt_id=template_id,
                rating=rating,
                feedback_text=feedback,
                user_id=user_id
            )
        
        return {
            "success": True,
            "template_id": template_id,
            "rating": rating,
            "avg_rating": avg_rating
        }
    
    def get_template_usage_stats(self, template_id: str) -> Dict[str, Any]:
        """
        Get usage statistics for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with usage statistics
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Get usage stats from analytics if available
        if self.analytics:
            stats = self.analytics.get_template_performance(template_id=template_id)
        else:
            stats = {
                "usage_count": template["usage_count"],
                "avg_quality_score": None,
                "avg_token_count": None
            }
        
        return {
            "success": True,
            "template_id": template_id,
            "stats": stats
        }
    
    def _initialize_database(self) -> Any:
        """Initialize the database connection"""
        # In a real implementation, this would connect to a database
        # For this design document, we'll use a simple in-memory database
        return {
            "templates": [],
            "versions": [],
            "permissions": [],
            "ratings": []
        }
```

### UserTemplateRegistry Class

The `UserTemplateRegistry` class manages the registry of user templates:

```python
class UserTemplateRegistry:
    """
    Registry for user-created prompt templates.
    """
    
    def __init__(self, db: Any):
        """Initialize the template registry"""
        self.db = db
    
    def add_template(self, template: Dict[str, Any]) -> bool:
        """
        Add a template to the registry.
        
        Args:
            template: Template data
            
        Returns:
            Whether the operation was successful
        """
        # Check if template with same ID already exists
        if any(t["id"] == template["id"] for t in self.db["templates"]):
            return False
        
        # Add to database
        self.db["templates"].append(template)
        
        return True
    
    def update_template(self, template_id: str, template: Dict[str, Any]) -> bool:
        """
        Update a template in the registry.
        
        Args:
            template_id: ID of the template to update
            template: Updated template data
            
        Returns:
            Whether the operation was successful
        """
        # Find template
        for i, t in enumerate(self.db["templates"]):
            if t["id"] == template_id:
                # Update template
                self.db["templates"][i] = template
                return True
        
        return False
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template from the registry.
        
        Args:
            template_id: ID of the template to delete
            
        Returns:
            Whether the operation was successful
        """
        # Find template
        for i, t in enumerate(self.db["templates"]):
            if t["id"] == template_id:
                # Delete template
                del self.db["templates"][i]
                return True
        
        return False
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """
        Get a template from the registry.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            Template data or None if not found
        """
        # Find template
        for t in self.db["templates"]:
            if t["id"] == template_id:
                return t
        
        return None
    
    def search_templates(self, 
                        query: str = None,
                        task_category: str = None,
                        task_domain: str = None,
                        tags: List[str] = None,
                        user_id: str = None,
                        organization_id: str = None,
                        include_public: bool = True,
                        sort_by: str = "updated_at",
                        sort_order: str = "desc",
                        limit: int = 100,
                        offset: int = 0) -> Dict[str, Any]:
        """
        Search for templates in the registry.
        
        Args:
            query: Search query (optional)
            task_category: Filter by task category (optional)
            task_domain: Filter by task domain (optional)
            tags: Filter by tags (optional)
            user_id: Filter by user ID (optional)
            organization_id: Filter by organization ID (optional)
            include_public: Whether to include public templates (optional)
            sort_by: Field to sort by (optional)
            sort_order: Sort order (asc or desc) (optional)
            limit: Maximum number of results (optional)
            offset: Offset for pagination (optional)
            
        Returns:
            Dictionary with search results
        """
        # Get all templates
        templates = self.db["templates"]
        
        # Filter templates
        filtered_templates = templates
        
        if query:
            query_lower = query.lower()
            filtered_templates = [
                t for t in filtered_templates if
                query_lower in t["name"].lower() or
                query_lower in t["description"].lower() or
                any(query_lower in tag.lower() for tag in t.get("tags", []))
            ]
        
        if task_category:
            filtered_templates = [t for t in filtered_templates if t.get("task_category") == task_category]
        
        if task_domain:
            filtered_templates = [t for t in filtered_templates if t.get("task_domain") == task_domain]
        
        if tags:
            filtered_templates = [
                t for t in filtered_templates if
                all(tag in t.get("tags", []) for tag in tags)
            ]
        
        if user_id:
            filtered_templates = [t for t in filtered_templates if t.get("user_id") == user_id]
        
        if organization_id:
            filtered_templates = [t for t in filtered_templates if t.get("organization_id") == organization_id]
        
        # Include public templates if requested
        if include_public:
            if user_id or organization_id:
                # Include templates that match user/org or are public
                public_templates = [t for t in templates if t.get("is_public", False)]
                filtered_templates = list(set(filtered_templates + public_templates))
        else:
            # Exclude public templates
            filtered_templates = [t for t in filtered_templates if not t.get("is_public", False)]
        
        # Sort templates
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "name":
            filtered_templates.sort(key=lambda t: t["name"], reverse=reverse)
        elif sort_by == "created_at":
            filtered_templates.sort(key=lambda t: t["created_at"], reverse=reverse)
        elif sort_by == "updated_at":
            filtered_templates.sort(key=lambda t: t["updated_at"], reverse=reverse)
        elif sort_by == "usage_count":
            filtered_templates.sort(key=lambda t: t.get("usage_count", 0), reverse=reverse)
        elif sort_by == "rating":
            filtered_templates.sort(key=lambda t: t.get("rating", 0) or 0, reverse=reverse)
        
        # Apply pagination
        total = len(filtered_templates)
        paginated_templates = filtered_templates[offset:offset + limit]
        
        return {
            "total": total,
            "templates": paginated_templates
        }
    
    def increment_usage_count(self, template_id: str) -> bool:
        """
        Increment the usage count for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Whether the operation was successful
        """
        # Find template
        for i, t in enumerate(self.db["templates"]):
            if t["id"] == template_id:
                # Increment usage count
                updated_template = t.copy()
                updated_template["usage_count"] = updated_template.get("usage_count", 0) + 1
                
                # Update template
                self.db["templates"][i] = updated_template
                return True
        
        return False
```

### TemplateEditor Class

The `TemplateEditor` class provides tools for editing templates:

```python
class TemplateEditor:
    """
    Tools for editing templates.
    """
    
    def __init__(self, template_registry: UserTemplateRegistry):
        """Initialize the template editor"""
        self.template_registry = template_registry
    
    def get_template_structure(self, template_id: str) -> Dict[str, Any]:
        """
        Get the structure of a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with template structure information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Parse template content
        try:
            structure = self._parse_template_structure(template["content"])
            
            return {
                "success": True,
                "template_id": template_id,
                "structure": structure
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse template structure: {str(e)}"
            }
    
    def update_template_section(self, 
                              template_id: str,
                              section_path: str,
                              content: str) -> Dict[str, Any]:
        """
        Update a section of a template.
        
        Args:
            template_id: ID of the template
            section_path: Path to the section to update
            content: New content for the section
            
        Returns:
            Dictionary with result information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Parse template content
        try:
            structure = self._parse_template_structure(template["content"])
            
            # Update section
            updated_structure = self._update_section(structure, section_path, content)
            
            # Generate updated template content
            updated_content = self._generate_template_content(updated_structure)
            
            # Update template
            updated_template = template.copy()
            updated_template["content"] = updated_content
            updated_template["updated_at"] = datetime.datetime.now().isoformat()
            updated_template["version"] += 1
            
            # Update in registry
            success = self.template_registry.update_template(template_id, updated_template)
            
            if success:
                return {
                    "success": True,
                    "template_id": template_id,
                    "template": updated_template
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update template in registry"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update template section: {str(e)}"
            }
    
    def add_template_section(self, 
                           template_id: str,
                           parent_path: str,
                           section_name: str,
                           content: str) -> Dict[str, Any]:
        """
        Add a section to a template.
        
        Args:
            template_id: ID of the template
            parent_path: Path to the parent section
            section_name: Name of the new section
            content: Content for the new section
            
        Returns:
            Dictionary with result information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Parse template content
        try:
            structure = self._parse_template_structure(template["content"])
            
            # Add section
            updated_structure = self._add_section(structure, parent_path, section_name, content)
            
            # Generate updated template content
            updated_content = self._generate_template_content(updated_structure)
            
            # Update template
            updated_template = template.copy()
            updated_template["content"] = updated_content
            updated_template["updated_at"] = datetime.datetime.now().isoformat()
            updated_template["version"] += 1
            
            # Update in registry
            success = self.template_registry.update_template(template_id, updated_template)
            
            if success:
                return {
                    "success": True,
                    "template_id": template_id,
                    "template": updated_template
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update template in registry"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to add template section: {str(e)}"
            }
    
    def delete_template_section(self, 
                              template_id: str,
                              section_path: str) -> Dict[str, Any]:
        """
        Delete a section from a template.
        
        Args:
            template_id: ID of the template
            section_path: Path to the section to delete
            
        Returns:
            Dictionary with result information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Parse template content
        try:
            structure = self._parse_template_structure(template["content"])
            
            # Delete section
            updated_structure = self._delete_section(structure, section_path)
            
            # Generate updated template content
            updated_content = self._generate_template_content(updated_structure)
            
            # Update template
            updated_template = template.copy()
            updated_template["content"] = updated_content
            updated_template["updated_at"] = datetime.datetime.now().isoformat()
            updated_template["version"] += 1
            
            # Update in registry
            success = self.template_registry.update_template(template_id, updated_template)
            
            if success:
                return {
                    "success": True,
                    "template_id": template_id,
                    "template": updated_template
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update template in registry"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete template section: {str(e)}"
            }
    
    def _parse_template_structure(self, content: str) -> Dict[str, Any]:
        """Parse the structure of a template"""
        # Placeholder implementation
        # In a real implementation, this would parse XML tags
        
        # Simple example structure
        return {
            "type": "root",
            "children": [
                {
                    "type": "section",
                    "name": "intro",
                    "content": "Introduction section"
                },
                {
                    "type": "section",
                    "name": "main",
                    "content": "Main section",
                    "children": [
                        {
                            "type": "section",
                            "name": "subsection1",
                            "content": "Subsection 1"
                        },
                        {
                            "type": "section",
                            "name": "subsection2",
                            "content": "Subsection 2"
                        }
                    ]
                },
                {
                    "type": "section",
                    "name": "conclusion",
                    "content": "Conclusion section"
                }
            ]
        }
    
    def _update_section(self, structure: Dict[str, Any], section_path: str, content: str) -> Dict[str, Any]:
        """Update a section in the template structure"""
        # Placeholder implementation
        return structure
    
    def _add_section(self, structure: Dict[str, Any], parent_path: str, section_name: str, content: str) -> Dict[str, Any]:
        """Add a section to the template structure"""
        # Placeholder implementation
        return structure
    
    def _delete_section(self, structure: Dict[str, Any], section_path: str) -> Dict[str, Any]:
        """Delete a section from the template structure"""
        # Placeholder implementation
        return structure
    
    def _generate_template_content(self, structure: Dict[str, Any]) -> str:
        """Generate template content from structure"""
        # Placeholder implementation
        return "Generated template content"
```

### TemplateVersionControl Class

The `TemplateVersionControl` class manages version control for templates:

```python
class TemplateVersionControl:
    """
    Version control for templates.
    """
    
    def __init__(self, db: Any):
        """Initialize the version control"""
        self.db = db
    
    def create_version(self, 
                      template_id: str,
                      template: Dict[str, Any],
                      commit_message: str) -> Dict[str, Any]:
        """
        Create a new version of a template.
        
        Args:
            template_id: ID of the template
            template: Template data
            commit_message: Message describing the changes
            
        Returns:
            Dictionary with version information
        """
        # Create version record
        version_record = {
            "template_id": template_id,
            "version": template["version"],
            "template": template,
            "commit_message": commit_message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add to database
        self.db["versions"].append(version_record)
        
        return version_record
    
    def get_versions(self, template_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            List of version records
        """
        # Get versions
        versions = [v for v in self.db["versions"] if v["template_id"] == template_id]
        
        # Sort by version number
        versions.sort(key=lambda v: v["version"])
        
        return versions
    
    def get_version(self, template_id: str, version: int) -> Dict[str, Any]:
        """
        Get a specific version of a template.
        
        Args:
            template_id: ID of the template
            version: Version number
            
        Returns:
            Version record or None if not found
        """
        # Get version
        for v in self.db["versions"]:
            if v["template_id"] == template_id and v["version"] == version:
                return v["template"]
        
        return None
    
    def compare_versions(self, 
                        template_id: str,
                        version1: int,
                        version2: int) -> Dict[str, Any]:
        """
        Compare two versions of a template.
        
        Args:
            template_id: ID of the template
            version1: First version number
            version2: Second version number
            
        Returns:
            Dictionary with comparison information
        """
        # Get versions
        template1 = self.get_version(template_id, version1)
        template2 = self.get_version(template_id, version2)
        
        if not template1 or not template2:
            return {
                "success": False,
                "error": "One or both versions not found"
            }
        
        # Compare templates
        differences = []
        
        # Compare basic fields
        for field in ["name", "description", "task_category", "task_domain", "tags", "is_public"]:
            if template1.get(field) != template2.get(field):
                differences.append({
                    "field": field,
                    "version1": template1.get(field),
                    "version2": template2.get(field)
                })
        
        # Compare content
        if template1["content"] != template2["content"]:
            # In a real implementation, this would use a diff algorithm
            differences.append({
                "field": "content",
                "version1": template1["content"],
                "version2": template2["content"]
            })
        
        return {
            "success": True,
            "template_id": template_id,
            "version1": version1,
            "version2": version2,
            "differences": differences
        }
```

### TemplateSharingManager Class

The `TemplateSharingManager` class manages sharing of templates:

```python
class TemplateSharingManager:
    """
    Manages sharing of templates.
    """
    
    def __init__(self, db: Any):
        """Initialize the sharing manager"""
        self.db = db
    
    def share_with_user(self, 
                       template_id: str,
                       user_id: str,
                       permission: str = "view") -> bool:
        """
        Share a template with a user.
        
        Args:
            template_id: ID of the template
            user_id: ID of the user
            permission: Permission level (view, edit, admin) (optional)
            
        Returns:
            Whether the operation was successful
        """
        # Check if already shared
        for p in self.db["permissions"]:
            if p["template_id"] == template_id and p["user_id"] == user_id:
                # Update permission
                p["permission"] = permission
                p["updated_at"] = datetime.datetime.now().isoformat()
                return True
        
        # Create permission record
        permission_record = {
            "template_id": template_id,
            "user_id": user_id,
            "permission": permission,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        # Add to database
        self.db["permissions"].append(permission_record)
        
        return True
    
    def share_with_organization(self, 
                              template_id: str,
                              organization_id: str,
                              permission: str = "view") -> bool:
        """
        Share a template with an organization.
        
        Args:
            template_id: ID of the template
            organization_id: ID of the organization
            permission: Permission level (view, edit, admin) (optional)
            
        Returns:
            Whether the operation was successful
        """
        # Check if already shared
        for p in self.db["permissions"]:
            if p["template_id"] == template_id and p.get("organization_id") == organization_id:
                # Update permission
                p["permission"] = permission
                p["updated_at"] = datetime.datetime.now().isoformat()
                return True
        
        # Create permission record
        permission_record = {
            "template_id": template_id,
            "organization_id": organization_id,
            "permission": permission,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        # Add to database
        self.db["permissions"].append(permission_record)
        
        return True
    
    def unshare_with_user(self, template_id: str, user_id: str) -> bool:
        """
        Unshare a template with a user.
        
        Args:
            template_id: ID of the template
            user_id: ID of the user
            
        Returns:
            Whether the operation was successful
        """
        # Find permission
        for i, p in enumerate(self.db["permissions"]):
            if p["template_id"] == template_id and p.get("user_id") == user_id:
                # Delete permission
                del self.db["permissions"][i]
                return True
        
        return False
    
    def unshare_with_organization(self, template_id: str, organization_id: str) -> bool:
        """
        Unshare a template with an organization.
        
        Args:
            template_id: ID of the template
            organization_id: ID of the organization
            
        Returns:
            Whether the operation was successful
        """
        # Find permission
        for i, p in enumerate(self.db["permissions"]):
            if p["template_id"] == template_id and p.get("organization_id") == organization_id:
                # Delete permission
                del self.db["permissions"][i]
                return True
        
        return False
    
    def get_permissions(self, template_id: str) -> Dict[str, Any]:
        """
        Get permissions for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with permission information
        """
        # Get permissions
        permissions = [p for p in self.db["permissions"] if p["template_id"] == template_id]
        
        # Organize by type
        user_permissions = [p for p in permissions if "user_id" in p]
        organization_permissions = [p for p in permissions if "organization_id" in p]
        
        return {
            "user_permissions": user_permissions,
            "organization_permissions": organization_permissions
        }
    
    def check_permission(self, 
                        template_id: str,
                        user_id: str = None,
                        organization_id: str = None,
                        required_permission: str = "view") -> bool:
        """
        Check if a user or organization has permission for a template.
        
        Args:
            template_id: ID of the template
            user_id: ID of the user (optional)
            organization_id: ID of the organization (optional)
            required_permission: Required permission level (optional)
            
        Returns:
            Whether the user or organization has the required permission
        """
        # Get permissions
        permissions = [p for p in self.db["permissions"] if p["template_id"] == template_id]
        
        # Check user permissions
        if user_id:
            user_permissions = [p for p in permissions if p.get("user_id") == user_id]
            
            for p in user_permissions:
                if self._has_permission(p["permission"], required_permission):
                    return True
        
        # Check organization permissions
        if organization_id:
            organization_permissions = [p for p in permissions if p.get("organization_id") == organization_id]
            
            for p in organization_permissions:
                if self._has_permission(p["permission"], required_permission):
                    return True
        
        return False
    
    def _has_permission(self, actual_permission: str, required_permission: str) -> bool:
        """Check if actual permission satisfies required permission"""
        permission_levels = {
            "view": 1,
            "edit": 2,
            "admin": 3
        }
        
        actual_level = permission_levels.get(actual_permission, 0)
        required_level = permission_levels.get(required_permission, 0)
        
        return actual_level >= required_level
```

### TemplateImportExport Class

The `TemplateImportExport` class handles import and export of templates:

```python
class TemplateImportExport:
    """
    Handles import and export of templates.
    """
    
    def __init__(self, template_registry: UserTemplateRegistry, storage_dir: str):
        """Initialize the import/export handler"""
        self.template_registry = template_registry
        self.storage_dir = storage_dir
    
    def export_template(self, template_id: str, format: str = "json") -> Dict[str, Any]:
        """
        Export a template.
        
        Args:
            template_id: ID of the template to export
            format: Export format (json, yaml, xml) (optional)
            
        Returns:
            Dictionary with export information
        """
        # Get template
        template = self.template_registry.get_template(template_id)
        if not template:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        # Create export data
        export_data = {
            "name": template["name"],
            "description": template["description"],
            "content": template["content"],
            "task_category": template.get("task_category"),
            "task_domain": template.get("task_domain"),
            "tags": template.get("tags", []),
            "is_public": template.get("is_public", False),
            "exported_at": datetime.datetime.now().isoformat(),
            "version": template["version"]
        }
        
        # Export in requested format
        if format == "json":
            content = json.dumps(export_data, indent=2)
            file_extension = "json"
        elif format == "yaml":
            # In a real implementation, this would use a YAML library
            content = json.dumps(export_data, indent=2)  # Placeholder
            file_extension = "yaml"
        elif format == "xml":
            # In a real implementation, this would use an XML library
            content = json.dumps(export_data, indent=2)  # Placeholder
            file_extension = "xml"
        else:
            return {
                "success": False,
                "error": f"Unsupported format: {format}"
            }
        
        # Create file name
        file_name = f"{template['name'].lower().replace(' ', '_')}_{template_id[:8]}.{file_extension}"
        file_path = os.path.join(self.storage_dir, file_name)
        
        # Write to file
        try:
            with open(file_path, "w") as f:
                f.write(content)
            
            return {
                "success": True,
                "template_id": template_id,
                "format": format,
                "file_path": file_path,
                "content": content
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write export file: {str(e)}"
            }
    
    def import_template(self, 
                       file_path: str = None,
                       content: str = None,
                       format: str = "json") -> Dict[str, Any]:
        """
        Import a template.
        
        Args:
            file_path: Path to template file (optional)
            content: Template content (optional)
            format: Import format (json, yaml, xml) (optional)
            
        Returns:
            Dictionary with import information
        """
        # Get content
        if file_path:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to read import file: {str(e)}"
                }
        elif not content:
            return {
                "success": False,
                "error": "No file path or content provided"
            }
        
        # Parse content
        try:
            if format == "json":
                template_data = json.loads(content)
            elif format == "yaml":
                # In a real implementation, this would use a YAML library
                template_data = json.loads(content)  # Placeholder
            elif format == "xml":
                # In a real implementation, this would use an XML library
                template_data = json.loads(content)  # Placeholder
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse import content: {str(e)}"
            }
        
        # Validate template data
        required_fields = ["name", "description", "content"]
        for field in required_fields:
            if field not in template_data:
                return {
                    "success": False,
                    "error": f"Missing required field: {field}"
                }
        
        return {
            "success": True,
            "template": template_data
        }
```

### TemplateValidator Class

The `TemplateValidator` class validates templates:

```python
class TemplateValidator:
    """
    Validates templates.
    """
    
    def validate_template(self, content: str) -> Dict[str, Any]:
        """
        Validate a template.
        
        Args:
            content: Template content
            
        Returns:
            Dictionary with validation information
        """
        # Placeholder implementation
        # In a real implementation, this would validate XML syntax, etc.
        
        errors = []
        
        # Check for empty content
        if not content:
            errors.append("Template content cannot be empty")
        
        # Check for valid XML
        try:
            # Placeholder XML validation
            if "<" not in content or ">" not in content:
                errors.append("Template content must contain XML tags")
        except Exception as e:
            errors.append(f"Invalid XML: {str(e)}")
        
        # Return validation result
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
```

### TemplateRecommendationEngine Class

The `TemplateRecommendationEngine` class provides template recommendations:

```python
class TemplateRecommendationEngine:
    """
    Provides template recommendations.
    """
    
    def __init__(self, analytics: Any, template_registry: UserTemplateRegistry):
        """Initialize the recommendation engine"""
        self.analytics = analytics
        self.template_registry = template_registry
    
    def get_recommendations(self, 
                          task_category: str = None,
                          task_domain: str = None,
                          user_id: str = None,
                          organization_id: str = None,
                          limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get template recommendations.
        
        Args:
            task_category: Category of tasks (optional)
            task_domain: Domain of tasks (optional)
            user_id: ID of the user (optional)
            organization_id: ID of the organization (optional)
            limit: Maximum number of recommendations (optional)
            
        Returns:
            List of recommended templates
        """
        # Get templates
        search_results = self.template_registry.search_templates(
            task_category=task_category,
            task_domain=task_domain,
            user_id=user_id,
            organization_id=organization_id,
            include_public=True,
            sort_by="rating",
            sort_order="desc",
            limit=100
        )
        
        templates = search_results["templates"]
        
        # If analytics is available, use it to improve recommendations
        if self.analytics:
            # Get performance data for templates
            template_ids = [t["id"] for t in templates]
            performance_data = {}
            
            for template_id in template_ids:
                performance = self.analytics.get_template_performance(template_id=template_id)
                performance_data[template_id] = performance
            
            # Score templates based on performance
            scored_templates = []
            
            for template in templates:
                template_id = template["id"]
                performance = performance_data.get(template_id, {})
                
                # Calculate score
                score = 0
                
                # Rating score (0-5)
                rating = template.get("rating")
                if rating is not None:
                    score += rating
                
                # Success rate score (0-1)
                success_rate = performance.get("success_rate")
                if success_rate is not None:
                    score += success_rate * 2
                
                # Quality score (0-1)
                quality_score = performance.get("avg_quality_score")
                if quality_score is not None:
                    score += quality_score * 2
                
                # Add to scored templates
                scored_templates.append({
                    "template": template,
                    "score": score
                })
            
            # Sort by score
            scored_templates.sort(key=lambda t: t["score"], reverse=True)
            
            # Get top templates
            recommendations = [t["template"] for t in scored_templates[:limit]]
        else:
            # Without analytics, just use top rated templates
            recommendations = templates[:limit]
        
        return recommendations
```

## User Interface Integration

The user template management system integrates with the Aideon AI Lite user interface:

```python
class UserInterfaceIntegration:
    """
    Integrates the template management system with the user interface.
    """
    
    def __init__(self, template_manager: UserTemplateManager):
        """Initialize the UI integration"""
        self.template_manager = template_manager
    
    def get_template_editor_data(self, template_id: str = None) -> Dict[str, Any]:
        """
        Get data for the template editor.
        
        Args:
            template_id: ID of the template to edit (optional)
            
        Returns:
            Dictionary with editor data
        """
        # Get template categories
        categories = [
            "General",
            "Development",
            "Research",
            "Writing",
            "Analysis",
            "Enterprise",
            "Integration",
            "Knowledge Management"
        ]
        
        # Get template domains
        domains = [
            "General",
            "Healthcare",
            "Finance",
            "Legal",
            "Education",
            "Technology",
            "Science",
            "Marketing"
        ]
        
        # Get template if provided
        template = None
        if template_id:
            result = self.template_manager.get_template(template_id)
            if result["success"]:
                template = result["template"]
        
        return {
            "success": True,
            "categories": categories,
            "domains": domains,
            "template": template
        }
    
    def get_template_library_data(self, 
                                user_id: str = None,
                                organization_id: str = None) -> Dict[str, Any]:
        """
        Get data for the template library.
        
        Args:
            user_id: ID of the user (optional)
            organization_id: ID of the organization (optional)
            
        Returns:
            Dictionary with library data
        """
        # Get user templates
        user_templates = []
        if user_id:
            result = self.template_manager.search_templates(
                user_id=user_id,
                include_public=False,
                sort_by="updated_at",
                sort_order="desc",
                limit=100
            )
            if result["success"]:
                user_templates = result["templates"]
        
        # Get organization templates
        organization_templates = []
        if organization_id:
            result = self.template_manager.search_templates(
                organization_id=organization_id,
                include_public=False,
                sort_by="updated_at",
                sort_order="desc",
                limit=100
            )
            if result["success"]:
                organization_templates = result["templates"]
        
        # Get public templates
        public_templates = []
        result = self.template_manager.search_templates(
            is_public=True,
            sort_by="rating",
            sort_order="desc",
            limit=100
        )
        if result["success"]:
            public_templates = result["templates"]
        
        # Get recommended templates
        recommended_templates = []
        result = self.template_manager.get_template_recommendations(
            user_id=user_id,
            organization_id=organization_id,
            limit=10
        )
        if result["success"]:
            recommended_templates = result["recommendations"]
        
        return {
            "success": True,
            "user_templates": user_templates,
            "organization_templates": organization_templates,
            "public_templates": public_templates,
            "recommended_templates": recommended_templates
        }
    
    def get_template_details_data(self, template_id: str) -> Dict[str, Any]:
        """
        Get data for the template details view.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with details data
        """
        # Get template
        template_result = self.template_manager.get_template(template_id)
        if not template_result["success"]:
            return template_result
        
        template = template_result["template"]
        
        # Get versions
        versions_result = self.template_manager.get_template_versions(template_id)
        versions = versions_result["versions"] if versions_result["success"] else []
        
        # Get permissions
        permissions_result = self.template_manager.get_template_permissions(template_id)
        permissions = permissions_result["permissions"] if permissions_result["success"] else {}
        
        # Get usage stats
        stats_result = self.template_manager.get_template_usage_stats(template_id)
        stats = stats_result["stats"] if stats_result["success"] else {}
        
        return {
            "success": True,
            "template": template,
            "versions": versions,
            "permissions": permissions,
            "stats": stats
        }
```

## Visual Template Editor

The system includes a visual template editor component:

```python
class VisualTemplateEditor:
    """
    Visual editor for templates.
    """
    
    def __init__(self, template_manager: UserTemplateManager):
        """Initialize the visual editor"""
        self.template_manager = template_manager
    
    def get_editor_components(self) -> Dict[str, Any]:
        """
        Get available components for the editor.
        
        Returns:
            Dictionary with component information
        """
        # Define component categories
        categories = [
            {
                "id": "basic",
                "name": "Basic Components",
                "components": [
                    {
                        "id": "text",
                        "name": "Text",
                        "description": "Plain text content",
                        "icon": "text_format"
                    },
                    {
                        "id": "section",
                        "name": "Section",
                        "description": "Container for other components",
                        "icon": "folder"
                    },
                    {
                        "id": "conditional",
                        "name": "Conditional",
                        "description": "Content that appears based on conditions",
                        "icon": "call_split"
                    }
                ]
            },
            {
                "id": "advanced",
                "name": "Advanced Components",
                "components": [
                    {
                        "id": "variable",
                        "name": "Variable",
                        "description": "Placeholder for dynamic content",
                        "icon": "code"
                    },
                    {
                        "id": "loop",
                        "name": "Loop",
                        "description": "Repeat content for each item in a collection",
                        "icon": "loop"
                    },
                    {
                        "id": "include",
                        "name": "Include",
                        "description": "Include content from another template",
                        "icon": "call_merge"
                    }
                ]
            },
            {
                "id": "enterprise",
                "name": "Enterprise Components",
                "components": [
                    {
                        "id": "compliance",
                        "name": "Compliance",
                        "description": "Compliance-related content",
                        "icon": "verified"
                    },
                    {
                        "id": "security",
                        "name": "Security",
                        "description": "Security-related content",
                        "icon": "security"
                    },
                    {
                        "id": "integration",
                        "name": "Integration",
                        "description": "Integration-related content",
                        "icon": "integration_instructions"
                    }
                ]
            }
        ]
        
        return {
            "success": True,
            "categories": categories
        }
    
    def get_editor_templates(self) -> Dict[str, Any]:
        """
        Get available templates for the editor.
        
        Returns:
            Dictionary with template information
        """
        # Define template categories
        categories = [
            {
                "id": "general",
                "name": "General Templates",
                "templates": [
                    {
                        "id": "blank",
                        "name": "Blank Template",
                        "description": "Start with a blank template",
                        "icon": "description"
                    },
                    {
                        "id": "basic",
                        "name": "Basic Template",
                        "description": "Simple template with basic sections",
                        "icon": "article"
                    }
                ]
            },
            {
                "id": "task",
                "name": "Task Templates",
                "templates": [
                    {
                        "id": "development",
                        "name": "Development Template",
                        "description": "Template for development tasks",
                        "icon": "code"
                    },
                    {
                        "id": "research",
                        "name": "Research Template",
                        "description": "Template for research tasks",
                        "icon": "search"
                    },
                    {
                        "id": "writing",
                        "name": "Writing Template",
                        "description": "Template for writing tasks",
                        "icon": "edit"
                    }
                ]
            },
            {
                "id": "enterprise",
                "name": "Enterprise Templates",
                "templates": [
                    {
                        "id": "compliance",
                        "name": "Compliance Template",
                        "description": "Template for compliance tasks",
                        "icon": "verified"
                    },
                    {
                        "id": "security",
                        "name": "Security Template",
                        "description": "Template for security tasks",
                        "icon": "security"
                    },
                    {
                        "id": "integration",
                        "name": "Integration Template",
                        "description": "Template for integration tasks",
                        "icon": "integration_instructions"
                    }
                ]
            }
        ]
        
        return {
            "success": True,
            "categories": categories
        }
    
    def create_template_from_visual(self, 
                                  name: str,
                                  description: str,
                                  visual_data: Dict[str, Any],
                                  task_category: str = None,
                                  task_domain: str = None,
                                  tags: List[str] = None,
                                  user_id: str = None,
                                  organization_id: str = None,
                                  is_public: bool = False) -> Dict[str, Any]:
        """
        Create a template from visual editor data.
        
        Args:
            name: Name of the template
            description: Description of the template
            visual_data: Visual editor data
            task_category: Category of tasks the template is for (optional)
            task_domain: Domain of tasks the template is for (optional)
            tags: Tags for the template (optional)
            user_id: ID of the user creating the template (optional)
            organization_id: ID of the organization (optional)
            is_public: Whether the template is public (optional)
            
        Returns:
            Dictionary with template information
        """
        # Convert visual data to template content
        try:
            content = self._convert_visual_to_content(visual_data)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to convert visual data to template content: {str(e)}"
            }
        
        # Create template
        result = self.template_manager.create_template(
            name=name,
            description=description,
            content=content,
            task_category=task_category,
            task_domain=task_domain,
            tags=tags,
            user_id=user_id,
            organization_id=organization_id,
            is_public=is_public
        )
        
        return result
    
    def update_template_from_visual(self, 
                                  template_id: str,
                                  visual_data: Dict[str, Any],
                                  name: str = None,
                                  description: str = None,
                                  task_category: str = None,
                                  task_domain: str = None,
                                  tags: List[str] = None,
                                  is_public: bool = None) -> Dict[str, Any]:
        """
        Update a template from visual editor data.
        
        Args:
            template_id: ID of the template to update
            visual_data: Visual editor data
            name: New name of the template (optional)
            description: New description of the template (optional)
            task_category: New category of tasks the template is for (optional)
            task_domain: New domain of tasks the template is for (optional)
            tags: New tags for the template (optional)
            is_public: New public status (optional)
            
        Returns:
            Dictionary with template information
        """
        # Convert visual data to template content
        try:
            content = self._convert_visual_to_content(visual_data)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to convert visual data to template content: {str(e)}"
            }
        
        # Update template
        result = self.template_manager.update_template(
            template_id=template_id,
            name=name,
            description=description,
            content=content,
            task_category=task_category,
            task_domain=task_domain,
            tags=tags,
            is_public=is_public,
            commit_message="Updated from visual editor"
        )
        
        return result
    
    def convert_template_to_visual(self, template_id: str) -> Dict[str, Any]:
        """
        Convert a template to visual editor data.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with visual editor data
        """
        # Get template
        result = self.template_manager.get_template(template_id)
        if not result["success"]:
            return result
        
        template = result["template"]
        
        # Convert template content to visual data
        try:
            visual_data = self._convert_content_to_visual(template["content"])
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to convert template content to visual data: {str(e)}"
            }
        
        return {
            "success": True,
            "template_id": template_id,
            "visual_data": visual_data
        }
    
    def _convert_visual_to_content(self, visual_data: Dict[str, Any]) -> str:
        """Convert visual editor data to template content"""
        # Placeholder implementation
        # In a real implementation, this would convert visual data to XML
        
        return "<template>\n  <section name=\"intro\">Introduction content</section>\n  <section name=\"main\">Main content</section>\n  <section name=\"conclusion\">Conclusion content</section>\n</template>"
    
    def _convert_content_to_visual(self, content: str) -> Dict[str, Any]:
        """Convert template content to visual editor data"""
        # Placeholder implementation
        # In a real implementation, this would parse XML and convert to visual data
        
        return {
            "type": "template",
            "children": [
                {
                    "type": "section",
                    "name": "intro",
                    "content": "Introduction content"
                },
                {
                    "type": "section",
                    "name": "main",
                    "content": "Main content"
                },
                {
                    "type": "section",
                    "name": "conclusion",
                    "content": "Conclusion content"
                }
            ]
        }
```

## Enterprise Integration

The system includes enterprise integration features:

```python
class EnterpriseIntegration:
    """
    Enterprise integration features.
    """
    
    def __init__(self, template_manager: UserTemplateManager):
        """Initialize the enterprise integration"""
        self.template_manager = template_manager
    
    def apply_governance_policy(self, 
                              template_id: str,
                              policy_id: str,
                              user_id: str = None) -> Dict[str, Any]:
        """
        Apply a governance policy to a template.
        
        Args:
            template_id: ID of the template
            policy_id: ID of the policy to apply
            user_id: ID of the user applying the policy (optional)
            
        Returns:
            Dictionary with result information
        """
        # Get template
        result = self.template_manager.get_template(template_id)
        if not result["success"]:
            return result
        
        template = result["template"]
        
        # Get policy
        policy = self._get_policy(policy_id)
        if not policy:
            return {
                "success": False,
                "error": f"Policy not found: {policy_id}"
            }
        
        # Apply policy
        updated_template = template.copy()
        
        # Update template based on policy
        if "required_tags" in policy:
            # Add required tags
            tags = set(updated_template.get("tags", []))
            tags.update(policy["required_tags"])
            updated_template["tags"] = list(tags)
        
        if "visibility" in policy:
            # Set visibility
            updated_template["is_public"] = policy["visibility"] == "public"
        
        # Update template
        update_result = self.template_manager.update_template(
            template_id=template_id,
            tags=updated_template.get("tags"),
            is_public=updated_template.get("is_public"),
            commit_message=f"Applied governance policy: {policy['name']}"
        )
        
        if update_result["success"]:
            # Record policy application
            self._record_policy_application(template_id, policy_id, user_id)
            
            return {
                "success": True,
                "template_id": template_id,
                "policy_id": policy_id,
                "template": update_result["template"]
            }
        else:
            return update_result
    
    def validate_compliance(self, template_id: str) -> Dict[str, Any]:
        """
        Validate compliance of a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with compliance information
        """
        # Get template
        result = self.template_manager.get_template(template_id)
        if not result["success"]:
            return result
        
        template = result["template"]
        
        # Validate compliance
        compliance_issues = []
        
        # Check for required tags
        if not template.get("tags"):
            compliance_issues.append({
                "type": "missing_tags",
                "message": "Template must have at least one tag"
            })
        
        # Check for description
        if not template.get("description"):
            compliance_issues.append({
                "type": "missing_description",
                "message": "Template must have a description"
            })
        
        # Check for content
        if not template.get("content"):
            compliance_issues.append({
                "type": "missing_content",
                "message": "Template must have content"
            })
        
        # Check for sensitive information in content
        if template.get("content") and self._contains_sensitive_info(template["content"]):
            compliance_issues.append({
                "type": "sensitive_info",
                "message": "Template content contains sensitive information"
            })
        
        return {
            "success": True,
            "template_id": template_id,
            "compliant": len(compliance_issues) == 0,
            "issues": compliance_issues
        }
    
    def get_audit_log(self, 
                     template_id: str = None,
                     user_id: str = None,
                     action_type: str = None,
                     time_range: Tuple[str, str] = None,
                     limit: int = 100,
                     offset: int = 0) -> Dict[str, Any]:
        """
        Get audit log entries.
        
        Args:
            template_id: Filter by template ID (optional)
            user_id: Filter by user ID (optional)
            action_type: Filter by action type (optional)
            time_range: Filter by time range (start, end) (optional)
            limit: Maximum number of entries (optional)
            offset: Offset for pagination (optional)
            
        Returns:
            Dictionary with audit log entries
        """
        # Placeholder implementation
        # In a real implementation, this would query an audit log database
        
        entries = [
            {
                "id": "1",
                "template_id": "template1",
                "user_id": "user1",
                "action_type": "create",
                "details": "Created template",
                "timestamp": "2023-01-01T12:00:00Z"
            },
            {
                "id": "2",
                "template_id": "template1",
                "user_id": "user1",
                "action_type": "update",
                "details": "Updated template content",
                "timestamp": "2023-01-02T12:00:00Z"
            },
            {
                "id": "3",
                "template_id": "template1",
                "user_id": "user2",
                "action_type": "share",
                "details": "Shared with organization",
                "timestamp": "2023-01-03T12:00:00Z"
            }
        ]
        
        # Filter entries
        filtered_entries = entries
        
        if template_id:
            filtered_entries = [e for e in filtered_entries if e["template_id"] == template_id]
        
        if user_id:
            filtered_entries = [e for e in filtered_entries if e["user_id"] == user_id]
        
        if action_type:
            filtered_entries = [e for e in filtered_entries if e["action_type"] == action_type]
        
        if time_range:
            start_time, end_time = time_range
            filtered_entries = [e for e in filtered_entries if start_time <= e["timestamp"] <= end_time]
        
        # Apply pagination
        total = len(filtered_entries)
        paginated_entries = filtered_entries[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "entries": paginated_entries
        }
    
    def _get_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get a governance policy"""
        # Placeholder implementation
        # In a real implementation, this would query a policy database
        
        policies = {
            "public": {
                "id": "public",
                "name": "Public Template Policy",
                "description": "Policy for public templates",
                "required_tags": ["public"],
                "visibility": "public"
            },
            "internal": {
                "id": "internal",
                "name": "Internal Template Policy",
                "description": "Policy for internal templates",
                "required_tags": ["internal"],
                "visibility": "private"
            },
            "confidential": {
                "id": "confidential",
                "name": "Confidential Template Policy",
                "description": "Policy for confidential templates",
                "required_tags": ["confidential"],
                "visibility": "private"
            }
        }
        
        return policies.get(policy_id)
    
    def _record_policy_application(self, template_id: str, policy_id: str, user_id: str = None):
        """Record application of a policy to a template"""
        # Placeholder implementation
        # In a real implementation, this would record in an audit log
        pass
    
    def _contains_sensitive_info(self, content: str) -> bool:
        """Check if content contains sensitive information"""
        # Placeholder implementation
        # In a real implementation, this would use pattern matching or ML
        
        sensitive_patterns = [
            "password",
            "api_key",
            "secret",
            "token",
            "credential"
        ]
        
        content_lower = content.lower()
        
        return any(pattern in content_lower for pattern in sensitive_patterns)
```

## Implementation Plan

The implementation of the user template management system will proceed in phases:

### Phase 1: Core Template Management
- Implement `UserTemplateManager` class with basic functionality
- Develop `UserTemplateRegistry` for template storage
- Create `TemplateValidator` for template validation
- Implement basic template CRUD operations

### Phase 2: Version Control and Sharing
- Implement `TemplateVersionControl` for version history
- Develop `TemplateSharingManager` for sharing templates
- Create `TemplateImportExport` for import/export functionality
- Implement template permissions and access control

### Phase 3: Template Editing and Visualization
- Implement `TemplateEditor` for editing templates
- Develop `VisualTemplateEditor` for visual editing
- Create template structure parsing and generation
- Implement template component library

### Phase 4: Analytics and Recommendations
- Integrate with prompt analytics system
- Implement `TemplateRecommendationEngine` for recommendations
- Develop template usage tracking
- Create template performance metrics

### Phase 5: Enterprise Integration
- Implement `EnterpriseIntegration` for governance
- Develop compliance validation
- Create audit logging
- Implement policy enforcement

### Phase 6: User Interface Integration
- Implement `UserInterfaceIntegration` for UI components
- Develop template library UI
- Create template editor UI
- Implement template details UI

## Testing and Validation

The implementation includes comprehensive testing and validation:

```python
class TemplateManagerTester:
    """
    Tests the template management system.
    """
    
    def __init__(self, template_manager: UserTemplateManager):
        """Initialize the template manager tester"""
        self.template_manager = template_manager
        self.test_cases = []
    
    def add_test_case(self, 
                     test_type: str,
                     test_data: Dict[str, Any],
                     expected_result: Dict[str, Any]):
        """Add a test case"""
        self.test_cases.append({
            "test_type": test_type,
            "test_data": test_data,
            "expected_result": expected_result
        })
    
    def run_tests(self) -> Dict[str, Any]:
        """Run all test cases"""
        results = {
            "total": len(self.test_cases),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for i, test_case in enumerate(self.test_cases):
            result = self.run_test_case(test_case)
            results["details"].append(result)
            
            if result["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        test_type = test_case["test_type"]
        test_data = test_case["test_data"]
        expected_result = test_case["expected_result"]
        
        try:
            # Run test based on type
            if test_type == "create_template":
                actual_result = self.template_manager.create_template(**test_data)
            elif test_type == "update_template":
                actual_result = self.template_manager.update_template(**test_data)
            elif test_type == "delete_template":
                actual_result = self.template_manager.delete_template(**test_data)
            elif test_type == "get_template":
                actual_result = self.template_manager.get_template(**test_data)
            elif test_type == "search_templates":
                actual_result = self.template_manager.search_templates(**test_data)
            elif test_type == "get_template_versions":
                actual_result = self.template_manager.get_template_versions(**test_data)
            elif test_type == "get_template_version":
                actual_result = self.template_manager.get_template_version(**test_data)
            elif test_type == "revert_to_version":
                actual_result = self.template_manager.revert_to_version(**test_data)
            elif test_type == "share_template":
                actual_result = self.template_manager.share_template(**test_data)
            elif test_type == "unshare_template":
                actual_result = self.template_manager.unshare_template(**test_data)
            elif test_type == "get_template_permissions":
                actual_result = self.template_manager.get_template_permissions(**test_data)
            elif test_type == "export_template":
                actual_result = self.template_manager.export_template(**test_data)
            elif test_type == "import_template":
                actual_result = self.template_manager.import_template(**test_data)
            elif test_type == "get_template_recommendations":
                actual_result = self.template_manager.get_template_recommendations(**test_data)
            elif test_type == "rate_template":
                actual_result = self.template_manager.rate_template(**test_data)
            elif test_type == "get_template_usage_stats":
                actual_result = self.template_manager.get_template_usage_stats(**test_data)
            else:
                return {
                    "passed": False,
                    "test_type": test_type,
                    "error": f"Invalid test type: {test_type}"
                }
            
            # Check result
            passed = self._check_result(actual_result, expected_result)
            
            return {
                "passed": passed,
                "test_type": test_type,
                "actual_result": actual_result,
                "expected_result": expected_result
            }
            
        except Exception as e:
            return {
                "passed": False,
                "test_type": test_type,
                "error": str(e)
            }
    
    def _check_result(self, actual_result: Dict[str, Any], expected_result: Dict[str, Any]) -> bool:
        """Check if actual result matches expected result"""
        # For simple success checks
        if "success" in expected_result:
            if expected_result["success"] != actual_result.get("success", False):
                return False
        
        # For more specific checks
        for key, expected_value in expected_result.items():
            if key not in actual_result:
                return False
            
            actual_value = actual_result[key]
            
            # Check type
            if type(expected_value) != type(actual_value):
                return False
            
            # Check value
            if isinstance(expected_value, dict):
                if not self._check_result(actual_value, expected_value):
                    return False
            elif isinstance(expected_value, list):
                if len(expected_value) != len(actual_value):
                    return False
                
                for i, item in enumerate(expected_value):
                    if isinstance(item, dict):
                        if not self._check_result(actual_value[i], item):
                            return False
                    elif item != actual_value[i]:
                        return False
            elif expected_value != actual_value:
                return False
        
        return True
```

## Conclusion

The user template management system provides a comprehensive framework for creating, customizing, sharing, and managing prompt templates in the Aideon AI Lite platform. By leveraging the enhanced modular prompt architecture and prompt analytics system, it enables users to create high-quality templates that improve prompt performance and token efficiency.

The design includes intuitive template creation, powerful customization options, version control, sharing and collaboration features, performance insights, cross-project compatibility, enterprise integration, and adaptive learning. It also provides a visual template editor for non-technical users and robust enterprise features for governance and compliance.

The implementation plan outlines a phased approach to developing the system, with comprehensive testing and validation to ensure quality and effectiveness.
