"""
UI model source indicators for Together AI integration.

This module implements UI model source indicators for Together AI integration,
ensuring users can clearly see which provider and model is serving their request.
"""

import logging
from enum import Enum
from typing import Dict, Optional, List, Any, Union

from src.plugins.llm_providers.internal.together_ai_provider import TogetherAIProvider
from src.api_key_management.together_ai_model_selector import (
    get_together_ai_model_selector,
    ModelModality,
    ModelPurpose
)
from src.api_key_management.together_ai_free_tier import (
    get_together_ai_free_tier_manager,
    FreeTierFeature
)
from src.user.subscription import UserTier, get_user_tier
from src.config.feature_flags import FeatureFlag, is_feature_enabled

logger = logging.getLogger(__name__)

class ProviderIndicatorType(str, Enum):
    """Enum for provider indicator types."""
    BADGE = "badge"
    TEXT = "text"
    ICON = "icon"
    TOOLTIP = "tooltip"
    WATERMARK = "watermark"

class ProviderIndicatorPosition(str, Enum):
    """Enum for provider indicator positions."""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    INLINE = "inline"

class ModelSourceIndicator:
    """
    Model source indicator for UI display.
    
    This class represents a model source indicator that can be
    included in API responses and rendered in the UI.
    """
    
    def __init__(
        self,
        provider_id: str,
        model_id: str,
        indicator_type: ProviderIndicatorType = ProviderIndicatorType.BADGE,
        position: ProviderIndicatorPosition = ProviderIndicatorPosition.BOTTOM_RIGHT,
        display_name: Optional[str] = None,
        icon_url: Optional[str] = None,
        color: Optional[str] = None,
        tooltip: Optional[str] = None,
        is_fallback: bool = False,
        is_free_tier: bool = False
    ):
        """
        Initialize a model source indicator.
        
        Args:
            provider_id: Provider identifier
            model_id: Model identifier
            indicator_type: Type of indicator
            position: Position of indicator
            display_name: Optional display name
            icon_url: Optional icon URL
            color: Optional color
            tooltip: Optional tooltip text
            is_fallback: Whether this is a fallback model
            is_free_tier: Whether this is a free tier model
        """
        self.provider_id = provider_id
        self.model_id = model_id
        self.indicator_type = indicator_type
        self.position = position
        self.display_name = display_name
        self.icon_url = icon_url
        self.color = color
        self.tooltip = tooltip
        self.is_fallback = is_fallback
        self.is_free_tier = is_free_tier
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for API response.
        
        Returns:
            Dictionary representation
        """
        return {
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "indicator_type": self.indicator_type,
            "position": self.position,
            "display_name": self.display_name,
            "icon_url": self.icon_url,
            "color": self.color,
            "tooltip": self.tooltip,
            "is_fallback": self.is_fallback,
            "is_free_tier": self.is_free_tier
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelSourceIndicator':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            ModelSourceIndicator instance
        """
        return cls(
            provider_id=data["provider_id"],
            model_id=data["model_id"],
            indicator_type=data.get("indicator_type", ProviderIndicatorType.BADGE),
            position=data.get("position", ProviderIndicatorPosition.BOTTOM_RIGHT),
            display_name=data.get("display_name"),
            icon_url=data.get("icon_url"),
            color=data.get("color"),
            tooltip=data.get("tooltip"),
            is_fallback=data.get("is_fallback", False),
            is_free_tier=data.get("is_free_tier", False)
        )


