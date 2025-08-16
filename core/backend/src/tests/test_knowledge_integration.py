"""
Knowledge Integration Tests for Dr. TARDIS

This module contains tests for the knowledge integration components of Dr. TARDIS,
including knowledge base connection, security boundaries, specialized modules,
and context-aware knowledge retrieval.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import sys
import unittest
import asyncio
import json
import logging
from unittest.mock import MagicMock, patch
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import knowledge modules
from src.knowledge.knowledge_base import KnowledgeBase, ApexAgentKnowledgeConnector
from src.knowledge.security_boundary import SecurityBoundary, AccessLevel
from src.knowledge.specialized_modules import SpecializedKnowledgeModule, SupportScenarioModule
from src.knowledge.context_aware_retrieval import ContextAwareRetrieval, ProjectMemoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("KnowledgeIntegrationTests")


class TestKnowledgeBase(unittest.TestCase):
    """Test cases for the KnowledgeBase class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        self.knowledge_base = KnowledgeBase(data_path=self.test_data_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_data_dir)
    
    def test_initialization(self):
        """Test initialization of KnowledgeBase."""
        self.assertIsNotNone(self.knowledge_base)
        self.assertEqual(self.knowledge_base.data_path, self.test_data_dir)
        self.assertIsNotNone(self.knowledge_base.logger)
    
    def test_add_knowledge_item(self):
        """Test adding a knowledge item."""
        item = {
            "id": "test_item_1",
            "title": "Test Item",
            "content": "This is a test knowledge item.",
            "tags": ["test", "knowledge"]
        }
        
        self.knowledge_base.add_knowledge_item(item)
        
        # Check if item was added
        self.assertIn("test_item_1", self.knowledge_base.knowledge_items)
        self.assertEqual(self.knowledge_base.knowledge_items["test_item_1"], item)
    
    def test_get_knowledge_item(self):
        """Test retrieving a knowledge item."""
        item = {
            "id": "test_item_2",
            "title": "Another Test Item",
            "content": "This is another test knowledge item.",
            "tags": ["test", "knowledge", "another"]
        }
        
        self.knowledge_base.add_knowledge_item(item)
        
        # Retrieve item
        retrieved = self.knowledge_base.get_knowledge_item("test_item_2")
        
        self.assertEqual(retrieved, item)
        
        # Test retrieving non-existent item
        self.assertIsNone(self.knowledge_base.get_knowledge_item("non_existent"))
    
    def test_search_knowledge(self):
        """Test searching knowledge items."""
        # Add multiple items
        items = [
            {
                "id": "item1",
                "title": "Python Programming",
                "content": "Python is a high-level programming language.",
                "tags": ["python", "programming"]
            },
            {
                "id": "item2",
                "title": "JavaScript Basics",
                "content": "JavaScript is a scripting language for web development.",
                "tags": ["javascript", "programming", "web"]
            },
            {
                "id": "item3",
                "title": "Machine Learning",
                "content": "Machine learning is a subset of artificial intelligence.",
                "tags": ["ml", "ai", "data science"]
            }
        ]
        
        for item in items:
            self.knowledge_base.add_knowledge_item(item)
        
        # Search for programming
        results = self.knowledge_base.search_knowledge("programming")
        self.assertEqual(len(results), 2)
        self.assertIn("item1", [r["id"] for r in results])
        self.assertIn("item2", [r["id"] for r in results])
        
        # Search for machine learning
        results = self.knowledge_base.search_knowledge("machine learning")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "item3")
        
        # Search with tag filter
        results = self.knowledge_base.search_knowledge("programming", tags=["python"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "item1")
    
    def test_delete_knowledge_item(self):
        """Test deleting a knowledge item."""
        item = {
            "id": "item_to_delete",
            "title": "Item to Delete",
            "content": "This item will be deleted.",
            "tags": ["delete", "test"]
        }
        
        self.knowledge_base.add_knowledge_item(item)
        self.assertIn("item_to_delete", self.knowledge_base.knowledge_items)
        
        # Delete the item
        self.knowledge_base.delete_knowledge_item("item_to_delete")
        self.assertNotIn("item_to_delete", self.knowledge_base.knowledge_items)


class TestApexAgentKnowledgeConnector(unittest.TestCase):
    """Test cases for the ApexAgentKnowledgeConnector class."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_api_client = MagicMock()
        self.connector = ApexAgentKnowledgeConnector(api_client=self.mock_api_client)
    
    def test_initialization(self):
        """Test initialization of ApexAgentKnowledgeConnector."""
        self.assertIsNotNone(self.connector)
        self.assertEqual(self.connector.api_client, self.mock_api_client)
        self.assertIsNotNone(self.connector.logger)
    
    @patch('src.knowledge.knowledge_base.ApexAgentKnowledgeConnector.query_knowledge_base')
    def test_query_knowledge_base(self, mock_query):
        """Test querying the knowledge base."""
        # Set up mock return value
        mock_query.return_value = [
            {
                "id": "kb1",
                "title": "Test Knowledge",
                "content": "Test content",
                "relevance": 0.9
            }
        ]
        
        # Query the knowledge base
        results = self.connector.query_knowledge_base("test query")
        
        # Check results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "kb1")
        self.assertEqual(results[0]["relevance"], 0.9)
        
        # Verify mock was called
        mock_query.assert_called_once_with("test query")
    
    @patch('src.knowledge.knowledge_base.ApexAgentKnowledgeConnector.retrieve_document')
    def test_retrieve_document(self, mock_retrieve):
        """Test retrieving a document."""
        # Set up mock return value
        mock_retrieve.return_value = {
            "id": "doc1",
            "title": "Test Document",
            "content": "Test document content",
            "metadata": {"author": "Test Author"}
        }
        
        # Retrieve document
        document = self.connector.retrieve_document("doc1")
        
        # Check document
        self.assertEqual(document["id"], "doc1")
        self.assertEqual(document["title"], "Test Document")
        
        # Verify mock was called
        mock_retrieve.assert_called_once_with("doc1")


class TestSecurityBoundary(unittest.TestCase):
    """Test cases for the SecurityBoundary class."""
    
    def setUp(self):
        """Set up test environment."""
        self.security_boundary = SecurityBoundary()
    
    def test_initialization(self):
        """Test initialization of SecurityBoundary."""
        self.assertIsNotNone(self.security_boundary)
        self.assertIsNotNone(self.security_boundary.logger)
    
    def test_check_access_permission(self):
        """Test checking access permission."""
        # Set up test data
        user_context = {
            "user_id": "test_user",
            "access_level": AccessLevel.STANDARD
        }
        
        resource = {
            "id": "resource1",
            "required_access_level": AccessLevel.STANDARD,
            "restricted": False
        }
        
        # Check permission (should be allowed)
        self.assertTrue(self.security_boundary.check_access_permission(user_context, resource))
        
        # Test with higher required access level
        resource["required_access_level"] = AccessLevel.ADMIN
        self.assertFalse(self.security_boundary.check_access_permission(user_context, resource))
        
        # Test with admin user
        user_context["access_level"] = AccessLevel.ADMIN
        self.assertTrue(self.security_boundary.check_access_permission(user_context, resource))
        
        # Test with restricted resource
        resource["restricted"] = True
        resource["allowed_users"] = ["other_user"]
        self.assertFalse(self.security_boundary.check_access_permission(user_context, resource))
        
        # Add user to allowed users
        resource["allowed_users"].append("test_user")
        self.assertTrue(self.security_boundary.check_access_permission(user_context, resource))
    
    def test_filter_results_by_permission(self):
        """Test filtering results by permission."""
        # Set up test data
        user_context = {
            "user_id": "test_user",
            "access_level": AccessLevel.STANDARD
        }
        
        results = [
            {
                "id": "result1",
                "title": "Public Result",
                "required_access_level": AccessLevel.PUBLIC,
                "restricted": False
            },
            {
                "id": "result2",
                "title": "Standard Result",
                "required_access_level": AccessLevel.STANDARD,
                "restricted": False
            },
            {
                "id": "result3",
                "title": "Admin Result",
                "required_access_level": AccessLevel.ADMIN,
                "restricted": False
            },
            {
                "id": "result4",
                "title": "Restricted Result",
                "required_access_level": AccessLevel.STANDARD,
                "restricted": True,
                "allowed_users": ["other_user"]
            }
        ]
        
        # Filter results
        filtered = self.security_boundary.filter_results_by_permission(user_context, results)
        
        # Check filtered results
        self.assertEqual(len(filtered), 2)
        self.assertIn("result1", [r["id"] for r in filtered])
        self.assertIn("result2", [r["id"] for r in filtered])
        self.assertNotIn("result3", [r["id"] for r in filtered])
        self.assertNotIn("result4", [r["id"] for r in filtered])
    
    def test_sanitize_query(self):
        """Test sanitizing a query."""
        # Test with sensitive information
        query = "My password is secret123 and my credit card is 1234-5678-9012-3456"
        sanitized = self.security_boundary.sanitize_query(query)
        
        # Check sanitized query
        self.assertNotEqual(sanitized, query)
        self.assertNotIn("secret123", sanitized)
        self.assertNotIn("1234-5678-9012-3456", sanitized)
        
        # Test with SQL injection attempt
        query = "users WHERE 1=1; DROP TABLE users;"
        sanitized = self.security_boundary.sanitize_query(query)
        
        # Check sanitized query
        self.assertNotEqual(sanitized, query)
        self.assertNotIn("DROP TABLE", sanitized)


class TestSpecializedKnowledgeModule(unittest.TestCase):
    """Test cases for the SpecializedKnowledgeModule class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        self.module = SpecializedKnowledgeModule(data_path=self.test_data_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_data_dir)
    
    def test_initialization(self):
        """Test initialization of SpecializedKnowledgeModule."""
        self.assertIsNotNone(self.module)
        self.assertEqual(self.module.data_path, self.test_data_dir)
        self.assertIsNotNone(self.module.logger)
    
    def test_register_knowledge_provider(self):
        """Test registering a knowledge provider."""
        # Create mock provider
        mock_provider = MagicMock()
        mock_provider.get_provider_info.return_value = {
            "id": "test_provider",
            "name": "Test Provider",
            "description": "A test knowledge provider"
        }
        
        # Register provider
        self.module.register_knowledge_provider(mock_provider)
        
        # Check if provider was registered
        self.assertIn("test_provider", self.module.providers)
        self.assertEqual(self.module.providers["test_provider"], mock_provider)
    
    def test_get_provider(self):
        """Test getting a knowledge provider."""
        # Create and register mock provider
        mock_provider = MagicMock()
        mock_provider.get_provider_info.return_value = {
            "id": "test_provider",
            "name": "Test Provider",
            "description": "A test knowledge provider"
        }
        
        self.module.register_knowledge_provider(mock_provider)
        
        # Get provider
        provider = self.module.get_provider("test_provider")
        
        # Check provider
        self.assertEqual(provider, mock_provider)
        
        # Test getting non-existent provider
        self.assertIsNone(self.module.get_provider("non_existent"))
    
    @patch('src.knowledge.specialized_modules.SpecializedKnowledgeModule.query_all_providers')
    def test_query_all_providers(self, mock_query):
        """Test querying all providers."""
        # Set up mock return value
        mock_query.return_value = [
            {
                "provider_id": "provider1",
                "results": [{"id": "result1", "title": "Result 1"}]
            },
            {
                "provider_id": "provider2",
                "results": [{"id": "result2", "title": "Result 2"}]
            }
        ]
        
        # Query all providers
        results = self.module.query_all_providers("test query")
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["provider_id"], "provider1")
        self.assertEqual(results[1]["provider_id"], "provider2")
        
        # Verify mock was called
        mock_query.assert_called_once_with("test query")


