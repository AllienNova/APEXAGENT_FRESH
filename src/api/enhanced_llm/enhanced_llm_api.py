"""
Enhanced LLM Provider API Endpoints
Provides comprehensive access to restored LLM providers with advanced features
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime

# Import restored LLM provider components
from services.ai_core.ApexAgent.src.plugins.llm_providers.base_provider import BaseProvider
from services.ai_core.ApexAgent.src.plugins.llm_providers.providers.openai_provider import OpenAIProvider
from services.ai_core.ApexAgent.src.plugins.llm_providers.providers.anthropic_claude_provider import AnthropicProvider
from services.ai_core.ApexAgent.src.plugins.llm_providers.providers.gemini_provider import GeminiProvider
from services.ai_core.ApexAgent.src.plugins.llm_providers.providers.together_ai_provider import TogetherAIProvider
from services.ai_core.ApexAgent.src.plugins.llm_providers.providers.ollama_provider import OllamaProvider

router = APIRouter(prefix="/api/v1/llm/enhanced", tags=["Enhanced LLM Providers"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize LLM providers
providers = {
    "openai": OpenAIProvider(),
    "anthropic": AnthropicProvider(),
    "gemini": GeminiProvider(),
    "together_ai": TogetherAIProvider(),
    "ollama": OllamaProvider()
}

# Pydantic models
class EnhancedChatRequest(BaseModel):
    provider: str = Field(..., description="LLM provider name")
    model: str = Field(..., description="Model name")
    messages: List[Dict[str, str]] = Field(..., description="Chat messages")
    temperature: Optional[float] = Field(0.7, description="Temperature for randomness")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Enable streaming response")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Available tools")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")

class ModelComparisonRequest(BaseModel):
    providers: List[str] = Field(..., description="Providers to compare")
    prompt: str = Field(..., description="Test prompt")
    criteria: List[str] = Field(..., description="Comparison criteria")
    models: Optional[Dict[str, str]] = Field(None, description="Specific models per provider")

class ProviderConfigRequest(BaseModel):
    provider: str = Field(..., description="Provider name")
    config: Dict[str, Any] = Field(..., description="Configuration parameters")
    api_key: Optional[str] = Field(None, description="API key")
    endpoint: Optional[str] = Field(None, description="Custom endpoint")

class MultiModalRequest(BaseModel):
    provider: str = Field(..., description="Provider supporting multimodal")
    model: str = Field(..., description="Multimodal model name")
    text_input: Optional[str] = Field(None, description="Text input")
    image_inputs: Optional[List[str]] = Field(None, description="Base64 encoded images")
    audio_input: Optional[str] = Field(None, description="Base64 encoded audio")
    video_input: Optional[str] = Field(None, description="Base64 encoded video")
    task_type: str = Field(..., description="Task type (chat, analysis, generation)")

# Enhanced chat endpoint
@router.post("/chat/advanced")
async def enhanced_chat(
    request: EnhancedChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Advanced chat with enhanced features and provider selection
    """
    try:
        # Verify provider exists
        if request.provider not in providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' not available"
            )
        
        provider = providers[request.provider]
        
        # Prepare enhanced request
        enhanced_request = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream,
            "system_prompt": request.system_prompt,
            "tools": request.tools,
            "user_preferences": request.user_preferences
        }
        
        # Execute chat request
        if request.stream:
            # Return streaming response
            response = await provider.stream_chat(**enhanced_request)
            return {
                "status": "streaming",
                "stream_id": response.stream_id,
                "provider": request.provider,
                "model": request.model
            }
        else:
            # Return complete response
            response = await provider.chat(**enhanced_request)
            
            return {
                "status": "success",
                "response": {
                    "content": response.content,
                    "role": response.role,
                    "finish_reason": response.finish_reason,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                        "cost": response.usage.estimated_cost
                    }
                },
                "provider_info": {
                    "provider": request.provider,
                    "model": request.model,
                    "response_time": response.response_time,
                    "quality_score": response.quality_score
                },
                "metadata": response.metadata
            }
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat request failed: {str(e)}"
        )

