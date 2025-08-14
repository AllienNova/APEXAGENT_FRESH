"""
License Generator module for ApexAgent Subscription and Licensing System.

This module provides functionality for generating cryptographically secure license keys
with embedded metadata, supporting different license types and formats.
"""

import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class LicenseType(Enum):
    """Enumeration of supported license types."""
    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    TRIAL = "trial"
    DEVELOPMENT = "development"
    ENTERPRISE = "enterprise"


class LicenseFeature(Enum):
    """Enumeration of features that can be enabled in a license."""
    CORE = "core"
    ADVANCED_PLUGINS = "advanced_plugins"
    ENTERPRISE_INTEGRATION = "enterprise_integration"
    MULTI_USER = "multi_user"
    OFFLINE_MODE = "offline_mode"
    PRIORITY_SUPPORT = "priority_support"
    WHITE_LABEL = "white_label"
    CUSTOM_BRANDING = "custom_branding"
    API_ACCESS = "api_access"
    ADVANCED_ANALYTICS = "advanced_analytics"


class LicenseStatus(Enum):
    """Enumeration of possible license statuses."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    PENDING_ACTIVATION = "pending_activation"


class LicenseMetadata:
    """Class representing license metadata."""

    def __init__(
        self,
        license_id: str,
        customer_id: str,
        license_type: LicenseType,
        features: List[LicenseFeature],
        issue_date: datetime,
        expiration_date: Optional[datetime] = None,
        organization_id: Optional[str] = None,
        activation_limit: int = 1,
        custom_attributes: Optional[Dict[str, str]] = None
    ):
        """
        Initialize license metadata.

        Args:
            license_id: Unique identifier for the license
            customer_id: Identifier for the customer
            license_type: Type of license
            features: List of enabled features
            issue_date: Date when the license was issued
            expiration_date: Date when the license expires (None for perpetual)
            organization_id: Identifier for the organization (for enterprise licenses)
            activation_limit: Maximum number of activations allowed
            custom_attributes: Additional custom attributes for the license
        """
        self.license_id = license_id
        self.customer_id = customer_id
        self.license_type = license_type
        self.features = features
        self.issue_date = issue_date
        self.expiration_date = expiration_date
        self.organization_id = organization_id
        self.activation_limit = activation_limit
        self.custom_attributes = custom_attributes or {}

    def to_dict(self) -> Dict[str, Union[str, int, List[str], Dict[str, str]]]:
        """
        Convert metadata to dictionary for serialization.

        Returns:
            Dictionary representation of the metadata
        """
        result = {
            "license_id": self.license_id,
            "customer_id": self.customer_id,
            "license_type": self.license_type.value,
            "features": [feature.value for feature in self.features],
            "issue_date": self.issue_date.isoformat(),
            "activation_limit": self.activation_limit,
            "custom_attributes": self.custom_attributes
        }

        if self.expiration_date:
            result["expiration_date"] = self.expiration_date.isoformat()

        if self.organization_id:
            result["organization_id"] = self.organization_id

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, int, List[str], Dict[str, str]]]) -> 'LicenseMetadata':
        """
        Create metadata from dictionary.

        Args:
            data: Dictionary representation of metadata

        Returns:
            LicenseMetadata instance
        """
        features = [LicenseFeature(feature) for feature in data.get("features", [])]
        license_type = LicenseType(data["license_type"])
        issue_date = datetime.fromisoformat(data["issue_date"])
        expiration_date = None
        if "expiration_date" in data and data["expiration_date"]:
            expiration_date = datetime.fromisoformat(data["expiration_date"])

        return cls(
            license_id=data["license_id"],
            customer_id=data["customer_id"],
            license_type=license_type,
            features=features,
            issue_date=issue_date,
            expiration_date=expiration_date,
            organization_id=data.get("organization_id"),
            activation_limit=data.get("activation_limit", 1),
            custom_attributes=data.get("custom_attributes", {})
        )


class LicenseKeyFactory:
    """Factory class for creating different types of license keys."""

    @staticmethod
    def create_license_id() -> str:
        """
        Create a unique license ID.

        Returns:
            Unique license ID as UUID string
        """
        return str(uuid.uuid4())

    @staticmethod
    def create_perpetual_license(
        customer_id: str,
        features: List[LicenseFeature],
        organization_id: Optional[str] = None,
        activation_limit: int = 1,
        custom_attributes: Optional[Dict[str, str]] = None
    ) -> LicenseMetadata:
        """
        Create metadata for a perpetual license.

        Args:
            customer_id: Identifier for the customer
            features: List of enabled features
            organization_id: Identifier for the organization
            activation_limit: Maximum number of activations allowed
            custom_attributes: Additional custom attributes

        Returns:
            LicenseMetadata for a perpetual license
        """
        return LicenseMetadata(
            license_id=LicenseKeyFactory.create_license_id(),
            customer_id=customer_id,
            license_type=LicenseType.PERPETUAL,
            features=features,
            issue_date=datetime.now(),
            expiration_date=None,
            organization_id=organization_id,
            activation_limit=activation_limit,
            custom_attributes=custom_attributes
        )

    @staticmethod
    def create_subscription_license(
        customer_id: str,
        features: List[LicenseFeature],
        duration_days: int,
        organization_id: Optional[str] = None,
        activation_limit: int = 1,
        custom_attributes: Optional[Dict[str, str]] = None
    ) -> LicenseMetadata:
        """
        Create metadata for a subscription license.

        Args:
            customer_id: Identifier for the customer
            features: List of enabled features
            duration_days: Duration of the subscription in days
            organization_id: Identifier for the organization
            activation_limit: Maximum number of activations allowed
            custom_attributes: Additional custom attributes

        Returns:
            LicenseMetadata for a subscription license
        """
        issue_date = datetime.now()
        expiration_date = issue_date + timedelta(days=duration_days)

        return LicenseMetadata(
            license_id=LicenseKeyFactory.create_license_id(),
            customer_id=customer_id,
            license_type=LicenseType.SUBSCRIPTION,
            features=features,
            issue_date=issue_date,
            expiration_date=expiration_date,
            organization_id=organization_id,
            activation_limit=activation_limit,
            custom_attributes=custom_attributes
        )

    @staticmethod
    def create_trial_license(
        customer_id: str,
        features: List[LicenseFeature],
        trial_days: int = 30,
        custom_attributes: Optional[Dict[str, str]] = None
    ) -> LicenseMetadata:
        """
        Create metadata for a trial license.

        Args:
            customer_id: Identifier for the customer
            features: List of enabled features
            trial_days: Duration of the trial in days
            custom_attributes: Additional custom attributes

        Returns:
            LicenseMetadata for a trial license
        """
        issue_date = datetime.now()
        expiration_date = issue_date + timedelta(days=trial_days)

        return LicenseMetadata(
            license_id=LicenseKeyFactory.create_license_id(),
            customer_id=customer_id,
            license_type=LicenseType.TRIAL,
            features=features,
            issue_date=issue_date,
            expiration_date=expiration_date,
            organization_id=None,
            activation_limit=1,
            custom_attributes=custom_attributes
        )


class LicenseSignature:
    """Class for handling cryptographic signing of licenses."""

    def __init__(self, private_key_path: Optional[str] = None, public_key_path: Optional[str] = None):
        """
        Initialize license signature handler.

        Args:
            private_key_path: Path to the private key file (for signing)
            public_key_path: Path to the public key file (for verification)
        """
        self.private_key = None
        self.public_key = None

        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )

        if public_key_path and os.path.exists(public_key_path):
            with open(public_key_path, "rb") as key_file:
                self.public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )

    def generate_key_pair(self, private_key_path: str, public_key_path: str) -> None:
        """
        Generate a new RSA key pair for license signing.

        Args:
            private_key_path: Path to save the private key
            public_key_path: Path to save the public key
        """
        # Generate a new RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        self.private_key = private_key
        self.public_key = private_key.public_key()

        # Save the private key
        with open(private_key_path, "wb") as key_file:
            key_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Save the public key
        with open(public_key_path, "wb") as key_file:
            key_file.write(
                self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

    def sign(self, data: str) -> str:
        """
        Sign data with the private key.

        Args:
            data: Data to sign

        Returns:
            Base64-encoded signature

        Raises:
            ValueError: If private key is not available
        """
        if not self.private_key:
            raise ValueError("Private key not available for signing")

        signature = self.private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode('utf-8')

    def verify(self, data: str, signature: str) -> bool:
        """
        Verify signature with the public key.

        Args:
            data: Original data
            signature: Base64-encoded signature

        Returns:
            True if signature is valid, False otherwise

        Raises:
            ValueError: If public key is not available
        """
        if not self.public_key:
            raise ValueError("Public key not available for verification")

        try:
            signature_bytes = base64.b64decode(signature)
            self.public_key.verify(
                signature_bytes,
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


class LicenseMetadataEncoder:
    """Class for encoding and decoding license metadata."""

    @staticmethod
    def encode(metadata: LicenseMetadata) -> str:
        """
        Encode license metadata to string.

        Args:
            metadata: License metadata to encode

        Returns:
            Base64-encoded metadata string
        """
        metadata_dict = metadata.to_dict()
        metadata_json = json.dumps(metadata_dict, sort_keys=True)
        return base64.b64encode(metadata_json.encode('utf-8')).decode('utf-8')

    @staticmethod
    def decode(encoded_metadata: str) -> LicenseMetadata:
        """
        Decode license metadata from string.

        Args:
            encoded_metadata: Base64-encoded metadata string

        Returns:
            Decoded LicenseMetadata object

        Raises:
            ValueError: If metadata cannot be decoded
        """
        try:
            metadata_json = base64.b64decode(encoded_metadata).decode('utf-8')
            metadata_dict = json.loads(metadata_json)
            return LicenseMetadata.from_dict(metadata_dict)
        except Exception as e:
            raise ValueError(f"Failed to decode license metadata: {str(e)}")


class LicenseGenerator:
    """Main class for license generation."""

    def __init__(self, signature_handler: LicenseSignature):
        """
        Initialize license generator.

        Args:
            signature_handler: Handler for license signing
        """
        self.signature_handler = signature_handler
        self.prefix_map = {
            LicenseType.PERPETUAL: "APX-PRP",
            LicenseType.SUBSCRIPTION: "APX-SUB",
            LicenseType.TRIAL: "APX-TRL",
            LicenseType.DEVELOPMENT: "APX-DEV",
            LicenseType.ENTERPRISE: "APX-ENT"
        }

    def _generate_prefix(self, license_type: LicenseType, version: int = 1) -> str:
        """
        Generate license key prefix.

        Args:
            license_type: Type of license
            version: License format version

        Returns:
            License key prefix
        """
        base_prefix = self.prefix_map.get(license_type, "APX-STD")
        return f"{base_prefix}-{version}"

    def _generate_checksum(self, data: str) -> str:
        """
        Generate checksum for license data.

        Args:
            data: License data

        Returns:
            Checksum string
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()[:8]

    def generate_license_key(self, metadata: LicenseMetadata) -> str:
        """
        Generate a complete license key.

        Args:
            metadata: License metadata

        Returns:
            Complete license key string

        Raises:
            ValueError: If license cannot be generated
        """
        try:
            # Generate prefix
            prefix = self._generate_prefix(metadata.license_type)

            # Encode metadata
            encoded_metadata = LicenseMetadataEncoder.encode(metadata)

            # Create data for signing (prefix + encoded metadata)
            data_to_sign = f"{prefix}.{encoded_metadata}"

            # Sign the data
            signature = self.signature_handler.sign(data_to_sign)

            # Generate checksum
            checksum = self._generate_checksum(f"{data_to_sign}.{signature}")

            # Combine all parts to form the license key
            license_key = f"{prefix}.{encoded_metadata}.{signature}.{checksum}"

            return license_key
        except Exception as e:
            raise ValueError(f"Failed to generate license key: {str(e)}")

    def generate_license(
        self,
        customer_id: str,
        license_type: LicenseType,
        features: List[LicenseFeature],
        duration_days: Optional[int] = None,
        organization_id: Optional[str] = None,
        activation_limit: int = 1,
        custom_attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a license key with the specified parameters.

        Args:
            customer_id: Identifier for the customer
            license_type: Type of license
            features: List of enabled features
            duration_days: Duration in days (for subscription/trial)
            organization_id: Identifier for the organization
            activation_limit: Maximum number of activations allowed
            custom_attributes: Additional custom attributes

        Returns:
            Generated license key

        Raises:
            ValueError: If license parameters are invalid
        """
        if license_type == LicenseType.PERPETUAL:
            metadata = LicenseKeyFactory.create_perpetual_license(
                customer_id=customer_id,
                features=features,
                organization_id=organization_id,
                activation_limit=activation_limit,
                custom_attributes=custom_attributes
            )
        elif license_type == LicenseType.SUBSCRIPTION:
            if not duration_days:
                raise ValueError("Duration days must be specified for subscription licenses")
            metadata = LicenseKeyFactory.create_subscription_license(
                customer_id=customer_id,
                features=features,
                duration_days=duration_days,
                organization_id=organization_id,
                activation_limit=activation_limit,
                custom_attributes=custom_attributes
            )
        elif license_type == LicenseType.TRIAL:
            trial_days = duration_days or 30
            metadata = LicenseKeyFactory.create_trial_license(
                customer_id=customer_id,
                features=features,
                trial_days=trial_days,
                custom_attributes=custom_attributes
            )
        else:
            raise ValueError(f"Unsupported license type: {license_type}")

        return self.generate_license_key(metadata)

    def generate_batch_licenses(
        self,
        count: int,
        customer_id: str,
        license_type: LicenseType,
        features: List[LicenseFeature],
        duration_days: Optional[int] = None,
        organization_id: Optional[str] = None,
        activation_limit: int = 1,
        custom_attributes: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Generate multiple license keys with the same parameters.

        Args:
            count: Number of licenses to generate
            customer_id: Identifier for the customer
            license_type: Type of license
            features: List of enabled features
            duration_days: Duration in days (for subscription/trial)
            organization_id: Identifier for the organization
            activation_limit: Maximum number of activations allowed
            custom_attributes: Additional custom attributes

        Returns:
            List of generated license keys

        Raises:
            ValueError: If license parameters are invalid
        """
        licenses = []
        for _ in range(count):
            license_key = self.generate_license(
                customer_id=customer_id,
                license_type=license_type,
                features=features,
                duration_days=duration_days,
                organization_id=organization_id,
                activation_limit=activation_limit,
                custom_attributes=custom_attributes
            )
            licenses.append(license_key)
        return licenses


if __name__ == "__main__":
    # Example usage
    # Generate key pair
    signature_handler = LicenseSignature()
    signature_handler.generate_key_pair("private_key.pem", "public_key.pem")

    # Create license generator
    generator = LicenseGenerator(signature_handler)

    # Generate a perpetual license
    perpetual_license = generator.generate_license(
        customer_id="customer123",
        license_type=LicenseType.PERPETUAL,
        features=[
            LicenseFeature.CORE,
            LicenseFeature.ADVANCED_PLUGINS,
            LicenseFeature.PRIORITY_SUPPORT
        ],
        activation_limit=2
    )
    print(f"Perpetual License: {perpetual_license}")

    # Generate a subscription license
    subscription_license = generator.generate_license(
        customer_id="customer456",
        license_type=LicenseType.SUBSCRIPTION,
        features=[
            LicenseFeature.CORE,
            LicenseFeature.ADVANCED_PLUGINS
        ],
        duration_days=365,
        organization_id="org789"
    )
    print(f"Subscription License: {subscription_license}")

    # Generate a trial license
    trial_license = generator.generate_license(
        customer_id="customer789",
        license_type=LicenseType.TRIAL,
        features=[
            LicenseFeature.CORE,
            LicenseFeature.ADVANCED_PLUGINS,
            LicenseFeature.ENTERPRISE_INTEGRATION,
            LicenseFeature.MULTI_USER
        ],
        duration_days=30
    )
    print(f"Trial License: {trial_license}")
