"""
Audio Integration Module for Dr. TARDIS Gemini Live API Integration

This module integrates the audio processing, voice activity detection, and speech synthesis
components for the Dr. TARDIS Gemini Live API integration, providing a unified interface
for voice-based interactions.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import logging
import numpy as np
import os
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

from .audio_processor import AudioProcessor, AudioState
from .voice_activity_detector import VoiceActivityDetector, VoiceActivityState, InterruptionDetector
from .speech_synthesizer import SpeechSynthesizer, SpeechSynthesisState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AudioIntegrationState(Enum):
    """Enum for different states of the audio integration."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"

class AudioIntegration:
    """
    Integrates audio processing, voice activity detection, and speech synthesis.
    
    This class provides a unified interface for voice-based interactions,
    coordinating the various audio components to enable natural conversations
    with Dr. TARDIS.
    
    Attributes:
        audio_processor (AudioProcessor): Audio capture and playback component
        vad (VoiceActivityDetector): Voice activity detection component
        interruption_detector (InterruptionDetector): Interruption detection component
        speech_synthesizer (SpeechSynthesizer): Speech synthesis component
        state (AudioIntegrationState): Current state of the audio integration
        logger (logging.Logger): Logger for the audio integration
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        Initialize the Audio Integration.
        
        Args:
            sample_rate: Sample rate for audio processing in Hz
            channels: Number of audio channels (1 for mono, 2 for stereo)
        """
        self.logger = logging.getLogger("AudioIntegration")
        self.logger.info(f"Initializing AudioIntegration with sample_rate={sample_rate}, channels={channels}")
        
        # Initialize components
        self.audio_processor = AudioProcessor(sample_rate=sample_rate, channels=channels)
        self.vad = VoiceActivityDetector()
        self.interruption_detector = InterruptionDetector(vad=self.vad)
        self.speech_synthesizer = SpeechSynthesizer(sample_rate=sample_rate)
        
        self.state = AudioIntegrationState.IDLE
        
        # Configuration
        self.auto_listen_after_speaking = True
        self.enable_interruptions = True
        
        # Internal state
        self._current_conversation_id = None
        self._listening_task = None
        self._speaking_task = None
        
        # Callbacks
        self.on_speech_detected = None
        self.on_speech_captured = None
        self.on_interruption = None
        self.on_speaking_started = None
        self.on_speaking_finished = None
        self.on_error = None
        
        # Register component callbacks
        self._register_component_callbacks()
        
        self.logger.info("AudioIntegration initialized")
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        self.close()
    
    def close(self):
        """Close the audio integration and release resources."""
        if hasattr(self, 'audio_processor'):
            self.audio_processor.close()
        
        self.logger.info("AudioIntegration closed and resources released")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_speech_detected', 'on_speech_captured', 'on_interruption',
                 'on_speaking_started', 'on_speaking_finished', 'on_error')
            callback: Function to call when the event occurs
        """
        if event_type == "on_speech_detected":
            self.on_speech_detected = callback
        elif event_type == "on_speech_captured":
            self.on_speech_captured = callback
        elif event_type == "on_interruption":
            self.on_interruption = callback
        elif event_type == "on_speaking_started":
            self.on_speaking_started = callback
        elif event_type == "on_speaking_finished":
            self.on_speaking_finished = callback
        elif event_type == "on_error":
            self.on_error = callback
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def configure(self, config: Dict[str, Any]):
        """
        Configure the audio integration.
        
        Args:
            config: Configuration dictionary with the following optional keys:
                - auto_listen_after_speaking (bool): Whether to automatically start listening after speaking
                - enable_interruptions (bool): Whether to enable interruption detection
                - vad_energy_threshold (float): Energy threshold for voice activity detection
                - vad_speech_timeout (float): Time in seconds of silence to consider speech ended
                - vad_speech_start_threshold (float): Minimum duration in seconds to consider speech started
                - interruption_threshold (float): Time in seconds of user speech to consider an interruption
                - tts_service (str): TTS service to use ('google', 'elevenlabs', 'local')
                - tts_voice_id (str): Voice ID to use for speech synthesis
        """
        # Audio integration configuration
        if "auto_listen_after_speaking" in config:
            self.auto_listen_after_speaking = config["auto_listen_after_speaking"]
        
        if "enable_interruptions" in config:
            self.enable_interruptions = config["enable_interruptions"]
        
        # VAD configuration
        vad_config = {}
        if "vad_energy_threshold" in config:
            vad_config["energy_threshold"] = config["vad_energy_threshold"]
        
        if "vad_speech_timeout" in config:
            vad_config["speech_timeout"] = config["vad_speech_timeout"]
        
        if "vad_speech_start_threshold" in config:
            vad_config["speech_start_threshold"] = config["vad_speech_start_threshold"]
        
        if vad_config:
            self.vad.configure(**vad_config)
        
        # Interruption detector configuration
        if "interruption_threshold" in config:
            self.interruption_detector.interruption_threshold = config["interruption_threshold"]
        
        # TTS configuration
        if "tts_service" in config:
            self.speech_synthesizer.set_tts_service(config["tts_service"])
        
        if "tts_voice_id" in config:
            self.speech_synthesizer.set_voice(config["tts_voice_id"])
        
        self.logger.info(f"AudioIntegration configured: {config}")
    
    def set_api_key(self, service: str, api_key: str):
        """
        Set an API key for a service.
        
        Args:
            service: Service name ('google', 'elevenlabs')
            api_key: API key
        """
        self.speech_synthesizer.set_api_key(service, api_key)
    
    def set_conversation_id(self, conversation_id: str):
        """
        Set the current conversation ID.
        
        Args:
            conversation_id: Conversation ID
        """
        self._current_conversation_id = conversation_id
    
    async def start_listening(self, max_duration: Optional[float] = None):
        """
        Start listening for user speech.
        
        Args:
            max_duration: Maximum duration to listen in seconds (None for no limit)
        """
        if self.state == AudioIntegrationState.LISTENING:
            self.logger.warning("Already listening")
            return
        
        if self._listening_task and not self._listening_task.done():
            self.logger.warning("Listening task already running")
            return
        
        self.state = AudioIntegrationState.LISTENING
        self.logger.info(f"Starting to listen (max_duration={max_duration}s)")
        
        # Create and start the listening task
        self._listening_task = asyncio.create_task(self._listen_task(max_duration))
    
    async def stop_listening(self):
        """Stop listening for user speech."""
        if self.state != AudioIntegrationState.LISTENING:
            self.logger.warning(f"Not listening (current state: {self.state.name})")
            return
        
        self.logger.info("Stopping listening")
        
        # Stop the audio processor
        await self.audio_processor.stop_recording()
        
        # Wait for the listening task to complete
        if self._listening_task and not self._listening_task.done():
            try:
                await asyncio.wait_for(asyncio.shield(self._listening_task), timeout=2.0)
            except asyncio.TimeoutError:
                self.logger.warning("Timeout waiting for listening task to complete")
    
    async def speak(self, text: str) -> bool:
        """
        Synthesize and speak text.
        
        Args:
            text: Text to speak
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.state == AudioIntegrationState.SPEAKING:
            self.logger.warning("Already speaking")
            return False
        
        if self._speaking_task and not self._speaking_task.done():
            self.logger.warning("Speaking task already running")
            return False
        
        # Stop listening if currently listening
        if self.state == AudioIntegrationState.LISTENING:
            await self.stop_listening()
        
        self.state = AudioIntegrationState.SPEAKING
        self.logger.info(f"Starting to speak: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # Notify interruption detector that system is speaking
        self.interruption_detector.set_system_speaking(True)
        
        # Create and start the speaking task
        self._speaking_task = asyncio.create_task(self._speak_task(text))
        
        # Wait for the speaking task to complete
        try:
            result = await self._speaking_task
            return result
        except Exception as e:
            self.logger.error(f"Error in speaking task: {e}")
            return False
    
    async def stop_speaking(self):
        """Stop current speech synthesis and playback."""
        if self.state != AudioIntegrationState.SPEAKING:
            self.logger.warning(f"Not speaking (current state: {self.state.name})")
            return
        
        self.logger.info("Stopping speaking")
        
        # TODO: Implement stopping speech playback
        # This would require modifications to the speech synthesizer to support stopping playback
        
        # Notify interruption detector that system is no longer speaking
        self.interruption_detector.set_system_speaking(False)
    
    async def save_speech_to_file(self, text: str, file_path: str) -> bool:
        """
        Synthesize speech and save it to a file.
        
        Args:
            text: Text to synthesize
            file_path: Path to save the audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        return await self.speech_synthesizer.save_to_file(text, file_path)
    
    async def reset(self):
        """Reset the audio integration state."""
        # Stop any ongoing activities
        if self.state == AudioIntegrationState.LISTENING:
            await self.stop_listening()
        
        if self.state == AudioIntegrationState.SPEAKING:
            await self.stop_speaking()
        
        # Reset components
        await self.vad.reset()
        await self.interruption_detector.reset()
        
        self.state = AudioIntegrationState.IDLE
        self.logger.info("AudioIntegration reset")
    
    def _register_component_callbacks(self):
        """Register callbacks for the audio components."""
        # Audio processor callbacks
        self.audio_processor.register_callback("on_audio_data", self._on_audio_data)
        self.audio_processor.register_callback("on_recording_complete", self._on_recording_complete)
        self.audio_processor.register_callback("on_error", self._on_audio_processor_error)
        
        # VAD callbacks
        self.vad.register_callback("on_speech_start", self._on_speech_start)
        self.vad.register_callback("on_speech_end", self._on_speech_end)
        
        # Interruption detector callbacks
        self.interruption_detector.register_interruption_callback(self._on_interruption_detected)
        
        # Speech synthesizer callbacks
        self.speech_synthesizer.register_callback("on_playback_start", self._on_playback_start)
        self.speech_synthesizer.register_callback("on_playback_complete", self._on_playback_complete)
        self.speech_synthesizer.register_callback("on_error", self._on_speech_synthesizer_error)
    
    async def _listen_task(self, max_duration: Optional[float]):
        """
        Task for listening to user speech.
        
        Args:
            max_duration: Maximum duration to listen in seconds
        """
        try:
            # Reset VAD and interruption detector
            await self.vad.reset()
            await self.interruption_detector.reset()
            
            # Start recording
            await self.audio_processor.start_recording(max_duration=max_duration)
            
            # State will be updated by callbacks
            
        except Exception as e:
            self.state = AudioIntegrationState.ERROR
            self.logger.error(f"Error in listening task: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
    
    async def _speak_task(self, text: str) -> bool:
        """
        Task for synthesizing and speaking text.
        
        Args:
            text: Text to speak
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Call the speaking started callback if registered
            if self.on_speaking_started:
                try:
                    await self.on_speaking_started(text)
                except Exception as e:
                    self.logger.error(f"Error in speaking started callback: {e}")
            
            # Synthesize and play speech
            result = await self.speech_synthesizer.synthesize_and_play(text)
            
            # State will be updated by callbacks
            
            return result
            
        except Exception as e:
            self.state = AudioIntegrationState.ERROR
            self.logger.error(f"Error in speaking task: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def _on_audio_data(self, audio_data: np.ndarray):
        """
        Handle audio data from the audio processor.
        
        Args:
            audio_data: Audio data as numpy array
        """
        if self.enable_interruptions and self.state == AudioIntegrationState.SPEAKING:
            # Process audio for interruption detection
            await self.interruption_detector.process_audio_frame(audio_data)
        elif self.state == AudioIntegrationState.LISTENING:
            # Process audio for VAD
            await self.vad.process_audio_frame(audio_data)
    
    async def _on_recording_complete(self, audio_data: bytes):
        """
        Handle recording completion from the audio processor.
        
        Args:
            audio_data: Recorded audio data
        """
        self.state = AudioIntegrationState.PROCESSING
        self.logger.info(f"Recording complete: {len(audio_data)} bytes")
        
        # Call the speech captured callback if registered
        if self.on_speech_captured:
            try:
                await self.on_speech_captured(self._current_conversation_id, audio_data)
            except Exception as e:
                self.logger.error(f"Error in speech captured callback: {e}")
        
        self.state = AudioIntegrationState.IDLE
    
    async def _on_audio_processor_error(self, error: str):
        """
        Handle errors from the audio processor.
        
        Args:
            error: Error message
        """
        self.state = AudioIntegrationState.ERROR
        self.logger.error(f"Audio processor error: {error}")
        
        # Call the error callback if registered
        if self.on_error:
            try:
                await self.on_error(error)
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}")
    
    async def _on_speech_start(self):
        """Handle speech start events from VAD."""
        self.logger.info("Speech detected")
        
        # Call the speech detected callback if registered
        if self.on_speech_detected:
            try:
                await self.on_speech_detected(self._current_conversation_id)
            except Exception as e:
                self.logger.error(f"Error in speech detected callback: {e}")
    
    async def _on_speech_end(self):
        """Handle speech end events from VAD."""
        self.logger.info("Speech ended")
    
    async def _on_interruption_detected(self):
        """Handle interruption detection events."""
        self.logger.info("Interruption detected")
        
        # Stop speaking
        await self.stop_speaking()
        
        # Call the interruption callback if registered
        if self.on_interruption:
            try:
                await self.on_interruption(self._current_conversation_id)
            except Exception as e:
                self.logger.error(f"Error in interruption callback: {e}")
    
    async def _on_playback_start(self):
        """Handle playback start events from speech synthesizer."""
        self.logger.info("Speech playback started")
    
    async def _on_playback_complete(self):
        """Handle playback completion events from speech synthesizer."""
        self.logger.info("Speech playback complete")
        
        # Update state
        self.state = AudioIntegrationState.IDLE
        
        # Notify interruption detector that system is no longer speaking
        self.interruption_detector.set_system_speaking(False)
        
        # Call the speaking finished callback if registered
        if self.on_speaking_finished:
            try:
                await self.on_speaking_finished(self._current_conversation_id)
            except Exception as e:
                self.logger.error(f"Error in speaking finished callback: {e}")
        
        # Start listening again if configured to do so
        if self.auto_listen_after_speaking:
            await self.start_listening()
    
    async def _on_speech_synthesizer_error(self, error: str):
        """
        Handle errors from the speech synthesizer.
        
        Args:
            error: Error message
        """
        self.state = AudioIntegrationState.ERROR
        self.logger.error(f"Speech synthesizer error: {error}")
        
        # Notify interruption detector that system is no longer speaking
        self.interruption_detector.set_system_speaking(False)
        
        # Call the error callback if registered
        if self.on_error:
            try:
                await self.on_error(error)
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}")

