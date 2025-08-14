# Aideon AI Lite Cross-Platform Installer Documentation

This directory contains comprehensive documentation for the Aideon AI Lite cross-platform installer build system.

## Overview

Aideon AI Lite is distributed as native installers for Windows, macOS, and Linux platforms. These installers are built using a robust GitHub Actions CI/CD pipeline that ensures consistent, reproducible builds across all supported operating systems.

## Documentation Index

1. [Cross-Platform Build Guide](./cross_platform_build_guide.md) - Complete guide to building installers for all platforms
2. [macOS Installer Guide](./mac_installer_guide.md) - Detailed instructions for macOS DMG installer builds
3. [GitHub Actions Workflow Guide](./github_actions_workflow_guide.md) - Comprehensive guide to the CI/CD pipeline

## Key Features

- **Windows Installer**: NSIS-based installer with desktop and start menu shortcuts
- **macOS DMG Installer**: Custom-branded DMG with drag-and-drop installation
- **Linux Packages**: AppImage for portable use and Debian package for system integration
- **Automated Builds**: GitHub Actions workflows for continuous integration and delivery
- **Code Signing**: Support for platform-specific code signing and notarization

## Getting Started

To build installers locally, refer to the [Cross-Platform Build Guide](./cross_platform_build_guide.md).

For automated builds via GitHub Actions, refer to the [GitHub Actions Workflow Guide](./github_actions_workflow_guide.md).

## Platform-Specific Considerations

### Windows
- Supports Windows 10 and later
- Includes both 64-bit installer and portable versions

### macOS
- Supports macOS 10.15 (Catalina) and later
- Universal binary for both Intel and Apple Silicon Macs
- DMG installer requires macOS for building due to platform-specific dependencies

### Linux
- AppImage for portable use across distributions
- Debian package for Ubuntu and other Debian-based distributions

## Troubleshooting

For common issues and solutions, refer to the platform-specific guides:
- Windows: See Cross-Platform Build Guide
- macOS: See macOS Installer Guide
- Linux: See Cross-Platform Build Guide

## Future Enhancements

- Automated testing of installers
- Integration with update server
- Telemetry for installation success rates
- Staged rollouts for major updates
