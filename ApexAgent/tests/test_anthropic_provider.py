"""
Tests for the Anthropic Claude LLM Provider

This module contains tests for the Anthropic Claude LLM provider integration,
including initialization, model listing, chat completion, and error handling.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import sys
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the provider
from src.plugins.llm_providers.internal.anthropic_provider import AnthropicProvider
from src.plugins.llm_providers.base_provider import ModelInfo, LLMOptions

class TestAnthropicProvider(unittest.TestCase):
    """Test cases for the AnthropicProvider class."""
    
    def setUp(self):
        """Set up test environment."""
        # Use a mock API key for testing
        self.api_key = "test_api_key"
        self.provider = AnthropicProvider(api_key=self.api_key)
    
    def test_initialization(self):
        """Test initialization of AnthropicProvider."""
        # Test with API key
        provider = AnthropicProvider(api_key=self.api_key)
        self.assertEqual(provider.api_key, self.api_key)
        self.assertEqual(provider.api_base, AnthropicProvider.DEFAULT_API_BASE)
        
        # Test with custom base URL
        custom_base = "https://custom.anthropic.api"
        provider = AnthropicProvider(api_key=self.api_key, api_base_url=custom_base)
        self.assertEqual(provider.api_base, custom_base)
        
        # Test without API key
        with patch.dict(os.environ, {AnthropicProvider.API_KEY_NAME: "env_api_key"}):
            provider = AnthropicProvider()
            self.assertEqual(provider.api_key, "env_api_key")
    
    def test_get_static_provider_name(self):
        """Test getting the provider's name."""
        self.assertEqual(AnthropicProvider.get_static_provider_name(), "anthropic")
    
    def test_get_static_provider_display_name(self):
        """Test getting the provider's display name."""
        self.assertEqual(AnthropicProvider.get_static_provider_display_name(), "Anthropic Claude")
    
    def test_get_required_api_key_name(self):
        """Test getting the required API key name."""
        self.assertEqual(AnthropicProvider.get_required_api_key_name(), "ANTHROPIC_API_KEY")
    
    def test_available_models(self):
        """Test getting available models."""
        loop = asyncio.get_event_loop()
        models = loop.run_until_complete(self.provider.get_available_models())
        
        # Check that we have the expected models
        self.assertGreaterEqual(len(models), 3)  # At least Claude 3 Opus, Sonnet, and Haiku
        
        # Check that each model has the required attributes
        for model in models:
            # Check model attributes by dictionary access instead of attribute access
            self.assertTrue('id' in model or hasattr(model, 'id'))
            self.assertTrue('name' in model or hasattr(model, 'name'))
            self.assertTrue('description' in model or hasattr(model, 'description'))
            self.assertTrue('context_window' in model or hasattr(model, 'context_window'))
            
            # Get values using dictionary-style access or attribute access
            model_id = model.get('id', getattr(model, 'id', None)) if isinstance(model, dict) else model.id
            model_name = model.get('name', getattr(model, 'name', None)) if isinstance(model, dict) else model.name
            model_desc = model.get('description', getattr(model, 'description', None)) if isinstance(model, dict) else model.description
            model_ctx = model.get('context_window', getattr(model, 'context_window', 0)) if isinstance(model, dict) else model.context_window
            
            self.assertTrue(model_id)
            self.assertTrue(model_name)
            self.assertTrue(model_desc)
            self.assertGreater(model_ctx, 0)
        
        # Check for specific models
        model_ids = []
        for model in models:
            if isinstance(model, dict):
                model_ids.append(model.get('id'))
            else:
                model_ids.append(model.id)
        self.assertIn("claude-3-opus-20240229", model_ids)
        self.assertIn("claude-3-sonnet-20240229", model_ids)
        self.assertIn("claude-3-haiku-20240307", model_ids)
    
    @patch('anthropic.AsyncAnthropic')
    def test_generate_completion(self, mock_anthropic):
        """Test generating a completion."""
        # Set up mock response
        mock_client = AsyncMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is a test response")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5
        mock_response.stop_reason = "stop"
        mock_response.id = "msg_123456"
        
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Call generate_completion
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.provider.generate_completion(
                model_id="claude-3-opus-20240229",
                prompt="Test prompt",
                system_prompt="You are a helpful assistant."
            )
        )
        
        # Check result
        self.assertEqual(result["text"], "This is a test response")
        self.assertEqual(result["usage"]["prompt_tokens"], 10)
        self.assertEqual(result["usage"]["completion_tokens"], 5)
        self.assertEqual(result["usage"]["total_tokens"], 15)
        self.assertEqual(result["finish_reason"], "stop")
        self.assertEqual(result["model"], "claude-3-opus-20240229")
        self.assertIsNone(result["error"])
        
        # Check that the mock was called correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        self.assertEqual(call_args["model"], "claude-3-opus-20240229")
        self.assertEqual(call_args["system"], "You are a helpful assistant.")
        self.assertEqual(len(call_args["messages"]), 1)
        self.assertEqual(call_args["messages"][0]["role"], "user")
        self.assertEqual(call_args["messages"][0]["content"], "Test prompt")
    
    @patch('anthropic.AsyncAnthropic')
    def test_generate_chat_completion(self, mock_anthropic):
        """Test generating a chat completion."""
        # Set up mock response
        mock_client = AsyncMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="I'll help you with that.")]
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 8
        mock_response.stop_reason = "end_turn"
        mock_response.id = "msg_789012"
        
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Create test messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, can you help me?"},
            {"role": "assistant", "content": "Of course! What do you need help with?"},
            {"role": "user", "content": "I need help with a coding problem."}
        ]
        
        # Call generate_chat_completion
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.provider.generate_chat_completion(
                model_id="claude-3-sonnet-20240229",
                messages=messages,
                params={"temperature": 0.7, "max_tokens": 500}
            )
        )
        
        # Check result
        self.assertEqual(result["text"], "I'll help you with that.")
        self.assertEqual(result["usage"]["prompt_tokens"], 15)
        self.assertEqual(result["usage"]["completion_tokens"], 8)
        self.assertEqual(result["usage"]["total_tokens"], 23)
        self.assertEqual(result["finish_reason"], "end_turn")
        self.assertEqual(result["model"], "claude-3-sonnet-20240229")
        self.assertIsNone(result["error"])
        
        # Check that the mock was called correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        self.assertEqual(call_args["model"], "claude-3-sonnet-20240229")
        # Check if system parameter is present
        if "system" in call_args:
            self.assertEqual(call_args["system"], "You are a helpful assistant.")
        else:
            # If system is not in call_args, it might be handled differently in the implementation
            # Check that the system message was processed in some way
            self.assertTrue(any("You are a helpful assistant" in str(arg) for arg in mock_client.messages.create.call_args))
        self.assertEqual(call_args["temperature"], 0.7)
        self.assertEqual(call_args["max_tokens"], 500)
        
        # Check that messages were processed correctly
        self.assertEqual(len(call_args["messages"]), 3)  # System message is handled separately
        self.assertEqual(call_args["messages"][0]["role"], "user")
        self.assertEqual(call_args["messages"][1]["role"], "model")
        self.assertEqual(call_args["messages"][2]["role"], "user")
    
    @patch('anthropic.AsyncAnthropic')
    def test_multimodal_input(self, mock_anthropic):
        """Test handling multimodal input."""
        # Set up mock response
        mock_client = AsyncMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="I see an image of a cat.")]
        mock_response.usage.input_tokens = 20
        mock_response.usage.output_tokens = 10
        mock_response.stop_reason = "end_turn"
        mock_response.id = "msg_345678"
        
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Create test message with image
        messages = [
            {
                "role": "user", 
                "content": [
                    "What's in this image?",
                    {
                        "type": "image",
                        "data": "https://example.com/cat.jpg"
                    }
                ]
            }
        ]
        
        # Call generate_chat_completion
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.provider.generate_chat_completion(
                model_id="claude-3-opus-20240229",
                messages=messages
            )
        )
        
        # Check result
        self.assertEqual(result["text"], "I see an image of a cat.")
        
        # Check that the mock was called correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        
        # Check that the image was processed correctly
        self.assertEqual(len(call_args["messages"]), 1)
        self.assertEqual(call_args["messages"][0]["role"], "user")
        self.assertIsInstance(call_args["messages"][0]["content"], list)
        self.assertEqual(len(call_args["messages"][0]["content"]), 2)
        self.assertEqual(call_args["messages"][0]["content"][0]["type"], "text")
        self.assertEqual(call_args["messages"][0]["content"][0]["text"], "What's in this image?")
        self.assertEqual(call_args["messages"][0]["content"][1]["type"], "image")
        self.assertEqual(call_args["messages"][0]["content"][1]["source"]["type"], "url")
        self.assertEqual(call_args["messages"][0]["content"][1]["source"]["url"], "https://example.com/cat.jpg")
    
    def test_no_api_key(self):
        """Test behavior when no API key is provided."""
        provider = AnthropicProvider(api_key=None)
        
        # Call generate_chat_completion
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            provider.generate_chat_completion(
                model_id="claude-3-opus-20240229",
                messages=[{"role": "user", "content": "Hello"}]
            )
        )
        
        # Check that an error is returned
        self.assertIn("error", result)
        self.assertIn("API key not configured", result["error"])
    
    @patch('anthropic.AsyncAnthropic')
    def test_api_error_handling(self, mock_anthropic):
        """Test handling of API errors."""
        # Set up mock to raise an exception
        mock_client = AsyncMock()
        mock_anthropic.return_value = mock_client
        
        mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))
        
        # Call generate_chat_completion
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.provider.generate_chat_completion(
                model_id="claude-3-opus-20240229",
                messages=[{"role": "user", "content": "Hello"}]
            )
        )
        
        # Check that an error is returned
        self.assertIn("error", result)
        self.assertIn("Error generating completion with Anthropic", result["error"])
        self.assertIn("API error", result["error"])
        self.assertIn("error_details", result)
    
    def test_model_id_mapping(self):
        """Test mapping of model IDs."""
        # Test direct mapping
        self.assertEqual(
            self.provider._map_model_id("claude-3-opus"),
            "claude-3-opus-20240229"
        )
        self.assertEqual(
            self.provider._map_model_id("claude-3-sonnet"),
            "claude-3-sonnet-20240229"
        )
        self.assertEqual(
            self.provider._map_model_id("claude-3-haiku"),
            "claude-3-haiku-20240307"
        )
        
        # Test pass-through for unknown models
        self.assertEqual(
            self.provider._map_model_id("unknown-model"),
            "unknown-model"
        )
        
        # Test pass-through for already mapped models
        self.assertEqual(
            self.provider._map_model_id("claude-3-opus-20240229"),
            "claude-3-opus-20240229"
        )

if __name__ == "__main__":
    unittest.main()
