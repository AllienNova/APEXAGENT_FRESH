"""
Fallback mechanism integration for Together AI.

This module implements robust fallback mechanisms for Together AI integration,
ensuring service continuity when primary models or providers fail.
"""

import logging
import time
from enum import Enum
from typing import Dict, Optional, List, Any, Tuple, Callable, Union

from src.plugins.llm_providers.internal.together_ai_provider import TogetherAIProvider
from src.api_key_management.together_ai_key_manager import get_together_ai_key_manager
from src.api_key_management.together_ai_model_selector import (
    get_together_ai_model_selector,
    ModelModality,
    ModelPurpose,
    TogetherAIModelSelector
)
from src.llm_providers.core.provider_interface import LLMError, LLMErrorType
from src.user.subscription import UserTier, get_user_tier
from src.config.feature_flags import FeatureFlag, is_feature_enabled
from src.monitoring.metrics import record_fallback_event, record_latency

logger = logging.getLogger(__name__)

class FallbackStrategy(str, Enum):
    """Enum for fallback strategies."""
    SAME_PROVIDER_DIFFERENT_MODEL = "same_provider_different_model"
    DIFFERENT_PROVIDER = "different_provider"
    DEGRADED_CAPABILITY = "degraded_capability"
    CACHED_RESPONSE = "cached_response"
    ERROR = "error"

class FallbackResult(Dict[str, Any]):
    """Type for fallback operation results."""
    pass

