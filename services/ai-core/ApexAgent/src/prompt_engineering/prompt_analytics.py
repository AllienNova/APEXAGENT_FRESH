"""
Comprehensive prompt analytics for the Aideon AI Lite platform.
This module provides robust tracking and optimization of prompt performance
to enable continuous improvement and token efficiency.
"""

from typing import Dict, Any, List, Optional, Union
import json
import os
import logging
import time
import datetime
from pathlib import Path
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptAnalytics:
    """
    Comprehensive analytics system for tracking and optimizing prompt performance.
    """
    
    def __init__(self, analytics_dir: str = None):
        """
        Initialize the prompt analytics system.
        
        Args:
            analytics_dir: Directory to store analytics data
        """
        # Set analytics directory
        if analytics_dir:
            self.analytics_dir = analytics_dir
        else:
            self.analytics_dir = os.path.join(os.path.dirname(__file__), "analytics_data")
        
        # Create directory if it doesn't exist
        os.makedirs(self.analytics_dir, exist_ok=True)
        
        # Initialize analytics storage
        self.prompt_metrics = {}
        self.template_metrics = {}
        self.user_metrics = {}
        
        # Load existing analytics data
        self._load_analytics()
    
    def record_prompt_usage(self, 
                           prompt_id: str,
                           template_name: str,
                           user_id: Optional[str],
                           task_category: str,
                           prompt_text: str,
                           token_count: int,
                           metadata: Dict[str, Any] = None):
        """
        Record usage of a prompt for analytics.
        
        Args:
            prompt_id: Unique identifier for the prompt instance
            template_name: Name of the template used
            user_id: Unique identifier for the user (optional)
            task_category: Category of the task
            prompt_text: Full text of the prompt
            token_count: Number of tokens in the prompt
            metadata: Additional metadata about the prompt usage
        """
        # Default values
        metadata = metadata or {}
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Create prompt usage record
        usage_record = {
            "prompt_id": prompt_id,
            "template_name": template_name,
            "user_id": user_id,
            "task_category": task_category,
            "token_count": token_count,
            "timestamp": timestamp,
            "metadata": metadata
        }
        
        # Store in prompt metrics
        self.prompt_metrics[prompt_id] = usage_record
        
        # Update template metrics
        if template_name not in self.template_metrics:
            self.template_metrics[template_name] = {
                "usage_count": 0,
                "total_tokens": 0,
                "token_counts": [],
                "task_categories": {},
                "last_used": None
            }
        
        template_stats = self.template_metrics[template_name]
        template_stats["usage_count"] += 1
        template_stats["total_tokens"] += token_count
        template_stats["token_counts"].append(token_count)
        template_stats["last_used"] = timestamp
        
        # Update task category count
        if task_category not in template_stats["task_categories"]:
            template_stats["task_categories"][task_category] = 0
        template_stats["task_categories"][task_category] += 1
        
        # Update user metrics if user_id provided
        if user_id:
            if user_id not in self.user_metrics:
                self.user_metrics[user_id] = {
                    "total_prompts": 0,
                    "total_tokens": 0,
                    "templates_used": {},
                    "task_categories": {},
                    "first_seen": timestamp,
                    "last_seen": timestamp
                }
            
            user_stats = self.user_metrics[user_id]
            user_stats["total_prompts"] += 1
            user_stats["total_tokens"] += token_count
            user_stats["last_seen"] = timestamp
            
            # Update templates used
            if template_name not in user_stats["templates_used"]:
                user_stats["templates_used"][template_name] = 0
            user_stats["templates_used"][template_name] += 1
            
            # Update task categories
            if task_category not in user_stats["task_categories"]:
                user_stats["task_categories"][task_category] = 0
            user_stats["task_categories"][task_category] += 1
        
        # Save analytics data periodically
        # In a production system, this would be more sophisticated with batching
        self._save_analytics()
        
        logger.info(f"Recorded prompt usage: {prompt_id}, template: {template_name}, tokens: {token_count}")
    
    def record_prompt_performance(self,
                                 prompt_id: str,
                                 success: bool,
                                 response_time: float,
                                 completion_time: Optional[float] = None,
                                 user_rating: Optional[int] = None,
                                 error_type: Optional[str] = None,
                                 metadata: Dict[str, Any] = None):
        """
        Record performance metrics for a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt instance
            success: Whether the prompt was successful
            response_time: Time to first response in seconds
            completion_time: Time to complete the entire task in seconds (optional)
            user_rating: User satisfaction rating (1-5) (optional)
            error_type: Type of error if unsuccessful (optional)
            metadata: Additional metadata about the performance
        """
        # Default values
        metadata = metadata or {}
        
        # Check if prompt exists
        if prompt_id not in self.prompt_metrics:
            logger.warning(f"Prompt ID {prompt_id} not found in metrics")
            return
        
        # Get prompt record
        prompt_record = self.prompt_metrics[prompt_id]
        
        # Add performance metrics
        prompt_record["success"] = success
        prompt_record["response_time"] = response_time
        
        if completion_time is not None:
            prompt_record["completion_time"] = completion_time
        
        if user_rating is not None:
            prompt_record["user_rating"] = user_rating
        
        if error_type is not None:
            prompt_record["error_type"] = error_type
        
        # Add performance metadata
        if "performance_metadata" not in prompt_record:
            prompt_record["performance_metadata"] = {}
        
        prompt_record["performance_metadata"].update(metadata)
        
        # Update template metrics
        template_name = prompt_record["template_name"]
        if template_name in self.template_metrics:
            template_stats = self.template_metrics[template_name]
            
            # Update success count
            if "success_count" not in template_stats:
                template_stats["success_count"] = 0
            if success:
                template_stats["success_count"] += 1
            
            # Update response times
            if "response_times" not in template_stats:
                template_stats["response_times"] = []
            template_stats["response_times"].append(response_time)
            
            # Update completion times
            if completion_time is not None:
                if "completion_times" not in template_stats:
                    template_stats["completion_times"] = []
                template_stats["completion_times"].append(completion_time)
            
            # Update user ratings
            if user_rating is not None:
                if "user_ratings" not in template_stats:
                    template_stats["user_ratings"] = []
                template_stats["user_ratings"].append(user_rating)
            
            # Update error types
            if not success and error_type is not None:
                if "error_types" not in template_stats:
                    template_stats["error_types"] = {}
                if error_type not in template_stats["error_types"]:
                    template_stats["error_types"][error_type] = 0
                template_stats["error_types"][error_type] += 1
        
        # Update user metrics if user_id provided
        user_id = prompt_record.get("user_id")
        if user_id and user_id in self.user_metrics:
            user_stats = self.user_metrics[user_id]
            
            # Update success count
            if "success_count" not in user_stats:
                user_stats["success_count"] = 0
            if success:
                user_stats["success_count"] += 1
            
            # Update response times
            if "response_times" not in user_stats:
                user_stats["response_times"] = []
            user_stats["response_times"].append(response_time)
            
            # Update completion times
            if completion_time is not None:
                if "completion_times" not in user_stats:
                    user_stats["completion_times"] = []
                user_stats["completion_times"].append(completion_time)
            
            # Update user ratings
            if user_rating is not None:
                if "user_ratings" not in user_stats:
                    user_stats["user_ratings"] = []
                user_stats["user_ratings"].append(user_rating)
        
        # Save analytics data
        self._save_analytics()
        
        logger.info(f"Recorded prompt performance: {prompt_id}, success: {success}, response time: {response_time}")
    
    def get_template_performance(self, template_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dictionary of performance metrics
        """
        if template_name not in self.template_metrics:
            logger.warning(f"Template {template_name} not found in metrics")
            return {}
        
        template_stats = self.template_metrics[template_name]
        
        # Calculate derived metrics
        metrics = {
            "usage_count": template_stats["usage_count"],
            "total_tokens": template_stats["total_tokens"],
            "avg_tokens": statistics.mean(template_stats["token_counts"]) if template_stats["token_counts"] else 0,
            "last_used": template_stats["last_used"]
        }
        
        # Add success rate if available
        if "success_count" in template_stats:
            metrics["success_rate"] = template_stats["success_count"] / template_stats["usage_count"]
        
        # Add average response time if available
        if "response_times" in template_stats and template_stats["response_times"]:
            metrics["avg_response_time"] = statistics.mean(template_stats["response_times"])
        
        # Add average completion time if available
        if "completion_times" in template_stats and template_stats["completion_times"]:
            metrics["avg_completion_time"] = statistics.mean(template_stats["completion_times"])
        
        # Add average user rating if available
        if "user_ratings" in template_stats and template_stats["user_ratings"]:
            metrics["avg_user_rating"] = statistics.mean(template_stats["user_ratings"])
        
        # Add most common task categories
        metrics["top_task_categories"] = sorted(
            template_stats["task_categories"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Add most common error types if available
        if "error_types" in template_stats:
            metrics["top_error_types"] = sorted(
                template_stats["error_types"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        
        return metrics
    
    def get_user_performance(self, user_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary of performance metrics
        """
        if user_id not in self.user_metrics:
            logger.warning(f"User {user_id} not found in metrics")
            return {}
        
        user_stats = self.user_metrics[user_id]
        
        # Calculate derived metrics
        metrics = {
            "total_prompts": user_stats["total_prompts"],
            "total_tokens": user_stats["total_tokens"],
            "avg_tokens_per_prompt": user_stats["total_tokens"] / user_stats["total_prompts"] if user_stats["total_prompts"] > 0 else 0,
            "first_seen": user_stats["first_seen"],
            "last_seen": user_stats["last_seen"]
        }
        
        # Add success rate if available
        if "success_count" in user_stats:
            metrics["success_rate"] = user_stats["success_count"] / user_stats["total_prompts"]
        
        # Add average response time if available
        if "response_times" in user_stats and user_stats["response_times"]:
            metrics["avg_response_time"] = statistics.mean(user_stats["response_times"])
        
        # Add average completion time if available
        if "completion_times" in user_stats and user_stats["completion_times"]:
            metrics["avg_completion_time"] = statistics.mean(user_stats["completion_times"])
        
        # Add average user rating if available
        if "user_ratings" in user_stats and user_stats["user_ratings"]:
            metrics["avg_user_rating"] = statistics.mean(user_stats["user_ratings"])
        
        # Add most used templates
        metrics["top_templates"] = sorted(
            user_stats["templates_used"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Add most common task categories
        metrics["top_task_categories"] = sorted(
            user_stats["task_categories"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return metrics
    
    def get_optimization_recommendations(self, template_name: str = None) -> List[Dict[str, Any]]:
        """
        Get recommendations for optimizing prompts.
        
        Args:
            template_name: Name of the template to get recommendations for (optional)
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # If template name provided, get recommendations for that template
        if template_name:
            if template_name not in self.template_metrics:
                logger.warning(f"Template {template_name} not found in metrics")
                return []
            
            template_stats = self.template_metrics[template_name]
            recommendations.extend(self._get_template_recommendations(template_name, template_stats))
        
        # Otherwise, get recommendations for all templates
        else:
            # Sort templates by usage count
            sorted_templates = sorted(
                self.template_metrics.items(),
                key=lambda x: x[1]["usage_count"],
                reverse=True
            )
            
            # Get recommendations for top 5 most used templates
            for template_name, template_stats in sorted_templates[:5]:
                recommendations.extend(self._get_template_recommendations(template_name, template_stats))
        
        return recommendations
    
    def _get_template_recommendations(self, template_name: str, template_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get optimization recommendations for a specific template.
        
        Args:
            template_name: Name of the template
            template_stats: Statistics for the template
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Check token usage
        if "token_counts" in template_stats and template_stats["token_counts"]:
            avg_tokens = statistics.mean(template_stats["token_counts"])
            if avg_tokens > 500:
                recommendations.append({
                    "template": template_name,
                    "type": "token_reduction",
                    "priority": "high",
                    "description": f"High token usage (avg: {avg_tokens:.1f}). Consider reducing prompt length.",
                    "potential_savings": f"{int(avg_tokens * 0.3)} tokens per prompt"
                })
        
        # Check success rate
        if "success_count" in template_stats:
            success_rate = template_stats["success_count"] / template_stats["usage_count"]
            if success_rate < 0.8:
                recommendations.append({
                    "template": template_name,
                    "type": "success_improvement",
                    "priority": "high",
                    "description": f"Low success rate ({success_rate:.1%}). Consider revising prompt structure.",
                    "potential_improvement": f"{int((0.9 - success_rate) * 100)}% increase in success rate"
                })
        
        # Check response time
        if "response_times" in template_stats and template_stats["response_times"]:
            avg_response_time = statistics.mean(template_stats["response_times"])
            if avg_response_time > 5.0:
                recommendations.append({
                    "template": template_name,
                    "type": "response_time_improvement",
                    "priority": "medium",
                    "description": f"Slow response time (avg: {avg_response_time:.1f}s). Consider simplifying prompt.",
                    "potential_improvement": f"{int(avg_response_time * 0.3)}s faster response"
                })
        
        # Check user ratings
        if "user_ratings" in template_stats and template_stats["user_ratings"]:
            avg_rating = statistics.mean(template_stats["user_ratings"])
            if avg_rating < 4.0:
                recommendations.append({
                    "template": template_name,
                    "type": "quality_improvement",
                    "priority": "high",
                    "description": f"Low user satisfaction (avg rating: {avg_rating:.1f}/5). Consider improving prompt quality.",
                    "potential_improvement": "Increased user satisfaction"
                })
        
        # Check error types
        if "error_types" in template_stats and template_stats["error_types"]:
            most_common_error = max(template_stats["error_types"].items(), key=lambda x: x[1])
            error_type, error_count = most_common_error
            error_rate = error_count / template_stats["usage_count"]
            
            if error_rate > 0.1:
                recommendations.append({
                    "template": template_name,
                    "type": "error_reduction",
                    "priority": "high",
                    "description": f"High rate of '{error_type}' errors ({error_rate:.1%}). Consider addressing this specific issue.",
                    "potential_improvement": f"Reduction in {error_type} errors"
                })
        
        return recommendations
    
    def _load_analytics(self):
        """Load analytics data from disk."""
        # Load prompt metrics
        prompt_metrics_path = os.path.join(self.analytics_dir, "prompt_metrics.json")
        if os.path.exists(prompt_metrics_path):
            try:
                with open(prompt_metrics_path, 'r') as f:
                    self.prompt_metrics = json.load(f)
                logger.info(f"Loaded {len(self.prompt_metrics)} prompt metrics")
            except Exception as e:
                logger.error(f"Error loading prompt metrics: {str(e)}")
        
        # Load template metrics
        template_metrics_path = os.path.join(self.analytics_dir, "template_metrics.json")
        if os.path.exists(template_metrics_path):
            try:
                with open(template_metrics_path, 'r') as f:
                    self.template_metrics = json.load(f)
                logger.info(f"Loaded {len(self.template_metrics)} template metrics")
            except Exception as e:
                logger.error(f"Error loading template metrics: {str(e)}")
        
        # Load user metrics
        user_metrics_path = os.path.join(self.analytics_dir, "user_metrics.json")
        if os.path.exists(user_metrics_path):
            try:
                with open(user_metrics_path, 'r') as f:
                    self.user_metrics = json.load(f)
                logger.info(f"Loaded {len(self.user_metrics)} user metrics")
            except Exception as e:
                logger.error(f"Error loading user metrics: {str(e)}")
    
    def _save_analytics(self):
        """Save analytics data to disk."""
        # Save prompt metrics
        prompt_metrics_path = os.path.join(self.analytics_dir, "prompt_metrics.json")
        try:
            with open(prompt_metrics_path, 'w') as f:
                json.dump(self.prompt_metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving prompt metrics: {str(e)}")
        
        # Save template metrics
        template_metrics_path = os.path.join(self.analytics_dir, "template_metrics.json")
        try:
            with open(template_metrics_path, 'w') as f:
                json.dump(self.template_metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving template metrics: {str(e)}")
        
        # Save user metrics
        user_metrics_path = os.path.join(self.analytics_dir, "user_metrics.json")
        try:
            with open(user_metrics_path, 'w') as f:
                json.dump(self.user_metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user metrics: {str(e)}")
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics report.
        
        Returns:
            Dictionary containing analytics report data
        """
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "summary": {
                "total_prompts": len(self.prompt_metrics),
                "total_templates": len(self.template_metrics),
                "total_users": len(self.user_metrics),
                "total_tokens": sum(prompt.get("token_count", 0) for prompt in self.prompt_metrics.values())
            },
            "template_performance": {},
            "user_performance": {},
            "optimization_recommendations": self.get_optimization_recommendations()
        }
        
        # Add template performance metrics
        for template_name in self.template_metrics:
            report["template_performance"][template_name] = self.get_template_performance(template_name)
        
        # Add user performance metrics (limited to top 10 users by prompt count)
        top_users = sorted(
            self.user_metrics.items(),
            key=lambda x: x[1]["total_prompts"],
            reverse=True
        )[:10]
        
        for user_id, _ in top_users:
            report["user_performance"][user_id] = self.get_user_performance(user_id)
        
        return report
