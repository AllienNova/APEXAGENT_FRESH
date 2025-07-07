"""
API endpoints for tier-aware routing in Together AI integration.

This module implements API endpoints for tier-aware routing in Together AI integration,
ensuring requests are properly routed according to user tier and selected model.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path, Request
from pydantic import BaseModel, Field

from llm_providers.together_ai import TogetherAIProvider
from api_key_management.together_ai_key_manager import get_together_ai_key_manager
from api_key_management.together_ai_model_selector import (
    get_together_ai_model_selector,
    ModelModality,
    ModelPurpose,
    TogetherAIModelSelector
)
from api_key_management.together_ai_fallback import (
    get_together_ai_fallback_manager,
    generate_text_with_fallback,
    generate_chat_with_fallback,
    generate_code_with_fallback,
    analyze_image_with_fallback,
    generate_image_with_fallback
)
from api_key_management.together_ai_free_tier import (
    get_together_ai_free_tier_manager,
    FreeTierFeature,
    FreeTierQuotaType,
    can_use_text_generation,
    record_text_generation_usage,
    can_use_image_generation,
    record_image_generation_usage
)
from api_key_management.together_ai_ui_indicators import (
    get_together_ai_indicator_manager,
    ModelSourceIndicator,
    ProviderIndicatorType,
    ProviderIndicatorPosition
)
from user.auth import get_current_user, User
from user.subscription import get_user_tier, UserTier
from config.feature_flags import FeatureFlag, is_feature_enabled
from monitoring.metrics import record_api_request, record_api_error

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/together",
    tags=["together_ai"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        429: {"description": "Rate limit exceeded"},
    },
)


# Request/response models
class TextCompletionRequest(BaseModel):
    """Text completion request model."""
    
    prompt: str = Field(..., description="Text prompt for completion")
    max_tokens: int = Field(256, description="Maximum number of tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    purpose: Optional[str] = Field(None, description="Specific purpose for model selection")
    stream: bool = Field(False, description="Whether to stream the response")


class ChatCompletionRequest(BaseModel):
    """Chat completion request model."""
    
    messages: List[Dict[str, str]] = Field(..., description="List of chat messages")
    max_tokens: int = Field(256, description="Maximum number of tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    purpose: Optional[str] = Field(None, description="Specific purpose for model selection")
    stream: bool = Field(False, description="Whether to stream the response")


class CodeCompletionRequest(BaseModel):
    """Code completion request model."""
    
    prompt: str = Field(..., description="Code prompt for completion")
    max_tokens: int = Field(512, description="Maximum number of tokens to generate")
    temperature: float = Field(0.2, description="Sampling temperature")
    purpose: Optional[str] = Field(None, description="Specific purpose for model selection")
    language: Optional[str] = Field(None, description="Programming language")
    stream: bool = Field(False, description="Whether to stream the response")


class ImageGenerationRequest(BaseModel):
    """Image generation request model."""
    
    prompt: str = Field(..., description="Image prompt for generation")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt")
    width: int = Field(1024, description="Image width")
    height: int = Field(1024, description="Image height")
    num_inference_steps: int = Field(50, description="Number of inference steps")
    purpose: Optional[str] = Field(None, description="Specific purpose for model selection")


class ImageAnalysisRequest(BaseModel):
    """Image analysis request model."""
    
    image_url: str = Field(..., description="URL of the image to analyze")
    prompt: str = Field(..., description="Text prompt describing what to analyze")
    max_tokens: int = Field(256, description="Maximum number of tokens to generate")
    purpose: Optional[str] = Field(None, description="Specific purpose for model selection")


class AudioTranscriptionRequest(BaseModel):
    """Audio transcription request model."""
    
    audio_url: str = Field(..., description="URL of the audio to transcribe")
    language: Optional[str] = Field(None, description="Language of the audio")
    purpose: Optional[str] = Field(None, description="Specific purpose for model selection")


class TextToSpeechRequest(BaseModel):
    """Text to speech request model."""
    
    text: str = Field(..., description="Text to convert to speech")
    voice: Optional[str] = Field(None, description="Voice to use")
    purpose: Optional[str] = Field(None, description="Specific purpose for model selection")


class ModelListResponse(BaseModel):
    """Model list response model."""
    
    models: List[Dict[str, Any]] = Field(..., description="List of available models")
    user_tier: str = Field(..., description="User's subscription tier")
    free_tier_enabled: bool = Field(..., description="Whether free tier is enabled")


# Helper functions
def get_model_purpose(purpose_str: Optional[str]) -> Optional[ModelPurpose]:
    """
    Convert purpose string to ModelPurpose enum.
    
    Args:
        purpose_str: Purpose string
        
    Returns:
        ModelPurpose enum or None
    """
    if not purpose_str:
        return None
    
    try:
        return ModelPurpose(purpose_str)
    except ValueError:
        logger.warning(f"Invalid purpose: {purpose_str}")
        return None


async def check_free_tier_access(
    user: User,
    feature: FreeTierFeature,
    token_count: Optional[int] = None
) -> None:
    """
    Check if user has access to free tier feature.
    
    Args:
        user: User object
        feature: Free tier feature
        token_count: Optional token count for text/code requests
        
    Raises:
        HTTPException: If user does not have access
    """
    # Get user tier
    user_tier = get_user_tier(user.id) or UserTier.FREE
    
    # Premium users bypass free tier restrictions
    if user_tier != UserTier.FREE:
        return
    
    # Get free tier manager
    free_tier_manager = get_together_ai_free_tier_manager()
    
    # Check if user can use feature
    can_use, reason = free_tier_manager.can_use_feature(user.id, feature)
    if not can_use:
        raise HTTPException(status_code=403, detail=reason)
    
    # Check token quota if applicable
    if token_count is not None:
        within_quota, reason = free_tier_manager.check_token_quota(
            user_id=user.id,
            feature=feature,
            token_count=token_count
        )
        if not within_quota:
            raise HTTPException(status_code=429, detail=reason)


# API endpoints
@router.get("/models", response_model=ModelListResponse)
async def list_models(
    request: Request,
    user: User = Depends(get_current_user),
    modality: Optional[str] = Query(None, description="Filter by modality")
):
    """
    List available models for the user.
    
    Args:
        request: Request object
        user: Current user
        modality: Optional filter by modality
        
    Returns:
        List of available models
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/models",
            user_id=user.id,
            method="GET"
        )
        
        # Get user tier
        user_tier = get_user_tier(user.id) or UserTier.FREE
        
        # Get model selector
        model_selector = get_together_ai_model_selector()
        
        # Get free tier manager
        free_tier_manager = get_together_ai_free_tier_manager()
        
        # Convert modality string to enum if provided
        modality_enum = None
        if modality:
            try:
                modality_enum = ModelModality(modality)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid modality: {modality}")
        
        # Get available models for user's tier
        models = model_selector.get_available_models_for_tier(
            tier=user_tier,
            modality=modality_enum
        )
        
        # Add indicator information
        indicator_manager = get_together_ai_indicator_manager()
        for model in models:
            indicator = indicator_manager.create_indicator(
                provider_id="together_ai",
                model_id=model["id"],
                is_fallback=False,
                is_free_tier=user_tier == UserTier.FREE
            )
            model["indicator"] = indicator.to_dict()
        
        # Create response
        response = {
            "models": models,
            "user_tier": str(user_tier),
            "free_tier_enabled": free_tier_manager.is_free_tier_enabled()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/models",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")


@router.post("/text/completions")
async def text_completions(
    request: Request,
    req_body: TextCompletionRequest,
    user: User = Depends(get_current_user)
):
    """
    Generate text completions.
    
    Args:
        request: Request object
        req_body: Request body
        user: Current user
        
    Returns:
        Text completion response
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/text/completions",
            user_id=user.id,
            method="POST"
        )
        
        # Estimate token count
        estimated_tokens = len(req_body.prompt.split()) * 1.3  # Rough estimate
        
        # Check free tier access
        await check_free_tier_access(
            user=user,
            feature=FreeTierFeature.TEXT_GENERATION,
            token_count=int(estimated_tokens) + req_body.max_tokens
        )
        
        # Get model purpose
        purpose = get_model_purpose(req_body.purpose)
        
        # Generate completion with fallback
        result = await generate_text_with_fallback(
            user_id=user.id,
            prompt=req_body.prompt,
            purpose=purpose
        )
        
        # Record usage for free tier
        user_tier = get_user_tier(user.id) or UserTier.FREE
        if user_tier == UserTier.FREE and "usage" in result:
            record_text_generation_usage(
                user_id=user.id,
                token_count=result["usage"].get("total_tokens", 0)
            )
        
        # Add indicator to response
        indicator_manager = get_together_ai_indicator_manager()
        result = indicator_manager.add_indicator_to_response(result)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error generating text completion: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/text/completions",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error generating text completion: {str(e)}")


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    req_body: ChatCompletionRequest,
    user: User = Depends(get_current_user)
):
    """
    Generate chat completions.
    
    Args:
        request: Request object
        req_body: Request body
        user: Current user
        
    Returns:
        Chat completion response
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/chat/completions",
            user_id=user.id,
            method="POST"
        )
        
        # Estimate token count
        estimated_tokens = sum(len(msg.get("content", "").split()) for msg in req_body.messages) * 1.3
        
        # Check free tier access
        await check_free_tier_access(
            user=user,
            feature=FreeTierFeature.TEXT_GENERATION,
            token_count=int(estimated_tokens) + req_body.max_tokens
        )
        
        # Get model purpose
        purpose = get_model_purpose(req_body.purpose)
        
        # Generate chat completion with fallback
        result = await generate_chat_with_fallback(
            user_id=user.id,
            messages=req_body.messages,
            purpose=purpose
        )
        
        # Record usage for free tier
        user_tier = get_user_tier(user.id) or UserTier.FREE
        if user_tier == UserTier.FREE and "usage" in result:
            record_text_generation_usage(
                user_id=user.id,
                token_count=result["usage"].get("total_tokens", 0)
            )
        
        # Add indicator to response
        indicator_manager = get_together_ai_indicator_manager()
        result = indicator_manager.add_indicator_to_response(result)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error generating chat completion: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/chat/completions",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error generating chat completion: {str(e)}")


