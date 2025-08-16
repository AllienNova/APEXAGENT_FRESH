"""
Embedding Utilities for Aideon AI Lite Vector Database

This module provides utilities for generating and managing embeddings
for the vector database integration in the Aideon AI Lite platform.

Production-ready features:
- Multiple embedding model support
- Batched embedding generation
- Caching for performance optimization
- Error handling and fallback strategies
- Multi-tenant awareness
"""

import os
import json
import logging
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import threading
from functools import lru_cache

logger = logging.getLogger(__name__)

# Default embedding dimension for different models
DEFAULT_DIMENSIONS = {
    "openai": 1536,  # OpenAI text-embedding-ada-002
    "huggingface": 768,  # Default for many HuggingFace models
    "sentence-transformers": 384,  # Default for many sentence-transformers models
    "tensorflow": 512,  # Default for many TensorFlow models
    "pytorch": 768,  # Default for many PyTorch models
    "mock": 128,  # Mock embeddings for testing
}


class EmbeddingError(Exception):
    """Base exception class for embedding errors."""
    pass


class ModelNotFoundError(EmbeddingError):
    """Exception raised when an embedding model is not found."""
    pass


class EmbeddingGenerationError(EmbeddingError):
    """Exception raised when embedding generation fails."""
    pass


class EmbeddingCache:
    """
    Cache for embeddings to avoid regenerating embeddings for the same content.
    
    This cache uses a combination of in-memory LRU cache and disk-based
    persistent cache for optimal performance.
    """
    
    def __init__(self, cache_dir: Optional[str] = None, max_size: int = 10000):
        """
        Initialize the embedding cache.
        
        Args:
            cache_dir: Directory to store persistent cache.
                       If None, uses a default directory.
            max_size: Maximum number of embeddings to keep in memory.
        """
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), "embedding_cache")
        self.max_size = max_size
        self.lock = threading.RLock()
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize in-memory cache
        self._init_memory_cache()
    
    def _init_memory_cache(self):
        """Initialize the in-memory LRU cache."""
        @lru_cache(maxsize=self.max_size)
        def _get_embedding(key: str, model_name: str) -> Optional[np.ndarray]:
            """Get embedding from disk cache."""
            return self._get_from_disk(key, model_name)
        
        self._get_cached_embedding = _get_embedding
    
    def _get_cache_key(self, content: str, tenant_id: Optional[str] = None) -> str:
        """
        Generate a cache key for content.
        
        Args:
            content: The content to generate a key for.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A cache key string.
        """
        # Add tenant_id to content if provided
        if tenant_id:
            content = f"{tenant_id}:{content}"
        
        # Generate SHA-256 hash of content
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def _get_cache_path(self, key: str, model_name: str) -> str:
        """
        Get the file path for a cached embedding.
        
        Args:
            key: The cache key.
            model_name: The name of the embedding model.
            
        Returns:
            The file path for the cached embedding.
        """
        return os.path.join(self.cache_dir, f"{key}_{model_name}.npy")
    
    def _get_from_disk(self, key: str, model_name: str) -> Optional[np.ndarray]:
        """
        Get an embedding from disk cache.
        
        Args:
            key: The cache key.
            model_name: The name of the embedding model.
            
        Returns:
            The embedding as a numpy array, or None if not found.
        """
        cache_path = self._get_cache_path(key, model_name)
        
        if os.path.exists(cache_path):
            try:
                return np.load(cache_path)
            except Exception as e:
                logger.warning(f"Failed to load cached embedding: {str(e)}")
                return None
        
        return None
    
    def _save_to_disk(self, key: str, model_name: str, embedding: np.ndarray):
        """
        Save an embedding to disk cache.
        
        Args:
            key: The cache key.
            model_name: The name of the embedding model.
            embedding: The embedding to save.
        """
        cache_path = self._get_cache_path(key, model_name)
        
        try:
            np.save(cache_path, embedding)
        except Exception as e:
            logger.warning(f"Failed to save embedding to cache: {str(e)}")
    
    def get(self, content: str, model_name: str, tenant_id: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Get an embedding from cache.
        
        Args:
            content: The content to get the embedding for.
            model_name: The name of the embedding model.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            The embedding as a numpy array, or None if not found.
        """
        key = self._get_cache_key(content, tenant_id)
        
        with self.lock:
            return self._get_cached_embedding(key, model_name)
    
    def put(self, content: str, model_name: str, embedding: np.ndarray, tenant_id: Optional[str] = None):
        """
        Put an embedding in cache.
        
        Args:
            content: The content the embedding is for.
            model_name: The name of the embedding model.
            embedding: The embedding to cache.
            tenant_id: Optional tenant ID for multi-tenant isolation.
        """
        key = self._get_cache_key(content, tenant_id)
        
        with self.lock:
            # Save to disk
            self._save_to_disk(key, model_name, embedding)
            
            # Update in-memory cache
            self._get_cached_embedding(key, model_name)
    
    def clear(self):
        """Clear the cache."""
        with self.lock:
            # Clear in-memory cache
            self._get_cached_embedding.cache_clear()
            
            # Clear disk cache
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".npy"):
                    try:
                        os.remove(os.path.join(self.cache_dir, filename))
                    except Exception as e:
                        logger.warning(f"Failed to remove cached embedding: {str(e)}")


class MockEmbeddingModel:
    """
    Mock embedding model for testing.
    
    This model generates deterministic embeddings based on the content hash,
    which is useful for testing without requiring actual embedding models.
    """
    
    def __init__(self, dimension: int = 128):
        """
        Initialize the mock embedding model.
        
        Args:
            dimension: The dimension of the embeddings to generate.
        """
        self.dimension = dimension
    
    def generate_embedding(self, content: str, tenant_id: Optional[str] = None) -> np.ndarray:
        """
        Generate a mock embedding for content.
        
        Args:
            content: The content to generate an embedding for.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            
        Returns:
            A mock embedding as a numpy array.
        """
        # Include tenant_id in the content hash if provided to ensure tenant isolation
        if tenant_id:
            content = f"{tenant_id}:{content}"
            
        # Generate a deterministic seed from the content
        seed = int(hashlib.md5(content.encode("utf-8")).hexdigest(), 16) % (2**32)
        
        # Set random seed for reproducibility
        np.random.seed(seed)
        
        # Generate a random embedding
        embedding = np.random.normal(0, 1, self.dimension).astype(np.float32)
        
        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding /= norm
        
        return embedding


class EmbeddingManager:
    """
    Manager for generating and managing embeddings.
    
    This class provides a unified interface for generating embeddings
    using various models and strategies.
    """
    
    def __init__(self, 
                 model_name: str = "mock",
                 cache_dir: Optional[str] = None,
                 cache_size: int = 10000):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: The name of the embedding model to use.
            cache_dir: Directory to store embedding cache.
            cache_size: Maximum number of embeddings to keep in memory cache.
        """
        self.model_name = model_name
        self.cache = EmbeddingCache(cache_dir, cache_size)
        self.models = {}
        
        # Initialize mock model by default
        self.models["mock"] = MockEmbeddingModel(DEFAULT_DIMENSIONS.get("mock", 128))
        
        # Try to initialize the requested model
        self._init_model(model_name)
    
    def _init_model(self, model_name: str):
        """
        Initialize an embedding model.
        
        Args:
            model_name: The name of the model to initialize.
            
        Raises:
            ModelNotFoundError: If the model is not found or cannot be initialized.
        """
        # Mock model is already initialized
        if model_name == "mock":
            return
        
        try:
            if model_name.startswith("openai:"):
                self._init_openai_model(model_name)
            elif model_name.startswith("huggingface:"):
                self._init_huggingface_model(model_name)
            elif model_name.startswith("sentence-transformers:"):
                self._init_sentence_transformers_model(model_name)
            else:
                logger.warning(f"Unknown model type: {model_name}, using mock model")
                # Use mock model as fallback
                self.models[model_name] = self.models["mock"]
        except Exception as e:
            logger.error(f"Failed to initialize model {model_name}: {str(e)}")
            raise ModelNotFoundError(f"Failed to initialize model {model_name}: {str(e)}")
    
    def _init_openai_model(self, model_name: str):
        """
        Initialize an OpenAI embedding model.
        
        Args:
            model_name: The name of the OpenAI model to initialize.
            
        Raises:
            ModelNotFoundError: If the model is not found or cannot be initialized.
        """
        try:
            import openai
            
            # Extract model name after prefix
            openai_model = model_name.split(":", 1)[1] if ":" in model_name else "text-embedding-ada-002"
            
            def generate_embedding(content: str, tenant_id: Optional[str] = None) -> np.ndarray:
                """Generate embedding using OpenAI API."""
                try:
                    # Include tenant_id in the content if provided
                    if tenant_id:
                        # Use a special prefix that won't affect the semantic meaning too much
                        content_with_tenant = f"[Tenant: {tenant_id}] {content}"
                    else:
                        content_with_tenant = content
                        
                    response = openai.Embedding.create(
                        input=content_with_tenant,
                        model=openai_model
                    )
                    embedding = np.array(response["data"][0]["embedding"], dtype=np.float32)
                    return embedding
                except Exception as e:
                    logger.error(f"OpenAI embedding generation failed: {str(e)}")
                    raise EmbeddingGenerationError(f"OpenAI embedding generation failed: {str(e)}")
            
            # Store the model
            self.models[model_name] = type("OpenAIModel", (), {
                "generate_embedding": generate_embedding
            })()
            
        except ImportError:
            logger.error("OpenAI package not installed")
            raise ModelNotFoundError("OpenAI package not installed")
    
    def _init_huggingface_model(self, model_name: str):
        """
        Initialize a HuggingFace embedding model.
        
        Args:
            model_name: The name of the HuggingFace model to initialize.
            
        Raises:
            ModelNotFoundError: If the model is not found or cannot be initialized.
        """
        try:
            from transformers import AutoModel, AutoTokenizer
            import torch
            
            # Extract model name after prefix
            hf_model_name = model_name.split(":", 1)[1] if ":" in model_name else "sentence-transformers/all-MiniLM-L6-v2"
            
            # Load model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(hf_model_name)
            model = AutoModel.from_pretrained(hf_model_name)
            
            def generate_embedding(content: str, tenant_id: Optional[str] = None) -> np.ndarray:
                """Generate embedding using HuggingFace model."""
                try:
                    # Include tenant_id in the content if provided
                    if tenant_id:
                        # Use a special prefix that won't affect the semantic meaning too much
                        content_with_tenant = f"[Tenant: {tenant_id}] {content}"
                    else:
                        content_with_tenant = content
                        
                    # Tokenize and prepare input
                    inputs = tokenizer(content_with_tenant, return_tensors="pt", padding=True, truncation=True, max_length=512)
                    
                    # Generate embedding
                    with torch.no_grad():
                        outputs = model(**inputs)
                    
                    # Use mean of last hidden state as embedding
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                    
                    # Normalize embedding
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding /= norm
                    
                    return embedding.astype(np.float32)
                except Exception as e:
                    logger.error(f"HuggingFace embedding generation failed: {str(e)}")
                    raise EmbeddingGenerationError(f"HuggingFace embedding generation failed: {str(e)}")
            
            # Store the model
            self.models[model_name] = type("HuggingFaceModel", (), {
                "generate_embedding": generate_embedding
            })()
            
        except ImportError:
            logger.error("Transformers package not installed")
            raise ModelNotFoundError("Transformers package not installed")
    
    def _init_sentence_transformers_model(self, model_name: str):
        """
        Initialize a sentence-transformers embedding model.
        
        Args:
            model_name: The name of the sentence-transformers model to initialize.
            
        Raises:
            ModelNotFoundError: If the model is not found or cannot be initialized.
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            # Extract model name after prefix
            st_model_name = model_name.split(":", 1)[1] if ":" in model_name else "a
(Content truncated due to size limit. Use line ranges to read in chunks)