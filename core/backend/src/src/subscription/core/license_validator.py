"""
License Validator module for ApexAgent Subscription and Licensing System.

This module provides functionality for validating license keys, checking their
authenticity, expiration status, and feature entitlements.
"""

import base64
import hashlib
import json
import os
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from subscription.core.license_generator import (
    LicenseFeature, LicenseMetadata, LicenseMetadataEncoder,
    LicenseSignature, LicenseStatus, LicenseType
)


class ValidationResult:
    """Class representing the result of license validation."""

    def __init__(
        self,
        is_valid: bool,
        license_id: Optional[str] = None,
        status: Optional[LicenseStatus] = None,
        features: Optional[List[LicenseFeature]] = None,
        expiration_date: Optional[datetime] = None,
        error_message: Optional[str] = None,
        metadata: Optional[LicenseMetadata] = None
    ):
        """
        Initialize validation result.

        Args:
            is_valid: Whether the license is valid
            license_id: Identifier for the license
            status: Status of the license
            features: List of enabled features
            expiration_date: Date when the license expires
            error_message: Error message if validation failed
            metadata: Full license metadata if available
        """
        self.is_valid = is_valid
        self.license_id = license_id
        self.status = status
        self.features = features
        self.expiration_date = expiration_date
        self.error_message = error_message
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Union[bool, str, List[str], Dict]]:
        """
        Convert validation result to dictionary.

        Returns:
            Dictionary representation of the validation result
        """
        result = {
            "is_valid": self.is_valid,
            "license_id": self.license_id,
        }

        if self.status:
            result["status"] = self.status.value

        if self.features:
            result["features"] = [feature.value for feature in self.features]

        if self.expiration_date:
            result["expiration_date"] = self.expiration_date.isoformat()

        if self.error_message:
            result["error_message"] = self.error_message

        if self.metadata:
            result["metadata"] = self.metadata.to_dict()

        return result


class ValidationCache:
    """Cache for license validation results to improve performance."""

    def __init__(self, cache_duration_seconds: int = 3600):
        """
        Initialize validation cache.

        Args:
            cache_duration_seconds: Duration to cache validation results in seconds
        """
        self.cache: Dict[str, Tuple[ValidationResult, float]] = {}
        self.cache_duration = cache_duration_seconds

    def get(self, license_key: str) -> Optional[ValidationResult]:
        """
        Get cached validation result for a license key.

        Args:
            license_key: License key to look up

        Returns:
            Cached validation result or None if not found or expired
        """
        if license_key not in self.cache:
            return None

        result, timestamp = self.cache[license_key]
        current_time = time.time()

        # Check if cache entry has expired
        if current_time - timestamp > self.cache_duration:
            del self.cache[license_key]
            return None

        return result

    def set(self, license_key: str, result: ValidationResult) -> None:
        """
        Cache validation result for a license key.

        Args:
            license_key: License key to cache
            result: Validation result to cache
        """
        self.cache[license_key] = (result, time.time())

    def invalidate(self, license_key: str) -> None:
        """
        Invalidate cached result for a license key.

        Args:
            license_key: License key to invalidate
        """
        if license_key in self.cache:
            del self.cache[license_key]

    def clear(self) -> None:
        """Clear all cached validation results."""
        self.cache.clear()