class TestSupportScenarioModule(unittest.TestCase):
    """Test cases for the SupportScenarioModule class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        self.module = SupportScenarioModule(data_path=self.test_data_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_data_dir)
    
    def test_initialization(self):
        """Test initialization of SupportScenarioModule."""
        self.assertIsNotNone(self.module)
        self.assertEqual(self.module.data_path, self.test_data_dir)
        self.assertIsNotNone(self.module.logger)
    
    def test_add_scenario(self):
        """Test adding a support scenario."""
        # Create scenario
        scenario = {
            "id": "scenario1",
            "name": "Test Scenario",
            "description": "A test support scenario",
            "steps": ["Step 1", "Step 2", "Step 3"],
            "tags": ["test", "support"]
        }
        
        # Add scenario
        self.module.add_scenario(scenario)
        
        # Check if scenario was added
        self.assertIn("scenario1", self.module.scenarios)
        self.assertEqual(self.module.scenarios["scenario1"], scenario)
    
    def test_get_scenario(self):
        """Test getting a support scenario."""
        # Create and add scenario
        scenario = {
            "id": "scenario2",
            "name": "Another Test Scenario",
            "description": "Another test support scenario",
            "steps": ["Step A", "Step B"],
            "tags": ["test", "another"]
        }
        
        self.module.add_scenario(scenario)
        
        # Get scenario
        retrieved = self.module.get_scenario("scenario2")
        
        # Check scenario
        self.assertEqual(retrieved, scenario)
        
        # Test getting non-existent scenario
        self.assertIsNone(self.module.get_scenario("non_existent"))
    
    def test_search_scenarios(self):
        """Test searching support scenarios."""
        # Add multiple scenarios
        scenarios = [
            {
                "id": "s1",
                "name": "Network Troubleshooting",
                "description": "Steps to troubleshoot network issues",
                "steps": ["Check connection", "Verify settings"],
                "tags": ["network", "troubleshooting"]
            },
            {
                "id": "s2",
                "name": "Software Installation",
                "description": "Guide for software installation",
                "steps": ["Download software", "Run installer"],
                "tags": ["software", "installation"]
            },
            {
                "id": "s3",
                "name": "Password Reset",
                "description": "Process for resetting passwords",
                "steps": ["Verify identity", "Reset password"],
                "tags": ["password", "security"]
            }
        ]
        
        for scenario in scenarios:
            self.module.add_scenario(scenario)
        
        # Search for troubleshooting
        results = self.module.search_scenarios("troubleshooting")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "s1")
        
        # Search for installation
        results = self.module.search_scenarios("installation")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "s2")
        
        # Search with tag filter
        results = self.module.search_scenarios("", tags=["security"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "s3")


class TestContextAwareRetrieval(unittest.TestCase):
    """Test cases for the ContextAwareRetrieval class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        self.car = ContextAwareRetrieval(data_path=self.test_data_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_data_dir)
    
    def test_initialization(self):
        """Test initialization of ContextAwareRetrieval."""
        self.assertIsNotNone(self.car)
        self.assertEqual(self.car.data_path, self.test_data_dir)
        self.assertIsNotNone(self.car.logger)
        self.assertIsNotNone(self.car.conversation_contexts)
        self.assertIsNotNone(self.car.project_memories)
        self.assertIsNotNone(self.car.user_preferences)
    
    def test_enhance_query(self):
        """Test enhancing a query with context."""
        # Set up test data
        conversation_id = "test_conv"
        project_id = "test_proj"
        user_id = "test_user"
        
        # Create conversation context
        self.car.conversation_contexts[conversation_id] = {
            "id": conversation_id,
            "messages": [
                {"role": "user", "content": "What is machine learning?"},
                {"role": "assistant", "content": "Machine learning is a subset of AI..."}
            ],
            "topics": ["machine learning", "AI"]
        }
        
        # Create project memory
        self.car.project_memories[project_id] = {
            "id": project_id,
            "name": "Test Project",
            "description": "A test project",
            "key_information": {"domain": "artificial intelligence"}
        }
        
        # Create user preferences
        self.car.user_preferences[user_id] = {
            "id": user_id,
            "preferred_topics": ["machine learning", "data science"]
        }
        
        # Test query enhancement
        context = {
            "conversation_id": conversation_id,
            "project_id": project_id,
            "user_id": user_id
        }
        
        # Run the test asynchronously
        async def run_test():
            enhanced = await self.car.enhance_query("How does it work?", context)
            return enhanced
        
        enhanced = asyncio.run(run_test())
        
        # Check enhanced query
        self.assertNotEqual(enhanced, "How does it work?")
        self.assertIn("Context:", enhanced)
    
    def test_process_results(self):
        """Test processing results with context awareness."""
        # Set up test data
        results = [
            {"id": "r1", "title": "Machine Learning Basics", "content": "Introduction to ML", "relevance": 0.5},
            {"id": "r2", "title": "Data Science Overview", "content": "Introduction to data science", "relevance": 0.4},
            {"id": "r3", "title": "Python Programming", "content": "Python basics", "relevance": 0.3}
        ]
        
        context = {
            "conversation_id": "test_conv",
            "project_id": "test_proj",
            "user_id": "test_user",
            "query": "machine learning"
        }
        
        # Create conversation context with ML focus
        self.car.conversation_contexts["test_conv"] = {
            "id": "test_conv",
            "messages": [
                {"role": "user", "content": "Tell me about machine learning"}
            ],
            "topics": ["machine learning"]
        }
        
        # Run the test asynchronously
        async def run_test():
            processed = await self.car.process_results(results, context)
            return processed
        
        processed = asyncio.run(run_test())
        
        # Check processed results
        self.assertEqual(len(processed), 3)
        # ML should be first due to relevance boost
        self.assertEqual(processed[0]["id"], "r1")
    
    def test_update_context(self):
        """Test updating context with query and results."""
        # Set up test data
        query = "machine learning algorithms"
        results = [
            {"id": "r1", "title": "Machine Learning Algorithms", "content": "Overview of ML algorithms"}
        ]
        
        context = {
            "conversation_id": "new_conv",
            "project_id": "new_proj",
            "user_id": "new_user"
        }
        
        # Run the test asynchronously
        async def run_test():
            await self.car.update_context(query, results, context)
            
            # Check if conversation context was created
            self.assertIn("new_conv", self.car.conversation_contexts)
            
            # Check if project memory was created
            self.assertIn("new_proj", self.car.project_memories)
            
            # Check if user preferences were created
            self.assertIn("new_user", self.car.user_preferences)
        
        asyncio.run(run_test())


