"""
API endpoints for Firebase Storage management.

This module provides REST API endpoints for file upload, download,
and management through Firebase Storage.
"""

import logging
import json
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, send_file, g
from werkzeug.utils import secure_filename
from .firebase_storage import get_storage_manager
from .feature_flags import require_feature
from .firebase_remote_config import get_remote_config_manager
import io

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint for storage endpoints
storage_bp = Blueprint('storage', __name__, url_prefix='/api/v1/storage')

@storage_bp.route('/upload', methods=['POST'])
@require_feature("firebase_storage")
def upload_file():
    """Upload a file to Firebase Storage.
    
    Returns:
        JSON response with upload result
    """
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided",
                "error_code": "NO_FILE"
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected",
                "error_code": "NO_FILE_SELECTED"
            }), 400
        
        # Get additional parameters
        storage_path = request.form.get('storage_path', 'user_uploads')
        user_id = request.form.get('user_id')
        project_id = request.form.get('project_id')
        public = request.form.get('public', 'false').lower() == 'true'
        
        # Get metadata if provided
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except json.JSONDecodeError:
                return jsonify({
                    "success": False,
                    "error": "Invalid metadata JSON",
                    "error_code": "INVALID_METADATA"
                }), 400
        
        # Add request metadata
        metadata.update({
            'uploaded_via': 'api',
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        })
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Upload file
        storage_manager = get_storage_manager()
        result = storage_manager.upload_file(
            file_data=file,
            filename=filename,
            storage_path=storage_path,
            user_id=user_id,
            project_id=project_id,
            metadata=metadata,
            public=public
        )
        
        if result['success']:
            return jsonify({
                "success": True,
                "file": {
                    "path": result['file_path'],
                    "download_url": result['download_url'],
                    "public_url": result.get('public_url'),
                    "size": result['file_size'],
                    "content_type": result['content_type'],
                    "uploaded_at": result['uploaded_at']
                },
                "message": "File uploaded successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 400
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@storage_bp.route('/download/<path:file_path>', methods=['GET'])
def download_file(file_path: str):
    """Download a file from Firebase Storage.
    
    Args:
        file_path: Path to the file in storage
        
    Returns:
        File download or JSON error response
    """
    try:
        # Get download type (inline or attachment)
        download_type = request.args.get('type', 'inline')
        
        # Download file
        storage_manager = get_storage_manager()
        result = storage_manager.download_file(file_path)
        
        if result['success']:
            # Create file-like object from bytes
            file_obj = io.BytesIO(result['file_data'])
            
            # Determine filename from path
            filename = file_path.split('/')[-1]
            
            # Set download disposition
            as_attachment = download_type == 'attachment'
            
            return send_file(
                file_obj,
                mimetype=result['content_type'],
                as_attachment=as_attachment,
                download_name=filename
            )
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 404 if result['error_code'] == 'FILE_NOT_FOUND' else 500
    except Exception as e:
        logger.error(f"Error in download endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@storage_bp.route('/info/<path:file_path>', methods=['GET'])
def get_file_info(file_path: str):
    """Get information about a file.
    
    Args:
        file_path: Path to the file in storage
        
    Returns:
        JSON response with file information
    """
    try:
        storage_manager = get_storage_manager()
        result = storage_manager.get_file_info(file_path)
        
        if result['success']:
            return jsonify({
                "success": True,
                "file": result['file_info']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 404 if result['error_code'] == 'FILE_NOT_FOUND' else 500
    except Exception as e:
        logger.error(f"Error in file info endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@storage_bp.route('/delete/<path:file_path>', methods=['DELETE'])
def delete_file(file_path: str):
    """Delete a file from Firebase Storage.
    
    Args:
        file_path: Path to the file in storage
        
    Returns:
        JSON response with deletion result
    """
    try:
        # Check permissions (implement proper auth)
        if not _is_authorized_for_file(file_path):
            return jsonify({
                "success": False,
                "error": "Unauthorized access",
                "error_code": "UNAUTHORIZED"
            }), 403
        
        storage_manager = get_storage_manager()
        result = storage_manager.delete_file(file_path)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": result['message']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 404 if result['error_code'] == 'FILE_NOT_FOUND' else 500
    except Exception as e:
        logger.error(f"Error in delete endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@storage_bp.route('/list', methods=['GET'])
def list_files():
    """List files in Firebase Storage.
    
    Returns:
        JSON response with file list
    """
    try:
        # Get query parameters
        path_prefix = request.args.get('prefix', '')
        max_results = int(request.args.get('max_results', 100))
        
        # Limit max_results to prevent abuse
        max_results = min(max_results, 1000)
        
        storage_manager = get_storage_manager()
        result = storage_manager.list_files(path_prefix, max_results)
        
        if result['success']:
            return jsonify({
                "success": True,
                "files": result['files'],
                "count": result['count'],
                "prefix": result['path_prefix']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 500
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid max_results parameter",
            "error_code": "INVALID_PARAMETER"
        }), 400
    except Exception as e:
        logger.error(f"Error in list endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@storage_bp.route('/signed-url/<path:file_path>', methods=['POST'])
def generate_signed_url(file_path: str):
    """Generate a signed URL for a file.
    
    Args:
        file_path: Path to the file in storage
        
    Returns:
        JSON response with signed URL
    """
    try:
        # Check permissions
        if not _is_authorized_for_file(file_path):
            return jsonify({
                "success": False,
                "error": "Unauthorized access",
                "error_code": "UNAUTHORIZED"
            }), 403
        
        # Get parameters
        data = request.get_json() or {}
        expiration_hours = data.get('expiration_hours', 1)
        method = data.get('method', 'GET').upper()
        
        # Validate parameters
        if expiration_hours < 1 or expiration_hours > 168:  # Max 1 week
            return jsonify({
                "success": False,
                "error": "Expiration hours must be between 1 and 168",
                "error_code": "INVALID_EXPIRATION"
            }), 400
        
        if method not in ['GET', 'PUT', 'POST', 'DELETE']:
            return jsonify({
                "success": False,
                "error": "Invalid HTTP method",
                "error_code": "INVALID_METHOD"
            }), 400
        
        storage_manager = get_storage_manager()
        result = storage_manager.generate_signed_url(file_path, expiration_hours, method)
        
        if result['success']:
            return jsonify({
                "success": True,
                "signed_url": result['signed_url'],
                "expiration": result['expiration'],
                "method": result['method']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 500
    except Exception as e:
        logger.error(f"Error in signed URL endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@storage_bp.route('/copy', methods=['POST'])
def copy_file():
    """Copy a file within Firebase Storage.
    
    Returns:
        JSON response with copy result
    """
    try:
        data = request.get_json()
        if not data or 'source_path' not in data or 'destination_path' not in data:
            return jsonify({
                "success": False,
                "error": "Missing source_path or destination_path",
                "error_code": "MISSING_PARAMETERS"
            }), 400
        
        source_path = data['source_path']
        destination_path = data['destination_path']
        
        # Check permissions for both paths
        if not _is_authorized_for_file(source_path) or not _is_authorized_for_file(destination_path):
            return jsonify({
                "success": False,
                "error": "Unauthorized access",
                "error_code": "UNAUTHORIZED"
            }), 403
        
        storage_manager = get_storage_manager()
        result = storage_manager.copy_file(source_path, destination_path)
        
        if result['success']:
            return jsonify({
                "success": True,
                "source_path": result['source_path'],
                "destination_path": result['destination_path'],
                "destination_url": result['destination_url']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 404 if result['error_code'] == 'SOURCE_NOT_FOUND' else 500
    except Exception as e:
        logger.error(f"Error in copy endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@storage_bp.route('/usage', methods=['GET'])
def get_storage_usage():
    """Get storage usage statistics.
    
    Returns:
        JSON response with usage statistics
    """
    try:
        # Get path prefix
        path_prefix = request.args.get('prefix', '')
        
        # Check if user is authorized to view usage for this prefix
        if not _is_authorized_for_path(path_prefix):
            return jsonify({
                "success": False,
                "error": "Unauthorized access",
                "error_code": "UNAUTHORIZED"
            }), 403
        
        storage_manager = get_storage_manager()
        result = storage_manager.get_storage_usage(path_prefix)
        
        if result['success']:
            return jsonify({
                "success": True,
                "usage": result['usage']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 500
    except Exception as e:
        logger.error(f"Error in usage endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

@storage_bp.route('/upload-url', methods=['POST'])
def generate_upload_url():
    """Generate a signed URL for direct file upload.
    
    Returns:
        JSON response with upload URL
    """
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({
                "success": False,
                "error": "Missing filename",
                "error_code": "MISSING_FILENAME"
            }), 400
        
        filename = data['filename']
        storage_path = data.get('storage_path', 'user_uploads')
        user_id = data.get('user_id')
        project_id = data.get('project_id')
        expiration_hours = data.get('expiration_hours', 1)
        
        # Generate unique file path
        storage_manager = get_storage_manager()
        
        # Get storage path template
        if storage_path not in storage_manager.STORAGE_PATHS:
            return jsonify({
                "success": False,
                "error": f"Invalid storage path: {storage_path}",
                "error_code": "INVALID_PATH"
            }), 400
        
        # Format storage path
        path_template = storage_manager.STORAGE_PATHS[storage_path]
        if user_id:
            path_template = path_template.format(user_id=user_id)
        if project_id:
            path_template = path_template.format(project_id=project_id)
        
        # Generate unique filename
        unique_path = storage_manager._generate_unique_filename(filename, path_template)
        
        # Generate signed URL for PUT operation
        result = storage_manager.generate_signed_url(unique_path, expiration_hours, 'PUT')
        
        if result['success']:
            return jsonify({
                "success": True,
                "upload_url": result['signed_url'],
                "file_path": unique_path,
                "expiration": result['expiration'],
                "method": "PUT"
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "error_code": result['error_code']
            }), 500
    except Exception as e:
        logger.error(f"Error in upload URL endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }), 500

def _is_authorized_for_file(file_path: str) -> bool:
    """Check if the current user is authorized to access a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if authorized, False otherwise
    """
    # This is a placeholder implementation
    # In production, implement proper authentication and authorization
    
    # For now, allow access to all files
    # You should implement logic based on:
    # - User authentication
    # - File ownership
    # - User roles and permissions
    # - Path-based access control
    
    return True

def _is_authorized_for_path(path_prefix: str) -> bool:
    """Check if the current user is authorized to access a path.
    
    Args:
        path_prefix: Path prefix to check
        
    Returns:
        True if authorized, False otherwise
    """
    # This is a placeholder implementation
    # In production, implement proper path-based authorization
    
    return True

# Error handlers
@storage_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "error_code": "ENDPOINT_NOT_FOUND"
    }), 404

@storage_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "error_code": "METHOD_NOT_ALLOWED"
    }), 405

@storage_bp.errorhandler(413)
def payload_too_large(error):
    """Handle 413 errors (file too large)."""
    return jsonify({
        "success": False,
        "error": "File too large",
        "error_code": "FILE_TOO_LARGE"
    }), 413

@storage_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "error_code": "INTERNAL_ERROR"
    }), 500

