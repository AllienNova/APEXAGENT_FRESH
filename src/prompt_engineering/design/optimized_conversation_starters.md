# Optimized Conversation Starters Design

## Overview

This document outlines the design for optimized conversation starters for the Aideon AI Lite platform. Building upon the enhanced modular prompt architecture and advanced dynamic prompt construction, this component provides standardized, context-aware conversation initiators with clear parameter settings.

## Design Goals

1. **Standardization** - Create consistent conversation starter formats across different use cases
2. **Context Awareness** - Adapt conversation starters based on task context and user preferences
3. **Domain Adaptation** - Provide specialized starters for different domains and industries
4. **Parameter Clarity** - Include explicit parameter settings for intelligence level, verbosity, etc.
5. **Efficiency** - Optimize token usage while maintaining effectiveness
6. **Adaptability** - Support different conversation styles and user preferences
7. **Measurability** - Enable analytics on conversation starter effectiveness

## Core Architecture

### ConversationStarter Class

The `ConversationStarter` class represents a standardized conversation starter:

```python
class ConversationStarter:
    """
    Represents a standardized conversation starter with explicit parameters.
    """
    
    def __init__(self, 
                template_id: str,
                name: str,
                description: str,
                starter_text: str,
                parameters: Dict[str, Any] = None,
                domain: str = "general",
                category: str = "general",
                tags: List[str] = None,
                version: str = "1.0.0"):
        """Initialize the conversation starter"""
        self.template_id = template_id
        self.name = name
        self.description = description
        self.starter_text = starter_text
        self.parameters = parameters or {}
        self.domain = domain
        self.category = category
        self.tags = tags or []
        self.version = version
        self.created_at = datetime.datetime.now().isoformat()
        self.usage_count = 0
        self.success_rate = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "starter_text": self.starter_text,
            "parameters": self.parameters,
            "domain": self.domain,
            "category": self.category,
            "tags": self.tags,
            "version": self.version,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationStarter":
        """Create from dictionary"""
        instance = cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data["description"],
            starter_text=data["starter_text"],
            parameters=data.get("parameters", {}),
            domain=data.get("domain", "general"),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            version=data.get("version", "1.0.0")
        )
        
        if "created_at" in data:
            instance.created_at = data["created_at"]
        
        if "usage_count" in data:
            instance.usage_count = data["usage_count"]
        
        if "success_rate" in data:
            instance.success_rate = data["success_rate"]
        
        return instance
    
    def format(self, context: Dict[str, Any] = None) -> str:
        """
        Format the starter text with context variables.
        
        Args:
            context: Context variables for formatting
            
        Returns:
            Formatted starter text
        """
        if not context:
            return self.starter_text
        
        try:
            return self.starter_text.format(**context)
        except KeyError as e:
            # Log missing key
            logging.warning(f"Missing context key in conversation starter: {str(e)}")
            return self.starter_text
        except Exception as e:
            # Log other errors
            logging.error(f"Error formatting conversation starter: {str(e)}")
            return self.starter_text
    
    def update_metrics(self, success: bool):
        """
        Update usage metrics for the conversation starter.
        
        Args:
            success: Whether the conversation was successful
        """
        self.usage_count += 1
        
        # Update success rate using weighted average
        if self.usage_count == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            weight = 1.0 / self.usage_count
            self.success_rate = (self.success_rate * (1 - weight)) + (1.0 if success else 0.0) * weight
```

### ConversationStarterManager Class

The `ConversationStarterManager` class manages a library of conversation starters:

