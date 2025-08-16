"""
Azure OpenAI API client for the LLM Providers integration.

This module provides the Azure OpenAI provider implementation for the LLM Providers
integration system, supporting text generation, chat, embeddings, and image generation.
"""

import json
import logging
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple

import requests

from ..core.provider_interface import (
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
from .auth import AzureAuthManager, AzureCredentials

logger = logging.getLogger(__name__)


class AzureOpenAIProvider(LLMProvider):
    """
    Azure OpenAI provider implementation.
    
    This class implements the LLMProvider interface for Azure OpenAI,
    providing access to Azure-hosted OpenAI models for text generation,
    chat, embeddings, and image generation.
    """
    
    def __init__(self, credentials: AzureCredentials):
        """
        Initialize the Azure OpenAI provider.
        
        Args:
            credentials: Azure OpenAI credentials
        """
        self.credentials = credentials
        self.auth_manager = AzureAuthManager(credentials)
        self.endpoint = credentials.endpoint.rstrip('/')
        self.api_version = credentials.api_version
        
        # Model capabilities mapping
        self.model_capabilities = {
            # GPT-4 models
            "gpt-4": [ProviderCapabilities.TEXT, ProviderCapabilities.CHAT],
            "gpt-4-32k": [ProviderCapabilities.TEXT, ProviderCapabilities.CHAT],
            "gpt-4-turbo": [ProviderCapabilities.TEXT, ProviderCapabilities.CHAT, ProviderCapabilities.VISION],
            "gpt-4o": [ProviderCapabilities.TEXT, ProviderCapabilities.CHAT, ProviderCapabilities.VISION],
            
            # GPT-3.5 models
            "gpt-35-turbo": [ProviderCapabilities.TEXT, ProviderCapabilities.CHAT],
            "gpt-35-turbo-16k": [ProviderCapabilities.TEXT, ProviderCapabilities.CHAT],
            
            # Embedding models
            "text-embedding-ada-002": [ProviderCapabilities.EMBEDDING],
            
            # Image generation models
            "dall-e-3": [ProviderCapabilities.IMAGE],
            "dall-e-2": [ProviderCapabilities.IMAGE]
        }
        
        # Model name mapping (Azure deployment name to standard model name)
        self.model_name_mapping = {}
        
        # Initialize model list
        self._models_cache = None
        self._models_cache_timestamp = 0
        self._models_cache_ttl = 300  # 5 minutes
    
    def _make_request(
        self, method: str, path: str, data: Optional[Dict[str, Any]] = None, 
        params: Optional[Dict[str, Any]] = None, stream: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a request to the Azure OpenAI API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (without endpoint)
            data: Request data (for POST, PUT, etc.)
            params: Query parameters
            stream: Whether to stream the response
            
        Returns:
            Response data as dictionary or Response object for streaming
            
        Raises:
            LLMError: If the request fails
        """
        url = f"{self.endpoint}{path}"
        headers = self.auth_manager.get_auth_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                stream=stream
            )
            
            if stream:
                if response.status_code != 200:
                    error_message = f"Azure OpenAI API request failed: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_message = f"{error_message} - {error_data.get('error', {}).get('message', 'Unknown error')}"
                    except:
                        pass
                    
                    raise LLMError(
                        message=error_message,
                        error_type=self._map_http_error_to_llm_error(response.status_code),
                        provider="azure_openai",
                        retryable=response.status_code >= 500 or response.status_code == 429
                    )
                return response
            
            if response.status_code >= 200 and response.status_code < 300:
                if response.content:
                    return response.json()
                return {}
            
            # Handle error response
            error_message = f"Azure OpenAI API request failed: {response.status_code}"
            try:
                error_data = response.json()
                error_message = f"{error_message} - {error_data.get('error', {}).get('message', 'Unknown error')}"
            except:
                pass
            
            raise LLMError(
                message=error_message,
                error_type=self._map_http_error_to_llm_error(response.status_code),
                provider="azure_openai",
                retryable=response.status_code >= 500 or response.status_code == 429
            )
        
        except requests.RequestException as e:
            raise LLMError(
                message=f"Azure OpenAI API request failed: {str(e)}",
                error_type=LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                provider="azure_openai",
                retryable=True
            )
    
    def _map_http_error_to_llm_error(self, status_code: int) -> LLMErrorType:
        """Map HTTP status code to LLMErrorType."""
        if status_code == 400:
            return LLMErrorType.INVALID_REQUEST_ERROR
        elif status_code == 401:
            return LLMErrorType.AUTHENTICATION_ERROR
        elif status_code == 403:
            return LLMErrorType.PERMISSION_ERROR
        elif status_code == 404:
            return LLMErrorType.NOT_FOUND_ERROR
        elif status_code == 429:
            return LLMErrorType.RATE_LIMIT_ERROR
        elif status_code >= 500:
            return LLMErrorType.SERVICE_UNAVAILABLE_ERROR
        else:
            return LLMErrorType.UNKNOWN_ERROR
    
    def _map_finish_reason(self, reason: Optional[str]) -> FinishReason:
        """Map Azure OpenAI finish reason to FinishReason enum."""
        if reason == "stop":
            return FinishReason.STOP
        elif reason == "length":
            return FinishReason.LENGTH
        elif reason == "content_filter":
            return FinishReason.CONTENT_FILTER
        elif reason == "function_call":
            return FinishReason.FUNCTION_CALL
        elif reason == "tool_calls":
            return FinishReason.TOOL_CALLS
        else:
            return FinishReason.OTHER
    
    def _map_chat_message_to_azure(self, message: ChatMessage) -> Dict[str, Any]:
        """Map ChatMessage to Azure OpenAI format."""
        result = {
            "role": message.role,
            "content": message.content
        }
        
        if message.name:
            result["name"] = message.name
        
        if message.function_call:
            result["function_call"] = message.function_call
        
        return result
    
    def _map_azure_message_to_chat_message(self, message: Dict[str, Any]) -> ChatMessage:
        """Map Azure OpenAI message to ChatMessage."""
        return ChatMessage(
            role=message.get("role", "assistant"),
            content=message.get("content", ""),
            name=message.get("name"),
            function_call=message.get("function_call")
        )
    
    def _map_function_to_azure(self, function: Dict[str, Any]) -> Dict[str, Any]:
        """Map function definition to Azure OpenAI format."""
        # Azure OpenAI uses the same format as OpenAI
        return function
    
    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        return ProviderType.AZURE_OPENAI
    
    def get_models(self) -> List[ModelInfo]:
        """
        Get available models from Azure OpenAI.
        
        Returns:
            List of model information
            
        Raises:
            LLMError: If the request fails
        """
        # Check cache first
        current_time = time.time()
        if self._models_cache is not None and current_time - self._models_cache_timestamp < self._models_cache_ttl:
            return self._models_cache
        
        try:
            # Get deployments from Azure OpenAI
            response = self._make_request("GET", "/openai/deployments")
            
            models = []
            for deployment in response.get("data", []):
                model_id = deployment.get("id")
                base_model = deployment.get("model")
                
                # Map deployment name to standard model name for future reference
                self.model_name_mapping[model_id] = base_model
                
                # Determine capabilities based on model type
                capabilities = self.model_capabilities.get(base_model, [])
                if not capabilities:
                    # Default to text and chat for unknown models
                    capabilities = [ProviderCapabilities.TEXT, ProviderCapabilities.CHAT]
                
                models.append(ModelInfo(
                    id=model_id,
                    name=model_id,
                    provider=ProviderType.AZURE_OPENAI,
                    capabilities=capabilities
                ))
            
            # Cache the results
            self._models_cache = models
            self._models_cache_timestamp = current_time
            
            return models
        
        except Exception as e:
            logger.error(f"Failed to get models from Azure OpenAI: {str(e)}")
            raise LLMError(
                message=f"Failed to get models from Azure OpenAI: {str(e)}",
                error_type=LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                provider="azure_openai",
                retryable=True
            )
    
    def get_health(self) -> HealthStatus:
        """
        Get the health status of the Azure OpenAI provider.
        
        Returns:
            Provider health status
        """
        start_time = time.time()
        try:
            # Make a simple request to check health
            self._make_request("GET", "/openai/deployments")
            
            # Calculate latency
            latency = time.time() - start_time
            
            return HealthStatus(
                available=True,
                latency=latency,
                error_rate=0.0,
                message="Azure OpenAI provider is healthy"
            )
        except Exception as e:
            # Calculate latency even for failed requests
            latency = time.time() - start_time
            
            logger.error(f"Azure OpenAI provider health check failed: {str(e)}")
            return HealthStatus(
                available=False,
                latency=latency,
                error_rate=1.0,
                message=f"Azure OpenAI provider is unhealthy: {str(e)}"
            )
    
    def generate_text(
        self, prompt: str, options: TextGenerationOptions
    ) -> TextGenerationResult:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The text prompt
            options: Text generation options
            
        Returns:
            Generated text result
            
        Raises:
            LLMError: If the request fails
        """
        # For Azure OpenAI, we use the chat endpoint with a single user message
        messages = [
            ChatMessage(role="user", content=prompt)
        ]
        
        # Convert to chat options
        chat_options = ChatGenerationOptions(
            model=options.model,
            max_tokens=options.max_tokens,
            temperature=options.temperature,
            top_p=options.top_p,
            frequency_penalty=options.frequency_penalty,
            presence_penalty=options.presence_penalty,
            stop=options.stop,
            provider=options.provider
        )
        
        # Generate chat response
        chat_result = self.generate_chat(messages, chat_options)
        
        # Convert to text result
        return TextGenerationResult(
            text=chat_result.message.content or "",
            model=chat_result.model,
            usage=chat_result.usage,
            finish_reason=chat_result.finish_reason
        )
    
    def generate_chat(
        self, messages: List[ChatMessage], options: ChatGenerationOptions
    ) -> ChatGenerationResult:
        """
        Generate a chat response.
        
        Args:
            messages: List of chat messages
            options: Chat generation options
            
        Returns:
            Generated chat result
            
        Raises:
            LLMError: If the request fails
        """
        # Prepare request data
        request_data = {
            "messages": [self._map_chat_message_to_azure(msg) for msg in messages],
            "temperature": options.temperature if options.temperature is not None else 0.7,
            "top_p": options.top_p if options.top_p is not None else 1.0,
            "n": 1  # Azure OpenAI only supports a single completion for now
        }
        
        if options.max_tokens is not None:
            request_data["max_tokens"] = options.max_tokens
        
        if options.stop is not None:
            request_data["stop"] = options.stop
        
        if options.frequency_penalty is not None:
            request_data["frequency_penalty"] = options.frequency_penalty
        
        if options.presence_penalty is not None:
            request_data["presence_penalty"] = options.presence_penalty
        
        if options.functions:
            request_data["functions"] = [
                self._map_function_to_azure(func) for func in options.functions
            ]
            
            if options.function_call:
                request_data["function_call"] = options.function_call
        
        # Make the API request
        try:
            response = self._make_request(
                "POST",
                f"/openai/deployments/{options.model}/chat/completions",
                data=request_data
            )
            
            # Extract response data
            choice = response.get("choices", [{}])[0]
            message = self._map_azure_message_to_chat_message(choice.get("message", {}))
            finish_reason = self._map_finish_reason(choice.get("finish_reason"))
            
            # Extract usage information
            usage_data = response.get("usage", {})
            usage = UsageInfo(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            return ChatGenerationResult(
                message=message,
                model=options.model,
                usage=usage,
                finish_reason=finish_reason
            )
        
        except LLMError:
            # Re-raise LLMError
            raise
        
        except Exception as e:
            logger.error(f"Failed to generate chat response: {str(e)}")
            raise LLMError(
                message=f"Failed to generate chat response: {str(e)}",
                error_type=LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                provider="azure_openai",
                retryable=True
            )
    
    def generate_embedding(
        self, text: str, options: EmbeddingOptions
    ) -> EmbeddingResult:
        """
        Generate embeddings for text.
        
        Args:
            text: The text to generate embeddings for
            options: Embedding options
            
        Returns:
            Generated embedding result
            
        Raises:
            LLMError: If the request fails
        """
        # Prepare request data
        request_data = {
            "input": text
        }
        
        # Make the API request
        try:
            response = self._make_request(
                "POST",
                f"/openai/deployments/{options.model}/embeddings",
                data=request_data
            )
            
            # Extract embedding data
            data = response.get("data", [{}])[0]
            embedding = data.get("embedding", [])
            
            # Extract usage information
            usage_data = response.get("usage", {})
            usage = UsageInfo(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=0,
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            return EmbeddingResult(
                embedding=embedding,
                model=options.model,
                usage=usage
            )
        
        except LLMError:
            # Re-raise LLMError
            raise
        
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise LLMError(
                message=f"Failed to generate embedding: {str(e)}",
                error_type=LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                provider="azure_openai",
                retryable=True
            )
    
    def generate_image(
        self, prompt: str, options: ImageGenerationOptions
    ) -> ImageGenerationResult:
        """
        Generate images from a prompt.
        
        Args:
            prompt: The text prompt
            options: Image generation options
            
        Returns:
            Generated image result
            
        Raises:
            LLMError: If the request fails
        """
        # Prepare request data
        request_data = {
            "prompt": prompt,
            "n": 1  # Azure OpenAI only supports a single image for now
        }
        
        # Map size to DALL-E format
        if options.size:
            # Convert common formats to DALL-E format
            size_mapping = {
                "small": "256x256",
                "medium": "512x512",
                "large": "1024x1024",
                "square": "1024x1024",
                "portrait": "1024x1792",
                "landscape": "1792x1024"
            }
            
            request_data["size"] = size_mapping.get(options.size.lower(), options.size)
        else:
            # Default to 1024x1024
            request_data["size"] = "1024x1024"
        
        # Add quality if specified
        if options.quality:
            request_data["quality"] = options.quality
        
        # Add style if specified
        if options.style:
            request_data["style"] = options.style
        
        # Make the API request
        try:
            response = self._make_request(
                "POST",
                f"/openai/deployments/{options.model}/images/generations",
                data=request_data
            )
            
            # Extract image data
            data = response.get("data", [])
            images = [item.get("url", "") for item in data]
            
            return ImageGenerationResult(
                images=images,
                model=options.model
            )
        
        except LLMError:
            # Re-raise LLMError
            raise
        
        except Exception as e:
            logger.error(f"Failed to generate image: {str(e)}")
            raise LLMError(
                message=f"Failed to generate image: {str(e)}",
                error_type=LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                provider="azure_openai",
                retryable=True
            )
