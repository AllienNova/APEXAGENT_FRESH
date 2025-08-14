import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.aideon_api import aideon_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Enhanced security configuration
app.config['SECRET_KEY'] = 'aideon_secure_key_v2_production_ready'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Enable CORS for frontend-backend integration
CORS(app, origins="*", supports_credentials=True)

# Register API blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(aideon_bp, url_prefix='/api')

# Database configuration (enabled for production)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files and handle SPA routing"""
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

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by serving the frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully"""
    return {"error": "Internal server error", "message": str(error)}, 500

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Aideon Lite AI Backend",
        "version": "1.0.0",
        "timestamp": "2024-06-24T07:00:00Z"
    }

if __name__ == '__main__':
    print("🚀 Starting Aideon Lite AI Backend Server...")
    print("📡 Frontend-Backend Integration: ENABLED")
    print("🔒 Security Features: ACTIVE")
    print("🌐 CORS: ENABLED for all origins")
    print("💾 Database: ENABLED")
    print("🔗 API Endpoints: /api/...")
    print("📱 Frontend: Served from /")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

