import re

def validate_api_key_format(api_key: str, provider: str) -> bool:
    """
    Validates the format of an API key based on the provider.

    Args:
        api_key: The API key string to validate.
        provider: The provider for which the API key is being validated (e.g., "together_ai").

    Returns:
        True if the API key format is valid, False otherwise.
    """
    if provider == "together_ai":
        # Example: Together AI API keys are typically 40 characters alphanumeric
        return bool(re.fullmatch(r"^[a-zA-Z0-9]{40}$", api_key))
    # Add more providers and their validation rules here
    return True  # Default to True if provider is not specifically handled


