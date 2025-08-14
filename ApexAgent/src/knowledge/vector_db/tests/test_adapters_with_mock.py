"""
Vector Database Tests with Mock Services

This module contains unit tests for the Milvus and Chroma adapters using mock services.
"""

import os
import unittest
import tempfile
import shutil
import numpy as np
from typing import Dict, Any, List, Optional

# Import mock Milvus implementation
from src.knowledge.vector_db.tests.mock_milvus import MockMilvus

# Import mock embedding function
from src.knowledge.vector_db.tests.mock_embedding import MockEmbeddingFunction

# Patch pymilvus with mock implementation
MockMilvus.patch()

from src.knowledge.vector_db.vector_database import VectorDocument, MetadataFilter
from src.knowledge.vector_db.adapters.milvus.milvus_adapter import MilvusAdapter
from src.knowledge.vector_db.adapters.chroma.chroma_adapter import ChromaAdapter


class TestMilvusAdapter(unittest.TestCase):
    """Test cases for the Milvus adapter using mock Milvus service."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for Milvus storage
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize Milvus adapter with in-memory mode
        self.adapter = MilvusAdapter(storage_path=self.temp_dir)
        
        # Connect to Milvus
        self.adapter.connect({})
        
        # Test collection parameters
        self.collection_name = "test_collection"
        self.dimension = 128
        self.tenant_id = "test_tenant"
    
    def tearDown(self):
        """Clean up test environment."""
        # Disconnect from Milvus
        self.adapter.disconnect()
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_create_collection(self):
        """Test creating a collection."""
        # Create collection
        result = self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check if collection exists
        exists = self.adapter.collection_exists(
            name=self.collection_name,
            tenant_id=self.tenant_id
        )
        
        self.assertTrue(exists)
    
    def test_list_collections(self):
        """Test listing collections."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # List collections
        collections = self.adapter.list_collections(tenant_id=self.tenant_id)
        
        # Check result
        self.assertIn(self.collection_name, collections)
    
    def test_delete_collection(self):
        """Test deleting a collection."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Delete collection
        result = self.adapter.delete_collection(
            name=self.collection_name,
            tenant_id=self.tenant_id
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check if collection exists
        exists = self.adapter.collection_exists(
            name=self.collection_name,
            tenant_id=self.tenant_id
        )
        
        self.assertFalse(exists)
    
    def test_insert_document(self):
        """Test inserting a document."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Create document
        document = VectorDocument(
            id="test_doc",
            content="Test document content",
            embedding=np.random.rand(self.dimension).astype(np.float32),
            metadata={"key": "value"},
            tenant_id=self.tenant_id
        )
        
        # Insert document
        doc_id = self.adapter.insert_document(
            collection_name=self.collection_name,
            document=document,
            tenant_id=self.tenant_id
        )
        
        # Check result
        self.assertEqual(doc_id, "test_doc")
        
        # Get document count
        count = self.adapter.count_documents(
            collection_name=self.collection_name,
            tenant_id=self.tenant_id
        )
        
        self.assertEqual(count, 1)
    
    def test_get_document(self):
        """Test getting a document."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Create document
        document = VectorDocument(
            id="test_doc",
            content="Test document content",
            embedding=np.random.rand(self.dimension).astype(np.float32),
            metadata={"key": "value"},
            tenant_id=self.tenant_id
        )
        
        # Insert document
        self.adapter.insert_document(
            collection_name=self.collection_name,
            document=document,
            tenant_id=self.tenant_id
        )
        
        # Get document
        retrieved_doc = self.adapter.get_document(
            collection_name=self.collection_name,
            document_id="test_doc",
            tenant_id=self.tenant_id
        )
        
        # Check result
        self.assertEqual(retrieved_doc.id, "test_doc")
        self.assertEqual(retrieved_doc.content, "Test document content")
        self.assertEqual(retrieved_doc.metadata.get("key"), "value")
        self.assertEqual(retrieved_doc.embedding.shape, (self.dimension,))
    
    def test_delete_document(self):
        """Test deleting a document."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Create document
        document = VectorDocument(
            id="test_doc",
            content="Test document content",
            embedding=np.random.rand(self.dimension).astype(np.float32),
            metadata={"key": "value"},
            tenant_id=self.tenant_id
        )
        
        # Insert document
        self.adapter.insert_document(
            collection_name=self.collection_name,
            document=document,
            tenant_id=self.tenant_id
        )
        
        # Delete document
        result = self.adapter.delete_document(
            collection_name=self.collection_name,
            document_id="test_doc",
            tenant_id=self.tenant_id
        )
        
        # Check result
        self.assertTrue(result)
        
        # Get document count
        count = self.adapter.count_documents(
            collection_name=self.collection_name,
            tenant_id=self.tenant_id
        )
        
        self.assertEqual(count, 0)
    
    def test_update_document(self):
        """Test updating a document."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Create document
        document = VectorDocument(
            id="test_doc",
            content="Test document content",
            embedding=np.random.rand(self.dimension).astype(np.float32),
            metadata={"key": "value"},
            tenant_id=self.tenant_id
        )
        
        # Insert document
        self.adapter.insert_document(
            collection_name=self.collection_name,
            document=document,
            tenant_id=self.tenant_id
        )
        
        # Update document
        updated_doc = VectorDocument(
            id="test_doc",
            content="Updated document content",
            embedding=np.random.rand(self.dimension).astype(np.float32),
            metadata={"key": "updated_value"},
            tenant_id=self.tenant_id
        )
        
        result = self.adapter.update_document(
            collection_name=self.collection_name,
            document=updated_doc,
            tenant_id=self.tenant_id
        )
        
        # Check result
        self.assertTrue(result)
        
        # Get document
        retrieved_doc = self.adapter.get_document(
            collection_name=self.collection_name,
            document_id="test_doc",
            tenant_id=self.tenant_id
        )
        
        # Check updated content
        self.assertEqual(retrieved_doc.content, "Updated document content")
        self.assertEqual(retrieved_doc.metadata.get("key"), "updated_value")
    
    def test_search_by_vector(self):
        """Test searching by vector."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Create documents
        docs = []
        for i in range(10):
            doc = VectorDocument(
                id=f"test_doc_{i}",
                content=f"Test document content {i}",
                embedding=np.random.rand(self.dimension).astype(np.float32),
                metadata={"index": i},
                tenant_id=self.tenant_id
            )
            docs.append(doc)
        
        # Insert documents
        for doc in docs:
            self.adapter.insert_document(
                collection_name=self.collection_name,
                document=doc,
                tenant_id=self.tenant_id
            )
        
        # Search by vector
        query_vector = np.random.rand(self.dimension).astype(np.float32)
        results = self.adapter.search_by_vector(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=5,
            tenant_id=self.tenant_id
        )
        
        # Check results
        self.assertLessEqual(len(results), 5)
        for result in results:
            self.assertIsNotNone(result.document)
            self.assertIsNotNone(result.score)
            self.assertIn("distance", result.metadata)
    
    def test_multi_tenant_isolation(self):
        """Test multi-tenant isolation."""
        # Create collection for tenant 1
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id="tenant1"
        )
        
        # Create collection for tenant 2
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id="tenant2"
        )
        
        # Create document for tenant 1
        doc1 = VectorDocument(
            id="test_doc",
            content="Tenant 1 document",
            embedding=np.random.rand(self.dimension).astype(np.float32),
            metadata={"tenant": "tenant1"},
            tenant_id="tenant1"
        )
        
        # Create document for tenant 2
        doc2 = VectorDocument(
            id="test_doc",
            content="Tenant 2 document",
            embedding=np.random.rand(self.dimension).astype(np.float32),
            metadata={"tenant": "tenant2"},
            tenant_id="tenant2"
        )
        
        # Insert documents
        self.adapter.insert_document(
            collection_name=self.collection_name,
            document=doc1,
            tenant_id="tenant1"
        )
        
        self.adapter.insert_document(
            collection_name=self.collection_name,
            document=doc2,
            tenant_id="tenant2"
        )
        
        # Get document for tenant 1
        doc1_retrieved = self.adapter.get_document(
            collection_name=self.collection_name,
            document_id="test_doc",
            tenant_id="tenant1"
        )
        
        # Get document for tenant 2
        doc2_retrieved = self.adapter.get_document(
            collection_name=self.collection_name,
            document_id="test_doc",
            tenant_id="tenant2"
        )
        
        # Check isolation
        self.assertEqual(doc1_retrieved.content, "Tenant 1 document")
        self.assertEqual(doc2_retrieved.content, "Tenant 2 document")
        
        # List collections for tenant 1
        collections1 = self.adapter.list_collections(tenant_id="tenant1")
        
        # List collections for tenant 2
        collections2 = self.adapter.list_collections(tenant_id="tenant2")
        
        # Check isolation
        self.assertIn(self.collection_name, collections1)
        self.assertIn(self.collection_name, collections2)
        
        # Delete collection for tenant 1
        self.adapter.delete_collection(
            name=self.collection_name,
            tenant_id="tenant1"
        )
        
        # Check if collection still exists for tenant 2
        exists = self.adapter.collection_exists(
            name=self.collection_name,
            tenant_id="tenant2"
        )
        
        self.assertTrue(exists)