@router.post("/multimodal/process")
async def multimodal_processing(
    request: MultiModalRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Process multimodal inputs (text, image, audio, video)
    """
    try:
        # Verify provider supports multimodal
        if request.provider not in providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' not available"
            )
        
        provider = providers[request.provider]
        
        # Check multimodal capability
        if not hasattr(provider, 'multimodal_process'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' doesn't support multimodal processing"
            )
        
        # Process multimodal request
        response = await provider.multimodal_process(
            model=request.model,
            text_input=request.text_input,
            image_inputs=request.image_inputs,
            audio_input=request.audio_input,
            video_input=request.video_input,
            task_type=request.task_type
        )
        
        return {
            "status": "success",
            "response": {
                "content": response.content,
                "analysis": response.analysis,
                "generated_content": response.generated_content,
                "confidence_scores": response.confidence_scores
            },
            "processing_info": {
                "provider": request.provider,
                "model": request.model,
                "task_type": request.task_type,
                "processing_time": response.processing_time,
                "input_types": response.processed_input_types
            },
            "usage": {
                "tokens_used": response.usage.tokens_used,
                "cost": response.usage.estimated_cost
            }
        }
        
    except Exception as e:
        logger.error(f"Multimodal processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multimodal processing failed: {str(e)}"
        )

@router.post("/compare/models")
async def compare_models(
    request: ModelComparisonRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Compare multiple models across different providers
    """
    try:
        comparison_results = []
        
        for provider_name in request.providers:
            if provider_name not in providers:
                continue
            
            provider = providers[provider_name]
            model = request.models.get(provider_name) if request.models else provider.default_model
            
            try:
                # Test the model with the prompt
                response = await provider.chat(
                    model=model,
                    messages=[{"role": "user", "content": request.prompt}],
                    temperature=0.7
                )
                
                # Evaluate based on criteria
                evaluation = await provider.evaluate_response(
                    response=response,
                    criteria=request.criteria
                )
                
                comparison_results.append({
                    "provider": provider_name,
                    "model": model,
                    "response": response.content,
                    "evaluation": {
                        "overall_score": evaluation.overall_score,
                        "criteria_scores": evaluation.criteria_scores,
                        "strengths": evaluation.strengths,
                        "weaknesses": evaluation.weaknesses
                    },
                    "performance": {
                        "response_time": response.response_time,
                        "tokens_used": response.usage.total_tokens,
                        "cost": response.usage.estimated_cost
                    }
                })
                
            except Exception as provider_error:
                comparison_results.append({
                    "provider": provider_name,
                    "model": model,
                    "error": str(provider_error),
                    "status": "failed"
                })
        
        # Generate comparison summary
        summary = {
            "best_overall": max(
                [r for r in comparison_results if "evaluation" in r],
                key=lambda x: x["evaluation"]["overall_score"],
                default=None
            ),
            "fastest": min(
                [r for r in comparison_results if "performance" in r],
                key=lambda x: x["performance"]["response_time"],
                default=None
            ),
            "most_cost_effective": min(
                [r for r in comparison_results if "performance" in r],
                key=lambda x: x["performance"]["cost"],
                default=None
            )
        }
        
        return {
            "status": "success",
            "comparison_results": comparison_results,
            "summary": summary,
            "test_prompt": request.prompt,
            "criteria": request.criteria,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model comparison error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model comparison failed: {str(e)}"
        )

@router.post("/provider/configure")
async def configure_provider(
    request: ProviderConfigRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Configure a specific LLM provider with custom settings
    """
    try:
        if request.provider not in providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' not available"
            )
        
        provider = providers[request.provider]
        
        # Apply configuration
        config_result = await provider.configure(
            config=request.config,
            api_key=request.api_key,
            endpoint=request.endpoint
        )
        
        # Test configuration
        test_result = await provider.test_configuration()
        
        return {
            "status": "success",
            "provider": request.provider,
            "configuration": {
                "applied": config_result.applied_settings,
                "status": config_result.status,
                "warnings": config_result.warnings
            },
            "test_result": {
                "connection_status": test_result.connection_status,
                "available_models": test_result.available_models,
                "rate_limits": test_result.rate_limits,
                "features": test_result.supported_features
            }
        }
        
    except Exception as e:
        logger.error(f"Provider configuration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provider configuration failed: {str(e)}"
        )

@router.get("/providers/available")
async def get_available_providers(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get list of available LLM providers and their capabilities
    """
    try:
        provider_info = []
        
        for provider_name, provider in providers.items():
            try:
                # Get provider capabilities
                capabilities = await provider.get_capabilities()
                status_info = await provider.get_status()
                
                provider_info.append({
                    "name": provider_name,
                    "display_name": provider.display_name,
                    "description": provider.description,
                    "status": status_info.status,
                    "capabilities": {
                        "chat": capabilities.supports_chat,
                        "completion": capabilities.supports_completion,
                        "embeddings": capabilities.supports_embeddings,
                        "multimodal": capabilities.supports_multimodal,
                        "function_calling": capabilities.supports_function_calling,
                        "streaming": capabilities.supports_streaming
                    },
                    "models": capabilities.available_models,
                    "rate_limits": status_info.rate_limits,
                    "pricing": capabilities.pricing_info,
                    "last_updated": status_info.last_updated
                })
                
            except Exception as provider_error:
                provider_info.append({
                    "name": provider_name,
                    "status": "error",
                    "error": str(provider_error)
                })
        
        return {
            "status": "success",
            "providers": provider_info,
            "total_providers": len(provider_info),
            "active_providers": len([p for p in provider_info if p.get("status") == "active"])
        }
        
    except Exception as e:
        logger.error(f"Get providers error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provider information: {str(e)}"
        )

@router.get("/usage/analytics")
async def get_usage_analytics(
    provider: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get usage analytics for LLM providers
    """
    try:
        analytics_data = {}
        
        target_providers = [provider] if provider else list(providers.keys())
        
        for provider_name in target_providers:
            if provider_name not in providers:
                continue
            
            provider_instance = providers[provider_name]
            
            # Get usage analytics
            analytics = await provider_instance.get_usage_analytics(
                start_date=start_date,
                end_date=end_date
            )
            
            analytics_data[provider_name] = {
                "total_requests": analytics.total_requests,
                "total_tokens": analytics.total_tokens,
                "total_cost": analytics.total_cost,
                "average_response_time": analytics.average_response_time,
                "success_rate": analytics.success_rate,
                "most_used_models": analytics.most_used_models,
                "daily_breakdown": analytics.daily_breakdown,
                "error_summary": analytics.error_summary
            }
        
        # Generate summary
        summary = {
            "total_requests": sum(data["total_requests"] for data in analytics_data.values()),
            "total_cost": sum(data["total_cost"] for data in analytics_data.values()),
            "average_success_rate": sum(data["success_rate"] for data in analytics_data.values()) / len(analytics_data) if analytics_data else 0
        }
        
        return {
            "status": "success",
            "analytics": analytics_data,
            "summary": summary,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
        
    except Exception as e:
        logger.error(f"Usage analytics error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage analytics: {str(e)}"
        )

@router.get("/system/health")
async def llm_system_health(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get health status of enhanced LLM provider system
    """
    try:
        health_data = {}
        overall_health = "healthy"
        
        for provider_name, provider in providers.items():
            try:
                health = await provider.get_health_status()
                health_data[provider_name] = {
                    "status": health.status,
                    "response_time": health.response_time,
                    "error_rate": health.error_rate,
                    "rate_limit_status": health.rate_limit_status,
                    "last_check": health.last_check
                }
                
                if health.status != "healthy":
                    overall_health = "degraded"
                    
            except Exception as provider_error:
                health_data[provider_name] = {
                    "status": "error",
                    "error": str(provider_error)
                }
                overall_health = "degraded"
        
        return {
            "status": "success",
            "overall_health": overall_health,
            "providers": health_data,
            "system_info": {
                "total_providers": len(providers),
                "healthy_providers": len([h for h in health_data.values() if h.get("status") == "healthy"]),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"LLM system health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )

