# Advanced Dynamic Prompt Construction Design

## Overview

This document outlines the design for advanced dynamic prompt construction for the Aideon AI Lite platform. Building upon the enhanced modular prompt architecture and expanded template library, this component provides sophisticated task analysis, context-aware template selection, and multi-template composition capabilities.

## Design Goals

1. **Enhanced Task Analysis** - Improve task classification and parameter extraction
2. **Context-Aware Selection** - Select templates based on comprehensive context analysis
3. **Multi-Template Composition** - Combine multiple templates for complex tasks
4. **Adaptive Optimization** - Dynamically optimize prompts based on task requirements
5. **Quality Assessment** - Evaluate and improve prompt quality before execution
6. **Continuous Learning** - Incorporate feedback to improve future prompt construction

## Core Architecture

### Advanced Prompt Constructor

The `AdvancedPromptConstructor` class serves as the central component for dynamic prompt construction:

```python
class AdvancedPromptConstructor:
    """
    Advanced dynamic prompt construction engine that builds optimized prompts
    based on comprehensive task analysis and context awareness.
    """
    
    def __init__(self, template_registry: TemplateRegistry, analytics: PromptAnalytics = None):
        """Initialize the prompt constructor with dependencies"""
        self.template_registry = template_registry
        self.analytics = analytics
        self.task_analyzer = TaskAnalyzer()
        self.context_analyzer = ContextAnalyzer()
        self.template_selector = TemplateSelector(template_registry)
        self.template_composer = TemplateComposer()
        self.prompt_optimizer = PromptOptimizer()
        self.quality_assessor = QualityAssessor()
    
    def construct_prompt(self, 
                         task_description: str, 
                         user_context: Dict[str, Any] = None,
                         user_preferences: Dict[str, Any] = None,
                         optimization_level: str = "standard") -> ConstructionResult:
        """
        Construct an optimized prompt based on task description and context.
        
        Args:
            task_description: Description of the task to be performed
            user_context: User's context information
            user_preferences: User's preferences for prompt parameters
            optimization_level: Level of token optimization to apply
            
        Returns:
            ConstructionResult with prompt and metadata
        """
        # Default values
        user_context = user_context or {}
        user_preferences = user_preferences or {}
        
        # Start timing
        start_time = time.time()
        
        try:
            # 1. Analyze task
            task_analysis = self.task_analyzer.analyze(task_description)
            
            # 2. Analyze context
            context_analysis = self.context_analyzer.analyze(user_context, task_analysis)
            
            # 3. Select appropriate templates
            selected_templates = self.template_selector.select(
                task_analysis, context_analysis, user_preferences)
            
            # 4. Compose templates
            composed_template = self.template_composer.compose(selected_templates)
            
            # 5. Apply context and user preferences
            contextualized_template = self._apply_context(
                composed_template, task_analysis, context_analysis, user_preferences)
            
            # 6. Optimize prompt
            optimized_template = self.prompt_optimizer.optimize(
                contextualized_template, optimization_level)
            
            # 7. Assess quality
            quality_score, quality_feedback = self.quality_assessor.assess(optimized_template)
            
            # 8. Generate final prompt string
            prompt_string = optimized_template.to_prompt_string()
            
            # Calculate token count (rough estimate)
            token_count = len(prompt_string) // 4
            
            # Record analytics if available
            if self.analytics:
                self._record_analytics(
                    task_analysis, selected_templates, quality_score, token_count)
            
            # Calculate construction time
            construction_time = time.time() - start_time
            
            # Return result
            return ConstructionResult(
                prompt=prompt_string,
                template=optimized_template,
                task_analysis=task_analysis,
                selected_templates=[t.template_id for t in selected_templates],
                quality_score=quality_score,
                quality_feedback=quality_feedback,
                token_count=token_count,
                construction_time=construction_time
            )
            
        except Exception as e:
            # Log error
            logging.error(f"Error constructing prompt: {str(e)}")
            
            # Return error result
            return ConstructionResult(
                error=str(e),
                construction_time=time.time() - start_time
            )
    
    def _apply_context(self, 
                      template: EnhancedModularPrompt,
                      task_analysis: TaskAnalysis,
                      context_analysis: ContextAnalysis,
                      user_preferences: Dict[str, Any]) -> EnhancedModularPrompt:
        """Apply context and user preferences to template"""
        # Create context dictionary
        context = {
            # Task parameters
            "task_type": task_analysis.task_type,
            "task_category": task_analysis.task_category,
            "task_complexity": task_analysis.complexity,
            "task_domain": task_analysis.domain,
            "task_parameters": task_analysis.parameters,
            
            # Context parameters
            "project": context_analysis.project,
            "previous_context": context_analysis.previous_context,
            "priority": context_analysis.priority,
            
            # User preferences
            "intelligence_level": user_preferences.get("intelligence_level", "Adaptive"),
            "verbosity": user_preferences.get("verbosity", "Balanced"),
            "creativity": user_preferences.get("creativity", "Balanced"),
            "format_preference": user_preferences.get("format_preference", "Default"),
            "domain_expertise": user_preferences.get("domain_expertise", "General"),
        }
        
        # Add custom context parameters
        for key, value in context_analysis.custom_context.items():
            context[key] = value
        
        # Apply conditions based on context
        contextualized_template = template.apply_conditions(context)
        
        # Update template parameters
        if contextualized_template.parameters:
            for param, value in user_preferences.items():
                if hasattr(contextualized_template.parameters, param):
                    setattr(contextualized_template.parameters, param, value)
        
        # Update template context
        if contextualized_template.context:
            contextualized_template.context.project = context_analysis.project
            contextualized_template.context.history = context_analysis.previous_context
            contextualized_template.context.priority = context_analysis.priority
            
            # Update custom context
            for key, value in context_analysis.custom_context.items():
                contextualized_template.context.custom_context[key] = value
        
        return contextualized_template
    
    def _record_analytics(self,
                         task_analysis: TaskAnalysis,
                         selected_templates: List[VersionedTemplate],
                         quality_score: float,
                         token_count: int):
        """Record analytics for prompt construction"""
        if not self.analytics:
            return
        
        # Record template usage
        for template in selected_templates:
            self.analytics.record_template_usage(
                template_id=template.template_id,
                task_category=task_analysis.task_category,
                quality_score=quality_score,
                token_count=token_count
            )
```

