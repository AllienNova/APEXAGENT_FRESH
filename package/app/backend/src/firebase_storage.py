"""
Firebase Storage integration for Aideon AI Lite.

This module provides comprehensive file storage management through Firebase Storage,
supporting user-generated content, project files, and media assets.
"""

import os
import uuid
import logging
import mimetypes
from typing import Dict, Any, Optional, List, Union, BinaryIO
from datetime import datetime, timedelta
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin.exceptions import FirebaseError
from werkzeug.datastructures import FileStorage
from PIL import Image
import io

# Configure logging
logger = logging.getLogger(__name__)

class FirebaseStorageManager:
    """Manages file storage operations through Firebase Storage."""
    
    # Supported file types and their configurations
    SUPPORTED_FILE_TYPES = {
        # Images
        'image/jpeg': {'max_size': 10 * 1024 * 1024, 'extensions': ['.jpg', '.jpeg']},
        'image/png': {'max_size': 10 * 1024 * 1024, 'extensions': ['.png']},
        'image/gif': {'max_size': 5 * 1024 * 1024, 'extensions': ['.gif']},
        'image/webp': {'max_size': 10 * 1024 * 1024, 'extensions': ['.webp']},
        'image/svg+xml': {'max_size': 1 * 1024 * 1024, 'extensions': ['.svg']},
        
        # Documents
        'application/pdf': {'max_size': 50 * 1024 * 1024, 'extensions': ['.pdf']},
        'text/plain': {'max_size': 10 * 1024 * 1024, 'extensions': ['.txt']},
        'text/markdown': {'max_size': 10 * 1024 * 1024, 'extensions': ['.md']},
        'application/json': {'max_size': 10 * 1024 * 1024, 'extensions': ['.json']},
        
        # Code files
        'text/x-python': {'max_size': 5 * 1024 * 1024, 'extensions': ['.py']},
        'text/javascript': {'max_size': 5 * 1024 * 1024, 'extensions': ['.js']},
        'text/html': {'max_size': 5 * 1024 * 1024, 'extensions': ['.html']},
        'text/css': {'max_size': 5 * 1024 * 1024, 'extensions': ['.css']},
        
        # Archives
        'application/zip': {'max_size': 100 * 1024 * 1024, 'extensions': ['.zip']},
        'application/x-tar': {'max_size': 100 * 1024 * 1024, 'extensions': ['.tar']},
        
        # Audio
        'audio/mpeg': {'max_size': 50 * 1024 * 1024, 'extensions': ['.mp3']},
        'audio/wav': {'max_size': 100 * 1024 * 1024, 'extensions': ['.wav']},
        'audio/ogg': {'max_size': 50 * 1024 * 1024, 'extensions': ['.ogg']},
        
        # Video
        'video/mp4': {'max_size': 500 * 1024 * 1024, 'extensions': ['.mp4']},
        'video/webm': {'max_size': 500 * 1024 * 1024, 'extensions': ['.webm']},
        'video/quicktime': {'max_size': 500 * 1024 * 1024, 'extensions': ['.mov']},
    }
    
    # Storage paths for different content types
    STORAGE_PATHS = {
        'user_uploads': 'user-uploads/{user_id}/',
        'project_files': 'projects/{project_id}/',
        'generated_content': 'generated/{content_type}/',
        'temp_files': 'temp/',
        'public_assets': 'public/',
        'backups': 'backups/{date}/',
        'logs': 'logs/{date}/',
        'exports': 'exports/{user_id}/'
    }
    
    def __init__(self, bucket_name: str = "aideonlite-ai.firebasestorage.app",
                 credentials_path: Optional[str] = None):
        """Initialize Firebase Storage manager.
        
        Args:
            bucket_name: Firebase Storage bucket name
            credentials_path: Path to Firebase service account credentials
        """
        self.bucket_name = bucket_name
        self.credentials_path = credentials_path
        self._bucket = None
        
        self._initialize_firebase()
    
    def _initialize_firebase(self) -> bool:
        """Initialize Firebase Admin SDK for Storage.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                if self.credentials_path and os.path.exists(self.credentials_path):
                    # Use service account credentials
                    cred = credentials.Certificate(self.credentials_path)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': self.bucket_name
                    })
                else:
                    # Use default credentials (for production environment)
                    firebase_admin.initialize_app(options={
                        'storageBucket': self.bucket_name
                    })
            
            # Get storage bucket
            self._bucket = storage.bucket()
            
            logger.info("Firebase Storage initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Storage: {str(e)}")
            return False
    
    def _validate_file(self, file_data: Union[FileStorage, bytes, BinaryIO],
                      filename: str, max_size: Optional[int] = None) -> Dict[str, Any]:
        """Validate file before upload.
        
        Args:
            file_data: File data to validate
            filename: Original filename
            max_size: Maximum file size in bytes (optional)
            
        Returns:
            Validation result dictionary
        """
        try:
            # Get file size
            if isinstance(file_data, FileStorage):
                file_size = len(file_data.read())
                file_data.seek(0)  # Reset file pointer
                content_type = file_data.content_type
            elif isinstance(file_data, bytes):
                file_size = len(file_data)
                content_type = mimetypes.guess_type(filename)[0]
            else:
                # BinaryIO
                current_pos = file_data.tell()
                file_data.seek(0, 2)  # Seek to end
                file_size = file_data.tell()
                file_data.seek(current_pos)  # Reset position
                content_type = mimetypes.guess_type(filename)[0]
            
            # Validate content type
            if content_type not in self.SUPPORTED_FILE_TYPES:
                return {
                    'valid': False,
                    'error': f'Unsupported file type: {content_type}',
                    'error_code': 'UNSUPPORTED_TYPE'
                }
            
            # Validate file size
            type_config = self.SUPPORTED_FILE_TYPES[content_type]
            max_allowed_size = max_size or type_config['max_size']
            
            if file_size > max_allowed_size:
                return {
                    'valid': False,
                    'error': f'File size ({file_size} bytes) exceeds maximum allowed size ({max_allowed_size} bytes)',
                    'error_code': 'FILE_TOO_LARGE'
                }
            
            # Validate file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext not in type_config['extensions']:
                return {
                    'valid': False,
                    'error': f'Invalid file extension: {file_ext}',
                    'error_code': 'INVALID_EXTENSION'
                }
            
            return {
                'valid': True,
                'content_type': content_type,
                'file_size': file_size,
                'file_extension': file_ext
            }
        except Exception as e:
            logger.error(f"Error validating file: {str(e)}")
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}',
                'error_code': 'VALIDATION_ERROR'
            }
    
    def _generate_unique_filename(self, original_filename: str,
                                 path_prefix: str = '') -> str:
        """Generate a unique filename to prevent conflicts.
        
        Args:
            original_filename: Original filename
            path_prefix: Path prefix for the file
            
        Returns:
            Unique filename with path
        """
        # Generate UUID for uniqueness
        unique_id = str(uuid.uuid4())
        
        # Get file extension
        file_ext = Path(original_filename).suffix.lower()
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate unique filename
        unique_filename = f"{timestamp}_{unique_id}{file_ext}"
        
        # Combine with path prefix
        if path_prefix:
            return f"{path_prefix.rstrip('/')}/{unique_filename}"
        
        return unique_filename
    
    def upload_file(self, file_data: Union[FileStorage, bytes, BinaryIO],
                   filename: str, storage_path: str = 'user_uploads',
                   user_id: Optional[str] = None, project_id: Optional[str] = None,
                   content_type: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   public: bool = False) -> Dict[str, Any]:
        """Upload a file to Firebase Storage.
        
        Args:
            file_data: File data to upload
            filename: Original filename
            storage_path: Storage path type (from STORAGE_PATHS)
            user_id: User ID for user-specific paths
            project_id: Project ID for project-specific paths
            content_type: Content type override
            metadata: Additional metadata
            public: Whether to make the file publicly accessible
            
        Returns:
            Upload result dictionary
        """
        try:
            # Validate file
            validation_result = self._validate_file(file_data, filename)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'error_code': validation_result['error_code']
                }
            
            # Get storage path template
            if storage_path not in self.STORAGE_PATHS:
                return {
                    'success': False,
                    'error': f'Invalid storage path: {storage_path}',
                    'error_code': 'INVALID_PATH'
                }
            
            # Format storage path
            path_template = self.STORAGE_PATHS[storage_path]
            if user_id:
                path_template = path_template.format(user_id=user_id)
            if project_id:
                path_template = path_template.format(project_id=project_id)
            if '{content_type}' in path_template:
                content_type_folder = validation_result['content_type'].split('/')[0]
                path_template = path_template.format(content_type=content_type_folder)
            if '{date}' in path_template:
                date_str = datetime.now().strftime('%Y-%m-%d')
                path_template = path_template.format(date=date_str)
            
            # Generate unique filename
            unique_path = self._generate_unique_filename(filename, path_template)
            
            # Prepare file data for upload
            if isinstance(file_data, FileStorage):
                upload_data = file_data.read()
                file_data.seek(0)  # Reset for potential reuse
            elif isinstance(file_data, bytes):
                upload_data = file_data
            else:
                # BinaryIO
                current_pos = file_data.tell()
                upload_data = file_data.read()
                file_data.seek(current_pos)  # Reset position
            
            # Create blob
            blob = self._bucket.blob(unique_path)
            
            # Set content type
            blob.content_type = content_type or validation_result['content_type']
            
            # Set metadata
            if metadata:
                blob.metadata = metadata
            
            # Add standard metadata
            blob.metadata = blob.metadata or {}
            blob.metadata.update({
                'uploaded_at': datetime.now().isoformat(),
                'original_filename': filename,
                'file_size': str(validation_result['file_size']),
                'uploader_user_id': user_id or 'system',
                'project_id': project_id or '',
                'storage_path_type': storage_path
            })
            
            # Upload file
            blob.upload_from_string(upload_data, content_type=blob.content_type)
            
            # Set public access if requested
            if public:
                blob.make_public()
            
            # Generate download URL
            if public:
                download_url = blob.public_url
            else:
                # Generate signed URL (valid for 1 hour)
                download_url = blob.generate_signed_url(
                    expiration=datetime.now() + timedelta(hours=1)
                )
            
            return {
                'success': True,
                'file_path': unique_path,
                'download_url': download_url,
                'public_url': blob.public_url if public else None,
                'file_size': validation_result['file_size'],
                'content_type': blob.content_type,
                'metadata': blob.metadata,
                'uploaded_at': datetime.now().isoformat()
            }
        except FirebaseError as e:
            logger.error(f"Firebase error uploading file: {str(e)}")
            return {
                'success': False,
                'error': f'Firebase storage error: {str(e)}',
                'error_code': 'FIREBASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return {
                'success': False,
                'error': f'Upload error: {str(e)}',
                'error_code': 'UPLOAD_ERROR'
            }
    
    def download_file(self, file_path: str, local_path: Optional[str] = None) -> Dict[str, Any]:
        """Download a file from Firebase Storage.
        
        Args:
            file_path: Path to the file in storage
            local_path: Local path to save the file (optional)
            
        Returns:
            Download result dictionary
        """
        try:
            # Get blob
            blob = self._bucket.blob(file_path)
            
            # Check if file exists
            if not blob.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            if local_path:
                # Download to local file
                blob.download_to_filename(local_path)
                return {
                    'success': True,
                    'local_path': local_path,
                    'file_size': blob.size,
                    'content_type': blob.content_type,
                    'metadata': blob.metadata
                }
            else:
                # Download to memory
                file_data = blob.download_as_bytes()
                return {
                    'success': True,
                    'file_data': file_data,
                    'file_size': blob.size,
                    'content_type': blob.content_type,
                    'metadata': blob.metadata
                }
        except FirebaseError as e:
            logger.error(f"Firebase error downloading file: {str(e)}")
            return {
                'success': False,
                'error': f'Firebase storage error: {str(e)}',
                'error_code': 'FIREBASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return {
                'success': False,
                'error': f'Download error: {str(e)}',
                'error_code': 'DOWNLOAD_ERROR'
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file from Firebase Storage.
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            Deletion result dictionary
        """
        try:
            # Get blob
            blob = self._bucket.blob(file_path)
            
            # Check if file exists
            if not blob.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            # Delete file
            blob.delete()
            
            return {
                'success': True,
                'message': f'File {file_path} deleted successfully'
            }
        except FirebaseError as e:
            logger.error(f"Firebase error deleting file: {str(e)}")
            return {
                'success': False,
                'error': f'Firebase storage error: {str(e)}',
                'error_code': 'FIREBASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return {
                'success': False,
                'error': f'Delete error: {str(e)}',
                'error_code': 'DELETE_ERROR'
            }
    
    def list_files(self, path_prefix: str = '', max_results: int = 100) -> Dict[str, Any]:
        """List files in Firebase Storage.
        
        Args:
            path_prefix: Path prefix to filter files
            max_results: Maximum number of results to return
            
        Returns:
            List result dictionary
        """
        try:
            # List blobs
            blobs = self._bucket.list_blobs(prefix=path_prefix, max_results=max_results)
            
            files = []
            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created.isoformat() if blob.time_created else None,
                    'updated': blob.updated.isoformat() if blob.updated else None,
                    'metadata': blob.metadata,
                    'public_url': blob.public_url,
                    'md5_hash': blob.md5_hash
                })
            
            return {
                'success': True,
                'files': files,
                'count': len(files),
                'path_prefix': path_prefix
            }
        except FirebaseError as e:
            logger.error(f"Firebase error listing files: {str(e)}")
            return {
                'success': False,
                'error': f'Firebase storage error: {str(e)}',
                'error_code': 'FIREBASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return {
                'success': False,
                'error': f'List error: {str(e)}',
                'error_code': 'LIST_ERROR'
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a file in Firebase Storage.
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            File information dictionary
        """
        try:
            # Get blob
            blob = self._bucket.blob(file_path)
            
            # Check if file exists
            if not blob.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            # Reload blob to get latest metadata
            blob.reload()
            
            return {
                'success': True,
                'file_info': {
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created.isoformat() if blob.time_created else None,
                    'updated': blob.updated.isoformat() if blob.updated else None,
                    'metadata': blob.metadata,
                    'public_url': blob.public_url,
                    'md5_hash': blob.md5_hash,
                    'etag': blob.etag
                }
            }
        except FirebaseError as e:
            logger.error(f"Firebase error getting file info: {str(e)}")
            return {
                'success': False,
                'error': f'Firebase storage error: {str(e)}',
                'error_code': 'FIREBASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return {
                'success': False,
                'error': f'Info error: {str(e)}',
                'error_code': 'INFO_ERROR'
            }
    
    def generate_signed_url(self, file_path: str, expiration_hours: int = 1,
                           method: str = 'GET') -> Dict[str, Any]:
        """Generate a signed URL for a file.
        
        Args:
            file_path: Path to the file in storage
            expiration_hours: URL expiration time in hours
            method: HTTP method for the URL (GET, PUT, POST, DELETE)
            
        Returns:
            Signed URL result dictionary
        """
        try:
            # Get blob
            blob = self._bucket.blob(file_path)
            
            # Generate signed URL
            expiration = datetime.now() + timedelta(hours=expiration_hours)
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method=method
            )
            
            return {
                'success': True,
                'signed_url': signed_url,
                'expiration': expiration.isoformat(),
                'method': method,
                'file_path': file_path
            }
        except FirebaseError as e:
            logger.error(f"Firebase error generating signed URL: {str(e)}")
            return {
                'success': False,
                'error': f'Firebase storage error: {str(e)}',
                'error_code': 'FIREBASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Error generating signed URL: {str(e)}")
            return {
                'success': False,
                'error': f'URL generation error: {str(e)}',
                'error_code': 'URL_ERROR'
            }
    
    def copy_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """Copy a file within Firebase Storage.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            Copy result dictionary
        """
        try:
            # Get source blob
            source_blob = self._bucket.blob(source_path)
            
            # Check if source file exists
            if not source_blob.exists():
                return {
                    'success': False,
                    'error': 'Source file not found',
                    'error_code': 'SOURCE_NOT_FOUND'
                }
            
            # Copy to destination
            destination_blob = self._bucket.copy_blob(source_blob, self._bucket, destination_path)
            
            return {
                'success': True,
                'source_path': source_path,
                'destination_path': destination_path,
                'destination_url': destination_blob.public_url
            }
        except FirebaseError as e:
            logger.error(f"Firebase error copying file: {str(e)}")
            return {
                'success': False,
                'error': f'Firebase storage error: {str(e)}',
                'error_code': 'FIREBASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Error copying file: {str(e)}")
            return {
                'success': False,
                'error': f'Copy error: {str(e)}',
                'error_code': 'COPY_ERROR'
            }
    
    def get_storage_usage(self, path_prefix: str = '') -> Dict[str, Any]:
        """Get storage usage statistics for a path.
        
        Args:
            path_prefix: Path prefix to analyze
            
        Returns:
            Storage usage dictionary
        """
        try:
            # List all blobs with prefix
            blobs = self._bucket.list_blobs(prefix=path_prefix)
            
            total_size = 0
            file_count = 0
            file_types = {}
            
            for blob in blobs:
                total_size += blob.size or 0
                file_count += 1
                
                # Count by content type
                content_type = blob.content_type or 'unknown'
                file_types[content_type] = file_types.get(content_type, 0) + 1
            
            return {
                'success': True,
                'usage': {
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'file_count': file_count,
                    'file_types': file_types,
                    'path_prefix': path_prefix,
                    'analyzed_at': datetime.now().isoformat()
                }
            }
        except FirebaseError as e:
            logger.error(f"Firebase error getting storage usage: {str(e)}")
            return {
                'success': False,
                'error': f'Firebase storage error: {str(e)}',
                'error_code': 'FIREBASE_ERROR'
            }
        except Exception as e:
            logger.error(f"Error getting storage usage: {str(e)}")
            return {
                'success': False,
                'error': f'Usage error: {str(e)}',
                'error_code': 'USAGE_ERROR'
            }

# Global instance for easy access
storage_manager = None

def get_storage_manager() -> FirebaseStorageManager:
    """Get the global storage manager instance.
    
    Returns:
        FirebaseStorageManager instance
    """
    global storage_manager
    
    if storage_manager is None:
        storage_manager = FirebaseStorageManager()
    
    return storage_manager

