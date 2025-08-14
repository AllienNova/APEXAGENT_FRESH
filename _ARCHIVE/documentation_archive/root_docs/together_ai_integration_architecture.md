# Aideon AI Lite + Together AI Integration Architecture

## Executive Summary

After conducting a deep review of the Aideon codebase, I've identified that the system already has a robust provider architecture for integrating LLM services. This document outlines how Together AI should be integrated as a complementary provider within the existing architecture, avoiding duplication of services and maintaining clean architectural principles.

## Existing Architecture Analysis

### Key Components Discovered

1. **Provider Manager System**
   - `ProviderManager` class in `src/llm_providers/provider_manager.py`
   - Handles provider registration, selection, routing, and fallback
   - Maintains health status and model-provider mapping
   - Implements intelligent routing based on availability and latency

2. **Provider Interface**
   - `LLMProvider` abstract base class in `src/llm_providers/core/provider_interface.py`
   - Defines standard interfaces for text, chat, embedding, and image generation
   - Includes both synchronous and asynchronous methods
   - Provides health check and capability reporting mechanisms

3. **Existing Provider Implementations**
   - Multiple provider implementations in `src/plugins/llm_providers/internal/`
   - Includes OpenAI, Anthropic, Gemini, and Ollama providers
   - Each follows the standard interface pattern

## Integration Approach

To avoid duplication and maintain architectural integrity, Together AI should be integrated as a new provider implementation within the existing framework:

### 1. New Provider Implementation

