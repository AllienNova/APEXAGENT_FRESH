"""
Template schema for the Aideon AI Lite Prompt Engineering System.

This module defines the data structures and validation for prompt templates.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class TaskType(str, Enum):
    """Enumeration of task types for prompt templates."""
    CONTENT_CREATION = "content_creation"
    RESEARCH = "research"
    DATA_PROCESSING = "data_processing"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE = "creative"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CONVERSATION = "conversation"
    PLANNING = "planning"
    DECISION_MAKING = "decision_making"


class ComplexityLevel(str, Enum):
    """Enumeration of complexity levels for prompt templates."""
    SIMPLE = "simple"  # Single-step tasks
    MODERATE = "moderate"  # Multi-step tasks
    COMPLEX = "complex"  # Projects requiring planning and coordination


class Domain(str, Enum):
    """Enumeration of domains for prompt templates."""
    GENERAL = "general"
    LEGAL = "legal"
    MEDICAL = "medical"
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    EDUCATIONAL = "educational"
    SCIENTIFIC = "scientific"
    MARKETING = "marketing"
    CREATIVE = "creative"
    BUSINESS = "business"


class LLMProvider(str, Enum):
    """Enumeration of supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    LLAMA = "llama"
    ANY = "any"  # Template works with any provider


class IntelligenceLevel(str, Enum):
    """Enumeration of intelligence levels for conversation initialization."""
    ADAPTIVE = "adaptive"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Verbosity(str, Enum):
    """Enumeration of verbosity levels for conversation initialization."""
    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"


class Creativity(str, Enum):
    """Enumeration of creativity levels for conversation initialization."""
    PRACTICAL = "practical"
    BALANCED = "balanced"
    CREATIVE = "creative"


class FormatPreference(str, Enum):
    """Enumeration of format preferences for conversation initialization."""
    DEFAULT = "default"
    STRUCTURED = "structured"
    CONVERSATIONAL = "conversational"


class Priority(str, Enum):
    """Enumeration of priority options for conversation initialization."""
    SPEED = "speed"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    BALANCE = "balance"


class TemplateVariable(BaseModel):
    """Model for template variables that can be substituted in prompts."""
    name: str = Field(..., description="Variable name")
    description: str = Field(..., description="Description of the variable")
    default_value: Optional[str] = Field(None, description="Default value if not provided")
    required: bool = Field(True, description="Whether this variable is required")
    options: Optional[List[str]] = Field(None, description="Possible values for this variable")


class PromptSection(BaseModel):
    """Model for a section within a prompt template."""
    name: str = Field(..., description="Section name")
    content: str = Field(..., description="Template content with variable placeholders")
    description: Optional[str] = Field(None, description="Description of this section's purpose")
    optional: bool = Field(False, description="Whether this section is optional")


