"""
Unit tests for the Aideon AI Lite prompt engineering system.
This module provides comprehensive tests for all components of the prompt engineering system.
"""

import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import prompt engineering components
from ..enhanced_architecture import ModularPromptArchitecture
from ..template_library import TemplateLibrary
from ..prompt_construction import PromptConstructionEngine
from ..conversation_starters import ConversationStarter
from ..prompt_analytics import PromptAnalytics
from ..user_template_manager import UserTemplateManager
from ..prompt_engineering_system import PromptEngineeringSystem

class TestModularPromptArchitecture(unittest.TestCase):
    """Tests for the ModularPromptArchitecture class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.architecture = ModularPromptArchitecture()
    
    def test_create_xml_structure(self):
        """Test creating XML structure."""
        components = {
            "system": "System instructions",
            "task": "Task description",
            "context": "Context information",
            "examples": ["Example 1", "Example 2"],
            "constraints": ["Constraint 1", "Constraint 2"]
        }
        
        result = self.architecture.create_xml_structure(components)
        
        # Check that all components are included
        self.assertIn("<system>", result)
        self.assertIn("System instructions", result)
        self.assertIn("<task>", result)
        self.assertIn("Task description", result)
        self.assertIn("<context>", result)
        self.assertIn("Context information", result)
        self.assertIn("<examples>", result)
        self.assertIn("Example 1", result)
        self.assertIn("Example 2", result)
        self.assertIn("<constraints>", result)
        self.assertIn("Constraint 1", result)
        self.assertIn("Constraint 2", result)
    
    def test_parse_xml_structure(self):
        """Test parsing XML structure."""
        xml_prompt = """
        <prompt>
            <system>System instructions</system>
            <task>Task description</task>
            <context>Context information</context>
            <examples>
                <example>Example 1</example>
                <example>Example 2</example>
            </examples>
            <constraints>
                <constraint>Constraint 1</constraint>
                <constraint>Constraint 2</constraint>
            </constraints>
        </prompt>
        """
        
        result = self.architecture.parse_xml_structure(xml_prompt)
        
        # Check that all components are extracted correctly
        self.assertEqual(result["system"], "System instructions")
        self.assertEqual(result["task"], "Task description")
        self.assertEqual(result["context"], "Context information")
        self.assertEqual(result["examples"], ["Example 1", "Example 2"])
        self.assertEqual(result["constraints"], ["Constraint 1", "Constraint 2"])
    
    def test_optimize_prompt_structure(self):
        """Test optimizing prompt structure."""
        components = {
            "system": "System instructions",
            "task": "Task description",
            "context": "Context information",
            "examples": ["Example 1", "Example 2"],
            "constraints": ["Constraint 1", "Constraint 2"]
        }
        
        result = self.architecture.optimize_prompt_structure(components, "coding")
        
        # Check that the result is a string
        self.assertIsInstance(result, str)
        
        # Check that all components are included
        self.assertIn("System instructions", result)
        self.assertIn("Task description", result)
        self.assertIn("Context information", result)
        self.assertIn("Example 1", result)
        self.assertIn("Example 2", result)
        self.assertIn("Constraint 1", result)
        self.assertIn("Constraint 2", result)


class TestTemplateLibrary(unittest.TestCase):
    """Tests for the TemplateLibrary class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.template_library = TemplateLibrary()
    
    def test_get_template(self):
        """Test getting a template."""
        # Test getting a template that exists
        template = self.template_library.get_template("general", "default")
        self.assertIsNotNone(template)
        self.assertIn("content", template)
        
        # Test getting a template that doesn't exist
        template = self.template_library.get_template("nonexistent", "nonexistent")
        self.assertIsNone(template)
    
    def test_list_templates(self):
        """Test listing templates."""
        templates = self.template_library.list_templates("general")
        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)
    
    def test_list_categories(self):
        """Test listing categories."""
        categories = self.template_library.list_categories()
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        self.assertIn("general", categories)


