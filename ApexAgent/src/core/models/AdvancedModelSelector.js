/**
 * AdvancedModelSelector.js
 * 
 * Advanced AI model selection system for Aideon AI Lite.
 * Dynamically selects the optimal AI model for each task based on requirements,
 * context, performance history, and available resources.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;

/**
 * Advanced Model Selector for Aideon AI Lite
 */
class AdvancedModelSelector extends EventEmitter {
  /**
   * Creates a new AdvancedModelSelector instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super();
    
    this.core = core;
    this.logger = core.getLogManager().getLogger('model-selector');
    this.configManager = core.getConfigManager();
    
    this.modelManager = null;
    this.modelCache = new Map();
    this.modelPerformanceHistory = new Map();
    this.taskContextHistory = new Map();
    
    this.selectionStrategies = new Map();
    this.fallbackChains = new Map();
    
    this.isInitialized = false;
    
    // Bind methods
    this._handleModelSuccess = this._handleModelSuccess.bind(this);
    this._handleModelFailure = this._handleModelFailure.bind(this);
  }
  
  /**
   * Initializes the advanced model selector
   * 
   * @param {Object} options - Initialization options
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize(options = {}) {
    try {
      this.logger.info('Initializing Advanced Model Selector');
      
      // Get model manager
      this.modelManager = this.core.getModelManager();
      
      if (!this.modelManager) {
        throw new Error('Model Manager not available');
      }
      
      // Load performance history
      await this._loadPerformanceHistory();
      
      // Register selection strategies
      this._registerSelectionStrategies();
      
      // Register fallback chains
      this._registerFallbackChains();
      
      // Register event listeners
      this._registerEventListeners();
      
      this.isInitialized = true;
      this.logger.info('Advanced Model Selector initialized successfully');
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Advanced Model Selector: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Selects the optimal model for a task
   * 
   * @param {Object} taskContext - Task context information
   * @returns {Promise<Object>} Selected model
   */
  async selectModel(taskContext) {
    try {
      if (!this.isInitialized) {
        throw new Error('Advanced Model Selector not initialized');
      }
      
      this.logger.debug(`Selecting model for task: ${taskContext.taskId}`);
      
      // Validate task context
      this._validateTaskContext(taskContext);
      
      // Get available models
      const availableModels = await this.modelManager.getAvailableModels(taskContext.modality);
      
      if (!availableModels || availableModels.length === 0) {
        throw new Error(`No models available for modality: ${taskContext.modality}`);
      }
      
      // Get selection strategy
      const strategyName = taskContext.strategy || 'default';
      const strategy = this.selectionStrategies.get(strategyName) || this.selectionStrategies.get('default');
      
      if (!strategy) {
        throw new Error(`Selection strategy not found: ${strategyName}`);
      }
      
      // Apply selection strategy
      const selectedModel = await strategy(taskContext, availableModels);
      
      if (!selectedModel) {
        throw new Error('Failed to select model');
      }
      
      // Store task context for learning
      this._storeTaskContext(taskContext, selectedModel.id);
      
      this.logger.info(`Selected model ${selectedModel.id} for task ${taskContext.taskId}`);
      
      // Emit model selected event
      this.emit('model:selected', {
        taskId: taskContext.taskId,
        modelId: selectedModel.id,
        strategy: strategyName
      });
      
      return selectedModel;
    } catch (error) {
      this.logger.error(`Failed to select model: ${error.message}`, error);
      
      // Try fallback chain
      if (taskContext.allowFallback !== false) {
        return this._tryFallbackChain(taskContext, error);
      }
      
      throw error;
    }
  }
  
  /**
   * Gets model performance history
   * 
   * @param {string} modelId - Model ID
   * @returns {Object} Model performance history
   */
  getModelPerformance(modelId) {
    return this.modelPerformanceHistory.get(modelId) || {
      successCount: 0,
      failureCount: 0,
      averageLatency: 0,
      averageTokens: 0,
      lastUsed: null
    };
  }
  
