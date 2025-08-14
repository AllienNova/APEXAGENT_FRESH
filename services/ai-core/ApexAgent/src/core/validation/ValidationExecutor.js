/**
 * ValidationExecutor.js
 * 
 * Core validation execution engine for Aideon AI Lite
 * Manages test suite execution, result collection, and reporting
 */

const path = require('path');
const fs = require('fs-extra');
const { GeneralToolTestSuite } = require('./tests/GeneralToolTestSuite');
const { IDEIntegrationTestSuite } = require('./tests/IDEIntegrationTestSuite');
const { ComputerVisionTestSuite } = require('./tests/ComputerVisionTestSuite');
const { DeviceSyncTestSuite } = require('./tests/DeviceSyncTestSuite');
const { LocalInteractionTestSuite } = require('./tests/LocalInteractionTestSuite');
const { PerformanceTestSuite } = require('./tests/PerformanceTestSuite');

/**
 * ValidationExecutor class
 * Manages the execution of validation test suites
 */
class ValidationExecutor {
  /**
   * Constructor
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    this.config = {
      suites: config.suites || 'all',
      verbose: config.verbose || false,
      failFast: config.failFast || false,
      reportPath: config.reportPath || null,
      platform: config.platform || 'current',
      dataDir: config.dataDir || path.join(__dirname, '..', '..', '..', 'test-data')
    };
    
    // Initialize available test suites
    this.availableSuites = {
      'general': () => new GeneralToolTestSuite(this.config),
      'ide': () => new IDEIntegrationTestSuite(this.config),
      'vision': () => new ComputerVisionTestSuite(this.config),
      'sync': () => new DeviceSyncTestSuite(this.config),
      'local': () => new LocalInteractionTestSuite(this.config),
      'performance': () => new PerformanceTestSuite(this.config)
    };
  }
  
  /**
   * Execute validation
   * @returns {Promise<Object>} - Validation results
   */
  async execute() {
    console.log(`Executing validation with ${this.config.verbose ? 'verbose' : 'standard'} output...`);
    
    // Determine which suites to run
    const suitesToRun = this.getSuitesToRun();
    
    // Initialize results
    const results = {
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      suites: [],
      failedTests: []
    };
    
    // Run each test suite
    for (const suiteName of suitesToRun) {
      try {
        console.log(`\nRunning test suite: ${suiteName}`);
        
        // Get suite instance
        const suite = this.availableSuites[suiteName]();
        
        // Run tests
        const suiteResults = await suite.runTests();
        
        // Aggregate results
        results.total += suiteResults.total;
        results.passed += suiteResults.passed;
        results.failed += suiteResults.failed;
        results.skipped += suiteResults.skipped;
        
        // Add suite results
        results.suites.push({
          name: suiteName,
          ...suiteResults
        });
        
        // Add failed tests
        if (suiteResults.failedTests && suiteResults.failedTests.length > 0) {
          for (const test of suiteResults.failedTests) {
            results.failedTests.push({
              suite: suiteName,
              ...test
            });
          }
        }
        
        // Stop if failFast is enabled and tests failed
        if (this.config.failFast && suiteResults.failed > 0) {
          console.log('Stopping validation due to test failures (failFast enabled)');
          break;
        }
      } catch (error) {
        console.error(`Error running test suite ${suiteName}:`, error);
        results.failed++;
        results.failedTests.push({
          suite: suiteName,
          name: 'suite_execution',
          error: error.message
        });
        
        // Stop if failFast is enabled
        if (this.config.failFast) {
          console.log('Stopping validation due to suite execution error (failFast enabled)');
          break;
        }
      }
    }
    
    // Save report if configured
    if (this.config.reportPath) {
      await this.saveReport(results);
    }
    
    return results;
  }
  
  /**
   * Get list of suites to run
   * @returns {Array<string>} - Suite names to run
   */
  getSuitesToRun() {
    if (this.config.suites === 'all') {
      return Object.keys(this.availableSuites);
    } else if (Array.isArray(this.config.suites)) {
      return this.config.suites.filter(suite => this.availableSuites[suite]);
    } else if (typeof this.config.suites === 'string') {
      return [this.config.suites].filter(suite => this.availableSuites[suite]);
    }
    
    return [];
  }
  
  /**
   * Save validation report
   * @param {Object} results - Validation results
   */
  async saveReport(results) {
    try {
      // Ensure directory exists
      const reportDir = path.dirname(this.config.reportPath);
      await fs.ensureDir(reportDir);
      
      // Add metadata
      const report = {
        timestamp: new Date().toISOString(),
        platform: this.config.platform,
        config: {
          ...this.config,
          // Remove circular references
          dataDir: this.config.dataDir
        },
        results
      };
      
      // Write report
      await fs.writeJson(this.config.reportPath, report, { spaces: 2 });
      
      console.log(`Report saved to: ${this.config.reportPath}`);
    } catch (error) {
      console.error('Failed to save report:', error);
    }
  }
}

module.exports = { ValidationExecutor };
