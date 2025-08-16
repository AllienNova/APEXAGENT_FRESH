/**
 * Model Integration Framework for Aideon AI Lite
 * 
 * This framework provides a unified interface for integrating and managing
 * multiple LLM models across different modalities (text, code, image, video, audio).
 * It supports hybrid processing (local + cloud), dynamic model selection,
 * fallback chains, and seamless integration with the multi-agent system.
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');

/**
 * Main Model Integration Framework class
 */
class ModelIntegrationFramework extends EventEmitter {
  /**
   * Initialize the Model Integration Framework
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    super();
    
    this.core = core;
    this.logger = core.logManager.getLogger('model-integration');
    this.config = core.configManager.getConfig().models || {};
    
    // Model registries for each modality
    this.textModels = new Map();
    this.codeModels = new Map();
    this.imageModels = new Map();
    this.videoModels = new Map();
    this.audioModels = new Map();
    
    // Provider registries
    this.providers = new Map();
    
    // Cache for model responses
    this.responseCache = new Map();
    
    // Performance metrics
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageLatency: 0,
      requestsByModality: {
        text: 0,
        code: 0,
        image: 0,
        video: 0,
        audio: 0
      }
    };
    
    this.initialized = false;
    
    this.logger.info('Model Integration Framework initialized');
  }
  
  /**
   * Initialize the framework
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    try {
      this.logger.info('Initializing Model Integration Framework...');
      
      // Register built-in model providers
      await this._registerBuiltInProviders();
      
      // Register custom model providers
      await this._registerCustomProviders();
      
      // Initialize all providers
      await this._initializeProviders();
      
      // Register models from all providers
      await this._registerModels();
      
      this.initialized = true;
      this.logger.info('Model Integration Framework initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize Model Integration Framework:', error);
      throw error;
    }
  }
  
  /**
   * Register built-in model providers
   * @returns {Promise<void>}
   * @private
   */
  async _registerBuiltInProviders() {
    // Text model providers
    this.registerProvider(new OpenAIProvider(this.core));
    this.registerProvider(new AnthropicProvider(this.core));
    this.registerProvider(new GoogleProvider(this.core));
    this.registerProvider(new MetaProvider(this.core));
    this.registerProvider(new MistralProvider(this.core));
    this.registerProvider(new DeepSeekProvider(this.core));
    
    // Image model providers
    this.registerProvider(new StabilityAIProvider(this.core));
    this.registerProvider(new MidjourneyProvider(this.core));
    this.registerProvider(new DalleProvider(this.core));
    
    // Video model providers
    this.registerProvider(new RunwayProvider(this.core));
    this.registerProvider(new PikaLabsProvider(this.core));
    this.registerProvider(new SkyworkAIProvider(this.core));
    
    // Audio model providers
    this.registerProvider(new SunoProvider(this.core));
    this.registerProvider(new UdioProvider(this.core));
    this.registerProvider(new AudioCraftProvider(this.core));
    
    this.logger.info('Built-in model providers registered');
  }
  
  /**
   * Register custom model providers
   * @returns {Promise<void>}
   * @private
   */
  async _registerCustomProviders() {
    const customProvidersPath = path.join(process.cwd(), 'custom_providers');
    
    try {
      // Check if custom providers directory exists
      await fs.access(customProvidersPath);
      
      // Get all files in the directory
      const files = await fs.readdir(customProvidersPath);
      
      for (const file of files) {
        if (file.endsWith('.js')) {
          try {
            const providerPath = path.join(customProvidersPath, file);
            const ProviderClass = require(providerPath);
            
            // Create and register provider instance
            const provider = new ProviderClass(this.core);
            this.registerProvider(provider);
            
            this.logger.info(`Custom provider registered: ${provider.id}`);
          } catch (error) {
            this.logger.warn(`Failed to load custom provider ${file}:`, error);
          }
        }
      }
    } catch (error) {
      // Directory doesn't exist, just log and continue
      this.logger.info('No custom providers directory found');
    }
  }
  
  /**
   * Initialize all registered providers
   * @returns {Promise<void>}
   * @private
   */
  async _initializeProviders() {
    const initPromises = [];
    
    for (const provider of this.providers.values()) {
      initPromises.push(this._initializeProvider(provider));
    }
    
    await Promise.all(initPromises);
  }
  
  /**
   * Initialize a specific provider
   * @param {ModelProvider} provider - Provider to initialize
   * @returns {Promise<void>}
   * @private
   */
  async _initializeProvider(provider) {
    try {
      await provider.initialize();
      this.logger.info(`Provider ${provider.id} initialized successfully`);
    } catch (error) {
      this.logger.error(`Failed to initialize provider ${provider.id}:`, error);
      // Don't throw, just log the error and continue with other providers
    }
  }
  
