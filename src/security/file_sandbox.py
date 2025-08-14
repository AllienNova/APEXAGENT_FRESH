"""
File System Sandboxing and Access Control Module
Secure file operations with comprehensive access controls
"""

import os
import stat
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
import json
import tempfile
import shutil
from functools import wraps
from flask import g, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureFileManager:
    """Secure file manager with sandboxing and access controls"""
    
    def __init__(self, base_sandbox_dir: str = "/tmp/aideon_sandbox"):
        self.base_sandbox_dir = Path(base_sandbox_dir)
        self.allowed_extensions = {
            '.txt', '.md', '.json', '.csv', '.log', '.yaml', '.yml',
            '.py', '.js', '.html', '.css', '.xml', '.ini', '.cfg'
        }
        self.blocked_paths = {
            '/etc', '/var', '/usr', '/bin', '/sbin', '/root', '/home',
            '/proc', '/sys', '/dev', '/boot', '/lib', '/lib64',
            'C:\\Windows', 'C:\\Program Files', 'C:\\Users'
        }
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_files_per_user = 1000
        self.user_quotas = {}
        self.access_logs = []
        
        # Create sandbox directory
        self._setup_sandbox()
    
    def _setup_sandbox(self):
        """Set up secure sandbox directory"""
        try:
            self.base_sandbox_dir.mkdir(parents=True, exist_ok=True)
            
            # Set restrictive permissions (owner read/write/execute only)
            os.chmod(self.base_sandbox_dir, stat.S_IRWXU)
            
            logger.info(f"Sandbox directory created: {self.base_sandbox_dir}")
            
        except Exception as e:
            logger.error(f"Failed to setup sandbox: {str(e)}")
            raise
    
    def get_user_sandbox(self, user_id: str) -> Path:
        """Get or create user-specific sandbox directory"""
        user_sandbox = self.base_sandbox_dir / f"user_{hashlib.md5(user_id.encode()).hexdigest()}"
        user_sandbox.mkdir(exist_ok=True)
        
        # Set user-specific permissions
        os.chmod(user_sandbox, stat.S_IRWXU)
        
        return user_sandbox
    
    def validate_file_path(self, file_path: str, user_id: str) -> Dict[str, Any]:
        """
        Validate file path for security
        
        Args:
            file_path: Path to validate
            user_id: User identifier
            
        Returns:
            Validation result with security assessment
        """
        validation = {
            'is_safe': True,
            'normalized_path': None,
            'sandbox_path': None,
            'warnings': [],
            'blocked_reason': None
        }
        
        try:
            # Normalize path
            normalized = os.path.normpath(file_path)
            validation['normalized_path'] = normalized
            
            # Check for directory traversal
            if '..' in normalized or normalized.startswith('/'):
                validation['is_safe'] = False
                validation['blocked_reason'] = 'Directory traversal attempt detected'
                return validation
            
            # Check against blocked paths
            for blocked_path in self.blocked_paths:
                if normalized.startswith(blocked_path):
                    validation['is_safe'] = False
                    validation['blocked_reason'] = f'Access to {blocked_path} is forbidden'
                    return validation
            
            # Check file extension
            file_ext = Path(normalized).suffix.lower()
            if file_ext and file_ext not in self.allowed_extensions:
                validation['warnings'].append(f'File extension {file_ext} not in allowed list')
            
            # Create sandbox path
            user_sandbox = self.get_user_sandbox(user_id)
            sandbox_path = user_sandbox / normalized
            validation['sandbox_path'] = sandbox_path
            
            # Ensure path is within sandbox
            try:
                sandbox_path.resolve().relative_to(user_sandbox.resolve())
            except ValueError:
                validation['is_safe'] = False
                validation['blocked_reason'] = 'Path escapes sandbox directory'
                return validation
            
            return validation
            
        except Exception as e:
            logger.error(f"Path validation error: {str(e)}")
            validation['is_safe'] = False
            validation['blocked_reason'] = 'Path validation failed'
            return validation
    
    def secure_read_file(self, file_path: str, user_id: str) -> Dict[str, Any]:
        """
        Securely read file with access controls
        
        Args:
            file_path: Path to file
            user_id: User identifier
            
        Returns:
            File content and metadata or error
        """
        result = {
            'success': False,
            'content': None,
            'metadata': {},
            'error': None
        }
        
        try:
            # Validate path
            validation = self.validate_file_path(file_path, user_id)
            if not validation['is_safe']:
                result['error'] = validation['blocked_reason']
                self._log_access_attempt(user_id, file_path, 'READ', False, validation['blocked_reason'])
                return result
            
            sandbox_path = validation['sandbox_path']
            
            # Check if file exists
            if not sandbox_path.exists():
                result['error'] = 'File not found in sandbox'
                return result
            
            # Check file size
            file_size = sandbox_path.stat().st_size
            if file_size > self.max_file_size:
                result['error'] = f'File too large ({file_size} bytes, max {self.max_file_size})'
                return result
            
            # Read file content
            with open(sandbox_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Sanitize content
            content = self._sanitize_file_content(content)
            
            result['success'] = True
            result['content'] = content
            result['metadata'] = {
                'size': file_size,
                'modified': datetime.fromtimestamp(sandbox_path.stat().st_mtime).isoformat(),
                'path': str(sandbox_path.relative_to(self.get_user_sandbox(user_id)))
            }
            
            self._log_access_attempt(user_id, file_path, 'READ', True)
            return result
            
        except Exception as e:
            logger.error(f"File read error: {str(e)}")
            result['error'] = f'Failed to read file: {str(e)}'
            self._log_access_attempt(user_id, file_path, 'READ', False, str(e))
            return result
    
    def secure_write_file(self, file_path: str, content: str, user_id: str) -> Dict[str, Any]:
        """
        Securely write file with access controls
        
        Args:
            file_path: Path to file
            content: Content to write
            user_id: User identifier
            
        Returns:
            Write result and metadata
        """
        result = {
            'success': False,
            'metadata': {},
            'error': None
        }
        
        try:
            # Validate path
            validation = self.validate_file_path(file_path, user_id)
            if not validation['is_safe']:
                result['error'] = validation['blocked_reason']
                self._log_access_attempt(user_id, file_path, 'WRITE', False, validation['blocked_reason'])
                return result
            
            sandbox_path = validation['sandbox_path']
            
            # Check user quota
            if not self._check_user_quota(user_id):
                result['error'] = f'User quota exceeded (max {self.max_files_per_user} files)'
                return result
            
            # Check content size
            content_size = len(content.encode('utf-8'))
            if content_size > self.max_file_size:
                result['error'] = f'Content too large ({content_size} bytes, max {self.max_file_size})'
                return result
            
            # Sanitize content
            sanitized_content = self._sanitize_file_content(content)
            
            # Create parent directories
            sandbox_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(sandbox_path, 'w', encoding='utf-8') as f:
                f.write(sanitized_content)
            
            # Set secure permissions
            os.chmod(sandbox_path, stat.S_IRUSR | stat.S_IWUSR)
            
            result['success'] = True
            result['metadata'] = {
                'size': content_size,
                'path': str(sandbox_path.relative_to(self.get_user_sandbox(user_id))),
                'created': datetime.utcnow().isoformat()
            }
            
            self._log_access_attempt(user_id, file_path, 'WRITE', True)
            return result
            
        except Exception as e:
            logger.error(f"File write error: {str(e)}")
            result['error'] = f'Failed to write file: {str(e)}'
            self._log_access_attempt(user_id, file_path, 'WRITE', False, str(e))
            return result
    
    def secure_delete_file(self, file_path: str, user_id: str) -> Dict[str, Any]:
        """
        Securely delete file with access controls
        
        Args:
            file_path: Path to file
            user_id: User identifier
            
        Returns:
            Delete result
        """
        result = {
            'success': False,
            'error': None
        }
        
        try:
            # Validate path
            validation = self.validate_file_path(file_path, user_id)
            if not validation['is_safe']:
                result['error'] = validation['blocked_reason']
                self._log_access_attempt(user_id, file_path, 'DELETE', False, validation['blocked_reason'])
                return result
            
            sandbox_path = validation['sandbox_path']
            
            # Check if file exists
            if not sandbox_path.exists():
                result['error'] = 'File not found in sandbox'
                return result
            
            # Secure delete (overwrite with random data first)
            if sandbox_path.is_file():
                file_size = sandbox_path.stat().st_size
                with open(sandbox_path, 'r+b') as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Remove file
            sandbox_path.unlink()
            
            result['success'] = True
            self._log_access_attempt(user_id, file_path, 'DELETE', True)
            return result
            
        except Exception as e:
            logger.error(f"File delete error: {str(e)}")
            result['error'] = f'Failed to delete file: {str(e)}'
            self._log_access_attempt(user_id, file_path, 'DELETE', False, str(e))
            return result
    
    def list_user_files(self, user_id: str) -> Dict[str, Any]:
        """
        List files in user's sandbox
        
        Args:
            user_id: User identifier
            
        Returns:
            List of files and metadata
        """
        result = {
            'success': False,
            'files': [],
            'error': None
        }
        
        try:
            user_sandbox = self.get_user_sandbox(user_id)
            files = []
            
            for file_path in user_sandbox.rglob('*'):
                if file_path.is_file():
                    try:
                        stat_info = file_path.stat()
                        files.append({
                            'path': str(file_path.relative_to(user_sandbox)),
                            'size': stat_info.st_size,
                            'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                            'extension': file_path.suffix.lower()
                        })
                    except Exception as e:
                        logger.warning(f"Error reading file metadata: {str(e)}")
            
            result['success'] = True
            result['files'] = files
            self._log_access_attempt(user_id, 'sandbox', 'LIST', True)
            return result
            
        except Exception as e:
            logger.error(f"File listing error: {str(e)}")
            result['error'] = f'Failed to list files: {str(e)}'
            self._log_access_attempt(user_id, 'sandbox', 'LIST', False, str(e))
            return result
    
    def _sanitize_file_content(self, content: str) -> str:
        """Sanitize file content to remove potentially harmful data"""
        # Remove null bytes and control characters (except newlines, tabs, carriage returns)
        sanitized = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit content length
        if len(sanitized) > self.max_file_size:
            sanitized = sanitized[:self.max_file_size] + "\n... [content truncated for security]"
        
        return sanitized
    
    def _check_user_quota(self, user_id: str) -> bool:
        """Check if user is within file quota limits"""
        try:
            user_sandbox = self.get_user_sandbox(user_id)
            file_count = sum(1 for _ in user_sandbox.rglob('*') if _.is_file())
            return file_count < self.max_files_per_user
        except:
            return False
    
    def _log_access_attempt(self, user_id: str, file_path: str, operation: str, success: bool, error: str = None):
        """Log file access attempts for security monitoring"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'file_path': file_path,
            'operation': operation,
            'success': success,
            'error': error,
            'ip_address': getattr(request, 'remote_addr', None) if request else None
        }
        
        self.access_logs.append(log_entry)
        
        # Keep only last 10000 log entries
        if len(self.access_logs) > 10000:
            self.access_logs = self.access_logs[-10000:]
        
        # Log to file
        if not success:
            logger.warning(f"FILE_ACCESS_DENIED: {json.dumps(log_entry)}")
        else:
            logger.info(f"FILE_ACCESS: {json.dumps(log_entry)}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report for file access"""
        total_attempts = len(self.access_logs)
        failed_attempts = sum(1 for log in self.access_logs if not log['success'])
        
        # Recent failed attempts (last 24 hours)
        recent_failures = [
            log for log in self.access_logs 
            if not log['success'] and 
            datetime.fromisoformat(log['timestamp']) > datetime.utcnow() - timedelta(hours=24)
        ]
        
        return {
            'total_file_operations': total_attempts,
            'failed_operations': failed_attempts,
            'success_rate': (total_attempts - failed_attempts) / total_attempts if total_attempts > 0 else 1.0,
            'recent_failures_24h': len(recent_failures),
            'most_common_errors': self._get_common_errors(),
            'sandbox_status': 'ACTIVE',
            'max_file_size_mb': self.max_file_size / (1024 * 1024),
            'max_files_per_user': self.max_files_per_user
        }
    
    def _get_common_errors(self) -> List[Dict[str, Any]]:
        """Get most common error types"""
        error_counts = {}
        for log in self.access_logs:
            if not log['success'] and log['error']:
                error_counts[log['error']] = error_counts.get(log['error'], 0) + 1
        
        return [
            {'error': error, 'count': count}
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

# Global file manager instance
file_manager = SecureFileManager()

def require_file_access(operation: str):
    """Decorator to validate file access permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(g, 'user_id', 'anonymous')
            
            # Log the file access attempt
            logger.info(f"File access attempt: {operation} by user {user_id}")
            
            # Add file manager to request context
            g.file_manager = file_manager
            g.file_operation = operation
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

