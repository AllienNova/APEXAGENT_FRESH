"""
Validation test suite for the LLM Providers integration.

This module provides comprehensive tests for validating the LLM Providers
integration system, including both AWS Bedrock and Azure OpenAI providers.
"""

import os
import sys
import time
import logging
import unittest
from typing import Dict, List, Any, Optional

# Add the src directory to the Python path
sys.path.append('/home/ubuntu/agent_project/src')

from llm_providers import (
    LLMProviders,
    ProviderType,
    LLMErrorType,
    ChatMessage,
    TextGenerationOptions,
    ChatGenerationOptions,
    EmbeddingOptions,
    ImageGenerationOptions,
    AWSCredentials,
    AWSAuthType,
    AWSBedrockProvider,
    AzureCredentials,
    AzureAuthType,
    AzureOpenAIProvider,
    LLMError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestLLMProvidersBase(unittest.TestCase):
    """Base class for LLM Providers integration tests."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = LLMProviders.create_provider_manager()
        self.aws_provider = None
        self.azure_provider = None
        
        # Set up AWS Bedrock provider if credentials are available
        if os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"):
            try:
                self.aws_provider = LLMProviders.create_aws_bedrock_provider()
                self.manager.register_provider("aws_bedrock", self.aws_provider)
                logger.info("Registered AWS Bedrock provider for testing")
            except Exception as e:
                logger.warning(f"Failed to register AWS Bedrock provider: {str(e)}")
        
        # Set up Azure OpenAI provider if credentials are available
        if os.environ.get("AZURE_OPENAI_API_KEY") and os.environ.get("AZURE_OPENAI_ENDPOINT"):
            try:
                self.azure_provider = LLMProviders.create_azure_openai_provider(
                    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                    endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
                )
                self.manager.register_provider("azure_openai", self.azure_provider)
                logger.info("Registered Azure OpenAI provider for testing")
            except Exception as e:
                logger.warning(f"Failed to register Azure OpenAI provider: {str(e)}")
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def skip_if_no_providers(self):
        """Skip test if no providers are available."""
        if not self.aws_provider and not self.azure_provider:
            self.skipTest("No LLM providers available for testing")


class TestProviderManager(TestLLMProvidersBase):
    """Test the provider manager functionality."""
    
    def test_provider_registration(self):
        """Test provider registration and retrieval."""
        # Create a new manager for this test
        manager = LLMProviders.create_provider_manager()
        
        # Register AWS provider
        if self.aws_provider:
            manager.register_provider("aws_test", self.aws_provider)
            retrieved_provider = manager.get_provider("aws_test")
            self.assertIsNotNone(retrieved_provider)
            self.assertEqual(retrieved_provider.get_provider_type(), ProviderType.AWS_BEDROCK)
        
        # Register Azure provider
        if self.azure_provider:
            manager.register_provider("azure_test", self.azure_provider)
            retrieved_provider = manager.get_provider("azure_test")
            self.assertIsNotNone(retrieved_provider)
            self.assertEqual(retrieved_provider.get_provider_type(), ProviderType.AZURE_OPENAI)
        
        # Test getting all providers
        providers = manager.get_all_providers()
        expected_count = (1 if self.aws_provider else 0) + (1 if self.azure_provider else 0)
        self.assertEqual(len(providers), expected_count)
    
    def test_provider_health(self):
        """Test provider health checking."""
        self.skip_if_no_providers()
        
        # Get health for all providers
        health_statuses = self.manager.get_all_provider_health()
        
        # Check that we got health statuses
        self.assertGreaterEqual(len(health_statuses), 1)
        
        # Check individual provider health
        for provider_id, health in health_statuses.items():
            self.assertIsNotNone(health)
            self.assertIsNotNone(health.available)
            self.assertIsNotNone(health.latency)
            self.assertIsNotNone(health.error_rate)
            self.assertIsNotNone(health.message)
    
    def test_model_listing(self):
        """Test listing available models."""
        self.skip_if_no_providers()
        
        # Get all models
        models = self.manager.get_all_models()
        
        # Check that we got models
        self.assertGreaterEqual(len(models), 1)
        
        # Check model information
        for model in models:
            self.assertIsNotNone(model.id)
            self.assertIsNotNone(model.provider)
            self.assertGreaterEqual(len(model.capabilities), 1)
    
    def test_provider_selection(self):
        """Test provider selection for models."""
        self.skip_if_no_providers()
        
        # Get all models
        models = self.manager.get_all_models()
        
        if not models:
            self.skipTest("No models available for testing")
        
        # Test provider selection for each model
        for model in models:
            providers = self.manager.get_providers_for_model(model.id)
            self.assertGreaterEqual(len(providers), 1)
            
            # Test selecting a provider
            selected_provider = self.manager.select_provider_for_model(model.id)
            self.assertIsNotNone(selected_provider)
            self.assertIn(selected_provider, providers)


class TestAWSBedrockProvider(TestLLMProvidersBase):
    """Test the AWS Bedrock provider functionality."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        if not self.aws_provider:
            self.skipTest("AWS Bedrock provider not available for testing")
    
    def test_text_generation(self):
        """Test text generation with AWS Bedrock."""
        # Generate text using Claude 3 Haiku (most cost-effective Claude 3 model)
        prompt = "Explain quantum computing in simple terms."
        options = TextGenerationOptions(
            model="claude-3-haiku",
            max_tokens=100,
            temperature=0.7
        )
        
        result = self.manager.generate_text(prompt, options)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.text)
        self.assertGreater(len(result.text), 0)
        self.assertEqual(result.model, "claude-3-haiku")
        self.assertIsNotNone(result.usage)
        self.assertGreater(result.usage.prompt_tokens, 0)
        self.assertGreater(result.usage.completion_tokens, 0)
        self.assertIsNotNone(result.finish_reason)
    
    def test_chat_generation(self):
        """Test chat generation with AWS Bedrock."""
        # Create chat messages
        messages = [
            ChatMessage(role="system", content="You are a helpful AI assistant specialized in explaining technical concepts."),
            ChatMessage(role="user", content="What is the difference between REST and GraphQL?")
        ]
        
        # Generate chat response using Claude 3 Haiku
        options = ChatGenerationOptions(
            model="claude-3-haiku",
            max_tokens=100,
            temperature=0.7
        )
        
        result = self.manager.generate_chat(messages, options)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.message)
        self.assertIsNotNone(result.message.content)
        self.assertGreater(len(result.message.content), 0)
        self.assertEqual(result.model, "claude-3-haiku")
        self.assertIsNotNone(result.usage)
        self.assertGreater(result.usage.prompt_tokens, 0)
        self.assertGreater(result.usage.completion_tokens, 0)
        self.assertIsNotNone(result.finish_reason)
    
    def test_embeddings(self):
        """Test embeddings with AWS Bedrock."""
        # Skip if Titan Embeddings model is not available
        models = self.manager.get_all_models()
        has_embedding_model = any(model.id == "titan-embeddings" for model in models)
        if not has_embedding_model:
            self.skipTest("Titan Embeddings model not available for testing")
        
        # Generate embeddings
        text = "This is a sample text for embedding generation."
        options = EmbeddingOptions(
            model="titan-embeddings"
        )
        
        result = self.manager.generate_embedding(text, options)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.embedding)
        self.assertGreater(len(result.embedding), 0)
        self.assertEqual(result.model, "titan-embeddings")
        self.assertIsNotNone(result.usage)
        self.assertGreater(result.usage.prompt_tokens, 0)


