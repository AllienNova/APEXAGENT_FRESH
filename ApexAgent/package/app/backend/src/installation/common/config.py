"""
Configuration module for ApexAgent installation system.

This module contains common configuration settings and constants used across
all installation platforms (Windows, macOS, Linux).
"""

import os
import sys
import platform
from pathlib import Path
from enum import Enum

# Version information
VERSION = "0.1.0"
REQUIRED_PYTHON_VERSION = (3, 8)  # Minimum Python version required

# Installation paths
DEFAULT_INSTALL_PATHS = {
    "windows": "C:\\Program Files\\ApexAgent",
    "darwin": "/Applications/ApexAgent",
    "linux": "/opt/apexagent"
}

# Required dependencies with version constraints
REQUIRED_DEPENDENCIES = {
    "pip": ">=21.0.0",
    "setuptools": ">=50.0.0",
    "wheel": ">=0.36.0",
    "requests": ">=2.25.0",
    "numpy": ">=1.19.0",
    "pandas": ">=1.2.0",
    "matplotlib": ">=3.3.0",
    "pillow": ">=8.0.0",
    "beautifulsoup4": ">=4.9.0",
    "playwright": ">=1.10.0",
    "flask": ">=2.0.0",
    "fastapi": ">=0.68.0",
    "uvicorn": ">=0.15.0"
}

# Optional dependencies
OPTIONAL_DEPENDENCIES = {
    "development": {
        "pytest": ">=6.2.0",
        "black": ">=21.5b2",
        "flake8": ">=3.9.0",
        "mypy": ">=0.812",
        "isort": ">=5.9.0"
    },
    "documentation": {
        "sphinx": ">=4.0.0",
        "sphinx-rtd-theme": ">=0.5.0",
        "sphinx-autodoc-typehints": ">=1.12.0"
    }
}

# Installation modes
INSTALLATION_MODES = [
    "standard",      # Standard installation with GUI
    "minimal",       # Minimal installation (core components only)
    "complete",      # Complete installation with all optional components
    "development",   # Development installation with testing tools
    "custom"         # Custom installation with user-selected components
]

# API Key Mode Enum
class ApiKeyMode(Enum):
    """Enumeration of API key modes."""
    COMPLETE_SYSTEM = "complete_system"  # ApexAgent-provided API keys
    USER_PROVIDED = "user_provided"      # User-provided API keys

# Default API Key Mode
DEFAULT_API_KEY_MODE = ApiKeyMode.COMPLETE_SYSTEM

# Component groups for custom installation
COMPONENT_GROUPS = {
    "core": {
        "required": True,
        "description": "Core ApexAgent framework and essential components",
        "components": ["base", "plugin_system", "error_handling"]
    },
    "llm_providers": {
        "required": False,
        "description": "LLM provider integrations",
        "components": ["openai", "anthropic", "gemini", "ollama"]
    },
    "tools": {
        "required": False,
        "description": "Utility tools and extensions",
        "components": ["file_tools", "shell_tools", "web_tools", "knowledge_tools"]
    },
    "ui": {
        "required": False,
        "description": "User interface components",
        "components": ["web_ui", "desktop_ui", "cli"]
    },
    "examples": {
        "required": False,
        "description": "Example plugins and templates",
        "components": ["hello_world", "sample_plugins", "templates"]
    }
}

# API Key Mode descriptions and benefits
API_KEY_MODE_INFO = {
    ApiKeyMode.COMPLETE_SYSTEM: {
        "title": "Complete System",
        "description": "ApexAgent provides all necessary API keys for LLM access",
        "benefits": [
            "Pre-configured API access to all supported AI models",
            "No need to obtain or manage your own API keys",
            "Simplified billing with a single monthly subscription",
            "Automatic model selection based on task requirements",
            "Immediate access to all supported models without additional setup"
        ],
        "ideal_for": [
            "Users new to AI who want simplicity and convenience",
            "Teams seeking a turnkey solution with minimal setup",
            "Organizations preferring predictable, consolidated billing",
            "Users who don't want to manage multiple API providers"
        ]
    },
    ApiKeyMode.USER_PROVIDED: {
        "title": "User-Provided API Keys",
        "description": "Use your own API keys with reduced subscription fees",
        "benefits": [
            "Reduced subscription fees across all tiers (20-45% lower)",
            "Direct control over API usage and costs",
            "Leverage existing API relationships and enterprise agreements",
            "Enhanced privacy by using your own authentication",
            "Flexibility to prioritize specific models or providers"
        ],
        "ideal_for": [
            "Users who already have API keys for major providers",
            "Organizations with existing enterprise agreements",
            "Developers and power users who prefer direct API control",
            "Privacy-focused users who want maximum control over data flow",
            "Cost-conscious users seeking to optimize spending"
        ]
    }
}

# Analytics settings (opt-in)
ANALYTICS_SETTINGS = {
    "enabled": False,
    "anonymous_usage_stats": False,
    "error_reporting": False,
    "update_check": True
}

# System detection
def get_system_info():
    """Get current system information."""
    return {
        "os": platform.system().lower(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version_info,
        "python_path": sys.executable,
        "user_home": str(Path.home())
    }

def get_default_install_path():
    """Get the default installation path for the current platform."""
    system = platform.system().lower()
    if system == "windows":
        return DEFAULT_INSTALL_PATHS["windows"]
    elif system == "darwin":
        return DEFAULT_INSTALL_PATHS["darwin"]
    else:
        return DEFAULT_INSTALL_PATHS["linux"]

def is_admin():
    """Check if the current user has administrative privileges."""
    try:
        if platform.system().lower() == "windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False