  /**
   * Register models from all providers
   * @returns {Promise<void>}
   * @private
   */
  async _registerModels() {
    for (const provider of this.providers.values()) {
      const models = provider.getModels();
      
      for (const model of models) {
        this.registerModel(model);
      }
    }
  }
  
  /**
   * Register a model provider
   * @param {ModelProvider} provider - Provider to register
   * @returns {boolean} Success status
   */
  registerProvider(provider) {
    if (this.providers.has(provider.id)) {
      this.logger.warn(`Provider ${provider.id} is already registered`);
      return false;
    }
    
    this.providers.set(provider.id, provider);
    this.logger.info(`Provider ${provider.id} registered`);
    return true;
  }
  
  /**
   * Register a model
   * @param {Model} model - Model to register
   * @returns {boolean} Success status
   */
  registerModel(model) {
    // Get the appropriate registry based on modality
    let registry;
    switch (model.modality) {
      case 'text':
        registry = this.textModels;
        break;
      case 'code':
        registry = this.codeModels;
        break;
      case 'image':
        registry = this.imageModels;
        break;
      case 'video':
        registry = this.videoModels;
        break;
      case 'audio':
        registry = this.audioModels;
        break;
      default:
        this.logger.warn(`Unknown modality: ${model.modality}`);
        return false;
    }
    
    // Check if model is already registered
    if (registry.has(model.id)) {
      this.logger.warn(`Model ${model.id} is already registered`);
      return false;
    }
    
    // Register the model
    registry.set(model.id, model);
    this.logger.info(`Model ${model.id} registered for ${model.modality} modality`);
    return true;
  }
  
  /**
   * Get a model by ID and modality
   * @param {string} modelId - Model ID
   * @param {string} modality - Model modality
   * @returns {Model} Model instance
   */
  getModel(modelId, modality) {
    // Get the appropriate registry based on modality
    let registry;
    switch (modality) {
      case 'text':
        registry = this.textModels;
        break;
      case 'code':
        registry = this.codeModels;
        break;
      case 'image':
        registry = this.imageModels;
        break;
      case 'video':
        registry = this.videoModels;
        break;
      case 'audio':
        registry = this.audioModels;
        break;
      default:
        throw new Error(`Unknown modality: ${modality}`);
    }
    
    // Get the model
    const model = registry.get(modelId);
    
    if (!model) {
      throw new Error(`Model ${modelId} not found for ${modality} modality`);
    }
    
    return model;
  }
  
  /**
   * Get all models for a specific modality
   * @param {string} modality - Model modality
   * @returns {Array<Model>} Array of models
   */
  getModelsByModality(modality) {
    // Get the appropriate registry based on modality
    let registry;
    switch (modality) {
      case 'text':
        registry = this.textModels;
        break;
      case 'code':
        registry = this.codeModels;
        break;
      case 'image':
        registry = this.imageModels;
        break;
      case 'video':
        registry = this.videoModels;
        break;
      case 'audio':
        registry = this.audioModels;
        break;
      default:
        throw new Error(`Unknown modality: ${modality}`);
    }
    
    return Array.from(registry.values());
  }
  
  /**
   * Select the best model for a specific task
   * @param {string} modality - Model modality
   * @param {Object} requirements - Task requirements
   * @returns {Model} Selected model
   */
  selectModel(modality, requirements = {}) {
    const models = this.getModelsByModality(modality);
    
    if (models.length === 0) {
      throw new Error(`No models available for ${modality} modality`);
    }
    
    // If a specific model is requested, use it
    if (requirements.modelId) {
      try {
        return this.getModel(requirements.modelId, modality);
      } catch (error) {
        this.logger.warn(`Requested model ${requirements.modelId} not found, selecting best alternative`);
        // Continue with selection logic
      }
    }
    
    // Filter models based on requirements
    let candidates = models.filter(model => {
      // Check if model meets minimum requirements
      if (requirements.minContextWindow && model.contextWindow < requirements.minContextWindow) {
        return false;
      }
      
      if (requirements.sourcePreference === 'open-source' && !model.isOpenSource) {
        return false;
      }
      
      if (requirements.sourcePreference === 'proprietary' && model.isOpenSource) {
        return false;
      }
      
      if (requirements.processingPreference === 'local' && !model.supportsLocalProcessing) {
        return false;
      }
      
      if (requirements.processingPreference === 'cloud' && !model.supportsCloudProcessing) {
        return false;
      }
      
      // Additional requirements can be checked here
      
      return true;
    });
    
    // If no models meet the requirements, use all models
    if (candidates.length === 0) {
      this.logger.warn(`No models meet the requirements for ${modality} modality, using all available models`);
      candidates = models;
    }
    
    // Sort candidates by preference
    candidates.sort((a, b) => {
      // Prioritize models based on processing preference
      if (requirements.processingPreference === 'local') {
        if (a.supportsLocalProcessing && !b.supportsLocalProcessing) return -1;
        if (!a.supportsLocalProcessing && b.supportsLocalProcessing) return 1;
      } else if (requirements.processingPreference === 'cloud') {
        if (a.supportsCloudProcessing && !b.supportsCloudProcessing) return -1;
        if (!a.supportsCloudProcessing && b.supportsCloudProcessing) return 1;
      }
      
      // Prioritize models based on source preference
      if (requirements.sourcePreference === 'open-source') {
        if (a.isOpenSource && !b.isOpenSource) return -1;
        if (!a.isOpenSource && b.isOpenSource) return 1;
      } else if (requirements.sourcePreference === 'proprietary') {
        if (!a.isOpenSource && b.isOpenSource) return -1;
        if (a.isOpenSource && !b.isOpenSource) return 1;
      }
      
      // Prioritize models based on performance score
      return b.performanceScore - a.performanceScore;
    });
    
    // Return the best candidate
    return candidates[0];
  }
  
