"""
Conversation UI Components for Dr. TARDIS

This module provides conversation UI components for the Dr. TARDIS system,
including conversation display, history management, and interaction controls.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import logging
import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from enum import Enum, auto
import threading
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MessageType(Enum):
    """
    Enumeration of message types in a conversation.
    
    Types:
        USER: Message from the user
        SYSTEM: Message from the system (Dr. TARDIS)
        INFO: Informational message
        ERROR: Error message
        WARNING: Warning message
    """
    USER = auto()
    SYSTEM = auto()
    INFO = auto()
    ERROR = auto()
    WARNING = auto()


class ConversationUIComponent:
    """
    Provides conversation UI functionality for the Dr. TARDIS system.
    
    This class manages conversation display, history, and interaction controls.
    
    Attributes:
        logger (logging.Logger): Logger for conversation UI
        current_conversation_id (str): ID of the current conversation
        conversations (Dict): Dictionary of conversations
        callbacks (Dict): Dictionary of registered callbacks
    """
    
    def __init__(self):
        """
        Initialize the Conversation UI Component.
        """
        self.logger = logging.getLogger("ConversationUIComponent")
        self.current_conversation_id = None
        self.conversations = {}
        self.callbacks = {
            "message_added": [],
            "conversation_created": [],
            "conversation_switched": [],
            "conversation_deleted": []
        }
        
        # UI settings
        self.settings = {
            "max_displayed_messages": 50,
            "timestamp_format": "%H:%M:%S",
            "show_typing_indicator": True,
            "auto_scroll": True,
            "message_grouping": True,
            "show_system_messages": True
        }
        
        self.logger.info("ConversationUIComponent initialized")
    
    def create_conversation(self, title: str = None) -> str:
        """
        Create a new conversation.
        
        Args:
            title: Title of the conversation (default: auto-generated)
            
        Returns:
            str: ID of the created conversation
        """
        # Generate conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Generate title if not provided
        if title is None:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create conversation
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "title": title,
            "created_at": time.time(),
            "updated_at": time.time(),
            "messages": [],
            "metadata": {}
        }
        
        # Log conversation creation
        self.logger.info(f"Created conversation: {title} (ID: {conversation_id})")
        
        # Set as current conversation if none is set
        if self.current_conversation_id is None:
            self.current_conversation_id = conversation_id
        
        # Trigger callbacks
        self._trigger_callbacks("conversation_created", {
            "conversation_id": conversation_id,
            "title": title
        })
        
        return conversation_id
    
    def switch_conversation(self, conversation_id: str) -> bool:
        """
        Switch to a different conversation.
        
        Args:
            conversation_id: ID of the conversation to switch to
            
        Returns:
            bool: Whether the switch was successful
        """
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation with ID {conversation_id} not found")
            return False
        
        if conversation_id == self.current_conversation_id:
            return True
        
        old_conversation_id = self.current_conversation_id
        self.current_conversation_id = conversation_id
        
        # Log conversation switch
        self.logger.info(f"Switched conversation: {old_conversation_id} -> {conversation_id}")
        
        # Trigger callbacks
        self._trigger_callbacks("conversation_switched", {
            "old_conversation_id": old_conversation_id,
            "new_conversation_id": conversation_id
        })
        
        return True
    
    def get_current_conversation_id(self) -> Optional[str]:
        """
        Get the ID of the current conversation.
        
        Returns:
            str or None: ID of the current conversation, or None if no conversation is active
        """
        return self.current_conversation_id
    
    def get_conversation(self, conversation_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to get (default: current conversation)
            
        Returns:
            Dict or None: Conversation data, or None if not found
        """
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        if conversation_id is None:
            self.logger.warning("No current conversation")
            return None
        
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation with ID {conversation_id} not found")
            return None
        
        return self.conversations[conversation_id].copy()
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Get all conversations.
        
        Returns:
            List: List of all conversations
        """
        return [conv.copy() for conv in self.conversations.values()]
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: ID of the conversation to delete
            
        Returns:
            bool: Whether the deletion was successful
        """
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation with ID {conversation_id} not found")
            return False
        
        # Get conversation title for logging
        title = self.conversations[conversation_id]["title"]
        
        # Delete conversation
        del self.conversations[conversation_id]
        
        # Log conversation deletion
        self.logger.info(f"Deleted conversation: {title} (ID: {conversation_id})")
        
        # If current conversation was deleted, switch to another one
        if conversation_id == self.current_conversation_id:
            if self.conversations:
                self.current_conversation_id = next(iter(self.conversations.keys()))
            else:
                self.current_conversation_id = None
        
        # Trigger callbacks
        self._trigger_callbacks("conversation_deleted", {
            "conversation_id": conversation_id,
            "title": title
        })
        
        return True
    
    def add_message(self, content: str, message_type: MessageType, 
                  conversation_id: str = None, metadata: Dict[str, Any] = None) -> str:
        """
        Add a message to a conversation.
        
        Args:
            content: Message content
            message_type: Type of message
            conversation_id: ID of the conversation to add to (default: current conversation)
            metadata: Additional metadata for the message
            
        Returns:
            str: ID of the added message
        """
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        if conversation_id is None:
            self.logger.warning("No current conversation")
            return None
        
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation with ID {conversation_id} not found")
            return None
        
        # Generate message ID
        message_id = str(uuid.uuid4())
        
        # Create message
        message = {
            "id": message_id,
            "content": content,
            "type": message_type,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        # Add message to conversation
        self.conversations[conversation_id]["messages"].append(message)
        
        # Update conversation timestamp
        self.conversations[conversation_id]["updated_at"] = time.time()
        
        # Log message addition
        self.logger.info(f"Added message to conversation {conversation_id}: "
                       f"{message_type} (ID: {message_id})")
        
        # Trigger callbacks
        self._trigger_callbacks("message_added", {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "message_type": message_type
        })
        
        return message_id
    
    def get_message(self, message_id: str, conversation_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a message by ID.
        
        Args:
            message_id: ID of the message to get
            conversation_id: ID of the conversation to get from (default: current conversation)
            
        Returns:
            Dict or None: Message data, or None if not found
        """
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        if conversation_id is None:
            self.logger.warning("No current conversation")
            return None
        
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation with ID {conversation_id} not found")
            return None
        
        # Find message in conversation
        for message in self.conversations[conversation_id]["messages"]:
            if message["id"] == message_id:
                return message.copy()
        
        self.logger.warning(f"Message with ID {message_id} not found in conversation {conversation_id}")
        return None
    
    def get_messages(self, conversation_id: str = None, 
                   limit: int = None, message_type: MessageType = None) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation.
        
        Args:
            conversation_id: ID of the conversation to get from (default: current conversation)
            limit: Maximum number of messages to get (default: all)
            message_type: Filter by message type (default: all types)
            
        Returns:
            List: List of messages
        """
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        if conversation_id is None:
            self.logger.warning("No current conversation")
            return []
        
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation with ID {conversation_id} not found")
            return []
        
        # Get messages
        messages = self.conversations[conversation_id]["messages"]
        
        # Filter by message type if specified
        if message_type is not None:
            messages = [msg for msg in messages if msg["type"] == message_type]
        
        # Limit number of messages if specified
        if limit is not None:
            messages = messages[-limit:]
        
        return [msg.copy() for msg in messages]
    
    def update_settings(self, settings: Dict[str, Any]):
        """
        Update UI settings.
        
        Args:
            settings: Dictionary of settings to update
        """
        old_settings = self.settings.copy()
        
        # Update settings
        for key, value in settings.items():
            if key in self.settings:
                self.settings[key] = value
            else:
                self.logger.warning(f"Unknown setting: {key}")
        
        # Log settings change
        self.logger.info(f"UI settings updated: {old_settings} -> {self.settings}")
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get the current UI settings.
        
        Returns:
            Dict: Current UI settings
        """
        return self.settings.copy()
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: Event type to register for
            callback: Callback function to register
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            self.logger.debug(f"Registered callback for event type: {event_type}")
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def unregister_callback(self, event_type: str, callback: Callable):
        """
        Unregister a callback for a specific event type.
        
        Args:
            event_type: Event type to unregister from
            callback: Callback function to unregister
        """
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            self.logger.debug(f"Unregistered callback for event type: {event_type}")
    
    def _trigger_callbacks(self, event_type: str, event_data: Dict[str, Any]):
        """
        Trigger callbacks for a specific event type.
        
        Args:
            event_type: Event type to trigger
            event_data: Event data to pass to callbacks
        """
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Error in callback for event type {event_type}: {e}")


class ConversationHistoryManager:
    """
    Manages conversation history for the Dr. TARDIS system.
    
    This class provides functionality for searching, exporting, and analyzing
    conversation history.
    
    Attributes:
        logger (logging.Logger): Logger for conversation history manager
        conversation_ui (ConversationUIComponent): Conversation UI component
    """
    
    def __init__(self, conversation_ui: ConversationUIComponent):
        """
        Initialize the Conversation History Manager.
        
        Args:
            conversation_ui: Conversation UI component
        """
        self.logger = logging.getLogger("ConversationHistoryManager")
        self.conversation_ui = conversation_ui
        
        # Register for conversation events
        self.conversation_ui.register_callback("conversation_created", self._on_conversation_created)
        self.conversation_ui.register_callback("conversation_deleted", self._on_conversation_deleted)
        self.conversation_ui.register_callback("message_added", self._on_message_added)
        
        self.logger.info("ConversationHistoryManager initialized")
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for conversations containing the query.
        
        Args:
            query: Search query
            
        Returns:
            List: List of matching conversations
        """
        query = query.lower()
        matching_conversations = []
        
        # Get all conversations
        all_conversations = self.conversation_ui.get_all_conversations()
        
        # Search in conversation titles and messages
        for conversation in all_conversations:
            # Check title
            if query in conversation["title"].lower():
                matching_conversations.append(conversation)
                continue
            
            # Check messages
            for message in conversation["messages"]:
                if query in message["content"].lower():
                    matching_conversations.append(conversation)
                    break
        
        self.logger.info(f"Found {len(matching_conversations)} conversations matching query: {query}")
        return matching_conversations
    
    def search_messages(self, query: str, conversation_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for messages containing the query.
        
        Args:
            query: Search query
            conversation_id: ID of the conversation to search in (default: all conversations)
            
        Returns:
            List: List of matching messages with conversation info
        """
        query = query.lower()
        matching_messages = []
        
        # Determine which conversations to search
        if conversation_id is not None:
            if conversation_id not in self.conversation_ui.conversations:
                self.logger.warning(f"Conversation with ID {conversation_id} not found")
                return []
            conversations = [self.conversation_ui.conversations[conversation_id]]
        else:
            conversations = self.conversation_ui.conversations.values()
        
        # Search in messages
        for conversation in conversations:
            for message in conversation["messages"]:
                if query in message["content"].lower():
                    # Add message with conversation info
                    matching_messages.append({
                        "message": message.copy(),
                        "conversation_id": conversation["id"],
                        "conversation_title": conversation["title"]
                    })
        
        self.logger.info(f"Found {len(matching_messages)} messages matching query: {query}")
        return matching_messages
    
    def export_conversation(self, conversation_id: str = None, 
                          format: str = "json") -> Optional[str]:
        """
        Export a conversation to a specific format.
        
        Args:
            conversation_id: ID of the conversation to export (default: current conversation)
            format: Export format (json, text, html)
            
        Returns:
            str or None: Exported conversation, or None if export failed
        """
        # Get conversation
        conversation = self.conversation_ui.get_conversation(conversation_id)
        if conversation is None:
            return None
        
        # Export based on format
        if format == "json":
            return json.dumps(conversation, indent=2)
        elif format == "text":
            return self._export_as_text(conversation)
        elif format == "html":
            return self._export_as_html(conversation)
        else:
            self.logger.warning(f"Unknown export format: {format}")
            return None
    
    def _export_as_text(self, conversation: Dict[str, Any]) -> str:
        """
        Export a conversation as plain text.
        
        Args:
            conversation: Conversation data
            
        Returns:
            str: Conversation as plain text
        """
        lines = [f"Conversation: {conversation['title']}", ""]
        
        # Format timestamp
        timestamp_format = self.conversation_ui.settings["timestamp_format"]
        
        # Add messages
        for message in conversation["messages"]:
            # Format timestamp
            timestamp = datetime.fromtimestamp(message["timestamp"]).strftime(timestamp_format)
            
            # Format message type
            if message["type"] == MessageType.USER:
                sender = "User"
            elif message["type"] == MessageType.SYSTEM:
                sender = "Dr. TARDIS"
            else:
                sender = str(message["type"]).split(".")[1]
            
            # Add message line
            lines.append(f"[{timestamp}] {sender}: {message['content']}")
        
        return "\n".join(lines)
    
    def _export_as_html(self, conversation: Dict[str, Any]) -> str:
        """
        Export a conversation as HTML.
        
        Args:
            conversation: Conversation data
            
        Returns:
            str: Conversation as HTML
        """
        # Start HTML
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>Conversation: {conversation['title']}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "h1 { color: #333; }",
            ".message { margin-bottom: 10px; padding: 10px; border-radius: 5px; }",
            ".user { background-color: #e6f7ff; text-align: right; }",
            ".system { background-color: #f0f0f0; }",
            ".info { background-color: #e6ffe6; }",
            ".warning { background-color: #fff9e6; }",
            ".error { background-color: #ffe6e6; }",
            ".timestamp { color: #888; font-size: 0.8em; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>Conversation: {conversation['title']}</h1>"
        ]
        
        # Format timestamp
        timestamp_format = self.conversation_ui.settings["timestamp_format"]
        
        # Add messages
        for message in conversation["messages"]:
            # Format timestamp
            timestamp = datetime.fromtimestamp(message["timestamp"]).strftime(timestamp_format)
            
            # Determine message class and sender
            if message["type"] == MessageType.USER:
                msg_class = "user"
                sender = "User"
            elif message["type"] == MessageType.SYSTEM:
                msg_class = "system"
                sender = "Dr. TARDIS"
            elif message["type"] == MessageType.INFO:
                msg_class = "info"
                sender = "Info"
            elif message["type"] == MessageType.WARNING:
                msg_class = "warning"
                sender = "Warning"
            elif message["type"] == MessageType.ERROR:
                msg_class = "error"
                sender = "Error"
            else:
                msg_class = ""
                sender = str(message["type"]).split(".")[1]
            
            # Add message
            html.append(f'<div class="message {msg_class}">')
            html.append(f'<div class="sender">{sender}</div>')
            html.append(f'<div class="content">{message["content"]}</div>')
            html.append(f'<div class="timestamp">{timestamp}</div>')
            html.append('</div>')
        
        # End HTML
        html.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html)
    
    def analyze_conversation(self, conversation_id: str = None) -> Dict[str, Any]:
        """
        Analyze a conversation for statistics and insights.
        
        Args:
            conversation_id: ID of the conversation to analyze (default: current conversation)
            
        Returns:
            Dict: Analysis results
        """
        # Get conversation
        conversation = self.conversation_ui.get_conversation(conversation_id)
        if conversation is None:
            return {}
        
        # Initialize analysis
        analysis = {
            "message_count": len(conversation["messages"]),
            "message_types": {},
            "user_message_count": 0,
            "system_message_count": 0,
            "average_message_length": 0,
            "conversation_duration": 0,
            "response_times": []
        }
        
        # Count message types
        for message in conversation["messages"]:
            msg_type = str(message["type"]).split(".")[1]
            if msg_type in analysis["message_types"]:
                analysis["message_types"][msg_type] += 1
            else:
                analysis["message_types"][msg_type] = 1
            
            # Count user and system messages
            if message["type"] == MessageType.USER:
                analysis["user_message_count"] += 1
            elif message["type"] == MessageType.SYSTEM:
                analysis["system_message_count"] += 1
            
            # Sum message lengths
            analysis["average_message_length"] += len(message["content"])
        
        # Calculate average message length
        if analysis["message_count"] > 0:
            analysis["average_message_length"] /= analysis["message_count"]
        
        # Calculate conversation duration
        if analysis["message_count"] >= 2:
            first_msg = conversation["messages"][0]
            last_msg = conversation["messages"][-1]
            analysis["conversation_duration"] = last_msg["timestamp"] - first_msg["timestamp"]
        
        # Calculate response times
        last_user_msg_time = None
        for message in conversation["messages"]:
            if message["type"] == MessageType.USER:
                last_user_msg_time = message["timestamp"]
            elif message["type"] == MessageType.SYSTEM and last_user_msg_time is not None:
                response_time = message["timestamp"] - last_user_msg_time
                analysis["response_times"].append(response_time)
                last_user_msg_time = None
        
        # Calculate average response time
        if analysis["response_times"]:
            analysis["average_response_time"] = sum(analysis["response_times"]) / len(analysis["response_times"])
        else:
            analysis["average_response_time"] = 0
        
        return analysis
    
    def _on_conversation_created(self, event_data: Dict[str, Any]):
        """
        Handle conversation creation events.
        
        Args:
            event_data: Event data
        """
        conversation_id = event_data["conversation_id"]
        title = event_data["title"]
        
        self.logger.debug(f"Conversation created: {title} (ID: {conversation_id})")
    
    def _on_conversation_deleted(self, event_data: Dict[str, Any]):
        """
        Handle conversation deletion events.
        
        Args:
            event_data: Event data
        """
        conversation_id = event_data["conversation_id"]
        title = event_data["title"]
        
        self.logger.debug(f"Conversation deleted: {title} (ID: {conversation_id})")
    
    def _on_message_added(self, event_data: Dict[str, Any]):
        """
        Handle message addition events.
        
        Args:
            event_data: Event data
        """
        conversation_id = event_data["conversation_id"]
        message_id = event_data["message_id"]
        message_type = event_data["message_type"]
        
        self.logger.debug(f"Message added to conversation {conversation_id}: "
                        f"{message_type} (ID: {message_id})")


# Example usage
def example_usage():
    # Create conversation UI component
    conversation_ui = ConversationUIComponent()
    
    # Create conversation history manager
    history_manager = ConversationHistoryManager(conversation_ui)
    
    # Create a conversation
    conversation_id = conversation_ui.create_conversation("Test Conversation")
    
    # Add messages
    conversation_ui.add_message("Hello, Dr. TARDIS!", MessageType.USER)
    conversation_ui.add_message("Hello! How can I assist you today?", MessageType.SYSTEM)
    conversation_ui.add_message("I need help with my computer.", MessageType.USER)
    conversation_ui.add_message("I'd be happy to help. What seems to be the problem?", MessageType.SYSTEM)
    
    # Get messages
    messages = conversation_ui.get_messages()
    print(f"Messages: {len(messages)}")
    
    # Export conversation
    text_export = history_manager.export_conversation(format="text")
    print(f"Text export:\n{text_export}")
    
    # Analyze conversation
    analysis = history_manager.analyze_conversation()
    print(f"Analysis: {analysis}")

if __name__ == "__main__":
    example_usage()