### Task Analyzer

The `TaskAnalyzer` class provides sophisticated task analysis capabilities:

```python
class TaskAnalysis:
    """Result of task analysis"""
    def __init__(self):
        self.task_type = ""
        self.task_category = ""
        self.complexity = "standard"
        self.domain = "general"
        self.parameters = {}
        self.entities = []
        self.keywords = []
        self.confidence = 0.0

class TaskAnalyzer:
    """
    Analyzes tasks to determine type, category, complexity, and parameters.
    """
    
    def __init__(self):
        """Initialize the task analyzer"""
        # Initialize category classifiers
        self.category_classifiers = {
            "software_development": self._classify_software_development,
            "data_analysis": self._classify_data_analysis,
            "content_creation": self._classify_content_creation,
            "business_operations": self._classify_business_operations,
            "system_administration": self._classify_system_administration,
            "enterprise_integration": self._classify_enterprise_integration,
            "user_experience": self._classify_user_experience,
            "knowledge_management": self._classify_knowledge_management
        }
        
        # Initialize domain classifiers
        self.domain_classifiers = {
            "healthcare": self._classify_healthcare_domain,
            "finance": self._classify_finance_domain,
            "legal": self._classify_legal_domain,
            "education": self._classify_education_domain,
            "retail": self._classify_retail_domain,
            "manufacturing": self._classify_manufacturing_domain,
            "technology": self._classify_technology_domain
        }
        
        # Initialize complexity indicators
        self.complexity_indicators = {
            "simple": ["simple", "basic", "quick", "brief", "straightforward", "easy"],
            "complex": ["complex", "advanced", "sophisticated", "detailed", "comprehensive", 
                       "thorough", "in-depth", "extensive", "complete"]
        }
        
        # Initialize NLP components
        self.nlp = self._initialize_nlp()
    
    def analyze(self, task_description: str) -> TaskAnalysis:
        """
        Analyze a task description to determine its characteristics.
        
        Args:
            task_description: Description of the task
            
        Returns:
            TaskAnalysis object with analysis results
        """
        # Create analysis result
        analysis = TaskAnalysis()
        
        # Process text with NLP
        doc = self.nlp(task_description)
        
        # Extract entities and keywords
        analysis.entities = self._extract_entities(doc)
        analysis.keywords = self._extract_keywords(doc)
        
        # Determine task category
        category_scores = self._classify_category(task_description, doc)
        analysis.task_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Determine task domain
        domain_scores = self._classify_domain(task_description, doc)
        analysis.domain = max(domain_scores.items(), key=lambda x: x[1])[0]
        
        # Determine task complexity
        analysis.complexity = self._determine_complexity(task_description, doc)
        
        # Extract task parameters
        analysis.parameters = self._extract_parameters(task_description, doc, analysis.task_category)
        
        # Set confidence score
        analysis.confidence = category_scores[analysis.task_category]
        
        return analysis
    
    def _initialize_nlp(self):
        """Initialize NLP components"""
        # In a real implementation, this would use spaCy or another NLP library
        # For this design document, we'll use a placeholder
        class SimpleNLP:
            def __call__(self, text):
                return text
        
        return SimpleNLP()
    
    def _extract_entities(self, doc) -> List[Dict[str, str]]:
        """Extract named entities from document"""
        # Placeholder implementation
        return []
    
    def _extract_keywords(self, doc) -> List[str]:
        """Extract keywords from document"""
        # Placeholder implementation
        return []
    
    def _classify_category(self, task_description: str, doc) -> Dict[str, float]:
        """Classify task into categories with confidence scores"""
        scores = {}
        
        # Calculate score for each category
        for category, classifier in self.category_classifiers.items():
            scores[category] = classifier(task_description, doc)
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            for category in scores:
                scores[category] /= total
        
        return scores
    
    def _classify_domain(self, task_description: str, doc) -> Dict[str, float]:
        """Classify task into domains with confidence scores"""
        scores = {}
        
        # Calculate score for each domain
        for domain, classifier in self.domain_classifiers.items():
            scores[domain] = classifier(task_description, doc)
        
        # Add general domain
        scores["general"] = 0.5  # Default score for general domain
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            for domain in scores:
                scores[domain] /= total
        
        return scores
    
    def _determine_complexity(self, task_description: str, doc) -> str:
        """Determine task complexity"""
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
    
    def _extract_parameters(self, task_description: str, doc, category: str) -> Dict[str, Any]:
        """Extract task-specific parameters"""
        parameters = {}
        
        # Call category-specific parameter extractors
        if category in self.category_classifiers:
            extractor_name = f"_extract_{category}_parameters"
            if hasattr(self, extractor_name):
                extractor = getattr(self, extractor_name)
                category_params = extractor(task_description, doc)
                parameters.update(category_params)
        
        return parameters
    
    # Category classifiers
    def _classify_software_development(self, task_description: str, doc) -> float:
        """Classify software development tasks"""
        keywords = ["code", "program", "develop", "build", "implement", "debug", "function", 
                   "class", "object", "method", "api", "framework", "library", "software",
                   "app", "application", "website", "web app", "mobile app", "script"]
        
        score = sum(1 for keyword in keywords if keyword in task_description.lower())
        return score / len(keywords)
    
    # Additional category classifiers would be implemented similarly
    
    # Domain classifiers
    def _classify_healthcare_domain(self, task_description: str, doc) -> float:
        """Classify healthcare domain tasks"""
        keywords = ["healthcare", "medical", "clinical", "patient", "hospital", "doctor", 
                   "nurse", "treatment", "diagnosis", "health record", "ehr", "hipaa"]
        
        score = sum(1 for keyword in keywords if keyword in task_description.lower())
        return score / len(keywords)
    
    # Additional domain classifiers would be implemented similarly
    
    # Parameter extractors
    def _extract_software_development_parameters(self, task_description: str, doc) -> Dict[str, Any]:
        """Extract parameters for software development tasks"""
        params = {}
        
        # Extract programming language if mentioned
        languages = ["python", "javascript", "typescript", "java", "c#", "c++", "go", 
                    "rust", "ruby", "php", "swift", "kotlin", "scala"]
        for lang in languages:
            pattern = r'\b' + re.escape(lang) + r'\b'
            if re.search(pattern, task_description.lower()):
                params["programming_language"] = lang
                break
        
        # Extract framework if mentioned
        frameworks = ["react", "angular", "vue", "django", "flask", "spring", "express",
                     "next.js", "nuxt", "laravel", "rails", "asp.net", "tensorflow"]
        for framework in frameworks:
            pattern = r'\b' + re.escape(framework) + r'\b'
            if re.search(pattern, task_description.lower()):
                params["framework"] = framework
                break
        
        # Detect task type
        if any(kw in task_description.lower() for kw in ["bug", "fix", "issue", "error", "debug"]):
            params["task_type"] = "debugging"
        elif any(kw in task_description.lower() for kw in ["test", "unit test", "integration test"]):
            params["task_type"] = "testing"
        elif any(kw in task_description.lower() for kw in ["refactor", "improve", "optimize"]):
            params["task_type"] = "refactoring"
        elif any(kw in task_description.lower() for kw in ["new", "create", "implement", "develop"]):
            params["task_type"] = "development"
        
        return params
    
    # Additional parameter extractors would be implemented similarly
```

