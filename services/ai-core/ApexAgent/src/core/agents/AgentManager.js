/**
 * Agent Manager for Aideon AI Lite
 * 
 * Manages the multi-agent architecture that powers Aideon AI Lite's autonomous capabilities.
 * Handles agent initialization, coordination, and communication.
 */

const EventEmitter = require('events');
const { v4: uuidv4 } = require('uuid');
const { PlannerAgent } = require('./PlannerAgent');
const { ExecutionAgent } = require('./ExecutionAgent');
const { VerificationAgent } = require('./VerificationAgent');
const { SecurityAgent } = require('./SecurityAgent');
const { OptimizationAgent } = require('./OptimizationAgent');
const { LearningAgent } = require('./LearningAgent');

class AgentManager extends EventEmitter {
  /**
   * Initialize the Agent Manager
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    super();
    
    this.core = core;
    this.logger = core.logManager.getLogger('agent-manager');
    this.config = core.configManager.getConfig().agents;
    
    this.agents = {};
    this.agentRegistry = {
      planner: PlannerAgent,
      execution: ExecutionAgent,
      verification: VerificationAgent,
      security: SecurityAgent,
      optimization: OptimizationAgent,
      learning: LearningAgent
    };
    
    this.logger.info('Agent Manager initialized');
  }
  
  /**
   * Initialize all configured agents
   * @returns {Promise<void>}
   */
  async initializeAgents() {
    this.logger.info('Initializing agents...');
    
    const agentPromises = [];
    
    // Create and initialize each agent based on configuration
    for (const [agentType, agentConfig] of Object.entries(this.config)) {
      if (agentConfig.enabled) {
        agentPromises.push(this._initializeAgent(agentType, agentConfig));
      } else {
        this.logger.info(`Agent ${agentType} is disabled in configuration`);
      }
    }
    
    await Promise.all(agentPromises);
    this.logger.info('All agents initialized successfully');
  }
  
  /**
   * Initialize a specific agent
   * @param {string} agentType - Type of agent to initialize
   * @param {Object} agentConfig - Agent configuration
   * @returns {Promise<void>}
   * @private
   */
  async _initializeAgent(agentType, agentConfig) {
    try {
      const AgentClass = this.agentRegistry[agentType];
      
      if (!AgentClass) {
        throw new Error(`Unknown agent type: ${agentType}`);
      }
      
      this.logger.info(`Initializing ${agentType} agent...`);
      
      const agent = new AgentClass(this.core, agentConfig);
      await agent.initialize();
      
      // Register agent event handlers
      agent.on('message', (message) => {
        this.emit('agent:message', agent.id, message);
      });
      
      agent.on('error', (error) => {
        this.logger.error(`Error in ${agentType} agent:`, error);
        this.emit('agent:error', agent.id, error);
      });
      
      // Store agent reference
      this.agents[agentType] = agent;
      
      this.logger.info(`${agentType} agent initialized successfully`);
    } catch (error) {
      this.logger.error(`Failed to initialize ${agentType} agent:`, error);
      throw error;
    }
  }
  
  /**
   * Get an agent by type
   * @param {string} agentType - Type of agent to retrieve
   * @returns {Object} Agent instance
   */
  getAgent(agentType) {
    const agent = this.agents[agentType];
    
    if (!agent) {
      throw new Error(`Agent ${agentType} not found or not initialized`);
    }
    
    return agent;
  }
  
  /**
   * Get status information for all agents
   * @returns {Object} Agent status information
   */
  getAgentStatus() {
    const status = {};
    
    for (const [agentType, agent] of Object.entries(this.agents)) {
      status[agentType] = {
        id: agent.id,
        type: agentType,
        name: agent.name,
        description: agent.description,
        status: agent.status,
        isActive: agent.isActive,
        taskCount: agent.taskCount,
        lastActivity: agent.lastActivity
      };
    }
    
    return status;
  }
  