```python
class ConversationStarterManager:
    """
    Manages a library of conversation starters.
    """
    
    def __init__(self, storage_dir: str = None):
        """Initialize the conversation starter manager"""
        # Set storage directory
        if storage_dir:
            self.storage_dir = storage_dir
        else:
            self.storage_dir = os.path.join(os.path.dirname(__file__), "conversation_starters")
        
        # Create directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize starter storage
        self.starters = {}
        
        # Load existing starters
        self._load_starters()
    
    def register_starter(self, starter: ConversationStarter) -> bool:
        """
        Register a new conversation starter.
        
        Args:
            starter: Conversation starter to register
            
        Returns:
            Whether the registration was successful
        """
        # Check if starter already exists
        if starter.template_id in self.starters:
            # Update existing starter
            self.starters[starter.template_id] = starter
        else:
            # Add new starter
            self.starters[starter.template_id] = starter
        
        # Save starters
        self._save_starters()
        
        return True
    
    def get_starter(self, template_id: str) -> Optional[ConversationStarter]:
        """
        Get a conversation starter by ID.
        
        Args:
            template_id: ID of the starter to get
            
        Returns:
            Conversation starter or None if not found
        """
        return self.starters.get(template_id)
    
    def list_starters(self, 
                     domain: str = None, 
                     category: str = None,
                     tags: List[str] = None) -> List[ConversationStarter]:
        """
        List conversation starters with optional filtering.
        
        Args:
            domain: Filter by domain
            category: Filter by category
            tags: Filter by tags (must have all specified tags)
            
        Returns:
            List of matching conversation starters
        """
        results = []
        
        for starter in self.starters.values():
            # Apply domain filter
            if domain and starter.domain != domain and starter.domain != "general":
                continue
            
            # Apply category filter
            if category and starter.category != category and starter.category != "general":
                continue
            
            # Apply tags filter
            if tags and not all(tag in starter.tags for tag in tags):
                continue
            
            results.append(starter)
        
        return results
    
    def select_starter(self, 
                      task_analysis: TaskAnalysis,
                      context_analysis: ContextAnalysis,
                      user_preferences: Dict[str, Any] = None) -> Optional[ConversationStarter]:
        """
        Select the most appropriate conversation starter based on task and context.
        
        Args:
            task_analysis: Result of task analysis
            context_analysis: Result of context analysis
            user_preferences: User's preferences
            
        Returns:
            Selected conversation starter or None if no suitable starter found
        """
        # Default values
        user_preferences = user_preferences or {}
        
        # Check if user has a preferred starter
        preferred_starter_id = user_preferences.get("preferred_starter")
        if preferred_starter_id and preferred_starter_id in self.starters:
            return self.starters[preferred_starter_id]
        
        # Filter starters by domain and category
        candidates = self.list_starters(
            domain=task_analysis.domain,
            category=task_analysis.task_category
        )
        
        # If no domain/category specific starters, try category only
        if not candidates:
            candidates = self.list_starters(category=task_analysis.task_category)
        
        # If still no candidates, try domain only
        if not candidates:
            candidates = self.list_starters(domain=task_analysis.domain)
        
        # If still no candidates, use general starters
        if not candidates:
            candidates = self.list_starters(domain="general", category="general")
        
        # If still no candidates, return None
        if not candidates:
            return None
        
        # Score candidates based on relevance
        scored_candidates = []
        for starter in candidates:
            score = self._calculate_relevance(starter, task_analysis, context_analysis, user_preferences)
            scored_candidates.append((starter, score))
        
        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Return highest scoring starter
        return scored_candidates[0][0] if scored_candidates else None
    
    def format_starter(self, 
                      starter: ConversationStarter,
                      task_analysis: TaskAnalysis,
                      context_analysis: ContextAnalysis,
                      user_preferences: Dict[str, Any] = None) -> str:
        """
        Format a conversation starter with context variables.
        
        Args:
            starter: Conversation starter to format
            task_analysis: Result of task analysis
            context_analysis: Result of context analysis
            user_preferences: User's preferences
            
        Returns:
            Formatted conversation starter text
        """
        # Default values
        user_preferences = user_preferences or {}
        
        # Create context dictionary
        context = {
            # Task parameters
            "task_type": task_analysis.task_type,
            "task_category": task_analysis.task_category,
            "task_complexity": task_analysis.complexity,
            "task_domain": task_analysis.domain,
            
            # Context parameters
            "project": context_analysis.project,
            "priority": context_analysis.priority,
            
            # User preferences
            "intelligence_level": user_preferences.get("intelligence_level", "Adaptive"),
            "verbosity": user_preferences.get("verbosity", "Balanced"),
            "creativity": user_preferences.get("creativity", "Balanced"),
            "format_preference": user_preferences.get("format_preference", "Default"),
        }
        
        # Add task parameters
        for key, value in task_analysis.parameters.items():
            context[key] = value
        
        # Add custom context
        for key, value in context_analysis.custom_context.items():
            context[key] = value
        
        # Format starter text
        return starter.format(context)
    
    def update_starter_metrics(self, template_id: str, success: bool):
        """
        Update metrics for a conversation starter.
        
        Args:
            template_id: ID of the starter to update
            success: Whether the conversation was successful
        """
        if template_id in self.starters:
            self.starters[template_id].update_metrics(success)
            self._save_starters()
    
    def _calculate_relevance(self, 
                           starter: ConversationStarter,
                           task_analysis: TaskAnalysis,
                           context_analysis: ContextAnalysis,
                           user_preferences: Dict[str, Any]) -> float:
        """Calculate relevance score for a starter"""
        score = 0.0
        
        # Base score based on domain and category match
        if starter.domain == task_analysis.domain:
            score += 2.0
        elif starter.domain == "general":
            score += 1.0
        
        if starter.category == task_analysis.task_category:
            score += 2.0
        elif starter.category == "general":
            score += 1.0
        
        # Adjust score based on tags
        for tag in starter.tags:
            if tag in task_analysis.keywords:
                score += 0.5
        
        # Adjust score based on success rate
        score += starter.success_rate
        
        # Adjust score based on user preferences
        if user_preferences:
            for key, value in user_preferences.items():
                if key in starter.parameters and starter.parameters[key] == value:
                    score += 0.5
        
        return score
    
    def _load_starters(self):
        """Load starters from disk"""
        starters_file = os.path.join(self.storage_dir, "starters.json")
        if os.path.exists(starters_file):
            try:
                with open(starters_file, 'r') as f:
                    data = json.load(f)
                
                # Load starters
                for starter_data in data["starters"]:
                    starter = ConversationStarter.from_dict(starter_data)
                    self.starters[starter.template_id] = starter
            except Exception as e:
                logging.error(f"Error loading conversation starters: {str(e)}")
    
    def _save_starters(self):
        """Save starters to disk"""
        starters_file = os.path.join(self.storage_dir, "starters.json")
        try:
            # Prepare data
            data = {
                "starters": [starter.to_dict() for starter in self.starters.values()]
            }
            
            # Write to file
            with open(starters_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving conversation starters: {str(e)}")
```

