# Aideon AI Lite + Together AI Integration Plan with Selected Models (Updated with Video Strategy)

## Executive Summary

This comprehensive integration plan outlines how Aideon AI Lite can leverage Together AI's platform to enhance existing capabilities, enable a free tier, and provide better fallback options. Based on thorough research of Together AI's model offerings, we've selected the optimal models for each modality to complement Aideon's core functionality while expanding model diversity across text, vision, image, audio, and coding. For video generation, which is not currently supported by Together AI, we've developed a multi-provider strategy.

## Strategic Alignment

This integration directly supports Aideon AI Lite's mission to build the world's first truly hybrid autonomous AI system by:

1. **Enhancing Model Diversity**: Access to complementary open-source models through a single API
2. **Enabling Free Tier**: Providing cost-effective options for basic functionality
3. **Improving Fallback Mechanisms**: Ensuring reliability when primary models are unavailable
4. **Enabling Hybrid Processing**: Combining local PC processing with cloud intelligence
5. **Expanding Modality Support**: Adding capabilities across text, vision, image, audio, and coding
6. **Multi-Provider Strategy for Video**: Implementing alternative providers for video generation until Together AI offers this capability

## Selected Models by Modality

### Text Models

| Tier | Role | Model | Context Length | Rationale |
|------|------|-------|---------------|-----------|
| Free | Primary | meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo | 8192 | Excellent performance/size ratio for general text tasks |
| Free | Fallback | mistralai/Mixtral-8x7B-Instruct-v0.1 | 32768 | Efficient MoE architecture with long context window |
| Premium | Fallback | meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo | 8192 | High-quality fallback when primary Aideon models are unavailable |
| Premium | Critical Tasks | meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo | 4096 | State-of-the-art performance for mission-critical tasks |

### Coding Models

| Tier | Role | Model | Context Length | Rationale |
|------|------|-------|---------------|-----------|
| Free | Primary | Nexusflow/NexusRaven-V2-13B | 16384 | Specialized for code generation with good context length |
| Free | Fallback | codellama/CodeLlama-13b-Instruct-hf | 16384 | Efficient performance for size with strong coding abilities |
| Premium | Fallback | deepseek-ai/deepseek-coder-33b-instruct | 16384 | Long context, specialized for code projects |
| Premium | Complex Tasks | codellama/CodeLlama-70b-Instruct-hf | 4096 | Highest parameter count for complex coding challenges |

### Vision Models

| Tier | Role | Model | Rationale |
|------|------|-------|-----------|
| Free | Primary | deepseek-ai/DeepSeek-VL-7B-Chat | Efficient vision-language model for basic image understanding |
| Premium | Fallback | Qwen/Qwen-VL-Chat | Strong multimodal capabilities for premium tier fallback |
| Premium | Specialized | Snowflake/snowflake-arctic-instruct | Strong instruction following with images |

### Image Generation Models

| Tier | Role | Model | Rationale |
|------|------|-------|-----------|
| Free | Primary | stabilityai/stable-diffusion-xl-base-1.0 | High-quality image generation for free tier |
| Free | Secondary | runwayml/stable-diffusion-v1-5 | Reliable, well-tested alternative |
| Premium | Quick Gen | stabilityai/sdxl-turbo | Fast inference for real-time applications |
| Premium | High Quality | playgroundai/playground-v2.5 | Creative, high-quality outputs for premium needs |

### Audio Models

| Tier | Role | Model | Rationale |
|------|------|-------|-----------|
| Both | TTS | cartesia/sonic | High-quality text-to-speech with multiple voices |
| Free | STT | whisper-medium | Efficient speech recognition for free tier |
| Premium | STT | whisper-large-v3 | State-of-the-art speech recognition for premium fallback |

### Video Generation Strategy

**Note: Together AI does not currently offer video generation models through their API.**

To address this gap, we recommend a multi-provider approach:

