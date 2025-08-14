"""
Credit Management module for ApexAgent.

This module handles credit allocation, tracking, and consumption for the ApexAgent
subscription system, including the threshold policy for user-provided API keys.
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from .api_key_manager import ApiKeyManager, ProviderType, ModelCategory


# Configure logging
logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Enumeration of operation types that consume credits."""
    LLM_REQUEST = "llm_request"
    FILE_OPERATION = "file_operation"
    WEB_SEARCH = "web_search"
    DATA_PROCESSING = "data_processing"
    IMAGE_GENERATION = "image_generation"
    SYSTEM_OPERATION = "system_operation"


class CreditManager:
    """Manages credit allocation, tracking, and consumption."""

    def __init__(self, database_connector, api_key_manager: ApiKeyManager):
        """Initialize the credit manager.
        
        Args:
            database_connector: Connection to the database
            api_key_manager: Instance of ApiKeyManager for API key operations
        """
        self.db = database_connector
        self.api_key_manager = api_key_manager
        self._initialize_credit_costs()
    
    def _initialize_credit_costs(self):
        """Initialize the credit costs for different operations."""
        self.credit_costs = {
            OperationType.LLM_REQUEST: {
                ModelCategory.STANDARD: {
                    "base_cost": 1,
                    "per_token": 0.001
                },
                ModelCategory.HIGH_REASONING: {
                    "base_cost": 2,
                    "per_token": 0.002
                }
            },
            OperationType.FILE_OPERATION: {
                "base_cost": 0.5,
                "per_mb": 0.1
            },
            OperationType.WEB_SEARCH: {
                "base_cost": 1,
                "per_result": 0.1
            },
            OperationType.DATA_PROCESSING: {
                "base_cost": 1,
                "per_mb": 0.2
            },
            OperationType.IMAGE_GENERATION: {
                "base_cost": 5,
                "per_image": 5
            },
            OperationType.SYSTEM_OPERATION: {
                "base_cost": 0.1
            }
        }
    
    def get_user_credits(self, user_id: str) -> Dict[str, Any]:
        """Get the credit balance and usage for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with credit information
        """
        try:
            # Get subscription information
            subscription = self.db.get_user_subscription(user_id)
            if not subscription:
                raise ValueError(f"No subscription found for user {user_id}")
            
            # Get credit usage
            credit_usage = self.db.get_user_credit_usage(user_id)
            
            # Calculate remaining credits
            total_allocated = subscription.get("credits_allocated", 0)
            total_used = sum(usage.get("credits", 0) for usage in credit_usage)
            remaining = total_allocated - total_used
            
            return {
                "total_allocated": total_allocated,
                "total_used": total_used,
                "remaining": remaining,
                "subscription_tier": subscription.get("tier"),
                "renewal_date": subscription.get("renewal_date"),
                "usage_history": credit_usage
            }
        except Exception as e:
            logger.error(f"Error getting user credits: {str(e)}")
            raise ValueError(f"Failed to get user credits: {str(e)}")
    
    def process_operation(self, user_id: str, operation_type: OperationType, 
                         metadata: Dict[str, Any]) -> Tuple[bool, float]:
        """Process a general operation and consume credits.
        
        Args:
            user_id: Unique identifier for the user
            operation_type: Type of operation
            metadata: Additional information about the operation
            
        Returns:
            Tuple of (success, credits_consumed)
        """
        try:
            # Calculate credit cost
            cost_config = self.credit_costs.get(operation_type)
            if not cost_config:
                raise ValueError(f"Unknown operation type: {operation_type}")
            
            base_cost = cost_config.get("base_cost", 0)
            credits = base_cost
            
            # Add variable costs based on operation type
            if operation_type == OperationType.FILE_OPERATION:
                file_size_mb = metadata.get("file_size_mb", 0)
                credits += cost_config.get("per_mb", 0) * file_size_mb
            elif operation_type == OperationType.WEB_SEARCH:
                num_results = metadata.get("num_results", 0)
                credits += cost_config.get("per_result", 0) * num_results
            elif operation_type == OperationType.DATA_PROCESSING:
                data_size_mb = metadata.get("data_size_mb", 0)
                credits += cost_config.get("per_mb", 0) * data_size_mb
            elif operation_type == OperationType.IMAGE_GENERATION:
                num_images = metadata.get("num_images", 1)
                credits += cost_config.get("per_image", 0) * num_images
            
            # Check if user has enough credits
            user_credits = self.get_user_credits(user_id)
            if user_credits["remaining"] < credits:
                logger.warning(f"User {user_id} has insufficient credits for operation {operation_type}")
                return False, 0
            
            # Log credit consumption
            self._log_credit_usage(user_id, operation_type, credits, metadata)
            
            return True, credits
        except Exception as e:
            logger.error(f"Error processing operation: {str(e)}")
            return False, 0
    
    def process_llm_operation(self, user_id: str, provider: ProviderType, model: str,
                             tokens: int, operation_metadata: Dict[str, Any]) -> Tuple[bool, float, bool]:
        """Process an LLM operation with threshold policy for user-provided API keys.
        
        Args:
            user_id: Unique identifier for the user
            provider: LLM provider
            model: Model name
            tokens: Number of tokens used
            operation_metadata: Additional information about the operation
            
        Returns:
            Tuple of (success, credits_consumed, used_user_api)
        """
        try:
            # Get model category
            model_category = self.api_key_manager.get_model_category(provider, model)
            
            # Check if user has access to this model category
            if not self.api_key_manager.has_access_to_model_category(user_id, model_category):
                logger.warning(f"User {user_id} does not have access to model category {model_category}")
                return False, 0, False
            
            # Try to get user's API key for this provider and model
            api_key, is_user_provided = self.api_key_manager.get_api_key_for_request(user_id, provider, model)
            
            # If user has their own API key, don't consume credits
            if is_user_provided and api_key:
                # Track usage for reporting but don't consume credits
                self._log_credit_usage(
                    user_id, 
                    OperationType.LLM_REQUEST, 
                    0,  # No credits consumed
                    {
                        "provider": provider.value,
                        "model": model,
                        "tokens": tokens,
                        "used_user_api": True,
                        **operation_metadata
                    }
                )
                return True, 0, True
            
            # If using ApexAgent's API key, calculate and consume credits
            cost_config = self.credit_costs.get(OperationType.LLM_REQUEST, {}).get(model_category, {})
            base_cost = cost_config.get("base_cost", 1)
            per_token = cost_config.get("per_token", 0.001)
            
            credits = base_cost + (tokens * per_token)
            
            # Check if user has enough credits
            user_credits = self.get_user_credits(user_id)
            if user_credits["remaining"] < credits:
                logger.warning(f"User {user_id} has insufficient credits for LLM operation")
                return False, 0, False
            
            # Log credit consumption
            self._log_credit_usage(
                user_id, 
                OperationType.LLM_REQUEST, 
                credits,
                {
                    "provider": provider.value,
                    "model": model,
                    "tokens": tokens,
                    "used_user_api": False,
                    **operation_metadata
                }
            )
            
            return True, credits, False
        except Exception as e:
            logger.error(f"Error processing LLM operation: {str(e)}")
            return False, 0, False
    
    def _log_credit_usage(self, user_id: str, operation_type: OperationType, 
                         credits: float, metadata: Dict[str, Any]) -> bool:
        """Log credit usage for a user.
        
        Args:
            user_id: Unique identifier for the user
            operation_type: Type of operation
            credits: Number of credits consumed
            metadata: Additional information about the operation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            usage_data = {
                "user_id": user_id,
                "operation_type": operation_type.value,
                "credits": credits,
                "timestamp": datetime.now(),
                "metadata": json.dumps(metadata)
            }
            
            self.db.log_credit_usage(usage_data)
            return True
        except Exception as e:
            logger.error(f"Error logging credit usage: {str(e)}")
            return False
    
    def get_usage_analytics(self, user_id: str, start_date: datetime = None, 
                           end_date: datetime = None) -> Dict[str, Any]:
        """Get detailed usage analytics for a user.
        
        Args:
            user_id: Unique identifier for the user
            start_date: Start date for analytics (optional)
            end_date: End date for analytics (optional)
            
        Returns:
            Dictionary with usage analytics
        """
        try:
            # Get credit usage
            credit_usage = self.db.get_user_credit_usage(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get API key usage
            api_usage = self.api_key_manager.get_usage_statistics(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Aggregate by operation type
            usage_by_operation = {}
            for usage in credit_usage:
                op_type = usage.get("operation_type")
                credits = usage.get("credits", 0)
                
                if op_type not in usage_by_operation:
                    usage_by_operation[op_type] = {
                        "count": 0,
                        "credits": 0
                    }
                
                usage_by_operation[op_type]["count"] += 1
                usage_by_operation[op_type]["credits"] += credits
            
            # Aggregate by day
            usage_by_day = {}
            for usage in credit_usage:
                timestamp = usage.get("timestamp")
                if not timestamp:
                    continue
                
                day = timestamp.strftime("%Y-%m-%d")
                credits = usage.get("credits", 0)
                
                if day not in usage_by_day:
                    usage_by_day[day] = {
                        "count": 0,
                        "credits": 0
                    }
                
                usage_by_day[day]["count"] += 1
                usage_by_day[day]["credits"] += credits
            
            # Calculate user vs. ApexAgent API usage
            user_api_operations = 0
            apex_api_operations = 0
            
            for usage in credit_usage:
                if usage.get("operation_type") != OperationType.LLM_REQUEST.value:
                    continue
                
                metadata = json.loads(usage.get("metadata", "{}"))
                if metadata.get("used_user_api", False):
                    user_api_operations += 1
                else:
                    apex_api_operations += 1
            
            return {
                "total_operations": len(credit_usage),
                "total_credits": sum(usage.get("credits", 0) for usage in credit_usage),
                "usage_by_operation": usage_by_operation,
                "usage_by_day": usage_by_day,
                "api_usage": {
                    "user_api_operations": user_api_operations,
                    "apex_api_operations": apex_api_operations,
                    "total_tokens": api_usage.get("total_tokens", 0),
                    "tokens_by_provider": api_usage.get("tokens_by_provider", {})
                },
                "start_date": start_date,
                "end_date": end_date
            }
        except Exception as e:
            logger.error(f"Error getting usage analytics: {str(e)}")
            raise ValueError(f"Failed to get usage analytics: {str(e)}")
    
    def forecast_usage(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Forecast future credit usage based on historical patterns.
        
        Args:
            user_id: Unique identifier for the user
            days: Number of days to forecast
            
        Returns:
            Dictionary with usage forecast
        """
        try:
            # Get historical usage for the past 30 days
            end_date = datetime.now()
            start_date = datetime(end_date.year, end_date.month, end_date.day) - \
                        datetime.timedelta(days=30)
            
            historical_usage = self.get_usage_analytics(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Calculate daily average
            total_credits = historical_usage.get("total_credits", 0)
            daily_average = total_credits / 30
            
            # Project future usage
            projected_usage = daily_average * days
            
            # Get current credit balance
            user_credits = self.get_user_credits(user_id)
            remaining = user_credits.get("remaining", 0)
            
            # Calculate if user will run out of credits
            will_deplete = projected_usage > remaining
            days_until_depleted = None
            
            if will_deplete and daily_average > 0:
                days_until_depleted = int(remaining / daily_average)
            
            return {
                "daily_average_usage": daily_average,
                "projected_usage": projected_usage,
                "remaining_credits": remaining,
                "will_deplete": will_deplete,
                "days_until_depleted": days_until_depleted,
                "forecast_days": days
            }
        except Exception as e:
            logger.error(f"Error forecasting usage: {str(e)}")
            raise ValueError(f"Failed to forecast usage: {str(e)}")
    
    def get_optimization_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get recommendations for optimizing credit usage.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with optimization recommendations
        """
        try:
            # Get usage analytics
            analytics = self.get_usage_analytics(user_id)
            
            recommendations = []
            
            # Check if user is using their own API keys
            api_usage = analytics.get("api_usage", {})
            user_api_operations = api_usage.get("user_api_operations", 0)
            apex_api_operations = api_usage.get("apex_api_operations", 0)
            
            if apex_api_operations > 0 and user_api_operations == 0:
                recommendations.append({
                    "type": "api_keys",
                    "description": "Consider adding your own API keys to reduce credit consumption",
                    "potential_savings": "Up to 100% of LLM operation credits"
                })
            
            # Check for high token usage
            tokens_by_provider = api_usage.get("tokens_by_provider", {})
            for provider, tokens in tokens_by_provider.items():
                if tokens > 100000:  # Arbitrary threshold
                    recommendations.append({
                        "type": "token_usage",
                        "description": f"High token usage detected for {provider}",
                        "potential_savings": "Consider using more efficient prompts to reduce token usage"
                    })
            
            # Check for expensive operation types
            usage_by_operation = analytics.get("usage_by_operation", {})
            for op_type, usage in usage_by_operation.items():
                if op_type == OperationType.IMAGE_GENERATION.value and usage.get("count", 0) > 10:
                    recommendations.append({
                        "type": "image_generation",
                        "description": "High usage of image generation detected",
                        "potential_savings": "Consider reducing the number of generated images"
                    })
            
            return {
                "recommendations": recommendations,
                "analytics_summary": {
                    "total_credits": analytics.get("total_credits", 0),
                    "operation_count": analytics.get("total_operations", 0),
                    "user_api_ratio": user_api_operations / (user_api_operations + apex_api_operations) if (user_api_operations + apex_api_operations) > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting optimization recommendations: {str(e)}")
            raise ValueError(f"Failed to get optimization recommendations: {str(e)}")
