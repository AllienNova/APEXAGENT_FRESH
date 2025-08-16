#!/usr/bin/env node
/**
 * update_github.js
 * 
 * Script to update the GitHub repository with the latest code and documentation
 * for Aideon AI Lite
 */
const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

// Configuration
const config = {
  repoUrl: 'https://github.com/AllienNova/ApexAgent.git',
  branch: 'main',
  // Use environment variable for token, never hardcode tokens
  token: process.env.GITHUB_TOKEN,
  commitMessage: 'Update Aideon AI Lite with latest features and documentation',
  tempDir: path.join(require('os').tmpdir(), 'aideon-github-update')
};

/**
 * Main update function
 */
async function updateGitHub() {
  try {
    console.log('Starting GitHub repository update...');
    
    // Check for GitHub token
    if (!config.token) {
      console.error('Error: GitHub token not found in environment variables.');
      console.error('Please set the GITHUB_TOKEN environment variable before running this script.');
      console.error('Example: GITHUB_TOKEN=your_token node update_github.js');
      return false;
    }
    
    // Prepare directories
    await prepareDirectories();
    
    // Clone repository
    await cloneRepository();
    
    // Copy latest files
    await copyLatestFiles();
    
    // Commit and push changes
    await commitAndPush();
    
    console.log('GitHub repository update completed successfully!');
    return true;
  } catch (error) {
    console.error('GitHub update failed:', error);
    return false;
  }
}

/**
 * Prepare directories for update
 */
async function prepareDirectories() {
  console.log('Preparing directories...');
  
  // Create temp directory
  await fs.ensureDir(config.tempDir);
  await fs.emptyDir(config.tempDir);
  
  console.log('Directories prepared.');
}

/**
 * Clone the repository
 */
async function cloneRepository() {
  console.log('Cloning repository...');
  
  try {
    // Clone with token for authentication
    const cloneUrl = config.repoUrl.replace('https://', `https://${config.token}@`);
    
    execSync(`git clone ${cloneUrl} ${config.tempDir}`, {
      stdio: 'inherit'
    });
    
    // Configure git user
    execSync('git config user.name "Aideon AI Bot"', {
      cwd: config.tempDir,
      stdio: 'inherit'
    });
    
    execSync('git config user.email "bot@aideonai.com"', {
      cwd: config.tempDir,
      stdio: 'inherit'
    });
    
    console.log('Repository cloned successfully.');
  } catch (error) {
    console.error('Failed to clone repository:', error);
    throw error;
  }
}

/**
 * Copy latest files to the repository
 */
async function copyLatestFiles() {
  console.log('Copying latest files...');
  
  try {
    // Source directory (current project)
    const sourceDir = path.join(__dirname, '..');
    
    // Directories to copy
    const dirsToCopy = [
      'src',
      'documentation',
      'scripts',
      'assets'
    ];
    
    // Files to copy
    const filesToCopy = [
      'package.json',
      'package-lock.json',
      'electron-builder.yml',
      'README.md'
    ];
    
    // Copy directories
    for (const dir of dirsToCopy) {
      const source = path.join(sourceDir, dir);
      const destination = path.join(config.tempDir, dir);
      
      // Check if source exists
      if (await fs.pathExists(source)) {
        // Ensure destination directory exists
        await fs.ensureDir(destination);
        
        // Copy directory
        await fs.copy(source, destination, {
          overwrite: true,
          errorOnExist: false
        });
        
        console.log(`Copied directory: ${dir}`);
      }
    }
    
    // Copy files
    for (const file of filesToCopy) {
      const source = path.join(sourceDir, file);
      const destination = path.join(config.tempDir, file);
      
      // Check if source exists
      if (await fs.pathExists(source)) {
        // Copy file
        await fs.copy(source, destination, {
          overwrite: true,
          errorOnExist: false
        });
        
        console.log(`Copied file: ${file}`);
      }
    }
    
    console.log('Files copied successfully.');
  } catch (error) {
    console.error('Failed to copy files:', error);
    throw error;
  }
}

/**
 * Commit and push changes
 */
async function commitAndPush() {
  console.log('Committing and pushing changes...');
  
  try {
    // Add all files
    execSync('git add -A', {
      cwd: config.tempDir,
      stdio: 'inherit'
    });
    
    // Commit changes
    execSync(`git commit -m "${config.commitMessage}"`, {
      cwd: config.tempDir,
      stdio: 'inherit'
    });
    
    // Push changes
    execSync(`git push origin ${config.branch}`, {
      cwd: config.tempDir,
      stdio: 'inherit'
    });
    
    console.log('Changes committed and pushed successfully.');
  } catch (error) {
    console.error('Failed to commit and push changes:', error);
    throw error;
  }
}

// Run update if executed directly
if (require.main === module) {
  updateGitHub().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = { updateGitHub };