class TestPromptConstructionEngine(unittest.TestCase):
    """Tests for the PromptConstructionEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.template_library = TemplateLibrary()
        self.construction_engine = PromptConstructionEngine(self.template_library)
    
    def test_construct_prompt(self):
        """Test constructing a prompt."""
        result = self.construction_engine.construct_prompt(
            task_type="coding",
            task_description="Write a Python function to calculate factorial",
            parameters={"language": "python", "complexity": "medium"},
            context={"project": "Math Library", "previous_code": "def add(a, b): return a + b"}
        )
        
        # Check that the result contains expected keys
        self.assertIn("prompt", result)
        self.assertIn("template_name", result)
        self.assertIn("token_count", result)
        
        # Check that the prompt contains the task description
        self.assertIn("factorial", result["prompt"])
        
        # Check that the token count is reasonable
        self.assertGreater(result["token_count"], 0)
    
    def test_construct_prompt_with_custom_template(self):
        """Test constructing a prompt with a custom template."""
        custom_template = {
            "name": "custom_template",
            "content": "Custom template with {{task_description}} and {{parameters.language}}",
            "variables": ["task_description", "parameters.language"]
        }
        
        result = self.construction_engine.construct_prompt(
            task_type="coding",
            task_description="Write a Python function to calculate factorial",
            template=custom_template,
            parameters={"language": "python"}
        )
        
        # Check that the result contains expected keys
        self.assertIn("prompt", result)
        self.assertIn("template_name", result)
        self.assertIn("token_count", result)
        
        # Check that the custom template was used
        self.assertEqual(result["template_name"], "custom_template")
        self.assertIn("Custom template with", result["prompt"])
        self.assertIn("Write a Python function to calculate factorial", result["prompt"])
        self.assertIn("python", result["prompt"])


class TestConversationStarter(unittest.TestCase):
    """Tests for the ConversationStarter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.conversation_starter = ConversationStarter()
    
    def test_generate_starter(self):
        """Test generating a conversation starter."""
        # Test default scenario
        starter = self.conversation_starter.generate_starter()
        self.assertIsInstance(starter, str)
        self.assertIn("Initializing Aideon AI Lite", starter)
        
        # Test coding scenario
        starter = self.conversation_starter.generate_starter(scenario="coding")
        self.assertIsInstance(starter, str)
        self.assertIn("coding", starter.lower())
        
        # Test with user preferences
        starter = self.conversation_starter.generate_starter(
            user_preferences={
                "intelligence_level": "Expert",
                "verbosity": "Concise",
                "creativity": "Practical"
            }
        )
        self.assertIsInstance(starter, str)
        self.assertIn("Expert", starter)
        self.assertIn("Concise", starter)
        self.assertIn("Practical", starter)
    
    def test_save_user_preferences(self):
        """Test saving user preferences."""
        user_id = "test_user"
        preferences = {
            "intelligence_level": "Expert",
            "verbosity": "Concise",
            "creativity": "Practical"
        }
        
        # Save preferences
        self.conversation_starter.save_user_preferences(user_id, preferences)
        
        # Get preferences
        saved_preferences = self.conversation_starter.get_user_preferences(user_id)
        
        # Check that preferences were saved correctly
        self.assertEqual(saved_preferences["intelligence_level"], "Expert")
        self.assertEqual(saved_preferences["verbosity"], "Concise")
        self.assertEqual(saved_preferences["creativity"], "Practical")
        
        # Clear preferences
        self.conversation_starter.clear_user_preferences(user_id)
        
        # Check that preferences were cleared
        saved_preferences = self.conversation_starter.get_user_preferences(user_id)
        self.assertEqual(saved_preferences, {})


