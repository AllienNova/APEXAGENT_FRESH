"""
Vector Factory for Aideon AI Lite Vector Database

This module provides a factory for creating vector database adapters.
The factory supports multiple backend types and handles adapter instantiation.
"""

import logging
from typing import Dict, Any, Optional, Type, cast

import numpy as np

from .vector_database import VectorDatabaseAdapter
from .adapters.faiss_adapter import FAISSAdapter
from .adapters.milvus.milvus_adapter import MilvusAdapter
from .adapters.chroma.chroma_adapter import ChromaAdapter

logger = logging.getLogger(__name__)


class VectorFactory:
    """
    Factory for creating vector database adapters.
    
    This factory supports multiple backend types and handles adapter instantiation
    with appropriate configuration.
    """
    
    # Registry of available adapter types
    _adapter_registry: Dict[str, Type[VectorDatabaseAdapter]] = {
        "faiss": FAISSAdapter,
        "milvus": MilvusAdapter,
        "chroma": ChromaAdapter,
    }
    
    @classmethod
    def create_adapter(cls, adapter_type: str, config: Dict[str, Any]) -> VectorDatabaseAdapter:
        """
        Create a vector database adapter.
        
        Args:
            adapter_type: The type of adapter to create.
            config: Configuration for the adapter.
            
        Returns:
            A vector database adapter.
            
        Raises:
            ValueError: If adapter type is not supported.
        """
        if adapter_type not in cls._adapter_registry:
            supported_types = ", ".join(cls._adapter_registry.keys())
            raise ValueError(f"Unsupported adapter type: {adapter_type}. Supported types: {supported_types}")
        
        adapter_class = cls._adapter_registry[adapter_type]
        
        logger.info(f"Creating {adapter_type} adapter")
        
        # Extract adapter-specific configuration
        adapter_config = config.get(adapter_type, {})
        
        # Create adapter instance
        adapter = adapter_class(**adapter_config)
        
        # Connect to database if connection parameters are provided
        connection_params = config.get("connection", {})
        if connection_params:
            adapter.connect(connection_params)
        
        return adapter
    
    @classmethod
    def register_adapter(cls, adapter_type: str, adapter_class: Type[VectorDatabaseAdapter]) -> None:
        """
        Register a new adapter type.
        
        Args:
            adapter_type: The type name for the adapter.
            adapter_class: The adapter class.
        """
        cls._adapter_registry[adapter_type] = adapter_class
        logger.info(f"Registered adapter type: {adapter_type}")
    
    @classmethod
    def get_supported_types(cls) -> list[str]:
        """
        Get a list of supported adapter types.
        
        Returns:
            A list of supported adapter types.
        """
        return list(cls._adapter_registry.keys())
