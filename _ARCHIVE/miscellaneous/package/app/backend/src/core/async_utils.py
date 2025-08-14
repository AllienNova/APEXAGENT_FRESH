from typing import Optional, List, Dict

# Assuming PluginActionExecutionError will be available in the context where this is used
# For now, let it be a generic Exception, or define a placeholder if needed for standalone use.
# We will adjust this if PluginManager needs a more specific hierarchy immediately.
try:
    # This path might not be valid when async_utils is imported by PluginManager
    # We rely on PluginManager to have plugin_exceptions in its scope
    from .plugin_exceptions import PluginActionExecutionError
except ImportError:
    # Fallback or placeholder if direct import fails (e.g. during unit testing of async_utils itself)
    class PluginActionExecutionError(Exception):
        pass

class ProgressUpdate:
    """Represents a progress update for an asynchronous operation."""
    def __init__(self, percentage: float, message: str, status: str, 
                 details: Optional[Dict] = None, sub_tasks: Optional[List["ProgressUpdate"]] = None):
        """
        Initializes a ProgressUpdate object.

        Args:
            percentage (float): The completion percentage (0.0 to 100.0).
            message (str): A human-readable message describing the current progress.
            status (str): The current status of the operation (e.g., "running", "completed", "error", "milestone_reached").
            details (Optional[Dict]): Additional details about the progress.
            sub_tasks (Optional[List[ProgressUpdate]]): A list of child ProgressUpdate objects for hierarchical progress (placeholder for future use).
        """
        self.percentage = percentage
        self.message = message
        self.status = status
        self.details = details if details is not None else {}
        self.sub_tasks = sub_tasks if sub_tasks is not None else [] # Placeholder for future use
    
    def validate(self) -> bool:
        """Validates the ProgressUpdate object."""
        if not isinstance(self.percentage, (int, float)) or not (0.0 <= self.percentage <= 100.0):
            return False
        if not isinstance(self.message, str) or not self.message:
            return False
        if not isinstance(self.status, str) or not self.status:
            return False
        return True

    def to_dict(self) -> Dict:
        """Converts the ProgressUpdate object to a dictionary."""
        return {
            "percentage": self.percentage,
            "message": self.message,
            "status": self.status,
            "details": self.details,
            "sub_tasks": [st.to_dict() for st in self.sub_tasks]
        }

class CancellationToken:
    """Represents a token that can be used to request cancellation of an operation."""
    def __init__(self):
        self._cancelled = False

    def cancel(self) -> None:
        """Requests cancellation of the operation."""
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Checks if cancellation has been requested."""
        return self._cancelled

class PluginActionTimeoutError(PluginActionExecutionError):
    """Custom exception for plugin action timeouts."""
    def __init__(self, message: str, timeout_seconds: Optional[float] = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds

