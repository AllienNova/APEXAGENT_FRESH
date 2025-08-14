# ApexAgent Production Packaging Guide

## Overview

This document provides instructions for packaging the ApexAgent software for production deployment as a downloadable desktop application. The packaging process ensures that all components are properly bundled, dependencies are managed, and the application is ready for distribution to end users.

## Prerequisites

Before packaging the application, ensure the following prerequisites are met:

- Node.js 20.18.0 or higher
- Python 3.11.0 or higher
- Git
- Electron (for desktop packaging)
- PyInstaller (for Python component packaging)

## Directory Structure

The packaged application will have the following structure:

```
ApexAgent/
├── app/                  # Main application files
│   ├── frontend/         # Frontend UI components
│   ├── backend/          # Backend services
│   │   └── src/          # Python source code
│   ├── resources/        # Application resources
│   └── config/           # Configuration files
├── bin/                  # Executable files
├── lib/                  # Library dependencies
├── docs/                 # Documentation
└── LICENSE               # License information
```

## Packaging Steps

### 1. Prepare the Environment

```bash
# Create packaging directory
mkdir -p ApexAgent_Package
cd ApexAgent_Package

# Clone the repository
git clone https://github.com/AllienNova/ApexAgent .
```

### 2. Frontend Packaging

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build production version
npm run build

# Move build to app directory
mkdir -p ../app/frontend
cp -r build/* ../app/frontend/
```

### 3. Backend Packaging

```bash
# Navigate to src directory
cd ../src

# Create requirements.txt if not exists
pip freeze > requirements.txt

# Package Python components with PyInstaller
pyinstaller --name apexagent_backend \
            --add-data "config_manager.py:." \
            --add-data "analytics:analytics" \
            --add-data "billing:billing" \
            --hidden-import cryptography \
            --hidden-import requests \
            --hidden-import json \
            --hidden-import logging \
            main.py

# Move dist files to app directory
mkdir -p ../app/backend
cp -r dist/apexagent_backend/* ../app/backend/
```

### 4. Electron Packaging

```bash
# Navigate to root directory
cd ..

# Create Electron main file
cat > main.js << 'EOL'
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Start backend process
let backendProcess = null;

function startBackend() {
  const backendPath = path.join(__dirname, 'app', 'backend', 'apexagent_backend');
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
  
  // Open DevTools in development
  // mainWindow.webContents.openDevTools();
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
EOL

# Create package.json for Electron
cat > package.json << 'EOL'
{
  "name": "apexagent",
  "version": "1.0.0",
  "description": "ApexAgent - Desktop AI Assistant",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder"
  },
  "author": "ApexAgent Team",
  "license": "Proprietary",
  "devDependencies": {
    "electron": "^28.0.0",
    "electron-builder": "^24.6.3"
  },
  "build": {
    "appId": "com.apexagent.desktop",
    "productName": "ApexAgent",
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
EOL

# Install Electron dependencies
npm install

# Create resources directory and add icons
mkdir -p app/resources
# Add icons here

# Build Electron package
npm run build
```

### 5. Create Installer

```bash
# For Windows (using NSIS)
# The electron-builder will create an installer automatically

# For macOS (using DMG)
# The electron-builder will create a DMG file automatically

# For Linux (using AppImage)
# The electron-builder will create an AppImage file automatically
```

### 6. Final Steps

```bash
# Copy documentation
mkdir -p docs
cp -r README.md docs/
cp -r business/final_four_tier_pricing_model.md docs/
cp -r frontend/frontend_documentation.md docs/

# Create LICENSE file
cat > LICENSE << 'EOL'
Copyright (c) 2025 ApexAgent

All rights reserved.

This software and associated documentation files (the "Software") are proprietary
and confidential. Unauthorized copying, distribution, or use of the Software is
strictly prohibited.
EOL

# Create final package
mkdir -p ApexAgent_Release
cp -r dist/* ApexAgent_Release/
cp -r docs ApexAgent_Release/
cp LICENSE ApexAgent_Release/
```

## Verification

Before distributing the packaged application, verify the following:

1. The application launches correctly on all target platforms
2. All features work as expected
3. Configuration files are properly loaded
4. API keys and sensitive information are properly secured
5. Error handling works correctly
6. Documentation is accessible to users

## Distribution

The packaged application can be distributed through:

1. Direct download from the ApexAgent website
2. Software distribution platforms
3. Enterprise deployment systems

## Troubleshooting

Common packaging issues and solutions:

1. **Missing dependencies**: Ensure all dependencies are included in the package
2. **Path issues**: Use relative paths in the application code
3. **Permission issues**: Ensure proper file permissions are set
4. **Platform-specific issues**: Test on all target platforms before distribution

## Conclusion

Following these packaging steps will create a production-ready ApexAgent desktop application that can be distributed to end users. The package includes all necessary components, dependencies, and documentation for a complete user experience.