```python
# src/plugins/llm_providers/internal/together_provider.py

from typing import AsyncIterator, List, Optional
import os
import time
import asyncio
from together import Together

from ....llm_providers.core.provider_interface import (
    LLMProvider,
    ProviderType,
    ChatMessage,
    ModelInfo,
    ProviderCapabilities,
    HealthStatus,
    TextGenerationOptions,
    ChatGenerationOptions,
    EmbeddingOptions,
    ImageGenerationOptions,
    TextGenerationResult,
    ChatGenerationResult,
    EmbeddingResult,
    ImageGenerationResult,
    TextGenerationChunk,
    ChatGenerationChunk,
    LLMError,
    LLMErrorType,
    UsageInfo,
    FinishReason
)

class TogetherProvider(LLMProvider):
    """Provider implementation for Together AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Together AI provider."""
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("Together API key is required")
        
        self.client = Together(api_key=self.api_key)
        self._models_cache = None
        self._models_cache_time = 0
        self._models_cache_ttl = 3600  # 1 hour
    
    def get_name(self) -> str:
        """Get provider name."""
        return "Together AI"
    
    def get_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.CUSTOM
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities."""
        return ProviderCapabilities(
            supports_text=True,
            supports_chat=True,
            supports_embeddings=True,
            supports_images=True,
            supports_streaming=True,
            supports_functions=True,
            supports_vision=True,
            supports_audio=False
        )
    
    def get_health(self) -> HealthStatus:
        """Get provider health status."""
        try:
            # Simple health check - just verify API connectivity
            start_time = time.time()
            models = self.client.models.list()
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            return HealthStatus(
                available=True,
                latency=latency,
                error_rate=0.0,
                message="Together AI is available"
            )
        except Exception as e:
            return HealthStatus(
                available=False,
                latency=0.0,
                error_rate=1.0,
                message=f"Together AI is unavailable: {str(e)}"
            )
    
    async def get_health_async(self) -> HealthStatus:
        """Get provider health status asynchronously."""
        return await asyncio.to_thread(self.get_health)
    
    def get_models(self) -> List[ModelInfo]:
        """Get information about available models."""
        current_time = time.time()
        if self._models_cache and current_time - self._models_cache_time < self._models_cache_ttl:
            return self._models_cache
        
        try:
            models_data = self.client.models.list()
            result = []
            
            for model_data in models_data:
                # Map Together AI model data to ModelInfo
                model_info = ModelInfo(
                    id=f"together/{model_data['name']}",  # Prefixed with provider name
                    provider_model_id=model_data['name'],
                    provider="together",
                    capabilities=self._get_model_capabilities(model_data),
                    max_tokens=model_data.get('context_length', 4096),
                    cost_per_input_token=model_data.get('pricing', {}).get('input', 0.0),
                    cost_per_output_token=model_data.get('pricing', {}).get('output', 0.0)
                )
                result.append(model_info)
            
            self._models_cache = result
            self._models_cache_time = current_time
            return result
        except Exception as e:
            raise LLMError(
                f"Failed to get models: {str(e)}",
                LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                "together",
                retryable=True,
                original_error=e
            )
    
    async def get_models_async(self) -> List[ModelInfo]:
        """Get information about available models asynchronously."""
        return await asyncio.to_thread(self.get_models)
    
    def _get_model_capabilities(self, model_data: dict) -> List[str]:
        """Extract capabilities from model data."""
        capabilities = []
        model_type = model_data.get('type', '').lower()
        
        if 'chat' in model_type:
            capabilities.append('chat')
        if 'text' in model_type or 'completion' in model_type:
            capabilities.append('text')
        if 'embedding' in model_type:
            capabilities.append('embeddings')
        if 'image' in model_type:
            capabilities.append('images')
        if 'vision' in model_type or 'multimodal' in model_type:
            capabilities.append('vision')
        
        return capabilities
    
    def _map_finish_reason(self, together_reason: str) -> FinishReason:
        """Map Together AI finish reason to our standard enum."""
        mapping = {
            "stop": FinishReason.STOP,
            "length": FinishReason.LENGTH,
            "content_filter": FinishReason.CONTENT_FILTER,
            "function_call": FinishReason.FUNCTION_CALL,
            "error": FinishReason.ERROR
        }
        return mapping.get(together_reason, FinishReason.UNKNOWN)
    
    def _extract_usage_info(self, response) -> UsageInfo:
        """Extract usage information from Together AI response."""
        usage = response.get('usage', {})
        return UsageInfo(
            prompt_tokens=usage.get('prompt_tokens', 0),
            completion_tokens=usage.get('completion_tokens', 0),
            total_tokens=usage.get('total_tokens', 0)
        )
    
    def generate_text(
        self, prompt: str, options: TextGenerationOptions
    ) -> TextGenerationResult:
        """Generate text from a prompt."""
        try:
            # Map our options to Together AI parameters
            model_id = options.model
            if model_id.startswith("together/"):
                model_id = model_id[9:]  # Remove "together/" prefix
            
            response = self.client.completions.create(
                model=model_id,
                prompt=prompt,
                max_tokens=options.max_tokens,
                temperature=options.temperature,
                top_p=options.top_p,
                frequency_penalty=options.frequency_penalty,
                presence_penalty=options.presence_penalty,
                stop=options.stop
            )
            
            return TextGenerationResult(
                text=response.choices[0].text,
                model=options.model,
                provider="together",
                usage=self._extract_usage_info(response),
                finish_reason=str(self._map_finish_reason(response.choices[0].finish_reason))
            )
        except Exception as e:
            raise LLMError(
                f"Text generation failed: {str(e)}",
                LLMErrorType.UNKNOWN_ERROR,
                "together",
                retryable=True,
                original_error=e
            )
    
    async def generate_text_async(
        self, prompt: str, options: TextGenerationOptions
    ) -> TextGenerationResult:
        """Generate text from a prompt asynchronously."""
        return await asyncio.to_thread(self.generate_text, prompt, options)
    
    def generate_text_stream(
        self, prompt: str, options: TextGenerationOptions
    ) -> AsyncIterator[TextGenerationChunk]:
        """Generate text from a prompt with streaming response."""
        async def stream_generator():
            try:
                model_id = options.model
                if model_id.startswith("together/"):
                    model_id = model_id[9:]
                
                stream = self.client.completions.create(
                    model=model_id,
                    prompt=prompt,
                    max_tokens=options.max_tokens,
                    temperature=options.temperature,
                    top_p=options.top_p,
                    frequency_penalty=options.frequency_penalty,
                    presence_penalty=options.presence_penalty,
                    stop=options.stop,
                    stream=True
                )
                
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    
                    is_final = chunk.choices[0].finish_reason is not None
                    yield TextGenerationChunk(
                        text=chunk.choices[0].text,
                        finish_reason=str(self._map_finish_reason(chunk.choices[0].finish_reason)) if is_final else None,
                        is_final=is_final
                    )
            except Exception as e:
                raise LLMError(
                    f"Text streaming failed: {str(e)}",
                    LLMErrorType.UNKNOWN_ERROR,
                    "together",
                    retryable=True,
                    original_error=e
                )
        
        return stream_generator()
    
    def generate_chat(
        self, messages: List[ChatMessage], options: ChatGenerationOptions
    ) -> ChatGenerationResult:
        """Generate a chat response from a conversation."""
        try:
            # Convert our messages to Together AI format
            together_messages = []
            for msg in messages:
                together_msg = {
                    "role": msg.role,
                    "content": msg.content
                }
                if msg.name:
                    together_msg["name"] = msg.name
                if msg.function_call:
                    together_msg["function_call"] = msg.function_call
                together_messages.append(together_msg)
            
            # Map our options to Together AI parameters
            model_id = options.model
            if model_id.startswith("together/"):
                model_id = model_id[9:]
            
            # Prepare function calling if needed
            functions = None
            function_call = None
            if options.functions:
                functions = [
                    {
                        "name": func.name,
                        "description": func.description,
                        "parameters": func.parameters
                    }
                    for func in options.functions
                ]
                function_call = options.function_call
            
            response = self.client.chat.completions.create(
                model=model_id,
                messages=together_messages,
                max_tokens=options.max_tokens,
                temperature=options.temperature,
                top_p=options.top_p,
                frequency_penalty=options.frequency_penalty,
                presence_penalty=options.presence_penalty,
                stop=options.stop,
                functions=functions,
                function_call=function_call
            )
            
            # Convert Together AI response to our format
            assistant_msg = response.choices[0].message
            result_message = ChatMessage(
                role=assistant_msg.role,
                content=assistant_msg.content or "",
                function_call=assistant_msg.function_call
            )
            
            return ChatGenerationResult(
                message=result_message,
                model=options.model,
                provider="together",
                usage=self._extract_usage_info(response),
                finish_reason=str(self._map_finish_reason(response.choices[0].finish_reason))
            )
        except Exception as e:
            raise LLMError(
                f"Chat generation failed: {str(e)}",
                LLMErrorType.UNKNOWN_ERROR,
                "together",
                retryable=True,
                original_error=e
            )
    
    async def generate_chat_async(
        self, messages: List[ChatMessage], options: ChatGenerationOptions
    ) -> ChatGenerationResult:
        """Generate a chat response from a conversation asynchronously."""
        return await asyncio.to_thread(self.generate_chat, messages, options)
    
    def generate_chat_stream(
        self, messages: List[ChatMessage], options: ChatGenerationOptions
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Generate a chat response with streaming."""
        async def stream_generator():
            try:
                # Convert our messages to Together AI format
                together_messages = []
                for msg in messages:
                    together_msg = {
                        "role": msg.role,
                        "content": msg.content
                    }
                    if msg.name:
                        together_msg["name"] = msg.name
                    if msg.function_call:
                        together_msg["function_call"] = msg.function_call
                    together_messages.append(together_msg)
                
                # Map our options to Together AI parameters
                model_id = options.model
                if model_id.startswith("together/"):
                    model_id = model_id[9:]
                
                # Prepare function calling if needed
                functions = None
                function_call = None
                if options.functions:
                    functions = [
                        {
                            "name": func.name,
                            "description": func.description,
                            "parameters": func.parameters
                        }
                        for func in options.functions
                    ]
                    function_call = options.function_call
                
                stream = self.client.chat.completions.create(
                    model=model_id,
                    messages=together_messages,
                    max_tokens=options.max_tokens,
                    temperature=options.temperature,
                    top_p=options.top_p,
                    frequency_penalty=options.frequency_penalty,
                    presence_penalty=options.presence_penalty,
                    stop=options.stop,
                    functions=functions,
                    function_call=function_call,
                    stream=True
                )
                
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    
                    delta = chunk.choices[0].delta
                    is_final = chunk.choices[0].finish_reason is not None
                    
                    # Convert delta to our format
                    delta_dict = {}
                    if hasattr(delta, "role") and delta.role:
                        delta_dict["role"] = delta.role
                    if hasattr(delta, "content") and delta.content:
                        delta_dict["content"] = delta.content
                    if hasattr(delta, "function_call") and delta.function_call:
                        delta_dict["function_call"] = delta.function_call
                    
                    yield ChatGenerationChunk(
                        delta=delta_dict,
                        finish_reason=str(self._map_finish_reason(chunk.choices[0].finish_reason)) if is_final else None,
                        is_final=is_final
                    )
            except Exception as e:
                raise LLMError(
                    f"Chat streaming failed: {str(e)}",
                    LLMErrorType.UNKNOWN_ERROR,
                    "together",
                    retryable=True,
                    original_error=e
                )
        
        return stream_generator()
    
    def generate_embedding(
        self, text: str, options: EmbeddingOptions
    ) -> EmbeddingResult:
        """Generate embeddings for text."""
        try:
            model_id = options.model
            if model_id.startswith("together/"):
                model_id = model_id[9:]
            
            response = self.client.embeddings.create(
                model=model_id,
                input=text,
                dimensions=options.dimensions
            )
            
            return EmbeddingResult(
                embedding=response.data[0].embedding,
                model=options.model,
                provider="together",
                usage=UsageInfo(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=0,
                    total_tokens=response.usage.total_tokens
                )
            )
        except Exception as e:
            raise LLMError(
                f"Embedding generation failed: {str(e)}",
                LLMErrorType.UNKNOWN_ERROR,
                "together",
                retryable=True,
                original_error=e
            )
    
    async def generate_embedding_async(
        self, text: str, options: EmbeddingOptions
    ) -> EmbeddingResult:
        """Generate embeddings for text asynchronously."""
        return await asyncio.to_thread(self.generate_embedding, text, options)
    
    def generate_image(
        self, prompt: str, options: ImageGenerationOptions
    ) -> ImageGenerationResult:
        """Generate images from a prompt."""
        try:
            model_id = options.model or "stabilityai/stable-diffusion-xl-base-1.0"
            if model_id.startswith("together/"):
                model_id = model_id[9:]
            
            response = self.client.images.generate(
                model=model_id,
                prompt=prompt,
                n=1,
                size=options.size or "1024x1024",
                response_format="url"
            )
            
            return ImageGenerationResult(
                images=[image.url for image in response.data],
                model=options.model or model_id,
                provider="together"
            )
        except Exception as e:
            raise LLMError(
                f"Image generation failed: {str(e)}",
                LLMErrorType.UNKNOWN_ERROR,
                "together",
                retryable=True,
                original_error=e
            )
    
    async def generate_image_async(
        self, prompt: str, options: ImageGenerationOptions
    ) -> ImageGenerationResult:
        """Generate images from a prompt asynchronously."""
        return await asyncio.to_thread(self.generate_image, prompt, options)
```

