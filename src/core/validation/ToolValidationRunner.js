/**
 * ToolValidationRunner.js
 * 
 * Runner script for validating all tools and IDE integrations in Aideon AI Lite.
 * Executes the validation framework and generates comprehensive reports.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const path = require('path');
const fs = require('fs').promises;
const AideonCore = require('../core/AideonCore');
const ToolValidationFramework = require('./ToolValidationFramework');

/**
 * Main validation runner function
 */
async function runValidation() {
  console.log('Starting Aideon AI Lite tool and IDE validation...');
  
  try {
    // Initialize Aideon Core
    const core = new AideonCore();
    await core.initialize();
    
    console.log('Aideon Core initialized successfully');
    
    // Initialize validation framework
    const validationFramework = new ToolValidationFramework(core);
    await validationFramework.initialize();
    
    console.log('Validation framework initialized successfully');
    
    // Create validation results directory
    const resultsDir = path.join(__dirname, 'validation_results');
    await fs.mkdir(resultsDir, { recursive: true });
    
    // Run tool validation
    console.log('Running tool validation...');
    const toolValidationResult = await validationFramework.validateTool();
    
    console.log(`Tool validation completed: ${toolValidationResult.passedTests}/${toolValidationResult.totalTests} tests passed`);
    
    // Run IDE integration validation
    console.log('Running IDE integration validation...');
    const ideValidationResult = await validationFramework.validateIDEIntegration();
    
    console.log(`IDE integration validation completed: ${ideValidationResult.passedTests}/${ideValidationResult.totalTests} tests passed`);
    
    // Generate summary reports
    console.log('Generating validation summary reports...');
    
    const toolSummaryPath = await validationFramework.generateValidationSummaryReport(toolValidationResult);
    const ideSummaryPath = await validationFramework.generateValidationSummaryReport(ideValidationResult);
    
    console.log(`Tool validation summary report saved to: ${toolSummaryPath}`);
    console.log(`IDE integration validation summary report saved to: ${ideSummaryPath}`);
    
    // Generate combined report
    const combinedResult = {
      validationId: `combined_${Date.now()}`,
      startTime: Math.min(toolValidationResult.startTime, ideValidationResult.startTime),
      endTime: Math.max(toolValidationResult.endTime, ideValidationResult.endTime),
      duration: toolValidationResult.duration + ideValidationResult.duration,
      totalTools: toolValidationResult.totalTools,
      totalIntegrations: ideValidationResult.totalIntegrations,
      totalTests: toolValidationResult.totalTests + ideValidationResult.totalTests,
      passedTests: toolValidationResult.passedTests + ideValidationResult.passedTests,
      failedTests: toolValidationResult.failedTests + ideValidationResult.failedTests,
      skippedTests: toolValidationResult.skippedTests + ideValidationResult.skippedTests,
      success: toolValidationResult.success && ideValidationResult.success,
      toolResults: toolValidationResult.toolResults,
      integrationResults: ideValidationResult.integrationResults
    };
    
    const combinedSummaryPath = await validationFramework.generateValidationSummaryReport(combinedResult);
    
    console.log(`Combined validation summary report saved to: ${combinedSummaryPath}`);
    
    // Check for failures
    if (!combinedResult.success) {
      console.error(`Validation failed: ${combinedResult.failedTests} tests failed`);
      process.exit(1);
    }
    
    console.log('All validations completed successfully!');
    process.exit(0);
  } catch (error) {
    console.error(`Validation failed with error: ${error.message}`);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run validation if this script is executed directly
if (require.main === module) {
  runValidation().catch(error => {
    console.error(`Unhandled error: ${error.message}`);
    console.error(error.stack);
    process.exit(1);
  });
}

module.exports = { runValidation };