class TestAzureOpenAIProvider(TestLLMProvidersBase):
    """Test the Azure OpenAI provider functionality."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        if not self.azure_provider:
            self.skipTest("Azure OpenAI provider not available for testing")
        
        # Get available models for testing
        self.available_models = self.manager.get_all_models()
        self.azure_models = [model for model in self.available_models 
                            if model.provider == ProviderType.AZURE_OPENAI]
        
        # Find suitable models for each test
        self.chat_model = None
        self.embedding_model = None
        self.image_model = None
        
        for model in self.azure_models:
            if not self.chat_model and any(cap in model.capabilities for cap in 
                                          [ProviderType.TEXT, ProviderType.CHAT]):
                self.chat_model = model.id
            
            if not self.embedding_model and ProviderType.EMBEDDING in model.capabilities:
                self.embedding_model = model.id
            
            if not self.image_model and ProviderType.IMAGE in model.capabilities:
                self.image_model = model.id
    
    def test_text_generation(self):
        """Test text generation with Azure OpenAI."""
        if not self.chat_model:
            self.skipTest("No suitable Azure OpenAI model available for text generation")
        
        # Generate text
        prompt = "Explain quantum computing in simple terms."
        options = TextGenerationOptions(
            model=self.chat_model,
            max_tokens=100,
            temperature=0.7
        )
        
        result = self.manager.generate_text(prompt, options)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.text)
        self.assertGreater(len(result.text), 0)
        self.assertEqual(result.model, self.chat_model)
        self.assertIsNotNone(result.usage)
        self.assertGreater(result.usage.prompt_tokens, 0)
        self.assertGreater(result.usage.completion_tokens, 0)
        self.assertIsNotNone(result.finish_reason)
    
    def test_chat_generation(self):
        """Test chat generation with Azure OpenAI."""
        if not self.chat_model:
            self.skipTest("No suitable Azure OpenAI model available for chat generation")
        
        # Create chat messages
        messages = [
            ChatMessage(role="system", content="You are a helpful AI assistant specialized in explaining technical concepts."),
            ChatMessage(role="user", content="What is the difference between REST and GraphQL?")
        ]
        
        # Generate chat response
        options = ChatGenerationOptions(
            model=self.chat_model,
            max_tokens=100,
            temperature=0.7
        )
        
        result = self.manager.generate_chat(messages, options)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.message)
        self.assertIsNotNone(result.message.content)
        self.assertGreater(len(result.message.content), 0)
        self.assertEqual(result.model, self.chat_model)
        self.assertIsNotNone(result.usage)
        self.assertGreater(result.usage.prompt_tokens, 0)
        self.assertGreater(result.usage.completion_tokens, 0)
        self.assertIsNotNone(result.finish_reason)
    
    def test_embeddings(self):
        """Test embeddings with Azure OpenAI."""
        if not self.embedding_model:
            self.skipTest("No suitable Azure OpenAI model available for embeddings")
        
        # Generate embeddings
        text = "This is a sample text for embedding generation."
        options = EmbeddingOptions(
            model=self.embedding_model
        )
        
        result = self.manager.generate_embedding(text, options)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.embedding)
        self.assertGreater(len(result.embedding), 0)
        self.assertEqual(result.model, self.embedding_model)
        self.assertIsNotNone(result.usage)
        self.assertGreater(result.usage.prompt_tokens, 0)
    
    def test_image_generation(self):
        """Test image generation with Azure OpenAI."""
        if not self.image_model:
            self.skipTest("No suitable Azure OpenAI model available for image generation")
        
        # Generate image
        prompt = "A beautiful mountain landscape at sunset"
        options = ImageGenerationOptions(
            model=self.image_model,
            size="1024x1024"
        )
        
        result = self.manager.generate_image(prompt, options)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.images)
        self.assertGreaterEqual(len(result.images), 1)
        self.assertEqual(result.model, self.image_model)


class TestErrorHandling(TestLLMProvidersBase):
    """Test error handling in the LLM Providers integration."""
    
    def test_invalid_model(self):
        """Test handling of invalid model errors."""
        self.skip_if_no_providers()
        
        # Try to generate text with an invalid model
        prompt = "This is a test."
        options = TextGenerationOptions(
            model="non-existent-model",
            max_tokens=10
        )
        
        with self.assertRaises(LLMError) as context:
            self.manager.generate_text(prompt, options)
        
        # Check error
        error = context.exception
        self.assertEqual(error.error_type, LLMErrorType.MODEL_NOT_FOUND_ERROR)
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameter errors."""
        self.skip_if_no_providers()
        
        # Get a valid model
        models = self.manager.get_all_models()
        if not models:
            self.skipTest("No models available for testing")
        
        model_id = models[0].id
        
        # Try to generate text with invalid parameters (negative max_tokens)
        prompt = "This is a test."
        options = TextGenerationOptions(
            model=model_id,
            max_tokens=-10
        )
        
        with self.assertRaises(LLMError) as context:
            self.manager.generate_text(prompt, options)
        
        # Check error
        error = context.exception
        self.assertIn(error.error_type, [
            LLMErrorType.INVALID_REQUEST_ERROR,
            LLMErrorType.VALIDATION_ERROR
        ])


