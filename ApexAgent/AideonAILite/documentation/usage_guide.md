# Aideon AI Lite - Usage Guide for Advanced LLM Integration

This guide provides practical instructions for using the newly integrated advanced LLM models in Aideon AI Lite across all modalities (text, code, image, video, and audio).

## Table of Contents

1. [Getting Started](#getting-started)
2. [Text Generation](#text-generation)
3. [Code Generation](#code-generation)
4. [Image Generation](#image-generation)
5. [Video Generation](#video-generation)
6. [Audio Generation](#audio-generation)
7. [Hybrid Processing](#hybrid-processing)
8. [Agent-Specific Configuration](#agent-specific-configuration)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Aideon AI Lite installed and configured
- API keys for proprietary models (if using cloud processing)
- Local model files for open-source models (if using local processing)

### Configuration

1. Open the configuration file at `/path/to/config.json`
2. Add your API keys for proprietary models:

```json
{
  "providers": {
    "openai": {
      "apiKey": "YOUR_OPENAI_API_KEY"
    },
    "anthropic": {
      "apiKey": "YOUR_ANTHROPIC_API_KEY"
    },
    "stabilityai": {
      "apiKey": "YOUR_STABILITY_API_KEY"
    }
  }
}
```

3. Configure local model paths for open-source models:

```json
{
  "providers": {
    "meta": {
      "modelPath": "/path/to/models/llama"
    }
  }
}
```

## Text Generation

### Basic Text Generation

```javascript
// Import the Aideon core
const { AideonCore } = require('aideon-ai-lite');

// Initialize the core
const core = new AideonCore();
await core.initialize();

// Get the model framework
const modelFramework = core.modelIntegrationFramework;

// Generate text with the default model
const result = await modelFramework.executeWithFallback('text', {
  prompt: 'Write a short story about a robot learning to paint.',
  temperature: 0.7,
  max_tokens: 1000
});

console.log(result.text);
```

### Advanced Text Generation

```javascript
// Generate text with specific requirements
const result = await modelFramework.executeWithFallback('text', {
  prompt: 'Explain quantum computing to a high school student.',
  temperature: 0.5,
  max_tokens: 2000
}, {
  requirements: {
    minContextWindow: 32000,
    processingPreference: 'cloud',
    requiredCapabilities: ['reasoning', 'education']
  }
});

console.log(result.text);
```

### Example: Multi-turn Conversation

```javascript
// Initialize conversation history
const history = [
  { role: 'system', content: 'You are a helpful assistant.' },
  { role: 'user', content: 'What is machine learning?' }
];

// Generate response
const result = await modelFramework.execute('gpt-4.5', 'text', {
  messages: history,
  temperature: 0.7,
  max_tokens: 1000
});

// Update history
history.push({ role: 'assistant', content: result.text });
history.push({ role: 'user', content: 'Can you give me a simple example?' });

// Generate next response
const nextResult = await modelFramework.execute('gpt-4.5', 'text', {
  messages: history,
  temperature: 0.7,
  max_tokens: 1000
});

console.log(nextResult.text);
```

## Code Generation

### Basic Code Generation

```javascript
// Generate code with the default model
const result = await modelFramework.executeWithFallback('code', {
  prompt: 'Write a function that calculates the Fibonacci sequence in Python.',
  temperature: 0.3,
  max_tokens: 1000
});

console.log(result.code);
```

### Advanced Code Generation

```javascript
// Generate code with specific requirements
const result = await modelFramework.executeWithFallback('code', {
  prompt: 'Create a React component that displays a paginated table with sorting and filtering.',
  temperature: 0.3,
  max_tokens: 2000
}, {
  requirements: {
    processingPreference: 'cloud',
    requiredCapabilities: ['code_generation', 'react']
  }
});

console.log(result.code);
```

### Example: Code Explanation

```javascript
// Generate code explanation
const code = `
function quickSort(arr) {
  if (arr.length <= 1) {
    return arr;
  }
  
  const pivot = arr[0];
  const left = [];
  const right = [];
  
  for (let i = 1; i < arr.length; i++) {
    if (arr[i] < pivot) {
      left.push(arr[i]);
    } else {
      right.push(arr[i]);
    }
  }
  
  return [...quickSort(left), pivot, ...quickSort(right)];
}
`;

const result = await modelFramework.execute('claude-3.7-sonnet', 'code', {
  prompt: `Explain the following code step by step:\n\n${code}`,
  temperature: 0.3,
  max_tokens: 2000
});

console.log(result.code);
```

## Image Generation

### Basic Image Generation

```javascript
// Generate image with the default model
const result = await modelFramework.executeWithFallback('image', {
  prompt: 'A serene landscape with mountains, a lake, and a sunset.',
  width: 1024,
  height: 1024
});

// Save the image
if (result.imageUrl) {
  // Image is available as a URL
  console.log(`Image URL: ${result.imageUrl}`);
} else if (result.imageBase64) {
  // Image is available as base64 data
  const fs = require('fs');
  fs.writeFileSync('generated_image.png', Buffer.from(result.imageBase64, 'base64'));
  console.log('Image saved as generated_image.png');
}
```

### Advanced Image Generation

```javascript
// Generate image with specific requirements
const result = await modelFramework.executeWithFallback('image', {
  prompt: 'A photorealistic portrait of a cybernetic being with glowing blue eyes.',
  negative_prompt: 'blurry, distorted, low quality',
  width: 1024,
  height: 1024
}, {
  requirements: {
    processingPreference: 'local',
    requiredCapabilities: ['photorealistic_images']
  }
});

// Process the result
console.log(result);
```

### Example: Image Variation

```javascript
// Generate image variation
const fs = require('fs');
const imageBuffer = fs.readFileSync('input_image.png');
const imageBase64 = imageBuffer.toString('base64');

const result = await modelFramework.execute('stable-diffusion-3', 'image', {
  prompt: 'Convert to oil painting style with vibrant colors.',
  image: imageBase64,
  width: 1024,
  height: 1024
});

// Save the image
if (result.imageBase64) {
  fs.writeFileSync('variation_image.png', Buffer.from(result.imageBase64, 'base64'));
  console.log('Image variation saved as variation_image.png');
}
```

## Video Generation

### Basic Video Generation

```javascript
// Generate video with the default model
const result = await modelFramework.executeWithFallback('video', {
  prompt: 'A timelapse of a flower blooming.',
  duration: 5.0
});

// Save the video
if (result.videoUrl) {
  // Video is available as a URL
  console.log(`Video URL: ${result.videoUrl}`);
} else if (result.videoBase64) {
  // Video is available as base64 data
  const fs = require('fs');
  fs.writeFileSync('generated_video.mp4', Buffer.from(result.videoBase64, 'base64'));
  console.log('Video saved as generated_video.mp4');
}
```

### Advanced Video Generation

```javascript
// Generate video with specific requirements
const result = await modelFramework.executeWithFallback('video', {
  prompt: 'A cinematic scene of a spaceship landing on an alien planet with two moons.',
  duration: 10.0
}, {
  requirements: {
    processingPreference: 'cloud',
    requiredCapabilities: ['cinematic_quality']
  }
});

// Process the result
console.log(result);
```

### Example: Image-to-Video

```javascript
// Generate video from image
const fs = require('fs');
const imageBuffer = fs.readFileSync('input_image.png');
const imageBase64 = imageBuffer.toString('base64');

const result = await modelFramework.execute('skyreel-v1', 'video', {
  prompt: 'Animate this image with gentle movement and particle effects.',
  image: imageBase64,
  duration: 5.0
});

// Save the video
if (result.videoUrl) {
  console.log(`Video URL: ${result.videoUrl}`);
}
```

## Audio Generation

### Basic Audio Generation

```javascript
// Generate audio with the default model
const result = await modelFramework.executeWithFallback('audio', {
  prompt: 'A calm piano melody with soft strings in the background.',
  duration: 10.0
});

// Save the audio
if (result.audioUrl) {
  // Audio is available as a URL
  console.log(`Audio URL: ${result.audioUrl}`);
} else if (result.audioBase64) {
  // Audio is available as base64 data
  const fs = require('fs');
  fs.writeFileSync('generated_audio.mp3', Buffer.from(result.audioBase64, 'base64'));
  console.log('Audio saved as generated_audio.mp3');
}
```

### Advanced Audio Generation

```javascript
// Generate audio with specific requirements
const result = await modelFramework.executeWithFallback('audio', {
  prompt: 'An electronic dance track with a strong beat and synthesizer melody.',
  duration: 30.0
}, {
  requirements: {
    processingPreference: 'cloud',
    requiredCapabilities: ['music_generation']
  }
});

// Process the result
console.log(result);
```

### Example: Text-to-Speech

```javascript
// Generate speech from text
const result = await modelFramework.execute('stable-audio-2.0', 'audio', {
  prompt: 'Generate speech for the following text: Welcome to Aideon AI Lite, your advanced AI assistant.',
  voice: 'female',
  duration: 5.0
});

// Save the audio
if (result.audioUrl) {
  console.log(`Audio URL: ${result.audioUrl}`);
}
```

## Hybrid Processing

### Automatic Mode

```javascript
// Let the framework decide between local and cloud processing
const result = await modelFramework.executeWithFallback('text', {
  prompt: 'Write a short story about a robot learning to paint.',
  temperature: 0.7,
  max_tokens: 1000
}, {
  requirements: {
    processingPreference: 'auto'
  }
});

console.log(`Processing type: ${result.processingType}`);
console.log(result.text);
```

### Force Local Processing

```javascript
// Force local processing
const result = await modelFramework.executeWithFallback('text', {
  prompt: 'Write a short story about a robot learning to paint.',
  temperature: 0.7,
  max_tokens: 1000
}, {
  requirements: {
    processingPreference: 'local'
  }
});

console.log(`Processing type: ${result.processingType}`);
console.log(result.text);
```

### Force Cloud Processing

```javascript
// Force cloud processing
const result = await modelFramework.executeWithFallback('text', {
  prompt: 'Write a short story about a robot learning to paint.',
  temperature: 0.7,
  max_tokens: 1000
}, {
  requirements: {
    processingPreference: 'cloud'
  }
});

console.log(`Processing type: ${result.processingType}`);
console.log(result.text);
```

## Agent-Specific Configuration

### Get Agent Model Integration

```javascript
// Get the agent-model integration
const agentModelIntegration = core.agentModelIntegration;
```

### Select Model for Agent

```javascript
// Select model for an agent
const model = agentModelIntegration.selectModelForAgent('agent-1', 'text', {
  minContextWindow: 32000,
  requiredCapabilities: ['reasoning', 'planning']
});

console.log(`Selected model: ${model.id}`);
```

### Execute Model for Agent

```javascript
// Execute model for an agent
const result = await agentModelIntegration.executeModelForAgent('agent-1', 'text', {
  prompt: 'Generate a plan for optimizing a machine learning model.',
  temperature: 0.7,
  max_tokens: 2000
}, {
  requirements: {
    processingPreference: 'cloud'
  }
});

console.log(result.text);
```

### Set Agent Model Preferences

```javascript
// Set agent model preferences
agentModelIntegration.setAgentModelPreferences('agent-1', {
  text: {
    preferredModels: ['claude-3.7-sonnet', 'gpt-4.5', 'llama-3.1-70b'],
    requirements: {
      processingPreference: 'cloud'
    }
  },
  code: {
    preferredModels: ['o3-mini', 'deepseek-coder-v2', 'qwen2-72b-coder'],
    requirements: {
      processingPreference: 'auto'
    }
  }
});
```

## Troubleshooting

### Check Model Availability

```javascript
// Check if a model is available
try {
  const model = modelFramework.getModel('gpt-4.5', 'text');
  console.log(`Model ${model.id} is available`);
} catch (error) {
  console.error(`Model not available: ${error.message}`);
}
```

### Validate Model

```javascript
// Validate a model
const modelValidation = new ModelValidation(core);
const result = await modelValidation.validateModel(
  modelFramework.getModel('gpt-4.5', 'text'),
  { offlineOnly: false }
);

console.log(`Validation status: ${result.status}`);
console.log(`Average latency: ${result.metrics.averageLatency}ms`);
console.log(`Quality score: ${result.metrics.qualityScore}`);
```

### Check Model Metrics

```javascript
// Get model metrics
const metrics = modelFramework.getMetrics();
console.log(`Total requests: ${metrics.totalRequests}`);
console.log(`Successful requests: ${metrics.successfulRequests}`);
console.log(`Failed requests: ${metrics.failedRequests}`);
console.log(`Average latency: ${metrics.averageLatency}ms`);
```

### Debug Mode

```javascript
// Enable debug mode
core.logManager.setLogLevel('debug');

// Execute model with debug logging
const result = await modelFramework.execute('gpt-4.5', 'text', {
  prompt: 'Generate a short paragraph about AI.'
});

// Disable debug mode
core.logManager.setLogLevel('info');
```

### Common Error Solutions

1. **API Key Issues**:
   - Check if API keys are correctly set in the configuration
   - Verify API key permissions and quotas

2. **Model Not Found**:
   - Ensure the model is registered and the provider is initialized
   - Check if the model ID is correct

3. **Local Model Issues**:
   - Verify that model files are downloaded and in the correct location
   - Check file permissions

4. **Network Issues**:
   - Check internet connectivity
   - Verify firewall settings
   - Check if the API endpoint is accessible

5. **Resource Limitations**:
   - Reduce model complexity or token count
   - Use a smaller model
   - Upgrade hardware resources
