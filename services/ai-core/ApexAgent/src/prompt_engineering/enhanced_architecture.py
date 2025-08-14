"""
Enhanced modular prompt architecture for the Aideon AI Lite platform.
This module provides a flexible framework for creating and managing structured prompts
with XML-tagged sections for different functional components.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import re

@dataclass
class ModularPrompt:
    """
    Enhanced modular prompt architecture with XML-tagged sections
    for different functional areas.
    """
    system_identity: str = ""
    operational_parameters: Dict[str, Union[str, int, float]] = field(default_factory=dict)
    task_context: Dict[str, str] = field(default_factory=dict)
    execution_rules: List[str] = field(default_factory=list)
    error_handling: List[str] = field(default_factory=list)
    
    def to_prompt_string(self) -> str:
        """
        Convert the modular prompt to a formatted string with XML tags.
        """
        sections = []
        
        if self.system_identity:
            sections.append(f"<system_identity>\n{self.system_identity}\n</system_identity>")
        
        if self.operational_parameters:
            params_str = "\n".join([f"- {k}: {v}" for k, v in self.operational_parameters.items()])
            sections.append(f"<operational_parameters>\n{params_str}\n</operational_parameters>")
        
        if self.task_context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in self.task_context.items()])
            sections.append(f"<task_context>\n{context_str}\n</task_context>")
        
        if self.execution_rules:
            rules_str = "\n".join([f"- {rule}" for rule in self.execution_rules])
            sections.append(f"<execution_rules>\n{rules_str}\n</execution_rules>")
        
        if self.error_handling:
            error_str = "\n".join([f"- {rule}" for rule in self.error_handling])
            sections.append(f"<error_handling>\n{error_str}\n</error_handling>")
        
        return "\n\n".join(sections)
    
    @classmethod
    def from_template(cls, template_data: Dict[str, any]) -> "ModularPrompt":
        """
        Create a ModularPrompt instance from a template dictionary.
        
        Args:
            template_data: Dictionary containing template data
            
        Returns:
            ModularPrompt instance
        """
        return cls(
            system_identity=template_data.get("system_identity", ""),
            operational_parameters=template_data.get("operational_parameters", {}),
            task_context=template_data.get("task_context", {}),
            execution_rules=template_data.get("execution_rules", []),
            error_handling=template_data.get("error_handling", [])
        )
    
    @classmethod
    def from_prompt_string(cls, prompt_string: str) -> "ModularPrompt":
        """
        Parse a prompt string with XML tags into a ModularPrompt instance.
        
        Args:
            prompt_string: Formatted prompt string with XML tags
            
        Returns:
            ModularPrompt instance
        """
        # Initialize empty prompt
        prompt = cls()
        
        # Extract system identity
        system_identity_match = re.search(r'<system_identity>(.*?)</system_identity>', 
                                         prompt_string, re.DOTALL)
        if system_identity_match:
            prompt.system_identity = system_identity_match.group(1).strip()
        
        # Extract operational parameters
        params_match = re.search(r'<operational_parameters>(.*?)</operational_parameters>', 
                               prompt_string, re.DOTALL)
        if params_match:
            params_text = params_match.group(1).strip()
            for line in params_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    parts = line[1:].strip().split(':', 1)
                    if len(parts) == 2:
                        key, value = parts[0].strip(), parts[1].strip()
                        # Try to convert value to appropriate type
                        try:
                            if value.isdigit():
                                value = int(value)
                            elif value.replace('.', '', 1).isdigit():
                                value = float(value)
                        except:
                            pass
                        prompt.operational_parameters[key] = value
        
        # Extract task context
        context_match = re.search(r'<task_context>(.*?)</task_context>', 
                                prompt_string, re.DOTALL)
        if context_match:
            context_text = context_match.group(1).strip()
            for line in context_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    parts = line[1:].strip().split(':', 1)
                    if len(parts) == 2:
                        key, value = parts[0].strip(), parts[1].strip()
                        prompt.task_context[key] = value
        
        # Extract execution rules
        rules_match = re.search(r'<execution_rules>(.*?)</execution_rules>', 
                              prompt_string, re.DOTALL)
        if rules_match:
            rules_text = rules_match.group(1).strip()
            for line in rules_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    rule = line[1:].strip()
                    prompt.execution_rules.append(rule)
        
        # Extract error handling
        error_match = re.search(r'<error_handling>(.*?)</error_handling>', 
                              prompt_string, re.DOTALL)
        if error_match:
            error_text = error_match.group(1).strip()
            for line in error_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    rule = line[1:].strip()
                    prompt.error_handling.append(rule)
        
        return prompt
    
    def optimize_tokens(self) -> "ModularPrompt":
        """
        Create an optimized version of the prompt with reduced token usage.
        
        Returns:
            Optimized ModularPrompt instance
        """
        optimized = ModularPrompt()
        
        # Optimize system identity (keep but compress)
        if self.system_identity:
            # Remove redundant phrases
            identity = self.system_identity
            identity = re.sub(r'\b(you are|you should|please)\b', '', identity, flags=re.IGNORECASE)
            identity = re.sub(r'\s+', ' ', identity).strip()
            optimized.system_identity = identity
        
        # Keep only essential operational parameters
        essential_params = ["intelligence_level", "verbosity", "creativity", "format_preference"]
        for param in essential_params:
            if param in self.operational_parameters:
                optimized.operational_parameters[param] = self.operational_parameters[param]
        
        # Keep only essential task context
        essential_context = ["project", "previous_context", "priority"]
        for ctx in essential_context:
            if ctx in self.task_context:
                optimized.task_context[ctx] = self.task_context[ctx]
        
        # Keep only the most important execution rules (up to 3)
        optimized.execution_rules = self.execution_rules[:3] if self.execution_rules else []
        
        # Keep only the most important error handling strategies (up to 2)
        optimized.error_handling = self.error_handling[:2] if self.error_handling else []
        
        return optimized
    
    def merge(self, other: "ModularPrompt") -> "ModularPrompt":
        """
        Merge another ModularPrompt into this one, with the other taking precedence
        for any overlapping fields.
        
        Args:
            other: Another ModularPrompt to merge with
            
        Returns:
            New merged ModularPrompt instance
        """
        merged = ModularPrompt()
        
        # Merge system identity (concatenate if both exist)
        if self.system_identity and other.system_identity:
            merged.system_identity = f"{self.system_identity}\n{other.system_identity}"
        else:
            merged.system_identity = other.system_identity or self.system_identity
        
        # Merge operational parameters (other takes precedence)
        merged.operational_parameters = {**self.operational_parameters, **other.operational_parameters}
        
        # Merge task context (other takes precedence)
        merged.task_context = {**self.task_context, **other.task_context}
        
        # Merge execution rules (combine and deduplicate)
        merged.execution_rules = list(set(self.execution_rules + other.execution_rules))
        
        # Merge error handling (combine and deduplicate)
        merged.error_handling = list(set(self.error_handling + other.error_handling))
        
        return merged
