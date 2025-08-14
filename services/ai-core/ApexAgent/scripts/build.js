#!/usr/bin/env node

/**
 * build.js
 * 
 * Build script for Aideon AI Lite
 * Creates packaged applications for Windows, macOS, and Linux
 */

const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');
const os = require('os');

// Configuration
const config = {
  platforms: ['win', 'mac', 'linux'],
  outputDir: path.join(__dirname, '..', 'dist'),
  assetsDir: path.join(__dirname, '..', 'assets'),
  tempDir: path.join(os.tmpdir(), 'aideon-build')
};

/**
 * Main build function
 */
async function build() {
  try {
    console.log('Starting Aideon AI Lite build process...');
    
    // Prepare directories
    await prepareDirectories();
    
    // Install dependencies
    await installDependencies();
    
    // Build for all platforms
    for (const platform of config.platforms) {
      await buildForPlatform(platform);
    }
    
    // Create checksums
    await createChecksums();
    
    // Create release notes
    await createReleaseNotes();
    
    console.log('Build process completed successfully!');
    console.log(`Packaged applications available in: ${config.outputDir}`);
    
    return true;
  } catch (error) {
    console.error('Build failed:', error);
    return false;
  }
}

/**
 * Prepare directories for build
 */
async function prepareDirectories() {
  console.log('Preparing directories...');
  
  // Ensure output directory exists
  await fs.ensureDir(config.outputDir);
  
  // Clean output directory
  await fs.emptyDir(config.outputDir);
  
  // Create temp directory
  await fs.ensureDir(config.tempDir);
  await fs.emptyDir(config.tempDir);
  
  console.log('Directories prepared.');
}

/**
 * Install dependencies
 */
async function installDependencies() {
  console.log('Installing dependencies...');
  
  try {
    // Install production dependencies
    execSync('npm install --production', {
      stdio: 'inherit'
    });
    
    console.log('Dependencies installed successfully.');
  } catch (error) {
    console.error('Failed to install dependencies:', error);
    throw error;
  }
}

/**
 * Build for a specific platform
 * 
 * @param {string} platform - Target platform (win, mac, linux)
 */
async function buildForPlatform(platform) {
  console.log(`Building for ${platform}...`);
  
  try {
    // Run electron-builder for platform
    execSync(`npm run package:${platform}`, {
      stdio: 'inherit'
    });
    
    console.log(`Build for ${platform} completed.`);
  } catch (error) {
    console.error(`Failed to build for ${platform}:`, error);
    throw error;
  }
}

/**
 * Create checksums for all packaged files
 */
async function createChecksums() {
  console.log('Creating checksums...');
  
  try {
    // Get all files in output directory
    const files = await fs.readdir(config.outputDir);
    
    // Create checksums file
    const checksumPath = path.join(config.outputDir, 'checksums.txt');
    let checksumContent = '';
    
    for (const file of files) {
      // Skip directories and checksums file
      const filePath = path.join(config.outputDir, file);
      const stats = await fs.stat(filePath);
      
      if (stats.isDirectory() || file === 'checksums.txt') {
        continue;
      }
      
      // Generate SHA-256 checksum
      const checksum = execSync(`sha256sum "${filePath}"`, {
        encoding: 'utf8'
      });
      
      checksumContent += `${checksum}`;
    }
    
    // Write checksums file
    await fs.writeFile(checksumPath, checksumContent);
    
    console.log('Checksums created.');
  } catch (error) {
    console.error('Failed to create checksums:', error);
    throw error;
  }
}

/**
 * Create release notes
 */
async function createReleaseNotes() {
  console.log('Creating release notes...');
  
  try {
    // Read package.json for version
    const packageJson = await fs.readJson(path.join(__dirname, '..', 'package.json'));
    const version = packageJson.version;
    
    // Create release notes content
    const releaseNotes = `# Aideon AI Lite v${version}

## Release Notes

### New Features
- Comprehensive domain-specific tool providers across 15 domains
- IDE integration with VS Code, JetBrains IDEs, Eclipse, Sublime Text, and GitHub
- Device synchronization for seamless work across multiple devices
- Voice command system for hands-free control
- Context-aware automation for intelligent task handling
- Personal knowledge management for organizing information
- Computer vision capabilities for image analysis
- Advanced AI model selection for optimal performance
- Offline capabilities for working without internet connection
- User dashboard for monitoring and control

### Improvements
- Enhanced performance and reliability
- Improved user interface and experience
- Better error handling and recovery
- More comprehensive documentation

### System Requirements
- Operating System: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- Processor: 4+ core CPU (8+ cores recommended)
- Memory: 8GB RAM minimum (16GB+ recommended)
- Storage: 10GB free space (20GB+ recommended for offline capabilities)
- Internet: Broadband connection (5+ Mbps)
- Graphics: OpenGL 3.3+ compatible GPU (for computer vision features)

### Installation Instructions
1. Download the appropriate installer for your platform
2. Run the installer and follow the on-screen instructions
3. Launch Aideon AI Lite and complete the initial setup

For detailed instructions, please refer to the User Onboarding Guide.

© 2025 Aideon AI - The World's First Truly Hybrid Autonomous AI System`;
    
    // Write release notes file
    const releaseNotesPath = path.join(config.outputDir, 'RELEASE_NOTES.md');
    await fs.writeFile(releaseNotesPath, releaseNotes);
    
    console.log('Release notes created.');
  } catch (error) {
    console.error('Failed to create release notes:', error);
    throw error;
  }
}

// Run build if executed directly
if (require.main === module) {
  build().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = { build };
