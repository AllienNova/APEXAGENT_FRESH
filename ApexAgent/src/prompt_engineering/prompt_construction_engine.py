"""
Dynamic prompt construction engine for the Aideon AI Lite Prompt Engineering System.

This module provides functionality for intelligently selecting and modifying
prompt templates based on user intent, context, and history.
"""

import re
import json
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime

from .templates.template_schema import (
    PromptTemplate, TaskType, ComplexityLevel, Domain, LLMProvider,
    IntelligenceLevel, Verbosity, Creativity, FormatPreference, Priority
)
from .templates.template_library import TemplateLibrary


class PromptConstructionEngine:
    """
    Engine for dynamically constructing optimized prompts based on templates.
    
    This class handles template selection, modification, and optimization
    based on user intent, context, and LLM characteristics.
    """
    
    def __init__(self, template_library: TemplateLibrary):
        """
        Initialize the prompt construction engine.
        
        Args:
            template_library: Library of prompt templates
        """
        self.template_library = template_library
        
    def analyze_user_input(self, user_input: str) -> Dict[str, any]:
        """
        Analyze user input to determine intent and requirements.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Dictionary containing analyzed properties
        """
        # This is a simplified implementation - in production, this would use
        # more sophisticated NLP techniques or even a dedicated LLM call
        
        analysis = {
            "task_type": None,
            "complexity_level": None,
            "domain": None,
            "keywords": [],
            "variables": {}
        }
        
        # Detect task type
        task_type_patterns = {
            TaskType.CONTENT_CREATION: r"(?:write|create|draft|compose|generate)\s+(?:a|an)\s+(?:article|blog|post|essay|report|content)",
            TaskType.RESEARCH: r"(?:research|investigate|explore|analyze|study|review)\s+(?:about|on|regarding)",
            TaskType.DATA_PROCESSING: r"(?:analyze|process|clean|transform|visualize)\s+(?:data|dataset|information)",
            TaskType.PROBLEM_SOLVING: r"(?:solve|fix|address|resolve|troubleshoot)\s+(?:problem|issue|challenge|error)",
            TaskType.CREATIVE: r"(?:imagine|brainstorm|ideate|create|invent)\s+(?:creative|novel|innovative|original)",
            TaskType.CODE_GENERATION: r"(?:code|program|develop|implement|script|write code)\s+(?:for|to|that)",
            TaskType.ANALYSIS: r"(?:analyze|examine|assess|evaluate|review)\s+(?:the|this|a|an)",
            TaskType.SUMMARIZATION: r"(?:summarize|condense|digest|brief|synopsis)\s+(?:the|this|a|an)",
            TaskType.TRANSLATION: r"(?:translate|convert|change)\s+(?:from|to|into)\s+(?:language|english|spanish|french)",
            TaskType.CONVERSATION: r"(?:chat|talk|converse|discuss|dialogue)\s+(?:about|on|regarding)",
            TaskType.PLANNING: r"(?:plan|schedule|organize|arrange|strategize)\s+(?:for|a|an|the)",
            TaskType.DECISION_MAKING: r"(?:decide|choose|select|determine|pick)\s+(?:between|among|which|what)"
        }
        
        for task_type, pattern in task_type_patterns.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                analysis["task_type"] = task_type
                break
                
        # Detect complexity level
        if re.search(r"(?:simple|basic|easy|quick|brief)", user_input, re.IGNORECASE):
            analysis["complexity_level"] = ComplexityLevel.SIMPLE
        elif re.search(r"(?:complex|comprehensive|detailed|thorough|in-depth|extensive)", user_input, re.IGNORECASE):
            analysis["complexity_level"] = ComplexityLevel.COMPLEX
        else:
            analysis["complexity_level"] = ComplexityLevel.MODERATE
            
        # Detect domain
        domain_patterns = {
            Domain.LEGAL: r"(?:legal|law|attorney|lawyer|court|judicial|contract)",
            Domain.MEDICAL: r"(?:medical|health|doctor|patient|clinical|disease|treatment|diagnosis)",
            Domain.TECHNICAL: r"(?:technical|technology|software|hardware|engineering|code|programming)",
            Domain.FINANCIAL: r"(?:financial|finance|money|investment|banking|stock|market|economic)",
            Domain.EDUCATIONAL: r"(?:education|learning|teaching|student|school|academic|course|lesson)",
            Domain.SCIENTIFIC: r"(?:scientific|science|research|experiment|laboratory|hypothesis)",
            Domain.MARKETING: r"(?:marketing|advertisement|promotion|brand|campaign|customer)",
            Domain.CREATIVE: r"(?:creative|artistic|design|art|music|writing|novel|story)",
            Domain.BUSINESS: r"(?:business|company|corporate|management|strategy|organization)"
        }
        
        for domain, pattern in domain_patterns.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                analysis["domain"] = domain
                break
                
        if not analysis["domain"]:
            analysis["domain"] = Domain.GENERAL
            
        # Extract keywords
        # This is a simplified implementation - in production, use more sophisticated NLP
        words = re.findall(r'\b\w+\b', user_input.lower())
        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "about", "is", "are", "was", "were"}
        analysis["keywords"] = [word for word in words if word not in stopwords and len(word) > 3]
        
        # Extract potential variables
        # This is a simplified implementation - in production, use more sophisticated NLP
        if analysis["task_type"] == TaskType.CONTENT_CREATION:
            topic_match = re.search(r"(?:about|on|regarding|for)\s+([^,.]+)", user_input, re.IGNORECASE)
            if topic_match:
                analysis["variables"]["topic"] = topic_match.group(1).strip()
                
            word_count_match = re.search(r"(\d+)\s+(?:words|word count)", user_input, re.IGNORECASE)
            if word_count_match:
                analysis["variables"]["word_count"] = word_count_match.group(1)
                
        elif analysis["task_type"] == TaskType.CODE_GENERATION:
            language_match = re.search(r"(?:in|using|with)\s+(python|javascript|java|c\+\+|ruby|go|rust|php)", user_input, re.IGNORECASE)
            if language_match:
                analysis["variables"]["programming_language"] = language_match.group(1).capitalize()
                
        return analysis
    
    def select_template(
        self,
        user_input: str,
        user_context: Optional[Dict[str, any]] = None,
        llm_provider: Optional[LLMProvider] = None
    ) -> Tuple[PromptTemplate, Dict[str, any]]:
        """
        Select the most appropriate template based on user input and context.
        
        Args:
            user_input: The user's input text
            user_context: Additional context about the user and their history
            llm_provider: The LLM provider to be used
            
        Returns:
            Tuple of (selected template, extracted variables)
        """
        # Analyze user input
        analysis = self.analyze_user_input(user_input)
        
        # Find matching templates
        matching_templates = self.template_library.find_templates(
            task_type=analysis["task_type"],
            complexity_level=analysis["complexity_level"],
            domain=analysis["domain"],
            provider=llm_provider
        )
        
        if not matching_templates:
            # Fall back to more general search
            matching_templates = self.template_library.find_templates(
                task_type=analysis["task_type"],
                provider=llm_provider
            )
            
        if not matching_templates:
            # Fall back to any template for the task type
            matching_templates = self.template_library.find_templates(
                task_type=analysis["task_type"]
            )
            
        if not matching_templates:
            # Fall back to general templates
            matching_templates = self.template_library.find_templates(
                domain=Domain.GENERAL,
                complexity_level=ComplexityLevel.MODERATE
            )
            
        if not matching_templates:
            raise ValueError("No suitable template found")
            
        # Score templates for best match
        scored_templates = []
        for template in matching_templates:
            score = 0
            
            # Exact task type match
            if template.task_type == analysis["task_type"]:
                score += 10
                
            # Secondary task type match
            if template.secondary_task_types and analysis["task_type"] in template.secondary_task_types:
                score += 5
                
            # Complexity level match
            if template.complexity_level == analysis["complexity_level"]:
                score += 5
                
            # Domain match
            if template.domain == analysis["domain"]:
                score += 8
                
            # Secondary domain match
            if template.secondary_domains and analysis["domain"] in template.secondary_domains:
                score += 4
                
            # Provider match
            if llm_provider and (llm_provider in template.compatible_providers or LLMProvider.ANY in template.compatible_providers):
                score += 3
                
            # Keyword match in tags
            for keyword in analysis["keywords"]:
                if any(keyword in tag.lower() for tag in template.tags):
                    score += 2
                    
            # Success rate bonus
            score += template.success_rate * 5
            
            scored_templates.append((template, score))
            
        # Select the highest scoring template
        selected_template = max(scored_templates, key=lambda x: x[1])[0]
        
        # Extract variables from user input for the selected template
        variables = self._extract_variables(user_input, selected_template, analysis["variables"])
        
        # Add context variables if available
        if user_context:
            self._add_context_variables(variables, user_context, selected_template)
            
        return selected_template, variables
    
    def _extract_variables(
        self,
        user_input: str,
        template: PromptTemplate,
        pre_extracted_variables: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Extract variables from user input for the selected template.
        
        Args:
            user_input: The user's input text
            template: The selected template
            pre_extracted_variables: Variables already extracted during analysis
            
        Returns:
            Dictionary of variable names and values
        """
        variables = pre_extracted_variables.copy()
        
        # For each template variable, try to extract a value if not already present
        for var in template.variables:
            if var.name in variables:
                continue
                
            # Try to extract based on variable name and description
            patterns = [
                # Format: "variable_name: value" or "variable name: value"
                rf"{var.name.replace('_', ' ')}:\s*([^,\.]+)",
                # Format: "with variable_name value" or "with variable name value"
                rf"with\s+{var.name.replace('_', ' ')}\s+([^,\.]+)",
                # Format: "variable_name should be value" or "variable name should be value"
                rf"{var.name.replace('_', ' ')}\s+should\s+be\s+([^,\.]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    variables[var.name] = match.group(1).strip()
                    break
                    
            # If still not found and there's a default, use it
            if var.name not in variables and var.default_value is not None:
                variables[var.name] = var.default_value
                
        # Handle special section inclusion variables
        include_sections = []
        for section in template.sections:
            if section.optional:
                section_name = section.name.lower()
                include_pattern = rf"(?:include|with|add)\s+{section_name.replace('_', ' ')}"
                exclude_pattern = rf"(?:exclude|without|no)\s+{section_name.replace('_', ' ')}"
                
                if re.search(include_pattern, user_input, re.IGNORECASE) and not re.search(exclude_pattern, user_input, re.IGNORECASE):
                    include_sections.append(section.name)
                    
        if include_sections:
            variables["_include_sections"] = include_sections
            
        return variables
    
    def _add_context_variables(
        self,
        variables: Dict[str, any],
        user_context: Dict[str, any],
        template: PromptTemplate
    ) -> None:
        """
        Add variables from user context.
        
        Args:
            variables: Current variables dictionary to update
            user_context: User context information
            template: The selected template
        """
        # Map context fields to template variables where appropriate
        context_to_variable_mapping = {
            "project_name": "project",
            "industry": "industry",
            "company_name": "business_name",
            "target_audience": "target_audience",
            "preferred_language": "programming_language",
            "preferred_tone": "tone"
        }
        
        for context_key, var_name in context_to_variable_mapping.items():
            if context_key in user_context and var_name not in variables:
                # Check if this variable exists in the template
                if any(var.name == var_name for var in template.variables):
                    variables[var_name] = user_context[context_key]
    
    def optimize_for_llm(
        self,
        prompt: str,
        llm_provider: LLMProvider,
        token_budget: Optional[int] = None
    ) -> str:
        """
        Optimize a prompt for a specific LLM provider.
        
        Args:
            prompt: The prompt to optimize
            llm_provider: The LLM provider
            token_budget: Maximum token budget (if applicable)
            
        Returns:
            Optimized prompt
        """
        # This is a simplified implementation - in production, this would be more sophisticated
        
        optimized_prompt = prompt
        
        # Provider-specific optimizations
        if llm_provider == LLMProvider.OPENAI:
            # OpenAI responds well to clear, direct instructions
            optimized_prompt = optimized_prompt.replace("Please ", "")
            optimized_prompt = optimized_prompt.replace("I would like ", "")
            optimized_prompt = optimized_prompt.replace("Could you ", "")
            
        elif llm_provider == LLMProvider.ANTHROPIC:
            # Anthropic responds well to conversational, ethical framing
            if not optimized_prompt.startswith("Human:"):
                optimized_prompt = f"Human: {optimized_prompt}\n\nAssistant:"
                
        elif llm_provider == LLMProvider.GOOGLE:
            # Google models respond well to structured, detailed prompts
            pass  # Already well-structured from templates
            
        # Token budget optimizations
        if token_budget:
            # This is a very simplified approach - in production, use a proper tokenizer
            current_tokens = len(optimized_prompt.split())
            
            if current_tokens > token_budget:
                # Simplify instructions if over budget
                lines = optimized_prompt.split('\n')
                reduced_lines = []
                
                for line in lines:
                    # Keep essential instructions, remove elaborations
                    if "should:" in line or ":" not in line:
                        reduced_lines.append(line)
                    elif not any(marker in line.lower() for marker in ["example", "note", "tip", "hint"]):
                        reduced_lines.append(line)
                        
                optimized_prompt = '\n'.join(reduced_lines)
                
        return optimized_prompt
    
    def construct_prompt(
        self,
        user_input: str,
        user_context: Optional[Dict[str, any]] = None,
        llm_provider: Optional[LLMProvider] = None,
        token_budget: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Construct an optimized prompt based on user input and context.
        
        Args:
            user_input: The user's input text
            user_context: Additional context about the user and their history
            llm_provider: The LLM provider to be used
            token_budget: Maximum token budget (if applicable)
            
        Returns:
            Dictionary containing the constructed prompt and metadata
        """
        # Select template and extract variables
        template, variables = self.select_template(user_input, user_context, llm_provider)
        
        # Render the template with variables
        prompt = template.render(variables)
        
        # Optimize for the specific LLM
        if llm_provider:
            prompt = self.optimize_for_llm(prompt, llm_provider, token_budget)
            
        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "template_id": template.id,
            "template_name": template.name,
            "task_type": template.task_type,
            "complexity_level": template.complexity_level,
            "domain": template.domain,
            "variables_used": variables,
            "estimated_tokens": template.token_estimate,
            "construction_timestamp": datetime.now().isoformat()
        }