### Context Analyzer

The `ContextAnalyzer` class analyzes user context to enhance prompt construction:

```python
class ContextAnalysis:
    """Result of context analysis"""
    def __init__(self):
        self.project = ""
        self.previous_context = ""
        self.priority = "Balance"
        self.custom_context = {}
        self.relevant_history = []

class ContextAnalyzer:
    """
    Analyzes user context to enhance prompt construction.
    """
    
    def __init__(self):
        """Initialize the context analyzer"""
        pass
    
    def analyze(self, user_context: Dict[str, Any], task_analysis: TaskAnalysis) -> ContextAnalysis:
        """
        Analyze user context in relation to the task.
        
        Args:
            user_context: User's context information
            task_analysis: Result of task analysis
            
        Returns:
            ContextAnalysis object with analysis results
        """
        # Create analysis result
        analysis = ContextAnalysis()
        
        # Extract basic context
        analysis.project = user_context.get("project", "")
        analysis.previous_context = user_context.get("previous_context", "")
        analysis.priority = user_context.get("priority", "Balance")
        
        # Extract relevant history
        if "history" in user_context:
            analysis.relevant_history = self._extract_relevant_history(
                user_context["history"], task_analysis)
        
        # Extract custom context based on task category
        analysis.custom_context = self._extract_custom_context(user_context, task_analysis)
        
        return analysis
    
    def _extract_relevant_history(self, history: List[Dict[str, Any]], 
                                 task_analysis: TaskAnalysis) -> List[Dict[str, Any]]:
        """Extract history items relevant to the current task"""
        relevant_items = []
        
        # Filter history by relevance
        for item in history:
            relevance_score = self._calculate_relevance(item, task_analysis)
            if relevance_score > 0.5:  # Threshold for relevance
                relevant_items.append({
                    "content": item.get("content", ""),
                    "timestamp": item.get("timestamp", ""),
                    "relevance": relevance_score
                })
        
        # Sort by relevance
        relevant_items.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Limit to most relevant items
        return relevant_items[:5]
    
    def _calculate_relevance(self, history_item: Dict[str, Any], 
                            task_analysis: TaskAnalysis) -> float:
        """Calculate relevance score of history item to current task"""
        # Placeholder implementation
        return 0.5
    
    def _extract_custom_context(self, user_context: Dict[str, Any], 
                               task_analysis: TaskAnalysis) -> Dict[str, Any]:
        """Extract custom context based on task category"""
        custom_context = {}
        
        # Add task-specific context
        if task_analysis.task_category == "software_development":
            custom_context["programming_language"] = user_context.get("programming_language", "")
            custom_context["framework"] = user_context.get("framework", "")
            custom_context["code_style"] = user_context.get("code_style", "")
        
        elif task_analysis.task_category == "data_analysis":
            custom_context["data_source"] = user_context.get("data_source", "")
            custom_context["analysis_type"] = user_context.get("analysis_type", "")
            custom_context["visualization_style"] = user_context.get("visualization_style", "")
        
        # Add domain-specific context
        if task_analysis.domain == "healthcare":
            custom_context["healthcare_domain"] = user_context.get("healthcare_domain", "")
            custom_context["clinical_setting"] = user_context.get("clinical_setting", "")
            custom_context["regulatory_requirements"] = user_context.get("regulatory_requirements", "")
        
        elif task_analysis.domain == "finance":
            custom_context["finance_domain"] = user_context.get("finance_domain", "")
            custom_context["regulatory_framework"] = user_context.get("regulatory_framework", "")
            custom_context["risk_profile"] = user_context.get("risk_profile", "")
        
        # Add any additional context provided by user
        for key, value in user_context.items():
            if key not in ["project", "previous_context", "priority", "history"]:
                if key not in custom_context:
                    custom_context[key] = value
        
        return custom_context
```

### Template Selector

The `TemplateSelector` class selects appropriate templates based on task and context:

```python
class TemplateSelector:
    """
    Selects appropriate templates based on task analysis and context.
    """
    
    def __init__(self, template_registry: TemplateRegistry):
        """Initialize the template selector"""
        self.template_registry = template_registry
    
    def select(self, 
              task_analysis: TaskAnalysis, 
              context_analysis: ContextAnalysis,
              user_preferences: Dict[str, Any]) -> List[VersionedTemplate]:
        """
        Select appropriate templates based on task and context.
        
        Args:
            task_analysis: Result of task analysis
            context_analysis: Result of context analysis
            user_preferences: User's preferences
            
        Returns:
            List of selected templates
        """
        selected_templates = []
        
        # Check if user has a preferred template
        preferred_template_id = user_preferences.get("preferred_template")
        if preferred_template_id:
            template = self.template_registry.get_template(preferred_template_id)
            if template:
                versioned_template = VersionedTemplate(
                    preferred_template_id, 
                    self.template_registry.template_versions.get(preferred_template_id),
                    template
                )
                selected_templates.append(versioned_template)
                return selected_templates
        
        # Select primary template based on task category and complexity
        primary_template_id = f"{task_analysis.task_category}/{task_analysis.complexity}"
        primary_template = self.template_registry.get_template(primary_template_id)
        if primary_template:
            versioned_template = VersionedTemplate(
                primary_template_id, 
                self.template_registry.template_versions.get(primary_template_id),
                primary_template
            )
            selected_templates.append(versioned_template)
        
        # Select domain-specific template if applicable
        if task_analysis.domain != "general":
            domain_template_id = f"domain/{task_analysis.domain}"
            domain_template = self.template_registry.get_template(domain_template_id)
            if domain_template:
                versioned_template = VersionedTemplate(
                    domain_template_id, 
                    self.template_registry.template_versions.get(domain_template_id),
                    domain_template
                )
                selected_templates.append(versioned_template)
        
        # Select additional templates based on task parameters
        additional_templates = self._select_additional_templates(
            task_analysis, context_analysis)
        selected_templates.extend(additional_templates)
        
        return selected_templates
    
    def _select_additional_templates(self, 
                                   task_analysis: TaskAnalysis, 
                                   context_analysis: ContextAnalysis) -> List[VersionedTemplate]:
        """Select additional templates based on task parameters"""
        additional_templates = []
        
        # Select templates based on task type
        if "task_type" in task_analysis.parameters:
            task_type = task_analysis.parameters["task_type"]
            template_id = f"{task_analysis.task_category}/{task_type}"
            template = self.template_registry.get_template(template_id)
            if template:
                versioned_template = VersionedTemplate(
                    template_id, 
                    self.template_registry.template_versions.get(template_id),
                    template
                )
                additional_templates.append(versioned_template)
        
        # Select templates based on specific parameters
        if task_analysis.task_category == "software_development":
            if "programming_language" in task_analysis.parameters:
                lang = task_analysis.parameters["programming_language"]
                template_id = f"language/{lang}"
                template = self.template_registry.get_template(template_id)
                if template:
                    versioned_template = VersionedTemplate(
                        template_id, 
                        self.template_registry.template_versions.get(template_id),
                        template
                    )
                    additional_templates.append(versioned_template)
        
        # Select templates based on context
        if context_analysis.project:
            project_template_id = f"project/{context_analysis.project}"
            template = self.template_registry.get_template(project_template_id)
            if template:
                versioned_template = VersionedTemplate(
                    project_template_id, 
                    self.template_registry.template_versions.get(project_template_id),
                    template
                )
                additional_templates.append(versioned_template)
        
        return additional_templates
```

### Template Composer

The `TemplateComposer` class combines multiple templates into a cohesive prompt:

```python
class TemplateComposer:
    """
    Combines multiple templates into a cohesive prompt.
    """
    
    def __init__(self):
        """Initialize the template composer"""
        pass
    
    def compose(self, templates: List[VersionedTemplate]) -> EnhancedModularPrompt:
        """
        Compose multiple templates into a single template.
        
        Args:
            templates: List of templates to compose
            
        Returns:
            Composed template
        """
        if not templates:
            # Return empty template if no templates provided
            return EnhancedModularPrompt()
        
        # Start with the first template
        composed_template = templates[0].template
        
        # Merge additional templates
        for template_info in templates[1:]:
            composed_template = self._merge_templates(composed_template, template_info.template)
        
        return composed_template
    
    def _merge_templates(self, base: EnhancedModularPrompt, 
                        extension: EnhancedModularPrompt) -> EnhancedModularPrompt:
        """Merge two templates, with extension taking precedence for conflicts"""
        # Create a new template for the result
        merged = EnhancedModularPrompt()
        
        # Merge system section
        if base.system and extension.system:
            merged.system = SystemSection()
            
            # Merge identity
            if extension.system.identity:
                merged.system.identity = extension.system.identity
            else:
                merged.system.identity = base.system.identity
            
            # Merge capabilities
            merged.system.capabilities = list(set(base.system.capabilities + extension.system.capabilities))
            
            # Merge constraints
            merged.system.constraints = list(set(base.system.constraints + extension.system.constraints))
        elif base.system:
            merged.system = copy.deepcopy(base.system)
        elif extension.system:
            merged.system = copy.deepcopy(extension.system)
        
        # Merge parameters section
        if base.parameters and extension.parameters:
            merged.parameters = ParametersSection()
            
            # Merge standard parameters
            for param in ["intelligence_level", "verbosity", "creativity", 
                         "format_preference", "domain_expertise"]:
                if hasattr(extension.parameters, param) and getattr(extension.parameters, param):
                    setattr(merged.parameters, param, getattr(extension.parameters, param))
                elif hasattr(base.parameters, param) and getattr(base.parameters, param):
                    setattr(merged.parameters, param, getattr(base.parameters, param))
            
            # Merge custom parameters
            merged.parameters.custom_parameters = {
                **base.parameters.custom_parameters,
                **extension.parameters.custom_parameters
            }
        elif base.parameters:
            merged.parameters = copy.deepcopy(base.parameters)
        elif extension.parameters:
            merged.parameters = copy.deepcopy(extension.parameters)
        
        # Merge context section
        if base.context and extension.context:
            merged.context = ContextSection()
            
            # Merge standard context
            for ctx in ["project", "history", "priority"]:
                if hasattr(extension.context, ctx) and getattr(extension.context, ctx):
                    setattr(merged.context, ctx, getattr(extension.context, ctx))
                elif hasattr(base.context, ctx) and getattr(base.context, ctx):
                    setattr(merged.context, ctx, getattr(base.context, ctx))
            
            # Merge custom context
            merged.context.custom_context = {
                **base.context.custom_context,
                **extension.context.custom_context
            }
        elif base.context:
            merged.context = copy.deepcopy(base.context)
        elif extension.context:
            merged.context = copy.deepcopy(extension.context)
        
        # Merge execution section
        if base.execution and extension.execution:
            merged.execution = ExecutionSection()
            
            # Merge rules (deduplicate)
            all_rules = base.execution.rules + extension.execution.rules
            unique_rules = []
            rule_contents = set()
            
            for rule in all_rules:
                if isinstance(rule, ConditionalElement):
                    rule_content = rule.content
                else:
                    rule_content = rule
                
                if rule_content not in rule_contents:
                    unique_rules.append(rule)
                    rule_contents.add(rule_content)
            
            merged.execution.rules = unique_rules
            
            # Merge workflow (keep order)
            merged.execution.workflow = base.execution.workflow + extension.execution.workflow
        elif base.execution:
            merged.execution = copy.deepcopy(base.execution)
        elif extension.execution:
            merged.execution = copy.deepcopy(extension.execution)
        
        # Merge error handling section
        if base.error_handling and extension.error_handling:
            merged.error_handling = ErrorHandlingSection()
            
            # Merge strategies
            merged.error_handling.strategies = base.error_handling.strategies + extension.error_handling.strategies
            
            # Merge fallback (extension takes precedence)
            if extension.error_handling.fallback:
                merged.error_handling.fallback = extension.error_handling.fallback
            else:
                merged.error_handling.fallback = base.error_handling.fallback
            
            # Merge recovery (extension takes precedence)
            if extension.error_handling.recovery:
                merged.error_handling.recovery = extension.error_handling.recovery
            else:
                merged.error_handling.recovery = base.error_handling.recovery
        elif base.error_handling:
            merged.error_handling = copy.deepcopy(base.error_handling)
        elif extension.error_handling:
            merged.error_handling = copy.deepcopy(extension.error_handling)
        
        # Merge agent loop section
        if base.agent_loop and extension.agent_loop:
            merged.agent_loop = AgentLoopSection()
            
            # Merge agent loop phases (extension takes precedence)
            for phase in ["analyze", "plan", "execute", "reflect"]:
                if hasattr(extension.agent_loop, phase) and getattr(extension.agent_loop, phase):
                    setattr(merged.agent_loop, phase, getattr(extension.agent_loop, phase))
                elif hasattr(base.agent_loop, phase) and getattr(base.agent_loop, phase):
                    setattr(merged.agent_loop, phase, getattr(base.agent_loop, phase))
        elif base.agent_loop:
            merged.agent_loop = copy.deepcopy(base.agent_loop)
        elif extension.agent_loop:
            merged.agent_loop = copy.deepcopy(extension.agent_loop)
        
        return merged
```

