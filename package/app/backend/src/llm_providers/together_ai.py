"""
Together AI Provider for the LLM Providers integration.

This module implements the Together AI provider adapter that integrates with
the existing LLM provider system, providing cost-effective AI models while
maintaining compatibility with the established architecture.
"""

import asyncio
import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from dataclasses import dataclass

import aiohttp

from llm_providers.core.provider_interface import (
    LLMProvider,
    ProviderType,
    LLMErrorType,
    FinishReason,
    ChatMessage,
    FunctionDefinition,
    ModelInfo,
    ProviderCapabilities,
    HealthStatus,
    UsageInfo,
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
    LLMError
)

logger = logging.getLogger(__name__)


@dataclass
class TogetherAICredentials:
    """Credentials for Together AI authentication."""
    api_key: str
    base_url: str = "https://api.together.xyz/v1"


class TogetherAIProvider(LLMProvider):
    """
    Together AI provider implementation.
    
    This provider integrates Together AI's cost-effective models into the existing
    LLM provider system, offering significant cost savings while maintaining
    compatibility with the established architecture.
    """
    
    def __init__(self, credentials: TogetherAICredentials):
        """
        Initialize the Together AI provider.
        
        Args:
            credentials: Together AI credentials
        """
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self._models_cache: Optional[List[ModelInfo]] = None
        self._models_cache_time: float = 0
        self._models_cache_ttl: float = 3600  # 1 hour
        
        # Together AI model configurations with cost information
        self.model_configs = {
            # LLM Models
            "meta-llama/Llama-3.1-8B-Instruct-Turbo": {
                "type": "chat",
                "cost_per_1m_tokens": {"input": 0.18, "output": 0.18},
                "max_tokens": 131072,
                "supports_functions": False,
                "supports_streaming": True
            },
            "meta-llama/Llama-3.1-70B-Instruct-Turbo": {
                "type": "chat", 
                "cost_per_1m_tokens": {"input": 0.88, "output": 0.88},
                "max_tokens": 131072,
                "supports_functions": False,
                "supports_streaming": True
            },
            "meta-llama/Llama-3.1-405B-Instruct-Turbo": {
                "type": "chat",
                "cost_per_1m_tokens": {"input": 3.50, "output": 3.50},
                "max_tokens": 131072,
                "supports_functions": False,
                "supports_streaming": True
            },
            "meta-llama/Llama-Vision-Free": {
                "type": "vision",
                "cost_per_1m_tokens": {"input": 0.0, "output": 0.0},
                "max_tokens": 8192,
                "supports_functions": False,
                "supports_streaming": True
            },
            "codellama/CodeLlama-34b-Instruct-hf": {
                "type": "chat",
                "cost_per_1m_tokens": {"input": 0.776, "output": 0.776},
                "max_tokens": 16384,
                "supports_functions": False,
                "supports_streaming": True
            },
            "mistralai/Mixtral-8x7B-Instruct-v0.1": {
                "type": "chat",
                "cost_per_1m_tokens": {"input": 0.6, "output": 0.6},
                "max_tokens": 32768,
                "supports_functions": False,
                "supports_streaming": True
            },
            # Image Generation Models
            "black-forest-labs/FLUX.1-schnell-Free": {
                "type": "image",
                "cost_per_image": 0.0,  # Free
                "max_resolution": "1024x1024",
                "supports_streaming": False
            },
            "black-forest-labs/FLUX.1-dev": {
                "type": "image", 
                "cost_per_image": 0.025,
                "max_resolution": "1024x1024",
                "supports_streaming": False
            },
            # Embedding Models
            "togethercomputer/m2-bert-80M-8k-retrieval": {
                "type": "embedding",
                "cost_per_1m_tokens": {"input": 0.02, "output": 0.0},
                "max_tokens": 8192,
                "embedding_dimensions": 768,
                "supports_streaming": False
            },
            "togethercomputer/m2-bert-80M-32k-retrieval": {
                "type": "embedding",
                "cost_per_1m_tokens": {"input": 0.02, "output": 0.0},
                "max_tokens": 32768,
                "embedding_dimensions": 768,
                "supports_streaming": False
            }
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.credentials.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Together AI API."""
        session = await self._get_session()
        url = f"{self.credentials.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise LLMError(
                        error_type=self._map_http_status_to_error_type(response.status),
                        message=f"Together AI API error: {error_text}",
                        status_code=response.status
                    )
        except aiohttp.ClientError as e:
            raise LLMError(
                error_type=LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                message=f"Network error: {str(e)}"
            )
    
    def _map_http_status_to_error_type(self, status_code: int) -> LLMErrorType:
        """Map HTTP status codes to LLM error types."""
        if status_code == 401:
            return LLMErrorType.AUTHENTICATION_ERROR
        elif status_code == 403:
            return LLMErrorType.AUTHORIZATION_ERROR
        elif status_code == 429:
            return LLMErrorType.RATE_LIMIT_ERROR
        elif status_code == 400:
            return LLMErrorType.INVALID_REQUEST_ERROR
        elif status_code == 404:
            return LLMErrorType.MODEL_NOT_FOUND_ERROR
        elif status_code >= 500:
            return LLMErrorType.SERVICE_UNAVAILABLE_ERROR
        else:
            return LLMErrorType.UNKNOWN_ERROR
    
    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        return ProviderType.CUSTOM
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "Together AI"
    
    async def get_models(self) -> List[ModelInfo]:
        """Get available models from Together AI."""
        # Check cache first
        current_time = time.time()
        if (self._models_cache is not None and 
            current_time - self._models_cache_time < self._models_cache_ttl):
            return self._models_cache
        
        try:
            response = await self._make_request("GET", "/models")
            models = []
            
            for model_data in response.get("data", []):
                model_id = model_data.get("id", "")
                if model_id in self.model_configs:
                    config = self.model_configs[model_id]
                    
                    # Determine capabilities based on model type
                    capabilities = ProviderCapabilities(
                        text_generation=config["type"] in ["chat", "completion"],
                        chat_generation=config["type"] == "chat",
                        embedding_generation=config["type"] == "embedding",
                        image_generation=config["type"] == "image",
                        function_calling=config.get("supports_functions", False),
                        streaming=config.get("supports_streaming", False)
                    )
                    
                    models.append(ModelInfo(
                        id=model_id,
                        name=model_data.get("display_name", model_id),
                        description=f"Together AI {config['type']} model",
                        capabilities=capabilities,
                        context_length=config.get("max_tokens", 4096),
                        cost_per_token=config.get("cost_per_1m_tokens", {}).get("input", 0.0) / 1_000_000
                    ))
            
            # Cache the results
            self._models_cache = models
            self._models_cache_time = current_time
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to get Together AI models: {str(e)}")
            # Return cached models if available, otherwise empty list
            return self._models_cache or []
    
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        models = await self.get_models()
        for model in models:
            if model.id == model_id:
                return model
        return None
    
    async def check_health(self) -> HealthStatus:
        """Check the health of the Together AI service."""
        try:
            # Simple health check by listing models
            await self._make_request("GET", "/models")
            return HealthStatus.HEALTHY
        except Exception as e:
            logger.error(f"Together AI health check failed: {str(e)}")
            return HealthStatus.UNHEALTHY
    
    async def generate_text(
        self,
        prompt: str,
        model_id: str,
        options: Optional[TextGenerationOptions] = None
    ) -> TextGenerationResult:
        """Generate text using Together AI."""
        if options is None:
            options = TextGenerationOptions()
        
        # Convert to chat format for Together AI
        messages = [{"role": "user", "content": prompt}]
        
        request_data = {
            "model": model_id,
            "messages": messages,
            "max_tokens": options.max_tokens or 1024,
            "temperature": options.temperature or 0.7,
            "top_p": options.top_p or 1.0,
            "stream": False
        }
        
        if options.stop_sequences:
            request_data["stop"] = options.stop_sequences
        
        try:
            response = await self._make_request("POST", "/chat/completions", json=request_data)
            
            choice = response["choices"][0]
            content = choice["message"]["content"]
            finish_reason = self._map_finish_reason(choice.get("finish_reason"))
            
            # Calculate usage and cost
            usage = response.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            cost = self._calculate_cost(model_id, input_tokens, output_tokens)
            
            return TextGenerationResult(
                text=content,
                finish_reason=finish_reason,
                usage=UsageInfo(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens
                ),
                cost=cost,
                model_id=model_id,
                provider_name=self.get_provider_name()
            )
            
        except Exception as e:
            logger.error(f"Together AI text generation failed: {str(e)}")
            raise
    
    async def generate_chat(
        self,
        messages: List[ChatMessage],
        model_id: str,
        options: Optional[ChatGenerationOptions] = None
    ) -> ChatGenerationResult:
        """Generate chat response using Together AI."""
        if options is None:
            options = ChatGenerationOptions()
        
        # Convert messages to Together AI format
        api_messages = []
        for msg in messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        request_data = {
            "model": model_id,
            "messages": api_messages,
            "max_tokens": options.max_tokens or 1024,
            "temperature": options.temperature or 0.7,
            "top_p": options.top_p or 1.0,
            "stream": False
        }
        
        if options.stop_sequences:
            request_data["stop"] = options.stop_sequences
        
        try:
            response = await self._make_request("POST", "/chat/completions", json=request_data)
            
            choice = response["choices"][0]
            content = choice["message"]["content"]
            finish_reason = self._map_finish_reason(choice.get("finish_reason"))
            
            # Calculate usage and cost
            usage = response.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            cost = self._calculate_cost(model_id, input_tokens, output_tokens)
            
            return ChatGenerationResult(
                message=ChatMessage(role="assistant", content=content),
                finish_reason=finish_reason,
                usage=UsageInfo(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens
                ),
                cost=cost,
                model_id=model_id,
                provider_name=self.get_provider_name()
            )
            
        except Exception as e:
            logger.error(f"Together AI chat generation failed: {str(e)}")
            raise
    
    async def generate_embedding(
        self,
        text: str,
        model_id: str,
        options: Optional[EmbeddingOptions] = None
    ) -> EmbeddingResult:
        """Generate embeddings using Together AI."""
        request_data = {
            "model": model_id,
            "input": text
        }
        
        try:
            response = await self._make_request("POST", "/embeddings", json=request_data)
            
            embedding_data = response["data"][0]
            embedding = embedding_data["embedding"]
            
            # Calculate usage and cost
            usage = response.get("usage", {})
            input_tokens = usage.get("prompt_tokens", len(text.split()))
            
            cost = self._calculate_embedding_cost(model_id, input_tokens)
            
            return EmbeddingResult(
                embedding=embedding,
                usage=UsageInfo(
                    input_tokens=input_tokens,
                    output_tokens=0,
                    total_tokens=input_tokens
                ),
                cost=cost,
                model_id=model_id,
                provider_name=self.get_provider_name()
            )
            
        except Exception as e:
            logger.error(f"Together AI embedding generation failed: {str(e)}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        model_id: str,
        options: Optional[ImageGenerationOptions] = None
    ) -> ImageGenerationResult:
        """Generate image using Together AI."""
        # Placeholder for image generation logic
        raise NotImplementedError("Image generation not yet implemented for Together AI")

    def _map_finish_reason(self, finish_reason: Optional[str]) -> FinishReason:
        """Map Together AI finish reasons to common FinishReason enum."""
        if finish_reason == "stop":
            return FinishReason.STOP
        elif finish_reason == "length":
            return FinishReason.LENGTH
        elif finish_reason == "content_filter":
            return FinishReason.CONTENT_FILTER
        else:
            return FinishReason.UNKNOWN

    def _calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost for text/chat generation."""
        config = self.model_configs.get(model_id)
        if not config or "cost_per_1m_tokens" not in config:
            return 0.0

        input_cost = (input_tokens / 1_000_000) * config["cost_per_1m_tokens"].get("input", 0.0)
        output_cost = (output_tokens / 1_000_000) * config["cost_per_1m_tokens"].get("output", 0.0)
        return input_cost + output_cost

    def _calculate_embedding_cost(self, model_id: str, input_tokens: int) -> float:
        """Calculate the cost for embedding generation."""
        config = self.model_configs.get(model_id)
        if not config or "cost_per_1m_tokens" not in config:
            return 0.0

        return (input_tokens / 1_000_000) * config["cost_per_1m_tokens"].get("input", 0.0)

    def _calculate_image_cost(self, model_id: str, num_images: int) -> float:
        """Calculate the cost for image generation."""
        config = self.model_configs.get(model_id)
        if not config or "cost_per_image" not in config:
            return 0.0
        return num_images * config["cost_per_image"]

def create_together_ai_provider(api_key: str) -> TogetherAIProvider:
    """Factory function to create a TogetherAIProvider instance."""
    credentials = TogetherAICredentials(api_key=api_key)
    return TogetherAIProvider(credentials)