| Timeframe | Strategy | Recommended Providers |
|-----------|----------|----------------------|
| Short-term (0-3 months) | Implement alternative video providers | Runway ML (Gen-2), Replicate (Zeroscope), Stability AI (Stable Video Diffusion) |
| Medium-term (3-6 months) | Develop provider-agnostic interface | Seamless provider switching capability |
| Long-term (6+ months) | Prepare for Together AI integration | Monitor for Together AI video model releases |

See the detailed [Video Integration Strategy](/home/ubuntu/github_repo/together_ai_video_strategy.md) document for implementation recommendations and migration path.

## Technical Integration Architecture

### 1. Core Integration Components

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│                     │     │                     │     │                     │
│   Aideon AI Lite    │◄────┤  Integration Layer  │◄────┤    Together AI      │
│   Primary Models    │     │  & Model Router     │     │ Complementary Models│
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
        ▲                            ▲                            ▲
        │                            │                            │
        ▼                            ▼                            ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│                     │     │                     │     │                     │
│   Local Processing  │     │ Intelligent Routing │     │  Fallback Options   │
│                     │     │   & Tier Manager    │     │   & Free Models     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                      ▲
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │                     │
                            │  Video Providers    │
                            │  (Alternative)      │
                            └─────────────────────┘
```

### 2. Integration Methods

#### a. Intelligent Model Router with Selected Models

```python
class AideonModelRouter:
    def __init__(self, together_api_key=None, video_provider_configs=None):
        self.primary_models = self._initialize_primary_models()
        self.together_client = None
        self.video_providers = {}
        
        if together_api_key:
            from together import Together
            self.together_client = Together(api_key=together_api_key)
        
        if video_provider_configs:
            self._initialize_video_providers(video_provider_configs)
    
    def _initialize_primary_models(self):
        # Initialize Aideon's existing primary models
        return {
            "text": PrimaryTextModel(),
            "vision": PrimaryVisionModel(),
            "image": PrimaryImageModel(),
            "audio": PrimaryAudioModel(),
            "code": PrimaryCodeModel(),
            "video": PrimaryVideoModel()
        }
    
    def _initialize_video_providers(self, configs):
        # Initialize alternative video providers
        if configs.get("runway"):
            from providers.video.runway import RunwayProvider
            self.video_providers["runway"] = RunwayProvider(configs["runway"])
        
        if configs.get("replicate"):
            from providers.video.replicate import ReplicateProvider
            self.video_providers["replicate"] = ReplicateProvider(configs["replicate"])
    
    def generate_response(self, prompt, modality="text", use_fallback=True, tier="premium"):
        try:
            # Handle video generation separately
            if modality == "video":
                return self._generate_video(prompt, tier)
            
            # First attempt with primary Aideon models (for premium tier)
            if tier == "premium":
                result = self.primary_models[modality].generate(prompt)
                if result.quality_score > 0.8:
                    return result
            
            # Use Together AI models as enhancement or fallback
            if tier == "free" or use_fallback:
                if self.together_client:
                    # Map modality to appropriate Together AI model
                    model = self._get_together_model_for_modality(modality, tier)
                    
                    # Handle different modalities appropriately
                    if modality == "text":
                        completion = self.together_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        return completion.choices[0].message.content
                    elif modality == "code":
                        completion = self.together_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        return completion.choices[0].message.content
                    elif modality == "image":
                        response = self.together_client.images.generate(
                            model=model,
                            prompt=prompt,
                            n=1,
                            size="1024x1024"
                        )
                        return response.data[0].url
                    elif modality == "audio":
                        response = self.together_client.audio.speech.create(
                            model="cartesia/sonic",
                            input=prompt,
                            voice="laidback woman"
                        )
                        return response
                    elif modality == "vision":
                        # For vision tasks with image input
                        completion = self.together_client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "user", "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {"url": image_url}}
                                ]}
                            ]
                        )
                        return completion.choices[0].message.content
            
            # If free tier but no Together client, use limited version of primary
            if tier == "free":
                return self.primary_models[modality].generate_limited(prompt)
                
            # Return original result if no fallback available
            return result
            
        except Exception as e:
            # Fallback to Together AI on exception if available
            if use_fallback and self.together_client:
                model = self._get_together_model_for_modality(modality, "free")
                completion = self.together_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return completion.choices[0].message.content
            raise e
    
    def _generate_video(self, prompt, tier="premium"):
        """Handle video generation using alternative providers."""
        try:
            # First attempt with primary Aideon models (for premium tier)
            if tier == "premium":
                result = self.primary_models["video"].generate(prompt)
                if result.quality_score > 0.8:
                    return result
            
            # Use alternative video providers
            if self.video_providers:
                # Select provider based on tier
                provider = self._get_video_provider_for_tier(tier)
                return provider.generate_video(prompt)
            
            # If free tier but no video providers, use limited version of primary
            if tier == "free":
                return self.primary_models["video"].generate_limited(prompt)
            
            # Return original result if no fallback available
            return result
            
        except Exception as e:
            # Log error and raise
            logger.error(f"Video generation failed: {e}")
            raise e
    
    def _get_video_provider_for_tier(self, tier):
        """Select appropriate video provider based on tier."""
        if tier == "premium" and "runway" in self.video_providers:
            return self.video_providers["runway"]
        elif "replicate" in self.video_providers:
            return self.video_providers["replicate"]
        else:
            # Return first available provider as fallback
            return next(iter(self.video_providers.values()))
    
    def _get_together_model_for_modality(self, modality, tier):
        # Map modality and tier to appropriate Together AI model
        models = {
            "text": {
                "free": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "free_fallback": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "premium": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "premium_critical": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
            },
            "code": {
                "free": "Nexusflow/NexusRaven-V2-13B",
                "free_fallback": "codellama/CodeLlama-13b-Instruct-hf",
                "premium": "deepseek-ai/deepseek-coder-33b-instruct",
                "premium_complex": "codellama/CodeLlama-70b-Instruct-hf"
            },
            "vision": {
                "free": "deepseek-ai/DeepSeek-VL-7B-Chat",
                "premium": "Qwen/Qwen-VL-Chat",
                "premium_specialized": "Snowflake/snowflake-arctic-instruct"
            },
            "image": {
                "free": "stabilityai/stable-diffusion-xl-base-1.0",
                "free_secondary": "runwayml/stable-diffusion-v1-5",
                "premium_fast": "stabilityai/sdxl-turbo",
                "premium_quality": "playgroundai/playground-v2.5"
            },
            "audio": {
                "tts": "cartesia/sonic",
                "stt_free": "whisper-medium",
                "stt_premium": "whisper-large-v3"
            }
        }
        
        # Return appropriate model based on tier and modality
        if modality == "audio":
            if "stt" in prompt.lower():
                return models[modality]["stt_" + tier]
            return models[modality]["tts"]
            
        return models[modality][tier]
