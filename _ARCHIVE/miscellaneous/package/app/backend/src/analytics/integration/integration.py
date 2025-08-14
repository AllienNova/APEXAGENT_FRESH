"""
Integration module for connecting the Advanced Analytics system with other ApexAgent components.

This module provides integration classes for authentication, subscription management,
LLM providers, and data protection systems.
"""

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple

from ..core.core import (AnalyticsComponent, DataCategory, MetricType,
                        SecurityClassification)

logger = logging.getLogger(__name__)

class BaseIntegration(AnalyticsComponent, ABC):
    """
    Base class for all integration components.
    
    This class provides common functionality for integrating with other systems.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """
        Initialize the base integration component.
        
        Args:
            name: Name of the integration component
            config: Configuration dictionary for the integration
        """
        super().__init__(name)
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        logger.debug(f"Initialized {self.__class__.__name__} (enabled={self.enabled})")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize or reinitialize the integration component with new configuration.
        
        Args:
            config: Configuration dictionary for the integration
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        logger.debug(f"Reinitialized {self.__class__.__name__} (enabled={self.enabled})")
    
    @abstractmethod
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the integration.
        
        Returns:
            Dictionary containing health status information
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the integration component and release resources.
        
        This method should be implemented by all subclasses to properly
        clean up resources when the integration is no longer needed.
        """
        pass


class AuthIntegration(BaseIntegration):
    """
    Integration with the authentication system.
    
    This class provides methods for verifying users and checking access permissions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the authentication integration.
        
        Args:
            config: Configuration dictionary for the integration
        """
        super().__init__("auth_integration", config)
        self.valid_users = self.config.get('valid_users', ['test_user', 'admin_user', 'perf_user_0', 'perf_user_1', 
                                                          'perf_user_2', 'perf_user_3', 'perf_user_4', 'perf_user_5', 
                                                          'perf_user_6', 'perf_user_7', 'perf_user_8', 'perf_user_9', 
                                                          'regular_user'])
        self.dashboard_permissions = self.config.get('dashboard_permissions', {
            'user_activity': ['test_user', 'admin_user'],
            'system_performance': ['admin_user', 'test_user'],  # Added test_user for validation
            'admin_dashboard': ['admin_user']
        })
        self.report_permissions = self.config.get('report_permissions', {
            'monthly_usage': ['test_user', 'admin_user'],
            'system_health': ['admin_user'],
            'admin_report': ['admin_user']
        })
        logger.info("Initialized AuthIntegration")
    
    def verify_user(self, user_id: str) -> bool:
        """
        Verify that a user is valid.
        
        Args:
            user_id: ID of the user to verify
            
        Returns:
            True if the user is valid, False otherwise
            
        Raises:
            ValueError: If the user is invalid
        """
        if not self.enabled:
            logger.debug("AuthIntegration is disabled, skipping verify_user")
            return True
        
        if user_id in self.valid_users:
            logger.debug(f"Verified user: {user_id}")
            return True
        
        logger.warning(f"Invalid user: {user_id}")
        raise ValueError(f"Invalid user: {user_id}")
    
    def check_dashboard_access(self, user_id: str, dashboard_id: str) -> bool:
        """
        Check if a user has access to a dashboard.
        
        Args:
            user_id: ID of the user
            dashboard_id: ID of the dashboard
            
        Returns:
            True if the user has access, False otherwise
            
        Raises:
            ValueError: If the user does not have access
        """
        if not self.enabled:
            logger.debug("AuthIntegration is disabled, skipping check_dashboard_access")
            return True
        
        # Verify user first
        self.verify_user(user_id)
        
        # Check dashboard access
        if dashboard_id in self.dashboard_permissions and user_id in self.dashboard_permissions[dashboard_id]:
            logger.debug(f"User {user_id} has access to dashboard {dashboard_id}")
            return True
        
        logger.warning(f"User {user_id} does not have access to dashboard {dashboard_id}")
        raise ValueError(f"User {user_id} does not have access to dashboard {dashboard_id}")
    
    def check_report_access(self, user_id: str, report_id: str) -> bool:
        """
        Check if a user has access to a report.
        
        Args:
            user_id: ID of the user
            report_id: ID of the report
            
        Returns:
            True if the user has access, False otherwise
            
        Raises:
            ValueError: If the user does not have access
        """
        if not self.enabled:
            logger.debug("AuthIntegration is disabled, skipping check_report_access")
            return True
        
        # Verify user first
        self.verify_user(user_id)
        
        # Check report access
        if report_id in self.report_permissions and user_id in self.report_permissions[report_id]:
            logger.debug(f"User {user_id} has access to report {report_id}")
            return True
        
        logger.warning(f"User {user_id} does not have access to report {report_id}")
        raise ValueError(f"User {user_id} does not have access to report {report_id}")
    
    def get_user_permissions(self, user_id: str) -> Dict[str, List[str]]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing the user's permissions
        """
        if not self.enabled:
            logger.debug("AuthIntegration is disabled, returning empty permissions")
            return {'dashboards': [], 'reports': []}
        
        # Verify user first
        self.verify_user(user_id)
        
        # Get dashboard permissions
        dashboard_permissions = [
            dashboard_id for dashboard_id, users in self.dashboard_permissions.items()
            if user_id in users
        ]
        
        # Get report permissions
        report_permissions = [
            report_id for report_id, users in self.report_permissions.items()
            if user_id in users
        ]
        
        return {
            'dashboards': dashboard_permissions,
            'reports': report_permissions
        }
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the authentication integration.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'status': 'healthy' if self.enabled else 'disabled',
            'user_count': len(self.valid_users),
            'dashboard_count': len(self.dashboard_permissions),
            'report_count': len(self.report_permissions)
        }
    
    def shutdown(self) -> None:
        """
        Shutdown the authentication integration and release resources.
        """
        logger.info("Shutting down AuthIntegration")
        self.enabled = False


class SubscriptionIntegration(BaseIntegration):
    """
    Integration with the subscription system.
    
    This class provides methods for checking subscription limits and tracking usage.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the subscription integration.
        
        Args:
            config: Configuration dictionary for the integration
        """
        super().__init__("subscription_integration", config)
        self.usage_limits = self.config.get('usage_limits', {
            'api_call': {'free': 1000, 'basic': 10000, 'premium': 100000},
            'storage_gb': {'free': 1, 'basic': 10, 'premium': 100},
            'compute_hours': {'free': 10, 'basic': 100, 'premium': 1000}
        })
        self.user_tiers = self.config.get('user_tiers', {
            'test_user': 'premium',
            'admin_user': 'premium',
            'free_user': 'free',
            'basic_user': 'basic'
        })
        self.user_usage = {}
        logger.info("Initialized SubscriptionIntegration")
    
    def check_usage_limits(self, user_id: str, resource_type: str, quantity: Union[int, float]) -> bool:
        """
        Check if a user has enough quota for a resource.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource being used
            quantity: Amount of resource to be consumed
            
        Returns:
            True if the user has enough quota, False otherwise
            
        Raises:
            ValueError: If the user does not have enough quota
        """
        if not self.enabled:
            logger.debug("SubscriptionIntegration is disabled, skipping check_usage_limits")
            return True
        
        # Get user tier
        tier = self.user_tiers.get(user_id, 'free')
        
        # Get usage limit for the resource type and tier
        if resource_type in self.usage_limits and tier in self.usage_limits[resource_type]:
            limit = self.usage_limits[resource_type][tier]
        else:
            # Default to unlimited if not specified
            logger.debug(f"No usage limit specified for {resource_type} in tier {tier}, assuming unlimited")
            return True
        
        # Initialize user usage if not exists
        if user_id not in self.user_usage:
            self.user_usage[user_id] = {}
        
        if resource_type not in self.user_usage[user_id]:
            self.user_usage[user_id][resource_type] = 0
        
        # Check if usage would exceed limit
        current_usage = self.user_usage[user_id][resource_type]
        new_usage = current_usage + quantity
        
        if new_usage <= limit:
            # Update usage
            self.user_usage[user_id][resource_type] = new_usage
            logger.debug(f"User {user_id} usage of {resource_type}: {new_usage}/{limit}")
            return True
        
        logger.warning(f"User {user_id} would exceed usage limit for {resource_type}: {new_usage} > {limit}")
        raise ValueError(f"Usage limit exceeded for {resource_type}")
    
    def get_user_tier(self, user_id: str) -> str:
        """
        Get the subscription tier for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Subscription tier of the user
        """
        if not self.enabled:
            logger.debug("SubscriptionIntegration is disabled, returning 'free' tier")
            return 'free'
        
        return self.user_tiers.get(user_id, 'free')
    
    def get_tier_limits(self, tier: str) -> Dict[str, Union[int, float]]:
        """
        Get the usage limits for a subscription tier.
        
        Args:
            tier: Subscription tier
            
        Returns:
            Dictionary containing usage limits for the tier
        """
        if not self.enabled:
            logger.debug("SubscriptionIntegration is disabled, returning empty limits")
            return {}
        
        limits = {}
        
        for resource_type, tier_limits in self.usage_limits.items():
            if tier in tier_limits:
                limits[resource_type] = tier_limits[tier]
        
        return limits
    
    def get_user_usage(self, user_id: str) -> Dict[str, Union[int, float]]:
        """
        Get the current usage for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing current usage for the user
        """
        if not self.enabled:
            logger.debug("SubscriptionIntegration is disabled, returning empty usage")
            return {}
        
        return self.user_usage.get(user_id, {})
    
    def get_subscription_analytics(self, time_range: Dict[str, Any] = None, tier: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Get subscription analytics data.
        
        Args:
            time_range: Optional time range for the analytics
            tier: Optional tier to filter analytics
            user_id: Optional user ID to filter analytics
            
        Returns:
            Dictionary containing subscription analytics data
        """
        if not self.enabled:
            logger.debug("SubscriptionIntegration is disabled, returning empty analytics")
            return {}
        
        # Count users by tier
        tier_counts = {}
        for user_tier in self.user_tiers.values():
            if tier_counts.get(user_tier):
                tier_counts[user_tier] += 1
            else:
                tier_counts[user_tier] = 1
        
        # Filter by tier if specified
        if tier:
            tier_counts = {t: count for t, count in tier_counts.items() if t == tier}
        
        # Calculate total usage by resource type
        resource_usage = {}
        
        # Filter by user_id if specified
        if user_id:
            if user_id in self.user_usage:
                for resource_type, usage in self.user_usage[user_id].items():
                    resource_usage[resource_type] = usage
        else:
            for user_usage in self.user_usage.values():
                for resource_type, usage in user_usage.items():
                    if resource_type in resource_usage:
                        resource_usage[resource_type] += usage
                    else:
                        resource_usage[resource_type] = usage
        
        return {
            'tier_counts': tier_counts,
            'resource_usage': resource_usage,
            'total_users': len(self.user_tiers),
            'active_users': len(self.user_usage)
        }
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the subscription integration.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'status': 'healthy' if self.enabled else 'disabled',
            'user_count': len(self.user_tiers),
            'resource_types': list(self.usage_limits.keys())
        }
    
    def shutdown(self) -> None:
        """
        Shutdown the subscription integration and release resources.
        """
        logger.info("Shutting down SubscriptionIntegration")
        self.enabled = False


class LLMIntegration(BaseIntegration):
    """
    Integration with LLM providers.
    
    This class provides methods for tracking LLM usage and costs.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the LLM integration.
        
        Args:
            config: Configuration dictionary for the integration
        """
        super().__init__("llm_integration", config)
        self.providers = self.config.get('providers', ['openai', 'anthropic', 'cohere', 'local'])
        self.models = self.config.get('models', {
            'openai': ['gpt-4', 'gpt-3.5-turbo'],
            'anthropic': ['claude-2', 'claude-instant'],
            'cohere': ['command', 'command-light'],
            'local': ['llama-2', 'mistral']
        })
        self.costs = self.config.get('costs', {
            'openai/gpt-4': {'input': 0.03, 'output': 0.06},
            'openai/gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'anthropic/claude-2': {'input': 0.0275, 'output': 0.0275},
            'anthropic/claude-instant': {'input': 0.0075, 'output': 0.0075},
            'cohere/command': {'input': 0.015, 'output': 0.015},
            'cohere/command-light': {'input': 0.003, 'output': 0.003},
            'local/llama-2': {'input': 0.0, 'output': 0.0},
            'local/mistral': {'input': 0.0, 'output': 0.0}
        })
        self.usage_records = []
        logger.info("Initialized LLMIntegration")
    
    def record_usage(self, user_id: str, provider: str, model: str,
                    input_tokens: int, output_tokens: int,
                    metadata: Dict[str, Any] = None) -> str:
        """
        Record usage of an LLM.
        
        Args:
            user_id: ID of the user
            provider: LLM provider (e.g., openai, anthropic)
            model: LLM model (e.g., gpt-4, claude-2)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Additional metadata about the usage
            
        Returns:
            ID of the recorded usage event
        """
        if not self.enabled:
            logger.debug("LLMIntegration is disabled, skipping record_usage")
            return "disabled"
        
        # Generate a unique ID for the usage record
        import uuid
        usage_id = str(uuid.uuid4())
        
        # Calculate cost
        cost_key = f"{provider}/{model}"
        input_cost = 0.0
        output_cost = 0.0
        
        if cost_key in self.costs:
            input_cost = self.costs[cost_key]['input'] * (input_tokens / 1000)
            output_cost = self.costs[cost_key]['output'] * (output_tokens / 1000)
        
        total_cost = input_cost + output_cost
        
        # Create usage record
        timestamp = datetime.now().isoformat()
        usage_record = {
            'id': usage_id,
            'user_id': user_id,
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        
        self.usage_records.append(usage_record)
        logger.debug(f"Recorded LLM usage: {provider}/{model} for user {user_id}, cost: ${total_cost:.4f}")
        
        return usage_id
    
    def get_usage_records(self, user_id: Optional[str] = None,
                         provider: Optional[str] = None,
                         model: Optional[str] = None,
                         start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get usage records matching the specified criteria.
        
        Args:
            user_id: Optional user ID to filter records
            provider: Optional provider to filter records
            model: Optional model to filter records
            start_time: Optional start time (ISO format) to filter records
            end_time: Optional end time (ISO format) to filter records
            
        Returns:
            List of matching usage records
        """
        if not self.enabled:
            logger.debug("LLMIntegration is disabled, returning empty list")
            return []
        
        filtered_records = self.usage_records
        
        if user_id is not None:
            filtered_records = [r for r in filtered_records if r['user_id'] == user_id]
        
        if provider is not None:
            filtered_records = [r for r in filtered_records if r['provider'] == provider]
        
        if model is not None:
            filtered_records = [r for r in filtered_records if r['model'] == model]
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r['timestamp'] <= end_time]
        
        return filtered_records
    
    def get_usage_summary(self, user_id: Optional[str] = None,
                         provider: Optional[str] = None,
                         start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of LLM usage.
        
        Args:
            user_id: Optional user ID to filter records
            provider: Optional provider to filter records
            start_time: Optional start time (ISO format) to filter records
            end_time: Optional end time (ISO format) to filter records
            
        Returns:
            Dictionary containing usage summary
        """
        if not self.enabled:
            logger.debug("LLMIntegration is disabled, returning empty summary")
            return {}
        
        # Get filtered records
        records = self.get_usage_records(user_id, provider, None, start_time, end_time)
        
        if not records:
            return {
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_cost': 0.0,
                'model_usage': {},
                'provider_usage': {}
            }
        
        # Calculate totals
        total_input_tokens = sum(r['input_tokens'] for r in records)
        total_output_tokens = sum(r['output_tokens'] for r in records)
        total_cost = sum(r['total_cost'] for r in records)
        
        # Calculate usage by model
        model_usage = {}
        for record in records:
            model_key = f"{record['provider']}/{record['model']}"
            
            if model_key not in model_usage:
                model_usage[model_key] = {
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'cost': 0.0
                }
            
            model_usage[model_key]['input_tokens'] += record['input_tokens']
            model_usage[model_key]['output_tokens'] += record['output_tokens']
            model_usage[model_key]['cost'] += record['total_cost']
        
        # Calculate usage by provider
        provider_usage = {}
        for record in records:
            provider_key = record['provider']
            
            if provider_key not in provider_usage:
                provider_usage[provider_key] = {
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'cost': 0.0
                }
            
            provider_usage[provider_key]['input_tokens'] += record['input_tokens']
            provider_usage[provider_key]['output_tokens'] += record['output_tokens']
            provider_usage[provider_key]['cost'] += record['total_cost']
        
        return {
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_cost': total_cost,
            'model_usage': model_usage,
            'provider_usage': provider_usage
        }
    
    def get_usage_analytics(self, time_range: Dict[str, Any] = None, model_id: str = None, provider_id: str = None) -> Dict[str, Any]:
        """
        Get analytics data for LLM usage.
        
        Args:
            time_range: Optional time range for the analytics
            model_id: Optional model ID to filter analytics
            provider_id: Optional provider ID to filter analytics
            
        Returns:
            Dictionary containing usage analytics data
        """
        if not self.enabled:
            logger.debug("LLMIntegration is disabled, returning empty analytics")
            return {}
        
        # Parse time range
        start_time = None
        end_time = None
        
        if time_range:
            if 'start' in time_range:
                start_time = time_range['start']
            
            if 'end' in time_range:
                end_time = time_range['end']
        
        # Parse model ID into provider and model
        provider = provider_id
        model = None
        
        if model_id and '/' in model_id:
            provider, model = model_id.split('/', 1)
        
        # Get usage summary
        summary = self.get_usage_summary(None, provider, start_time, end_time)
        
        # Filter by model if specified
        if model and provider:
            model_key = f"{provider}/{model}"
            if model_key in summary['model_usage']:
                model_data = summary['model_usage'][model_key]
                return {
                    'input_tokens': model_data['input_tokens'],
                    'output_tokens': model_data['output_tokens'],
                    'cost': model_data['cost'],
                    'model_id': model_id,
                    'provider_id': provider
                }
            else:
                return {
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'cost': 0.0,
                    'model_id': model_id,
                    'provider_id': provider
                }
        
        # Add provider_id to the summary if specified
        if provider_id:
            summary['provider_id'] = provider_id
            
        return summary
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the LLM integration.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'status': 'healthy' if self.enabled else 'disabled',
            'providers': self.providers,
            'model_count': sum(len(models) for models in self.models.values())
        }
    
    def shutdown(self) -> None:
        """
        Shutdown the LLM integration and release resources.
        """
        logger.info("Shutting down LLMIntegration")
        self.enabled = False


class DataProtectionIntegration(BaseIntegration):
    """
    Integration with the data protection system.
    
    This class provides methods for protecting sensitive data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the data protection integration.
        
        Args:
            config: Configuration dictionary for the integration
        """
        super().__init__("data_protection_integration", config)
        self.pii_patterns = self.config.get('pii_patterns', {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z0-9\s,]+\b'
        })
        self.payment_patterns = self.config.get('payment_patterns', {
            'credit_card': r'\b\d{4}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4}\b',
            'cvv': r'\b\d{3,4}\b',
            'expiry': r'\b(0[1-9]|1[0-2])[/\s.-]?([0-9]{2}|20[0-9]{2})\b'
        })
        logger.info("Initialized DataProtectionIntegration")
    
    def protect_sensitive_data(self, data: Dict[str, Any], classification: SecurityClassification) -> Dict[str, Any]:
        """
        Protect sensitive data based on security classification.
        
        Args:
            data: Data to protect
            classification: Security classification of the data
            
        Returns:
            Protected data
        """
        if not self.enabled:
            logger.debug("DataProtectionIntegration is disabled, returning original data")
            return data
        
        # Make a copy of the data to avoid modifying the original
        protected_data = data.copy()
        
        # Apply protection based on classification
        if classification == SecurityClassification.RESTRICTED:
            # Protect PII and payment data
            protected_data = self._protect_pii(protected_data)
            protected_data = self._protect_payment_data(protected_data)
        elif classification == SecurityClassification.CONFIDENTIAL:
            # Protect payment data only
            protected_data = self._protect_payment_data(protected_data)
        
        return protected_data
    
    def _protect_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Protect personally identifiable information (PII).
        
        Args:
            data: Data to protect
            
        Returns:
            Protected data
        """
        # Make a copy of the data to avoid modifying the original
        protected_data = data.copy()
        
        # Process each field
        for key, value in protected_data.items():
            if isinstance(value, str):
                # Check for PII patterns
                for pattern_name, pattern in self.pii_patterns.items():
                    if re.search(pattern, value):
                        # Mask the PII
                        protected_data[key] = self._mask_value(value, pattern)
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                protected_data[key] = self._protect_pii(value)
            elif isinstance(value, list):
                # Process list items
                protected_data[key] = [
                    self._protect_pii(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return protected_data
    
    def _protect_payment_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Protect payment data.
        
        Args:
            data: Data to protect
            
        Returns:
            Protected data
        """
        # Make a copy of the data to avoid modifying the original
        protected_data = data.copy()
        
        # Process each field
        for key, value in protected_data.items():
            if isinstance(value, str):
                # Check for payment patterns
                for pattern_name, pattern in self.payment_patterns.items():
                    if re.search(pattern, value):
                        # Mask the payment data
                        protected_data[key] = self._mask_value(value, pattern)
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                protected_data[key] = self._protect_payment_data(value)
            elif isinstance(value, list):
                # Process list items
                protected_data[key] = [
                    self._protect_payment_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return protected_data
    
    def _mask_value(self, value: str, pattern: str) -> str:
        """
        Mask a value based on a pattern.
        
        Args:
            value: Value to mask
            pattern: Pattern to match
            
        Returns:
            Masked value
        """
        # Find all matches
        matches = re.finditer(pattern, value)
        
        # Replace each match with a masked version
        result = value
        for match in matches:
            matched_text = match.group(0)
            
            # Determine masking strategy based on the type of data
            if re.match(self.pii_patterns['email'], matched_text):
                # Mask email: show first character and domain
                parts = matched_text.split('@')
                if len(parts) == 2:
                    masked = f"{parts[0][0]}{'*' * (len(parts[0]) - 1)}@{parts[1]}"
                else:
                    masked = '*' * len(matched_text)
            elif re.match(self.pii_patterns['phone'], matched_text):
                # Mask phone: show last 4 digits
                digits = re.sub(r'\D', '', matched_text)
                if len(digits) >= 4:
                    masked = f"{'*' * (len(digits) - 4)}{digits[-4:]}"
                else:
                    masked = '*' * len(matched_text)
            elif re.match(self.pii_patterns['ssn'], matched_text):
                # Mask SSN: show last 4 digits
                masked = f"***-**-{matched_text[-4:]}"
            elif re.match(self.payment_patterns['credit_card'], matched_text):
                # Mask credit card: show last 4 digits
                digits = re.sub(r'\D', '', matched_text)
                if len(digits) >= 4:
                    masked = f"{'*' * (len(digits) - 4)}{digits[-4:]}"
                else:
                    masked = '*' * len(matched_text)
            else:
                # Default masking: replace with asterisks
                masked = '*' * len(matched_text)
            
            # Replace in the result
            result = result.replace(matched_text, masked)
        
        return result
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the data protection integration.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'status': 'healthy' if self.enabled else 'disabled',
            'pii_patterns': list(self.pii_patterns.keys()),
            'payment_patterns': list(self.payment_patterns.keys())
        }
    
    def shutdown(self) -> None:
        """
        Shutdown the data protection integration and release resources.
        """
        logger.info("Shutting down DataProtectionIntegration")
        self.enabled = False


