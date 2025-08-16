/**
 * ToolValidationFramework.js
 * 
 * Comprehensive validation framework for Aideon AI Lite tools and IDE integrations.
 * Provides automated testing, quality assurance, and validation reporting.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const EventEmitter = require('events');

class ToolValidationFramework {
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger('validation:framework');
    this.testResults = new Map();
    this.testSuites = new Map();
    this.events = new EventEmitter();
    this.runningTests = new Map();
    this.validationReportsDir = path.join(this.core.configManager.getDataDir(), 'validation_reports');
  }

  /**
   * Initialize the validation framework
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    this.logger.info('Initializing Tool Validation Framework');
    
    try {
      // Ensure validation reports directory exists
      await fs.mkdir(this.validationReportsDir, { recursive: true });
      
      // Load test suites
      await this._loadTestSuites();
      
      this.logger.info(`Tool Validation Framework initialized with ${this.testSuites.size} test suites`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Tool Validation Framework: ${error.message}`, error);
      return false;
    }
  }

  /**
   * Load test suites from the test directory
   * @private
   */
  async _loadTestSuites() {
    const testDir = path.join(__dirname, 'tests');
    
    try {
      // Ensure test directory exists
      await fs.mkdir(testDir, { recursive: true });
      
      // Get all test suite files
      const files = await fs.readdir(testDir);
      const testSuiteFiles = files.filter(file => file.endsWith('TestSuite.js'));
      
      for (const file of testSuiteFiles) {
        try {
          const TestSuiteClass = require(path.join(testDir, file));
          const testSuite = new TestSuiteClass(this.core);
          const suiteId = testSuite.getId();
          
          this.testSuites.set(suiteId, testSuite);
          this.logger.info(`Loaded test suite: ${suiteId}`);
        } catch (error) {
          this.logger.error(`Failed to load test suite from ${file}: ${error.message}`);
        }
      }
      
      this.logger.info(`Loaded ${this.testSuites.size} test suites`);
    } catch (error) {
      this.logger.error(`Error loading test suites: ${error.message}`);
      throw error;
    }
  }

  /**
   * Run validation for a specific tool or all tools
   * @param {string} [toolId] - Tool ID to validate, or undefined for all tools
   * @param {Object} [options] - Validation options
   * @returns {Promise<Object>} Validation results
   */
  async validateTool(toolId, options = {}) {
    if (toolId) {
      this.logger.info(`Starting validation for tool: ${toolId}`);
    } else {
      this.logger.info('Starting validation for all tools');
    }
    
    const validationId = uuidv4();
    const startTime = Date.now();
    
    try {
      // Get all tools to validate
      const toolManager = this.core.toolManager;
      const tools = toolId ? 
        [await toolManager.getTool(toolId)] : 
        await toolManager.getAllTools();
      
      if (tools.length === 0) {
        throw new Error(toolId ? `Tool not found: ${toolId}` : 'No tools found');
      }
      
      // Run validation for each tool
      const results = [];
      
      for (const tool of tools) {
        if (!tool) continue;
        
        const toolResult = await this._validateSingleTool(tool, options);
        results.push(toolResult);
      }
      
      // Aggregate results
      const endTime = Date.now();
      const totalTests = results.reduce((sum, r) => sum + r.totalTests, 0);
      const passedTests = results.reduce((sum, r) => sum + r.passedTests, 0);
      const failedTests = results.reduce((sum, r) => sum + r.failedTests, 0);
      const skippedTests = results.reduce((sum, r) => sum + r.skippedTests, 0);
      
      const validationResult = {
        validationId,
        startTime,
        endTime,
        duration: endTime - startTime,
        totalTools: results.length,
        totalTests,
        passedTests,
        failedTests,
        skippedTests,
        success: failedTests === 0,
        toolResults: results
      };
      
      // Save validation report
      await this._saveValidationReport(validationResult);
      
      this.logger.info(`Validation completed: ${passedTests}/${totalTests} tests passed`);
      
      return validationResult;
    } catch (error) {
      this.logger.error(`Validation failed: ${error.message}`, error);
      
      const validationResult = {
        validationId,
        startTime,
        endTime: Date.now(),
        duration: Date.now() - startTime,
        error: error.message,
        success: false
      };
      
      // Save validation report
      await this._saveValidationReport(validationResult);
      
      return validationResult;
    }
  }

  /**
   * Validate a single tool
   * @param {Object} tool - Tool to validate
   * @param {Object} options - Validation options
   * @returns {Promise<Object>} Validation result
   * @private
   */
  async _validateSingleTool(tool, options) {
    const toolId = tool.id;
    this.logger.debug(`Validating tool: ${toolId}`);
    
    const startTime = Date.now();
    const testResults = [];
    
    try {
      // Find test suites for this tool
      const applicableTestSuites = Array.from(this.testSuites.values())
        .filter(suite => suite.isApplicableForTool(tool));
      
      if (applicableTestSuites.length === 0) {
        this.logger.warn(`No test suites found for tool: ${toolId}`);
        
        return {
          toolId,
          startTime,
          endTime: Date.now(),
          duration: Date.now() - startTime,
          totalTests: 0,
          passedTests: 0,
          failedTests: 0,
          skippedTests: 0,
          success: true,
          testResults: []
        };
      }
      
      // Run each test suite
      for (const testSuite of applicableTestSuites) {
        const suiteResults = await testSuite.runTests(tool, options);
        testResults.push(...suiteResults);
      }
      
      // Aggregate results
      const endTime = Date.now();
      const passedTests = testResults.filter(r => r.status === 'passed').length;
      const failedTests = testResults.filter(r => r.status === 'failed').length;
      const skippedTests = testResults.filter(r => r.status === 'skipped').length;
      
      const toolResult = {
        toolId,
        startTime,
        endTime,
        duration: endTime - startTime,
        totalTests: testResults.length,
        passedTests,
        failedTests,
        skippedTests,
        success: failedTests === 0,
        testResults
      };
      
      this.logger.debug(`Tool validation completed: ${toolId}, ${passedTests}/${testResults.length} tests passed`);
      
      return toolResult;
    } catch (error) {
      this.logger.error(`Tool validation failed: ${toolId}, ${error.message}`, error);
      
      return {
        toolId,
        startTime,
        endTime: Date.now(),
        duration: Date.now() - startTime,
        error: error.message,
        totalTests: testResults.length,
        passedTests: testResults.filter(r => r.status === 'passed').length,
        failedTests: testResults.filter(r => r.status === 'failed').length + 1, // Count the error as a failure
        skippedTests: testResults.filter(r => r.status === 'skipped').length,
        success: false,
        testResults
      };
    }
  }

  /**
   * Run validation for a specific IDE integration or all IDE integrations
   * @param {string} [ideId] - IDE ID to validate, or undefined for all IDE integrations
   * @param {Object} [options] - Validation options
   * @returns {Promise<Object>} Validation results
   */
  async validateIDEIntegration(ideId, options = {}) {
    if (ideId) {
      this.logger.info(`Starting validation for IDE integration: ${ideId}`);
    } else {
      this.logger.info('Starting validation for all IDE integrations');
    }
    
    const validationId = uuidv4();
    const startTime = Date.now();
    
    try {
      // Get all IDE integrations to validate
      const ideManager = this.core.ideIntegrationManager;
      const integrations = ideId ? 
        [ideManager.getIntegration(ideId)] : 
        ideManager.getAllIntegrations();
      
      if (integrations.length === 0) {
        throw new Error(ideId ? `IDE integration not found: ${ideId}` : 'No IDE integrations found');
      }
      
      // Run validation for each IDE integration
      const results = [];
      
      for (const integration of integrations) {
        if (!integration) continue;
        
        const integrationResult = await this._validateSingleIDEIntegration(integration, options);
        results.push(integrationResult);
      }
      
      // Aggregate results
      const endTime = Date.now();
      const totalTests = results.reduce((sum, r) => sum + r.totalTests, 0);
      const passedTests = results.reduce((sum, r) => sum + r.passedTests, 0);
      const failedTests = results.reduce((sum, r) => sum + r.failedTests, 0);
      const skippedTests = results.reduce((sum, r) => sum + r.skippedTests, 0);
      
      const validationResult = {
        validationId,
        startTime,
        endTime,
        duration: endTime - startTime,
        totalIntegrations: results.length,
        totalTests,
        passedTests,
        failedTests,
        skippedTests,
        success: failedTests === 0,
        integrationResults: results
      };
      
      // Save validation report
      await this._saveValidationReport(validationResult, 'ide');
      
      this.logger.info(`IDE integration validation completed: ${passedTests}/${totalTests} tests passed`);
      
      return validationResult;
    } catch (error) {
      this.logger.error(`IDE integration validation failed: ${error.message}`, error);
      
      const validationResult = {
        validationId,
        startTime,
        endTime: Date.now(),
        duration: Date.now() - startTime,
        error: error.message,
        success: false
      };
      
      // Save validation report
      await this._saveValidationReport(validationResult, 'ide');
      
      return validationResult;
    }
  }

  /**
   * Validate a single IDE integration
   * @param {Object} integration - IDE integration to validate
   * @param {Object} options - Validation options
   * @returns {Promise<Object>} Validation result
   * @private
   */
  async _validateSingleIDEIntegration(integration, options) {
    const ideId = integration.getIDEName().toLowerCase();
    this.logger.debug(`Validating IDE integration: ${ideId}`);
    
    const startTime = Date.now();
    const testResults = [];
    
    try {
      // Find test suites for this IDE integration
      const applicableTestSuites = Array.from(this.testSuites.values())
        .filter(suite => suite.isApplicableForIDEIntegration(integration));
      
      if (applicableTestSuites.length === 0) {
        this.logger.warn(`No test suites found for IDE integration: ${ideId}`);
        
        return {
          ideId,
          startTime,
          endTime: Date.now(),
          duration: Date.now() - startTime,
          totalTests: 0,
          passedTests: 0,
          failedTests: 0,
          skippedTests: 0,
          success: true,
          testResults: []
        };
      }
      
      // Run each test suite
      for (const testSuite of applicableTestSuites) {
        const suiteResults = await testSuite.runIDETests(integration, options);
        testResults.push(...suiteResults);
      }
      
      // Aggregate results
      const endTime = Date.now();
      const passedTests = testResults.filter(r => r.status === 'passed').length;
      const failedTests = testResults.filter(r => r.status === 'failed').length;
      const skippedTests = testResults.filter(r => r.status === 'skipped').length;
      
      const integrationResult = {
        ideId,
        startTime,
        endTime,
        duration: endTime - startTime,
        totalTests: testResults.length,
        passedTests,
        failedTests,
        skippedTests,
        success: failedTests === 0,
        testResults
      };
      
      this.logger.debug(`IDE integration validation completed: ${ideId}, ${passedTests}/${testResults.length} tests passed`);
      
      return integrationResult;
    } catch (error) {
      this.logger.error(`IDE integration validation failed: ${ideId}, ${error.message}`, error);
      
      return {
        ideId,
        startTime,
        endTime: Date.now(),
        duration: Date.now() - startTime,
        error: error.message,
        totalTests: testResults.length,
        passedTests: testResults.filter(r => r.status === 'passed').length,
        failedTests: testResults.filter(r => r.status === 'failed').length + 1, // Count the error as a failure
        skippedTests: testResults.filter(r => r.status === 'skipped').length,
        success: false,
        testResults
      };
    }
  }

  /**
   * Save validation report to file
   * @param {Object} report - Validation report
   * @param {string} [type='tool'] - Report type ('tool' or 'ide')
   * @returns {Promise<string>} Report file path
   * @private
   */
  async _saveValidationReport(report, type = 'tool') {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `${type}_validation_${timestamp}.json`;
    const filePath = path.join(this.validationReportsDir, fileName);
    
    await fs.writeFile(filePath, JSON.stringify(report, null, 2));
    
    this.logger.debug(`Validation report saved: ${filePath}`);
    
    return filePath;
  }

  /**
   * Get all validation reports
   * @param {string} [type] - Report type filter ('tool' or 'ide')
   * @returns {Promise<Array<Object>>} Validation reports
   */
  async getValidationReports(type) {
    try {
      const files = await fs.readdir(this.validationReportsDir);
      
      // Filter by type if specified
      const reportFiles = type ? 
        files.filter(file => file.startsWith(`${type}_validation_`)) : 
        files.filter(file => file.endsWith('.json'));
      
      // Load each report
      const reports = [];
      
      for (const file of reportFiles) {
        try {
          const filePath = path.join(this.validationReportsDir, file);
          const content = await fs.readFile(filePath, 'utf8');
          const report = JSON.parse(content);
          
          reports.push({
            ...report,
            fileName: file,
            filePath
          });
        } catch (error) {
          this.logger.error(`Failed to load validation report ${file}: ${error.message}`);
        }
      }
      
      // Sort by timestamp (newest first)
      reports.sort((a, b) => b.startTime - a.startTime);
      
      return reports;
    } catch (error) {
      this.logger.error(`Failed to get validation reports: ${error.message}`);
      return [];
    }
  }

  /**
   * Get the latest validation report
   * @param {string} [type] - Report type filter ('tool' or 'ide')
   * @returns {Promise<Object|null>} Latest validation report or null if none found
   */
  async getLatestValidationReport(type) {
    const reports = await this.getValidationReports(type);
    return reports.length > 0 ? reports[0] : null;
  }

  /**
   * Register a test event listener
   * @param {string} event - Event name
   * @param {Function} listener - Event listener
   */
  on(event, listener) {
    this.events.on(event, listener);
  }

  /**
   * Remove a test event listener
   * @param {string} event - Event name
   * @param {Function} listener - Event listener
   */
  off(event, listener) {
    this.events.off(event, listener);
  }

  /**
   * Generate a validation summary report
   * @param {Object} validationResult - Validation result
   * @returns {Promise<string>} Report file path
   */
  async generateValidationSummaryReport(validationResult) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `validation_summary_${timestamp}.md`;
    const filePath = path.join(this.validationReportsDir, fileName);
    
    let report = `# Aideon AI Lite Validation Summary\n\n`;
    report += `**Date:** ${new Date(validationResult.startTime).toLocaleString()}\n`;
    report += `**Duration:** ${(validationResult.duration / 1000).toFixed(2)} seconds\n`;
    report += `**Status:** ${validationResult.success ? '✅ PASSED' : '❌ FAILED'}\n\n`;
    
    if (validationResult.error) {
      report += `## Error\n\n\`\`\`\n${validationResult.error}\n\`\`\`\n\n`;
    }
    
    if (validationResult.toolResults) {
      report += `## Tool Validation Results\n\n`;
      report += `| Tool ID | Status | Tests | Passed | Failed | Skipped |\n`;
      report += `|---------|--------|-------|--------|--------|--------|\n`;
      
      for (const toolResult of validationResult.toolResults) {
        const status = toolResult.success ? '✅' : '❌';
        report += `| ${toolResult.toolId} | ${status} | ${toolResult.totalTests} | ${toolResult.passedTests} | ${toolResult.failedTests} | ${toolResult.skippedTests} |\n`;
      }
      
      report += `\n`;
      
      // Add failed test details
      const failedTests = validationResult.toolResults
        .flatMap(tr => tr.testResults.filter(r => r.status === 'failed')
        .map(r => ({ ...r, toolId: tr.toolId })));
      
      if (failedTests.length > 0) {
        report += `## Failed Tests\n\n`;
        
        for (const test of failedTests) {
          report += `### ${test.toolId}: ${test.name}\n\n`;
          report += `**Error:** ${test.error}\n\n`;
          
          if (test.expected && test.actual) {
            report += `**Expected:**\n\`\`\`json\n${JSON.stringify(test.expected, null, 2)}\n\`\`\`\n\n`;
            report += `**Actual:**\n\`\`\`json\n${JSON.stringify(test.actual, null, 2)}\n\`\`\`\n\n`;
          }
        }
      }
    }
    
    if (validationResult.integrationResults) {
      report += `## IDE Integration Validation Results\n\n`;
      report += `| IDE | Status | Tests | Passed | Failed | Skipped |\n`;
      report += `|-----|--------|-------|--------|--------|--------|\n`;
      
      for (const integrationResult of validationResult.integrationResults) {
        const status = integrationResult.success ? '✅' : '❌';
        report += `| ${integrationResult.ideId} | ${status} | ${integrationResult.totalTests} | ${integrationResult.passedTests} | ${integrationResult.failedTests} | ${integrationResult.skippedTests} |\n`;
      }
      
      report += `\n`;
      
      // Add failed test details
      const failedTests = validationResult.integrationResults
        .flatMap(ir => ir.testResults.filter(r => r.status === 'failed')
        .map(r => ({ ...r, ideId: ir.ideId })));
      
      if (failedTests.length > 0) {
        report += `## Failed IDE Integration Tests\n\n`;
        
        for (const test of failedTests) {
          report += `### ${test.ideId}: ${test.name}\n\n`;
          report += `**Error:** ${test.error}\n\n`;
          
          if (test.expected && test.actual) {
            report += `**Expected:**\n\`\`\`json\n${JSON.stringify(test.expected, null, 2)}\n\`\`\`\n\n`;
            report += `**Actual:**\n\`\`\`json\n${JSON.stringify(test.actual, null, 2)}\n\`\`\`\n\n`;
          }
        }
      }
    }
    
    await fs.writeFile(filePath, report);
    
    this.logger.info(`Validation summary report saved: ${filePath}`);
    
    return filePath;
  }
}

module.exports = ToolValidationFramework;
