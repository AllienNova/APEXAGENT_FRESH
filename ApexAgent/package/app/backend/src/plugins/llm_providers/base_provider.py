# src/plugins/llm_providers/base_provider.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TypedDict, Optional

class ModelInfo(TypedDict):
    id: str # e.g., "claude-3-opus-20240229"
    name: str # e.g., "Claude 3 Opus"
    description: Optional[str]
    context_window: Optional[int]
    # Add other relevant model capabilities, e.g., multimodal_support: bool

class LLMProvider(ABC):
    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        self.api_key = api_key
        self.api_base_url = api_base_url # Added for providers like Ollama that might need a base URL

    @classmethod
    @abstractmethod
    def get_static_provider_name(cls) -> str:
        """Returns a unique machine-readable name for the provider (e.g., "anthropic", "openai").
           This is a classmethod to allow discovery without instantiation.
        """
        pass

    @classmethod
    @abstractmethod
    def get_static_provider_display_name(cls) -> str:
        """Returns a user-friendly name for the provider (e.g., "Anthropic Claude", "OpenAI GPT").
           This is a classmethod for discovery.
        """
        pass

    def get_provider_name(self) -> str:
        """Returns a unique machine-readable name for the provider."""
        return self.__class__.get_static_provider_name()

    def get_provider_display_name(self) -> str:
        """Returns a user-friendly name for the provider."""
        return self.__class__.get_static_provider_display_name()

    @abstractmethod
    async def get_available_models(self) -> List[ModelInfo]:
        """Returns a list of available models from this provider. Made async."""
        pass

    @abstractmethod
    async def generate_completion(self, model_id: str, prompt: str, system_prompt: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates a text completion based on the prompt.
           Should return a dictionary with at least a "text" key for the completion.
           Example: {"text": "Generated response...", "usage": {...}, "error": null}
        """
        pass

    @abstractmethod
    async def generate_chat_completion(self, model_id: str, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates a chat completion based on a list of messages.
           Messages are typically {"role": "user"/"assistant", "content": "..."}.
           Should return a dictionary with at least a "text" key for the completion.
           Example: {"text": "Generated response...", "usage": {...}, "error": null}
        """
        pass

    @classmethod
    def get_required_api_key_name(cls) -> Optional[str]:
        """Returns the environment variable name or a unique key name expected for the API key (e.g., ANTHROPIC_API_KEY).
           Returns None if no API key is required.
        """
        return None # Default, override in subclasses




class LLMOptions(TypedDict, total=False):
    temperature: Optional[float]
    max_tokens: Optional[int]
    top_p: Optional[float]
    top_k: Optional[int]
    stop_sequences: Optional[List[str]]
    stream: Optional[bool] # Added for Ollama, useful for others too
    # Add other common LLM parameters as needed