### 2. Provider Registration

```python
# src/llm_providers/provider_registration.py

from .provider_manager import ProviderManager
from ..plugins.llm_providers.internal.together_provider import TogetherProvider

def register_together_provider(manager: ProviderManager, api_key: str = None) -> None:
    """
    Register the Together AI provider with the provider manager.
    
    Args:
        manager: The provider manager instance
        api_key: Optional API key (will use environment variable if not provided)
    """
    provider = TogetherProvider(api_key)
    manager.register_provider("together", provider)
```

### 3. Tier-Based Model Selection

```python
# src/subscription/tier_based_model_selector.py

from typing import Dict, List, Optional
from ..llm_providers.provider_manager import ProviderManager

class TierBasedModelSelector:
    """
    Selects appropriate models based on user subscription tier.
    """
    
    def __init__(self, provider_manager: ProviderManager):
        """Initialize the tier-based model selector."""
        self.provider_manager = provider_manager
        self.tier_model_mapping = {
            "free": {
                "text": "together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "chat": "together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "vision": "together/deepseek-ai/DeepSeek-VL-7B-Chat",
                "image": "together/stabilityai/stable-diffusion-xl-base-1.0",
                "embedding": "together/nomic-ai/nomic-embed-text-v1"
            },
            "premium": {
                # Premium tier uses Aideon's primary models
                "text": "anthropic/claude-3-opus",
                "chat": "anthropic/claude-3-opus",
                "vision": "anthropic/claude-3-opus",
                "image": "openai/dall-e-3",
                "embedding": "openai/text-embedding-3-large"
            }
        }
        self.fallback_models = {
            "text": "together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "chat": "together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "vision": "together/deepseek-ai/DeepSeek-VL-7B-Chat",
            "image": "together/stabilityai/stable-diffusion-xl-base-1.0",
            "embedding": "together/nomic-ai/nomic-embed-text-v1"
        }
    
    def get_model_for_tier(self, tier: str, modality: str) -> str:
        """
        Get the appropriate model for the given tier and modality.
        
        Args:
            tier: User subscription tier ('free' or 'premium')
            modality: Type of model ('text', 'chat', 'vision', 'image', 'embedding')
            
        Returns:
            Model ID to use
        """
        if tier not in self.tier_model_mapping:
            tier = "free"  # Default to free tier
        
        if modality not in self.tier_model_mapping[tier]:
            raise ValueError(f"Unsupported modality: {modality}")
        
        return self.tier_model_mapping[tier][modality]
    
    def get_fallback_model(self, modality: str) -> Optional[str]:
        """
        Get a fallback model for the given modality.
        
        Args:
            modality: Type of model ('text', 'chat', 'vision', 'image', 'embedding')
            
        Returns:
            Fallback model ID or None if no fallback is available
        """
        return self.fallback_models.get(modality)
```

