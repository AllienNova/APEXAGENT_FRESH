"""
Advanced Security Controls module for ApexAgent.

This module provides advanced security features including IP-based access controls,
geo-restrictions, device management, and other security mechanisms.
"""

import os
import json
import uuid
import logging
import ipaddress
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Pattern

from src.core.error_handling.errors import SecurityError, ConfigurationError
from src.core.event_system.event_manager import EventManager

logger = logging.getLogger(__name__)

class IPAccessRule:
    """
    Represents an IP-based access control rule.
    """
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        ip_ranges: List[str],
        rule_type: str,  # "allow" or "deny"
        priority: int = 0,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.rule_id = rule_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.ip_ranges = ip_ranges
        self.rule_type = rule_type
        self.priority = priority
        self.is_active = is_active
        self.metadata = metadata or {}
        
        # Parse IP ranges
        self.parsed_ranges = []
        for ip_range in ip_ranges:
            try:
                self.parsed_ranges.append(ipaddress.ip_network(ip_range, strict=False))
            except ValueError as e:
                logger.error(f"Invalid IP range '{ip_range}': {e}")
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert rule object to dictionary representation.
        
        Returns:
            Dictionary representation of the rule
        """
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "ip_ranges": self.ip_ranges,
            "rule_type": self.rule_type,
            "priority": self.priority,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, rule_dict: Dict[str, Any]) -> 'IPAccessRule':
        """
        Create a rule object from dictionary representation.
        
        Args:
            rule_dict: Dictionary representation of the rule
            
        Returns:
            IPAccessRule object
        """
        return cls(
            rule_id=rule_dict.get("rule_id"),
            name=rule_dict["name"],
            description=rule_dict["description"],
            ip_ranges=rule_dict["ip_ranges"],
            rule_type=rule_dict["rule_type"],
            priority=rule_dict.get("priority", 0),
            is_active=rule_dict.get("is_active", True),
            metadata=rule_dict.get("metadata", {})
        )
    
    def matches_ip(self, ip_address: str) -> bool:
        """
        Check if an IP address matches this rule.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            True if IP address matches, False otherwise
        """
        try:
            ip = ipaddress.ip_address(ip_address)
            for network in self.parsed_ranges:
                if ip in network:
                    return True
            return False
        except ValueError:
            logger.error(f"Invalid IP address '{ip_address}'")
            return False
    
    def __str__(self) -> str:
        return f"IPAccessRule(id={self.rule_id}, name={self.name}, type={self.rule_type})"


class GeoRestriction:
    """
    Represents a geographic restriction.
    """
    def __init__(
        self,
        restriction_id: str,
        name: str,
        description: str,
        countries: List[str],
        restriction_type: str,  # "allow" or "deny"
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.restriction_id = restriction_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.countries = countries
        self.restriction_type = restriction_type
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert restriction object to dictionary representation.
        
        Returns:
            Dictionary representation of the restriction
        """
        return {
            "restriction_id": self.restriction_id,
            "name": self.name,
            "description": self.description,
            "countries": self.countries,
            "restriction_type": self.restriction_type,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, restriction_dict: Dict[str, Any]) -> 'GeoRestriction':
        """
        Create a restriction object from dictionary representation.
        
        Args:
            restriction_dict: Dictionary representation of the restriction
            
        Returns:
            GeoRestriction object
        """
        return cls(
            restriction_id=restriction_dict.get("restriction_id"),
            name=restriction_dict["name"],
            description=restriction_dict["description"],
            countries=restriction_dict["countries"],
            restriction_type=restriction_dict["restriction_type"],
            is_active=restriction_dict.get("is_active", True),
            metadata=restriction_dict.get("metadata", {})
        )
    
    def matches_country(self, country_code: str) -> bool:
        """
        Check if a country code matches this restriction.
        
        Args:
            country_code: ISO country code to check
            
        Returns:
            True if country code matches, False otherwise
        """
        return country_code.upper() in [c.upper() for c in self.countries]
    
    def __str__(self) -> str:
        return f"GeoRestriction(id={self.restriction_id}, name={self.name}, type={self.restriction_type})"


