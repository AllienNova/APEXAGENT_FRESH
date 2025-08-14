"""
AWS Bedrock API client for the LLM Providers integration.

This module implements the API client for AWS Bedrock, handling all API calls
and transformations between the common interface and AWS Bedrock's specific formats.
"""

import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional, Union, cast

import boto3
from botocore.exceptions import ClientError, ConnectionError, HTTPClientError, ReadTimeoutError

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
from .auth import AWSAuthManager, AWSCredentials

logger = logging.getLogger(__name__)


# Model ID mappings
BEDROCK_MODEL_MAPPINGS = {
    # Claude 3 models
    "claude-3-opus": "anthropic.claude-3-opus-20240229-v1:0",
    "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    
    # Claude 2 models
    "claude-2": "anthropic.claude-v2:1",
    "claude-2.0": "anthropic.claude-v2:1",
    "claude-2.1": "anthropic.claude-v2:1",
    "claude-instant": "anthropic.claude-instant-v1",
    
    # Amazon Titan models
    "titan-text": "amazon.titan-text-express-v1",
    "titan-text-express": "amazon.titan-text-express-v1",
    "titan-text-lite": "amazon.titan-text-lite-v1",
    "titan-embeddings": "amazon.titan-embed-text-v1",
    "titan-image-generator": "amazon.titan-image-generator-v1",
    
    # AI21 Jurassic models
    "jurassic-2": "ai21.j2-mid-v1",
    "jurassic-2-mid": "ai21.j2-mid-v1",
    "jurassic-2-ultra": "ai21.j2-ultra-v1",
    
    # Cohere models
    "command": "cohere.command-text-v14",
    "command-light": "cohere.command-light-text-v14",
    "command-r": "cohere.command-r-v1:0",
    "command-r-plus": "cohere.command-r-plus-v1:0",
    "embed": "cohere.embed-english-v3",
    "embed-english": "cohere.embed-english-v3",
    "embed-multilingual": "cohere.embed-multilingual-v3",
    
    # Stability AI models
    "stable-diffusion": "stability.stable-diffusion-xl-v1",
    "stable-diffusion-xl": "stability.stable-diffusion-xl-v1",
    "stable-diffusion-3": "stability.stable-diffusion-3-v1:0",
}

# Reverse mapping for model IDs
BEDROCK_MODEL_REVERSE_MAPPINGS = {v: k for k, v in BEDROCK_MODEL_MAPPINGS.items()}

# Model capabilities
BEDROCK_MODEL_CAPABILITIES = {
    # Claude models
    "anthropic.claude-3-opus-20240229-v1:0": ["text", "chat", "vision", "functions"],
    "anthropic.claude-3-sonnet-20240229-v1:0": ["text", "chat", "vision", "functions"],
    "anthropic.claude-3-haiku-20240307-v1:0": ["text", "chat", "vision", "functions"],
    "anthropic.claude-v2:1": ["text", "chat"],
    "anthropic.claude-instant-v1": ["text", "chat"],
    
    # Amazon Titan models
    "amazon.titan-text-express-v1": ["text", "chat"],
    "amazon.titan-text-lite-v1": ["text", "chat"],
    "amazon.titan-embed-text-v1": ["embeddings"],
    "amazon.titan-image-generator-v1": ["image"],
    
    # AI21 Jurassic models
    "ai21.j2-mid-v1": ["text"],
    "ai21.j2-ultra-v1": ["text"],
    
    # Cohere models
    "cohere.command-text-v14": ["text", "chat"],
    "cohere.command-light-text-v14": ["text", "chat"],
    "cohere.command-r-v1:0": ["text", "chat"],
    "cohere.command-r-plus-v1:0": ["text", "chat"],
    "cohere.embed-english-v3": ["embeddings"],
    "cohere.embed-multilingual-v3": ["embeddings"],
    
    # Stability AI models
    "stability.stable-diffusion-xl-v1": ["image"],
    "stability.stable-diffusion-3-v1:0": ["image"],
}

# Token cost estimates (per 1000 tokens)
BEDROCK_MODEL_COSTS = {
    # Claude 3 models
    "anthropic.claude-3-opus-20240229-v1:0": {"input": 15.0, "output": 75.0},
    "anthropic.claude-3-sonnet-20240229-v1:0": {"input": 3.0, "output": 15.0},
    "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.25, "output": 1.25},
    
    # Claude 2 models
    "anthropic.claude-v2:1": {"input": 8.0, "output": 24.0},
    "anthropic.claude-instant-v1": {"input": 1.63, "output": 5.51},
    
    # Amazon Titan models
    "amazon.titan-text-express-v1": {"input": 0.8, "output": 1.2},
    "amazon.titan-text-lite-v1": {"input": 0.3, "output": 0.4},
    "amazon.titan-embed-text-v1": {"input": 0.1, "output": 0.0},
    
    # AI21 Jurassic models
    "ai21.j2-mid-v1": {"input": 1.0, "output": 2.0},
    "ai21.j2-ultra-v1": {"input": 3.0, "output": 15.0},
    
    # Cohere models
    "cohere.command-text-v14": {"input": 1.0, "output": 2.0},
    "cohere.command-light-text-v14": {"input": 0.3, "output": 0.6},
    "cohere.command-r-v1:0": {"input": 3.0, "output": 15.0},
    "cohere.command-r-plus-v1:0": {"input": 5.0, "output": 25.0},
    "cohere.embed-english-v3": {"input": 0.1, "output": 0.0},
    "cohere.embed-multilingual-v3": {"input": 0.1, "output": 0.0},
}

