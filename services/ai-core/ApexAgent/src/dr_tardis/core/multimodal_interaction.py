"""
Multimodal Interaction Layer for Dr. TARDIS

This module implements the multimodal input processing, output generation,
and modality coordination components of Dr. TARDIS as defined in the architecture.
"""

import base64
import datetime
import io
import json
import os
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set, Union, BinaryIO

class ModalityType(Enum):
    """Types of interaction modalities supported by Dr. TARDIS."""
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"
    IMAGE = "image"
    MULTIMODAL = "multimodal"

class ResourceConstraints:
    """Represents constraints on system resources."""
    
    def __init__(
        self,
        bandwidth: Optional[float] = None,  # in Mbps
        latency: Optional[float] = None,    # in ms
        device_memory: Optional[float] = None,  # in MB
        screen_size: Optional[Tuple[int, int]] = None,  # width, height in pixels
        supports_audio: bool = True,
        supports_video: bool = True,
        supports_images: bool = True,
        battery_level: Optional[float] = None,  # percentage
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.bandwidth = bandwidth
        self.latency = latency
        self.device_memory = device_memory
        self.screen_size = screen_size
        self.supports_audio = supports_audio
        self.supports_video = supports_video
        self.supports_images = supports_images
        self.battery_level = battery_level
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the resource constraints to a dictionary."""
        return {
            "bandwidth": self.bandwidth,
            "latency": self.latency,
            "device_memory": self.device_memory,
            "screen_size": self.screen_size,
            "supports_audio": self.supports_audio,
            "supports_video": self.supports_video,
            "supports_images": self.supports_images,
            "battery_level": self.battery_level,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceConstraints':
        """Create resource constraints from a dictionary."""
        return cls(
            bandwidth=data.get("bandwidth"),
            latency=data.get("latency"),
            device_memory=data.get("device_memory"),
            screen_size=data.get("screen_size"),
            supports_audio=data.get("supports_audio", True),
            supports_video=data.get("supports_video", True),
            supports_images=data.get("supports_images", True),
            battery_level=data.get("battery_level"),
            metadata=data.get("metadata", {})
        )
    
    def is_low_bandwidth(self) -> bool:
        """Check if bandwidth is low."""
        return self.bandwidth is not None and self.bandwidth < 1.0  # Less than 1 Mbps
    
    def is_high_latency(self) -> bool:
        """Check if latency is high."""
        return self.latency is not None and self.latency > 300  # More than 300ms
    
    def is_low_memory(self) -> bool:
        """Check if device memory is low."""
        return self.device_memory is not None and self.device_memory < 512  # Less than 512MB
    
    def is_small_screen(self) -> bool:
        """Check if screen size is small."""
        return (self.screen_size is not None and 
                (self.screen_size[0] < 480 or self.screen_size[1] < 800))  # Smaller than 480x800
    
    def is_low_battery(self) -> bool:
        """Check if battery level is low."""
        return self.battery_level is not None and self.battery_level < 20  # Less than 20%

class ProcessedInput:
    """Represents processed user input."""
    
    def __init__(
        self,
        raw_input: Any,
        modality_type: ModalityType,
        processed_text: str,
        confidence: float,
        timestamp: datetime.datetime,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.raw_input = raw_input
        self.modality_type = modality_type
        self.processed_text = processed_text
        self.confidence = confidence
        self.timestamp = timestamp
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the processed input to a dictionary."""
        return {
            "modality_type": self.modality_type.value,
            "processed_text": self.processed_text,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], raw_input: Any = None) -> 'ProcessedInput':
        """Create processed input from a dictionary."""
        return cls(
            raw_input=raw_input,
            modality_type=ModalityType(data["modality_type"]),
            processed_text=data["processed_text"],
            confidence=data["confidence"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )

class MultimodalContent:
    """Represents content in a specific modality."""
    
    def __init__(
        self,
        modality_type: ModalityType,
        content: Any,
        mime_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.modality_type = modality_type
        self.content = content
        self.mime_type = mime_type
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the multimodal content to a dictionary."""
        content_value = self.content
        
        # Handle binary content
        if isinstance(self.content, bytes):
            content_value = base64.b64encode(self.content).decode('utf-8')
            self.metadata["encoding"] = "base64"
        
        return {
            "modality_type": self.modality_type.value,
            "content": content_value,
            "mime_type": self.mime_type,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultimodalContent':
        """Create multimodal content from a dictionary."""
        content = data["content"]
        
        # Handle encoded content
        if data.get("metadata", {}).get("encoding") == "base64":
            content = base64.b64decode(content)
        
        return cls(
            modality_type=ModalityType(data["modality_type"]),
            content=content,
            mime_type=data.get("mime_type"),
            metadata=data.get("metadata", {})
        )

class MultimodalOutput:
    """Represents output across multiple modalities."""
    
    def __init__(
        self,
        primary_modality: ModalityType,
        contents: Dict[ModalityType, MultimodalContent],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.primary_modality = primary_modality
        self.contents = contents
        self.metadata = metadata or {}
    
    def add_content(self, content: MultimodalContent) -> None:
        """Add content for a modality."""
        self.contents[content.modality_type] = content
    
    def get_content(self, modality_type: ModalityType) -> Optional[MultimodalContent]:
        """Get content for a specific modality."""
        return self.contents.get(modality_type)
    
    def has_modality(self, modality_type: ModalityType) -> bool:
        """Check if output includes a specific modality."""
        return modality_type in self.contents
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the multimodal output to a dictionary."""
        return {
            "primary_modality": self.primary_modality.value,
            "contents": {
                modality.value: content.to_dict()
                for modality, content in self.contents.items()
            },
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultimodalOutput':
        """Create multimodal output from a dictionary."""
        contents = {
            ModalityType(modality): MultimodalContent.from_dict(content_data)
            for modality, content_data in data["contents"].items()
        }
        
        return cls(
            primary_modality=ModalityType(data["primary_modality"]),
            contents=contents,
            metadata=data.get("metadata", {})
        )

class TextInputHandler:
    """Handles text-based input processing."""
    
    def __init__(self):
        # Initialize text processing components
        pass
    
    def process(self, text: str) -> ProcessedInput:
        """Process text input."""
        # This is a placeholder for actual text processing logic
        # In a real implementation, this would include normalization, entity extraction, etc.
        
        return ProcessedInput(
            raw_input=text,
            modality_type=ModalityType.TEXT,
            processed_text=text,
            confidence=1.0,  # High confidence for text input
            timestamp=datetime.datetime.now(),
            metadata={}
        )

class VoiceInputHandler:
    """Handles voice-based input processing."""
    
    def __init__(self):
        # Initialize speech recognition components
        pass
    
    def process(self, audio_data: bytes, mime_type: str) -> ProcessedInput:
        """Process voice input."""
        # This is a placeholder for actual voice processing logic
        # In a real implementation, this would use speech recognition
        
        # Simulate speech recognition with a placeholder
        recognized_text = "This is a placeholder for speech recognition"
        
        return ProcessedInput(
            raw_input=audio_data,
            modality_type=ModalityType.VOICE,
            processed_text=recognized_text,
            confidence=0.8,  # Moderate confidence for voice recognition
            timestamp=datetime.datetime.now(),
            metadata={
                "mime_type": mime_type,
                "audio_duration_ms": 1000  # Placeholder duration
            }
        )

class VideoInputHandler:
    """Handles video-based input processing."""
    
    def __init__(self):
        # Initialize video processing components
        pass
    
    def process(self, video_data: bytes, mime_type: str) -> ProcessedInput:
        """Process video input."""
        # This is a placeholder for actual video processing logic
        # In a real implementation, this would use computer vision and possibly OCR
        
        # Simulate video analysis with a placeholder
        analyzed_text = "This is a placeholder for video analysis"
        
        return ProcessedInput(
            raw_input=video_data,
            modality_type=ModalityType.VIDEO,
            processed_text=analyzed_text,
            confidence=0.7,  # Lower confidence for video analysis
            timestamp=datetime.datetime.now(),
            metadata={
                "mime_type": mime_type,
                "video_duration_ms": 2000,  # Placeholder duration
                "frame_count": 60  # Placeholder frame count
            }
        )

class ImageInputHandler:
    """Handles image-based input processing."""
    
    def __init__(self):
        # Initialize image processing components
        pass
    
    def process(self, image_data: bytes, mime_type: str) -> ProcessedInput:
        """Process image input."""
        # This is a placeholder for actual image processing logic
        # In a real implementation, this would use computer vision and possibly OCR
        
        # Simulate image analysis with a placeholder
        analyzed_text = "This is a placeholder for image analysis"
        
        return ProcessedInput(
            raw_input=image_data,
            modality_type=ModalityType.IMAGE,
            processed_text=analyzed_text,
            confidence=0.75,  # Moderate confidence for image analysis
            timestamp=datetime.datetime.now(),
            metadata={
                "mime_type": mime_type,
                "image_dimensions": (800, 600)  # Placeholder dimensions
            }
        )

class InputProcessor:
    """Manages and normalizes inputs from different modalities."""
    
    def __init__(self):
        self.text_handler = TextInputHandler()
        self.voice_handler = VoiceInputHandler()
        self.video_handler = VideoInputHandler()
        self.image_handler = ImageInputHandler()
    
    def process_input(self, input_data: Any, modality_type: ModalityType) -> ProcessedInput:
        """Process input from any modality into a normalized format."""
        if modality_type == ModalityType.TEXT:
            if isinstance(input_data, str):
                return self.text_handler.process(input_data)
            else:
                raise ValueError("Text input must be a string")
        
        elif modality_type == ModalityType.VOICE:
            if isinstance(input_data, dict) and "data" in input_data and "mime_type" in input_data:
                return self.voice_handler.process(input_data["data"], input_data["mime_type"])
            else:
                raise ValueError("Voice input must be a dict with 'data' and 'mime_type' keys")
        
        elif modality_type == ModalityType.VIDEO:
            if isinstance(input_data, dict) and "data" in input_data and "mime_type" in input_data:
                return self.video_handler.process(input_data["data"], input_data["mime_type"])
            else:
                raise ValueError("Video input must be a dict with 'data' and 'mime_type' keys")
        
        elif modality_type == ModalityType.IMAGE:
            if isinstance(input_data, dict) and "data" in input_data and "mime_type" in input_data:
                return self.image_handler.process(input_data["data"], input_data["mime_type"])
            else:
                raise ValueError("Image input must be a dict with 'data' and 'mime_type' keys")
        
        elif modality_type == ModalityType.MULTIMODAL:
            # For multimodal input, we need to process each modality separately
            if not isinstance(input_data, dict):
                raise ValueError("Multimodal input must be a dict mapping modality types to data")
            
            # Process each modality
            processed_inputs = {}
            for modality_str, data in input_data.items():
                try:
                    modality = ModalityType(modality_str)
                    processed_inputs[modality] = self.process_input(data, modality)
                except ValueError:
                    # Skip invalid modality types
                    continue
            
            # Combine processed inputs
            # In a real implementation, this would use more sophisticated fusion techniques
            combined_text = " ".join(
                input.processed_text for input in processed_inputs.values()
            )
            
            # Use the highest confidence as the combined confidence
            combined_confidence = max(
                (input.confidence for input in processed_inputs.values()),
                default=0.5
            )
            
            return ProcessedInput(
                raw_input=input_data,
                modality_type=ModalityType.MULTIMODAL,
                processed_text=combined_text,
                confidence=combined_confidence,
                timestamp=datetime.datetime.now(),
                metadata={"processed_inputs": {
                    modality.value: input.to_dict()
                    for modality, input in processed_inputs.items()
                }}
            )
        
        else:
            raise ValueError(f"Unsupported modality type: {modality_type}")
    
    def detect_modality_switch(self, input_data: Any) -> Optional[ModalityType]:
        """Detect if user is attempting to switch modalities."""
        # This is a placeholder for actual modality switch detection logic
        # In a real implementation, this would analyze the input for indicators of modality switching
        
        if isinstance(input_data, str):
            # Check for text indicators of modality switching
            lower_input = input_data.lower()
            
            if any(phrase in lower_input for phrase in ["let me show you", "look at this", "see this"]):
                return ModalityType.IMAGE
            
            if any(phrase in lower_input for phrase in ["let me tell you", "listen to this"]):
                return ModalityType.VOICE
            
            if any(phrase in lower_input for phrase in ["watch this", "see this video"]):
                return ModalityType.VIDEO
        
        # No modality switch detected
        return None

class TextOutputFormatter:
    """Generates formatted text responses."""
    
    def __init__(self):
        # Initialize text formatting components
        pass
    
    def format(self, text: str, format_type: str = "plain") -> str:
        """Format text for output."""
        if format_type == "plain":
            return text
        
        elif format_type == "markdown":
            # This is a placeholder for actual markdown formatting
            # In a real implementation, this would apply proper markdown formatting
            return text
        
        elif format_type == "html":
            # This is a placeholder for actual HTML formatting
            # In a real implementation, this would apply proper HTML formatting
            return f"<div>{text}</div>"
        
        else:
            return text
    
    def truncate(self, text: str, max_length: int) -> str:
        """Truncate text to a maximum length."""
        if len(text) <= max_length:
            return text
        
        # Try to truncate at a sentence boundary
        sentences = text.split(". ")
        result = ""
        
        for sentence in sentences:
            if len(result) + len(sentence) + 2 <= max_length:  # +2 for ". "
                result += sentence + ". "
            else:
                break
        
        # If we couldn't fit even one sentence, truncate at max_length
        if not result:
            result = text[:max_length - 3] + "..."
        
        return result.strip()
    
    def simplify(self, text: str, complexity_level: int = 1) -> str:
        """Simplify text based on complexity level (1-5, where 1 is simplest)."""
        # This is a placeholder for actual text simplification logic
        # In a real implementation, this would use NLP techniques to simplify text
        
        # For now, just return the original text
        return text

class VoiceOutputSynthesizer:
    """Produces natural speech output."""
    
    def __init__(self):
        # Initialize speech synthesis components
        pass
    
    def synthesize(self, text: str, voice_id: str = "default", 
                 speed: float = 1.0) -> bytes:
        """Synthesize speech from text."""
        # This is a placeholder for actual speech synthesis
        # In a real implementation, this would use a TTS engine
        
        # Return a placeholder audio data
        return b"PLACEHOLDER_AUDIO_DATA"
    
    def get_audio_duration(self, text: str, speed: float = 1.0) -> int:
        """Estimate the duration of synthesized audio in milliseconds."""
        # This is a placeholder for actual duration estimation
        # In a real implementation, this would calculate based on text length and speed
        
        # Rough estimate: ~100ms per character at normal speed
        return int(len(text) * 100 / speed)
    
    def get_mime_type(self) -> str:
        """Get the MIME type of synthesized audio."""
        return "audio/wav"  # Placeholder MIME type

class VisualOutputComposer:
    """Creates visual aids and demonstrations."""
    
    def __init__(self):
        # Initialize visual composition components
        pass
    
    def create_image(self, description: str, width: int = 800, 
                   height: int = 600) -> bytes:
        """Create an image based on a description."""
        # This is a placeholder for actual image generation
        # In a real implementation, this would use image generation techniques
        
        # Return a placeholder image data
        return b"PLACEHOLDER_IMAGE_DATA"
    
    def create_diagram(self, elements: List[Dict[str, Any]], 
                     width: int = 800, height: int = 600) -> bytes:
        """Create a diagram based on elements."""
        # This is a placeholder for actual diagram generation
        # In a real implementation, this would use diagram generation techniques
        
        # Return a placeholder diagram data
        return b"PLACEHOLDER_DIAGRAM_DATA"
    
    def create_animation(self, frames: List[Dict[str, Any]], 
                       width: int = 800, height: int = 600) -> bytes:
        """Create an animation based on frames."""
        # This is a placeholder for actual animation generation
        # In a real implementation, this would use animation generation techniques
        
        # Return a placeholder animation data
        return b"PLACEHOLDER_ANIMATION_DATA"
    
    def get_mime_type(self, output_type: str) -> str:
        """Get the MIME type of visual output."""
        mime_types = {
            "image": "image/png",
            "diagram": "image/svg+xml",
            "animation": "image/gif"
        }
        
        return mime_types.get(output_type, "application/octet-stream")

class OutputGenerator:
    """Creates appropriate responses across modalities."""
    
    def __init__(self):
        self.text_formatter = TextOutputFormatter()
        self.voice_synthesizer = VoiceOutputSynthesizer()
        self.visual_composer = VisualOutputComposer()
    
    def generate_output(self, response_data: Dict[str, Any], 
                      preferred_modalities: List[ModalityType]) -> MultimodalOutput:
        """Generate output across specified modalities."""
        # Ensure text is always included
        if ModalityType.TEXT not in preferred_modalities:
            preferred_modalities.append(ModalityType.TEXT)
        
        # Determine primary modality (first in the list)
        primary_modality = preferred_modalities[0]
        
        # Create output contents
        contents = {}
        
        # Always generate text output
        text_content = self.text_formatter.format(
            response_data["text"],
            response_data.get("text_format", "plain")
        )
        contents[ModalityType.TEXT] = MultimodalContent(
            modality_type=ModalityType.TEXT,
            content=text_content,
            mime_type="text/plain",
            metadata={"format": response_data.get("text_format", "plain")}
        )
        
        # Generate voice output if requested
        if ModalityType.VOICE in preferred_modalities and "text" in response_data:
            voice_id = response_data.get("voice_id", "default")
            speed = response_data.get("voice_speed", 1.0)
            
            audio_data = self.voice_synthesizer.synthesize(
                response_data["text"],
                voice_id,
                speed
            )
            
            contents[ModalityType.VOICE] = MultimodalContent(
                modality_type=ModalityType.VOICE,
                content=audio_data,
                mime_type=self.voice_synthesizer.get_mime_type(),
                metadata={
                    "voice_id": voice_id,
                    "speed": speed,
                    "duration_ms": self.voice_synthesizer.get_audio_duration(
                        response_data["text"],
                        speed
                    )
                }
            )
        
        # Generate image output if requested
        if ModalityType.IMAGE in preferred_modalities and "image_description" in response_data:
            width = response_data.get("image_width", 800)
            height = response_data.get("image_height", 600)
            
            image_data = self.visual_composer.create_image(
                response_data["image_description"],
                width,
                height
            )
            
            contents[ModalityType.IMAGE] = MultimodalContent(
                modality_type=ModalityType.IMAGE,
                content=image_data,
                mime_type=self.visual_composer.get_mime_type("image"),
                metadata={
                    "width": width,
                    "height": height,
                    "description": response_data["image_description"]
                }
            )
        
        # Create the multimodal output
        return MultimodalOutput(
            primary_modality=primary_modality,
            contents=contents,
            metadata=response_data.get("metadata", {})
        )
    
    def adapt_output_for_constraints(self, output: MultimodalOutput, 
                                   constraints: ResourceConstraints) -> MultimodalOutput:
        """Adapt output based on bandwidth, device capabilities, etc."""
        adapted_output = MultimodalOutput(
            primary_modality=output.primary_modality,
            contents={},
            metadata=output.metadata.copy()
        )
        
        # Always include text content
        text_content = output.get_content(ModalityType.TEXT)
        if text_content:
            # If low bandwidth or memory, simplify and truncate text
            if constraints.is_low_bandwidth() or constraints.is_low_memory():
                simplified_text = self.text_formatter.simplify(text_content.content)
                truncated_text = self.text_formatter.truncate(simplified_text, 1000)
                
                adapted_output.add_content(MultimodalContent(
                    modality_type=ModalityType.TEXT,
                    content=truncated_text,
                    mime_type=text_content.mime_type,
                    metadata=text_content.metadata.copy()
                ))
            else:
                adapted_output.add_content(text_content)
        
        # Include voice content if supported and not constrained
        voice_content = output.get_content(ModalityType.VOICE)
        if voice_content and constraints.supports_audio:
            # Skip voice if low bandwidth, high latency, or low battery
            if not (constraints.is_low_bandwidth() or 
                   constraints.is_high_latency() or 
                   constraints.is_low_battery()):
                adapted_output.add_content(voice_content)
        
        # Include image content if supported and not constrained
        image_content = output.get_content(ModalityType.IMAGE)
        if image_content and constraints.supports_images:
            # Skip images if low bandwidth or low battery
            if not (constraints.is_low_bandwidth() or constraints.is_low_battery()):
                adapted_output.add_content(image_content)
        
        # Adjust primary modality if needed
        if not adapted_output.has_modality(output.primary_modality):
            # Fall back to text if original primary modality is not available
            adapted_output.primary_modality = ModalityType.TEXT
        
        return adapted_output

class ContextualModalitySelector:
    """Chooses optimal modality based on context."""
    
    def __init__(self):
        # Initialize modality selection components
        pass
    
    def select_modalities(self, context: Dict[str, Any], 
                        constraints: ResourceConstraints) -> List[ModalityType]:
        """Select appropriate modalities based on context and constraints."""
        selected_modalities = [ModalityType.TEXT]  # Always include text
        
        # Check if user has a preferred modality
        user_preference = context.get("preferred_modality")
        if user_preference and user_preference != ModalityType.TEXT.value:
            try:
                preferred_modality = ModalityType(user_preference)
                selected_modalities.insert(0, preferred_modality)
            except ValueError:
                pass
        
        # Check content type
        content_type = context.get("content_type", "")
        
        if "visual" in content_type and constraints.supports_images:
            if ModalityType.IMAGE not in selected_modalities:
                selected_modalities.append(ModalityType.IMAGE)
        
        if "audio" in content_type and constraints.supports_audio:
            if ModalityType.VOICE not in selected_modalities:
                selected_modalities.append(ModalityType.VOICE)
        
        # Check resource constraints
        if constraints.is_low_bandwidth() or constraints.is_low_battery():
            # Remove all but text if resources are constrained
            return [ModalityType.TEXT]
        
        return selected_modalities

class MultimodalFusionEngine:
    """Combines information from multiple modalities."""
    
    def __init__(self):
        # Initialize fusion components
        pass
    
    def fuse_inputs(self, inputs: Dict[ModalityType, ProcessedInput]) -> ProcessedInput:
        """Combine information from multiple input modalities."""
        # This is a placeholder for actual multimodal fusion logic
        # In a real implementation, this would use more sophisticated fusion techniques
        
        # Start with text if available
        text_input = inputs.get(ModalityType.TEXT)
        if text_input:
            fused_text = text_input.processed_text
            confidence = text_input.confidence
        else:
            fused_text = ""
            confidence = 0.0
        
        # Add information from other modalities
        for modality, input in inputs.items():
            if modality != ModalityType.TEXT:
                # In a real implementation, this would use more sophisticated fusion
                if fused_text:
                    fused_text += " " + input.processed_text
                else:
                    fused_text = input.processed_text
                
                # Update confidence (simple average for demonstration)
                confidence = (confidence + input.confidence) / 2
        
        return ProcessedInput(
            raw_input=inputs,
            modality_type=ModalityType.MULTIMODAL,
            processed_text=fused_text,
            confidence=confidence,
            timestamp=datetime.datetime.now(),
            metadata={"source_modalities": [m.value for m in inputs.keys()]}
        )

class FallbackManager:
    """Handles degradation paths when a modality is unavailable."""
    
    def __init__(self):
        # Initialize fallback components
        pass
    
    def get_fallback_modality(self, original_modality: ModalityType, 
                            constraints: ResourceConstraints) -> ModalityType:
        """Get a fallback modality when the original is unavailable."""
        # Text is always available
        if original_modality == ModalityType.TEXT:
            return ModalityType.TEXT
        
        # For voice, fall back to text
        if original_modality == ModalityType.VOICE:
            return ModalityType.TEXT
        
        # For image or video, check if text descriptions are available
        if original_modality in [ModalityType.IMAGE, ModalityType.VIDEO]:
            return ModalityType.TEXT
        
        # Default fallback is text
        return ModalityType.TEXT
    
    def create_fallback_content(self, original_content: MultimodalContent, 
                              fallback_modality: ModalityType) -> MultimodalContent:
        """Create fallback content for a different modality."""
        # This is a placeholder for actual fallback content creation
        # In a real implementation, this would generate appropriate fallback content
        
        if fallback_modality == ModalityType.TEXT:
            # Create text description of non-text content
            if original_content.modality_type == ModalityType.IMAGE:
                description = original_content.metadata.get("description", "Image content")
                return MultimodalContent(
                    modality_type=ModalityType.TEXT,
                    content=f"[Image description: {description}]",
                    mime_type="text/plain",
                    metadata={"original_modality": original_content.modality_type.value}
                )
            
            elif original_content.modality_type == ModalityType.VOICE:
                return MultimodalContent(
                    modality_type=ModalityType.TEXT,
                    content="[Audio content not available]",
                    mime_type="text/plain",
                    metadata={"original_modality": original_content.modality_type.value}
                )
            
            elif original_content.modality_type == ModalityType.VIDEO:
                return MultimodalContent(
                    modality_type=ModalityType.TEXT,
                    content="[Video content not available]",
                    mime_type="text/plain",
                    metadata={"original_modality": original_content.modality_type.value}
                )
        
        # Default fallback is empty text
        return MultimodalContent(
            modality_type=ModalityType.TEXT,
            content="[Content not available]",
            mime_type="text/plain",
            metadata={"original_modality": original_content.modality_type.value}
        )

class ModalityCoordinator:
    """Orchestrates the use of different interaction modes."""
    
    def __init__(self):
        self.modality_selector = ContextualModalitySelector()
        self.fusion_engine = MultimodalFusionEngine()
        self.fallback_manager = FallbackManager()
    
    def select_output_modalities(self, context: Dict[str, Any], 
                               constraints: ResourceConstraints) -> List[ModalityType]:
        """Select appropriate output modalities based on context and constraints."""
        return self.modality_selector.select_modalities(context, constraints)
    
    def fuse_multimodal_inputs(self, inputs: Dict[ModalityType, ProcessedInput]) -> ProcessedInput:
        """Combine information from multiple input modalities."""
        return self.fusion_engine.fuse_inputs(inputs)
    
    def handle_modality_unavailability(self, output: MultimodalOutput, 
                                     constraints: ResourceConstraints) -> MultimodalOutput:
        """Handle cases where preferred modalities are unavailable."""
        adapted_output = MultimodalOutput(
            primary_modality=output.primary_modality,
            contents={},
            metadata=output.metadata.copy()
        )
        
        # Check each modality in the original output
        for modality, content in output.contents.items():
            # Check if modality is available based on constraints
            if self._is_modality_available(modality, constraints):
                # If available, keep the original content
                adapted_output.add_content(content)
            else:
                # If unavailable, get fallback modality
                fallback_modality = self.fallback_manager.get_fallback_modality(
                    modality, constraints
                )
                
                # Create fallback content
                fallback_content = self.fallback_manager.create_fallback_content(
                    content, fallback_modality
                )
                
                # Add fallback content
                adapted_output.add_content(fallback_content)
        
        # Update primary modality if needed
        if not adapted_output.has_modality(output.primary_modality):
            # Find the first available modality
            for modality in output.contents.keys():
                fallback_modality = self.fallback_manager.get_fallback_modality(
                    modality, constraints
                )
                if adapted_output.has_modality(fallback_modality):
                    adapted_output.primary_modality = fallback_modality
                    break
        
        return adapted_output
    
    def _is_modality_available(self, modality: ModalityType, 
                             constraints: ResourceConstraints) -> bool:
        """Check if a modality is available based on constraints."""
        if modality == ModalityType.TEXT:
            # Text is always available
            return True
        
        elif modality == ModalityType.VOICE:
            return (constraints.supports_audio and 
                   not constraints.is_low_bandwidth() and 
                   not constraints.is_low_battery())
        
        elif modality == ModalityType.IMAGE:
            return (constraints.supports_images and 
                   not constraints.is_low_bandwidth() and 
                   not constraints.is_low_battery())
        
        elif modality == ModalityType.VIDEO:
            return (constraints.supports_video and 
                   not constraints.is_low_bandwidth() and 
                   not constraints.is_low_battery() and 
                   not constraints.is_low_memory())
        
        return False

class MultimodalInteractionLayer:
    """Main class that coordinates multimodal interaction components."""
    
    def __init__(self):
        self.input_processor = InputProcessor()
        self.output_generator = OutputGenerator()
        self.modality_coordinator = ModalityCoordinator()
    
    def process_input(self, input_data: Any, modality_type: ModalityType) -> ProcessedInput:
        """Process user input from any modality."""
        return self.input_processor.process_input(input_data, modality_type)
    
    def detect_modality_switch(self, input_data: Any) -> Optional[ModalityType]:
        """Detect if user is attempting to switch modalities."""
        return self.input_processor.detect_modality_switch(input_data)
    
    def generate_output(self, response_data: Dict[str, Any], 
                      context: Dict[str, Any], 
                      constraints: ResourceConstraints) -> MultimodalOutput:
        """Generate appropriate multimodal output based on context and constraints."""
        # Select appropriate modalities
        selected_modalities = self.modality_coordinator.select_output_modalities(
            context, constraints
        )
        
        # Generate output across selected modalities
        output = self.output_generator.generate_output(response_data, selected_modalities)
        
        # Adapt output for constraints
        adapted_output = self.output_generator.adapt_output_for_constraints(output, constraints)
        
        # Handle modality unavailability
        final_output = self.modality_coordinator.handle_modality_unavailability(
            adapted_output, constraints
        )
        
        return final_output
    
    def fuse_multimodal_inputs(self, inputs: Dict[ModalityType, ProcessedInput]) -> ProcessedInput:
        """Combine information from multiple input modalities."""
        return self.modality_coordinator.fuse_multimodal_inputs(inputs)
    
    def estimate_resource_requirements(self, output: MultimodalOutput) -> Dict[str, Any]:
        """Estimate resource requirements for a multimodal output."""
        requirements = {
            "bandwidth_required": 0.0,  # in Mbps
            "storage_required": 0.0,    # in MB
            "processing_required": 0.0,  # arbitrary units
            "modalities": []
        }
        
        # Add modalities
        requirements["modalities"] = [m.value for m in output.contents.keys()]
        
        # Estimate bandwidth requirements
        for modality, content in output.contents.items():
            if modality == ModalityType.TEXT:
                # Text requires minimal bandwidth
                text_size = len(content.content) if isinstance(content.content, str) else 0
                requirements["bandwidth_required"] += text_size * 8 / 1000000  # Convert bytes to Mbps
                requirements["storage_required"] += text_size / 1000000  # Convert bytes to MB
            
            elif modality == ModalityType.VOICE:
                # Voice requires moderate bandwidth
                # Assume 16kbps for voice
                duration_ms = content.metadata.get("duration_ms", 0)
                requirements["bandwidth_required"] += 16 * (duration_ms / 1000)
                requirements["storage_required"] += 16 * (duration_ms / 8000)  # Convert bits to MB
            
            elif modality == ModalityType.IMAGE:
                # Images require higher bandwidth
                # Assume 100KB for a typical image
                requirements["bandwidth_required"] += 0.8  # 0.8 Mbps
                requirements["storage_required"] += 0.1  # 0.1 MB
            
            elif modality == ModalityType.VIDEO:
                # Video requires highest bandwidth
                # Assume 1Mbps for video
                duration_ms = content.metadata.get("duration_ms", 0)
                requirements["bandwidth_required"] += 1.0 * (duration_ms / 1000)
                requirements["storage_required"] += 0.125 * (duration_ms / 1000)  # Convert Mbps to MB
        
        # Estimate processing requirements (arbitrary units)
        requirements["processing_required"] = len(output.contents) * 10
        
        return requirements
