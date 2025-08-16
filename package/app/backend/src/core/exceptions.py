# ApexAgent Plugin Custom Exceptions

class PluginError(Exception):
    """Base exception for all plugin-related errors."""
    pass

class PluginInitializationError(PluginError):
    """For errors during plugin setup or initialization."""
    pass

class PluginExecutionError(PluginError):
    """For errors during a plugin action's execution."""
    pass

class PluginConfigurationError(PluginError):
    """For errors related to invalid or missing plugin configuration."""
    pass

class PluginArgumentError(PluginExecutionError, ValueError):
    """For invalid arguments passed to a plugin action."""
    pass

class PluginDependencyError(PluginError):
    """For issues with plugin dependencies (e.g., missing or incompatible)."""
    pass

class PluginStateError(PluginError):
    """For errors related to plugin state persistence (saving/loading state)."""
    pass

class PluginNotImplementedError(PluginError, NotImplementedError):
    """For actions or features that are declared but not implemented in a plugin."""
    pass

