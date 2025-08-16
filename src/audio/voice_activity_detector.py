"""
Voice Activity Detection Module for Dr. TARDIS Gemini Live API Integration

This module provides advanced voice activity detection capabilities for the Dr. TARDIS
Gemini Live API integration, enabling natural conversation flows with proper
turn-taking and interruption handling.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import logging
import numpy as np
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class VoiceActivityState(Enum):
    """Enum for different states of voice activity."""
    SILENCE = "silence"
    SPEECH = "speech"
    UNCERTAIN = "uncertain"

class VoiceActivityDetector:
    """
    Advanced Voice Activity Detection (VAD) for natural conversations.
    
    This class provides sophisticated voice activity detection capabilities,
    enabling natural conversation flows with proper turn-taking and
    interruption handling.
    
    Attributes:
        energy_threshold (float): Energy threshold for speech detection
        speech_timeout (float): Time in seconds of silence to consider speech ended
        speech_start_threshold (float): Minimum duration in seconds to consider speech started
        history_size (int): Size of the audio history buffer in frames
        state (VoiceActivityState): Current state of voice activity
        logger (logging.Logger): Logger for the VAD
    """
    
    def __init__(self, energy_threshold: float = 0.01, speech_timeout: float = 0.8,
                 speech_start_threshold: float = 0.2, history_size: int = 30):
        """
        Initialize the Voice Activity Detector.
        
        Args:
            energy_threshold: Energy threshold for speech detection
            speech_timeout: Time in seconds of silence to consider speech ended
            speech_start_threshold: Minimum duration in seconds to consider speech started
            history_size: Size of the audio history buffer in frames
        """
        self.energy_threshold = energy_threshold
        self.speech_timeout = speech_timeout
        self.speech_start_threshold = speech_start_threshold
        self.history_size = history_size
        
        self.state = VoiceActivityState.SILENCE
        self.logger = logging.getLogger("VoiceActivityDetector")
        
        # Internal state
        self._audio_history = deque(maxlen=history_size)
        self._energy_history = deque(maxlen=history_size)
        self._last_speech_time = 0
        self._speech_start_time = 0
        self._frame_duration = 0.03  # Assuming 30ms frames
        
        # Callbacks
        self.on_speech_start = None
        self.on_speech_end = None
        self.on_state_change = None
        
        self.logger.info(f"VoiceActivityDetector initialized with energy_threshold={energy_threshold}, "
                        f"speech_timeout={speech_timeout}s, speech_start_threshold={speech_start_threshold}s")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_speech_start', 'on_speech_end', 'on_state_change')
            callback: Function to call when the event occurs
        """
        if event_type == "on_speech_start":
            self.on_speech_start = callback
        elif event_type == "on_speech_end":
            self.on_speech_end = callback
        elif event_type == "on_state_change":
            self.on_state_change = callback
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def configure(self, energy_threshold: Optional[float] = None, 
                 speech_timeout: Optional[float] = None,
                 speech_start_threshold: Optional[float] = None):
        """
        Configure VAD parameters.
        
        Args:
            energy_threshold: Energy threshold for speech detection
            speech_timeout: Time in seconds of silence to consider speech ended
            speech_start_threshold: Minimum duration in seconds to consider speech started
        """
        if energy_threshold is not None:
            self.energy_threshold = energy_threshold
        
        if speech_timeout is not None:
            self.speech_timeout = speech_timeout
        
        if speech_start_threshold is not None:
            self.speech_start_threshold = speech_start_threshold
        
        self.logger.info(f"VAD reconfigured: energy_threshold={self.energy_threshold}, "
                        f"speech_timeout={self.speech_timeout}s, "
                        f"speech_start_threshold={self.speech_start_threshold}s")
    
    def set_frame_duration(self, duration: float):
        """
        Set the duration of each audio frame in seconds.
        
        Args:
            duration: Frame duration in seconds
        """
        self._frame_duration = duration
        self.logger.debug(f"Frame duration set to {duration}s")
    
    async def process_audio_frame(self, audio_frame: np.ndarray) -> VoiceActivityState:
        """
        Process an audio frame and detect voice activity.
        
        Args:
            audio_frame: Audio data as numpy array
            
        Returns:
            VoiceActivityState: Current voice activity state
        """
        # Calculate energy
        energy = np.mean(np.abs(audio_frame))
        
        # Store in history
        self._audio_history.append(audio_frame)
        self._energy_history.append(energy)
        
        # Detect speech
        is_speech = energy > self.energy_threshold
        
        # Update state based on current detection and history
        new_state = await self._update_state(is_speech)
        
        return new_state
    
    async def reset(self):
        """Reset the VAD state."""
        self._audio_history.clear()
        self._energy_history.clear()
        self._last_speech_time = 0
        self._speech_start_time = 0
        
        old_state = self.state
        self.state = VoiceActivityState.SILENCE
        
        if old_state != self.state:
            await self._notify_state_change(old_state, self.state)
        
        self.logger.debug("VAD state reset")
    
    async def get_audio_history(self) -> np.ndarray:
        """
        Get the audio history buffer.
        
        Returns:
            np.ndarray: Concatenated audio history
        """
        if not self._audio_history:
            return np.array([], dtype=np.float32)
        
        return np.concatenate(list(self._audio_history))
    
    async def get_energy_history(self) -> List[float]:
        """
        Get the energy history buffer.
        
        Returns:
            List[float]: Energy history values
        """
        return list(self._energy_history)
    
    async def _update_state(self, is_speech: bool) -> VoiceActivityState:
        """
        Update the VAD state based on current detection and history.
        
        Args:
            is_speech: Whether the current frame is detected as speech
            
        Returns:
            VoiceActivityState: Updated voice activity state
        """
        old_state = self.state
        current_time = time.time()
        
        if is_speech:
            self._last_speech_time = current_time
            
            if self.state == VoiceActivityState.SILENCE:
                # Potential start of speech
                if self._speech_start_time == 0:
                    self._speech_start_time = current_time
                
                # Check if speech has been ongoing for long enough
                if current_time - self._speech_start_time >= self.speech_start_threshold:
                    self.state = VoiceActivityState.SPEECH
            
        else:  # Not speech
            if self.state == VoiceActivityState.SPEECH:
                # Check if silence has been ongoing for long enough
                if current_time - self._last_speech_time >= self.speech_timeout:
                    self.state = VoiceActivityState.SILENCE
                    self._speech_start_time = 0
        
        # Notify if state changed
        if old_state != self.state:
            await self._notify_state_change(old_state, self.state)
        
        return self.state
    
    async def _notify_state_change(self, old_state: VoiceActivityState, new_state: VoiceActivityState):
        """
        Notify listeners of state changes.
        
        Args:
            old_state: Previous voice activity state
            new_state: New voice activity state
        """
        self.logger.debug(f"VAD state changed: {old_state.name} -> {new_state.name}")
        
        # Call state change callback
        if self.on_state_change:
            try:
                await self.on_state_change(old_state, new_state)
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")
        
        # Call specific callbacks
        if old_state == VoiceActivityState.SILENCE and new_state == VoiceActivityState.SPEECH:
            if self.on_speech_start:
                try:
                    await self.on_speech_start()
                except Exception as e:
                    self.logger.error(f"Error in speech start callback: {e}")
        
        elif old_state == VoiceActivityState.SPEECH and new_state == VoiceActivityState.SILENCE:
            if self.on_speech_end:
                try:
                    await self.on_speech_end()
                except Exception as e:
                    self.logger.error(f"Error in speech end callback: {e}")