@router.post("/code/completions")
async def code_completions(
    request: Request,
    req_body: CodeCompletionRequest,
    user: User = Depends(get_current_user)
):
    """
    Generate code completions.
    
    Args:
        request: Request object
        req_body: Request body
        user: Current user
        
    Returns:
        Code completion response
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/code/completions",
            user_id=user.id,
            method="POST"
        )
        
        # Estimate token count
        estimated_tokens = len(req_body.prompt.split()) * 1.3
        
        # Check free tier access
        await check_free_tier_access(
            user=user,
            feature=FreeTierFeature.CODE_GENERATION,
            token_count=int(estimated_tokens) + req_body.max_tokens
        )
        
        # Get model purpose
        purpose = get_model_purpose(req_body.purpose)
        
        # Generate code completion with fallback
        result = await generate_code_with_fallback(
            user_id=user.id,
            prompt=req_body.prompt,
            purpose=purpose
        )
        
        # Record usage for free tier
        user_tier = get_user_tier(user.id) or UserTier.FREE
        if user_tier == UserTier.FREE and "usage" in result:
            free_tier_manager = get_together_ai_free_tier_manager()
            free_tier_manager.record_request(
                user_id=user.id,
                modality=ModelModality.CODE,
                token_count=result["usage"].get("total_tokens", 0)
            )
        
        # Add indicator to response
        indicator_manager = get_together_ai_indicator_manager()
        result = indicator_manager.add_indicator_to_response(result)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error generating code completion: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/code/completions",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error generating code completion: {str(e)}")


@router.post("/images/generations")
async def image_generations(
    request: Request,
    req_body: ImageGenerationRequest,
    user: User = Depends(get_current_user)
):
    """
    Generate images.
    
    Args:
        request: Request object
        req_body: Request body
        user: Current user
        
    Returns:
        Image generation response
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/images/generations",
            user_id=user.id,
            method="POST"
        )
        
        # Check free tier access
        await check_free_tier_access(
            user=user,
            feature=FreeTierFeature.IMAGE_GENERATION
        )
        
        # Get model purpose
        purpose = get_model_purpose(req_body.purpose)
        
        # Generate image with fallback
        result = await generate_image_with_fallback(
            user_id=user.id,
            prompt=req_body.prompt,
            purpose=purpose
        )
        
        # Record usage for free tier
        user_tier = get_user_tier(user.id) or UserTier.FREE
        if user_tier == UserTier.FREE:
            free_tier_manager = get_together_ai_free_tier_manager()
            free_tier_manager.record_request(
                user_id=user.id,
                modality=ModelModality.IMAGE
            )
        
        # Add indicator to response
        indicator_manager = get_together_ai_indicator_manager()
        result = indicator_manager.add_indicator_to_response(result)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/images/generations",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")


