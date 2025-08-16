"""
Integration module for connecting the Data Protection Framework with the Authentication and Authorization System.

This module provides the necessary interfaces and adapters to securely integrate
the data protection capabilities with the authentication, authorization, and
subscription systems of the ApexAgent platform.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Union

# Import from data protection modules
from ..core.encryption import encryption_service
from ..core.key_management import key_manager
from ..core.anonymization import data_anonymization
from ..core.storage import secure_storage
from ..core.backup import backup_recovery
from ..core.compliance import compliance_tools

# Import from auth system
from auth.authentication import auth_manager
from auth.authentication import mfa_manager
from auth.authorization import auth_rbac, enhanced_rbac
from auth.identity import identity_manager, enterprise_identity_manager
from auth.plugin_security import plugin_security_manager

# Import from subscription system
from subscription.core import license_validator, subscription_manager, usage_tracking

logger = logging.getLogger(__name__)


class AuthIntegrationManager:
    """
    Manages the integration between the Data Protection Framework and the
    Authentication and Authorization System.
    
    This class provides secure interfaces for:
    - Obtaining encryption keys based on user authentication
    - Enforcing data access based on authorization policies
    - Managing data visibility based on user roles and permissions
    - Integrating with MFA for sensitive data operations
    """
    
    def __init__(self, 
                 encryption_service_instance: encryption_service.EncryptionService,
                 key_manager_instance: key_manager.KeyManager,
                 auth_manager_instance: auth_manager.AuthManager,
                 rbac_manager_instance: enhanced_rbac.EnhancedRBACManager):
        """
        Initialize the integration manager with required service instances.
        
        Args:
            encryption_service_instance: Instance of the encryption service
            key_manager_instance: Instance of the key management service
            auth_manager_instance: Instance of the authentication manager
            rbac_manager_instance: Instance of the RBAC manager
        """
        self.encryption_service = encryption_service_instance
        self.key_manager = key_manager_instance
        self.auth_manager = auth_manager_instance
        self.rbac_manager = rbac_manager_instance
        logger.info("AuthIntegrationManager initialized")
    
    def get_user_encryption_key(self, user_id: str, session_token: str, 
                               purpose: str, require_mfa: bool = False) -> Optional[bytes]:
        """
        Securely obtain a user's encryption key after verifying authentication and authorization.
        
        Args:
            user_id: The ID of the user requesting the key
            session_token: The current session token for authentication
            purpose: The purpose for which the key will be used
            require_mfa: Whether MFA verification is required for this operation
            
        Returns:
            The encryption key if authorized, None otherwise
        """
        # Verify session is valid
        if not self.auth_manager.verify_session(session_token):
            logger.warning(f"Invalid session for user {user_id} when requesting encryption key")
            return None
            
        # Verify user identity matches session
        session_user = self.auth_manager.get_session_user(session_token)
        if session_user != user_id:
            logger.warning(f"User ID mismatch: {user_id} vs {session_user} in session")
            return None
            
        # Check if MFA is required and verified
        if require_mfa and not self.auth_manager.is_mfa_verified(session_token):
            logger.warning(f"MFA required but not verified for user {user_id}")
            return None
            
        # Check authorization for the specific purpose
        if not self.rbac_manager.check_permission(user_id, f"data_protection.key.{purpose}"):
            logger.warning(f"User {user_id} not authorized for key purpose: {purpose}")
            return None
            
        # All checks passed, retrieve the key
        return self.key_manager.get_user_key(user_id, purpose)
    
    def enforce_data_access_policy(self, user_id: str, session_token: str, 
                                  data_id: str, operation: str) -> bool:
        """
        Enforce data access policies based on authentication and authorization.
        
        Args:
            user_id: The ID of the user requesting access
            session_token: The current session token for authentication
            data_id: The identifier of the data being accessed
            operation: The operation being performed (read, write, delete)
            
        Returns:
            True if access is allowed, False otherwise
        """
        # Verify authentication
        if not self.auth_manager.verify_session(session_token):
            return False
            
        # Verify user identity
        session_user = self.auth_manager.get_session_user(session_token)
        if session_user != user_id:
            return False
            
        # Get data classification and sensitivity
        data_metadata = self.encryption_service.get_data_metadata(data_id)
        if not data_metadata:
            return False
            
        classification = data_metadata.get('classification', 'unknown')
        sensitivity = data_metadata.get('sensitivity', 'high')
        
        # Check if operation requires MFA based on classification and sensitivity
        requires_mfa = (
            (classification == 'confidential' and operation in ['write', 'delete']) or
            (sensitivity == 'high' and operation in ['write', 'delete']) or
            (classification == 'restricted' and operation in ['read', 'write', 'delete'])
        )
        
        if requires_mfa and not self.auth_manager.is_mfa_verified(session_token):
            logger.warning(f"MFA required but not verified for {user_id} accessing {data_id}")
            return False
            
        # Check RBAC permissions
        permission = f"data.{classification}.{operation}"
        if not self.rbac_manager.check_permission(user_id, permission):
            logger.warning(f"User {user_id} lacks permission {permission} for {data_id}")
            return False
            
        # Check data ownership if applicable
        if data_metadata.get('owner_id') and operation in ['write', 'delete']:
            if data_metadata['owner_id'] != user_id:
                # Check if user has delegation for this data
                if not self.rbac_manager.check_delegation(
                    user_id, data_metadata['owner_id'], f"data.{classification}.{operation}"
                ):
                    logger.warning(f"User {user_id} is not owner of {data_id} and has no delegation")
                    return False
        
        # All checks passed
        return True


class SubscriptionIntegrationManager:
    """
    Manages the integration between the Data Protection Framework and the
    Subscription and Licensing System.
    
    This class provides interfaces for:
    - Enforcing data protection features based on subscription tier
    - Tracking usage of data protection features
    - Managing quota for secure storage and backup
    """
    
    def __init__(self,
                 subscription_manager_instance: subscription_manager.SubscriptionManager,
                 usage_tracking_instance: usage_tracking.UsageTracker,
                 secure_storage_instance: secure_storage.SecureStorageManager,
                 backup_manager_instance: backup_recovery.BackupManager):
        """
        Initialize the integration manager with required service instances.
        
        Args:
            subscription_manager_instance: Instance of the subscription manager
            usage_tracking_instance: Instance of the usage tracker
            secure_storage_instance: Instance of the secure storage manager
            backup_manager_instance: Instance of the backup manager
        """
        self.subscription_manager = subscription_manager_instance
        self.usage_tracker = usage_tracking_instance
        self.secure_storage = secure_storage_instance
        self.backup_manager = backup_manager_instance
        logger.info("SubscriptionIntegrationManager initialized")
    
    def check_feature_access(self, user_id: str, feature: str) -> bool:
        """
        Check if a user has access to a specific data protection feature
        based on their subscription tier.
        
        Args:
            user_id: The ID of the user
            feature: The data protection feature to check
            
        Returns:
            True if the user has access to the feature, False otherwise
        """
        # Get user's subscription tier
        subscription = self.subscription_manager.get_user_subscription(user_id)
        if not subscription:
            logger.warning(f"No subscription found for user {user_id}")
            return False
            
        # Check if the feature is available in the user's tier
        feature_path = f"data_protection.{feature}"
        has_access = self.subscription_manager.check_feature_access(
            subscription.tier_id, feature_path
        )
        
        if not has_access:
            logger.info(f"User {user_id} with tier {subscription.tier_id} does not have access to {feature}")
            return False
            
        return True
    
    def track_feature_usage(self, user_id: str, feature: str, 
                           quantity: float = 1.0, metadata: Dict[str, Any] = None) -> bool:
        """
        Track usage of a data protection feature for a user.
        
        Args:
            user_id: The ID of the user
            feature: The data protection feature being used
            quantity: The amount of usage to track
            metadata: Additional metadata about the usage
            
        Returns:
            True if tracking was successful, False otherwise
        """
        # Check if user has access to the feature
        if not self.check_feature_access(user_id, feature):
            return False
            
        # Track the usage
        feature_path = f"data_protection.{feature}"
        tracking_metadata = metadata or {}
        tracking_metadata['component'] = 'data_protection'
        
        return self.usage_tracker.track_usage(
            user_id, feature_path, quantity, tracking_metadata
        )
    
    def check_storage_quota(self, user_id: str, storage_type: str, 
                           size_bytes: int) -> bool:
        """
        Check if a user has sufficient quota for secure storage operations.
        
        Args:
            user_id: The ID of the user
            storage_type: The type of storage (object, file, database)
            size_bytes: The size of the data in bytes
            
        Returns:
            True if the user has sufficient quota, False otherwise
        """
        # Get user's subscription tier
        subscription = self.subscription_manager.get_user_subscription(user_id)
        if not subscription:
            return False
            
        # Get current usage
        current_usage = self.usage_tracker.get_current_usage(
            user_id, f"storage.{storage_type}"
        )
        
        # Get quota limit
        quota_limit = self.subscription_manager.get_quota_limit(
            subscription.tier_id, f"storage.{storage_type}"
        )
        
        # Check if operation would exceed quota
        if current_usage + size_bytes > quota_limit:
            logger.warning(
                f"Storage quota exceeded for user {user_id}: "
                f"current={current_usage}, requested={size_bytes}, limit={quota_limit}"
            )
            return False
            
        return True
    
    def check_backup_quota(self, user_id: str, backup_type: str, 
                          retention_days: int, size_bytes: int) -> bool:
        """
        Check if a user has sufficient quota for backup operations.
        
        Args:
            user_id: The ID of the user
            backup_type: The type of backup (full, incremental, differential)
            retention_days: The number of days to retain the backup
            size_bytes: The size of the backup in bytes
            
        Returns:
            True if the user has sufficient quota, False otherwise
        """
        # Get user's subscription tier
        subscription = self.subscription_manager.get_user_subscription(user_id)
        if not subscription:
            return False
            
        # Check if backup type is allowed for this tier
        if not self.check_feature_access(user_id, f"backup.{backup_type}"):
            return False
            
        # Get max retention period for this tier
        max_retention = self.subscription_manager.get_quota_limit(
            subscription.tier_id, "backup.retention_days"
        )
        
        if retention_days > max_retention:
            logger.warning(
                f"Backup retention period exceeds limit for user {user_id}: "
                f"requested={retention_days}, limit={max_retention}"
            )
            return False
            
        # Check storage quota for backups
        current_usage = self.usage_tracker.get_current_usage(
            user_id, "backup.storage"
        )
        
        quota_limit = self.subscription_manager.get_quota_limit(
            subscription.tier_id, "backup.storage"
        )
        
        if current_usage + size_bytes > quota_limit:
            logger.warning(
                f"Backup storage quota exceeded for user {user_id}: "
                f"current={current_usage}, requested={size_bytes}, limit={quota_limit}"
            )
            return False
            
        return True


class DataProtectionIntegration:
    """
    Main integration class for the Data Protection Framework.
    
    This class coordinates the integration between the Data Protection Framework
    and other ApexAgent systems, providing a unified interface for secure data
    operations that respect authentication, authorization, and subscription constraints.
    """
    
    def __init__(self):
        """Initialize the Data Protection Integration system."""
        # Initialize core data protection services
        self.encryption_service = encryption_service.EncryptionService()
        self.key_manager = key_manager.KeyManager()
        self.anonymization_service = data_anonymization.DataAnonymizationService()
        self.secure_storage = secure_storage.SecureStorageManager()
        self.backup_manager = backup_recovery.BackupManager()
        self.compliance_manager = compliance_tools.ComplianceManager()
        
        # Initialize auth services
        self.auth_manager = auth_manager.AuthManager()
        self.rbac_manager = enhanced_rbac.EnhancedRBACManager()
        
        # Initialize subscription services
        self.subscription_manager = subscription_manager.SubscriptionManager()
        self.usage_tracker = usage_tracking.UsageTracker()
        
        # Initialize integration managers
        self.auth_integration = AuthIntegrationManager(
            self.encryption_service,
            self.key_manager,
            self.auth_manager,
            self.rbac_manager
        )
        
        self.subscription_integration = SubscriptionIntegrationManager(
            self.subscription_manager,
            self.usage_tracker,
            self.secure_storage,
            self.backup_manager
        )
        
        logger.info("DataProtectionIntegration initialized")
    
    def secure_data_operation(self, user_id: str, session_token: str, 
                             operation: str, data_id: str = None, 
                             data: bytes = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform a secure data operation with full integration of authentication,
        authorization, and subscription constraints.
        
        Args:
            user_id: The ID of the user performing the operation
            session_token: The current session token for authentication
            operation: The operation to perform (encrypt, decrypt, anonymize, store, retrieve, backup)
            data_id: The identifier of the data (if applicable)
            data: The actual data for the operation (if applicable)
            metadata: Additional metadata for the operation
            
        Returns:
            A dictionary containing the result of the operation
        """
        result = {
            'success': False,
            'message': '',
            'data': None,
            'data_id': data_id
        }
        
        # Verify authentication
        if not self.auth_manager.verify_session(session_token):
            result['message'] = 'Authentication failed: Invalid session'
            return result
            
        # Verify user identity
        session_user = self.auth_manager.get_session_user(session_token)
        if session_user != user_id:
            result['message'] = 'Authentication failed: User ID mismatch'
            return result
        
        # Check subscription for feature access
        if not self.subscription_integration.check_feature_access(user_id, operation):
            result['message'] = f'Subscription does not include access to {operation}'
            return result
            
        # Track feature usage
        self.subscription_integration.track_feature_usage(
            user_id, operation, metadata=metadata
        )
        
        # Perform the requested operation with appropriate security checks
        try:
            if operation == 'encrypt':
                if not data:
                    result['message'] = 'No data provided for encryption'
                    return result
                    
                # Check authorization
                if not self.auth_integration.enforce_data_access_policy(
                    user_id, session_token, data_id or 'new_data', 'write'
                ):
                    result['message'] = 'Authorization failed: Insufficient permissions'
                    return result
                    
                # Get encryption key
                key = self.auth_integration.get_user_encryption_key(
                    user_id, session_token, 'encrypt', 
                    require_mfa=metadata.get('sensitivity', 'low') == 'high'
                )
                
                if not key:
                    result['message'] = 'Failed to obtain encryption key'
                    return result
                    
                # Perform encryption
                encrypted_data, new_data_id = self.encryption_service.encrypt_data(
                    data, key, metadata
                )
                
                result['success'] = True
                result['message'] = 'Data encrypted successfully'
                result['data'] = encrypted_data
                result['data_id'] = new_data_id or data_id
                
            elif operation == 'decrypt':
                if not data_id:
                    result['message'] = 'No data ID provided for decryption'
                    return result
                    
                # Check authorization
                if not self.auth_integration.enforce_data_access_policy(
                    user_id, session_token, data_id, 'read'
                ):
                    result['message'] = 'Authorization failed: Insufficient permissions'
                    return result
                    
                # Get decryption key
                key = self.auth_integration.get_user_encryption_key(
                    user_id, session_token, 'decrypt',
                    require_mfa=metadata.get('sensitivity', 'low') == 'high'
                )
                
                if not key:
                    result['message'] = 'Failed to obtain decryption key'
                    return result
                    
                # Perform decryption
                decrypted_data = self.encryption_service.decrypt_data(
                    data_id, key
                )
                
                result['success'] = True
                result['message'] = 'Data decrypted successfully'
                result['data'] = decrypted_data
                
            elif operation == 'anonymize':
                if not data:
                    result['message'] = 'No data provided for anonymization'
                    return result
                    
                # Check authorization
                if not self.rbac_manager.check_permission(
                    user_id, 'data_protection.anonymize'
                ):
                    result['message'] = 'Authorization failed: Insufficient permissions'
                    return result
                    
                # Perform anonymization
                anonymized_data = self.anonymization_service.anonymize_data(
                    data, metadata.get('anonymization_level', 'standard'),
                    metadata.get('fields_to_anonymize', [])
                )
                
                result['success'] = True
                result['message'] = 'Data anonymized successfully'
                result['data'] = anonymized_data
                
            elif operation == 'store':
                if not data:
                    result['message'] = 'No data provided for storage'
                    return result
                    
                storage_type = metadata.get('storage_type', 'object')
                size_bytes = len(data)
                
                # Check quota
                if not self.subscription_integration.check_storage_quota(
                    user_id, storage_type, size_bytes
                ):
                    result['message'] = 'Storage quota exceeded'
                    return result
                    
                # Check authorization
                if not self.rbac_manager.check_permission(
                    user_id, f'data_protection.storage.{storage_type}'
                ):
                    result['message'] = 'Authorization failed: Insufficient permissions'
                    return result
                    
                # Store data
                storage_result = self.secure_storage.store_data(
                    data, user_id, metadata
                )
                
                result['success'] = storage_result['success']
                result['message'] = storage_result['message']
                result['data_id'] = storage_result.get('data_id')
                
            elif operation == 'retrieve':
                if not data_id:
                    result['message'] = 'No data ID provided for retrieval'
                    return result
                    
                # Check authorization
                if not self.auth_integration.enforce_data_access_policy(
                    user_id, session_token, data_id, 'read'
                ):
                    result['message'] = 'Authorization failed: Insufficient permissions'
                    return result
                    
                # Retrieve data
                retrieval_result = self.secure_storage.retrieve_data(
                    data_id, user_id
                )
                
                result['success'] = retrieval_result['success']
                result['message'] = retrieval_result['message']
                result['data'] = retrieval_result.get('data')
                
            elif operation == 'backup':
                if not data_id and not data:
                    result['message'] = 'No data provided for backup'
                    return result
                    
                backup_type = metadata.get('backup_type', 'full')
                retention_days = metadata.get('retention_days', 30)
                size_bytes = len(data) if data else metadata.get('size_bytes', 0)
                
                # Check quota
                if not self.subscription_integration.check_backup_quota(
                    user_id, backup_type, retention_days, size_bytes
                ):
                    result['message'] = 'Backup quota exceeded or retention period too long'
                    return result
                    
                # Check authorization
                if not self.rbac_manager.check_permission(
                    user_id, f'data_protection.backup.{backup_type}'
                ):
                    result['message'] = 'Authorization failed: Insufficient permissions'
                    return result
                    
                # Perform backup
                backup_result = self.backup_manager.create_backup(
                    user_id, data_id, data, metadata
                )
                
                result['success'] = backup_result['success']
                result['message'] = backup_result['message']
                result['data_id'] = backup_result.get('backup_id')
                
            elif operation == 'restore':
                if not data_id:
                    result['message'] = 'No backup ID provided for restore'
                    return result
                    
                # Check authorization
                if not self.rbac_manager.check_permission(
                    user_id, 'data_protection.backup.restore'
                ):
                    result['message'] = 'Authorization failed: Insufficient permissions'
                    return result
                    
                # Perform restore
                restore_result = self.backup_manager.restore_backup(
                    user_id, data_id, metadata
                )
                
                result['success'] = restore_result['success']
                result['message'] = restore_result['message']
                result['data'] = restore_result.get('data')
                result['data_id'] = restore_result.get('original_data_id')
                
            else:
                result['message'] = f'Unknown operation: {operation}'
                
        except Exception as e:
            logger.exception(f"Error in secure_data_operation: {str(e)}")
            result['success'] = False
            result['message'] = f'Operation failed: {str(e)}'
            
        # Log the operation for compliance
        self.compliance_manager.log_data_operation(
            user_id=user_id,
            operation=operation,
            data_id=result.get('data_id'),
            success=result['success'],
            metadata={
                'session_id': session_token,
                'timestamp': self.compliance_manager.get_current_timestamp(),
                'ip_address': self.auth_manager.get_session_ip(session_token),
                'user_agent': self.auth_manager.get_session_user_agent(session_token),
                'operation_metadata': metadata or {}
            }
        )
        
        return result
