"""
Multi-Factor Authentication module for ApexAgent.

This module provides the core MFA functionality for the ApexAgent platform,
including various authentication factors and verification workflows.
"""

import os
import base64
import hmac
import time
import uuid
import logging
import secrets
import hashlib
import pyotp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Protocol

from src.core.error_handling.errors import AuthenticationError, ConfigurationError
from src.core.event_system.event_manager import EventManager

logger = logging.getLogger(__name__)

class MFAProvider:
    """Base interface for MFA providers."""
    
    def generate_challenge(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an authentication challenge.
        
        Args:
            user_id: User ID to generate challenge for
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing challenge details
        """
        raise NotImplementedError("Subclasses must implement generate_challenge method")
        
    def verify_response(self, user_id: str, challenge_id: str, response: str) -> bool:
        """
        Verify a response to an authentication challenge.
        
        Args:
            user_id: User ID to verify response for
            challenge_id: ID of the challenge being responded to
            response: User's response to the challenge
            
        Returns:
            True if response is valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement verify_response method")
        
    def get_setup_instructions(self, user_id: str) -> Dict[str, Any]:
        """
        Get setup instructions for this MFA method.
        
        Args:
            user_id: User ID to get setup instructions for
            
        Returns:
            Dictionary containing setup instructions and data
        """
        raise NotImplementedError("Subclasses must implement get_setup_instructions method")


class TOTPProvider(MFAProvider):
    """Time-based One-Time Password (TOTP) MFA provider."""
    
    def __init__(self, issuer_name: str = "ApexAgent"):
        """
        Initialize the TOTP provider.
        
        Args:
            issuer_name: Name of the issuer for TOTP apps
        """
        self.issuer_name = issuer_name
        self.secrets: Dict[str, str] = {}  # user_id -> secret
        self.challenges: Dict[str, Dict[str, Any]] = {}  # challenge_id -> challenge_data
        
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret.
        
        Returns:
            Base32 encoded secret
        """
        return pyotp.random_base32()
        
    def generate_challenge(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a TOTP challenge.
        
        Args:
            user_id: User ID to generate challenge for
            
        Returns:
            Dictionary containing challenge details
            
        Raises:
            AuthenticationError: If user does not have TOTP set up
        """
        if user_id not in self.secrets:
            raise AuthenticationError("TOTP not set up for this user")
            
        challenge_id = str(uuid.uuid4())
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "type": "totp",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat()
        }
        
        self.challenges[challenge_id] = challenge
        return challenge
        
    def verify_response(self, user_id: str, challenge_id: str, response: str) -> bool:
        """
        Verify a TOTP response.
        
        Args:
            user_id: User ID to verify response for
            challenge_id: ID of the challenge being responded to
            response: TOTP code entered by the user
            
        Returns:
            True if TOTP code is valid, False otherwise
        """
        # Check if challenge exists and is valid
        if challenge_id not in self.challenges:
            return False
            
        challenge = self.challenges[challenge_id]
        if challenge["user_id"] != user_id:
            return False
            
        # Check if challenge has expired
        expires_at = datetime.fromisoformat(challenge["expires_at"])
        if datetime.now() > expires_at:
            return False
            
        # Verify TOTP code
        if user_id not in self.secrets:
            return False
            
        totp = pyotp.TOTP(self.secrets[user_id])
        is_valid = totp.verify(response)
        
        # Remove challenge after verification
        if is_valid:
            del self.challenges[challenge_id]
            
        return is_valid
        
    def get_setup_instructions(self, user_id: str) -> Dict[str, Any]:
        """
        Get TOTP setup instructions.
        
        Args:
            user_id: User ID to get setup instructions for
            
        Returns:
            Dictionary containing setup instructions and data
        """
        # Generate a new secret for the user
        secret = self.generate_secret()
        self.secrets[user_id] = secret
        
        # Generate provisioning URI for QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=user_id, issuer_name=self.issuer_name)
        
        return {
            "type": "totp",
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "instructions": "Scan the QR code with your authenticator app or manually enter the secret key."
        }