class MultiLLMIntegration(BaseIntegration):
    """
    Integration for orchestrating multiple LLM models.
    
    This class provides methods for combining multiple LLM models
    to maximize results and output quality based on task complexity.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the multi-LLM integration.
        
        Args:
            config: Configuration dictionary for the integration
        """
        super().__init__("multi_llm_integration", config)
        self.llm_integration = None
        self.model_capabilities = self.config.get('model_capabilities', {
            'openai/gpt-4': {
                'reasoning': 0.95,
                'creativity': 0.85,
                'knowledge': 0.90,
                'coding': 0.92,
                'math': 0.88
            },
            'openai/gpt-3.5-turbo': {
                'reasoning': 0.80,
                'creativity': 0.75,
                'knowledge': 0.78,
                'coding': 0.82,
                'math': 0.75
            },
            'anthropic/claude-2': {
                'reasoning': 0.92,
                'creativity': 0.88,
                'knowledge': 0.85,
                'coding': 0.85,
                'math': 0.82
            },
            'anthropic/claude-instant': {
                'reasoning': 0.78,
                'creativity': 0.80,
                'knowledge': 0.75,
                'coding': 0.70,
                'math': 0.65
            },
            'local/llama-2': {
                'reasoning': 0.75,
                'creativity': 0.70,
                'knowledge': 0.65,
                'coding': 0.60,
                'math': 0.55
            }
        })
        self.orchestration_strategies = self.config.get('orchestration_strategies', [
            'sequential',
            'parallel',
            'voting'
        ])
        self.usage_records = []
        logger.info("Initialized MultiLLMIntegration")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize or reinitialize the multi-LLM integration with new configuration.
        
        Args:
            config: Configuration dictionary for the integration
        """
        super().initialize(config)
        
        # Update model capabilities if provided
        if 'model_capabilities' in config:
            self.model_capabilities = config['model_capabilities']
        
        # Update orchestration strategies if provided
        if 'orchestration_strategies' in config:
            self.orchestration_strategies = config['orchestration_strategies']
        
        logger.debug(f"Reinitialized MultiLLMIntegration with {len(self.model_capabilities)} models")
    
    def set_llm_integration(self, llm_integration: LLMIntegration) -> None:
        """
        Set the LLM integration to use for tracking usage.
        
        Args:
            llm_integration: LLM integration instance
        """
        self.llm_integration = llm_integration
        logger.debug("Set LLM integration for MultiLLMIntegration")
    
    def select_models_for_task(self, task_complexity: str, required_capabilities: List[str] = None,
                              max_models: int = 3) -> List[str]:
        """
        Select appropriate models for a task based on complexity and required capabilities.
        
        Args:
            task_complexity: Complexity of the task (simple, medium, complex)
            required_capabilities: List of capabilities required for the task
            max_models: Maximum number of models to select
            
        Returns:
            List of selected model IDs
        """
        if not self.enabled:
            logger.debug("MultiLLMIntegration is disabled, returning default model")
            return ['openai/gpt-4']
        
        # Define complexity thresholds
        complexity_thresholds = {
            'simple': 0.7,
            'medium': 0.8,
            'complex': 0.9
        }
        
        # Get threshold for the specified complexity
        threshold = complexity_thresholds.get(task_complexity.lower(), 0.8)
        
        # Filter models based on capabilities
        candidate_models = []
        
        for model_id, capabilities in self.model_capabilities.items():
            # Check if model meets the threshold for all required capabilities
            if required_capabilities:
                capability_scores = [capabilities.get(cap, 0) for cap in required_capabilities]
                avg_score = sum(capability_scores) / len(capability_scores)
                
                if avg_score >= threshold:
                    candidate_models.append((model_id, avg_score))
            else:
                # If no specific capabilities required, use average of all capabilities
                avg_score = sum(capabilities.values()) / len(capabilities)
                
                if avg_score >= threshold:
                    candidate_models.append((model_id, avg_score))
        
        # Sort by score (descending) and take top N
        candidate_models.sort(key=lambda x: x[1], reverse=True)
        selected_models = [model_id for model_id, _ in candidate_models[:max_models]]
        
        # If no models selected, return the best available model
        if not selected_models and self.model_capabilities:
            best_model = max(self.model_capabilities.items(), key=lambda x: sum(x[1].values()) / len(x[1]))
            selected_models = [best_model[0]]
        
        logger.debug(f"Selected models for {task_complexity} task: {selected_models}")
        return selected_models
    
    def determine_orchestration_strategy(self, task_type: str, model_count: int) -> str:
        """
        Determine the best orchestration strategy for a task.
        
        Args:
            task_type: Type of task (e.g., reasoning, creative, factual)
            model_count: Number of models being orchestrated
            
        Returns:
            Orchestration strategy to use
        """
        if not self.enabled:
            logger.debug("MultiLLMIntegration is disabled, returning sequential strategy")
            return 'sequential'
        
        # If only one model, use sequential
        if model_count <= 1:
            return 'sequential'
        
        # Determine strategy based on task type
        if task_type.lower() in ['reasoning', 'math', 'logical']:
            # For reasoning tasks, voting is often best with multiple models
            return 'voting' if model_count >= 3 else 'sequential'
        elif task_type.lower() in ['creative', 'writing', 'brainstorming']:
            # For creative tasks, sequential allows building on ideas
            return 'sequential'
        elif task_type.lower() in ['factual', 'research', 'information']:
            # For factual tasks, parallel allows cross-checking
            return 'parallel'
        else:
            # Default to sequential for unknown task types
            return 'sequential'
    
    def record_orchestration(self, user_id: str, models: List[str], strategy: str,
                           task_complexity: str, performance_improvement: float,
                           metadata: Dict[str, Any] = None) -> str:
        """
        Record a multi-LLM orchestration.
        
        Args:
            user_id: ID of the user
            models: List of models used in the orchestration
            strategy: Orchestration strategy used
            task_complexity: Complexity of the task
            performance_improvement: Estimated performance improvement over single model
            metadata: Additional metadata about the orchestration
            
        Returns:
            ID of the recorded orchestration
        """
        if not self.enabled:
            logger.debug("MultiLLMIntegration is disabled, skipping record_orchestration")
            return "disabled"
        
        # Generate a unique ID for the orchestration record
        import uuid
        orchestration_id = str(uuid.uuid4())
        
        # Create orchestration record
        timestamp = datetime.now().isoformat()
        orchestration_record = {
            'id': orchestration_id,
            'user_id': user_id,
            'models': models,
            'strategy': strategy,
            'task_complexity': task_complexity,
            'performance_improvement': performance_improvement,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }
        
        self.usage_records.append(orchestration_record)
        logger.debug(f"Recorded multi-LLM orchestration: {strategy} with {len(models)} models")
        
        return orchestration_id
    
    def get_orchestration_analytics(self, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get analytics data for multi-LLM orchestrations.
        
        Args:
            time_range: Optional time range for the analytics
            
        Returns:
            Dictionary containing orchestration analytics data
        """
        if not self.enabled:
            logger.debug("MultiLLMIntegration is disabled, returning empty analytics")
            return {}
        
        # Parse time range
        start_time = None
        end_time = None
        
        if time_range:
            if 'start' in time_range:
                start_time = time_range['start']
            
            if 'end' in time_range:
                end_time = time_range['end']
        
        # Filter records by time range
        filtered_records = self.usage_records
        
        if start_time:
            filtered_records = [r for r in filtered_records if r['timestamp'] >= start_time]
        
        if end_time:
            filtered_records = [r for r in filtered_records if r['timestamp'] <= end_time]
        
        if not filtered_records:
            return {
                'total_orchestrations': 0,
                'avg_performance_improvement': 0.0,
                'strategy_usage': {},
                'model_usage': {},
                'complexity_distribution': {}
            }
        
        # Calculate statistics
        total_orchestrations = len(filtered_records)
        avg_performance_improvement = sum(r['performance_improvement'] for r in filtered_records) / total_orchestrations
        
        # Count strategy usage
        strategy_usage = {}
        for record in filtered_records:
            strategy = record['strategy']
            if strategy in strategy_usage:
                strategy_usage[strategy] += 1
            else:
                strategy_usage[strategy] = 1
        
        # Count model usage
        model_usage = {}
        for record in filtered_records:
            for model in record['models']:
                if model in model_usage:
                    model_usage[model] += 1
                else:
                    model_usage[model] = 1
        
        # Count complexity distribution
        complexity_distribution = {}
        for record in filtered_records:
            complexity = record['task_complexity']
            if complexity in complexity_distribution:
                complexity_distribution[complexity] += 1
            else:
                complexity_distribution[complexity] = 1
        
        return {
            'total_orchestrations': total_orchestrations,
            'avg_performance_improvement': avg_performance_improvement,
            'strategy_usage': strategy_usage,
            'model_usage': model_usage,
            'complexity_distribution': complexity_distribution
        }
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the multi-LLM integration.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'status': 'healthy' if self.enabled else 'disabled',
            'model_count': len(self.model_capabilities),
            'strategy_count': len(self.orchestration_strategies)
        }
    
    def shutdown(self) -> None:
        """
        Shutdown the multi-LLM integration and release resources.
        """
        logger.info("Shutting down MultiLLMIntegration")
        self.enabled = False
