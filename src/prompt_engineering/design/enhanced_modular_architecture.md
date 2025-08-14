# Enhanced Modular Prompt Architecture Design

## Overview

This document outlines the design for the enhanced modular prompt architecture for the Aideon AI Lite platform. The architecture builds upon the existing XML-tagged structure while introducing more sophisticated organization, conditional processing, and robust parsing capabilities.

## Design Goals

1. **Hierarchical Structure** - Support nested XML tags for more granular control over prompt components
2. **Conditional Processing** - Enable conditional sections that adapt based on context and parameters
3. **Extensibility** - Ensure easy addition of new tag types and processing rules
4. **Backward Compatibility** - Maintain compatibility with existing prompt templates
5. **Performance Optimization** - Improve token efficiency through structural optimizations
6. **Validation** - Provide robust validation of prompt structure and content
7. **Visualization** - Support visual editing and representation of prompt structures

## Core Architecture

### Enhanced XML Tag Structure

The enhanced architecture introduces a hierarchical tag structure with the following primary components:

```
<prompt>
  <system>
    <identity>...</identity>
    <capabilities>...</capabilities>
    <constraints>...</constraints>
  </system>
  
  <parameters>
    <intelligence_level>...</intelligence_level>
    <verbosity>...</verbosity>
    <creativity>...</creativity>
    <format_preference>...</format_preference>
    <domain_expertise>...</domain_expertise>
  </parameters>
  
  <context>
    <project>...</project>
    <history>...</history>
    <priority>...</priority>
    <custom_context key="value">...</custom_context>
  </context>
  
  <execution>
    <rules>
      <rule condition="...">...</rule>
      <rule>...</rule>
    </rules>
    <workflow>
      <step id="1">...</step>
      <step id="2" condition="...">...</step>
    </workflow>
  </execution>
  
  <error_handling>
    <strategy type="graceful_degradation">...</strategy>
    <fallback>...</fallback>
    <recovery>...</recovery>
  </error_handling>
  
  <agent_loop>
    <analyze>...</analyze>
    <plan>...</plan>
    <execute>...</execute>
    <reflect>...</reflect>
  </agent_loop>
</prompt>
```

### Conditional Processing

The architecture supports conditional processing through attributes on tags:

```xml
<rule condition="task_type == 'coding'">Follow code style guidelines and include comments</rule>
<step id="2" condition="complexity == 'complex'">Perform detailed error analysis</step>
<strategy type="graceful_degradation" condition="error_type == 'api_timeout'">
  Fall back to cached data if available
</strategy>
```

Conditions can reference:
- Template parameters
- Context variables
- System state
- User preferences
- Previous execution results

### Tag Inheritance and Composition

The architecture supports inheritance and composition of tags:

```xml
<template id="base_coding">
  <rule>Follow code style guidelines</rule>
  <rule>Include comprehensive error handling</rule>
</template>

<template id="python_coding" extends="base_coding">
  <rule>Follow PEP 8 style guidelines</rule>
  <rule>Use type hints for function parameters</rule>
</template>
```

## Component Design

### ModularPromptParser

The `ModularPromptParser` class is responsible for parsing XML prompt templates into structured objects:

```python
class ModularPromptParser:
    def parse(self, xml_string: str) -> ModularPrompt:
        """Parse XML string into ModularPrompt object"""
        
    def validate(self, xml_string: str) -> List[ValidationError]:
        """Validate XML structure and content"""
        
    def parse_file(self, file_path: str) -> ModularPrompt:
        """Parse XML file into ModularPrompt object"""
```

### EnhancedModularPrompt

The `EnhancedModularPrompt` class represents a parsed prompt template with methods for manipulation and rendering:

```python
class EnhancedModularPrompt:
    def __init__(self):
        self.system = SystemSection()
        self.parameters = ParametersSection()
        self.context = ContextSection()
        self.execution = ExecutionSection()
        self.error_handling = ErrorHandlingSection()
        self.agent_loop = AgentLoopSection()
    
    def to_xml(self) -> str:
        """Convert to XML string"""
    
    def to_prompt_string(self, context: Dict[str, Any] = None) -> str:
        """Convert to formatted prompt string with context applied"""
    
    def optimize_tokens(self, level: str = "standard") -> "EnhancedModularPrompt":
        """Create optimized version with reduced token usage"""
    
    def merge(self, other: "EnhancedModularPrompt") -> "EnhancedModularPrompt":
        """Merge with another prompt template"""
    
    def apply_conditions(self, context: Dict[str, Any]) -> "EnhancedModularPrompt":
        """Apply conditional processing based on context"""
```

### Section Classes

Each major section of the prompt is represented by a dedicated class:

```python
class SystemSection:
    def __init__(self):
        self.identity = ""
        self.capabilities = []
        self.constraints = []

class ParametersSection:
    def __init__(self):
        self.intelligence_level = "Adaptive"
        self.verbosity = "Balanced"
        self.creativity = "Balanced"
        self.format_preference = "Default"
        self.domain_expertise = "General"
        self.custom_parameters = {}

class ContextSection:
    def __init__(self):
        self.project = ""
        self.history = ""
        self.priority = "Balance"
        self.custom_context = {}

class ExecutionSection:
    def __init__(self):
        self.rules = []
        self.workflow = []

class ErrorHandlingSection:
    def __init__(self):
        self.strategies = []
        self.fallback = ""
        self.recovery = ""

class AgentLoopSection:
    def __init__(self):
        self.analyze = ""
        self.plan = ""
        self.execute = ""
        self.reflect = ""
```

### Conditional Elements

Conditional elements are represented by classes that include condition evaluation:

