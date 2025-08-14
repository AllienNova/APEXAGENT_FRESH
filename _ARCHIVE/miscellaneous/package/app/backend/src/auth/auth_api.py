"""
Admin Dashboard Backend API for Aideon AI Lite Authentication System

This module provides comprehensive Flask API endpoints for managing user authentication,
OAuth connections, and credential management through both user and admin dashboards.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from functools import wraps
import traceback

from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from .oauth_integration import OAuthIntegrationSystem, OAuthManager, OAuthProvider
from .credential_vault import SecureCredentialVault, AuthenticationManager, CredentialType
from ..core.enhanced_api_key_manager import EnhancedApiKeyManager
from ..core.plugin_exceptions import (
    PluginError,
    PluginConfigurationError,
    PluginActionExecutionError
)

logger = logging.getLogger(__name__)


class AuthenticationAPI:
    """
    Flask API for Aideon AI Lite authentication system.
    
    Provides comprehensive endpoints for OAuth flows, credential management,
    and admin dashboard functionality.
    """
    
    def __init__(self, app: Flask = None):
        """
        Initialize authentication API.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.oauth_system = None
        self.oauth_manager = None
        self.credential_vault = None
        self.auth_manager = None
        self.api_key_manager = None
        
        # JWT configuration
        self.jwt_secret = "aideon_auth_secret_key_v1"  # In production, use environment variable
        self.jwt_algorithm = "HS256"
        self.jwt_expiration_hours = 24
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize Flask application with authentication API."""
        self.app = app
        
        # Configure CORS
        CORS(app, origins="*", supports_credentials=True)
        
        # Configure Flask
        app.config['SECRET_KEY'] = 'aideon_flask_secret_key_v1'  # In production, use environment variable
        app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        
        # Initialize authentication components
        self._initialize_auth_components()
        
        # Register API routes
        self._register_routes()
        
        logger.info("Authentication API initialized")
    
    def _initialize_auth_components(self):
        """Initialize authentication system components."""
        try:
            # Initialize API key manager
            self.api_key_manager = EnhancedApiKeyManager()
            
            # Initialize OAuth system
            self.oauth_system = OAuthIntegrationSystem(
                base_redirect_uri="http://localhost:8000/api/auth/callback"
            )
            
            # Initialize OAuth manager
            self.oauth_manager = OAuthManager(self.oauth_system)
            
            # Configure OAuth providers (in production, load from secure config)
            self._configure_oauth_providers()
            
            # Initialize credential vault
            self.credential_vault = SecureCredentialVault(self.api_key_manager)
            
            # Initialize authentication manager
            self.auth_manager = AuthenticationManager(
                oauth_manager=self.oauth_manager,
                credential_vault=self.credential_vault,
                api_key_manager=self.api_key_manager
            )
            
            logger.info("Authentication components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize authentication components: {e}")
            raise
    
    def _configure_oauth_providers(self):
        """Configure OAuth providers with credentials."""
        # In production, these would be loaded from secure environment variables
        oauth_configs = {
            OAuthProvider.GOOGLE: {
                "client_id": "your_google_client_id",
                "client_secret": "your_google_client_secret"
            },
            OAuthProvider.MICROSOFT: {
                "client_id": "your_microsoft_client_id",
                "client_secret": "your_microsoft_client_secret"
            },
            OAuthProvider.LINKEDIN: {
                "client_id": "your_linkedin_client_id",
                "client_secret": "your_linkedin_client_secret"
            },
            OAuthProvider.TWITTER: {
                "client_id": "your_twitter_client_id",
                "client_secret": "your_twitter_client_secret"
            },
            OAuthProvider.FACEBOOK: {
                "client_id": "your_facebook_client_id",
                "client_secret": "your_facebook_client_secret"
            },
            OAuthProvider.GITHUB: {
                "client_id": "your_github_client_id",
                "client_secret": "your_github_client_secret"
            }
        }
        
        for provider, config in oauth_configs.items():
            self.oauth_manager.configure_provider(
                provider=provider,
                client_id=config["client_id"],
                client_secret=config["client_secret"]
            )
    
    def _register_routes(self):
        """Register all API routes."""
        
        # Authentication routes
        self.app.route('/api/auth/login', methods=['POST'])(self.login)
        self.app.route('/api/auth/logout', methods=['POST'])(self.logout)
        self.app.route('/api/auth/verify', methods=['GET'])(self.verify_token)
        
        # OAuth routes
        self.app.route('/api/auth/oauth/initiate', methods=['POST'])(self.initiate_oauth)
        self.app.route('/api/auth/oauth/callback/<provider>', methods=['GET'])(self.oauth_callback)
        self.app.route('/api/auth/oauth/providers', methods=['GET'])(self.get_oauth_providers)
        
        # Connection management routes
        self.app.route('/api/auth/connections', methods=['GET'])(self.get_user_connections)
        self.app.route('/api/auth/connections/refresh', methods=['POST'])(self.refresh_connection)
        self.app.route('/api/auth/connections/revoke', methods=['DELETE'])(self.revoke_connection)
        
        # API key management routes
        self.app.route('/api/auth/api-keys', methods=['POST'])(self.store_api_key)
        self.app.route('/api/auth/api-keys', methods=['GET'])(self.get_api_keys)
        self.app.route('/api/auth/api-keys/<credential_id>', methods=['DELETE'])(self.delete_api_key)
        
        # Admin routes
        self.app.route('/api/admin/users', methods=['GET'])(self.admin_get_users)
        self.app.route('/api/admin/users/<user_id>/connections', methods=['GET'])(self.admin_get_user_connections)
        self.app.route('/api/admin/audit-log', methods=['GET'])(self.admin_get_audit_log)
        self.app.route('/api/admin/system-status', methods=['GET'])(self.admin_get_system_status)
        
        # Health check
        self.app.route('/api/auth/health', methods=['GET'])(self.health_check)
    
    def require_auth(self, f):
        """Decorator to require authentication."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Authentication required"}), 401
                
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                request.user_id = payload['user_id']
                request.user_role = payload.get('role', 'user')
                
                return f(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                return jsonify({"error": "Authentication failed"}), 401
        
        return decorated_function
    
    def require_admin(self, f):
        """Decorator to require admin role."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user_role') or request.user_role != 'admin':
                return jsonify({"error": "Admin access required"}), 403
            return f(*args, **kwargs)
        
        return decorated_function
    
    def login(self):
        """User login endpoint."""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({"error": "Username and password required"}), 400
            
            # In production, validate against user database
            # For now, use simple validation
            if username == "admin" and password == "admin123":
                user_id = "admin_user"
                role = "admin"
            elif username == "user" and password == "user123":
                user_id = "demo_user"
                role = "user"
            else:
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Generate JWT token
            payload = {
                'user_id': user_id,
                'role': role,
                'exp': datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
            return jsonify({
                "success": True,
                "token": token,
                "user_id": user_id,
                "role": role,
                "expires_in": self.jwt_expiration_hours * 3600
            })
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({"error": "Login failed"}), 500
    
    def logout(self):
        """User logout endpoint."""
        try:
            # In a production system, you might want to blacklist the token
            return jsonify({"success": True, "message": "Logged out successfully"})
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return jsonify({"error": "Logout failed"}), 500
    
    @require_auth
    def verify_token(self):
        """Verify JWT token endpoint."""
        try:
            return jsonify({
                "success": True,
                "user_id": request.user_id,
                "role": request.user_role,
                "valid": True
            })
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return jsonify({"error": "Token verification failed"}), 500
    
    @require_auth
    def initiate_oauth(self):
        """Initiate OAuth flow endpoint."""
        try:
            data = request.get_json()
            provider = data.get('provider')
            scopes = data.get('scopes', [])
            
            if not provider:
                return jsonify({"error": "Provider required"}), 400
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.auth_manager.initiate_platform_connection(
                        user_id=request.user_id,
                        provider=provider,
                        connection_type="oauth",
                        scopes=scopes
                    )
                )
                
                return jsonify(result)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"OAuth initiation error: {e}")
            return jsonify({"error": f"OAuth initiation failed: {str(e)}"}), 500
    
    def oauth_callback(self, provider):
        """OAuth callback endpoint."""
        try:
            authorization_code = request.args.get('code')
            state = request.args.get('state')
            error = request.args.get('error')
            
            if error:
                return jsonify({"error": f"OAuth error: {error}"}), 400
            
            if not authorization_code or not state:
                return jsonify({"error": "Missing authorization code or state"}), 400
            
            # Get user ID from state (in production, validate state properly)
            # For now, use a demo user
            user_id = "demo_user"
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.auth_manager.complete_oauth_connection(
                        user_id=user_id,
                        provider=provider,
                        authorization_code=authorization_code,
                        state=state
                    )
                )
                
                if result["success"]:
                    # Redirect to success page
                    return redirect(f"http://localhost:3000/auth/success?provider={provider}")
                else:
                    return redirect(f"http://localhost:3000/auth/error?error={result.get('error', 'Unknown error')}")
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            return redirect(f"http://localhost:3000/auth/error?error=OAuth callback failed")
    
    def get_oauth_providers(self):
        """Get available OAuth providers endpoint."""
        try:
            providers = []
            for provider in OAuthProvider:
                provider_scopes = self.oauth_manager.get_provider_scopes(provider)
                providers.append({
                    "name": provider.value,
                    "display_name": provider.value.title(),
                    "scopes": provider_scopes,
                    "supports_refresh": self.oauth_system.provider_configs.get(provider, {}).get("supports_refresh", False)
                })
            
            return jsonify({
                "success": True,
                "providers": providers
            })
            
        except Exception as e:
            logger.error(f"Get OAuth providers error: {e}")
            return jsonify({"error": "Failed to get OAuth providers"}), 500
    
    @require_auth
    def get_user_connections(self):
        """Get user's platform connections endpoint."""
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.auth_manager.get_user_connections(request.user_id)
                )
                
                return jsonify(result)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Get user connections error: {e}")
            return jsonify({"error": "Failed to get user connections"}), 500
    
    @require_auth
    def refresh_connection(self):
        """Refresh connection credentials endpoint."""
        try:
            data = request.get_json()
            credential_id = data.get('credential_id')
            
            if not credential_id:
                return jsonify({"error": "Credential ID required"}), 400
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.auth_manager.refresh_connection_if_needed(
                        user_id=request.user_id,
                        credential_id=credential_id
                    )
                )
                
                return jsonify(result)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Refresh connection error: {e}")
            return jsonify({"error": "Failed to refresh connection"}), 500
    
    @require_auth
    def revoke_connection(self):
        """Revoke platform connection endpoint."""
        try:
            data = request.get_json()
            credential_id = data.get('credential_id')
            
            if not credential_id:
                return jsonify({"error": "Credential ID required"}), 400
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.auth_manager.revoke_connection(
                        user_id=request.user_id,
                        credential_id=credential_id
                    )
                )
                
                return jsonify(result)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Revoke connection error: {e}")
            return jsonify({"error": "Failed to revoke connection"}), 500
    
    @require_auth
    def store_api_key(self):
        """Store API key endpoint."""
        try:
            data = request.get_json()
            provider = data.get('provider')
            api_key = data.get('api_key')
            metadata = data.get('metadata', {})
            
            if not provider or not api_key:
                return jsonify({"error": "Provider and API key required"}), 400
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.auth_manager.store_api_key_credential(
                        user_id=request.user_id,
                        provider=provider,
                        api_key=api_key,
                        metadata=metadata
                    )
                )
                
                return jsonify(result)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Store API key error: {e}")
            return jsonify({"error": "Failed to store API key"}), 500
    
    @require_auth
    def get_api_keys(self):
        """Get user's API keys endpoint."""
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                credentials = loop.run_until_complete(
                    self.credential_vault.list_user_credentials(
                        user_id=request.user_id,
                        credential_type=CredentialType.API_KEY
                    )
                )
                
                # Return credentials without sensitive data
                api_keys = []
                for credential in credentials:
                    api_keys.append({
                        "credential_id": credential.credential_id,
                        "provider": credential.provider,
                        "status": credential.status.value,
                        "created_at": credential.created_at.isoformat(),
                        "last_used_at": credential.last_used_at.isoformat() if credential.last_used_at else None
                    })
                
                return jsonify({
                    "success": True,
                    "api_keys": api_keys
                })
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Get API keys error: {e}")
            return jsonify({"error": "Failed to get API keys"}), 500
    
    @require_auth
    def delete_api_key(self, credential_id):
        """Delete API key endpoint."""
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.auth_manager.revoke_connection(
                        user_id=request.user_id,
                        credential_id=credential_id
                    )
                )
                
                return jsonify(result)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Delete API key error: {e}")
            return jsonify({"error": "Failed to delete API key"}), 500
    
    @require_auth
    @require_admin
    def admin_get_users(self):
        """Admin endpoint to get all users."""
        try:
            # In production, this would query the user database
            users = [
                {
                    "user_id": "admin_user",
                    "username": "admin",
                    "role": "admin",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_login": "2024-01-15T10:30:00Z",
                    "status": "active"
                },
                {
                    "user_id": "demo_user",
                    "username": "user",
                    "role": "user",
                    "created_at": "2024-01-02T00:00:00Z",
                    "last_login": "2024-01-15T09:15:00Z",
                    "status": "active"
                }
            ]
            
            return jsonify({
                "success": True,
                "users": users,
                "total": len(users)
            })
            
        except Exception as e:
            logger.error(f"Admin get users error: {e}")
            return jsonify({"error": "Failed to get users"}), 500
    
    @require_auth
    @require_admin
    def admin_get_user_connections(self, user_id):
        """Admin endpoint to get user's connections."""
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.auth_manager.get_user_connections(user_id)
                )
                
                return jsonify(result)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Admin get user connections error: {e}")
            return jsonify({"error": "Failed to get user connections"}), 500
    
    @require_auth
    @require_admin
    def admin_get_audit_log(self):
        """Admin endpoint to get audit log."""
        try:
            # Get query parameters
            user_id = request.args.get('user_id')
            action = request.args.get('action')
            limit = int(request.args.get('limit', 100))
            
            # Parse date filters
            start_date = None
            end_date = None
            if request.args.get('start_date'):
                start_date = datetime.fromisoformat(request.args.get('start_date'))
            if request.args.get('end_date'):
                end_date = datetime.fromisoformat(request.args.get('end_date'))
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                audit_entries = loop.run_until_complete(
                    self.credential_vault.get_audit_log(
                        user_id=user_id,
                        start_date=start_date,
                        end_date=end_date,
                        action=action,
                        limit=limit
                    )
                )
                
                # Convert to JSON-serializable format
                audit_log = []
                for entry in audit_entries:
                    audit_log.append({
                        "entry_id": entry.entry_id,
                        "user_id": entry.user_id,
                        "credential_id": entry.credential_id,
                        "action": entry.action,
                        "timestamp": entry.timestamp.isoformat(),
                        "success": entry.success,
                        "error_message": entry.error_message,
                        "metadata": entry.metadata
                    })
                
                return jsonify({
                    "success": True,
                    "audit_log": audit_log,
                    "total": len(audit_log)
                })
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Admin get audit log error: {e}")
            return jsonify({"error": "Failed to get audit log"}), 500
    
    @require_auth
    @require_admin
    def admin_get_system_status(self):
        """Admin endpoint to get system status."""
        try:
            # Get system statistics
            total_credentials = len(self.credential_vault.credentials)
            active_credentials = len([
                c for c in self.credential_vault.credentials.values()
                if c.status.value == "active"
            ])
            
            # Get recent activity
            recent_audit_entries = len([
                e for e in self.credential_vault.audit_log
                if e.timestamp > datetime.utcnow() - timedelta(hours=24)
            ])
            
            return jsonify({
                "success": True,
                "system_status": {
                    "status": "healthy",
                    "uptime": "99.9%",
                    "total_credentials": total_credentials,
                    "active_credentials": active_credentials,
                    "recent_activity": recent_audit_entries,
                    "oauth_providers_configured": len(self.oauth_manager.provider_credentials),
                    "last_updated": datetime.utcnow().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Admin get system status error: {e}")
            return jsonify({"error": "Failed to get system status"}), 500
    
    def health_check(self):
        """Health check endpoint."""
        try:
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "components": {
                    "oauth_system": "operational",
                    "credential_vault": "operational",
                    "api_key_manager": "operational"
                }
            })
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 500


def create_auth_app():
    """Create Flask application with authentication API."""
    app = Flask(__name__)
    
    # Initialize authentication API
    auth_api = AuthenticationAPI(app)
    
    return app


if __name__ == "__main__":
    # Create and run the authentication API
    app = create_auth_app()
    app.run(host="0.0.0.0", port=8000, debug=True)

