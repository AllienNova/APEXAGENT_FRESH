"""
Test suite for Together AI integration.

This module implements comprehensive tests for Together AI integration,
ensuring all components work correctly and reliably.
"""

import unittest
import asyncio
import json
import os
import time
from unittest import mock
from typing import Dict, Any, List, Optional

# Import components to test
from src.plugins.llm_providers.internal.together_ai_provider import TogetherAIProvider
from src.api_key_management.together_ai_key_manager import (
    TogetherAIKeyManager,
    get_together_ai_key_manager
)
from src.api_key_management.together_ai_model_selector import (
    TogetherAIModelSelector,
    get_together_ai_model_selector,
    ModelModality,
    ModelPurpose
)
from src.api_key_management.together_ai_fallback import (
    TogetherAIFallbackManager,
    get_together_ai_fallback_manager,
    FallbackStrategy
)
from src.api_key_management.together_ai_free_tier import (
    TogetherAIFreeTierManager,
    get_together_ai_free_tier_manager,
    FreeTierFeature,
    FreeTierQuotaType
)
from src.api_key_management.together_ai_ui_indicators import (
    TogetherAIIndicatorManager,
    get_together_ai_indicator_manager,
    ModelSourceIndicator,
    ProviderIndicatorType,
    ProviderIndicatorPosition
)
from src.api_key_management.together_ai_registration import (
    register_together_ai_provider,
    initialize_together_ai_integration
)

# Mock dependencies
from src.user.subscription import UserTier
from src.llm_providers.provider_manager import ProviderManager
from src.llm_providers.core.provider_interface import LLMError, LLMErrorType