class InterruptionDetector:
    """
    Detects and manages interruptions in conversations.
    
    This class works with the VoiceActivityDetector to identify when a user
    interrupts the system's speech, enabling more natural conversation flows.
    
    Attributes:
        vad (VoiceActivityDetector): Voice activity detector instance
        system_speaking (bool): Whether the system is currently speaking
        interruption_threshold (float): Time in seconds of user speech to consider an interruption
        logger (logging.Logger): Logger for the interruption detector
    """
    
    def __init__(self, vad: VoiceActivityDetector, interruption_threshold: float = 0.5):
        """
        Initialize the Interruption Detector.
        
        Args:
            vad: Voice activity detector instance
            interruption_threshold: Time in seconds of user speech to consider an interruption
        """
        self.vad = vad
        self.system_speaking = False
        self.interruption_threshold = interruption_threshold
        self.logger = logging.getLogger("InterruptionDetector")
        
        # Internal state
        self._user_speech_start_time = 0
        self._interruption_detected = False
        
        # Callbacks
        self.on_interruption = None
        
        # Register VAD callbacks
        self.vad.register_callback("on_speech_start", self._on_speech_start)
        self.vad.register_callback("on_speech_end", self._on_speech_end)
        
        self.logger.info(f"InterruptionDetector initialized with threshold={interruption_threshold}s")
    
    def register_interruption_callback(self, callback: Callable):
        """
        Register a callback for interruption events.
        
        Args:
            callback: Function to call when an interruption is detected
        """
        self.on_interruption = callback
    
    def set_system_speaking(self, speaking: bool):
        """
        Set whether the system is currently speaking.
        
        Args:
            speaking: Whether the system is speaking
        """
        self.system_speaking = speaking
        
        if not speaking:
            # Reset interruption state when system stops speaking
            self._interruption_detected = False
        
        self.logger.debug(f"System speaking state set to: {speaking}")
    
    async def reset(self):
        """Reset the interruption detector state."""
        self.system_speaking = False
        self._user_speech_start_time = 0
        self._interruption_detected = False
        
        self.logger.debug("Interruption detector reset")
    
    async def _on_speech_start(self):
        """Handle speech start events from VAD."""
        if self.system_speaking:
            # User started speaking while system is speaking
            self._user_speech_start_time = time.time()
            self.logger.debug("Potential interruption detected: user started speaking while system is speaking")
    
    async def _on_speech_end(self):
        """Handle speech end events from VAD."""
        if self._user_speech_start_time > 0:
            # Reset speech start time
            self._user_speech_start_time = 0
    
    async def process_audio_frame(self, audio_frame: np.ndarray) -> bool:
        """
        Process an audio frame and check for interruptions.
        
        Args:
            audio_frame: Audio data as numpy array
            
        Returns:
            bool: Whether an interruption was detected
        """
        # First, let the VAD process the frame
        await self.vad.process_audio_frame(audio_frame)
        
        # Check for interruption
        if (self.system_speaking and 
            self.vad.state == VoiceActivityState.SPEECH and 
            self._user_speech_start_time > 0 and 
            not self._interruption_detected):
            
            # Check if user has been speaking long enough to consider it an interruption
            speech_duration = time.time() - self._user_speech_start_time
            
            if speech_duration >= self.interruption_threshold:
                self._interruption_detected = True
                self.logger.info(f"Interruption detected after {speech_duration:.2f}s of user speech")
                
                # Call the interruption callback
                if self.on_interruption:
                    try:
                        await self.on_interruption()
                    except Exception as e:
                        self.logger.error(f"Error in interruption callback: {e}")
                
                return True
        
        return False

