#!/usr/bin/env python3
'''
ApexAgent Backend Entry Point with Comprehensive Authentication System
'''

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    '''Main entry point for the ApexAgent backend with authentication system.'''
    logger.info("Starting ApexAgent backend with authentication system...")
    
    try:
        # Import local modules
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize configuration
        from src.config_manager import ConfigManager
        config = ConfigManager()
        
        # Create Flask app
        from flask import Flask
        from flask_cors import CORS
        app = Flask(__name__)
        
        # Configure CORS for frontend integration
        CORS(app, origins="*", supports_credentials=True)
        
        # Configure Flask
        app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'aideon_flask_secret_key_v1')
        app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        
        # Initialize authentication system
        from src.auth.auth_api import AuthenticationAPI
        from src.auth.security_monitor import start_security_monitoring
        
        # Start security monitoring
        start_security_monitoring()
        logger.info("Security monitoring started")
        
        # Initialize authentication API
        auth_api = AuthenticationAPI(app)
        logger.info("Authentication API initialized")
        
        # Original home route
        @app.route('/')
        def home():
            return {"status": "ok", "message": "ApexAgent backend with authentication is running"}
        
        # Health check route
        @app.route('/health')
        def health():
            return {
                "status": "healthy",
                "services": {
                    "authentication": "operational",
                    "security_monitoring": "operational",
                    "backend": "operational"
                }
            }
        
        # Run the server
        logger.info("Starting Flask server on 0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logger.error(f"Error starting backend: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
