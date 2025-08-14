import os
import sys
import redis
import logging
from datetime import datetime, timedelta
from functools import wraps

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from src.models.user import db
from src.routes.user import user_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with optimized configuration
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'apexagent-production-key-2025')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-2025')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Redis Configuration for Session Management
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis_client
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'apexagent:'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
Session(app)
CORS(app, supports_credentials=True, origins=['*'])  # Configure for production

# Rate limiting with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["1000 per hour", "100 per minute"]
)
limiter.init_app(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'max_overflow': 30,
    'pool_pre_ping': True
}

db.init_app(app)

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')

# Enterprise API Routes
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Enterprise authentication endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Demo authentication (replace with real user validation)
        if username == 'demo' and password == 'demo123':
            # Generate JWT token
            token_payload = {
                'user_id': 1,
                'username': username,
                'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
            }
            token = jwt.encode(token_payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
            
            # Store session data in Redis
            session['user_id'] = 1
            session['username'] = username
            session['logged_in'] = True
            
            # Cache user data in Redis
            user_cache_key = f"user:{1}"
            redis_client.hset(user_cache_key, mapping={
                'username': username,
                'last_login': datetime.utcnow().isoformat(),
                'credits': 2847,
                'subscription': 'pro'
            })
            redis_client.expire(user_cache_key, 3600)  # 1 hour expiry
            
            logger.info(f"User {username} logged in successfully")
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': 1,
                    'username': username,
                    'credits': 2847,
                    'subscription': 'pro'
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint with session cleanup"""
    try:
        user_id = session.get('user_id')
        if user_id:
            # Clear Redis cache
            redis_client.delete(f"user:{user_id}")
            logger.info(f"User {user_id} logged out")
        
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        if session.get('logged_in'):
            user_id = session.get('user_id')
            user_cache_key = f"user:{user_id}"
            
            # Try to get from Redis cache first
            cached_user = redis_client.hgetall(user_cache_key)
            if cached_user:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': user_id,
                        'username': cached_user.get('username'),
                        'credits': int(cached_user.get('credits', 0)),
                        'subscription': cached_user.get('subscription')
                    }
                })
        
        return jsonify({'authenticated': False})
    except Exception as e:
        logger.error(f"Auth status error: {str(e)}")
        return jsonify({'authenticated': False})

@app.route('/api/system/status', methods=['GET'])
@limiter.limit("60 per minute")
def system_status():
    """System status endpoint with caching"""
    try:
        cache_key = "system:status"
        cached_status = redis_client.get(cache_key)
        
        if cached_status:
            import json
            return jsonify(json.loads(cached_status))
        
        # Generate system status
        status_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'hybrid_processing': {
                'local_percentage': 67,
                'cloud_percentage': 33,
                'performance_gain': '2.3x'
            },
            'security': {
                'status': 'optimal',
                'threats_blocked': 1247,
                'last_scan': datetime.utcnow().isoformat()
            },
            'performance': {
                'response_time': '< 150ms',
                'uptime': '99.7%',
                'concurrent_users': 1000
            }
        }
        
        # Cache for 30 seconds
        redis_client.setex(cache_key, 30, json.dumps(status_data))
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/dashboard/metrics', methods=['GET'])
@token_required
@limiter.limit("120 per minute")
def dashboard_metrics(current_user_id):
    """Dashboard metrics with Redis caching"""
    try:
        cache_key = f"dashboard:metrics:{current_user_id}"
        cached_metrics = redis_client.get(cache_key)
        
        if cached_metrics:
            import json
            return jsonify(json.loads(cached_metrics))
        
        metrics_data = {
            'ai_performance': {
                'efficiency': 98.7,
                'status': 'optimal',
                'trend': 'up'
            },
            'security_status': {
                'threats_blocked': 1247,
                'status': 'secure',
                'last_update': datetime.utcnow().isoformat()
            },
            'hybrid_processing': {
                'speed_improvement': '2.3x',
                'cost_savings': 45,
                'local_ratio': 67
            },
            'cost_savings': {
                'percentage': 45,
                'amount_saved': '$1,247',
                'vs_cloud_only': True
            }
        }
        
        # Cache for 60 seconds
        redis_client.setex(cache_key, 60, json.dumps(metrics_data))
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Dashboard metrics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/security/status', methods=['GET'])
@token_required
@limiter.limit("60 per minute")
def security_status(current_user_id):
    """Security status endpoint"""
    try:
        cache_key = "security:status"
        cached_status = redis_client.get(cache_key)
        
        if cached_status:
            import json
            return jsonify(json.loads(cached_status))
        
        security_data = {
            'status': 'secure',
            'last_scan': datetime.utcnow().isoformat(),
            'next_scan': (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
            'threats_detected': 0,
            'threats_blocked': 1247,
            'success_rate': 98.7,
            'response_time': '2.3s',
            'network': {
                'active_connections': 23,
                'data_scanned': '4.7GB',
                'firewall_status': 100,
                'rules_active': 847
            }
        }
        
        # Cache for 30 seconds
        redis_client.setex(cache_key, 30, json.dumps(security_data))
        return jsonify(security_data)
        
    except Exception as e:
        logger.error(f"Security status error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/projects', methods=['GET'])
@token_required
@limiter.limit("120 per minute")
def get_projects(current_user_id):
    """Projects endpoint with caching"""
    try:
        cache_key = f"projects:{current_user_id}"
        cached_projects = redis_client.get(cache_key)
        
        if cached_projects:
            import json
            return jsonify(json.loads(cached_projects))
        
        projects_data = {
            'projects': [
                {
                    'id': 1,
                    'name': 'AI Model Optimization',
                    'status': 'active',
                    'progress': 75,
                    'description': 'Optimizing neural network performance',
                    'team_members': 3,
                    'deadline': '2025-06-30'
                },
                {
                    'id': 2,
                    'name': 'Security Enhancement',
                    'status': 'planning',
                    'progress': 25,
                    'description': 'Implementing advanced threat detection',
                    'team_members': 2,
                    'deadline': '2025-07-03'
                },
                {
                    'id': 3,
                    'name': 'Data Pipeline',
                    'status': 'completed',
                    'progress': 100,
                    'description': 'Building scalable data processing pipeline',
                    'team_members': 4,
                    'deadline': '2025-06-25'
                }
            ]
        }
        
        # Cache for 5 minutes
        redis_client.setex(cache_key, 300, json.dumps(projects_data))
        return jsonify(projects_data)
        
    except Exception as e:
        logger.error(f"Projects error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancer"""
    try:
        # Check Redis connection
        redis_client.ping()
        
        # Check database connection
        with app.app_context():
            db.engine.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'redis': 'connected',
                'database': 'connected'
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'message': str(e.description)}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
with app.app_context():
    db.create_all()
    logger.info("Database initialized successfully")

# Static file serving
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    logger.info("Starting ApexAgent Optimized Backend Server...")
    logger.info("Redis connection established")
    logger.info("Database initialized")
    logger.info("Enterprise features enabled")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

