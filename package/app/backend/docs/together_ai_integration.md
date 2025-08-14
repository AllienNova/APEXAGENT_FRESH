# Together AI Integration Documentation

## Overview

This comprehensive documentation covers the integration of Together AI with Aideon AI Lite, providing a complete guide for developers, administrators, and users. The integration enhances Aideon's capabilities by adding complementary models across text, code, vision, image, and audio modalities, enabling a free tier offering, and providing robust fallback options.

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Installation and Setup](#installation-and-setup)
4. [API Reference](#api-reference)
5. [Administration Guide](#administration-guide)
6. [User Guide](#user-guide)
7. [Developer Guide](#developer-guide)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Introduction

Together AI integration enhances Aideon AI Lite by providing access to 100+ open-source models through a unified API. This integration serves two primary purposes:

1. **Free Tier Enablement**: Powers a basic free tier of Aideon with cost-effective models
2. **Enhanced Fallback System**: Provides reliable alternatives when primary models are unavailable

The integration is designed to complement Aideon's existing capabilities rather than replace them, maintaining the core hybrid autonomous AI system vision while expanding accessibility and reliability.

### Key Features

- **Multi-Modal Support**: Text, code, vision, image, and audio capabilities
- **Tier-Based Access**: Different models for free, premium, and enterprise tiers
- **Intelligent Fallbacks**: Automatic switching to alternative models when needed
- **Usage Tracking**: Comprehensive monitoring and quota enforcement
- **Transparent UI**: Clear indicators showing model sources to users

## Architecture

The Together AI integration follows Aideon's existing provider architecture, ensuring clean separation of concerns and avoiding duplication of services or layers.

### Component Overview

1. **TogetherAIProvider**: Core provider implementation following the LLMProvider interface
2. **TogetherAIKeyManager**: Secure API key management for system and user keys
3. **TogetherAIModelSelector**: Tier-based model selection logic
4. **TogetherAIFallbackManager**: Intelligent fallback mechanisms
5. **TogetherAIFreeTierManager**: Free tier feature access and quota enforcement
6. **TogetherAIIndicatorManager**: UI indicators for model sources
7. **TogetherAIUsageTracker**: Usage tracking and reporting
8. **TogetherAIDeploymentAutomation**: Deployment automation and CI/CD

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Aideon AI Lite System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐      ┌─────────────────┐                   │
│  │  Provider       │      │  API            │                   │
│  │  Manager        │◄────►│  Endpoints      │◄─────┐            │
│  └────────┬────────┘      └─────────────────┘      │            │
│           │                                        │            │
│           ▼                                        ▼            │
│  ┌─────────────────┐      ┌─────────────────┐      │            │
│  │  Together AI    │      │  Usage          │      │            │
│  │  Provider       │◄────►│  Tracking       │      │            │
│  └────────┬────────┘      └────────┬────────┘      │            │
│           │                        │               │            │
│           ▼                        ▼               │            │
│  ┌─────────────────┐      ┌─────────────────┐      │            │
│  │  Model          │      │  Free Tier      │      │            │
│  │  Selector       │◄────►│  Manager        │◄─────┘            │
│  └────────┬────────┘      └────────┬────────┘                   │
│           │                        │                            │
│           ▼                        ▼                            │
│  ┌─────────────────┐      ┌─────────────────┐                   │
│  │  Fallback       │      │  UI             │                   │
│  │  Manager        │◄────►│  Indicators     │                   │
│  └─────────────────┘      └─────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. User request comes through API endpoints
2. Request is authenticated and user tier is determined
3. Model selector chooses appropriate model based on tier and purpose
4. Provider executes the request with the selected model
5. If primary model fails, fallback manager tries alternative models
6. Response is returned with appropriate UI indicators
7. Usage is tracked and quotas are enforced

## Installation and Setup

### Prerequisites

- Aideon AI Lite system installed and configured
- Python 3.11 or higher
- Together AI account with API key

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AllienNova/ApexAgent.git
   cd ApexAgent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Together AI API key**:
   
   Through the admin dashboard:
   1. Navigate to Admin Dashboard > API Keys > Together AI
   2. Click "Add System API Key"
   3. Enter your Together AI API key
   4. Click "Save"
   
   Or through environment variables:
   ```bash
   export TOGETHER_AI_API_KEY="your-api-key-here"
   ```

4. **Enable the integration**:
   
   Through the admin dashboard:
   1. Navigate to Admin Dashboard > Feature Flags
   2. Enable "together_ai_integration"
   3. Enable "together_ai_free_tier" if desired
   
   Or through configuration file:
   ```python
   # config/feature_flags.py
   FEATURE_FLAGS = {
       "together_ai_integration": True,
       "together_ai_free_tier": True
   }
   ```

5. **Deploy the integration**:
   ```bash
   ./scripts/deploy_together_ai.sh --environment development
   ```

### Configuration Options

#### Tier-Based Model Configuration

```python
# Default tier-based model configuration
TIER_MODEL_CONFIG = {
    "free": {
        "text": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "code": "Nexusflow/NexusRaven-V2-13B",
        "vision": "Qwen/Qwen-VL-Chat",
        "image": "stabilityai/sdxl-turbo",
        "audio_tts": "cartesia/Sonic-English",
        "audio_stt": "openai/whisper-large-v3"
    },
    "premium": {
        "text": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "code": "deepseek-ai/deepseek-coder-33b-instruct",
        "vision": "deepseek-ai/deepseek-vl-7b-chat",
        "image": "stabilityai/stable-diffusion-xl-base-1.0",
        "audio_tts": "cartesia/Sonic-English-Plus",
        "audio_stt": "openai/whisper-large-v3"
    },
    "enterprise": {
        "text": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "code": "deepseek-ai/deepseek-coder-33b-instruct",
        "vision": "deepseek-ai/deepseek-vl-7b-chat",
        "image": "stabilityai/stable-diffusion-xl-base-1.0",
        "audio_tts": "cartesia/Sonic-English-Plus",
        "audio_stt": "openai/whisper-large-v3"
    }
}
```

#### Free Tier Quotas

```python
# Default free tier quotas
FREE_TIER_QUOTAS = {
    "text_generation": {
        "requests_per_day": 50,
        "tokens_per_day": 10000,
        "tokens_per_request": 2000
    },
    "code_generation": {
        "requests_per_day": 30,
        "tokens_per_day": 15000,
        "tokens_per_request": 3000
    },
    "image_generation": {
        "requests_per_day": 10
    },
    "vision_analysis": {
        "requests_per_day": 20
    },
    "audio_tts": {
        "requests_per_day": 10,
        "minutes_per_day": 5
    },
    "audio_stt": {
        "requests_per_day": 10,
        "minutes_per_day": 10
    }
}
```

## API Reference

### Endpoints

#### Model Listing

```
GET /api/v1/together/models
```

Returns a list of available models for the authenticated user based on their tier.

**Parameters:**
- `modality` (optional): Filter by modality (text, code, vision, image, audio_tts, audio_stt)

**Response:**
```json
{
  "models": [
    {
      "id": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
      "name": "Llama 3.1 8B Instruct",
      "modality": "text",
      "indicator": {
        "provider_id": "together_ai",
        "display_name": "Together AI",
        "is_free_tier": true,
        "is_fallback": false
      }
    },
    ...
  ],
  "user_tier": "free",
  "free_tier_enabled": true
}
```

#### Text Completion

```
POST /api/v1/together/text/completions
```

Generates text completions.

**Request Body:**
```json
{
  "prompt": "Write a poem about artificial intelligence",
  "max_tokens": 256,
  "temperature": 0.7,
  "purpose": "creative",
  "stream": false
}
```

**Response:**
```json
{
  "text": "In silicon dreams and digital streams,\nAI awakens with thoughtful gleams...",
  "usage": {
    "prompt_tokens": 7,
    "completion_tokens": 50,
    "total_tokens": 57
  },
  "model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
  "provider": "together_ai",
  "model_source_indicator": {
    "provider_id": "together_ai",
    "display_name": "Together AI",
    "is_free_tier": true,
    "is_fallback": false
  }
}
```

#### Chat Completion

```
POST /api/v1/together/chat/completions
```

Generates chat completions.

**Request Body:**
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is artificial intelligence?"}
  ],
  "max_tokens": 256,
  "temperature": 0.7,
  "purpose": "educational",
  "stream": false
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "Artificial intelligence (AI) refers to the simulation of human intelligence in machines..."
  },
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 75,
    "total_tokens": 100
  },
  "model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
  "provider": "together_ai",
  "model_source_indicator": {
    "provider_id": "together_ai",
    "display_name": "Together AI",
    "is_free_tier": true,
    "is_fallback": false
  }
}
```

#### Code Completion

```
POST /api/v1/together/code/completions
```

Generates code completions.

**Request Body:**
```json
{
  "prompt": "def fibonacci(n):",
  "max_tokens": 512,
  "temperature": 0.2,
  "purpose": "coding",
  "language": "python",
  "stream": false
}
```

**Response:**
```json
{
  "text": "    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
  "usage": {
    "prompt_tokens": 4,
    "completion_tokens": 30,
    "total_tokens": 34
  },
  "model_id": "Nexusflow/NexusRaven-V2-13B",
  "provider": "together_ai",
  "model_source_indicator": {
    "provider_id": "together_ai",
    "display_name": "Together AI",
    "is_free_tier": true,
    "is_fallback": false
  }
}
```

#### Image Generation

```
POST /api/v1/together/images/generations
```

Generates images.

**Request Body:**
```json
{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blurry, distorted",
  "width": 1024,
  "height": 1024,
  "num_inference_steps": 50,
  "purpose": "creative"
}
```

**Response:**
```json
{
  "url": "https://storage.aideon.ai/images/generated/12345.png",
  "model_id": "stabilityai/sdxl-turbo",
  "provider": "together_ai",
  "model_source_indicator": {
    "provider_id": "together_ai",
    "display_name": "Together AI",
    "is_free_tier": true,
    "is_fallback": false
  }
}
```

#### Image Analysis

```
POST /api/v1/together/images/analysis
```

Analyzes images.

**Request Body:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "prompt": "Describe what you see in this image",
  "max_tokens": 256,
  "purpose": "analysis"
}
```

**Response:**
```json
{
  "text": "The image shows a mountain landscape at sunset. The sky is painted with vibrant orange and purple hues...",
  "model_id": "Qwen/Qwen-VL-Chat",
  "provider": "together_ai",
  "model_source_indicator": {
    "provider_id": "together_ai",
    "display_name": "Together AI",
    "is_free_tier": true,
    "is_fallback": false
  }
}
```

#### Audio Transcription

```
POST /api/v1/together/audio/transcriptions
```

Transcribes audio.

**Request Body:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "language": "en",
  "purpose": "transcription"
}
```

**Response:**
```json
{
  "text": "Welcome to Aideon AI Lite, the world's first truly hybrid autonomous AI system.",
  "model_id": "openai/whisper-large-v3",
  "provider": "together_ai",
  "model_source_indicator": {
    "provider_id": "together_ai",
    "display_name": "Together AI",
    "is_free_tier": true,
    "is_fallback": false
  }
}
```

#### Text to Speech

```
POST /api/v1/together/audio/speech
```

Converts text to speech.

**Request Body:**
```json
{
  "text": "Welcome to Aideon AI Lite, the world's first truly hybrid autonomous AI system.",
  "voice": "default",
  "purpose": "tts"
}
```

**Response:**
```json
{
  "audio_url": "https://storage.aideon.ai/audio/generated/12345.mp3",
  "model_id": "cartesia/Sonic-English",
  "provider": "together_ai",
  "model_source_indicator": {
    "provider_id": "together_ai",
    "display_name": "Together AI",
    "is_free_tier": true,
    "is_fallback": false
  }
}
```

#### Quota Information

```
GET /api/v1/together/quota
```

Returns quota information for the authenticated user.

**Response:**
```json
{
  "text_generation": {
    "requests_used": 10,
    "requests_limit": 50,
    "tokens_used": 2500,
    "tokens_limit": 10000
  },
  "code_generation": {
    "requests_used": 5,
    "requests_limit": 30,
    "tokens_used": 1500,
    "tokens_limit": 15000
  },
  "image_generation": {
    "requests_used": 2,
    "requests_limit": 10
  },
  "vision_analysis": {
    "requests_used": 3,
    "requests_limit": 20
  },
  "audio_tts": {
    "requests_used": 1,
    "requests_limit": 10,
    "minutes_used": 0.5,
    "minutes_limit": 5
  },
  "audio_stt": {
    "requests_used": 1,
    "requests_limit": 10,
    "minutes_used": 1.2,
    "minutes_limit": 10
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions or quota exceeded |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit or quota exceeded |
| 500 | Internal Server Error - Server-side error |

## Administration Guide

### API Key Management

#### System API Key

The system API key is used as a fallback when users don't provide their own API keys. It's managed exclusively through the admin dashboard.

1. Navigate to Admin Dashboard > API Keys > Together AI
2. Click "Add System API Key"
3. Enter your Together AI API key
4. Click "Save"

To rotate the system API key:
1. Navigate to Admin Dashboard > API Keys > Together AI
2. Click "Rotate System API Key"
3. Enter the new API key
4. Click "Save"

#### User API Keys

Users can provide their own Together AI API keys to reduce their monthly charges by 10% and avoid consuming credits for operations using those keys.

To enable user API key management:
1. Navigate to Admin Dashboard > Settings > API Keys
2. Enable "Allow User API Keys for Together AI"
3. Click "Save"

### Feature Flags

The integration uses feature flags to control functionality:

| Flag | Description |
|------|-------------|
| together_ai_integration | Master switch for the entire integration |
| together_ai_free_tier | Controls free tier access |
| together_ai_fallback | Controls fallback functionality |
| together_ai_ui_indicators | Controls UI indicators for model sources |

To manage feature flags:
1. Navigate to Admin Dashboard > Feature Flags
2. Toggle the desired flags
3. Click "Save"

### Quota Management

Administrators can adjust free tier quotas:

1. Navigate to Admin Dashboard > Quotas > Free Tier
2. Adjust quotas for each feature
3. Click "Save"

Custom quotas can be set for specific users:
1. Navigate to Admin Dashboard > Users
2. Select a user
3. Click "Custom Quotas"
4. Adjust quotas for each feature
5. Click "Save"

### Usage Monitoring

Monitor usage across the system:
1. Navigate to Admin Dashboard > Analytics > Usage
2. Select date range and filters
3. View usage charts and tables

Export usage data:
1. Navigate to Admin Dashboard > Analytics > Usage
2. Click "Export Data"
3. Select format (CSV, JSON, Excel)
4. Click "Download"

### Deployment

#### Automated Deployment

Use the deployment script:
```bash
./scripts/deploy_together_ai.sh --environment [development|staging|production]
```

Or trigger GitHub Actions workflow:
1. Navigate to GitHub repository
2. Go to Actions > Together AI Integration CI/CD
3. Click "Run workflow"
4. Select environment
5. Click "Run workflow"

#### Manual Deployment

1. Build the package:
   ```bash
   mkdir -p dist
   zip -r dist/together_ai_integration.zip src/plugins/llm_providers/internal/together_ai_provider.py src/api_key_management/together_ai_*.py src/api/together_ai_endpoints.py tests/test_together_ai_integration.py
   ```

2. Deploy the package:
   ```bash
   curl -X POST \
     -H "Authorization: Bearer $API_KEY" \
     -H "Content-Type: multipart/form-data" \
     -F "package=@dist/together_ai_integration.zip" \
     -F "environment=development" \
     $API_URL/admin/deploy
   ```

## User Guide

### Free Tier Access

The free tier provides access to basic AI capabilities powered by Together AI models:

- **Text Generation**: Up to 50 requests per day, 10,000 tokens total
- **Code Generation**: Up to 30 requests per day, 15,000 tokens total
- **Image Generation**: Up to 10 images per day
- **Vision Analysis**: Up to 20 analyses per day
- **Text-to-Speech**: Up to 10 requests per day, 5 minutes total
- **Speech-to-Text**: Up to 10 requests per day, 10 minutes total

### Model Source Indicators

When using the system, you'll notice indicators showing the source of the model being used:

- **Together AI**: Indicates the response was generated by a Together AI model
- **Free Tier**: Indicates you're using a free tier model
- **Fallback**: Indicates a fallback model was used due to issues with the primary model

### Using Your Own API Keys

To use your own Together AI API key:

1. Create an account at [Together AI](https://www.together.ai/)
2. Generate an API key
3. Navigate to User Settings > API Keys
4. Click "Add API Key"
5. Select "Together AI" from the dropdown
6. Enter your API key
7. Click "Save"

Benefits of using your own API key:
- 10% reduction in monthly charges
- Operations don't consume credits from your allocation
- Access to all models you've enabled in your Together AI account

### Quota Management

Monitor your quota usage:
1. Navigate to User Dashboard > Quota
2. View current usage and limits

Request quota increase:
1. Navigate to User Dashboard > Quota
2. Click "Request Increase"
3. Select feature and desired quota
4. Click "Submit Request"

### Best Practices

- **Text Generation**: Be specific in your prompts for better results
- **Code Generation**: Include language and context for more accurate code
- **Image Generation**: Use detailed descriptions and negative prompts
- **Vision Analysis**: Ask specific questions about the image
- **Audio Processing**: Use clear audio files for better transcription

## Developer Guide

### Provider Implementation

The `TogetherAIProvider` class implements the `LLMProvider` interface:

```python
from src.llm_providers.core.provider_interface import LLMProvider, LLMError, LLMErrorType

class TogetherAIProvider(LLMProvider):
    """Together AI provider implementation."""
    
    def __init__(self, api_key: str):
        """Initialize the provider with API key."""
        self.api_key = api_key
        self.base_url = "https://api.together.xyz/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "together_ai"
    
    def get_supported_models(self) -> List[str]:
        """Get supported models."""
        return [
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            # ... other models
        ]
    
    async def generate_completion(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text completion."""
        # Implementation details
    
    async def generate_chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completion."""
        # Implementation details
    
    # ... other methods
```

### Integration with Existing Code

To use the Together AI provider in your code:

```python
from src.api_key_management.together_ai_model_selector import get_together_ai_model_selector, ModelModality

async def generate_text(user_id: str, prompt: str):
    # Get model selector
    model_selector = get_together_ai_model_selector()
    
    # Get provider with model
    result = model_selector.get_provider_with_model(
        user_id=user_id,
        modality=ModelModality.TEXT
    )
    
    if result.get("error"):
        return {"error": result["error"]}
    
    provider = result["provider"]
    model_id = result["model_id"]
    
    # Generate text
    response = await provider.generate_completion(
        model=model_id,
        prompt=prompt
    )
    
    return response
```

### Fallback Implementation

To implement fallbacks in your code:

```python
from src.api_key_management.together_ai_fallback import get_together_ai_fallback_manager, FallbackStrategy

async def generate_with_fallback(user_id: str, prompt: str):
    # Get fallback manager
    fallback_manager = get_together_ai_fallback_manager()
    
    # Define operation
    async def text_operation(provider, model_id, input_data):
        return await provider.generate_completion(
            model=model_id,
            prompt=input_data
        )
    
    # Execute with fallback
    result = await fallback_manager.execute_with_fallback(
        user_id=user_id,
        modality=ModelModality.TEXT,
        operation=text_operation,
        input_data=prompt,
        fallback_strategies=[
            FallbackStrategy.SAME_PROVIDER_DIFFERENT_MODEL,
            FallbackStrategy.DIFFERENT_PROVIDER,
            FallbackStrategy.CACHED_RESPONSE
        ]
    )
    
    return result
```

### Custom Model Selection

To implement custom model selection logic:

```python
from src.api_key_management.together_ai_model_selector import get_together_ai_model_selector, ModelPurpose

def get_model_for_specific_purpose(user_id: str, purpose: str):
    # Get model selector
    model_selector = get_together_ai_model_selector()
    
    # Map string purpose to enum
    purpose_enum = None
    try:
        purpose_enum = ModelPurpose(purpose)
    except ValueError:
        purpose_enum = ModelPurpose.GENERAL
    
    # Get model for purpose
    model_id = model_selector.get_model_for_user(
        user_id=user_id,
        modality=ModelModality.TEXT,
        purpose=purpose_enum
    )
    
    return model_id
```

### Testing

Run the comprehensive test suite:

```bash
python -m unittest tests/test_together_ai_integration.py
```

Write your own tests:

```python
import unittest
from unittest import mock
from src.plugins.llm_providers.internal.together_ai_provider import TogetherAIProvider

class TestMyIntegration(unittest.TestCase):
    def setUp(self):
        self.provider = TogetherAIProvider(api_key="test_key")
    
    @mock.patch("src.plugins.llm_providers.internal.together_ai_provider.requests.post")
    def test_my_feature(self, mock_post):
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response
        
        # Test your feature
        # ...
        
        self.assertEqual(result, expected)
```

## Troubleshooting

### Common Issues

#### API Key Issues

**Symptom**: "Authentication failed" or "Invalid API key" errors

**Solutions**:
1. Verify the API key is correct in the admin dashboard
2. Check if the API key has been rotated or expired
3. Ensure the API key has the necessary permissions
4. Check if the Together AI account has billing information set up

#### Quota Exceeded

**Symptom**: "Quota exceeded" errors

**Solutions**:
1. Check current quota usage in the user dashboard
2. Request a quota increase if needed
3. Upgrade to a higher tier for increased quotas
4. Use your own API key to avoid consuming credits

#### Model Unavailable

**Symptom**: "Model not available" errors

**Solutions**:
1. Check if the model is supported by Together AI
2. Verify the model is enabled for your tier
3. Check if the model is temporarily unavailable
4. Try a different model or wait for the model to become available

#### Slow Response Times

**Symptom**: Requests take a long time to complete

**Solutions**:
1. Check network connectivity
2. Try a smaller model for faster responses
3. Reduce the number of tokens requested
4. Check Together AI status page for service issues

### Logging and Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("src.plugins.llm_providers.internal.together_ai_provider").setLevel(logging.DEBUG)
```

View logs:

```bash
tail -f logs/together_ai.log
```

### Support Resources

- **Documentation**: [https://docs.aideon.ai/together-ai-integration](https://docs.aideon.ai/together-ai-integration)
- **Together AI Status**: [https://status.together.ai](https://status.together.ai)
- **Support Email**: support@aideon.ai
- **Community Forum**: [https://community.aideon.ai/together-ai](https://community.aideon.ai/together-ai)

## FAQ

### General Questions

**Q: What is Together AI?**
A: Together AI is a platform that provides access to 100+ open-source models through a unified API, including models from Meta, Mistral, DeepSeek, and more.

**Q: How does Together AI integration benefit Aideon?**
A: It enables a free tier offering, provides fallback options for improved reliability, and expands the range of available models across multiple modalities.

**Q: Does Together AI replace existing models in Aideon?**
A: No, Together AI complements existing models rather than replacing them, maintaining Aideon's core hybrid autonomous AI system vision.

### Technical Questions

**Q: Which models are available through Together AI?**
A: Over 100 models including Llama 3.1, Mixtral, DeepSeek, Qwen, Stable Diffusion, and more. The full list is available at [https://docs.together.ai/docs/inference-models](https://docs.together.ai/docs/inference-models).

**Q: How are models selected for different tiers?**
A: Models are selected based on capabilities, performance, and cost. Free tier uses smaller, cost-effective models, while premium tiers use larger, more powerful models.

**Q: How does the fallback system work?**
A: When a primary model fails, the system automatically tries alternative models based on configured fallback strategies, ensuring reliable service even during outages.

### Pricing and Quotas

**Q: What are the free tier limits?**
A: Free tier includes 50 text requests, 30 code requests, 10 image generations, 20 vision analyses, 10 TTS requests, and 10 STT requests per day.

**Q: Can I increase my free tier quotas?**
A: Free tier quotas are fixed, but you can upgrade to premium tiers for higher limits or use your own API key to avoid consuming credits.

**Q: How do I use my own Together AI API key?**
A: Create an account at Together AI, generate an API key, and add it to your user settings in Aideon. This reduces your monthly charges by 10% and operations don't consume credits from your allocation.

### Troubleshooting

**Q: What should I do if I get "Quota exceeded" errors?**
A: Check your current quota usage in the user dashboard, request a quota increase, upgrade to a higher tier, or use your own API key.

**Q: How can I tell which model was used for a response?**
A: Look for the model source indicator in the response, which shows the provider, model name, and whether it's a free tier or fallback model.

**Q: What happens if Together AI is temporarily unavailable?**
A: The system will automatically fall back to alternative providers if configured, ensuring continued service availability.
