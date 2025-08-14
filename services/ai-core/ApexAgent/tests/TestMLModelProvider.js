/**
 * TestMLModelProvider.js
 * Test implementation of MLModelProvider for validation tests
 */

const MLModelProvider = require('../src/ml/MLModelProvider');

class TestMLModelProvider extends MLModelProvider {
  /**
   * Get provider ID
   * @returns {string} Provider ID
   */
  get id() {
    return 'test-ml-provider';
  }
  
  /**
   * Get provider name
   * @returns {string} Provider name
   */
  get name() {
    return 'Test ML Provider';
  }
  
  /**
   * Register models provided by this provider
   * @returns {Promise<void>}
   * @protected
   */
  async _registerModels() {
    // Test implementation - no models to register
    return Promise.resolve();
  }
}

module.exports = TestMLModelProvider;
