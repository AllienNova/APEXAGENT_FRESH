# Aideon AI Lite Installation Guide

This comprehensive guide provides step-by-step instructions for installing Aideon AI Lite on Windows, macOS, and Linux operating systems.

## Table of Contents
- [Windows Installation](#windows-installation)
- [macOS Installation](#macos-installation)
- [Linux Installation](#linux-installation)
- [System Requirements](#system-requirements)
- [Troubleshooting](#troubleshooting)
- [Getting Support](#getting-support)

## Windows Installation

### Prerequisites
- Windows 10 or Windows 11 (64-bit)
- 4GB RAM minimum, 8GB recommended
- 500MB free disk space

### Installation Steps
1. **Download the installer**
   - Access the Windows installer from: https://github.com/AllienNova/ApexAgent/actions/runs/15513850611/artifacts/3282519580
   - You'll need to be logged into GitHub with appropriate permissions to download the artifact
   - Extract the downloaded ZIP file to access the `.exe` installer

2. **Run the installer**
   - Right-click on `Aideon AI Lite Setup 1.0.0.exe` and select "Run as administrator"
   - If you see a Windows SmartScreen warning, click "More info" and then "Run anyway"

3. **Follow the installation wizard**
   - Accept the license agreement
   - Choose installation location (default is recommended)
   - Select additional components if prompted
   - Click "Install" to begin the installation process

4. **Complete the installation**
   - Wait for the installation to complete
   - Click "Finish" to exit the installer
   - Aideon AI Lite will launch automatically (if the option was selected)

5. **Verify installation**
   - Check that Aideon AI Lite appears in your Start menu
   - Launch the application to ensure it starts correctly

## macOS Installation

### Prerequisites
- macOS 11.0 (Big Sur) or later
- Intel or Apple Silicon processor
- 4GB RAM minimum, 8GB recommended
- 500MB free disk space

### Installation Steps
1. **Download the installer**
   - Access the macOS installer from: https://github.com/AllienNova/ApexAgent/actions/runs/15513850611/artifacts/3282514439
   - You'll need to be logged into GitHub with appropriate permissions to download the artifact
   - Extract the downloaded ZIP file to access the `.dmg` installer

2. **Open the DMG file**
   - Double-click the `Aideon AI Lite-1.0.0.dmg` file
   - Wait for the disk image to mount and the installer window to appear

3. **Install the application**
   - Drag the Aideon AI Lite icon to the Applications folder shortcut
   - Wait for the copying process to complete

4. **First launch**
   - Open Finder and navigate to Applications
   - Right-click on "Aideon AI Lite" and select "Open"
   - When prompted about opening an application from an unidentified developer:
     - Click "Open" to proceed (this is only required the first time)

5. **Verify installation**
   - Ensure the application launches correctly
   - Check for any initial setup prompts or configuration options

### Notarization Notice
The macOS DMG installer is signed and notarized with Apple, ensuring security and compatibility with macOS Gatekeeper security features.

## Linux Installation

### Prerequisites
- Ubuntu 22.04 LTS or later (or compatible distribution)
- 4GB RAM minimum, 8GB recommended
- 500MB free disk space

### Installation Steps (Debian/Ubuntu)
1. **Download the installer**
   - Access the Linux installer from: https://github.com/AllienNova/ApexAgent/actions/runs/15513850611/artifacts/3282516877
   - You'll need to be logged into GitHub with appropriate permissions to download the artifact
   - Extract the downloaded ZIP file to access both the `.deb` package and AppImage

2. **Option 1: Install using .deb package**
   - Open a terminal window
   - Navigate to the directory containing the downloaded .deb file
   - Run the following command:
     ```
     sudo dpkg -i aideon-ai-lite_1.0.0_amd64.deb
     ```
   - If you encounter dependency issues, run:
     ```
     sudo apt-get install -f
     ```

3. **Option 2: Run using AppImage**
   - Make the AppImage executable:
     ```
     chmod +x Aideon_AI_Lite-1.0.0.AppImage
     ```
   - Run the AppImage:
     ```
     ./Aideon_AI_Lite-1.0.0.AppImage
     ```

4. **Verify installation**
   - Launch Aideon AI Lite from your application menu
   - Or run from terminal:
     ```
     aideon-ai-lite
     ```

### Installation Steps (Other Linux Distributions)
For other Linux distributions, we recommend using the AppImage which works across most modern Linux distributions without additional dependencies.

1. **Make the AppImage executable**
   ```
   chmod +x Aideon_AI_Lite-1.0.0.AppImage
   ```

2. **Run the AppImage**
   ```
   ./Aideon_AI_Lite-1.0.0.AppImage
   ```

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 11.0, Ubuntu 22.04 LTS or compatible Linux distribution
- **Processor**: Dual-core 2.0 GHz or higher
- **Memory**: 4GB RAM
- **Storage**: 500MB available space
- **Display**: 1280x720 resolution
- **Internet**: Broadband connection for online features

### Recommended Requirements
- **OS**: Windows 11, macOS 12.0 or later, Ubuntu 22.04 LTS or later
- **Processor**: Quad-core 2.5 GHz or higher
- **Memory**: 8GB RAM
- **Storage**: 1GB available space
- **Display**: 1920x1080 resolution
- **Internet**: High-speed broadband connection

## Troubleshooting

### Windows Issues
- **Application fails to start**: Ensure all Visual C++ redistributables are installed
- **Missing DLL errors**: Install the latest Microsoft Visual C++ Redistributable package
- **Permission errors**: Right-click and select "Run as administrator"

### macOS Issues
- **"App is damaged" message**: Control-click the app, choose Open, then click Open in the dialog
- **App won't open due to security settings**: Go to System Preferences > Security & Privacy > General and click "Open Anyway"
- **Permissions issues**: Reset permissions with `sudo chown -R $(whoami) /Applications/Aideon\ AI\ Lite.app`

### Linux Issues
- **Missing dependencies (Debian/Ubuntu)**: Run `sudo apt-get install -f` to install missing dependencies
- **AppImage won't run**: Ensure the file is executable with `chmod +x Aideon_AI_Lite-1.0.0.AppImage`
- **Missing libraries**: Install required libraries with `sudo apt-get install libasound2t64 libgtk-3-0`

## Getting Support

If you encounter any issues during installation or while using Aideon AI Lite:

- **Documentation**: Visit our [official documentation](https://github.com/AllienNova/ApexAgent/documentation)
- **GitHub Issues**: Submit issues at [https://github.com/AllienNova/ApexAgent/issues](https://github.com/AllienNova/ApexAgent/issues)
- **Email Support**: Contact support at dev@aideonai.com

---

© 2025 Aideon AI Team. All rights reserved.