class PromptTemplate(BaseModel):
    """Model for a complete prompt template."""
    id: str = Field(..., description="Unique identifier for the template")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description of the template's purpose")
    version: str = Field("1.0.0", description="Template version in semver format")
    task_type: TaskType = Field(..., description="Primary task type this template is designed for")
    secondary_task_types: Optional[List[TaskType]] = Field(None, description="Secondary task types")
    complexity_level: ComplexityLevel = Field(..., description="Complexity level of tasks this template is suited for")
    domain: Domain = Field(Domain.GENERAL, description="Primary domain this template is designed for")
    secondary_domains: Optional[List[Domain]] = Field(None, description="Secondary domains")
    compatible_providers: List[LLMProvider] = Field([LLMProvider.ANY], description="LLM providers this template works with")
    variables: List[TemplateVariable] = Field(..., description="Variables that can be substituted in the template")
    sections: List[PromptSection] = Field(..., description="Sections that make up the complete prompt")
    example_inputs: Dict[str, str] = Field({}, description="Example variable values for demonstration")
    example_output: Optional[str] = Field(None, description="Example output when using the example inputs")
    tags: List[str] = Field([], description="Tags for categorization and searching")
    author: Optional[str] = Field(None, description="Template author")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    token_estimate: int = Field(0, description="Estimated token count for this template")
    success_rate: float = Field(0.0, description="Historical success rate (0.0-1.0)")
    average_token_usage: Optional[int] = Field(None, description="Average token usage in practice")
    user_rating: Optional[float] = Field(None, description="Average user rating (0.0-5.0)")
    is_system: bool = Field(False, description="Whether this is a system template or user-created")
    
    @validator('version')
    def validate_semver(cls, v):
        """Validate that version follows semantic versioning format."""
        import re
        if not re.match(r'^(\d+)\.(\d+)\.(\d+)$', v):
            raise ValueError('Version must follow semantic versioning (e.g., 1.0.0)')
        return v
    
    def render(self, variables: Dict[str, str]) -> str:
        """
        Render the template with the provided variables.
        
        Args:
            variables: Dictionary of variable names and values
            
        Returns:
            Rendered prompt string
        """
        # Check for required variables
        for var in self.variables:
            if var.required and var.name not in variables and var.default_value is None:
                raise ValueError(f"Required variable '{var.name}' not provided")
        
        # Combine sections
        result = ""
        for section in self.sections:
            if section.optional and section.name not in variables.get('_include_sections', []):
                continue
                
            section_content = section.content
            
            # Replace variables
            for var_name, var_value in variables.items():
                if var_name.startswith('_'):  # Skip special variables
                    continue
                placeholder = f"{{{var_name}}}"
                section_content = section_content.replace(placeholder, str(var_value))
            
            # Add default values for missing variables
            for var in self.variables:
                placeholder = f"{{{var.name}}}"
                if placeholder in section_content and var.default_value is not None:
                    section_content = section_content.replace(placeholder, var.default_value)
            
            result += section_content + "\n\n"
        
        return result.strip()


class ConversationStarter(BaseModel):
    """Model for standardized conversation starters."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of this conversation starter")
    template: str = Field(..., description="Template with placeholders")
    intelligence_level: IntelligenceLevel = Field(IntelligenceLevel.ADAPTIVE, description="Default intelligence level")
    verbosity: Verbosity = Field(Verbosity.BALANCED, description="Default verbosity level")
    creativity: Creativity = Field(Creativity.BALANCED, description="Default creativity level")
    format_preference: FormatPreference = Field(FormatPreference.DEFAULT, description="Default format preference")
    domain_expertise: Domain = Field(Domain.GENERAL, description="Default domain expertise")
    variables: List[TemplateVariable] = Field([], description="Additional variables beyond the standard ones")
    is_system: bool = Field(False, description="Whether this is a system template or user-created")
    
    def render(self, variables: Dict[str, str]) -> str:
        """
        Render the conversation starter with the provided variables.
        
        Args:
            variables: Dictionary of variable names and values
            
        Returns:
            Rendered conversation starter string
        """
        result = self.template
        
        # Replace standard variables
        standard_vars = {
            "intelligence_level": variables.get("intelligence_level", self.intelligence_level),
            "verbosity": variables.get("verbosity", self.verbosity),
            "creativity": variables.get("creativity", self.creativity),
            "format_preference": variables.get("format_preference", self.format_preference),
            "domain_expertise": variables.get("domain_expertise", self.domain_expertise),
            "project": variables.get("project", "New project"),
            "previous_context": variables.get("previous_context", "None"),
            "priority": variables.get("priority", Priority.BALANCE),
        }
        
        for var_name, var_value in standard_vars.items():
            placeholder = f"[{var_name.upper()}]"
            result = result.replace(placeholder, str(var_value))
        
        # Replace custom variables
        for var in self.variables:
            placeholder = f"[{var.name.upper()}]"
            if var.name in variables:
                result = result.replace(placeholder, str(variables[var.name]))
            elif var.default_value is not None:
                result = result.replace(placeholder, var.default_value)
        
        return result