class TogetherAIIndicatorManager:
    """
    Manager for Together AI model source indicators.
    
    This class handles the creation and management of model source
    indicators for Together AI models.
    """
    
    # Provider display information
    PROVIDER_INFO = {
        "together_ai": {
            "display_name": "Together AI",
            "icon_url": "/assets/images/providers/together_ai_logo.png",
            "color": "#6366f1",  # Indigo
            "tooltip_template": "Powered by {model_name} via Together AI"
        },
        "openai": {
            "display_name": "OpenAI",
            "icon_url": "/assets/images/providers/openai_logo.png",
            "color": "#10b981",  # Emerald
            "tooltip_template": "Powered by {model_name} via OpenAI"
        },
        "anthropic": {
            "display_name": "Anthropic",
            "icon_url": "/assets/images/providers/anthropic_logo.png",
            "color": "#f59e0b",  # Amber
            "tooltip_template": "Powered by {model_name} via Anthropic"
        },
        "gemini": {
            "display_name": "Google Gemini",
            "icon_url": "/assets/images/providers/gemini_logo.png",
            "color": "#3b82f6",  # Blue
            "tooltip_template": "Powered by {model_name} via Google Gemini"
        },
        "ollama": {
            "display_name": "Ollama",
            "icon_url": "/assets/images/providers/ollama_logo.png",
            "color": "#8b5cf6",  # Violet
            "tooltip_template": "Powered by {model_name} via Ollama"
        }
    }
    
    # Model display names (for common models)
    MODEL_DISPLAY_NAMES = {
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": "Llama 3.1 405B",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": "Llama 3.1 70B",
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": "Llama 3.1 8B",
        "mistralai/Mixtral-8x7B-Instruct-v0.1": "Mixtral 8x7B",
        "deepseek-ai/deepseek-coder-33b-instruct": "DeepSeek Coder 33B",
        "codellama/CodeLlama-70b-Instruct-hf": "CodeLlama 70B",
        "Nexusflow/NexusRaven-V2-13B": "NexusRaven V2",
        "codellama/CodeLlama-13b-Instruct-hf": "CodeLlama 13B",
        "Qwen/Qwen-VL-Chat": "Qwen VL",
        "deepseek-ai/DeepSeek-VL-7B-Chat": "DeepSeek VL",
        "stabilityai/stable-diffusion-xl-base-1.0": "SDXL",
        "stabilityai/sdxl-turbo": "SDXL Turbo",
        "playgroundai/playground-v2.5": "Playground v2.5",
        "runwayml/stable-diffusion-v1-5": "SD v1.5",
        "cartesia/sonic": "Sonic TTS",
        "whisper-large-v3": "Whisper Large v3",
        "whisper-medium": "Whisper Medium",
        "gpt-4-turbo": "GPT-4 Turbo",
        "gpt-4": "GPT-4",
        "gpt-3.5-turbo": "GPT-3.5 Turbo",
        "claude-3-opus-20240229": "Claude 3 Opus",
        "claude-3-sonnet-20240229": "Claude 3 Sonnet",
        "claude-3-haiku-20240307": "Claude 3 Haiku",
        "gemini-pro": "Gemini Pro",
        "gemini-pro-vision": "Gemini Pro Vision"
    }
    
    def __init__(self):
        """Initialize the indicator manager."""
        self.model_selector = get_together_ai_model_selector()
        self.free_tier_manager = get_together_ai_free_tier_manager()
    
    def _get_model_display_name(self, model_id: str) -> str:
        """
        Get a user-friendly display name for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            User-friendly display name
        """
        # Check if we have a predefined display name
        if model_id in self.MODEL_DISPLAY_NAMES:
            return self.MODEL_DISPLAY_NAMES[model_id]
        
        # Extract name from model ID
        parts = model_id.split("/")
        if len(parts) > 1:
            # Format like "Organization/Model" -> "Model"
            return parts[-1]
        
        # Just return the model ID if no better name is available
        return model_id
    
    def _get_provider_info(self, provider_id: str) -> Dict[str, Any]:
        """
        Get provider display information.
        
        Args:
            provider_id: Provider identifier
            
        Returns:
            Provider display information
        """
        # Check if we have predefined provider info
        if provider_id in self.PROVIDER_INFO:
            return self.PROVIDER_INFO[provider_id]
        
        # Return generic info
        return {
            "display_name": provider_id.title(),
            "icon_url": "/assets/images/providers/generic_logo.png",
            "color": "#6b7280",  # Gray
            "tooltip_template": "Powered by {model_name}"
        }
    
    def create_indicator(
        self,
        provider_id: str,
        model_id: str,
        is_fallback: bool = False,
        is_free_tier: bool = False,
        indicator_type: Optional[ProviderIndicatorType] = None,
        position: Optional[ProviderIndicatorPosition] = None
    ) -> ModelSourceIndicator:
        """
        Create a model source indicator.
        
        Args:
            provider_id: Provider identifier
            model_id: Model identifier
            is_fallback: Whether this is a fallback model
            is_free_tier: Whether this is a free tier model
            indicator_type: Optional indicator type
            position: Optional indicator position
            
        Returns:
            ModelSourceIndicator instance
        """
        # Get provider info
        provider_info = self._get_provider_info(provider_id)
        
        # Get model display name
        model_display_name = self._get_model_display_name(model_id)
        
        # Create tooltip
        tooltip = provider_info["tooltip_template"].format(model_name=model_display_name)
        
        # Add fallback/free tier info to tooltip
        if is_fallback:
            tooltip += " (Fallback)"
        if is_free_tier:
            tooltip += " (Free Tier)"
        
        # Use default indicator type and position if not specified
        if indicator_type is None:
            indicator_type = ProviderIndicatorType.BADGE
        if position is None:
            position = ProviderIndicatorPosition.BOTTOM_RIGHT
        
        # Create indicator
        return ModelSourceIndicator(
            provider_id=provider_id,
            model_id=model_id,
            indicator_type=indicator_type,
            position=position,
            display_name=provider_info["display_name"],
            icon_url=provider_info["icon_url"],
            color=provider_info["color"],
            tooltip=tooltip,
            is_fallback=is_fallback,
            is_free_tier=is_free_tier
        )
    
    def create_indicator_for_response(
        self,
        response: Dict[str, Any],
        indicator_type: Optional[ProviderIndicatorType] = None,
        position: Optional[ProviderIndicatorPosition] = None
    ) -> Optional[ModelSourceIndicator]:
        """
        Create a model source indicator for an API response.
        
        Args:
            response: API response dictionary
            indicator_type: Optional indicator type
            position: Optional indicator position
            
        Returns:
            ModelSourceIndicator instance or None if not applicable
        """
        # Check if response contains provider and model info
        provider_id = response.get("provider")
        model_id = response.get("model_id")
        
        if not provider_id or not model_id:
            return None
        
        # Check if response indicates fallback
        is_fallback = response.get("fallback_used", False)
        
        # Check if response indicates free tier
        is_free_tier = response.get("is_free_tier", False)
        
        # Create indicator
        return self.create_indicator(
            provider_id=provider_id,
            model_id=model_id,
            is_fallback=is_fallback,
            is_free_tier=is_free_tier,
            indicator_type=indicator_type,
            position=position
        )
    
    def add_indicator_to_response(
        self,
        response: Dict[str, Any],
        indicator_type: Optional[ProviderIndicatorType] = None,
        position: Optional[ProviderIndicatorPosition] = None
    ) -> Dict[str, Any]:
        """
        Add a model source indicator to an API response.
        
        Args:
            response: API response dictionary
            indicator_type: Optional indicator type
            position: Optional indicator position
            
        Returns:
            Updated API response dictionary
        """
        # Create indicator
        indicator = self.create_indicator_for_response(
            response=response,
            indicator_type=indicator_type,
            position=position
        )
        
        if indicator:
            # Add indicator to response
            response["model_source_indicator"] = indicator.to_dict()
        
        return response
    
    def get_indicator_for_user_request(
        self,
        user_id: str,
        modality: ModelModality,
        purpose: Optional[ModelPurpose] = None,
        indicator_type: Optional[ProviderIndicatorType] = None,
        position: Optional[ProviderIndicatorPosition] = None
    ) -> ModelSourceIndicator:
        """
        Get a model source indicator for a user request.
        
        Args:
            user_id: User identifier
            modality: Model modality
            purpose: Optional specific purpose
            indicator_type: Optional indicator type
            position: Optional indicator position
            
        Returns:
            ModelSourceIndicator instance
        """
        # Get user tier
        user_tier = get_user_tier(user_id) or UserTier.FREE
        
        # Determine if free tier
        is_free_tier = user_tier == UserTier.FREE
        
        # Get model for user
        model_id = self.model_selector.get_model_for_user(
            user_id=user_id,
            modality=modality,
            purpose=purpose
        )
        
        # Create indicator
        return self.create_indicator(
            provider_id="together_ai",
            model_id=model_id,
            is_fallback=False,
            is_free_tier=is_free_tier,
            indicator_type=indicator_type,
            position=position
        )