  /**
   * Create a fallback chain for a specific modality
   * @param {string} modality - Model modality
   * @param {Object} requirements - Task requirements
   * @returns {Array<Model>} Fallback chain
   */
  createFallbackChain(modality, requirements = {}) {
    const models = this.getModelsByModality(modality);
    
    if (models.length === 0) {
      throw new Error(`No models available for ${modality} modality`);
    }
    
    // Sort models by preference (same logic as selectModel)
    const sortedModels = [...models].sort((a, b) => {
      // Prioritize models based on processing preference
      if (requirements.processingPreference === 'local') {
        if (a.supportsLocalProcessing && !b.supportsLocalProcessing) return -1;
        if (!a.supportsLocalProcessing && b.supportsLocalProcessing) return 1;
      } else if (requirements.processingPreference === 'cloud') {
        if (a.supportsCloudProcessing && !b.supportsCloudProcessing) return -1;
        if (!a.supportsCloudProcessing && b.supportsCloudProcessing) return 1;
      }
      
      // Prioritize models based on source preference
      if (requirements.sourcePreference === 'open-source') {
        if (a.isOpenSource && !b.isOpenSource) return -1;
        if (!a.isOpenSource && b.isOpenSource) return 1;
      } else if (requirements.sourcePreference === 'proprietary') {
        if (!a.isOpenSource && b.isOpenSource) return -1;
        if (a.isOpenSource && !b.isOpenSource) return 1;
      }
      
      // Prioritize models based on performance score
      return b.performanceScore - a.performanceScore;
    });
    
    // Create fallback chain
    return sortedModels;
  }
  
  /**
   * Execute a model request with fallback
   * @param {string} modality - Model modality
   * @param {Object} params - Request parameters
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Model response
   */
  async executeWithFallback(modality, params, options = {}) {
    // Create a fallback chain
    const fallbackChain = this.createFallbackChain(modality, options.requirements || {});
    
    // Try each model in the chain
    let lastError = null;
    
    for (const model of fallbackChain) {
      try {
        // Try to execute the request with this model
        const result = await this.execute(model.id, modality, params, options);
        
        // If successful, return the result
        return result;
      } catch (error) {
        // Log the error and continue with the next model
        this.logger.warn(`Model ${model.id} failed:`, error);
        lastError = error;
      }
    }
    
    // If all models failed, throw the last error
    throw new Error(`All models failed for ${modality} modality: ${lastError.message}`);
  }
  
  /**
   * Execute a model request
   * @param {string} modelId - Model ID
   * @param {string} modality - Model modality
   * @param {Object} params - Request parameters
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Model response
   */
  async execute(modelId, modality, params, options = {}) {
    if (!this.initialized) {
      throw new Error('Model Integration Framework is not initialized');
    }
    
    // Get the model
    const model = this.getModel(modelId, modality);
    
    // Check if response is cached
    const cacheKey = this._getCacheKey(modelId, modality, params);
    
    if (options.useCache !== false && this.responseCache.has(cacheKey)) {
      this.logger.debug(`Using cached response for ${modelId}`);
      return this.responseCache.get(cacheKey);
    }
    
    // Start timing
    const startTime = Date.now();
    
    try {
      // Update metrics
      this.metrics.totalRequests++;
      this.metrics.requestsByModality[modality]++;
      
      // Execute the request
      const result = await model.execute(params, options);
      
      // Update metrics
      this.metrics.successfulRequests++;
      
      // Calculate latency
      const latency = Date.now() - startTime;
      
      // Update average latency
      this.metrics.averageLatency = 
        (this.metrics.averageLatency * (this.metrics.totalRequests - 1) + latency) / 
        this.metrics.totalRequests;
      
      // Cache the response if caching is enabled
      if (options.useCache !== false && options.cacheExpiry !== 0) {
        const expiry = options.cacheExpiry || 3600000; // Default: 1 hour
        
        // Set cache with expiry
        this.responseCache.set(cacheKey, result);
        
        // Set timeout to remove from cache
        setTimeout(() => {
          this.responseCache.delete(cacheKey);
        }, expiry);
      }
      
      return result;
    } catch (error) {
      // Update metrics
      this.metrics.failedRequests++;
      
      // Log and rethrow
      this.logger.error(`Model ${modelId} execution failed:`, error);
      throw error;
    }
  }
  
