"""
Provider Manager for the LLM Providers integration.

This module implements the provider manager that handles provider selection,
routing, and fallback mechanisms for the LLM Providers integration system.
"""

import logging
import random
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from .core.provider_interface import (
    LLMProvider,
    ProviderType,
    LLMErrorType,
    FinishReason,
    ChatMessage,
    FunctionDefinition,
    ModelInfo,
    ProviderCapabilities,
    HealthStatus,
    UsageInfo,
    TextGenerationOptions,
    ChatGenerationOptions,
    EmbeddingOptions,
    ImageGenerationOptions,
    TextGenerationResult,
    ChatGenerationResult,
    EmbeddingResult,
    ImageGenerationResult,
    TextGenerationChunk,
    ChatGenerationChunk,
    LLMError
)

logger = logging.getLogger(__name__)


class ProviderManager:
    """
    Manager for LLM providers.
    
    This class handles provider registration, selection, routing, and fallback
    mechanisms for the LLM Providers integration system.
    """
    
    def __init__(self):
        """Initialize the provider manager."""
        self.providers: Dict[str, LLMProvider] = {}
        self.provider_health_cache: Dict[str, Tuple[HealthStatus, float]] = {}
        self.provider_health_ttl = 60  # 1 minute
        self.model_provider_mapping: Dict[str, Set[str]] = {}
    
    def register_provider(self, provider_id: str, provider: LLMProvider) -> None:
        """
        Register a provider with the manager.
        
        Args:
            provider_id: Unique identifier for the provider
            provider: Provider instance
        """
        self.providers[provider_id] = provider
        logger.info(f"Registered provider: {provider_id}")
        
        # Update model-provider mapping
        try:
            models = provider.get_models()
            for model in models:
                if model.id not in self.model_provider_mapping:
                    self.model_provider_mapping[model.id] = set()
                self.model_provider_mapping[model.id].add(provider_id)
        except Exception as e:
            logger.warning(f"Failed to get models from provider {provider_id}: {str(e)}")
    
    def unregister_provider(self, provider_id: str) -> None:
        """
        Unregister a provider from the manager.
        
        Args:
            provider_id: Unique identifier for the provider
        """
        if provider_id in self.providers:
            del self.providers[provider_id]
            logger.info(f"Unregistered provider: {provider_id}")
            
            # Update model-provider mapping
            for model_id, providers in list(self.model_provider_mapping.items()):
                if provider_id in providers:
                    providers.remove(provider_id)
                    if not providers:
                        del self.model_provider_mapping[model_id]
    
    def get_provider(self, provider_id: str) -> Optional[LLMProvider]:
        """
        Get a provider by ID.
        
        Args:
            provider_id: Unique identifier for the provider
            
        Returns:
            Provider instance or None if not found
        """
        return self.providers.get(provider_id)
    
    def get_all_providers(self) -> Dict[str, LLMProvider]:
        """
        Get all registered providers.
        
        Returns:
            Dictionary of provider ID to provider instance
        """
        return self.providers
    
    def get_provider_health(self, provider_id: str) -> HealthStatus:
        """
        Get the health status of a provider.
        
        Args:
            provider_id: Unique identifier for the provider
            
        Returns:
            Provider health status
            
        Raises:
            LLMError: If the provider is not found
        """
        provider = self.get_provider(provider_id)
        if not provider:
            raise LLMError(
                f"Provider not found: {provider_id}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "provider_manager",
                retryable=False
            )
        
        # Check cache first
        current_time = time.time()
        if provider_id in self.provider_health_cache:
            health, timestamp = self.provider_health_cache[provider_id]
            if current_time - timestamp < self.provider_health_ttl:
                return health
        
        # Get fresh health status
        health = provider.get_health()
        self.provider_health_cache[provider_id] = (health, current_time)
        return health
    
    def get_all_provider_health(self) -> Dict[str, HealthStatus]:
        """
        Get health status for all providers.
        
        Returns:
            Dictionary of provider ID to health status
        """
        result = {}
        for provider_id in self.providers:
            try:
                result[provider_id] = self.get_provider_health(provider_id)
            except Exception as e:
                logger.error(f"Failed to get health for provider {provider_id}: {str(e)}")
                result[provider_id] = HealthStatus(
                    available=False,
                    latency=0.0,
                    error_rate=1.0,
                    message=f"Error getting health: {str(e)}"
                )
        return result
    
    def get_providers_for_model(self, model_id: str) -> List[str]:
        """
        Get providers that support a specific model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            List of provider IDs that support the model
        """
        return list(self.model_provider_mapping.get(model_id, set()))
    
    def get_all_models(self) -> List[ModelInfo]:
        """
        Get information about all available models across all providers.
        
        Returns:
            List of model information
        """
        all_models = []
        for provider_id, provider in self.providers.items():
            try:
                models = provider.get_models()
                all_models.extend(models)
            except Exception as e:
                logger.error(f"Failed to get models from provider {provider_id}: {str(e)}")
        return all_models
    
    def select_provider_for_model(
        self, model_id: str, preferred_provider: Optional[str] = None
    ) -> str:
        """
        Select the best provider for a specific model.
        
        Args:
            model_id: Model identifier
            preferred_provider: Optional preferred provider ID
            
        Returns:
            Selected provider ID
            
        Raises:
            LLMError: If no suitable provider is found
        """
        # Check if preferred provider supports the model
        if preferred_provider and preferred_provider in self.providers:
            if model_id in self.model_provider_mapping and preferred_provider in self.model_provider_mapping[model_id]:
                # Check if the preferred provider is healthy
                health = self.get_provider_health(preferred_provider)
                if health.available:
                    return preferred_provider
        
        # Get all providers that support the model
        providers = self.get_providers_for_model(model_id)
        if not providers:
            raise LLMError(
                f"No provider found for model: {model_id}",
                LLMErrorType.MODEL_NOT_FOUND_ERROR,
                "provider_manager",
                retryable=False
            )
        
        # Filter to available providers
        available_providers = []
        for provider_id in providers:
            try:
                health = self.get_provider_health(provider_id)
                if health.available:
                    available_providers.append((provider_id, health))
            except Exception as e:
                logger.warning(f"Failed to get health for provider {provider_id}: {str(e)}")
        
        if not available_providers:
            raise LLMError(
                f"No available provider found for model: {model_id}",
                LLMErrorType.SERVICE_UNAVAILABLE_ERROR,
                "provider_manager",
                retryable=True
            )
        
        # Sort by latency (lower is better)
        available_providers.sort(key=lambda x: x[1].latency)
        
        # Return the provider with the lowest latency
        return available_providers[0][0]
    
    def generate_text(
        self, prompt: str, options: TextGenerationOptions
    ) -> TextGenerationResult:
        """
        Generate text from a prompt using the best available provider.
        
        Args:
            prompt: The text prompt
            options: Text generation options
            
        Returns:
            Generated text result
        """
        provider_id = self.select_provider_for_model(options.model, options.provider)
        provider = self.get_provider(provider_id)
        if not provider:
            raise LLMError(
                f"Provider not found: {provider_id}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "provider_manager",
                retryable=False
            )
        
        return provider.generate_text(prompt, options)
    
    def generate_chat(
        self, messages: List[ChatMessage], options: ChatGenerationOptions
    ) -> ChatGenerationResult:
        """
        Generate a chat response using the best available provider.
        
        Args:
            messages: List of chat messages
            options: Chat generation options
            
        Returns:
            Generated chat result
        """
        provider_id = self.select_provider_for_model(options.model, options.provider)
        provider = self.get_provider(provider_id)
        if not provider:
            raise LLMError(
                f"Provider not found: {provider_id}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "provider_manager",
                retryable=False
            )
        
        return provider.generate_chat(messages, options)
    
    def generate_embedding(
        self, text: str, options: EmbeddingOptions
    ) -> EmbeddingResult:
        """
        Generate embeddings for text using the best available provider.
        
        Args:
            text: The text to generate embeddings for
            options: Embedding options
            
        Returns:
            Generated embedding result
        """
        provider_id = self.select_provider_for_model(options.model, options.provider)
        provider = self.get_provider(provider_id)
        if not provider:
            raise LLMError(
                f"Provider not found: {provider_id}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "provider_manager",
                retryable=False
            )
        
        return provider.generate_embedding(text, options)
    
    def generate_image(
        self, prompt: str, options: ImageGenerationOptions
    ) -> ImageGenerationResult:
        """
        Generate images from a prompt using the best available provider.
        
        Args:
            prompt: The text prompt
            options: Image generation options
            
        Returns:
            Generated image result
        """
        # If no model specified, use a default one
        model_id = options.model or "stable-diffusion-xl"
        
        provider_id = self.select_provider_for_model(model_id, options.provider)
        provider = self.get_provider(provider_id)
        if not provider:
            raise LLMError(
                f"Provider not found: {provider_id}",
                LLMErrorType.INVALID_REQUEST_ERROR,
                "provider_manager",
                retryable=False
            )
        
        # Update options with the model ID if it wasn't provided
        if not options.model:
            options = ImageGenerationOptions(
                model=model_id,
                size=options.size,
                quality=options.quality,
                style=options.style,
                provider=options.provider
            )
        
        return provider.generate_image(prompt, options)
