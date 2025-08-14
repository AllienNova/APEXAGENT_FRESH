"""
Tier-based model selection for Together AI integration.

This module implements tier-based model selection for Together AI,
ensuring appropriate models are selected based on user tier and modality.
"""

import logging
from enum import Enum
from typing import Dict, Optional, List, Any

from src.plugins.llm_providers.internal.together_ai_provider import TogetherAIProvider
from api_key_management.together_ai_key_manager import get_together_ai_key_manager
from user.subscription import UserTier, get_user_tier
from config.feature_flags import FeatureFlag, is_feature_enabled

logger = logging.getLogger(__name__)

class ModelModality(str, Enum):
    """Enum for model modalities."""
    TEXT = "text"
    CODE = "code"
    VISION = "vision"
    IMAGE = "image"
    AUDIO_TTS = "audio_tts"
    AUDIO_STT = "audio_stt"

class ModelPurpose(str, Enum):
    """Enum for specific model purposes."""
    GENERAL = "general"
    CRITICAL = "critical"
    COMPLEX = "complex"
    FAST = "fast"
    QUALITY = "quality"
    FALLBACK = "fallback"
    SPECIALIZED = "specialized"

class TogetherAIModelSelector:
    """
    Tier-based model selector for Together AI.
    
    This class handles the selection of appropriate Together AI models
    based on user tier, modality, and specific purpose.
    """
    
    # Model mappings by tier, modality, and purpose
    MODEL_MAPPINGS = {
        UserTier.FREE: {
            ModelModality.TEXT: {
                ModelPurpose.GENERAL: "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                ModelPurpose.FALLBACK: "mistralai/Mixtral-8x7B-Instruct-v0.1",
            },
            ModelModality.CODE: {
                ModelPurpose.GENERAL: "Nexusflow/NexusRaven-V2-13B",
                ModelPurpose.FALLBACK: "codellama/CodeLlama-13b-Instruct-hf",
            },
            ModelModality.VISION: {
                ModelPurpose.GENERAL: "deepseek-ai/DeepSeek-VL-7B-Chat",
            },
            ModelModality.IMAGE: {
                ModelPurpose.GENERAL: "stabilityai/stable-diffusion-xl-base-1.0",
                ModelPurpose.FALLBACK: "runwayml/stable-diffusion-v1-5",
            },
            ModelModality.AUDIO_TTS: {
                ModelPurpose.GENERAL: "cartesia/sonic",
            },
            ModelModality.AUDIO_STT: {
                ModelPurpose.GENERAL: "whisper-medium",
            },
        },
        UserTier.PREMIUM: {
            ModelModality.TEXT: {
                ModelPurpose.GENERAL: "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                ModelPurpose.CRITICAL: "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                ModelPurpose.FALLBACK: "mistralai/Mixtral-8x7B-Instruct-v0.1",
            },
            ModelModality.CODE: {
                ModelPurpose.GENERAL: "deepseek-ai/deepseek-coder-33b-instruct",
                ModelPurpose.COMPLEX: "codellama/CodeLlama-70b-Instruct-hf",
                ModelPurpose.FALLBACK: "Nexusflow/NexusRaven-V2-13B",
            },
            ModelModality.VISION: {
                ModelPurpose.GENERAL: "Qwen/Qwen-VL-Chat",
                ModelPurpose.SPECIALIZED: "Snowflake/snowflake-arctic-instruct",
                ModelPurpose.FALLBACK: "deepseek-ai/DeepSeek-VL-7B-Chat",
            },
            ModelModality.IMAGE: {
                ModelPurpose.GENERAL: "stabilityai/stable-diffusion-xl-base-1.0",
                ModelPurpose.FAST: "stabilityai/sdxl-turbo",
                ModelPurpose.QUALITY: "playgroundai/playground-v2.5",
                ModelPurpose.FALLBACK: "runwayml/stable-diffusion-v1-5",
            },
            ModelModality.AUDIO_TTS: {
                ModelPurpose.GENERAL: "cartesia/sonic",
            },
            ModelModality.AUDIO_STT: {
                ModelPurpose.GENERAL: "whisper-large-v3",
                ModelPurpose.FALLBACK: "whisper-medium",
            },
        },
        UserTier.ENTERPRISE: {
            ModelModality.TEXT: {
                ModelPurpose.GENERAL: "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                ModelPurpose.FALLBACK: "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            },
            ModelModality.CODE: {
                ModelPurpose.GENERAL: "codellama/CodeLlama-70b-Instruct-hf",
                ModelPurpose.FALLBACK: "deepseek-ai/deepseek-coder-33b-instruct",
            },
            ModelModality.VISION: {
                ModelPurpose.GENERAL: "Qwen/Qwen-VL-Chat",
                ModelPurpose.SPECIALIZED: "Snowflake/snowflake-arctic-instruct",
                ModelPurpose.FALLBACK: "deepseek-ai/DeepSeek-VL-7B-Chat",
            },
            ModelModality.IMAGE: {
                ModelPurpose.GENERAL: "playgroundai/playground-v2.5",
                ModelPurpose.FAST: "stabilityai/sdxl-turbo",
                ModelPurpose.FALLBACK: "stabilityai/stable-diffusion-xl-base-1.0",
            },
            ModelModality.AUDIO_TTS: {
                ModelPurpose.GENERAL: "cartesia/sonic",
            },
            ModelModality.AUDIO_STT: {
                ModelPurpose.GENERAL: "whisper-large-v3",
                ModelPurpose.FALLBACK: "whisper-medium",
            },
        },
    }
    
    def __init__(self):
        """Initialize the model selector."""
        self.provider = None
    
    def get_model_for_user(
        self,
        user_id: str,
        modality: ModelModality,
        purpose: Optional[ModelPurpose] = None,
        override_tier: Optional[UserTier] = None
    ) -> str:
        """
        Get the appropriate model for a user based on their tier.
        
        Args:
            user_id: User identifier
            modality: Model modality (text, code, vision, etc.)
            purpose: Optional specific purpose (general, critical, etc.)
            override_tier: Optional tier override
            
        Returns:
            Model ID string for the specified parameters
        """
        # Determine user tier
        user_tier = override_tier or get_user_tier(user_id)
        
        # Default to FREE tier if not found
        if not user_tier:
            user_tier = UserTier.FREE
            logger.warning(f"No tier found for user {user_id}, defaulting to FREE")
        
        # Default purpose to GENERAL if not specified
        if not purpose:
            purpose = ModelPurpose.GENERAL
        
        # Get tier-specific model mappings
        tier_mappings = self.MODEL_MAPPINGS.get(user_tier, self.MODEL_MAPPINGS[UserTier.FREE])
        
        # Get modality-specific model mappings
        modality_mappings = tier_mappings.get(modality)
        
        if not modality_mappings:
            # If modality not found for this tier, fall back to FREE tier
            logger.warning(f"No models found for modality {modality} in tier {user_tier}, falling back to FREE tier")
            modality_mappings = self.MODEL_MAPPINGS[UserTier.FREE].get(modality, {})
        
        # Get purpose-specific model
        model_id = modality_mappings.get(purpose)
        
        if not model_id:
            # If purpose not found, try GENERAL purpose
            model_id = modality_mappings.get(ModelPurpose.GENERAL)
            
            if not model_id:
                # If still not found, use a reasonable default
                logger.warning(f"No model found for modality {modality} and purpose {purpose}, using default")
                
                # Default models by modality
                defaults = {
                    ModelModality.TEXT: "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                    ModelModality.CODE: "Nexusflow/NexusRaven-V2-13B",
                    ModelModality.VISION: "deepseek-ai/DeepSeek-VL-7B-Chat",
                    ModelModality.IMAGE: "stabilityai/stable-diffusion-xl-base-1.0",
                    ModelModality.AUDIO_TTS: "cartesia/sonic",
                    ModelModality.AUDIO_STT: "whisper-medium",
                }
                
                model_id = defaults.get(modality, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        
        logger.info(f"Selected model {model_id} for user {user_id} (tier: {user_tier}, modality: {modality}, purpose: {purpose})")
        return model_id
    
    def get_fallback_model(
        self,
        user_id: str,
        modality: ModelModality,
        primary_model_id: str
    ) -> Optional[str]:
        """
        Get a fallback model for a specific modality and user.
        
        Args:
            user_id: User identifier
            modality: Model modality (text, code, vision, etc.)
            primary_model_id: The primary model that failed
            
        Returns:
            Fallback model ID or None if no suitable fallback
        """
        # Determine user tier
        user_tier = get_user_tier(user_id) or UserTier.FREE
        
        # Get tier-specific model mappings
        tier_mappings = self.MODEL_MAPPINGS.get(user_tier, self.MODEL_MAPPINGS[UserTier.FREE])
        
        # Get modality-specific model mappings
        modality_mappings = tier_mappings.get(modality, {})
        
        # Try to get explicit fallback model
        fallback_model = modality_mappings.get(ModelPurpose.FALLBACK)
        
        # If no explicit fallback and primary model is the fallback, avoid loop
        if not fallback_model or fallback_model == primary_model_id:
            # Try to find any other model for this modality
            for purpose, model_id in modality_mappings.items():
                if purpose != ModelPurpose.FALLBACK and model_id != primary_model_id:
                    fallback_model = model_id
                    break
        
        # If still no fallback, try FREE tier
        if not fallback_model and user_tier != UserTier.FREE:
            free_mappings = self.MODEL_MAPPINGS[UserTier.FREE].get(modality, {})
            fallback_model = free_mappings.get(ModelPurpose.GENERAL)
        
        if fallback_model:
            logger.info(f"Selected fallback model {fallback_model} for user {user_id} (modality: {modality}, primary: {primary_model_id})")
        else:
            logger.warning(f"No fallback model available for modality {modality}")
        
        return fallback_model
    
    def get_available_models_for_tier(
        self,
        tier: UserTier,
        modality: Optional[ModelModality] = None
    ) -> List[Dict[str, Any]]:
        """
        Get a list of available models for a specific tier.
        
        Args:
            tier: User tier
            modality: Optional filter by modality
            
        Returns:
            List of model information dictionaries
        """
        result = []
        
        # Get tier-specific model mappings
        tier_mappings = self.MODEL_MAPPINGS.get(tier, self.MODEL_MAPPINGS[UserTier.FREE])
        
        # Filter by modality if specified
        if modality:
            modality_mappings = tier_mappings.get(modality, {})
            for purpose, model_id in modality_mappings.items():
                result.append({
                    "id": model_id,
                    "modality": modality,
                    "purpose": purpose,
                    "tier": tier
                })
        else:
            # Include all modalities
            for mod, mappings in tier_mappings.items():
                for purpose, model_id in mappings.items():
                    result.append({
                        "id": model_id,
                        "modality": mod,
                        "purpose": purpose,
                        "tier": tier
                    })
        
        return result
    
    def is_model_available_for_tier(
        self,
        model_id: str,
        tier: UserTier
    ) -> bool:
        """
        Check if a specific model is available for a tier.
        
        Args:
            model_id: Model identifier
            tier: User tier
            
        Returns:
            True if the model is available, False otherwise
        """
        # Get tier-specific model mappings
        tier_mappings = self.MODEL_MAPPINGS.get(tier, self.MODEL_MAPPINGS[UserTier.FREE])
        
        # Check if model is in any modality mapping
        for modality_mappings in tier_mappings.values():
            if model_id in modality_mappings.values():
                return True
        
        return False
    
    def get_provider_with_model(
        self,
        user_id: str,
        modality: ModelModality,
        purpose: Optional[ModelPurpose] = None
    ) -> Dict[str, Any]:
        """
        Get a provider instance and appropriate model for a user.
        
        This method returns both a provider instance with the user's API key
        and the appropriate model ID for their tier.
        
        Args:
            user_id: User identifier
            modality: Model modality (text, code, vision, etc.)
            purpose: Optional specific purpose (general, critical, etc.)
            
        Returns:
            Dictionary with provider and model_id
        """
        # Get the key manager
        key_manager = get_together_ai_key_manager()
        
        # Get the appropriate API key for this user
        api_key = key_manager.get_api_key(user_id)
        
        if not api_key:
            logger.warning(f"No API key available for user {user_id}")
            return {"error": "No API key available", "provider": None, "model_id": None}
        
        # Create the provider instance with the user's key
        provider = TogetherAIProvider(api_key=api_key)
        
        # Get the appropriate model for this user
        model_id = self.get_model_for_user(user_id, modality, purpose)
        
        return {
            "provider": provider,
            "model_id": model_id,
            "error": None
        }


# Singleton instance
_instance = None

def get_together_ai_model_selector() -> TogetherAIModelSelector:
    """
    Get the singleton instance of the Together AI model selector.
    
    Returns:
        Together AI model selector instance
    """
    global _instance
    if _instance is None:
        _instance = TogetherAIModelSelector()
    return _instance