### ConversationStarterIntegration Class

The `ConversationStarterIntegration` class integrates conversation starters with the prompt construction system:

```python
class ConversationStarterIntegration:
    """
    Integrates conversation starters with the prompt construction system.
    """
    
    def __init__(self, 
                starter_manager: ConversationStarterManager,
                prompt_constructor: AdvancedPromptConstructor):
        """Initialize the conversation starter integration"""
        self.starter_manager = starter_manager
        self.prompt_constructor = prompt_constructor
    
    def start_conversation(self, 
                          task_description: str,
                          user_context: Dict[str, Any] = None,
                          user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start a conversation with an appropriate starter.
        
        Args:
            task_description: Description of the task
            user_context: User's context information
            user_preferences: User's preferences
            
        Returns:
            Dictionary with starter text and metadata
        """
        # Default values
        user_context = user_context or {}
        user_preferences = user_preferences or {}
        
        try:
            # Analyze task
            task_analysis = self.prompt_constructor.task_analyzer.analyze(task_description)
            
            # Analyze context
            context_analysis = self.prompt_constructor.context_analyzer.analyze(user_context, task_analysis)
            
            # Select appropriate starter
            starter = self.starter_manager.select_starter(
                task_analysis, context_analysis, user_preferences)
            
            if not starter:
                # Use default starter if no appropriate starter found
                starter = self._get_default_starter()
            
            # Format starter text
            starter_text = self.starter_manager.format_starter(
                starter, task_analysis, context_analysis, user_preferences)
            
            # Construct prompt for the task
            prompt_result = self.prompt_constructor.construct_prompt(
                task_description, user_context, user_preferences)
            
            # Return result
            return {
                "success": True,
                "starter_text": starter_text,
                "starter_id": starter.template_id,
                "starter_name": starter.name,
                "task_category": task_analysis.task_category,
                "task_domain": task_analysis.domain,
                "prompt": prompt_result.prompt if prompt_result.success else None
            }
            
        except Exception as e:
            # Log error
            logging.error(f"Error starting conversation: {str(e)}")
            
            # Return error result
            return {
                "success": False,
                "error": str(e),
                "starter_text": self._get_fallback_starter_text()
            }
    
    def record_conversation_result(self, starter_id: str, success: bool):
        """
        Record the result of a conversation.
        
        Args:
            starter_id: ID of the starter used
            success: Whether the conversation was successful
        """
        self.starter_manager.update_starter_metrics(starter_id, success)
    
    def _get_default_starter(self) -> ConversationStarter:
        """Get default conversation starter"""
        # Try to get general starter
        starter = self.starter_manager.get_starter("general/default")
        
        # If not found, create a new one
        if not starter:
            starter = ConversationStarter(
                template_id="general/default",
                name="Default Starter",
                description="Default conversation starter for general use",
                starter_text="I'll help you with your task. Let me analyze what you need.",
                parameters={
                    "intelligence_level": "Adaptive",
                    "verbosity": "Balanced",
                    "creativity": "Balanced",
                    "format_preference": "Default"
                },
                domain="general",
                category="general",
                tags=["default", "general"]
            )
            
            # Register the starter
            self.starter_manager.register_starter(starter)
        
        return starter
    
    def _get_fallback_starter_text(self) -> str:
        """Get fallback starter text for error cases"""
        return "I'll help you with your task. Please provide more details if needed."
```