class TestPerformance(TestLLMProvidersBase):
    """Test performance of the LLM Providers integration."""
    
    def test_latency(self):
        """Test latency of text generation."""
        self.skip_if_no_providers()
        
        # Get a valid model
        models = self.manager.get_all_models()
        if not models:
            self.skipTest("No models available for testing")
        
        # Find a text generation model
        text_models = [model for model in models 
                      if ProviderType.TEXT in model.capabilities]
        
        if not text_models:
            self.skipTest("No text generation models available for testing")
        
        model_id = text_models[0].id
        
        # Generate text and measure latency
        prompt = "Hello, world!"
        options = TextGenerationOptions(
            model=model_id,
            max_tokens=5
        )
        
        start_time = time.time()
        result = self.manager.generate_text(prompt, options)
        end_time = time.time()
        
        latency = end_time - start_time
        
        # Log latency
        logger.info(f"Text generation latency: {latency:.2f} seconds")
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.text)
    
    def test_throughput(self):
        """Test throughput of text generation."""
        self.skip_if_no_providers()
        
        # Get a valid model
        models = self.manager.get_all_models()
        if not models:
            self.skipTest("No models available for testing")
        
        # Find a text generation model
        text_models = [model for model in models 
                      if ProviderType.TEXT in model.capabilities]
        
        if not text_models:
            self.skipTest("No text generation models available for testing")
        
        model_id = text_models[0].id
        
        # Generate text multiple times and measure throughput
        prompt = "Hello, world!"
        options = TextGenerationOptions(
            model=model_id,
            max_tokens=5
        )
        
        num_requests = 3
        start_time = time.time()
        
        for _ in range(num_requests):
            result = self.manager.generate_text(prompt, options)
            self.assertIsNotNone(result)
        
        end_time = time.time()
        
        total_time = end_time - start_time
        throughput = num_requests / total_time
        
        # Log throughput
        logger.info(f"Text generation throughput: {throughput:.2f} requests/second")


