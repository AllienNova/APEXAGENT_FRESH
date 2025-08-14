# src/plugins/llm_providers/internal/together_ai_provider.py
from typing import List, Dict, Any, Optional, Union
import os
import json
import logging
import httpx
import asyncio
from src.plugins.llm_providers.base_provider import LLMProvider, ModelInfo, LLMOptions

logger = logging.getLogger(__name__)

class TogetherAIProvider(LLMProvider):
    """
    Provider implementation for Together AI platform.
    
    This provider enables access to 100+ open-source models through Together AI's
    unified API, supporting both text and multimodal capabilities.
    """
    
    PROVIDER_NAME = "together_ai"
    DISPLAY_NAME = "Together AI"
    API_KEY_NAME = "TOGETHER_API_KEY"
    API_BASE_URL = "https://api.together.xyz/v1"
    
    # Model tiers for free and premium access
    MODEL_TIERS = {
        "free": {
            "text": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "text_fallback": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "code": "Nexusflow/NexusRaven-V2-13B",
            "code_fallback": "codellama/CodeLlama-13b-Instruct-hf",
            "vision": "deepseek-ai/DeepSeek-VL-7B-Chat",
            "image": "stabilityai/stable-diffusion-xl-base-1.0",
            "image_fallback": "runwayml/stable-diffusion-v1-5",
            "audio_tts": "cartesia/sonic",
            "audio_stt": "whisper-medium"
        },
        "premium": {
            "text": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "text_critical": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            "code": "deepseek-ai/deepseek-coder-33b-instruct",
            "code_complex": "codellama/CodeLlama-70b-Instruct-hf",
            "vision": "Qwen/Qwen-VL-Chat",
            "vision_specialized": "Snowflake/snowflake-arctic-instruct",
            "image_fast": "stabilityai/sdxl-turbo",
            "image_quality": "playgroundai/playground-v2.5",
            "audio_tts": "cartesia/sonic",
            "audio_stt": "whisper-large-v3"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        """
        Initialize the Together AI provider.
        
        Args:
            api_key: Together AI API key. If None, will attempt to load from environment.
            api_base_url: Optional custom API base URL. Defaults to standard Together AI endpoint.
        """
        # Use provided API key or try to get from environment
        if api_key is None:
            api_key = os.environ.get(self.API_KEY_NAME)
        
        # Use provided base URL or default
        if api_base_url is None:
            api_base_url = self.API_BASE_URL
            
        super().__init__(api_key=api_key, api_base_url=api_base_url)
        
        # Initialize HTTP client for API calls
        self.client = httpx.AsyncClient(
            base_url=self.api_base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0  # Longer timeout for large model inference
        )
        
        logger.info(f"TogetherAIProvider initialized. API Key provided: {bool(self.api_key)}, Base URL: {self.api_base_url}")

    @classmethod
    def get_static_provider_name(cls) -> str:
        """Returns the machine-readable provider name."""
        return cls.PROVIDER_NAME

    @classmethod
    def get_static_provider_display_name(cls) -> str:
        """Returns the user-friendly provider display name."""
        return cls.DISPLAY_NAME

    @classmethod
    def get_required_api_key_name(cls) -> Optional[str]:
        """Returns the environment variable name for the API key."""
        return cls.API_KEY_NAME
    
    def get_model_for_tier(self, modality: str, tier: str = "premium", purpose: Optional[str] = None) -> str:
        """
        Get the appropriate model ID for the specified modality and tier.
        
        Args:
            modality: The modality type (text, code, vision, image, audio_tts, audio_stt)
            tier: The tier level (free, premium)
            purpose: Optional specific purpose (e.g., "critical", "fallback", "complex")
            
        Returns:
            Model ID string for the specified parameters
        """
        tier_models = self.MODEL_TIERS.get(tier, self.MODEL_TIERS["free"])
        
        if purpose:
            model_key = f"{modality}_{purpose}"
            if model_key in tier_models:
                return tier_models[model_key]
        
        # Return the base model for the modality if available, otherwise fallback
        if modality in tier_models:
            return tier_models[modality]
        
        # If modality not found, return a reasonable default
        if modality.startswith("audio"):
            return tier_models.get("audio_tts", "cartesia/sonic")
        
        # Default to text model as final fallback
        return tier_models.get("text", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

    async def get_available_models(self) -> List[ModelInfo]:
        """
        Returns a list of available models from Together AI.
        
        Makes an API call to fetch the current list of supported models.
        """
        if not self.api_key:
            logger.warning("API key not configured for TogetherAIProvider.")
            return []
        
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            
            models_data = response.json().get("data", [])
            result = []
            
            for model in models_data:
                # Extract relevant model information
                model_info = ModelInfo(
                    id=model.get("id", ""),
                    name=model.get("name", model.get("id", "")),
                    description=model.get("description", ""),
                    context_window=model.get("context_length", None)
                )
                result.append(model_info)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Together AI models: {str(e)}")
            
            # Return a predefined list of our selected models as fallback
            return [
                # Text models
                ModelInfo(id="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", name="Llama 3.1 405B Instruct", 
                         description="Meta's largest and most capable model for critical tasks", context_window=4096),
                ModelInfo(id="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", name="Llama 3.1 70B Instruct", 
                         description="Powerful general-purpose model with strong reasoning", context_window=8192),
                ModelInfo(id="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", name="Llama 3.1 8B Instruct", 
                         description="Efficient model for general text tasks", context_window=8192),
                ModelInfo(id="mistralai/Mixtral-8x7B-Instruct-v0.1", name="Mixtral 8x7B Instruct", 
                         description="Efficient MoE architecture with long context window", context_window=32768),
                
                # Code models
                ModelInfo(id="codellama/CodeLlama-70b-Instruct-hf", name="CodeLlama 70B", 
                         description="Large model specialized for complex coding tasks", context_window=4096),
                ModelInfo(id="deepseek-ai/deepseek-coder-33b-instruct", name="DeepSeek Coder 33B", 
                         description="Specialized code model with long context window", context_window=16384),
                ModelInfo(id="Nexusflow/NexusRaven-V2-13B", name="NexusRaven V2 13B", 
                         description="Purpose-built for efficient code generation", context_window=16384),
                ModelInfo(id="codellama/CodeLlama-13b-Instruct-hf", name="CodeLlama 13B", 
                         description="Efficient code model with good context length", context_window=16384),
                
                # Vision models
                ModelInfo(id="Qwen/Qwen-VL-Chat", name="Qwen VL Chat", 
                         description="Strong multimodal vision-language model", context_window=8192),
                ModelInfo(id="deepseek-ai/DeepSeek-VL-7B-Chat", name="DeepSeek VL 7B Chat", 
                         description="Efficient vision-language model for basic image understanding", context_window=4096),
                ModelInfo(id="Snowflake/snowflake-arctic-instruct", name="Snowflake Arctic", 
                         description="Strong instruction following with images", context_window=4096),
                
                # Image models
                ModelInfo(id="stabilityai/stable-diffusion-xl-base-1.0", name="SDXL Base", 
                         description="High-quality image generation", context_window=None),
                ModelInfo(id="stabilityai/sdxl-turbo", name="SDXL Turbo", 
                         description="Fast inference for real-time applications", context_window=None),
                ModelInfo(id="playgroundai/playground-v2.5", name="Playground v2.5", 
                         description="Creative, high-quality outputs", context_window=None),
                ModelInfo(id="runwayml/stable-diffusion-v1-5", name="Stable Diffusion v1.5", 
                         description="Reliable, well-tested image generation", context_window=None),
                
                # Audio models
                ModelInfo(id="cartesia/sonic", name="Sonic TTS", 
                         description="High-quality text-to-speech with multiple voices", context_window=None),
                ModelInfo(id="whisper-large-v3", name="Whisper Large v3", 
                         description="State-of-the-art speech recognition", context_window=None),
                ModelInfo(id="whisper-medium", name="Whisper Medium", 
                         description="Efficient speech recognition", context_window=None),
            ]

    async def generate_completion(self, model_id: str, prompt: str, system_prompt: Optional[str] = None, params: Optional[LLMOptions] = None) -> Dict[str, Any]:
        """
        Generates a text completion using Together AI.
        
        For compatibility with older models that don't support chat format, this uses the completions endpoint.
        For chat-optimized models, it falls back to the chat completions endpoint.
        
        Args:
            model_id: The ID of the model to use
            prompt: The prompt text
            system_prompt: Optional system instructions
            params: Optional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        logger.info(f"TogetherAIProvider: Generating completion for model {model_id}")
        
        if not self.api_key:
            return {"error": "API key not configured for TogetherAIProvider."}
        
        # Check if model is chat-optimized (most modern models are)
        if "instruct" in model_id.lower() or "chat" in model_id.lower():
            # For chat-optimized models, use chat completions endpoint
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            return await self.generate_chat_completion(model_id, messages, system_prompt=None, params=params)
        
        # For non-chat models, use completions endpoint
        try:
            # Prepare prompt with system instructions if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Prepare API parameters
            api_params = {
                "model": model_id,
                "prompt": full_prompt,
                "max_tokens": 1024,  # Default max tokens
                "temperature": 0.7,  # Default temperature
            }
            
            # Override with any provided parameters
            if params:
                if params.get("temperature") is not None:
                    api_params["temperature"] = params["temperature"]
                if params.get("max_tokens") is not None:
                    api_params["max_tokens"] = params["max_tokens"]
                if params.get("top_p") is not None:
                    api_params["top_p"] = params["top_p"]
                if params.get("top_k") is not None:
                    api_params["top_k"] = params["top_k"]
                if params.get("stop_sequences"):
                    api_params["stop"] = params["stop_sequences"]
            
            # Make API call
            response = await self.client.post("/completions", json=api_params)
            response.raise_for_status()
            response_data = response.json()
            
            # Extract completion text and usage info
            completion_text = response_data.get("choices", [{}])[0].get("text", "")
            usage_info = response_data.get("usage", {})
            
            return {
                "text": completion_text,
                "usage": usage_info,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error generating completion with Together AI: {str(e)}")
            return {"error": str(e)}

    async def generate_chat_completion(self, model_id: str, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, params: Optional[LLMOptions] = None) -> Dict[str, Any]:
        """
        Generates a chat completion using Together AI.
        
        Args:
            model_id: The ID of the model to use
            messages: List of message dictionaries with role and content
            system_prompt: Optional system instructions (if not already in messages)
            params: Optional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        logger.info(f"TogetherAIProvider: Generating chat completion for model {model_id}")
        
        if not self.api_key:
            return {"error": "API key not configured for TogetherAIProvider."}
        
        try:
            # Prepare messages for API
            api_messages = []
            
            # Add system message if provided and not already in messages
            if system_prompt:
                has_system_message = any(msg.get("role") == "system" for msg in messages)
                if not has_system_message:
                    api_messages.append({"role": "system", "content": system_prompt})
            
            # Add all provided messages
            api_messages.extend(messages)
            
            # Prepare API parameters
            api_params = {
                "model": model_id,
                "messages": api_messages,
                "max_tokens": 1024,  # Default max tokens
                "temperature": 0.7,  # Default temperature
            }
            
            # Override with any provided parameters
            if params:
                if params.get("temperature") is not None:
                    api_params["temperature"] = params["temperature"]
                if params.get("max_tokens") is not None:
                    api_params["max_tokens"] = params["max_tokens"]
                if params.get("top_p") is not None:
                    api_params["top_p"] = params["top_p"]
                if params.get("top_k") is not None:
                    api_params["top_k"] = params["top_k"]
                if params.get("stop_sequences"):
                    api_params["stop"] = params["stop_sequences"]
            
            # Make API call
            response = await self.client.post("/chat/completions", json=api_params)
            response.raise_for_status()
            response_data = response.json()
            
            # Extract completion text and usage info
            completion_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage_info = response_data.get("usage", {})
            
            return {
                "text": completion_text,
                "usage": usage_info,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error generating chat completion with Together AI: {str(e)}")
            return {"error": str(e)}
    
    async def generate_image(self, prompt: str, model_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates an image using Together AI's image generation models.
        
        Args:
            prompt: Text description of the desired image
            model_id: Optional model ID (defaults to SDXL)
            params: Optional generation parameters
            
        Returns:
            Dictionary with image URL and metadata
        """
        logger.info(f"TogetherAIProvider: Generating image with prompt: {prompt[:50]}...")
        
        if not self.api_key:
            return {"error": "API key not configured for TogetherAIProvider."}
        
        # Use default model if none specified
        if not model_id:
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        try:
            # Prepare API parameters
            api_params = {
                "model": model_id,
                "prompt": prompt,
                "n": 1,  # Generate one image
                "size": "1024x1024",  # Default size
            }
            
            # Override with any provided parameters
            if params:
                if params.get("size"):
                    api_params["size"] = params["size"]
                if params.get("n") is not None:
                    api_params["n"] = params["n"]
                if params.get("response_format"):
                    api_params["response_format"] = params["response_format"]
            
            # Make API call
            response = await self.client.post("/images/generations", json=api_params)
            response.raise_for_status()
            response_data = response.json()
            
            # Extract image URL
            image_url = response_data.get("data", [{}])[0].get("url", "")
            
            return {
                "url": image_url,
                "model": model_id,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error generating image with Together AI: {str(e)}")
            return {"error": str(e)}
    
    async def generate_speech(self, text: str, voice: str = "default", model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates speech from text using Together AI's TTS models.
        
        Args:
            text: Text to convert to speech
            voice: Voice identifier to use
            model_id: Optional model ID (defaults to cartesia/sonic)
            
        Returns:
            Dictionary with audio data and metadata
        """
        logger.info(f"TogetherAIProvider: Generating speech for text: {text[:50]}...")
        
        if not self.api_key:
            return {"error": "API key not configured for TogetherAIProvider."}
        
        # Use default model if none specified
        if not model_id:
            model_id = "cartesia/sonic"
        
        try:
            # Prepare API parameters
            api_params = {
                "model": model_id,
                "input": text,
                "voice": voice
            }
            
            # Make API call
            response = await self.client.post("/audio/speech", json=api_params)
            response.raise_for_status()
            
            # Extract audio data
            audio_content = response.content
            
            return {
                "audio": audio_content,
                "model": model_id,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error generating speech with Together AI: {str(e)}")
            return {"error": str(e)}
    
    async def transcribe_audio(self, audio_file: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribes audio to text using Together AI's STT models.
        
        Args:
            audio_file: Path to audio file
            model_id: Optional model ID (defaults to whisper-large-v3)
            
        Returns:
            Dictionary with transcription text and metadata
        """
        logger.info(f"TogetherAIProvider: Transcribing audio file: {audio_file}")
        
        if not self.api_key:
            return {"error": "API key not configured for TogetherAIProvider."}
        
        # Use default model if none specified
        if not model_id:
            model_id = "whisper-large-v3"
        
        try:
            # Prepare form data with file
            with open(audio_file, "rb") as f:
                files = {"file": f}
                form_data = {"model": model_id}
                
                # Make API call
                response = await self.client.post("/audio/transcriptions", data=form_data, files=files)
                response.raise_for_status()
                response_data = response.json()
            
            # Extract transcription text
            transcription = response_data.get("text", "")
            
            return {
                "text": transcription,
                "model": model_id,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio with Together AI: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_image(self, image_url: str, prompt: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes an image using Together AI's vision models.
        
        Args:
            image_url: URL of the image to analyze
            prompt: Text prompt describing what to analyze about the image
            model_id: Optional model ID (defaults to Qwen/Qwen-VL-Chat)
            
        Returns:
            Dictionary with analysis text and metadata
        """
        logger.info(f"TogetherAIProvider: Analyzing image at {image_url}")
        
        if not self.api_key:
            return {"error": "API key not configured for TogetherAIProvider."}
        
        # Use default model if none specified
        if not model_id:
            model_id = "Qwen/Qwen-VL-Chat"
        
        try:
            # Prepare messages with image content
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
            
            # Prepare API parameters
            api_params = {
                "model": model_id,
                "messages": messages,
                "max_tokens": 1024
            }
            
            # Make API call
            response = await self.client.post("/chat/completions", json=api_params)
            response.raise_for_status()
            response_data = response.json()
            
            # Extract analysis text
            analysis_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "text": analysis_text,
                "model": model_id,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image with Together AI: {str(e)}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the HTTP client session."""
        if hasattr(self, 'client'):
            await self.client.aclose()
