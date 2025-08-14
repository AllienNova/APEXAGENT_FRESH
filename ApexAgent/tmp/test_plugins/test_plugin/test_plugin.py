"""
Test Plugin for ApexAgent plugin system unit testing
"""

class TestPlugin:
    """A simple test plugin for unit testing the plugin system."""
    
    def __init__(self, plugin_id, plugin_config=None):
        """Initialize the test plugin.
        
        Args:
            plugin_id: Unique identifier for this plugin instance
            plugin_config: Optional configuration dictionary
        """
        self.plugin_id = plugin_id
        self.config = plugin_config or {}
        self.initialized = True
        self.active = False
        self.api_endpoints = {}
        self.event_handlers = {}
    
    def start(self):
        """Start the plugin."""
        self.active = True
        return True
    
    def stop(self):
        """Stop the plugin."""
        self.active = False
        return True
    
    def reload(self):
        """Reload the plugin."""
        return True
    
    def register_api_endpoint(self, endpoint_name, handler_fn):
        """Register an API endpoint.
        
        Args:
            endpoint_name: Name of the endpoint
            handler_fn: Function to handle API calls to this endpoint
        """
        self.api_endpoints[endpoint_name] = handler_fn
        return True
    
    def register_event_handler(self, event_type, handler_fn):
        """Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler_fn: Function to handle events of this type
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler_fn)
        return True
    
    def test_method(self):
        """Test method for unit testing."""
        return "Test method called"
    
    def get_info(self):
        """Get plugin information."""
        return {
            "id": self.plugin_id,
            "active": self.active,
            "api_endpoints": list(self.api_endpoints.keys()),
            "event_handlers": {k: len(v) for k, v in self.event_handlers.items()}
        }
