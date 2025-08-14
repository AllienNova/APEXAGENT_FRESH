"""
Session Manager for Gemini Live API Integration

This module implements session management functionality for the Gemini Live API integration,
handling connection pooling, authentication, and resource management.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import logging
import time
import uuid
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field

from .gemini_live_provider import GeminiLiveProvider, ConnectionState, MessageType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SessionState(Enum):
    """Enum for different states of a Gemini Live session."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    TERMINATED = "terminated"

@dataclass
class SessionMetrics:
    """Data class for tracking session metrics."""
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    message_count: int = 0
    error_count: int = 0
    total_tokens: int = 0
    response_times: List[float] = field(default_factory=list)
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time in seconds."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    @property
    def session_duration(self) -> float:
        """Calculate session duration in seconds."""
        return time.time() - self.created_at
    
    @property
    def idle_time(self) -> float:
        """Calculate idle time in seconds."""
        return time.time() - self.last_activity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "message_count": self.message_count,
            "error_count": self.error_count,
            "total_tokens": self.total_tokens,
            "avg_response_time": self.avg_response_time,
            "session_duration": self.session_duration,
            "idle_time": self.idle_time
        }
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = time.time()
    
    def record_message(self, tokens: int = 0):
        """Record a message and its token count."""
        self.message_count += 1
        self.total_tokens += tokens
        self.update_activity()
    
    def record_error(self):
        """Record an error occurrence."""
        self.error_count += 1
        self.update_activity()
    
    def record_response_time(self, seconds: float):
        """Record a response time measurement."""
        self.response_times.append(seconds)
        self.update_activity()