# Example usage
async def example_usage():
    # Create an audio integration
    integration = AudioIntegration(sample_rate=16000, channels=1)
    
    # Configure the integration
    integration.configure({
        "auto_listen_after_speaking": True,
        "enable_interruptions": True,
        "vad_energy_threshold": 0.01,
        "vad_speech_timeout": 0.8,
        "vad_speech_start_threshold": 0.2,
        "interruption_threshold": 0.5,
        "tts_service": "local"
    })
    
    # Set conversation ID
    integration.set_conversation_id("test-conversation")
    
    # Define callbacks
    async def on_speech_detected(conversation_id):
        print(f"Speech detected in conversation {conversation_id}")
    
    async def on_speech_captured(conversation_id, audio_data):
        print(f"Speech captured in conversation {conversation_id}: {len(audio_data)} bytes")
    
    async def on_interruption(conversation_id):
        print(f"Interruption detected in conversation {conversation_id}")
    
    async def on_speaking_started(text):
        print(f"Speaking started: '{text}'")
    
    async def on_speaking_finished(conversation_id):
        print(f"Speaking finished in conversation {conversation_id}")
    
    async def on_error(error):
        print(f"Error: {error}")
    
    # Register callbacks
    integration.register_callback("on_speech_detected", on_speech_detected)
    integration.register_callback("on_speech_captured", on_speech_captured)
    integration.register_callback("on_interruption", on_interruption)
    integration.register_callback("on_speaking_started", on_speaking_started)
    integration.register_callback("on_speaking_finished", on_speaking_finished)
    integration.register_callback("on_error", on_error)
    
    try:
        # Speak a greeting
        print("Speaking greeting...")
        await integration.speak("Hello, I am Dr. TARDIS. How can I assist you today?")
        
        # Wait for auto-listening and user response
        print("Waiting for user response...")
        await asyncio.sleep(10)
        
        # Speak a response
        print("Speaking response...")
        await integration.speak("I understand. Let me help you with that.")
        
        # Wait for auto-listening and user response
        print("Waiting for user response...")
        await asyncio.sleep(10)
        
    finally:
        # Clean up
        integration.close()

if __name__ == "__main__":
    asyncio.run(example_usage())
