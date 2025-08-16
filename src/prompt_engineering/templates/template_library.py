"""
Core template library for the Aideon AI Lite Prompt Engineering System.

This module provides a collection of optimized prompt templates for various task types,
complexity levels, and domains.
"""

import os
import json
import datetime
from typing import Dict, List, Optional, Union
from .template_schema import (
    PromptTemplate, PromptSection, TemplateVariable, 
    TaskType, ComplexityLevel, Domain, LLMProvider
)

class TemplateLibrary:
    """
    Manages the collection of prompt templates for the Aideon AI Lite system.
    
    This class handles loading, storing, retrieving, and filtering templates
    based on various criteria.
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the template library.
        
        Args:
            templates_dir: Directory where template files are stored
        """
        self.templates: Dict[str, PromptTemplate] = {}
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "template_data"
        )
        os.makedirs(self.templates_dir, exist_ok=True)
        
    def load_templates(self) -> None:
        """Load all templates from the templates directory."""
        self.templates = {}
        
        # Load system templates first
        system_templates = self._create_system_templates()
        for template in system_templates:
            self.templates[template.id] = template
            
        # Load user templates from files
        if os.path.exists(self.templates_dir):
            for filename in os.listdir(self.templates_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.templates_dir, filename), "r") as f:
                            template_data = json.load(f)
                            template = PromptTemplate(**template_data)
                            self.templates[template.id] = template
                    except Exception as e:
                        print(f"Error loading template {filename}: {e}")
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: Unique identifier for the template
            
        Returns:
            The template if found, None otherwise
        """
        return self.templates.get(template_id)
    
    def find_templates(
        self,
        task_type: Optional[TaskType] = None,
        complexity_level: Optional[ComplexityLevel] = None,
        domain: Optional[Domain] = None,
        provider: Optional[LLMProvider] = None,
        tags: Optional[List[str]] = None,
        is_system: Optional[bool] = None
    ) -> List[PromptTemplate]:
        """
        Find templates matching the specified criteria.
        
        Args:
            task_type: Filter by primary task type
            complexity_level: Filter by complexity level
            domain: Filter by primary domain
            provider: Filter by compatible provider
            tags: Filter by tags (all tags must match)
            is_system: Filter by system/user status
            
        Returns:
            List of matching templates
        """
        results = []
        
        for template in self.templates.values():
            # Apply filters
            if task_type and template.task_type != task_type:
                if not template.secondary_task_types or task_type not in template.secondary_task_types:
                    continue
                    
            if complexity_level and template.complexity_level != complexity_level:
                continue
                
            if domain and template.domain != domain:
                if not template.secondary_domains or domain not in template.secondary_domains:
                    continue
                    
            if provider and provider not in template.compatible_providers and LLMProvider.ANY not in template.compatible_providers:
                continue
                
            if tags:
                if not all(tag in template.tags for tag in tags):
                    continue
                    
            if is_system is not None and template.is_system != is_system:
                continue
                
            results.append(template)
            
        return results
    
    def add_template(self, template: PromptTemplate, save_to_file: bool = True) -> None:
        """
        Add a template to the library.
        
        Args:
            template: The template to add
            save_to_file: Whether to save the template to a file
        """
        self.templates[template.id] = template
        
        if save_to_file and not template.is_system:
            template_path = os.path.join(self.templates_dir, f"{template.id}.json")
            with open(template_path, "w") as f:
                f.write(template.json(indent=2))
    
    def update_template(self, template: PromptTemplate, save_to_file: bool = True) -> None:
        """
        Update an existing template.
        
        Args:
            template: The updated template
            save_to_file: Whether to save the template to a file
        """
        if template.id not in self.templates:
            raise ValueError(f"Template with ID {template.id} not found")
            
        # Update timestamp
        template.updated_at = datetime.datetime.now().isoformat()
        
        self.templates[template.id] = template
        
        if save_to_file and not template.is_system:
            template_path = os.path.join(self.templates_dir, f"{template.id}.json")
            with open(template_path, "w") as f:
                f.write(template.json(indent=2))
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template from the library.
        
        Args:
            template_id: ID of the template to delete
            
        Returns:
            True if the template was deleted, False if not found
        """
        if template_id not in self.templates:
            return False
            
        # Don't allow deleting system templates
        if self.templates[template_id].is_system:
            raise ValueError("Cannot delete system templates")
            
        # Remove from memory
        del self.templates[template_id]
        
        # Remove from file system
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        if os.path.exists(template_path):
            os.remove(template_path)
            
        return True
    
    def _create_system_templates(self) -> List[PromptTemplate]:
        """
        Create the built-in system templates.
        
        Returns:
            List of system templates
        """
        templates = []
        
        # Content Creation - Article Template
        templates.append(PromptTemplate(
            id="system_content_article",
            name="Comprehensive Article Template",
            description="Template for creating detailed, well-structured articles on any topic",
            version="1.0.0",
            task_type=TaskType.CONTENT_CREATION,
            complexity_level=ComplexityLevel.MODERATE,
            domain=Domain.GENERAL,
            compatible_providers=[LLMProvider.ANY],
            variables=[
                TemplateVariable(
                    name="topic",
                    description="The main topic of the article",
                    required=True
                ),
                TemplateVariable(
                    name="target_audience",
                    description="The intended audience for the article",
                    default_value="general readers",
                    required=False
                ),
                TemplateVariable(
                    name="tone",
                    description="The tone of the article",
                    default_value="informative",
                    required=False,
                    options=["informative", "persuasive", "conversational", "formal", "technical"]
                ),
                TemplateVariable(
                    name="word_count",
                    description="Target word count for the article",
                    default_value="1500",
                    required=False
                ),
                TemplateVariable(
                    name="include_examples",
                    description="Whether to include examples",
                    default_value="yes",
                    required=False,
                    options=["yes", "no"]
                ),
                TemplateVariable(
                    name="include_statistics",
                    description="Whether to include statistics",
                    default_value="yes",
                    required=False,
                    options=["yes", "no"]
                ),
                TemplateVariable(
                    name="include_quotes",
                    description="Whether to include quotes",
                    default_value="yes",
                    required=False,
                    options=["yes", "no"]
                )
            ],
            sections=[
                PromptSection(
                    name="instructions",
                    content="Write a comprehensive, well-structured article about {topic}. The article should be approximately {word_count} words and written in a {tone} tone for {target_audience}.",
                    optional=False
                ),
                PromptSection(
                    name="structure",
                    content="Structure the article with:\n- An engaging introduction that hooks the reader\n- A clear thesis statement\n- Logical sections with descriptive headings\n- A compelling conclusion\n- Include a title that captures the essence of the article",
                    optional=False
                ),
                PromptSection(
                    name="content_requirements",
                    content="The article should:\n- Provide comprehensive coverage of the topic\n- Present balanced viewpoints\n- Use clear, concise language\n- Support claims with evidence\n- Avoid jargon unless necessary for the target audience",
                    optional=False
                ),
                PromptSection(
                    name="examples",
                    content="Include relevant examples to illustrate key points.",
                    optional=True
                ),
                PromptSection(
                    name="statistics",
                    content="Incorporate relevant statistics and data to support the article's claims.",
                    optional=True
                ),
                PromptSection(
                    name="quotes",
                    content="Include quotes from relevant experts or sources to add authority to the article.",
                    optional=True
                )
            ],
            example_inputs={
                "topic": "The Impact of Artificial Intelligence on Healthcare",
                "target_audience": "healthcare professionals",
                "tone": "informative",
                "word_count": "2000",
                "include_examples": "yes",
                "include_statistics": "yes",
                "include_quotes": "yes",
                "_include_sections": ["examples", "statistics", "quotes"]
            },
            example_output="# The Transformative Impact of Artificial Intelligence on Modern Healthcare\n\n## Introduction\n\nThe healthcare industry stands at the precipice of a technological revolution...",
            tags=["article", "content", "writing"],
            author="Aideon System",
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            token_estimate=150,
            success_rate=0.95,
            is_system=True
        ))
        
        # Research - Literature Review Template
        templates.append(PromptTemplate(
            id="system_research_literature",
            name="Literature Review Template",
            description="Template for conducting a comprehensive literature review on any topic",
            version="1.0.0",
            task_type=TaskType.RESEARCH,
            complexity_level=ComplexityLevel.COMPLEX,
            domain=Domain.GENERAL,
            secondary_domains=[Domain.SCIENTIFIC, Domain.EDUCATIONAL],
            compatible_providers=[LLMProvider.ANY],
            variables=[
                TemplateVariable(
                    name="research_topic",
                    description="The specific topic for the literature review",
                    required=True
                ),
                TemplateVariable(
                    name="time_period",
                    description="The time period to cover in the review",
                    default_value="last 10 years",
                    required=False
                ),
                TemplateVariable(
                    name="focus_areas",
                    description="Specific areas to focus on within the topic",
                    required=False
                ),
                TemplateVariable(
                    name="methodology",
                    description="The methodology to use for the review",
                    default_value="systematic review",
                    required=False,
                    options=["systematic review", "meta-analysis", "narrative review", "scoping review"]
                ),
                TemplateVariable(
                    name="include_gaps",
                    description="Whether to identify research gaps",
                    default_value="yes",
                    required=False,
                    options=["yes", "no"]
                )
            ],
            sections=[
                PromptSection(
                    name="instructions",
                    content="Conduct a comprehensive literature review on {research_topic}, focusing on research from the {time_period}. Use a {methodology} approach.",
                    optional=False
                ),
                PromptSection(
                    name="focus_areas",
                    content="Within this topic, pay particular attention to: {focus_areas}",
                    optional=True
                ),
                PromptSection(
                    name="structure",
                    content="Structure the literature review with:\n- An introduction explaining the importance of the topic\n- A methodology section describing the review approach\n- Thematic sections organizing the findings\n- A synthesis of the current state of knowledge\n- A conclusion summarizing key insights",
                    optional=False
                ),
                PromptSection(
                    name="content_requirements",
                    content="The review should:\n- Identify major theories and concepts\n- Highlight significant studies and findings\n- Note areas of consensus and controversy\n- Evaluate the strength of evidence\n- Use proper academic tone and citation style",
                    optional=False
                ),
                PromptSection(
                    name="gaps",
                    content="Identify gaps in the current research and suggest directions for future studies.",
                    optional=True
                )
            ],
            example_inputs={
                "research_topic": "Machine Learning Applications in Cancer Detection",
                "time_period": "last 5 years",
                "focus_areas": "image recognition for early detection, predictive modeling for treatment outcomes, and integration with existing clinical workflows",
                "methodology": "systematic review",
                "include_gaps": "yes",
                "_include_sections": ["focus_areas", "gaps"]
            },
            example_output="# Literature Review: Machine Learning Applications in Cancer Detection (2018-2023)\n\n## Introduction\n\nEarly detection remains one of the most significant factors in successful cancer treatment outcomes...",
            tags=["research", "literature review", "academic"],
            author="Aideon System",
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            token_estimate=200,
            success_rate=0.92,
            is_system=True
        ))
        
        # Code Generation - Full-Stack Application Template
        templates.append(PromptTemplate(
            id="system_code_fullstack",
            name="Full-Stack Application Template",
            description="Template for generating a complete full-stack application with frontend, backend, and database",
            version="1.0.0",
            task_type=TaskType.CODE_GENERATION,
            complexity_level=ComplexityLevel.COMPLEX,
            domain=Domain.TECHNICAL,
            compatible_providers=[LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GOOGLE],
            variables=[
                TemplateVariable(
                    name="app_name",
                    description="Name of the application",
                    required=True
                ),
                TemplateVariable(
                    name="app_description",
                    description="Brief description of the application's purpose",
                    required=True
                ),
                TemplateVariable(
                    name="frontend_framework",
                    description="Frontend framework to use",
                    default_value="React",
                    required=False,
                    options=["React", "Vue", "Angular", "Svelte"]
                ),
                TemplateVariable(
                    name="backend_framework",
                    description="Backend framework to use",
                    default_value="Node.js/Express",
                    required=False,
                    options=["Node.js/Express", "Django", "Flask", "Spring Boot", "Ruby on Rails"]
                ),
                TemplateVariable(
                    name="database",
                    description="Database to use",
                    default_value="MongoDB",
                    required=False,
                    options=["MongoDB", "PostgreSQL", "MySQL", "SQLite", "Firebase"]
                ),
                TemplateVariable(
                    name="features",
                    description="Key features to implement",
                    required=True
                ),
                TemplateVariable(
                    name="authentication",
                    description="Authentication method",
                    default_value="JWT",
                    required=False,
                    options=["JWT", "OAuth", "Session-based", "None"]
                )
            ],
            sections=[
                PromptSection(
                    name="instructions",
                    content="Create a complete full-stack application named '{app_name}' that {app_description}. Use {frontend_framework} for the frontend, {backend_framework} for the backend, and {database} for data storage. Implement {authentication} authentication.",
                    optional=False
                ),
                PromptSection(
                    name="features",
                    content="The application should include the following features:\n{features}",
                    optional=False
                ),
                PromptSection(
                    name="structure",
                    content="Provide the complete application structure including:\n- Project organization and file structure\n- Frontend components and pages\n- Backend API routes and controllers\n- Database schema and models\n- Authentication implementation\n- Key utility functions",
                    optional=False
                ),
                PromptSection(
                    name="code_requirements",
                    content="The code should:\n- Follow best practices for each technology\n- Include proper error handling\n- Implement security measures\n- Be well-commented\n- Use modern syntax and patterns\n- Be production-ready",
                    optional=False
                ),
                PromptSection(
                    name="deployment",
                    content="Include instructions for:\n- Setting up the development environment\n- Installing dependencies\n- Running the application locally\n- Deploying to production",
                    optional=False
                )
            ],
            example_inputs={
                "app_name": "TaskMaster",
                "app_description": "helps teams manage projects and tasks with real-time collaboration",
                "frontend_framework": "React",
                "backend_framework": "Node.js/Express",
                "database": "MongoDB",
                "features": "- User registration and profile management\n- Project creation and team assignment\n- Task creation, assignment, and status tracking\n- Real-time notifications\n- Dashboard with progress metrics\n- File attachment support",
                "authentication": "JWT"
            },
            example_output="# TaskMaster: Team Project Management Application\n\n## Project Overview\n\nTaskMaster is a collaborative project management application built with React, Node.js/Express, and MongoDB...",
            tags=["code", "full-stack", "application"],
            author="Aideon System",
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            token_estimate=300,
            success_rate=0.88,
            is_system=True
        ))
        
        # Data Analysis - Exploratory Data Analysis Template
        templates.append(PromptTemplate(
            id="system_data_eda",
            name="Exploratory Data Analysis Template",
            description="Template for conducting exploratory data analysis on a dataset",
            version="1.0.0",
            task_type=TaskType.DATA_PROCESSING,
            secondary_task_types=[TaskType.ANALYSIS],
            complexity_level=ComplexityLevel.MODERATE,
            domain=Domain.TECHNICAL,
            secondary_domains=[Domain.SCIENTIFIC, Domain.BUSINESS],
            compatible_providers=[LLMProvider.ANY],
            variables=[
                TemplateVariable(
                    name="dataset_description",
                    description="Description of the dataset to analyze",
                    required=True
                ),
                TemplateVariable(
                    name="analysis_goals",
                    description="Specific goals for the analysis",
                    required=True
                ),
                TemplateVariable(
                    name="programming_language",
                    description="Programming language to use",
                    default_value="Python",
                    required=False,
                    options=["Python", "R", "SQL"]
                ),
                TemplateVariable(
                    name="visualization_library",
                    description="Visualization library to use",
                    default_value="matplotlib/seaborn",
                    required=False,
                    options=["matplotlib/seaborn", "plotly", "ggplot2", "tableau"]
                ),
                TemplateVariable(
                    name="include_statistical_tests",
                    description="Whether to include statistical tests",
                    default_value="yes",
                    required=False,
                    options=["yes", "no"]
                )
            ],
            sections=[
                PromptSection(
                    name="instructions",
                    content="Conduct an exploratory data analysis on a dataset with the following description: {dataset_description}. Use {programming_language} with {visualization_library} for visualizations.",
                    optional=False
                ),
                PromptSection(
                    name="analysis_goals",
                    content="The analysis should address the following goals:\n{analysis_goals}",
                    optional=False
                ),
                PromptSection(
                    name="analysis_steps",
                    content="Perform the following analysis steps:\n1. Data loading and initial inspection\n2. Data cleaning and preprocessing\n3. Descriptive statistics\n4. Distribution analysis of key variables\n5. Correlation analysis\n6. Pattern identification\n7. Outlier detection and handling\n8. Feature engineering considerations\n9. Summary of key findings",
                    optional=False
                ),
                PromptSection(
                    name="visualization_requirements",
                    content="Create visualizations to illustrate:\n- Distributions of key variables\n- Relationships between variables\n- Temporal patterns (if applicable)\n- Geographical patterns (if applicable)\n- Comparative analyses\n- Anomalies and outliers",
                    optional=False
                ),
                PromptSection(
                    name="statistical_tests",
                    content="Include appropriate statistical tests to validate observations and hypotheses.",
                    optional=True
                ),
                PromptSection(
                    name="code_requirements",
                    content="Provide complete, well-commented code that:\n- Is modular and reusable\n- Includes error handling\n- Is optimized for performance\n- Follows best practices for the chosen language\n- Is well-documented",
                    optional=False
                )
            ],
            example_inputs={
                "dataset_description": "E-commerce customer behavior dataset with 50,000 records containing customer demographics, browsing history, purchase history, and customer service interactions over a 12-month period",
                "analysis_goals": "1. Identify key factors influencing purchase decisions\n2. Segment customers based on behavior patterns\n3. Analyze seasonal trends in purchasing behavior\n4. Evaluate the relationship between customer service interactions and future purchases",
                "programming_language": "Python",
                "visualization_library": "matplotlib/seaborn",
                "include_statistical_tests": "yes",
                "_include_sections": ["statistical_tests"]
            },
            example_output="# Exploratory Data Analysis: E-commerce Customer Behavior\n\n## 1. Data Loading and Initial Inspection\n\n```python\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\n# Load the dataset\ndf = pd.read_csv('ecommerce_data.csv')\n\n# Display basic information\nprint(df.info())\ndf.head()\n```\n\n...",
            tags=["data analysis", "EDA", "visualization"],
            author="Aideon System",
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            token_estimate=250,
            success_rate=0.94,
            is_system=True
        ))
        
        # Problem Solving - Business Strategy Template
        templates.append(PromptTemplate(
            id="system_problem_business_strategy",
            name="Business Strategy Development Template",
            description="Template for developing comprehensive business strategies",
            version="1.0.0",
            task_type=TaskType.PROBLEM_SOLVING,
            secondary_task_types=[TaskType.PLANNING, TaskType.ANALYSIS],
            complexity_level=ComplexityLevel.COMPLEX,
            domain=Domain.BUSINESS,
            compatible_providers=[LLMProvider.ANY],
            variables=[
                TemplateVariable(
                    name="business_name",
                    description="Name of the business",
                    required=True
                ),
                TemplateVariable(
                    name="industry",
                    description="Industry the business operates in",
                    required=True
                ),
                TemplateVariable(
                    name="current_situation",
                    description="Brief description of the current business situation",
                    required=True
                ),
                TemplateVariable(
                    name="strategic_objectives",
                    description="Key strategic objectives to achieve",
                    required=True
                ),
                TemplateVariable(
                    name="timeframe",
                    description="Timeframe for the strategy",
                    default_value="3 years",
                    required=False
                ),
                TemplateVariable(
                    name="include_financial_projections",
                    description="Whether to include financial projections",
                    default_value="yes",
                    required=False,
                    options=["yes", "no"]
                ),
                TemplateVariable(
                    name="include_risk_assessment",
                    description="Whether to include risk assessment",
                    default_value="yes",
                    required=False,
                    options=["yes", "no"]
                )
            ],
            sections=[
                PromptSection(
                    name="instructions",
                    content="Develop a comprehensive {timeframe} business strategy for {business_name}, a company in the {industry} industry. The company is currently in the following situation: {current_situation}",
                    optional=False
                ),
                PromptSection(
                    name="objectives",
                    content="The strategy should address the following strategic objectives:\n{strategic_objectives}",
                    optional=False
                ),
                PromptSection(
                    name="strategy_components",
                    content="Include the following components in the strategy:\n1. Executive Summary\n2. Market Analysis\n   - Industry trends\n   - Competitive landscape\n   - Target market segments\n3. SWOT Analysis\n4. Value Proposition\n5. Strategic Initiatives\n   - Key initiatives\n   - Resource requirements\n   - Timeline\n6. Implementation Roadmap\n7. Success Metrics and KPIs",
                    optional=False
                ),
                PromptSection(
                    name="financial_projections",
                    content="Include financial projections covering:\n- Revenue forecasts\n- Cost structure analysis\n- Profitability projections\n- Investment requirements\n- ROI analysis",
                    optional=True
                ),
                PromptSection(
                    name="risk_assessment",
                    content="Include a comprehensive risk assessment covering:\n- Strategic risks\n- Operational risks\n- Financial risks\n- External risks\n- Mitigation strategies",
                    optional=True
                ),
                PromptSection(
                    name="format_requirements",
                    content="The strategy should be:\n- Well-structured with clear sections\n- Supported by data and analysis\n- Actionable with specific recommendations\n- Realistic and achievable\n- Aligned with industry best practices",
                    optional=False
                )
            ],
            example_inputs={
                "business_name": "GreenTech Solutions",
                "industry": "renewable energy",
                "current_situation": "A mid-sized company with $50M annual revenue, facing increased competition and changing regulations, but with proprietary technology that improves solar panel efficiency by 20%",
                "strategic_objectives": "1. Double market share in the commercial sector within 3 years\n2. Expand into three new international markets\n3. Develop two new product lines leveraging the proprietary technology\n4. Achieve 30% improvement in operational efficiency",
                "timeframe": "3 years",
                "include_financial_projections": "yes",
                "include_risk_assessment": "yes",
                "_include_sections": ["financial_projections", "risk_assessment"]
            },
            example_output="# GreenTech Solutions: 3-Year Strategic Plan (2025-2028)\n\n## Executive Summary\n\nGreenTech Solutions stands at a pivotal moment in its growth trajectory...",
            tags=["business", "strategy", "planning"],
            author="Aideon System",
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            token_estimate=280,
            success_rate=0.91,
            is_system=True
        ))
        
        # Add more system templates here...
        
        return templates