class LicenseValidator:
    """Main class for license validation."""

    def __init__(
        self,
        signature_handler: LicenseSignature,
        cache_duration_seconds: int = 3600,
        license_db_connector: Optional[object] = None
    ):
        """
        Initialize license validator.

        Args:
            signature_handler: Handler for license signature verification
            cache_duration_seconds: Duration to cache validation results
            license_db_connector: Connector to license database for online validation
        """
        self.signature_handler = signature_handler
        self.cache = ValidationCache(cache_duration_seconds)
        self.license_db_connector = license_db_connector
        self.prefix_map = {
            "APX-PRP": LicenseType.PERPETUAL,
            "APX-SUB": LicenseType.SUBSCRIPTION,
            "APX-TRL": LicenseType.TRIAL,
            "APX-DEV": LicenseType.DEVELOPMENT,
            "APX-ENT": LicenseType.ENTERPRISE
        }

    def _parse_license_key(self, license_key: str) -> Tuple[str, str, str, str]:
        """
        Parse license key into components.

        Args:
            license_key: License key to parse

        Returns:
            Tuple of (prefix, encoded_metadata, signature, checksum)

        Raises:
            ValueError: If license key format is invalid
        """
        try:
            parts = license_key.split(".")
            if len(parts) != 4:
                raise ValueError("Invalid license key format")

            prefix, encoded_metadata, signature, checksum = parts
            return prefix, encoded_metadata, signature, checksum
        except Exception as e:
            raise ValueError(f"Failed to parse license key: {str(e)}")

    def _verify_checksum(self, data: str, checksum: str) -> bool:
        """
        Verify checksum for license data.

        Args:
            data: License data
            checksum: Checksum to verify

        Returns:
            True if checksum is valid, False otherwise
        """
        calculated_checksum = hashlib.sha256(data.encode('utf-8')).hexdigest()[:8]
        return calculated_checksum == checksum

    def _verify_signature(self, data: str, signature: str) -> bool:
        """
        Verify signature for license data.

        Args:
            data: License data
            signature: Signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        return self.signature_handler.verify(data, signature)

    def _check_expiration(self, metadata: LicenseMetadata) -> bool:
        """
        Check if license has expired.

        Args:
            metadata: License metadata

        Returns:
            True if license is valid (not expired), False otherwise
        """
        if metadata.license_type == LicenseType.PERPETUAL:
            return True

        if not metadata.expiration_date:
            return True

        current_date = datetime.now()
        return current_date <= metadata.expiration_date

    def _check_online_status(self, license_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check license status with online database.

        Args:
            license_id: License ID to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.license_db_connector:
            # If no database connector is available, assume license is valid
            return True, None

        try:
            # This would be implemented to query the license database
            # For now, we'll just return True
            return True, None
        except Exception as e:
            return False, f"Failed to verify license online: {str(e)}"

    def validate_license_key(self, license_key: str, skip_cache: bool = False) -> ValidationResult:
        """
        Validate a license key.

        Args:
            license_key: License key to validate
            skip_cache: Whether to skip cache lookup

        Returns:
            ValidationResult with validation status and details
        """
        # Check cache first if not skipping
        if not skip_cache:
            cached_result = self.cache.get(license_key)
            if cached_result:
                return cached_result

        try:
            # Parse license key
            prefix, encoded_metadata, signature, checksum = self._parse_license_key(license_key)

            # Verify checksum
            data_to_verify = f"{prefix}.{encoded_metadata}.{signature}"
            if not self._verify_checksum(data_to_verify, checksum):
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid license checksum"
                )

            # Verify signature
            data_to_sign = f"{prefix}.{encoded_metadata}"
            if not self._verify_signature(data_to_sign, signature):
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid license signature"
                )

            # Decode metadata
            metadata = LicenseMetadataEncoder.decode(encoded_metadata)

            # Check expiration
            is_expired = not self._check_expiration(metadata)
            if is_expired:
                return ValidationResult(
                    is_valid=False,
                    license_id=metadata.license_id,
                    status=LicenseStatus.EXPIRED,
                    features=metadata.features,
                    expiration_date=metadata.expiration_date,
                    error_message="License has expired",
                    metadata=metadata
                )

            # Check online status if available
            online_valid, error_message = self._check_online_status(metadata.license_id)
            if not online_valid:
                return ValidationResult(
                    is_valid=False,
                    license_id=metadata.license_id,
                    status=LicenseStatus.REVOKED,
                    features=metadata.features,
                    expiration_date=metadata.expiration_date,
                    error_message=error_message,
                    metadata=metadata
                )

            # License is valid
            result = ValidationResult(
                is_valid=True,
                license_id=metadata.license_id,
                status=LicenseStatus.ACTIVE,
                features=metadata.features,
                expiration_date=metadata.expiration_date,
                metadata=metadata
            )

            # Cache the result
            self.cache.set(license_key, result)

            return result
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"License validation failed: {str(e)}"
            )

    def has_feature(self, license_key: str, feature: LicenseFeature) -> bool:
        """
        Check if a license has a specific feature.

        Args:
            license_key: License key to check
            feature: Feature to check for

        Returns:
            True if license has the feature, False otherwise
        """
        result = self.validate_license_key(license_key)
        if not result.is_valid or not result.features:
            return False

        return feature in result.features

    def get_license_status(self, license_key: str) -> LicenseStatus:
        """
        Get the status of a license.

        Args:
            license_key: License key to check

        Returns:
            Status of the license
        """
        result = self.validate_license_key(license_key)
        if not result.status:
            return LicenseStatus.REVOKED

        return result.status

    def get_expiration_date(self, license_key: str) -> Optional[datetime]:
        """
        Get the expiration date of a license.

        Args:
            license_key: License key to check

        Returns:
            Expiration date of the license or None if perpetual
        """
        result = self.validate_license_key(license_key)
        if not result.is_valid:
            return None

        return result.expiration_date

    def invalidate_cache(self, license_key: Optional[str] = None) -> None:
        """
        Invalidate cache for a license key or all licenses.

        Args:
            license_key: License key to invalidate or None for all
        """
        if license_key:
            self.cache.invalidate(license_key)
        else:
            self.cache.clear()


class OfflineValidator:
    """Class for offline license validation."""

    def __init__(
        self,
        signature_handler: LicenseSignature,
        storage_path: str,
        max_offline_days: int = 30
    ):
        """
        Initialize offline validator.

        Args:
            signature_handler: Handler for license signature verification
            storage_path: Path to store offline validation data
            max_offline_days: Maximum days allowed for offline validation
        """
        self.validator = LicenseValidator(signature_handler)
        self.storage_path = storage_path
        self.max_offline_days = max_offline_days
        os.makedirs(storage_path, exist_ok=True)

    def _get_storage_file(self, license_id: str) -> str:
        """
        Get storage file path for a license.

        Args:
            license_id: License ID

        Returns:
            Path to storage file
        """
        filename = f"{license_id}.json"
        return os.path.join(self.storage_path, filename)

    def _store_validation_data(self, license_key: str, result: ValidationResult) -> None:
        """
        Store validation data for offline use.

        Args:
            license_key: License key
            result: Validation result to store
        """
        if not result.is_valid or not result.license_id:
            return

        data = {
            "license_key": license_key,
            "validation_result": result.to_dict(),
            "last_online_validation": datetime.now().isoformat(),
            "device_fingerprint": self._generate_device_fingerprint()
        }

        with open(self._get_storage_file(result.license_id), "w") as f:
            json.dump(data, f)

    def _load_validation_data(self, license_id: str) -> Optional[Dict]:
        """
        Load validation data for offline use.

        Args:
            license_id: License ID

        Returns:
            Loaded validation data or None if not found
        """
        file_path = self._get_storage_file(license_id)
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def _generate_device_fingerprint(self) -> str:
        """
        Generate a fingerprint for the current device.

        Returns:
            Device fingerprint string
        """
        # In a real implementation, this would collect various hardware identifiers
        # For now, we'll just use a placeholder
        return "device-fingerprint-placeholder"

    def _verify_device_fingerprint(self, stored_fingerprint: str) -> bool:
        """
        Verify that the current device matches the stored fingerprint.

        Args:
            stored_fingerprint: Stored device fingerprint

        Returns:
            True if device matches, False otherwise
        """
        current_fingerprint = self._generate_device_fingerprint()
        return current_fingerprint == stored_fingerprint

    def _is_offline_validation_valid(self, validation_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check if offline validation data is still valid.

        Args:
            validation_data: Offline validation data

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check device fingerprint
            if not self._verify_device_fingerprint(validation_data.get("device_fingerprint", "")):
                return False, "Device fingerprint mismatch"

            # Check last online validation date
            last_validation = datetime.fromisoformat(validation_data["last_online_validation"])
            current_date = datetime.now()
            days_since_validation = (current_date - last_validation).days

            if days_since_validation > self.max_offline_days:
                return False, f"Offline validation expired (max {self.max_offline_days} days)"

            return True, None
        except Exception as e:
            return False, f"Failed to verify offline validation: {str(e)}"

    def validate_license_key(self, license_key: str) -> ValidationResult:
        """
        Validate a license key with offline support.

        Args:
            license_key: License key to validate

        Returns:
            ValidationResult with validation status and details
        """
        # Try online validation first
        result = self.validator.validate_license_key(license_key)
        
        # If online validation succeeded, store the result for offline use
        if result.is_valid and result.license_id:
            self._store_validation_data(license_key, result)
            return result

        # If online validation failed due to connectivity issues, try offline validation
        try:
            # Parse license key to get metadata
            _, encoded_metadata, _, _ = self.validator._parse_license_key(license_key)
            metadata = LicenseMetadataEncoder.decode(encoded_metadata)
            license_id = metadata.license_id

            # Load offline validation data
            validation_data = self._load_validation_data(license_id)
            if not validation_data:
                # No offline data available
                return result

            # Check if offline validation is still valid
            is_valid, error_message = self._is_offline_validation_valid(validation_data)
            if not is_valid:
                return ValidationResult(
                    is_valid=False,
                    license_id=license_id,
                    error_message=error_message
                )

            # Reconstruct validation result from stored data
            stored_result = validation_data["validation_result"]
            
            # Check if the license has expired since last online validation
            if metadata.expiration_date:
                expiration_date = datetime.fromisoformat(stored_result["expiration_date"])
                if datetime.now() > expiration_date:
                    return ValidationResult(
                        is_valid=False,
                        license_id=license_id,
                        status=LicenseStatus.EXPIRED,
                        features=[LicenseFeature(f) for f in stored_result.get("features", [])],
                        expiration_date=expiration_date,
                        error_message="License has expired",
                        metadata=metadata
                    )

            # Return offline validation result
            return ValidationResult(
                is_valid=True,
                license_id=license_id,
                status=LicenseStatus(stored_result["status"]),
                features=[LicenseFeature(f) for f in stored_result.get("features", [])],
                expiration_date=datetime.fromisoformat(stored_result["expiration_date"]) if "expiration_date" in stored_result else None,
                metadata=metadata
            )
        except Exception as e:
            # If offline validation fails, return the original online validation result
            return ValidationResult(
                is_valid=False,
                error_message=f"License validation failed (offline): {str(e)}"
            )


class LicenseActivation:
    """Class for handling license activation and deactivation."""

    def __init__(self, validator: LicenseValidator, storage_path: str):
        """
        Initialize license activation handler.

        Args:
            validator: License validator
            storage_path: Path to store activation data
        """
        self.validator = validator
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def _get_activation_file(self, license_id: str) -> str:
        """
        Get activation file path for a license.

        Args:
            license_id: License ID

        Returns:
            Path to activation file
        """
        filename = f"{license_id}_activation.json"
        return os.path.join(self.storage_path, filename)

    def _generate_device_id(self) -> str:
        """
        Generate a unique identifier for the current device.

        Returns:
            Device ID string
        """
        # In a real implementation, this would generate a unique device ID
        # based on hardware characteristics
        import uuid
        return str(uuid.uuid4())

    def _get_device_fingerprint(self) -> Dict[str, str]:
        """
        Get a fingerprint of the current device.

        Returns:
            Dictionary with device fingerprint data
        """
        # In a real implementation, this would collect various hardware identifiers
        # For now, we'll just use placeholders
        return {
            "hostname": "hostname-placeholder",
            "mac_address": "mac-address-placeholder",
            "cpu_id": "cpu-id-placeholder",
            "disk_id": "disk-id-placeholder"
        }

    def activate_license(self, license_key: str) -> Tuple[bool, Optional[str]]:
        """
        Activate a license on the current device.

        Args:
            license_key: License key to activate

        Returns:
            Tuple of (success, error_message)
        """
        # Validate the license first
        result = self.validator.validate_license_key(license_key, skip_cache=True)
        if not result.is_valid:
            return False, result.error_message

        license_id = result.license_id
        if not license_id:
            return False, "Invalid license ID"

        try:
            # Check if license is already activated
            activation_file = self._get_activation_file(license_id)
            if os.path.exists(activation_file):
                with open(activation_file, "r") as f:
                    activation_data = json.load(f)
                    if activation_data.get("is_activated", False):
                        return True, "License is already activated"

            # Generate device information
            device_id = self._generate_device_id()
            device_fingerprint = self._get_device_fingerprint()

            # Create activation data
            activation_data = {
                "license_id": license_id,
                "license_key": license_key,
                "device_id": device_id,
                "device_fingerprint": device_fingerprint,
                "activation_date": datetime.now().isoformat(),
                "is_activated": True
            }

            # Save activation data
            with open(activation_file, "w") as f:
                json.dump(activation_data, f)

            return True, None
        except Exception as e:
            return False, f"License activation failed: {str(e)}"

    def deactivate_license(self, license_key: str) -> Tuple[bool, Optional[str]]:
        """
        Deactivate a license on the current device.

        Args:
            license_key: License key to deactivate

        Returns:
            Tuple of (success, error_message)
        """
        # Validate the license first
        result = self.validator.validate_license_key(license_key, skip_cache=True)
        license_id = result.license_id
        if not license_id:
            return False, "Invalid license ID"

        try:
            # Check if license is activated
            activation_file = self._get_activation_file(license_id)
            if not os.path.exists(activation_file):
                return False, "License is not activated on this device"

            # Read activation data
            with open(activation_file, "r") as f:
                activation_data = json.load(f)

            # Update activation status
            activation_data["is_activated"] = False
            activation_data["deactivation_date"] = datetime.now().isoformat()

            # Save updated activation data
            with open(activation_file, "w") as f:
                json.dump(activation_data, f)

            return True, None
        except Exception as e:
            return False, f"License deactivation failed: {str(e)}"

    def is_license_activated(self, license_key: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a license is activated on the current device.

        Args:
            license_key: License key to check

        Returns:
            Tuple of (is_activated, error_message)
        """
        # Validate the license first
        result = self.validator.validate_license_key(license_key)
        license_id = result.license_id
        if not license_id:
            return False, "Invalid license ID"

        try:
            # Check if activation file exists
            activation_file = self._get_activation_file(license_id)
            if not os.path.exists(activation_file):
                return False, "License is not activated on this device"

            # Read activation data
            with open(activation_file, "r") as f:
                activation_data = json.load(f)

            # Check activation status
            is_activated = activation_data.get("is_activated", False)
            if not is_activated:
                return False, "License is deactivated on this device"

            # Verify device fingerprint
            stored_fingerprint = activation_data.get("device_fingerprint", {})
            current_fingerprint = self._get_device_fingerprint()

            # In a real implementation, this would compare the fingerprints
            # with some tolerance for changes
            # For now, we'll just assume they match
            
            return True, None
        except Exception as e:
            return False, f"Failed to check license activation: {str(e)}"


