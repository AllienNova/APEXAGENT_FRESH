#!/usr/bin/env python3
"""
Performance Optimization Framework for ApexAgent

This module provides a comprehensive performance optimization framework
with profiling, monitoring, adaptive resource allocation, and automatic
optimization capabilities.
"""

import os
import sys
import time
import json
import logging
import threading
import queue
import random
import functools
import inspect
import cProfile
import pstats
import io
import gc
import tracemalloc
import psutil
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, TypeVar, cast, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("performance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("performance")

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')

class OptimizationLevel(Enum):
    """Enumeration of optimization levels."""
    NONE = 0        # No optimization
    MINIMAL = 1     # Basic optimizations only
    STANDARD = 2    # Standard optimizations
    AGGRESSIVE = 3  # Aggressive optimizations
    MAXIMUM = 4     # Maximum optimizations (may affect functionality)

class ResourceType(Enum):
    """Enumeration of resource types."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    ALL = "all"

class OptimizationStrategy(Enum):
    """Enumeration of optimization strategies."""
    CACHING = "caching"
    LAZY_LOADING = "lazy_loading"
    BATCHING = "batching"
    PARALLELIZATION = "parallelization"
    COMPRESSION = "compression"
    INDEXING = "indexing"
    QUERY_OPTIMIZATION = "query_optimization"
    CONNECTION_POOLING = "connection_pooling"
    CODE_OPTIMIZATION = "code_optimization"
    RESOURCE_LIMITING = "resource_limiting"

@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation."""
    operation: str
    component: str
    execution_time: float  # in seconds
    cpu_usage: float  # percentage
    memory_usage: float  # in bytes
    disk_io: Optional[float] = None  # in bytes
    network_io: Optional[float] = None  # in bytes
    database_queries: Optional[int] = None
    api_calls: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    additional_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metrics to a dictionary."""
        return {
            "operation": self.operation,
            "component": self.component,
            "execution_time": self.execution_time,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_io": self.disk_io,
            "network_io": self.network_io,
            "database_queries": self.database_queries,
            "api_calls": self.api_calls,
            "timestamp": self.timestamp.isoformat(),
            "additional_metrics": self.additional_metrics
        }

@dataclass
class OptimizationConfig:
    """Configuration for optimization behavior."""
    level: OptimizationLevel = OptimizationLevel.STANDARD
    enabled_strategies: Set[OptimizationStrategy] = field(default_factory=set)
    disabled_strategies: Set[OptimizationStrategy] = field(default_factory=set)
    resource_limits: Dict[ResourceType, float] = field(default_factory=dict)
    cache_ttl: int = 300  # seconds
    batch_size: int = 100
    max_parallel_tasks: int = 10
    compression_threshold: int = 1024  # bytes
    adaptive: bool = True
    
    def __post_init__(self):
        """Initialize default strategies based on level."""
        if not self.enabled_strategies:
            if self.level == OptimizationLevel.NONE:
                pass  # No strategies enabled
            elif self.level == OptimizationLevel.MINIMAL:
                self.enabled_strategies = {
                    OptimizationStrategy.CACHING,
                    OptimizationStrategy.RESOURCE_LIMITING
                }
            elif self.level == OptimizationLevel.STANDARD:
                self.enabled_strategies = {
                    OptimizationStrategy.CACHING,
                    OptimizationStrategy.LAZY_LOADING,
                    OptimizationStrategy.BATCHING,
                    OptimizationStrategy.RESOURCE_LIMITING,
                    OptimizationStrategy.CONNECTION_POOLING
                }
            elif self.level == OptimizationLevel.AGGRESSIVE:
                self.enabled_strategies = {
                    OptimizationStrategy.CACHING,
                    OptimizationStrategy.LAZY_LOADING,
                    OptimizationStrategy.BATCHING,
                    OptimizationStrategy.PARALLELIZATION,
                    OptimizationStrategy.COMPRESSION,
                    OptimizationStrategy.INDEXING,
                    OptimizationStrategy.QUERY_OPTIMIZATION,
                    OptimizationStrategy.CONNECTION_POOLING,
                    OptimizationStrategy.RESOURCE_LIMITING
                }
            elif self.level == OptimizationLevel.MAXIMUM:
                self.enabled_strategies = set(OptimizationStrategy)
    
    def is_strategy_enabled(self, strategy: OptimizationStrategy) -> bool:
        """
        Check if a strategy is enabled.
        
        Args:
            strategy: The strategy to check
            
        Returns:
            bool: True if the strategy is enabled, False otherwise
        """
        return strategy in self.enabled_strategies and strategy not in self.disabled_strategies
    
    def get_resource_limit(self, resource_type: ResourceType) -> Optional[float]:
        """
        Get the limit for a resource type.
        
        Args:
            resource_type: The resource type
            
        Returns:
            Optional[float]: The resource limit, or None if not set
        """
        return self.resource_limits.get(resource_type)

class PerformanceConfig:
    """Configuration for the performance optimization framework."""
    
    def __init__(self):
        """Initialize the performance configuration."""
        self.optimization_configs: Dict[str, OptimizationConfig] = {}
        self.global_optimization_config = OptimizationConfig()
        self.metrics_queue_size: int = 1000
        self.metrics_processors: int = 2
        self.profiling_enabled: bool = True
        self.monitoring_interval: int = 60  # seconds
        self.alert_thresholds: Dict[str, float] = {
            "execution_time": 5.0,  # seconds
            "cpu_usage": 80.0,  # percentage
            "memory_usage": 1024 * 1024 * 1024  # 1 GB
        }
        self.optimization_interval: int = 3600  # seconds
        self.telemetry_enabled: bool = True
    
    def get_optimization_config(self, operation: str) -> OptimizationConfig:
        """
        Get the optimization configuration for an operation.
        
        Args:
            operation: The operation name
            
        Returns:
            OptimizationConfig: The optimization configuration
        """
        return self.optimization_configs.get(operation, self.global_optimization_config)
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Load global optimization config
            if "global_optimization" in config_data:
                opt_data = config_data["global_optimization"]
                self.global_optimization_config = OptimizationConfig(
                    level=OptimizationLevel(opt_data.get("level", 2)),
                    cache_ttl=opt_data.get("cache_ttl", 300),
                    batch_size=opt_data.get("batch_size", 100),
                    max_parallel_tasks=opt_data.get("max_parallel_tasks", 10),
                    compression_threshold=opt_data.get("compression_threshold", 1024),
                    adaptive=opt_data.get("adaptive", True)
                )
                
                # Load enabled strategies
                if "enabled_strategies" in opt_data:
                    self.global_optimization_config.enabled_strategies = {
                        OptimizationStrategy(strategy) for strategy in opt_data["enabled_strategies"]
                    }
                
                # Load disabled strategies
                if "disabled_strategies" in opt_data:
                    self.global_optimization_config.disabled_strategies = {
                        OptimizationStrategy(strategy) for strategy in opt_data["disabled_strategies"]
                    }
                
                # Load resource limits
                if "resource_limits" in opt_data:
                    self.global_optimization_config.resource_limits = {
                        ResourceType(resource): limit
                        for resource, limit in opt_data["resource_limits"].items()
                    }
            
            # Load operation-specific configs
            if "operations" in config_data:
                for op_name, op_config in config_data["operations"].items():
                    # Load optimization config
                    if "optimization" in op_config:
                        opt_data = op_config["optimization"]
                        self.optimization_configs[op_name] = OptimizationConfig(
                            level=OptimizationLevel(opt_data.get("level", 2)),
                            cache_ttl=opt_data.get("cache_ttl", 300),
                            batch_size=opt_data.get("batch_size", 100),
                            max_parallel_tasks=opt_data.get("max_parallel_tasks", 10),
                            compression_threshold=opt_data.get("compression_threshold", 1024),
                            adaptive=opt_data.get("adaptive", True)
                        )
                        
                        # Load enabled strategies
                        if "enabled_strategies" in opt_data:
                            self.optimization_configs[op_name].enabled_strategies = {
                                OptimizationStrategy(strategy) for strategy in opt_data["enabled_strategies"]
                            }
                        
                        # Load disabled strategies
                        if "disabled_strategies" in opt_data:
                            self.optimization_configs[op_name].disabled_strategies = {
                                OptimizationStrategy(strategy) for strategy in opt_data["disabled_strategies"]
                            }
                        
                        # Load resource limits
                        if "resource_limits" in opt_data:
                            self.optimization_configs[op_name].resource_limits = {
                                ResourceType(resource): limit
                                for resource, limit in opt_data["resource_limits"].items()
                            }
            
            # Load framework settings
            if "framework" in config_data:
                framework = config_data["framework"]
                self.metrics_queue_size = framework.get("metrics_queue_size", 1000)
                self.metrics_processors = framework.get("metrics_processors", 2)
                self.profiling_enabled = framework.get("profiling_enabled", True)
                self.monitoring_interval = framework.get("monitoring_interval", 60)
                self.optimization_interval = framework.get("optimization_interval", 3600)
                self.telemetry_enabled = framework.get("telemetry_enabled", True)
                
                # Load alert thresholds
                if "alert_thresholds" in framework:
                    self.alert_thresholds = framework["alert_thresholds"]
            
            logger.info(f"Configuration loaded successfully from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {str(e)}")
            return False

class Cache:
    """
    Simple in-memory cache implementation.
    
    This class provides a thread-safe cache with TTL support.
    """
    
    def __init__(self, ttl: int = 300):
        """
        Initialize the cache.
        
        Args:
            ttl: Time-to-live in seconds (default: 300)
        """
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            Any: The cached value, or None if not found or expired
        """
        with self._lock:
            if key not in self.cache:
                return None
            
            value, expiry = self.cache[key]
            
            # Check if expired
            if expiry < datetime.now():
                del self.cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Optional custom TTL in seconds
        """
        with self._lock:
            expiry = datetime.now() + timedelta(seconds=ttl or self.ttl)
            self.cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            bool: True if the key was deleted, False if not found
        """
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all values from the cache."""
        with self._lock:
            self.cache.clear()
    
    def cleanup(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            int: Number of entries removed
        """
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if expiry < now
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dict: Cache statistics
        """
        with self._lock:
            return {
                "size": len(self.cache),
                "ttl": self.ttl,
                "expired": sum(1 for _, expiry in self.cache.values() if expiry < datetime.now())
            }

class BatchProcessor:
    """
    Batch processor for efficient processing of multiple items.
    
    This class collects items into batches and processes them together
    for improved efficiency.
    """
    
    def __init__(self, processor: Callable[[List[Any]], List[Any]], batch_size: int = 100, max_wait: float = 1.0):
        """
        Initialize the batch processor.
        
        Args:
            processor: Function to process a batch of items
            batch_size: Maximum batch size
            max_wait: Maximum wait time in seconds before processing a partial batch
        """
        self.processor = processor
        self.batch_size = batch_size
        self.max_wait = max_wait
        self.items: List[Any] = []
        self.results: Dict[int, Any] = {}
        self.next_id = 0
        self.last_add_time = datetime.now()
        self._lock = threading.RLock()
        self._event = threading.Event()
        self._thread = threading.Thread(target=self._process_batches, daemon=True)
        self._running = False
    
    def start(self) -> None:
        """Start the batch processor."""
        with self._lock:
            if not self._running:
                self._running = True
                self._thread.start()
    
    def stop(self) -> None:
        """Stop the batch processor."""
        with self._lock:
            if self._running:
                self._running = False
                self._event.set()
                self._thread.join(timeout=5.0)
    
    def add(self, item: Any) -> int:
        """
        Add an item to the batch.
        
        Args:
            item: The item to add
            
        Returns:
            int: Item ID for retrieving the result
        """
        with self._lock:
            item_id = self.next_id
            self.next_id += 1
            self.items.append((item_id, item))
            self.last_add_time = datetime.now()
            
            # Signal the processing thread if batch is full
            if len(self.items) >= self.batch_size:
                self._event.set()
            
            return item_id
    
    def get_result(self, item_id: int, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Get the result for an item.
        
        Args:
            item_id: The item ID
            timeout: Optional timeout in seconds
            
        Returns:
            Any: The result, or None if not available
        """
        start_time = time.time()
        
        while timeout is None or time.time() - start_time < timeout:
            with self._lock:
                if item_id in self.results:
                    return self.results.pop(item_id)
            
            # Wait a bit before checking again
            time.sleep(0.01)
        
        return None
    
    def _process_batches(self) -> None:
        """Process batches in a background thread."""
        while self._running:
            # Wait for batch to be full or max wait time to elapse
            self._event.wait(timeout=0.1)
            self._event.clear()
            
            current_time = datetime.now()
            
            with self._lock:
                # Process batch if it's full or max wait time has elapsed
                if (len(self.items) >= self.batch_size or
                    (len(self.items) > 0 and
                     (current_time - self.last_add_time).total_seconds() >= self.max_wait)):
                    
                    # Get batch items
                    batch_items = self.items
                    self.items = []
                    
                    # Extract item IDs and items
                    item_ids, items = zip(*batch_items) if batch_items else ([], [])
                    
                    # Release lock during processing
                    
                # Skip processing if no items
                if not batch_items:
                    continue
            
            try:
                # Process the batch
                batch_results = self.processor(list(items))
                
                # Store results
                with self._lock:
                    for item_id, result in zip(item_ids, batch_results):
                        self.results[item_id] = result
            except Exception as e:
                logger.error(f"Error processing batch: {str(e)}")
                
                # Store error as result
                with self._lock:
                    for item_id in item_ids:
                        self.results[item_id] = e

class TaskPool:
    """
    Task pool for parallel execution of tasks.
    
    This class manages a pool of worker threads for executing tasks in parallel.
    """
    
    def __init__(self, max_workers: int = 10, queue_size: int = 100):
        """
        Initialize the task pool.
        
        Args:
            max_workers: Maximum number of worker threads
            queue_size: Maximum task queue size
        """
        self.max_workers = max_workers
        self.task_queue: queue.Queue = queue.Queue(maxsize=queue_size)
        self.workers: List[threading.Thread] = []
        self.results: Dict[int, Any] = {}
        self.next_task_id = 0
        self._lock = threading.RLock()
        self._running = False
    
    def start(self) -> None:
        """Start the task pool."""
        with self._lock:
            if not self._running:
                self._running = True
                
                # Create worker threads
                for i in range(self.max_workers):
                    worker = threading.Thread(
                        target=self._worker_loop,
                        name=f"TaskPool-Worker-{i}",
                        daemon=True
                    )
                    worker.start()
                    self.workers.append(worker)
    
    def stop(self) -> None:
        """Stop the task pool."""
        with self._lock:
            if self._running:
                self._running = False
                
                # Add sentinel values to stop workers
                for _ in range(len(self.workers)):
                    try:
                        self.task_queue.put(None, block=False)
                    except queue.Full:
                        pass
                
                # Wait for workers to finish
                for worker in self.workers:
                    worker.join(timeout=5.0)
                
                self.workers = []
    
    def submit(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> int:
        """
        Submit a task for execution.
        
        Args:
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            int: Task ID for retrieving the result
            
        Raises:
            queue.Full: If the task queue is full
        """
        with self._lock:
            task_id = self.next_task_id
            self.next_task_id += 1
            
            # Create task
            task = (task_id, func, args, kwargs)
            
            # Add to queue
            self.task_queue.put(task, block=False)
            
            return task_id
    
    def get_result(self, task_id: int, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Get the result of a task.
        
        Args:
            task_id: The task ID
            timeout: Optional timeout in seconds
            
        Returns:
            Any: The result, or None if not available
        """
        start_time = time.time()
        
        while timeout is None or time.time() - start_time < timeout:
            with self._lock:
                if task_id in self.results:
                    return self.results.pop(task_id)
            
            # Wait a bit before checking again
            time.sleep(0.01)
        
        return None
    
    def _worker_loop(self) -> None:
        """Worker thread loop."""
        while self._running:
            try:
                # Get task from queue
                task = self.task_queue.get(timeout=1.0)
                
                # Check for sentinel value
                if task is None:
                    break
                
                # Unpack task
                task_id, func, args, kwargs = task
                
                try:
                    # Execute task
                    result = func(*args, **kwargs)
                    
                    # Store result
                    with self._lock:
                        self.results[task_id] = result
                except Exception as e:
                    # Store exception as result
                    with self._lock:
                        self.results[task_id] = e
                
                # Mark task as done
                self.task_queue.task_done()
            except queue.Empty:
                # Queue is empty, continue
                continue
            except Exception as e:
                logger.error(f"Error in worker thread: {str(e)}")

class PerformanceOptimizer:
    """
    Performance optimization framework for ApexAgent.
    
    This class provides comprehensive performance optimization capabilities including:
    - Performance profiling and monitoring
    - Adaptive resource allocation
    - Automatic optimization strategies
    - Caching, batching, and parallelization
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'PerformanceOptimizer':
        """
        Get the singleton instance of the performance optimizer.
        
        Returns:
            PerformanceOptimizer: The singleton instance
        """
        if cls._instance is None:
            cls._instance = PerformanceOptimizer()
        return cls._instance
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.config = PerformanceConfig()
        self.metrics_queue: queue.Queue = queue.Queue(maxsize=self.config.metrics_queue_size)
        self.metrics_processors_threads: List[threading.Thread] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.optimization_thread: Optional[threading.Thread] = None
        self.caches: Dict[str, Cache] = {}
        self.batch_processors: Dict[str, BatchProcessor] = {}
        self.task_pools: Dict[str, TaskPool] = {}
        self.operation_metrics: Dict[str, List[PerformanceMetrics]] = {}
        self.running = False
        self._lock = threading.RLock()
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the performance optimizer.
        
        Args:
            config_path: Optional path to configuration file
        """
        if config_path and os.path.exists(config_path):
            self.config.load_from_file(config_path)
        
        # Start metrics processor threads
        self.running = True
        for i in range(self.config.metrics_processors):
            thread = threading.Thread(
                target=self._process_metrics_queue,
                name=f"MetricsProcessor-{i}",
                daemon=True
            )
            thread.start()
            self.metrics_processors_threads.append(thread)
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            name="PerformanceMonitor",
            daemon=True
        )
        self.monitoring_thread.start()
        
        # Start optimization thread
        self.optimization_thread = threading.Thread(
            target=self._optimization_loop,
            name="PerformanceOptimizer",
            daemon=True
        )
        self.optimization_thread.start()
        
        # Initialize tracemalloc for memory profiling
        tracemalloc.start()
        
        logger.info("Performance optimizer initialized")
    
    def shutdown(self) -> None:
        """Shutdown the performance optimizer."""
        self.running = False
        
        # Wait for threads to finish
        for thread in self.metrics_processors_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        
        if self.optimization_thread and self.optimization_thread.is_alive():
            self.optimization_thread.join(timeout=5.0)
        
        # Stop batch processors
        for processor in self.batch_processors.values():
            processor.stop()
        
        # Stop task pools
        for pool in self.task_pools.values():
            pool.stop()
        
        # Stop tracemalloc
        tracemalloc.stop()
        
        logger.info("Performance optimizer shut down")
    
    def _process_metrics_queue(self) -> None:
        """Process metrics from the metrics queue."""
        while self.running:
            try:
                # Get metrics from queue with timeout
                try:
                    metrics = self.metrics_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process the metrics
                self._handle_metrics(metrics)
                
                # Mark task as done
                self.metrics_queue.task_done()
            except Exception as e:
                logger.error(f"Error in metrics processor: {str(e)}")
    
    def _handle_metrics(self, metrics: PerformanceMetrics) -> None:
        """
        Handle performance metrics.
        
        Args:
            metrics: The performance metrics to handle
        """
        # Store metrics for the operation
        with self._lock:
            if metrics.operation not in self.operation_metrics:
                self.operation_metrics[metrics.operation] = []
            
            # Add metrics to the list (keep last 100 entries)
            self.operation_metrics[metrics.operation].append(metrics)
            if len(self.operation_metrics[metrics.operation]) > 100:
                self.operation_metrics[metrics.operation] = self.operation_metrics[metrics.operation][-100:]
        
        # Check for alert thresholds
        self._check_alert_thresholds(metrics)
        
        # Send telemetry
        if self.config.telemetry_enabled:
            self._send_telemetry(metrics)
    
    def _check_alert_thresholds(self, metrics: PerformanceMetrics) -> None:
        """
        Check if metrics exceed alert thresholds.
        
        Args:
            metrics: The performance metrics to check
        """
        # Check execution time
        if (
            "execution_time" in self.config.alert_thresholds and
            metrics.execution_time > self.config.alert_thresholds["execution_time"]
        ):
            logger.warning(
                f"Performance alert: {metrics.operation} execution time "
                f"({metrics.execution_time:.2f}s) exceeds threshold "
                f"({self.config.alert_thresholds['execution_time']:.2f}s)"
            )
        
        # Check CPU usage
        if (
            "cpu_usage" in self.config.alert_thresholds and
            metrics.cpu_usage > self.config.alert_thresholds["cpu_usage"]
        ):
            logger.warning(
                f"Performance alert: {metrics.operation} CPU usage "
                f"({metrics.cpu_usage:.2f}%) exceeds threshold "
                f"({self.config.alert_thresholds['cpu_usage']:.2f}%)"
            )
        
        # Check memory usage
        if (
            "memory_usage" in self.config.alert_thresholds and
            metrics.memory_usage > self.config.alert_thresholds["memory_usage"]
        ):
            logger.warning(
                f"Performance alert: {metrics.operation} memory usage "
                f"({metrics.memory_usage / (1024 * 1024):.2f} MB) exceeds threshold "
                f"({self.config.alert_thresholds['memory_usage'] / (1024 * 1024):.2f} MB)"
            )
    
    def _send_telemetry(self, metrics: PerformanceMetrics) -> None:
        """
        Send telemetry for performance metrics.
        
        Args:
            metrics: The performance metrics to send telemetry for
        """
        # In a real implementation, this would send telemetry to a monitoring system
        # For this example, we'll just log it
        logger.debug(f"Sending telemetry for operation: {metrics.operation}")
    
    def _monitoring_loop(self) -> None:
        """Monitoring thread loop."""
        while self.running:
            try:
                # Collect system-wide metrics
                self._collect_system_metrics()
                
                # Sleep until next monitoring interval
                time.sleep(self.config.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(10)  # Sleep a bit before retrying
    
    def _collect_system_metrics(self) -> None:
        """Collect system-wide performance metrics."""
        try:
            # Get system metrics using psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Log system metrics
            logger.info(
                f"System metrics: CPU: {cpu_percent:.1f}%, "
                f"Memory: {memory.percent:.1f}% ({memory.used / (1024 * 1024 * 1024):.2f} GB), "
                f"Disk: {disk.percent:.1f}% ({disk.used / (1024 * 1024 * 1024):.2f} GB)"
            )
            
            # Check for resource constraints
            if cpu_percent > 90:
                logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > 90:
                logger.warning(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 90:
                logger.warning(f"High disk usage: {disk.percent:.1f}%")
            
            # Collect garbage if memory usage is high
            if memory.percent > 80:
                logger.info("High memory usage detected, collecting garbage")
                gc.collect()
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
    
    def _optimization_loop(self) -> None:
        """Optimization thread loop."""
        while self.running:
            try:
                # Perform automatic optimizations
                self._perform_optimizations()
                
                # Sleep until next optimization interval
                time.sleep(self.config.optimization_interval)
            except Exception as e:
                logger.error(f"Error in optimization loop: {str(e)}")
                time.sleep(60)  # Sleep a bit before retrying
    
    def _perform_optimizations(self) -> None:
        """Perform automatic optimizations based on collected metrics."""
        with self._lock:
            # Analyze operation metrics
            for operation, metrics_list in self.operation_metrics.items():
                if not metrics_list:
                    continue
                
                # Calculate average metrics
                avg_execution_time = sum(m.execution_time for m in metrics_list) / len(metrics_list)
                avg_cpu_usage = sum(m.cpu_usage for m in metrics_list) / len(metrics_list)
                avg_memory_usage = sum(m.memory_usage for m in metrics_list) / len(metrics_list)
                
                # Get optimization config
                opt_config = self.config.get_optimization_config(operation)
                
                # Skip if not adaptive
                if not opt_config.adaptive:
                    continue
                
                # Check for optimization opportunities
                if avg_execution_time > 1.0:  # More than 1 second
                    # Enable caching if not already enabled
                    if (
                        OptimizationStrategy.CACHING not in opt_config.enabled_strategies and
                        OptimizationStrategy.CACHING not in opt_config.disabled_strategies
                    ):
                        logger.info(f"Enabling caching for {operation} due to high execution time")
                        opt_config.enabled_strategies.add(OptimizationStrategy.CACHING)
                
                if avg_cpu_usage > 50:  # More than 50% CPU
                    # Enable resource limiting if not already enabled
                    if (
                        OptimizationStrategy.RESOURCE_LIMITING not in opt_config.enabled_strategies and
                        OptimizationStrategy.RESOURCE_LIMITING not in opt_config.disabled_strategies
                    ):
                        logger.info(f"Enabling resource limiting for {operation} due to high CPU usage")
                        opt_config.enabled_strategies.add(OptimizationStrategy.RESOURCE_LIMITING)
                
                if avg_memory_usage > 100 * 1024 * 1024:  # More than 100 MB
                    # Enable compression if not already enabled
                    if (
                        OptimizationStrategy.COMPRESSION not in opt_config.enabled_strategies and
                        OptimizationStrategy.COMPRESSION not in opt_config.disabled_strategies
                    ):
                        logger.info(f"Enabling compression for {operation} due to high memory usage")
                        opt_config.enabled_strategies.add(OptimizationStrategy.COMPRESSION)
        
        # Clean up caches
        for cache in self.caches.values():
            removed = cache.cleanup()
            if removed > 0:
                logger.debug(f"Removed {removed} expired cache entries")
    
    def get_cache(self, name: str, ttl: Optional[int] = None) -> Cache:
        """
        Get or create a cache.
        
        Args:
            name: The cache name
            ttl: Optional time-to-live in seconds
            
        Returns:
            Cache: The cache
        """
        with self._lock:
            if name not in self.caches:
                cache_ttl = ttl or self.config.global_optimization_config.cache_ttl
                self.caches[name] = Cache(ttl=cache_ttl)
            return self.caches[name]
    
    def get_batch_processor(self, name: str, processor: Callable[[List[Any]], List[Any]],
                           batch_size: Optional[int] = None, max_wait: float = 1.0) -> BatchProcessor:
        """
        Get or create a batch processor.
        
        Args:
            name: The batch processor name
            processor: Function to process a batch of items
            batch_size: Optional maximum batch size
            max_wait: Maximum wait time in seconds
            
        Returns:
            BatchProcessor: The batch processor
        """
        with self._lock:
            if name not in self.batch_processors:
                batch_size = batch_size or self.config.global_optimization_config.batch_size
                self.batch_processors[name] = BatchProcessor(
                    processor=processor,
                    batch_size=batch_size,
                    max_wait=max_wait
                )
                self.batch_processors[name].start()
            return self.batch_processors[name]
    
    def get_task_pool(self, name: str, max_workers: Optional[int] = None,
                     queue_size: int = 100) -> TaskPool:
        """
        Get or create a task pool.
        
        Args:
            name: The task pool name
            max_workers: Optional maximum number of workers
            queue_size: Maximum task queue size
            
        Returns:
            TaskPool: The task pool
        """
        with self._lock:
            if name not in self.task_pools:
                max_workers = max_workers or self.config.global_optimization_config.max_parallel_tasks
                self.task_pools[name] = TaskPool(
                    max_workers=max_workers,
                    queue_size=queue_size
                )
                self.task_pools[name].start()
            return self.task_pools[name]
    
    @contextmanager
    def profile(self, operation: str, component: str) -> None:
        """
        Context manager for profiling an operation.
        
        Args:
            operation: The operation name
            component: The component name
            
        Yields:
            None
        """
        # Skip if profiling is disabled
        if not self.config.profiling_enabled:
            yield
            return
        
        # Get process for resource usage
        process = psutil.Process()
        
        # Get initial resource usage
        start_time = time.time()
        start_cpu_time = process.cpu_times()
        start_memory = process.memory_info()
        
        # Start CPU profiler
        pr = cProfile.Profile()
        pr.enable()
        
        # Get initial tracemalloc snapshot
        start_snapshot = tracemalloc.take_snapshot()
        
        try:
            # Execute the operation
            yield
        finally:
            # Stop CPU profiler
            pr.disable()
            
            # Get final tracemalloc snapshot
            end_snapshot = tracemalloc.take_snapshot()
            
            # Get final resource usage
            end_time = time.time()
            end_cpu_time = process.cpu_times()
            end_memory = process.memory_info()
            
            # Calculate metrics
            execution_time = end_time - start_time
            cpu_time = (
                (end_cpu_time.user - start_cpu_time.user) +
                (end_cpu_time.system - start_cpu_time.system)
            )
            cpu_usage = (cpu_time / execution_time) * 100 if execution_time > 0 else 0
            memory_usage = end_memory.rss - start_memory.rss
            
            # Create metrics object
            metrics = PerformanceMetrics(
                operation=operation,
                component=component,
                execution_time=execution_time,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage
            )
            
            # Add profiling data
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
            ps.print_stats(20)  # Print top 20 functions
            metrics.additional_metrics['profile'] = s.getvalue()
            
            # Add memory allocation data
            top_stats = end_snapshot.compare_to(start_snapshot, 'lineno')
            metrics.additional_metrics['memory_allocations'] = [
                {
                    'file': stat.traceback[0].filename,
                    'line': stat.traceback[0].lineno,
                    'size': stat.size,
                    'count': stat.count
                }
                for stat in top_stats[:10]  # Top 10 allocations
            ]
            
            # Add to metrics queue
            try:
                self.metrics_queue.put(metrics, block=False)
            except queue.Full:
                logger.warning("Metrics queue is full, dropping metrics")
    
    def with_profiling(self, operation: str, component: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Decorator for profiling a function.
        
        Args:
            operation: The operation name
            component: The component name
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> R:
                with self.profile(operation, component):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def with_caching(self, cache_name: str, key_func: Optional[Callable[..., str]] = None,
                    ttl: Optional[int] = None) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Decorator for caching function results.
        
        Args:
            cache_name: The cache name
            key_func: Optional function to generate cache key
            ttl: Optional time-to-live in seconds
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> R:
                # Get cache
                cache = self.get_cache(cache_name, ttl)
                
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key generation
                    arg_str = ','.join(str(arg) for arg in args)
                    kwarg_str = ','.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = f"{func.__module__}.{func.__name__}({arg_str},{kwarg_str})"
                
                # Check cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result
                cache.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    def with_batching(self, batch_name: str, processor: Callable[[List[Any]], List[Any]],
                     batch_size: Optional[int] = None, max_wait: float = 1.0) -> Callable[[Callable[[Any], R]], Callable[[Any], R]]:
        """
        Decorator for batching function calls.
        
        Args:
            batch_name: The batch processor name
            processor: Function to process a batch of items
            batch_size: Optional maximum batch size
            max_wait: Maximum wait time in seconds
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[[Any], R]) -> Callable[[Any], R]:
            @functools.wraps(func)
            def wrapper(item: Any) -> R:
                # Get batch processor
                batch_processor = self.get_batch_processor(
                    batch_name,
                    processor,
                    batch_size,
                    max_wait
                )
                
                # Add item to batch
                item_id = batch_processor.add(item)
                
                # Wait for result
                result = batch_processor.get_result(item_id)
                
                # Check for exception
                if isinstance(result, Exception):
                    raise result
                
                return result
            return wrapper
        return decorator
    
    def with_parallelization(self, pool_name: str, max_workers: Optional[int] = None) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Decorator for parallel execution of functions.
        
        Args:
            pool_name: The task pool name
            max_workers: Optional maximum number of workers
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> R:
                # Get task pool
                task_pool = self.get_task_pool(pool_name, max_workers)
                
                # Submit task
                task_id = task_pool.submit(func, *args, **kwargs)
                
                # Wait for result
                result = task_pool.get_result(task_id)
                
                # Check for exception
                if isinstance(result, Exception):
                    raise result
                
                return result
            return wrapper
        return decorator
    
    def with_resource_limiting(self, cpu_limit: Optional[float] = None,
                              memory_limit: Optional[float] = None) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Decorator for limiting resource usage of a function.
        
        Args:
            cpu_limit: Optional CPU usage limit (percentage)
            memory_limit: Optional memory usage limit (bytes)
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> R:
                # Get process
                process = psutil.Process()
                
                # Get initial resource usage
                start_cpu_percent = process.cpu_percent(interval=None)
                start_memory = process.memory_info().rss
                
                # Execute function with periodic checks
                result = None
                exception = None
                
                def execute_func():
                    nonlocal result, exception
                    try:
                        result = func(*args, **kwargs)
                    except Exception as e:
                        exception = e
                
                # Start execution thread
                thread = threading.Thread(target=execute_func)
                thread.start()
                
                # Monitor resource usage
                while thread.is_alive():
                    # Check CPU usage
                    if cpu_limit is not None:
                        cpu_percent = process.cpu_percent(interval=0.1)
                        if cpu_percent > cpu_limit:
                            logger.warning(f"CPU usage ({cpu_percent:.1f}%) exceeds limit ({cpu_limit:.1f}%)")
                            # Throttle by sleeping
                            time.sleep(0.1)
                    
                    # Check memory usage
                    if memory_limit is not None:
                        memory_usage = process.memory_info().rss - start_memory
                        if memory_usage > memory_limit:
                            logger.warning(f"Memory usage ({memory_usage / (1024 * 1024):.1f} MB) exceeds limit ({memory_limit / (1024 * 1024):.1f} MB)")
                            # Force garbage collection
                            gc.collect()
                    
                    # Sleep a bit
                    time.sleep(0.1)
                
                # Wait for thread to finish
                thread.join()
                
                # Check for exception
                if exception:
                    raise exception
                
                return result
            return wrapper
        return decorator
    
    def with_optimization(self, operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
        """
        Combined decorator for applying all enabled optimization strategies.
        
        Args:
            operation: The operation name
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> R:
                # Get optimization config
                opt_config = self.config.get_optimization_config(operation)
                
                # Apply profiling
                profiled_func = self.with_profiling(operation, func.__module__)(func)
                
                # Apply caching if enabled
                if opt_config.is_strategy_enabled(OptimizationStrategy.CACHING):
                    profiled_func = self.with_caching(f"{operation}_cache")(profiled_func)
                
                # Apply resource limiting if enabled
                if opt_config.is_strategy_enabled(OptimizationStrategy.RESOURCE_LIMITING):
                    cpu_limit = opt_config.get_resource_limit(ResourceType.CPU)
                    memory_limit = opt_config.get_resource_limit(ResourceType.MEMORY)
                    profiled_func = self.with_resource_limiting(cpu_limit, memory_limit)(profiled_func)
                
                # Apply parallelization if enabled
                if opt_config.is_strategy_enabled(OptimizationStrategy.PARALLELIZATION):
                    profiled_func = self.with_parallelization(f"{operation}_pool")(profiled_func)
                
                # Execute the optimized function
                return profiled_func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the performance optimizer.
        
        Returns:
            Dict: Metrics about the performance optimizer
        """
        with self._lock:
            metrics = {
                "metrics_queue_size": self.metrics_queue.qsize(),
                "metrics_queue_capacity": self.metrics_queue.maxsize,
                "metrics_processors": len(self.metrics_processors_threads),
                "caches": {
                    name: cache.get_stats() for name, cache in self.caches.items()
                },
                "batch_processors": list(self.batch_processors.keys()),
                "task_pools": list(self.task_pools.keys()),
                "operations": {
                    operation: {
                        "count": len(metrics_list),
                        "avg_execution_time": sum(m.execution_time for m in metrics_list) / len(metrics_list) if metrics_list else 0,
                        "avg_cpu_usage": sum(m.cpu_usage for m in metrics_list) / len(metrics_list) if metrics_list else 0,
                        "avg_memory_usage": sum(m.memory_usage for m in metrics_list) / len(metrics_list) if metrics_list else 0
                    }
                    for operation, metrics_list in self.operation_metrics.items()
                }
            }
            
            return metrics


# Global instance for easy access
performance_optimizer = PerformanceOptimizer.get_instance()


def initialize_performance_optimization(config_path: Optional[str] = None) -> None:
    """
    Initialize the performance optimization framework.
    
    Args:
        config_path: Optional path to configuration file
    """
    performance_optimizer.initialize(config_path)


def shutdown_performance_optimization() -> None:
    """Shutdown the performance optimization framework."""
    performance_optimizer.shutdown()


def with_profiling(operation: str, component: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for profiling a function.
    
    Args:
        operation: The operation name
        component: The component name
        
    Returns:
        Callable: Decorator function
    """
    return performance_optimizer.with_profiling(operation, component)


def with_caching(cache_name: str, key_func: Optional[Callable[..., str]] = None,
                ttl: Optional[int] = None) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for caching function results.
    
    Args:
        cache_name: The cache name
        key_func: Optional function to generate cache key
        ttl: Optional time-to-live in seconds
        
    Returns:
        Callable: Decorator function
    """
    return performance_optimizer.with_caching(cache_name, key_func, ttl)


def with_batching(batch_name: str, processor: Callable[[List[Any]], List[Any]],
                 batch_size: Optional[int] = None, max_wait: float = 1.0) -> Callable[[Callable[[Any], R]], Callable[[Any], R]]:
    """
    Decorator for batching function calls.
    
    Args:
        batch_name: The batch processor name
        processor: Function to process a batch of items
        batch_size: Optional maximum batch size
        max_wait: Maximum wait time in seconds
        
    Returns:
        Callable: Decorator function
    """
    return performance_optimizer.with_batching(batch_name, processor, batch_size, max_wait)


def with_parallelization(pool_name: str, max_workers: Optional[int] = None) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for parallel execution of functions.
    
    Args:
        pool_name: The task pool name
        max_workers: Optional maximum number of workers
        
    Returns:
        Callable: Decorator function
    """
    return performance_optimizer.with_parallelization(pool_name, max_workers)


def with_resource_limiting(cpu_limit: Optional[float] = None,
                          memory_limit: Optional[float] = None) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for limiting resource usage of a function.
    
    Args:
        cpu_limit: Optional CPU usage limit (percentage)
        memory_limit: Optional memory usage limit (bytes)
        
    Returns:
        Callable: Decorator function
    """
    return performance_optimizer.with_resource_limiting(cpu_limit, memory_limit)


def with_optimization(operation: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Combined decorator for applying all enabled optimization strategies.
    
    Args:
        operation: The operation name
        
    Returns:
        Callable: Decorator function
    """
    return performance_optimizer.with_optimization(operation)


def get_cache(name: str, ttl: Optional[int] = None) -> Cache:
    """
    Get or create a cache.
    
    Args:
        name: The cache name
        ttl: Optional time-to-live in seconds
        
    Returns:
        Cache: The cache
    """
    return performance_optimizer.get_cache(name, ttl)


def get_batch_processor(name: str, processor: Callable[[List[Any]], List[Any]],
                       batch_size: Optional[int] = None, max_wait: float = 1.0) -> BatchProcessor:
    """
    Get or create a batch processor.
    
    Args:
        name: The batch processor name
        processor: Function to process a batch of items
        batch_size: Optional maximum batch size
        max_wait: Maximum wait time in seconds
        
    Returns:
        BatchProcessor: The batch processor
    """
    return performance_optimizer.get_batch_processor(name, processor, batch_size, max_wait)


def get_task_pool(name: str, max_workers: Optional[int] = None,
                 queue_size: int = 100) -> TaskPool:
    """
    Get or create a task pool.
    
    Args:
        name: The task pool name
        max_workers: Optional maximum number of workers
        queue_size: Maximum task queue size
        
    Returns:
        TaskPool: The task pool
    """
    return performance_optimizer.get_task_pool(name, max_workers, queue_size)


@contextmanager
def profile(operation: str, component: str) -> None:
    """
    Context manager for profiling an operation.
    
    Args:
        operation: The operation name
        component: The component name
        
    Yields:
        None
    """
    with performance_optimizer.profile(operation, component):
        yield


def get_metrics() -> Dict[str, Any]:
    """
    Get metrics about the performance optimizer.
    
    Returns:
        Dict: Metrics about the performance optimizer
    """
    return performance_optimizer.get_metrics()


# Example usage
if __name__ == "__main__":
    # Initialize performance optimization
    initialize_performance_optimization()
    
    # Define a function with optimization
    @with_optimization("example_operation")
    def example_function(n):
        # Simulate CPU-intensive work
        result = 0
        for i in range(n):
            result += i * i
        return result
    
    # Define a function with caching
    @with_caching("example_cache")
    def cached_function(n):
        print(f"Computing for {n}...")
        # Simulate expensive computation
        time.sleep(1)
        return n * n
    
    # Try the functions
    try:
        # Test optimization
        print("Testing optimization...")
        result = example_function(1000000)
        print(f"Result: {result}")
        
        # Test caching
        print("\nTesting caching...")
        print(f"First call: {cached_function(10)}")
        print(f"Second call (should be cached): {cached_function(10)}")
        print(f"Different argument: {cached_function(20)}")
        
        # Test profiling
        print("\nTesting profiling...")
        with profile("manual_operation", "main"):
            # Simulate work
            time.sleep(0.5)
            result = sum(i * i for i in range(100000))
            print(f"Result: {result}")
        
        # Print metrics
        print("\nPerformance metrics:")
        metrics = get_metrics()
        print(f"Operations: {list(metrics['operations'].keys())}")
        for op, op_metrics in metrics['operations'].items():
            print(f"  {op}: {op_metrics['avg_execution_time']:.4f}s, {op_metrics['avg_cpu_usage']:.1f}% CPU")
    finally:
        # Shutdown performance optimization
        shutdown_performance_optimization()
