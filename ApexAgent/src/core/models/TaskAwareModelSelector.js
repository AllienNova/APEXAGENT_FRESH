/**
 * Task-Aware Model Selector for Aideon AI Lite
 * 
 * This module provides automatic "best-by-default" model selection based on task analysis,
 * performance metrics, and historical outcomes. It ensures the optimal LLM is chosen
 * for any given task or subtask without requiring explicit configuration.
 */

const natural = require('natural');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs').promises;
const path = require('path');

/**
 * TaskAwareModelSelector class
 * Provides intelligent model selection based on task analysis
 */
class TaskAwareModelSelector {
  /**
   * Initialize the Task-Aware Model Selector
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger('task-aware-model-selector');
    this.modelFramework = core.modelIntegrationFramework;
    this.agentModelIntegration = core.agentModelIntegration;
    this.config = core.configManager.getConfig().taskAwareModelSelector || {};
    
    // Task classification system
    this.taskClassifier = new TaskClassifier();
    
    // Performance tracking
    this.performanceTracker = new PerformanceTracker(this.config.performanceHistorySize || 1000);
    
    // Model rankings by task type
    this.modelRankings = new Map();
    
    // Historical selection outcomes
    this.selectionHistory = [];
    
    // Maximum history size
    this.maxHistorySize = this.config.historySize || 10000;
    
    this.initialized = false;
    
    this.logger.info('Task-Aware Model Selector initialized');
  }
  
  /**
   * Initialize the selector
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    try {
      this.logger.info('Initializing Task-Aware Model Selector...');
      
      // Initialize task classifier
      await this.taskClassifier.initialize();
      
      // Load historical performance data
      await this._loadPerformanceData();
      
      // Build initial model rankings
      await this._buildInitialModelRankings();
      
      this.initialized = true;
      this.logger.info('Task-Aware Model Selector initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize Task-Aware Model Selector:', error);
      throw error;
    }
  }
  
  /**
   * Load historical performance data
   * @returns {Promise<void>}
   * @private
   */
  async _loadPerformanceData() {
    try {
      const dataPath = path.join(process.cwd(), 'data', 'model_performance.json');
      
      try {
        await fs.access(dataPath);
        
        // Load data
        const data = await fs.readFile(dataPath, 'utf8');
        const performanceData = JSON.parse(data);
        
        // Load into performance tracker
        this.performanceTracker.loadData(performanceData);
        
        this.logger.info('Loaded historical performance data');
      } catch (error) {
        // File doesn't exist or is invalid, just log and continue
        this.logger.info('No historical performance data found, starting fresh');
      }
    } catch (error) {
      this.logger.error('Failed to load performance data:', error);
      // Don't throw, just start with empty data
    }
  }
  
  /**
   * Build initial model rankings
   * @returns {Promise<void>}
   * @private
   */
  async _buildInitialModelRankings() {
    try {
      // Get all task types
      const taskTypes = this.taskClassifier.getAllTaskTypes();
      
      // Get all modalities
      const modalities = ['text', 'code', 'image', 'video', 'audio'];
      
      // For each task type and modality, build rankings
      for (const taskType of taskTypes) {
        for (const modality of modalities) {
          const key = `${taskType}:${modality}`;
          
          // Get models for this modality
          const models = this.modelFramework.getModelsByModality(modality);
          
          if (models.length === 0) {
            continue;
          }
          
          // Sort models by performance score for this task type
          const sortedModels = [...models].sort((a, b) => {
            // Get performance scores
            const scoreA = this.performanceTracker.getAverageScore(a.id, taskType) || a.performanceScore;
            const scoreB = this.performanceTracker.getAverageScore(b.id, taskType) || b.performanceScore;
            
            // Sort by score (descending)
            return scoreB - scoreA;
          });
          
          // Store ranking
          this.modelRankings.set(key, sortedModels.map(model => model.id));
        }
      }
      
      this.logger.info('Built initial model rankings');
    } catch (error) {
      this.logger.error('Failed to build initial model rankings:', error);
      throw error;
    }
  }
  