class TestPromptAnalytics(unittest.TestCase):
    """Tests for the PromptAnalytics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for analytics data
        self.temp_dir = tempfile.mkdtemp()
        self.analytics = PromptAnalytics(self.temp_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_record_prompt_usage(self):
        """Test recording prompt usage."""
        self.analytics.record_prompt_usage(
            prompt_id="test_prompt",
            template_name="test_template",
            user_id="test_user",
            task_category="coding",
            prompt_text="Test prompt",
            token_count=100
        )
        
        # Check that prompt was recorded
        self.assertIn("test_prompt", self.analytics.prompt_metrics)
        
        # Check that template was recorded
        self.assertIn("test_template", self.analytics.template_metrics)
        
        # Check that user was recorded
        self.assertIn("test_user", self.analytics.user_metrics)
    
    def test_record_prompt_performance(self):
        """Test recording prompt performance."""
        # Record prompt usage first
        self.analytics.record_prompt_usage(
            prompt_id="test_prompt",
            template_name="test_template",
            user_id="test_user",
            task_category="coding",
            prompt_text="Test prompt",
            token_count=100
        )
        
        # Record performance
        self.analytics.record_prompt_performance(
            prompt_id="test_prompt",
            success=True,
            response_time=1.5,
            completion_time=5.0,
            user_rating=4
        )
        
        # Check that performance was recorded
        prompt_record = self.analytics.prompt_metrics["test_prompt"]
        self.assertEqual(prompt_record["success"], True)
        self.assertEqual(prompt_record["response_time"], 1.5)
        self.assertEqual(prompt_record["completion_time"], 5.0)
        self.assertEqual(prompt_record["user_rating"], 4)
    
    def test_get_template_performance(self):
        """Test getting template performance."""
        # Record prompt usage and performance
        self.analytics.record_prompt_usage(
            prompt_id="test_prompt",
            template_name="test_template",
            user_id="test_user",
            task_category="coding",
            prompt_text="Test prompt",
            token_count=100
        )
        
        self.analytics.record_prompt_performance(
            prompt_id="test_prompt",
            success=True,
            response_time=1.5
        )
        
        # Get template performance
        performance = self.analytics.get_template_performance("test_template")
        
        # Check that performance metrics are correct
        self.assertEqual(performance["usage_count"], 1)
        self.assertEqual(performance["total_tokens"], 100)
        self.assertEqual(performance["avg_tokens"], 100)
        self.assertEqual(performance["success_rate"], 1.0)
        self.assertEqual(performance["avg_response_time"], 1.5)
    
    def test_get_optimization_recommendations(self):
        """Test getting optimization recommendations."""
        # Record prompt usage with high token count
        self.analytics.record_prompt_usage(
            prompt_id="test_prompt",
            template_name="test_template",
            user_id="test_user",
            task_category="coding",
            prompt_text="Test prompt",
            token_count=1000
        )
        
        # Record performance with low success rate
        self.analytics.record_prompt_performance(
            prompt_id="test_prompt",
            success=False,
            response_time=1.5,
            error_type="timeout"
        )
        
        # Get optimization recommendations
        recommendations = self.analytics.get_optimization_recommendations("test_template")
        
        # Check that recommendations were generated
        self.assertGreater(len(recommendations), 0)
        
        # Check that token reduction recommendation was generated
        token_recommendations = [r for r in recommendations if r["type"] == "token_reduction"]
        self.assertEqual(len(token_recommendations), 1)
        
        # Check that error reduction recommendation was generated
        error_recommendations = [r for r in recommendations if r["type"] == "error_reduction"]
        self.assertEqual(len(error_recommendations), 1)


class TestUserTemplateManager(unittest.TestCase):
    """Tests for the UserTemplateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        self.template_manager = UserTemplateManager(self.temp_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_create_template(self):
        """Test creating a template."""
        template_id = self.template_manager.create_template(
            user_id="test_user",
            template_name="Test Template",
            template_content="Test content with {{variable}}",
            description="Test description",
            task_category="coding",
            variables=[{"name": "variable", "description": "Test variable", "default": "default value"}],
            is_public=True
        )
        
        # Check that template was created
        self.assertIn("test_user", self.template_manager.user_templates)
        self.assertIn(template_id, self.template_manager.user_templates["test_user"])
        
        # Check that template is public
        self.assertIn(template_id, self.template_manager.shared_templates)
    
    def test_update_template(self):
        """Test updating a template."""
        # Create template
        template_id = self.template_manager.create_template(
            user_id="test_user",
            template_name="Test Template",
            template_content="Test content",
            description="Test description",
            task_category="coding",
            variables=[],
            is_public=False
        )
        
        # Update template
        success = self.template_manager.update_template(
            template_id=template_id,
            user_id="test_user",
            template_name="Updated Template",
            template_content="Updated content",
            is_public=True
        )
        
        # Check that update was successful
        self.assertTrue(success)
        
        # Check that template was updated
        template = self.template_manager.get_template(template_id, "test_user")
        self.assertEqual(template["template_name"], "Updated Template")
        self.assertEqual(template["template_content"], "Updated content")
        
        # Check that template is now public
        self.assertIn(template_id, self.template_manager.shared_templates)
    
    def test_delete_template(self):
        """Test deleting a template."""
        # Create template
        template_id = self.template_manager.create_template(
            user_id="test_user",
            template_name="Test Template",
            template_content="Test content",
            description="Test description",
            task_category="coding",
            variables=[],
            is_public=True
        )
        
        # Delete template
        success = self.template_manager.delete_template(template_id, "test_user")
        
        # Check that deletion was successful
        self.assertTrue(success)
        
        # Check that template was deleted from user templates
        self.assertNotIn(template_id, self.template_manager.user_templates["test_user"])
        
        # Check that template was deleted from shared templates
        self.assertNotIn(template_id, self.template_manager.shared_templates)
    
    def test_list_user_templates(self):
        """Test listing user templates."""
        # Create templates
        self.template_manager.create_template(
            user_id="test_user",
            template_name="Template 1",
            template_content="Content 1",
            description="Description 1",
            task_category="coding",
            variables=[],
            is_public=False
        )
        
        self.template_manager.create_template(
            user_id="test_user",
            template_name="Template 2",
            template_content="Content 2",
            description="Description 2",
            task_category="data_analysis",
            variables=[],
            is_public=True
        )
        
        # List templates
        templates = self.template_manager.list_user_templates("test_user")
        
        # Check that both templates are listed
        self.assertEqual(len(templates), 2)
        template_names = [t["template_name"] for t in templates]
        self.assertIn("Template 1", template_names)
        self.assertIn("Template 2", template_names)
    
    def test_list_shared_templates(self):
        """Test listing shared templates."""
        # Create templates
        self.template_manager.create_template(
            user_id="test_user",
            template_name="Template 1",
            template_content="Content 1",
            description="Description 1",
            task_category="coding",
            variables=[],
            is_public=True
        )
        
        self.template_manager.create_template(
            user_id="test_user",
            template_name="Template 2",
            template_content="Content 2",
            description="Description 2",
            task_category="data_analysis",
            variables=[],
            is_public=True
        )
        
        # List all shared templates
        templates = self.template_manager.list_shared_templates()
        self.assertEqual(len(templates), 2)
        
        # List shared templates filtered by category
        templates = self.template_manager.list_shared_templates("coding")
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]["template_name"], "Template 1")