class SMSProvider(MFAProvider):
    """SMS-based verification code MFA provider."""
    
    def __init__(self, sms_service=None):
        """
        Initialize the SMS provider.
        
        Args:
            sms_service: Service for sending SMS messages
        """
        self.sms_service = sms_service
        self.phone_numbers: Dict[str, str] = {}  # user_id -> phone_number
        self.challenges: Dict[str, Dict[str, Any]] = {}  # challenge_id -> challenge_data
        
    def generate_code(self, length: int = 6) -> str:
        """
        Generate a random verification code.
        
        Args:
            length: Length of the code
            
        Returns:
            Random numeric code
        """
        return ''.join(secrets.choice('0123456789') for _ in range(length))
        
    def generate_challenge(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an SMS challenge.
        
        Args:
            user_id: User ID to generate challenge for
            
        Returns:
            Dictionary containing challenge details
            
        Raises:
            AuthenticationError: If user does not have a phone number set up
        """
        if user_id not in self.phone_numbers:
            raise AuthenticationError("Phone number not set up for this user")
            
        phone_number = self.phone_numbers[user_id]
        code = self.generate_code()
        challenge_id = str(uuid.uuid4())
        
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "type": "sms",
            "code": code,
            "phone_number": phone_number,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
        }
        
        self.challenges[challenge_id] = challenge
        
        # Send SMS if service is available
        if self.sms_service:
            message = f"Your verification code is: {code}"
            self.sms_service.send_sms(phone_number, message)
            
        return {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "type": "sms",
            "phone_number": self._mask_phone_number(phone_number),
            "created_at": challenge["created_at"],
            "expires_at": challenge["expires_at"]
        }
        
    def verify_response(self, user_id: str, challenge_id: str, response: str) -> bool:
        """
        Verify an SMS response.
        
        Args:
            user_id: User ID to verify response for
            challenge_id: ID of the challenge being responded to
            response: Verification code entered by the user
            
        Returns:
            True if verification code is valid, False otherwise
        """
        # Check if challenge exists and is valid
        if challenge_id not in self.challenges:
            return False
            
        challenge = self.challenges[challenge_id]
        if challenge["user_id"] != user_id:
            return False
            
        # Check if challenge has expired
        expires_at = datetime.fromisoformat(challenge["expires_at"])
        if datetime.now() > expires_at:
            return False
            
        # Verify code
        is_valid = challenge["code"] == response
        
        # Remove challenge after verification
        if is_valid:
            del self.challenges[challenge_id]
            
        return is_valid
        
    def get_setup_instructions(self, user_id: str) -> Dict[str, Any]:
        """
        Get SMS setup instructions.
        
        Args:
            user_id: User ID to get setup instructions for
            
        Returns:
            Dictionary containing setup instructions and data
        """
        return {
            "type": "sms",
            "instructions": "Enter your phone number to receive verification codes via SMS."
        }
        
    def set_phone_number(self, user_id: str, phone_number: str) -> bool:
        """
        Set a user's phone number for SMS verification.
        
        Args:
            user_id: User ID to set phone number for
            phone_number: Phone number in E.164 format
            
        Returns:
            True if phone number was set successfully
        """
        # TODO: Validate phone number format
        self.phone_numbers[user_id] = phone_number
        return True
        
    def _mask_phone_number(self, phone_number: str) -> str:
        """
        Mask a phone number for display.
        
        Args:
            phone_number: Phone number to mask
            
        Returns:
            Masked phone number
        """
        if len(phone_number) <= 4:
            return phone_number
            
        return '*' * (len(phone_number) - 4) + phone_number[-4:]


class EmailProvider(MFAProvider):
    """Email-based verification code MFA provider."""
    
    def __init__(self, email_service=None):
        """
        Initialize the Email provider.
        
        Args:
            email_service: Service for sending emails
        """
        self.email_service = email_service
        self.email_addresses: Dict[str, str] = {}  # user_id -> email_address
        self.challenges: Dict[str, Dict[str, Any]] = {}  # challenge_id -> challenge_data
        
    def generate_code(self, length: int = 8) -> str:
        """
        Generate a random verification code.
        
        Args:
            length: Length of the code
            
        Returns:
            Random alphanumeric code
        """
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return ''.join(secrets.choice(alphabet) for _ in range(length))
        
    def generate_challenge(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an email challenge.
        
        Args:
            user_id: User ID to generate challenge for
            
        Returns:
            Dictionary containing challenge details
            
        Raises:
            AuthenticationError: If user does not have an email address set up
        """
        if user_id not in self.email_addresses:
            raise AuthenticationError("Email address not set up for this user")
            
        email_address = self.email_addresses[user_id]
        code = self.generate_code()
        challenge_id = str(uuid.uuid4())
        
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "type": "email",
            "code": code,
            "email_address": email_address,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
        
        self.challenges[challenge_id] = challenge
        
        # Send email if service is available
        if self.email_service:
            subject = "Your verification code"
            body = f"Your verification code is: {code}"
            self.email_service.send_email(email_address, subject, body)
            
        return {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "type": "email",
            "email_address": self._mask_email_address(email_address),
            "created_at": challenge["created_at"],
            "expires_at": challenge["expires_at"]
        }
        
    def verify_response(self, user_id: str, challenge_id: str, response: str) -> bool:
        """
        Verify an email response.
        
        Args:
            user_id: User ID to verify response for
            challenge_id: ID of the challenge being responded to
            response: Verification code entered by the user
            
        Returns:
            True if verification code is valid, False otherwise
        """
        # Check if challenge exists and is valid
        if challenge_id not in self.challenges:
            return False
            
        challenge = self.challenges[challenge_id]
        if challenge["user_id"] != user_id:
            return False
            
        # Check if challenge has expired
        expires_at = datetime.fromisoformat(challenge["expires_at"])
        if datetime.now() > expires_at:
            return False
            
        # Verify code
        is_valid = challenge["code"] == response
        
        # Remove challenge after verification
        if is_valid:
            del self.challenges[challenge_id]
            
        return is_valid
        
    def get_setup_instructions(self, user_id: str) -> Dict[str, Any]:
        """
        Get email setup instructions.
        
        Args:
            user_id: User ID to get setup instructions for
            
        Returns:
            Dictionary containing setup instructions and data
        """
        return {
            "type": "email",
            "instructions": "Enter your email address to receive verification codes via email."
        }
        
    def set_email_address(self, user_id: str, email_address: str) -> bool:
        """
        Set a user's email address for email verification.
        
        Args:
            user_id: User ID to set email address for
            email_address: Email address
            
        Returns:
            True if email address was set successfully
        """
        # TODO: Validate email address format
        self.email_addresses[user_id] = email_address
        return True
        
    def _mask_email_address(self, email_address: str) -> str:
        """
        Mask an email address for display.
        
        Args:
            email_address: Email address to mask
            
        Returns:
            Masked email address
        """
        parts = email_address.split('@')
        if len(parts) != 2:
            return email_address
            
        username, domain = parts
        if len(username) <= 2:
            masked_username = username
        else:
            masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
            
        return f"{masked_username}@{domain}"


class BackupCodesProvider(MFAProvider):
    """Backup codes MFA provider."""
    
    def __init__(self, code_count: int = 10, code_length: int = 8):
        """
        Initialize the backup codes provider.
        
        Args:
            code_count: Number of backup codes to generate
            code_length: Length of each backup code
        """
        self.code_count = code_count
        self.code_length = code_length
        self.user_codes: Dict[str, Dict[str, bool]] = {}  # user_id -> {code -> used}
        self.challenges: Dict[str, Dict[str, Any]] = {}  # challenge_id -> challenge_data
        
    def generate_codes(self) -> List[str]:
        """
        Generate a set of backup codes.
        
        Returns:
            List of backup codes
        """
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        codes = []
        for _ in range(self.code_count):
            code = ''.join(secrets.choice(alphabet) for _ in range(self.code_length))
            codes.append(code)
        return codes
        
    def generate_challenge(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a backup code challenge.
        
        Args:
            user_id: User ID to generate challenge for
            
        Returns:
            Dictionary containing challenge details
            
        Raises:
            AuthenticationError: If user does not have backup codes set up
        """
        if user_id not in self.user_codes or not self.user_codes[user_id]:
            raise AuthenticationError("Backup codes not set up for this user")
            
        challenge_id = str(uuid.uuid4())
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "type": "backup_codes",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
        
        self.challenges[challenge_id] = challenge
        
        return challenge
        
    def verify_response(self, user_id: str, challenge_id: str, response: str) -> bool:
        """
        Verify a backup code response.
        
        Args:
            user_id: User ID to verify response for
            challenge_id: ID of the challenge being responded to
            response: Backup code entered by the user
            
        Returns:
            True if backup code is valid, False otherwise
        """
        # Check if challenge exists and is valid
        if challenge_id not in self.challenges:
            return False
            
        challenge = self.challenges[challenge_id]
        if challenge["user_id"] != user_id:
            return False
            
        # Check if challenge has expired
        expires_at = datetime.fromisoformat(challenge["expires_at"])
        if datetime.now() > expires_at:
            return False
            
        # Check if user has backup codes
        if user_id not in self.user_codes:
            return False
            
        # Verify code
        user_backup_codes = self.user_codes[user_id]
        if response not in user_backup_codes:
            return False
            
        # Check if code has been used
        if user_backup_codes[response]:
            return False
            
        # Mark code as used
        user_backup_codes[response] = True
        
        # Remove challenge after verification
        del self.challenges[challenge_id]
        
        return True
        
    def get_setup_instructions(self, user_id: str) -> Dict[str, Any]:
        """
        Get backup codes setup instructions.
        
        Args:
            user_id: User ID to get setup instructions for
            
        Returns:
            Dictionary containing setup instructions and data
        """
        codes = self.generate_codes()
        
        # Store codes for the user
        self.user_codes[user_id] = {code: False for code in codes}
        
        return {
            "type": "backup_codes",
            "codes": codes,
            "instructions": "Save these backup codes in a secure location. Each code can only be used once."
        }
        
    def get_remaining_codes(self, user_id: str) -> List[str]:
        """
        Get a user's remaining backup codes.
        
        Args:
            user_id: User ID to get codes for
            
        Returns:
            List of unused backup codes
        """
        if user_id not in self.user_codes:
            return []
            
        return [code for code, used in self.user_codes[user_id].items() if not used]
        
    def regenerate_codes(self, user_id: str) -> List[str]:
        """
        Regenerate a user's backup codes.
        
        Args:
            user_id: User ID to regenerate codes for
            
        Returns:
            List of new backup codes
        """
        codes = self.generate_codes()
        self.user_codes[user_id] = {code: False for code in codes}
        return codes


class MFAManager:
    """Manages MFA methods and verification workflows."""
    
    def __init__(self, event_manager: EventManager = None):
        """
        Initialize the MFA manager.
        
        Args:
            event_manager: Event manager for emitting events
        """
        self.providers: Dict[str, MFAProvider] = {}
        self.user_methods: Dict[str, Dict[str, Dict[str, Any]]] = {}  # user_id -> provider_id -> method_data
        self.event_manager = event_manager or EventManager()
        
        # Register default providers
        self.register_provider("totp", TOTPProvider())
        self.register_provider("sms", SMSProvider())
        self.register_provider("email", EmailProvider())
        self.register_provider("backup_codes", BackupCodesProvider())
        
    def register_provider(self, provider_id: str, provider: MFAProvider) -> None:
        """
        Register an MFA provider.
        
        Args:
            provider_id: Unique identifier for the provider
            provider: MFAProvider instance
            
        Raises:
            ConfigurationError: If provider ID already exists
        """
        if provider_id in self.providers:
            raise ConfigurationError(f"MFA provider '{provider_id}' already registered")
            
        self.providers[provider_id] = provider
        
    def enable_method(self, user_id: str, provider_id: str, setup_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enable an MFA method for a user.
        
        Args:
            user_id: User ID to enable method for
            provider_id: Provider ID to enable
            setup_data: Provider-specific setup data
            
        Returns:
            Dictionary containing setup result
            
        Raises:
            ConfigurationError: If provider does not exist
        """
        if provider_id not in self.providers:
            raise ConfigurationError(f"MFA provider '{provider_id}' not found")
            
        provider = self.providers[provider_id]
        
        # Get setup instructions if not already set up
        if setup_data is None:
            setup_result = provider.get_setup_instructions(user_id)
        else:
            # Process provider-specific setup
            if provider_id == "sms" and "phone_number" in setup_data:
                provider.set_phone_number(user_id, setup_data["phone_number"])
                setup_result = {"success": True, "type": "sms"}
            elif provider_id == "email" and "email_address" in setup_data:
                provider.set_email_address(user_id, setup_data["email_address"])
                setup_result = {"success": True, "type": "email"}
            else:
                setup_result = {"success": False, "error": "Invalid setup data"}
        
        # Initialize user methods if needed
        if user_id not in self.user_methods:
            self.user_methods[user_id] = {}
            
        # Store method data
        self.user_methods[user_id][provider_id] = {
            "enabled": True,
            "enabled_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        # Emit event
        self.event_manager.emit_event("mfa.method_enabled", {
            "user_id": user_id,
            "provider_id": provider_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return setup_result
        
    def disable_method(self, user_id: str, provider_id: str) -> bool:
        """
        Disable an MFA method for a user.
        
        Args:
            user_id: User ID to disable method for
            provider_id: Provider ID to disable
            
        Returns:
            True if method was disabled, False otherwise
        """
        if user_id not in self.user_methods or provider_id not in self.user_methods[user_id]:
            return False
            
        # Disable the method
        self.user_methods[user_id][provider_id]["enabled"] = False
        
        # Emit event
        self.event_manager.emit_event("mfa.method_disabled", {
            "user_id": user_id,
            "provider_id": provider_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
        
    def get_enabled_methods(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all enabled MFA methods for a user.
        
        Args:
            user_id: User ID to get methods for
            
        Returns:
            List of enabled MFA methods
        """
        if user_id not in self.user_methods:
            return []
            
        enabled_methods = []
        for provider_id, method_data in self.user_methods[user_id].items():
            if method_data.get("enabled", False):
                method_info = {
                    "provider_id": provider_id,
                    "enabled_at": method_data.get("enabled_at"),
                    "last_used": method_data.get("last_used")
                }
                enabled_methods.append(method_info)
                
        return enabled_methods
        
    def initiate_verification(self, user_id: str, provider_id: str) -> Dict[str, Any]:
        """
        Initiate MFA verification.
        
        Args:
            user_id: User ID to verify
            provider_id: Provider ID to use for verification
            
        Returns:
            Dictionary containing challenge details
            
        Raises:
            AuthenticationError: If method is not enabled for the user
            ConfigurationError: If provider does not exist
        """
        if provider_id not in self.providers:
            raise ConfigurationError(f"MFA provider '{provider_id}' not found")
            
        if (user_id not in self.user_methods or 
            provider_id not in self.user_methods[user_id] or 
            not self.user_methods[user_id][provider_id].get("enabled", False)):
            raise AuthenticationError(f"MFA method '{provider_id}' not enabled for this user")
            
        provider = self.providers[provider_id]
        challenge = provider.generate_challenge(user_id)
        
        # Emit event
        self.event_manager.emit_event("mfa.verification_initiated", {
            "user_id": user_id,
            "provider_id": provider_id,
            "challenge_id": challenge.get("challenge_id"),
            "timestamp": datetime.now().isoformat()
        })
        
        return challenge
        
    def complete_verification(self, user_id: str, provider_id: str, challenge_id: str, response: str) -> bool:
        """
        Complete MFA verification.
        
        Args:
            user_id: User ID to verify
            provider_id: Provider ID used for verification
            challenge_id: ID of the challenge being responded to
            response: User's response to the challenge
            
        Returns:
            True if verification was successful, False otherwise
            
        Raises:
            ConfigurationError: If provider does not exist
        """
        if provider_id not in self.providers:
            raise ConfigurationError(f"MFA provider '{provider_id}' not found")
            
        provider = self.providers[provider_id]
        is_valid = provider.verify_response(user_id, challenge_id, response)
        
        if is_valid and user_id in self.user_methods and provider_id in self.user_methods[user_id]:
            # Update last used timestamp
            self.user_methods[user_id][provider_id]["last_used"] = datetime.now().isoformat()
            
            # Emit event
            self.event_manager.emit_event("mfa.verification_completed", {
                "user_id": user_id,
                "provider_id": provider_id,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
        elif not is_valid:
            # Emit event for failed verification
            self.event_manager.emit_event("mfa.verification_failed", {
                "user_id": user_id,
                "provider_id": provider_id,
                "challenge_id": challenge_id,
                "timestamp": datetime.now().isoformat()
            })
            
        return is_valid
        
    def is_mfa_enabled(self, user_id: str) -> bool:
        """
        Check if a user has any MFA methods enabled.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user has at least one MFA method enabled, False otherwise
        """
        if user_id not in self.user_methods:
            return False
            
        return any(method_data.get("enabled", False) 
                  for method_data in self.user_methods[user_id].values())