### Prompt Optimizer

The `PromptOptimizer` class optimizes prompts for token efficiency:

```python
class PromptOptimizer:
    """
    Optimizes prompts for token efficiency.
    """
    
    def __init__(self):
        """Initialize the prompt optimizer"""
        self.optimization_strategies = {
            "minimal": self._minimal_optimization,
            "standard": self._standard_optimization,
            "aggressive": self._aggressive_optimization
        }
    
    def optimize(self, template: EnhancedModularPrompt, 
                level: str = "standard") -> EnhancedModularPrompt:
        """
        Optimize a template for token efficiency.
        
        Args:
            template: Template to optimize
            level: Optimization level (minimal, standard, aggressive)
            
        Returns:
            Optimized template
        """
        # Use appropriate optimization strategy
        if level in self.optimization_strategies:
            return self.optimization_strategies[level](template)
        else:
            # Default to standard optimization
            return self._standard_optimization(template)
    
    def _minimal_optimization(self, template: EnhancedModularPrompt) -> EnhancedModularPrompt:
        """Apply minimal token optimization"""
        # Create a copy of the template
        optimized = copy.deepcopy(template)
        
        # Optimize system identity
        if optimized.system and optimized.system.identity:
            # Remove redundant phrases
            identity = optimized.system.identity
            identity = re.sub(r'\b(you are|you should|please)\b', '', identity, flags=re.IGNORECASE)
            identity = re.sub(r'\s+', ' ', identity).strip()
            optimized.system.identity = identity
        
        return optimized
    
    def _standard_optimization(self, template: EnhancedModularPrompt) -> EnhancedModularPrompt:
        """Apply standard token optimization"""
        # Start with minimal optimization
        optimized = self._minimal_optimization(template)
        
        # Optimize system capabilities
        if optimized.system and optimized.system.capabilities:
            # Keep only the most important capabilities (up to 5)
            optimized.system.capabilities = optimized.system.capabilities[:5]
        
        # Optimize system constraints
        if optimized.system and optimized.system.constraints:
            # Keep only the most important constraints (up to 3)
            optimized.system.constraints = optimized.system.constraints[:3]
        
        # Optimize execution rules
        if optimized.execution and optimized.execution.rules:
            # Keep only the most important rules (up to 7)
            optimized.execution.rules = optimized.execution.rules[:7]
        
        # Optimize workflow steps
        if optimized.execution and optimized.execution.workflow:
            # Keep all steps but simplify descriptions
            for i, step in enumerate(optimized.execution.workflow):
                if isinstance(step, ConditionalElement):
                    step.content = self._simplify_text(step.content)
                else:
                    optimized.execution.workflow[i] = self._simplify_text(step)
        
        return optimized
    
    def _aggressive_optimization(self, template: EnhancedModularPrompt) -> EnhancedModularPrompt:
        """Apply aggressive token optimization"""
        # Start with standard optimization
        optimized = self._standard_optimization(template)
        
        # Optimize system capabilities
        if optimized.system and optimized.system.capabilities:
            # Keep only the most important capabilities (up to 3)
            optimized.system.capabilities = optimized.system.capabilities[:3]
        
        # Optimize system constraints
        if optimized.system and optimized.system.constraints:
            # Keep only the most important constraint
            optimized.system.constraints = optimized.system.constraints[:1]
        
        # Optimize execution rules
        if optimized.execution and optimized.execution.rules:
            # Keep only the most important rules (up to 5)
            optimized.execution.rules = optimized.execution.rules[:5]
        
        # Optimize workflow steps
        if optimized.execution and optimized.execution.workflow:
            # Keep only essential steps
            essential_steps = []
            for step in optimized.execution.workflow:
                if isinstance(step, ConditionalElement) and step.condition:
                    # Keep conditional steps with simplified content
                    step.content = self._simplify_text(step.content, aggressive=True)
                    essential_steps.append(step)
                else:
                    # Keep only essential steps with simplified content
                    step_content = step if isinstance(step, str) else step.content
                    if self._is_essential_step(step_content):
                        simplified = self._simplify_text(step_content, aggressive=True)
                        essential_steps.append(simplified)
            
            optimized.execution.workflow = essential_steps
        
        # Optimize error handling
        if optimized.error_handling:
            # Keep only fallback strategy
            optimized.error_handling.strategies = []
            optimized.error_handling.recovery = ""
        
        # Optimize agent loop
        if optimized.agent_loop:
            # Keep only analyze and execute phases
            optimized.agent_loop.plan = ""
            optimized.agent_loop.reflect = ""
        
        return optimized
    
    def _simplify_text(self, text: str, aggressive: bool = False) -> str:
        """Simplify text for token efficiency"""
        # Remove redundant phrases
        simplified = re.sub(r'\b(in order to|for the purpose of|with the goal of)\b', 'to', text, flags=re.IGNORECASE)
        simplified = re.sub(r'\b(take into account|consider)\b', 'consider', simplified, flags=re.IGNORECASE)
        simplified = re.sub(r'\b(make sure|ensure that)\b', 'ensure', simplified, flags=re.IGNORECASE)
        
        # Remove filler words
        filler_words = ['very', 'really', 'quite', 'simply', 'just', 'basically', 'actually']
        for word in filler_words:
            simplified = re.sub(r'\b' + word + r'\b', '', simplified, flags=re.IGNORECASE)
        
        # Aggressive simplification
        if aggressive:
            # Use abbreviations
            abbreviations = {
                'implementation': 'impl',
                'development': 'dev',
                'application': 'app',
                'configuration': 'config',
                'documentation': 'docs',
                'requirements': 'reqs',
                'functionality': 'func',
                'performance': 'perf',
                'optimization': 'opt',
                'management': 'mgmt'
            }
            for word, abbrev in abbreviations.items():
                simplified = re.sub(r'\b' + word + r'\b', abbrev, simplified, flags=re.IGNORECASE)
        
        # Clean up whitespace
        simplified = re.sub(r'\s+', ' ', simplified).strip()
        
        return simplified
    
    def _is_essential_step(self, step: str) -> bool:
        """Determine if a workflow step is essential"""
        # Steps that involve analysis, implementation, or testing are essential
        essential_keywords = ['analyze', 'implement', 'test', 'validate', 'design', 'develop', 'create']
        return any(keyword in step.lower() for keyword in essential_keywords)
```