### 4. Fallback Mechanism Integration

```python
# src/core/fallback_handler.py

from typing import Any, Dict, List, Optional, Union
from ..llm_providers.provider_manager import ProviderManager
from ..llm_providers.core.provider_interface import (
    ChatMessage,
    TextGenerationOptions,
    ChatGenerationOptions,
    EmbeddingOptions,
    ImageGenerationOptions,
    TextGenerationResult,
    ChatGenerationResult,
    EmbeddingResult,
    ImageGenerationResult,
    LLMError
)
from ..subscription.tier_based_model_selector import TierBasedModelSelector
import logging

logger = logging.getLogger(__name__)

class FallbackHandler:
    """
    Handles fallback logic when primary models fail.
    """
    
    def __init__(
        self,
        provider_manager: ProviderManager,
        model_selector: TierBasedModelSelector
    ):
        """Initialize the fallback handler."""
        self.provider_manager = provider_manager
        self.model_selector = model_selector
    
    def generate_chat_with_fallback(
        self,
        messages: List[ChatMessage],
        options: ChatGenerationOptions,
        tier: str = "premium"
    ) -> ChatGenerationResult:
        """
        Generate a chat response with fallback support.
        
        Args:
            messages: List of chat messages
            options: Chat generation options
            tier: User subscription tier
            
        Returns:
            Generated chat result
        """
        # First try with the tier-appropriate model
        original_model = options.model
        try:
            # If no model specified or using tier-based selection
            if not original_model or original_model == "auto":
                options.model = self.model_selector.get_model_for_tier(tier, "chat")
            
            return self.provider_manager.generate_chat(messages, options)
        except LLMError as e:
            logger.warning(f"Primary model failed: {str(e)}")
            
            # Only attempt fallback for retryable errors or if using premium tier
            if e.retryable or tier == "premium":
                fallback_model = self.model_selector.get_fallback_model("chat")
                if fallback_model:
                    logger.info(f"Attempting fallback with model: {fallback_model}")
                    options.model = fallback_model
                    try:
                        result = self.provider_manager.generate_chat(messages, options)
                        logger.info("Fallback successful")
                        return result
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {str(fallback_error)}")
            
            # Re-raise the original error if fallback failed or wasn't attempted
            raise
```

