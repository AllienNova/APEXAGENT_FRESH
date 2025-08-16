"""
Example usage script for the LLM Providers integration.

This script demonstrates how to use the LLM Providers integration system
with AWS Bedrock and shows various capabilities including text generation,
chat, embeddings, and image generation.
"""

import os
import sys
import logging
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.append('/home/ubuntu/agent_project/src')

from llm_providers import (
    LLMProviders,
    ChatMessage,
    TextGenerationOptions,
    ChatGenerationOptions,
    EmbeddingOptions,
    ImageGenerationOptions,
    generate_text,
    generate_chat_response,
    generate_embedding,
    generate_image
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_text_generation():
    """Test text generation with AWS Bedrock."""
    logger.info("Testing text generation with AWS Bedrock...")
    
    # Create AWS Bedrock provider
    aws_provider = LLMProviders.create_aws_bedrock_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("aws_bedrock", aws_provider)
    
    # Generate text using Claude 3 Haiku (most cost-effective Claude 3 model)
    prompt = "Explain quantum computing in simple terms."
    options = TextGenerationOptions(
        model="claude-3-haiku",
        max_tokens=500,
        temperature=0.7
    )
    
    result = manager.generate_text(prompt, options)
    
    logger.info(f"Generated text using {result.model}:")
    logger.info(result.text)
    logger.info(f"Token usage: {result.usage.prompt_tokens} prompt, {result.usage.completion_tokens} completion")
    logger.info(f"Finish reason: {result.finish_reason}")
    
    return result


def test_chat_generation():
    """Test chat generation with AWS Bedrock."""
    logger.info("Testing chat generation with AWS Bedrock...")
    
    # Create AWS Bedrock provider
    aws_provider = LLMProviders.create_aws_bedrock_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("aws_bedrock", aws_provider)
    
    # Create chat messages
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant specialized in explaining technical concepts."),
        ChatMessage(role="user", content="What is the difference between REST and GraphQL?")
    ]
    
    # Generate chat response using Claude 3 Sonnet
    options = ChatGenerationOptions(
        model="claude-3-sonnet",
        max_tokens=1000,
        temperature=0.7
    )
    
    result = manager.generate_chat(messages, options)
    
    logger.info(f"Generated chat response using {result.model}:")
    logger.info(result.message.content)
    logger.info(f"Token usage: {result.usage.prompt_tokens} prompt, {result.usage.completion_tokens} completion")
    logger.info(f"Finish reason: {result.finish_reason}")
    
    return result


def test_function_calling():
    """Test function calling with AWS Bedrock."""
    logger.info("Testing function calling with AWS Bedrock...")
    
    # Create AWS Bedrock provider
    aws_provider = LLMProviders.create_aws_bedrock_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("aws_bedrock", aws_provider)
    
    # Define a function for weather information
    weather_function = {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use"
                }
            },
            "required": ["location"]
        }
    }
    
    # Create chat messages
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant."),
        ChatMessage(role="user", content="What's the weather like in Boston?")
    ]
    
    # Generate chat response with function calling using Claude 3 Opus
    options = ChatGenerationOptions(
        model="claude-3-opus",
        max_tokens=1000,
        temperature=0.7,
        functions=[weather_function],
        function_call="auto"
    )
    
    result = manager.generate_chat(messages, options)
    
    logger.info(f"Generated chat response using {result.model}:")
    if result.message.function_call:
        logger.info(f"Function call: {result.message.function_call}")
    else:
        logger.info(result.message.content)
    logger.info(f"Token usage: {result.usage.prompt_tokens} prompt, {result.usage.completion_tokens} completion")
    logger.info(f"Finish reason: {result.finish_reason}")
    
    return result


def test_embeddings():
    """Test embeddings with AWS Bedrock."""
    logger.info("Testing embeddings with AWS Bedrock...")
    
    # Create AWS Bedrock provider
    aws_provider = LLMProviders.create_aws_bedrock_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("aws_bedrock", aws_provider)
    
    # Generate embeddings using Titan Embeddings
    text = "This is a sample text for embedding generation."
    options = EmbeddingOptions(
        model="titan-embeddings"
    )
    
    result = manager.generate_embedding(text, options)
    
    logger.info(f"Generated embeddings using {result.model}:")
    logger.info(f"Embedding dimension: {len(result.embedding)}")
    logger.info(f"First 5 values: {result.embedding[:5]}")
    logger.info(f"Token usage: {result.usage.prompt_tokens} tokens")
    
    return result


def test_image_generation():
    """Test image generation with AWS Bedrock."""
    logger.info("Testing image generation with AWS Bedrock...")
    
    # Create AWS Bedrock provider
    aws_provider = LLMProviders.create_aws_bedrock_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("aws_bedrock", aws_provider)
    
    # Generate image using Stable Diffusion
    prompt = "A futuristic city with flying cars and tall skyscrapers, digital art style"
    options = ImageGenerationOptions(
        model="stable-diffusion-xl",
        size="1024x1024"
    )
    
    result = manager.generate_image(prompt, options)
    
    logger.info(f"Generated image using {result.model}:")
    logger.info(f"Number of images: {len(result.images)}")
    logger.info(f"First image (base64 preview): {result.images[0][:50]}...")
    
    return result


def test_convenience_functions():
    """Test convenience functions."""
    logger.info("Testing convenience functions...")
    
    # Generate text
    text = generate_text(
        prompt="Explain the concept of machine learning in simple terms.",
        model="claude-3-haiku",
        max_tokens=500,
        temperature=0.7
    )
    logger.info(f"Generated text (convenience function):\n{text[:100]}...")
    
    # Generate chat response
    chat_response = generate_chat_response(
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "What are the benefits of cloud computing?"}
        ],
        model="claude-3-haiku",
        max_tokens=500,
        temperature=0.7
    )
    logger.info(f"Generated chat response (convenience function):\n{chat_response[:100]}...")
    
    # Generate embeddings
    embedding = generate_embedding(
        text="This is a sample text for embedding generation.",
        model="titan-embeddings"
    )
    logger.info(f"Generated embedding (convenience function):\nDimension: {len(embedding)}, First 5 values: {embedding[:5]}")
    
    # Generate image
    images = generate_image(
        prompt="A beautiful mountain landscape at sunset",
        model="stable-diffusion-xl",
        size="1024x1024"
    )
    logger.info(f"Generated image (convenience function):\nNumber of images: {len(images)}")


def test_model_listing():
    """Test listing available models."""
    logger.info("Testing model listing...")
    
    # Create AWS Bedrock provider
    aws_provider = LLMProviders.create_aws_bedrock_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("aws_bedrock", aws_provider)
    
    # Get all available models
    models = manager.get_all_models()
    
    logger.info(f"Available models ({len(models)}):")
    for model in models:
        logger.info(f"- {model.id} (Provider: {model.provider}, Capabilities: {model.capabilities})")
    
    return models


def main():
    """Main function to run all tests."""
    logger.info("Starting LLM Providers integration tests...")
    
    # Uncomment the tests you want to run
    test_text_generation()
    test_chat_generation()
    # test_function_calling()  # Requires Claude 3 Opus/Sonnet
    test_embeddings()
    # test_image_generation()  # Requires Stable Diffusion access
    test_convenience_functions()
    test_model_listing()
    
    logger.info("All tests completed successfully!")


if __name__ == "__main__":
    main()