@router.post("/images/analysis")
async def image_analysis(
    request: Request,
    req_body: ImageAnalysisRequest,
    user: User = Depends(get_current_user)
):
    """
    Analyze images.
    
    Args:
        request: Request object
        req_body: Request body
        user: Current user
        
    Returns:
        Image analysis response
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/images/analysis",
            user_id=user.id,
            method="POST"
        )
        
        # Check free tier access
        await check_free_tier_access(
            user=user,
            feature=FreeTierFeature.VISION_ANALYSIS
        )
        
        # Get model purpose
        purpose = get_model_purpose(req_body.purpose)
        
        # Analyze image with fallback
        result = await analyze_image_with_fallback(
            user_id=user.id,
            image_url=req_body.image_url,
            prompt=req_body.prompt,
            purpose=purpose
        )
        
        # Record usage for free tier
        user_tier = get_user_tier(user.id) or UserTier.FREE
        if user_tier == UserTier.FREE:
            free_tier_manager = get_together_ai_free_tier_manager()
            free_tier_manager.record_request(
                user_id=user.id,
                modality=ModelModality.VISION
            )
        
        # Add indicator to response
        indicator_manager = get_together_ai_indicator_manager()
        result = indicator_manager.add_indicator_to_response(result)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/images/analysis",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


@router.post("/audio/transcriptions")
async def audio_transcriptions(
    request: Request,
    req_body: AudioTranscriptionRequest,
    user: User = Depends(get_current_user)
):
    """
    Transcribe audio.
    
    Args:
        request: Request object
        req_body: Request body
        user: Current user
        
    Returns:
        Audio transcription response
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/audio/transcriptions",
            user_id=user.id,
            method="POST"
        )
        
        # Check free tier access
        await check_free_tier_access(
            user=user,
            feature=FreeTierFeature.AUDIO_STT
        )
        
        # Get model purpose
        purpose = get_model_purpose(req_body.purpose)
        
        # Get model selector
        model_selector = get_together_ai_model_selector()
        
        # Get provider with model
        result = model_selector.get_provider_with_model(
            user_id=user.id,
            modality=ModelModality.AUDIO_STT,
            purpose=purpose
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        provider = result["provider"]
        model_id = result["model_id"]
        
        # Transcribe audio
        transcription = await provider.transcribe_audio(
            audio_url=req_body.audio_url,
            model=model_id,
            language=req_body.language
        )
        
        # Record usage for free tier
        user_tier = get_user_tier(user.id) or UserTier.FREE
        if user_tier == UserTier.FREE:
            free_tier_manager = get_together_ai_free_tier_manager()
            free_tier_manager.record_request(
                user_id=user.id,
                modality=ModelModality.AUDIO_STT
            )
        
        # Add provider and model info
        response = {
            **transcription,
            "provider": "together_ai",
            "model_id": model_id
        }
        
        # Add indicator to response
        indicator_manager = get_together_ai_indicator_manager()
        response = indicator_manager.add_indicator_to_response(response)
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/audio/transcriptions",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")


@router.post("/audio/speech")
async def text_to_speech(
    request: Request,
    req_body: TextToSpeechRequest,
    user: User = Depends(get_current_user)
):
    """
    Convert text to speech.
    
    Args:
        request: Request object
        req_body: Request body
        user: Current user
        
    Returns:
        Text to speech response
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/audio/speech",
            user_id=user.id,
            method="POST"
        )
        
        # Check free tier access
        await check_free_tier_access(
            user=user,
            feature=FreeTierFeature.AUDIO_TTS
        )
        
        # Get model purpose
        purpose = get_model_purpose(req_body.purpose)
        
        # Get model selector
        model_selector = get_together_ai_model_selector()
        
        # Get provider with model
        result = model_selector.get_provider_with_model(
            user_id=user.id,
            modality=ModelModality.AUDIO_TTS,
            purpose=purpose
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        provider = result["provider"]
        model_id = result["model_id"]
        
        # Convert text to speech
        speech = await provider.text_to_speech(
            text=req_body.text,
            model=model_id,
            voice=req_body.voice
        )
        
        # Record usage for free tier
        user_tier = get_user_tier(user.id) or UserTier.FREE
        if user_tier == UserTier.FREE:
            free_tier_manager = get_together_ai_free_tier_manager()
            free_tier_manager.record_request(
                user_id=user.id,
                modality=ModelModality.AUDIO_TTS
            )
        
        # Add provider and model info
        response = {
            **speech,
            "provider": "together_ai",
            "model_id": model_id
        }
        
        # Add indicator to response
        indicator_manager = get_together_ai_indicator_manager()
        response = indicator_manager.add_indicator_to_response(response)
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Error converting text to speech: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/audio/speech",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")


@router.get("/quota")
async def get_quota(
    request: Request,
    user: User = Depends(get_current_user)
):
    """
    Get user's quota information.
    
    Args:
        request: Request object
        user: Current user
        
    Returns:
        Quota information
    """
    try:
        # Record API request
        record_api_request(
            endpoint="/api/v1/together/quota",
            user_id=user.id,
            method="GET"
        )
        
        # Get free tier manager
        free_tier_manager = get_together_ai_free_tier_manager()
        
        # Get usage summary
        usage_summary = free_tier_manager.get_usage_summary(user.id)
        
        return usage_summary
        
    except Exception as e:
        logger.error(f"Error getting quota information: {str(e)}")
        record_api_error(
            endpoint="/api/v1/together/quota",
            user_id=user.id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error getting quota information: {str(e)}")


# Register router with FastAPI app
def register_together_ai_api_endpoints(app):
    """
    Register Together AI API endpoints with FastAPI app.
    
    Args:
        app: FastAPI app
    """
    try:
        app.include_router(router)
        logger.info("Registered Together AI API endpoints")
    except Exception as e:
        logger.error(f"Failed to register Together AI API endpoints: {str(e)}")