  /**
   * Select the best model for a task
   * @param {string} agentId - Agent ID
   * @param {string} modality - Model modality
   * @param {Object} task - Task details
   * @param {Object} options - Selection options
   * @returns {Object} Selected model
   */
  selectBestModel(agentId, modality, task, options = {}) {
    if (!this.initialized) {
      throw new Error('Task-Aware Model Selector is not initialized');
    }
    
    try {
      // Analyze task to determine task type
      const taskType = this.taskClassifier.classifyTask(task);
      
      // Get context features
      const contextFeatures = this._extractContextFeatures(task, options);
      
      // Get model ranking for this task type and modality
      const key = `${taskType}:${modality}`;
      const modelRanking = this.modelRankings.get(key) || [];
      
      // If no specific ranking, get all models for this modality
      const models = modelRanking.length > 0 
        ? modelRanking.map(id => this.modelFramework.getModel(id, modality))
        : this.modelFramework.getModelsByModality(modality);
      
      if (models.length === 0) {
        throw new Error(`No models available for ${modality} modality and ${taskType} task type`);
      }
      
      // Apply contextual adjustments
      const adjustedModels = this._applyContextualAdjustments(models, contextFeatures);
      
      // Get the best model
      const bestModel = adjustedModels[0];
      
      // Record selection for learning
      this._recordSelection(agentId, bestModel.id, taskType, modality, contextFeatures);
      
      this.logger.info(`Selected model ${bestModel.id} for agent ${agentId}, task type ${taskType}, modality ${modality}`);
      
      return bestModel;
    } catch (error) {
      this.logger.error(`Failed to select best model: ${error.message}`);
      
      // Fallback to default selection
      return this.agentModelIntegration.selectModelForAgent(agentId, modality, options.requirements || {});
    }
  }
  
  /**
   * Extract context features from task
   * @param {Object} task - Task details
   * @param {Object} options - Selection options
   * @returns {Object} Context features
   * @private
   */
  _extractContextFeatures(task, options) {
    const features = {
      complexity: 'medium',
      length: 'medium',
      precision: 'medium',
      creativity: 'medium',
      timeConstraint: 'medium'
    };
    
    // Extract complexity
    if (task.prompt) {
      const promptLength = task.prompt.length;
      if (promptLength > 1000) {
        features.complexity = 'high';
        features.length = 'long';
      } else if (promptLength > 300) {
        features.complexity = 'medium';
        features.length = 'medium';
      } else {
        features.complexity = 'low';
        features.length = 'short';
      }
      
      // Check for code indicators
      if (task.prompt.includes('function') || task.prompt.includes('class') || 
          task.prompt.includes('def ') || task.prompt.includes('```')) {
        features.precision = 'high';
        features.creativity = 'low';
      }
      
      // Check for creative indicators
      if (task.prompt.includes('creative') || task.prompt.includes('imagine') || 
          task.prompt.includes('story') || task.prompt.includes('novel')) {
        features.creativity = 'high';
      }
    }
    
    // Extract time constraint
    if (options.timeConstraint) {
      features.timeConstraint = options.timeConstraint;
    } else if (options.urgent) {
      features.timeConstraint = 'low';
    }
    
    return features;
  }
  
  /**
   * Apply contextual adjustments to model ranking
   * @param {Array<Object>} models - Models to adjust
   * @param {Object} contextFeatures - Context features
   * @returns {Array<Object>} Adjusted models
   * @private
   */
  _applyContextualAdjustments(models, contextFeatures) {
    // Clone models to avoid modifying originals
    const adjustedModels = [...models];
    
    // Apply adjustments based on context features
    adjustedModels.sort((a, b) => {
      let scoreA = 0;
      let scoreB = 0;
      
      // Adjust for complexity
      if (contextFeatures.complexity === 'high') {
        // Prefer models with larger context windows
        scoreA += a.contextWindow / 10000;
        scoreB += b.contextWindow / 10000;
      }
      
      // Adjust for time constraint
      if (contextFeatures.timeConstraint === 'low') {
        // Prefer faster models
        if (a.supportsLocalProcessing) scoreA += 5;
        if (b.supportsLocalProcessing) scoreB += 5;
      }
      
      // Adjust for precision
      if (contextFeatures.precision === 'high') {
        // Check model capabilities
        const capabilitiesA = this.agentModelIntegration.getModelCapabilities(a.id);
        const capabilitiesB = this.agentModelIntegration.getModelCapabilities(b.id);
        
        if (capabilitiesA.includes('reasoning')) scoreA += 3;
        if (capabilitiesB.includes('reasoning')) scoreB += 3;
      }
      
      // Adjust for creativity
      if (contextFeatures.creativity === 'high') {
        // Proprietary models often have better creative capabilities
        if (!a.isOpenSource) scoreA += 2;
        if (!b.isOpenSource) scoreB += 2;
      }
      
      // Use performance score as base
      scoreA += a.performanceScore;
      scoreB += b.performanceScore;
      
      // Sort by adjusted score (descending)
      return scoreB - scoreA;
    });
    
    return adjustedModels;
  }
  
