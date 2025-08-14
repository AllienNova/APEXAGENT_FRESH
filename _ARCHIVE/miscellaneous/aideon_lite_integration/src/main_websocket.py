import os
import sys
# DON'T CHANGE THIS PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
from datetime import datetime
import hashlib
from routes.user import user_bp
from routes.aideon_api import aideon_bp
from websocket_handler import init_socketio

def create_app():
    app = Flask(__name__)
    app.secret_key = 'aideon_lite_ai_secret_key_2025'
    
    # Enable CORS for all routes
    CORS(app, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(aideon_bp, url_prefix='/api')
    
    # Initialize database
    init_db()
    
    # Initialize WebSocket
    socketio = init_socketio(app)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Demo authentication
        if username == 'demo' and password == 'demo123':
            session['user_id'] = 'demo'
            session['username'] = 'demo'
            return jsonify({
                'success': True,
                'user': {
                    'id': 'demo',
                    'username': 'demo',
                    'credits': 2847,
                    'cost_today': 0.42
                }
            })
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    @app.route('/api/logout', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({'success': True})
    
    @app.route('/api/user/status')
    def user_status():
        if 'user_id' in session:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': session['user_id'],
                    'username': session['username'],
                    'credits': 2847,
                    'cost_today': 0.42
                }
            })
        return jsonify({'authenticated': False})
    
    return app, socketio

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect('aideon.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                credits INTEGER DEFAULT 1000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'ACTIVE',
                progress INTEGER DEFAULT 0,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create security_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                source TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

if __name__ == '__main__':
    print("🚀 Starting Aideon Lite AI Backend Server...")
    print("📡 Frontend-Backend Integration: ENABLED")
    print("🔒 Security Features: ACTIVE")
    print("🌐 CORS: ENABLED for all origins")
    print("💾 Database: ENABLED")
    print("🔗 API Endpoints: /api/...")
    print("📱 Frontend: Served from /")
    print("🔄 WebSocket: ENABLED for real-time updates")
    
    app, socketio = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

