# ApexAgent Packaging Script

"""
This script packages the ApexAgent application for distribution as a downloadable program.
It bundles all necessary components, manages dependencies, and creates platform-specific installers.
"""

import os
import sys
import shutil
import subprocess
import json
import platform
from pathlib import Path

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
        PACKAGE_DIR / "bin",
        PACKAGE_DIR / "lib",
        PACKAGE_DIR / "docs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Package frontend
def package_frontend():
    """Package frontend components."""
    print("Packaging frontend components...")
    
    # Change to frontend directory
    os.chdir(FRONTEND_DIR)
    
    # Install dependencies
    subprocess.run(["npm", "install"], check=True)
    
    # Build production version
    subprocess.run(["npm", "run", "build"], check=True)
    
    # Copy build to package directory
    if (FRONTEND_DIR / "build").exists():
        shutil.copytree(
            FRONTEND_DIR / "build", 
            PACKAGE_DIR / "app" / "frontend", 
            dirs_exist_ok=True
        )
    else:
        print("WARNING: Frontend build directory not found. Copying source files instead.")
        # Copy source files instead
        for item in (FRONTEND_DIR / "src").glob("**/*"):
            if item.is_file():
                relative_path = item.relative_to(FRONTEND_DIR / "src")
                target_path = PACKAGE_DIR / "app" / "frontend" / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_path)

# Package backend
def package_backend():
    """Package backend components."""
    print("Packaging backend components...")
    
    # Create requirements.txt
    os.chdir(ROOT_DIR)
    subprocess.run([
        sys.executable, "-m", "pip", "freeze"
    ], stdout=open(ROOT_DIR / "requirements.txt", "w"), check=True)
    
    # Copy backend source files
    for item in SRC_DIR.glob("**/*"):
        if item.is_file() and not item.name.startswith("__pycache__"):
            relative_path = item.relative_to(SRC_DIR)
            target_path = PACKAGE_DIR / "app" / "backend" / "src" / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_path)
    
    # Copy requirements.txt
    shutil.copy2(ROOT_DIR / "requirements.txt", PACKAGE_DIR / "app" / "backend")

# Create Electron files
def create_electron_files():
    """Create Electron packaging files."""
    print("Creating Electron packaging files...")
    
    # Create main.js
    main_js = """
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Start backend process
let backendProcess = null;

function startBackend() {
  const isWindows = process.platform === 'win32';
  const backendExe = isWindows ? 'apexagent_backend.exe' : 'apexagent_backend';
  const backendPath = path.join(__dirname, 'app', 'backend', backendExe);
  
  backendProcess = spawn(backendPath);
  
  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });
  
  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend error: ${data}`);
  });
  
  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'app', 'frontend', 'index.html'));
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
  
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
"""
    
    # Create package.json
    package_json = {
        "name": "apexagent",
        "version": VERSION,
        "description": DESCRIPTION,
        "main": "main.js",
        "scripts": {
            "start": "electron .",
            "build": "electron-builder"
        },
        "author": AUTHOR,
        "license": "Proprietary",
        "devDependencies": {
            "electron": "^28.0.0",
            "electron-builder": "^24.6.3"
        },
        "build": {
            "appId": "com.apexagent.desktop",
            "productName": PACKAGE_NAME,
            "directories": {
                "output": "dist"
            },
            "files": [
                "**/*",
                "!**/node_modules/*/{CHANGELOG.md,README.md,README,readme.md,readme}",
                "!**/node_modules/*/{test,__tests__,tests,powered-test,example,examples}",
                "!**/node_modules/*.d.ts",
                "!**/node_modules/.bin",
                "!**/*.{iml,o,hprof,orig,pyc,pyo,rbc,swp,csproj,sln,xproj}",
                "!.editorconfig",
                "!**/._*",
                "!**/{.DS_Store,.git,.hg,.svn,CVS,RCS,SCCS,.gitignore,.gitattributes}",
                "!**/{__pycache__,thumbs.db,.flowconfig,.idea,.vs,.nyc_output}",
                "!**/{appveyor.yml,.travis.yml,circle.yml}",
                "!**/{npm-debug.log,yarn.lock,.yarn-integrity,.yarn-metadata.json}"
            ],
            "win": {
                "target": "nsis",
                "icon": "app/resources/icon.ico"
            },
            "mac": {
                "target": "dmg",
                "icon": "app/resources/icon.icns"
            },
            "linux": {
                "target": "AppImage",
                "icon": "app/resources/icon.png"
            }
        }
    }
    
    # Create preload.js
    preload_js = """
window.addEventListener('DOMContentLoaded', () => {
  const replaceText = (selector, text) => {
    const element = document.getElementById(selector)
    if (element) element.innerText = text
  }

  for (const type of ['chrome', 'node', 'electron']) {
    replaceText(`${type}-version`, process.versions[type])
  }
})
"""
    
    # Write files
    with open(PACKAGE_DIR / "main.js", "w") as f:
        f.write(main_js)
    
    with open(PACKAGE_DIR / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    with open(PACKAGE_DIR / "preload.js", "w") as f:
        f.write(preload_js)

# Copy documentation
def copy_documentation():
    """Copy documentation files."""
    print("Copying documentation...")
    
    # Copy README
    if (ROOT_DIR / "README.md").exists():
        shutil.copy2(ROOT_DIR / "README.md", PACKAGE_DIR / "docs")
    
    # Copy business documentation
    business_docs = ROOT_DIR / "business"
    if business_docs.exists():
        for doc in business_docs.glob("*.md"):
            shutil.copy2(doc, PACKAGE_DIR / "docs")
    
    # Copy frontend documentation
    frontend_docs = FRONTEND_DIR
    if frontend_docs.exists():
        for doc in frontend_docs.glob("*.md"):
            shutil.copy2(doc, PACKAGE_DIR / "docs")
    
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

# Create platform-specific resources
def create_resources():
    """Create platform-specific resources."""
    print("Creating resources...")
    
    # Create placeholder icons
    icons_dir = PACKAGE_DIR / "app" / "resources"
    
    # Create a simple text file as placeholder
    with open(icons_dir / "icon.txt", "w") as f:
        f.write("Placeholder for application icons")
    
    # In a real scenario, you would copy actual icon files here

# Build package
def build_package():
    """Build the final package."""
    print("Building final package...")
    
    # Change to package directory
    os.chdir(PACKAGE_DIR)
    
    # Install dependencies
    subprocess.run(["npm", "install"], check=True)
    
    # Create a zip archive of the package
    shutil.make_archive(
        str(DIST_DIR / PACKAGE_NAME), 
        'zip', 
        PACKAGE_DIR
    )
    
    print(f"Package created at: {DIST_DIR / PACKAGE_NAME}.zip")

# Main function
def main():
    """Main packaging function."""
    print(f"Packaging {PACKAGE_NAME} v{VERSION}...")
    
    try:
        clean_directories()
        create_directories()
        package_frontend()
        package_backend()
        create_electron_files()
        copy_documentation()
        create_resources()
        build_package()
        
        print("Packaging completed successfully!")
        return True
    except Exception as e:
        print(f"Error during packaging: {str(e)}")
        return False

if __name__ == "__main__":
    main()
