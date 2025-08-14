"""
Dr. TARDIS Integration with Gemini Live API

This module integrates the Dr. TARDIS expert agent system with the Gemini Live API,
enabling multimodal interactions through text, audio, and video.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

from .gemini_live_provider import GeminiLiveProvider, ConnectionState, MessageType
from .session_manager import SessionManager
from .gemini_key_manager import GeminiKeyManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DrTardisGeminiIntegration:
    """
    Integrates the Dr. TARDIS expert agent system with the Gemini Live API.
    
    This class serves as the main entry point for the integration, providing a high-level
    interface for creating and managing multimodal conversations with Dr. TARDIS.
    
    Attributes:
        session_manager (SessionManager): Manager for Gemini Live API sessions
        key_manager (GeminiKeyManager): Manager for API keys
        logger (logging.Logger): Logger for the integration
    """
    
    def __init__(self, max_sessions: int = 10, idle_timeout: int = 300):
        """
        Initialize the Dr. TARDIS Gemini Integration.
        
        Args:
            max_sessions: Maximum number of concurrent sessions
            idle_timeout: Timeout in seconds for idle sessions
        """
        self.session_manager = SessionManager(max_sessions=max_sessions, idle_timeout=idle_timeout)
        self.key_manager = GeminiKeyManager()
        self.logger = logging.getLogger("DrTardisGeminiIntegration")
        self.logger.info("DrTardisGeminiIntegration initialized")
        
        # Dr. TARDIS system instructions
        self.system_instructions = """
        You are Dr. TARDIS (Technical Assistance, Remote Diagnostics, Installation, and Support), 
        an expert agent designed to provide technical assistance, explain system activities, 
        and support users with ApexAgent installation and usage.
        
        Your capabilities include:
        1. Providing technical support for ApexAgent
        2. Explaining ongoing system activities
        3. Assisting with installation and configuration
        4. Diagnosing and troubleshooting issues
        5. Explaining broader concepts about projects and agent activity
        
        You should maintain a helpful, knowledgeable, and professional tone while being accessible
        to users of all technical levels. Adapt your explanations based on the user's expertise.
        
        When providing technical assistance:
        - Ask clarifying questions when needed
        - Provide step-by-step instructions
        - Explain the reasoning behind recommendations
        - Offer alternative solutions when appropriate
        
        For security reasons, you should never:
        - Share internal system details that could compromise security
        - Provide access to restricted functionality
        - Override security protocols
        - Share API keys or credentials
        
        You have access to the ApexAgent knowledge base and can retrieve information about
        system architecture, installation procedures, troubleshooting guides, and FAQs.
        """
    
    async def start(self):
        """Start the integration and initialize components."""
        await self.session_manager.start()
        self.logger.info("DrTardisGeminiIntegration started")
    
    async def stop(self):
        """Stop the integration and clean up resources."""
        await self.session_manager.stop()
        self.logger.info("DrTardisGeminiIntegration stopped")
    
    async def create_conversation(self, api_key_id: str = "default", 
                                model_name: str = "gemini-1.5-pro-live") -> str:
        """
        Create a new conversation with Dr. TARDIS.
        
        Args:
            api_key_id: ID of the API key to use
            model_name: Name of the Gemini model to use
            
        Returns:
            str: Conversation ID for the new conversation
        """
        # Get the API key
        api_key = self.key_manager.get_api_key(api_key_id)
        if not api_key:
            raise ValueError(f"API key with ID '{api_key_id}' not found")
        
        # Create a new session
        conversation_id = await self.session_manager.create_session(
            api_key=api_key,
            model_name=model_name,
            system_instructions=self.system_instructions
        )
        
        self.logger.info(f"Created conversation {conversation_id} with Dr. TARDIS")
        return conversation_id
    
    async def end_conversation(self, conversation_id: str):
        """
        End a conversation with Dr. TARDIS.
        
        Args:
            conversation_id: ID of the conversation to end
        """
        await self.session_manager.close_session(conversation_id)
        self.logger.info(f"Ended conversation {conversation_id}")
    
    def register_conversation_callbacks(self, conversation_id: str, 
                                      on_message: Optional[Callable] = None,
                                      on_error: Optional[Callable] = None,
                                      on_state_change: Optional[Callable] = None):
        """
        Register callbacks for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            on_message: Callback for received messages
            on_error: Callback for errors
            on_state_change: Callback for state changes
        """
        if on_message:
            self.session_manager.register_session_callback(conversation_id, "on_message", on_message)
        
        if on_error:
            self.session_manager.register_session_callback(conversation_id, "on_error", on_error)
        
        if on_state_change:
            self.session_manager.register_session_callback(conversation_id, "on_state_change", on_state_change)
    
    async def send_text(self, conversation_id: str, text: str):
        """
        Send a text message to Dr. TARDIS.
        
        Args:
            conversation_id: ID of the conversation
            text: Text message to send
        """
        await self.session_manager.send_text(conversation_id, text)
        self.logger.debug(f"Sent text message in conversation {conversation_id}")
    
    async def send_audio(self, conversation_id: str, audio_data: bytes, sample_rate: int = 16000):
        """
        Send audio to Dr. TARDIS.
        
        Args:
            conversation_id: ID of the conversation
            audio_data: Raw audio bytes
            sample_rate: Sample rate of the audio in Hz
        """
        await self.session_manager.send_audio(conversation_id, audio_data, sample_rate)
        self.logger.debug(f"Sent audio in conversation {conversation_id}")
    
    async def send_video_frame(self, conversation_id: str, video_frame: bytes, width: int, height: int):
        """
        Send a video frame to Dr. TARDIS.
        
        Args:
            conversation_id: ID of the conversation
            video_frame: Raw video frame bytes
            width: Width of the video frame in pixels
            height: Height of the video frame in pixels
        """
        await self.session_manager.send_video_frame(conversation_id, video_frame, width, height)
        self.logger.debug(f"Sent video frame in conversation {conversation_id}")
    
    def get_conversation_metrics(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dict: Conversation metrics or None if conversation not found
        """
        return self.session_manager.get_session_metrics(conversation_id)
    
    def get_all_conversation_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all active conversations.
        
        Returns:
            Dict: Dictionary of conversation IDs to metrics
        """
        return self.session_manager.get_all_session_metrics()
    
    def configure_api_key(self, api_key: str, key_id: str = "default") -> bool:
        """
        Configure an API key for use with Dr. TARDIS.
        
        Args:
            api_key: Google API key
            key_id: Identifier for the API key
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.key_manager.store_api_key(key_id, api_key)
    
    def import_api_key_from_env(self, env_var: str = "GOOGLE_API_KEY", key_id: str = "default") -> bool:
        """
        Import an API key from an environment variable.
        
        Args:
            env_var: Name of the environment variable
            key_id: Identifier for the API key
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.key_manager.import_from_env(env_var, key_id)
    
    def import_api_key_from_file(self, file_path: str, key_id: str = "default") -> bool:
        """
        Import an API key from a file.
        
        Args:
            file_path: Path to the file containing the API key
            key_id: Identifier for the API key
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.key_manager.import_from_file(file_path, key_id)

# Example usage
async def example_usage():
    # Create the integration
    integration = DrTardisGeminiIntegration()
    await integration.start()
    
    try:
        # Configure API key from environment
        if not integration.import_api_key_from_env():
            print("Failed to import API key from environment")
            return
        
        # Define callbacks
        def on_message(msg_type, content, data):
            print(f"Dr. TARDIS: {content}")
        
        def on_error(error):
            print(f"Error: {error}")
        
        # Create a conversation
        conversation_id = await integration.create_conversation()
        
        # Register callbacks
        integration.register_conversation_callbacks(
            conversation_id,
            on_message=on_message,
            on_error=on_error
        )
        
        # Send a message
        await integration.send_text(conversation_id, "Hello Dr. TARDIS, I need help installing ApexAgent.")
        
        # Wait for responses
        await asyncio.sleep(5)
        
        # Get conversation metrics
        metrics = integration.get_conversation_metrics(conversation_id)
        print(f"Conversation metrics: {metrics}")
        
        # End the conversation
        await integration.end_conversation(conversation_id)
        
    finally:
        # Stop the integration
        await integration.stop()

if __name__ == "__main__":
    asyncio.run(example_usage())
