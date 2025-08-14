# One-Click Installer Guide for Aideon AI Lite

This guide provides detailed instructions for building and using the one-click installer for Aideon AI Lite across all major platforms.

## Overview

Aideon AI Lite's one-click installer is designed to provide a seamless installation experience with all dependencies bundled. The installer is built using Electron Builder, which creates native installers for Windows, macOS, and Linux.

## Prerequisites

### For All Platforms
- Node.js 16.x or later
- npm 7.x or later
- Git

### Platform-Specific Requirements

#### Windows
- Windows 10 or later
- PowerShell or Command Prompt
- Visual Studio Build Tools (for native modules)

#### macOS
- macOS 10.15 (Catalina) or later
- Xcode Command Line Tools
- For notarization (optional): Apple Developer account

#### Linux
- Ubuntu 20.04 or later / Debian / Fedora
- build-essential package
- For building Windows installers: Wine 1.6 or later

## Building the Installer

### Clone the Repository

```bash
git clone https://github.com/AllienNova/ApexAgent.git
cd ApexAgent
```

### Install Dependencies

```bash
npm install
```

### Building for Your Platform

#### Windows

On a Windows machine, run:

```powershell
# Install development dependencies
npm install --save-dev electron-builder

# Build the Windows installer
npm run package:win
```

The installer will be created in the `dist` directory as `Aideon AI Lite-Setup-1.0.0.exe`.

#### macOS

On a macOS machine, run:

```bash
# Install development dependencies
npm install --save-dev electron-builder

# Build the macOS installer
npm run package:mac
```

The installer will be created in the `dist` directory as `Aideon AI Lite-1.0.0.dmg`.

#### Linux

On a Linux machine, run:

```bash
# Install development dependencies
npm install --save-dev electron-builder

# Build the Linux installer (AppImage and deb)
npm run package:linux
```

The installers will be created in the `dist` directory as `Aideon AI Lite-1.0.0.AppImage` and `aideon-ai-lite_1.0.0_amd64.deb`.

### Building for All Platforms

To build for all platforms, you need to run the build on each target platform separately. Cross-compilation has limitations:

- Windows installers can only be built on Windows or on Linux with Wine installed
- macOS installers can only be built on macOS due to Apple's restrictions
- Linux installers can be built on any platform

For convenience, we've provided a script that handles the build process:

```bash
# Make the script executable
chmod +x scripts/build-installers.js

# Run the build script
node scripts/build-installers.js
```

## Using the One-Click Installer

### Windows

1. Download the `Aideon AI Lite-Setup-1.0.0.exe` file
2. Double-click the installer
3. The application will install automatically and launch when complete
4. A desktop shortcut and start menu entry will be created

### macOS

1. Download the `Aideon AI Lite-1.0.0.dmg` file
2. Double-click to mount the DMG
3. Drag the Aideon AI Lite icon to the Applications folder
4. Launch from Applications or Spotlight

### Linux

#### AppImage

1. Download the `Aideon AI Lite-1.0.0.AppImage` file
2. Make it executable: `chmod +x Aideon\ AI\ Lite-1.0.0.AppImage`
3. Double-click or run from terminal: `./Aideon\ AI\ Lite-1.0.0.AppImage`

#### Debian/Ubuntu

1. Download the `aideon-ai-lite_1.0.0_amd64.deb` file
2. Install using: `sudo dpkg -i aideon-ai-lite_1.0.0_amd64.deb` or double-click to open with your package manager
3. Launch from your applications menu

## Customizing the Installer

The installer configuration is defined in `electron-builder.yml` in the project root. You can customize various aspects:

- Application metadata
- Icons and branding
- Installation options
- Platform-specific settings

For detailed customization options, refer to the [Electron Builder documentation](https://www.electron.build/).

## Troubleshooting

### Common Issues

#### Windows: "Windows protected your PC" message
This occurs because the application isn't signed with a trusted certificate. You can:
- Click "More info" and then "Run anyway"
- Sign the application with a trusted certificate (recommended for production)

#### macOS: "App is damaged and can't be opened"
This occurs because the application isn't notarized. You can:
- Right-click the app, select "Open" and confirm
- Properly notarize the app using an Apple Developer account (recommended for production)

#### Linux: Missing dependencies
If you encounter missing dependencies on Linux:
- For AppImage: Try using the `--no-sandbox` flag
- For deb packages: Install missing dependencies using your package manager

### Getting Help

If you encounter issues building or using the installer:
- Check the build logs in the console
- Verify all prerequisites are installed
- Ensure you're using the correct Node.js version
- Refer to the [Electron Builder documentation](https://www.electron.build/) for platform-specific issues

## Security Considerations

- The one-click installer is configured to install per-user by default, not requiring administrator privileges
- All application files are bundled within the installer, ensuring a consistent environment
- Updates can be configured through the `electron-updater` module (not enabled by default)

## Advanced Configuration

For advanced configuration options, including:
- Auto-updates
- Code signing
- Custom installation directories
- Silent installation

Please refer to the [Electron Builder documentation](https://www.electron.build/) and modify the `electron-builder.yml` file accordingly.
