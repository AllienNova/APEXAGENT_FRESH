"""
Example Plugin: Hello World

This is a simple example plugin for the ApexAgent plugin system.
It demonstrates basic plugin functionality including lifecycle hooks,
API registration, and event handling.
"""

import logging
from typing import Dict, Any, List

from core.base_plugin import BasePlugin

# Configure logging
logger = logging.getLogger(__name__)

class HelloWorldPlugin(BasePlugin):
    """
    A simple Hello World plugin that demonstrates basic plugin functionality.
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any]):
        """
        Initialize the plugin.
        
        Args:
            plugin_id: Unique identifier for this plugin instance
            config: Configuration dictionary for this plugin
        """
        super().__init__(plugin_id, config)
        self.greeting = config.get("greeting", "Hello, World!")
        self.counter = 0
        logger.info(f"HelloWorldPlugin initialized with ID: {plugin_id}")
    
    def on_load(self) -> None:
        """Called when the plugin is loaded."""
        logger.info(f"HelloWorldPlugin {self.plugin_id} loaded")
    
    def on_start(self) -> None:
        """Called when the plugin is started."""
        logger.info(f"HelloWorldPlugin {self.plugin_id} started")
        logger.info(f"Initial greeting: {self.greeting}")
    
    def on_stop(self) -> None:
        """Called when the plugin is stopped."""
        logger.info(f"HelloWorldPlugin {self.plugin_id} stopped")
        logger.info(f"Final counter value: {self.counter}")
    
    def on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        logger.info(f"HelloWorldPlugin {self.plugin_id} unloaded")
    
    def register_apis(self, api_context):
        """
        Register plugin APIs.
        
        Args:
            api_context: API registration context
        """
        # Register a simple greeting API
        api_context.register_endpoint(
            "get_greeting",
            self.get_greeting,
            version="1.0.0",
            description="Get the current greeting message",
            returns={"type": "str"}
        )
        
        # Register a counter API
        api_context.register_endpoint(
            "increment_counter",
            self.increment_counter,
            version="1.0.0",
            description="Increment the counter and return the new value",
            returns={"type": "int"}
        )
        
        # Register an API to change the greeting
        api_context.register_endpoint(
            "set_greeting",
            self.set_greeting,
            version="1.0.0",
            description="Set a new greeting message",
            params={"greeting": {"type": "str", "required": True}}
        )
        
        # Use the decorator syntax for API registration
        @api_context.api_endpoint(
            version="1.0.0",
            description="Get plugin statistics"
        )
        def get_stats(self):
            return {
                "greeting": self.greeting,
                "counter": self.counter,
                "plugin_id": self.plugin_id
            }
    
    def register_event_handlers(self, event_context):
        """
        Register event handlers.
        
        Args:
            event_context: Event registration context
        """
        # Register a handler for system.startup events
        event_context.register_handler(
            "system.startup",
            self.handle_system_startup
        )
        
        # Register a handler for system.shutdown events
        event_context.register_handler(
            "system.shutdown",
            self.handle_system_shutdown
        )
        
        # Use the decorator syntax for event handler registration
        @event_context.event_handler("plugin.loaded")
        def handle_plugin_loaded(self, event):
            logger.info(f"HelloWorldPlugin {self.plugin_id} detected plugin loaded: {event.data.get('plugin_id')}")
    
    def get_greeting(self) -> str:
        """
        Get the current greeting message.
        
        Returns:
            Current greeting message
        """
        return self.greeting
    
    def set_greeting(self, greeting: str) -> None:
        """
        Set a new greeting message.
        
        Args:
            greeting: New greeting message
        """
        self.greeting = greeting
        logger.info(f"Greeting changed to: {self.greeting}")
    
    def increment_counter(self) -> int:
        """
        Increment the counter and return the new value.
        
        Returns:
            New counter value
        """
        self.counter += 1
        return self.counter
    
    def handle_system_startup(self, event):
        """
        Handle system startup events.
        
        Args:
            event: Event object
        """
        logger.info(f"HelloWorldPlugin {self.plugin_id} received system startup event")
        logger.info(f"System started at: {event.data.get('timestamp')}")
    
    def handle_system_shutdown(self, event):
        """
        Handle system shutdown events.
        
        Args:
            event: Event object
        """
        logger.info(f"HelloWorldPlugin {self.plugin_id} received system shutdown event")
        logger.info(f"System shutting down at: {event.data.get('timestamp')}")


# Plugin manifest
PLUGIN_MANIFEST = {
    "name": "Hello World Plugin",
    "version": "1.0.0",
    "description": "A simple Hello World plugin for ApexAgent",
    "author": "ApexAgent Team",
    "license": "MIT",
    "main_class": "HelloWorldPlugin",
    "permissions": [
        "event.subscribe",
        "event.emit",
        "api.register"
    ],
    "dependencies": [],
    "config_schema": {
        "greeting": {
            "type": "string",
            "default": "Hello, World!",
            "description": "Initial greeting message"
        }
    }
}
