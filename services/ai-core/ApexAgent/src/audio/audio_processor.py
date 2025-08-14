"""
Audio Processing Module for Dr. TARDIS Gemini Live API Integration

This module handles audio capture, processing, and streaming for the Dr. TARDIS
Gemini Live API integration, enabling voice-based interactions.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import logging
import numpy as np
import threading
import time
import wave
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

import sounddevice as sd
import pyaudio
from pydub import AudioSegment
from pydub.silence import detect_silence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AudioState(Enum):
    """Enum for different states of the audio processor."""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    PLAYING = "playing"
    ERROR = "error"

class AudioProcessor:
    """
    Handles audio capture, processing, and playback for voice interactions.
    
    This class provides functionality for capturing audio from a microphone,
    processing it for use with the Gemini Live API, and playing back audio
    responses from Dr. TARDIS.
    
    Attributes:
        sample_rate (int): Sample rate for audio processing in Hz
        channels (int): Number of audio channels (1 for mono, 2 for stereo)
        format (int): Audio format (bit depth)
        chunk_size (int): Size of audio chunks for processing
        state (AudioState): Current state of the audio processor
        vad_enabled (bool): Whether voice activity detection is enabled
        vad_threshold (float): Threshold for voice activity detection in dB
        vad_min_silence (int): Minimum silence duration in ms to end recording
        logger (logging.Logger): Logger for the audio processor
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, 
                 format_type: str = "int16", chunk_size: int = 1024):
        """
        Initialize the Audio Processor.
        
        Args:
            sample_rate: Sample rate for audio processing in Hz
            channels: Number of audio channels (1 for mono, 2 for stereo)
            format_type: Audio format type ('int16', 'int32', 'float32')
            chunk_size: Size of audio chunks for processing
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        
        # Set format based on format_type
        if format_type == "int16":
            self.format = pyaudio.paInt16
            self.numpy_format = np.int16
        elif format_type == "int32":
            self.format = pyaudio.paInt32
            self.numpy_format = np.int32
        elif format_type == "float32":
            self.format = pyaudio.paFloat32
            self.numpy_format = np.float32
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        self.state = AudioState.IDLE
        self.vad_enabled = True
        self.vad_threshold = -40  # dB
        self.vad_min_silence = 1000  # ms
        
        self.logger = logging.getLogger("AudioProcessor")
        self.logger.info(f"AudioProcessor initialized with sample_rate={sample_rate}, channels={channels}, format={format_type}")
        
        # Initialize PyAudio
        self.pyaudio = pyaudio.PyAudio()
        
        # Recording state
        self._recording_stream = None
        self._recording_frames = []
        self._recording_event = asyncio.Event()
        self._stop_recording_event = asyncio.Event()
        
        # Playback state
        self._playback_stream = None
        self._playback_event = asyncio.Event()
        
        # Callbacks
        self.on_audio_data = None
        self.on_recording_complete = None
        self.on_playback_complete = None
        self.on_error = None
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        self.close()
    
    def close(self):
        """Close the audio processor and release resources."""
        if self._recording_stream:
            self._recording_stream.stop_stream()
            self._recording_stream.close()
            self._recording_stream = None
        
        if self._playback_stream:
            self._playback_stream.stop_stream()
            self._playback_stream.close()
            self._playback_stream = None
        
        if hasattr(self, 'pyaudio') and self.pyaudio:
            self.pyaudio.terminate()
            self.pyaudio = None
        
        self.logger.info("AudioProcessor closed and resources released")
    
    def configure_vad(self, enabled: bool = True, threshold: float = -40, min_silence: int = 1000):
        """
        Configure Voice Activity Detection (VAD) settings.
        
        Args:
            enabled: Whether VAD is enabled
            threshold: Threshold for voice activity detection in dB
            min_silence: Minimum silence duration in ms to end recording
        """
        self.vad_enabled = enabled
        self.vad_threshold = threshold
        self.vad_min_silence = min_silence
        self.logger.info(f"VAD configured: enabled={enabled}, threshold={threshold}dB, min_silence={min_silence}ms")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_audio_data', 'on_recording_complete', 'on_playback_complete', 'on_error')
            callback: Function to call when the event occurs
        """
        if event_type == "on_audio_data":
            self.on_audio_data = callback
        elif event_type == "on_recording_complete":
            self.on_recording_complete = callback
        elif event_type == "on_playback_complete":
            self.on_playback_complete = callback
        elif event_type == "on_error":
            self.on_error = callback
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    async def start_recording(self, max_duration: Optional[float] = None):
        """
        Start recording audio from the microphone.
        
        Args:
            max_duration: Maximum recording duration in seconds (None for no limit)
        """
        if self.state == AudioState.RECORDING:
            self.logger.warning("Already recording")
            return
        
        self.state = AudioState.RECORDING
        self._recording_frames = []
        self._stop_recording_event.clear()
        
        try:
            def audio_callback(in_data, frame_count, time_info, status):
                if status:
                    self.logger.warning(f"Audio input status: {status}")
                
                # Convert audio data to numpy array
                audio_data = np.frombuffer(in_data, dtype=self.numpy_format)
                
                # Store the audio data
                self._recording_frames.append(in_data)
                
                # Call the callback if registered
                if self.on_audio_data:
                    asyncio.run_coroutine_threadsafe(
                        self._call_audio_data_callback(audio_data),
                        asyncio.get_event_loop()
                    )
                
                return (None, pyaudio.paContinue)
            
            # Open the input stream
            self._recording_stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=audio_callback
            )
            
            self.logger.info("Started recording")
            
            # Start the stream
            self._recording_stream.start_stream()
            
            # Set up max duration timer if specified
            if max_duration is not None:
                asyncio.create_task(self._stop_recording_after(max_duration))
            
            # Wait for recording to complete
            await self._stop_recording_event.wait()
            
            # Process the recorded audio
            await self._process_recorded_audio()
            
        except Exception as e:
            self.state = AudioState.ERROR
            self.logger.error(f"Error during recording: {e}")
            if self.on_error:
                await self._call_error_callback(str(e))
    
    async def stop_recording(self):
        """Stop recording audio."""
        if self.state != AudioState.RECORDING:
            self.logger.warning(f"Not recording (current state: {self.state.name})")
            return
        
        self.logger.info("Stopping recording")
        self._stop_recording_event.set()
    
    async def play_audio(self, audio_data: bytes):
        """
        Play audio data through the speakers.
        
        Args:
            audio_data: Raw audio bytes to play
        """
        if self.state == AudioState.PLAYING:
            self.logger.warning("Already playing audio")
            return
        
        self.state = AudioState.PLAYING
        self._playback_event.clear()
        
        try:
            def audio_callback(in_data, frame_count, time_info, status):
                if status:
                    self.logger.warning(f"Audio output status: {status}")
                
                # Check if we've reached the end of the audio data
                if self._playback_position >= len(self._playback_data):
                    # End of playback
                    asyncio.run_coroutine_threadsafe(
                        self._on_playback_finished(),
                        asyncio.get_event_loop()
                    )
                    return (None, pyaudio.paComplete)
                
                # Calculate how much data to send
                end_pos = min(self._playback_position + frame_count * self.channels * 2, len(self._playback_data))
                chunk = self._playback_data[self._playback_position:end_pos]
                self._playback_position = end_pos
                
                # Pad with silence if we don't have enough data
                if len(chunk) < frame_count * self.channels * 2:
                    chunk = chunk + b'\x00' * (frame_count * self.channels * 2 - len(chunk))
                
                return (chunk, pyaudio.paContinue)
            
            # Convert audio data to the correct format if needed
            self._playback_data = audio_data
            self._playback_position = 0
            
            # Open the output stream
            self._playback_stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=audio_callback
            )
            
            self.logger.info("Started playback")
            
            # Start the stream
            self._playback_stream.start_stream()
            
            # Wait for playback to complete
            await self._playback_event.wait()
            
        except Exception as e:
            self.state = AudioState.ERROR
            self.logger.error(f"Error during playback: {e}")
            if self.on_error:
                await self._call_error_callback(str(e))
    
    async def convert_audio_file(self, file_path: str) -> bytes:
        """
        Convert an audio file to the format used by the processor.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            bytes: Raw audio data in the processor's format
        """
        try:
            # Load the audio file using pydub
            audio = AudioSegment.from_file(file_path)
            
            # Convert to the processor's format
            audio = audio.set_frame_rate(self.sample_rate)
            audio = audio.set_channels(self.channels)
            
            # Get raw audio data
            if self.format == pyaudio.paInt16:
                audio = audio.set_sample_width(2)  # 16-bit
            elif self.format == pyaudio.paInt32:
                audio = audio.set_sample_width(4)  # 32-bit
            elif self.format == pyaudio.paFloat32:
                # pydub doesn't directly support float32, so we'll convert from int16
                audio = audio.set_sample_width(2)
                raw_data = audio.raw_data
                int_data = np.frombuffer(raw_data, dtype=np.int16)
                float_data = int_data.astype(np.float32) / 32768.0  # Convert to -1.0 to 1.0 range
                return float_data.tobytes()
            
            return audio.raw_data
            
        except Exception as e:
            self.logger.error(f"Error converting audio file: {e}")
            if self.on_error:
                await self._call_error_callback(str(e))
            return b''
    
    async def save_audio_to_file(self, audio_data: bytes, file_path: str):
        """
        Save audio data to a file.
        
        Args:
            audio_data: Raw audio bytes to save
            file_path: Path to save the audio file
        """
        try:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.pyaudio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)
            
            self.logger.info(f"Saved audio to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving audio to file: {e}")
            if self.on_error:
                await self._call_error_callback(str(e))
    
    async def _stop_recording_after(self, duration: float):
        """
        Stop recording after a specified duration.
        
        Args:
            duration: Duration in seconds
        """
        await asyncio.sleep(duration)
        if self.state == AudioState.RECORDING:
            await self.stop_recording()
    
    async def _process_recorded_audio(self):
        """Process the recorded audio data."""
        self.state = AudioState.PROCESSING
        
        try:
            # Combine all audio frames
            audio_data = b''.join(self._recording_frames)
            
            # Apply VAD if enabled
            if self.vad_enabled:
                audio_data = await self._apply_vad(audio_data)
            
            self.logger.info(f"Processed {len(audio_data)} bytes of audio data")
            
            # Call the callback if registered
            if self.on_recording_complete:
                await self.on_recording_complete(audio_data)
            
            self.state = AudioState.IDLE
            
        except Exception as e:
            self.state = AudioState.ERROR
            self.logger.error(f"Error processing recorded audio: {e}")
            if self.on_error:
                await self._call_error_callback(str(e))
    
    async def _apply_vad(self, audio_data: bytes) -> bytes:
        """
        Apply Voice Activity Detection to trim silence.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            bytes: Trimmed audio data
        """
        try:
            # Convert to pydub AudioSegment
            if self.format == pyaudio.paInt16:
                sample_width = 2
            elif self.format == pyaudio.paInt32:
                sample_width = 4
            else:  # float32
                # Convert float32 to int16 for pydub
                float_data = np.frombuffer(audio_data, dtype=np.float32)
                int_data = (float_data * 32768.0).astype(np.int16)
                audio_data = int_data.tobytes()
                sample_width = 2
            
            audio_segment = AudioSegment(
                data=audio_data,
                sample_width=sample_width,
                frame_rate=self.sample_rate,
                channels=self.channels
            )
            
            # Detect silence
            silence_ranges = detect_silence(
                audio_segment,
                min_silence_len=self.vad_min_silence,
                silence_thresh=self.vad_threshold
            )
            
            # Trim leading and trailing silence
            if silence_ranges:
                if silence_ranges[0][0] == 0:
                    # Trim leading silence
                    audio_segment = audio_segment[silence_ranges[0][1]:]
                
                if silence_ranges[-1][1] == len(audio_segment):
                    # Trim trailing silence
                    audio_segment = audio_segment[:silence_ranges[-1][0]]
            
            # Convert back to raw bytes
            if self.format == pyaudio.paFloat32:
                # Convert int16 back to float32
                int_data = np.frombuffer(audio_segment.raw_data, dtype=np.int16)
                float_data = int_data.astype(np.float32) / 32768.0
                return float_data.tobytes()
            else:
                return audio_segment.raw_data
            
        except Exception as e:
            self.logger.error(f"Error applying VAD: {e}")
            # Return original audio data if VAD fails
            return audio_data
    
    async def _on_playback_finished(self):
        """Handle playback completion."""
        self.logger.info("Playback finished")
        
        # Clean up playback stream
        if self._playback_stream:
            self._playback_stream.stop_stream()
            self._playback_stream.close()
            self._playback_stream = None
        
        self.state = AudioState.IDLE
        self._playback_event.set()
        
        # Call the callback if registered
        if self.on_playback_complete:
            await self.on_playback_complete()
    
    async def _call_audio_data_callback(self, audio_data: np.ndarray):
        """
        Call the audio data callback safely.
        
        Args:
            audio_data: Audio data as numpy array
        """
        if self.on_audio_data:
            try:
                await self.on_audio_data(audio_data)
            except Exception as e:
                self.logger.error(f"Error in audio data callback: {e}")
    
    async def _call_error_callback(self, error: str):
        """
        Call the error callback safely.
        
        Args:
            error: Error message
        """
        if self.on_error:
            try:
                await self.on_error(error)
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}")

