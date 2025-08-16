"""
Test suite for Firebase Storage integration.

This module provides comprehensive tests for the Firebase Storage
functionality in Aideon AI Lite.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import io
from datetime import datetime, timedelta
from werkzeug.datastructures import FileStorage

# Import the modules to test
from ..firebase_storage import FirebaseStorageManager
from ..api.storage_endpoints import storage_bp

class TestFirebaseStorageManager(unittest.TestCase):
    """Test cases for FirebaseStorageManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FirebaseStorageManager()
        
        # Mock Firebase dependencies
        self.mock_bucket = Mock()
        self.manager._bucket = self.mock_bucket
    
    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin._apps', [])
    @patch('firebase_admin.storage.bucket')
    def test_initialize_firebase_success(self, mock_bucket, mock_init_app):
        """Test successful Firebase initialization."""
        mock_app = Mock()
        mock_init_app.return_value = mock_app
        mock_bucket.return_value = Mock()
        
        manager = FirebaseStorageManager()
        self.assertIsNotNone(manager._bucket)
    
    def test_validate_file_success(self):
        """Test successful file validation."""
        # Create test file data
        test_data = b"test file content"
        filename = "test.txt"
        
        result = self.manager._validate_file(test_data, filename)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['content_type'], 'text/plain')
        self.assertEqual(result['file_size'], len(test_data))
        self.assertEqual(result['file_extension'], '.txt')
    
    def test_validate_file_unsupported_type(self):
        """Test file validation with unsupported type."""
        test_data = b"test file content"
        filename = "test.xyz"  # Unsupported extension
        
        result = self.manager._validate_file(test_data, filename)
        
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_code'], 'UNSUPPORTED_TYPE')
    
    def test_validate_file_too_large(self):
        """Test file validation with file too large."""
        # Create large file data
        test_data = b"x" * (11 * 1024 * 1024)  # 11MB (exceeds 10MB limit for text)
        filename = "test.txt"
        
        result = self.manager._validate_file(test_data, filename)
        
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_code'], 'FILE_TOO_LARGE')
    
    def test_generate_unique_filename(self):
        """Test unique filename generation."""
        original_filename = "test.txt"
        path_prefix = "user-uploads/123"
        
        unique_filename = self.manager._generate_unique_filename(original_filename, path_prefix)
        
        self.assertTrue(unique_filename.startswith(path_prefix))
        self.assertTrue(unique_filename.endswith('.txt'))
        self.assertIn('_', unique_filename)  # Should contain timestamp and UUID
    
    def test_upload_file_success(self):
        """Test successful file upload."""
        # Mock blob
        mock_blob = Mock()
        mock_blob.content_type = 'text/plain'
        mock_blob.metadata = {}
        mock_blob.public_url = 'https://example.com/file.txt'
        mock_blob.generate_signed_url.return_value = 'https://example.com/signed-url'
        
        self.mock_bucket.blob.return_value = mock_blob
        
        # Test data
        test_data = b"test file content"
        filename = "test.txt"
        
        result = self.manager.upload_file(test_data, filename, user_id="123")
        
        self.assertTrue(result['success'])
        self.assertIn('file_path', result)
        self.assertIn('download_url', result)
        self.assertEqual(result['file_size'], len(test_data))
        
        # Verify blob operations
        mock_blob.upload_from_string.assert_called_once()
        mock_blob.generate_signed_url.assert_called_once()
    
    def test_upload_file_validation_failure(self):
        """Test file upload with validation failure."""
        test_data = b"test file content"
        filename = "test.xyz"  # Unsupported extension
        
        result = self.manager.upload_file(test_data, filename)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_code'], 'UNSUPPORTED_TYPE')
    
    def test_download_file_success(self):
        """Test successful file download."""
        # Mock blob
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.size = 100
        mock_blob.content_type = 'text/plain'
        mock_blob.metadata = {'test': 'value'}
        mock_blob.download_as_bytes.return_value = b"test content"
        
        self.mock_bucket.blob.return_value = mock_blob
        
        result = self.manager.download_file("test/file.txt")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['file_data'], b"test content")
        self.assertEqual(result['file_size'], 100)
        self.assertEqual(result['content_type'], 'text/plain')
    
    def test_download_file_not_found(self):
        """Test file download when file doesn't exist."""
        # Mock blob
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        
        self.mock_bucket.blob.return_value = mock_blob
        
        result = self.manager.download_file("nonexistent/file.txt")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_code'], 'FILE_NOT_FOUND')
    
    def test_delete_file_success(self):
        """Test successful file deletion."""
        # Mock blob
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        
        self.mock_bucket.blob.return_value = mock_blob
        
        result = self.manager.delete_file("test/file.txt")
        
        self.assertTrue(result['success'])
        mock_blob.delete.assert_called_once()
    
    def test_list_files_success(self):
        """Test successful file listing."""
        # Mock blobs
        mock_blob1 = Mock()
        mock_blob1.name = "file1.txt"
        mock_blob1.size = 100
        mock_blob1.content_type = "text/plain"
        mock_blob1.time_created = datetime.now()
        mock_blob1.updated = datetime.now()
        mock_blob1.metadata = {}
        mock_blob1.public_url = "https://example.com/file1.txt"
        mock_blob1.md5_hash = "abc123"
        
        mock_blob2 = Mock()
        mock_blob2.name = "file2.txt"
        mock_blob2.size = 200
        mock_blob2.content_type = "text/plain"
        mock_blob2.time_created = datetime.now()
        mock_blob2.updated = datetime.now()
        mock_blob2.metadata = {}
        mock_blob2.public_url = "https://example.com/file2.txt"
        mock_blob2.md5_hash = "def456"
        
        self.mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
        
        result = self.manager.list_files("test/")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['files']), 2)
        self.assertEqual(result['files'][0]['name'], "file1.txt")
        self.assertEqual(result['files'][1]['name'], "file2.txt")
    
    def test_get_file_info_success(self):
        """Test successful file info retrieval."""
        # Mock blob
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.name = "test.txt"
        mock_blob.size = 100
        mock_blob.content_type = "text/plain"
        mock_blob.time_created = datetime.now()
        mock_blob.updated = datetime.now()
        mock_blob.metadata = {"test": "value"}
        mock_blob.public_url = "https://example.com/test.txt"
        mock_blob.md5_hash = "abc123"
        mock_blob.etag = "etag123"
        
        self.mock_bucket.blob.return_value = mock_blob
        
        result = self.manager.get_file_info("test.txt")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['file_info']['name'], "test.txt")
        self.assertEqual(result['file_info']['size'], 100)
        mock_blob.reload.assert_called_once()
    
    def test_generate_signed_url_success(self):
        """Test successful signed URL generation."""
        # Mock blob
        mock_blob = Mock()
        mock_blob.generate_signed_url.return_value = "https://example.com/signed-url"
        
        self.mock_bucket.blob.return_value = mock_blob
        
        result = self.manager.generate_signed_url("test.txt", expiration_hours=2)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['signed_url'], "https://example.com/signed-url")
        self.assertEqual(result['method'], 'GET')
        mock_blob.generate_signed_url.assert_called_once()
    
    def test_copy_file_success(self):
        """Test successful file copy."""
        # Mock source blob
        mock_source_blob = Mock()
        mock_source_blob.exists.return_value = True
        
        # Mock destination blob
        mock_dest_blob = Mock()
        mock_dest_blob.public_url = "https://example.com/dest.txt"
        
        self.mock_bucket.blob.return_value = mock_source_blob
        self.mock_bucket.copy_blob.return_value = mock_dest_blob
        
        result = self.manager.copy_file("source.txt", "dest.txt")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['source_path'], "source.txt")
        self.assertEqual(result['destination_path'], "dest.txt")
        self.mock_bucket.copy_blob.assert_called_once()
    
    def test_get_storage_usage_success(self):
        """Test successful storage usage calculation."""
        # Mock blobs
        mock_blob1 = Mock()
        mock_blob1.size = 100
        mock_blob1.content_type = "text/plain"
        
        mock_blob2 = Mock()
        mock_blob2.size = 200
        mock_blob2.content_type = "image/jpeg"
        
        self.mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
        
        result = self.manager.get_storage_usage("test/")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['usage']['total_size_bytes'], 300)
        self.assertEqual(result['usage']['file_count'], 2)
        self.assertEqual(result['usage']['file_types']['text/plain'], 1)
        self.assertEqual(result['usage']['file_types']['image/jpeg'], 1)