### Quality Assessor

The `QualityAssessor` class evaluates prompt quality before execution:

```python
class QualityAssessor:
    """
    Evaluates prompt quality before execution.
    """
    
    def __init__(self):
        """Initialize the quality assessor"""
        pass
    
    def assess(self, template: EnhancedModularPrompt) -> Tuple[float, List[str]]:
        """
        Assess the quality of a template.
        
        Args:
            template: Template to assess
            
        Returns:
            Tuple of (quality score, feedback list)
        """
        feedback = []
        scores = {}
        
        # Assess completeness
        completeness_score, completeness_feedback = self._assess_completeness(template)
        scores["completeness"] = completeness_score
        feedback.extend(completeness_feedback)
        
        # Assess clarity
        clarity_score, clarity_feedback = self._assess_clarity(template)
        scores["clarity"] = clarity_score
        feedback.extend(clarity_feedback)
        
        # Assess specificity
        specificity_score, specificity_feedback = self._assess_specificity(template)
        scores["specificity"] = specificity_score
        feedback.extend(specificity_feedback)
        
        # Assess token efficiency
        efficiency_score, efficiency_feedback = self._assess_efficiency(template)
        scores["efficiency"] = efficiency_score
        feedback.extend(efficiency_feedback)
        
        # Calculate overall score
        weights = {
            "completeness": 0.3,
            "clarity": 0.3,
            "specificity": 0.2,
            "efficiency": 0.2
        }
        
        overall_score = sum(scores[key] * weights[key] for key in weights)
        
        return overall_score, feedback
    
    def _assess_completeness(self, template: EnhancedModularPrompt) -> Tuple[float, List[str]]:
        """Assess template completeness"""
        feedback = []
        score = 1.0
        
        # Check for required sections
        if not template.system or not template.system.identity:
            feedback.append("Missing system identity")
            score -= 0.2
        
        if not template.parameters:
            feedback.append("Missing parameters section")
            score -= 0.1
        
        if not template.context:
            feedback.append("Missing context section")
            score -= 0.1
        
        if not template.execution or not template.execution.rules:
            feedback.append("Missing execution rules")
            score -= 0.2
        
        if not template.error_handling:
            feedback.append("Missing error handling section")
            score -= 0.1
        
        if not template.agent_loop:
            feedback.append("Missing agent loop section")
            score -= 0.1
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score, feedback
    
    def _assess_clarity(self, template: EnhancedModularPrompt) -> Tuple[float, List[str]]:
        """Assess template clarity"""
        feedback = []
        score = 1.0
        
        # Check system identity clarity
        if template.system and template.system.identity:
            identity = template.system.identity
            if len(identity) < 10:
                feedback.append("System identity is too short")
                score -= 0.1
            elif len(identity) > 200:
                feedback.append("System identity is too long")
                score -= 0.1
        
        # Check execution rules clarity
        if template.execution and template.execution.rules:
            for rule in template.execution.rules:
                rule_text = rule.content if isinstance(rule, ConditionalElement) else rule
                if len(rule_text) < 5:
                    feedback.append("Execution rule is too short")
                    score -= 0.05
                    break
                elif len(rule_text) > 100:
                    feedback.append("Execution rule is too long")
                    score -= 0.05
                    break
        
        # Check for jargon and complex language
        if template.system and template.system.identity:
            if self._contains_jargon(template.system.identity):
                feedback.append("System identity contains jargon")
                score -= 0.1
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score, feedback
    
    def _assess_specificity(self, template: EnhancedModularPrompt) -> Tuple[float, List[str]]:
        """Assess template specificity"""
        feedback = []
        score = 1.0
        
        # Check for specific capabilities
        if template.system and template.system.capabilities:
            if len(template.system.capabilities) < 2:
                feedback.append("Few system capabilities defined")
                score -= 0.1
        else:
            feedback.append("No system capabilities defined")
            score -= 0.2
        
        # Check for specific execution rules
        if template.execution and template.execution.rules:
            if len(template.execution.rules) < 3:
                feedback.append("Few execution rules defined")
                score -= 0.1
        
        # Check for conditional elements
        has_conditionals = False
        
        if template.execution and template.execution.rules:
            for rule in template.execution.rules:
                if isinstance(rule, ConditionalElement) and rule.condition:
                    has_conditionals = True
                    break
        
        if not has_conditionals and template.execution and template.execution.workflow:
            for step in template.execution.workflow:
                if isinstance(step, ConditionalElement) and step.condition:
                    has_conditionals = True
                    break
        
        if not has_conditionals:
            feedback.append("No conditional elements defined")
            score -= 0.2
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score, feedback
    
    def _assess_efficiency(self, template: EnhancedModularPrompt) -> Tuple[float, List[str]]:
        """Assess template token efficiency"""
        feedback = []
        score = 1.0
        
        # Convert to string to estimate tokens
        template_str = template.to_prompt_string()
        token_count = len(template_str) // 4  # Rough estimate
        
        # Assess token count
        if token_count > 1000:
            feedback.append(f"Template is very large ({token_count} tokens)")
            score -= 0.3
        elif token_count > 700:
            feedback.append(f"Template is large ({token_count} tokens)")
            score -= 0.2
        elif token_count > 500:
            feedback.append(f"Template is moderately large ({token_count} tokens)")
            score -= 0.1
        
        # Check for redundancy
        if self._contains_redundancy(template_str):
            feedback.append("Template contains redundant information")
            score -= 0.1
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score, feedback
    
    def _contains_jargon(self, text: str) -> bool:
        """Check if text contains technical jargon"""
        # Placeholder implementation
        return False
    
    def _contains_redundancy(self, text: str) -> bool:
        """Check if text contains redundant information"""
        # Placeholder implementation
        return False
```