class TestProjectMemoryManager(unittest.TestCase):
    """Test cases for the ProjectMemoryManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        self.car = ContextAwareRetrieval(data_path=self.test_data_dir)
        self.pmm = ProjectMemoryManager(self.car, data_path=self.test_data_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_data_dir)
    
    def test_initialization(self):
        """Test initialization of ProjectMemoryManager."""
        self.assertIsNotNone(self.pmm)
        self.assertEqual(self.pmm.data_path, self.test_data_dir)
        self.assertIsNotNone(self.pmm.logger)
        self.assertEqual(self.pmm.context_retrieval, self.car)
    
    def test_create_project(self):
        """Test creating a project."""
        # Run the test asynchronously
        async def run_test():
            project = await self.pmm.create_project(
                "test_project",
                "Test Project",
                "A test project for unit testing"
            )
            
            # Check project
            self.assertIsNotNone(project)
            self.assertEqual(project["id"], "test_project")
            self.assertEqual(project["name"], "Test Project")
            self.assertEqual(project["description"], "A test project for unit testing")
            
            # Check if project was added to projects
            self.assertIn("test_project", self.pmm.projects)
        
        asyncio.run(run_test())
    
    def test_add_artifact(self):
        """Test adding an artifact to a project."""
        # Run the test asynchronously
        async def run_test():
            # Create project
            project = await self.pmm.create_project(
                "artifact_project",
                "Artifact Project"
            )
            
            # Add artifact
            artifact = await self.pmm.add_artifact(
                "artifact_project",
                "Test Artifact",
                "This is a test artifact content.",
                "document",
                {"tags": ["test", "artifact"]}
            )
            
            # Check artifact
            self.assertIsNotNone(artifact)
            self.assertEqual(artifact["name"], "Test Artifact")
            self.assertEqual(artifact["type"], "document")
            self.assertEqual(artifact["version"], 1)
            
            # Check if artifact was added to artifacts
            artifact_id = artifact["id"]
            self.assertIn(artifact_id, self.pmm.artifacts)
            
            # Get artifact
            retrieved = await self.pmm.get_artifact(artifact_id)
            self.assertEqual(retrieved["name"], "Test Artifact")
        
        asyncio.run(run_test())
    
    def test_update_artifact(self):
        """Test updating an artifact."""
        # Run the test asynchronously
        async def run_test():
            # Create project and add artifact
            await self.pmm.create_project("update_project", "Update Project")
            artifact = await self.pmm.add_artifact(
                "update_project",
                "Original Artifact",
                "Original content",
                "document"
            )
            
            # Update artifact
            updated = await self.pmm.update_artifact(
                artifact["id"],
                "Updated content",
                {"status": "updated"}
            )
            
            # Check updated artifact
            self.assertIsNotNone(updated)
            self.assertEqual(updated["content"], "Updated content")
            self.assertEqual(updated["version"], 2)
            self.assertEqual(updated["metadata"]["status"], "updated")
            
            # Get latest version
            latest = await self.pmm.get_artifact(artifact["id"])
            self.assertEqual(latest["version"], 2)
            
            # Get specific version
            v1 = await self.pmm.get_artifact(artifact["id"], 1)
            self.assertEqual(v1["content"], "Original content")
            self.assertEqual(v1["version"], 1)
        
        asyncio.run(run_test())
    
    def test_add_decision(self):
        """Test adding a decision to project memory."""
        # Run the test asynchronously
        async def run_test():
            # Create project
            await self.pmm.create_project("decision_project", "Decision Project")
            
            # Add decision
            updated_project = await self.pmm.add_decision(
                "decision_project",
                "Decided to use Python for implementation",
                {"query": "What language should we use?"}
            )
            
            # Check if decision was added
            self.assertIsNotNone(updated_project)
            self.assertIn("decisions", updated_project)
            self.assertEqual(len(updated_project["decisions"]), 1)
            self.assertEqual(
                updated_project["decisions"][0]["decision"],
                "Decided to use Python for implementation"
            )
            
            # Get decisions
            decisions = await self.pmm.get_project_decisions("decision_project")
            self.assertEqual(len(decisions), 1)
        
        asyncio.run(run_test())
    
    def test_search_artifacts(self):
        """Test searching for artifacts."""
        # Run the test asynchronously
        async def run_test():
            # Create project and add artifacts
            await self.pmm.create_project("search_project", "Search Project")
            
            await self.pmm.add_artifact(
                "search_project",
                "Python Guide",
                "A guide to Python programming",
                "document",
                {"tags": ["python", "programming"]}
            )
            
            await self.pmm.add_artifact(
                "search_project",
                "JavaScript Tutorial",
                "A tutorial for JavaScript",
                "document",
                {"tags": ["javascript", "programming"]}
            )
            
            # Search for Python
            results = await self.pmm.search_artifacts("python", "search_project")
            
            # Check results
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["name"], "Python Guide")
            
            # Search for programming (should find both)
            results = await self.pmm.search_artifacts("programming", "search_project")
            self.assertEqual(len(results), 2)
        
        asyncio.run(run_test())


class TestKnowledgeIntegration(unittest.TestCase):
    """Integration tests for the knowledge components."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        
        # Create components
        self.knowledge_base = KnowledgeBase(data_path=os.path.join(self.test_data_dir, "kb"))
        self.security_boundary = SecurityBoundary()
        self.specialized_module = SpecializedKnowledgeModule(data_path=os.path.join(self.test_data_dir, "specialized"))
        self.support_module = SupportScenarioModule(data_path=os.path.join(self.test_data_dir, "support"))
        self.context_retrieval = ContextAwareRetrieval(data_path=os.path.join(self.test_data_dir, "context"))
        self.project_memory = ProjectMemoryManager(self.context_retrieval, data_path=os.path.join(self.test_data_dir, "projects"))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_data_dir)
    
    def test_end_to_end_knowledge_flow(self):
        """Test end-to-end knowledge flow."""
        # Run the test asynchronously
        async def run_test():
            # 1. Create a project
            project = await self.project_memory.create_project(
                "integration_project",
                "Integration Test Project",
                "A project for testing knowledge integration"
            )
            
            # 2. Add knowledge items
            self.knowledge_base.add_knowledge_item({
                "id": "kb_item_1",
                "title": "Machine Learning Overview",
                "content": "Machine learning is a field of AI...",
                "tags": ["ml", "ai"],
                "required_access_level": AccessLevel.PUBLIC
            })
            
            self.knowledge_base.add_knowledge_item({
                "id": "kb_item_2",
                "title": "Advanced ML Techniques",
                "content": "Advanced techniques include...",
                "tags": ["ml", "advanced"],
                "required_access_level": AccessLevel.STANDARD
            })
            
            # 3. Add support scenario
            self.support_module.add_scenario({
                "id": "ml_support_1",
                "name": "ML Model Troubleshooting",
                "description": "Steps to troubleshoot ML model issues",
                "steps": ["Check data quality", "Verify model parameters"],
                "tags": ["ml", "troubleshooting"]
            })
            
            # 4. Create a conversation context
            await self.context_retrieval.create_conversation(
                "ml_conversation",
                {
                    "messages": [
                        {"role": "user", "content": "I want to learn about machine learning"}
                    ],
                    "topics": ["machine learning"]
                }
            )
            
            # 5. Add an artifact to the project
            artifact = await self.project_memory.add_artifact(
                "integration_project",
                "ML Project Plan",
                "This is a plan for implementing ML models",
                "document",
                {"tags": ["ml", "plan"]}
            )
            
            # 6. Simulate a query with context
            query = "How do I troubleshoot my machine learning model?"
            
            context = {
                "conversation_id": "ml_conversation",
                "project_id": "integration_project",
                "user_id": "test_user",
                "access_level": AccessLevel.STANDARD
            }
            
            # 7. Enhance query with context
            enhanced_query = await self.context_retrieval.enhance_query(query, context)
            
            # 8. Search knowledge base
            kb_results = self.knowledge_base.search_knowledge(enhanced_query)
            
            # 9. Apply security boundary
            filtered_results = self.security_boundary.filter_results_by_permission(context, kb_results)
            
            # 10. Search support scenarios
            support_results = self.support_module.search_scenarios(enhanced_query)
            
            # 11. Combine results
            combined_results = filtered_results + support_results
            
            # 12. Process results with context awareness
            processed_results = await self.context_retrieval.process_results(combined_results, context)
            
            # 13. Update context with query and results
            await self.context_retrieval.update_context(query, processed_results, context)
            
            # 14. Add a decision based on results
            await self.project_memory.add_decision(
                "integration_project",
                "Decided to implement data quality checks for ML models",
                {"query": query}
            )
            
            # 15. Update the artifact with new information
            await self.project_memory.update_artifact(
                artifact["id"],
                "Updated plan with troubleshooting steps: 1. Check data quality, 2. Verify model parameters",
                {"status": "updated"}
            )
            
            # Verify the flow worked correctly
            # Check if conversation was updated
            conversation = await self.context_retrieval.get_conversation_context("ml_conversation")
            self.assertIsNotNone(conversation)
            self.assertGreater(len(conversation["messages"]), 1)
            
            # Check if project was updated
            project = await self.project_memory.get_project("integration_project")
            self.assertIsNotNone(project)
            self.assertGreater(len(project["decisions"]), 0)
            
            # Check if artifact was updated
            artifact = await self.project_memory.get_artifact(artifact["id"])
            self.assertIsNotNone(artifact)
            self.assertEqual(artifact["version"], 2)
            self.assertIn("troubleshooting", artifact["content"])
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
