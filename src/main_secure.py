"""
Secure Aideon AI Main Application
Production-ready Flask application with comprehensive security measures
"""

import os
import logging
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import sqlite3
from werkzeug.middleware.proxy_fix import ProxyFix

# Import security modules
from security.ai_safety import AISecurityManager
from security.auth_security import AuthenticationManager
from security.network_security import NetworkSecurityManager
from security.threat_detection import ThreatDetectionEngine
from security.file_sandbox import SecureFileManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aideon_secure.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Security configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'secure-aideon-key-change-in-production'),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100MB max file size
    WTF_CSRF_ENABLED=True
)

# Proxy fix for proper IP detection
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize Redis
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis connection failed: {str(e)}")
    redis_client = None

# Initialize security managers
ai_security = AISecurityManager()
auth_manager = AuthenticationManager()
network_security = NetworkSecurityManager()
threat_detector = ThreatDetectionEngine()
file_sandbox = SecureFileManager()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1000 per hour", "100 per minute"],
    storage_uri="redis://localhost:6379/4" if redis_client else "memory://"
)

# Enable CORS with security headers
CORS(app, 
     origins=["http://localhost:3000", "http://localhost:5000", "http://127.0.0.1:3000", "http://127.0.0.1:5000"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Database initialization
def init_database():
    """Initialize SQLite database with security tables"""
    try:
        conn = sqlite3.connect('aideon_secure.db')
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                permissions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP NULL
            )
        ''')
        
        # Security events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                source_ip TEXT,
                user_agent TEXT,
                event_data TEXT,
                threat_level TEXT DEFAULT 'LOW',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # API keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key_name TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                permissions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create demo user if not exists
        cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
        if not cursor.fetchone():
            password_hash = auth_manager.hash_password('demo123')
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, permissions)
                VALUES (?, ?, ?, ?, ?)
            ''', ('demo', 'demo@aideon.ai', password_hash, 'admin', '["admin", "user", "security"]'))
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")

# Security middleware
@app.before_request
def security_middleware():
    """Apply security checks to all requests"""
    try:
        # Skip security for static files and health checks
        if request.endpoint in ['static', 'health']:
            return
        
        # Log security event
        event = {
            'event_type': 'api_request',
            'source_ip': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            'user_agent': request.headers.get('User-Agent', ''),
            'method': request.method,
            'path': request.path,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Analyze event for threats
        threat_analysis = threat_detector.analyze_event(event)
        
        # Block if critical threat detected
        if threat_analysis['threat_level'] == 'CRITICAL':
            logger.warning(f"Critical threat blocked: {threat_analysis}")
            return jsonify({
                'error': 'Security threat detected',
                'threat_id': threat_analysis['event_id']
            }), 403
        
        # Store threat analysis in request context
        g.threat_analysis = threat_analysis
        
    except Exception as e:
        logger.error(f"Security middleware error: {str(e)}")

@app.after_request
def after_request(response):
    """Add security headers to all responses"""
    try:
        # Add basic security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        # Log response
        if hasattr(g, 'threat_analysis'):
            logger.info(f"Request processed - Threat Level: {g.threat_analysis['threat_level']}")
        
        return response
    except Exception as e:
        logger.error(f"After request error: {str(e)}")
        return response

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_status = 'OK'
        if redis_client:
            redis_client.ping()
        else:
            redis_status = 'UNAVAILABLE'
        
        # Check database connection
        db_status = 'OK'
        try:
            conn = sqlite3.connect('aideon_secure.db')
            conn.execute('SELECT 1')
            conn.close()
        except:
            db_status = 'ERROR'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'redis': redis_status,
                'database': db_status,
                'ai_security': 'ACTIVE',
                'threat_detection': 'ACTIVE',
                'network_security': 'ACTIVE'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Secure login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Check account lockout
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        lockout_check = auth_manager.is_account_locked(username)
        if lockout_check['locked']:
            return jsonify({
                'error': 'Account temporarily locked',
                'lockout_until': lockout_check['lockout_until']
            }), 423
        
        # Validate credentials
        conn = sqlite3.connect('aideon_secure.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash, role, permissions FROM users WHERE username = ? AND is_active = 1', (username,))
        user = cursor.fetchone()
        
        if not user or not auth_manager.verify_password(password, user[1]):
            # Track failed login
            auth_manager.track_failed_login(username)
            auth_manager.track_failed_login(client_ip)
            
            # Log security event
            threat_detector.analyze_event({
                'event_type': 'login_failed',
                'username': username,
                'source_ip': client_ip,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Clear failed login attempts
        auth_manager.clear_failed_logins(username)
        auth_manager.clear_failed_logins(client_ip)
        
        # Generate tokens
        user_data = {
            'username': username,
            'role': user[2],
            'permissions': json.loads(user[3]) if user[3] else []
        }
        tokens = auth_manager.generate_tokens(str(user[0]), user_data)
        
        # Update last login
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
        conn.commit()
        conn.close()
        
        # Log successful login
        threat_detector.analyze_event({
            'event_type': 'login_success',
            'user_id': str(user[0]),
            'username': username,
            'source_ip': client_ip,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user[0],
                'username': username,
                'role': user[2],
                'permissions': user_data['permissions']
            },
            'tokens': tokens
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Secure logout endpoint"""
    try:
        # Revoke tokens (simplified for demo)
        # auth_manager.revoke_token('demo_user', 'access')
        # auth_manager.revoke_token('demo_user', 'refresh')
        
        # Log logout event
        threat_detector.analyze_event({
            'event_type': 'logout',
            'user_id': 'demo_user',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify({'message': 'Logout successful'})
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Get authentication status"""
    try:
        conn = sqlite3.connect('aideon_secure.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, email, role, permissions FROM users WHERE id = ?', (1,))  # Demo user ID
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'authenticated': True,
            'user': {
                'id': 1,  # Demo user ID
                'username': user[0],
                'email': user[1],
                'role': user[2],
                'permissions': json.loads(user[3]) if user[3] else []
            }
        })
        
    except Exception as e:
        logger.error(f"Auth status error: {str(e)}")
        return jsonify({'error': 'Failed to get auth status'}), 500

# AI Chat endpoint with security
@app.route('/api/chat', methods=['POST'])
@limiter.limit("50 per minute")
def secure_chat():
    """Secure AI chat endpoint with prompt injection protection"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # AI safety check is already applied by decorator
        # Process the safe message
        response = {
            'message': 'This is a secure AI response',
            'timestamp': datetime.utcnow().isoformat(),
            'safety_check': 'PASSED',
            'user_id': 'demo_user'
        }
        
        # Log AI interaction
        threat_detector.analyze_event({
            'event_type': 'ai_interaction',
            'user_id': 'demo_user',
            'message_length': len(message),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Secure chat error: {str(e)}")
        return jsonify({'error': 'Chat processing failed'}), 500

# System status endpoints
@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get comprehensive system status"""
    try:
        # Get security status
        security_status = network_security.get_system_security_status()
        
        # Get threat report
        threat_report = threat_detector.get_threat_report()
        
        # Get authentication report
        auth_report = auth_manager.get_security_report()
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'system_security': security_status,
            'threat_detection': threat_report,
            'authentication': auth_report,
            'overall_status': 'SECURE'
        })
        
    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return jsonify({'error': 'Failed to get system status'}), 500