### Construction Result

The `ConstructionResult` class represents the result of prompt construction:

```python
class ConstructionResult:
    """
    Result of prompt construction.
    """
    
    def __init__(self, 
                prompt: str = None,
                template: EnhancedModularPrompt = None,
                task_analysis: TaskAnalysis = None,
                selected_templates: List[str] = None,
                quality_score: float = 0.0,
                quality_feedback: List[str] = None,
                token_count: int = 0,
                construction_time: float = 0.0,
                error: str = None):
        """Initialize the construction result"""
        self.prompt = prompt
        self.template = template
        self.task_analysis = task_analysis
        self.selected_templates = selected_templates or []
        self.quality_score = quality_score
        self.quality_feedback = quality_feedback or []
        self.token_count = token_count
        self.construction_time = construction_time
        self.error = error
        self.success = error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "success": self.success,
            "construction_time": self.construction_time
        }
        
        if self.success:
            result.update({
                "prompt": self.prompt,
                "selected_templates": self.selected_templates,
                "quality_score": self.quality_score,
                "quality_feedback": self.quality_feedback,
                "token_count": self.token_count
            })
            
            if self.task_analysis:
                result["task_analysis"] = {
                    "task_category": self.task_analysis.task_category,
                    "complexity": self.task_analysis.complexity,
                    "domain": self.task_analysis.domain,
                    "confidence": self.task_analysis.confidence
                }
        else:
            result["error"] = self.error
        
        return result
```

## Integration with Agent Loop

The advanced dynamic prompt construction integrates with the agent loop pattern:

```python
class AgentLoopIntegration:
    """
    Integrates prompt construction with the agent loop pattern.
    """
    
    def __init__(self, prompt_constructor: AdvancedPromptConstructor):
        """Initialize the agent loop integration"""
        self.prompt_constructor = prompt_constructor
    
    def construct_analyze_prompt(self, 
                               task_description: str, 
                               user_context: Dict[str, Any] = None) -> str:
        """
        Construct a prompt for the analyze phase.
        
        Args:
            task_description: Description of the task
            user_context: User's context information
            
        Returns:
            Prompt string for the analyze phase
        """
        # Add analyze phase marker to context
        context = user_context.copy() if user_context else {}
        context["agent_loop_phase"] = "analyze"
        
        # Construct prompt
        result = self.prompt_constructor.construct_prompt(
            task_description, context, optimization_level="minimal")
        
        return result.prompt
    
    def construct_plan_prompt(self, 
                            task_description: str, 
                            analysis_result: str,
                            user_context: Dict[str, Any] = None) -> str:
        """
        Construct a prompt for the plan phase.
        
        Args:
            task_description: Description of the task
            analysis_result: Result of the analyze phase
            user_context: User's context information
            
        Returns:
            Prompt string for the plan phase
        """
        # Add plan phase marker to context
        context = user_context.copy() if user_context else {}
        context["agent_loop_phase"] = "plan"
        context["analysis_result"] = analysis_result
        
        # Construct prompt
        result = self.prompt_constructor.construct_prompt(
            task_description, context, optimization_level="standard")
        
        return result.prompt
    
    def construct_execute_prompt(self, 
                               task_description: str, 
                               analysis_result: str,
                               plan_result: str,
                               user_context: Dict[str, Any] = None) -> str:
        """
        Construct a prompt for the execute phase.
        
        Args:
            task_description: Description of the task
            analysis_result: Result of the analyze phase
            plan_result: Result of the plan phase
            user_context: User's context information
            
        Returns:
            Prompt string for the execute phase
        """
        # Add execute phase marker to context
        context = user_context.copy() if user_context else {}
        context["agent_loop_phase"] = "execute"
        context["analysis_result"] = analysis_result
        context["plan_result"] = plan_result
        
        # Construct prompt
        result = self.prompt_constructor.construct_prompt(
            task_description, context, optimization_level="standard")
        
        return result.prompt
    
    def construct_reflect_prompt(self, 
                               task_description: str, 
                               analysis_result: str,
                               plan_result: str,
                               execute_result: str,
                               user_context: Dict[str, Any] = None) -> str:
        """
        Construct a prompt for the reflect phase.
        
        Args:
            task_description: Description of the task
            analysis_result: Result of the analyze phase
            plan_result: Result of the plan phase
            execute_result: Result of the execute phase
            user_context: User's context information
            
        Returns:
            Prompt string for the reflect phase
        """
        # Add reflect phase marker to context
        context = user_context.copy() if user_context else {}
        context["agent_loop_phase"] = "reflect"
        context["analysis_result"] = analysis_result
        context["plan_result"] = plan_result
        context["execute_result"] = execute_result
        
        # Construct prompt
        result = self.prompt_constructor.construct_prompt(
            task_description, context, optimization_level="minimal")
        
        return result.prompt
```