```

#### b. Video Provider Interface

```python
class VideoProviderInterface:
    """Interface for video generation providers."""
    
    def generate_video(self, prompt, duration_seconds=5, fps=24, resolution="720p", **kwargs):
        """Generate video from text prompt."""
        raise NotImplementedError
    
    def edit_video(self, source_video, edit_prompt, **kwargs):
        """Edit existing video based on prompt."""
        raise NotImplementedError
    
    def extend_video(self, source_video, extension_seconds, **kwargs):
        """Extend video by specified duration."""
        raise NotImplementedError


class RunwayVideoProvider(VideoProviderInterface):
    """Runway ML implementation of video provider."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = RunwayClient(api_key)
    
    def generate_video(self, prompt, duration_seconds=5, fps=24, resolution="720p", **kwargs):
        """Generate video using Runway ML Gen-2 model."""
        try:
            response = self.client.generate(
                model="gen-2",
                prompt=prompt,
                duration=duration_seconds,
                fps=fps,
                resolution=resolution,
                **kwargs
            )
            return response.output_url
        except Exception as e:
            logger.error(f"Runway video generation failed: {e}")
            return None


class ReplicateVideoProvider(VideoProviderInterface):
    """Replicate implementation of video provider."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        import replicate
        replicate.api_token = api_key
        self.client = replicate
    
    def generate_video(self, prompt, duration_seconds=5, fps=24, resolution="720p", **kwargs):
        """Generate video using Replicate models."""
        try:
            # Use Zeroscope XL model
            output = self.client.run(
                "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                input={
                    "prompt": prompt,
                    "fps": fps,
                    "seconds": duration_seconds
                }
            )
            return output[0]
        except Exception as e:
            logger.error(f"Replicate video generation failed: {e}")
            return None