# Example usage
async def example_usage():
    # Create an audio processor
    processor = AudioProcessor(sample_rate=16000, channels=1)
    
    # Configure VAD
    processor.configure_vad(enabled=True, threshold=-40, min_silence=500)
    
    # Define callbacks
    async def on_audio_data(audio_data):
        # This would be called for each chunk of audio data during recording
        print(f"Received audio chunk: {len(audio_data)} samples")
    
    async def on_recording_complete(audio_data):
        print(f"Recording complete: {len(audio_data)} bytes")
        # Save the recording to a file
        await processor.save_audio_to_file(audio_data, "recording.wav")
        
        # Play back the recording
        await processor.play_audio(audio_data)
    
    async def on_playback_complete():
        print("Playback complete")
    
    async def on_error(error):
        print(f"Error: {error}")
    
    # Register callbacks
    processor.register_callback("on_audio_data", on_audio_data)
    processor.register_callback("on_recording_complete", on_recording_complete)
    processor.register_callback("on_playback_complete", on_playback_complete)
    processor.register_callback("on_error", on_error)
    
    try:
        # Start recording for 5 seconds
        print("Recording for 5 seconds...")
        await processor.start_recording(max_duration=5)
        
        # Wait for playback to complete
        while processor.state != AudioState.IDLE:
            await asyncio.sleep(0.1)
        
    finally:
        # Clean up
        processor.close()

if __name__ == "__main__":
    asyncio.run(example_usage())
"""
