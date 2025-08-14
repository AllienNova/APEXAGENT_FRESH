#!/usr/bin/env node

/**
 * validate_all.js
 * 
 * Comprehensive validation script for Aideon AI Lite
 * Runs all test suites across all platforms and generates detailed reports
 */

const { ValidationExecutor } = require('../src/core/validation/ValidationExecutor');
const path = require('path');
const fs = require('fs-extra');
const os = require('os');

// Configuration
const config = {
  reportDir: path.join(__dirname, '..', 'validation-reports'),
  platforms: ['windows', 'macos', 'linux'],
  suites: 'all',
  verbose: true,
  failFast: false
};

/**
 * Main validation function
 */
async function validateAll() {
  console.log('Starting comprehensive Aideon AI Lite validation...');
  console.log('===============================================');
  
  try {
    // Ensure report directory exists
    await fs.ensureDir(config.reportDir);
    
    // Get current platform
    const currentPlatform = getPlatform();
    console.log(`Current platform: ${currentPlatform}`);
    
    // Create timestamp for reports
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    // Run validation for current platform
    console.log(`\nRunning validation for ${currentPlatform}...`);
    const platformResults = await runPlatformValidation(currentPlatform, timestamp);
    
    // Generate summary report
    await generateSummaryReport(platformResults, timestamp);
    
    console.log('\nValidation complete!');
    console.log(`Summary report: ${path.join(config.reportDir, `summary-${timestamp}.json`)}`);
    
    return platformResults.failed === 0;
  } catch (error) {
    console.error('Validation failed:', error);
    return false;
  }
}

/**
 * Run validation for a specific platform
 */
async function runPlatformValidation(platform, timestamp) {
  // Create platform-specific executor
  const executor = new ValidationExecutor({
    ...config,
    platform,
    reportPath: path.join(config.reportDir, `${platform}-${timestamp}.json`)
  });
  
  // Run validation
  const startTime = Date.now();
  const results = await executor.execute();
  const endTime = Date.now();
  
  // Display results
  console.log(`\nResults for ${platform}:`);
  console.log(`Total Tests: ${results.total}`);
  console.log(`Passed: ${results.passed}`);
  console.log(`Failed: ${results.failed}`);
  console.log(`Skipped: ${results.skipped}`);
  console.log(`Duration: ${(endTime - startTime) / 1000} seconds`);
  
  // Display failed tests if any
  if (results.failed > 0 && results.failedTests && results.failedTests.length > 0) {
    console.log('\nFailed Tests:');
    results.failedTests.forEach((test, index) => {
      console.log(`\n${index + 1}. ${test.suite} - ${test.name}`);
      console.log(`   Error: ${test.error}`);
    });
  }
  
  return {
    platform,
    ...results,
    duration: endTime - startTime
  };
}

/**
 * Generate summary report
 */
async function generateSummaryReport(platformResults, timestamp) {
  const summary = {
    timestamp: new Date().toISOString(),
    platforms: [platformResults],
    overall: {
      total: platformResults.total,
      passed: platformResults.passed,
      failed: platformResults.failed,
      skipped: platformResults.skipped,
      duration: platformResults.duration
    }
  };
  
  // Write summary report
  await fs.writeJson(
    path.join(config.reportDir, `summary-${timestamp}.json`),
    summary,
    { spaces: 2 }
  );
  
  return summary;
}

/**
 * Get current platform
 */
function getPlatform() {
  const platform = os.platform();
  
  if (platform === 'win32') {
    return 'windows';
  } else if (platform === 'darwin') {
    return 'macos';
  } else {
    return 'linux';
  }
}

// Run validation if executed directly
if (require.main === module) {
  validateAll().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = { validateAll };