  /**
   * Stop all agents
   * @returns {Promise<void>}
   */
  async stopAgents() {
    this.logger.info('Stopping all agents...');
    
    const stopPromises = Object.values(this.agents).map(agent => agent.shutdown());
    await Promise.all(stopPromises);
    
    this.logger.info('All agents stopped successfully');
  }
  
  /**
   * Coordinate a task across multiple agents
   * @param {Object} task - Task to coordinate
   * @returns {Promise<Object>} Task result
   */
  async coordinateTask(task) {
    this.logger.info(`Coordinating task ${task.id} across agents`);
    
    try {
      // 1. Planning phase with Planner Agent
      const plannerAgent = this.getAgent('planner');
      const plan = await plannerAgent.createPlan(task);
      
      // 2. Execution phase with Execution Agent
      const executionAgent = this.getAgent('execution');
      const executionResult = await executionAgent.executeTask(task, plan);
      
      // 3. Verification phase with Verification Agent
      const verificationAgent = this.getAgent('verification');
      const verificationResult = await verificationAgent.verifyResult(task, executionResult);
      
      // 4. If verification failed, retry or escalate
      if (!verificationResult.success) {
        this.logger.warn(`Task ${task.id} verification failed, retrying...`);
        return this.handleVerificationFailure(task, executionResult, verificationResult);
      }
      
      // 5. Optimization phase with Optimization Agent (async, doesn't block)
      const optimizationAgent = this.getAgent('optimization');
      optimizationAgent.optimizeExecution(task, executionResult, verificationResult)
        .catch(error => this.logger.error('Optimization error:', error));
      
      // 6. Learning phase with Learning Agent (async, doesn't block)
      const learningAgent = this.getAgent('learning');
      learningAgent.learnFromExecution(task, executionResult, verificationResult)
        .catch(error => this.logger.error('Learning error:', error));
      
      return {
        taskId: task.id,
        success: true,
        result: executionResult.result,
        verification: verificationResult,
        plan: plan
      };
    } catch (error) {
      this.logger.error(`Task coordination failed for task ${task.id}:`, error);
      throw error;
    }
  }
  
  /**
   * Handle verification failure for a task
   * @param {Object} task - Original task
   * @param {Object} executionResult - Execution result
   * @param {Object} verificationResult - Verification result
   * @returns {Promise<Object>} Updated task result
   * @private
   */
  async handleVerificationFailure(task, executionResult, verificationResult) {
    // If we've already retried too many times, escalate
    if (task.retryCount && task.retryCount >= this.config.maxRetries) {
      this.logger.warn(`Task ${task.id} exceeded max retries, escalating`);
      return {
        taskId: task.id,
        success: false,
        error: 'Max retries exceeded',
        verification: verificationResult,
        needsHumanIntervention: true
      };
    }
    
    // Increment retry count
    const updatedTask = {
      ...task,
      retryCount: (task.retryCount || 0) + 1
    };
    
    // Get planner to revise the plan based on verification feedback
    const plannerAgent = this.getAgent('planner');
    const revisedPlan = await plannerAgent.revisePlan(
      updatedTask, 
      executionResult, 
      verificationResult
    );
    
    // Re-execute with the revised plan
    const executionAgent = this.getAgent('execution');
    const newExecutionResult = await executionAgent.executeTask(updatedTask, revisedPlan);
    
    // Re-verify
    const verificationAgent = this.getAgent('verification');
    const newVerificationResult = await verificationAgent.verifyResult(
      updatedTask, 
      newExecutionResult
    );
    
    // If still failed, recurse (will eventually hit max retries)
    if (!newVerificationResult.success) {
      return this.handleVerificationFailure(
        updatedTask, 
        newExecutionResult, 
        newVerificationResult
      );
    }
    
    // Success on retry
    return {
      taskId: task.id,
      success: true,
      result: newExecutionResult.result,
      verification: newVerificationResult,
      plan: revisedPlan,
      retryCount: updatedTask.retryCount
    };
  }
}

module.exports = { AgentManager };