class TestFallback(TestLLMProvidersBase):
    """Test fallback mechanisms in the LLM Providers integration."""
    
    def test_provider_fallback(self):
        """Test fallback to alternative provider."""
        # Skip if we don't have multiple providers
        if not (self.aws_provider and self.azure_provider):
            self.skipTest("Multiple providers required for fallback testing")
        
        # Find a model that's available on both providers
        # This is a bit tricky since model IDs are different between providers
        # For this test, we'll simulate fallback by temporarily disabling a provider
        
        # Get all models
        aws_models = [model for model in self.manager.get_all_models() 
                     if model.provider == ProviderType.AWS_BEDROCK]
        
        if not aws_models:
            self.skipTest("No AWS models available for testing")
        
        # Create a new manager with only AWS provider
        manager = LLMProviders.create_provider_manager()
        manager.register_provider("aws_bedrock", self.aws_provider)
        
        # Generate text with AWS provider
        prompt = "Hello, world!"
        options = TextGenerationOptions(
            model=aws_models[0].id,
            max_tokens=5
        )
        
        result = manager.generate_text(prompt, options)
        self.assertIsNotNone(result)
        
        # Now unregister AWS provider and register Azure provider
        manager.unregister_provider("aws_bedrock")
        manager.register_provider("azure_openai", self.azure_provider)
        
        # Try to generate text with the same model (should fail)
        with self.assertRaises(LLMError) as context:
            manager.generate_text(prompt, options)
        
        # Check error
        error = context.exception
        self.assertEqual(error.error_type, LLMErrorType.MODEL_NOT_FOUND_ERROR)


def run_tests():
    """Run all tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestProviderManager))
    suite.addTest(unittest.makeSuite(TestAWSBedrockProvider))
    suite.addTest(unittest.makeSuite(TestAzureOpenAIProvider))
    suite.addTest(unittest.makeSuite(TestErrorHandling))
    suite.addTest(unittest.makeSuite(TestPerformance))
    suite.addTest(unittest.makeSuite(TestFallback))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    run_tests()
