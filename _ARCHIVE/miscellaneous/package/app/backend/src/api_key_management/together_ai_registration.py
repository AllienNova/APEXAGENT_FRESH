"""
Provider registration module for Together AI integration.

This module handles the registration of the Together AI provider
during application startup, ensuring it's available system-wide.
"""

import logging
import os
from typing import Optional

from src.plugins.llm_providers.internal.together_ai_provider import TogetherAIProvider
from src.api_key_management.together_ai_key_manager import get_together_ai_key_manager
from src.llm_providers.provider_manager import ProviderManager

logger = logging.getLogger(__name__)

def register_together_ai_provider(provider_manager: ProviderManager) -> bool:
    """
    Register the Together AI provider with the provider manager.
    
    This function creates and registers the Together AI provider
    with the system's provider manager, making it available for use.
    
    Args:
        provider_manager: The provider manager instance
        
    Returns:
        True if registration was successful, False otherwise
    """
    try:
        # Get the key manager
        key_manager = get_together_ai_key_manager()
        
        # Register the key manager with the admin dashboard
        key_manager.register_with_admin_dashboard()
        
        # Get the system API key
        api_key = key_manager.get_system_key()
        
        # Create the provider instance
        provider = TogetherAIProvider(api_key=api_key)
        
        # Register the provider with the manager
        provider_id = provider.get_provider_name()
        provider_manager.register_provider(provider_id, provider)
        
        logger.info(f"Successfully registered Together AI provider (API key available: {api_key is not None})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to register Together AI provider: {str(e)}")
        return False

def get_together_ai_provider_for_user(provider_manager: ProviderManager, user_id: str) -> Optional[TogetherAIProvider]:
    """
    Get a Together AI provider instance for a specific user.
    
    This function creates a provider instance with the user's API key
    if available, otherwise falls back to the system default key.
    
    Args:
        provider_manager: The provider manager instance
        user_id: User identifier
        
    Returns:
        Together AI provider instance or None if creation failed
    """
    try:
        # Get the key manager
        key_manager = get_together_ai_key_manager()
        
        # Get the appropriate API key for this user
        api_key = key_manager.get_api_key(user_id)
        
        if not api_key:
            logger.warning(f"No API key available for user {user_id}")
            return None
        
        # Create the provider instance with the user's key
        provider = TogetherAIProvider(api_key=api_key)
        
        return provider
        
    except Exception as e:
        logger.error(f"Failed to create Together AI provider for user {user_id}: {str(e)}")
        return None

def initialize_together_ai_integration() -> bool:
    """
    Initialize the Together AI integration during application startup.
    
    This function should be called during application startup to ensure
    the Together AI provider is registered and available system-wide.
    
    Returns:
        True if initialization was successful, False otherwise
    """
    try:
        # Get the provider manager instance
        from src.llm_providers import get_provider_manager
        provider_manager = get_provider_manager()
        
        # Register the provider
        success = register_together_ai_provider(provider_manager)
        
        if success:
            logger.info("Together AI integration initialized successfully")
        else:
            logger.error("Failed to initialize Together AI integration")
        
        return success
        
    except Exception as e:
        logger.error(f"Error initializing Together AI integration: {str(e)}")
        return False