class TestTogetherAIProvider(unittest.TestCase):
    """Test the Together AI provider implementation."""
    
    def setUp(self):
        """Set up test environment."""
        # Create provider with mock API key
        self.api_key = "test_api_key_12345"
        self.provider = TogetherAIProvider(api_key=self.api_key)
        
        # Mock API responses
        self.mock_completion_response = {
            "id": "cmpl-12345",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "choices": [
                {
                    "text": "This is a test response.",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        
        self.mock_chat_response = {
            "id": "chatcmpl-12345",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "This is a test response."
                    },
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 5,
                "total_tokens": 20
            }
        }
        
        self.mock_image_response = {
            "created": int(time.time()),
            "data": [
                {
                    "url": "https://example.com/image.png"
                }
            ]
        }
    
    @mock.patch("src.plugins.llm_providers.internal.together_ai_provider.requests.post")
    def test_generate_completion(self, mock_post):
        """Test text completion generation."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_completion_response
        mock_post.return_value = mock_response
        
        # Call method
        result = asyncio.run(self.provider.generate_completion(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            prompt="Test prompt"
        ))
        
        # Verify result
        self.assertEqual(result["text"], "This is a test response.")
        self.assertEqual(result["usage"]["total_tokens"], 15)
        
        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.api_key}")
    
    @mock.patch("src.plugins.llm_providers.internal.together_ai_provider.requests.post")
    def test_generate_chat_completion(self, mock_post):
        """Test chat completion generation."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_chat_response
        mock_post.return_value = mock_response
        
        # Call method
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        result = asyncio.run(self.provider.generate_chat_completion(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=messages
        ))
        
        # Verify result
        self.assertEqual(result["message"]["content"], "This is a test response.")
        self.assertEqual(result["usage"]["total_tokens"], 20)
        
        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(kwargs["json"]["messages"], messages)
    
    @mock.patch("src.plugins.llm_providers.internal.together_ai_provider.requests.post")
    def test_generate_image(self, mock_post):
        """Test image generation."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_image_response
        mock_post.return_value = mock_response
        
        # Call method
        result = asyncio.run(self.provider.generate_image(
            prompt="A beautiful sunset",
            model="stabilityai/stable-diffusion-xl-base-1.0"
        ))
        
        # Verify result
        self.assertEqual(result["url"], "https://example.com/image.png")
        
        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(kwargs["json"]["prompt"], "A beautiful sunset")
    
    @mock.patch("src.plugins.llm_providers.internal.together_ai_provider.requests.post")
    def test_error_handling(self, mock_post):
        """Test error handling."""
        # Mock error response
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_post.return_value = mock_response
        
        # Call method and expect exception
        with self.assertRaises(LLMError) as context:
            asyncio.run(self.provider.generate_completion(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                prompt="Test prompt"
            ))
        
        # Verify exception
        self.assertEqual(context.exception.error_type, LLMErrorType.AUTHENTICATION)
    
    def test_provider_metadata(self):
        """Test provider metadata."""
        # Verify provider name
        self.assertEqual(self.provider.get_provider_name(), "together_ai")
        
        # Verify supported models
        supported_models = self.provider.get_supported_models()
        self.assertIn("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", supported_models)
        self.assertIn("stabilityai/stable-diffusion-xl-base-1.0", supported_models)
        
        # Verify capabilities
        self.assertTrue(self.provider.supports_streaming())
        self.assertTrue(self.provider.supports_function_calling())


class TestTogetherAIKeyManager(unittest.TestCase):
    """Test the Together AI key manager."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary key file path
        self.temp_key_file = "/tmp/test_together_ai_keys.enc"
        
        # Create key manager with test config
        self.key_manager = TogetherAIKeyManager(config_dir="/tmp")
        self.key_manager.KEY_FILE_PATH = "test_together_ai_keys.enc"
        
        # Set test keys
        self.system_key = "test_system_key_12345"
        self.user_key = "test_user_key_67890"
        self.user_id = "test_user_123"
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary key file
        if os.path.exists(self.temp_key_file):
            os.remove(self.temp_key_file)
    
    def test_set_get_system_key(self):
        """Test setting and getting system key."""
        # Set system key
        result = self.key_manager.set_system_key(self.system_key)
        self.assertTrue(result)
        
        # Get system key
        key = self.key_manager.get_system_key()
        self.assertEqual(key, self.system_key)
    
    def test_set_get_user_key(self):
        """Test setting and getting user key."""
        # Set user key
        result = self.key_manager.set_user_key(self.user_id, self.user_key)
        self.assertTrue(result)
        
        # Get user key
        key = self.key_manager.get_user_key(self.user_id)
        self.assertEqual(key, self.user_key)
    
    def test_get_api_key_precedence(self):
        """Test API key precedence."""
        # Set both system and user keys
        self.key_manager.set_system_key(self.system_key)
        self.key_manager.set_user_key(self.user_id, self.user_key)
        
        # User key should take precedence
        key = self.key_manager.get_api_key(self.user_id)
        self.assertEqual(key, self.user_key)
        
        # System key should be used for unknown user
        key = self.key_manager.get_api_key("unknown_user")
        self.assertEqual(key, self.system_key)
    
    def test_delete_user_key(self):
        """Test deleting user key."""
        # Set user key
        self.key_manager.set_user_key(self.user_id, self.user_key)
        
        # Delete user key
        result = self.key_manager.delete_user_key(self.user_id)
        self.assertTrue(result)
        
        # Verify key is deleted
        key = self.key_manager.get_user_key(self.user_id)
        self.assertIsNone(key)
    
    def test_key_persistence(self):
        """Test key persistence across instances."""
        # Set keys
        self.key_manager.set_system_key(self.system_key)
        self.key_manager.set_user_key(self.user_id, self.user_key)
        
        # Create new instance
        new_manager = TogetherAIKeyManager(config_dir="/tmp")
        new_manager.KEY_FILE_PATH = "test_together_ai_keys.enc"
        
        # Verify keys are loaded
        self.assertEqual(new_manager.get_system_key(), self.system_key)
        self.assertEqual(new_manager.get_user_key(self.user_id), self.user_key)
    
    def test_rotate_system_key(self):
        """Test rotating system key."""
        # Set initial system key
        self.key_manager.set_system_key(self.system_key)
        
        # Rotate key
        new_key = "new_system_key_54321"
        result = self.key_manager.rotate_system_key(new_key)
        self.assertTrue(result)
        
        # Verify new key is set
        self.assertEqual(self.key_manager.get_system_key(), new_key)


class TestTogetherAIModelSelector(unittest.TestCase):
    """Test the Together AI model selector."""
    
    def setUp(self):
        """Set up test environment."""
        self.model_selector = TogetherAIModelSelector()
        self.user_id = "test_user_123"
    
    @mock.patch("src.api_key_management.together_ai_model_selector.get_user_tier")
    def test_get_model_for_user(self, mock_get_user_tier):
        """Test getting model for user based on tier."""
        # Test FREE tier
        mock_get_user_tier.return_value = UserTier.FREE
        model_id = self.model_selector.get_model_for_user(
            user_id=self.user_id,
            modality=ModelModality.TEXT
        )
        self.assertEqual(model_id, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        
        # Test PREMIUM tier
        mock_get_user_tier.return_value = UserTier.PREMIUM
        model_id = self.model_selector.get_model_for_user(
            user_id=self.user_id,
            modality=ModelModality.TEXT
        )
        self.assertEqual(model_id, "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo")
        
        # Test ENTERPRISE tier
        mock_get_user_tier.return_value = UserTier.ENTERPRISE
        model_id = self.model_selector.get_model_for_user(
            user_id=self.user_id,
            modality=ModelModality.TEXT
        )
        self.assertEqual(model_id, "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo")
    
    def test_get_model_for_purpose(self):
        """Test getting model for specific purpose."""
        # Test CRITICAL purpose for PREMIUM tier
        model_id = self.model_selector.get_model_for_user(
            user_id=self.user_id,
            modality=ModelModality.TEXT,
            purpose=ModelPurpose.CRITICAL,
            override_tier=UserTier.PREMIUM
        )
        self.assertEqual(model_id, "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo")
        
        # Test FAST purpose for PREMIUM tier
        model_id = self.model_selector.get_model_for_user(
            user_id=self.user_id,
            modality=ModelModality.IMAGE,
            purpose=ModelPurpose.FAST,
            override_tier=UserTier.PREMIUM
        )
        self.assertEqual(model_id, "stabilityai/sdxl-turbo")
    
    def test_get_fallback_model(self):
        """Test getting fallback model."""
        # Test fallback for TEXT modality
        primary_model = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
        fallback_model = self.model_selector.get_fallback_model(
            user_id=self.user_id,
            modality=ModelModality.TEXT,
            primary_model_id=primary_model
        )
        self.assertEqual(fallback_model, "mistralai/Mixtral-8x7B-Instruct-v0.1")
        
        # Test fallback for CODE modality
        primary_model = "deepseek-ai/deepseek-coder-33b-instruct"
        fallback_model = self.model_selector.get_fallback_model(
            user_id=self.user_id,
            modality=ModelModality.CODE,
            primary_model_id=primary_model
        )
        self.assertEqual(fallback_model, "Nexusflow/NexusRaven-V2-13B")
    
    @mock.patch("src.api_key_management.together_ai_model_selector.get_together_ai_key_manager")
    def test_get_provider_with_model(self, mock_get_key_manager):
        """Test getting provider with model."""
        # Mock key manager
        mock_key_manager = mock.Mock()
        mock_key_manager.get_api_key.return_value = "test_api_key"
        mock_get_key_manager.return_value = mock_key_manager
        
        # Get provider with model
        result = self.model_selector.get_provider_with_model(
            user_id=self.user_id,
            modality=ModelModality.TEXT
        )
        
        # Verify result
        self.assertIsNotNone(result["provider"])
        self.assertIsNotNone(result["model_id"])
        self.assertIsNone(result["error"])
        
        # Test error case
        mock_key_manager.get_api_key.return_value = None
        result = self.model_selector.get_provider_with_model(
            user_id=self.user_id,
            modality=ModelModality.TEXT
        )
        self.assertIsNotNone(result["error"])


class TestTogetherAIFallbackManager(unittest.TestCase):
    """Test the Together AI fallback manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.fallback_manager = TogetherAIFallbackManager()
        self.user_id = "test_user_123"
        
        # Mock operation for testing
        async def mock_operation(provider, model_id, input_data):
            if model_id == "failing_model":
                raise LLMError("Test error", LLMErrorType.SERVICE_UNAVAILABLE)
            return {"result": f"Success with {model_id}"}
        
        self.mock_operation = mock_operation
    
    @mock.patch("src.api_key_management.together_ai_fallback.get_together_ai_model_selector")
    @mock.patch("src.api_key_management.together_ai_fallback.get_together_ai_key_manager")
    async def test_execute_with_fallback_success(self, mock_get_key_manager, mock_get_model_selector):
        """Test successful execution without fallback."""
        # Mock dependencies
        mock_model_selector = mock.Mock()
        mock_model_selector.get_provider_with_model.return_value = {
            "provider": mock.Mock(),
            "model_id": "success_model",
            "error": None
        }
        mock_get_model_selector.return_value = mock_model_selector
        
        # Execute with fallback
        result = await self.fallback_manager.execute_with_fallback(
            user_id=self.user_id,
            modality=ModelModality.TEXT,
            operation=self.mock_operation,
            input_data="Test input"
        )
        
        # Verify result
        self.assertEqual(result["result"], "Success with success_model")
        self.assertEqual(result["fallback_used"], False)
    
    @mock.patch("src.api_key_management.together_ai_fallback.get_together_ai_model_selector")
    @mock.patch("src.api_key_management.together_ai_fallback.get_together_ai_key_manager")
    async def test_execute_with_fallback_failure(self, mock_get_key_manager, mock_get_model_selector):
        """Test execution with fallback after failure."""
        # Mock dependencies
        mock_model_selector = mock.Mock()
        mock_model_selector.get_provider_with_model.return_value = {
            "provider": mock.Mock(),
            "model_id": "failing_model",
            "error": None
        }
        mock_model_selector.get_fallback_model.return_value = "fallback_model"
        mock_get_model_selector.return_value = mock_model_selector
        
        mock_key_manager = mock.Mock()
        mock_key_manager.get_api_key.return_value = "test_api_key"
        mock_get_key_manager.return_value = mock_key_manager
        
        # Execute with fallback
        result = await self.fallback_manager.execute_with_fallback(
            user_id=self.user_id,
            modality=ModelModality.TEXT,
            operation=self.mock_operation,
            input_data="Test input",
            fallback_strategies=[FallbackStrategy.SAME_PROVIDER_DIFFERENT_MODEL]
        )
        
        # Verify result
        self.assertEqual(result["result"], "Success with fallback_model")
        self.assertEqual(result["fallback_used"], True)
        self.assertEqual(result["fallback_strategy"], FallbackStrategy.SAME_PROVIDER_DIFFERENT_MODEL)
    
    @mock.patch("src.api_key_management.together_ai_fallback.get_together_ai_model_selector")
    @mock.patch("src.api_key_management.together_ai_fallback.get_together_ai_key_manager")
    async def test_cached_response_fallback(self, mock_get_key_manager, mock_get_model_selector):
        """Test fallback to cached response."""
        # Mock dependencies
        mock_model_selector = mock.Mock()
        mock_model_selector.get_provider_with_model.return_value = {
            "provider": mock.Mock(),
            "model_id": "success_model",
            "error": None
        }
        mock_get_model_selector.return_value = mock_model_selector
        
        # First call to cache response
        result1 = await self.fallback_manager.execute_with_fallback(
            user_id=self.user_id,
            modality=ModelModality.TEXT,
            operation=self.mock_operation,
            input_data="Test input"
        )
        
        # Change model to failing model
        mock_model_selector.get_provider_with_model.return_value = {
            "provider": mock.Mock(),
            "model_id": "failing_model",
            "error": None
        }
        
        # Second call should use cached response
        result2 = await self.fallback_manager.execute_with_fallback(
            user_id=self.user_id,
            modality=ModelModality.TEXT,
            operation=self.mock_operation,
            input_data="Test input",
            fallback_strategies=[
                FallbackStrategy.SAME_PROVIDER_DIFFERENT_MODEL,
                FallbackStrategy.CACHED_RESPONSE
            ]
        )
        
        # Verify result
        self.assertEqual(result2["result"], "Success with success_model")
        self.assertEqual(result2["fallback_used"], True)
        self.assertEqual(result2["fallback_strategy"], FallbackStrategy.CACHED_RESPONSE)
        self.assertTrue(result2["from_cache"])


class TestTogetherAIFreeTierManager(unittest.TestCase):
    """Test the Together AI free tier manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.free_tier_manager = TogetherAIFreeTierManager()
        self.user_id = "test_user_123"
    
    @mock.patch("src.api_key_management.together_ai_free_tier.get_user_tier")
    @mock.patch("src.api_key_management.together_ai_free_tier.is_feature_enabled")
    def test_can_use_feature(self, mock_is_feature_enabled, mock_get_user_tier):
        """Test checking if user can use feature."""
        # Enable free tier and feature
        mock_is_feature_enabled.return_value = True
        
        # Test FREE tier user
        mock_get_user_tier.return_value = UserTier.FREE
        can_use, reason = self.free_tier_manager.can_use_feature(
            user_id=self.user_id,
            feature=FreeTierFeature.TEXT_GENERATION
        )
        self.assertTrue(can_use)
        
        # Test PREMIUM tier user (should always be allowed)
        mock_get_user_tier.return_value = UserTier.PREMIUM
        can_use, reason = self.free_tier_manager.can_use_feature(
            user_id=self.user_id,
            feature=FreeTierFeature.TEXT_GENERATION
        )
        self.assertTrue(can_use)
        
        # Test quota exceeded
        mock_get_user_tier.return_value = UserTier.FREE
        self.free_tier_manager._increment_usage(
            user_id=self.user_id,
            quota_type=FreeTierQuotaType.REQUESTS_PER_DAY,
            feature=FreeTierFeature.TEXT_GENERATION,
            amount=1000  # Exceed quota
        )
        can_use, reason = self.free_tier_manager.can_use_feature(
            user_id=self.user_id,
            feature=FreeTierFeature.TEXT_GENERATION
        )
        self.assertFalse(can_use)
        self.assertIn("quota exceeded", reason)
    
    @mock.patch("src.api_key_management.together_ai_free_tier.get_user_tier")
    def test_check_token_quota(self, mock_get_user_tier):
        """Test checking token quota."""
        # Test FREE tier user
        mock_get_user_tier.return_value = UserTier.FREE
        
        # Test within token per request quota
        within_quota, reason = self.free_tier_manager.check_token_quota(
            user_id=self.user_id,
            feature=FreeTierFeature.TEXT_GENERATION,
            token_count=1000
        )
        self.assertTrue(within_quota)
        
        # Test exceeding token per request quota
        within_quota, reason = self.free_tier_manager.check_token_quota(
            user_id=self.user_id,
            feature=FreeTierFeature.TEXT_GENERATION,
            token_count=5000
        )
        self.assertFalse(within_quota)
        self.assertIn("Token per request quota exceeded", reason)
        
        # Test PREMIUM tier user (should always be allowed)
        mock_get_user_tier.return_value = UserTier.PREMIUM
        within_quota, reason = self.free_tier_manager.check_token_quota(
            user_id=self.user_id,
            feature=FreeTierFeature.TEXT_GENERATION,
            token_count=5000
        )
        self.assertTrue(within_quota)
    
    def test_record_request(self):
        """Test recording request usage."""
        # Record text request
        self.free_tier_manager.record_request(
            user_id=self.user_id,
            modality=ModelModality.TEXT,
            token_count=100
        )
        
        # Verify usage
        feature = FreeTierFeature.TEXT_GENERATION
        requests_used = self.free_tier_manager._get_usage(
            user_id=self.user_id,
            quota_type=FreeTierQuotaType.REQUESTS_PER_DAY,
            feature=feature
        )
        tokens_used = self.free_tier_manager._get_usage(
            user_id=self.user_id,
            quota_type=FreeTierQuotaType.TOKENS_PER_DAY,
            feature=feature
        )
        
        self.assertEqual(requests_used, 1)
        self.assertEqual(tokens_used, 100)
    
    def test_custom_quota(self):
        """Test setting custom quota."""
        # Set custom quota
        self.free_tier_manager.set_custom_quota(
            user_id=self.user_id,
            quota_type=FreeTierQuotaType.REQUESTS_PER_DAY,
            feature=FreeTierFeature.TEXT_GENERATION,
            value=200
        )
        
        # Verify custom quota
        quota = self.free_tier_manager._get_quota(
            user_id=self.user_id,
            quota_type=FreeTierQuotaType.REQUESTS_PER_DAY,
            feature=FreeTierFeature.TEXT_GENERATION
        )
        
        self.assertEqual(quota, 200)


class TestTogetherAIIndicatorManager(unittest.TestCase):
    """Test the Together AI indicator manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.indicator_manager = TogetherAIIndicatorManager()
        self.user_id = "test_user_123"
    
    def test_create_indicator(self):
        """Test creating model source indicator."""
        # Create indicator
        indicator = self.indicator_manager.create_indicator(
            provider_id="together_ai",
            model_id="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            is_fallback=False,
            is_free_tier=True
        )
        
        # Verify indicator
        self.assertEqual(indicator.provider_id, "together_ai")
        self.assertEqual(indicator.model_id, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        self.assertEqual(indicator.display_name, "Together AI")
        self.assertTrue(indicator.is_free_tier)
        self.assertFalse(indicator.is_fallback)
    
    def test_add_indicator_to_response(self):
        """Test adding indicator to API response."""
        # Create response
        response = {
            "text": "This is a test response.",
            "provider": "together_ai",
            "model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "fallback_used": True,
            "is_free_tier": True
        }
        
        # Add indicator
        result = self.indicator_manager.add_indicator_to_response(response)
        
        # Verify indicator in response
        self.assertIn("model_source_indicator", result)
        indicator = result["model_source_indicator"]
        self.assertEqual(indicator["provider_id"], "together_ai")
        self.assertEqual(indicator["model_id"], "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        self.assertTrue(indicator["is_fallback"])
        self.assertTrue(indicator["is_free_tier"])
    
    @mock.patch("src.api_key_management.together_ai_ui_indicators.get_user_tier")
    @mock.patch("src.api_key_management.together_ai_ui_indicators.get_together_ai_model_selector")
    def test_get_indicator_for_user_request(self, mock_get_model_selector, mock_get_user_tier):
        """Test getting indicator for user request."""
        # Mock dependencies
        mock_model_selector = mock.Mock()
        mock_model_selector.get_model_for_user.return_value = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        mock_get_model_selector.return_value = mock_model_selector
        
        # Test FREE tier
        mock_get_user_tier.return_value = UserTier.FREE
        indicator = self.indicator_manager.get_indicator_for_user_request(
            user_id=self.user_id,
            modality=ModelModality.TEXT
        )
        
        # Verify indicator
        self.assertEqual(indicator.provider_id, "together_ai")
        self.assertEqual(indicator.model_id, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        self.assertTrue(indicator.is_free_tier)
        
        # Test PREMIUM tier
        mock_get_user_tier.return_value = UserTier.PREMIUM
        indicator = self.indicator_manager.get_indicator_for_user_request(
            user_id=self.user_id,
            modality=ModelModality.TEXT
        )
        
        # Verify indicator
        self.assertFalse(indicator.is_free_tier)


class TestTogetherAIRegistration(unittest.TestCase):
    """Test the Together AI registration."""
    
    def setUp(self):
        """Set up test environment."""
        self.provider_manager = mock.Mock(spec=ProviderManager)
    
    @mock.patch("src.api_key_management.together_ai_registration.get_together_ai_key_manager")
    def test_register_together_ai_provider(self, mock_get_key_manager):
        """Test registering Together AI provider."""
        # Mock key manager
        mock_key_manager = mock.Mock()
        mock_key_manager.get_system_key.return_value = "test_api_key"
        mock_get_key_manager.return_value = mock_key_manager
        
        # Register provider
        result = register_together_ai_provider(self.provider_manager)
        
        # Verify result
        self.assertTrue(result)
        
        # Verify provider registration
        self.provider_manager.register_provider.assert_called_once()
        args, kwargs = self.provider_manager.register_provider.call_args
        self.assertEqual(args[0], "together_ai")
    
    @mock.patch("src.api_key_management.together_ai_registration.get_provider_manager")
    @mock.patch("src.api_key_management.together_ai_registration.register_together_ai_provider")
    def test_initialize_together_ai_integration(self, mock_register, mock_get_provider_manager):
        """Test initializing Together AI integration."""
        # Mock dependencies
        mock_provider_manager = mock.Mock()
        mock_get_provider_manager.return_value = mock_provider_manager
        mock_register.return_value = True
        
        # Initialize integration
        result = initialize_together_ai_integration()
        
        # Verify result
        self.assertTrue(result)
        
        # Verify provider registration
        mock_register.assert_called_once_with(mock_provider_manager)


class TestIntegrationTests(unittest.TestCase):
    """Integration tests for Together AI components."""
    
    def setUp(self):
        """Set up test environment."""
        self.user_id = "test_user_123"
        
        # Create components
        self.key_manager = get_together_ai_key_manager()
        self.model_selector = get_together_ai_model_selector()
        self.fallback_manager = get_together_ai_fallback_manager()
        self.free_tier_manager = get_together_ai_free_tier_manager()
        self.indicator_manager = get_together_ai_indicator_manager()
        
        # Set test API key
        self.api_key = "test_api_key_12345"
        self.key_manager.set_system_key(self.api_key)
    
    @mock.patch("src.api_key_management.together_ai_model_selector.get_user_tier")
    @mock.patch("src.plugins.llm_providers.internal.together_ai_provider.requests.post")
    async def test_end_to_end_text_generation(self, mock_post, mock_get_user_tier):
        """Test end-to-end text generation flow."""
        # Mock user tier
        mock_get_user_tier.return_value = UserTier.FREE
        
        # Mock API response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "cmpl-12345",
            "object": "text_completion",
            "created": int(time.time()),
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "choices": [
                {
                    "text": "This is a test response.",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_post.return_value = mock_response
        
        # Check if user can use text generation
        can_use, reason = self.free_tier_manager.can_use_feature(
            user_id=self.user_id,
            feature=FreeTierFeature.TEXT_GENERATION
        )
        self.assertTrue(can_use)
        
        # Get model for user
        model_id = self.model_selector.get_model_for_user(
            user_id=self.user_id,
            modality=ModelModality.TEXT
        )
        self.assertEqual(model_id, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        
        # Create provider
        provider = TogetherAIProvider(api_key=self.api_key)
        
        # Generate text
        prompt = "This is a test prompt."
        result = await provider.generate_completion(model_id, prompt)
        
        # Record usage
        self.free_tier_manager.record_request(
            user_id=self.user_id,
            modality=ModelModality.TEXT,
            token_count=result["usage"]["total_tokens"]
        )
        
        # Add indicator
        response = {
            **result,
            "provider": "together_ai",
            "model_id": model_id
        }
        response_with_indicator = self.indicator_manager.add_indicator_to_response(response)
        
        # Verify indicator
        self.assertIn("model_source_indicator", response_with_indicator)
        indicator = response_with_indicator["model_source_indicator"]
        self.assertEqual(indicator["provider_id"], "together_ai")
        self.assertEqual(indicator["model_id"], model_id)


if __name__ == "__main__":
    unittest.main()
