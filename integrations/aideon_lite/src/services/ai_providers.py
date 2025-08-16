"""
AI Provider Integration System for Aideon Lite AI
Comprehensive multi-provider AI system with hybrid processing and cost optimization.
"""

import os
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProviderType(Enum):
    """AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"

class ProcessingMode(Enum):
    """Processing mode types"""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    HYBRID = "hybrid"

@dataclass
class ProviderConfig:
    """Provider configuration"""
    name: str
    type: ProviderType
    api_key: str
    models: List[str]
    cost_per_token: float
    max_tokens: int
    rate_limit: int
    priority: int
    enabled: bool = True

@dataclass
class AIRequest:
    """AI request structure"""
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    stream: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class AIResponse:
    """AI response structure"""
    content: str
    provider: str
    model: str
    tokens_used: int
    cost: float
    processing_time: float
    processing_mode: ProcessingMode
    timestamp: datetime
    success: bool
    error: Optional[str] = None

class LocalProvider:
    """Local AI provider for privacy-sensitive content"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.models = config.models
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using local processing"""
        start_time = time.time()
        
        # Simulate local processing
        content = f"Local AI response to: {request.prompt[:50]}... [This is a simulated local response for privacy-sensitive content]"
        
        return AIResponse(
            content=content,
            provider="local",
            model="local-llm",
            tokens_used=len(content.split()),
            cost=0.0,
            processing_time=time.time() - start_time,
            processing_mode=ProcessingMode.LOCAL_ONLY,
            timestamp=datetime.now(),
            success=True
        )

class OpenAIProvider:
    """OpenAI provider implementation"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.models = config.models
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using OpenAI"""
        start_time = time.time()
        
        # Simulate OpenAI API call
        content = f"OpenAI response to: {request.prompt[:50]}... [Simulated response - requires API key]"
        
        return AIResponse(
            content=content,
            provider="openai",
            model=request.model or "gpt-3.5-turbo",
            tokens_used=len(content.split()),
            cost=len(content.split()) * self.config.cost_per_token,
            processing_time=time.time() - start_time,
            processing_mode=ProcessingMode.CLOUD_ONLY,
            timestamp=datetime.now(),
            success=True
        )

class AnthropicProvider:
    """Anthropic provider implementation"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.models = config.models
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using Anthropic"""
        start_time = time.time()
        
        # Simulate Anthropic API call
        content = f"Anthropic Claude response to: {request.prompt[:50]}... [Simulated response - requires API key]"
        
        return AIResponse(
            content=content,
            provider="anthropic",
            model=request.model or "claude-3-haiku-20240307",
            tokens_used=len(content.split()),
            cost=len(content.split()) * self.config.cost_per_token,
            processing_time=time.time() - start_time,
            processing_mode=ProcessingMode.CLOUD_ONLY,
            timestamp=datetime.now(),
            success=True
        )

class GoogleProvider:
    """Google provider implementation"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.models = config.models
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using Google"""
        start_time = time.time()
        
        # Simulate Google API call
        content = f"Google Gemini response to: {request.prompt[:50]}... [Simulated response - requires API key]"
        
        return AIResponse(
            content=content,
            provider="google",
            model=request.model or "gemini-pro",
            tokens_used=len(content.split()),
            cost=len(content.split()) * self.config.cost_per_token,
            processing_time=time.time() - start_time,
            processing_mode=ProcessingMode.CLOUD_ONLY,
            timestamp=datetime.now(),
            success=True
        )

class TogetherAIProviderWrapper:
    """Wrapper for Together AI provider to integrate with main system"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.models = config.models
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using Together AI"""
        start_time = time.time()
        
        # Simulate Together AI API call
        content = f"Together AI (Llama/Mixtral) response to: {request.prompt[:50]}... [Open-source model response - cost-effective]"
        
        return AIResponse(
            content=content,
            provider="together",
            model=request.model or "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            tokens_used=len(content.split()),
            cost=len(content.split()) * self.config.cost_per_token,
            processing_time=time.time() - start_time,
            processing_mode=ProcessingMode.CLOUD_ONLY,
            timestamp=datetime.now(),
            success=True
        )

class HuggingFaceProviderWrapper:
    """Wrapper for Hugging Face provider to integrate with main system"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.models = config.models
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using Hugging Face"""
        start_time = time.time()
        
        # Simulate Hugging Face API call
        content = f"Hugging Face (Zephyr/DialoGPT) response to: {request.prompt[:50]}... [Free open-source model response]"
        
        return AIResponse(
            content=content,
            provider="huggingface",
            model=request.model or "HuggingFaceH4/zephyr-7b-beta",
            tokens_used=len(content.split()),
            cost=0.0,  # Free tier
            processing_time=time.time() - start_time,
            processing_mode=ProcessingMode.LOCAL_ONLY,
            timestamp=datetime.now(),
            success=True
        )

class HybridProcessor:
    """Hybrid processing decision engine"""
    
    def should_process_locally(self, request: AIRequest) -> bool:
        """Determine if request should be processed locally"""
        
        # Privacy-sensitive keywords
        privacy_keywords = ["password", "ssn", "credit card", "personal", "private", "confidential"]
        
        # Check for privacy-sensitive content
        if any(keyword in request.prompt.lower() for keyword in privacy_keywords):
            return True
        
        # Check for simple requests that can be handled locally
        simple_keywords = ["hello", "hi", "test", "simple"]
        if any(keyword in request.prompt.lower() for keyword in simple_keywords):
            return True
        
        return False

class ProviderMetrics:
    """Provider performance metrics tracking"""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, List[float]]] = {}
    
    def record_response(self, provider: str, response_time: float, cost: float, success: bool):
        """Record provider response metrics"""
        if provider not in self.metrics:
            self.metrics[provider] = {
                "response_times": [],
                "costs": [],
                "successes": []
            }
        
        self.metrics[provider]["response_times"].append(response_time)
        self.metrics[provider]["costs"].append(cost)
        self.metrics[provider]["successes"].append(1.0 if success else 0.0)
    
    def get_avg_response_time(self, provider: str) -> float:
        """Get average response time for provider"""
        if provider not in self.metrics or not self.metrics[provider]["response_times"]:
            return 0.0
        return sum(self.metrics[provider]["response_times"]) / len(self.metrics[provider]["response_times"])
    
    def get_success_rate(self, provider: str) -> float:
        """Get success rate for provider"""
        if provider not in self.metrics or not self.metrics[provider]["successes"]:
            return 1.0
        return sum(self.metrics[provider]["successes"]) / len(self.metrics[provider]["successes"])
    
    def get_avg_cost(self, provider: str) -> float:
        """Get average cost for provider"""
        if provider not in self.metrics or not self.metrics[provider]["costs"]:
            return 0.0
        return sum(self.metrics[provider]["costs"]) / len(self.metrics[provider]["costs"])

class ProviderRouter:
    """Intelligent provider routing system"""
    
    def __init__(self, providers: Dict[str, Any], metrics: ProviderMetrics):
        self.providers = providers
        self.metrics = metrics
        self.hybrid_processor = HybridProcessor()
    
    def select_provider(self, request: AIRequest) -> str:
        """Select optimal provider based on request characteristics"""
        
        # Check if local processing is preferred
        if self.hybrid_processor.should_process_locally(request):
            if "local" in self.providers:
                return "local"
        
        # Filter available providers
        available_providers = [name for name, provider in self.providers.items() 
                             if provider.config.enabled and name != "local"]
        
        if not available_providers:
            return "local" if "local" in self.providers else None
        
        # Prioritize cost-effective open-source providers for general tasks
        cost_effective_providers = ["huggingface", "together"]
        premium_providers = ["openai", "anthropic", "google"]
        
        # Check for code-related requests that benefit from specialized models
        code_keywords = ["code", "programming", "function", "class", "import", "def", "var", "const"]
        is_code_request = any(keyword in request.prompt.lower() for keyword in code_keywords)
        
        # Check for complex reasoning tasks that benefit from premium models
        complex_keywords = ["analyze", "reasoning", "complex", "detailed analysis", "comprehensive"]
        is_complex_request = any(keyword in request.prompt.lower() for keyword in complex_keywords)
        
        # Routing logic based on request type and provider availability
        if is_code_request and "together" in available_providers:
            # Together AI has excellent code models (CodeLlama, WizardCoder)
            return "together"
        
        if not is_complex_request:
            # For general tasks, prefer cost-effective providers
            for provider in cost_effective_providers:
                if provider in available_providers:
                    return provider
        
        # Score providers based on performance metrics for complex tasks
        provider_scores = {}
        
        for provider_name in available_providers:
            score = 0.0
            
            # Cost efficiency score (higher weight for cost-effective providers)
            if provider_name in cost_effective_providers:
                score += 0.5  # Bonus for cost-effective providers
            
            # Response time score (lower is better)
            avg_response_time = self.metrics.get_avg_response_time(provider_name)
            if avg_response_time > 0:
                score += (1.0 / avg_response_time) * 0.2
            
            # Success rate score
            success_rate = self.metrics.get_success_rate(provider_name)
            score += success_rate * 0.2
            
            # Cost score (lower cost is better)
            avg_cost = self.metrics.get_avg_cost(provider_name)
            if avg_cost > 0:
                score += (1.0 / (avg_cost * 1000)) * 0.1  # Normalize cost impact
            
            provider_scores[provider_name] = score
        
        # Select provider with highest score
        if provider_scores:
            return max(provider_scores, key=provider_scores.get)
        
        # Fallback to first available provider
        return available_providers[0] if available_providers else "local"

class AIProviderManager:
    """Main AI provider management system"""
    
    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.metrics = ProviderMetrics()
        self.router = ProviderRouter(self.providers, self.metrics)
        self.request_history: List[AIResponse] = []
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all AI providers"""
        
        # OpenAI configuration
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            openai_config = ProviderConfig(
                name="OpenAI",
                type=ProviderType.OPENAI,
                api_key=openai_key,
                models=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"],
                cost_per_token=0.00003,  # Approximate cost
                max_tokens=4096,
                rate_limit=60,
                priority=1
            )
            self.providers["openai"] = OpenAIProvider(openai_config)
        
        # Anthropic configuration
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            anthropic_config = ProviderConfig(
                name="Anthropic",
                type=ProviderType.ANTHROPIC,
                api_key=anthropic_key,
                models=["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-5-sonnet-20241022"],
                cost_per_token=0.00003,
                max_tokens=4096,
                rate_limit=60,
                priority=2
            )
            self.providers["anthropic"] = AnthropicProvider(anthropic_config)
        
        # Google configuration
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            google_config = ProviderConfig(
                name="Google",
                type=ProviderType.GOOGLE,
                api_key=google_key,
                models=["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"],
                cost_per_token=0.00002,
                max_tokens=4096,
                rate_limit=60,
                priority=3
            )
            self.providers["google"] = GoogleProvider(google_config)
        
        # Together AI configuration (Open Source)
        together_key = os.getenv('TOGETHER_API_KEY')
        if together_key:
            together_config = ProviderConfig(
                name="Together AI",
                type=ProviderType.OPENAI,  # Uses OpenAI-compatible API
                api_key=together_key,
                models=["meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
                cost_per_token=0.0000002,  # Much cheaper than proprietary
                max_tokens=4096,
                rate_limit=100,
                priority=4
            )
            self.providers["together"] = TogetherAIProviderWrapper(together_config)
        
        # Hugging Face configuration (Open Source)
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        if hf_key:
            hf_config = ProviderConfig(
                name="Hugging Face",
                type=ProviderType.LOCAL,  # Treated as local/open-source
                api_key=hf_key,
                models=["HuggingFaceH4/zephyr-7b-beta", "microsoft/DialoGPT-large", "bigcode/starcoder"],
                cost_per_token=0.0,  # Free tier
                max_tokens=2048,
                rate_limit=1000,
                priority=5
            )
            self.providers["huggingface"] = HuggingFaceProviderWrapper(hf_config)
        
        # Local provider (always available)
        local_config = ProviderConfig(
            name="Local",
            type=ProviderType.LOCAL,
            api_key="",
            models=["local-llm"],
            cost_per_token=0.0,
            max_tokens=4096,
            rate_limit=1000,
            priority=6
        )
        self.providers["local"] = LocalProvider(local_config)
        
        # Update router with providers
        self.router = ProviderRouter(self.providers, self.metrics)
        
        logger.info(f"Initialized {len(self.providers)} AI providers: {list(self.providers.keys())}")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate AI response using optimal provider"""
        
        # Select provider
        provider_name = self.router.select_provider(request)
        
        if not provider_name or provider_name not in self.providers:
            return AIResponse(
                content="No available AI providers",
                provider="none",
                model="none",
                tokens_used=0,
                cost=0.0,
                processing_time=0.0,
                processing_mode=ProcessingMode.LOCAL_ONLY,
                timestamp=datetime.now(),
                success=False,
                error="No available providers"
            )
        
        # Generate response
        provider = self.providers[provider_name]
        response = await provider.generate(request)
        
        # Record metrics
        self.metrics.record_response(
            provider_name,
            response.processing_time,
            response.cost,
            response.success
        )
        
        # Store in history
        self.request_history.append(response)
        if len(self.request_history) > 1000:
            self.request_history.pop(0)
        
        logger.info(f"Generated response using {provider_name}: {response.success}")
        
        return response
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = {
                "enabled": provider.config.enabled,
                "models": provider.models,
                "avg_response_time": self.metrics.get_avg_response_time(name),
                "success_rate": self.metrics.get_success_rate(name),
                "avg_cost": self.metrics.get_avg_cost(name)
            }
        
        return status
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        total_requests = len(self.request_history)
        successful_requests = sum(1 for r in self.request_history if r.success)
        
        if total_requests == 0:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "total_cost": 0.0,
                "cost_savings": 0.0
            }
        
        avg_response_time = sum(r.processing_time for r in self.request_history) / total_requests
        total_cost = sum(r.cost for r in self.request_history)
        
        # Calculate cost savings from using open-source providers
        open_source_requests = sum(1 for r in self.request_history if r.provider in ["huggingface", "together", "local"])
        cost_savings = (open_source_requests / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "success_rate": successful_requests / total_requests,
            "avg_response_time": avg_response_time,
            "total_cost": total_cost,
            "cost_savings": cost_savings,
            "provider_distribution": self._get_provider_distribution()
        }
    
    def _get_provider_distribution(self) -> Dict[str, int]:
        """Get distribution of requests across providers"""
        distribution = {}
        for response in self.request_history:
            provider = response.provider
            distribution[provider] = distribution.get(provider, 0) + 1
        return distribution

# Global AI provider manager instance
ai_manager = AIProviderManager()

# Convenience functions for API integration
async def generate_ai_response(prompt: str, model: str = None, **kwargs) -> AIResponse:
    """Generate AI response with automatic provider selection"""
    request = AIRequest(
        prompt=prompt,
        model=model,
        **kwargs
    )
    return await ai_manager.generate_response(request)

def get_ai_providers_status() -> Dict[str, Any]:
    """Get status of all AI providers"""
    return ai_manager.get_provider_status()

def get_ai_performance_metrics() -> Dict[str, Any]:
    """Get AI system performance metrics"""
    return ai_manager.get_performance_metrics()

