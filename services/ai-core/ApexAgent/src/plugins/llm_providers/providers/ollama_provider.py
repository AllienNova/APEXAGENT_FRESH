# src/plugins/llm_providers/internal/ollama_provider.py
import json
import httpx
from typing import List, Dict, Any, Optional

from src.plugins.llm_providers.base_provider import LLMProvider, ModelInfo

class OllamaProvider(LLMProvider):
    # Default base URL for a local Ollama instance
    DEFAULT_API_BASE_URL = "http://localhost:11434"

    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        # Ollama doesn_t use an API key, so api_key will be None.
        # api_base_url can be passed if the user has Ollama running on a non-default port/host.
        effective_api_base_url = api_base_url if api_base_url else self.DEFAULT_API_BASE_URL
        super().__init__(api_key=None, api_base_url=effective_api_base_url)
        self.client = httpx.AsyncClient(base_url=self.api_base_url) # Use self.api_base_url from parent

    @classmethod
    def get_static_provider_name(cls) -> str:
        return "ollama"

    @classmethod
    def get_static_provider_display_name(cls) -> str:
        return "Ollama (Local)"

    # get_provider_name and get_provider_display_name are inherited from LLMProvider
    # and will use the static methods above.

    async def get_available_models(self) -> List[ModelInfo]:
        """Fetches available models from the Ollama API."""
        models_info = []
        if not self.client: # Should not happen if __init__ is called correctly
            return models_info
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            if "models" in data:
                for model_data in data["models"]:
                    # Ollama model names often include version tags like :latest or :7b
                    # The ID should be the full name Ollama uses.
                    model_id = model_data.get("name", "unknown_ollama_model")
                    models_info.append(
                        ModelInfo(
                            id=model_id,
                            name=model_id, # Use the full name as the display name too for clarity
                            description=f"Ollama model: {model_id}, Size: {model_data.get('size')}, Modified: {model_data.get('modified_at')}",
                            context_window=None # Ollama API doesn_t directly expose this per model easily
                        )
                    )
        except httpx.RequestError as e:
            print(f"Error fetching Ollama models from {self.api_base_url}: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding Ollama models response: {e}")
        return models_info

    async def generate_completion(self, model_id: str, prompt: str, system_prompt: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates a text completion using Ollama_s /api/generate endpoint."""
        request_payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            request_payload["system"] = system_prompt
        if params:
            request_payload["options"] = params

        response_text = ""
        error_message = None
        usage_info = {}

        if not self.client:
            return {"text": "", "usage": {}, "error": "HTTP client not initialized"}

        try:
            response = await self.client.post("/api/generate", json=request_payload, timeout=120.0)
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "")
            usage_info = {
                "prompt_eval_count": data.get("prompt_eval_count"),
                "eval_count": data.get("eval_count"),
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
            }
        except httpx.HTTPStatusError as e:
            error_message = f"HTTP error: {e.response.status_code} - {e.response.text}"
            print(error_message)
        except httpx.RequestError as e:
            error_message = f"Request error: {e}"
            print(error_message)
        except json.JSONDecodeError as e:
            error_message = f"JSON decode error: {e}"
            print(error_message)

        return {
            "text": response_text,
            "usage": usage_info,
            "error": error_message
        }

    async def generate_chat_completion(self, model_id: str, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates a chat completion using Ollama_s /api/chat endpoint."""
        ollama_messages = []
        if system_prompt:
            ollama_messages.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            ollama_messages.append(msg)

        request_payload = {
            "model": model_id,
            "messages": ollama_messages,
            "stream": False
        }
        if params:
            request_payload["options"] = params

        response_text = ""
        error_message = None
        usage_info = {}

        if not self.client:
            return {"text": "", "usage": {}, "error": "HTTP client not initialized"}

        try:
            response = await self.client.post("/api/chat", json=request_payload, timeout=120.0)
            response.raise_for_status()
            data = response.json()
            if data.get("message") and isinstance(data["message"], dict):
                response_text = data["message"].get("content", "")
            
            usage_info = {
                "prompt_eval_count": data.get("prompt_eval_count"),
                "eval_count": data.get("eval_count"),
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
            }

        except httpx.HTTPStatusError as e:
            error_message = f"HTTP error: {e.response.status_code} - {e.response.text}"
            print(error_message)
        except httpx.RequestError as e:
            error_message = f"Request error: {e}"
            print(error_message)
        except json.JSONDecodeError as e:
            error_message = f"JSON decode error: {e}"
            print(error_message)

        return {
            "text": response_text,
            "usage": usage_info,
            "error": error_message
        }

    @classmethod
    def get_required_api_key_name(cls) -> Optional[str]:
        return None

