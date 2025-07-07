"""
Vector Database Adapters for Aideon AI Lite

This package contains concrete implementations of the VectorDatabaseAdapter
interface for various vector database backends.
"""

from typing import Dict, Type, Any

# Import adapter implementations as they are created
# These will be populated as we implement each adapter
from .faiss_adapter import FAISSAdapter

# Registry of available adapters
ADAPTER_REGISTRY: Dict[str, Type[Any]] = {
    "faiss": FAISSAdapter,
}


def get_adapter(adapter_type: str, **kwargs):
    """
    Factory function to get a vector database adapter instance.
    
    Args:
        adapter_type: The type of adapter to get (e.g., "faiss", "chroma").
        **kwargs: Additional arguments to pass to the adapter constructor.
        
    Returns:
        An instance of the requested adapter.
        
    Raises:
        ValueError: If the requested adapter type is not available.
    """
    if adapter_type not in ADAPTER_REGISTRY:
        available_adapters = ", ".join(ADAPTER_REGISTRY.keys())
        raise ValueError(
            f"Adapter type '{adapter_type}' not available. "
            f"Available adapters: {available_adapters}"
        )
    
    return ADAPTER_REGISTRY[adapter_type](**kwargs)
