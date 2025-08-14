/**
 * PlannerAgent.js
 * 
 * Advanced reasoning and task decomposition agent for Aideon AI Lite.
 * Responsible for breaking down complex tasks into manageable steps and creating execution plans.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const { v4: uuidv4 } = require('uuid');

class PlannerAgent {
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger('agent:planner');
    this.events = new EventEmitter();
    this.activePlans = new Map();
    this.planHistory = new Map();
    this.modelProvider = null;
    this.config = {
      defaultModel: 'gpt-4-turbo',
      maxPlanningAttempts: 3,
      planRevisionThreshold: 0.7,
      contextWindow: 16000,
      maxSteps: 20,
      minConfidence: 0.85
    };
  }

  /**
   * Initialize the Planner Agent
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    this.logger.info('Initializing Planner Agent');
    
    try {
      // Load configuration
      const agentConfig = this.core.configManager.getConfig().agents?.planner || {};
      this.config = { ...this.config, ...agentConfig };
      
      // Initialize model provider
      this.modelProvider = await this.core.modelIntegrationFramework.getModelProvider(
        this.config.defaultModel
      );
      
      if (!this.modelProvider) {
        throw new Error(`Failed to initialize model provider for ${this.config.defaultModel}`);
      }
      
      this.logger.info('Planner Agent initialized successfully');
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Planner Agent: ${error.message}`, error);
      return false;
    }
  }

  /**
   * Create a plan for a task
   * @param {Object} task - Task to plan for
   * @param {Object} options - Planning options
   * @returns {Promise<Object>} Plan object
   */
  async createPlan(task, options = {}) {
    this.logger.info(`Creating plan for task: ${task.id}`);
    
    try {
      const planId = uuidv4();
      const startTime = Date.now();
      
      // Create initial plan
      const plan = {
        id: planId,
        taskId: task.id,
        status: 'planning',
        steps: [],
        currentStep: 0,
        startTime,
        lastUpdated: startTime,
        metadata: {
          attempts: 0,
          confidence: 0,
          model: this.config.defaultModel,
          ...options.metadata
        }
      };
      
      // Store plan
      this.activePlans.set(planId, plan);
      
      // Generate plan steps
      const updatedPlan = await this._generatePlanSteps(plan, task, options);
      
      // Update plan status
      updatedPlan.status = 'ready';
      updatedPlan.lastUpdated = Date.now();
      
      this.logger.info(`Plan created for task ${task.id}: ${updatedPlan.steps.length} steps`);
      
      // Emit plan created event
      this.events.emit('plan:created', updatedPlan);
      
      return updatedPlan;
    } catch (error) {
      this.logger.error(`Failed to create plan: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Get a plan by ID
   * @param {string} planId - Plan ID
   * @returns {Object|null} Plan object or null if not found
   */
  getPlan(planId) {
    // Check active plans
    if (this.activePlans.has(planId)) {
      return this.activePlans.get(planId);
    }
    
    // Check plan history
    if (this.planHistory.has(planId)) {
      return this.planHistory.get(planId);
    }
    
    return null;
  }

  /**
   * Get all active plans
   * @returns {Array<Object>} Array of active plans
   */
  getActivePlans() {
    return Array.from(this.activePlans.values());
  }

  /**
   * Update a plan
   * @param {string} planId - Plan ID
   * @param {Object} updates - Plan updates
   * @returns {Object} Updated plan
   */
  updatePlan(planId, updates) {
    if (!this.activePlans.has(planId)) {
      throw new Error(`Plan not found: ${planId}`);
    }
    
    const plan = this.activePlans.get(planId);
    const updatedPlan = { ...plan, ...updates, lastUpdated: Date.now() };
    
    this.activePlans.set(planId, updatedPlan);
    
    // Emit plan updated event
    this.events.emit('plan:updated', updatedPlan);
    
    return updatedPlan;
  }

  /**
   * Advance to the next step in a plan
   * @param {string} planId - Plan ID
   * @param {Object} stepResult - Result of the current step
   * @returns {Object} Updated plan
   */
  advancePlan(planId, stepResult = {}) {
    if (!this.activePlans.has(planId)) {
      throw new Error(`Plan not found: ${planId}`);
    }
    
    const plan = this.activePlans.get(planId);
    
    // Update current step result
    if (plan.steps[plan.currentStep]) {
      plan.steps[plan.currentStep].result = stepResult;
      plan.steps[plan.currentStep].completed = true;
      plan.steps[plan.currentStep].completedAt = Date.now();
    }
    
    // Advance to next step
    const nextStep = plan.currentStep + 1;
    
    // Check if plan is complete
    if (nextStep >= plan.steps.length) {
      plan.status = 'completed';
      plan.completedAt = Date.now();
      
      // Move to history
      this.planHistory.set(planId, plan);
      this.activePlans.delete(planId);
      
      // Emit plan completed event
      this.events.emit('plan:completed', plan);
    } else {
      plan.currentStep = nextStep;
      plan.lastUpdated = Date.now();
      
      // Emit plan advanced event
      this.events.emit('plan:advanced', plan);
    }
    
    return plan;
  }

  /**
   * Revise a plan based on new information or changed requirements
   * @param {string} planId - Plan ID
   * @param {Object} task - Updated task
   * @param {Object} options - Revision options
   * @returns {Promise<Object>} Revised plan
   */
  async revisePlan(planId, task, options = {}) {
    if (!this.activePlans.has(planId)) {
      throw new Error(`Plan not found: ${planId}`);
    }
    
    const plan = this.activePlans.get(planId);
    
    this.logger.info(`Revising plan ${planId} for task ${task.id}`);
    
    try {
      // Create revision
      const revision = {
        originalPlanId: planId,
        timestamp: Date.now(),
        reason: options.reason || 'Task requirements changed'
      };
      
      // Generate new plan steps
      const revisedPlan = await this._generatePlanSteps(plan, task, {
        ...options,
        revision
      });
      
      // Update plan
      revisedPlan.status = 'ready';
      revisedPlan.lastUpdated = Date.now();
      revisedPlan.revisions = [...(plan.revisions || []), revision];
      
      // Replace active plan
      this.activePlans.set(planId, revisedPlan);
      
      this.logger.info(`Plan ${planId} revised: ${revisedPlan.steps.length} steps`);
      
      // Emit plan revised event
      this.events.emit('plan:revised', revisedPlan);
      
      return revisedPlan;
    } catch (error) {
      this.logger.error(`Failed to revise plan: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Cancel a plan
   * @param {string} planId - Plan ID
   * @param {string} reason - Cancellation reason
   * @returns {Object} Cancelled plan
   */
  cancelPlan(planId, reason = 'User requested cancellation') {
    if (!this.activePlans.has(planId)) {
      throw new Error(`Plan not found: ${planId}`);
    }
    
    const plan = this.activePlans.get(planId);
    
    // Update plan status
    plan.status = 'cancelled';
    plan.cancelledAt = Date.now();
    plan.cancellationReason = reason;
    
    // Move to history
    this.planHistory.set(planId, plan);
    this.activePlans.delete(planId);
    
    // Emit plan cancelled event
    this.events.emit('plan:cancelled', plan);
    
    return plan;
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
   * Generate plan steps for a task
   * @param {Object} plan - Plan object
   * @param {Object} task - Task object
   * @param {Object} options - Generation options
   * @returns {Promise<Object>} Updated plan with steps
   * @private
   */
  async _generatePlanSteps(plan, task, options = {}) {
    const maxAttempts = options.maxAttempts || this.config.maxPlanningAttempts;
    let attempts = 0;
    let success = false;
    let error = null;
    
    while (attempts < maxAttempts && !success) {
      attempts++;
      plan.metadata.attempts = attempts;
      
      try {
        // Prepare planning prompt
        const prompt = this._preparePlanningPrompt(task, plan, options);
        
        // Call model to generate plan
        const response = await this.modelProvider.generateText({
          prompt,
          maxTokens: 2000,
          temperature: 0.2,
          topP: 0.8,
          stopSequences: ['END_OF_PLAN']
        });
        
        // Parse plan steps
        const steps = this._parsePlanSteps(response.text);
        
        if (steps.length === 0) {
          throw new Error('Failed to generate valid plan steps');
        }
        
        if (steps.length > this.config.maxSteps) {
          this.logger.warn(`Generated plan has ${steps.length} steps, which exceeds the maximum of ${this.config.maxSteps}. Truncating.`);
          steps.length = this.config.maxSteps;
        }
        
        // Update plan with steps
        plan.steps = steps;
        plan.metadata.confidence = response.metadata?.confidence || 0.9;
        
        success = true;
      } catch (err) {
        this.logger.error(`Plan generation attempt ${attempts} failed: ${err.message}`);
        error = err;
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    if (!success) {
      throw new Error(`Failed to generate plan after ${attempts} attempts: ${error.message}`);
    }
    
    return plan;
  }

  /**
   * Prepare planning prompt for the model
   * @param {Object} task - Task object
   * @param {Object} plan - Plan object
   * @param {Object} options - Planning options
   * @returns {string} Planning prompt
   * @private
   */
  _preparePlanningPrompt(task, plan, options = {}) {
    // In a real implementation, this would construct a detailed prompt
    // For now, we'll use a simplified version
    
    let prompt = `
You are the Planner Agent for Aideon AI Lite, an advanced autonomous AI system.
Your task is to create a detailed step-by-step plan for the following task:

TASK ID: ${task.id}
TASK TITLE: ${task.title}
TASK DESCRIPTION: ${task.description}

REQUIREMENTS:
${task.requirements || 'No specific requirements provided.'}

CONSTRAINTS:
${task.constraints || 'No specific constraints provided.'}

Please create a numbered list of steps to complete this task. Each step should be clear, actionable, and specific.
Format your response as follows:

PLAN:
1. [First step description]
2. [Second step description]
3. [Third step description]
...
END_OF_PLAN

`;

    // Add context from previous steps if this is a revision
    if (options.revision && plan.steps.length > 0) {
      prompt += `\nPREVIOUS PLAN STEPS:\n`;
      plan.steps.forEach((step, index) => {
        prompt += `${index + 1}. ${step.description}\n`;
      });
      
      prompt += `\nREVISION REASON: ${options.revision.reason}\n`;
    }
    
    // Add any additional context
    if (options.additionalContext) {
      prompt += `\nADDITIONAL CONTEXT:\n${options.additionalContext}\n`;
    }
    
    return prompt;
  }

  /**
   * Parse plan steps from model response
   * @param {string} response - Model response text
   * @returns {Array<Object>} Array of plan steps
   * @private
   */
  _parsePlanSteps(response) {
    try {
      // Extract plan section
      const planMatch = response.match(/PLAN:([\s\S]*?)END_OF_PLAN/);
      
      if (!planMatch) {
        throw new Error('Plan section not found in response');
      }
      
      const planText = planMatch[1].trim();
      
      // Parse numbered steps
      const stepRegex = /(\d+)\.\s+(.+?)(?=\n\d+\.|\n*$)/gs;
      const steps = [];
      let match;
      
      while ((match = stepRegex.exec(planText)) !== null) {
        const stepNumber = parseInt(match[1], 10);
        const description = match[2].trim();
        
        steps.push({
          id: `step_${stepNumber}`,
          number: stepNumber,
          description,
          completed: false,
          result: null
        });
      }
      
      // Ensure steps are in correct order
      steps.sort((a, b) => a.number - b.number);
      
      return steps;
    } catch (error) {
      this.logger.error(`Failed to parse plan steps: ${error.message}`);
      return [];
    }
  }
}

module.exports = PlannerAgent;
