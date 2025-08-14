"""
Example usage script for the LLM Providers integration with Azure OpenAI.

This script demonstrates how to use the LLM Providers integration system
with Azure OpenAI and shows various capabilities including text generation,
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
    AzureCredentials,
    AzureAuthType,
    AzureOpenAIProvider
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_text_generation():
    """Test text generation with Azure OpenAI."""
    logger.info("Testing text generation with Azure OpenAI...")
    
    # Create Azure OpenAI provider
    azure_provider = create_azure_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("azure_openai", azure_provider)
    
    # Generate text using GPT-4 Turbo
    prompt = "Explain quantum computing in simple terms."
    options = TextGenerationOptions(
        model="gpt-4-turbo",  # Use your actual deployment name
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
    """Test chat generation with Azure OpenAI."""
    logger.info("Testing chat generation with Azure OpenAI...")
    
    # Create Azure OpenAI provider
    azure_provider = create_azure_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("azure_openai", azure_provider)
    
    # Create chat messages
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant specialized in explaining technical concepts."),
        ChatMessage(role="user", content="What is the difference between REST and GraphQL?")
    ]
    
    # Generate chat response using GPT-4
    options = ChatGenerationOptions(
        model="gpt-4",  # Use your actual deployment name
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
    """Test function calling with Azure OpenAI."""
    logger.info("Testing function calling with Azure OpenAI...")
    
    # Create Azure OpenAI provider
    azure_provider = create_azure_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("azure_openai", azure_provider)
    
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
    
    # Generate chat response with function calling using GPT-4 Turbo
    options = ChatGenerationOptions(
        model="gpt-4-turbo",  # Use your actual deployment name
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
    """Test embeddings with Azure OpenAI."""
    logger.info("Testing embeddings with Azure OpenAI...")
    
    # Create Azure OpenAI provider
    azure_provider = create_azure_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("azure_openai", azure_provider)
    
    # Generate embeddings using text-embedding-ada-002
    text = "This is a sample text for embedding generation."
    options = EmbeddingOptions(
        model="text-embedding-ada-002"  # Use your actual deployment name
    )
    
    result = manager.generate_embedding(text, options)
    
    logger.info(f"Generated embeddings using {result.model}:")
    logger.info(f"Embedding dimension: {len(result.embedding)}")
    logger.info(f"First 5 values: {result.embedding[:5]}")
    logger.info(f"Token usage: {result.usage.prompt_tokens} tokens")
    
    return result


def test_image_generation():
    """Test image generation with Azure OpenAI."""
    logger.info("Testing image generation with Azure OpenAI...")
    
    # Create Azure OpenAI provider
    azure_provider = create_azure_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("azure_openai", azure_provider)
    
    # Generate image using DALL-E 3
    prompt = "A futuristic city with flying cars and tall skyscrapers, digital art style"
    options = ImageGenerationOptions(
        model="dall-e-3",  # Use your actual deployment name
        size="1024x1024"
    )
    
    result = manager.generate_image(prompt, options)
    
    logger.info(f"Generated image using {result.model}:")
    logger.info(f"Number of images: {len(result.images)}")
    logger.info(f"First image URL: {result.images[0][:100]}...")
    
    return result


def test_model_listing():
    """Test listing available models."""
    logger.info("Testing model listing...")
    
    # Create Azure OpenAI provider
    azure_provider = create_azure_provider()
    
    # Create provider manager and register the provider
    manager = LLMProviders.create_provider_manager()
    manager.register_provider("azure_openai", azure_provider)
    
    # Get all available models
    models = manager.get_all_models()
    
    logger.info(f"Available models ({len(models)}):")
    for model in models:
        logger.info(f"- {model.id} (Provider: {model.provider}, Capabilities: {model.capabilities})")
    
    return models


def create_azure_provider():
    """Create an Azure OpenAI provider with credentials from environment variables."""
    # Get credentials from environment variables
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    
    if api_key and endpoint:
        # Use API key authentication
        credentials = AzureCredentials(
            auth_type=AzureAuthType.API_KEY,
            api_key=api_key,
            endpoint=endpoint,
            api_version="2023-12-01-preview"  # Latest version with GPT-4 Turbo support
        )
    else:
        # Try Microsoft Entra ID (Azure AD) authentication
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        
        if tenant_id and client_id and client_secret and endpoint:
            credentials = AzureCredentials(
                auth_type=AzureAuthType.ENTRA_ID,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                endpoint=endpoint,
                api_version="2023-12-01-preview"
            )
        else:
            # Fall back to default credential
            credentials = AzureCredentials(
                auth_type=AzureAuthType.DEFAULT_CREDENTIAL,
                endpoint=endpoint or "https://your-resource-name.openai.azure.com",
                api_version="2023-12-01-preview"
            )
    
    return AzureOpenAIProvider(credentials=credentials)


def main():
    """Main function to run all tests."""
    logger.info("Starting Azure OpenAI integration tests...")
    
    # Check if Azure OpenAI credentials are available
    if not (os.environ.get("AZURE_OPENAI_API_KEY") and os.environ.get("AZURE_OPENAI_ENDPOINT")):
        logger.warning("Azure OpenAI credentials not found in environment variables.")
        logger.warning("Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")
        logger.warning("Alternatively, set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_OPENAI_ENDPOINT for Microsoft Entra ID authentication.")
        logger.warning("Tests will use placeholder values and will not make actual API calls.")
    
    # Uncomment the tests you want to run
    # test_text_generation()
    # test_chat_generation()
    # test_function_calling()
    # test_embeddings()
    # test_image_generation()
    # test_model_listing()
    
    logger.info("All tests completed!")


if __name__ == "__main__":
    main()