## Standard Conversation Starters

The implementation includes a comprehensive library of standard conversation starters:

### General Starters

```python
general_starters = [
    ConversationStarter(
        template_id="general/default",
        name="Default Starter",
        description="Default conversation starter for general use",
        starter_text="I'll help you with your task. Let me analyze what you need.",
        parameters={
            "intelligence_level": "Adaptive",
            "verbosity": "Balanced",
            "creativity": "Balanced",
            "format_preference": "Default"
        },
        domain="general",
        category="general",
        tags=["default", "general"]
    ),
    
    ConversationStarter(
        template_id="general/detailed",
        name="Detailed Starter",
        description="Detailed conversation starter for complex tasks",
        starter_text="I'll help you with your {task_complexity} {task_category} task. I'll provide a detailed analysis and step-by-step approach.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Balanced",
            "format_preference": "Structured"
        },
        domain="general",
        category="general",
        tags=["detailed", "complex", "thorough"]
    ),
    
    ConversationStarter(
        template_id="general/concise",
        name="Concise Starter",
        description="Concise conversation starter for simple tasks",
        starter_text="I'll help you with your {task_category} task. I'll be concise and to the point.",
        parameters={
            "intelligence_level": "Adaptive",
            "verbosity": "Concise",
            "creativity": "Practical",
            "format_preference": "Default"
        },
        domain="general",
        category="general",
        tags=["concise", "simple", "brief"]
    ),
    
    ConversationStarter(
        template_id="general/creative",
        name="Creative Starter",
        description="Creative conversation starter for innovative tasks",
        starter_text="I'll help you with your {task_category} task. I'll take a creative approach to provide innovative solutions.",
        parameters={
            "intelligence_level": "Adaptive",
            "verbosity": "Balanced",
            "creativity": "High",
            "format_preference": "Default"
        },
        domain="general",
        category="general",
        tags=["creative", "innovative", "original"]
    )
]
```

### Software Development Starters

```python
software_development_starters = [
    ConversationStarter(
        template_id="software_development/default",
        name="Software Development Starter",
        description="Default starter for software development tasks",
        starter_text="I'll help you with your software development task. Let me analyze your requirements and provide a solution.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Balanced",
            "creativity": "Balanced",
            "format_preference": "Structured"
        },
        domain="general",
        category="software_development",
        tags=["coding", "development", "programming"]
    ),
    
    ConversationStarter(
        template_id="software_development/code_generation",
        name="Code Generation Starter",
        description="Starter for code generation tasks",
        starter_text="I'll help you generate code for your {programming_language} project. I'll focus on writing clean, efficient, and well-documented code.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Balanced",
            "format_preference": "Structured"
        },
        domain="general",
        category="software_development",
        tags=["code", "generation", "programming"]
    ),
    
    ConversationStarter(
        template_id="software_development/debugging",
        name="Debugging Starter",
        description="Starter for debugging tasks",
        starter_text="I'll help you debug your {programming_language} code. I'll analyze the issue, identify the root cause, and suggest a fix.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="general",
        category="software_development",
        tags=["debugging", "troubleshooting", "bug fixing"]
    ),
    
    ConversationStarter(
        template_id="software_development/code_review",
        name="Code Review Starter",
        description="Starter for code review tasks",
        starter_text="I'll review your {programming_language} code. I'll focus on code quality, performance, security, and best practices.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="general",
        category="software_development",
        tags=["code review", "quality", "best practices"]
    )
]
```

