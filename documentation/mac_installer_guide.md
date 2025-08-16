# macOS Installer Guide for Aideon AI Lite

This document provides detailed instructions for building, testing, and distributing the macOS DMG installer for Aideon AI Lite.

## Prerequisites

Building a proper macOS DMG installer requires:

- **macOS Environment**: Due to platform-specific dependencies like `dmg-license` and Apple's code signing tools, DMG installers can only be built on macOS.
- **Node.js**: Version 18 or later
- **Xcode Command Line Tools**: For code signing and notarization
- **Apple Developer Account**: For code signing and notarization (production releases only)

## Build Process

### Automated Builds via GitHub Actions

We've implemented a GitHub Actions workflow that automatically builds macOS DMG installers on macOS runners. This is the recommended approach for consistent, reproducible builds.

The workflow:
1. Runs on macOS GitHub-hosted runners
2. Installs all dependencies, including the macOS-specific `dmg-license` package
3. Builds the DMG installer with proper configuration
4. Uploads the installer as an artifact
5. Creates GitHub releases for tagged versions

### Manual Builds on macOS

For local development on macOS:

```bash
# Clone the repository
git clone https://github.com/AllienNova/ApexAgent.git
cd ApexAgent

# Install dependencies
npm install
npm install dmg-license --save-dev

# Build macOS DMG installer
npm run build:mac
```

The DMG installer will be created in the `dist` directory.

## DMG Installer Features

The Aideon AI Lite DMG installer includes:

- Custom background image with application and Applications folder shortcuts
- Proper icon and branding
- Automatic mounting and unmounting
- Drag-and-drop installation experience
- Support for both Intel (x64) and Apple Silicon (arm64) Macs

## Code Signing and Notarization

For production releases, macOS installers should be code signed and notarized:

1. **Code Signing**: Signs the application with your Developer ID
   ```bash
   # Configured in electron-builder.yml
   ```

2. **Notarization**: Submits the signed app to Apple for notarization
   ```bash
   # Handled automatically by electron-builder with proper configuration
   ```

### Configuration

Code signing and notarization are configured in `electron-builder.yml`:

```yaml
mac:
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: assets/entitlements.mac.plist
  entitlementsInherit: assets/entitlements.mac.plist
```

## Testing

Before distribution, test the DMG installer:

1. Mount the DMG by double-clicking it
2. Drag the application to the Applications folder
3. Unmount the DMG
4. Launch the application from the Applications folder
5. Verify all functionality works as expected
6. Test on both Intel and Apple Silicon Macs if possible

## Troubleshooting

### Common Issues

1. **DMG Creation Fails**:
   - Ensure `dmg-license` is installed
   - Verify the background image exists and is properly formatted
   - Check that all icon files are valid

2. **Code Signing Fails**:
   - Verify your Developer ID certificate is valid and installed
   - Check that entitlements files exist and are properly formatted
   - Ensure you have the correct signing identity specified

3. **Notarization Fails**:
   - Check Apple Developer account credentials
   - Verify the app meets Apple's security requirements
   - Review notarization logs for specific issues

## Distribution

Once built and tested, the DMG installer can be distributed through:

1. **GitHub Releases**: Automatically created by our CI/CD pipeline
2. **Website Downloads**: Upload the DMG to your website for direct downloads
3. **Update Server**: Configure electron-updater to provide automatic updates

## Platform-Specific Considerations

- **Apple Silicon Support**: The DMG includes universal binaries for both Intel and Apple Silicon Macs
- **macOS Version Compatibility**: Tested and supported on macOS 10.15 (Catalina) and later
- **Security Features**: Includes hardened runtime and proper entitlements for modern macOS security requirements

## Future Enhancements

- App Store distribution option
- Enhanced update mechanism with delta updates
- Improved installation analytics
- Custom installation options
