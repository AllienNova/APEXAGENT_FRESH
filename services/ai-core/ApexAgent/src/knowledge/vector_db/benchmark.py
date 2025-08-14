"""
Vector Database Performance Benchmark for Aideon AI Lite

This script benchmarks the performance of the vector database integration
for the Aideon AI Lite platform, focusing on:
1. Insert performance
2. Search performance
3. Multi-tenant isolation
4. Concurrent operations
5. Memory usage

The benchmark results are used to validate that the implementation meets
enterprise-level performance requirements.
"""

import os
import time
import json
import numpy as np
import threading
import psutil
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Add the project root to the Python path
import sys
sys.path.append('/home/ubuntu/gemini_live_integration')

# Import vector database components
from src.knowledge.vector_db.vector_database import VectorDatabase, VectorDocument
from src.knowledge.vector_db.embedding_utils import EmbeddingManager
from src.knowledge.vector_db.tenant_middleware import TenantMiddleware, with_tenant_context, TenantContext, set_current_tenant_context
from src.knowledge.vector_db.adapters.faiss_adapter import FAISSAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vector_db_benchmark.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("vector_db_benchmark")

class VectorDBBenchmark:
    """Benchmark for vector database performance."""
    
    def __init__(self, storage_path: str = "/tmp/vector_db_benchmark"):
        """
        Initialize the benchmark.
        
        Args:
            storage_path: Path to store benchmark data.
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize components
        self.embedding_manager = EmbeddingManager(model_name="mock")
        self.adapter = FAISSAdapter(storage_path=os.path.join(storage_path, "faiss"))
        self.tenant_middleware = TenantMiddleware(
            tenant_validator=lambda tenant_id: tenant_id.startswith("tenant_")
        )
        
        # Initialize vector database
        self.db = VectorDatabase(
            adapter=self.adapter,
            embedding_manager=self.embedding_manager,
            tenant_middleware=self.tenant_middleware
        )
        
        # Connect to database
        self.db.connect({})
        
        # Set default tenant context for all operations
        self.default_tenant_id = "tenant_1"
        self.default_tenant_context = TenantContext(
            tenant_id=self.default_tenant_id,
            user_id="benchmark_user",
            roles=["admin"]
        )
        set_current_tenant_context(self.default_tenant_context)
        
        # Benchmark results
        self.results = {
            "insert_performance": {},
            "search_performance": {},
            "multi_tenant_isolation": {},
            "concurrent_operations": {},
            "memory_usage": {},
            "error_recovery": {},
            "system_info": self._get_system_info()
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dictionary with system information.
        """
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "platform": sys.platform,
            "python_version": sys.version,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_random_documents(self, count: int, dimension: int = 128) -> List[VectorDocument]:
        """
        Generate random documents for benchmarking.
        
        Args:
            count: Number of documents to generate.
            dimension: Dimension of embeddings.
            
        Returns:
            List of random documents.
        """
        documents = []
        
        for i in range(count):
            # Generate random embedding
            embedding = np.random.randn(dimension).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            
            # Create document
            document = VectorDocument(
                id=f"doc_{i}",
                content=f"Document {i} content for benchmarking",
                embedding=embedding,
                metadata={
                    "index": i,
                    "category": f"category_{i % 5}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            documents.append(document)
        
        return documents
    
    def benchmark_insert_performance(self, collection_name: str = "benchmark_collection",
                                    document_counts: List[int] = [100, 1000, 10000]):
        """
        Benchmark insert performance.
        
        Args:
            collection_name: Name of the collection.
            document_counts: List of document counts to benchmark.
        """
        logger.info("Benchmarking insert performance...")
        
        results = {}
        
        for count in document_counts:
            # Create collection
            if self.db.collection_exists(collection_name):
                self.db.delete_collection(collection_name)
            
            self.db.create_collection(collection_name, dimension=128)
            
            # Generate documents
            documents = self._generate_random_documents(count)
            
            # Measure insert time
            start_time = time.time()
            
            self.db.insert_documents(collection_name, documents)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Calculate insert rate
            insert_rate = count / elapsed_time
            
            results[count] = {
                "elapsed_time": elapsed_time,
                "insert_rate": insert_rate,
                "documents_per_second": insert_rate
            }
            
            logger.info(f"Insert performance for {count} documents: {insert_rate:.2f} docs/sec")
        
        self.results["insert_performance"] = results
    
    def benchmark_search_performance(self, collection_name: str = "benchmark_collection",
                                   query_counts: List[int] = [10, 100, 1000]):
        """
        Benchmark search performance.
        
        Args:
            collection_name: Name of the collection.
            query_counts: List of query counts to benchmark.
        """
        logger.info("Benchmarking search performance...")
        
        results = {}
        
        # Ensure collection exists with documents
        if not self.db.collection_exists(collection_name):
            self.db.create_collection(collection_name, dimension=128)
            documents = self._generate_random_documents(1000)
            self.db.insert_documents(collection_name, documents)
        
        for count in query_counts:
            # Generate query vectors
            query_vectors = [np.random.randn(128).astype(np.float32) for _ in range(count)]
            for vector in query_vectors:
                vector /= np.linalg.norm(vector)
            
            # Measure search time
            start_time = time.time()
            
            for vector in query_vectors:
                self.db.search_by_vector(collection_name, vector, limit=10)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Calculate search rate
            search_rate = count / elapsed_time
            
            results[count] = {
                "elapsed_time": elapsed_time,
                "search_rate": search_rate,
                "searches_per_second": search_rate
            }
            
            logger.info(f"Search performance for {count} queries: {search_rate:.2f} searches/sec")
        
        self.results["search_performance"] = results
    
    def benchmark_multi_tenant_isolation(self, collection_name: str = "shared_collection",
                                       tenant_count: int = 5,
                                       documents_per_tenant: int = 100):
        """
        Benchmark multi-tenant isolation.
        
        Args:
            collection_name: Name of the collection.
            tenant_count: Number of tenants to benchmark.
            documents_per_tenant: Number of documents per tenant.
        """
        logger.info("Benchmarking multi-tenant isolation...")
        
        results = {
            "isolation_verification": {},
            "cross_tenant_search": {}
        }
        
        # Create tenants
        tenants = [f"tenant_{i}" for i in range(1, tenant_count + 1)]
        
        # Create collection for each tenant
        for tenant_id in tenants:
            # Set tenant context for this operation
            tenant_context = TenantContext(tenant_id=tenant_id, roles=["admin"])
            set_current_tenant_context(tenant_context)
            
            if self.db.collection_exists(collection_name):
                self.db.delete_collection(collection_name)
            
            self.db.create_collection(collection_name, dimension=128)
            
            # Generate and insert documents
            documents = self._generate_random_documents(documents_per_tenant)
            self.db.insert_documents(collection_name, documents)
        
        # Verify isolation
        for tenant_id in tenants:
            # Set tenant context for this operation
            tenant_context = TenantContext(tenant_id=tenant_id, roles=["admin"])
            set_current_tenant_context(tenant_context)
            
            # Count documents in tenant's collection
            count = self.db.count_documents(collection_name)
            
            # Verify count matches expected
            isolation_verified = count == documents_per_tenant
            
            results["isolation_verification"][tenant_id] = {
                "document_count": count,
                "expected_count": documents_per_tenant,
                "isolation_verified": isolation_verified
            }
            
            logger.info(f"Tenant {tenant_id} isolation verified: {isolation_verified}")
        
        # Test cross-tenant search
        for i, tenant_id in enumerate(tenants):
            # Set tenant context for this operation
            tenant_context = TenantContext(tenant_id=tenant_id, roles=["admin"])
            set_current_tenant_context(tenant_context)
            
            # Generate query vector
            query_vector = np.random.randn(128).astype(np.float32)
            query_vector /= np.linalg.norm(query_vector)
            
            # Search in tenant's collection
            tenant_results = self.db.search_by_vector(collection_name, query_vector, limit=10)
            
            # Try to search in another tenant's collection
            other_tenant = tenants[(i + 1) % tenant_count]
            
            try:
                # This should fail due to tenant isolation
                other_tenant_context = TenantContext(tenant_id=other_tenant, roles=["admin"])
                set_current_tenant_context(other_tenant_context)
                self.db.search_by_vector(collection_name, query_vector, limit=10)
                cross_tenant_access = True
            except Exception:
                cross_tenant_access = False
            
            results["cross_tenant_search"][f"{tenant_id}_to_{other_tenant}"] = {
                "cross_tenant_access": cross_tenant_access,
                "isolation_enforced": not cross_tenant_access
            }
            
            logger.info(f"Cross-tenant search from {tenant_id} to {other_tenant} blocked: {not cross_tenant_access}")
        
        # Reset to default tenant context
        set_current_tenant_context(self.default_tenant_context)
        
        self.results["multi_tenant_isolation"] = results
    
    def benchmark_concurrent_operations(self, collection_name: str = "concurrent_collection",
                                      thread_counts: List[int] = [2, 4, 8, 16],
                                      operations_per_thread: int = 100):
        """
        Benchmark concurrent operations.
        
        Args:
            collection_name: Name of the collection.
            thread_counts: List of thread counts to benchmark.
            operations_per_thread: Number of operations per thread.
        """
        logger.info("Benchmarking concurrent operations...")
        
        results = {}
        
        # Create collection
        if self.db.collection_exists(collection_name):
            self.db.delete_collection(collection_name)
        
        self.db.create_collection(collection_name, dimension=128)
        
        # Insert initial documents
        documents = self._generate_random_documents(1000)
        self.db.insert_documents(collection_name, documents)
        
        for thread_count in thread_counts:
            # Define worker function for concurrent searches
            def search_worker():
                # Set tenant context for this thread
                tenant_context = TenantContext(tenant_id=self.default_tenant_id, roles=["admin"])
                set_current_tenant_context(tenant_context)
                
                for _ in range(operations_per_thread):
                    # Generate query vector
                    query_vector = np.random.randn(128).astype(np.float32)
                    query_vector /= np.linalg.norm(query_vector)
                    
                    # Search
                    self.db.search_by_vector(collection_name, query_vector, limit=10)
            
            # Measure concurrent search time
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(search_worker) for _ in range(thread_count)]
                for future in futures:
                    future.result()
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Calculate concurrent search rate
            total_searches = thread_count * operations_per_thread
            search_rate = total_searches / elapsed_time
            
            results[thread_count] = {
                "elapsed_time": elapsed_time,
                "total_searches": total_searches,
                "search_rate": search_rate,
                "searches_per_second": search_rate
            }
            
            logger.info(f"Concurrent search performance with {thread_count} threads: {search_rate:.2f} searches/sec")
        
        self.results["concurrent_operations"] = results
    
    def benchmark_memory_usage(self, collection_name: str = "memory_collection",
                             document_counts: List[int] = [1000, 10000, 100000]):
        """
        Benchmark memory usage.
        
        Args:
            collection_name: Name of the collection.
            document_counts: List of document counts to benchmark.
        """
        logger.info("Benchmarking memory usage...")
        
        results = {}
        
        for count in document_counts:
            # Create collection
            if self.db.collection_exists(collection_name):
                self.db.delete_collection(collection_name)
            
            self.db.create_collection(collection_name, dimension=128)
            
            # Measure initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Generate and insert documents
            documents = self._generate_random_documents(count)
            self.db.insert_documents(collection_name, documents)
            
            # Measure final memory usage
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Calculate memory per document
            memory_per_document = memory_increase / count if count > 0 else 0
            
            results[count] = {
                "initial_memory_bytes": initial_memory,
                "final_memory_bytes": final_memory,
                "memory_increase_bytes": memory_increase,
                "memory_per_document_bytes": memory_per_document
            }
            
            logger.info(f"Memory usage for {count} documents: {memory_increase / (1024 * 1024):.2f} MB, {memory_per_document:.2f} bytes/doc")
        
        self.results["memory_usage"] = results
    
    def benchmark_error_recovery(self, collection_name: str = "error_collection"):
        """
        Benchmark error recovery.
        
        Args:
            collection_name: Name of the collection.
        """
        logger.info("Benchmarking error recovery...")
        
        results = {}
        
        # Create collection
        if self.db.collection_exists(collection_name):
            self.db.delete_collection(collection_name)
        
        self.db.create_collection(collection_name, dimension=128)
        
        # Test function with retry mechanism
        def test_function():
            """Test function that fails and then succeeds."""
            if not hasattr(test_function, "attempts"):
                test_function.attempts = 0
            
            test_function.attempts += 1
            
            if test_function.attempts <= 2:
                raise Exception("Test error")
            
            return "Success"
        
        # Test error recovery
        start_time = time.time()
        
        try:
            # Use the error recovery framework
            from src.core.error_recovery.error_recovery_framework import retry_with_backoff
            
            result = retry_with_backoff(
                test_function,
                max_retries=3,
                initial_backoff=0.1,
                backoff_factor=2,
                exceptions=(Exception,)
            )
            
            recovery_successful = result == "Success"
        except Exception:
            recovery_successful = False
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        results["retry_mechanism"] = {
            "recovery_successful": recovery_successful,
            "elapsed_time": elapsed_time
        }
        
        logger.info(f"Error recovery successful: {recovery_successful}, time: {elapsed_time:.2f}s")
        
        # Test transaction rollback
        start_time = time.time()
        
        try:
            # Insert documents
            documents = self._generate_random_documents(10)
            self.db.insert_documents(collection_name, documents)
            
            # Attempt an operation that should fail
            self.db.get_document(collection_name, "non_existent_doc")
        except Exception:
            # Check if documents were inserted despite the error
            count = self.db.count_documents(collection_name)
            transaction_integrity = count == 10
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        results["transaction_integrity"] = {
            "integrity_maintained": transaction_integrity,
            "elapsed_time": elapsed_time
        }
        
        logger.info(f"Transaction integrity maintained: {transaction_integrity}, time: {elapsed_time:.2f}s")
        
        self.results["error_recovery"] = results
    
    def run_all_benchmarks(self):
        """Run all benchmarks."""
        logger.info("Running all benchmarks...")
        
        self.benchmark_insert_performance()
        self.benchmark_search_performance()
        self.benchmark_multi_tenant_isolation()
        self.benchmark_concurrent_operations()
        self.benchmark_memory_usage()
        self.benchmark_error_recovery()
        
        logger.info("All benchmarks completed.")
    
    def save_results(self, output_file: str = "vector_db_benchmark_results.json"):
        """
        Save benchmark results to file.
        
        Args:
            output_file: Output file path.
        """
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Benchmark results saved to {output_file}")
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n=== Vector Database Benchmark Summary ===\n")
        
        # Insert performance
        if "insert_performance" in self.results:
            print("Insert Performance:")
            for count, data in self.results["insert_performance"].items():
                print(f"  {count} documents: {data['documents_per_second']:.2f} docs/sec")
            print()
        
        # Search performance
        if "search_performance" in self.results:
            print("Search Performance:")
            for count, data in self.results["search_performance"].items():
                print(f"  {count} queries: {data['searches_per_second']:.2f} searches/sec")
            print()
        
        # Concurrent operations
        if "concurrent_operations" in self.results:
            print("Concurrent Operations:")
            for threads, data in self.results["concurrent_operations"].items():
                print(f"  {threads} threads: {data['searches_per_second']:.2f} searches/sec")
            print()
        
        # Memory usage
        if "memory_usage" in self.results:
            print("Memory Usage:")
            for count, data in self.results["memory_usage"].items():
                memory_mb = data["memory_increase_bytes"] / (1024 * 1024)
                memory_per_doc = data["memory_per_document_bytes"]
                print(f"  {count} documents: {memory_mb:.2f} MB total, {memory_per_doc:.2f} bytes/doc")
            print()
        
        # Multi-tenant isolation
        if "multi_tenant_isolation" in self.results:
            print("Multi-Tenant Isolation:")
            isolation_verified = all(
                data["isolation_verified"] 
                for data in self.results["multi_tenant_isolation"]["isolation_verification"].values()
            )
            cross_tenant_blocked = all(
                data["isolation_enforced"] 
                for data in self.results["multi_tenant_isolation"]["cross_tenant_search"].values()
            )
            print(f"  Isolation verified: {isolation_verified}")
            print(f"  Cross-tenant access blocked: {cross_tenant_blocked}")
            print()
        
        # Error recovery
        if "error_recovery" in self.results:
            print("Error Recovery:")
            retry_successful = self.results["error_recovery"]["retry_mechanism"]["recovery_successful"]
            integrity_maintained = self.results["error_recovery"]["transaction_integrity"]["integrity_maintained"]
            print(f"  Retry mechanism successful: {retry_successful}")
            print(f"  Transaction integrity maintained: {integrity_maintained}")
            print()
        
        print("=== End of Summary ===\n")


if __name__ == "__main__":
    # Run benchmarks
    benchmark = VectorDBBenchmark()
    benchmark.run_all_benchmarks()
    benchmark.save_results()
    benchmark.print_summary()