if __name__ == "__main__":
    # Example usage
    # Load public key for validation
    signature_handler = LicenseSignature(public_key_path="public_key.pem")

    # Create license validator
    validator = LicenseValidator(signature_handler)

    # Validate a license key
    license_key = "APX-PRP-1.eyJsaWNlbnNlX2lkIjoiMTIzNDU2Nzg5MCIsImN1c3RvbWVyX2lkIjoiY3VzdG9tZXIxMjMiLCJsaWNlbnNlX3R5cGUiOiJwZXJwZXR1YWwiLCJmZWF0dXJlcyI6WyJjb3JlIiwiYWR2YW5jZWRfcGx1Z2lucyIsInByaW9yaXR5X3N1cHBvcnQiXSwiaXNzdWVfZGF0ZSI6IjIwMjUtMDUtMjBUMDE6MDU6MDAiLCJhY3RpdmF0aW9uX2xpbWl0IjoyLCJjdXN0b21fYXR0cmlidXRlcyI6e319.signature.checksum"
    result = validator.validate_license_key(license_key)
    print(f"License valid: {result.is_valid}")
    if result.is_valid:
        print(f"License ID: {result.license_id}")
        print(f"Status: {result.status}")
        print(f"Features: {[f.value for f in result.features]}")
        print(f"Expiration: {result.expiration_date}")

    # Check if license has specific feature
    has_feature = validator.has_feature(license_key, LicenseFeature.ADVANCED_PLUGINS)
    print(f"Has advanced plugins feature: {has_feature}")

    # Create offline validator
    offline_validator = OfflineValidator(signature_handler, "offline_licenses")
    offline_result = offline_validator.validate_license_key(license_key)
    print(f"Offline validation valid: {offline_result.is_valid}")

    # Create license activation handler
    activation_handler = LicenseActivation(validator, "license_activations")
    success, message = activation_handler.activate_license(license_key)
    print(f"Activation success: {success}")
    if message:
        print(f"Activation message: {message}")

    # Check if license is activated
    is_activated, message = activation_handler.is_license_activated(license_key)
    print(f"Is activated: {is_activated}")
    if message:
        print(f"Activation status message: {message}")
