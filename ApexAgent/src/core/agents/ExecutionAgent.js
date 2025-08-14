/**
 * ExecutionAgent.js
 * 
 * Execution agent for Aideon AI Lite.
 * Responsible for executing tasks and tool integrations across multiple domains.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const { v4: uuidv4 } = require('uuid');

class ExecutionAgent {
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger('agent:execution');
    this.events = new EventEmitter();
    this.activeExecutions = new Map();
    this.executionHistory = new Map();
    this.modelProvider = null;
    this.config = {
      defaultModel: 'gpt-4-turbo',
      maxRetries: 3,
      retryDelay: 1000,
      timeoutMs: 60000,
      maxConcurrentExecutions: 10,
      minConfidence: 0.85
    };
  }

  /**
   * Initialize the Execution Agent
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    this.logger.info('Initializing Execution Agent');
    
    try {
      // Load configuration
      const agentConfig = this.core.configManager.getConfig().agents?.execution || {};
      this.config = { ...this.config, ...agentConfig };
      
      // Initialize model provider
      this.modelProvider = await this.core.modelIntegrationFramework.getModelProvider(
        this.config.defaultModel
      );
      
      if (!this.modelProvider) {
        throw new Error(`Failed to initialize model provider for ${this.config.defaultModel}`);
      }
      
      this.logger.info('Execution Agent initialized successfully');
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Execution Agent: ${error.message}`, error);
      return false;
    }
  }

  /**
   * Execute a task step
   * @param {Object} task - Task object
   * @param {Object} step - Step to execute
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Execution result
   */
  async executeStep(task, step, options = {}) {
    this.logger.info(`Executing step ${step.id} for task ${task.id}`);
    
    try {
      const executionId = uuidv4();
      const startTime = Date.now();
      
      // Create execution record
      const execution = {
        id: executionId,
        taskId: task.id,
        stepId: step.id,
        status: 'executing',
        startTime,
        lastUpdated: startTime,
        result: null,
        error: null,
        metadata: {
          attempts: 0,
          retries: 0,
          tools: [],
          ...options.metadata
        }
      };
      
      // Store execution
      this.activeExecutions.set(executionId, execution);
      
      // Execute step
      const updatedExecution = await this._executeStepWithRetries(execution, task, step, options);
      
      // Update execution status
      updatedExecution.status = updatedExecution.error ? 'failed' : 'completed';
      updatedExecution.lastUpdated = Date.now();
      updatedExecution.duration = Date.now() - startTime;
      
      // Move to history
      this.executionHistory.set(executionId, updatedExecution);
      this.activeExecutions.delete(executionId);
      
      // Emit execution completed event
      this.events.emit('execution:completed', updatedExecution);
      
      if (updatedExecution.error) {
        throw new Error(updatedExecution.error);
      }
      
      return updatedExecution.result;
    } catch (error) {
      this.logger.error(`Failed to execute step ${step.id}: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Execute a tool
   * @param {string} toolId - Tool ID
   * @param {Object} params - Tool parameters
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Tool execution result
   */
  async executeTool(toolId, params, options = {}) {
    this.logger.info(`Executing tool ${toolId}`);
    
    try {
      // Get tool
      const tool = await this.core.toolManager.getTool(toolId);
      
      if (!tool) {
        throw new Error(`Tool not found: ${toolId}`);
      }
      
      // Validate parameters
      const validationResult = await tool.validate(params);
      
      if (!validationResult.valid) {
        throw new Error(`Invalid parameters for tool ${toolId}: ${validationResult.errors.join(', ')}`);
      }
      
      // Execute tool
      const result = await tool.execute(params);
      
      this.logger.info(`Tool ${toolId} executed successfully`);
      
      return result;
    } catch (error) {
      this.logger.error(`Failed to execute tool ${toolId}: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Get an execution by ID
   * @param {string} executionId - Execution ID
   * @returns {Object|null} Execution object or null if not found
   */
  getExecution(executionId) {
    // Check active executions
    if (this.activeExecutions.has(executionId)) {
      return this.activeExecutions.get(executionId);
    }
    
    // Check execution history
    if (this.executionHistory.has(executionId)) {
      return this.executionHistory.get(executionId);
    }
    
    return null;
  }

  /**
   * Get all active executions
   * @returns {Array<Object>} Array of active executions
   */
  getActiveExecutions() {
    return Array.from(this.activeExecutions.values());
  }

  /**
   * Cancel an execution
   * @param {string} executionId - Execution ID
   * @param {string} reason - Cancellation reason
   * @returns {Object} Cancelled execution
   */
  cancelExecution(executionId, reason = 'User requested cancellation') {
    if (!this.activeExecutions.has(executionId)) {
      throw new Error(`Execution not found: ${executionId}`);
    }
    
    const execution = this.activeExecutions.get(executionId);
    
    // Update execution status
    execution.status = 'cancelled';
    execution.cancelledAt = Date.now();
    execution.cancellationReason = reason;
    
    // Move to history
    this.executionHistory.set(executionId, execution);
    this.activeExecutions.delete(executionId);
    
    // Emit execution cancelled event
    this.events.emit('execution:cancelled', execution);
    
    return execution;
  }

  /**
   * Register an event listener
   * @param {string} event - Event name
   * @param {Function} listener - Event listener
   */
  on(event, listener) {
    this.events.on(event, listener);
  }

  /**
   * Remove an event listener
   * @param {string} event - Event name
   * @param {Function} listener - Event listener
   */
  off(event, listener) {
    this.events.off(event, listener);
  }

  /**
   * Execute a step with retries
   * @param {Object} execution - Execution object
   * @param {Object} task - Task object
   * @param {Object} step - Step to execute
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Updated execution
   * @private
   */
  async _executeStepWithRetries(execution, task, step, options = {}) {
    const maxRetries = options.maxRetries || this.config.maxRetries;
    const retryDelay = options.retryDelay || this.config.retryDelay;
    
    let attempts = 0;
    let success = false;
    let result = null;
    let error = null;
    
    while (attempts <= maxRetries && !success) {
      attempts++;
      execution.metadata.attempts = attempts;
      
      try {
        // Determine execution strategy
        const strategy = await this._determineExecutionStrategy(task, step);
        
        // Execute step based on strategy
        switch (strategy.type) {
          case 'tool':
            result = await this._executeToolStrategy(strategy, task, step);
            break;
          case 'sequence':
            result = await this._executeSequenceStrategy(strategy, task, step);
            break;
          case 'parallel':
            result = await this._executeParallelStrategy(strategy, task, step);
            break;
          case 'conditional':
            result = await this._executeConditionalStrategy(strategy, task, step);
            break;
          default:
            throw new Error(`Unknown execution strategy: ${strategy.type}`);
        }
        
        success = true;
      } catch (err) {
        this.logger.error(`Execution attempt ${attempts} failed: ${err.message}`);
        error = err;
        execution.metadata.retries = attempts - 1;
        
        // Wait before retrying
        if (attempts <= maxRetries) {
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
      }
    }
    
    // Update execution
    execution.result = result;
    execution.error = success ? null : error.message;
    
    return execution;
  }

  /**
   * Determine execution strategy for a step
   * @param {Object} task - Task object
   * @param {Object} step - Step to execute
   * @returns {Promise<Object>} Execution strategy
   * @private
   */
  async _determineExecutionStrategy(task, step) {
    // In a real implementation, this would analyze the step and determine the best strategy
    // For now, we'll use a simplified approach
    
    // Check if step specifies a tool
    if (step.tool) {
      return {
        type: 'tool',
        toolId: step.tool,
        params: step.params || {}
      };
    }
    
    // Check if step specifies a sequence of tools
    if (step.sequence) {
      return {
        type: 'sequence',
        steps: step.sequence
      };
    }
    
    // Check if step specifies parallel tools
    if (step.parallel) {
      return {
        type: 'parallel',
        steps: step.parallel
      };
    }
    
    // Check if step specifies conditional execution
    if (step.condition) {
      return {
        type: 'conditional',
        condition: step.condition,
        ifTrue: step.ifTrue,
        ifFalse: step.ifFalse
      };
    }
    
    // Default to using the step description to determine the tool
    return {
      type: 'tool',
      toolId: 'default',
      params: {
        description: step.description,
        context: task
      }
    };
  }

  /**
   * Execute a tool strategy
   * @param {Object} strategy - Tool strategy
   * @param {Object} task - Task object
   * @param {Object} step - Step to execute
   * @returns {Promise<Object>} Execution result
   * @private
   */
  async _executeToolStrategy(strategy, task, step) {
    return this.executeTool(strategy.toolId, strategy.params);
  }

  /**
   * Execute a sequence strategy
   * @param {Object} strategy - Sequence strategy
   * @param {Object} task - Task object
   * @param {Object} step - Step to execute
   * @returns {Promise<Array<Object>>} Execution results
   * @private
   */
  async _executeSequenceStrategy(strategy, task, step) {
    const results = [];
    
    for (const subStep of strategy.steps) {
      const result = await this.executeStep(task, subStep);
      results.push(result);
    }
    
    return results;
  }

  /**
   * Execute a parallel strategy
   * @param {Object} strategy - Parallel strategy
   * @param {Object} task - Task object
   * @param {Object} step - Step to execute
   * @returns {Promise<Array<Object>>} Execution results
   * @private
   */
  async _executeParallelStrategy(strategy, task, step) {
    const promises = strategy.steps.map(subStep => this.executeStep(task, subStep));
    return Promise.all(promises);
  }

  /**
   * Execute a conditional strategy
   * @param {Object} strategy - Conditional strategy
   * @param {Object} task - Task object
   * @param {Object} step - Step to execute
   * @returns {Promise<Object>} Execution result
   * @private
   */
  async _executeConditionalStrategy(strategy, task, step) {
    // Evaluate condition
    const conditionResult = await this._evaluateCondition(strategy.condition, task);
    
    // Execute branch based on condition
    if (conditionResult) {
      return this.executeStep(task, strategy.ifTrue);
    } else {
      return this.executeStep(task, strategy.ifFalse);
    }
  }

  /**
   * Evaluate a condition
   * @param {Object} condition - Condition to evaluate
   * @param {Object} task - Task object
   * @returns {Promise<boolean>} Condition result
   * @private
   */
  async _evaluateCondition(condition, task) {
    // In a real implementation, this would evaluate complex conditions
    // For now, we'll use a simplified approach
    
    if (typeof condition === 'boolean') {
      return condition;
    }
    
    if (typeof condition === 'function') {
      return condition(task);
    }
    
    if (condition.type === 'equals') {
      return condition.left === condition.right;
    }
    
    if (condition.type === 'contains') {
      return condition.haystack.includes(condition.needle);
    }
    
    if (condition.type === 'tool') {
      const result = await this.executeTool(condition.toolId, condition.params);
      return !!result;
    }
    
    return false;
  }
}

module.exports = ExecutionAgent;
