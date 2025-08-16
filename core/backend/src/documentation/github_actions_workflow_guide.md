# GitHub Actions Workflow Guide for Aideon AI Lite

This document provides a comprehensive guide to the GitHub Actions CI/CD pipeline implemented for Aideon AI Lite cross-platform builds.

## Overview

The GitHub Actions workflow automates the building, testing, and distribution of Aideon AI Lite installers for Windows, macOS, and Linux platforms. This ensures consistent, reproducible builds across all supported operating systems.

## Workflow Structure

The workflow is defined in `.github/workflows/build-release.yml` and consists of the following jobs:

### 1. build-windows
- **Runner**: Windows latest
- **Purpose**: Build Windows installers (.exe, portable)
- **Key Steps**:
  - Set up Node.js and Python environments
  - Install dependencies
  - Build Windows installers
  - Upload artifacts for release

### 2. build-macos
- **Runner**: macOS latest
- **Purpose**: Build macOS DMG installers
- **Key Steps**:
  - Set up Node.js and Python environments
  - Install dependencies including macOS-specific `dmg-license`
  - Build macOS DMG installers
  - Upload artifacts for release

### 3. build-linux
- **Runner**: Ubuntu latest
- **Purpose**: Build Linux packages (AppImage, deb)
- **Key Steps**:
  - Set up Node.js and Python environments
  - Install system dependencies
  - Build Linux packages
  - Upload artifacts for release

### 4. create-release
- **Runner**: Ubuntu latest
- **Purpose**: Create GitHub releases with all installers
- **Trigger**: Only runs when a tag is pushed (e.g., v1.0.0)
- **Dependencies**: Requires all build jobs to complete successfully
- **Key Steps**:
  - Download all artifacts
  - Create GitHub release
  - Attach all installers to the release

### 5. test-installers
- **Runner**: Matrix of Windows, macOS, and Linux
- **Purpose**: Validate installers on each platform
- **Dependencies**: Requires all build jobs to complete successfully
- **Key Steps**:
  - Download platform-specific artifacts
  - Perform basic validation tests

## Workflow Triggers

The CI/CD pipeline is triggered by:
- Pushes to `main` or `develop` branches
- Any tag starting with `v` (e.g., `v1.0.0`)
- Pull requests to the `main` branch
- Manual dispatch from GitHub Actions UI

## Environment Variables

The workflow uses the following environment variables:
- `NODE_VERSION`: Node.js version (currently 18)
- `PYTHON_VERSION`: Python version (currently 3.11)

## Secrets Management

For production builds with code signing, the following secrets should be configured in GitHub:

### Windows Code Signing
- `WINDOWS_CERTIFICATE`: Base64-encoded certificate
- `WINDOWS_CERTIFICATE_PASSWORD`: Certificate password

### macOS Code Signing and Notarization
- `APPLE_ID`: Apple Developer ID
- `APPLE_ID_PASSWORD`: App-specific password
- `APPLE_TEAM_ID`: Team identifier

## Error Handling and Recovery

The workflow implements robust error handling:

1. **Job Dependencies**: Jobs are properly sequenced with dependencies
2. **Artifact Retention**: Artifacts are retained for 30 days for debugging
3. **Conditional Execution**: Release creation only occurs on tag pushes
4. **Matrix Testing**: Installers are tested on all target platforms

## Monitoring and Debugging

To monitor workflow runs:
1. Go to the GitHub repository
2. Click on "Actions" tab
3. Select the workflow run to view
4. Expand job details to see logs

For debugging failed builds:
1. Check the specific job that failed
2. Review error messages in the logs
3. Download artifacts for inspection
4. Make necessary adjustments to code or configuration
5. Re-run the workflow

## Customization

The workflow can be customized by modifying:
- `.github/workflows/build-release.yml`: Main workflow definition
- `electron-builder.json` and `electron-builder.yml`: Build configuration
- `package.json`: Build scripts and dependencies

## Best Practices

1. **Version Tagging**: Use semantic versioning for tags (e.g., v1.0.0)
2. **Branch Protection**: Enable branch protection for main branch
3. **Code Reviews**: Require code reviews for PRs to main
4. **Test Coverage**: Ensure comprehensive tests before merging
5. **Artifact Management**: Clean up old artifacts periodically

## Troubleshooting Common Issues

### Windows Build Issues
- Ensure proper icon files are available
- Verify NSIS configuration is correct
- Check Windows-specific dependencies

### macOS Build Issues
- Verify macOS runner is available
- Ensure dmg-license is properly installed
- Check entitlements configuration

### Linux Build Issues
- Verify system dependencies are installed
- Check AppImage configuration
- Ensure proper permissions for executable files

## Future Enhancements

1. **Automated Testing**: Expand test coverage for installers
2. **Release Notes Generation**: Automate changelog creation
3. **Deployment Integration**: Connect to update server
4. **Telemetry**: Add installation success tracking
5. **Staged Rollouts**: Implement phased release strategy

## Conclusion

This GitHub Actions workflow provides a robust, automated pipeline for building, testing, and distributing Aideon AI Lite installers across all supported platforms. By leveraging platform-specific runners, we ensure that each installer is built in its native environment, providing the best possible experience for end users.