# Singleton instance
_instance = None

def get_together_ai_indicator_manager() -> TogetherAIIndicatorManager:
    """
    Get the singleton instance of the Together AI indicator manager.
    
    Returns:
        Together AI indicator manager instance
    """
    global _instance
    if _instance is None:
        _instance = TogetherAIIndicatorManager()
    return _instance


# Frontend component integration

def get_frontend_indicator_config() -> Dict[str, Any]:
    """
    Get frontend configuration for model source indicators.
    
    This function returns a configuration object that can be used
    by frontend components to render model source indicators.
    
    Returns:
        Frontend configuration dictionary
    """
    manager = get_together_ai_indicator_manager()
    
    # Get provider info for all providers
    provider_info = {}
    for provider_id, info in manager.PROVIDER_INFO.items():
        provider_info[provider_id] = {
            "display_name": info["display_name"],
            "icon_url": info["icon_url"],
            "color": info["color"]
        }
    
    # Create configuration
    return {
        "providers": provider_info,
        "indicator_types": [t.value for t in ProviderIndicatorType],
        "positions": [p.value for p in ProviderIndicatorPosition],
        "default_type": ProviderIndicatorType.BADGE.value,
        "default_position": ProviderIndicatorPosition.BOTTOM_RIGHT.value
    }


# API middleware integration

