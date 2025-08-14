"""
Integration tests for the Aideon AI Lite prompt engineering system.
This module provides comprehensive integration tests to ensure all components
work together seamlessly in real-world scenarios.
"""

import unittest
import os
import json
import tempfile
import shutil
import time
from unittest.mock import patch, MagicMock

# Import prompt engineering system
from ..prompt_engineering_system import PromptEngineeringSystem

class TestPromptEngineeringIntegration(unittest.TestCase):
    """Integration tests for the prompt engineering system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create prompt engineering system
        self.system = PromptEngineeringSystem(self.temp_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow with all components."""
        # 1. Create a user template
        template_id = self.system.create_user_template(
            user_id="test_user",
            template_name="Custom Coding Template",
            template_content="Write a {{language}} function to {{task_description}}. Include comments and error handling.",
            description="Template for coding tasks",
            task_category="coding",
            variables=[
                {"name": "language", "description": "Programming language", "default": "Python"},
                {"name": "task_description", "description": "Description of the coding task", "default": ""}
            ],
            is_public=True
        )
        
        # 2. Generate a conversation starter
        starter_result = self.system.generate_conversation_starter(
            scenario="coding",
            user_id="test_user",
            task_category="software_development",
            user_preferences={
                "intelligence_level": "Expert",
                "project": "Algorithm Library"
            }
        )
        
        self.assertTrue(starter_result["success"])
        self.assertIn("Algorithm Library", starter_result["starter"])
        
        # 3. Generate a prompt using the custom template
        prompt_result = self.system.generate_prompt(
            task_type="coding",
            task_description="calculate factorial recursively",
            user_id="test_user",
            template_id=template_id,
            parameters={"language": "JavaScript"}
        )
        
        self.assertTrue(prompt_result["success"])
        self.assertIn("JavaScript", prompt_result["prompt"])
        self.assertIn("factorial", prompt_result["prompt"])
        
        prompt_id = prompt_result["prompt_id"]
        
        # 4. Record prompt feedback
        self.system.record_prompt_feedback(
            prompt_id=prompt_id,
            success=True,
            completion_time=15.0,
            user_rating=4
        )
        
        # 5. Generate another prompt without custom template
        prompt_result2 = self.system.generate_prompt(
            task_type="data_analysis",
            task_description="analyze sales data and create visualizations",
            user_id="test_user"
        )
        
        self.assertTrue(prompt_result2["success"])
        self.assertIn("sales data", prompt_result2["prompt"])
        self.assertIn("visualization", prompt_result2["prompt"].lower())
        
        # 6. Get optimization recommendations
        recommendations = self.system.get_optimization_recommendations()
        self.assertIsInstance(recommendations, list)
        
        # 7. Generate analytics report
        report = self.system.generate_analytics_report()
        
        self.assertIn("summary", report)
        self.assertIn("template_performance", report)
        self.assertEqual(report["summary"]["total_prompts"], 2)
        
        # 8. List user templates
        templates = self.system.list_user_templates("test_user")
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]["template_id"], template_id)
        
        # 9. List shared templates
        shared_templates = self.system.list_shared_templates("coding")
        self.assertEqual(len(shared_templates), 1)
        self.assertEqual(shared_templates[0]["template_id"], template_id)
    
    def test_error_handling(self):
        """Test error handling in the prompt engineering system."""
        # Test with invalid template ID
        prompt_result = self.system.generate_prompt(
            task_type="coding",
            task_description="calculate factorial",
            user_id="test_user",
            template_id="nonexistent_template"
        )
        
        # Should fall back to system templates and still succeed
        self.assertTrue(prompt_result["success"])
        self.assertIn("factorial", prompt_result["prompt"])
        
        # Test with invalid user ID for templates
        templates = self.system.list_user_templates("nonexistent_user")
        self.assertEqual(templates, [])
        
        # Test recording feedback for nonexistent prompt
        self.system.record_prompt_feedback(
            prompt_id="nonexistent_prompt",
            success=False,
            error_type="not_found"
        )
        
        # Should not raise an exception
        
        # Test with empty task description
        prompt_result = self.system.generate_prompt(
            task_type="coding",
            task_description=""
        )
        
        # Should still generate a prompt
        self.assertTrue(prompt_result["success"])
    
    def test_performance_under_load(self):
        """Test performance under load."""
        start_time = time.time()
        
        # Generate multiple prompts in sequence
        for i in range(10):
            prompt_result = self.system.generate_prompt(
                task_type="coding",
                task_description=f"Task {i}: Write a function to calculate the {i}th Fibonacci number",
                user_id=f"user_{i % 3}"  # Simulate 3 different users
            )
            
            self.assertTrue(prompt_result["success"])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check that total time is reasonable (less than 5 seconds)
        self.assertLess(total_time, 5.0)
        
        # Generate analytics report
        report = self.system.generate_analytics_report()
        
        # Check that all prompts were recorded
        self.assertEqual(report["summary"]["total_prompts"], 10)
        
        # Check that all users were recorded
        self.assertEqual(len(report["user_performance"]), 3)
    
    def test_template_variables_substitution(self):
        """Test template variables substitution."""
        # Create a template with multiple variables
        template_id = self.system.create_user_template(
            user_id="test_user",
            template_name="Multi-Variable Template",
            template_content="Create a {{format}} about {{topic}} for {{audience}} with a {{tone}} tone.",
            description="Template with multiple variables",
            task_category="content_creation",
            variables=[
                {"name": "format", "description": "Content format", "default": "blog post"},
                {"name": "topic", "description": "Content topic", "default": "technology"},
                {"name": "audience", "description": "Target audience", "default": "general readers"},
                {"name": "tone", "description": "Content tone", "default": "informative"}
            ],
            is_public=True
        )
        
        # Generate a prompt with all variables specified
        prompt_result = self.system.generate_prompt(
            task_type="content_creation",
            task_description="Create content about artificial intelligence",
            user_id="test_user",
            template_id=template_id,
            parameters={
                "format": "video script",
                "topic": "artificial intelligence",
                "audience": "technology enthusiasts",
                "tone": "enthusiastic"
            }
        )
        
        self.assertTrue(prompt_result["success"])
        self.assertIn("video script", prompt_result["prompt"])
        self.assertIn("artificial intelligence", prompt_result["prompt"])
        self.assertIn("technology enthusiasts", prompt_result["prompt"])
        self.assertIn("enthusiastic", prompt_result["prompt"])
        
        # Generate a prompt with some variables using defaults
        prompt_result = self.system.generate_prompt(
            task_type="content_creation",
            task_description="Create content about space exploration",
            user_id="test_user",
            template_id=template_id,
            parameters={
                "topic": "space exploration",
                "audience": "science students"
            }
        )
        
        self.assertTrue(prompt_result["success"])
        self.assertIn("blog post", prompt_result["prompt"])  # Default value
        self.assertIn("space exploration", prompt_result["prompt"])
        self.assertIn("science students", prompt_result["prompt"])
        self.assertIn("informative", prompt_result["prompt"])  # Default value


if __name__ == "__main__":
    unittest.main()
