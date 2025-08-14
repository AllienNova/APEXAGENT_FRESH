/**
 * BaseTestSuite.js
 * 
 * Abstract base class for all test suites in Aideon AI Lite
 * Provides common functionality for test registration, execution, and reporting
 */

class BaseTestSuite {
  /**
   * Constructor
   * @param {string} name - Name of the test suite
   * @param {Object} config - Configuration options
   */
  constructor(name, config = {}) {
    this.name = name;
    this.config = config;
    this.tests = new Map();
    this.results = {
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      failedTests: []
    };
    this.logs = [];
  }
  
  /**
   * Register a test
   * @param {string} name - Test name
   * @param {Function} testFn - Test function
   */
  registerTest(name, testFn) {
    this.tests.set(name, testFn);
  }
  
  /**
   * Execute all registered tests
   * @returns {Promise<Object>} - Test results
   */
  async executeTests() {
    this.results.total = this.tests.size;
    
    for (const [name, testFn] of this.tests.entries()) {
      try {
        if (this.config.verbose) {
          console.log(`  Running test: ${name}`);
        }
        
        await testFn();
        
        if (this.config.verbose) {
          console.log(`  ✓ Passed: ${name}`);
        }
        
        this.results.passed++;
      } catch (error) {
        if (error.message === 'SKIP') {
          if (this.config.verbose) {
            console.log(`  ⚠ Skipped: ${name}`);
          }
          
          this.results.skipped++;
        } else {
          console.error(`  ✗ Failed: ${name}`);
          console.error(`    Error: ${error.message}`);
          
          this.results.failed++;
          this.results.failedTests.push({
            name,
            error: error.message
          });
          
          if (this.config.failFast) {
            break;
          }
        }
      }
    }
    
    this.logSummary();
    return this.results;
  }
  
  /**
   * Log test summary
   */
  logSummary() {
    console.log(`\nSummary for ${this.name}:`);
    console.log(`  Total: ${this.results.total}`);
    console.log(`  Passed: ${this.results.passed}`);
    console.log(`  Failed: ${this.results.failed}`);
    console.log(`  Skipped: ${this.results.skipped}`);
  }
  
  /**
   * Assert that a condition is true
   * @param {boolean} condition - Condition to assert
   * @param {string} message - Assertion message
   */
  assert(condition, message) {
    if (!condition) {
      throw new Error(message || 'Assertion failed');
    }
  }
  
  /**
   * Assert that two values are equal
   * @param {*} actual - Actual value
   * @param {*} expected - Expected value
   * @param {string} message - Assertion message
   */
  assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(message || `Expected ${expected}, got ${actual}`);
    }
  }
  
  /**
   * Assert that two values are not equal
   * @param {*} actual - Actual value
   * @param {*} expected - Expected value
   * @param {string} message - Assertion message
   */
  assertNotEqual(actual, expected, message) {
    if (actual === expected) {
      throw new Error(message || `Expected ${actual} to be different from ${expected}`);
    }
  }
  
  /**
   * Assert that a value contains another value
   * @param {*} haystack - Container value
   * @param {*} needle - Value to find
   * @param {string} message - Assertion message
   */
  assertContains(haystack, needle, message) {
    if (Array.isArray(haystack)) {
      if (!haystack.includes(needle)) {
        throw new Error(message || `Expected ${JSON.stringify(haystack)} to contain ${needle}`);
      }
    } else if (typeof haystack === 'string') {
      if (!haystack.includes(needle)) {
        throw new Error(message || `Expected "${haystack}" to contain "${needle}"`);
      }
    } else if (typeof haystack === 'object' && haystack !== null) {
      if (!Object.values(haystack).includes(needle) && !Object.keys(haystack).includes(needle)) {
        throw new Error(message || `Expected ${JSON.stringify(haystack)} to contain ${needle}`);
      }
    } else {
      throw new Error(message || `Cannot check if ${typeof haystack} contains ${needle}`);
    }
  }
  
  /**
   * Assert that a function throws an exception
   * @param {Function} fn - Function to execute
   * @param {string} message - Assertion message
   */
  assertThrows(fn, message) {
    try {
      fn();
      throw new Error(message || 'Expected function to throw an exception');
    } catch (error) {
      if (error.message === message) {
        throw error;
      }
    }
  }
  
  /**
   * Mark a test as passed
   * @param {string} message - Success message
   */
  pass(message) {
    if (this.config.verbose && message) {
      console.log(`    ${message}`);
    }
  }
  
  /**
   * Mark a test as failed
   * @param {string} message - Failure message
   */
  fail(message) {
    throw new Error(message || 'Test failed');
  }
  
  /**
   * Mark a test as skipped
   * @param {string} message - Skip reason
   */
  skip(message) {
    if (this.config.verbose && message) {
      console.log(`    Skipped: ${message}`);
    }
    throw new Error('SKIP');
  }
  
  /**
   * Log a debug message
   * @param {string} message - Debug message
   */
  debug(message) {
    if (this.config.verbose) {
      console.log(`    Debug: ${message}`);
    }
    this.logs.push({
      type: 'debug',
      message,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Log a message
   * @param {string} message - Log message
   */
  log(message) {
    if (this.config.verbose) {
      console.log(`    ${message}`);
    }
    this.logs.push({
      type: 'info',
      message,
      timestamp: new Date().toISOString()
    });
  }
}

module.exports = { BaseTestSuite };
