"""
Core provider interface for the LLM Providers integration.

This module defines the common interfaces and data models that all LLM provider
adapters must implement, ensuring a consistent API across different providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union


class ProviderType(str, Enum):
    """Enumeration of supported LLM provider types."""
    AWS_BEDROCK = "aws_bedrock"
    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_VERTEX = "google_vertex"
    CUSTOM = "custom"


class LLMErrorType(str, Enum):
    """Enumeration of common LLM error types."""
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    QUOTA_EXCEEDED_ERROR = "quota_exceeded_error"
    INVALID_REQUEST_ERROR = "invalid_request_error"
    MODEL_NOT_FOUND_ERROR = "model_not_found_error"
    CONTEXT_LENGTH_EXCEEDED_ERROR = "context_length_exceeded_error"
    CONTENT_FILTER_ERROR = "content_filter_error"
    SERVICE_UNAVAILABLE_ERROR = "service_unavailable_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class FinishReason(str, Enum):
    """Enumeration of reasons why a generation completed."""
    STOP = "stop"  # Generation reached a natural stopping point or stop token
    LENGTH = "length"  # Generation reached max tokens limit
    CONTENT_FILTER = "content_filter"  # Content was filtered due to safety concerns
    FUNCTION_CALL = "function_call"  # Generation resulted in a function call
    ERROR = "error"  # Generation failed due to an error
    UNKNOWN = "unknown"  # Unknown reason


@dataclass
class ChatMessage:
    """Represents a message in a chat conversation."""
    role: str  # 'system', 'user', 'assistant', or 'function'
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None


@dataclass
class FunctionDefinition:
    """Defines a function that can be called by the model."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: Optional[List[str]] = None


@dataclass
class ModelInfo:
    """Information about an LLM model."""
    id: str  # Internal model ID
    provider_model_id: str  # Provider-specific model ID
    provider: str  # Provider name
    capabilities: List[str]  # List of capabilities (text, chat, embeddings, etc.)
    max_tokens: int  # Maximum context length
    cost_per_input_token: float  # Cost per input token in USD
    cost_per_output_token: float  # Cost per output token in USD


@dataclass
class ProviderCapabilities:
    """Capabilities of an LLM provider."""
    supports_text: bool = False
    supports_chat: bool = False
    supports_embeddings: bool = False
    supports_images: bool = False
    supports_streaming: bool = False
    supports_functions: bool = False
    supports_vision: bool = False
    supports_audio: bool = False


@dataclass
class HealthStatus:
    """Health status of an LLM provider."""
    available: bool
    latency: float  # in milliseconds
    error_rate: float  # percentage of errors in recent requests
    quota_remaining: Optional[float] = None  # remaining quota if applicable
    message: Optional[str] = None  # additional status information


@dataclass
class UsageInfo:
    """Token usage information for an LLM request."""
    prompt_tokens: int
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


@dataclass
class TextGenerationOptions:
    """Options for text generation requests."""
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    provider: Optional[str] = None
    timeout: Optional[float] = None
    retry_count: Optional[int] = None


@dataclass
class ChatGenerationOptions(TextGenerationOptions):
    """Options for chat generation requests."""
    functions: Optional[List[FunctionDefinition]] = None
    function_call: Optional[Union[str, Dict[str, str]]] = None


@dataclass
class EmbeddingOptions:
    """Options for embedding generation requests."""
    model: str
    dimensions: Optional[int] = None
    provider: Optional[str] = None


@dataclass
class ImageGenerationOptions:
    """Options for image generation requests."""
    model: Optional[str] = None
    size: Optional[str] = None
    quality: Optional[str] = None
    style: Optional[str] = None
    provider: Optional[str] = None


@dataclass
class TextGenerationResult:
    """Result of a text generation request."""
    text: str
    model: str
    provider: str
    usage: UsageInfo
    finish_reason: str


@dataclass
class ChatGenerationResult:
    """Result of a chat generation request."""
    message: ChatMessage
    model: str
    provider: str
    usage: UsageInfo
    finish_reason: str


@dataclass
class EmbeddingResult:
    """Result of an embedding generation request."""
    embedding: List[float]
    model: str
    provider: str
    usage: UsageInfo


@dataclass
class ImageGenerationResult:
    """Result of an image generation request."""
    images: List[str]  # Base64 encoded images or URLs
    model: str
    provider: str


@dataclass
class TextGenerationChunk:
    """Chunk of a streaming text generation response."""
    text: str
    finish_reason: Optional[str] = None
    is_final: bool = False


@dataclass
class ChatGenerationChunk:
    """Chunk of a streaming chat generation response."""
    delta: Dict[str, Any]  # Contains role, content, or function_call updates
    finish_reason: Optional[str] = None
    is_final: bool = False


class LLMError(Exception):
    """Base exception class for LLM-related errors."""
    
    def __init__(
        self,
        message: str,
        error_type: LLMErrorType,
        provider: str,
        retryable: bool = False,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.type = error_type
        self.provider = provider
        self.retryable = retryable
        self.original_error = original_error


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_text(
        self, prompt: str, options: TextGenerationOptions
    ) -> TextGenerationResult:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    async def generate_text_async(
        self, prompt: str, options: TextGenerationOptions
    ) -> TextGenerationResult:
        """Generate text from a prompt asynchronously."""
        pass
    
    @abstractmethod
    def generate_text_stream(
        self, prompt: str, options: TextGenerationOptions
    ) -> AsyncIterator[TextGenerationChunk]:
        """Generate text from a prompt with streaming response."""
        pass
    
    @abstractmethod
    def generate_chat(
        self, messages: List[ChatMessage], options: ChatGenerationOptions
    ) -> ChatGenerationResult:
        """Generate a chat response from a conversation."""
        pass
    
    @abstractmethod
    async def generate_chat_async(
        self, messages: List[ChatMessage], options: ChatGenerationOptions
    ) -> ChatGenerationResult:
        """Generate a chat response from a conversation asynchronously."""
        pass
    
    @abstractmethod
    def generate_chat_stream(
        self, messages: List[ChatMessage], options: ChatGenerationOptions
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Generate a chat response with streaming."""
        pass
    
    @abstractmethod
    def generate_embedding(
        self, text: str, options: EmbeddingOptions
    ) -> EmbeddingResult:
        """Generate embeddings for text."""
        pass
    
    @abstractmethod
    async def generate_embedding_async(
        self, text: str, options: EmbeddingOptions
    ) -> EmbeddingResult:
        """Generate embeddings for text asynchronously."""
        pass
    
    @abstractmethod
    def generate_image(
        self, prompt: str, options: ImageGenerationOptions
    ) -> ImageGenerationResult:
        """Generate images from a prompt."""
        pass
    
    @abstractmethod
    async def generate_image_async(
        self, prompt: str, options: ImageGenerationOptions
    ) -> ImageGenerationResult:
        """Generate images from a prompt asynchronously."""
        pass
    
    @abstractmethod
    def get_models(self) -> List[ModelInfo]:
        """Get information about available models."""
        pass
    
    @abstractmethod
    async def get_models_async(self) -> List[ModelInfo]:
        """Get information about available models asynchronously."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities."""
        pass
    
    @abstractmethod
    def get_health(self) -> HealthStatus:
        """Get provider health status."""
        pass
    
    @abstractmethod
    async def get_health_async(self) -> HealthStatus:
        """Get provider health status asynchronously."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name."""
        pass
    
    @abstractmethod
    def get_type(self) -> ProviderType:
        """Get provider type."""
        pass
