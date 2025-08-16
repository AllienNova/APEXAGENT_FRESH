"""
Task-specific template expansion for the Aideon AI Lite platform.
This module provides a comprehensive library of prompt templates
optimized for different task categories and complexity levels.
"""

from typing import Dict, Any, List, Optional
import json
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

# Task categories
TASK_CATEGORIES = [
    "software_development",
    "data_analysis",
    "content_creation",
    "business_operations",
    "system_administration"
]

# Complexity levels
COMPLEXITY_LEVELS = ["simple", "standard", "complex"]

# Template registry
_template_registry = {}

def initialize_templates():
    """
    Initialize the template directory structure and default templates.
    """
    # Create base templates directory if it doesn't exist
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    
    # Create category subdirectories and default templates
    for category in TASK_CATEGORIES:
        category_dir = os.path.join(TEMPLATES_DIR, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Create default templates for each complexity level
        for complexity in COMPLEXITY_LEVELS:
            template_path = os.path.join(category_dir, f"{complexity}.json")
            if not os.path.exists(template_path):
                create_default_template(category, complexity, template_path)

def load_templates():
    """
    Load all templates from the templates directory.
    """
    global _template_registry
    
    # Ensure template directories exist
    initialize_templates()
    
    # Clear existing registry
    _template_registry = {}
    
    # Load all templates
    for category in TASK_CATEGORIES:
        category_dir = os.path.join(TEMPLATES_DIR, category)
        
        for template_file in os.listdir(category_dir):
            if template_file.endswith(".json"):
                complexity = template_file[:-5]  # Remove .json
                template_name = f"{category}/{complexity}"
                template_path = os.path.join(category_dir, template_file)
                
                try:
                    with open(template_path, 'r') as f:
                        template_data = json.load(f)
                        _template_registry[template_name] = template_data
                        logger.info(f"Loaded template: {template_name}")
                except Exception as e:
                    logger.error(f"Error loading template {template_path}: {str(e)}")

def create_default_template(category: str, complexity: str, template_path: str) -> Dict[str, Any]:
    """
    Create a default template for a category and complexity level.
    
    Args:
        category: Task category
        complexity: Complexity level
        template_path: Path to save the template
        
    Returns:
        Template data dictionary
    """
    # Base template structure
    template = {
        "system_identity": get_default_identity(category, complexity),
        "operational_parameters": get_default_parameters(complexity),
        "task_context": {
            "project": "",
            "previous_context": "",
            "priority": get_default_priority(complexity)
        },
        "execution_rules": get_default_rules_for_category(category, complexity),
        "error_handling": get_default_error_handling(complexity)
    }
    
    # Save template to file
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    logger.info(f"Created default template: {category}/{complexity}")
    return template

def get_default_identity(category: str, complexity: str) -> str:
    """
    Get default system identity for a category and complexity level.
    
    Args:
        category: Task category
        complexity: Complexity level
        
    Returns:
        Default system identity string
    """
    category_name = category.replace('_', ' ').title()
    
    if complexity == "simple":
        return f"Aideon AI Lite specialized in {category_name} tasks. I provide straightforward, efficient solutions."
    elif complexity == "complex":
        return f"Aideon AI Lite expert in complex {category_name} tasks. I provide sophisticated, comprehensive solutions with advanced techniques and best practices."
    else:  # standard
        return f"Aideon AI Lite specialized in {category_name} tasks. I provide balanced, effective solutions tailored to your needs."

def get_default_parameters(complexity: str) -> Dict[str, str]:
    """
    Get default operational parameters for a complexity level.
    
    Args:
        complexity: Complexity level
        
    Returns:
        Dictionary of default parameters
    """
    if complexity == "simple":
        return {
            "intelligence_level": "Standard",
            "verbosity": "Concise",
            "creativity": "Practical",
            "format_preference": "Structured"
        }
    elif complexity == "complex":
        return {
            "intelligence_level": "Expert",
            "verbosity": "Detailed",
            "creativity": "Balanced",
            "format_preference": "Comprehensive"
        }
    else:  # standard
        return {
            "intelligence_level": "Adaptive",
            "verbosity": "Balanced",
            "creativity": "Balanced",
            "format_preference": "Default"
        }

def get_default_priority(complexity: str) -> str:
    """
    Get default priority for a complexity level.
    
    Args:
        complexity: Complexity level
        
    Returns:
        Default priority string
    """
    if complexity == "simple":
        return "Speed"
    elif complexity == "complex":
        return "Quality"
    else:  # standard
        return "Balance"

def get_default_rules_for_category(category: str, complexity: str) -> List[str]:
    """
    Get default execution rules for a category and complexity level.
    
    Args:
        category: Task category
        complexity: Complexity level
        
    Returns:
        List of default execution rules
    """
    # Base rules for all categories
    base_rules = []
    
    # Add complexity-specific base rules
    if complexity == "simple":
        base_rules.append("Focus on providing quick, straightforward solutions")
        base_rules.append("Prioritize clarity and simplicity over comprehensiveness")
    elif complexity == "complex":
        base_rules.append("Provide comprehensive, detailed solutions")
        base_rules.append("Consider edge cases and potential issues")
        base_rules.append("Incorporate advanced techniques and best practices")
    else:  # standard
        base_rules.append("Balance thoroughness with efficiency")
        base_rules.append("Adapt level of detail based on task requirements")
    
    # Add category-specific rules
    if category == "software_development":
        category_rules = [
            "Prioritize code readability and maintainability",
            "Follow established coding standards and patterns",
            "Include appropriate error handling and validation"
        ]
        
        if complexity == "complex":
            category_rules.extend([
                "Write tests for critical functionality",
                "Document code with clear comments and docstrings",
                "Consider performance implications",
                "Implement proper logging and debugging support"
            ])
    
    elif category == "data_analysis":
        category_rules = [
            "Verify data quality and integrity before analysis",
            "Use appropriate statistical methods for the data type",
            "Visualize results in clear, informative ways"
        ]
        
        if complexity == "complex":
            category_rules.extend([
                "Document assumptions and limitations",
                "Provide actionable insights based on analysis",
                "Consider alternative analytical approaches",
                "Assess statistical significance and confidence levels"
            ])
    
    elif category == "content_creation":
        category_rules = [
            "Ensure content is well-structured and flows logically",
            "Adapt tone and style to the target audience",
            "Focus on clarity and engagement"
        ]
        
        if complexity == "complex":
            category_rules.extend([
                "Incorporate relevant research and citations",
                "Develop nuanced arguments with supporting evidence",
                "Consider multiple perspectives on the topic",
                "Optimize content for specific platforms or formats"
            ])
    
    elif category == "business_operations":
        category_rules = [
            "Focus on practical, actionable recommendations",
            "Consider business constraints and resources",
            "Align solutions with business objectives"
        ]
        
        if complexity == "complex":
            category_rules.extend([
                "Analyze potential risks and mitigation strategies",
                "Consider market trends and competitive landscape",
                "Provide implementation roadmaps with milestones",
                "Include metrics for measuring success"
            ])
    
    elif category == "system_administration":
        category_rules = [
            "Prioritize security and stability",
            "Document configuration changes and procedures",
            "Consider scalability and maintenance"
        ]
        
        if complexity == "complex":
            category_rules.extend([
                "Implement monitoring and alerting",
                "Design for high availability and disaster recovery",
                "Optimize for performance and resource utilization",
                "Automate routine tasks and maintenance"
            ])
    
    else:
        category_rules = ["Follow best practices for this task type"]
    
    # Combine base and category rules
    return base_rules + category_rules

def get_default_error_handling(complexity: str) -> List[str]:
    """
    Get default error handling rules for a complexity level.
    
    Args:
        complexity: Complexity level
        
    Returns:
        List of default error handling rules
    """
    # Base error handling for all complexity levels
    base_error_handling = [
        "Identify and report errors clearly",
        "Suggest potential solutions when errors occur"
    ]
    
    # Add complexity-specific error handling
    if complexity == "simple":
        return base_error_handling
    elif complexity == "complex":
        return base_error_handling + [
            "Provide context for why errors might be happening",
            "Implement graceful degradation when primary approaches fail",
            "Document error resolution steps for future reference",
            "Consider preventative measures to avoid similar errors"
        ]
    else:  # standard
        return base_error_handling + [
            "Provide context for why errors might be happening",
            "Implement graceful degradation when primary approaches fail"
        ]

def get_template(template_name: str) -> Dict[str, Any]:
    """
    Get a template by name. If the template doesn't exist, return a default template.
    
    Args:
        template_name: Name of the template in format "category/complexity"
        
    Returns:
        Template data dictionary
    """
    global _template_registry
    
    # Load templates if registry is empty
    if not _template_registry:
        load_templates()
    
    # Return template if it exists
    if template_name in _template_registry:
        return _template_registry[template_name]
    
    # Parse category and complexity from template name
    parts = template_name.split('/')
    if len(parts) != 2:
        logger.warning(f"Invalid template name format: {template_name}, using general/standard")
        category = "general"
        complexity = "standard"
    else:
        category, complexity = parts
    
    # Validate category
    if category not in TASK_CATEGORIES:
        logger.warning(f"Unknown category: {category}, using general")
        category = "general"
    
    # Validate complexity
    if complexity not in COMPLEXITY_LEVELS:
        logger.warning(f"Unknown complexity: {complexity}, using standard")
        complexity = "standard"
    
    # Create default template
    template_path = os.path.join(TEMPLATES_DIR, category, f"{complexity}.json")
    template = create_default_template(category, complexity, template_path)
    _template_registry[template_name] = template
    
    return template

def save_template(template_name: str, template_data: Dict[str, Any]):
    """
    Save a template to the registry and disk.
    
    Args:
        template_name: Name of the template in format "category/complexity"
        template_data: Template data dictionary
    """
    global _template_registry
    
    # Load templates if registry is empty
    if not _template_registry:
        load_templates()
    
    # Parse category and complexity from template name
    parts = template_name.split('/')
    if len(parts) != 2:
        logger.warning(f"Invalid template name format: {template_name}, using general/standard")
        category = "general"
        complexity = "standard"
    else:
        category, complexity = parts
    
    # Validate category
    if category not in TASK_CATEGORIES:
        logger.warning(f"Unknown category: {category}, using general")
        category = "general"
    
    # Validate complexity
    if complexity not in COMPLEXITY_LEVELS:
        logger.warning(f"Unknown complexity: {complexity}, using standard")
        complexity = "standard"
    
    # Update registry
    _template_registry[template_name] = template_data
    
    # Save to disk
    template_dir = os.path.join(TEMPLATES_DIR, category)
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, f"{complexity}.json")
    with open(template_path, 'w') as f:
        json.dump(template_data, f, indent=2)
    
    logger.info(f"Saved template: {template_name}")

def list_templates() -> Dict[str, List[str]]:
    """
    List all available templates grouped by category.
    
    Returns:
        Dictionary mapping categories to lists of available complexity levels
    """
    global _template_registry
    
    # Load templates if registry is empty
    if not _template_registry:
        load_templates()
    
    # Group templates by category
    templates_by_category = {}
    for template_name in _template_registry:
        parts = template_name.split('/')
        if len(parts) == 2:
            category, complexity = parts
            if category not in templates_by_category:
                templates_by_category[category] = []
            templates_by_category[category].append(complexity)
    
    return templates_by_category

# Initialize templates on module import
initialize_templates()
