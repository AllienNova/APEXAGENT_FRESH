"""
Speech Synthesis Module for Dr. TARDIS Gemini Live API Integration

This module handles text-to-speech conversion and audio output for the Dr. TARDIS
Gemini Live API integration, enabling natural voice responses.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import logging
import numpy as np
import os
import tempfile
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

import aiohttp
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SpeechSynthesisState(Enum):
    """Enum for different states of the speech synthesizer."""
    IDLE = "idle"
    SYNTHESIZING = "synthesizing"
    PLAYING = "playing"
    ERROR = "error"

class SpeechSynthesizer:
    """
    Handles text-to-speech conversion and audio output for voice responses.
    
    This class provides functionality for converting text to speech using
    various TTS services and playing the resulting audio for Dr. TARDIS
    voice responses.
    
    Attributes:
        tts_service (str): Name of the TTS service to use
        voice_id (str): ID of the voice to use
        sample_rate (int): Sample rate for audio output in Hz
        state (SpeechSynthesisState): Current state of the speech synthesizer
        logger (logging.Logger): Logger for the speech synthesizer
    """
    
    def __init__(self, tts_service: str = "google", voice_id: str = "en-US-Neural2-C",
                 sample_rate: int = 24000):
        """
        Initialize the Speech Synthesizer.
        
        Args:
            tts_service: Name of the TTS service to use ('google', 'elevenlabs', 'local')
            voice_id: ID of the voice to use
            sample_rate: Sample rate for audio output in Hz
        """
        self.tts_service = tts_service
        self.voice_id = voice_id
        self.sample_rate = sample_rate
        self.state = SpeechSynthesisState.IDLE
        self.logger = logging.getLogger("SpeechSynthesizer")
        
        # API keys (to be set by the user)
        self.api_keys = {}
        
        # TTS service configurations
        self.service_configs = {
            "google": {
                "api_url": "https://texttospeech.googleapis.com/v1/text:synthesize",
                "voices": {
                    "en-US-Neural2-C": {"gender": "MALE", "language_code": "en-US"},
                    "en-US-Neural2-F": {"gender": "FEMALE", "language_code": "en-US"},
                    "en-US-Polyglot-1": {"gender": "MALE", "language_code": "en-US"},
                    "en-GB-Neural2-B": {"gender": "MALE", "language_code": "en-GB"},
                    "en-GB-Neural2-A": {"gender": "FEMALE", "language_code": "en-GB"}
                }
            },
            "elevenlabs": {
                "api_url": "https://api.elevenlabs.io/v1/text-to-speech",
                "voices": {
                    "Adam": {"voice_id": "pNInz6obpgDQGcFmaJgB"},
                    "Antoni": {"voice_id": "ErXwobaYiN019PkySvjV"},
                    "Bella": {"voice_id": "EXAVITQu4vr4xnSDxMaL"},
                    "Elli": {"voice_id": "MF3mGyEYCl7XYWbV9V6O"},
                    "Josh": {"voice_id": "TxGEqnHWrfWFTfGW9XjX"}
                }
            },
            "local": {
                "engine": "pyttsx3",
                "voices": {
                    "default": {"id": None},
                    "male": {"id": "male"},
                    "female": {"id": "female"}
                }
            }
        }
        
        # Playback state
        self._current_audio = None
        self._playback_event = asyncio.Event()
        
        # Callbacks
        self.on_synthesis_complete = None
        self.on_playback_start = None
        self.on_playback_complete = None
        self.on_error = None
        
        self.logger.info(f"SpeechSynthesizer initialized with service={tts_service}, voice={voice_id}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_synthesis_complete', 'on_playback_start', 'on_playback_complete', 'on_error')
            callback: Function to call when the event occurs
        """
        if event_type == "on_synthesis_complete":
            self.on_synthesis_complete = callback
        elif event_type == "on_playback_start":
            self.on_playback_start = callback
        elif event_type == "on_playback_complete":
            self.on_playback_complete = callback
        elif event_type == "on_error":
            self.on_error = callback
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def set_api_key(self, service: str, api_key: str):
        """
        Set the API key for a TTS service.
        
        Args:
            service: Name of the TTS service ('google', 'elevenlabs')
            api_key: API key for the service
        """
        self.api_keys[service] = api_key
        self.logger.info(f"API key set for {service}")
    
    def set_voice(self, voice_id: str):
        """
        Set the voice to use for speech synthesis.
        
        Args:
            voice_id: ID of the voice to use
        """
        # Validate voice ID
        if self.tts_service in self.service_configs:
            if voice_id in self.service_configs[self.tts_service]["voices"]:
                self.voice_id = voice_id
                self.logger.info(f"Voice set to {voice_id}")
            else:
                available_voices = list(self.service_configs[self.tts_service]["voices"].keys())
                self.logger.warning(f"Invalid voice ID: {voice_id}. Available voices: {available_voices}")
        else:
            self.logger.warning(f"Unknown TTS service: {self.tts_service}")
    
    def set_tts_service(self, service: str):
        """
        Set the TTS service to use.
        
        Args:
            service: Name of the TTS service ('google', 'elevenlabs', 'local')
        """
        if service in self.service_configs:
            self.tts_service = service
            
            # Reset voice to a default for the new service
            default_voice = next(iter(self.service_configs[service]["voices"]))
            self.voice_id = default_voice
            
            self.logger.info(f"TTS service set to {service} with default voice {default_voice}")
        else:
            self.logger.warning(f"Unknown TTS service: {service}")
    
    async def synthesize_speech(self, text: str) -> Optional[bytes]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            
        Returns:
            bytes: Raw audio data or None if synthesis failed
        """
        if not text:
            self.logger.warning("Empty text provided for synthesis")
            return None
        
        self.state = SpeechSynthesisState.SYNTHESIZING
        self.logger.info(f"Synthesizing speech: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        try:
            # Choose synthesis method based on service
            if self.tts_service == "google":
                audio_data = await self._synthesize_google(text)
            elif self.tts_service == "elevenlabs":
                audio_data = await self._synthesize_elevenlabs(text)
            elif self.tts_service == "local":
                audio_data = await self._synthesize_local(text)
            else:
                raise ValueError(f"Unknown TTS service: {self.tts_service}")
            
            if audio_data:
                self.logger.info(f"Speech synthesis complete: {len(audio_data)} bytes")
                self._current_audio = audio_data
                
                # Call the callback if registered
                if self.on_synthesis_complete:
                    try:
                        await self.on_synthesis_complete(audio_data)
                    except Exception as e:
                        self.logger.error(f"Error in synthesis complete callback: {e}")
                
                self.state = SpeechSynthesisState.IDLE
                return audio_data
            else:
                self.state = SpeechSynthesisState.ERROR
                self.logger.error("Speech synthesis failed: no audio data returned")
                return None
            
        except Exception as e:
            self.state = SpeechSynthesisState.ERROR
            self.logger.error(f"Error during speech synthesis: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def play_speech(self, audio_data: Optional[bytes] = None) -> bool:
        """
        Play synthesized speech.
        
        Args:
            audio_data: Raw audio data to play (uses last synthesized audio if None)
            
        Returns:
            bool: True if playback started successfully, False otherwise
        """
        # Use provided audio data or the last synthesized audio
        audio_to_play = audio_data if audio_data is not None else self._current_audio
        
        if not audio_to_play:
            self.logger.warning("No audio data available for playback")
            return False
        
        self.state = SpeechSynthesisState.PLAYING
        self._playback_event.clear()
        
        try:
            # Call the playback start callback if registered
            if self.on_playback_start:
                try:
                    await self.on_playback_start()
                except Exception as e:
                    self.logger.error(f"Error in playback start callback: {e}")
            
            # Play audio in a separate thread to avoid blocking
            playback_task = asyncio.create_task(self._play_audio(audio_to_play))
            
            # Wait for playback to complete
            await self._playback_event.wait()
            
            return True
            
        except Exception as e:
            self.state = SpeechSynthesisState.ERROR
            self.logger.error(f"Error during speech playback: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def synthesize_and_play(self, text: str) -> bool:
        """
        Synthesize speech from text and play it.
        
        Args:
            text: Text to synthesize and play
            
        Returns:
            bool: True if synthesis and playback were successful, False otherwise
        """
        audio_data = await self.synthesize_speech(text)
        if audio_data:
            return await self.play_speech(audio_data)
        return False
    
    async def save_to_file(self, text: str, file_path: str) -> bool:
        """
        Synthesize speech and save it to a file.
        
        Args:
            text: Text to synthesize
            file_path: Path to save the audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        audio_data = await self.synthesize_speech(text)
        if not audio_data:
            return False
        
        try:
            # Determine file format from extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == ".wav":
                # Save as WAV
                with open(file_path, "wb") as f:
                    f.write(audio_data)
            else:
                # Convert to other formats using pydub
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_path = temp_file.name
                    temp_file.write(audio_data)
                
                try:
                    # Load the WAV file
                    audio = AudioSegment.from_wav(temp_path)
                    
                    # Export to the desired format
                    audio.export(file_path, format=file_ext[1:])
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
            
            self.logger.info(f"Audio saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving audio to file: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def _synthesize_google(self, text: str) -> Optional[bytes]:
        """
        Synthesize speech using Google Cloud TTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            bytes: Raw audio data or None if synthesis failed
        """
        if "google" not in self.api_keys:
            self.logger.error("Google API key not set")
            return None
        
        api_key = self.api_keys["google"]
        api_url = self.service_configs["google"]["api_url"]
        
        # Get voice configuration
        voice_config = self.service_configs["google"]["voices"].get(self.voice_id)
        if not voice_config:
            self.logger.error(f"Invalid voice ID for Google TTS: {self.voice_id}")
            return None
        
        # Prepare request payload
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": voice_config["language_code"],
                "name": self.voice_id,
                "ssmlGender": voice_config["gender"]
            },
            "audioConfig": {
                "audioEncoding": "LINEAR16",
                "sampleRateHertz": self.sample_rate,
                "effectsProfileId": ["headphone-class-device"]
            }
        }
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_url}?key={api_key}",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "audioContent" in result:
                        # Decode base64 audio content
                        import base64
                        audio_data = base64.b64decode(result["audioContent"])
                        return audio_data
                    else:
                        self.logger.error("No audio content in Google TTS response")
                        return None
                else:
                    error_text = await response.text()
                    self.logger.error(f"Google TTS API error: {response.status} - {error_text}")
                    return None
    
    async def _synthesize_elevenlabs(self, text: str) -> Optional[bytes]:
        """
        Synthesize speech using ElevenLabs TTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            bytes: Raw audio data or None if synthesis failed
        """
        if "elevenlabs" not in self.api_keys:
            self.logger.error("ElevenLabs API key not set")
            return None
        
        api_key = self.api_keys["elevenlabs"]
        
        # Get voice configuration
        voice_config = self.service_configs["elevenlabs"]["voices"].get(self.voice_id)
        if not voice_config:
            self.logger.error(f"Invalid voice ID for ElevenLabs TTS: {self.voice_id}")
            return None
        
        voice_id = voice_config["voice_id"]
        api_url = f"{self.service_configs['elevenlabs']['api_url']}/{voice_id}"
        
        # Prepare request payload
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "xi-api-key": api_key
                }
            ) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    return audio_data
                else:
                    error_text = await response.text()
                    self.logger.error(f"ElevenLabs TTS API error: {response.status} - {error_text}")
                    return None
    
    async def _synthesize_local(self, text: str) -> Optional[bytes]:
        """
        Synthesize speech using local TTS engine.
        
        Args:
            text: Text to synthesize
            
        Returns:
            bytes: Raw audio data or None if synthesis failed
        """
        try:
            import pyttsx3
            import io
            import wave
            
            # Initialize the TTS engine
            engine = pyttsx3.init()
            
            # Get voice configuration
            voice_config = self.service_configs["local"]["voices"].get(self.voice_id)
            if voice_config and voice_config["id"]:
                # Set voice if specified
                voices = engine.getProperty('voices')
                for voice in voices:
                    if voice_config["id"] in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set properties
            engine.setProperty('rate', 175)  # Speed
            engine.setProperty('volume', 1.0)  # Volume
            
            # Create a temporary file to save the audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Save speech to the temporary file
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            try:
                # Read the audio data
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                return audio_data
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except ImportError:
            self.logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            return None
        except Exception as e:
            self.logger.error(f"Error using local TTS engine: {e}")
            return None
    
    async def _play_audio(self, audio_data: bytes):
        """
        Play audio data.
        
        Args:
            audio_data: Raw audio data to play
        """
        try:
            # Create a temporary file to save the audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_data)
            
            try:
                # Load and play the audio
                audio = AudioSegment.from_file(temp_path)
                
                # Play in a separate thread to avoid blocking
                def play_thread():
                    play(audio)
                    # Signal completion
                    asyncio.run_coroutine_threadsafe(
                        self._on_playback_finished(),
                        asyncio.get_event_loop()
                    )
                
                # Start playback thread
                import threading
                threading.Thread(target=play_thread).start()
                
            finally:
                # Clean up temp file (after a delay to ensure playback has started)
                async def delayed_cleanup():
                    await asyncio.sleep(1)
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                
                asyncio.create_task(delayed_cleanup())
            
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            self.state = SpeechSynthesisState.ERROR
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            # Signal completion despite error
            self._playback_event.set()
    
    async def _on_playback_finished(self):
        """Handle playback completion."""
        self.logger.info("Playback finished")
        self.state = SpeechSynthesisState.IDLE
        
        # Signal completion
        self._playback_event.set()
        
        # Call the callback if registered
        if self.on_playback_complete:
            try:
                await self.on_playback_complete()
            except Exception as e:
                self.logger.error(f"Error in playback complete callback: {e}")

# Example usage
async def example_usage():
    # Create a speech synthesizer
    synthesizer = SpeechSynthesizer(tts_service="local")
    
    # Define callbacks
    async def on_synthesis_complete(audio_data):
        print(f"Synthesis complete: {len(audio_data)} bytes")
    
    async def on_playback_start():
        print("Playback started")
    
    async def on_playback_complete():
        print("Playback complete")
    
    async def on_error(error):
        print(f"Error: {error}")
    
    # Register callbacks
    synthesizer.register_callback("on_synthesis_complete", on_synthesis_complete)
    synthesizer.register_callback("on_playback_start", on_playback_start)
    synthesizer.register_callback("on_playback_complete", on_playback_complete)
    synthesizer.register_callback("on_error", on_error)
    
    # Synthesize and play speech
    text = "Hello, I am Dr. TARDIS. How can I assist you today?"
    await synthesizer.synthesize_and_play(text)
    
    # Save speech to a file
    await synthesizer.save_to_file("This is a test of saving speech to a file.", "test_speech.wav")

if __name__ == "__main__":
    asyncio.run(example_usage())
"""
