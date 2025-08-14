#!/usr/bin/env node

/**
 * create-app-icons.js
 * 
 * Script to generate application icons for all platforms
 */

const fs = require('fs-extra');
const path = require('path');
const { createCanvas } = require('canvas');

// Configuration
const config = {
  appName: 'Aideon AI Lite',
  outputDir: path.join(__dirname, '..', 'assets', 'icons'),
  sizes: {
    win: [16, 24, 32, 48, 64, 128, 256],
    mac: [16, 32, 64, 128, 256, 512, 1024],
    linux: [16, 24, 32, 48, 64, 128, 256, 512]
  },
  colors: {
    primary: '#3a86ff',
    secondary: '#8338ec',
    accent: '#ff006e',
    background: '#16213e'
  }
};

/**
 * Main function to generate all icons
 */
async function generateIcons() {
  console.log(`\n🖼️ Generating application icons for ${config.appName}\n`);
  
  try {
    // Ensure output directories exist
    await fs.ensureDir(path.join(config.outputDir, 'win'));
    await fs.ensureDir(path.join(config.outputDir, 'mac'));
    await fs.ensureDir(path.join(config.outputDir, 'linux'));
    
    // Generate Windows icon
    await generateWindowsIcon();
    
    // Generate macOS icon
    await generateMacIcon();
    
    // Generate Linux icons
    await generateLinuxIcons();
    
    console.log('\n✅ All icons generated successfully!\n');
  } catch (error) {
    console.error(`\n❌ Error generating icons: ${error.message}\n`);
    process.exit(1);
  }
}

/**
 * Generate Windows icon (.ico)
 */
async function generateWindowsIcon() {
  console.log('🖼️ Generating Windows icon...');
  
  // For now, we'll create a PNG and save it as .ico
  // In a real scenario, you'd want to use a library to create a proper .ico file
  const iconPath = path.join(config.outputDir, 'win', 'icon.ico');
  
  // Generate a 256x256 icon
  const canvas = createCanvas(256, 256);
  const ctx = canvas.getContext('2d');
  
  // Draw icon
  drawAppIcon(ctx, 256);
  
  // Save as PNG for now
  const buffer = canvas.toBuffer('image/png');
  await fs.writeFile(iconPath, buffer);
  
  console.log('✅ Windows icon generated.');
}

/**
 * Generate macOS icon (.icns)
 */
async function generateMacIcon() {
  console.log('🖼️ Generating macOS icon...');
  
  // For now, we'll create a PNG and save it as .icns
  // In a real scenario, you'd want to use a library to create a proper .icns file
  const iconPath = path.join(config.outputDir, 'mac', 'icon.icns');
  
  // Generate a 1024x1024 icon
  const canvas = createCanvas(1024, 1024);
  const ctx = canvas.getContext('2d');
  
  // Draw icon
  drawAppIcon(ctx, 1024);
  
  // Save as PNG for now
  const buffer = canvas.toBuffer('image/png');
  await fs.writeFile(iconPath, buffer);
  
  console.log('✅ macOS icon generated.');
}

/**
 * Generate Linux icons (multiple PNGs)
 */
async function generateLinuxIcons() {
  console.log('🖼️ Generating Linux icons...');
  
  // Create main icon
  const iconPath = path.join(config.outputDir, 'linux', 'icon.png');
  
  // Generate a 512x512 icon
  const canvas = createCanvas(512, 512);
  const ctx = canvas.getContext('2d');
  
  // Draw icon
  drawAppIcon(ctx, 512);
  
  // Save as PNG
  const buffer = canvas.toBuffer('image/png');
  await fs.writeFile(iconPath, buffer);
  
  console.log('✅ Linux icons generated.');
}

/**
 * Draw the application icon on a canvas
 */
function drawAppIcon(ctx, size) {
  const { primary, secondary, accent, background } = config.colors;
  
  // Draw background
  ctx.fillStyle = background;
  ctx.fillRect(0, 0, size, size);
  
  // Draw a rounded rectangle
  const padding = size * 0.15;
  const rectSize = size - (padding * 2);
  const radius = rectSize * 0.2;
  
  ctx.fillStyle = primary;
  roundRect(ctx, padding, padding, rectSize, rectSize, radius, true);
  
  // Draw an "A" letter
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${size * 0.5}px Arial`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('A', size / 2, size / 2);
  
  // Draw accent circle
  ctx.fillStyle = accent;
  ctx.beginPath();
  ctx.arc(size * 0.75, size * 0.25, size * 0.15, 0, Math.PI * 2);
  ctx.fill();
}

/**
 * Helper function to draw a rounded rectangle
 */
function roundRect(ctx, x, y, width, height, radius, fill) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
  
  if (fill) {
    ctx.fill();
  } else {
    ctx.stroke();
  }
}

// Run the icon generation
generateIcons().catch(error => {
  console.error(`❌ Icon generation failed: ${error.message}`);
  process.exit(1);
});
