from typing import Dict
from .models import ApiKeyProvider

_registered_providers: Dict[str, ApiKeyProvider] = {}

def register_provider(provider: ApiKeyProvider) -> None:
    """
    Registers an API key provider with the admin dashboard.
    """
    _registered_providers[provider.id] = provider

def get_registered_providers() -> Dict[str, ApiKeyProvider]:
    """
    Returns all registered API key providers.
    """
    return _registered_providers