  /**
   * Record model selection for learning
   * @param {string} agentId - Agent ID
   * @param {string} modelId - Model ID
   * @param {string} taskType - Task type
   * @param {string} modality - Model modality
   * @param {Object} contextFeatures - Context features
   * @private
   */
  _recordSelection(agentId, modelId, taskType, modality, contextFeatures) {
    // Create selection record
    const record = {
      id: uuidv4(),
      timestamp: Date.now(),
      agentId,
      modelId,
      taskType,
      modality,
      contextFeatures,
      outcome: null // Will be updated later
    };
    
    // Add to history
    this.selectionHistory.push(record);
    
    // Trim history if needed
    if (this.selectionHistory.length > this.maxHistorySize) {
      this.selectionHistory = this.selectionHistory.slice(-this.maxHistorySize);
    }
  }
  
  /**
   * Update selection outcome
   * @param {string} selectionId - Selection ID
   * @param {Object} outcome - Outcome details
   * @returns {boolean} Success status
   */
  updateSelectionOutcome(selectionId, outcome) {
    // Find selection record
    const recordIndex = this.selectionHistory.findIndex(record => record.id === selectionId);
    
    if (recordIndex === -1) {
      this.logger.warn(`Selection record ${selectionId} not found`);
      return false;
    }
    
    // Update outcome
    this.selectionHistory[recordIndex].outcome = outcome;
    
    // Update performance tracker
    const record = this.selectionHistory[recordIndex];
    this.performanceTracker.recordOutcome(
      record.modelId,
      record.taskType,
      outcome.score,
      outcome.metrics
    );
    
    // Update model rankings
    this._updateModelRankings(record.taskType, record.modality);
    
    return true;
  }
  
  /**
   * Update model rankings for a task type and modality
   * @param {string} taskType - Task type
   * @param {string} modality - Model modality
   * @private
   */
  _updateModelRankings(taskType, modality) {
    // Get models for this modality
    const models = this.modelFramework.getModelsByModality(modality);
    
    if (models.length === 0) {
      return;
    }
    
    // Sort models by performance score for this task type
    const sortedModels = [...models].sort((a, b) => {
      // Get performance scores
      const scoreA = this.performanceTracker.getAverageScore(a.id, taskType) || a.performanceScore;
      const scoreB = this.performanceTracker.getAverageScore(b.id, taskType) || b.performanceScore;
      
      // Sort by score (descending)
      return scoreB - scoreA;
    });
    
    // Update ranking
    const key = `${taskType}:${modality}`;
    this.modelRankings.set(key, sortedModels.map(model => model.id));
  }
  
  /**
   * Save performance data
   * @returns {Promise<void>}
   */
  async savePerformanceData() {
    try {
      // Create data directory if it doesn't exist
      const dataDir = path.join(process.cwd(), 'data');
      await fs.mkdir(dataDir, { recursive: true });
      
      // Save performance data
      const dataPath = path.join(dataDir, 'model_performance.json');
      await fs.writeFile(dataPath, JSON.stringify(this.performanceTracker.getData(), null, 2));
      
      this.logger.info('Saved performance data');
    } catch (error) {
      this.logger.error('Failed to save performance data:', error);
    }
  }
  
  /**
   * Get model rankings
   * @returns {Map<string, Array<string>>} Model rankings
   */
  getModelRankings() {
    return this.modelRankings;
  }
  
  /**
   * Get selection history
   * @param {number} limit - Maximum number of records to return
   * @returns {Array<Object>} Selection history
   */
  getSelectionHistory(limit = 100) {
    return this.selectionHistory.slice(-limit);
  }
  
  /**
   * Clean up resources
   * @returns {Promise<void>}
   */
  async shutdown() {
    if (!this.initialized) {
      return;
    }
    
    this.logger.info('Shutting down Task-Aware Model Selector...');
    
    // Save performance data
    await this.savePerformanceData();
    
    this.initialized = false;
    this.logger.info('Task-Aware Model Selector shut down successfully');
  }
}

/**
 * TaskClassifier class
 * Classifies tasks into different types
 */
class TaskClassifier {
  constructor() {
    // Task types
    this.taskTypes = [
      'general_conversation',
      'creative_writing',
      'factual_qa',
      'summarization',
      'translation',
      'code_generation',
      'code_explanation',
      'debugging',
      'image_generation',
      'image_editing',
      'video_generation',
      'audio_generation',
      'data_analysis',
      'reasoning',
      'planning'
    ];
    
    // Classifier
    this.classifier = new natural.BayesClassifier();
    
    // Initialized flag
    this.initialized = false;
  }
  
