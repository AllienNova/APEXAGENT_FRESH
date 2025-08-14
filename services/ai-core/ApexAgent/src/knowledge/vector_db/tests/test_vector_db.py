        np.testing.assert_array_equal(embedding1, embedding2)
    
    def test_batch_embedding(self):
        """Test batch embedding generation."""
        # Generate batch of embeddings
        contents = [
            "This is document 1",
            "This is document 2",
            "This is document 3"
        ]
        
        embeddings = self.embedding_manager.generate_embeddings_batch(contents)
        
        # Check embeddings
        self.assertEqual(len(embeddings), 3)
        for embedding in embeddings:
            self.assertIsInstance(embedding, np.ndarray)
            self.assertEqual(embedding.shape, (128,))
    
    def test_multi_tenant_embedding(self):
        """Test multi-tenant embedding isolation."""
        # Generate embeddings for different tenants
        embedding1 = self.embedding_manager.generate_embedding(
            content="Shared content",
            tenant_id="tenant_1"
        )
        
        embedding2 = self.embedding_manager.generate_embedding(
            content="Shared content",
            tenant_id="tenant_2"
        )
        
        # Check that embeddings are different (due to tenant isolation)
        self.assertFalse(np.array_equal(embedding1, embedding2))


class TestTenantMiddleware(unittest.TestCase):
    """Test suite for tenant middleware."""
    
    def setUp(self):
        """Set up test environment."""
        # Create tenant middleware
        self.middleware = TenantMiddleware(
            tenant_validator=lambda tenant_id: tenant_id.startswith("tenant_")
        )
        
        # Clear tenant context
        clear_current_tenant_context()
    
    def tearDown(self):