class SessionManager:
    """
    Manages Gemini Live API sessions, handling connection pooling, authentication,
    and resource management.
    
    Attributes:
        sessions (Dict[str, Dict]): Dictionary of active sessions
        max_sessions (int): Maximum number of concurrent sessions
        idle_timeout (int): Timeout in seconds for idle sessions
        logger (logging.Logger): Logger for the session manager
    """
    
    def __init__(self, max_sessions: int = 10, idle_timeout: int = 300):
        """
        Initialize the Session Manager.
        
        Args:
            max_sessions: Maximum number of concurrent sessions
            idle_timeout: Timeout in seconds for idle sessions
        """
        self.sessions: Dict[str, Dict] = {}
        self.max_sessions = max_sessions
        self.idle_timeout = idle_timeout
        self.logger = logging.getLogger("SessionManager")
        self._cleanup_task = None
        self.logger.info(f"SessionManager initialized with max_sessions={max_sessions}, idle_timeout={idle_timeout}s")
    
    async def start(self):
        """Start the session manager and background tasks."""
        self._cleanup_task = asyncio.create_task(self._cleanup_idle_sessions())
        self.logger.info("SessionManager started")
    
    async def stop(self):
        """Stop the session manager and clean up resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all active sessions
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)
        
        self.logger.info("SessionManager stopped")
    
    async def create_session(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro-live",
                           system_instructions: Optional[str] = None) -> str:
        """
        Create a new Gemini Live session.
        
        Args:
            api_key: Google API key for authentication
            model_name: Name of the Gemini model to use
            system_instructions: Optional system instructions for the model
            
        Returns:
            str: Session ID of the newly created session
        """
        # Check if we've reached the maximum number of sessions
        if len(self.sessions) >= self.max_sessions:
            # Try to clean up idle sessions first
            await self._cleanup_idle_sessions(force=True)
            
            # If still at max, reject the new session
            if len(self.sessions) >= self.max_sessions:
                raise RuntimeError(f"Maximum number of sessions ({self.max_sessions}) reached")
        
        # Create a new session ID
        session_id = str(uuid.uuid4())
        
        # Create a new Gemini Live provider
        provider = GeminiLiveProvider(api_key=api_key, model_name=model_name)
        
        # Set up callbacks
        provider.register_callback("on_message", lambda msg_type, content, data: 
                                 self._handle_message(session_id, msg_type, content, data))
        provider.register_callback("on_error", lambda error: 
                                 self._handle_error(session_id, error))
        provider.register_callback("on_state_change", lambda state: 
                                 self._handle_state_change(session_id, state))
        
        # Create session object
        session = {
            "id": session_id,
            "provider": provider,
            "state": SessionState.INITIALIZING,
            "metrics": SessionMetrics(),
            "callbacks": {
                "on_message": None,
                "on_error": None,
                "on_state_change": None
            }
        }
        
        # Store the session
        self.sessions[session_id] = session
        self.logger.info(f"Created session {session_id} with model {model_name}")
        
        # Connect to the Gemini Live API
        try:
            await provider.connect(system_instructions=system_instructions)
            session["state"] = SessionState.ACTIVE
            self.logger.info(f"Session {session_id} connected successfully")
        except Exception as e:
            session["state"] = SessionState.ERROR
            self.logger.error(f"Failed to connect session {session_id}: {e}")
            session["metrics"].record_error()
            # Re-raise the exception
            raise
        
        return session_id
    
    async def close_session(self, session_id: str):
        """
        Close a Gemini Live session.
        
        Args:
            session_id: ID of the session to close
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Session {session_id} not found")
            return
        
        session = self.sessions[session_id]
        provider = session["provider"]
        
        # Update session state
        session["state"] = SessionState.TERMINATED
        
        # Disconnect from the Gemini Live API
        try:
            await provider.disconnect()
            self.logger.info(f"Session {session_id} disconnected")
        except Exception as e:
            self.logger.error(f"Error disconnecting session {session_id}: {e}")
        
        # Remove the session
        del self.sessions[session_id]
        self.logger.info(f"Session {session_id} closed and removed")
    
    def register_session_callback(self, session_id: str, event_type: str, callback: Callable):
        """
        Register a callback function for a specific session event.
        
        Args:
            session_id: ID of the session
            event_type: Type of event to register callback for ('on_message', 'on_error', etc.)
            callback: Function to call when the event occurs
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Session {session_id} not found")
            return
        
        session = self.sessions[session_id]
        
        if event_type in session["callbacks"]:
            session["callbacks"][event_type] = callback
            self.logger.debug(f"Registered {event_type} callback for session {session_id}")
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    async def send_text(self, session_id: str, text: str):
        """
        Send a text message in a session.
        
        Args:
            session_id: ID of the session
            text: Text content to send
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Session {session_id} not found")
            return
        
        session = self.sessions[session_id]
        provider = session["provider"]
        
        # Update metrics
        session["metrics"].record_message(tokens=len(text.split()))
        session["metrics"].update_activity()
        
        # Send the message
        await provider.send_text(text)
    
    async def send_audio(self, session_id: str, audio_data: bytes, sample_rate: int = 16000):
        """
        Send audio data in a session.
        
        Args:
            session_id: ID of the session
            audio_data: Raw audio bytes
            sample_rate: Sample rate of the audio in Hz
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Session {session_id} not found")
            return
        
        session = self.sessions[session_id]
        provider = session["provider"]
        
        # Update metrics
        session["metrics"].record_message()
        session["metrics"].update_activity()
        
        # Send the audio
        await provider.send_audio(audio_data, sample_rate)
    
    async def send_video_frame(self, session_id: str, video_frame: bytes, width: int, height: int):
        """
        Send a video frame in a session.
        
        Args:
            session_id: ID of the session
            video_frame: Raw video frame bytes
            width: Width of the video frame in pixels
            height: Height of the video frame in pixels
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Session {session_id} not found")
            return
        
        session = self.sessions[session_id]
        provider = session["provider"]
        
        # Update metrics
        session["metrics"].record_message()
        session["metrics"].update_activity()
        
        # Send the video frame
        await provider.send_video_frame(video_frame, width, height)
    
    def get_session_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Dict: Session metrics or None if session not found
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Session {session_id} not found")
            return None
        
        session = self.sessions[session_id]
        metrics = session["metrics"].to_dict()
        metrics["state"] = session["state"].name
        
        return metrics
    
    def get_all_session_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all active sessions.
        
        Returns:
            Dict: Dictionary of session IDs to metrics
        """
        return {
            session_id: {
                **session["metrics"].to_dict(),
                "state": session["state"].name
            }
            for session_id, session in self.sessions.items()
        }
    
    def _handle_message(self, session_id: str, msg_type: str, content: Any, data: Dict):
        """
        Handle a message received from the Gemini Live API.
        
        Args:
            session_id: ID of the session
            msg_type: Type of message received
            content: Message content
            data: Full message data
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Received message for unknown session {session_id}")
            return
        
        session = self.sessions[session_id]
        
        # Update metrics
        session["metrics"].update_activity()
        
        # Call the session callback if registered
        if session["callbacks"]["on_message"]:
            session["callbacks"]["on_message"](msg_type, content, data)
    
    def _handle_error(self, session_id: str, error: str):
        """
        Handle an error from the Gemini Live API.
        
        Args:
            session_id: ID of the session
            error: Error message
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Received error for unknown session {session_id}")
            return
        
        session = self.sessions[session_id]
        
        # Update session state and metrics
        session["state"] = SessionState.ERROR
        session["metrics"].record_error()
        
        self.logger.error(f"Error in session {session_id}: {error}")
        
        # Call the session callback if registered
        if session["callbacks"]["on_error"]:
            session["callbacks"]["on_error"](error)
    
    def _handle_state_change(self, session_id: str, state: ConnectionState):
        """
        Handle a connection state change from the Gemini Live API.
        
        Args:
            session_id: ID of the session
            state: New connection state
        """
        if session_id not in self.sessions:
            self.logger.warning(f"Received state change for unknown session {session_id}")
            return
        
        session = self.sessions[session_id]
        
        # Update session state based on connection state
        if state == ConnectionState.CONNECTED:
            session["state"] = SessionState.ACTIVE
        elif state == ConnectionState.DISCONNECTED:
            session["state"] = SessionState.TERMINATED
        elif state == ConnectionState.ERROR:
            session["state"] = SessionState.ERROR
        
        # Update metrics
        session["metrics"].update_activity()
        
        self.logger.debug(f"Session {session_id} connection state changed to {state.name}")
        
        # Call the session callback if registered
        if session["callbacks"]["on_state_change"]:
            session["callbacks"]["on_state_change"](state)
    
    async def _cleanup_idle_sessions(self, force: bool = False):
        """
        Background task to clean up idle sessions.
        
        Args:
            force: If True, immediately clean up idle sessions instead of waiting
        """
        while True:
            try:
                # Find idle sessions
                now = time.time()
                idle_sessions = [
                    session_id for session_id, session in self.sessions.items()
                    if session["state"] == SessionState.ACTIVE and 
                    (now - session["metrics"].last_activity) > self.idle_timeout
                ]
                
                # Close idle sessions
                for session_id in idle_sessions:
                    self.logger.info(f"Closing idle session {session_id} (idle for {now - self.sessions[session_id]['metrics'].last_activity:.1f}s)")
                    await self.close_session(session_id)
                
                if not force:
                    # Wait before next cleanup
                    await asyncio.sleep(60)  # Check every minute
                else:
                    # If forced, just do one cleanup and return
                    return
                    
            except asyncio.CancelledError:
                # Task was cancelled, exit cleanly
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(10)

# Example usage
async def example_usage():
    # Create a session manager
    manager = SessionManager(max_sessions=5, idle_timeout=120)
    await manager.start()
    
    try:
        # Create a session
        session_id = await manager.create_session(
            system_instructions="You are Dr. TARDIS, a helpful technical assistant."
        )
        
        # Register callbacks
        def on_message(msg_type, content, data):
            print(f"Received {msg_type} message: {content[:100]}...")
        
        manager.register_session_callback(session_id, "on_message", on_message)
        
        # Send a message
        await manager.send_text(session_id, "Hello, I need help with my ApexAgent installation.")
        
        # Wait for responses
        await asyncio.sleep(5)
        
        # Get session metrics
        metrics = manager.get_session_metrics(session_id)
        print(f"Session metrics: {metrics}")
        
        # Close the session
        await manager.close_session(session_id)
        
    finally:
        # Stop the session manager
        await manager.stop()

if __name__ == "__main__":
    asyncio.run(example_usage())