### Data Analysis Starters

```python
data_analysis_starters = [
    ConversationStarter(
        template_id="data_analysis/default",
        name="Data Analysis Starter",
        description="Default starter for data analysis tasks",
        starter_text="I'll help you with your data analysis task. Let me understand your data and requirements to provide meaningful insights.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Balanced",
            "creativity": "Balanced",
            "format_preference": "Structured"
        },
        domain="general",
        category="data_analysis",
        tags=["data", "analysis", "insights"]
    ),
    
    ConversationStarter(
        template_id="data_analysis/exploratory",
        name="Exploratory Data Analysis Starter",
        description="Starter for exploratory data analysis tasks",
        starter_text="I'll help you explore your data. I'll analyze patterns, distributions, and relationships to provide comprehensive insights.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Balanced",
            "format_preference": "Structured"
        },
        domain="general",
        category="data_analysis",
        tags=["exploratory", "data", "analysis"]
    ),
    
    ConversationStarter(
        template_id="data_analysis/visualization",
        name="Data Visualization Starter",
        description="Starter for data visualization tasks",
        starter_text="I'll help you visualize your data. I'll create clear, informative, and visually appealing charts and graphs.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Balanced",
            "creativity": "High",
            "format_preference": "Visual"
        },
        domain="general",
        category="data_analysis",
        tags=["visualization", "charts", "graphs"]
    ),
    
    ConversationStarter(
        template_id="data_analysis/machine_learning",
        name="Machine Learning Starter",
        description="Starter for machine learning tasks",
        starter_text="I'll help you with your machine learning task. I'll design, implement, and evaluate models to solve your problem.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Balanced",
            "format_preference": "Structured"
        },
        domain="general",
        category="data_analysis",
        tags=["machine learning", "models", "prediction"]
    )
]
```

### Content Creation Starters

```python
content_creation_starters = [
    ConversationStarter(
        template_id="content_creation/default",
        name="Content Creation Starter",
        description="Default starter for content creation tasks",
        starter_text="I'll help you create content for your {project}. Let me understand your requirements and audience to craft compelling content.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Balanced",
            "creativity": "High",
            "format_preference": "Default"
        },
        domain="general",
        category="content_creation",
        tags=["content", "creation", "writing"]
    ),
    
    ConversationStarter(
        template_id="content_creation/article",
        name="Article Writing Starter",
        description="Starter for article writing tasks",
        starter_text="I'll help you write an article on {topic}. I'll create well-researched, engaging, and informative content.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "High",
            "format_preference": "Default"
        },
        domain="general",
        category="content_creation",
        tags=["article", "writing", "content"]
    ),
    
    ConversationStarter(
        template_id="content_creation/technical_documentation",
        name="Technical Documentation Starter",
        description="Starter for technical documentation tasks",
        starter_text="I'll help you create technical documentation for your {project}. I'll focus on clarity, accuracy, and completeness.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="general",
        category="content_creation",
        tags=["documentation", "technical", "writing"]
    ),
    
    ConversationStarter(
        template_id="content_creation/marketing",
        name="Marketing Content Starter",
        description="Starter for marketing content tasks",
        starter_text="I'll help you create marketing content for your {project}. I'll craft persuasive, engaging, and audience-focused messaging.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Balanced",
            "creativity": "High",
            "format_preference": "Default"
        },
        domain="general",
        category="content_creation",
        tags=["marketing", "content", "persuasive"]
    )
]
```

### Domain-Specific Starters