class TogetherAIFallbackManager:
    """
    Fallback manager for Together AI integration.
    
    This class handles fallback strategies when primary models or the
    Together AI provider itself fails, ensuring service continuity.
    """
    
    # Maximum number of fallback attempts
    MAX_FALLBACK_ATTEMPTS = 3
    
    # Fallback timeout in seconds
    FALLBACK_TIMEOUT = 30
    
    # Cache TTL in seconds
    CACHE_TTL = 3600  # 1 hour
    
    def __init__(self):
        """Initialize the fallback manager."""
        self.model_selector = get_together_ai_model_selector()
        self.response_cache = {}
        self.fallback_stats = {
            "attempts": 0,
            "successes": 0,
            "failures": 0,
            "strategies": {}
        }
    
    def _get_cache_key(self, user_id: str, modality: ModelModality, input_data: Any) -> str:
        """
        Generate a cache key for response caching.
        
        Args:
            user_id: User identifier
            modality: Model modality
            input_data: Input data (prompt, messages, etc.)
            
        Returns:
            Cache key string
        """
        # Convert input data to string representation
        if isinstance(input_data, str):
            input_str = input_data
        elif isinstance(input_data, list):
            # For chat messages, extract content
            input_str = " ".join([
                msg.get("content", "") if isinstance(msg, dict) else str(msg)
                for msg in input_data
            ])
        else:
            input_str = str(input_data)
        
        # Generate a hash of the input
        import hashlib
        input_hash = hashlib.md5(input_str.encode()).hexdigest()
        
        return f"{user_id}:{modality}:{input_hash}"
    
    def _cache_response(self, cache_key: str, response: Any) -> None:
        """
        Cache a response for future fallback.
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Prune old cache entries
        self._prune_cache()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Any]:
        """
        Get a cached response if available and not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None if not found or expired
        """
        if cache_key not in self.response_cache:
            return None
        
        cache_entry = self.response_cache[cache_key]
        current_time = time.time()
        
        # Check if cache entry is expired
        if current_time - cache_entry["timestamp"] > self.CACHE_TTL:
            # Remove expired entry
            del self.response_cache[cache_key]
            return None
        
        return cache_entry["response"]
    
    def _prune_cache(self) -> None:
        """Prune expired cache entries."""
        current_time = time.time()
        keys_to_remove = []
        
        for key, entry in self.response_cache.items():
            if current_time - entry["timestamp"] > self.CACHE_TTL:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.response_cache[key]
    
    def _record_fallback_stats(self, strategy: FallbackStrategy, success: bool) -> None:
        """
        Record fallback statistics.
        
        Args:
            strategy: Fallback strategy used
            success: Whether the fallback was successful
        """
        self.fallback_stats["attempts"] += 1
        
        if success:
            self.fallback_stats["successes"] += 1
        else:
            self.fallback_stats["failures"] += 1
        
        # Update strategy stats
        if strategy not in self.fallback_stats["strategies"]:
            self.fallback_stats["strategies"][strategy] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0
            }
        
        self.fallback_stats["strategies"][strategy]["attempts"] += 1
        
        if success:
            self.fallback_stats["strategies"][strategy]["successes"] += 1
        else:
            self.fallback_stats["strategies"][strategy]["failures"] += 1
        
        # Record metrics
        record_fallback_event(
            provider="together_ai",
            strategy=strategy,
            success=success
        )
    
    async def execute_with_fallback(
        self,
        user_id: str,
        modality: ModelModality,
        operation: Callable,
        input_data: Any,
        purpose: Optional[ModelPurpose] = None,
        fallback_strategies: Optional[List[FallbackStrategy]] = None
    ) -> FallbackResult:
        """
        Execute an operation with fallback support.
        
        This method attempts to execute the provided operation and falls back
        to alternative strategies if the primary attempt fails.
        
        Args:
            user_id: User identifier
            modality: Model modality
            operation: Callable operation to execute
            input_data: Input data for the operation
            purpose: Optional specific purpose
            fallback_strategies: Optional list of fallback strategies to try
            
        Returns:
            Operation result or fallback result
        """
        # Default fallback strategies if not provided
        if fallback_strategies is None:
            fallback_strategies = [
                FallbackStrategy.SAME_PROVIDER_DIFFERENT_MODEL,
                FallbackStrategy.DIFFERENT_PROVIDER,
                FallbackStrategy.DEGRADED_CAPABILITY,
                FallbackStrategy.CACHED_RESPONSE,
                FallbackStrategy.ERROR
            ]
        
        # Generate cache key for potential caching
        cache_key = self._get_cache_key(user_id, modality, input_data)
        
        # Get the primary model and provider
        primary_result = self.model_selector.get_provider_with_model(
            user_id=user_id,
            modality=modality,
            purpose=purpose
        )
        
        if primary_result.get("error"):
            logger.error(f"Failed to get provider and model: {primary_result['error']}")
            return {"error": primary_result["error"], "fallback_used": False}
        
        primary_provider = primary_result["provider"]
        primary_model_id = primary_result["model_id"]
        
        # Try primary operation
        try:
            start_time = time.time()
            result = await operation(primary_provider, primary_model_id, input_data)
            end_time = time.time()
            
            # Record latency
            record_latency(
                provider="together_ai",
                model=primary_model_id,
                operation_type=str(modality),
                latency_ms=(end_time - start_time) * 1000
            )
            
            # Cache successful response
            self._cache_response(cache_key, result)
            
            return {
                **result,
                "model_id": primary_model_id,
                "provider": "together_ai",
                "fallback_used": False
            }
            
        except Exception as e:
            logger.warning(f"Primary operation failed with model {primary_model_id}: {str(e)}")
            
            # Try fallback strategies
            return await self._try_fallback_strategies(
                user_id=user_id,
                modality=modality,
                operation=operation,
                input_data=input_data,
                purpose=purpose,
                fallback_strategies=fallback_strategies,
                primary_model_id=primary_model_id,
                cache_key=cache_key,
                original_error=str(e)
            )
    
    async def _try_fallback_strategies(
        self,
        user_id: str,
        modality: ModelModality,
        operation: Callable,
        input_data: Any,
        purpose: Optional[ModelPurpose],
        fallback_strategies: List[FallbackStrategy],
        primary_model_id: str,
        cache_key: str,
        original_error: str
    ) -> FallbackResult:
        """
        Try fallback strategies in sequence.
        
        Args:
            user_id: User identifier
            modality: Model modality
            operation: Callable operation to execute
            input_data: Input data for the operation
            purpose: Optional specific purpose
            fallback_strategies: List of fallback strategies to try
            primary_model_id: Primary model ID that failed
            cache_key: Cache key for response caching
            original_error: Original error message
            
        Returns:
            Operation result or fallback result
        """
        for strategy in fallback_strategies:
            try:
                if strategy == FallbackStrategy.SAME_PROVIDER_DIFFERENT_MODEL:
                    result = await self._try_different_model(
                        user_id, modality, operation, input_data, primary_model_id
                    )
                    
                elif strategy == FallbackStrategy.DIFFERENT_PROVIDER:
                    result = await self._try_different_provider(
                        user_id, modality, operation, input_data
                    )
                    
                elif strategy == FallbackStrategy.DEGRADED_CAPABILITY:
                    result = await self._try_degraded_capability(
                        user_id, modality, operation, input_data
                    )
                    
                elif strategy == FallbackStrategy.CACHED_RESPONSE:
                    result = self._try_cached_response(cache_key)
                    
                else:  # FallbackStrategy.ERROR
                    result = None
                
                if result is not None:
                    self._record_fallback_stats(strategy, True)
                    return {
                        **result,
                        "fallback_used": True,
                        "fallback_strategy": strategy,
                        "original_error": original_error
                    }
                
                self._record_fallback_stats(strategy, False)
                
            except Exception as e:
                logger.warning(f"Fallback strategy {strategy} failed: {str(e)}")
                self._record_fallback_stats(strategy, False)
        
        # All fallback strategies failed
        return {
            "error": f"All fallback strategies failed. Original error: {original_error}",
            "fallback_used": True,
            "fallback_strategy": FallbackStrategy.ERROR,
            "original_error": original_error
        }
    
    async def _try_different_model(
        self,
        user_id: str,
        modality: ModelModality,
        operation: Callable,
        input_data: Any,
        primary_model_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Try a different model from the same provider.
        
        Args:
            user_id: User identifier
            modality: Model modality
            operation: Callable operation to execute
            input_data: Input data for the operation
            primary_model_id: Primary model ID that failed
            
        Returns:
            Operation result or None if failed
        """
        logger.info(f"Trying fallback with different model for user {user_id}")
        
        # Get fallback model
        fallback_model_id = self.model_selector.get_fallback_model(
            user_id=user_id,
            modality=modality,
            primary_model_id=primary_model_id
        )
        
        if not fallback_model_id:
            logger.warning(f"No fallback model available for modality {modality}")
            return None
        
        # Get provider with user's API key
        key_manager = get_together_ai_key_manager()
        api_key = key_manager.get_api_key(user_id)
        
        if not api_key:
            logger.warning(f"No API key available for user {user_id}")
            return None
        
        # Create provider instance
        provider = TogetherAIProvider(api_key=api_key)
        
        # Try operation with fallback model
        try:
            start_time = time.time()
            result = await operation(provider, fallback_model_id, input_data)
            end_time = time.time()
            
            # Record latency
            record_latency(
                provider="together_ai",
                model=fallback_model_id,
                operation_type=str(modality),
                latency_ms=(end_time - start_time) * 1000
            )
            
            logger.info(f"Fallback to model {fallback_model_id} successful")
            
            return {
                **result,
                "model_id": fallback_model_id,
                "provider": "together_ai"
            }
            
        except Exception as e:
            logger.warning(f"Fallback to model {fallback_model_id} failed: {str(e)}")
            return None
    
    async def _try_different_provider(
        self,
        user_id: str,
        modality: ModelModality,
        operation: Callable,
        input_data: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Try a different provider.
        
        Args:
            user_id: User identifier
            modality: Model modality
            operation: Callable operation to execute
            input_data: Input data for the operation
            
        Returns:
            Operation result or None if failed
        """
        logger.info(f"Trying fallback with different provider for user {user_id}")
        
        # Import alternative providers
        try:
            if modality == ModelModality.TEXT:
                from src.plugins.llm_providers.internal.openai_provider import OpenAIProvider
                provider = OpenAIProvider()
                model_id = "gpt-3.5-turbo"
            elif modality == ModelModality.CODE:
                from src.plugins.llm_providers.internal.anthropic_claude_provider import AnthropicClaudeProvider
                provider = AnthropicClaudeProvider()
                model_id = "claude-3-haiku-20240307"
            elif modality == ModelModality.VISION:
                from src.plugins.llm_providers.internal.gemini_provider import GeminiProvider
                provider = GeminiProvider()
                model_id = "gemini-pro-vision"
            else:
                logger.warning(f"No alternative provider available for modality {modality}")
                return None
            
            # Try operation with alternative provider
            start_time = time.time()
            result = await operation(provider, model_id, input_data)
            end_time = time.time()
            
            # Record latency
            record_latency(
                provider=provider.get_provider_name(),
                model=model_id,
                operation_type=str(modality),
                latency_ms=(end_time - start_time) * 1000
            )
            
            logger.info(f"Fallback to provider {provider.get_provider_name()} successful")
            
            return {
                **result,
                "model_id": model_id,
                "provider": provider.get_provider_name()
            }
            
        except Exception as e:
            logger.warning(f"Fallback to different provider failed: {str(e)}")
            return None
    
    async def _try_degraded_capability(
        self,
        user_id: str,
        modality: ModelModality,
        operation: Callable,
        input_data: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Try with degraded capability (e.g., smaller model, simpler task).
        
        Args:
            user_id: User identifier
            modality: Model modality
            operation: Callable operation to execute
            input_data: Input data for the operation
            
        Returns:
            Operation result or None if failed
        """
        logger.info(f"Trying fallback with degraded capability for user {user_id}")
        
        # For text/chat, use the smallest available model
        if modality in [ModelModality.TEXT, ModelModality.CODE]:
            # Get the smallest model
            smallest_model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
            
            # Get provider with user's API key
            key_manager = get_together_ai_key_manager()
            api_key = key_manager.get_api_key(user_id)
            
            if not api_key:
                logger.warning(f"No API key available for user {user_id}")
                return None
            
            # Create provider instance
            provider = TogetherAIProvider(api_key=api_key)
            
            # Simplify input if possible
            simplified_input = input_data
            if isinstance(input_data, str) and len(input_data) > 1000:
                # Truncate long prompts
                simplified_input = input_data[:1000] + "..."
            elif isinstance(input_data, list):
                # For chat messages, keep only the last few
                if len(input_data) > 3:
                    simplified_input = input_data[-3:]
            
            # Try operation with smallest model and simplified input
            try:
                start_time = time.time()
                result = await operation(provider, smallest_model_id, simplified_input)
                end_time = time.time()
                
                # Record latency
                record_latency(
                    provider="together_ai",
                    model=smallest_model_id,
                    operation_type=str(modality),
                    latency_ms=(end_time - start_time) * 1000
                )
                
                logger.info(f"Fallback with degraded capability successful")
                
                return {
                    **result,
                    "model_id": smallest_model_id,
                    "provider": "together_ai",
                    "degraded": True
                }
                
            except Exception as e:
                logger.warning(f"Fallback with degraded capability failed: {str(e)}")
                return None
        
        # For other modalities, no degraded capability available yet
        logger.warning(f"No degraded capability available for modality {modality}")
        return None
    
    def _try_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Try to use a cached response.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None if not available
        """
        logger.info(f"Trying fallback with cached response")
        
        cached_response = self._get_cached_response(cache_key)
        
        if cached_response:
            logger.info(f"Using cached response")
            
            # Add cache metadata
            return {
                **cached_response,
                "from_cache": True,
                "cache_key": cache_key
            }
        
        logger.warning(f"No cached response available")
        return None
    
    def get_fallback_stats(self) -> Dict[str, Any]:
        """
        Get fallback statistics.
        
        Returns:
            Dictionary with fallback statistics
        """
        return self.fallback_stats


# Singleton instance
_instance = None

def get_together_ai_fallback_manager() -> TogetherAIFallbackManager:
    """
    Get the singleton instance of the Together AI fallback manager.
    
    Returns:
        Together AI fallback manager instance
    """
    global _instance
    if _instance is None:
        _instance = TogetherAIFallbackManager()
    return _instance


# Example usage functions

async def generate_text_with_fallback(
    user_id: str,
    prompt: str,
    purpose: Optional[ModelPurpose] = None
) -> Dict[str, Any]:
    """
    Generate text with fallback support.
    
    Args:
        user_id: User identifier
        prompt: Text prompt
        purpose: Optional specific purpose
        
    Returns:
        Generated text result
    """
    fallback_manager = get_together_ai_fallback_manager()
    
    async def text_operation(provider, model_id, prompt_data):
        return await provider.generate_completion(model_id, prompt_data)
    
    return await fallback_manager.execute_with_fallback(
        user_id=user_id,
        modality=ModelModality.TEXT,
        operation=text_operation,
        input_data=prompt,
        purpose=purpose
    )

async def generate_chat_with_fallback(
    user_id: str,
    messages: List[Dict[str, str]],
    purpose: Optional[ModelPurpose] = None
) -> Dict[str, Any]:
    """
    Generate chat response with fallback support.
    
    Args:
        user_id: User identifier
        messages: List of chat messages
        purpose: Optional specific purpose
        
    Returns:
        Generated chat result
    """
    fallback_manager = get_together_ai_fallback_manager()
    
    async def chat_operation(provider, model_id, messages_data):
        return await provider.generate_chat_completion(model_id, messages_data)
    
    return await fallback_manager.execute_with_fallback(
        user_id=user_id,
        modality=ModelModality.TEXT,
        operation=chat_operation,
        input_data=messages,
        purpose=purpose
    )

async def generate_code_with_fallback(
    user_id: str,
    prompt: str,
    purpose: Optional[ModelPurpose] = None
) -> Dict[str, Any]:
    """
    Generate code with fallback support.
    
    Args:
        user_id: User identifier
        prompt: Code prompt
        purpose: Optional specific purpose
        
    Returns:
        Generated code result
    """
    fallback_manager = get_together_ai_fallback_manager()
    
    async def code_operation(provider, model_id, prompt_data):
        return await provider.generate_completion(model_id, prompt_data)
    
    return await fallback_manager.execute_with_fallback(
        user_id=user_id,
        modality=ModelModality.CODE,
        operation=code_operation,
        input_data=prompt,
        purpose=purpose
    )

async def analyze_image_with_fallback(
    user_id: str,
    image_url: str,
    prompt: str,
    purpose: Optional[ModelPurpose] = None
) -> Dict[str, Any]:
    """
    Analyze image with fallback support.
    
    Args:
        user_id: User identifier
        image_url: URL of the image to analyze
        prompt: Text prompt describing what to analyze
        purpose: Optional specific purpose
        
    Returns:
        Image analysis result
    """
    fallback_manager = get_together_ai_fallback_manager()
    
    async def vision_operation(provider, model_id, input_data):
        image_url, prompt = input_data
        return await provider.analyze_image(image_url, prompt, model_id)
    
    return await fallback_manager.execute_with_fallback(
        user_id=user_id,
        modality=ModelModality.VISION,
        operation=vision_operation,
        input_data=(image_url, prompt),
        purpose=purpose
    )

async def generate_image_with_fallback(
    user_id: str,
    prompt: str,
    purpose: Optional[ModelPurpose] = None
) -> Dict[str, Any]:
    """
    Generate image with fallback support.
    
    Args:
        user_id: User identifier
        prompt: Image prompt
        purpose: Optional specific purpose
        
    Returns:
        Generated image result
    """
    fallback_manager = get_together_ai_fallback_manager()
    
    async def image_operation(provider, model_id, prompt_data):
        return await provider.generate_image(prompt_data, model_id)
    
    return await fallback_manager.execute_with_fallback(
        user_id=user_id,
        modality=ModelModality.IMAGE,
        operation=image_operation,
        input_data=prompt,
        purpose=purpose
    )