### 5. Free Tier Integration

```python
# src/subscription/free_tier_manager.py

from typing import Dict, Optional
from ..llm_providers.provider_manager import ProviderManager
from ..subscription.tier_based_model_selector import TierBasedModelSelector

class FreeTierManager:
    """
    Manages free tier access and limitations.
    """
    
    def __init__(
        self,
        provider_manager: ProviderManager,
        model_selector: TierBasedModelSelector
    ):
        """Initialize the free tier manager."""
        self.provider_manager = provider_manager
        self.model_selector = model_selector
        self.free_tier_limits = {
            "daily_requests": 25,
            "max_tokens": 2048,
            "image_generations": 5
        }
    
    def get_free_tier_model(self, modality: str) -> str:
        """
        Get the appropriate model for free tier users.
        
        Args:
            modality: Type of model ('text', 'chat', 'vision', 'image', 'embedding')
            
        Returns:
            Model ID to use for free tier
        """
        return self.model_selector.get_model_for_tier("free", modality)
    
    def apply_free_tier_limits(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply free tier limitations to request options.
        
        Args:
            options: Request options
            
        Returns:
            Modified options with free tier limitations applied
        """
        # Clone options to avoid modifying the original
        limited_options = options.copy()
        
        # Apply token limit
        if "max_tokens" not in limited_options or limited_options["max_tokens"] > self.free_tier_limits["max_tokens"]:
            limited_options["max_tokens"] = self.free_tier_limits["max_tokens"]
        
        return limited_options
    
    def check_quota_available(self, user_id: str, request_type: str) -> bool:
        """
        Check if the user has quota available for the requested operation.
        
        Args:
            user_id: User identifier
            request_type: Type of request ('text', 'chat', 'image', etc.)
            
        Returns:
            True if quota is available, False otherwise
        """
        # Implementation would check a database or cache for user's usage
        # This is a placeholder implementation
        return True
    
    def record_usage(self, user_id: str, request_type: str, tokens_used: int = 0) -> None:
        """
        Record usage for quota tracking.
        
        Args:
            user_id: User identifier
            request_type: Type of request ('text', 'chat', 'image', etc.)
            tokens_used: Number of tokens used in the request
        """
        # Implementation would update a database or cache with user's usage
        # This is a placeholder implementation
        pass
```