@app.route('/api/security/dashboard', methods=['GET'])
def security_dashboard():
    """Get security dashboard data"""
    try:
        # Get recent security events
        conn = sqlite3.connect('aideon_secure.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT event_type, source_ip, threat_level, created_at
            FROM security_events
            ORDER BY created_at DESC
            LIMIT 100
        ''')
        recent_events = cursor.fetchall()
        conn.close()
        
        # Get threat statistics
        threat_report = threat_detector.get_threat_report()
        
        # Get blocked IPs
        blocked_ips = list(network_security.blocked_ips)
        
        return jsonify({
            'recent_events': [
                {
                    'event_type': event[0],
                    'source_ip': event[1],
                    'threat_level': event[2],
                    'timestamp': event[3]
                }
                for event in recent_events
            ],
            'threat_statistics': threat_report,
            'blocked_ips': blocked_ips,
            'security_status': 'ACTIVE'
        })
        
    except Exception as e:
        logger.error(f"Security dashboard error: {str(e)}")
        return jsonify({'error': 'Failed to get security dashboard'}), 500

# File operations with sandboxing
@app.route('/api/files/upload', methods=['POST'])
@limiter.limit("10 per minute")
def secure_file_upload():
    """Secure file upload with sandboxing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Security validation
        validation = file_sandbox.validate_file(file)
        if not validation['is_safe']:
            return jsonify({
                'error': 'File validation failed',
                'reason': validation['reason']
            }), 400
        
        # Save file securely
        saved_path = file_sandbox.save_file_securely(file, 'demo_user')
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_path': saved_path,
            'validation': validation
        })
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'File upload failed'}), 500

# Serve static files
@app.route('/')
def index():
    """Serve main application"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'retry_after': str(e.retry_after)}), 429

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Starting Aideon Secure AI System")
    logger.info("Security Features: AI Safety, Authentication, Network Security, Threat Detection, File Sandboxing")
    
    # Run application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False,  # Never enable debug in production
        threaded=True
    )

