#!/usr/bin/env node

/**
 * build-installers.js
 * 
 * Script to build one-click installers for all platforms
 * Includes all dependencies and ensures seamless installation
 */

const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');
const os = require('os');

// Configuration
const config = {
  appName: 'Aideon AI Lite',
  version: '1.0.0',
  platforms: ['win', 'mac', 'linux'],
  outputDir: path.join(__dirname, '..', 'dist'),
  assetsDir: path.join(__dirname, '..', 'assets'),
  iconsDir: path.join(__dirname, '..', 'assets', 'icons')
};

/**
 * Main build function
 */
async function buildInstallers() {
  try {
    console.log(`\n🚀 Building one-click installers for ${config.appName} v${config.version}\n`);
    
    // Ensure output directory exists
    await fs.ensureDir(config.outputDir);
    
    // Ensure assets directory exists
    await fs.ensureDir(config.assetsDir);
    
    // Ensure icons directory exists
    await fs.ensureDir(config.iconsDir);
    await fs.ensureDir(path.join(config.iconsDir, 'win'));
    await fs.ensureDir(path.join(config.iconsDir, 'mac'));
    await fs.ensureDir(path.join(config.iconsDir, 'linux'));
    
    // Create placeholder icons if they don't exist
    await createPlaceholderIcons();
    
    // Create entitlements file for macOS
    await createMacEntitlements();
    
    // Create DMG background for macOS
    await createDmgBackground();
    
    // Install dependencies if needed
    await installDependencies();
    
    // Build installers for each platform
    for (const platform of config.platforms) {
      await buildForPlatform(platform);
    }
    
    console.log(`\n✅ All installers built successfully!\n`);
    console.log(`📦 Installers are available in: ${config.outputDir}\n`);
    
    // List built installers
    const files = await fs.readdir(config.outputDir);
    const installers = files.filter(file => 
      file.endsWith('.exe') || 
      file.endsWith('.dmg') || 
      file.endsWith('.AppImage') || 
      file.endsWith('.deb')
    );
    
    if (installers.length > 0) {
      console.log('📋 Built installers:');
      installers.forEach(installer => {
        console.log(`   - ${installer}`);
      });
      console.log('');
    }
    
  } catch (error) {
    console.error(`❌ Error building installers: ${error.message}`);
    process.exit(1);
  }
}

/**
 * Build installer for specific platform
 */
async function buildForPlatform(platform) {
  console.log(`\n🔨 Building for ${getPlatformName(platform)}...`);
  
  try {
    // Run electron-builder for platform
    execSync(`npm run package:${platform}`, {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    
    console.log(`✅ ${getPlatformName(platform)} installer built successfully!`);
  } catch (error) {
    console.error(`❌ Error building ${getPlatformName(platform)} installer: ${error.message}`);
    throw error;
  }
}

/**
 * Install dependencies if needed
 */
async function installDependencies() {
  console.log('\n📦 Checking dependencies...');
  
  try {
    // Check if node_modules exists
    const nodeModulesPath = path.join(__dirname, '..', 'node_modules');
    const hasNodeModules = await fs.pathExists(nodeModulesPath);
    
    if (!hasNodeModules) {
      console.log('📦 Installing dependencies...');
      
      execSync('npm install', {
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
      });
      
      console.log('✅ Dependencies installed successfully!');
    } else {
      console.log('✅ Dependencies already installed.');
    }
  } catch (error) {
    console.error(`❌ Error installing dependencies: ${error.message}`);
    throw error;
  }
}

/**
 * Create placeholder icons if they don't exist
 */
async function createPlaceholderIcons() {
  console.log('\n🖼️ Checking application icons...');
  
  const iconPaths = {
    win: path.join(config.iconsDir, 'win', 'icon.ico'),
    mac: path.join(config.iconsDir, 'mac', 'icon.icns'),
    linux: path.join(config.iconsDir, 'linux', 'icon.png')
  };
  
  for (const [platform, iconPath] of Object.entries(iconPaths)) {
    const hasIcon = await fs.pathExists(iconPath);
    
    if (!hasIcon) {
      console.log(`🖼️ Creating placeholder icon for ${getPlatformName(platform)}...`);
      
      // For simplicity, we'll create a basic PNG icon for all platforms
      // In a real scenario, you'd want to convert to the appropriate format
      await createPlaceholderPng(iconPath);
      
      console.log(`✅ Placeholder icon created for ${getPlatformName(platform)}.`);
    } else {
      console.log(`✅ Icon for ${getPlatformName(platform)} already exists.`);
    }
  }
}

/**
 * Create a placeholder PNG icon
 * This is a very basic implementation - in a real scenario, you'd want to use
 * a proper icon generation library or pre-made icons
 */
async function createPlaceholderPng(iconPath) {
  // Ensure directory exists
  await fs.ensureDir(path.dirname(iconPath));
  
  // For this example, we'll just copy a placeholder icon if it exists
  // or create a very basic one if not
  const placeholderPath = path.join(__dirname, '..', 'assets', 'placeholder-icon.png');
  
  if (await fs.pathExists(placeholderPath)) {
    await fs.copy(placeholderPath, iconPath);
  } else {
    // This would be where you'd generate an icon
    // For now, we'll just write a message
    await fs.writeFile(iconPath, 'Placeholder Icon');
  }
}

/**
 * Create entitlements file for macOS
 */
async function createMacEntitlements() {
  const entitlementsPath = path.join(config.assetsDir, 'entitlements.mac.plist');
  const hasEntitlements = await fs.pathExists(entitlementsPath);
  
  if (!hasEntitlements) {
    console.log('📝 Creating macOS entitlements file...');
    
    const entitlements = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
  </dict>
</plist>`;
    
    await fs.writeFile(entitlementsPath, entitlements);
    console.log('✅ macOS entitlements file created.');
  } else {
    console.log('✅ macOS entitlements file already exists.');
  }
}

/**
 * Create DMG background for macOS
 */
async function createDmgBackground() {
  const backgroundPath = path.join(config.assetsDir, 'dmg-background.png');
  const hasBackground = await fs.pathExists(backgroundPath);
  
  if (!hasBackground) {
    console.log('🖼️ Creating DMG background for macOS...');
    
    // For this example, we'll just create a placeholder file
    // In a real scenario, you'd want to use a proper image
    await fs.writeFile(backgroundPath, 'DMG Background Placeholder');
    
    console.log('✅ DMG background created.');
  } else {
    console.log('✅ DMG background already exists.');
  }
}

/**
 * Get human-readable platform name
 */
function getPlatformName(platform) {
  const names = {
    win: 'Windows',
    mac: 'macOS',
    linux: 'Linux'
  };
  
  return names[platform] || platform;
}

// Run the build process
buildInstallers().catch(error => {
  console.error(`❌ Build failed: ${error.message}`);
  process.exit(1);
});
