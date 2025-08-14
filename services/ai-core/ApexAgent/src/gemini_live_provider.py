"""
Gemini Live API Provider for Dr. TARDIS

This module implements the core infrastructure for integrating with Google's Gemini Live API,
enabling real-time multimodal conversations with text, audio, and video capabilities.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import asyncio
import json
import logging
import time
import uuid
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

import google.generativeai as genai
import websockets
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

class MessageType(Enum):
    """Enum for different types of messages in the Gemini Live conversation."""
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    SYSTEM = "system"
    ERROR = "error"

class ConnectionState(Enum):
    """Enum for connection states of the Gemini Live provider."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    CLOSING = "closing"

class GeminiLiveProvider:
    """
    Provider for Google's Gemini Live API that enables real-time multimodal conversations.
    
    This class handles WebSocket connections to the Gemini Live API, manages authentication,
    and provides methods for sending and receiving different types of content (text, audio, video).
    
    Attributes:
        api_key (str): Google API key for authentication
        model_name (str): Name of the Gemini model to use
        session_id (str): Unique identifier for the current session
        connection_state (ConnectionState): Current state of the WebSocket connection
        logger (logging.Logger): Logger for the provider
        websocket (websockets.WebSocketClientProtocol): WebSocket connection to Gemini Live API
        callbacks (Dict): Dictionary of callback functions for different event types
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro-live"):
        """
        Initialize the Gemini Live Provider.
        
        Args:
            api_key: Google API key for authentication (if None, will try to load from environment)
            model_name: Name of the Gemini model to use
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as GOOGLE_API_KEY environment variable")
        
        self.model_name = model_name
        self.session_id = str(uuid.uuid4())
        self.connection_state = ConnectionState.DISCONNECTED
        self.logger = logging.getLogger("GeminiLiveProvider")
        self.websocket = None
        self.callbacks = {
            "on_message": None,
            "on_error": None,
            "on_state_change": None,
            "on_close": None
        }
        
        # Initialize the Google Generative AI library
        genai.configure(api_key=self.api_key)
        self.logger.info(f"GeminiLiveProvider initialized with model: {model_name}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for ('on_message', 'on_error', etc.)
            callback: Function to call when the event occurs
        """
        if event_type in self.callbacks:
            self.callbacks[event_type] = callback
            self.logger.debug(f"Registered callback for {event_type}")
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    async def connect(self, system_instructions: Optional[str] = None):
        """
        Establish a WebSocket connection to the Gemini Live API.
        
        Args:
            system_instructions: Optional system instructions to configure the model behavior
        """
        if self.connection_state == ConnectionState.CONNECTED:
            self.logger.warning("Already connected to Gemini Live API")
            return
        
        self._update_connection_state(ConnectionState.CONNECTING)
        
        try:
            # Construct the WebSocket URL with authentication and model parameters
            ws_url = f"wss://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:streamGenerateContent?key={self.api_key}"
            
            # Connect to the WebSocket
            self.websocket = await websockets.connect(ws_url)
            self._update_connection_state(ConnectionState.CONNECTED)
            self.logger.info(f"Connected to Gemini Live API with session ID: {self.session_id}")
            
            # Send system instructions if provided
            if system_instructions:
                await self.send_system_message(system_instructions)
            
            # Start the message listener
            asyncio.create_task(self._message_listener())
            
        except Exception as e:
            self._update_connection_state(ConnectionState.ERROR)
            self.logger.error(f"Failed to connect to Gemini Live API: {e}")
            if self.callbacks["on_error"]:
                self.callbacks["on_error"](str(e))
    
    async def disconnect(self):
        """Close the WebSocket connection to the Gemini Live API."""
        if self.connection_state != ConnectionState.CONNECTED:
            self.logger.warning(f"Not connected to Gemini Live API (current state: {self.connection_state.name})")
            return
        
        self._update_connection_state(ConnectionState.CLOSING)
        
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
                self.logger.info("Disconnected from Gemini Live API")
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
        finally:
            self._update_connection_state(ConnectionState.DISCONNECTED)
    
    async def send_text(self, text: str):
        """
        Send a text message to the Gemini Live API.
        
        Args:
            text: Text content to send
        """
        if not self._check_connection():
            return
        
        try:
            message = {
                "type": "text",
                "content": text,
                "timestamp": time.time()
            }
            await self.websocket.send(json.dumps(message))
            self.logger.debug(f"Sent text message: {text[:50]}...")
        except Exception as e:
            self._handle_error(f"Error sending text message: {e}")
    
    async def send_audio(self, audio_data: bytes, sample_rate: int = 16000):
        """
        Send audio data to the Gemini Live API.
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Sample rate of the audio in Hz
        """
        if not self._check_connection():
            return
        
        try:
            # Convert audio data to base64 for transmission
            import base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            message = {
                "type": "audio",
                "content": audio_base64,
                "metadata": {
                    "sample_rate": sample_rate,
                    "encoding": "LINEAR16"
                },
                "timestamp": time.time()
            }
            await self.websocket.send(json.dumps(message))
            self.logger.debug(f"Sent audio data: {len(audio_data)} bytes")
        except Exception as e:
            self._handle_error(f"Error sending audio data: {e}")
    
    async def send_video_frame(self, video_frame: bytes, width: int, height: int):
        """
        Send a video frame to the Gemini Live API.
        
        Args:
            video_frame: Raw video frame bytes (JPEG/PNG encoded)
            width: Width of the video frame in pixels
            height: Height of the video frame in pixels
        """
        if not self._check_connection():
            return
        
        try:
            # Convert video frame to base64 for transmission
            import base64
            frame_base64 = base64.b64encode(video_frame).decode('utf-8')
            
            message = {
                "type": "video",
                "content": frame_base64,
                "metadata": {
                    "width": width,
                    "height": height,
                    "format": "jpeg"  # Assuming JPEG format, adjust if needed
                },
                "timestamp": time.time()
            }
            await self.websocket.send(json.dumps(message))
            self.logger.debug(f"Sent video frame: {len(video_frame)} bytes")
        except Exception as e:
            self._handle_error(f"Error sending video frame: {e}")
    
    async def send_image(self, image_data: bytes):
        """
        Send an image to the Gemini Live API.
        
        Args:
            image_data: Raw image bytes (JPEG/PNG encoded)
        """
        if not self._check_connection():
            return
        
        try:
            # Convert image to base64 for transmission
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            message = {
                "type": "image",
                "content": image_base64,
                "timestamp": time.time()
            }
            await self.websocket.send(json.dumps(message))
            self.logger.debug(f"Sent image: {len(image_data)} bytes")
        except Exception as e:
            self._handle_error(f"Error sending image: {e}")
    
    async def send_system_message(self, system_instructions: str):
        """
        Send system instructions to the Gemini Live API.
        
        Args:
            system_instructions: System instructions to configure model behavior
        """
        if not self._check_connection():
            return
        
        try:
            message = {
                "type": "system",
                "content": system_instructions,
                "timestamp": time.time()
            }
            await self.websocket.send(json.dumps(message))
            self.logger.debug(f"Sent system instructions: {system_instructions[:50]}...")
        except Exception as e:
            self._handle_error(f"Error sending system instructions: {e}")
    
    async def _message_listener(self):
        """Listen for messages from the Gemini Live API and process them."""
        if not self.websocket:
            self.logger.error("WebSocket connection not established")
            return
        
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    self._process_message(data)
                except json.JSONDecodeError:
                    self.logger.error(f"Failed to parse message: {message}")
        except websockets.exceptions.ConnectionClosed as e:
            self._update_connection_state(ConnectionState.DISCONNECTED)
            self.logger.info(f"WebSocket connection closed: {e}")
            if self.callbacks["on_close"]:
                self.callbacks["on_close"](str(e))
        except Exception as e:
            self._handle_error(f"Error in message listener: {e}")
    
    def _process_message(self, data: Dict):
        """
        Process a message received from the Gemini Live API.
        
        Args:
            data: Message data as a dictionary
        """
        message_type = data.get("type")
        content = data.get("content")
        
        if not message_type or not content:
            self.logger.warning(f"Received malformed message: {data}")
            return
        
        self.logger.debug(f"Received {message_type} message")
        
        if self.callbacks["on_message"]:
            self.callbacks["on_message"](message_type, content, data)
    
    def _check_connection(self) -> bool:
        """
        Check if the WebSocket connection is established.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self.connection_state != ConnectionState.CONNECTED or not self.websocket:
            self.logger.error(f"Not connected to Gemini Live API (current state: {self.connection_state.name})")
            return False
        return True
    
    def _update_connection_state(self, state: ConnectionState):
        """
        Update the connection state and trigger the state change callback.
        
        Args:
            state: New connection state
        """
        self.connection_state = state
        self.logger.debug(f"Connection state changed to: {state.name}")
        
        if self.callbacks["on_state_change"]:
            self.callbacks["on_state_change"](state)
    
    def _handle_error(self, error_message: str):
        """
        Handle an error by logging it and triggering the error callback.
        
        Args:
            error_message: Error message to log and send to callback
        """
        self.logger.error(error_message)
        
        if self.callbacks["on_error"]:
            self.callbacks["on_error"](error_message)

# Example usage
async def example_usage():
    # Create a provider instance
    provider = GeminiLiveProvider()
    
    # Define callback functions
    def on_message(message_type, content, data):
        print(f"Received {message_type} message: {content[:100]}...")
    
    def on_error(error):
        print(f"Error: {error}")
    
    def on_state_change(state):
        print(f"Connection state changed to: {state.name}")
    
    # Register callbacks
    provider.register_callback("on_message", on_message)
    provider.register_callback("on_error", on_error)
    provider.register_callback("on_state_change", on_state_change)
    
    # Connect to the API
    await provider.connect(system_instructions="You are Dr. TARDIS, a helpful technical assistant.")
    
    # Send a text message
    await provider.send_text("Hello, I need help with my ApexAgent installation.")
    
    # Wait for responses
    await asyncio.sleep(5)
    
    # Disconnect
    await provider.disconnect()

if __name__ == "__main__":
    asyncio.run(example_usage())
