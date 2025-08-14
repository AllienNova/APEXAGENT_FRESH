# Alternative Video Providers Research for Aideon AI Lite

## Overview

This research document evaluates alternative video providers for integration with Aideon AI Lite, focusing on providers that can be used until Together AI adds native video generation capabilities. The goal is to identify suitable providers for both free and premium tiers while maintaining a consistent interface that will allow for seamless migration when Together AI adds video support.

## Table of Contents

1. [Evaluation Criteria](#evaluation-criteria)
2. [Provider Analysis](#provider-analysis)
3. [Recommended Integration Strategy](#recommended-integration-strategy)
4. [Implementation Considerations](#implementation-considerations)
5. [Cost Analysis](#cost-analysis)
6. [Migration Path](#migration-path)

## Evaluation Criteria

Providers were evaluated based on the following criteria:

1. **API Compatibility**: How easily the provider's API can be integrated with Aideon's existing architecture
2. **Quality**: Video generation quality and capabilities
3. **Cost**: Pricing structure and affordability for free/premium tiers
4. **Reliability**: Service uptime and performance
5. **Features**: Support for text-to-video, image-to-video, and video editing
6. **Customization**: Control over video parameters (resolution, duration, style)
7. **Documentation**: Quality and completeness of API documentation
8. **Community Support**: Active development and community resources

## Provider Analysis

### 1. Runway ML

**Overview**: Runway ML offers state-of-the-art video generation capabilities with their Gen-2 model, supporting both text-to-video and image-to-video generation.

**Strengths**:
- High-quality video generation
- Excellent control over style and parameters
- Robust API with good documentation
- Support for image-to-video (useful for continuity with Together AI generated images)
- Strong customization options

**Weaknesses**:
- Higher cost compared to other providers
- Limited free tier options
- Requires separate API key management

**API Compatibility**: 8/10  
**Quality**: 9/10  
**Cost**: 6/10  
**Reliability**: 8/10  
**Features**: 9/10  
**Customization**: 9/10  
**Documentation**: 8/10  
**Community Support**: 7/10  

**Sample API Request**:
```python
import requests

url = "https://api.runwayml.com/v1/inference"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "gen-2",
    "input": {
        "prompt": "A beautiful sunset over mountains",
        "negative_prompt": "blurry, distorted",
        "num_frames": 24,
        "fps": 8
    }
}
response = requests.post(url, json=payload, headers=headers)
```

### 2. Replicate

**Overview**: Replicate provides access to multiple open-source video generation models through a unified API, including Zeroscope, ModelScope, and AnimateDiff.

**Strengths**:
- Access to multiple models through one API
- More affordable pricing
- Good for free tier implementation
- Simple API structure
- Pay-as-you-go pricing

**Weaknesses**:
- Quality varies between models
- Less consistent results
- Limited customization for some models

**API Compatibility**: 9/10  
**Quality**: 7/10  
**Cost**: 8/10  
**Reliability**: 7/10  
**Features**: 8/10  
**Customization**: 7/10  
**Documentation**: 8/10  
**Community Support**: 9/10  

**Sample API Request**:
```python
import replicate

output = replicate.run(
    "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
    input={
        "prompt": "A beautiful sunset over mountains",
        "negative_prompt": "blurry, distorted",
        "fps": 24,
        "seconds": 3
    }
)
```

### 3. Stability AI

**Overview**: Stability AI, known for Stable Diffusion, has recently introduced video generation capabilities with their Stable Video Diffusion model.

**Strengths**:
- Integration potential with existing Stable Diffusion models from Together AI
- Good image-to-video capabilities
- Active development and improvements
- Familiar interface for developers already using Stable Diffusion

**Weaknesses**:
- Newer offering with less maturity
- Limited text-to-video capabilities
- Shorter video durations
- Less control over parameters

**API Compatibility**: 7/10  
**Quality**: 7/10  
**Cost**: 7/10  
**Reliability**: 6/10  
**Features**: 6/10  
**Customization**: 6/10  
**Documentation**: 6/10  
**Community Support**: 8/10  

**Sample API Request**:
```python
import requests

url = "https://api.stability.ai/v1/generation/stable-video-diffusion/text-to-video"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "text_prompts": [
        {
            "text": "A beautiful sunset over mountains",
            "weight": 1.0
        }
    ],
    "height": 576,
    "width": 1024,
    "cfg_scale": 7.5,
    "motion_bucket_id": 40
}
response = requests.post(url, json=payload, headers=headers)
```

### 4. Pika Labs

**Overview**: Pika Labs offers advanced video generation with strong style control and animation capabilities.

**Strengths**:
- High-quality video generation
- Strong style control
- Good for creative applications
- Support for longer video sequences
- Advanced motion control

**Weaknesses**:
- Limited API access (currently in beta)
- Higher cost for production use
- Less documentation compared to others

**API Compatibility**: 6/10  
**Quality**: 9/10  
**Cost**: 5/10  
**Reliability**: 7/10  
**Features**: 8/10  
**Customization**: 8/10  
**Documentation**: 5/10  
**Community Support**: 6/10  

**Sample API Request**:
```python
# Note: API structure may change as Pika Labs is still in beta
import requests

url = "https://api.pika.art/v1/generate"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "prompt": "A beautiful sunset over mountains",
    "negative_prompt": "blurry, distorted",
    "duration": 5,
    "fps": 24,
    "style": "cinematic"
}
response = requests.post(url, json=payload, headers=headers)
```

### 5. HuggingFace Inference API

**Overview**: HuggingFace provides access to various open-source video generation models through their Inference API.

**Strengths**:
- Access to multiple models
- Integration with existing HuggingFace ecosystem
- Open-source focus
- Community-driven improvements
- Affordable pricing

**Weaknesses**:
- Variable quality between models
- Less consistent support
- Limited commercial guarantees
- Performance can vary

**API Compatibility**: 8/10  
**Quality**: 6/10  
**Cost**: 9/10  
**Reliability**: 6/10  
**Features**: 7/10  
**Customization**: 6/10  
**Documentation**: 7/10  
**Community Support**: 9/10  

**Sample API Request**:
```python
import requests

API_URL = "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b"
headers = {"Authorization": f"Bearer {api_key}"}
payload = {"inputs": "A beautiful sunset over mountains"}

response = requests.post(API_URL, headers=headers, json=payload)
```

## Recommended Integration Strategy

Based on the evaluation, we recommend a dual-provider approach:

### Premium Tier: Runway ML

Runway ML offers the highest quality video generation with excellent control over parameters, making it ideal for premium tier users who expect professional-quality results. The strong image-to-video capabilities also allow for seamless integration with Together AI's image generation models.

### Free Tier: Replicate

Replicate provides access to multiple models at a more affordable price point, making it suitable for free tier implementation. The simple API structure and pay-as-you-go pricing allow for cost-effective scaling while still providing decent quality results.

### Provider Interface

To ensure seamless migration when Together AI adds video support, we recommend implementing a provider-agnostic interface that abstracts the underlying video generation provider:

```python
class VideoProvider(ABC):
    """Abstract base class for video providers."""
    
    @abstractmethod
    async def generate_video_from_text(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        duration: float = 3.0,
        fps: int = 24,
        width: int = 1024,
        height: int = 576,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video from text prompt."""
        pass
    
    @abstractmethod
    async def generate_video_from_image(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        duration: float = 3.0,
        fps: int = 24,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video from image."""
        pass
```

## Implementation Considerations

### 1. API Key Management

Extend the existing API key management system to support multiple video providers:

```python
class VideoProviderKeyManager:
    """API key manager for video providers."""
    
    def __init__(self, config_dir: str = "/etc/aideon/api_keys"):
        """Initialize the key manager."""
        self.config_dir = config_dir
        self.runway_key_file = os.path.join(config_dir, "runway_keys.enc")
        self.replicate_key_file = os.path.join(config_dir, "replicate_keys.enc")
        # Load keys from encrypted storage
        self.runway_keys = self._load_keys(self.runway_key_file)
        self.replicate_keys = self._load_keys(self.replicate_key_file)
    
    def get_runway_key(self, user_id: Optional[str] = None) -> Optional[str]:
        """Get Runway ML API key for user or system default."""
        if user_id and user_id in self.runway_keys:
            return self.runway_keys[user_id]
        return self.runway_keys.get("system")
    
    def get_replicate_key(self, user_id: Optional[str] = None) -> Optional[str]:
        """Get Replicate API key for user or system default."""
        if user_id and user_id in self.replicate_keys:
            return self.replicate_keys[user_id]
        return self.replicate_keys.get("system")
```

### 2. Provider Selection Logic

Implement tier-based provider selection similar to the Together AI model selector:

```python
class VideoProviderSelector:
    """Video provider selector based on user tier."""
    
    def __init__(self):
        """Initialize the provider selector."""
        self.key_manager = VideoProviderKeyManager()
    
    def get_provider_for_user(
        self,
        user_id: str,
        purpose: Optional[str] = None
    ) -> Tuple[VideoProvider, str]:
        """Get appropriate video provider for user based on tier."""
        # Get user tier
        user_tier = get_user_tier(user_id) or UserTier.FREE
        
        if user_tier in [UserTier.PREMIUM, UserTier.ENTERPRISE]:
            # Premium users get Runway ML
            api_key = self.key_manager.get_runway_key(user_id)
            if api_key:
                return RunwayMLVideoProvider(api_key), "runway"
        
        # Free tier or fallback to Replicate
        api_key = self.key_manager.get_replicate_key(user_id)
        if api_key:
            return ReplicateVideoProvider(api_key), "replicate"
        
        # No valid provider found
        raise ValueError("No valid video provider available")
```

### 3. Fallback Mechanism

Implement fallback between providers when one fails:

```python
class VideoProviderFallbackManager:
    """Fallback manager for video providers."""
    
    def __init__(self):
        """Initialize the fallback manager."""
        self.selector = VideoProviderSelector()
    
    async def generate_video_with_fallback(
        self,
        user_id: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video with fallback between providers."""
        try:
            # Get primary provider
            provider, provider_id = self.selector.get_provider_for_user(user_id)
            
            # Try primary provider
            result = await provider.generate_video_from_text(prompt, **kwargs)
            return {
                **result,
                "provider": provider_id,
                "fallback_used": False
            }
        except Exception as e:
            # Log error
            logger.error(f"Primary video provider failed: {str(e)}")
            
            try:
                # Fallback to Replicate for premium users
                if provider_id == "runway":
                    api_key = self.selector.key_manager.get_replicate_key(user_id)
                    if api_key:
                        fallback_provider = ReplicateVideoProvider(api_key)
                        result = await fallback_provider.generate_video_from_text(prompt, **kwargs)
                        return {
                            **result,
                            "provider": "replicate",
                            "fallback_used": True
                        }
                
                # No fallback available
                raise ValueError("No fallback provider available")
            except Exception as fallback_error:
                # Log fallback error
                logger.error(f"Fallback video provider failed: {str(fallback_error)}")
                raise
```

## Cost Analysis

### Runway ML (Premium Tier)

- **Text-to-Video**: $0.05 per second of generated video
- **Image-to-Video**: $0.06 per second of generated video
- **Estimated monthly cost per user**: $15-30 (assuming 5-10 minutes of video generation)

### Replicate (Free Tier)

- **Zeroscope model**: $0.002 per second of generated video
- **ModelScope model**: $0.003 per second of generated video
- **Estimated monthly cost per user**: $0.60-1.20 (assuming 5-10 minutes of video generation)

### Cost Control Measures

1. **Duration Limits**:
   - Free tier: Maximum 10 seconds per video, 60 seconds total per day
   - Premium tier: Maximum 30 seconds per video, 300 seconds total per day

2. **Resolution Limits**:
   - Free tier: 576p maximum resolution
   - Premium tier: 1080p maximum resolution

3. **Request Limits**:
   - Free tier: 10 video generations per day
   - Premium tier: 50 video generations per day

## Migration Path

When Together AI adds video generation capabilities, the migration path will be straightforward due to the provider-agnostic interface:

1. **Implement Together AI Video Provider**:
   ```python
   class TogetherAIVideoProvider(VideoProvider):
       """Together AI video provider implementation."""
       
       def __init__(self, api_key: str):
           """Initialize the provider with API key."""
           self.api_key = api_key
           self.base_url = "https://api.together.xyz/v1"
           self.headers = {
               "Authorization": f"Bearer {api_key}",
               "Content-Type": "application/json"
           }
       
       async def generate_video_from_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
           """Generate video from text prompt."""
           # Implementation using Together AI API
       
       async def generate_video_from_image(self, image_url: str, **kwargs) -> Dict[str, Any]:
           """Generate video from image."""
           # Implementation using Together AI API
   ```

2. **Update Provider Selection Logic**:
   ```python
   def get_provider_for_user(self, user_id: str, purpose: Optional[str] = None) -> Tuple[VideoProvider, str]:
       """Get appropriate video provider for user based on tier."""
       # Get user tier
       user_tier = get_user_tier(user_id) or UserTier.FREE
       
       # Check if Together AI video is available
       if is_feature_enabled("together_ai_video"):
           api_key = self.key_manager.get_together_ai_key(user_id)
           if api_key:
               return TogetherAIVideoProvider(api_key), "together_ai"
       
       # Fall back to existing providers
       if user_tier in [UserTier.PREMIUM, UserTier.ENTERPRISE]:
           # Premium users get Runway ML
           api_key = self.key_manager.get_runway_key(user_id)
           if api_key:
               return RunwayMLVideoProvider(api_key), "runway"
       
       # Free tier or fallback to Replicate
       api_key = self.key_manager.get_replicate_key(user_id)
       if api_key:
           return ReplicateVideoProvider(api_key), "replicate"
       
       # No valid provider found
       raise ValueError("No valid video provider available")
   ```

3. **Monitoring for Together AI Video Release**:
   - Set up automated monitoring of Together AI API documentation
   - Create alerts for new video-related endpoints
   - Prepare test cases for quick validation when available

4. **Gradual Rollout Strategy**:
   - Phase 1: Limited beta testing with Together AI video
   - Phase 2: A/B testing between existing providers and Together AI
   - Phase 3: Full migration to Together AI with fallback to existing providers
   - Phase 4: Deprecation of alternative providers (optional)

## Conclusion

The recommended dual-provider approach with Runway ML for premium tier and Replicate for free tier offers the best balance of quality, cost, and reliability while maintaining a clear migration path for when Together AI adds video generation capabilities. The provider-agnostic interface ensures that the integration remains flexible and future-proof, allowing Aideon AI Lite to offer video generation capabilities immediately while positioning for seamless adoption of Together AI's video models when they become available.
