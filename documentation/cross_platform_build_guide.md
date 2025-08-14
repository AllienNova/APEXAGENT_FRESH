# Cross-Platform Build Guide for Aideon AI Lite

This document provides comprehensive guidance for building Aideon AI Lite installers across all supported platforms (Windows, macOS, and Linux) using GitHub Actions CI/CD.

## Overview

Aideon AI Lite requires platform-specific build processes to create native installers for each operating system. While Windows and Linux builds can be created on any platform, macOS DMG installers require a macOS environment due to platform-specific dependencies.

## GitHub Actions CI/CD Pipeline

We've implemented a robust GitHub Actions workflow that automatically builds installers for all platforms:

- **Windows**: NSIS installer (.exe)
- **macOS**: DMG installer (.dmg)
- **Linux**: AppImage (.AppImage) and Debian package (.deb)

### Workflow Structure

The workflow consists of four main jobs:

1. **build-windows**: Builds Windows installers on Windows runners
2. **build-macos**: Builds macOS DMG installers on macOS runners
3. **build-linux**: Builds Linux packages on Linux runners
4. **create-release**: Creates GitHub releases with all installers when tags are pushed
5. **test-installers**: Validates installers on each platform

### Workflow Triggers

The CI/CD pipeline is triggered by:
- Pushes to `main` or `develop` branches
- Any tag starting with `v` (e.g., `v1.0.0`)
- Pull requests to the `main` branch
- Manual dispatch from GitHub Actions UI

## Build Configuration

### Windows Build

Windows builds use electron-builder with NSIS to create:
- Standard installer (.exe)
- Portable version (optional)

Configuration is defined in `electron-builder.json` and `electron-builder.yml`.

### macOS Build

macOS builds require:
- macOS runner (GitHub-hosted or self-hosted)
- dmg-license package (macOS-specific dependency)
- Proper code signing configuration (for production releases)

The DMG installer includes:
- Custom background image
- Application and Applications folder shortcuts
- Icon customization

### Linux Build

Linux builds create:
- AppImage for portable use across distributions
- Debian package for Debian-based distributions (Ubuntu, etc.)

## Local Development Builds

For local development, you can build installers for your current platform:

```bash
# Install dependencies
npm install

# Build for current platform
npm run build

# Platform-specific builds
npm run build:win    # Windows only
npm run build:mac    # macOS only
npm run build:linux  # Linux only
```

Note: Cross-platform builds have limitations:
- Windows and Linux builds can be created on any platform
- macOS DMG installers can only be built on macOS due to platform-specific dependencies

## Code Signing and Notarization

For production releases:

### Windows
- Requires a valid code signing certificate
- Set up in GitHub Secrets as `WINDOWS_CERTIFICATE` and `WINDOWS_CERTIFICATE_PASSWORD`

### macOS
- Requires Apple Developer ID
- Set up in GitHub Secrets as `APPLE_ID` and `APPLE_ID_PASSWORD`
- Notarization is required for distribution outside the App Store

### Linux
- No code signing required for AppImage
- Debian packages can be signed with GPG keys

## Troubleshooting

### Common Issues

1. **macOS DMG build fails**:
   - Ensure you're building on macOS
   - Verify dmg-license is installed
   - Check entitlements configuration

2. **Windows code signing fails**:
   - Verify certificate validity
   - Check certificate password
   - Ensure certificate is properly formatted

3. **Linux build dependencies**:
   - Some Linux builds require additional system libraries
   - See the workflow file for required apt packages

## Release Process

1. Update version in `package.json`
2. Commit changes and push
3. Create and push a tag (e.g., `git tag v1.0.0 && git push --tags`)
4. GitHub Actions will automatically build all installers
5. Verify the release on GitHub Releases page
6. Publish the release when ready

## Future Enhancements

- Automated testing of installers
- Integration with update server
- Telemetry for installation success rates
- Staged rollouts for major updates
