"""
Anthropic Claude LLM Provider for Dr. TARDIS

This module implements the Anthropic Claude LLM provider integration,
supporting all Claude models with full API functionality, error handling,
and multimodal capabilities.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

from typing import List, Dict, Any, Optional, Union
import os
import json
import logging
import asyncio
from datetime import datetime

# Import base provider
from src.plugins.llm_providers.base_provider import LLMProvider, ModelInfo, LLMOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnthropicProvider")

class AnthropicProvider(LLMProvider):
    """
    Provider implementation for Anthropic's Claude models.
    
    Supports all Claude models including Claude 3 Opus, Sonnet, and Haiku,
    with full chat completion functionality and multimodal capabilities.
    """
    
    PROVIDER_NAME = "anthropic"
    DISPLAY_NAME = "Anthropic Claude"
    API_KEY_NAME = "ANTHROPIC_API_KEY"
    DEFAULT_API_BASE = "https://api.anthropic.com"
    API_VERSION = "2023-06-01"  # Current Anthropic API version
    
    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        """
        Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key (optional, will use environment variable if not provided)
            api_base_url: Base URL for Anthropic API (optional, will use default if not provided)
        """
        # If api_key is not provided, try to get it from environment variable
        if api_key is None:
            api_key = os.environ.get(self.API_KEY_NAME)
            
        super().__init__(api_key=api_key, api_base_url=api_base_url)
        self.api_base = self.api_base_url if self.api_base_url else self.DEFAULT_API_BASE
        self.logger = logger
        self.logger.info(f"AnthropicProvider initialized. API Key provided: {bool(self.api_key)}")
    
    @classmethod
    def get_static_provider_name(cls) -> str:
        """Get the provider's unique identifier."""
        return cls.PROVIDER_NAME
    
    @classmethod
    def get_static_provider_display_name(cls) -> str:
        """Get the provider's display name."""
        return cls.DISPLAY_NAME
    
    @classmethod
    def get_required_api_key_name(cls) -> Optional[str]:
        """Get the name of the environment variable for the API key."""
        return cls.API_KEY_NAME
    
    async def get_available_models(self) -> List[ModelInfo]:
        """
        Returns a list of available models from Anthropic.
        
        Returns:
            List of ModelInfo objects representing available Claude models.
        """
        self.logger.info("AnthropicProvider: Fetching available models")
        
        # Anthropic doesn't currently have a models endpoint, so we return a predefined list
        # This should be updated if Anthropic adds a models endpoint in the future
        return [
            ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                description="Anthropic's most powerful model, with exceptional intelligence and capabilities across tasks.",
                context_window=200000
            ),
            ModelInfo(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                description="Anthropic's balanced model, offering strong performance with greater efficiency.",
                context_window=200000
            ),
            ModelInfo(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                description="Anthropic's fastest and most compact model, optimized for efficiency.",
                context_window=200000
            ),
            ModelInfo(
                id="claude-2.1",
                name="Claude 2.1",
                description="Anthropic's previous generation model with strong reasoning capabilities.",
                context_window=100000
            ),
            ModelInfo(
                id="claude-instant-1.2",
                name="Claude Instant 1.2",
                description="Anthropic's faster, more affordable model from the previous generation.",
                context_window=100000
            )
        ]
    
    async def generate_completion(self, model_id: str, prompt: str, system_prompt: Optional[str] = None, params: Optional[LLMOptions] = None) -> Dict[str, Any]:
        """
        Generates a text completion using Anthropic Claude.
        
        For Claude, we convert this to a chat completion with a single user message.
        
        Args:
            model_id: ID of the model to use
            prompt: Text prompt for completion
            system_prompt: Optional system prompt to guide the model
            params: Optional parameters for generation
            
        Returns:
            Dictionary containing the completion result
        """
        self.logger.info(f"AnthropicProvider: Generating completion for model {model_id}")
        
        # Convert to chat format
        messages = [{"role": "user", "content": prompt}]
        
        # Use the chat completion method
        return await self.generate_chat_completion(model_id, messages, system_prompt, params)
    
    async def generate_chat_completion(self, model_id: str, messages: List[Dict[str, Union[str, List[Dict[str, Any]]]]], system_prompt: Optional[str] = None, params: Optional[LLMOptions] = None) -> Dict[str, Any]:
        """
        Generates a chat completion using Anthropic Claude.
        
        Args:
            model_id: ID of the model to use
            messages: List of message dictionaries with role and content
            system_prompt: Optional system prompt to guide the model
            params: Optional parameters for generation
            
        Returns:
            Dictionary containing the chat completion result
        """
        if not self.api_key:
            return {"error": "API key not configured for AnthropicProvider."}
        
        self.logger.info(f"AnthropicProvider: Generating chat completion for model {model_id}")
        
        try:
            # Import Anthropic SDK
            try:
                import anthropic
                from anthropic import AsyncAnthropic
            except ImportError:
                return {
                    "error": "Anthropic SDK not installed. Please install with 'pip install anthropic'."
                }
            
            # Initialize Anthropic client
            client = AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.api_base
            )
            
            # Convert messages to Anthropic format
            anthropic_messages = []
            
               # Process messages
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                # Map roles from standard format to Anthropic's format
                if role == "user":
                    anthropic_role = "user"
                elif role in ["assistant", "model"]:
                    anthropic_role = "model"
                elif role == "system":
                    # Claude handles system messages differently, store it for later use
                    if system_prompt is None:  # Only use if not already set
                        system_prompt = content
                    continue
                else:
                    # Skip unknown roles
                    continue
                
                # Handle multimodal content if present
                if isinstance(content, str):
                    anthropic_messages.append({"role": anthropic_role, "content": content})
                elif isinstance(content, list):
                    # Handle multimodal content (text and images)
                    anthropic_content = []
                    
                    for part in content:
                        if isinstance(part, str):
                            anthropic_content.append({"type": "text", "text": part})
                        elif isinstance(part, dict) and part.get("type") == "image":
                            # Convert image data to Anthropic's format
                            image_data = part.get("data")
                            if image_data:
                                if image_data.startswith("http"):
                                    # Image URL
                                    anthropic_content.append({
                                        "type": "image",
                                        "source": {
                                            "type": "url",
                                            "url": image_data
                                        }
                                    })
                                else:
                                    # Base64 encoded image
                                    anthropic_content.append({
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/jpeg",
                                            "data": image_data
                                        }
                                    })
                    
                    anthropic_messages.append({"role": anthropic_role, "content": anthropic_content})
            
            # Set up generation parameters
            request_params = {
                "model": model_id,
                "messages": anthropic_messages,
                "max_tokens": 1024  # Default max tokens
            }
            
            # Add system prompt if provided
            if system_prompt:
                request_params["system"] = system_prompt
            
            # Add optional parameters if provided
            if params:
                # Temperature controls randomness (higher = more random)
                if params.get("temperature") is not None:
                    request_params["temperature"] = params["temperature"]
                
                # Max tokens limits response length
                if params.get("max_tokens") is not None:
                    request_params["max_tokens"] = params["max_tokens"]
                
                # Top-p (nucleus sampling) controls diversity
                if params.get("top_p") is not None:
                    request_params["top_p"] = params["top_p"]
                
                # Stop sequences tell the model when to stop generating
                if params.get("stop_sequences"):
                    request_params["stop_sequences"] = params["stop_sequences"]
                
                # Stream parameter for streaming responses
                if params.get("stream") is not None:
                    request_params["stream"] = params["stream"]
            
            # Make the API call
            response = await client.messages.create(**request_params)
            
            # Extract response text
            response_text = response.content[0].text if response.content else ""
            
            # Extract usage information
            usage_info = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            # Extract finish reason
            finish_reason = response.stop_reason
            
            return {
                "text": response_text,
                "usage": usage_info,
                "error": None,
                "model": model_id,
                "finish_reason": finish_reason,
                "id": response.id,
                "created": int(datetime.now().timestamp()),  # Anthropic doesn't provide this directly
                "content_type": "text"
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.logger.error(f"Error generating completion with Anthropic: {str(e)}\n{error_details}")
            return {
                "error": f"Error generating completion with Anthropic: {str(e)}",
                "error_details": error_details
            }
    
    def _map_model_id(self, model_id: str) -> str:
        """
        Maps internal model IDs to Anthropic model IDs if needed.
        
        Args:
            model_id: Internal model ID
            
        Returns:
            Anthropic model ID
        """
        # Map of internal model IDs to Anthropic model IDs
        model_map = {
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-sonnet-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307"
        }
        
        return model_map.get(model_id, model_id)
