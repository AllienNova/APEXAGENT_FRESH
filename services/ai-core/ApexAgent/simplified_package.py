"""
Modified packaging script for ApexAgent that works around npm dependency issues.

This script creates a simplified package structure focusing on the core components
without requiring a full npm build process.
"""

import os
import sys
import shutil
import subprocess
import json
import platform
from pathlib import Path
import zipfile
import datetime

# Configuration
PACKAGE_NAME = "ApexAgent"
VERSION = "1.0.0"
AUTHOR = "ApexAgent Team"
DESCRIPTION = "Desktop-native AI agent with sophisticated project management and LLM orchestration"

# Directory paths
ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = ROOT_DIR / "package"
DIST_DIR = ROOT_DIR / "dist"
SRC_DIR = ROOT_DIR / "src"
FRONTEND_DIR = ROOT_DIR / "frontend"
DOCS_DIR = ROOT_DIR / "docs"
BUSINESS_DIR = ROOT_DIR / "business"

# Ensure clean directories
def clean_directories():
    """Clean packaging directories."""
    print("Cleaning packaging directories...")
    
    for directory in [PACKAGE_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

# Create necessary directories
def create_directories():
    """Create necessary directories for packaging."""
    print("Creating package directories...")
    
    directories = [
        PACKAGE_DIR / "app" / "frontend",
        PACKAGE_DIR / "app" / "backend" / "src",
        PACKAGE_DIR / "app" / "resources",
        PACKAGE_DIR / "app" / "config",
        PACKAGE_DIR / "docs",
        PACKAGE_DIR / "business"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Package frontend source files (skip npm build)
def package_frontend_source():
    """Package frontend source files directly (skipping npm build)."""
    print("Packaging frontend source files...")
    
    # Copy frontend source files
    if (FRONTEND_DIR / "src").exists():
        for item in (FRONTEND_DIR / "src").glob("**/*"):
            if item.is_file():
                relative_path = item.relative_to(FRONTEND_DIR / "src")
                target_path = PACKAGE_DIR / "app" / "frontend" / "src" / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_path)
    
    # Copy package.json and other config files
    for config_file in ["package.json", "tsconfig.json", "README.md"]:
        if (FRONTEND_DIR / config_file).exists():
            shutil.copy2(FRONTEND_DIR / config_file, PACKAGE_DIR / "app" / "frontend")
    
    # Copy public directory if it exists
    if (FRONTEND_DIR / "public").exists():
        shutil.copytree(
            FRONTEND_DIR / "public", 
            PACKAGE_DIR / "app" / "frontend" / "public", 
            dirs_exist_ok=True
        )
    
    # Create a simple HTML file for testing
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ApexAgent</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 800px;
        }
        h1 {
            color: #0066cc;
            margin-bottom: 1rem;
        }
        p {
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: #0066cc;
        }
        .button {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #0055aa;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">⚡</div>
        <h1>ApexAgent</h1>
        <p>Desktop-native AI agent with sophisticated project management and LLM orchestration</p>
        <p>This is a placeholder frontend for the packaged application.</p>
        <button class="button">Launch ApexAgent</button>
    </div>
</body>
</html>
"""
    
    with open(PACKAGE_DIR / "app" / "frontend" / "index.html", "w") as f:
        f.write(index_html)

# Package backend
def package_backend():
    """Package backend components."""
    print("Packaging backend components...")
    
    # Create requirements.txt
    os.chdir(ROOT_DIR)
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "freeze"
        ], stdout=open(ROOT_DIR / "requirements.txt", "w"), check=True)
    except Exception as e:
        print(f"Warning: Could not generate requirements.txt: {str(e)}")
        # Create a minimal requirements file
        with open(ROOT_DIR / "requirements.txt", "w") as f:
            f.write("cryptography>=41.0.0\n")
            f.write("requests>=2.31.0\n")
            f.write("flask>=2.3.0\n")
            f.write("pyyaml>=6.0.0\n")
    
    # Copy backend source files
    for item in SRC_DIR.glob("**/*"):
        if item.is_file() and "__pycache__" not in str(item):
            relative_path = item.relative_to(SRC_DIR)
            target_path = PACKAGE_DIR / "app" / "backend" / "src" / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_path)
    
    # Copy requirements.txt
    shutil.copy2(ROOT_DIR / "requirements.txt", PACKAGE_DIR / "app" / "backend")
    
    # Create a simple main.py if it doesn't exist
    if not (SRC_DIR / "main.py").exists():
        main_py = """#!/usr/bin/env python3
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
"""
        with open(PACKAGE_DIR / "app" / "backend" / "main.py", "w") as f:
            f.write(main_py)
    else:
        shutil.copy2(SRC_DIR / "main.py", PACKAGE_DIR / "app" / "backend")

# Copy documentation and business files
def copy_documentation_and_business():
    """Copy documentation and business files."""
    print("Copying documentation and business files...")
    
    # Copy README
    if (ROOT_DIR / "README.md").exists():
        shutil.copy2(ROOT_DIR / "README.md", PACKAGE_DIR / "docs")
    
    # Copy business documentation
    if BUSINESS_DIR.exists():
        for doc in BUSINESS_DIR.glob("*.md"):
            shutil.copy2(doc, PACKAGE_DIR / "business")
    
    # Copy frontend documentation
    if FRONTEND_DIR.exists():
        for doc in FRONTEND_DIR.glob("*.md"):
            shutil.copy2(doc, PACKAGE_DIR / "docs")
    
    # Copy packaging guide
    if (ROOT_DIR / "packaging_guide.md").exists():
        shutil.copy2(ROOT_DIR / "packaging_guide.md", PACKAGE_DIR / "docs")
    
    # Create LICENSE file
    license_text = f"""
Copyright (c) 2025 {AUTHOR}

All rights reserved.

This software and associated documentation files (the "Software") are proprietary
and confidential. Unauthorized copying, distribution, or use of the Software is
strictly prohibited.
"""
    
    with open(PACKAGE_DIR / "LICENSE", "w") as f:
        f.write(license_text)

# Create README for the package
def create_package_readme():
    """Create README for the package."""
    print("Creating package README...")
    
    readme_text = f"""# {PACKAGE_NAME} v{VERSION}

{DESCRIPTION}

## Overview

ApexAgent is a desktop-native AI agent with sophisticated project management and LLM orchestration capabilities. It provides a comprehensive environment for working with multiple LLM models, managing projects, and automating complex tasks.

## Features

- Four-tier pricing model (Basic, Pro, Expert, Enterprise)
- Support for user-provided API keys with threshold policy
- Sophisticated project management with memory preservation
- Horizontal tab navigation for intuitive interface
- Dr. Tardis multimodal assistant for explaining agent activities
- Plugin system for extending functionality

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 20.18.0 or higher

### Setup

1. Install Python dependencies:
   ```
   cd app/backend
   pip install -r requirements.txt
   ```

2. Install Node.js dependencies:
   ```
   cd app/frontend
   npm install
   ```

3. Start the backend:
   ```
   cd app/backend
   python main.py
   ```

4. Start the frontend:
   ```
   cd app/frontend
   npm start
   ```

## Documentation

See the `docs` directory for detailed documentation.

## License

Proprietary - All rights reserved.

Copyright (c) 2025 {AUTHOR}
"""
    
    with open(PACKAGE_DIR / "README.md", "w") as f:
        f.write(readme_text)

# Create startup scripts
def create_startup_scripts():
    """Create startup scripts for different platforms."""
    print("Creating startup scripts...")
    
    # Windows batch script
    windows_bat = """@echo off
echo Starting ApexAgent...

:: Start backend
start cmd /c "cd app\\backend && python main.py"

:: Wait a moment for backend to initialize
timeout /t 2 /nobreak > nul

:: Open frontend in browser
start http://localhost:5000

echo ApexAgent is running!
"""
    
    # Unix shell script
    unix_sh = """#!/bin/bash
echo "Starting ApexAgent..."

# Start backend
cd app/backend && python3 main.py &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Open frontend in browser
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000
elif command -v open > /dev/null; then
    open http://localhost:5000
else
    echo "Frontend available at: http://localhost:5000"
fi

echo "ApexAgent is running!"
echo "Press Ctrl+C to stop"

# Wait for user to stop the process
trap "kill $BACKEND_PID; echo 'ApexAgent stopped.'; exit 0" INT
wait
"""
    
    with open(PACKAGE_DIR / "start_apexagent.bat", "w") as f:
        f.write(windows_bat)
    
    with open(PACKAGE_DIR / "start_apexagent.sh", "w") as f:
        f.write(unix_sh)
    
    # Make the shell script executable
    os.chmod(PACKAGE_DIR / "start_apexagent.sh", 0o755)

# Build package
def build_package():
    """Build the final package."""
    print("Building final package...")
    
    # Create a zip archive of the package
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{PACKAGE_NAME}_v{VERSION}_{timestamp}"
    
    shutil.make_archive(
        str(DIST_DIR / zip_filename), 
        'zip', 
        PACKAGE_DIR
    )
    
    print(f"Package created at: {DIST_DIR / zip_filename}.zip")
    return f"{DIST_DIR / zip_filename}.zip"

# Main function
def main():
    """Main packaging function."""
    print(f"Packaging {PACKAGE_NAME} v{VERSION}...")
    
    try:
        clean_directories()
        create_directories()
        package_frontend_source()  # Use source files instead of npm build
        package_backend()
        copy_documentation_and_business()
        create_package_readme()
        create_startup_scripts()
        package_path = build_package()
        
        print("Packaging completed successfully!")
        return package_path
    except Exception as e:
        print(f"Error during packaging: {str(e)}")
        return None

if __name__ == "__main__":
    main()
