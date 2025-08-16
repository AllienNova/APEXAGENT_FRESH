# src/plugins/llm_providers/internal/anthropic_claude_provider.py
import os
from typing import List, Dict, Any, Optional
import anthropic # Ensure 'anthropic' is in requirements.txt

from src.plugins.llm_providers.base_provider import LLMProvider, ModelInfo

class AnthropicClaudeProvider(LLMProvider):
    # Class variable for API key name, used by APIKeyManager and LLMManager
    API_KEY_NAME = "ANTHROPIC_API_KEY"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        if not self.api_key:
            # In a real scenario, APIKeyManager would fetch this.
            # For direct instantiation or testing, it might be passed or read from env.
            self.api_key = os.environ.get(self.API_KEY_NAME)
        
        if not self.api_key:
            # This provider cannot function without an API key.
            # The LLMManager or PluginManager should handle this state gracefully.
            print(f"Warning: {self.get_provider_display_name()} initialized without an API key. It will not be functional.")
            self.client = None
        else:
            try:
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing Anthropic client for {self.get_provider_display_name()}: {e}")
                self.client = None

    def get_provider_name(self) -> str:
        return "anthropic_claude"

    def get_provider_display_name(self) -> str:
        return "Anthropic Claude"

    @classmethod
    def get_required_api_key_name(cls) -> Optional[str]:
        return cls.API_KEY_NAME

    def get_available_models(self) -> List[ModelInfo]:
        # This is a static list for the example. A real provider might query an API.
        # Ensure these model IDs are valid for the Anthropic API.
        return [
            {
                "id": "claude-3-opus-20240229", 
                "name": "Claude 3 Opus", 
                "description": "Most powerful model for highly complex tasks.",
                "context_window": 200000
            },
            {
                "id": "claude-3-sonnet-20240229", 
                "name": "Claude 3 Sonnet", 
                "description": "Ideal balance of intelligence and speed for enterprise workloads.",
                "context_window": 200000
            },
            {
                "id": "claude-3-haiku-20240307", 
                "name": "Claude 3 Haiku", 
                "description": "Fastest and most compact model for near-instant responsiveness.",
                "context_window": 200000
            },
            {
                "id": "claude-2.1", 
                "name": "Claude 2.1", 
                "description": "Updated Claude 2 model with a 200K context window.",
                "context_window": 200000
            },
            {
                "id": "claude-2.0", 
                "name": "Claude 2.0", 
                "description": "Predecessor to Claude 3, with a 100K context window.",
                "context_window": 100000
            }
        ]

    async def generate_completion(self, model_id: str, prompt: str, system_prompt: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.client:
            return {"text": None, "error": f"{self.get_provider_display_name()} is not configured (missing API key or client initialization failed)."}
        
        merged_params = {
            "max_tokens": 1024, # Default, can be overridden by params
            **(params or {})
        }

        try:
            # Anthropic uses a messages-based API even for "completions" in the traditional sense.
            # We adapt the single prompt to the messages format.
            messages_payload = []
            if system_prompt:
                 # Anthropic API expects system prompt at top level for newer models, not in messages for older ones.
                # For claude-3 models, system prompt is a top-level parameter.
                # For older models, it might need to be part of the first user message or handled differently.
                if model_id.startswith("claude-2"):
                    # For Claude 2.x models, include system prompt in the first user message
                    system_prefix = f"{system_prompt}\n\n"
                    messages_payload.append({"role": "user", "content": system_prefix + prompt})
                    return messages_payload
            
            messages_payload.append({"role": "user", "content": prompt})

            completion_args = {
                "model": model_id,
                "messages": messages_payload,
                "max_tokens": merged_params["max_tokens"]
            }
            if system_prompt:
                completion_args["system"] = system_prompt
            if "temperature" in merged_params:
                completion_args["temperature"] = merged_params["temperature"]
            # Add other supported parameters as needed

            response = await self.client.messages.create(**completion_args)
            
            text_response = ""
            if response.content and isinstance(response.content, list):
                for block in response.content:
                    if hasattr(block, "text"):
                        text_response += block.text
            
            return {
                "text": text_response,
                "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
                "error": None,
                "raw_response": response.model_dump() # Optional: for debugging or more detailed info
            }
        except anthropic.APIConnectionError as e:
            return {"text": None, "error": f"Anthropic API connection error: {e}"}
        except anthropic.RateLimitError as e:
            return {"text": None, "error": f"Anthropic API rate limit exceeded: {e}"}
        except anthropic.APIStatusError as e:
            return {"text": None, "error": f"Anthropic API status error {e.status_code}: {e.response}"}
        except Exception as e:
            return {"text": None, "error": f"Error during Anthropic completion: {str(e)}"}

    async def generate_chat_completion(self, model_id: str, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.client:
            return {"text": None, "error": f"{self.get_provider_display_name()} is not configured (missing API key or client initialization failed)."}

        merged_params = {
            "max_tokens": 1024, # Default, can be overridden by params
            **(params or {})
        }

        try:
            completion_args = {
                "model": model_id,
                "messages": messages,
                "max_tokens": merged_params["max_tokens"]
            }
            if system_prompt:
                completion_args["system"] = system_prompt
            if "temperature" in merged_params:
                completion_args["temperature"] = merged_params["temperature"]
            # Add other supported parameters

            response = await self.client.messages.create(**completion_args)
            
            text_response = ""
            if response.content and isinstance(response.content, list):
                for block in response.content:
                    if hasattr(block, "text"):
                        text_response += block.text

            return {
                "text": text_response,
                "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
                "error": None,
                "raw_response": response.model_dump()
            }
        except anthropic.APIConnectionError as e:
            return {"text": None, "error": f"Anthropic API connection error: {e}"}
        except anthropic.RateLimitError as e:
            return {"text": None, "error": f"Anthropic API rate limit exceeded: {e}"}
        except anthropic.APIStatusError as e:
            return {"text": None, "error": f"Anthropic API status error {e.status_code}: {e.response}"}
        except Exception as e:
            return {"text": None, "error": f"Error during Anthropic chat completion: {str(e)}"}

# To make this discoverable, place it in a directory scanned by PluginManager,
# e.g., /home/ubuntu/agent_project/src/plugins/llm_providers/internal/anthropic_claude_provider.py