  /**
   * Initialize the classifier
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    // Train classifier with examples
    this._trainClassifier();
    
    this.initialized = true;
  }
  
  /**
   * Train the classifier with examples
   * @private
   */
  _trainClassifier() {
    // General conversation
    this.classifier.addDocument('How are you today?', 'general_conversation');
    this.classifier.addDocument('Tell me about yourself', 'general_conversation');
    this.classifier.addDocument('What can you do?', 'general_conversation');
    
    // Creative writing
    this.classifier.addDocument('Write a short story about a robot', 'creative_writing');
    this.classifier.addDocument('Create a poem about nature', 'creative_writing');
    this.classifier.addDocument('Write a creative description of a sunset', 'creative_writing');
    
    // Factual QA
    this.classifier.addDocument('What is the capital of France?', 'factual_qa');
    this.classifier.addDocument('Who invented the telephone?', 'factual_qa');
    this.classifier.addDocument('What is the boiling point of water?', 'factual_qa');
    
    // Summarization
    this.classifier.addDocument('Summarize this article', 'summarization');
    this.classifier.addDocument('Give me a summary of', 'summarization');
    this.classifier.addDocument('Can you summarize the main points', 'summarization');
    
    // Translation
    this.classifier.addDocument('Translate this to Spanish', 'translation');
    this.classifier.addDocument('How do you say hello in Japanese?', 'translation');
    this.classifier.addDocument('Convert this text to French', 'translation');
    
    // Code generation
    this.classifier.addDocument('Write a function that', 'code_generation');
    this.classifier.addDocument('Create a class for', 'code_generation');
    this.classifier.addDocument('Generate code for', 'code_generation');
    
    // Code explanation
    this.classifier.addDocument('Explain this code', 'code_explanation');
    this.classifier.addDocument('What does this function do?', 'code_explanation');
    this.classifier.addDocument('Help me understand this algorithm', 'code_explanation');
    
    // Debugging
    this.classifier.addDocument('Fix this code', 'debugging');
    this.classifier.addDocument('Why am I getting this error?', 'debugging');
    this.classifier.addDocument('Debug this function', 'debugging');
    
    // Image generation
    this.classifier.addDocument('Generate an image of', 'image_generation');
    this.classifier.addDocument('Create a picture of', 'image_generation');
    this.classifier.addDocument('Make an illustration of', 'image_generation');
    
    // Image editing
    this.classifier.addDocument('Edit this image to', 'image_editing');
    this.classifier.addDocument('Change the background of this image', 'image_editing');
    this.classifier.addDocument('Remove the object from this picture', 'image_editing');
    
    // Video generation
    this.classifier.addDocument('Create a video of', 'video_generation');
    this.classifier.addDocument('Generate an animation showing', 'video_generation');
    this.classifier.addDocument('Make a short clip of', 'video_generation');
    
    // Audio generation
    this.classifier.addDocument('Generate audio for', 'audio_generation');
    this.classifier.addDocument('Create a sound effect of', 'audio_generation');
    this.classifier.addDocument('Make a melody that', 'audio_generation');
    
    // Data analysis
    this.classifier.addDocument('Analyze this data', 'data_analysis');
    this.classifier.addDocument('Find patterns in', 'data_analysis');
    this.classifier.addDocument('What insights can you derive from', 'data_analysis');
    
    // Reasoning
    this.classifier.addDocument('Solve this problem', 'reasoning');
    this.classifier.addDocument('What is the logical conclusion', 'reasoning');
    this.classifier.addDocument('If A implies B and B implies C, what can we say about', 'reasoning');
    
    // Planning
    this.classifier.addDocument('Create a plan for', 'planning');
    this.classifier.addDocument('What steps should I take to', 'planning');
    this.classifier.addDocument('Develop a strategy for', 'planning');
    
    // Train the classifier
    this.classifier.train();
  }
  
  /**
   * Classify a task
   * @param {Object} task - Task details
   * @returns {string} Task type
   */
  classifyTask(task) {
    if (!this.initialized) {
      throw new Error('TaskClassifier is not initialized');
    }
    
    // Extract text from task
    let text = '';
    
    if (task.prompt) {
      text = task.prompt;
    } else if (task.messages) {
      // Extract from messages
      text = task.messages.map(msg => msg.content).join(' ');
    } else if (task.text) {
      text = task.text;
    } else {
      // Default to general conversation
      return 'general_conversation';
    }
    
    // Classify text
    const classification = this.classifier.classify(text);
    
    return classification;
  }
  
