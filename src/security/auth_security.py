"""
Authentication and Authorization Security Module
Comprehensive security for user authentication and access control
"""

import jwt
import bcrypt
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from functools import wraps
from flask import request, jsonify, g, current_app
import redis
import json
import re
from cryptography.fernet import Fernet
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration constants"""
    
    # JWT Configuration
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Password Requirements
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_DURATION = timedelta(minutes=30)
    MAX_REQUESTS_PER_MINUTE = 100
    MAX_REQUESTS_PER_HOUR = 1000
    
    # Session Security
    SESSION_TIMEOUT = timedelta(hours=8)
    REQUIRE_2FA = False  # Can be enabled for enhanced security
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

class AuthenticationManager:
    """Comprehensive authentication and authorization manager"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
        self.secret_key = self._get_or_create_secret_key()
        self.encryption_key = self._get_or_create_encryption_key()
        self.failed_attempts = {}
        self.active_sessions = {}
        self.security_events = []
        
    def _get_or_create_secret_key(self) -> str:
        """Get or create JWT secret key"""
        try:
            key = self.redis_client.get('jwt_secret_key')
            if not key:
                key = secrets.token_urlsafe(64)
                self.redis_client.set('jwt_secret_key', key)
            return key
        except:
            # Fallback to generated key if Redis unavailable
            return secrets.token_urlsafe(64)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        try:
            key = self.redis_client.get('encryption_key')
            if not key:
                key = base64.urlsafe_b64encode(Fernet.generate_key()).decode()
                self.redis_client.set('encryption_key', key)
            return base64.urlsafe_b64decode(key.encode())
        except:
            return Fernet.generate_key()
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength against security requirements
        
        Args:
            password: Password to validate
            
        Returns:
            Validation result with strength assessment
        """
        validation = {
            'is_valid': True,
            'strength_score': 0,
            'requirements_met': [],
            'requirements_failed': [],
            'suggestions': []
        }
        
        # Length check
        if len(password) >= SecurityConfig.MIN_PASSWORD_LENGTH:
            validation['requirements_met'].append('Minimum length')
            validation['strength_score'] += 20
        else:
            validation['is_valid'] = False
            validation['requirements_failed'].append(f'Minimum {SecurityConfig.MIN_PASSWORD_LENGTH} characters')
            validation['suggestions'].append(f'Use at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters')
        
        # Uppercase check
        if SecurityConfig.REQUIRE_UPPERCASE:
            if re.search(r'[A-Z]', password):
                validation['requirements_met'].append('Uppercase letter')
                validation['strength_score'] += 15
            else:
                validation['is_valid'] = False
                validation['requirements_failed'].append('Uppercase letter')
                validation['suggestions'].append('Include at least one uppercase letter')
        
        # Lowercase check
        if SecurityConfig.REQUIRE_LOWERCASE:
            if re.search(r'[a-z]', password):
                validation['requirements_met'].append('Lowercase letter')
                validation['strength_score'] += 15
            else:
                validation['is_valid'] = False
                validation['requirements_failed'].append('Lowercase letter')
                validation['suggestions'].append('Include at least one lowercase letter')
        
        # Digit check
        if SecurityConfig.REQUIRE_DIGITS:
            if re.search(r'[0-9]', password):
                validation['requirements_met'].append('Number')
                validation['strength_score'] += 15
            else:
                validation['is_valid'] = False
                validation['requirements_failed'].append('Number')
                validation['suggestions'].append('Include at least one number')
        
        # Special character check
        if SecurityConfig.REQUIRE_SPECIAL_CHARS:
            if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\?]', password):
                validation['requirements_met'].append('Special character')
                validation['strength_score'] += 15
            else:
                validation['is_valid'] = False
                validation['requirements_failed'].append('Special character')
                validation['suggestions'].append('Include at least one special character (!@#$%^&*)')
        
        # Additional strength checks
        if len(set(password)) > len(password) * 0.7:  # Character diversity
            validation['strength_score'] += 10
        
        if not re.search(r'(.)\1{2,}', password):  # No repeated characters
            validation['strength_score'] += 10
        
        # Common password check (basic)
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() not in common_passwords:
            validation['strength_score'] += 10
        else:
            validation['is_valid'] = False
            validation['requirements_failed'].append('Not a common password')
            validation['suggestions'].append('Avoid common passwords')
        
        return validation
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    
    def generate_tokens(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate JWT access and refresh tokens
        
        Args:
            user_id: User identifier
            user_data: Additional user data for token
            
        Returns:
            Dictionary with access and refresh tokens
        """
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'username': user_data.get('username'),
            'role': user_data.get('role', 'user'),
            'permissions': user_data.get('permissions', []),
            'iat': now,
            'exp': now + SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES,
            'type': 'access'
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'iat': now,
            'exp': now + SecurityConfig.JWT_REFRESH_TOKEN_EXPIRES,
            'type': 'refresh'
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=SecurityConfig.JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=SecurityConfig.JWT_ALGORITHM)
        
        # Store tokens in Redis for revocation capability
        try:
            self.redis_client.setex(f'access_token:{user_id}', 
                                  int(SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES.total_seconds()), 
                                  access_token)
            self.redis_client.setex(f'refresh_token:{user_id}', 
                                  int(SecurityConfig.JWT_REFRESH_TOKEN_EXPIRES.total_seconds()), 
                                  refresh_token)
        except Exception as e:
            logger.warning(f"Failed to store tokens in Redis: {str(e)}")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
        }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token payload or error information
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[SecurityConfig.JWT_ALGORITHM])
            
            # Check if token is revoked
            user_id = payload.get('user_id')
            token_type = payload.get('type', 'access')
            
            try:
                stored_token = self.redis_client.get(f'{token_type}_token:{user_id}')
                if stored_token != token:
                    return {'valid': False, 'error': 'Token revoked'}
            except:
                pass  # Continue if Redis unavailable
            
            return {'valid': True, 'payload': payload}
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return {'valid': False, 'error': 'Token verification failed'}
    
    def revoke_token(self, user_id: str, token_type: str = 'access'):
        """Revoke user token"""
        try:
            self.redis_client.delete(f'{token_type}_token:{user_id}')
        except Exception as e:
            logger.warning(f"Failed to revoke token: {str(e)}")
    
    def check_rate_limit(self, identifier: str, limit_type: str = 'general') -> Dict[str, Any]:
        """
        Check rate limiting for requests
        
        Args:
            identifier: IP address or user ID
            limit_type: Type of rate limit (login, general, api)
            
        Returns:
            Rate limit status
        """
        try:
            current_time = datetime.utcnow()
            minute_key = f'rate_limit:{limit_type}:{identifier}:minute:{current_time.strftime("%Y%m%d%H%M")}'
            hour_key = f'rate_limit:{limit_type}:{identifier}:hour:{current_time.strftime("%Y%m%d%H")}'
            
            # Get current counts
            minute_count = int(self.redis_client.get(minute_key) or 0)
            hour_count = int(self.redis_client.get(hour_key) or 0)
            
            # Check limits
            if limit_type == 'login':
                minute_limit = 10
                hour_limit = 50
            else:
                minute_limit = SecurityConfig.MAX_REQUESTS_PER_MINUTE
                hour_limit = SecurityConfig.MAX_REQUESTS_PER_HOUR
            
            if minute_count >= minute_limit:
                return {
                    'allowed': False,
                    'reason': 'Rate limit exceeded (per minute)',
                    'retry_after': 60 - current_time.second
                }
            
            if hour_count >= hour_limit:
                return {
                    'allowed': False,
                    'reason': 'Rate limit exceeded (per hour)',
                    'retry_after': 3600 - (current_time.minute * 60 + current_time.second)
                }
            
            # Increment counters
            pipe = self.redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            pipe.execute()
            
            return {
                'allowed': True,
                'remaining_minute': minute_limit - minute_count - 1,
                'remaining_hour': hour_limit - hour_count - 1
            }
            
        except Exception as e:
            logger.warning(f"Rate limit check failed: {str(e)}")
            return {'allowed': True}  # Allow if rate limiting fails
    
    def track_failed_login(self, identifier: str) -> Dict[str, Any]:
        """
        Track failed login attempts
        
        Args:
            identifier: IP address or username
            
        Returns:
            Account lockout status
        """
        try:
            key = f'failed_login:{identifier}'
            current_time = datetime.utcnow()
            
            # Get current failed attempts
            attempts_data = self.redis_client.get(key)
            if attempts_data:
                attempts_info = json.loads(attempts_data)
                attempts = attempts_info['count']
                first_attempt = datetime.fromisoformat(attempts_info['first_attempt'])
            else:
                attempts = 0
                first_attempt = current_time
            
            attempts += 1
            
            # Check if account should be locked
            if attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
                lockout_until = current_time + SecurityConfig.LOGIN_LOCKOUT_DURATION
                
                # Store lockout information
                lockout_data = {
                    'locked': True,
                    'lockout_until': lockout_until.isoformat(),
                    'attempts': attempts,
                    'first_attempt': first_attempt.isoformat()
                }
                
                self.redis_client.setex(key, 
                                      int(SecurityConfig.LOGIN_LOCKOUT_DURATION.total_seconds()),
                                      json.dumps(lockout_data))
                
                self._log_security_event('ACCOUNT_LOCKED', identifier, {
                    'attempts': attempts,
                    'lockout_duration': SecurityConfig.LOGIN_LOCKOUT_DURATION.total_seconds()
                })
                
                return {
                    'locked': True,
                    'lockout_until': lockout_until.isoformat(),
                    'attempts': attempts
                }
            else:
                # Store failed attempt
                attempt_data = {
                    'locked': False,
                    'count': attempts,
                    'first_attempt': first_attempt.isoformat(),
                    'last_attempt': current_time.isoformat()
                }
                
                self.redis_client.setex(key, 1800, json.dumps(attempt_data))  # 30 minutes
                
                return {
                    'locked': False,
                    'attempts': attempts,
                    'remaining_attempts': SecurityConfig.MAX_LOGIN_ATTEMPTS - attempts
                }
                
        except Exception as e:
            logger.error(f"Failed login tracking error: {str(e)}")
            return {'locked': False, 'attempts': 0}
    
    def clear_failed_logins(self, identifier: str):
        """Clear failed login attempts after successful login"""
        try:
            self.redis_client.delete(f'failed_login:{identifier}')
        except Exception as e:
            logger.warning(f"Failed to clear login attempts: {str(e)}")
    
    def is_account_locked(self, identifier: str) -> Dict[str, Any]:
        """Check if account is locked due to failed attempts"""
        try:
            key = f'failed_login:{identifier}'
            attempts_data = self.redis_client.get(key)
            
            if not attempts_data:
                return {'locked': False}
            
            attempts_info = json.loads(attempts_data)
            
            if attempts_info.get('locked'):
                lockout_until = datetime.fromisoformat(attempts_info['lockout_until'])
                if datetime.utcnow() < lockout_until:
                    return {
                        'locked': True,
                        'lockout_until': lockout_until.isoformat(),
                        'time_remaining': (lockout_until - datetime.utcnow()).total_seconds()
                    }
                else:
                    # Lockout expired, clear it
                    self.redis_client.delete(key)
                    return {'locked': False}
            
            return {'locked': False}
            
        except Exception as e:
            logger.error(f"Account lock check error: {str(e)}")
            return {'locked': False}
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        f = Fernet(self.encryption_key)
        return f.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_data.encode()).decode()
    
    def _log_security_event(self, event_type: str, identifier: str, details: Dict[str, Any]):
        """Log security events for monitoring"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'identifier': identifier,
            'details': details,
            'ip_address': getattr(request, 'remote_addr', None) if request else None,
            'user_agent': getattr(request, 'user_agent', None) if request else None
        }
        
        self.security_events.append(event)
        
        # Keep only last 10000 events
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-10000:]
        
        logger.warning(f"SECURITY_EVENT: {json.dumps(event)}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        recent_events = [
            event for event in self.security_events
            if datetime.fromisoformat(event['timestamp']) > datetime.utcnow() - timedelta(hours=24)
        ]
        
        event_types = {}
        for event in recent_events:
            event_type = event['event_type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            'total_security_events': len(self.security_events),
            'recent_events_24h': len(recent_events),
            'event_types': event_types,
            'authentication_status': 'SECURE',
            'rate_limiting_status': 'ACTIVE',
            'token_security': 'JWT_WITH_REVOCATION'
        }

# Global authentication manager
auth_manager = AuthenticationManager()

def require_auth(permissions: List[str] = None):
    """Decorator to require authentication and optional permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            token = auth_header.split(' ')[1]
            
            # Verify token
            token_result = auth_manager.verify_token(token)
            if not token_result['valid']:
                return jsonify({'error': token_result['error']}), 401
            
            # Add user info to request context
            g.user_id = token_result['payload']['user_id']
            g.user_role = token_result['payload'].get('role', 'user')
            g.user_permissions = token_result['payload'].get('permissions', [])
            
            # Check permissions if required
            if permissions:
                user_permissions = set(g.user_permissions)
                required_permissions = set(permissions)
                if not required_permissions.issubset(user_permissions):
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def add_security_headers(response):
    """Add security headers to response"""
    for header, value in SecurityConfig.SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