  /**
   * Generate a cache key for a request
   * @param {string} modelId - Model ID
   * @param {string} modality - Model modality
   * @param {Object} params - Request parameters
   * @returns {string} Cache key
   * @private
   */
  _getCacheKey(modelId, modality, params) {
    return `${modelId}:${modality}:${JSON.stringify(params)}`;
  }
  
  /**
   * Get metrics for the framework
   * @returns {Object} Metrics
   */
  getMetrics() {
    return this.metrics;
  }
  
  /**
   * Clean up resources
   * @returns {Promise<void>}
   */
  async shutdown() {
    if (!this.initialized) {
      return;
    }
    
    this.logger.info('Shutting down Model Integration Framework...');
    
    // Shutdown all providers
    const shutdownPromises = [];
    
    for (const provider of this.providers.values()) {
      shutdownPromises.push(provider.shutdown().catch(error => {
        this.logger.error(`Error shutting down provider ${provider.id}:`, error);
      }));
    }
    
    await Promise.all(shutdownPromises);
    
    // Clear caches
    this.responseCache.clear();
    
    this.initialized = false;
    this.logger.info('Model Integration Framework shut down successfully');
  }
}

/**
 * Base Model Provider class
 * All model providers should extend this class
 */
class ModelProvider {
  /**
   * Initialize the Model Provider
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger(`provider-${this.id}`);
    this.models = [];
    this.initialized = false;
  }
  
  /**
   * Get provider ID
   * @returns {string} Provider ID
   */
  get id() {
    throw new Error('Provider ID not implemented');
  }
  
  /**
   * Get provider name
   * @returns {string} Provider name
   */
  get name() {
    throw new Error('Provider name not implemented');
  }
  
  /**
   * Initialize the provider
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    await this._registerModels();
    this.initialized = true;
  }
  
  /**
   * Register models provided by this provider
   * @returns {Promise<void>}
   * @protected
   */
  async _registerModels() {
    // To be implemented by subclasses
    throw new Error('_registerModels not implemented');
  }
  
  /**
   * Get all models from this provider
   * @returns {Array<Model>} Array of models
   */
  getModels() {
    return this.models;
  }
  
  /**
   * Clean up resources
   * @returns {Promise<void>}
   */
  async shutdown() {
    // To be implemented by subclasses if needed
  }
}

/**
 * Base Model class
 * All models should extend this class
 */
class Model {
  /**
   * Initialize the Model
   * @param {ModelProvider} provider - Provider that owns this model
   * @param {Object} config - Model configuration
   */
  constructor(provider, config) {
    this.provider = provider;
    this.id = config.id;
    this.name = config.name;
    this.modality = config.modality;
    this.version = config.version || '1.0.0';
    this.description = config.description || '';
    this.contextWindow = config.contextWindow || 4096;
    this.isOpenSource = config.isOpenSource || false;
    this.supportsLocalProcessing = config.supportsLocalProcessing || false;
    this.supportsCloudProcessing = config.supportsCloudProcessing || true;
    this.performanceScore = config.performanceScore || 0;
    this.parameters = config.parameters || [];
    this.logger = provider.logger;
  }
  
  /**
   * Execute the model
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @returns {Promise<any>} Model execution result
   */
  async execute(params, options) {
    throw new Error('Model execution not implemented');
  }
  
  /**
   * Validate parameters for this model
   * @param {Object} params - Parameters to validate
   * @returns {Promise<boolean>} Validation result
   */
  async validateParams(params) {
    // Basic validation - check required parameters
    for (const param of this.parameters) {
      if (param.required && (params[param.name] === undefined || params[param.name] === null)) {
        throw new Error(`Required parameter '${param.name}' is missing`);
      }
    }
    
    return true;
  }
}

// Export classes
module.exports = {
  ModelIntegrationFramework,
  ModelProvider,
  Model
};
