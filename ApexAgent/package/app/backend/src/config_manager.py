"""
Configuration management module for ApexAgent.

This module centralizes configuration settings for the entire application,
providing a consistent interface for accessing and modifying configuration values.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration settings for ApexAgent."""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "application": {
            "name": "ApexAgent",
            "version": "1.0.0",
            "environment": "production",
            "log_level": "info",
            "data_directory": "~/.apexagent/data",
            "temp_directory": "~/.apexagent/temp",
            "max_concurrent_tasks": 5
        },
        "security": {
            "encryption_key_env_var": "APEX_ENCRYPTION_KEY",
            "token_expiration_minutes": 60,
            "password_min_length": 10,
            "password_require_special": True,
            "password_require_number": True,
            "password_require_uppercase": True
        },
        "billing": {
            "tiers": {
                "basic": {
                    "price_api_provided": 24.99,
                    "price_user_provided": 19.99,
                    "credits": 2000,
                    "standard_llms": 2,
                    "high_reasoning_llms": 0
                },
                "pro": {
                    "price_api_provided": 89.99,
                    "price_user_provided": 49.99,
                    "credits": 5000,
                    "standard_llms": 3,
                    "high_reasoning_llms": 2
                },
                "expert": {
                    "price_api_provided": 149.99,
                    "price_user_provided": 99.99,
                    "credits": 15000,
                    "standard_llms": -1,  # Unlimited
                    "high_reasoning_llms": -1  # Unlimited
                }
            },
            "credit_pack_price": 14.00,
            "credit_pack_amount": 1000,
            "annual_discount_percentage": 17
        },
        "llm": {
            "default_provider": "openai",
            "default_model": "gpt-3.5-turbo",
            "timeout_seconds": 30,
            "max_tokens": 4096,
            "temperature": 0.7,
            "providers": {
                "openai": {
                    "api_base": "https://api.openai.com/v1",
                    "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
                },
                "anthropic": {
                    "api_base": "https://api.anthropic.com/v1",
                    "models": ["claude-instant-1", "claude-2", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
                },
                "google": {
                    "api_base": "https://generativelanguage.googleapis.com/v1",
                    "models": ["gemini-pro", "gemini-ultra"]
                }
            }
        },
        "ui": {
            "theme": "light",
            "accent_color": "#0066cc",
            "font_size": "medium",
            "enable_animations": True,
            "sidebar_collapsed": False,
            "default_tab": "chat"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path.
        
        Returns:
            Default configuration file path
        """
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, ".apexagent")
        
        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, "config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default.
        
        Returns:
            Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                
                # Merge with default config to ensure all keys exist
                config = self._merge_configs(self.DEFAULT_CONFIG, user_config)
            else:
                # Use default config
                config = self.DEFAULT_CONFIG.copy()
                
                # Save default config
                self._save_config(config)
            
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            logger.warning("Using default configuration")
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def _merge_configs(self, default_config: Dict[str, Any], 
                      user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user configuration with default configuration.
        
        Args:
            default_config: Default configuration dictionary
            user_config: User configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        result = default_config.copy()
        
        for key, value in user_config.items():
            # If the value is a dictionary and the key exists in the default config
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Recursively merge the dictionaries
                result[key] = self._merge_configs(result[key], value)
            else:
                # Otherwise, use the user value
                result[key] = value
        
        return result
    
    def get(self, section: str, key: Optional[str] = None) -> Any:
        """Get a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key (optional)
            
        Returns:
            Configuration value or section dictionary
        """
        try:
            if section not in self.config:
                logger.warning(f"Configuration section '{section}' not found")
                return None
            
            if key is None:
                return self.config[section]
            
            if key not in self.config[section]:
                logger.warning(f"Configuration key '{key}' not found in section '{section}'")
                return None
            
            return self.config[section][key]
        except Exception as e:
            logger.error(f"Error getting configuration: {str(e)}")
            return None
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """Set a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create section if it doesn't exist
            if section not in self.config:
                self.config[section] = {}
            
            # Set value
            self.config[section][key] = value
            
            # Save configuration
            return self._save_config(self.config)
        except Exception as e:
            logger.error(f"Error setting configuration: {str(e)}")
            return False
    
    def reset(self, section: Optional[str] = None, key: Optional[str] = None) -> bool:
        """Reset configuration to default values.
        
        Args:
            section: Configuration section (optional)
            key: Configuration key (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if section is None:
                # Reset entire configuration
                self.config = self.DEFAULT_CONFIG.copy()
            elif key is None:
                # Reset section
                if section in self.DEFAULT_CONFIG:
                    self.config[section] = self.DEFAULT_CONFIG[section].copy()
                else:
                    logger.warning(f"Default configuration section '{section}' not found")
                    return False
            else:
                # Reset key
                if section in self.DEFAULT_CONFIG and key in self.DEFAULT_CONFIG[section]:
                    self.config[section][key] = self.DEFAULT_CONFIG[section][key]
                else:
                    logger.warning(f"Default configuration key '{key}' not found in section '{section}'")
                    return False
            
            # Save configuration
            return self._save_config(self.config)
        except Exception as e:
            logger.error(f"Error resetting configuration: {str(e)}")
            return False
    
    def get_data_directory(self) -> str:
        """Get the data directory path.
        
        Returns:
            Data directory path
        """
        data_dir = self.get("application", "data_directory")
        
        # Expand user directory
        data_dir = os.path.expanduser(data_dir)
        
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        return data_dir
    
    def get_temp_directory(self) -> str:
        """Get the temporary directory path.
        
        Returns:
            Temporary directory path
        """
        temp_dir = self.get("application", "temp_directory")
        
        # Expand user directory
        temp_dir = os.path.expanduser(temp_dir)
        
        # Create directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
        
        return temp_dir
    
    def get_log_level(self) -> int:
        """Get the log level.
        
        Returns:
            Log level as an integer
        """
        log_level_str = self.get("application", "log_level").upper()
        
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        return log_levels.get(log_level_str, logging.INFO)
    
    def get_billing_tier_info(self, tier: str) -> Dict[str, Any]:
        """Get information for a specific billing tier.
        
        Args:
            tier: Billing tier name
            
        Returns:
            Tier information dictionary
        """
        tiers = self.get("billing", "tiers")
        
        if tier not in tiers:
            logger.warning(f"Billing tier '{tier}' not found")
            return {}
        
        return tiers[tier]
    
    def get_llm_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get information for a specific LLM provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Provider information dictionary
        """
        providers = self.get("llm", "providers")
        
        if provider not in providers:
            logger.warning(f"LLM provider '{provider}' not found")
            return {}
        
        return providers[provider]
    
    def export_config(self, export_path: Optional[str] = None) -> bool:
        """Export configuration to a file.
        
        Args:
            export_path: Path to export the configuration (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if export_path is None:
                # Use default export path
                export_path = os.path.join(
                    os.path.dirname(self.config_path),
                    "config_export.json"
                )
            
            with open(export_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error exporting configuration: {str(e)}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configuration from a file.
        
        Args:
            import_path: Path to import the configuration from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(import_path):
                logger.error(f"Import file not found: {import_path}")
                return False
            
            with open(import_path, 'r') as f:
                import_config = json.load(f)
            
            # Merge with default config to ensure all keys exist
            self.config = self._merge_configs(self.DEFAULT_CONFIG, import_config)
            
            # Save configuration
            return self._save_config(self.config)
        except Exception as e:
            logger.error(f"Error importing configuration: {str(e)}")
            return False