# Maximum context lengths
BEDROCK_MODEL_MAX_TOKENS = {
    # Claude 3 models
    "anthropic.claude-3-opus-20240229-v1:0": 200000,
    "anthropic.claude-3-sonnet-20240229-v1:0": 200000,
    "anthropic.claude-3-haiku-20240307-v1:0": 200000,
    
    # Claude 2 models
    "anthropic.claude-v2:1": 100000,
    "anthropic.claude-instant-v1": 100000,
    
    # Amazon Titan models
    "amazon.titan-text-express-v1": 8000,
    "amazon.titan-text-lite-v1": 4000,
    
    # AI21 Jurassic models
    "ai21.j2-mid-v1": 8192,
    "ai21.j2-ultra-v1": 8192,
    
    # Cohere models
    "cohere.command-text-v14": 4096,
    "cohere.command-light-text-v14": 4096,
    "cohere.command-r-v1:0": 128000,
    "cohere.command-r-plus-v1:0": 128000,
}


class AWSBedrockProvider(LLMProvider):
    """
    AWS Bedrock provider implementation.
    
    This class implements the LLMProvider interface for AWS Bedrock,
    handling all API calls and transformations between the common interface
    and AWS Bedrock's specific formats.
    """
    
    def __init__(self, auth_manager: Optional[AWSAuthManager] = None, credentials: Optional[AWSCredentials] = None):
        """
        Initialize the AWS Bedrock provider.
        
        Args:
            auth_manager: Optional pre-configured AWS authentication manager
            credentials: Optional AWS credentials to create an auth manager
        """
        if auth_manager:
            self.auth_manager = auth_manager
        elif credentials:
            self.auth_manager = AWSAuthManager(credentials)
        else:
            # Default to environment-based authentication
            self.auth_manager = AWSAuthManager.from_environment()
        
        # Initialize clients
        self.bedrock_client = self.auth_manager.get_bedrock_client()
        self.bedrock_runtime_client = self.auth_manager.get_bedrock_runtime_client()
        
        # Cache for model information
        self._models_cache: Optional[List[ModelInfo]] = None
        self._models_cache_timestamp = 0
        self._models_cache_ttl = 300  # 5 minutes
        
        # Health check cache
        self._health_cache: Optional[HealthStatus] = None
        self._health_cache_timestamp = 0
        self._health_cache_ttl = 60  # 1 minute
        
        logger.info("AWS Bedrock provider initialized")
    
    def _resolve_model_id(self, model: str) -> str:
        """
        Resolve a user-friendly model name to the AWS Bedrock model ID.
        
        Args:
            model: User-friendly model name
            
        Returns:
            AWS Bedrock model ID
            
        Raises:
            LLMError: If the model is not supported
        """
        # Check if it's already a valid Bedrock model ID
        if model.startswith(("anthropic.", "amazon.", "ai21.", "cohere.", "stability.")):
            return model
        
        # Try to map from user-friendly name
        if model in BEDROCK_MODEL_MAPPINGS:
            return BEDROCK_MODEL_MAPPINGS[model]
        
        # If not found, raise an error
        raise LLMError(
            f"Unsupported model: {model}",
            LLMErrorType.MODEL_NOT_FOUND_ERROR,
            "aws_bedrock",
            retryable=False
        )
    
    def _get_provider_for_model(self, model_id: str) -> str:
        """
        Get the provider name for a given model ID.
        
        Args:
            model_id: AWS Bedrock model ID
            
        Returns:
            Provider name (anthropic, amazon, ai21, cohere, stability)
        """
        if model_id.startswith("anthropic."):
            return "anthropic"
        elif model_id.startswith("amazon."):
            return "amazon"
        elif model_id.startswith("ai21."):
            return "ai21"
        elif model_id.startswith("cohere."):
            return "cohere"
        elif model_id.startswith("stability."):
            return "stability"
        else:
            return "unknown"
    
    def _format_anthropic_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Format a prompt for Anthropic Claude models.
        
        Args:
            prompt: The text prompt
            
        Returns:
            Formatted request body for Anthropic Claude
        """
        return {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens_to_sample": 4096,
            "stop_sequences": ["\n\nHuman:"]
        }
    
    def _format_anthropic_messages(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """
        Format chat messages for Anthropic Claude 3 models.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Formatted request body for Anthropic Claude 3
        """
        # Convert to Anthropic message format
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "system":
                # Claude 3 supports system messages directly
                anthropic_messages.append({
                    "role": "system",
                    "content": msg.content
                })
            elif msg.role == "user":
                anthropic_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif msg.role == "assistant":
                anthropic_messages.append({
                    "role": "assistant",
                    "content": msg.content
                })
            elif msg.role == "function":
                # Claude doesn't have a direct function role, so we'll format it as an assistant message
                anthropic_messages.append({
                    "role": "assistant",
                    "content": f"Function {msg.name} returned: {msg.content}"
                })
        
        return {
            "messages": anthropic_messages,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 4096,
            "anthropic_version": "bedrock-2023-05-31"
        }
    
    def _format_titan_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Format a prompt for Amazon Titan models.
        
        Args:
            prompt: The text prompt
            
        Returns:
            Formatted request body for Amazon Titan
        """
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxTokenCount": 4096,
                "stopSequences": []
            }
        }
    
    def _format_titan_messages(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """
        Format chat messages for Amazon Titan models.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Formatted request body for Amazon Titan
        """
        # Convert to a format Titan understands (simple text with role prefixes)
        formatted_text = ""
        
        for msg in messages:
            if msg.role == "system":
                formatted_text += f"System: {msg.content}\n"
            elif msg.role == "user":
                formatted_text += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                formatted_text += f"Assistant: {msg.content}\n"
            elif msg.role == "function":
                formatted_text += f"Function ({msg.name}): {msg.content}\n"
        
        formatted_text += "Assistant: "
        
        return {
            "inputText": formatted_text,
            "textGenerationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxTokenCount": 4096,
                "stopSequences": []
            }
        }
    
    def _format_cohere_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Format a prompt for Cohere models.
        
        Args:
            prompt: The text prompt
            
        Returns:
            Formatted request body for Cohere
        """
        return {
            "prompt": prompt,
            "temperature": 0.7,
            "p": 0.9,
            "max_tokens": 4096,
            "return_likelihoods": "NONE"
        }
    
    def _format_cohere_messages(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """
        Format chat messages for Cohere models.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Formatted request body for Cohere
        """
        # Convert to Cohere chat format
        cohere_messages = []
        
        # Extract system message if present
        system_message = None
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
                break
        
        # Add the rest of the messages
        for msg in messages:
            if msg.role == "system":
                continue  # Already handled
            elif msg.role == "user":
                cohere_messages.append({
                    "role": "USER",
                    "message": msg.content
                })
            elif msg.role == "assistant":
                cohere_messages.append({
                    "role": "CHATBOT",
                    "message": msg.content
                })
            elif msg.role == "function":
                # Cohere doesn't have a function role, so format as user message
                cohere_messages.append({
                    "role": "USER",
                    "message": f"Function {msg.name} returned: {msg.content}"
                })
        
        request = {
            "chat_history": cohere_messages,
            "message": "",  # No current message, we want the model to generate next
            "temperature": 0.7,
            "p": 0.9,
            "max_tokens": 4096
        }
        
        if system_message:
            request["preamble"] = system_message
        
        return request
    
    def _format_ai21_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Format a prompt for AI21 Jurassic models.
        
        Args:
            prompt: The text prompt
            
        Returns:
            Formatted request body for AI21 Jurassic
        """
        return {
            "prompt": prompt,
            "temperature": 0.7,
            "topP": 0.9,
            "maxTokens": 4096,
            "stopSequences": []
        }
    
    def _format_stability_prompt(self, prompt: str, options: ImageGenerationOptions) -> Dict[str, Any]:
        """
        Format a prompt for Stability AI image generation models.
        
        Args:
            prompt: The text prompt
            options: Image generation options
            
        Returns:
            Formatted request body for Stability AI
        """
        # Map size option to width and height
        size_mapping = {
            "1024x1024": (1024, 1024),
            "1024x1792": (1024, 1792),
            "1792x1024": (1792, 1024),
            "square": (1024, 1024),
            "portrait": (1024, 1792),
            "landscape": (1792, 1024)
        }
        
        width, height = size_mapping.get(options.size or "1024x1024", (1024, 1024))
        
        return {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7.0,
            "steps": 30,
            "width": width,
            "height": height
        }
    
    def _parse_anthropic_response(self, response: Dict[str, Any]) -> str:
        """
        Parse the response from Anthropic Claude models.
        
        Args:
            response: Raw response from AWS Bedrock
            
        Returns:
            Generated text
        """
        if "completion" in response:
            return response["completion"]
        elif "content" in response:
            # Claude 3 format
            content = response.get("content", [])
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                return "".join(text_parts)
            return str(content)
        else:
            raise LLMError(
                "Unexpected response format from Anthropic Claude",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
    
    def _parse_titan_response(self, response: Dict[str, Any]) -> str:
        """
        Parse the response from Amazon Titan models.
        
        Args:
            response: Raw response from AWS Bedrock
            
        Returns:
            Generated text
        """
        if "results" in response and len(response["results"]) > 0:
            return response["results"][0].get("outputText", "")
        else:
            raise LLMError(
                "Unexpected response format from Amazon Titan",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
    
    def _parse_cohere_response(self, response: Dict[str, Any]) -> str:
        """
        Parse the response from Cohere models.
        
        Args:
            response: Raw response from AWS Bedrock
            
        Returns:
            Generated text
        """
        if "generations" in response and len(response["generations"]) > 0:
            return response["generations"][0].get("text", "")
        else:
            raise LLMError(
                "Unexpected response format from Cohere",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
    
    def _parse_ai21_response(self, response: Dict[str, Any]) -> str:
        """
        Parse the response from AI21 Jurassic models.
        
        Args:
            response: Raw response from AWS Bedrock
            
        Returns:
            Generated text
        """
        if "completions" in response and len(response["completions"]) > 0:
            return response["completions"][0].get("data", {}).get("text", "")
        else:
            raise LLMError(
                "Unexpected response format from AI21 Jurassic",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
    
    def _parse_stability_response(self, response: Dict[str, Any]) -> List[str]:
        """
        Parse the response from Stability AI models.
        
        Args:
            response: Raw response from AWS Bedrock
            
        Returns:
            List of base64-encoded images
        """
        if "artifacts" in response and len(response["artifacts"]) > 0:
            return [artifact.get("base64", "") for artifact in response["artifacts"]]
        else:
            raise LLMError(
                "Unexpected response format from Stability AI",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text string.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def _handle_bedrock_error(self, error: Exception, model_id: str) -> LLMError:
        """
        Handle AWS Bedrock errors and convert to LLMError.
        
        Args:
            error: The original AWS error
            model_id: The model ID being used
            
        Returns:
            Converted LLMError
        """
        if isinstance(error, ClientError):
            error_code = error.response.get("Error", {}).get("Code", "")
            error_message = error.response.get("Error", {}).get("Message", str(error))
            
            if error_code == "AccessDeniedException":
                return LLMError(
                    f"Authentication failed: {error_message}",
                    LLMErrorType.AUTHENTICATION_ERROR,
                    "aws_bedrock",
                    retryable=False,
                    original_error=error
                )
            elif error_code == "ValidationException":
                if "exceeded your quota" in error_message or "rate limit" in error_message.lower():
                    return LLMError(
                        f"Rate limit exceeded: {error_message}",
                        LLMErrorType.RATE_LIMIT_ERROR,
                        "aws_bedrock",
                        retryable=True,
                        original_error=error
                    )
                else:
                    return LLMError(
                        f"Invalid request: {error_message}",
                        LLMErrorType.INVALID_REQUEST_ERROR,
                        "aws_bedrock",
                        retryable=False,
                        original_error=error
                    )
            elif error_code == "ThrottlingException":
                return LLMError(
                    f"Rate limit exceeded: {error_message}",
                    LLMErrorType.RATE_LIMIT_ERROR,
                    "aws_bedrock",
                    retryable=True,
                    original_error=error
                )
            elif error_code == "ResourceNotFoundException":
                return LLMError(
                    f"Model not found: {model_id}",
                    LLMErrorType.MODEL_NOT_FOUND_ERROR,
                    "aws_bedrock",
                    retryable=False,
                    original_error=error
                )
            elif error_code == "ServiceUnavailableException":
                return LLMError(
                    f"Service unavailable: {error_message}",
                    LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                    "aws_bedrock",
                    retryable=True,
                    original_error=error
                )
            else:
                return LLMError(
                    f"AWS Bedrock error: {error_code} - {error_message}",
                    LLMErrorType.UNKNOWN_ERROR,
                    "aws_bedrock",
                    retryable=True,
                    original_error=error
                )
        elif isinstance(error, ConnectionError):
            return LLMError(
                f"Connection error: {str(error)}",
                LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                "aws_bedrock",
                retryable=True,
                original_error=error
            )
        elif isinstance(error, ReadTimeoutError):
            return LLMError(
                f"Request timed out: {str(error)}",
                LLMErrorType.TIMEOUT_ERROR,
                "aws_bedrock",
                retryable=True,
                original_error=error
            )
        else:
            return LLMError(
                f"Unknown error: {str(error)}",
                LLMErrorType.UNKNOWN_ERROR,
                "aws_bedrock",
                retryable=True,
                original_error=error
            )
    
    def generate_text(self, prompt: str, options: TextGenerationOptions) -> TextGenerationResult:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The text prompt
            options: Text generation options
            
        Returns:
            Generated text result
        """
        model_id = self._resolve_model_id(options.model)
        provider = self._get_provider_for_model(model_id)
        
        # Prepare request body based on the provider
        if provider == "anthropic":
            if "claude-3" in model_id:
                # Claude 3 uses the messages format
                request_body = self._format_anthropic_messages([
                    ChatMessage(role="user", content=prompt)
                ])
            else:
                request_body = self._format_anthropic_prompt(prompt)
            
            # Apply options
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["top_p"] = options.top_p
            if options.max_tokens is not None:
                if "max_tokens_to_sample" in request_body:
                    request_body["max_tokens_to_sample"] = options.max_tokens
                else:
                    request_body["max_tokens"] = options.max_tokens
        
        elif provider == "amazon":
            request_body = self._format_titan_prompt(prompt)
            
            # Apply options
            if options.temperature is not None:
                request_body["textGenerationConfig"]["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["textGenerationConfig"]["topP"] = options.top_p
            if options.max_tokens is not None:
                request_body["textGenerationConfig"]["maxTokenCount"] = options.max_tokens
        
        elif provider == "cohere":
            request_body = self._format_cohere_prompt(prompt)
            
            # Apply options
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["p"] = options.top_p
            if options.max_tokens is not None:
                request_body["max_tokens"] = options.max_tokens
        
        elif provider == "ai21":
            request_body = self._format_ai21_prompt(prompt)
            
            # Apply options
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["topP"] = options.top_p
            if options.max_tokens is not None:
                request_body["maxTokens"] = options.max_tokens
        
        else:
            raise LLMError(
                f"Text generation not supported for provider: {provider}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
        
        # Make the API call
        try:
            response = self.bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response["body"].read())
            
            # Extract the generated text based on the provider
            if provider == "anthropic":
                if "claude-3" in model_id:
                    text = self._parse_anthropic_response(response_body)
                    finish_reason = response_body.get("stop_reason", "stop")
                else:
                    text = response_body.get("completion", "")
                    finish_reason = response_body.get("stop_reason", "stop")
            elif provider == "amazon":
                text = self._parse_titan_response(response_body)
                finish_reason = "stop"  # Titan doesn't provide a finish reason
            elif provider == "cohere":
                text = self._parse_cohere_response(response_body)
                finish_reason = response_body.get("finish_reason", "stop")
            elif provider == "ai21":
                text = self._parse_ai21_response(response_body)
                finish_reason = "stop"  # AI21 doesn't provide a finish reason
            else:
                raise LLMError(
                    f"Unsupported provider: {provider}",
                    LLMErrorType.INVALID_REQUEST_ERROR,
                    "aws_bedrock",
                    retryable=False
                )
            
            # Map finish reason to common format
            if finish_reason == "stop_sequence":
                finish_reason = FinishReason.STOP
            elif finish_reason == "max_tokens":
                finish_reason = FinishReason.LENGTH
            elif finish_reason in ["content_filtered", "content-filter"]:
                finish_reason = FinishReason.CONTENT_FILTER
            else:
                finish_reason = FinishReason.STOP
            
            # Estimate token usage
            prompt_tokens = self._estimate_tokens(prompt)
            completion_tokens = self._estimate_tokens(text)
            
            return TextGenerationResult(
                text=text,
                model=model_id,
                provider="aws_bedrock",
                usage=UsageInfo(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens
                ),
                finish_reason=finish_reason
            )
        
        except Exception as e:
            logger.error(f"Error generating text with AWS Bedrock: {str(e)}")
            raise self._handle_bedrock_error(e, model_id)
    
    async def generate_text_async(self, prompt: str, options: TextGenerationOptions) -> TextGenerationResult:
        """
        Generate text from a prompt asynchronously.
        
        Args:
            prompt: The text prompt
            options: Text generation options
            
        Returns:
            Generated text result
        """
        # AWS SDK doesn't have native async support, so we'll just call the sync version
        return self.generate_text(prompt, options)
    
    async def generate_text_stream(self, prompt: str, options: TextGenerationOptions) -> AsyncIterator[TextGenerationChunk]:
        """
        Generate text from a prompt with streaming response.
        
        Args:
            prompt: The text prompt
            options: Text generation options
            
        Returns:
            Stream of text generation chunks
        """
        model_id = self._resolve_model_id(options.model)
        provider = self._get_provider_for_model(model_id)
        
        # Prepare request body based on the provider
        if provider == "anthropic":
            if "claude-3" in model_id:
                # Claude 3 uses the messages format
                request_body = self._format_anthropic_messages([
                    ChatMessage(role="user", content=prompt)
                ])
            else:
                request_body = self._format_anthropic_prompt(prompt)
            
            # Apply options
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["top_p"] = options.top_p
            if options.max_tokens is not None:
                if "max_tokens_to_sample" in request_body:
                    request_body["max_tokens_to_sample"] = options.max_tokens
                else:
                    request_body["max_tokens"] = options.max_tokens
        
        elif provider == "amazon":
            request_body = self._format_titan_prompt(prompt)
            
            # Apply options
            if options.temperature is not None:
                request_body["textGenerationConfig"]["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["textGenerationConfig"]["topP"] = options.top_p
            if options.max_tokens is not None:
                request_body["textGenerationConfig"]["maxTokenCount"] = options.max_tokens
        
        else:
            raise LLMError(
                f"Streaming not supported for provider: {provider}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
        
        # Make the API call
        try:
            response = self.bedrock_runtime_client.invoke_model_with_response_stream(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # Process the streaming response
            stream = response.get("body", None)
            if not stream:
                raise LLMError(
                    "No stream returned from AWS Bedrock",
                    LLMErrorType.INVALID_REQUEST_ERROR,
                    "aws_bedrock",
                    retryable=False
                )
            
            # Yield chunks as they arrive
            for event in stream:
                chunk = event.get("chunk", {})
                if not chunk:
                    continue
                
                chunk_data = json.loads(chunk.get("bytes", b"{}").decode("utf-8"))
                
                if provider == "anthropic":
                    if "claude-3" in model_id:
                        # Claude 3 streaming format
                        if "delta" in chunk_data:
                            delta = chunk_data["delta"]
                            if "text" in delta:
                                yield TextGenerationChunk(
                                    text=delta["text"],
                                    is_final=False
                                )
                        elif "stop_reason" in chunk_data:
                            # Final chunk with stop reason
                            finish_reason = chunk_data.get("stop_reason", "stop")
                            if finish_reason == "stop_sequence":
                                finish_reason = FinishReason.STOP
                            elif finish_reason == "max_tokens":
                                finish_reason = FinishReason.LENGTH
                            elif finish_reason in ["content_filtered", "content-filter"]:
                                finish_reason = FinishReason.CONTENT_FILTER
                            else:
                                finish_reason = FinishReason.STOP
                            
                            yield TextGenerationChunk(
                                text="",
                                finish_reason=finish_reason,
                                is_final=True
                            )
                    else:
                        # Claude 2 streaming format
                        if "completion" in chunk_data:
                            yield TextGenerationChunk(
                                text=chunk_data["completion"],
                                is_final=False
                            )
                        elif "stop_reason" in chunk_data:
                            # Final chunk with stop reason
                            finish_reason = chunk_data.get("stop_reason", "stop")
                            if finish_reason == "stop_sequence":
                                finish_reason = FinishReason.STOP
                            elif finish_reason == "max_tokens":
                                finish_reason = FinishReason.LENGTH
                            elif finish_reason in ["content_filtered", "content-filter"]:
                                finish_reason = FinishReason.CONTENT_FILTER
                            else:
                                finish_reason = FinishReason.STOP
                            
                            yield TextGenerationChunk(
                                text="",
                                finish_reason=finish_reason,
                                is_final=True
                            )
                
                elif provider == "amazon":
                    # Titan streaming format
                    if "outputText" in chunk_data:
                        yield TextGenerationChunk(
                            text=chunk_data["outputText"],
                            is_final=False
                        )
                    else:
                        # Assume it's the final chunk if no outputText
                        yield TextGenerationChunk(
                            text="",
                            finish_reason=FinishReason.STOP,
                            is_final=True
                        )
        
        except Exception as e:
            logger.error(f"Error generating text stream with AWS Bedrock: {str(e)}")
            raise self._handle_bedrock_error(e, model_id)
    
    def generate_chat(self, messages: List[ChatMessage], options: ChatGenerationOptions) -> ChatGenerationResult:
        """
        Generate a chat response from a conversation.
        
        Args:
            messages: List of chat messages
            options: Chat generation options
            
        Returns:
            Generated chat result
        """
        model_id = self._resolve_model_id(options.model)
        provider = self._get_provider_for_model(model_id)
        
        # Prepare request body based on the provider
        if provider == "anthropic":
            if "claude-3" in model_id:
                # Claude 3 uses the messages format
                request_body = self._format_anthropic_messages(messages)
            else:
                # Convert messages to a prompt for older Claude models
                prompt = ""
                for msg in messages:
                    if msg.role == "system":
                        prompt += f"{msg.content}\n\n"
                    elif msg.role == "user":
                        prompt += f"Human: {msg.content}\n\n"
                    elif msg.role == "assistant":
                        prompt += f"Assistant: {msg.content}\n\n"
                    elif msg.role == "function":
                        prompt += f"Function ({msg.name}): {msg.content}\n\n"
                
                request_body = self._format_anthropic_prompt(prompt)
            
            # Apply options
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["top_p"] = options.top_p
            if options.max_tokens is not None:
                if "max_tokens_to_sample" in request_body:
                    request_body["max_tokens_to_sample"] = options.max_tokens
                else:
                    request_body["max_tokens"] = options.max_tokens
            
            # Handle function calling for Claude 3
            if "claude-3" in model_id and options.functions:
                tools = []
                for func in options.functions:
                    tools.append({
                        "type": "function",
                        "function": {
                            "name": func.name,
                            "description": func.description,
                            "parameters": func.parameters
                        }
                    })
                request_body["tools"] = tools
                
                if options.function_call:
                    if isinstance(options.function_call, str):
                        if options.function_call != "auto":
                            request_body["tool_choice"] = {
                                "type": "function",
                                "function": {
                                    "name": options.function_call
                                }
                            }
                    elif isinstance(options.function_call, dict) and "name" in options.function_call:
                        request_body["tool_choice"] = {
                            "type": "function",
                            "function": {
                                "name": options.function_call["name"]
                            }
                        }
        
        elif provider == "amazon":
            request_body = self._format_titan_messages(messages)
            
            # Apply options
            if options.temperature is not None:
                request_body["textGenerationConfig"]["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["textGenerationConfig"]["topP"] = options.top_p
            if options.max_tokens is not None:
                request_body["textGenerationConfig"]["maxTokenCount"] = options.max_tokens
        
        elif provider == "cohere":
            request_body = self._format_cohere_messages(messages)
            
            # Apply options
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["p"] = options.top_p
            if options.max_tokens is not None:
                request_body["max_tokens"] = options.max_tokens
        
        else:
            raise LLMError(
                f"Chat generation not supported for provider: {provider}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
        
        # Make the API call
        try:
            response = self.bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response["body"].read())
            
            # Extract the generated text based on the provider
            if provider == "anthropic":
                if "claude-3" in model_id:
                    # Check for tool calls (function calls)
                    function_call = None
                    content = ""
                    
                    if "content" in response_body:
                        content_items = response_body.get("content", [])
                        text_parts = []
                        
                        for item in content_items:
                            if item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            elif item.get("type") == "tool_use":
                                tool_use = item.get("tool_use", {})
                                if tool_use.get("type") == "function":
                                    function_call = {
                                        "name": tool_use.get("function", {}).get("name", ""),
                                        "arguments": json.dumps(tool_use.get("function", {}).get("arguments", {}))
                                    }
                        
                        content = "".join(text_parts)
                    
                    finish_reason = response_body.get("stop_reason", "stop")
                    if function_call:
                        finish_reason = FinishReason.FUNCTION_CALL
                    
                    # Create the chat message
                    chat_message = ChatMessage(
                        role="assistant",
                        content=content,
                        function_call=function_call
                    )
                else:
                    # Claude 2 format
                    text = response_body.get("completion", "")
                    finish_reason = response_body.get("stop_reason", "stop")
                    
                    # Create the chat message
                    chat_message = ChatMessage(
                        role="assistant",
                        content=text
                    )
            
            elif provider == "amazon":
                text = self._parse_titan_response(response_body)
                finish_reason = "stop"  # Titan doesn't provide a finish reason
                
                # Create the chat message
                chat_message = ChatMessage(
                    role="assistant",
                    content=text
                )
            
            elif provider == "cohere":
                text = self._parse_cohere_response(response_body)
                finish_reason = response_body.get("finish_reason", "stop")
                
                # Create the chat message
                chat_message = ChatMessage(
                    role="assistant",
                    content=text
                )
            
            else:
                raise LLMError(
                    f"Unsupported provider: {provider}",
                    LLMErrorType.INVALID_REQUEST_ERROR,
                    "aws_bedrock",
                    retryable=False
                )
            
            # Map finish reason to common format
            if finish_reason == "stop_sequence":
                finish_reason = FinishReason.STOP
            elif finish_reason == "max_tokens":
                finish_reason = FinishReason.LENGTH
            elif finish_reason in ["content_filtered", "content-filter"]:
                finish_reason = FinishReason.CONTENT_FILTER
            elif finish_reason == "tool_use" or finish_reason == "function_call":
                finish_reason = FinishReason.FUNCTION_CALL
            else:
                finish_reason = FinishReason.STOP
            
            # Estimate token usage
            prompt_tokens = sum(self._estimate_tokens(msg.content) for msg in messages)
            completion_tokens = self._estimate_tokens(chat_message.content)
            
            return ChatGenerationResult(
                message=chat_message,
                model=model_id,
                provider="aws_bedrock",
                usage=UsageInfo(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens
                ),
                finish_reason=finish_reason
            )
        
        except Exception as e:
            logger.error(f"Error generating chat with AWS Bedrock: {str(e)}")
            raise self._handle_bedrock_error(e, model_id)
    
    async def generate_chat_async(self, messages: List[ChatMessage], options: ChatGenerationOptions) -> ChatGenerationResult:
        """
        Generate a chat response from a conversation asynchronously.
        
        Args:
            messages: List of chat messages
            options: Chat generation options
            
        Returns:
            Generated chat result
        """
        # AWS SDK doesn't have native async support, so we'll just call the sync version
        return self.generate_chat(messages, options)
    
    async def generate_chat_stream(self, messages: List[ChatMessage], options: ChatGenerationOptions) -> AsyncIterator[ChatGenerationChunk]:
        """
        Generate a chat response with streaming.
        
        Args:
            messages: List of chat messages
            options: Chat generation options
            
        Returns:
            Stream of chat generation chunks
        """
        model_id = self._resolve_model_id(options.model)
        provider = self._get_provider_for_model(model_id)
        
        # Prepare request body based on the provider
        if provider == "anthropic":
            if "claude-3" in model_id:
                # Claude 3 uses the messages format
                request_body = self._format_anthropic_messages(messages)
            else:
                # Convert messages to a prompt for older Claude models
                prompt = ""
                for msg in messages:
                    if msg.role == "system":
                        prompt += f"{msg.content}\n\n"
                    elif msg.role == "user":
                        prompt += f"Human: {msg.content}\n\n"
                    elif msg.role == "assistant":
                        prompt += f"Assistant: {msg.content}\n\n"
                    elif msg.role == "function":
                        prompt += f"Function ({msg.name}): {msg.content}\n\n"
                
                request_body = self._format_anthropic_prompt(prompt)
            
            # Apply options
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["top_p"] = options.top_p
            if options.max_tokens is not None:
                if "max_tokens_to_sample" in request_body:
                    request_body["max_tokens_to_sample"] = options.max_tokens
                else:
                    request_body["max_tokens"] = options.max_tokens
            
            # Handle function calling for Claude 3
            if "claude-3" in model_id and options.functions:
                tools = []
                for func in options.functions:
                    tools.append({
                        "type": "function",
                        "function": {
                            "name": func.name,
                            "description": func.description,
                            "parameters": func.parameters
                        }
                    })
                request_body["tools"] = tools
                
                if options.function_call:
                    if isinstance(options.function_call, str):
                        if options.function_call != "auto":
                            request_body["tool_choice"] = {
                                "type": "function",
                                "function": {
                                    "name": options.function_call
                                }
                            }
                    elif isinstance(options.function_call, dict) and "name" in options.function_call:
                        request_body["tool_choice"] = {
                            "type": "function",
                            "function": {
                                "name": options.function_call["name"]
                            }
                        }
        
        else:
            raise LLMError(
                f"Chat streaming not supported for provider: {provider}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
        
        # Make the API call
        try:
            response = self.bedrock_runtime_client.invoke_model_with_response_stream(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # Process the streaming response
            stream = response.get("body", None)
            if not stream:
                raise LLMError(
                    "No stream returned from AWS Bedrock",
                    LLMErrorType.INVALID_REQUEST_ERROR,
                    "aws_bedrock",
                    retryable=False
                )
            
            # Yield chunks as they arrive
            for event in stream:
                chunk = event.get("chunk", {})
                if not chunk:
                    continue
                
                chunk_data = json.loads(chunk.get("bytes", b"{}").decode("utf-8"))
                
                if provider == "anthropic":
                    if "claude-3" in model_id:
                        # Claude 3 streaming format
                        if "delta" in chunk_data:
                            delta = chunk_data["delta"]
                            delta_dict = {}
                            
                            if "text" in delta:
                                delta_dict["content"] = delta["text"]
                            
                            if "tool_use" in delta:
                                tool_use = delta["tool_use"]
                                if tool_use.get("type") == "function":
                                    delta_dict["function_call"] = {
                                        "name": tool_use.get("function", {}).get("name", ""),
                                        "arguments": json.dumps(tool_use.get("function", {}).get("arguments", {}))
                                    }
                            
                            if delta_dict:
                                yield ChatGenerationChunk(
                                    delta=delta_dict,
                                    is_final=False
                                )
                        
                        elif "stop_reason" in chunk_data:
                            # Final chunk with stop reason
                            finish_reason = chunk_data.get("stop_reason", "stop")
                            if finish_reason == "stop_sequence":
                                finish_reason = FinishReason.STOP
                            elif finish_reason == "max_tokens":
                                finish_reason = FinishReason.LENGTH
                            elif finish_reason in ["content_filtered", "content-filter"]:
                                finish_reason = FinishReason.CONTENT_FILTER
                            elif finish_reason == "tool_use":
                                finish_reason = FinishReason.FUNCTION_CALL
                            else:
                                finish_reason = FinishReason.STOP
                            
                            yield ChatGenerationChunk(
                                delta={},
                                finish_reason=finish_reason,
                                is_final=True
                            )
                    
                    else:
                        # Claude 2 streaming format
                        if "completion" in chunk_data:
                            yield ChatGenerationChunk(
                                delta={"content": chunk_data["completion"]},
                                is_final=False
                            )
                        elif "stop_reason" in chunk_data:
                            # Final chunk with stop reason
                            finish_reason = chunk_data.get("stop_reason", "stop")
                            if finish_reason == "stop_sequence":
                                finish_reason = FinishReason.STOP
                            elif finish_reason == "max_tokens":
                                finish_reason = FinishReason.LENGTH
                            elif finish_reason in ["content_filtered", "content-filter"]:
                                finish_reason = FinishReason.CONTENT_FILTER
                            else:
                                finish_reason = FinishReason.STOP
                            
                            yield ChatGenerationChunk(
                                delta={},
                                finish_reason=finish_reason,
                                is_final=True
                            )
        
        except Exception as e:
            logger.error(f"Error generating chat stream with AWS Bedrock: {str(e)}")
            raise self._handle_bedrock_error(e, model_id)
    
    def generate_embedding(self, text: str, options: EmbeddingOptions) -> EmbeddingResult:
        """
        Generate embeddings for text.
        
        Args:
            text: The text to generate embeddings for
            options: Embedding options
            
        Returns:
            Generated embedding result
        """
        model_id = self._resolve_model_id(options.model)
        provider = self._get_provider_for_model(model_id)
        
        # Prepare request body based on the provider
        if provider == "amazon" and "embed" in model_id:
            request_body = {
                "inputText": text
            }
        elif provider == "cohere" and "embed" in model_id:
            request_body = {
                "texts": [text],
                "input_type": "search_document"
            }
        else:
            raise LLMError(
                f"Embeddings not supported for model: {model_id}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
        
        # Make the API call
        try:
            response = self.bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response["body"].read())
            
            # Extract the embedding based on the provider
            if provider == "amazon":
                if "embedding" in response_body:
                    embedding = response_body["embedding"]
                else:
                    raise LLMError(
                        "Unexpected response format from Amazon Titan",
                        LLMErrorType.INVALID_REQUEST_ERROR,
                        "aws_bedrock",
                        retryable=False
                    )
            elif provider == "cohere":
                if "embeddings" in response_body and len(response_body["embeddings"]) > 0:
                    embedding = response_body["embeddings"][0]
                else:
                    raise LLMError(
                        "Unexpected response format from Cohere",
                        LLMErrorType.INVALID_REQUEST_ERROR,
                        "aws_bedrock",
                        retryable=False
                    )
            else:
                raise LLMError(
                    f"Unsupported provider for embeddings: {provider}",
                    LLMErrorType.INVALID_REQUEST_ERROR,
                    "aws_bedrock",
                    retryable=False
                )
            
            # Estimate token usage
            prompt_tokens = self._estimate_tokens(text)
            
            return EmbeddingResult(
                embedding=embedding,
                model=model_id,
                provider="aws_bedrock",
                usage=UsageInfo(
                    prompt_tokens=prompt_tokens,
                    total_tokens=prompt_tokens
                )
            )
        
        except Exception as e:
            logger.error(f"Error generating embedding with AWS Bedrock: {str(e)}")
            raise self._handle_bedrock_error(e, model_id)
    
    async def generate_embedding_async(self, text: str, options: EmbeddingOptions) -> EmbeddingResult:
        """
        Generate embeddings for text asynchronously.
        
        Args:
            text: The text to generate embeddings for
            options: Embedding options
            
        Returns:
            Generated embedding result
        """
        # AWS SDK doesn't have native async support, so we'll just call the sync version
        return self.generate_embedding(text, options)
    
    def generate_image(self, prompt: str, options: ImageGenerationOptions) -> ImageGenerationResult:
        """
        Generate images from a prompt.
        
        Args:
            prompt: The text prompt
            options: Image generation options
            
        Returns:
            Generated image result
        """
        model_id = self._resolve_model_id(options.model or "stable-diffusion-xl")
        provider = self._get_provider_for_model(model_id)
        
        # Prepare request body based on the provider
        if provider == "stability":
            request_body = self._format_stability_prompt(prompt, options)
        else:
            raise LLMError(
                f"Image generation not supported for provider: {provider}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "aws_bedrock",
                retryable=False
            )
        
        # Make the API call
        try:
            response = self.bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response["body"].read())
            
            # Extract the generated images based on the provider
            if provider == "stability":
                images = self._parse_stability_response(response_body)
            else:
                raise LLMError(
                    f"Unsupported provider for image generation: {provider}",
                    LLMErrorType.INVALID_REQUEST_ERROR,
                    "aws_bedrock",
                    retryable=False
                )
            
            return ImageGenerationResult(
                images=images,
                model=model_id,
                provider="aws_bedrock"
            )
        
        except Exception as e:
            logger.error(f"Error generating image with AWS Bedrock: {str(e)}")
            raise self._handle_bedrock_error(e, model_id)
    
    async def generate_image_async(self, prompt: str, options: ImageGenerationOptions) -> ImageGenerationResult:
        """
        Generate images from a prompt asynchronously.
        
        Args:
            prompt: The text prompt
            options: Image generation options
            
        Returns:
            Generated image result
        """
        # AWS SDK doesn't have native async support, so we'll just call the sync version
        return self.generate_image(prompt, options)
    
    def get_models(self) -> List[ModelInfo]:
        """
        Get information about available models.
        
        Returns:
            List of model information
        """
        # Check cache first
        current_time = time.time()
        if (
            self._models_cache is not None
            and current_time - self._models_cache_timestamp < self._models_cache_ttl
        ):
            return self._models_cache
        
        try:
            # Get list of foundation models from Bedrock
            response = self.bedrock_client.list_foundation_models()
            
            models = []
            for model_summary in response.get("modelSummaries", []):
                model_id = model_summary.get("modelId", "")
                model_name = BEDROCK_MODEL_REVERSE_MAPPINGS.get(model_id, model_id)
                
                # Get capabilities
                capabilities = BEDROCK_MODEL_CAPABILITIES.get(model_id, [])
                
                # Get cost information
                cost_info = BEDROCK_MODEL_COSTS.get(model_id, {"input": 0.0, "output": 0.0})
                
                # Get max tokens
                max_tokens = BEDROCK_MODEL_MAX_TOKENS.get(model_id, 4096)
                
                models.append(ModelInfo(
                    id=model_name,
                    provider_model_id=model_id,
                    provider="aws_bedrock",
                    capabilities=capabilities,
                    max_tokens=max_tokens,
                    cost_per_input_token=cost_info["input"] / 1000.0,  # Convert from per 1000 tokens to per token
                    cost_per_output_token=cost_info["output"] / 1000.0  # Convert from per 1000 tokens to per token
                ))
            
            # Update cache
            self._models_cache = models
            self._models_cache_timestamp = current_time
            
            return models
        
        except Exception as e:
            logger.error(f"Error getting models from AWS Bedrock: {str(e)}")
            raise self._handle_bedrock_error(e, "")
    
    async def get_models_async(self) -> List[ModelInfo]:
        """
        Get information about available models asynchronously.
        
        Returns:
            List of model information
        """
        # AWS SDK doesn't have native async support, so we'll just call the sync version
        return self.get_models()
    
    def get_capabilities(self) -> ProviderCapabilities:
        """
        Get provider capabilities.
        
        Returns:
            Provider capabilities
        """
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
        """
        Get provider health status.
        
        Returns:
            Provider health status
        """
        # Check cache first
        current_time = time.time()
        if (
            self._health_cache is not None
            and current_time - self._health_cache_timestamp < self._health_cache_ttl
        ):
            return self._health_cache
        
        try:
            # Simple health check: list models
            start_time = time.time()
            self.bedrock_client.list_foundation_models()
            end_time = time.time()
            
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            
            health = HealthStatus(
                available=True,
                latency=latency,
                error_rate=0.0,
                message="AWS Bedrock is available"
            )
            
            # Update cache
            self._health_cache = health
            self._health_cache_timestamp = current_time
            
            return health
        
        except Exception as e:
            logger.error(f"AWS Bedrock health check failed: {str(e)}")
            
            health = HealthStatus(
                available=False,
                latency=0.0,
                error_rate=1.0,
                message=f"AWS Bedrock is unavailable: {str(e)}"
            )
            
            # Update cache
            self._health_cache = health
            self._health_cache_timestamp = current_time
            
            return health
    
    async def get_health_async(self) -> HealthStatus:
        """
        Get provider health status asynchronously.
        
        Returns:
            Provider health status
        """
        # AWS SDK doesn't have native async support, so we'll just call the sync version
        return self.get_health()
    
    def get_name(self) -> str:
        """
        Get provider name.
        
        Returns:
            Provider name
        """
        return "AWS Bedrock"
    
    def get_type(self) -> ProviderType:
        """
        Get provider type.
        
        Returns:
            Provider type
        """
        return ProviderType.AWS_BEDROCK