class ModelSourceIndicatorMiddleware:
    """
    Middleware for adding model source indicators to API responses.
    
    This middleware automatically adds model source indicators to
    API responses that contain provider and model information.
    """
    
    def __init__(self):
        """Initialize the middleware."""
        self.indicator_manager = get_together_ai_indicator_manager()
    
    async def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an API response.
        
        Args:
            response: API response dictionary
            
        Returns:
            Updated API response dictionary
        """
        # Check if response is a dictionary
        if not isinstance(response, dict):
            return response
        
        # Add indicator to response
        return self.indicator_manager.add_indicator_to_response(response)


# Register middleware
def register_indicator_middleware():
    """Register the model source indicator middleware."""
    try:
        from src.api.middleware import register_response_middleware
        middleware = ModelSourceIndicatorMiddleware()
        register_response_middleware(middleware.process_response)
        logger.info("Registered model source indicator middleware")
    except Exception as e:
        logger.error(f"Failed to register model source indicator middleware: {str(e)}")


# Frontend React component (TypeScript)
FRONTEND_COMPONENT_CODE = """
// ModelSourceIndicator.tsx
import React from 'react';

interface ModelSourceIndicatorProps {
  indicator: {
    provider_id: string;
    model_id: string;
    indicator_type: string;
    position: string;
    display_name?: string;
    icon_url?: string;
    color?: string;
    tooltip?: string;
    is_fallback: boolean;
    is_free_tier: boolean;
  };
  className?: string;
  style?: React.CSSProperties;
}

const ModelSourceIndicator: React.FC<ModelSourceIndicatorProps> = ({
  indicator,
  className = '',
  style = {},
}) => {
  const {
    provider_id,
    model_id,
    indicator_type,
    position,
    display_name,
    icon_url,
    color,
    tooltip,
    is_fallback,
    is_free_tier,
  } = indicator;

  // Determine position classes
  const positionClasses = {
    top_left: 'top-2 left-2',
    top_right: 'top-2 right-2',
    bottom_left: 'bottom-2 left-2',
    bottom_right: 'bottom-2 right-2',
    inline: 'inline-flex',
  }[position] || 'bottom-right';

  // Determine if position is inline or absolute
  const isInline = position === 'inline';
  const positionStyle = isInline ? {} : { position: 'absolute' };

  // Render different indicator types
  switch (indicator_type) {
    case 'badge':
      return (
        <div
          className={`flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-white ${
            isInline ? 'inline-flex' : 'absolute'
          } ${positionClasses} ${className}`}
          style={{ backgroundColor: color || '#6b7280', ...positionStyle, ...style }}
          title={tooltip}
        >
          {icon_url && (
            <img src={icon_url} alt={display_name || provider_id} className="h-4 w-4" />
          )}
          <span>{display_name || provider_id}</span>
          {is_fallback && <span className="ml-1">(Fallback)</span>}
          {is_free_tier && <span className="ml-1">(Free)</span>}
        </div>
      );

    case 'icon':
      return (
        <div
          className={`flex items-center justify-center rounded-full p-1 ${
            isInline ? 'inline-flex' : 'absolute'
          } ${positionClasses} ${className}`}
          style={{ backgroundColor: color || '#6b7280', ...positionStyle, ...style }}
          title={tooltip}
        >
          {icon_url ? (
            <img src={icon_url} alt={display_name || provider_id} className="h-5 w-5" />
          ) : (
            <span className="h-5 w-5 flex items-center justify-center text-white text-xs font-bold">
              {(display_name || provider_id).charAt(0)}
            </span>
          )}
        </div>
      );

    case 'text':
      return (
        <div
          className={`text-xs ${isInline ? 'inline' : 'absolute'} ${positionClasses} ${className}`}
          style={{ color: color || '#6b7280', ...positionStyle, ...style }}
          title={tooltip}
        >
          {display_name || provider_id}
          {is_fallback && <span className="ml-1">(Fallback)</span>}
          {is_free_tier && <span className="ml-1">(Free)</span>}
        </div>
      );

    case 'tooltip':
      // Tooltip is invisible but shows on hover
      return (
        <div
          className={`cursor-help ${isInline ? 'inline' : 'absolute'} ${positionClasses} ${className}`}
          style={{ ...positionStyle, ...style }}
          title={tooltip}
        >
          <span className="sr-only">{tooltip}</span>
          <div className="h-4 w-4 rounded-full border border-gray-300"></div>
        </div>
      );

    case 'watermark':
      return (
        <div
          className={`pointer-events-none select-none opacity-20 ${
            isInline ? 'inline-flex' : 'absolute'
          } ${positionClasses} ${className}`}
          style={{ ...positionStyle, ...style }}
          title={tooltip}
        >
          {icon_url ? (
            <img src={icon_url} alt={display_name || provider_id} className="h-8 w-8" />
          ) : (
            <span className="text-sm font-medium" style={{ color: color || '#6b7280' }}>
              {display_name || provider_id}
            </span>
          )}
        </div>
      );

    default:
      return null;
  }
};

export default ModelSourceIndicator;
"""