```python
healthcare_starters = [
    ConversationStarter(
        template_id="healthcare/default",
        name="Healthcare Starter",
        description="Default starter for healthcare tasks",
        starter_text="I'll help you with your healthcare-related task. I'll ensure compliance with regulations while addressing your specific needs.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="healthcare",
        category="general",
        tags=["healthcare", "medical", "clinical"]
    ),
    
    ConversationStarter(
        template_id="healthcare/clinical_workflow",
        name="Clinical Workflow Starter",
        description="Starter for clinical workflow tasks",
        starter_text="I'll help you optimize your clinical workflow. I'll focus on efficiency, safety, and patient care quality.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="healthcare",
        category="business_operations",
        tags=["clinical", "workflow", "optimization"]
    )
]

finance_starters = [
    ConversationStarter(
        template_id="finance/default",
        name="Finance Starter",
        description="Default starter for finance tasks",
        starter_text="I'll help you with your finance-related task. I'll ensure accuracy, compliance, and attention to detail.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="finance",
        category="general",
        tags=["finance", "financial", "banking"]
    ),
    
    ConversationStarter(
        template_id="finance/financial_analysis",
        name="Financial Analysis Starter",
        description="Starter for financial analysis tasks",
        starter_text="I'll help you with your financial analysis. I'll provide comprehensive insights and actionable recommendations.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="finance",
        category="data_analysis",
        tags=["financial", "analysis", "insights"]
    )
]

legal_starters = [
    ConversationStarter(
        template_id="legal/default",
        name="Legal Starter",
        description="Default starter for legal tasks",
        starter_text="I'll help you with your legal-related task. I'll focus on accuracy, compliance, and attention to detail.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="legal",
        category="general",
        tags=["legal", "law", "compliance"]
    ),
    
    ConversationStarter(
        template_id="legal/contract_analysis",
        name="Contract Analysis Starter",
        description="Starter for contract analysis tasks",
        starter_text="I'll help you analyze your contract. I'll identify key terms, potential issues, and provide recommendations.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="legal",
        category="content_creation",
        tags=["contract", "analysis", "legal"]
    )
]
```

### Enterprise-Specific Starters

```python
enterprise_starters = [
    ConversationStarter(
        template_id="enterprise/default",
        name="Enterprise Starter",
        description="Default starter for enterprise tasks",
        starter_text="I'll help you with your enterprise-level task. I'll focus on scalability, security, and business value.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="general",
        category="enterprise_integration",
        tags=["enterprise", "business", "corporate"]
    ),
    
    ConversationStarter(
        template_id="enterprise/compliance",
        name="Compliance Starter",
        description="Starter for compliance tasks",
        starter_text="I'll help you with your compliance requirements for {regulation}. I'll ensure thorough coverage and documentation.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="general",
        category="enterprise_integration",
        tags=["compliance", "regulation", "governance"]
    ),
    
    ConversationStarter(
        template_id="enterprise/architecture",
        name="Enterprise Architecture Starter",
        description="Starter for enterprise architecture tasks",
        starter_text="I'll help you design your enterprise architecture. I'll focus on scalability, security, and integration.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Balanced",
            "format_preference": "Structured"
        },
        domain="general",
        category="enterprise_integration",
        tags=["architecture", "enterprise", "design"]
    ),
    
    ConversationStarter(
        template_id="enterprise/security",
        name="Enterprise Security Starter",
        description="Starter for enterprise security tasks",
        starter_text="I'll help you with your enterprise security requirements. I'll focus on threat modeling, controls, and compliance.",
        parameters={
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Practical",
            "format_preference": "Structured"
        },
        domain="general",
        category="enterprise_integration",
        tags=["security", "enterprise", "protection"]
    )
]
```

## Starter Initialization

The implementation includes a function to initialize the standard conversation starters:

```python
def initialize_standard_starters(manager: ConversationStarterManager):
    """
    Initialize the standard conversation starters.
    
    Args:
        manager: Conversation starter manager
    """
    # Register general starters
    for starter in general_starters:
        manager.register_starter(starter)
    
    # Register software development starters
    for starter in software_development_starters:
        manager.register_starter(starter)
    
    # Register data analysis starters
    for starter in data_analysis_starters:
        manager.register_starter(starter)
    
    # Register content creation starters
    for starter in content_creation_starters:
        manager.register_starter(starter)
    
    # Register domain-specific starters
    for starter in healthcare_starters + finance_starters + legal_starters:
        manager.register_starter(starter)
    
    # Register enterprise-specific starters
    for starter in enterprise_starters:
        manager.register_starter(starter)
```

## Integration with Enhanced Modular Architecture

The conversation starters integrate with the enhanced modular architecture:

