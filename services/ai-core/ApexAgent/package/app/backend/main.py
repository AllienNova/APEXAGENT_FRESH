#!/usr/bin/env python3
'''
ApexAgent Backend Entry Point
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
    '''Main entry point for the ApexAgent backend.'''
    logger.info("Starting ApexAgent backend...")
    
    try:
        # Import local modules
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize configuration
        from src.config_manager import ConfigManager
        config = ConfigManager()
        
        # Start API server
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return {"status": "ok", "message": "ApexAgent backend is running"}
        
        # Run the server
        app.run(host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.error(f"Error starting backend: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
