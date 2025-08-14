/**
 * MLModelProvider.js
 * Base class for ML model providers in Aideon AI Lite
 * Extends the existing provider framework to support ML models
 */

const { Provider } = require('../core/providers/Provider');
const CircuitBreaker = require('../core/models/providers/utils/CustomCircuitBreaker');

class MLModelProvider extends Provider {
  /**
   * Create a new ML model provider
   * @param {Object} core - Core system reference
   */
  constructor(core) {
    super(core);
    
    this.models = [];
    this.config = core.configManager.getConfig().mlProviders?.[this.id] || {};
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 3,
      resetTimeout: 30000,
      maxRetries: 2,
      retryDelay: 1000,
      timeout: 10000,
      errorHandler: this._handleError.bind(this)
    });
    
    // Model type registries
    this.visionModels = [];
    this.audioModels = [];
    this.embeddingModels = [];
    this.classificationModels = [];
    this.forecastingModels = [];
  }
  
  /**
   * Initialize the provider
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    try {
      this.logger.info(`Initializing ML provider: ${this.name}`);
      
      // Validate configuration
      if (!this._validateConfig()) {
        this.logger.error(`Invalid configuration for ML provider: ${this.name}`);
        return false;
      }
      
      // Register models
      await this._registerModels();
      
      // Initialize models
      for (const model of this.models) {
        await model.initialize();
      }
      
      this.logger.info(`ML provider initialized: ${this.name}`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize ML provider: ${this.name}`, error);
      return false;
    }
  }
  
  /**
   * Get a model by ID
   * @param {string} modelId - Model ID
   * @returns {Object|null} Model object or null if not found
   */
  getModel(modelId) {
    return this.models.find(model => model.id === modelId) || null;
  }
  
  /**
   * Get models by type
   * @param {string} type - Model type (vision, audio, embedding, classification, forecasting)
   * @returns {Array} Array of models of the specified type
   */
  getModelsByType(type) {
    switch (type) {
      case 'vision':
        return this.visionModels;
      case 'audio':
        return this.audioModels;
      case 'embedding':
        return this.embeddingModels;
      case 'classification':
        return this.classificationModels;
      case 'forecasting':
        return this.forecastingModels;
      default:
        return [];
    }
  }
  
  /**
   * Execute a model with circuit breaker protection
   * @param {string} modelId - Model ID
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Model result
   */
  async executeModel(modelId, params, options = {}) {
    const model = this.getModel(modelId);
    
    if (!model) {
      throw new Error(`Model not found: ${modelId}`);
    }
    
    return this.circuitBreaker.execute(async () => {
      const startTime = Date.now();
      
      try {
        // Pre-execution hooks
        await this._preExecute(model, params, options);
        
        // Execute model
        const result = await model.execute(params, options);
        
        // Post-execution hooks
        await this._postExecute(model, params, options, result);
        
        // Track metrics
        this._trackMetrics(model, params, options, result, Date.now() - startTime);
        
        return result;
      } catch (error) {
        this.logger.error(`Error executing model ${modelId}:`, error);
        throw error;
      }
    });
  }
  
  /**
   * Validate provider configuration
   * @returns {boolean} Validation result
   * @protected
   */
  _validateConfig() {
    // Base validation, to be extended by subclasses
    return true;
  }
  
  /**
   * Register models provided by this provider
   * @returns {Promise<void>}
   * @protected
   */
  async _registerModels() {
    // To be implemented by subclasses
    throw new Error('_registerModels must be implemented by subclass');
  }
  
  /**
   * Pre-execution hook
   * @param {Object} model - Model object
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @returns {Promise<void>}
   * @protected
   */
  async _preExecute(model, params, options) {
    // Default implementation, can be extended by subclasses
  }
  
  /**
   * Post-execution hook
   * @param {Object} model - Model object
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @param {Object} result - Model result
   * @returns {Promise<void>}
   * @protected
   */
  async _postExecute(model, params, options, result) {
    // Default implementation, can be extended by subclasses
  }
  
  /**
   * Track metrics for model execution
   * @param {Object} model - Model object
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @param {Object} result - Model result
   * @param {number} duration - Execution duration in milliseconds
   * @protected
   */
  _trackMetrics(model, params, options, result, duration) {
    // Track execution metrics
    this.core.metricsManager?.trackModelExecution({
      providerId: this.id,
      modelId: model.id,
      modelType: model.type,
      duration,
      success: true,
      inputSize: this._estimateInputSize(params),
      outputSize: this._estimateOutputSize(result),
      timestamp: Date.now()
    });
  }
  
  /**
   * Handle errors from circuit breaker
   * @param {Error} error - Error object
   * @param {Object} context - Error context
   * @protected
   */
  _handleError(error, context) {
    this.logger.error(`Circuit breaker error in ${this.name}:`, error);
    
    // Track error metrics
    this.core.metricsManager?.trackModelError({
      providerId: this.id,
      modelId: context?.modelId,
      errorType: error.name,
      errorMessage: error.message,
      timestamp: Date.now()
    });
    
    // Rethrow the error
    throw error;
  }
  
  /**
   * Estimate the size of input parameters
   * @param {Object} params - Input parameters
   * @returns {number} Estimated size in bytes
   * @protected
   */
  _estimateInputSize(params) {
    try {
      return JSON.stringify(params).length;
    } catch (error) {
      return 0;
    }
  }
  
  /**
   * Estimate the size of output result
   * @param {Object} result - Output result
   * @returns {number} Estimated size in bytes
   * @protected
   */
  _estimateOutputSize(result) {
    try {
      return JSON.stringify(result).length;
    } catch (error) {
      return 0;
    }
  }
}

module.exports = MLModelProvider;