## Continuous Learning Integration

The advanced dynamic prompt construction integrates with continuous learning:

```python
class ContinuousLearningIntegration:
    """
    Integrates prompt construction with continuous learning.
    """
    
    def __init__(self, prompt_constructor: AdvancedPromptConstructor, analytics: PromptAnalytics):
        """Initialize the continuous learning integration"""
        self.prompt_constructor = prompt_constructor
        self.analytics = analytics
    
    def record_prompt_feedback(self, 
                             prompt_id: str,
                             success: bool,
                             user_rating: Optional[int] = None,
                             completion_time: Optional[float] = None,
                             error_type: Optional[str] = None):
        """
        Record feedback for a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            success: Whether the prompt was successful
            user_rating: User satisfaction rating (1-5)
            completion_time: Time to complete the task
            error_type: Type of error if unsuccessful
        """
        self.analytics.record_prompt_performance(
            prompt_id=prompt_id,
            success=success,
            user_rating=user_rating,
            completion_time=completion_time,
            error_type=error_type
        )
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommendations for optimizing prompts.
        
        Returns:
            List of optimization recommendations
        """
        return self.analytics.get_optimization_recommendations()
    
    def apply_optimization_recommendations(self, 
                                         recommendations: List[Dict[str, Any]]) -> bool:
        """
        Apply optimization recommendations to the prompt constructor.
        
        Args:
            recommendations: List of optimization recommendations
            
        Returns:
            Whether the recommendations were applied successfully
        """
        # Placeholder implementation
        return True
```

## Implementation Plan

The implementation of advanced dynamic prompt construction will proceed in phases:

### Phase 1: Core Components
- Implement `AdvancedPromptConstructor` class
- Develop basic `TaskAnalyzer` with category classification
- Create simple `ContextAnalyzer` for context extraction
- Implement basic `TemplateSelector` for template selection
- Develop simple `TemplateComposer` for template merging

### Phase 2: Enhanced Analysis
- Enhance `TaskAnalyzer` with domain classification
- Improve parameter extraction for different task types
- Develop sophisticated `ContextAnalyzer` with relevance scoring
- Implement context-aware template selection

### Phase 3: Composition and Optimization
- Enhance `TemplateComposer` with conflict resolution
- Implement `PromptOptimizer` with multiple strategies
- Develop `QualityAssessor` for prompt evaluation
- Create comprehensive validation framework

### Phase 4: Agent Loop Integration
- Implement `AgentLoopIntegration` class
- Develop phase-specific prompt construction
- Create context preservation between phases
- Implement feedback mechanisms

### Phase 5: Continuous Learning
- Implement `ContinuousLearningIntegration` class
- Develop feedback recording and analysis
- Create optimization recommendation system
- Implement automatic template improvement

## Testing and Validation

The implementation includes comprehensive testing and validation:

```python
class PromptConstructionTester:
    """
    Tests prompt construction with various scenarios.
    """
    
    def __init__(self, prompt_constructor: AdvancedPromptConstructor):
        """Initialize the prompt construction tester"""
        self.prompt_constructor = prompt_constructor
        self.test_cases = []
    
    def add_test_case(self, 
                     task_description: str, 
                     expected_category: str,
                     expected_complexity: str,
                     expected_token_range: Tuple[int, int],
                     user_context: Dict[str, Any] = None,
                     user_preferences: Dict[str, Any] = None):
        """Add a test case"""
        self.test_cases.append({
            "task_description": task_description,
            "expected_category": expected_category,
            "expected_complexity": expected_complexity,
            "expected_token_range": expected_token_range,
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
        expected_complexity = test_case["expected_complexity"]
        expected_token_range = test_case["expected_token_range"]
        user_context = test_case["user_context"]
        user_preferences = test_case["user_preferences"]
        
        # Construct prompt
        result = self.prompt_constructor.construct_prompt(
            task_description, user_context, user_preferences)
        
        # Check if construction was successful
        if not result.success:
            return {
                "passed": False,
                "task_description": task_description,
                "error": result.error
            }
        
        # Check category
        category_correct = result.task_analysis.task_category == expected_category
        
        # Check complexity
        complexity_correct = result.task_analysis.complexity == expected_complexity
        
        # Check token count
        min_tokens, max_tokens = expected_token_range
        token_count_correct = min_tokens <= result.token_count <= max_tokens
        
        # Overall result
        passed = category_correct and complexity_correct and token_count_correct
        
        return {
            "passed": passed,
            "task_description": task_description,
            "expected_category": expected_category,
            "actual_category": result.task_analysis.task_category,
            "category_correct": category_correct,
            "expected_complexity": expected_complexity,
            "actual_complexity": result.task_analysis.complexity,
            "complexity_correct": complexity_correct,
            "expected_token_range": expected_token_range,
            "actual_token_count": result.token_count,
            "token_count_correct": token_count_correct,
            "quality_score": result.quality_score,
            "construction_time": result.construction_time
        }
```

## Conclusion

The advanced dynamic prompt construction design provides a sophisticated system for analyzing tasks, selecting appropriate templates, and constructing optimized prompts. By leveraging the enhanced modular prompt architecture and expanded template library, it enables more effective and efficient prompt engineering for the Aideon AI Lite platform.

The design includes comprehensive task analysis, context-aware template selection, multi-template composition, and quality assessment capabilities. It also integrates with the agent loop pattern and continuous learning to provide a complete solution for dynamic prompt construction.

The implementation plan outlines a phased approach to developing the system, with comprehensive testing and validation to ensure quality and effectiveness.