## Integration with Existing Components

### 1. Provider Registration in Application Startup

```python
# src/app.py (or equivalent startup file)

from .llm_providers.provider_manager import ProviderManager
from .llm_providers.provider_registration import register_together_provider
from .subscription.tier_based_model_selector import TierBasedModelSelector
from .core.fallback_handler import FallbackHandler
from .subscription.free_tier_manager import FreeTierManager
import os

def initialize_llm_providers():
    """Initialize and register all LLM providers."""
    # Create provider manager
    provider_manager = ProviderManager()
    
    # Register existing providers
    # ...
    
    # Register Together AI provider
    together_api_key = os.environ.get("TOGETHER_API_KEY")
    register_together_provider(provider_manager, together_api_key)
    
    # Create supporting components
    model_selector = TierBasedModelSelector(provider_manager)
    fallback_handler = FallbackHandler(provider_manager, model_selector)
    free_tier_manager = FreeTierManager(provider_manager, model_selector)
    
    return {
        "provider_manager": provider_manager,
        "model_selector": model_selector,
        "fallback_handler": fallback_handler,
        "free_tier_manager": free_tier_manager
    }
```

### 2. API Integration

```python
# src/api/llm_endpoints.py

from fastapi import APIRouter, Depends, HTTPException
from ..auth.user import get_current_user, User
from ..llm_providers.provider_manager import ProviderManager
from ..core.fallback_handler import FallbackHandler
from ..subscription.free_tier_manager import FreeTierManager
from ..subscription.tier_based_model_selector import TierBasedModelSelector
from ..llm_providers.core.provider_interface import (
    ChatMessage,
    ChatGenerationOptions,
    LLMError
)
from typing import List, Dict, Any

router = APIRouter()

# Dependency injection
def get_provider_manager():
    # Implementation to get the provider manager instance
    pass

def get_fallback_handler():
    # Implementation to get the fallback handler instance
    pass

def get_free_tier_manager():
    # Implementation to get the free tier manager instance
    pass

def get_model_selector():
    # Implementation to get the model selector instance
    pass

@router.post("/chat/completions")
async def chat_completions(
    messages: List[Dict[str, Any]],
    options: Dict[str, Any],
    user: User = Depends(get_current_user),
    provider_manager: ProviderManager = Depends(get_provider_manager),
    fallback_handler: FallbackHandler = Depends(get_fallback_handler),
    free_tier_manager: FreeTierManager = Depends(get_free_tier_manager),
    model_selector: TierBasedModelSelector = Depends(get_model_selector)
):
    """Generate a chat completion."""
    try:
        # Convert request messages to internal format
        chat_messages = [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                name=msg.get("name"),
                function_call=msg.get("function_call")
            )
            for msg in messages
        ]
        
        # Determine user tier and apply appropriate model and limits
        tier = user.subscription_tier
        
        # For free tier, use Together AI models and apply limits
        if tier == "free":
            if not free_tier_manager.check_quota_available(user.id, "chat"):
                raise HTTPException(status_code=429, detail="Free tier quota exceeded")
            
            # Apply free tier model and limits
            options["model"] = free_tier_manager.get_free_tier_model("chat")
            options = free_tier_manager.apply_free_tier_limits(options)
        
        # Create options object
        chat_options = ChatGenerationOptions(
            model=options.get("model", "auto"),
            max_tokens=options.get("max_tokens"),
            temperature=options.get("temperature"),
            top_p=options.get("top_p"),
            frequency_penalty=options.get("frequency_penalty"),
            presence_penalty=options.get("presence_penalty"),
            stop=options.get("stop"),
            functions=options.get("functions"),
            function_call=options.get("function_call"),
            provider=options.get("provider")
        )
        
        # Generate response with fallback support
        result = fallback_handler.generate_chat_with_fallback(
            chat_messages, chat_options, tier
        )
        
        # Record usage for free tier
        if tier == "free":
            free_tier_manager.record_usage(
                user.id, "chat", result.usage.total_tokens
            )
        
        # Convert result to API response format
        return {
            "id": f"chatcmpl-{id(result)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": result.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": result.message.role,
                        "content": result.message.content,
                        "function_call": result.message.function_call
                    },
                    "finish_reason": result.finish_reason
                }
            ],
            "usage": {
                "prompt_tokens": result.usage.prompt_tokens,
                "completion_tokens": result.usage.completion_tokens,
                "total_tokens": result.usage.total_tokens
            }
        }
    except LLMError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## UI Integration

```javascript
// src/ui/components/ModelSourceIndicator.js