class TestStorageEndpoints(unittest.TestCase):
    """Test cases for storage API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        from flask import Flask
        
        self.app = Flask(__name__)
        self.app.register_blueprint(storage_bp)
        self.client = self.app.test_client()
        
        # Mock storage manager
        self.mock_manager = Mock()
        
        # Patch the get_storage_manager function
        self.patcher = patch('src.api.storage_endpoints.get_storage_manager')
        self.mock_get_manager = self.patcher.start()
        self.mock_get_manager.return_value = self.mock_manager
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.patcher.stop()
    
    def test_upload_file_success(self):
        """Test successful file upload via API."""
        # Mock storage manager response
        self.mock_manager.upload_file.return_value = {
            'success': True,
            'file_path': 'test/file.txt',
            'download_url': 'https://example.com/download',
            'file_size': 100,
            'content_type': 'text/plain',
            'uploaded_at': datetime.now().isoformat()
        }
        
        # Create test file
        test_file = FileStorage(
            stream=io.BytesIO(b"test content"),
            filename="test.txt",
            content_type="text/plain"
        )
        
        response = self.client.post(
            '/api/v1/storage/upload',
            data={
                'file': test_file,
                'storage_path': 'user_uploads',
                'user_id': '123'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('file', data)
    
    def test_upload_file_no_file(self):
        """Test file upload with no file provided."""
        response = self.client.post('/api/v1/storage/upload')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'NO_FILE')
    
    def test_download_file_success(self):
        """Test successful file download via API."""
        # Mock storage manager response
        self.mock_manager.download_file.return_value = {
            'success': True,
            'file_data': b"test content",
            'content_type': 'text/plain'
        }
        
        response = self.client.get('/api/v1/storage/download/test/file.txt')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"test content")
    
    def test_download_file_not_found(self):
        """Test file download when file doesn't exist."""
        # Mock storage manager response
        self.mock_manager.download_file.return_value = {
            'success': False,
            'error': 'File not found',
            'error_code': 'FILE_NOT_FOUND'
        }
        
        response = self.client.get('/api/v1/storage/download/nonexistent.txt')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_get_file_info_success(self):
        """Test successful file info retrieval via API."""
        # Mock storage manager response
        self.mock_manager.get_file_info.return_value = {
            'success': True,
            'file_info': {
                'name': 'test.txt',
                'size': 100,
                'content_type': 'text/plain',
                'created': datetime.now().isoformat()
            }
        }
        
        response = self.client.get('/api/v1/storage/info/test.txt')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('file', data)
    
    @patch('src.api.storage_endpoints._is_authorized_for_file')
    def test_delete_file_success(self, mock_is_authorized):
        """Test successful file deletion via API."""
        mock_is_authorized.return_value = True
        
        # Mock storage manager response
        self.mock_manager.delete_file.return_value = {
            'success': True,
            'message': 'File deleted successfully'
        }
        
        response = self.client.delete('/api/v1/storage/delete/test.txt')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    @patch('src.api.storage_endpoints._is_authorized_for_file')
    def test_delete_file_unauthorized(self, mock_is_authorized):
        """Test unauthorized file deletion."""
        mock_is_authorized.return_value = False
        
        response = self.client.delete('/api/v1/storage/delete/test.txt')
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'UNAUTHORIZED')
    
    def test_list_files_success(self):
        """Test successful file listing via API."""
        # Mock storage manager response
        self.mock_manager.list_files.return_value = {
            'success': True,
            'files': [
                {'name': 'file1.txt', 'size': 100},
                {'name': 'file2.txt', 'size': 200}
            ],
            'count': 2,
            'path_prefix': 'test/'
        }
        
        response = self.client.get('/api/v1/storage/list?prefix=test/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)
    
    @patch('src.api.storage_endpoints._is_authorized_for_file')
    def test_generate_signed_url_success(self, mock_is_authorized):
        """Test successful signed URL generation via API."""
        mock_is_authorized.return_value = True
        
        # Mock storage manager response
        self.mock_manager.generate_signed_url.return_value = {
            'success': True,
            'signed_url': 'https://example.com/signed-url',
            'expiration': datetime.now().isoformat(),
            'method': 'GET'
        }
        
        response = self.client.post(
            '/api/v1/storage/signed-url/test.txt',
            json={'expiration_hours': 2, 'method': 'GET'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('signed_url', data)
    
    @patch('src.api.storage_endpoints._is_authorized_for_file')
    def test_copy_file_success(self, mock_is_authorized):
        """Test successful file copy via API."""
        mock_is_authorized.return_value = True
        
        # Mock storage manager response
        self.mock_manager.copy_file.return_value = {
            'success': True,
            'source_path': 'source.txt',
            'destination_path': 'dest.txt',
            'destination_url': 'https://example.com/dest.txt'
        }
        
        response = self.client.post(
            '/api/v1/storage/copy',
            json={
                'source_path': 'source.txt',
                'destination_path': 'dest.txt'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    @patch('src.api.storage_endpoints._is_authorized_for_path')
    def test_get_storage_usage_success(self, mock_is_authorized):
        """Test successful storage usage retrieval via API."""
        mock_is_authorized.return_value = True
        
        # Mock storage manager response
        self.mock_manager.get_storage_usage.return_value = {
            'success': True,
            'usage': {
                'total_size_bytes': 1000,
                'total_size_mb': 0.95,
                'file_count': 5,
                'file_types': {'text/plain': 3, 'image/jpeg': 2}
            }
        }
        
        response = self.client.get('/api/v1/storage/usage?prefix=test/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('usage', data)

if __name__ == '__main__':
    unittest.main()