  /**
   * Get all task types
   * @returns {Array<string>} Task types
   */
  getAllTaskTypes() {
    return this.taskTypes;
  }
}

/**
 * PerformanceTracker class
 * Tracks model performance for different task types
 */
class PerformanceTracker {
  /**
   * Initialize the Performance Tracker
   * @param {number} maxSize - Maximum number of outcomes to track per model and task type
   */
  constructor(maxSize = 1000) {
    // Performance data
    // Structure: { modelId: { taskType: { scores: [], metrics: {} } } }
    this.performanceData = new Map();
    
    // Maximum size
    this.maxSize = maxSize;
  }
  
  /**
   * Record an outcome
   * @param {string} modelId - Model ID
   * @param {string} taskType - Task type
   * @param {number} score - Performance score (0-100)
   * @param {Object} metrics - Additional metrics
   */
  recordOutcome(modelId, taskType, score, metrics = {}) {
    // Get or create model data
    if (!this.performanceData.has(modelId)) {
      this.performanceData.set(modelId, new Map());
    }
    
    const modelData = this.performanceData.get(modelId);
    
    // Get or create task type data
    if (!modelData.has(taskType)) {
      modelData.set(taskType, {
        scores: [],
        metrics: {}
      });
    }
    
    const taskData = modelData.get(taskType);
    
    // Add score
    taskData.scores.push(score);
    
    // Trim scores if needed
    if (taskData.scores.length > this.maxSize) {
      taskData.scores = taskData.scores.slice(-this.maxSize);
    }
    
    // Update metrics
    for (const [key, value] of Object.entries(metrics)) {
      if (!taskData.metrics[key]) {
        taskData.metrics[key] = [];
      }
      
      taskData.metrics[key].push(value);
      
      // Trim metrics if needed
      if (taskData.metrics[key].length > this.maxSize) {
        taskData.metrics[key] = taskData.metrics[key].slice(-this.maxSize);
      }
    }
  }
  
  /**
   * Get average score for a model and task type
   * @param {string} modelId - Model ID
   * @param {string} taskType - Task type
   * @returns {number|null} Average score or null if no data
   */
  getAverageScore(modelId, taskType) {
    // Get model data
    const modelData = this.performanceData.get(modelId);
    
    if (!modelData) {
      return null;
    }
    
    // Get task type data
    const taskData = modelData.get(taskType);
    
    if (!taskData || taskData.scores.length === 0) {
      return null;
    }
    
    // Calculate average
    const sum = taskData.scores.reduce((a, b) => a + b, 0);
    return sum / taskData.scores.length;
  }
  
  /**
   * Get average metric for a model and task type
   * @param {string} modelId - Model ID
   * @param {string} taskType - Task type
   * @param {string} metricName - Metric name
   * @returns {number|null} Average metric or null if no data
   */
  getAverageMetric(modelId, taskType, metricName) {
    // Get model data
    const modelData = this.performanceData.get(modelId);
    
    if (!modelData) {
      return null;
    }
    
    // Get task type data
    const taskData = modelData.get(taskType);
    
    if (!taskData || !taskData.metrics[metricName] || taskData.metrics[metricName].length === 0) {
      return null;
    }
    
    // Calculate average
    const sum = taskData.metrics[metricName].reduce((a, b) => a + b, 0);
    return sum / taskData.metrics[metricName].length;
  }
  
  /**
   * Load performance data
   * @param {Object} data - Performance data
   */
  loadData(data) {
    // Convert plain object to Map structure
    this.performanceData = new Map();
    
    for (const [modelId, modelData] of Object.entries(data)) {
      const modelMap = new Map();
      
      for (const [taskType, taskData] of Object.entries(modelData)) {
        modelMap.set(taskType, taskData);
      }
      
      this.performanceData.set(modelId, modelMap);
    }
  }
  
  /**
   * Get performance data
   * @returns {Object} Performance data
   */
  getData() {
    // Convert Map structure to plain object
    const data = {};
    
    for (const [modelId, modelData] of this.performanceData.entries()) {
      data[modelId] = {};
      
      for (const [taskType, taskData] of modelData.entries()) {
        data[modelId][taskType] = taskData;
      }
    }
    
    return data;
  }
}

module.exports = {
  TaskAwareModelSelector,
  TaskClassifier,
  PerformanceTracker
};
