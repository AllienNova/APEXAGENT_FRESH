"""
Open Source AI Provider Integration for Aideon Lite AI
Implements Together AI and Hugging Face integrations for cost-effective open-source models.
"""

import os
import time
import json
import asyncio
import logging
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OpenSourceRequest:
    """Open source AI request structure"""
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    stream: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class OpenSourceResponse:
    """Open source AI response structure"""
    content: str
    provider: str
    model: str
    tokens_used: int
    cost: float
    processing_time: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None

class TogetherAIProvider:
    """Together AI provider for open-source models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.together.xyz/v1"
        self.models = [
            # Meta Llama models
            "meta-llama/Llama-2-7b-chat-hf",
            "meta-llama/Llama-2-13b-chat-hf",
            "meta-llama/Llama-2-70b-chat-hf",
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "meta-llama/Meta-Llama-3-70B-Instruct",
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            
            # Mistral models
            "mistralai/Mistral-7B-Instruct-v0.1",
            "mistralai/Mistral-7B-Instruct-v0.2",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "mistralai/Mixtral-8x22B-Instruct-v0.1",
            
            # Code models
            "codellama/CodeLlama-7b-Instruct-hf",
            "codellama/CodeLlama-13b-Instruct-hf",
            "codellama/CodeLlama-34b-Instruct-hf",
            "WizardLM/WizardCoder-Python-34B-V1.0",
            
            # Other popular open-source models
            "togethercomputer/RedPajama-INCITE-Chat-3B-v1",
            "togethercomputer/RedPajama-INCITE-7B-Chat",
            "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
            "NousResearch/Nous-Hermes-2-Yi-34B",
            "teknium/OpenHermes-2.5-Mistral-7B",
            "Qwen/Qwen1.5-7B-Chat",
            "Qwen/Qwen1.5-14B-Chat",
            "Qwen/Qwen1.5-72B-Chat"
        ]
        
        # Cost per token (approximate, much cheaper than proprietary models)
        self.cost_per_token = 0.0000002  # $0.0002 per 1K tokens
    
    async def generate(self, request: OpenSourceRequest) -> OpenSourceResponse:
        """Generate response using Together AI"""
        start_time = time.time()
        
        try:
            model = request.model or "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
            if model not in self.models:
                model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens or 2048,
                "temperature": request.temperature,
                "stream": request.stream
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", len(content.split()))
                cost = tokens_used * self.cost_per_token
                processing_time = time.time() - start_time
                
                return OpenSourceResponse(
                    content=content,
                    provider="together",
                    model=model,
                    tokens_used=tokens_used,
                    cost=cost,
                    processing_time=processing_time,
                    timestamp=datetime.now(),
                    success=True
                )
            else:
                error_msg = f"Together AI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return OpenSourceResponse(
                    content="",
                    provider="together",
                    model=model,
                    tokens_used=0,
                    cost=0.0,
                    processing_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    success=False,
                    error=error_msg
                )
                
        except Exception as e:
            logger.error(f"Together AI provider error: {str(e)}")
            return OpenSourceResponse(
                content="",
                provider="together",
                model=request.model or "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                tokens_used=0,
                cost=0.0,
                processing_time=time.time() - start_time,
                timestamp=datetime.now(),
                success=False,
                error=str(e)
            )

class HuggingFaceProvider:
    """Hugging Face Inference API provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.models = [
            # Text generation models
            "microsoft/DialoGPT-large",
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill",
            "facebook/blenderbot-1B-distill",
            "facebook/blenderbot-3B",
            
            # Instruction-following models
            "HuggingFaceH4/zephyr-7b-beta",
            "HuggingFaceH4/zephyr-7b-alpha",
            "microsoft/DialoGPT-small",
            
            # Code generation models
            "Salesforce/codegen-350M-mono",
            "Salesforce/codegen-2B-mono",
            "Salesforce/codegen-6B-mono",
            "bigcode/starcoder",
            "bigcode/starcoderbase",
            
            # Smaller efficient models
            "distilgpt2",
            "gpt2",
            "gpt2-medium",
            "gpt2-large",
            "gpt2-xl",
            
            # Specialized models
            "EleutherAI/gpt-neo-1.3B",
            "EleutherAI/gpt-neo-2.7B",
            "EleutherAI/gpt-j-6b",
            "EleutherAI/gpt-neox-20b"
        ]
        
        # Cost per token (Hugging Face Inference API is free for limited usage)
        self.cost_per_token = 0.0  # Free tier
    
    async def generate(self, request: OpenSourceRequest) -> OpenSourceResponse:
        """Generate response using Hugging Face Inference API"""
        start_time = time.time()
        
        try:
            model = request.model or "HuggingFaceH4/zephyr-7b-beta"
            if model not in self.models:
                model = "HuggingFaceH4/zephyr-7b-beta"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Format prompt for instruction-following models
            if "zephyr" in model.lower() or "instruct" in model.lower():
                formatted_prompt = f"<|system|>\nYou are a helpful AI assistant.</s>\n<|user|>\n{request.prompt}</s>\n<|assistant|>\n"
            else:
                formatted_prompt = request.prompt
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": request.max_tokens or 512,
                    "temperature": request.temperature,
                    "return_full_text": False,
                    "do_sample": True
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{model}",
                headers=headers,
                json=payload,
                timeout=60  # Longer timeout for model loading
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list) and len(data) > 0:
                    content = data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    content = data.get("generated_text", "")
                else:
                    content = str(data)
                
                # Clean up the response
                content = content.strip()
                if not content:
                    content = "I apologize, but I couldn't generate a proper response. Please try again."
                
                tokens_used = len(content.split())
                cost = tokens_used * self.cost_per_token
                processing_time = time.time() - start_time
                
                return OpenSourceResponse(
                    content=content,
                    provider="huggingface",
                    model=model,
                    tokens_used=tokens_used,
                    cost=cost,
                    processing_time=processing_time,
                    timestamp=datetime.now(),
                    success=True
                )
            else:
                error_msg = f"Hugging Face API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return OpenSourceResponse(
                    content="",
                    provider="huggingface",
                    model=model,
                    tokens_used=0,
                    cost=0.0,
                    processing_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    success=False,
                    error=error_msg
                )
                
        except Exception as e:
            logger.error(f"Hugging Face provider error: {str(e)}")
            return OpenSourceResponse(
                content="",
                provider="huggingface",
                model=request.model or "HuggingFaceH4/zephyr-7b-beta",
                tokens_used=0,
                cost=0.0,
                processing_time=time.time() - start_time,
                timestamp=datetime.now(),
                success=False,
                error=str(e)
            )

