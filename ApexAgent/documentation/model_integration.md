# Aideon AI Lite Model Integration Documentation

## Overview

This document provides comprehensive documentation for the Model Integration Framework in Aideon AI Lite. The framework enables seamless integration of multiple LLM models across different modalities (text, code, image, video, audio), supporting hybrid processing (local + cloud), dynamic model selection, fallback chains, and integration with the multi-agent system.

## Table of Contents

1. [Architecture](#architecture)
2. [Model Integration Framework](#model-integration-framework)
3. [Model Providers](#model-providers)
4. [Agent-Model Integration](#agent-model-integration)
5. [Model Validation](#model-validation)
6. [Configuration](#configuration)
7. [Usage Examples](#usage-examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Architecture

The Model Integration Framework consists of several key components:

- **ModelIntegrationFramework**: Core class that manages model registration, selection, and execution
- **ModelProvider**: Base class for model providers (e.g., OpenAI, Anthropic, Meta)
- **Model**: Base class for individual models across different modalities
- **AgentModelIntegration**: Connects the Agent Manager with the Model Integration Framework
- **ModelValidation**: Provides utilities for validating model performance and compatibility

The architecture follows these design principles:

- **Modularity**: Each component has a clear responsibility and can be extended independently
- **Extensibility**: New models and providers can be added without modifying existing code
- **Resilience**: Fallback mechanisms ensure the system continues to function even if specific models fail
- **Hybrid Processing**: Support for both local and cloud-based model execution
- **Dynamic Selection**: Intelligent model selection based on task requirements and available resources

## Model Integration Framework

The `ModelIntegrationFramework` class is the central component that manages model registration, selection, and execution.

### Key Features

- **Model Registry**: Maintains registries for models across different modalities
- **Provider Registry**: Manages model providers and their initialization
- **Dynamic Model Selection**: Selects the best model based on task requirements
- **Fallback Chains**: Creates fallback chains to ensure resilience
- **Response Caching**: Caches model responses to improve performance
- **Metrics Tracking**: Tracks performance metrics for models

### Usage

```javascript
// Initialize the framework
const modelFramework = new ModelIntegrationFramework(core);
await modelFramework.initialize();

// Select a model
const model = modelFramework.selectModel('text', {
  minContextWindow: 32000,
  processingPreference: 'local'
});

// Execute a model
const result = await modelFramework.execute(model.id, 'text', {
  prompt: 'Generate a short paragraph about AI.'
});

// Execute with fallback
const result = await modelFramework.executeWithFallback('text', {
  prompt: 'Generate a short paragraph about AI.'
}, {
  requirements: {
    processingPreference: 'local'
  }
});
```

## Model Providers

Model providers are responsible for registering and managing models from specific sources (e.g., OpenAI, Anthropic, Meta).

### Built-in Providers

The framework includes the following built-in providers:

- **OpenAIProvider**: Provides access to OpenAI models for text, code, and image generation
- **AnthropicProvider**: Provides access to Anthropic Claude models for text and code generation
- **MetaProvider**: Provides access to Meta's Llama models for text and code generation
- **StabilityAIProvider**: Provides access to Stability AI models for image and audio generation
- **SkyworkAIProvider**: Provides access to SkyworkAI models for video generation

### Custom Providers

You can create custom providers by extending the `ModelProvider` class:

```javascript
class CustomProvider extends ModelProvider {
  constructor(core) {
    super(core);
    this.config = core.configManager.getConfig().providers?.custom || {};
  }
  
  get id() {
    return 'custom';
  }
  
  get name() {
    return 'Custom Provider';
  }
  
  async _registerModels() {
    // Register models
    this.models.push(new CustomTextModel(this, {
      id: 'custom-text',
      name: 'Custom Text Model',
      modality: 'text',
      // ... other properties
    }));
  }
}
```

### Model Implementation

Models are implemented by extending the `Model` class:

```javascript
class CustomTextModel extends Model {
  async execute(params, options = {}) {
    const { prompt, temperature = 0.7, max_tokens = 1000 } = params;
    
    // Implementation details
    // ...
    
    return {
      text: 'Generated text',
      usage: { total_tokens: 100 },
      model: this.id
    };
  }
}
```

## Agent-Model Integration

The `AgentModelIntegration` class connects the Agent Manager with the Model Integration Framework, allowing agents to seamlessly use different models across modalities.

### Key Features

- **Agent-Specific Model Preferences**: Maintains preferences for each agent
- **Role-Based Defaults**: Provides default model preferences based on agent roles
- **Model Capability Registry**: Tracks capabilities of different models
- **Dynamic Model Selection**: Selects the best model for an agent based on task requirements

### Usage

```javascript
// Initialize the integration
const agentModelIntegration = new AgentModelIntegration(core);
await agentModelIntegration.initialize();

// Select model for an agent
const model = agentModelIntegration.selectModelForAgent('agent-1', 'text', {
  minContextWindow: 32000
});

// Execute model for an agent
const result = await agentModelIntegration.executeModelForAgent('agent-1', 'text', {
  prompt: 'Generate a short paragraph about AI.'
}, {
  requirements: {
    processingPreference: 'local'
  }
});
```

## Model Validation

The `ModelValidation` class provides utilities for validating model performance and compatibility across the multi-agent system.

### Key Features

- **Model Validation**: Validates individual models across different modalities
- **Benchmarking**: Benchmarks model performance for comparison
- **Agent-Model Integration Validation**: Validates the integration between agents and models
- **Result Storage**: Stores validation and benchmark results for analysis

### Usage

```javascript
// Initialize the validation
const modelValidation = new ModelValidation(core);

// Validate all models
const results = await modelValidation.validateAllModels({
  offlineOnly: false,
  skipModels: ['model-1', 'model-2']
});

// Benchmark all models
const benchmarkResults = await modelValidation.benchmarkAllModels({
  offlineOnly: false
});

// Validate agent-model integration
const integrationResults = await modelValidation.validateAgentModelIntegration({
  testFallback: true
});
```

## Configuration

The Model Integration Framework can be configured through the Aideon AI Lite configuration system.

### Example Configuration

```json
{
  "models": {
    "defaultProcessingPreference": "auto",
    "cacheExpiry": 3600000,
    "fallbackEnabled": true
  },
  "providers": {
    "openai": {
      "apiKey": "YOUR_API_KEY",
      "baseUrl": "https://api.openai.com/v1"
    },
    "anthropic": {
      "apiKey": "YOUR_API_KEY",
      "baseUrl": "https://api.anthropic.com/v1"
    },
    "meta": {
      "modelPath": "/path/to/models/llama"
    },
    "stabilityai": {
      "apiKey": "YOUR_API_KEY",
      "baseUrl": "https://api.stability.ai/v1"
    },
    "skyworkai": {
      "apiKey": "YOUR_API_KEY",
      "baseUrl": "https://api.skywork.ai/v1"
    }
  },
  "agentModel": {
    "defaultPreferences": {
      "planner": {
        "text": {
          "preferredModels": ["gpt-4.5", "claude-3.7-sonnet", "llama-3.1-70b"],
          "requirements": {
            "minContextWindow": 32000,
            "processingPreference": "cloud"
          }
        }
      }
    }
  },
  "modelValidation": {
    "offlineOnly": false,
    "testFallback": true
  }
}
```

## Usage Examples

### Basic Text Generation

```javascript
// Get the model framework
const modelFramework = core.modelIntegrationFramework;

// Execute a text model
const result = await modelFramework.execute('gpt-4.5', 'text', {
  prompt: 'Generate a short paragraph about artificial intelligence.',
  temperature: 0.7,
  max_tokens: 1000
});

console.log(result.text);
```

### Code Generation with Fallback

```javascript
// Get the model framework
const modelFramework = core.modelIntegrationFramework;

// Execute a code model with fallback
const result = await modelFramework.executeWithFallback('code', {
  prompt: 'Write a function that calculates the factorial of a number in JavaScript.',
  temperature: 0.3,
  max_tokens: 2000
}, {
  requirements: {
    processingPreference: 'local'
  }
});

console.log(result.code);
```

### Image Generation

```javascript
// Get the model framework
const modelFramework = core.modelIntegrationFramework;

// Execute an image model
const result = await modelFramework.execute('dall-e-3', 'image', {
  prompt: 'A beautiful landscape with mountains and a lake at sunset.',
  size: '1024x1024'
});

console.log(result.imageUrl);
```

### Agent-Specific Model Selection

```javascript
// Get the agent-model integration
const agentModelIntegration = core.agentModelIntegration;

// Select a model for an agent
const model = agentModelIntegration.selectModelForAgent('agent-1', 'text', {
  minContextWindow: 32000,
  requiredCapabilities: ['reasoning', 'planning']
});

console.log(`Selected model: ${model.id}`);
```

### Model Validation

```javascript
// Get the model validation
const modelValidation = new ModelValidation(core);

// Validate a specific model
const result = await modelValidation.validateModel(
  modelFramework.getModel('gpt-4.5', 'text'),
  { offlineOnly: false }
);

console.log(`Validation status: ${result.status}`);
console.log(`Average latency: ${result.metrics.averageLatency}ms`);
console.log(`Quality score: ${result.metrics.qualityScore}`);
```

## Best Practices

### Model Selection

- **Use Dynamic Selection**: Let the framework select the best model based on task requirements
- **Specify Requirements**: Provide detailed requirements to ensure the selected model meets your needs
- **Enable Fallback**: Use fallback chains for critical operations to ensure resilience

### Performance Optimization

- **Use Caching**: Enable response caching for repetitive tasks
- **Batch Requests**: Batch similar requests to reduce overhead
- **Monitor Metrics**: Regularly check model performance metrics to identify bottlenecks

### Hybrid Processing

- **Local for Speed**: Use local processing for latency-sensitive tasks
- **Cloud for Quality**: Use cloud processing for tasks requiring high-quality results
- **Auto Mode**: Use 'auto' processing preference to let the framework decide based on available resources

### Security

- **API Key Management**: Store API keys securely and rotate them regularly
- **Input Validation**: Validate all inputs before sending them to models
- **Output Filtering**: Filter model outputs to prevent sensitive information leakage

## Troubleshooting

### Common Issues

#### Model Not Found

```
Error: Model gpt-4.5 not found for text modality
```

**Solution**: Ensure the model is registered and the provider is initialized.

#### API Key Missing

```
Error: OpenAI API key is missing
```

**Solution**: Set the API key in the configuration or environment variables.

#### Local Model File Missing

```
Error: Model file not found: /path/to/models/llama/llama-3.1-70b.gguf
```

**Solution**: Download the model file or update the model path in the configuration.

#### Execution Timeout

```
Error: Request timed out after 30000ms
```

**Solution**: Increase the timeout in the options or reduce the complexity of the request.

### Debugging

- **Enable Debug Logging**: Set the log level to 'debug' to see detailed logs
- **Check Validation Results**: Run validation tests to identify issues with specific models
- **Monitor Metrics**: Check performance metrics to identify bottlenecks
- **Test with Simple Prompts**: Start with simple prompts to isolate issues

### Getting Help

If you encounter issues that you cannot resolve, please:

1. Check the [GitHub repository](https://github.com/aideon/aideon-ai-lite) for known issues
2. Join the [Aideon AI Lite community](https://community.aideon.ai) for support
3. Contact [support@aideon.ai](mailto:support@aideon.ai) for direct assistance
