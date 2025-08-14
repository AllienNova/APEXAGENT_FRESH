/**
 * MLModel.js
 * Base class for ML models in Aideon AI Lite
 * Provides common functionality for all ML model types
 */

class MLModel {
  /**
   * Create a new ML model
   * @param {Object} provider - Provider instance
   * @param {Object} options - Model options
   * @param {string} options.id - Unique model identifier
   * @param {string} options.name - Human-readable model name
   * @param {string} options.type - Model type (vision, audio, embedding, classification, forecasting)
   * @param {string} options.version - Model version
   * @param {boolean} options.isLocal - Whether the model runs locally
   * @param {Object} options.capabilities - Model capabilities
   * @param {Object} options.requirements - Model requirements
   */
  constructor(provider, options) {
    this.provider = provider;
    this.core = provider.core;
    this.logger = provider.logger;
    
    this.id = options.id;
    this.name = options.name;
    this.type = options.type;
    this.version = options.version || '1.0.0';
    this.isLocal = options.isLocal || false;
    this.capabilities = options.capabilities || {};
    this.requirements = options.requirements || {};
    
    this.initialized = false;
    this.status = 'created';
    this.metrics = {
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      totalExecutionTime: 0,
      averageExecutionTime: 0
    };
  }
  
  /**
   * Initialize the model
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    try {
      this.logger.info(`Initializing ML model: ${this.name} (${this.id})`);
      
      // Perform model-specific initialization
      await this._initialize();
      
      this.initialized = true;
      this.status = 'ready';
      this.logger.info(`ML model initialized: ${this.name} (${this.id})`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize ML model: ${this.name} (${this.id})`, error);
      this.status = 'error';
      return false;
    }
  }
  
  /**
   * Execute the model
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Model result
   */
  async execute(params, options = {}) {
    if (!this.initialized) {
      throw new Error(`Model ${this.id} is not initialized`);
    }
    
    const startTime = Date.now();
    this.metrics.totalExecutions++;
    
    try {
      // Validate parameters
      this._validateParams(params);
      
      // Execute model-specific logic
      const result = await this._execute(params, options);
      
      // Update metrics
      const executionTime = Date.now() - startTime;
      this.metrics.successfulExecutions++;
      this.metrics.totalExecutionTime += executionTime;
      this.metrics.averageExecutionTime = this.metrics.totalExecutionTime / this.metrics.successfulExecutions;
      
      return result;
    } catch (error) {
      this.metrics.failedExecutions++;
      throw error;
    }
  }
  
  /**
   * Get model information
   * @returns {Object} Model information
   */
  getInfo() {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      version: this.version,
      isLocal: this.isLocal,
      status: this.status,
      capabilities: this.capabilities,
      requirements: this.requirements,
      metrics: {
        totalExecutions: this.metrics.totalExecutions,
        successfulExecutions: this.metrics.successfulExecutions,
        failedExecutions: this.metrics.failedExecutions,
        averageExecutionTime: this.metrics.averageExecutionTime
      }
    };
  }
  
  /**
   * Check if the model meets the specified requirements
   * @param {Object} requirements - Requirements to check
   * @returns {boolean} Whether the model meets the requirements
   */
  meetsRequirements(requirements) {
    if (!requirements) {
      return true;
    }
    
    // Check each requirement
    for (const [key, value] of Object.entries(requirements)) {
      // Special handling for capabilities
      if (key === 'capabilities') {
        if (Array.isArray(value)) {
          // Check if model has all required capabilities
          if (!value.every(cap => this.capabilities[cap])) {
            return false;
          }
        }
        continue;
      }
      
      // Check if requirement is met
      if (this.requirements[key] !== undefined && this.requirements[key] !== value) {
        return false;
      }
    }
    
    return true;
  }
  
  /**
   * Model-specific initialization logic
   * @returns {Promise<void>}
   * @protected
   */
  async _initialize() {
    // To be implemented by subclasses
    throw new Error('_initialize must be implemented by subclass');
  }
  
  /**
   * Model-specific execution logic
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Model result
   * @protected
   */
  async _execute(params, options) {
    // To be implemented by subclasses
    throw new Error('_execute must be implemented by subclass');
  }
  
  /**
   * Validate model parameters
   * @param {Object} params - Model parameters
   * @protected
   */
  _validateParams(params) {
    // Default implementation, can be extended by subclasses
    if (!params) {
      throw new Error('Model parameters are required');
    }
  }
}

module.exports = MLModel;
