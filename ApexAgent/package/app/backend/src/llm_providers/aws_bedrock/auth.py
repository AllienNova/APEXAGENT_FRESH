"""
AWS Bedrock authentication module for the LLM Providers integration.

This module handles authentication with AWS Bedrock, supporting various
authentication methods including IAM roles, access keys, and temporary credentials.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from ..core.provider_interface import LLMError, LLMErrorType

logger = logging.getLogger(__name__)


class AWSAuthType(str, Enum):
    """Enumeration of supported AWS authentication types."""
    IAM_ROLE = "iam_role"
    ACCESS_KEY = "access_key"
    TEMPORARY_CREDENTIALS = "temporary_credentials"
    PROFILE = "profile"
    ENVIRONMENT = "environment"


@dataclass
class AWSCredentials:
    """AWS credentials configuration."""
    auth_type: AWSAuthType
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    profile_name: Optional[str] = None
    role_arn: Optional[str] = None
    region: str = "us-east-1"
    endpoint_url: Optional[str] = None


class AWSAuthManager:
    """
    Manages authentication with AWS services, including Bedrock.
    
    This class handles different authentication methods and provides
    authenticated clients for AWS services.
    """
    
    def __init__(self, credentials: AWSCredentials):
        """
        Initialize the AWS authentication manager.
        
        Args:
            credentials: AWS credentials configuration
        """
        self.credentials = credentials
        self.session = None
        self.bedrock_client = None
        self.bedrock_runtime_client = None
        
        # Initialize session and clients
        self._initialize_session()
    
    def _initialize_session(self) -> None:
        """Initialize the AWS session based on the provided credentials."""
        try:
            if self.credentials.auth_type == AWSAuthType.ACCESS_KEY:
                if not self.credentials.access_key_id or not self.credentials.secret_access_key:
                    raise LLMError(
                        "Missing AWS access key ID or secret access key",
                        LLMErrorType.AUTHENTICATION_ERROR,
                        "aws_bedrock",
                        retryable=False
                    )
                
                self.session = boto3.Session(
                    aws_access_key_id=self.credentials.access_key_id,
                    aws_secret_access_key=self.credentials.secret_access_key,
                    aws_session_token=self.credentials.session_token,
                    region_name=self.credentials.region
                )
            
            elif self.credentials.auth_type == AWSAuthType.PROFILE:
                if not self.credentials.profile_name:
                    raise LLMError(
                        "Missing AWS profile name",
                        LLMErrorType.AUTHENTICATION_ERROR,
                        "aws_bedrock",
                        retryable=False
                    )
                
                self.session = boto3.Session(
                    profile_name=self.credentials.profile_name,
                    region_name=self.credentials.region
                )
            
            elif self.credentials.auth_type == AWSAuthType.ENVIRONMENT:
                # Use environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc.)
                self.session = boto3.Session(region_name=self.credentials.region)
            
            elif self.credentials.auth_type == AWSAuthType.IAM_ROLE:
                # Default to instance role or container role
                self.session = boto3.Session(region_name=self.credentials.region)
                
                # If role_arn is provided, assume that role
                if self.credentials.role_arn:
                    sts_client = self.session.client('sts')
                    assumed_role = sts_client.assume_role(
                        RoleArn=self.credentials.role_arn,
                        RoleSessionName="ApexAgentBedrockSession"
                    )
                    
                    credentials = assumed_role['Credentials']
                    self.session = boto3.Session(
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken'],
                        region_name=self.credentials.region
                    )
            
            elif self.credentials.auth_type == AWSAuthType.TEMPORARY_CREDENTIALS:
                if not all([
                    self.credentials.access_key_id,
                    self.credentials.secret_access_key,
                    self.credentials.session_token
                ]):
                    raise LLMError(
                        "Missing temporary credentials (access key, secret key, or session token)",
                        LLMErrorType.AUTHENTICATION_ERROR,
                        "aws_bedrock",
                        retryable=False
                    )
                
                self.session = boto3.Session(
                    aws_access_key_id=self.credentials.access_key_id,
                    aws_secret_access_key=self.credentials.secret_access_key,
                    aws_session_token=self.credentials.session_token,
                    region_name=self.credentials.region
                )
            
            else:
                raise LLMError(
                    f"Unsupported AWS authentication type: {self.credentials.auth_type}",
                    LLMErrorType.AUTHENTICATION_ERROR,
                    "aws_bedrock",
                    retryable=False
                )
            
            # Validate the session by checking if we can get the caller identity
            try:
                sts_client = self.session.client('sts')
                sts_client.get_caller_identity()
            except (ClientError, NoCredentialsError) as e:
                raise LLMError(
                    f"Failed to validate AWS credentials: {str(e)}",
                    LLMErrorType.AUTHENTICATION_ERROR,
                    "aws_bedrock",
                    retryable=False,
                    original_error=e
                )
            
            logger.info(f"Successfully initialized AWS session for region {self.credentials.region}")
        
        except (ClientError, NoCredentialsError) as e:
            error_message = f"AWS authentication failed: {str(e)}"
            logger.error(error_message)
            raise LLMError(
                error_message,
                LLMErrorType.AUTHENTICATION_ERROR,
                "aws_bedrock",
                retryable=False,
                original_error=e
            )
    
    def get_bedrock_client(self) -> Any:
        """
        Get an authenticated AWS Bedrock client.
        
        Returns:
            An authenticated boto3 client for AWS Bedrock
        """
        if not self.bedrock_client:
            config = Config(
                retries={
                    'max_attempts': 3,
                    'mode': 'standard'
                }
            )
            
            # Create the Bedrock client
            self.bedrock_client = self.session.client(
                service_name='bedrock',
                region_name=self.credentials.region,
                endpoint_url=self.credentials.endpoint_url,
                config=config
            )
        
        return self.bedrock_client
    
    def get_bedrock_runtime_client(self) -> Any:
        """
        Get an authenticated AWS Bedrock Runtime client.
        
        Returns:
            An authenticated boto3 client for AWS Bedrock Runtime
        """
        if not self.bedrock_runtime_client:
            config = Config(
                retries={
                    'max_attempts': 3,
                    'mode': 'standard'
                }
            )
            
            # Create the Bedrock Runtime client
            self.bedrock_runtime_client = self.session.client(
                service_name='bedrock-runtime',
                region_name=self.credentials.region,
                endpoint_url=self.credentials.endpoint_url,
                config=config
            )
        
        return self.bedrock_runtime_client
    
    def validate_authentication(self) -> bool:
        """
        Validate that the authentication is working correctly.
        
        Returns:
            True if authentication is valid, False otherwise
        """
        try:
            # Try to list Bedrock models to validate authentication
            client = self.get_bedrock_client()
            client.list_foundation_models()
            return True
        except ClientError as e:
            logger.error(f"Failed to validate AWS Bedrock authentication: {str(e)}")
            return False
    
    @staticmethod
    def from_environment() -> 'AWSAuthManager':
        """
        Create an AWSAuthManager instance from environment variables.
        
        Returns:
            An initialized AWSAuthManager
        """
        # Check if AWS_PROFILE is set
        if os.environ.get('AWS_PROFILE'):
            credentials = AWSCredentials(
                auth_type=AWSAuthType.PROFILE,
                profile_name=os.environ.get('AWS_PROFILE'),
                region=os.environ.get('AWS_REGION', 'us-east-1')
            )
        # Check if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set
        elif os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            credentials = AWSCredentials(
                auth_type=AWSAuthType.ACCESS_KEY,
                access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                session_token=os.environ.get('AWS_SESSION_TOKEN'),
                region=os.environ.get('AWS_REGION', 'us-east-1')
            )
        # Default to environment auth type (will use instance role if available)
        else:
            credentials = AWSCredentials(
                auth_type=AWSAuthType.ENVIRONMENT,
                region=os.environ.get('AWS_REGION', 'us-east-1')
            )
        
        return AWSAuthManager(credentials)