class DeviceFingerprint:
    """
    Represents a device fingerprint.
    """
    def __init__(
        self,
        fingerprint_id: str,
        user_id: str,
        device_name: str,
        fingerprint_data: Dict[str, Any],
        trust_level: str,  # "trusted", "known", "unknown", "suspicious"
        created_at: datetime = None,
        last_seen_at: datetime = None,
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.fingerprint_id = fingerprint_id or str(uuid.uuid4())
        self.user_id = user_id
        self.device_name = device_name
        self.fingerprint_data = fingerprint_data
        self.trust_level = trust_level
        self.created_at = created_at or datetime.now()
        self.last_seen_at = last_seen_at or self.created_at
        self.is_active = is_active
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert fingerprint object to dictionary representation.
        
        Returns:
            Dictionary representation of the fingerprint
        """
        return {
            "fingerprint_id": self.fingerprint_id,
            "user_id": self.user_id,
            "device_name": self.device_name,
            "fingerprint_data": self.fingerprint_data,
            "trust_level": self.trust_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, fingerprint_dict: Dict[str, Any]) -> 'DeviceFingerprint':
        """
        Create a fingerprint object from dictionary representation.
        
        Args:
            fingerprint_dict: Dictionary representation of the fingerprint
            
        Returns:
            DeviceFingerprint object
        """
        created_at = fingerprint_dict.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        last_seen_at = fingerprint_dict.get("last_seen_at")
        if last_seen_at and isinstance(last_seen_at, str):
            last_seen_at = datetime.fromisoformat(last_seen_at)
            
        return cls(
            fingerprint_id=fingerprint_dict.get("fingerprint_id"),
            user_id=fingerprint_dict["user_id"],
            device_name=fingerprint_dict["device_name"],
            fingerprint_data=fingerprint_dict["fingerprint_data"],
            trust_level=fingerprint_dict["trust_level"],
            created_at=created_at,
            last_seen_at=last_seen_at,
            is_active=fingerprint_dict.get("is_active", True),
            metadata=fingerprint_dict.get("metadata", {})
        )
    
    def matches(self, fingerprint_data: Dict[str, Any], threshold: float = 0.8) -> bool:
        """
        Check if fingerprint data matches this fingerprint.
        
        Args:
            fingerprint_data: Fingerprint data to check
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            True if fingerprint data matches, False otherwise
        """
        # Calculate similarity score
        score = self._calculate_similarity(fingerprint_data)
        return score >= threshold
    
    def _calculate_similarity(self, fingerprint_data: Dict[str, Any]) -> float:
        """
        Calculate similarity between fingerprint data.
        
        Args:
            fingerprint_data: Fingerprint data to compare
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # This is a simplified implementation
        # In a real system, you would use more sophisticated matching algorithms
        
        # Count matching fields
        matching_fields = 0
        total_fields = 0
        
        for key, value in self.fingerprint_data.items():
            if key in fingerprint_data:
                total_fields += 1
                if fingerprint_data[key] == value:
                    matching_fields += 1
        
        # Add fields in fingerprint_data that are not in self.fingerprint_data
        for key in fingerprint_data:
            if key not in self.fingerprint_data:
                total_fields += 1
        
        # Calculate similarity score
        if total_fields == 0:
            return 0.0
        
        return matching_fields / total_fields
    
    def update_last_seen(self) -> None:
        """
        Update the last seen timestamp.
        """
        self.last_seen_at = datetime.now()
    
    def __str__(self) -> str:
        return f"DeviceFingerprint(id={self.fingerprint_id}, user={self.user_id}, trust={self.trust_level})"


class RateLimitRule:
    """
    Represents a rate limiting rule.
    """
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        resource_pattern: str,
        limit: int,
        window_seconds: int,
        scope: str,  # "global", "ip", "user", "user_ip"
        action: str,  # "block", "delay", "captcha", "log"
        is_active: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.rule_id = rule_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.resource_pattern = resource_pattern
        self.limit = limit
        self.window_seconds = window_seconds
        self.scope = scope
        self.action = action
        self.is_active = is_active
        self.metadata = metadata or {}
        
        # Compile resource pattern
        try:
            self.compiled_pattern = re.compile(resource_pattern)
        except re.error as e:
            logger.error(f"Invalid resource pattern '{resource_pattern}': {e}")
            self.compiled_pattern = None
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert rule object to dictionary representation.
        
        Returns:
            Dictionary representation of the rule
        """
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "resource_pattern": self.resource_pattern,
            "limit": self.limit,
            "window_seconds": self.window_seconds,
            "scope": self.scope,
            "action": self.action,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, rule_dict: Dict[str, Any]) -> 'RateLimitRule':
        """
        Create a rule object from dictionary representation.
        
        Args:
            rule_dict: Dictionary representation of the rule
            
        Returns:
            RateLimitRule object
        """
        return cls(
            rule_id=rule_dict.get("rule_id"),
            name=rule_dict["name"],
            description=rule_dict["description"],
            resource_pattern=rule_dict["resource_pattern"],
            limit=rule_dict["limit"],
            window_seconds=rule_dict["window_seconds"],
            scope=rule_dict["scope"],
            action=rule_dict["action"],
            is_active=rule_dict.get("is_active", True),
            metadata=rule_dict.get("metadata", {})
        )
    
    def matches_resource(self, resource: str) -> bool:
        """
        Check if a resource matches this rule.
        
        Args:
            resource: Resource to check
            
        Returns:
            True if resource matches, False otherwise
        """
        if not self.compiled_pattern:
            return False
        
        return bool(self.compiled_pattern.match(resource))
    
    def __str__(self) -> str:
        return f"RateLimitRule(id={self.rule_id}, name={self.name}, limit={self.limit}/{self.window_seconds}s)"


class SecurityEvent:
    """
    Represents a security event.
    """
    def __init__(
        self,
        event_id: str,
        event_type: str,
        severity: str,  # "info", "low", "medium", "high", "critical"
        source: str,
        user_id: Optional[str],
        ip_address: Optional[str],
        resource: Optional[str],
        description: str,
        timestamp: datetime = None,
        metadata: Dict[str, Any] = None
    ):
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.severity = severity
        self.source = source
        self.user_id = user_id
        self.ip_address = ip_address
        self.resource = resource
        self.description = description
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event object to dictionary representation.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "severity": self.severity,
            "source": self.source,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "resource": self.resource,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, event_dict: Dict[str, Any]) -> 'SecurityEvent':
        """
        Create an event object from dictionary representation.
        
        Args:
            event_dict: Dictionary representation of the event
            
        Returns:
            SecurityEvent object
        """
        timestamp = event_dict.get("timestamp")
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
            
        return cls(
            event_id=event_dict.get("event_id"),
            event_type=event_dict["event_type"],
            severity=event_dict["severity"],
            source=event_dict["source"],
            user_id=event_dict.get("user_id"),
            ip_address=event_dict.get("ip_address"),
            resource=event_dict.get("resource"),
            description=event_dict["description"],
            timestamp=timestamp,
            metadata=event_dict.get("metadata", {})
        )
    
    def __str__(self) -> str:
        return f"SecurityEvent(id={self.event_id}, type={self.event_type}, severity={self.severity})"


class AdvancedSecurityManager:
    """
    Manages advanced security controls.
    """
    def __init__(
        self,
        event_manager: EventManager = None
    ):
        self.event_manager = event_manager or EventManager()
        
        # IP access rules
        self.ip_rules: Dict[str, IPAccessRule] = {}
        
        # Geo restrictions
        self.geo_restrictions: Dict[str, GeoRestriction] = {}
        
        # Device fingerprints
        self.device_fingerprints: Dict[str, DeviceFingerprint] = {}
        self.user_devices: Dict[str, List[str]] = {}  # user_id -> [fingerprint_id]
        
        # Rate limiting
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.rate_limit_counters: Dict[str, Dict[str, List[datetime]]] = {}  # rule_id -> scope_key -> [timestamps]
        
        # Security events
        self.security_events: List[SecurityEvent] = []
        
        # Register default IP rules
        self._register_default_ip_rules()
        
        # Register default rate limit rules
        self._register_default_rate_limit_rules()
        
    def _register_default_ip_rules(self) -> None:
        """
        Register default IP access rules.
        """
        # Block known malicious IP ranges
        self.register_ip_rule(IPAccessRule(
            rule_id="default-block-malicious",
            name="Block Malicious IPs",
            description="Block known malicious IP ranges",
            ip_ranges=[
                "198.51.100.0/24",  # Example range, would be actual malicious IPs in production
                "203.0.113.0/24"     # Example range, would be actual malicious IPs in production
            ],
            rule_type="deny",
            priority=100
        ))
        
        # Allow internal network
        self.register_ip_rule(IPAccessRule(
            rule_id="default-allow-internal",
            name="Allow Internal Network",
            description="Allow internal network access",
            ip_ranges=[
                "10.0.0.0/8",
                "172.16.0.0/12",
                "192.168.0.0/16"
            ],
            rule_type="allow",
            priority=10
        ))
    
    def _register_default_rate_limit_rules(self) -> None:
        """
        Register default rate limit rules.
        """
        # Login attempts
        self.register_rate_limit_rule(RateLimitRule(
            rule_id="default-login-attempts",
            name="Login Attempts",
            description="Limit login attempts per user",
            resource_pattern="^/auth/login$",
            limit=5,
            window_seconds=300,  # 5 minutes
            scope="user_ip",
            action="block"
        ))
        
        # API requests
        self.register_rate_limit_rule(RateLimitRule(
            rule_id="default-api-requests",
            name="API Requests",
            description="Limit API requests per IP",
            resource_pattern="^/api/",
            limit=100,
            window_seconds=60,  # 1 minute
            scope="ip",
            action="delay"
        ))
    
    def register_ip_rule(self, rule: IPAccessRule) -> IPAccessRule:
        """
        Register an IP access rule.
        
        Args:
            rule: IPAccessRule instance
            
        Returns:
            Registered IPAccessRule
            
        Raises:
            ConfigurationError: If rule ID already exists
        """
        if rule.rule_id in self.ip_rules:
            raise ConfigurationError(f"IP rule '{rule.rule_id}' already registered")
            
        # Store rule
        self.ip_rules[rule.rule_id] = rule
        
        # Emit event
        self.event_manager.emit_event("security.ip_rule_registered", {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "rule_type": rule.rule_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return rule
    
    def get_ip_rule(self, rule_id: str) -> Optional[IPAccessRule]:
        """
        Get an IP rule by ID.
        
        Args:
            rule_id: Rule ID to get
            
        Returns:
            IPAccessRule instance or None if not found
        """
        return self.ip_rules.get(rule_id)
    
    def check_ip_access(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an IP address is allowed.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Tuple of (is_allowed, deny_reason)
        """
        # Get all active rules
        active_rules = [rule for rule in self.ip_rules.values() if rule.is_active]
        
        # Sort rules by priority (highest first)
        active_rules.sort(key=lambda r: r.priority, reverse=True)
        
        # Check rules
        for rule in active_rules:
            if rule.matches_ip(ip_address):
                if rule.rule_type == "allow":
                    return True, None
                elif rule.rule_type == "deny":
                    return False, f"IP address blocked by rule: {rule.name}"
        
        # Default to allow if no rules match
        return True, None
    
    def register_geo_restriction(self, restriction: GeoRestriction) -> GeoRestriction:
        """
        Register a geographic restriction.
        
        Args:
            restriction: GeoRestriction instance
            
        Returns:
            Registered GeoRestriction
            
        Raises:
            ConfigurationError: If restriction ID already exists
        """
        if restriction.restriction_id in self.geo_restrictions:
            raise ConfigurationError(f"Geo restriction '{restriction.restriction_id}' already registered")
            
        # Store restriction
        self.geo_restrictions[restriction.restriction_id] = restriction
        
        # Emit event
        self.event_manager.emit_event("security.geo_restriction_registered", {
            "restriction_id": restriction.restriction_id,
            "name": restriction.name,
            "restriction_type": restriction.restriction_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return restriction
    
    def get_geo_restriction(self, restriction_id: str) -> Optional[GeoRestriction]:
        """
        Get a geo restriction by ID.
        
        Args:
            restriction_id: Restriction ID to get
            
        Returns:
            GeoRestriction instance or None if not found
        """
        return self.geo_restrictions.get(restriction_id)
    
    def check_geo_access(self, country_code: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a country is allowed.
        
        Args:
            country_code: ISO country code to check
            
        Returns:
            Tuple of (is_allowed, deny_reason)
        """
        # Get all active restrictions
        active_restrictions = [r for r in self.geo_restrictions.values() if r.is_active]
        
        # Check allow restrictions first
        allow_restrictions = [r for r in active_restrictions if r.restriction_type == "allow"]
        if allow_restrictions:
            # If there are allow restrictions, country must match at least one
            for restriction in allow_restrictions:
                if restriction.matches_country(country_code):
                    return True, None
            return False, "Country not in allowed list"
        
        # Check deny restrictions
        deny_restrictions = [r for r in active_restrictions if r.restriction_type == "deny"]
        for restriction in deny_restrictions:
            if restriction.matches_country(country_code):
                return False, f"Country blocked by restriction: {restriction.name}"
        
        # Default to allow if no restrictions match
        return True, None
    
    def register_device_fingerprint(
        self,
        user_id: str,
        device_name: str,
        fingerprint_data: Dict[str, Any],
        trust_level: str = "known"
    ) -> DeviceFingerprint:
        """
        Register a device fingerprint.
        
        Args:
            user_id: User ID the device belongs to
            device_name: Name of the device
            fingerprint_data: Device fingerprint data
            trust_level: Trust level for the device
            
        Returns:
            Registered DeviceFingerprint
        """
        # Create fingerprint
        fingerprint_id = str(uuid.uuid4())
        fingerprint = DeviceFingerprint(
            fingerprint_id=fingerprint_id,
            user_id=user_id,
            device_name=device_name,
            fingerprint_data=fingerprint_data,
            trust_level=trust_level
        )
        
        # Store fingerprint
        self.device_fingerprints[fingerprint_id] = fingerprint
        
        # Update user devices index
        if user_id not in self.user_devices:
            self.user_devices[user_id] = []
        self.user_devices[user_id].append(fingerprint_id)
        
        # Emit event
        self.event_manager.emit_event("security.device_registered", {
            "fingerprint_id": fingerprint_id,
            "user_id": user_id,
            "device_name": device_name,
            "trust_level": trust_level,
            "timestamp": datetime.now().isoformat()
        })
        
        return fingerprint
    
    def get_device_fingerprint(self, fingerprint_id: str) -> Optional[DeviceFingerprint]:
        """
        Get a device fingerprint by ID.
        
        Args:
            fingerprint_id: Fingerprint ID to get
            
        Returns:
            DeviceFingerprint instance or None if not found
        """
        return self.device_fingerprints.get(fingerprint_id)
    
    def get_user_devices(self, user_id: str) -> List[DeviceFingerprint]:
        """
        Get all devices for a user.
        
        Args:
            user_id: User ID to get devices for
            
        Returns:
            List of DeviceFingerprint instances
        """
        if user_id not in self.user_devices:
            return []
            
        return [self.device_fingerprints[fingerprint_id] for fingerprint_id in self.user_devices[user_id]
                if fingerprint_id in self.device_fingerprints]
    
    def match_device_fingerprint(
        self,
        user_id: str,
        fingerprint_data: Dict[str, Any],
        threshold: float = 0.8
    ) -> Tuple[bool, Optional[DeviceFingerprint]]:
        """
        Match a device fingerprint to a user's known devices.
        
        Args:
            user_id: User ID to match devices for
            fingerprint_data: Device fingerprint data to match
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            Tuple of (is_match, matching_fingerprint)
        """
        # Get user devices
        user_devices = self.get_user_devices(user_id)
        
        # Check for matches
        for fingerprint in user_devices:
            if fingerprint.matches(fingerprint_data, threshold):
                # Update last seen
                fingerprint.update_last_seen()
                return True, fingerprint
        
        return False, None
    
    def update_device_trust_level(
        self,
        fingerprint_id: str,
        trust_level: str
    ) -> bool:
        """
        Update a device's trust level.
        
        Args:
            fingerprint_id: Fingerprint ID to update
            trust_level: New trust level
            
        Returns:
            True if trust level was updated, False otherwise
        """
        fingerprint = self.get_device_fingerprint(fingerprint_id)
        if not fingerprint:
            return False
            
        # Update trust level
        fingerprint.trust_level = trust_level
        
        # Emit event
        self.event_manager.emit_event("security.device_trust_updated", {
            "fingerprint_id": fingerprint_id,
            "user_id": fingerprint.user_id,
            "device_name": fingerprint.device_name,
            "trust_level": trust_level,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def register_rate_limit_rule(self, rule: RateLimitRule) -> RateLimitRule:
        """
        Register a rate limit rule.
        
        Args:
            rule: RateLimitRule instance
            
        Returns:
            Registered RateLimitRule
            
        Raises:
            ConfigurationError: If rule ID already exists
        """
        if rule.rule_id in self.rate_limit_rules:
            raise ConfigurationError(f"Rate limit rule '{rule.rule_id}' already registered")
            
        # Store rule
        self.rate_limit_rules[rule.rule_id] = rule
        
        # Initialize counters
        self.rate_limit_counters[rule.rule_id] = {}
        
        # Emit event
        self.event_manager.emit_event("security.rate_limit_rule_registered", {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "limit": rule.limit,
            "window_seconds": rule.window_seconds,
            "timestamp": datetime.now().isoformat()
        })
        
        return rule
    
    def get_rate_limit_rule(self, rule_id: str) -> Optional[RateLimitRule]:
        """
        Get a rate limit rule by ID.
        
        Args:
            rule_id: Rule ID to get
            
        Returns:
            RateLimitRule instance or None if not found
        """
        return self.rate_limit_rules.get(rule_id)
    
    def check_rate_limit(
        self,
        resource: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if a request is rate limited.
        
        Args:
            resource: Resource being accessed
            user_id: Optional user ID making the request
            ip_address: Optional IP address making the request
            
        Returns:
            Tuple of (is_allowed, action, deny_reason)
        """
        # Get all active rules
        active_rules = [rule for rule in self.rate_limit_rules.values() if rule.is_active]
        
        # Find matching rules
        matching_rules = [rule for rule in active_rules if rule.matches_resource(resource)]
        
        # Check each rule
        for rule in matching_rules:
            # Determine scope key
            scope_key = self._get_scope_key(rule.scope, user_id, ip_address)
            if not scope_key:
                continue
                
            # Get counter for this rule and scope
            if rule.rule_id not in self.rate_limit_counters:
                self.rate_limit_counters[rule.rule_id] = {}
                
            if scope_key not in self.rate_limit_counters[rule.rule_id]:
                self.rate_limit_counters[rule.rule_id][scope_key] = []
                
            counter = self.rate_limit_counters[rule.rule_id][scope_key]
            
            # Remove expired timestamps
            now = datetime.now()
            window_start = now - timedelta(seconds=rule.window_seconds)
            counter = [ts for ts in counter if ts >= window_start]
            self.rate_limit_counters[rule.rule_id][scope_key] = counter
            
            # Check if limit is exceeded
            if len(counter) >= rule.limit:
                return False, rule.action, f"Rate limit exceeded: {rule.name}"
            
            # Add current timestamp
            counter.append(now)
            
        # No rate limits exceeded
        return True, None, None
    
    def _get_scope_key(
        self,
        scope: str,
        user_id: Optional[str],
        ip_address: Optional[str]
    ) -> Optional[str]:
        """
        Get a scope key for rate limiting.
        
        Args:
            scope: Scope type
            user_id: Optional user ID
            ip_address: Optional IP address
            
        Returns:
            Scope key or None if scope is not applicable
        """
        if scope == "global":
            return "global"
        elif scope == "ip" and ip_address:
            return f"ip:{ip_address}"
        elif scope == "user" and user_id:
            return f"user:{user_id}"
        elif scope == "user_ip" and user_id and ip_address:
            return f"user:{user_id}:ip:{ip_address}"
        return None
    
    def record_security_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        resource: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> SecurityEvent:
        """
        Record a security event.
        
        Args:
            event_type: Type of event
            severity: Severity level
            source: Source of the event
            description: Description of the event
            user_id: Optional user ID related to the event
            ip_address: Optional IP address related to the event
            resource: Optional resource related to the event
            metadata: Optional additional metadata
            
        Returns:
            Recorded SecurityEvent
        """
        # Create event
        event_id = str(uuid.uuid4())
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            source=source,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            description=description,
            metadata=metadata
        )
        
        # Store event
        self.security_events.append(event)
        
        # Emit event
        self.event_manager.emit_event("security.event_recorded", {
            "event_id": event_id,
            "event_type": event_type,
            "severity": severity,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        
        return event
    
    def get_security_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SecurityEvent]:
        """
        Get security events with optional filtering.
        
        Args:
            event_type: Optional event type to filter by
            severity: Optional severity level to filter by
            user_id: Optional user ID to filter by
            ip_address: Optional IP address to filter by
            start_time: Optional start time to filter by
            end_time: Optional end time to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of SecurityEvent instances
        """
        # Apply filters
        filtered_events = self.security_events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
        if severity:
            filtered_events = [e for e in filtered_events if e.severity == severity]
            
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
            
        if ip_address:
            filtered_events = [e for e in filtered_events if e.ip_address == ip_address]
            
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
            
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
            
        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit
        return filtered_events[:limit]