class TestChromaAdapter(unittest.TestCase):
    """Test cases for the Chroma adapter."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for Chroma storage
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize Chroma adapter with persistent storage
        self.adapter = ChromaAdapter(persist_directory=self.temp_dir)
        
        # Connect to Chroma
        self.adapter.connect({})
        
        # Replace default embedding function with mock
        self.adapter.default_embedding_function = MockEmbeddingFunction(dimension=128)
        
        # Test collection parameters
        self.collection_name = "test_collection"
        self.dimension = 128
        self.tenant_id = "test_tenant"
    
    def tearDown(self):
        """Clean up test environment."""
        # Disconnect from Chroma
        self.adapter.disconnect()
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_create_collection(self):
        """Test creating a collection."""
        # Create collection
        result = self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check if collection exists
        exists = self.adapter.collection_exists(
            name=self.collection_name,
            tenant_id=self.tenant_id
        )
        
        self.assertTrue(exists)
    
    def test_list_collections(self):
        """Test listing collections."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # List collections
        collections = self.adapter.list_collections(tenant_id=self.tenant_id)
        
        # Check result
        self.assertIn(self.collection_name, collections)
    
    def test_delete_collection(self):
        """Test deleting a collection."""
        # Create collection
        self.adapter.create_collection(
            name=self.collection_name,
            dimension=self.dimension,
            tenant_id=self.tenant_id
        )
        
        # Delete collection
        result = self.adapter.delete_collection(
            name=self.collection_name,
            tenant_id=self.tenant_id
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check if collection exists
        exists = self.adapter.collection_exists(
            name=self.collection_name,
            tenant_id=self.tenant_id
        )
        
        
(Content truncated due to size limit. Use line ranges to read in chunks)