class OpenSourceProviderManager:
    """Manager for open-source AI providers"""
    
    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.request_history: List[OpenSourceResponse] = []
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize open-source AI providers"""
        
        # Together AI configuration
        together_key = os.getenv('TOGETHER_API_KEY')
        if together_key:
            self.providers["together"] = TogetherAIProvider(together_key)
            logger.info("Together AI provider initialized")
        
        # Hugging Face configuration
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        if hf_key:
            self.providers["huggingface"] = HuggingFaceProvider(hf_key)
            logger.info("Hugging Face provider initialized")
        
        logger.info(f"Initialized {len(self.providers)} open-source providers: {list(self.providers.keys())}")
    
    async def generate_response(self, request: OpenSourceRequest, provider: str = None) -> OpenSourceResponse:
        """Generate response using specified or optimal open-source provider"""
        
        # Select provider
        if provider and provider in self.providers:
            selected_provider = provider
        elif self.providers:
            # Default to Together AI if available, otherwise first available
            selected_provider = "together" if "together" in self.providers else list(self.providers.keys())[0]
        else:
            return OpenSourceResponse(
                content="No open-source AI providers available",
                provider="none",
                model="none",
                tokens_used=0,
                cost=0.0,
                processing_time=0.0,
                timestamp=datetime.now(),
                success=False,
                error="No available providers"
            )
        
        # Generate response
        provider_instance = self.providers[selected_provider]
        response = await provider_instance.generate(request)
        
        # Store in history
        self.request_history.append(response)
        if len(self.request_history) > 1000:
            self.request_history.pop(0)
        
        logger.info(f"Generated response using {selected_provider}: {response.success}")
        
        return response
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all open-source providers"""
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = {
                "enabled": True,
                "models": provider.models[:10],  # Show first 10 models
                "total_models": len(provider.models),
                "cost_per_token": provider.cost_per_token
            }
        
        return status
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models from all providers"""
        models = {}
        
        for name, provider in self.providers.items():
            models[name] = provider.models
        
        return models
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for open-source providers"""
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
        
        # Calculate cost savings compared to proprietary models
        # Assuming proprietary models cost ~$0.03 per 1K tokens
        proprietary_cost = sum(r.tokens_used for r in self.request_history) * 0.00003
        cost_savings = ((proprietary_cost - total_cost) / proprietary_cost * 100) if proprietary_cost > 0 else 0
        
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

# Global open-source provider manager instance
open_source_manager = OpenSourceProviderManager()

# Convenience functions for API integration
async def generate_open_source_response(prompt: str, model: str = None, provider: str = None, **kwargs) -> OpenSourceResponse:
    """Generate response using open-source providers"""
    request = OpenSourceRequest(
        prompt=prompt,
        model=model,
        **kwargs
    )
    return await open_source_manager.generate_response(request, provider)

def get_open_source_providers_status() -> Dict[str, Any]:
    """Get status of all open-source providers"""
    return open_source_manager.get_provider_status()

def get_open_source_models() -> Dict[str, List[str]]:
    """Get all available open-source models"""
    return open_source_manager.get_available_models()

def get_open_source_metrics() -> Dict[str, Any]:
    """Get open-source provider performance metrics"""
    return open_source_manager.get_performance_metrics()

