# src/plugins/llm_providers/internal/openai_provider.py
from typing import List, Dict, Any, Optional
import os

# Assuming base_provider.py is in the same directory or accessible in PYTHONPATH
from src.plugins.llm_providers.base_provider import LLMProvider, ModelInfo, LLMOptions

# In a real scenario, you would install the OpenAI Python SDK
# e.g., pip install openai
# For now, we will mock the interactions.

class OpenAIProvider(LLMProvider):
    PROVIDER_NAME = "openai"
    DISPLAY_NAME = "OpenAI GPT"
    API_KEY_NAME = "OPENAI_API_KEY"

    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        super().__init__(api_key=api_key, api_base_url=api_base_url) # api_base_url can be used for Azure OpenAI or compatible APIs
        # Initialize the OpenAI client here if an API key is provided
        # For example:
        # if self.api_key:
        #     from openai import OpenAI
        #     self.client = OpenAI(api_key=self.api_key, base_url=self.api_base_url)
        # else:
        #     print("Warning: OpenAIProvider initialized without an API key.")
        print(f"OpenAIProvider initialized. API Key provided: {bool(self.api_key)}, Base URL: {self.api_base_url}")

    @classmethod
    def get_static_provider_name(cls) -> str:
        return cls.PROVIDER_NAME

    @classmethod
    def get_static_provider_display_name(cls) -> str:
        return cls.DISPLAY_NAME

    @classmethod
    def get_required_api_key_name(cls) -> Optional[str]:
        return cls.API_KEY_NAME

    async def get_available_models(self) -> List[ModelInfo]:
        """Returns a list of available models from OpenAI."""
        # In a real implementation, this might make an API call to list models
        # or return a predefined list based on the SDK/API knowledge.
        # For now, returning a mock list.
        print("OpenAIProvider: Fetching available models (mocked)...")
        return [
            ModelInfo(id="gpt-4-turbo", name="GPT-4 Turbo", description="OpenAI's most advanced model with a large context window and updated knowledge.", context_window=128000),
            ModelInfo(id="gpt-4", name="GPT-4", description="OpenAI's powerful model with broad general knowledge and advanced reasoning capabilities.", context_window=8192),
            ModelInfo(id="gpt-3.5-turbo", name="GPT-3.5 Turbo", description="OpenAI's fast and cost-effective model, optimized for chat.", context_window=16385),
        ]

    async def generate_completion(self, model_id: str, prompt: str, system_prompt: Optional[str] = None, params: Optional[LLMOptions] = None) -> Dict[str, Any]:
        """Generates a text completion using OpenAI (legacy, prefer chat completions)."""
        print(f"OpenAIProvider: Generating completion for model {model_id} (using chat completion as fallback)...")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.generate_chat_completion(model_id, messages, system_prompt=None, params=params) # system_prompt already in messages

    async def generate_chat_completion(self, model_id: str, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, params: Optional[LLMOptions] = None) -> Dict[str, Any]:
        """Generates a chat completion using OpenAI."""
        if not self.api_key:
            return {"error": "API key not configured for OpenAIProvider."}

        print(f"OpenAIProvider: Generating chat completion for model {model_id}...")
        
        # Prepare messages for OpenAI API
        openai_messages = []
        if system_prompt:
            # Check if a system message already exists from a previous step (e.g. generate_completion)
            has_system_message = any(msg["role"] == "system" for msg in messages)
            if not has_system_message:
                openai_messages.append({"role": "system", "content": system_prompt})
        
        openai_messages.extend(messages)

        # Placeholder for actual API call to OpenAI
        # Example structure of how you might call the SDK:
        # try:
        #     from openai import OpenAI # Already imported if client is initialized
        #     # self.client should be an instance of OpenAI client
        #     api_params = {"model": model_id, "messages": openai_messages}
        #     if params:
        #         if params.get("temperature") is not None: api_params["temperature"] = params["temperature"]
        #         if params.get("max_tokens") is not None: api_params["max_tokens"] = params["max_tokens"]
        #         if params.get("top_p") is not None: api_params["top_p"] = params["top_p"]
        #         if params.get("stop_sequences"): api_params["stop"] = params["stop_sequences"]
        #         # OpenAI uses "stop" not "stop_sequences"

        #     chat_completion = await self.client.chat.completions.create(**api_params) # Use async client if available or run in executor
        #     response_text = chat_completion.choices[0].message.content
        #     usage_info = chat_completion.usage # Contains prompt_tokens, completion_tokens, total_tokens
        #     return {"text": response_text, "usage": dict(usage_info), "error": None}
        # except Exception as e:
        #     return {"error": str(e)}

        # Mocked response for now
        if openai_messages:
            last_user_message = next((msg["content"] for msg in reversed(openai_messages) if msg["role"] == "user"), "No user message found")
            mock_response_text = f"Mocked OpenAI response to: 	{last_user_message[:50]}...	 for model {model_id}"
        else:
            mock_response_text = f"Mocked OpenAI response for model {model_id}"
        
        return {"text": mock_response_text, "usage": {"prompt_tokens": 60, "completion_tokens": 25, "total_tokens": 85}, "error": None}