```python
class ModularPromptWithStarter(EnhancedModularPrompt):
    """
    Enhanced modular prompt with integrated conversation starter.
    """
    
    def __init__(self):
        """Initialize the modular prompt with starter"""
        super().__init__()
        self.starter = StarterSection()
    
    def to_xml(self) -> str:
        """Convert to XML string"""
        # Implementation details
        pass
    
    def to_prompt_string(self, context: Dict[str, Any] = None) -> str:
        """Convert to formatted prompt string with context applied"""
        # Get base prompt string
        prompt_string = super().to_prompt_string(context)
        
        # Add starter if available
        if self.starter and self.starter.text:
            starter_text = self.starter.text
            if context:
                try:
                    starter_text = starter_text.format(**context)
                except (KeyError, ValueError):
                    pass
            
            # Combine starter with prompt
            return f"{starter_text}\n\n{prompt_string}"
        
        return prompt_string

class StarterSection:
    """
    Represents the starter section of a modular prompt.
    """
    
    def __init__(self):
        """Initialize the starter section"""
        self.text = ""
        self.template_id = ""
        self.parameters = {}
```

## Implementation Plan

The implementation of optimized conversation starters will proceed in phases:

### Phase 1: Core Components
- Implement `ConversationStarter` class
- Develop `ConversationStarterManager` with basic functionality
- Create initial set of general starters
- Implement basic integration with prompt construction

### Phase 2: Expanded Starter Library
- Implement category-specific starters
- Develop domain-specific starters
- Create enterprise-specific starters
- Implement starter initialization function

### Phase 3: Context-Aware Selection
- Enhance starter selection algorithm
- Implement relevance scoring
- Develop context-based formatting
- Create metrics tracking

### Phase 4: Integration with Modular Architecture
- Implement `ModularPromptWithStarter` class
- Develop `StarterSection` for XML representation
- Create integration with template system
- Implement XML parsing and generation

### Phase 5: Testing and Validation
- Implement comprehensive test suite
- Develop validation metrics
- Create starter quality scoring
- Test across diverse scenarios

## Testing and Validation

The implementation includes comprehensive testing and validation:

```python
class ConversationStarterTester:
    """
    Tests conversation starters with various scenarios.
    """
    
    def __init__(self, starter_integration: ConversationStarterIntegration):
        """Initialize the conversation starter tester"""
        self.starter_integration = starter_integration
        self.test_cases = []
    
    def add_test_case(self, 
                     task_description: str, 
                     expected_category: str,
                     expected_domain: str,
                     user_context: Dict[str, Any] = None,
                     user_preferences: Dict[str, Any] = None):
        """Add a test case"""
        self.test_cases.append({
            "task_description": task_description,
            "expected_category": expected_category,
            "expected_domain": expected_domain,
            "user_context": user_context or {},
            "user_preferences": user_preferences or {}
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
        task_description = test_case["task_description"]
        expected_category = test_case["expected_category"]
        expected_domain = test_case["expected_domain"]
        user_context = test_case["user_context"]
        user_preferences = test_case["user_preferences"]
        
        # Start conversation
        result = self.starter_integration.start_conversation(
            task_description, user_context, user_preferences)
        
        # Check if conversation was started successfully
        if not result["success"]:
            return {
                "passed": False,
                "task_description": task_description,
                "error": result["error"]
            }
        
        # Check category
        category_correct = result["task_category"] == expected_category
        
        # Check domain
        domain_correct = result["task_domain"] == expected_domain
        
        # Check starter text
        starter_text_valid = bool(result["starter_text"])
        
        # Overall result
        passed = category_correct and domain_correct and starter_text_valid
        
        return {
            "passed": passed,
            "task_description": task_description,
            "expected_category": expected_category,
            "actual_category": result["task_category"],
            "category_correct": category_correct,
            "expected_domain": expected_domain,
            "actual_domain": result["task_domain"],
            "domain_correct": domain_correct,
            "starter_text": result["starter_text"],
            "starter_text_valid": starter_text_valid,
            "starter_id": result["starter_id"],
            "starter_name": result["starter_name"]
        }
```

## Conclusion

The optimized conversation starters design provides a comprehensive system for creating standardized, context-aware conversation initiators for the Aideon AI Lite platform. By leveraging the enhanced modular prompt architecture and advanced dynamic prompt construction, it enables more effective and efficient conversations across diverse use cases.

The design includes a robust starter library with general, category-specific, domain-specific, and enterprise-specific starters. It also provides sophisticated selection algorithms, context-aware formatting, and integration with the modular architecture.

The implementation plan outlines a phased approach to developing the system, with comprehensive testing and validation to ensure quality and effectiveness.