  /**
   * Gets all model performance history
   * 
   * @returns {Map<string, Object>} All model performance history
   */
  getAllModelPerformance() {
    return new Map(this.modelPerformanceHistory);
  }
  
  /**
   * Registers a custom selection strategy
   * 
   * @param {string} name - Strategy name
   * @param {Function} strategyFn - Strategy function
   * @returns {boolean} True if strategy was registered
   */
  registerSelectionStrategy(name, strategyFn) {
    try {
      if (!name || typeof name !== 'string') {
        throw new Error('Strategy name must be a string');
      }
      
      if (!strategyFn || typeof strategyFn !== 'function') {
        throw new Error('Strategy function must be a function');
      }
      
      this.selectionStrategies.set(name, strategyFn);
      
      this.logger.info(`Registered selection strategy: ${name}`);
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to register selection strategy: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Registers a fallback chain
   * 
   * @param {string} modality - Modality
   * @param {Array<string>} modelIds - Model IDs in fallback order
   * @returns {boolean} True if fallback chain was registered
   */
  registerFallbackChain(modality, modelIds) {
    try {
      if (!modality || typeof modality !== 'string') {
        throw new Error('Modality must be a string');
      }
      
      if (!Array.isArray(modelIds) || modelIds.length === 0) {
        throw new Error('Model IDs must be a non-empty array');
      }
      
      this.fallbackChains.set(modality, [...modelIds]);
      
      this.logger.info(`Registered fallback chain for ${modality}: ${modelIds.join(' -> ')}`);
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to register fallback chain: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Records model usage result
   * 
   * @param {string} modelId - Model ID
   * @param {boolean} success - Whether the model usage was successful
   * @param {Object} metrics - Usage metrics
   * @returns {Promise<boolean>} True if result was recorded
   */
  async recordModelUsage(modelId, success, metrics = {}) {
    try {
      if (!this.isInitialized) {
        throw new Error('Advanced Model Selector not initialized');
      }
      
      // Get current performance data
      const performance = this.modelPerformanceHistory.get(modelId) || {
        successCount: 0,
        failureCount: 0,
        averageLatency: 0,
        averageTokens: 0,
        lastUsed: null
      };
      
      // Update performance data
      if (success) {
        performance.successCount++;
      } else {
        performance.failureCount++;
      }
      
      // Update latency
      if (metrics.latency !== undefined) {
        const totalLatency = performance.averageLatency * (performance.successCount + performance.failureCount - 1);
        performance.averageLatency = (totalLatency + metrics.latency) / (performance.successCount + performance.failureCount);
      }
      
      // Update tokens
      if (metrics.tokens !== undefined) {
        const totalTokens = performance.averageTokens * (performance.successCount + performance.failureCount - 1);
        performance.averageTokens = (totalTokens + metrics.tokens) / (performance.successCount + performance.failureCount);
      }
      
      // Update last used
      performance.lastUsed = new Date();
      
      // Store updated performance data
      this.modelPerformanceHistory.set(modelId, performance);
      
      // Save performance history periodically
      this._savePerformanceHistory();
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to record model usage: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Clears model cache
   * 
   * @returns {boolean} True if cache was cleared
   */
  clearCache() {
    try {
      this.modelCache.clear();
      this.logger.info('Model cache cleared');
      return true;
    } catch (error) {
      this.logger.error(`Failed to clear model cache: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Validates task context
   * 
   * @private
   * @param {Object} taskContext - Task context
   */
  _validateTaskContext(taskContext) {
    if (!taskContext) {
      throw new Error('Task context is required');
    }
    
    if (!taskContext.taskId) {
      throw new Error('Task ID is required');
    }
    
    if (!taskContext.modality) {
      throw new Error('Modality is required');
    }
  }
  
  /**
   * Stores task context for learning
   * 
   * @private
   * @param {Object} taskContext - Task context
   * @param {string} modelId - Selected model ID
   */
  _storeTaskContext(taskContext, modelId) {
    // Store only the last 1000 task contexts
    if (this.taskContextHistory.size >= 1000) {
      // Remove oldest entry
      const oldestKey = this.taskContextHistory.keys().next().value;
      this.taskContextHistory.delete(oldestKey);
    }
    
    // Store task context with timestamp and selected model
    this.taskContextHistory.set(taskContext.taskId, {
      context: taskContext,
      modelId,
      timestamp: new Date()
    });
  }
  
  /**
   * Tries fallback chain for model selection
   * 
   * @private
   * @param {Object} taskContext - Task context
   * @param {Error} originalError - Original error
   * @returns {Promise<Object>} Selected model
   */
  async _tryFallbackChain(taskContext, originalError) {
    try {
      this.logger.warn(`Trying fallback chain for ${taskContext.modality} due to: ${originalError.message}`);
      
      // Get fallback chain
      const fallbackChain = this.fallbackChains.get(taskContext.modality);
      
      if (!fallbackChain || fallbackChain.length === 0) {
        throw new Error(`No fallback chain available for modality: ${taskContext.modality}`);
      }
      
      // Try each model in the fallback chain
      for (const modelId of fallbackChain) {
        try {
          const model = await this.modelManager.getModel(modelId);
          
          if (model) {
            this.logger.info(`Using fallback model ${modelId} for task ${taskContext.taskId}`);
            
            // Emit fallback event
            this.emit('model:fallback', {
              taskId: taskContext.taskId,
              originalError: originalError.message,
              fallbackModelId: modelId
            });
            
            return model;
          }
        } catch (error) {
          this.logger.warn(`Fallback model ${modelId} not available: ${error.message}`);
        }
      }
      
      // If all fallbacks fail, throw original error
      throw originalError;
    } catch (error) {
      this.logger.error(`Fallback chain failed: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Registers built-in selection strategies
   * 
   * @private
   */
  _registerSelectionStrategies() {
    // Default strategy - balances performance, cost, and capabilities
    this.registerSelectionStrategy('default', async (taskContext, availableModels) => {
      // Filter models by required capabilities
      let candidates = availableModels;
      
      if (taskContext.requiredCapabilities && taskContext.requiredCapabilities.length > 0) {
        candidates = candidates.filter(model => {
          return taskContext.requiredCapabilities.every(cap => 
            model.capabilities && model.capabilities.includes(cap)
          );
        });
      }
      
      if (candidates.length === 0) {
        throw new Error('No models match required capabilities');
      }
      
      // Calculate score for each model
      const scoredModels = candidates.map(model => {
        const performance = this.getModelPerformance(model.id);
        
        // Calculate success rate (default to 1 if no history)
        const totalUses = performance.successCount + performance.failureCount;
        const successRate = totalUses > 0 ? performance.successCount / totalUses : 1;
        
        // Calculate recency score (higher for recently used models)
        const recencyScore = performance.lastUsed 
          ? Math.max(0, 1 - (Date.now() - performance.lastUsed.getTime()) / (7 * 24 * 60 * 60 * 1000))
          : 0;
        
        // Calculate latency score (higher for faster models)
        const latencyScore = performance.averageLatency > 0 
          ? Math.max(0, 1 - performance.averageLatency / 10000)
          : 0.5;
        
        // Calculate cost score (higher for cheaper models)
        const costScore = 1 - (model.costPerToken || 0.5);
        
        // Calculate capability match score
        const capabilityScore = taskContext.preferredCapabilities 
          ? taskContext.preferredCapabilities.filter(cap => 
              model.capabilities && model.capabilities.includes(cap)
            ).length / taskContext.preferredCapabilities.length
          : 0.5;
        
        // Calculate final score
        const score = (
          successRate * 0.3 +
          recencyScore * 0.1 +
          latencyScore * 0.2 +
          costScore * 0.2 +
          capabilityScore * 0.2
        );
        
        return { model, score };
      });
      
      // Sort by score (descending)
      scoredModels.sort((a, b) => b.score - a.score);
      
      // Return highest scoring model
      return scoredModels[0].model;
    });
    
    // Performance strategy - prioritizes models with best performance
    this.registerSelectionStrategy('performance', async (taskContext, availableModels) => {
      // Filter models by required capabilities
      let candidates = availableModels;
      
      if (taskContext.requiredCapabilities && taskContext.requiredCapabilities.length > 0) {
        candidates = candidates.filter(model => {
          return taskContext.requiredCapabilities.every(cap => 
            model.capabilities && model.capabilities.includes(cap)
          );
        });
      }
      
      if (candidates.length === 0) {
        throw new Error('No models match required capabilities');
      }
      
      // Sort by performance metrics
      candidates.sort((a, b) => {
        const perfA = this.getModelPerformance(a.id);
        const perfB = this.getModelPerformance(b.id);
        
        // Calculate success rate
        const successRateA = perfA.successCount + perfA.failureCount > 0 
          ? perfA.successCount / (perfA.successCount + perfA.failureCount) 
          : 0;
        
        const successRateB = perfB.successCount + perfB.failureCount > 0 
          ? perfB.successCount / (perfB.successCount + perfB.failureCount) 
          : 0;
        
        // Compare success rates
        if (Math.abs(successRateA - successRateB) > 0.1) {
          return successRateB - successRateA;
        }
        
        // If success rates are similar, compare latency
        return perfA.averageLatency - perfB.averageLatency;
      });
      
      // Return best performing model
      return candidates[0];
    });
    
    // Cost strategy - prioritizes cheaper models
    this.registerSelectionStrategy('cost', async (taskContext, availableModels) => {
      // Filter models by required capabilities
      let candidates = availableModels;
      
      if (taskContext.requiredCapabilities && taskContext.requiredCapabilities.length > 0) {
        candidates = candidates.filter(model => {
          return taskContext.requiredCapabilities.every(cap => 
            model.capabilities && model.capabilities.includes(cap)
          );
        });
      }
      
      if (candidates.length === 0) {
        throw new Error('No models match required capabilities');
      }
      
      // Sort by cost (ascending)
      candidates.sort((a, b) => (a.costPerToken || 0) - (b.costPerToken || 0));
      
      // Return cheapest model
      return candidates[0];
    });
    
    // Capability strategy - prioritizes models with most capabilities
    this.registerSelectionStrategy('capability', async (taskContext, availableModels) => {
      // Filter models by required capabilities
      let candidates = availableModels;
      
      if (taskContext.requiredCapabilities && taskContext.requiredCapabilities.length > 0) {
        candidates = candidates.filter(model => {
          return taskContext.requiredCapabilities.every(cap => 
            model.capabilities && model.capabilities.includes(cap)
          );
        });
      }
      
      if (candidates.length === 0) {
        throw new Error('No models match required capabilities');
      }
      
      // Sort by number of capabilities (descending)
      candidates.sort((a, b) => 
        (b.capabilities ? b.capabilities.length : 0) - 
        (a.capabilities ? a.capabilities.length : 0)
      );
      
      // Return model with most capabilities
      return candidates[0];
    });
    
    // Local strategy - prioritizes local models
    this.registerSelectionStrategy('local', async (taskContext, availableModels) => {
      // Filter models by required capabilities
      let candidates = availableModels;
      
      if (taskContext.requiredCapabilities && taskContext.requiredCapabilities.length > 0) {
        candidates = candidates.filter(model => {
          return taskContext.requiredCapabilities.every(cap => 
            model.capabilities && model.capabilities.includes(cap)
          );
        });
      }
      
      // Filter local models
      const localModels = candidates.filter(model => model.deployment === 'local');
      
      if (localModels.length === 0) {
        throw new Error('No local models available that match requirements');
      }
      
      // Sort by performance
      localModels.sort((a, b) => {
        const perfA = this.getModelPerformance(a.id);
        const perfB = this.getModelPerformance(b.id);
        
        // Calculate success rate
        const successRateA = perfA.successCount + perfA.failureCount > 0 
          ? perfA.successCount / (perfA.successCount + perfA.failureCount) 
          : 0;
        
        const successRateB = perfB.successCount + perfB.failureCount > 0 
          ? perfB.successCount / (perfB.successCount + perfB.failureCount) 
          : 0;
        
        return successRateB - successRateA;
      });
      
      // Return best local model
      return localModels[0];
    });
    
    // Cloud strategy - prioritizes cloud models
    this.registerSelectionStrategy('cloud', async (taskContext, availableModels) => {
      // Filter models by required capabilities
      let candidates = availableModels;
      
      if (taskContext.requiredCapabilities && taskContext.requiredCapabilities.length > 0) {
        candidates = candidates.filter(model => {
          return taskContext.requiredCapabilities.every(cap => 
            model.capabilities && model.capabilities.includes(cap)
          );
        });
      }
      
      // Filter cloud models
      const cloudModels = candidates.filter(model => model.deployment === 'cloud');
      
      if (cloudModels.length === 0) {
        throw new Error('No cloud models available that match requirements');
      }
      
      // Sort by performance
      cloudModels.sort((a, b) => {
        const perfA = this.getModelPerformance(a.id);
        const perfB = this.getModelPerformance(b.id);
        
        // Calculate success rate
        const successRateA = perfA.successCount + perfA.failureCount > 0 
          ? perfA.successCount / (perfA.successCount + perfA.failureCount) 
          : 0;
        
        const successRateB = perfB.successCount + perfB.failureCount > 0 
          ? perfB.successCount / (perfB.successCount + perfB.failureCount) 
          : 0;
        
        return successRateB - successRateA;
      });
      
      // Return best cloud model
      return cloudModels[0];
    });
    
    // Learning strategy - uses historical task context to select models
    this.registerSelectionStrategy('learning', async (taskContext, availableModels) => {
      // Filter models by required capabilities
      let candidates = availableModels;
      
      if (taskContext.requiredCapabilities && taskContext.requiredCapabilities.length > 0) {
        candidates = candidates.filter(model => {
          return taskContext.requiredCapabilities.every(cap => 
            model.capabilities && model.capabilities.includes(cap)
          );
        });
      }
      
      if (candidates.length === 0) {
        throw new Error('No models match required capabilities');
      }
      
      // Find similar tasks in history
      const similarTasks = Array.from(this.taskContextHistory.values())
        .filter(entry => {
          // Check if modality matches
          if (entry.context.modality !== taskContext.modality) {
            return false;
          }
          
          // Check if task type matches
          if (entry.context.taskType && taskContext.taskType && 
              entry.context.taskType !== taskContext.taskType) {
            return false;
          }
          
          // Check if there are common tags
          if (entry.context.tags && taskContext.tags) {
            const commonTags = entry.context.tags.filter(tag => 
              taskContext.tags.includes(tag)
            );
            
            if (commonTags.length === 0) {
              return false;
            }
          }
          
          return true;
        });
      
      if (similarTasks.length > 0) {
        // Count model usage in similar tasks
        const modelCounts = new Map();
        
        for (const task of similarTasks) {
          const count = modelCounts.get(task.modelId) || 0;
          modelCounts.set(task.modelId, count + 1);
        }
        
        // Find most used model that's available
        let mostUsedModel = null;
        let highestCount = 0;
        
        for (const [modelId, count] of modelCounts.entries()) {
          if (count > highestCount) {
            const model = candidates.find(m => m.id === modelId);
            
            if (model) {
              mostUsedModel = model;
              highestCount = count;
            }
          }
        }
        
        if (mostUsedModel) {
          return mostUsedModel;
        }
      }
      
      // Fall back to default strategy if no similar tasks found
      return this.selectionStrategies.get('default')(taskContext, availableModels);
    });
  }
  
  /**
   * Registers default fallback chains
   * 
   * @private
   */
  _registerFallbackChains() {
    // Text modality fallback chain
    this.registerFallbackChain('text', [
      'gpt-4-turbo',
      'claude-3-opus',
      'gpt-4',
      'claude-3-sonnet',
      'gpt-3.5-turbo',
      'llama-3-70b',
      'llama-3-8b',
      'mistral-7b'
    ]);
    
    // Code modality fallback chain
    this.registerFallbackChain('code', [
      'claude-3-opus',
      'gpt-4-turbo',
      'codellama-34b',
      'gpt-4',
      'claude-3-sonnet',
      'codellama-13b',
      'gpt-3.5-turbo'
    ]);
    
    // Image modality fallback chain
    this.registerFallbackChain('image', [
      'dalle-3',
      'midjourney',
      'stable-diffusion-xl',
      'stable-diffusion-3',
      'kandinsky-2'
    ]);
    
    // Video modality fallback chain
    this.registerFallbackChain('video', [
      'sora',
      'gen-2',
      'pika-1',
      'runway-gen-2'
    ]);
    
    // Audio modality fallback chain
    this.registerFallbackChain('audio', [
      'whisper-large-v3',
      'whisper-medium',
      'bark',
      'musicgen'
    ]);
    
    // Multimodal fallback chain
    this.registerFallbackChain('multimodal', [
      'gpt-4-vision',
      'claude-3-opus',
      'claude-3-sonnet',
      'gemini-pro',
      'llava-13b'
    ]);
  }
  
  /**
   * Registers event listeners
   * 
   * @private
   */
  _registerEventListeners() {
    // Listen for model success events
    this.modelManager.on('model:success', this._handleModelSuccess);
    
    // Listen for model failure events
    this.modelManager.on('model:failure', this._handleModelFailure);
  }
  
  /**
   * Handles model success events
   * 
   * @private
   * @param {Object} data - Event data
   */
  _handleModelSuccess(data) {
    this.recordModelUsage(data.modelId, true, {
      latency: data.latency,
      tokens: data.tokens
    });
  }
  
  /**
   * Handles model failure events
   * 
   * @private
   * @param {Object} data - Event data
   */
  _handleModelFailure(data) {
    this.recordModelUsage(data.modelId, false, {
      latency: data.latency
    });
  }
  
  /**
   * Loads model performance history
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _loadPerformanceHistory() {
    try {
      const historyPath = path.join(
        this.configManager.getDataDir(),
        'model-performance-history.json'
      );
      
      // Check if file exists
      const exists = await fs.stat(historyPath).catch(() => null);
      
      if (!exists) {
        this.logger.info('No model performance history found');
        return;
      }
      
      // Read and parse file
      const content = await fs.readFile(historyPath, 'utf8');
      const history = JSON.parse(content);
      
      // Convert to Map
      this.modelPerformanceHistory = new Map(Object.entries(history));
      
      // Convert date strings back to Date objects
      for (const [modelId, performance] of this.modelPerformanceHistory.entries()) {
        if (performance.lastUsed) {
          performance.lastUsed = new Date(performance.lastUsed);
        }
      }
      
      this.logger.info(`Loaded performance history for ${this.modelPerformanceHistory.size} models`);
    } catch (error) {
      this.logger.error(`Failed to load performance history: ${error.message}`, error);
    }
  }
  
  /**
   * Saves model performance history
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _savePerformanceHistory() {
    try {
      const historyPath = path.join(
        this.configManager.getDataDir(),
        'model-performance-history.json'
      );
      
      // Convert Map to object
      const history = Object.fromEntries(this.modelPerformanceHistory);
      
      // Write to file
      await fs.writeFile(historyPath, JSON.stringify(history, null, 2));
      
      this.logger.debug(`Saved performance history for ${this.modelPerformanceHistory.size} models`);
    } catch (error) {
      this.logger.error(`Failed to save performance history: ${error.message}`, error);
    }
  }
}

module.exports = { AdvancedModelSelector };