class TestPromptEngineeringSystem(unittest.TestCase):
    """Tests for the PromptEngineeringSystem class."""
    
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
    
    def test_generate_prompt(self):
        """Test generating a prompt."""
        result = self.system.generate_prompt(
            task_type="coding",
            task_description="Write a Python function to calculate factorial",
            parameters={"language": "python"}
        )
        
        # Check that result contains expected keys
        self.assertIn("prompt_id", result)
        self.assertIn("prompt", result)
        self.assertIn("template_name", result)
        self.assertIn("token_count", result)
        self.assertIn("success", result)
        self.assertIn("response_time", result)
        
        # Check that prompt was successful
        self.assertTrue(result["success"])
        
        # Check that prompt contains task description
        self.assertIn("factorial", result["prompt"])
    
    def test_generate_conversation_starter(self):
        """Test generating a conversation starter."""
        result = self.system.generate_conversation_starter(
            scenario="coding",
            task_category="software_development",
            user_preferences={"intelligence_level": "Expert"}
        )
        
        # Check that result contains expected keys
        self.assertIn("prompt_id", result)
        self.assertIn("starter", result)
        self.assertIn("scenario", result)
        self.assertIn("token_count", result)
        self.assertIn("success", result)
        self.assertIn("response_time", result)
        
        # Check that starter was successful
        self.assertTrue(result["success"])
        
        # Check that starter contains expected content
        self.assertIn("coding", result["starter"].lower())
        self.assertIn("Expert", result["starter"])
    
    def test_record_prompt_feedback(self):
        """Test recording prompt feedback."""
        # Generate prompt
        prompt_result = self.system.generate_prompt(
            task_type="coding",
            task_description="Write a Python function to calculate factorial"
        )
        
        prompt_id = prompt_result["prompt_id"]
        
        # Record feedback
        self.system.record_prompt_feedback(
            prompt_id=prompt_id,
            success=True,
            completion_time=10.0,
            user_rating=5
        )
        
        # Generate analytics report
        report = self.system.generate_analytics_report()
        
        # Check that report contains prompt
        self.assertGreaterEqual(report["summary"]["total_prompts"], 1)
    
    def test_create_user_template(self):
        """Test creating a user template."""
        template_id = self.system.create_user_template(
            user_id="test_user",
            template_name="Test Template",
            template_content="Test content with {{variable}}",
            description="Test description",
            task_category="coding",
            variables=[{"name": "variable", "description": "Test variable", "default": "default value"}],
            is_public=True
        )
        
        # List user templates
        templates = self.system.list_user_templates("test_user")
        
        # Check that template was created
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]["template_id"], template_id)
        
        # List shared templates
        shared_templates = self.system.list_shared_templates()
        
        # Check that template is shared
        self.assertEqual(len(shared_templates), 1)
        self.assertEqual(shared_templates[0]["template_id"], template_id)


if __name__ == "__main__":
    unittest.main()
