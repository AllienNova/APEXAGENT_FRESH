"""
Logging Manager for Dr. TARDIS Gemini Live API Integration.

This module provides comprehensive logging capabilities for the Dr. TARDIS
integration, including hierarchical loggers, multiple output destinations,
and performance impact monitoring.

Classes:
    LogLevel: Enumeration of log levels
    LogFormat: Enumeration of log formats
    LogDestination: Enumeration of log destinations
    LoggingManager: Manager for logging configuration and operations

Author: Manus Agent
Date: May 26, 2025
"""

import json
import logging
import os
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


class LogLevel(Enum):
    """Enumeration of log levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogFormat(Enum):
    """Enumeration of log formats."""
    TEXT = "text"
    JSON = "json"


class LogDestination(Enum):
    """Enumeration of log destinations."""
    CONSOLE = "console"
    FILE = "file"
    REMOTE = "remote"


class LoggingManager:
    """
    Manager for logging configuration and operations.
    
    Features:
    - Hierarchical loggers with component-specific settings
    - Multiple output destinations (console, file, remote)
    - Structured logging with JSON format option
    - Log rotation and archiving
    - Performance impact monitoring
    
    Attributes:
        log_dir (Path): Directory for log files
        config (Dict): Configuration settings
    """
    
    def __init__(
        self,
        log_dir: Optional[Union[str, Path]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the LoggingManager.
        
        Args:
            log_dir: Directory for log files, defaults to 'logs' in current directory
            config: Configuration settings
        """
        # Set up basic configuration
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.config = config or {
            "default_level": LogLevel.INFO,
            "default_format": LogFormat.TEXT,
            "component_levels": {
                "video": LogLevel.INFO,
                "audio": LogLevel.INFO,
                "knowledge": LogLevel.INFO,
                "ui": LogLevel.INFO,
            },
            "rotation": {
                "max_size": 10485760,  # 10 MB
                "backup_count": 5,
            },
        }
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Set up root logger
        self.root_logger = logging.getLogger("dr_tardis")
        self.root_logger.setLevel(self.config["default_level"].value)
        
        # Add default console handler to root logger
        console_handler = logging.StreamHandler()
        console_formatter = self._create_formatter(self.config["default_format"])
        console_handler.setFormatter(console_formatter)
        self.root_logger.addHandler(console_handler)
        
        # Dictionary to track handlers for each logger
        self.logger_handlers = {"dr_tardis": [console_handler]}
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """
        Get a logger with the specified name.
        
        Args:
            name: Logger name, if None returns the root logger
            
        Returns:
            Logger instance
        """
        if name is None:
            return self.root_logger
        
        # Create hierarchical logger
        logger = logging.getLogger(f"dr_tardis.{name}")
        
        # Set level based on component if applicable
        for component, level in self.config["component_levels"].items():
            if name.startswith(component):
                logger.setLevel(level.value)
                break
        else:
            # Default to root logger level
            logger.setLevel(self.root_logger.level)
        
        # Initialize handlers dictionary for this logger if not exists
        if name not in self.logger_handlers:
            self.logger_handlers[name] = []
        
        return logger
    
    def set_level(self, name: str, level: LogLevel) -> None:
        """
        Set the log level for a logger or component.
        
        Args:
            name: Logger or component name
            level: Log level to set
        """
        # Check if this is a component
        if name in self.config["component_levels"]:
            self.config["component_levels"][name] = level
            
            # Update all loggers for this component
            for logger_name in logging.root.manager.loggerDict:
                if logger_name.startswith(f"dr_tardis.{name}"):
                    logging.getLogger(logger_name).setLevel(level.value)
        else:
            # Set level for specific logger
            logger = self.get_logger(name)
            logger.setLevel(level.value)
    
    def add_destination(self, name: str, destination: LogDestination) -> None:
        """
        Add a log destination to a logger.
        
        Args:
            name: Logger name
            destination: Log destination to add
        """
        logger = self.get_logger(name)
        
        if destination == LogDestination.CONSOLE:
            handler = logging.StreamHandler()
        elif destination == LogDestination.FILE:
            log_file = self.log_dir / f"{name}.log"
            handler = logging.FileHandler(log_file)
        elif destination == LogDestination.REMOTE:
            # In a real implementation, this would set up a remote logging handler
            # For this implementation, we'll use a null handler
            handler = logging.NullHandler()
        else:
            raise ValueError(f"Unsupported log destination: {destination}")
        
        formatter = self._create_formatter(self.config["default_format"])
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Track this handler
        if name not in self.logger_handlers:
            self.logger_handlers[name] = []
        self.logger_handlers[name].append(handler)
    
    def remove_destination(self, name: str, destination: LogDestination) -> None:
        """
        Remove a log destination from a logger.
        
        Args:
            name: Logger name
            destination: Log destination to remove
        """
        logger = self.get_logger(name)
        
        # Find handlers of the specified destination type
        handlers_to_remove = []
        for handler in logger.handlers:
            if (destination == LogDestination.CONSOLE and isinstance(handler, logging.StreamHandler) and 
                not isinstance(handler, logging.FileHandler)):
                handlers_to_remove.append(handler)
            elif destination == LogDestination.FILE and isinstance(handler, logging.FileHandler):
                handlers_to_remove.append(handler)
            elif destination == LogDestination.REMOTE and isinstance(handler, logging.NullHandler):
                handlers_to_remove.append(handler)
        
        # Remove the handlers
        for handler in handlers_to_remove:
            logger.removeHandler(handler)
            if name in self.logger_handlers and handler in self.logger_handlers[name]:
                self.logger_handlers[name].remove(handler)
    
    def set_format(self, format: LogFormat) -> None:
        """
        Set the log format for all handlers.
        
        Args:
            format: Log format to set
        """
        self.config["default_format"] = format
        
        # Update formatters for all handlers
        formatter = self._create_formatter(format)
        
        for logger_name, handlers in self.logger_handlers.items():
            for handler in handlers:
                handler.setFormatter(formatter)
    
    def _create_formatter(self, format: LogFormat) -> logging.Formatter:
        """
        Create a formatter for the specified format.
        
        Args:
            format: Log format
            
        Returns:
            Formatter instance
        """
        if format == LogFormat.JSON:
            return logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def log_with_context(
        self,
        name: str,
        level: LogLevel,
        message: str,
        context: Dict[str, Any],
    ) -> None:
        """
        Log a message with additional context.
        
        Args:
            name: Logger name
            level: Log level
            message: Log message
            context: Additional context as key-value pairs
        """
        logger = self.get_logger(name)
        
        if self.config["default_format"] == LogFormat.JSON:
            # For JSON format, include context in the message
            context_str = json.dumps(context)
            full_message = f"{message} - Context: {context_str}"
        else:
            # For text format, append context as key-value pairs
            context_items = [f"{k}={v}" for k, v in context.items()]
            context_str = ", ".join(context_items)
            full_message = f"{message} - Context: {context_str}"
        
        logger.log(level.value, full_message)
    
    def measure_performance_impact(self, iterations: int = 1000) -> Dict[str, float]:
        """
        Measure the performance impact of logging.
        
        Args:
            iterations: Number of log messages to generate for measurement
            
        Returns:
            Dictionary with performance metrics
        """
        logger = self.get_logger("performance_test")
        
        # Measure time to log messages
        start_time = time.time()
        
        for i in range(iterations):
            logger.info(f"Performance test message {i}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics
        metrics = {
            "total_time_ms": total_time * 1000,
            "avg_time_ms": (total_time * 1000) / iterations,
            "messages_per_second": iterations / total_time,
        }
        
        return metrics
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update the configuration settings.
        
        Args:
            config: New configuration settings
        """
        self.config.update(config)
        
        # Update log levels if specified
        if "default_level" in config:
            self.root_logger.setLevel(config["default_level"].value)
        
        if "component_levels" in config:
            for component, level in config["component_levels"].items():
                # Update all loggers for this component
                for logger_name in logging.root.manager.loggerDict:
                    if logger_name.startswith(f"dr_tardis.{component}"):
                        logging.getLogger(logger_name).setLevel(level.value)
        
        # Update format if specified
        if "default_format" in config:
            self.set_format(config["default_format"])
