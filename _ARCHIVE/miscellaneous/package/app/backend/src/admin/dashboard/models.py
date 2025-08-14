from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ApiKeyEntry:
    id: str
    key_id: str
    provider_id: str
    user_id: Optional[str] = None
    api_key_masked: str = "****"
    created_at: str = field(default_factory=str)
    last_used_at: Optional[str] = None
    status: str = "active"

@dataclass
class ApiKeyProvider:
    id: str
    name: str
    description: str
    env_var: Optional[str] = None
    required_for_tier: Optional[str] = None
    format_regex: Optional[str] = None
    format_description: Optional[str] = None
    docs_url: Optional[str] = None
    has_system_key: bool = False
    user_configurable: bool = False