# Example usage
async def example_usage():
    # Create a VAD instance
    vad = VoiceActivityDetector(
        energy_threshold=0.01,
        speech_timeout=0.8,
        speech_start_threshold=0.2
    )
    
    # Create an interruption detector
    interruption_detector = InterruptionDetector(
        vad=vad,
        interruption_threshold=0.5
    )
    
    # Define callbacks
    async def on_speech_start():
        print("Speech started")
    
    async def on_speech_end():
        print("Speech ended")
    
    async def on_interruption():
        print("Interruption detected!")
    
    # Register callbacks
    vad.register_callback("on_speech_start", on_speech_start)
    vad.register_callback("on_speech_end", on_speech_end)
    interruption_detector.register_interruption_callback(on_interruption)
    
    # Simulate system speaking
    interruption_detector.set_system_speaking(True)
    
    # Simulate processing audio frames
    # (In a real application, these would come from a microphone)
    for i in range(100):
        # Generate some fake audio data
        # Silence for the first 30 frames, then speech for the rest
        if i < 30:
            audio_frame = np.random.normal(0, 0.001, 1024)  # Very quiet
        else:
            audio_frame = np.random.normal(0, 0.1, 1024)  # Louder
        
        # Process the frame
        await interruption_detector.process_audio_frame(audio_frame)
        
        # Simulate frame timing
        await asyncio.sleep(0.01)
    
    # Reset the detector
    await interruption_detector.reset()

if __name__ == "__main__":
    asyncio.run(example_usage())
