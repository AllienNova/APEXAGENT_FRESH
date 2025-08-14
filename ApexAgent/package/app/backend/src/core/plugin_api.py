"""
Plugin API and Event Hooks Module for ApexAgent

This module provides the API and event hook functionality for the ApexAgent plugin system.
It handles plugin event subscription, event emission, and API integration.
"""

import logging
import inspect
from typing import Dict, List, Any, Optional, Set, Tuple, Callable, Union
from functools import wraps

from src.core.event_system.event import Event
from src.core.event_system.event_manager import EventManager
from src.core.plugin_exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginAPIError
)

# Configure logging
logger = logging.getLogger(__name__)

class PluginEventTypes:
    """Constants for plugin-related event types."""
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_STARTED = "plugin.started"
    PLUGIN_STOPPED = "plugin.stopped"
    PLUGIN_RELOADED = "plugin.reloaded"
    PLUGIN_FAILED = "plugin.failed"
    PLUGIN_API_CALL = "plugin.api.call"
    PLUGIN_API_RESPONSE = "plugin.api.response"
    PLUGIN_API_ERROR = "plugin.api.error"


class PluginAPI:
    """
    Provides API functionality for plugins in the ApexAgent system.
    
    The PluginAPI is responsible for:
    1. Exposing plugin functionality through a consistent API
    2. Managing API versioning and compatibility
    3. Handling API call routing and responses
    4. Providing API documentation and discovery
    """
    
    def __init__(self, plugin_system, event_manager: Optional[EventManager] = None):
        """
        Initialize the PluginAPI.
        
        Args:
            plugin_system: Reference to the plugin system
            event_manager: Optional event manager for API events
        """
        self.plugin_system = plugin_system
        self.event_manager = event_manager
        self.api_endpoints = {}  # Maps endpoint names to handler functions
        self.api_documentation = {}  # Maps endpoint names to documentation
        self.api_versions = {}  # Maps endpoint names to version info
    
    def register_api_endpoint(
        self,
        plugin_id: str,
        endpoint_name: str,
        handler_fn: Callable,
        version: str = "1.0.0",
        description: str = "",
        params: Dict[str, Any] = None,
        returns: Dict[str, Any] = None
    ) -> None:
        """
        Register an API endpoint for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            endpoint_name: Name of the API endpoint
            handler_fn: Function to handle API calls
            version: API version string
            description: Description of the API endpoint
            params: Parameter documentation
            returns: Return value documentation
            
        Raises:
            PluginAPIError: If the endpoint is already registered
        """
        # Create full endpoint name
        full_endpoint = f"{plugin_id}.{endpoint_name}"
        
        # Check if endpoint already exists
        if full_endpoint in self.api_endpoints:
            raise PluginAPIError(f"API endpoint '{full_endpoint}' is already registered")
        
        # Register endpoint
        self.api_endpoints[full_endpoint] = handler_fn
        
        # Store API documentation
        self.api_documentation[full_endpoint] = {
            "plugin_id": plugin_id,
            "endpoint": endpoint_name,
            "description": description,
            "params": params or {},
            "returns": returns or {}
        }
        
        # Store API version
        self.api_versions[full_endpoint] = version
        
        logger.debug(f"Registered API endpoint: {full_endpoint} (v{version})")
    
    def unregister_api_endpoint(self, plugin_id: str, endpoint_name: str) -> None:
        """
        Unregister an API endpoint.
        
        Args:
            plugin_id: ID of the plugin
            endpoint_name: Name of the API endpoint
            
        Raises:
            PluginAPIError: If the endpoint is not registered
        """
        # Create full endpoint name
        full_endpoint = f"{plugin_id}.{endpoint_name}"
        
        # Check if endpoint exists
        if full_endpoint not in self.api_endpoints:
            raise PluginAPIError(f"API endpoint '{full_endpoint}' is not registered")
        
        # Unregister endpoint
        del self.api_endpoints[full_endpoint]
        
        # Remove documentation and version info
        if full_endpoint in self.api_documentation:
            del self.api_documentation[full_endpoint]
        
        if full_endpoint in self.api_versions:
            del self.api_versions[full_endpoint]
        
        logger.debug(f"Unregistered API endpoint: {full_endpoint}")
    
    def call_api(
        self,
        plugin_id: str,
        endpoint_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Call an API endpoint.
        
        Args:
            plugin_id: ID of the plugin
            endpoint_name: Name of the API endpoint
            *args: Positional arguments to pass to the handler
            **kwargs: Keyword arguments to pass to the handler
            
        Returns:
            Result of the API call
            
        Raises:
            PluginNotFoundError: If the plugin is not found
            PluginAPIError: If the endpoint is not registered or the call fails
        """
        # Create full endpoint name
        full_endpoint = f"{plugin_id}.{endpoint_name}"
        
        # Check if endpoint exists
        if full_endpoint not in self.api_endpoints:
            raise PluginAPIError(f"API endpoint '{full_endpoint}' is not registered")
        
        # Get handler function
        handler_fn = self.api_endpoints[full_endpoint]
        
        # Emit API call event
        if self.event_manager:
            event_data = {
                "plugin_id": plugin_id,
                "endpoint": endpoint_name,
                "args": args,
                "kwargs": kwargs
            }
            self.event_manager.emit_event(
                Event(PluginEventTypes.PLUGIN_API_CALL, event_data)
            )
        
        try:
            # Call handler function
            result = handler_fn(*args, **kwargs)
            
            # Emit API response event
            if self.event_manager:
                event_data = {
                    "plugin_id": plugin_id,
                    "endpoint": endpoint_name,
                    "result": result
                }
                self.event_manager.emit_event(
                    Event(PluginEventTypes.PLUGIN_API_RESPONSE, event_data)
                )
            
            return result
            
        except Exception as e:
            # Emit API error event
            if self.event_manager:
                event_data = {
                    "plugin_id": plugin_id,
                    "endpoint": endpoint_name,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                self.event_manager.emit_event(
                    Event(PluginEventTypes.PLUGIN_API_ERROR, event_data)
                )
            
            # Re-raise as PluginAPIError
            raise PluginAPIError(f"API call to '{full_endpoint}' failed: {e}")
    
    def get_api_documentation(self, plugin_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get API documentation.
        
        Args:
            plugin_id: Optional plugin ID to filter by
            
        Returns:
            Dictionary of API documentation
        """
        if plugin_id:
            # Filter by plugin ID
            return {
                endpoint: doc
                for endpoint, doc in self.api_documentation.items()
                if doc["plugin_id"] == plugin_id
            }
        
        return self.api_documentation
    
    def get_api_versions(self, plugin_id: Optional[str] = None) -> Dict[str, str]:
        """
        Get API versions.
        
        Args:
            plugin_id: Optional plugin ID to filter by
            
        Returns:
            Dictionary mapping endpoint names to version strings
        """
        if plugin_id:
            # Filter by plugin ID
            return {
                endpoint: version
                for endpoint, version in self.api_versions.items()
                if endpoint.startswith(f"{plugin_id}.")
            }
        
        return self.api_versions
    
    def register_plugin_apis(self, plugin_id: str) -> None:
        """
        Register all API endpoints for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        # Get plugin instance
        try:
            plugin = self.plugin_system.get_plugin(plugin_id)
        except Exception:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Check if plugin has API registration method
        if hasattr(plugin, 'register_apis') and callable(getattr(plugin, 'register_apis')):
            # Create API registration context
            api_context = PluginAPIRegistrationContext(self, plugin_id)
            
            # Call plugin's API registration method
            plugin.register_apis(api_context)
            
            logger.info(f"Registered APIs for plugin: {plugin_id}")
        else:
            logger.debug(f"Plugin {plugin_id} does not implement register_apis method")
    
    def unregister_plugin_apis(self, plugin_id: str) -> None:
        """
        Unregister all API endpoints for a plugin.
        
        Args:
            plugin_id: ID of the plugin
        """
        # Find all endpoints for this plugin
        endpoints_to_remove = [
            endpoint for endpoint in self.api_endpoints
            if endpoint.startswith(f"{plugin_id}.")
        ]
        
        # Unregister each endpoint
        for endpoint in endpoints_to_remove:
            endpoint_name = endpoint[len(f"{plugin_id}."):]
            try:
                self.unregister_api_endpoint(plugin_id, endpoint_name)
            except Exception as e:
                logger.warning(f"Error unregistering API endpoint {endpoint}: {e}")
        
        logger.info(f"Unregistered {len(endpoints_to_remove)} APIs for plugin: {plugin_id}")


class PluginAPIRegistrationContext:
    """
    Context object for plugin API registration.
    
    This class provides a simplified interface for plugins to register API endpoints.
    """
    
    def __init__(self, plugin_api: PluginAPI, plugin_id: str):
        """
        Initialize the API registration context.
        
        Args:
            plugin_api: Reference to the PluginAPI instance
            plugin_id: ID of the plugin
        """
        self.plugin_api = plugin_api
        self.plugin_id = plugin_id
    
    def register_endpoint(
        self,
        endpoint_name: str,
        handler_fn: Callable,
        version: str = "1.0.0",
        description: str = "",
        params: Dict[str, Any] = None,
        returns: Dict[str, Any] = None
    ) -> None:
        """
        Register an API endpoint.
        
        Args:
            endpoint_name: Name of the API endpoint
            handler_fn: Function to handle API calls
            version: API version string
            description: Description of the API endpoint
            params: Parameter documentation
            returns: Return value documentation
        """
        self.plugin_api.register_api_endpoint(
            self.plugin_id,
            endpoint_name,
            handler_fn,
            version,
            description,
            params,
            returns
        )
    
    def api_endpoint(
        self,
        endpoint_name: Optional[str] = None,
        version: str = "1.0.0",
        description: str = ""
    ) -> Callable:
        """
        Decorator for registering API endpoints.
        
        Args:
            endpoint_name: Optional name of the API endpoint (defaults to function name)
            version: API version string
            description: Description of the API endpoint
            
        Returns:
            Decorator function
        """
        def decorator(func):
            # Get function signature for documentation
            sig = inspect.signature(func)
            params = {}
            for name, param in sig.parameters.items():
                if name == 'self':
                    continue
                
                param_doc = {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                    "required": param.default == inspect.Parameter.empty
                }
                params[name] = param_doc
            
            # Get return type for documentation
            returns = {
                "type": str(func.__annotations__.get('return', 'Any'))
            }
            
            # Register the endpoint
            name = endpoint_name or func.__name__
            self.register_endpoint(
                name,
                func,
                version,
                description or func.__doc__ or "",
                params,
                returns
            )
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        
        return decorator


class PluginEventHooks:
    """
    Manages event hooks for plugins in the ApexAgent system.
    
    The PluginEventHooks is responsible for:
    1. Registering plugin event handlers
    2. Routing events to appropriate plugin handlers
    3. Managing event subscriptions
    """
    
    def __init__(self, plugin_system, event_manager: EventManager):
        """
        Initialize the PluginEventHooks.
        
        Args:
            plugin_system: Reference to the plugin system
            event_manager: Event manager for event handling
        """
        self.plugin_system = plugin_system
        self.event_manager = event_manager
        self.event_handlers = {}  # Maps (plugin_id, event_type) to handler functions
        self.plugin_subscriptions = {}  # Maps plugin_id to list of event types
    
    def register_event_handler(
        self,
        plugin_id: str,
        event_type: str,
        handler_fn: Callable[[Event], None],
        priority: int = 0
    ) -> None:
        """
        Register an event handler for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            event_type: Type of event to handle
            handler_fn: Function to handle the event
            priority: Priority of the handler (higher values = higher priority)
            
        Raises:
            PluginError: If the handler is already registered
        """
        # Create handler key
        handler_key = (plugin_id, event_type)
        
        # Check if handler already exists
        if handler_key in self.event_handlers:
            raise PluginError(f"Event handler for {event_type} is already registered for plugin {plugin_id}")
        
        # Register handler
        self.event_handlers[handler_key] = handler_fn
        
        # Update plugin subscriptions
        if plugin_id not in self.plugin_subscriptions:
            self.plugin_subscriptions[plugin_id] = []
        
        if event_type not in self.plugin_subscriptions[plugin_id]:
            self.plugin_subscriptions[plugin_id].append(event_type)
        
        # Subscribe to event
        self.event_manager.subscribe(
            event_type,
            lambda event: self._route_event(plugin_id, event_type, event),
            priority=priority
        )
        
        logger.debug(f"Registered event handler for {event_type} in plugin {plugin_id}")
    
    def unregister_event_handler(self, plugin_id: str, event_type: str) -> None:
        """
        Unregister an event handler.
        
        Args:
            plugin_id: ID of the plugin
            event_type: Type of event
            
        Raises:
            PluginError: If the handler is not registered
        """
        # Create handler key
        handler_key = (plugin_id, event_type)
        
        # Check if handler exists
        if handler_key not in self.event_handlers:
            raise PluginError(f"No event handler for {event_type} is registered for plugin {plugin_id}")
        
        # Unregister handler
        del self.event_handlers[handler_key]
        
        # Update plugin subscriptions
        if plugin_id in self.plugin_subscriptions and event_type in self.plugin_subscriptions[plugin_id]:
            self.plugin_subscriptions[plugin_id].remove(event_type)
        
        # Unsubscribe from event (this is approximate since we can't identify the exact subscriber)
        # The event manager will need to handle this properly
        
        logger.debug(f"Unregistered event handler for {event_type} in plugin {plugin_id}")
    
    def _route_event(self, plugin_id: str, event_type: str, event: Event) -> None:
        """
        Route an event to the appropriate plugin handler.
        
        Args:
            plugin_id: ID of the plugin
            event_type: Type of event
            event: Event object
        """
        # Create handler key
        handler_key = (plugin_id, event_type)
        
        # Check if handler exists
        if handler_key not in self.event_handlers:
            return
        
        # Get handler function
        handler_fn = self.event_handlers[handler_key]
        
        try:
            # Call handler function
            handler_fn(event)
        except Exception as e:
            logger.error(f"Error in event handler for {event_type} in plugin {plugin_id}: {e}")
    
    def register_plugin_event_handlers(self, plugin_id: str) -> None:
        """
        Register all event handlers for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Raises:
            PluginNotFoundError: If the plugin is not found
        """
        # Get plugin instance
        try:
            plugin = self.plugin_system.get_plugin(plugin_id)
        except Exception:
            raise PluginNotFoundError(f"Plugin {plugin_id} not found")
        
        # Check if plugin has event registration method
        if hasattr(plugin, 'register_event_handlers') and callable(getattr(plugin, 'register_event_handlers')):
            # Create event registration context
            event_context = PluginEventRegistrationContext(self, plugin_id)
            
            # Call plugin's event registration method
            plugin.register_event_handlers(event_context)
            
            logger.info(f"Registered event handlers for plugin: {plugin_id}")
        else:
            logger.debug(f"Plugin {plugin_id} does not implement register_event_handlers method")
    
    def unregister_plugin_event_handlers(self, plugin_id: str) -> None:
        """
        Unregister all event handlers for a plugin.
        
        Args:
            plugin_id: ID of the plugin
        """
        # Find all handlers for this plugin
        handlers_to_remove = [
            event_type for (pid, event_type) in self.event_handlers.keys()
            if pid == plugin_id
        ]
        
        # Unregister each handler
        for event_type in handlers_to_remove:
            try:
                self.unregister_event_handler(plugin_id, event_type)
            except Exception as e:
                logger.warning(f"Error unregistering event handler for {event_type} in plugin {plugin_id}: {e}")
        
        # Remove plugin subscriptions
        if plugin_id in self.plugin_subscriptions:
            del self.plugin_subscriptions[plugin_id]
        
        logger.info(f"Unregistered {len(handlers_to_remove)} event handlers for plugin: {plugin_id}")
    
    def get_plugin_subscriptions(self, plugin_id: str) -> List[str]:
        """
        Get a list of event types a plugin is subscribed to.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            List of event types
        """
        return self.plugin_subscriptions.get(plugin_id, [])
    
    def emit_plugin_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        source_plugin_id: Optional[str] = None
    ) -> None:
        """
        Emit an event from a plugin.
        
        Args:
            event_type: Type of event to emit
            data: Event data
            source_plugin_id: Optional ID of the source plugin
        """
        # Create event
        event = Event(event_type, data)
        
        # Set source plugin if provided
        if source_plugin_id:
            event.metadata['source_plugin'] = source_plugin_id
        
        # Emit event
        self.event_manager.emit_event(event)
        
        logger.debug(f"Emitted event {event_type} from plugin {source_plugin_id or 'unknown'}")


class PluginEventRegistrationContext:
    """
    Context object for plugin event handler registration.
    
    This class provides a simplified interface for plugins to register event handlers.
    """
    
    def __init__(self, plugin_event_hooks: PluginEventHooks, plugin_id: str):
        """
        Initialize the event registration context.
        
        Args:
            plugin_event_hooks: Reference to the PluginEventHooks instance
            plugin_id: ID of the plugin
        """
        self.plugin_event_hooks = plugin_event_hooks
        self.plugin_id = plugin_id
    
    def register_handler(
        self,
        event_type: str,
        handler_fn: Callable[[Event], None],
        priority: int = 0
    ) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler_fn: Function to handle the event
            priority: Priority of the handler (higher values = higher priority)
        """
        self.plugin_event_hooks.register_event_handler(
            self.plugin_id,
            event_type,
            handler_fn,
            priority
        )
    
    def event_handler(self, event_type: str, priority: int = 0) -> Callable:
        """
        Decorator for registering event handlers.
        
        Args:
            event_type: Type of event to handle
            priority: Priority of the handler (higher values = higher priority)
            
        Returns:
            Decorator function
        """
        def decorator(func):
            self.register_handler(event_type, func, priority)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit an event.
        
        Args:
            event_type: Type of event to emit
            data: Event data
        """
        self.plugin_event_hooks.emit_plugin_event(event_type, data, self.plugin_id)
