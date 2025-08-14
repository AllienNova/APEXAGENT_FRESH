"""
Unit tests for the Aideon AI Lite Prompt Engineering System.

This module contains comprehensive tests for all components of the
prompt engineering system, ensuring functionality, integration, and edge cases.
"""

import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import the modules to test
from src.prompt_engineering.templates.template_schema import (
    PromptTemplate, PromptSection, TemplateVariable,
    TaskType, ComplexityLevel, Domain, LLMProvider,
    ConversationStarter
)
from src.prompt_engineering.templates.template_library import TemplateLibrary
from src.prompt_engineering.prompt_construction_engine import PromptConstructionEngine
from src.prompt_engineering.conversation_starters import ConversationStarterLibrary
from src.prompt_engineering.prompt_analytics import (
    PromptAnalytics, PromptUsageRecord, PromptOutcomeType
)
from src.prompt_engineering.user_template_manager import UserTemplateManager
from src.prompt_engineering.prompt_engineering_system import PromptEngineeringSystem


class TestTemplateSchema(unittest.TestCase):
    """Tests for the template schema classes."""
    
    def test_prompt_template_creation(self):
        """Test creating a prompt template."""
        # Create a template
        template = PromptTemplate(
            id="test_template",
            name="Test Template",
            description="A test template",
            version="1.0.0",
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            sections=[
                PromptSection(
                    name="introduction",
                    content="This is an introduction.",
                    description="Introduces the task",
                    optional=False
                ),
                PromptSection(
                    name="instructions",
                    content="These are the instructions: {{instructions}}",
                    description="Provides instructions",
                    optional=False
                )
            ],
            variables=[
                TemplateVariable(
                    name="instructions",
                    description="The instructions to follow",
                    default_value="Follow these steps",
                    required=True
                )
            ],
            author="Test Author",
            tags=["test", "example"],
            created_at="2025-05-27T00:00:00",
            updated_at="2025-05-27T00:00:00",
            token_estimate=50,
            success_rate=0.95,
            is_system=True,
            compatible_providers=[LLMProvider.OPENAI, LLMProvider.ANTHROPIC]
        )
        
        # Check attributes
        self.assertEqual(template.id, "test_template")
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.task_type, TaskType.TEXT_GENERATION)
        self.assertEqual(len(template.sections), 2)
        self.assertEqual(len(template.variables), 1)
        self.assertEqual(template.variables[0].name, "instructions")
        self.assertEqual(template.success_rate, 0.95)
        
    def test_conversation_starter_creation(self):
        """Test creating a conversation starter."""
        # Create a starter
        starter = ConversationStarter(
            id="test_starter",
            name="Test Starter",
            description="A test starter",
            template="SYSTEM: Initializing Aideon AI Lite with {{intelligence_level}} intelligence.",
            domain_expertise=Domain.GENERAL,
            intelligence_level="Advanced",
            verbosity="Balanced",
            creativity="Creative",
            format_preference="Default",
            variables=[
                TemplateVariable(
                    name="intelligence_level",
                    description="The intelligence level",
                    default_value="Advanced",
                    required=True
                )
            ],
            is_system=True
        )
        
        # Check attributes
        self.assertEqual(starter.id, "test_starter")
        self.assertEqual(starter.name, "Test Starter")
        self.assertEqual(starter.domain_expertise, Domain.GENERAL)
        self.assertEqual(starter.intelligence_level, "Advanced")
        self.assertEqual(len(starter.variables), 1)
        self.assertEqual(starter.variables[0].name, "intelligence_level")


class TestTemplateLibrary(unittest.TestCase):
    """Tests for the template library."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a template library with the temp directory
        self.library = TemplateLibrary(templates_dir=self.temp_dir)
        
        # Create a test template
        self.test_template = PromptTemplate(
            id="test_template",
            name="Test Template",
            description="A test template",
            version="1.0.0",
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            sections=[
                PromptSection(
                    name="content",
                    content="This is a test template with {{variable}}.",
                    description="Main content",
                    optional=False
                )
            ],
            variables=[
                TemplateVariable(
                    name="variable",
                    description="A test variable",
                    default_value="default value",
                    required=True
                )
            ],
            author="Test Author",
            tags=["test"],
            created_at="2025-05-27T00:00:00",
            updated_at="2025-05-27T00:00:00",
            token_estimate=20,
            success_rate=0.9,
            is_system=True,
            compatible_providers=[LLMProvider.ANY]
        )
        
        # Save the test template
        template_path = os.path.join(self.temp_dir, "test_template.json")
        with open(template_path, "w") as f:
            json.dump(json.loads(self.test_template.json()), f)
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_load_templates(self):
        """Test loading templates from the directory."""
        # Load templates
        self.library.load_templates()
        
        # Check that the test template was loaded
        self.assertIn("test_template", self.library.templates)
        loaded_template = self.library.templates["test_template"]
        self.assertEqual(loaded_template.name, "Test Template")
        self.assertEqual(loaded_template.task_type, TaskType.TEXT_GENERATION)
    
    def test_get_template(self):
        """Test getting a template by ID."""
        # Load templates
        self.library.load_templates()
        
        # Get the test template
        template = self.library.get_template("test_template")
        self.assertIsNotNone(template)
        self.assertEqual(template.id, "test_template")
        
        # Try to get a non-existent template
        template = self.library.get_template("non_existent")
        self.assertIsNone(template)
    
    def test_list_templates(self):
        """Test listing templates with filtering."""
        # Load templates
        self.library.load_templates()
        
        # List all templates
        templates = self.library.list_templates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]["id"], "test_template")
        
        # Filter by task type
        templates = self.library.list_templates(task_type=TaskType.TEXT_GENERATION)
        self.assertEqual(len(templates), 1)
        
        templates = self.library.list_templates(task_type=TaskType.CODE_GENERATION)
        self.assertEqual(len(templates), 0)
        
        # Filter by complexity level
        templates = self.library.list_templates(complexity_level=ComplexityLevel.MEDIUM)
        self.assertEqual(len(templates), 1)
        
        templates = self.library.list_templates(complexity_level=ComplexityLevel.HIGH)
        self.assertEqual(len(templates), 0)
        
        # Filter by domain
        templates = self.library.list_templates(domain=Domain.GENERAL)
        self.assertEqual(len(templates), 1)
        
        templates = self.library.list_templates(domain=Domain.TECHNICAL)
        self.assertEqual(len(templates), 0)


class TestPromptConstructionEngine(unittest.TestCase):
    """Tests for the prompt construction engine."""
    
    def setUp(self):
        """Set up the test environment."""
        self.engine = PromptConstructionEngine()
        
        # Create a test template
        self.test_template = PromptTemplate(
            id="test_template",
            name="Test Template",
            description="A test template",
            version="1.0.0",
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            sections=[
                PromptSection(
                    name="introduction",
                    content="This is an introduction.",
                    description="Introduces the task",
                    optional=False
                ),
                PromptSection(
                    name="instructions",
                    content="These are the instructions: {{instructions}}",
                    description="Provides instructions",
                    optional=False
                ),
                PromptSection(
                    name="optional_section",
                    content="This is an optional section with {{optional_var}}.",
                    description="An optional section",
                    optional=True
                )
            ],
            variables=[
                TemplateVariable(
                    name="instructions",
                    description="The instructions to follow",
                    default_value="Follow these steps",
                    required=True
                ),
                TemplateVariable(
                    name="optional_var",
                    description="An optional variable",
                    default_value="default value",
                    required=False
                )
            ],
            author="Test Author",
            tags=["test"],
            created_at="2025-05-27T00:00:00",
            updated_at="2025-05-27T00:00:00",
            token_estimate=50,
            success_rate=0.9,
            is_system=True,
            compatible_providers=[LLMProvider.ANY]
        )
    
    def test_apply_variables(self):
        """Test applying variables to a template string."""
        # Test with a simple template
        template_str = "Hello, {{name}}!"
        variables = {"name": "World"}
        result = self.engine.apply_variables(template_str, variables)
        self.assertEqual(result, "Hello, World!")
        
        # Test with missing variable (should use empty string)
        template_str = "Hello, {{name}}!"
        variables = {}
        result = self.engine.apply_variables(template_str, variables)
        self.assertEqual(result, "Hello, !")
        
        # Test with multiple variables
        template_str = "{{greeting}}, {{name}}!"
        variables = {"greeting": "Hello", "name": "World"}
        result = self.engine.apply_variables(template_str, variables)
        self.assertEqual(result, "Hello, World!")
    
    def test_construct_prompt(self):
        """Test constructing a prompt from a template."""
        # Test with required variables
        variables = {"instructions": "Do this and that"}
        result = self.engine.construct_prompt(self.test_template, variables)
        expected = "This is an introduction.\nThese are the instructions: Do this and that\nThis is an optional section with default value."
        self.assertEqual(result, expected)
        
        # Test with all variables
        variables = {"instructions": "Do this and that", "optional_var": "custom value"}
        result = self.engine.construct_prompt(self.test_template, variables)
        expected = "This is an introduction.\nThese are the instructions: Do this and that\nThis is an optional section with custom value."
        self.assertEqual(result, expected)
        
        # Test with exclude_optional=True
        variables = {"instructions": "Do this and that"}
        result = self.engine.construct_prompt(self.test_template, variables, exclude_optional=True)
        expected = "This is an introduction.\nThese are the instructions: Do this and that"
        self.assertEqual(result, expected)
        
        # Test with missing required variable (should use default)
        variables = {}
        result = self.engine.construct_prompt(self.test_template, variables)
        expected = "This is an introduction.\nThese are the instructions: Follow these steps\nThis is an optional section with default value."
        self.assertEqual(result, expected)


class TestConversationStarterLibrary(unittest.TestCase):
    """Tests for the conversation starter library."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for starters
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a starter library with the temp directory
        self.library = ConversationStarterLibrary(starters_dir=self.temp_dir)
        
        # Create a test starter
        self.test_starter = ConversationStarter(
            id="test_starter",
            name="Test Starter",
            description="A test starter",
            template="SYSTEM: Initializing Aideon AI Lite with {{intelligence_level}} intelligence.",
            domain_expertise=Domain.GENERAL,
            intelligence_level="Advanced",
            verbosity="Balanced",
            creativity="Creative",
            format_preference="Default",
            variables=[
                TemplateVariable(
                    name="intelligence_level",
                    description="The intelligence level",
                    default_value="Advanced",
                    required=True
                )
            ],
            is_system=True
        )
        
        # Save the test starter
        starter_path = os.path.join(self.temp_dir, "test_starter.json")
        with open(starter_path, "w") as f:
            json.dump(json.loads(self.test_starter.json()), f)
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_load_starters(self):
        """Test loading starters from the directory."""
        # Load starters
        self.library.load_starters()
        
        # Check that the test starter was loaded
        self.assertIn("test_starter", self.library.starters)
        loaded_starter = self.library.starters["test_starter"]
        self.assertEqual(loaded_starter.name, "Test Starter")
        self.assertEqual(loaded_starter.domain_expertise, Domain.GENERAL)
    
    def test_get_starter(self):
        """Test getting a starter by ID."""
        # Load starters
        self.library.load_starters()
        
        # Get the test starter
        starter = self.library.get_starter("test_starter")
        self.assertIsNotNone(starter)
        self.assertEqual(starter.id, "test_starter")
        
        # Try to get a non-existent starter
        starter = self.library.get_starter("non_existent")
        self.assertIsNone(starter)
    
    def test_list_starters(self):
        """Test listing starters with filtering."""
        # Load starters
        self.library.load_starters()
        
        # List all starters
        starters = self.library.list_starters()
        self.assertEqual(len(starters), 1)
        self.assertEqual(starters[0]["id"], "test_starter")
        
        # Filter by domain expertise
        starters = self.library.list_starters(domain_expertise=Domain.GENERAL)
        self.assertEqual(len(starters), 1)
        
        starters = self.library.list_starters(domain_expertise=Domain.TECHNICAL)
        self.assertEqual(len(starters), 0)


class TestPromptAnalytics(unittest.TestCase):
    """Tests for the prompt analytics system."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for analytics data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create an analytics instance with the temp directory
        self.analytics = PromptAnalytics(analytics_dir=self.temp_dir)
        
        # Create a test record
        self.test_record = PromptUsageRecord(
            prompt_id="test_prompt_1",
            template_id="test_template",
            conversation_id="test_conversation",
            user_id="test_user",
            timestamp="2025-05-27T00:00:00",
            prompt_text="This is a test prompt.",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            duration_ms=500,
            outcome=PromptOutcomeType.SUCCESS,
            user_rating=4,
            user_feedback="Good response",
            llm_provider="openai",
            llm_model="gpt-4",
            task_type="text_generation",
            domain="general",
            complexity_level="medium"
        )
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_record_prompt_usage(self):
        """Test recording prompt usage."""
        # Record the test prompt usage
        self.analytics.record_prompt_usage(self.test_record)
        
        # Check that it was added to the cache
        self.assertEqual(len(self.analytics.record_cache), 1)
        self.assertEqual(self.analytics.record_cache[0].prompt_id, "test_prompt_1")
    
    def test_record_prompt_outcome(self):
        """Test recording prompt outcome."""
        # Record the test prompt usage
        self.analytics.record_prompt_usage(self.test_record)
        
        # Update the outcome
        self.analytics.record_prompt_outcome(
            prompt_id="test_prompt_1",
            outcome=PromptOutcomeType.PARTIAL_SUCCESS,
            completion_tokens=25,
            duration_ms=600
        )
        
        # Check that the outcome was updated
        self.assertEqual(self.analytics.record_cache[0].outcome, PromptOutcomeType.PARTIAL_SUCCESS)
        self.assertEqual(self.analytics.record_cache[0].completion_tokens, 25)
        self.assertEqual(self.analytics.record_cache[0].duration_ms, 600)
    
    def test_record_user_feedback(self):
        """Test recording user feedback."""
        # Record the test prompt usage
        self.analytics.record_prompt_usage(self.test_record)
        
        # Update the user feedback
        self.analytics.record_user_feedback(
            prompt_id="test_prompt_1",
            user_rating=5,
            user_feedback="Excellent response"
        )
        
        # Check that the feedback was updated
        self.assertEqual(self.analytics.record_cache[0].user_rating, 5)
        self.assertEqual(self.analytics.record_cache[0].user_feedback, "Excellent response")
    
    def test_calculate_template_metrics(self):
        """Test calculating template metrics."""
        # Record multiple prompt usages
        self.analytics.record_prompt_usage(self.test_record)
        
        # Create another record with different outcome
        record2 = PromptUsageRecord(
            prompt_id="test_prompt_2",
            template_id="test_template",
            conversation_id="test_conversation",
            user_id="test_user",
            timestamp="2025-05-27T00:01:00",
            prompt_text="This is another test prompt.",
            prompt_tokens=15,
            completion_tokens=25,
            total_tokens=40,
            duration_ms=600,
            outcome=PromptOutcomeType.FAILURE,
            user_rating=2,
            user_feedback="Poor response",
            llm_provider="openai",
            llm_model="gpt-4",
            task_type="text_generation",
            domain="general",
            complexity_level="medium"
        )
        self.analytics.record_prompt_usage(record2)
        
        # Calculate metrics for the template
        metrics = self.analytics._calculate_template_metrics(self.analytics.record_cache)
        
        # Check the metrics
        self.assertEqual(metrics["total_count"], 2)
        self.assertEqual(metrics["success_count"], 1)
        self.assertEqual(metrics["failure_count"], 1)
        self.assertEqual(metrics["success_rate"], 0.5)
        self.assertEqual(metrics["avg_prompt_tokens"], 12.5)
        self.assertEqual(metrics["avg_completion_tokens"], 22.5)
        self.assertEqual(metrics["avg_total_tokens"], 35)
        self.assertEqual(metrics["avg_duration_ms"], 550)
        self.assertEqual(metrics["avg_user_rating"], 3)
        self.assertEqual(metrics["rating_count"], 2)


class TestUserTemplateManager(unittest.TestCase):
    """Tests for the user template manager."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for user templates
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a user template manager with the temp directory
        self.manager = UserTemplateManager(user_templates_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_prompt_template(self):
        """Test creating a user prompt template."""
        # Create a user template
        template = self.manager.create_prompt_template(
            name="User Template",
            description="A user template",
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            sections=[
                {
                    "name": "content",
                    "content": "This is a user template with {{variable}}.",
                    "description": "Main content",
                    "optional": False
                }
            ],
            variables=[
                {
                    "name": "variable",
                    "description": "A test variable",
                    "default_value": "default value",
                    "required": True
                }
            ],
            author="Test User",
            tags=["user", "test"],
            user_id="test_user"
        )
        
        # Check that the template was created
        self.assertIsNotNone(template)
        self.assertTrue(template.id.startswith("user_"))
        self.assertEqual(template.name, "User Template")
        self.assertEqual(template.task_type, TaskType.TEXT_GENERATION)
        
        # Check that it was added to the cache
        self.assertIn(template.id, self.manager.prompt_templates)
        
        # Check that it was saved to file
        template_path = os.path.join(self.manager.prompt_templates_dir, f"{template.id}.json")
        self.assertTrue(os.path.exists(template_path))
    
    def test_create_conversation_starter(self):
        """Test creating a user conversation starter."""
        # Create a user starter
        starter = self.manager.create_conversation_starter(
            name="User Starter",
            description="A user starter",
            template="SYSTEM: Initializing Aideon AI Lite with {{intelligence_level}} intelligence.",
            domain_expertise=Domain.GENERAL,
            intelligence_level="Advanced",
            verbosity="Balanced",
            creativity="Creative",
            format_preference="Default",
            variables=[
                {
                    "name": "intelligence_level",
                    "description": "The intelligence level",
                    "default_value": "Advanced",
                    "required": True
                }
            ],
            author="Test User",
            user_id="test_user"
        )
        
        # Check that the starter was created
        self.assertIsNotNone(starter)
        self.assertTrue(starter.id.startswith("user_"))
        self.assertEqual(starter.name, "User Starter")
        self.assertEqual(starter.domain_expertise, Domain.GENERAL)
        
        # Check that it was added to the cache
        self.assertIn(starter.id, self.manager.conversation_starters)
        
        # Check that it was saved to file
        starter_path = os.path.join(self.manager.conversation_starters_dir, f"{starter.id}.json")
        self.assertTrue(os.path.exists(starter_path))
    
    def test_update_prompt_template(self):
        """Test updating a user prompt template."""
        # Create a user template
        template = self.manager.create_prompt_template(
            name="User Template",
            description="A user template",
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            sections=[
                {
                    "name": "content",
                    "content": "This is a user template with {{variable}}.",
                    "description": "Main content",
                    "optional": False
                }
            ],
            variables=[
                {
                    "name": "variable",
                    "description": "A test variable",
                    "default_value": "default value",
                    "required": True
                }
            ],
            author="Test User",
            tags=["user", "test"],
            user_id="test_user"
        )
        
        # Update the template
        updated_template = self.manager.update_prompt_template(
            template_id=template.id,
            updates={
                "name": "Updated Template",
                "description": "An updated template",
                "task_type": TaskType.CODE_GENERATION,
                "tags": ["user", "test", "updated"]
            }
        )
        
        # Check that the template was updated
        self.assertEqual(updated_template.name, "Updated Template")
        self.assertEqual(updated_template.description, "An updated template")
        self.assertEqual(updated_template.task_type, TaskType.CODE_GENERATION)
        self.assertEqual(updated_template.tags, ["user", "test", "updated"])
        
        # Check that the cache was updated
        self.assertEqual(self.manager.prompt_templates[template.id].name, "Updated Template")
    
    def test_delete_prompt_template(self):
        """Test deleting a user prompt template."""
        # Create a user template
        template = self.manager.create_prompt_template(
            name="User Template",
            description="A user template",
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            sections=[
                {
                    "name": "content",
                    "content": "This is a user template with {{variable}}.",
                    "description": "Main content",
                    "optional": False
                }
            ],
            variables=[
                {
                    "name": "variable",
                    "description": "A test variable",
                    "default_value": "default value",
                    "required": True
                }
            ],
            author="Test User",
            tags=["user", "test"],
            user_id="test_user"
        )
        
        # Delete the template
        result = self.manager.delete_prompt_template(template.id)
        
        # Check that the template was deleted
        self.assertTrue(result)
        self.assertNotIn(template.id, self.manager.prompt_templates)
        
        # Check that the file was deleted
        template_path = os.path.join(self.manager.prompt_templates_dir, f"{template.id}.json")
        self.assertFalse(os.path.exists(template_path))


class TestPromptEngineeringSystem(unittest.TestCase):
    """Tests for the prompt engineering system."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for the system
        self.temp_dir = tempfile.mkdtemp()
        
        # Create subdirectories
        os.makedirs(os.path.join(self.temp_dir, "templates"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "starters"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "analytics"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "user_templates"), exist_ok=True)
        
        # Mock the components
        self.mock_template_library = MagicMock()
        self.mock_prompt_engine = MagicMock()
        self.mock_starter_library = MagicMock()
        self.mock_analytics = MagicMock()
        self.mock_user_templates = MagicMock()
        
        # Create a system with mocked components
        with patch("src.prompt_engineering.prompt_engineering_system.TemplateLibrary", return_value=self.mock_template_library), \
             patch("src.prompt_engineering.prompt_engineering_system.PromptConstructionEngine", return_value=self.mock_prompt_engine), \
             patch("src.prompt_engineering.prompt_engineering_system.ConversationStarterLibrary", return_value=self.mock_starter_library), \
             patch("src.prompt_engineering.prompt_engineering_system.PromptAnalytics", return_value=self.mock_analytics), \
             patch("src.prompt_engineering.prompt_engineering_system.UserTemplateManager", return_value=self.mock_user_templates):
            self.system = PromptEngineeringSystem(base_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test system initialization."""
        # Check that components were initialized
        self.assertEqual(self.system.template_library, self.mock_template_library)
        self.assertEqual(self.system.prompt_engine, self.mock_prompt_engine)
        self.assertEqual(self.system.starter_library, self.mock_starter_library)
        self.assertEqual(self.system.analytics, self.mock_analytics)
        self.assertEqual(self.system.user_templates, self.mock_user_templates)
        
        # Check that load methods were called
        self.mock_template_library.load_templates.assert_called_once()
        self.mock_starter_library.load_starters.assert_called_once()
        self.mock_user_templates.load_user_templates.assert_called_once()
    
    def test_get_prompt(self):
        """Test getting a prompt from a template."""
        # Mock the template
        mock_template = MagicMock()
        mock_template.task_type = TaskType.TEXT_GENERATION
        mock_template.domain = Domain.GENERAL
        mock_template.complexity_level = ComplexityLevel.MEDIUM
        
        # Mock the template library
        self.mock_template_library.get_template.return_value = mock_template
        
        # Mock the prompt engine
        self.mock_prompt_engine.construct_prompt.return_value = "This is a test prompt."
        
        # Get a prompt
        with patch("src.prompt_engineering.prompt_engineering_system.uuid.uuid4", return_value=MagicMock(hex="test_uuid")):
            prompt_id, prompt_text = self.system.get_prompt(
                template_id="test_template",
                variables={"var": "value"},
                user_id="test_user",
                conversation_id="test_conversation",
                llm_provider=LLMProvider.OPENAI,
                llm_model="gpt-4"
            )
        
        # Check the result
        self.assertEqual(prompt_id, "prompt_test_uuid")
        self.assertEqual(prompt_text, "This is a test prompt.")
        
        # Check that the template was retrieved
        self.mock_template_library.get_template.assert_called_once_with("test_template")
        
        # Check that the prompt was constructed
        self.mock_prompt_engine.construct_prompt.assert_called_once_with(mock_template, {"var": "value"})
        
        # Check that the usage was recorded
        self.mock_analytics.record_prompt_usage.assert_called_once()
    
    def test_get_conversation_starter(self):
        """Test getting a conversation starter."""
        # Mock the starter
        mock_starter = MagicMock()
        mock_starter.domain_expertise = Domain.GENERAL
        mock_starter.intelligence_level = "Advanced"
        mock_starter.verbosity = "Balanced"
        mock_starter.creativity = "Creative"
        mock_starter.format_preference = "Default"
        mock_starter.template = "SYSTEM: Initializing Aideon AI Lite with {{intelligence_level}} intelligence."
        
        # Mock the starter library
        self.mock_starter_library.get_starter.return_value = mock_starter
        
        # Mock the prompt engine
        self.mock_prompt_engine.apply_variables.return_value = "SYSTEM: Initializing Aideon AI Lite with Advanced intelligence."
        
        # Get a starter
        starter_text = self.system.get_conversation_starter(
            starter_id="test_starter",
            variables={"intelligence_level": "Advanced"},
            user_id="test_user",
            project_name="Test Project"
        )
        
        # Check the result
        self.assertEqual(starter_text, "SYSTEM: Initializing Aideon AI Lite with Advanced intelligence.")
        
        # Check that the starter was retrieved
        self.mock_starter_library.get_starter.assert_called_once_with("test_starter")
        
        # Check that the variables were applied
        self.mock_prompt_engine.apply_variables.assert_called_once()
    
    def test_record_prompt_outcome(self):
        """Test recording prompt outcome."""
        # Record an outcome
        self.system.record_prompt_outcome(
            prompt_id="test_prompt",
            outcome=PromptOutcomeType.SUCCESS,
            completion_tokens=20,
            duration_ms=500
        )
        
        # Check that the outcome was recorded
        self.mock_analytics.record_prompt_outcome.assert_called_once_with(
            prompt_id="test_prompt",
            outcome=PromptOutcomeType.SUCCESS,
            completion_tokens=20,
            duration_ms=500
        )
    
    def test_record_user_feedback(self):
        """Test recording user feedback."""
        # Record feedback
        self.system.record_user_feedback(
            prompt_id="test_prompt",
            user_rating=4,
            user_feedback="Good response"
        )
        
        # Check that the feedback was recorded
        self.mock_analytics.record_user_feedback.assert_called_once_with(
            prompt_id="test_prompt",
            user_rating=4,
            user_feedback="Good response"
        )
    
    def test_list_templates(self):
        """Test listing templates."""
        # Mock the template library
        self.mock_template_library.list_templates.return_value = [
            {"id": "system_template", "name": "System Template"}
        ]
        
        # Mock the user template manager
        self.mock_user_templates.list_user_prompt_templates.return_value = [
            {"id": "user_template", "name": "User Template"}
        ]
        
        # List templates
        templates = self.system.list_templates(
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            include_user_templates=True,
            user_id="test_user"
        )
        
        # Check the result
        self.assertEqual(len(templates), 2)
        self.assertEqual(templates[0]["id"], "system_template")
        self.assertEqual(templates[1]["id"], "user_template")
        
        # Check that the libraries were queried
        self.mock_template_library.list_templates.assert_called_once_with(
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL
        )
        
        self.mock_user_templates.list_user_prompt_templates.assert_called_once_with(
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            user_id="test_user"
        )
    
    def test_create_user_template(self):
        """Test creating a user template."""
        # Mock the user template manager
        mock_template = MagicMock()
        self.mock_user_templates.create_prompt_template.return_value = mock_template
        
        # Create a template
        template = self.system.create_user_template(
            name="User Template",
            description="A user template",
            task_type=TaskType.TEXT_GENERATION,
            complexity_level=ComplexityLevel.MEDIUM,
            domain=Domain.GENERAL,
            sections=[{"name": "content", "content": "Test content"}],
            variables=[{"name": "var", "description": "A variable"}],
            author="Test User",
            user_id="test_user"
        )
        
        # Check the result
        self.assertEqual(template, mock_template)
        
        # Check that the manager was called
        self.mock_user_templates.create_prompt_template.assert_called_once()


if __name__ == "__main__":
    unittest.main()