```

### 3. Authentication & Security

```python
class AideonSecureIntegration:
    def __init__(self):
        self.primary_api_key = self._load_primary_api_key()
        self.together_api_key = self._load_together_api_key_from_secure_storage()
        self.video_provider_keys = self._load_video_provider_keys()
        
        self.together_client = None
        if self.together_api_key:
            from together import Together
            self.together_client = Together(api_key=self.together_api_key)
    
    def _load_primary_api_key(self):
        # Load Aideon's primary API key
        return os.environ.get("AIDEON_API_KEY")
    
    def _load_together_api_key_from_secure_storage(self):
        # Implement secure key retrieval from environment variables or vault
        return os.environ.get("TOGETHER_API_KEY")
    
    def _load_video_provider_keys(self):
        # Load keys for video providers
        return {
            "runway": os.environ.get("RUNWAY_API_KEY"),
            "replicate": os.environ.get("REPLICATE_API_KEY")
        }
    
    def rotate_api_keys(self):
        # Implement key rotation logic for both primary and fallback
        pass
```

## Implementation Roadmap

### Phase 1: Foundation Setup (2 Weeks)

1. **Tier Management System**
   - Create free tier configuration
   - Implement tier detection logic
   - Develop feature limitations for free tier
   - Set up tier upgrade pathway

2. **Model Router Implementation**
   - Create intelligent routing system with selected models
   - Implement primary/fallback logic
   - Develop modality-specific routing
   - Set up quality assessment metrics

3. **Together AI Integration**
   - Create secure API client wrapper
   - Implement authentication and key management
   - Develop error handling and retry logic
   - Set up logging and monitoring

### Phase 2: Feature Enhancement (3 Weeks)

4. **Multi-Modal Fallbacks**
   - Implement text generation fallbacks with selected models
   - Add image generation alternatives
   - Create vision model backups
   - Develop audio processing alternatives
   - Implement code generation fallbacks

5. **Video Provider Integration**
   - Implement video provider interface
   - Integrate Runway ML for premium tier
   - Integrate Replicate for free tier
   - Create seamless provider switching capability

6. **Framework Connectors**
   - Build LangChain fallback chains
   - Implement LlamaIndex alternative retrievers
   - Create HuggingFace model alternatives
   - Develop CrewAI backup agents

7. **Free Tier Optimization**
   - Implement usage quotas and limits
   - Create cost-optimized processing paths
   - Develop caching strategies for free tier
   - Build upgrade conversion points

### Phase 3: User Experience & Production (3 Weeks)

8. **User Interface Enhancements**
   - Create tier selection interface
   - Implement model source indicators
   - Develop cost estimation features
   - Add usage analytics dashboard

9. **Hybrid Processing Logic**
   - Implement intelligent routing between local and cloud
   - Create fallback mechanisms
   - Develop caching strategies
   - Build offline mode capabilities

10. **Production Deployment**
    - Implement comprehensive testing
    - Create deployment automation
    - Develop monitoring and alerting
    - Create documentation and training materials

11. **Video Integration Monitoring**
    - Set up monitoring for Together AI video model releases
    - Prepare integration code templates
    - Create migration plan for when Together AI adds video support

## Technical Benefits

1. **Enhanced Model Diversity**
   - Complementary models for different use cases
   - Specialized alternatives for specific tasks
   - Broader coverage across modalities
   - Regular updates with new model options

2. **Improved Reliability**
   - Robust fallback mechanisms with selected models
   - Alternative processing paths
   - Graceful degradation options
   - Higher overall system availability

3. **Free Tier Enablement**
   - Cost-effective model options
   - Usage-optimized processing
   - Quota management system
   - Conversion pathway to premium

4. **Cost Optimization**
   - Pay-as-you-go pricing for fallbacks
   - No upfront infrastructure costs for alternatives
   - Intelligent routing to optimize costs
   - Batch processing for efficiency

5. **Comprehensive Modality Support**
   - Together AI for text, coding, vision, image, and audio
   - Alternative providers for video
   - Seamless user experience across all modalities
   - Future-proof architecture for Together AI video integration

## Business Impact

1. **Enhanced User Experience**
   - More reliable service
   - Broader capability options
   - Free entry point for new users
   - Seamless premium upgrade path

2. **Competitive Advantage**
   - Free tier to compete with basic offerings
   - More reliable service than competitors
   - Broader model coverage
   - Cost-effective scaling

3. **Market Expansion**
   - Reach cost-sensitive segments
   - Provide entry-level offering
   - Create upgrade conversion funnel
   - Expand total addressable market

4. **Revenue Opportunities**
   - Free-to-premium conversion
   - Higher user acquisition
   - Increased retention through reliability
   - Expanded use cases with fallback options

## Risk Assessment & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| Quality Disparity | High | Medium | Implement quality thresholds and user feedback |
| Cost Management | Medium | Medium | Set up usage limits and intelligent routing |
| User Confusion | Medium | Low | Clear UI indicators for model sources |
| Security Concerns | High | Low | Use secure key management and audit access |
| Dependency Risk | Medium | Medium | Maintain multiple fallback options |
| Video Provider Reliability | Medium | Medium | Implement multiple video providers with fallbacks |

## Accessibility Enhancements

1. **Economic Accessibility**
   - Free tier for cost-sensitive users
   - Pay-as-you-go options for occasional users
   - Premium tier for power users
   - Transparent upgrade path

2. **Technical Accessibility**
   - Simplified API reduces integration complexity
   - Multiple language support (Python, TypeScript, etc.)
   - Framework compatibility reduces learning curve
   - Comprehensive documentation and examples

3. **User Accessibility**
   - Intuitive tier selection interface
   - Clear model source indicators
   - Transparent capability differences
   - Simplified onboarding for free tier

## Implementation Requirements

1. **Technical Resources**
   - 1 Senior Backend Developer
   - 1 ML Engineer
   - 1 Frontend Developer (part-time)
   - 1 DevOps Engineer (part-time)

2. **Infrastructure**
   - Tier management system
   - Model routing infrastructure
   - Cost tracking and reporting system
   - Testing environment

3. **External Dependencies**
   - Together AI account and API key
   - Video provider accounts and API keys
   - Integration libraries (LangChain, etc.)
   - Monitoring tools
   - Documentation platform

## Next Steps

1. **Immediate Actions**
   - Create Together AI account
   - Generate API key
   - Set up secure key storage
   - Create initial free tier prototype
   - Research and select video provider

2. **Key Decisions**
   - Free tier feature limitations
   - Model fallback hierarchy
   - Cost management approach
   - Deployment timeline
   - Primary video provider selection

3. **Success Metrics**
   - Free tier user acquisition
   - Conversion rate to premium
   - Fallback utilization rate
   - User satisfaction across tiers
   - Video generation quality ratings

## Conclusion

The integration of Together AI with Aideon AI Lite represents a strategic opportunity to enhance existing capabilities, enable a free tier, and provide better fallback options. By leveraging Together AI's platform as a complementary service with carefully selected models for each modality, Aideon can expand its model diversity across text, vision, image, audio, and coding modalities while maintaining the primacy of its core models.

For video generation, which is not currently supported by Together AI, we've developed a multi-provider strategy that ensures Aideon can still offer comprehensive modality support while positioning for future Together AI video integration.

This integration aligns perfectly with Aideon's mission to build the world's first truly hybrid autonomous AI system, combining local PC processing with cloud intelligence. The implementation roadmap provides a clear path forward, with defined phases and specific tasks to ensure successful integration.

By proceeding with this integration, Aideon AI Lite will be positioned to definitively surpass existing competitors in privacy, performance, and reliability, while also offering a more accessible and cost-effective solution for users through its new free tier and enhanced fallback capabilities.