import React from 'react';

/**
 * Component to indicate the source of the model being used
 * (primary Aideon model or Together AI fallback)
 */
const ModelSourceIndicator = ({ modelId, tier }) => {
  const isTogetherModel = modelId.startsWith('together/');
  const isPrimaryModel = !isTogetherModel;
  
  // For premium tier, Together models are fallbacks
  const isFallback = tier === 'premium' && isTogetherModel;
  
  return (
    <div className={`model-indicator ${isFallback ? 'fallback' : ''}`}>
      {isPrimaryModel ? (
        <span className="primary-model">
          <i className="fa fa-star"></i> Aideon Model
        </span>
      ) : (
        <span className="together-model">
          <i className="fa fa-bolt"></i> Together AI {isFallback ? '(Fallback)' : ''}
        </span>
      )}
    </div>
  );
};

export default ModelSourceIndicator;
```

## Coding Standards and Variable Naming

To maintain clean architecture and prevent bugs, the following coding standards should be applied:

1. **Naming Conventions**
   - Use `snake_case` for variables and functions in Python
   - Use `PascalCase` for classes in Python
   - Use `camelCase` for variables and functions in JavaScript
   - Use `PascalCase` for React components
   - Prefix private methods and variables with underscore (e.g., `_private_method`)

2. **Type Annotations**
   - Use type hints for all Python functions and methods
   - Document parameter and return types in docstrings
   - Use TypeScript for JavaScript code when possible

3. **Error Handling**
   - Use specific exception types rather than generic exceptions
   - Provide detailed error messages with context
   - Include retry logic for transient errors
   - Log errors with appropriate severity levels

4. **Documentation**
   - Include docstrings for all classes and methods
   - Document parameters, return values, and exceptions
   - Provide usage examples for complex functionality
   - Keep documentation up-to-date with code changes

5. **Testing**
   - Write unit tests for all new functionality
   - Include integration tests for provider interactions
   - Mock external API calls in tests
   - Test both success and failure scenarios

## Conclusion

This integration approach ensures that Together AI is seamlessly incorporated into Aideon's existing architecture without duplicating services or creating parallel layers. By implementing Together AI as a provider within the established provider framework, we maintain architectural integrity while enhancing the system with complementary capabilities.

The design supports both the free tier use case (using Together AI models as primary) and the premium tier use case (using Together AI models as fallbacks), all while leveraging the existing provider manager's routing, health checking, and selection capabilities.
