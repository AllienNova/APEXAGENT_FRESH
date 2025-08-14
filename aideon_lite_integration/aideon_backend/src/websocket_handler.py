from flask_socketio import SocketIO, emit
import threading
import time
import random
from datetime import datetime

# Initialize SocketIO
socketio = None

def init_socketio(app):
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")
        emit('status', {'message': 'Connected to Aideon Lite AI'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('subscribe_security')
    def handle_security_subscription():
        print("Client subscribed to security updates")
        emit('security_status', get_security_status())
    
    @socketio.on('subscribe_projects')
    def handle_projects_subscription():
        print("Client subscribed to project updates")
        emit('project_status', get_project_status())
    
    # Start background tasks
    start_background_tasks()
    
    return socketio

def get_security_status():
    """Get current security status"""
    return {
        'timestamp': datetime.now().isoformat(),
        'threats_blocked': random.randint(1200, 1300),
        'active_threats': random.randint(0, 3),
        'success_rate': round(random.uniform(97.5, 99.5), 1),
        'response_time': round(random.uniform(1.8, 2.8), 1),
        'active_connections': random.randint(20, 30),
        'data_scanned': round(random.uniform(4.0, 5.0), 1),
        'firewall_status': 100,
        'rules_active': random.randint(840, 860)
    }

def get_project_status():
    """Get current project status"""
    projects = [
        {
            'id': 'ai_optimization',
            'name': 'AI Model Optimization',
            'progress': random.randint(70, 80),
            'status': 'ACTIVE',
            'members': 3
        },
        {
            'id': 'security_enhancement',
            'name': 'Security Enhancement',
            'progress': random.randint(20, 30),
            'status': 'PLANNING',
            'members': 2
        },
        {
            'id': 'data_pipeline',
            'name': 'Data Pipeline',
            'progress': 100,
            'status': 'COMPLETED',
            'members': 4
        }
    ]
    return {'projects': projects, 'timestamp': datetime.now().isoformat()}

def get_system_metrics():
    """Get current system metrics"""
    return {
        'timestamp': datetime.now().isoformat(),
        'credits': random.randint(2800, 2900),
        'cost_today': round(random.uniform(0.35, 0.50), 2),
        'hybrid_local': random.randint(65, 70),
        'hybrid_cloud': random.randint(30, 35),
        'system_speed': round(random.uniform(2.2, 2.5), 1),
        'threats_blocked_today': random.randint(1200, 1300)
    }

def broadcast_security_updates():
    """Broadcast security updates to all connected clients"""
    while True:
        if socketio:
            security_data = get_security_status()
            socketio.emit('security_update', security_data)
        time.sleep(30)  # Update every 30 seconds

def broadcast_system_updates():
    """Broadcast system metrics to all connected clients"""
    while True:
        if socketio:
            system_data = get_system_metrics()
            socketio.emit('system_update', system_data)
        time.sleep(60)  # Update every minute

def broadcast_project_updates():
    """Broadcast project updates to all connected clients"""
    while True:
        if socketio:
            project_data = get_project_status()
            socketio.emit('project_update', project_data)
        time.sleep(45)  # Update every 45 seconds

def start_background_tasks():
    """Start background tasks for real-time updates"""
    # Start security updates thread
    security_thread = threading.Thread(target=broadcast_security_updates, daemon=True)
    security_thread.start()
    
    # Start system updates thread
    system_thread = threading.Thread(target=broadcast_system_updates, daemon=True)
    system_thread.start()
    
    # Start project updates thread
    project_thread = threading.Thread(target=broadcast_project_updates, daemon=True)
    project_thread.start()
    
    print("🔄 Real-time update threads started")

