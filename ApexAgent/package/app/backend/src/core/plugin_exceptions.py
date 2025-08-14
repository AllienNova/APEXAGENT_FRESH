"""
Exception classes for the plugin system.
"""

class PluginError(Exception):
    """Base class for all plugin-related exceptions."""
    pass

class PluginStateError(PluginError):
    """Raised when a plugin is in an invalid state for the requested operation."""
    pass

class PluginAPIError(PluginError):
    """Raised when there's an error related to the plugin API."""
    pass

class PluginSecurityError(PluginError):
    """Raised when there's a security-related error in the plugin system."""
    pass

class PluginPermissionError(PluginSecurityError):
    """Raised when a plugin attempts an operation without the required permissions."""
    pass

class PluginResourceError(PluginError):
    """Raised when there's an error related to plugin resource management."""
    pass

class PluginLoadError(PluginError):
    """Raised when there's an error loading a plugin."""
    pass

class PluginInitializationError(PluginError):
    """Raised when a plugin fails to initialize."""
    pass

class PluginConfigurationError(PluginError):
    """Raised when there's an issue with plugin configuration."""
    pass

class PluginActionNotFoundError(PluginError):
    """Raised when a requested action is not found in a plugin."""
    pass

class PluginInvalidActionParametersError(PluginError):
    """Raised when invalid parameters are provided to a plugin action."""
    pass

class PluginActionExecutionError(PluginError):
    """Raised when there's an error during plugin action execution."""
    pass

class PluginDependencyError(PluginError):
    """Raised when there's an issue with plugin dependencies."""
    pass

class PluginMissingDependencyError(PluginDependencyError):
    """Raised when a required dependency is missing."""
    def __init__(self, plugin_id, version, missing_plugins=None, missing_libraries=None, message=None):
        self.plugin_id = plugin_id
        self.version = version
        self.missing_plugins = missing_plugins or {}
        self.missing_libraries = missing_libraries or {}
        
        if not message:
            message = f"Plugin {plugin_id} version {version} has missing dependencies"
            if self.missing_plugins:
                message += f"\n  Missing plugins: {self.missing_plugins}"
            if self.missing_libraries:
                message += f"\n  Missing libraries: {self.missing_libraries}"
        
        super().__init__(message)

class PluginIncompatibleDependencyError(PluginDependencyError):
    """Raised when a dependency is found but is incompatible with the required version."""
    def __init__(self, plugin_id, version, incompatible_plugins=None, incompatible_libraries=None, message=None):
        self.plugin_id = plugin_id
        self.version = version
        self.incompatible_plugins = incompatible_plugins or {}
        self.incompatible_libraries = incompatible_libraries or {}
        
        if not message:
            message = f"Plugin {plugin_id} version {version} has incompatible dependencies"
            if self.incompatible_plugins:
                message += f"\n  Incompatible plugins: {self.incompatible_plugins}"
            if self.incompatible_libraries:
                message += f"\n  Incompatible libraries: {self.incompatible_libraries}"
        
        super().__init__(message)

class PluginInvalidDependencySpecificationError(PluginDependencyError):
    """Raised when a dependency specification is invalid."""
    def __init__(self, plugin_id, version, invalid_specs=None, message=None):
        self.plugin_id = plugin_id
        self.version = version
        self.invalid_specs = invalid_specs or {}
        
        if not message:
            message = f"Plugin {plugin_id} version {version} has invalid dependency specifications: {self.invalid_specs}"
        
        super().__init__(message)

class PluginCircularDependencyError(PluginDependencyError):
    """Raised when a circular dependency is detected."""
    def __init__(self, dependency_chain, message=None):
        self.dependency_chain = dependency_chain
        
        if not message:
            message = f"Circular dependency detected: {' -> '.join(dependency_chain)}"
        
        super().__init__(message)

class PluginResourceNotFoundError(PluginError):
    """Raised when a plugin resource is not found."""
    pass

class StreamingNotSupportedError(PluginError):
    """Raised when streaming is not supported by a plugin action."""
    pass

class StreamTransformationError(PluginError):
    """Raised when there's an error during stream transformation."""
    pass

class PluginNotFoundError(PluginError):
    """Raised when a requested plugin is not found."""
    pass
