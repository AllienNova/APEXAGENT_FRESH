# Aideon AI Lite Installation Guide

This comprehensive guide provides step-by-step instructions for installing Aideon AI Lite using our new one-click installer.

## System Requirements

### Windows
- Windows 10 or later (64-bit)
- 4GB RAM minimum, 8GB recommended
- 2GB free disk space
- Intel Core i5 or equivalent (4th generation or newer)

### macOS
- macOS 10.15 (Catalina) or later
- 4GB RAM minimum, 8GB recommended
- 2GB free disk space
- Intel or Apple Silicon processor

### Linux
- Ubuntu 20.04 or later, Debian 10 or later, or Fedora 32 or later
- 4GB RAM minimum, 8GB recommended
- 2GB free disk space
- Intel Core i5 or equivalent (4th generation or newer)

## Installation Instructions

### Windows Installation

1. **Download the Installer**
   - Download the `Aideon AI Lite-Setup-1.0.0.exe` file from the official website or release page

2. **Run the Installer**
   - Double-click the downloaded `.exe` file
   - If you see a security warning, click "More info" and then "Run anyway"

3. **Complete Installation**
   - The installer will automatically install Aideon AI Lite and all required dependencies
   - No manual configuration is needed
   - When installation completes, the application will launch automatically

4. **Verify Installation**
   - Ensure the application launches correctly
   - Verify that all tabs and features are accessible

### macOS Installation

1. **Download the Installer**
   - Download the `Aideon AI Lite-1.0.0.dmg` file from the official website or release page

2. **Mount the DMG**
   - Double-click the downloaded `.dmg` file to mount it
   - A window will appear showing the Aideon AI Lite application and the Applications folder

3. **Install the Application**
   - Drag the Aideon AI Lite icon to the Applications folder
   - This will copy the application to your Applications directory

4. **First Launch**
   - Open the Applications folder and double-click Aideon AI Lite
   - On first launch, you may see a security warning
   - Right-click (or Control-click) on the app icon and select "Open"
   - Click "Open" in the dialog that appears

5. **Verify Installation**
   - Ensure the application launches correctly
   - Verify that all tabs and features are accessible

### Linux Installation

#### Using AppImage (Recommended)

1. **Download the AppImage**
   - Download the `Aideon AI Lite-1.0.0.AppImage` file from the official website or release page

2. **Make it Executable**
   - Open a terminal in the download directory
   - Run: `chmod +x "Aideon AI Lite-1.0.0.AppImage"`

3. **Run the Application**
   - Double-click the AppImage file or run it from the terminal:
   - `./Aideon\ AI\ Lite-1.0.0.AppImage`

4. **Verify Installation**
   - Ensure the application launches correctly
   - Verify that all tabs and features are accessible

#### Using Debian Package (.deb)

1. **Download the Package**
   - Download the `aideon-ai-lite_1.0.0_amd64.deb` file from the official website or release page

2. **Install the Package**
   - Option 1: Double-click the .deb file to open with your package manager
   - Option 2: Open a terminal in the download directory and run:
   - `sudo dpkg -i aideon-ai-lite_1.0.0_amd64.deb`
   - `sudo apt-get install -f` (to resolve any dependencies)

3. **Launch the Application**
   - Find Aideon AI Lite in your applications menu or run from terminal:
   - `aideon-ai-lite`

4. **Verify Installation**
   - Ensure the application launches correctly
   - Verify that all tabs and features are accessible

## Post-Installation Setup

After installing Aideon AI Lite, we recommend the following steps:

1. **Create or Sign In to Your Account**
   - Launch Aideon AI Lite
   - Follow the on-screen instructions to create a new account or sign in

2. **Configure Default Settings**
   - Go to Settings (gear icon)
   - Set your preferred language and theme
   - Configure API keys if needed
   - Set default project location

3. **Run the System Check**
   - Go to Help > System Check
   - Verify that all components are working correctly
   - Address any warnings or errors

4. **Explore the Interface**
   - Familiarize yourself with the horizontal tab navigation
   - Explore each section to understand its features

## Troubleshooting

### Common Installation Issues

#### Windows

- **"Windows protected your PC" message**
  - Click "More info" and then "Run anyway"
  - This occurs because the application isn't signed with a Microsoft-verified certificate

- **Missing dependencies error**
  - Reinstall the application to ensure all dependencies are properly installed
  - Make sure your Windows is up to date

#### macOS

- **"App is damaged and can't be opened" message**
  - Right-click the app, select "Open" and confirm
  - This occurs because the application isn't notarized with Apple

- **"App can't be opened because Apple cannot check it for malicious software"**
  - Go to System Preferences > Security & Privacy
  - Click "Open Anyway" for Aideon AI Lite

#### Linux

- **AppImage doesn't run**
  - Ensure it's executable: `chmod +x "Aideon AI Lite-1.0.0.AppImage"`
  - Try running with `--no-sandbox` flag if you encounter sandbox errors

- **Missing libraries**
  - Install required dependencies:
  - Ubuntu/Debian: `sudo apt-get install libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libuuid1 libsecret-1-0`
  - Fedora: `sudo dnf install gtk3 libnotify nss libXScrnSaver libXtst xdg-utils at-spi2-core libuuid libsecret`

### Getting Help

If you encounter issues during installation:

1. Check our [FAQ page](https://aideonai.com/support/faq)
2. Visit the [Community Forum](https://community.aideonai.com)
3. Contact support at support@aideonai.com

## Uninstallation Instructions

### Windows
- Go to Settings > Apps > Apps & features
- Find Aideon AI Lite in the list
- Click on it and select "Uninstall"
- Follow the uninstallation wizard

### macOS
- Open the Applications folder in Finder
- Drag Aideon AI Lite to the Trash
- Empty the Trash

### Linux
- AppImage: Simply delete the AppImage file
- Debian package: `sudo apt-get remove aideon-ai-lite`

## Updating Aideon AI Lite

Aideon AI Lite includes an automatic update system:

1. When a new version is available, you'll see a notification
2. Click "Update Now" to download and install the update
3. The application will restart automatically after updating

You can also check for updates manually by going to Help > Check for Updates.
