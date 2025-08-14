#!/usr/bin/env node

/**
 * run_validation.js
 * 
 * Command-line tool for running validation tests for Aideon AI Lite
 */

const { ValidationExecutor } = require('./ValidationExecutor');
const path = require('path');
const fs = require('fs');
const { program } = require('commander');

// Configure command-line options
program
  .option('-s, --suite <name>', 'Run a specific test suite (default: all)')
  .option('-v, --verbose', 'Show detailed output')
  .option('-r, --report <path>', 'Save report to file')
  .option('-f, --fail-fast', 'Stop on first failure')
  .option('-p, --platform <name>', 'Run tests for specific platform (default: current)')
  .parse(process.argv);

const options = program.opts();

// Default configuration
const config = {
  suites: options.suite === 'all' ? 'all' : [options.suite || 'all'],
  verbose: options.verbose || false,
  failFast: options.failFast || false,
  reportPath: options.report || null,
  platform: options.platform || 'current',
  dataDir: path.join(__dirname, '..', '..', '..', 'test-data')
};

/**
 * Main validation function
 */
async function runValidation() {
  console.log('Starting Aideon AI Lite validation...');
  
  try {
    // Ensure test data directory exists
    if (!fs.existsSync(config.dataDir)) {
      fs.mkdirSync(config.dataDir, { recursive: true });
    }
    
    // Create validation executor
    const executor = new ValidationExecutor(config);
    
    // Run validation
    const startTime = Date.now();
    const results = await executor.execute();
    const endTime = Date.now();
    
    // Display results
    console.log('\nValidation Results:');
    console.log('------------------');
    console.log(`Total Tests: ${results.total}`);
    console.log(`Passed: ${results.passed}`);
    console.log(`Failed: ${results.failed}`);
    console.log(`Skipped: ${results.skipped}`);
    console.log(`Duration: ${(endTime - startTime) / 1000} seconds`);
    
    // Display failed tests if any
    if (results.failed > 0 && results.failedTests.length > 0) {
      console.log('\nFailed Tests:');
      results.failedTests.forEach((test, index) => {
        console.log(`\n${index + 1}. ${test.suite} - ${test.name}`);
        console.log(`   Error: ${test.error}`);
      });
    }
    
    // Save report if requested
    if (config.reportPath) {
      const reportDir = path.dirname(config.reportPath);
      if (!fs.existsSync(reportDir)) {
        fs.mkdirSync(reportDir, { recursive: true });
      }
      
      fs.writeFileSync(config.reportPath, JSON.stringify(results, null, 2));
      console.log(`\nReport saved to: ${config.reportPath}`);
    }
    
    // Return exit code based on results
    return results.failed === 0 ? 0 : 1;
  } catch (error) {
    console.error('Validation failed:', error);
    return 1;
  }
}

// Run validation if executed directly
if (require.main === module) {
  runValidation().then(exitCode => {
    process.exit(exitCode);
  });
}

module.exports = { runValidation };
