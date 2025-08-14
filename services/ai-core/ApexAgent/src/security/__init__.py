"""
Security Package for Dr. TARDIS Gemini Live API Integration.

This package provides comprehensive security and compliance features for the
Dr. TARDIS system, including secure data handling, privacy controls,
audit capabilities, and security incident response procedures.

Author: Manus Agent
Date: May 26, 2025
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union

# Export public interfaces
__all__ = [
    'SecurityManager',
    'PrivacyManager',
    'AuditManager',
    'IncidentResponseManager',
    'SecurityLevel',
    'DataCategory',
    'ConsentStatus',
    'ConsentLevel',
    'AuditEventType',
    'IncidentSeverity',
    'AuditEventSeverity',
    'IncidentStatus'
]

# Enumerations for security and compliance
class SecurityLevel(Enum):
    """Security levels for data and operations."""
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3
    CRITICAL = 4
    LOW = 1      # Alias for INTERNAL
    MEDIUM = 2   # Alias for CONFIDENTIAL
    HIGH = 3     # Alias for RESTRICTED

class DataCategory(Enum):
    """Categories of data for privacy and compliance purposes."""
    SYSTEM = auto()
    DIAGNOSTIC = auto()
    USER_PROVIDED = auto()
    GENERATED = auto()
    BIOMETRIC = auto()
    HEALTH = auto()
    FINANCIAL = auto()
    LOCATION = auto()
    CONTACT_INFO = auto()
    CONTENT = auto()
    GENERAL = auto()  # General purpose data category
    CONVERSATION = auto()  # Conversation data category
    AUDIO = auto()  # Audio data category
    VIDEO = auto()  # Video data category
    VISUAL = auto()  # Visual data category
    SCREEN_CONTENT = auto()  # Screen content data category
    KNOWLEDGE_BASE = auto()  # Knowledge base data category

class ConsentStatus(Enum):
    """User consent status for data processing."""
    GRANTED = auto()
    DENIED = auto()
    PARTIAL = auto()
    EXPIRED = auto()
    UNKNOWN = auto()

class ConsentLevel(Enum):
    """Levels of user consent for data processing."""
    NO_PROCESSING = auto()
    STORAGE_ONLY = auto()
    LIMITED_PROCESSING = auto()
    FULL_PROCESSING = auto()
    EXPLICIT_CONSENT = auto()

class AuditEventType(Enum):
    """Types of events to be audited."""
    AUTHENTICATION = auto()
    AUTHORIZATION = auto()
    DATA_ACCESS = auto()
    DATA_MODIFICATION = auto()
    SYSTEM_CHANGE = auto()
    SECURITY_EVENT = auto()
    COMPLIANCE_CHECK = auto()
    USER_CONSENT = auto()

class AuditEventSeverity(Enum):
    """Severity levels for audit events."""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

class IncidentSeverity(Enum):
    """Severity levels for security incidents."""
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class IncidentStatus(Enum):
    """Status values for security incidents."""
    OPEN = auto()
    INVESTIGATING = auto()
    CONTAINED = auto()
    RESOLVED = auto()
    CLOSED = auto()
