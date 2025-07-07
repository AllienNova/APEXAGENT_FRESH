"""
Advanced dynamic prompt construction for the Aideon AI Lite platform.
This module provides an intelligent engine that builds optimized prompts
based on task context and user preferences.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import re
import logging
from prompt_engineering.enhanced_architecture import ModularPrompt
from prompt_engineering.template_library import get_template, TASK_CATEGORIES, COMPLEXITY_LEVELS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedPromptConstructor:
    """
    Advanced dynamic prompt construction engine that builds optimized prompts
    based on task context and user preferences.
    """
    
    def __init__(self):
        """Initialize the prompt constructor with task analyzers."""
        self.task_analyzers = {
            "software_development": self._analyze_software_task,
            "data_analysis": self._analyze_data_task,
            "content_creation": self._analyze_content_task,
            "business_operations": self._analyze_business_task,
            "system_administration": self._analyze_system_task,
        }
        
        # Keywords for complexity detection
        self.complexity_indicators = {
            "simple": ["simple", "basic", "quick", "brief", "straightforward", "easy"],
            "complex": ["complex", "advanced", "sophisticated", "detailed", "comprehensive", 
                       "thorough", "in-depth", "extensive", "complete"]
        }
    
    def construct_prompt(self, 
                         task_description: str, 
                         user_preferences: Dict[str, Any] = None,
                         user_history: Dict[str, Any] = None) -> str:
        """
        Construct an optimized prompt based on task description, user preferences, and history.
        
        Args:
            task_description: Description of the task to be performed
            user_preferences: User's preferences for prompt parameters
            user_history: User's interaction history
            
        Returns:
            Optimized prompt string
        """
        # Default values
        user_preferences = user_preferences or {}
        user_history = user_history or {}
        
        # Analyze task to determine category and complexity
        task_category, task_complexity, task_params = self._analyze_task(task_description)
        
        # Select appropriate template
        template_name = self._select_template(task_category, task_complexity, user_preferences)
        
        # Get template data
        template_data = get_template(template_name)
        
        # Create modular prompt from template
        prompt = ModularPrompt.from_template(template_data)
        
        # Customize prompt based on task parameters
        self._customize_prompt(prompt, task_params, user_preferences, user_history)
        
        # Apply token optimization if needed
        if user_preferences.get("optimize_tokens", False):
            prompt = prompt.optimize_tokens()
        
        # Convert to string
        prompt_str = prompt.to_prompt_string()
        
        # Apply final token optimization
        optimized_prompt_str = self._optimize_tokens(prompt_str, task_category)
        
        logger.info(f"Constructed prompt for {task_category}/{task_complexity} task")
        return optimized_prompt_str
    
    def _analyze_task(self, task_description: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Analyze the task description to determine category, complexity, and parameters.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Tuple of (task_category, task_complexity, task_params)
        """
        # Default values
        task_category = "general"
        task_complexity = "standard"
        task_params = {}
        
        # Check for keywords indicating task category
        for category, analyzer in self.task_analyzers.items():
            if analyzer(task_description, task_params):
                task_category = category
                break
        
        # Determine complexity based on task description
        task_complexity = self._determine_complexity(task_description)
        
        # Add task description to parameters
        task_params["description"] = task_description
        
        return task_category, task_complexity, task_params
    
    def _determine_complexity(self, task_description: str) -> str:
        """
        Determine the complexity level of a task based on its description.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Complexity level (simple, standard, or complex)
        """
        # Check for explicit complexity indicators
        for complexity, indicators in self.complexity_indicators.items():
            if any(indicator in task_description.lower() for indicator in indicators):
                return complexity
        
        # Determine complexity based on description length
        word_count = len(task_description.split())
        if word_count < 20:
            return "simple"
        elif word_count > 100:
            return "complex"
        
        # Check for multiple requirements or steps
        if task_description.count(",") > 5 or task_description.count(";") > 2:
            return "complex"
        
        # Default to standard
        return "standard"
    
    def _select_template(self, 
                        task_category: str, 
                        task_complexity: str, 
                        user_preferences: Dict[str, Any]) -> str:
        """
        Select the most appropriate template based on task category, complexity, and user preferences.
        
        Args:
            task_category: Category of the task
            task_complexity: Complexity of the task
            user_preferences: User's preferences
            
        Returns:
            Template name
        """
        # Check if user has a preferred template for this category
        preferred_template = user_preferences.get("preferred_template")
        if preferred_template:
            parts = preferred_template.split('/')
            if len(parts) == 2 and parts[0] == task_category:
                return preferred_template
        
        # Select template based on category and complexity
        template_name = f"{task_category}/{task_complexity}"
        
        return template_name
    
    def _customize_prompt(self, 
                         prompt: ModularPrompt, 
                         task_params: Dict[str, Any],
                         user_preferences: Dict[str, Any],
                         user_history: Dict[str, Any]):
        """
        Customize the prompt based on task parameters, user preferences, and history.
        
        Args:
            prompt: ModularPrompt to customize
            task_params: Task-specific parameters
            user_preferences: User's preferences
            user_history: User's interaction history
        """
        # Update operational parameters based on user preferences
        for param in ["intelligence_level", "verbosity", "creativity", "format_preference"]:
            if param in user_preferences:
                prompt.operational_parameters[param] = user_preferences[param]
        
        # Update task context based on user history
        if "current_project" in user_history:
            prompt.task_context["project"] = user_history["current_project"]
        
        if "recent_interactions" in user_history and user_history["recent_interactions"]:
            prompt.task_context["previous_context"] = "Previous interactions related to this task"
        
        # Add task-specific parameters
        for key, value in task_params.items():
            if key.startswith("rule_"):
                # Add as execution rule
                prompt.execution_rules.append(value)
            elif key.startswith("error_"):
                # Add as error handling
                prompt.error_handling.append(value)
            elif key != "description":  # Skip the full description
                # Add as task context
                prompt.task_context[key] = value
    
    def _optimize_tokens(self, prompt_str: str, task_category: str) -> str:
        """
        Apply token optimization strategies based on task category.
        
        Args:
            prompt_str: Prompt string to optimize
            task_category: Category of the task
            
        Returns:
            Optimized prompt string
        """
        # Remove redundant whitespace
        optimized = re.sub(r'\n\s*\n', '\n\n', prompt_str)
        optimized = re.sub(r' +', ' ', optimized)
        
        # Apply category-specific optimizations
        if task_category == "software_development":
            # Abbreviate common programming terms
            replacements = {
                r'\bfunction\b': 'func',
                r'\bparameter\b': 'param',
                r'\bimplementation\b': 'impl',
                r'\bdocumentation\b': 'docs',
                r'\bapplication\b': 'app',
                r'\bdevelopment\b': 'dev'
            }
            for pattern, replacement in replacements.items():
                optimized = re.sub(pattern, replacement, optimized)
        
        elif task_category == "data_analysis":
            # Abbreviate common data analysis terms
            replacements = {
                r'\bvisualization\b': 'viz',
                r'\bstatistics\b': 'stats',
                r'\banalysis\b': 'analysis',
                r'\bdistribution\b': 'dist',
                r'\bcorrelation\b': 'corr'
            }
            for pattern, replacement in replacements.items():
                optimized = re.sub(pattern, replacement, optimized)
        
        return optimized
    
    # Task analyzers
    def _analyze_software_task(self, task_description: str, task_params: Dict[str, Any]) -> bool:
        """
        Analyze software development tasks.
        
        Args:
            task_description: Description of the task
            task_params: Dictionary to populate with task parameters
            
        Returns:
            Whether the task is a software development task
        """
        keywords = ["code", "program", "develop", "build", "implement", "debug", "function", 
                   "class", "object", "method", "api", "framework", "library", "software",
                   "app", "application", "website", "web app", "mobile app", "script"]
        
        if any(keyword in task_description.lower() for keyword in keywords):
            # Extract programming language if mentioned
            languages = ["python", "javascript", "typescript", "java", "c#", "c++", "go", 
                        "rust", "ruby", "php", "swift", "kotlin", "scala"]
            for lang in languages:
                pattern = r'\b' + re.escape(lang) + r'\b'
                if re.search(pattern, task_description.lower()):
                    task_params["programming_language"] = lang
                    break
            
            # Extract framework if mentioned
            frameworks = ["react", "angular", "vue", "django", "flask", "spring", "express",
                         "next.js", "nuxt", "laravel", "rails", "asp.net", "tensorflow"]
            for framework in frameworks:
                pattern = r'\b' + re.escape(framework) + r'\b'
                if re.search(pattern, task_description.lower()):
                    task_params["framework"] = framework
                    break
            
            # Detect task type
            if any(kw in task_description.lower() for kw in ["bug", "fix", "issue", "error", "debug"]):
                task_params["task_type"] = "debugging"
            elif any(kw in task_description.lower() for kw in ["test", "unit test", "integration test"]):
                task_params["task_type"] = "testing"
            elif any(kw in task_description.lower() for kw in ["refactor", "improve", "optimize"]):
                task_params["task_type"] = "refactoring"
            elif any(kw in task_description.lower() for kw in ["new", "create", "implement", "develop"]):
                task_params["task_type"] = "development"
            
            return True
        return False
    
    def _analyze_data_task(self, task_description: str, task_params: Dict[str, Any]) -> bool:
        """
        Analyze data analysis tasks.
        
        Args:
            task_description: Description of the task
            task_params: Dictionary to populate with task parameters
            
        Returns:
            Whether the task is a data analysis task
        """
        keywords = ["data", "analysis", "analyze", "dataset", "statistics", "visualization", 
                   "chart", "graph", "plot", "pandas", "numpy", "regression", "correlation",
                   "machine learning", "ml", "ai", "predict", "cluster", "classify"]
        
        if any(keyword in task_description.lower() for keyword in keywords):
            # Extract data type if mentioned
            data_types = ["csv", "excel", "database", "sql", "json", "api", "xml", "text"]
            for data_type in data_types:
                pattern = r'\b' + re.escape(data_type) + r'\b'
                if re.search(pattern, task_description.lower()):
                    task_params["data_source"] = data_type
                    break
            
            # Extract analysis type if mentioned
            analysis_types = {
                "descriptive": ["descriptive", "summary", "summarize", "describe"],
                "exploratory": ["exploratory", "explore", "eda"],
                "predictive": ["predictive", "predict", "forecast", "regression"],
                "prescriptive": ["prescriptive", "recommend", "optimization"],
                "statistical": ["statistical", "hypothesis", "test", "significance"]
            }
            
            for analysis_type, indicators in analysis_types.items():
                if any(indicator in task_description.lower() for indicator in indicators):
                    task_params["analysis_type"] = analysis_type
                    break
            
            # Detect visualization needs
            if any(kw in task_description.lower() for kw in ["visual", "chart", "graph", "plot", "dashboard"]):
                task_params["needs_visualization"] = True
            
            return True
        return False
    
    def _analyze_content_task(self, task_description: str, task_params: Dict[str, Any]) -> bool:
        """
        Analyze content creation tasks.
        
        Args:
            task_description: Description of the task
            task_params: Dictionary to populate with task parameters
            
        Returns:
            Whether the task is a content creation task
        """
        keywords = ["write", "content", "article", "blog", "essay", "report", "document", 
                   "research", "summarize", "creative", "story", "narrative", "post",
                   "copywriting", "content marketing", "seo", "email"]
        
        if any(keyword in task_description.lower() for keyword in keywords):
            # Extract content type if mentioned
            content_types = {
                "article": ["article", "blog post", "blog"],
                "report": ["report", "white paper", "case study"],
                "email": ["email", "newsletter", "campaign"],
                "social": ["social media", "post", "tweet", "linkedin"],
                "creative": ["story", "creative", "narrative", "fiction"],
                "technical": ["documentation", "technical", "manual", "guide"]
            }
            
            for content_type, indicators in content_types.items():
                if any(indicator in task_description.lower() for indicator in indicators):
                    task_params["content_type"] = content_type
                    break
            
            # Detect tone if mentioned
            tones = {
                "formal": ["formal", "professional", "academic"],
                "conversational": ["conversational", "casual", "friendly"],
                "persuasive": ["persuasive", "convincing", "sales"],
                "informative": ["informative", "educational", "instructional"]
            }
            
            for tone, indicators in tones.items():
                if any(indicator in task_description.lower() for indicator in indicators):
                    task_params["tone"] = tone
                    break
            
            return True
        return False
    
    def _analyze_business_task(self, task_description: str, task_params: Dict[str, Any]) -> bool:
        """
        Analyze business operations tasks.
        
        Args:
            task_description: Description of the task
            task_params: Dictionary to populate with task parameters
            
        Returns:
            Whether the task is a business operations task
        """
        keywords = ["business", "strategy", "plan", "market", "financial", "budget", 
                   "forecast", "analysis", "proposal", "presentation", "project management",
                   "operations", "process", "workflow", "efficiency", "optimization"]
        
        if any(keyword in task_description.lower() for keyword in keywords):
            # Extract business area if mentioned
            business_areas = {
                "strategy": ["strategy", "strategic", "planning", "growth"],
                "marketing": ["marketing", "brand", "customer", "market"],
                "finance": ["financial", "finance", "budget", "cost", "revenue"],
                "operations": ["operations", "process", "workflow", "efficiency"],
                "hr": ["hr", "human resources", "talent", "recruitment", "hiring"]
            }
            
            for area, indicators in business_areas.items():
                if any(indicator in task_description.lower() for indicator in indicators):
                    task_params["business_area"] = area
                    break
            
            # Detect deliverable type
            deliverables = {
                "plan": ["plan", "strategy", "roadmap"],
                "analysis": ["analysis", "assessment", "evaluation"],
                "report": ["report", "summary", "overview"],
                "presentation": ["presentation", "slides", "deck"]
            }
            
            for deliverable, indicators in deliverables.items():
                if any(indicator in task_description.lower() for indicator in indicators):
                    task_params["deliverable_type"] = deliverable
                    break
            
            return True
        return False
    
    def _analyze_system_task(self, task_description: str, task_params: Dict[str, Any]) -> bool:
        """
        Analyze system administration tasks.
        
        Args:
            task_description: Description of the task
            task_params: Dictionary to populate with task parameters
            
        Returns:
            Whether the task is a system administration task
        """
        keywords = ["system", "server", "network", "configuration", "setup", "install", 
                   "deploy", "security", "backup", "monitoring", "infrastructure",
                   "cloud", "aws", "azure", "gcp", "devops", "ci/cd", "container"]
        
        if any(keyword in task_description.lower() for keyword in keywords):
            # Extract system type if mentioned
            system_types = {
                "linux": ["linux", "ubuntu", "debian", "centos", "redhat", "unix"],
                "windows": ["windows", "microsoft", "active directory"],
                "cloud": ["aws", "amazon", "azure", "microsoft", "gcp", "google cloud"],
                "container": ["docker", "kubernetes", "k8s", "container"],
                "network": ["network", "router", "switch", "firewall", "vpn"]
            }
            
            for system_type, indicators in system_types.items():
                if any(indicator in task_description.lower() for indicator in indicators):
                    task_params["system_type"] = system_type
                    break
            
            # Detect task type
            task_types = {
                "setup": ["setup", "install", "configure", "provision"],
                "maintenance": ["update", "upgrade", "patch", "maintain"],
                "security": ["security", "secure", "harden", "vulnerability"],
                "monitoring": ["monitor", "alert", "log", "observe"],
                "backup": ["backup", "restore", "recovery", "disaster"]
            }
            
            for task_type, indicators in task_types.items():
                if any(indicator in task_description.lower() for indicator in indicators):
                    task_params["admin_task_type"] = task_type
                    break
            
            return True
        return False