```python
class ConditionalElement:
    def __init__(self, content: str, condition: str = None):
        self.content = content
        self.condition = condition
    
    def should_include(self, context: Dict[str, Any]) -> bool:
        """Evaluate whether this element should be included based on context"""
        if not self.condition:
            return True
        
        # Evaluate condition expression against context
        return self._evaluate_condition(self.condition, context)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate condition expression"""
        # Implementation with safe evaluation logic
```

## Condition Evaluation Engine

The condition evaluation engine provides safe evaluation of conditional expressions:

```python
class ConditionEvaluator:
    def __init__(self):
        self.safe_functions = {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "contains": lambda a, b: b in a,
            "startswith": lambda a, b: a.startswith(b),
            "endswith": lambda a, b: a.endswith(b),
        }
    
    def evaluate(self, condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate condition expression against context"""
        # Implementation with restricted evaluation for security
```

## Template Inheritance Engine

The template inheritance engine manages template extension and composition:

```python
class TemplateInheritanceEngine:
    def __init__(self, template_registry: Dict[str, EnhancedModularPrompt]):
        self.template_registry = template_registry
    
    def resolve_inheritance(self, template_id: str) -> EnhancedModularPrompt:
        """Resolve template inheritance chain and return complete template"""
        
    def compose_templates(self, base_template_id: str, 
                          extension_template_ids: List[str]) -> EnhancedModularPrompt:
        """Compose multiple templates together"""
```

## Visual Editor Integration

The architecture includes interfaces for visual editor integration:

```python
class VisualEditorInterface:
    def to_editor_format(self, prompt: EnhancedModularPrompt) -> Dict[str, Any]:
        """Convert prompt to format suitable for visual editor"""
    
    def from_editor_format(self, editor_data: Dict[str, Any]) -> EnhancedModularPrompt:
        """Convert editor format back to prompt"""
```

## Token Optimization Strategies

The architecture includes multiple token optimization strategies:

```python
class TokenOptimizer:
    def __init__(self):
        self.strategies = {
            "minimal": self._minimal_optimization,
            "standard": self._standard_optimization,
            "aggressive": self._aggressive_optimization
        }
    
    def optimize(self, prompt: EnhancedModularPrompt, 
                level: str = "standard") -> EnhancedModularPrompt:
        """Apply optimization strategy to prompt"""
        
    def _minimal_optimization(self, prompt: EnhancedModularPrompt) -> EnhancedModularPrompt:
        """Apply minimal token optimization"""
        
    def _standard_optimization(self, prompt: EnhancedModularPrompt) -> EnhancedModularPrompt:
        """Apply standard token optimization"""
        
    def _aggressive_optimization(self, prompt: EnhancedModularPrompt) -> EnhancedModularPrompt:
        """Apply aggressive token optimization"""
```

## Integration with Agent Loop

The architecture integrates with the agent loop pattern:

```python
class AgentLoopIntegration:
    def __init__(self, prompt: EnhancedModularPrompt):
        self.prompt = prompt
    
    def get_analyze_instructions(self, context: Dict[str, Any]) -> str:
        """Get instructions for the analyze phase"""
        
    def get_plan_instructions(self, context: Dict[str, Any]) -> str:
        """Get instructions for the plan phase"""
        
    def get_execute_instructions(self, context: Dict[str, Any]) -> str:
        """Get instructions for the execute phase"""
        
    def get_reflect_instructions(self, context: Dict[str, Any]) -> str:
        """Get instructions for the reflect phase"""
```

## Implementation Plan

The implementation of the enhanced modular prompt architecture will proceed in phases:

### Phase 1: Core Structure and Parsing
- Implement basic hierarchical tag structure
- Develop robust XML parsing with error handling
- Ensure backward compatibility with existing templates
- Create basic validation functionality

### Phase 2: Conditional Processing
- Implement condition evaluation engine
- Add conditional elements to all sections
- Develop context-based condition application
- Create test suite for conditional processing

### Phase 3: Inheritance and Composition
- Implement template inheritance engine
- Add composition capabilities
- Develop inheritance resolution algorithm
- Create test suite for inheritance and composition

### Phase 4: Token Optimization
- Implement multiple optimization strategies
- Add token usage estimation
- Develop context-aware optimization
- Create benchmarking for optimization effectiveness

### Phase 5: Visual Editor Integration
- Design editor data format
- Implement conversion to/from editor format
- Create sample visual editor interface
- Develop documentation for editor integration

## Backward Compatibility

To ensure backward compatibility with existing templates:

1. The parser will automatically convert legacy templates to the new format
2. A compatibility layer will translate between old and new APIs
3. Existing template files will continue to work without modification
4. A migration utility will be provided to upgrade templates to the new format

## Security Considerations

The architecture includes several security measures:

1. Safe condition evaluation with restricted expressions
2. Input validation for all XML parsing
3. Sanitization of template content
4. Proper error handling for malformed templates
5. Resource limits to prevent DoS attacks

## Performance Considerations

The architecture is designed with performance in mind:

1. Lazy evaluation of conditional sections
2. Caching of parsed templates
3. Efficient XML parsing with minimal overhead
4. Multiple optimization strategies for different use cases
5. Benchmarking tools to measure performance impact

## Conclusion

The enhanced modular prompt architecture provides a robust, extensible foundation for the Aideon AI Lite prompt engineering system. By supporting hierarchical structure, conditional processing, and template inheritance, it enables more sophisticated and efficient prompts while maintaining backward compatibility with existing templates.

The architecture is designed to integrate seamlessly with the agent loop pattern and other specialized modules, providing a comprehensive solution for prompt engineering needs across diverse use cases.
