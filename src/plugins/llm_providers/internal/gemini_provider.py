# src/plugins/llm_providers/internal/gemini_provider.py
from typing import List, Dict, Any, Optional
import os

# Assuming base_provider.py is in the same directory or accessible in PYTHONPATH
from src.plugins.llm_providers.base_provider import LLMProvider, ModelInfo, LLMOptions

# In a real scenario, you would install the Google Generative AI SDK
# e.g., pip install google-generativeai
# For now, we will mock the interactions.

class GeminiProvider(LLMProvider):
    PROVIDER_NAME = "google_gemini"
    DISPLAY_NAME = "Google Gemini"
    API_KEY_NAME = "GOOGLE_GEMINI_API_KEY" # Or simply GOOGLE_API_KEY if that's standard

    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        super().__init__(api_key=api_key, api_base_url=api_base_url)
        # Initialize the Gemini client here if an API key is provided
        # For example:
        # if self.api_key:
        #     import google.generativeai as genai
        #     genai.configure(api_key=self.api_key)
        # else:
        #     print("Warning: GeminiProvider initialized without an API key.")
        print(f"GeminiProvider initialized. API Key provided: {bool(self.api_key)}")

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
        """Returns a list of available models from Google Gemini."""
        # In a real implementation, this would make an API call to list models
        # or return a predefined list based on the SDK.
        # For now, returning a mock list.
        print("GeminiProvider: Fetching available models (mocked)...")
        return [
            ModelInfo(id="gemini-1.5-pro-latest", name="Gemini 1.5 Pro", description="Google's most capable model, with a large context window.", context_window=1048576),
            ModelInfo(id="gemini-1.0-pro", name="Gemini 1.0 Pro", description="Google's best model for scaling across a wide range of tasks.", context_window=32768),
            ModelInfo(id="gemini-1.5-flash-latest", name="Gemini 1.5 Flash", description="Google's fast and versatile multimodal model.", context_window=1048576),
            # Add other models like gemini-ultra, gemini-pro-vision etc. as appropriate
        ]

    async def generate_completion(self, model_id: str, prompt: str, system_prompt: Optional[str] = None, params: Optional[LLMOptions] = None) -> Dict[str, Any]:
        """Generates a text completion using Gemini (typically chat models are preferred)."""
        print(f"GeminiProvider: Generating completion for model {model_id} (using chat completion as fallback)...")
        # Gemini API primarily uses a chat-like structure even for single prompts.
        # We can adapt the prompt to a chat message format.
        messages = []
        if system_prompt:
            # Gemini's newer APIs might handle system prompts differently or as part of the first user message context
            # For older models or direct text generation, system prompt might be prepended.
            # For this example, we'll assume it's part of the context for a chat-like interaction.
            messages.append({"role": "user", "content": f"{system_prompt}\n\nUser: {prompt}"}) # Simplified adaptation
            messages.append({"role": "model", "content": "Okay, I understand the context."}) # Mock assistant ack
            messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt})
        
        return await self.generate_chat_completion(model_id, messages, system_prompt=None, params=params)

    async def generate_chat_completion(self, model_id: str, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, params: Optional[LLMOptions] = None) -> Dict[str, Any]:
        """Generates a chat completion using Gemini."""
        if not self.api_key:
            return {"error": "API key not configured for GeminiProvider."}

        print(f"GeminiProvider: Generating chat completion for model {model_id}...")
        
        try:
            import google.generativeai as genai
            import asyncio
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Convert messages to Gemini's format
            gemini_messages = []
            
            # Handle system prompt for Gemini
            # Gemini doesn't have a dedicated system message type, so we need to adapt
            if system_prompt:
                # For Gemini 1.5+ models, we can use the system parameter in the generation config
                system_instruction = system_prompt
            else:
                system_instruction = None
            
            # Process messages
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                # Map roles from standard format to Gemini's format
                if role == "user":
                    gemini_role = "user"
                elif role in ["assistant", "model"]:
                    gemini_role = "model"
                elif role == "system":
                    # If we encounter a system message in the messages list,
                    # use it as the system instruction instead of adding it as a message
                    system_instruction = content
                    continue
                else:
                    # Skip unknown roles
                    continue
                
                # Handle multimodal content if present
                if isinstance(content, str):
                    gemini_messages.append({"role": gemini_role, "parts": [content]})
                elif isinstance(content, list):
                    # Handle multimodal content (text and images)
                    parts = []
                    for part in content:
                        if isinstance(part, str):
                            parts.append(part)
                        elif isinstance(part, dict) and part.get("type") == "image":
                            # Convert image data to Gemini's format
                            image_data = part.get("data")
                            if image_data:
                                if image_data.startswith("http"):
                                    # Image URL
                                    parts.append({"inline_data": {"mime_type": "image/jpeg", "url": image_data}})
                                else:
                                    # Base64 encoded image
                                    parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_data}})
                    gemini_messages.append({"role": gemini_role, "parts": parts})
            
            # Set up generation config
            generation_config = {}
            safety_settings = {}
            
            if params:
                # Temperature controls randomness (higher = more random)
                if params.get("temperature") is not None:
                    generation_config["temperature"] = params["temperature"]
                
                # Max tokens limits response length
                if params.get("max_tokens") is not None:
                    generation_config["max_output_tokens"] = params["max_tokens"]
                
                # Top-p (nucleus sampling) controls diversity
                if params.get("top_p") is not None:
                    generation_config["top_p"] = params["top_p"]
                
                # Top-k controls diversity by limiting token selection
                if params.get("top_k") is not None:
                    generation_config["top_k"] = params["top_k"]
                
                # Stop sequences tell the model when to stop generating
                if params.get("stop_sequences"):
                    generation_config["stop_sequences"] = params["stop_sequences"]
                
                # Safety settings
                if params.get("safety_level"):
                    safety_level = params["safety_level"]
                    # Map safety level to Gemini's HarmBlockThreshold
                    threshold_map = {
                        "high": HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        "medium": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        "low": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                        "none": HarmBlockThreshold.BLOCK_NONE
                    }
                    
                    # Apply safety settings to all harm categories
                    for category in [
                        HarmCategory.HARM_CATEGORY_HARASSMENT,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
                    ]:
                        safety_settings[category] = threshold_map.get(
                            safety_level, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        )
            
            # Initialize the model
            model = genai.GenerativeModel(model_id)
            
            # Create a chat session
            chat = model.start_chat(history=gemini_messages)
            
            # Generate the response
            response = await asyncio.to_thread(
                chat.send_message,
                "",  # Empty message since we've already provided the history
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=system_instruction
            )
            
            # Extract response text
            response_text = response.text
            
            # Get token usage information
            # Note: Gemini API might not provide detailed token counts in the same way as OpenAI
            # We'll estimate based on character counts as a fallback
            prompt_text = " ".join([msg.get("content", "") for msg in messages if isinstance(msg.get("content"), str)])
            prompt_tokens = len(prompt_text) // 4  # Rough estimate: ~4 chars per token
            completion_tokens = len(response_text) // 4
            total_tokens = prompt_tokens + completion_tokens
            
            # Try to get actual token counts if available in the response
            usage = {
                "prompt_tokens": getattr(response, "prompt_token_count", prompt_tokens),
                "completion_tokens": getattr(response, "candidates_token_count", completion_tokens),
                "total_tokens": getattr(response, "total_token_count", total_tokens)
            }
            
            return {
                "text": response_text,
                "usage": usage,
                "error": None,
                "model": model_id,
                "finish_reason": "stop"  # Assuming normal completion
            }
            
        except ImportError as e:
            return {
                "error": f"Google Generative AI SDK not installed: {str(e)}. Please install with 'pip install google-generativeai'."
            }
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return {
                "error": f"Error generating completion with Gemini: {str(e)}",
                "error_details": error_details
            }

# Example of how to register this provider (would be in plugin_manager.py or similar)
# from .gemini_provider import GeminiProvider
# plugin_manager.register_llm_provider(GeminiProvider)

