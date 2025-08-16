/**
 * Aideon AI Lite - Core Engine
 * The world's first truly hybrid, fully autonomous general intelligence AI system
 * 
 * This is the main core engine that orchestrates the multi-agent architecture
 * and provides the foundation for all Aideon AI Lite capabilities.
 */

const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');
const { v4: uuidv4 } = require('uuid');
const { AgentManager } = require('./agents/AgentManager');
const { TaskManager } = require('./tasks/TaskManager');
const { MemoryManager } = require('./memory/MemoryManager');
const { ToolManager } = require('./tools/ToolManager');
const { ConfigManager } = require('./config/ConfigManager');
const { LogManager } = require('./utils/LogManager');
const { SecurityManager } = require('./security/SecurityManager');
const { APIManager } = require('./api/APIManager');
const { LocalProcessingManager } = require('./processing/LocalProcessingManager');
const { CloudProcessingManager } = require('./processing/CloudProcessingManager');

class AideonCore extends EventEmitter {
  /**
   * Initialize the Aideon AI Lite core system
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    super();
    
    this.id = uuidv4();
    this.startTime = new Date();
    this.isRunning = false;
    this.isInitialized = false;
    
    // Initialize configuration
    this.configManager = new ConfigManager(options.configPath);
    
    // Set default configuration if not initialized yet
    this.config = {
      version: '1.0.0',
      system: {
        name: 'Aideon AI Lite',
        description: 'Intelligence Everywhere, Limits Nowhere',
        logLevel: 'info'
      },
      memory: {
        persistencePath: path.join(process.cwd(), 'data', 'memory'),
        autoSave: true,
        autoSaveInterval: 60000,
        maxHistoryLength: 1000
      },
      tools: {
        toolsPath: path.join(process.cwd(), 'tools'),
        customToolsPath: path.join(process.cwd(), 'custom_tools')
      },
      tasks: {
        maxConcurrentTasks: 5,
        taskTimeout: 300000,
        retryLimit: 3
      },
      security: {
        encryption: {
          enabled: true,
          algorithm: 'aes-256-gcm'
        },
        authentication: {
          enabled: true,
          method: 'jwt',
          tokenExpiration: '24h'
        }
      },
      api: {
        enabled: true,
        port: 3000,
        host: 'localhost'
      },
      logging: {
        console: {
          enabled: true,
          level: 'info'
        },
        file: {
          enabled: true,
          level: 'debug',
          path: path.join(process.cwd(), 'logs')
        }
      },
      processing: {
        local: {
          enabled: true,
          maxConcurrency: 4
        },
        cloud: {
          enabled: true,
          apiEndpoint: process.env.CLOUD_API_ENDPOINT || 'https://api.aideon.ai'
        }
      }
    };
    
    // Try to get config from ConfigManager if available
    try {
      if (this.configManager.getConfig) {
        const managerConfig = this.configManager.getConfig();
        if (managerConfig) {
          this.config = managerConfig;
        }
      }
    } catch (error) {
      console.warn('Could not load configuration from ConfigManager, using defaults');
    }
    
    // Initialize logging
    this.logManager = new LogManager(this.config.logging || {});
    this.logger = this.logManager.getLogger('core');
    
    this.logger.info(`Initializing Aideon AI Lite v${this.config.version}`);
    this.logger.info('Intelligence Everywhere, Limits Nowhere');
    
    // Initialize core components with proper configuration
    this.securityManager = new SecurityManager(this.config.security || {});
    this.memoryManager = new MemoryManager(this.config.memory || {});
    this.toolManager = new ToolManager(this.config.tools || {});
    this.taskManager = new TaskManager(this.config.tasks || {});
    
    // Initialize processing managers
    this.localProcessingManager = new LocalProcessingManager(this.config.processing?.local || {});
    this.cloudProcessingManager = new CloudProcessingManager(this.config.processing?.cloud || {});
    
    // Initialize API manager
    this.apiManager = new APIManager(this.config.api || {});
    
    // Initialize agent manager and agents
    this.agentManager = new AgentManager(this);
    
    // Register event listeners
    this._registerEventListeners();
    
    this.logger.info('Core components initialized');
  }
  
  /**
   * Initialize the Aideon AI Lite system
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    if (this.isInitialized) {
      this.logger.warn('Aideon AI Lite is already initialized');
      return true;
    }
    
    try {
      this.logger.info('Initializing Aideon AI Lite components...');
      
      // Initialize configuration
      await this.configManager.initialize();
      
      // Initialize memory systems
      await this.memoryManager.initialize();
      
      // Initialize security
      await this.securityManager.performStartupChecks();
      
      // Initialize tools
      await this.toolManager.initialize();
      
      // Initialize API connections
      await this.apiManager.initialize();
      
      // Initialize processing systems
      await this.localProcessingManager.initialize();
      await this.cloudProcessingManager.initialize();
      
      this.isInitialized = true;
      
      this.emit('system:initialized');
      this.logger.info('Aideon AI Lite initialized successfully');
      
      return true;
    } catch (error) {
      this.logger.error('Failed to initialize Aideon AI Lite', error);
      this.emit('system:error', error);
      return false;
    }
  }
  
  /**
   * Start the Aideon AI Lite system
   * @returns {Promise<boolean>} Success status
   */
  async start() {
    if (this.isRunning) {
      this.logger.warn('Aideon AI Lite is already running');
      return true;
    }
    
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    try {
      this.logger.info('Starting Aideon AI Lite...');
      
      // Initialize agents
      await this.agentManager.initializeAgents();
      
      // Initialize task manager
      await this.taskManager.initialize();
      
      this.isRunning = true;
      
      this.emit('system:started');
      this.logger.info('Aideon AI Lite started successfully');
      
      return true;
    } catch (error) {
      this.logger.error('Failed to start Aideon AI Lite', error);
      this.emit('system:error', error);
      return false;
    }
  }
  
  /**
   * Stop the Aideon AI Lite system
   * @returns {Promise<boolean>} Success status
   */
  async stop() {
    if (!this.isRunning) {
      this.logger.warn('Aideon AI Lite is not running');
      return true;
    }
    
    try {
      this.logger.info('Stopping Aideon AI Lite...');
      
      // Stop task processing
      await this.taskManager.stopAllTasks();
      
      // Stop agents
      await this.agentManager.stopAgents();
      
      // Stop processing systems
      await this.cloudProcessingManager.shutdown();
      await this.localProcessingManager.shutdown();
      
      // Close API connections
      await this.apiManager.shutdown();
      
      // Release tools
      await this.toolManager.shutdown();
      
      // Persist memory
      await this.memoryManager.persistMemory();
      
      this.isRunning = false;
      
      this.emit('system:stopped');
      this.logger.info('Aideon AI Lite stopped successfully');
      
      return true;
    } catch (error) {
      this.logger.error('Failed to stop Aideon AI Lite', error);
      this.emit('system:error', error);
      return false;
    }
  }
  
  /**
   * Process a task using the multi-agent system
   * @param {string|Object} task - Task description or task object
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} Task result
   */
  async processTask(task, options = {}) {
    if (!this.isRunning) {
      throw new Error('Aideon AI Lite is not running');
    }
    
    try {
      // Create task object if string was provided
      const taskObj = typeof task === 'string' 
        ? { description: task, type: 'general' } 
        : task;
      
      // Add task metadata
      taskObj.id = taskObj.id || uuidv4();
      taskObj.createdAt = taskObj.createdAt || new Date();
      taskObj.options = { ...options, ...taskObj.options };
      
      this.logger.info(`Processing task: ${taskObj.id}`, { 
        description: taskObj.description,
        type: taskObj.type
      });
      
      // Submit task to task manager
      const result = await this.taskManager.submitTask(taskObj);
      
      this.logger.info(`Task completed: ${taskObj.id}`);
      return result;
    } catch (error) {
      this.logger.error(`Task processing failed: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Get system status information
   * @returns {Object} System status
   */
  getStatus() {
    const uptime = new Date() - this.startTime;
    
    return {
      id: this.id,
      version: this.config.version,
      isRunning: this.isRunning,
      uptime: uptime,
      startTime: this.startTime,
      agents: this.agentManager.getAgentStatus(),
      tasks: this.taskManager.getTaskStats(),
      memory: this.memoryManager.getMemoryStats(),
      processing: {
        local: this.localProcessingManager.getStatus(),
        cloud: this.cloudProcessingManager.getStatus()
      },
      security: this.securityManager.getStatus()
    };
  }
  
  /**
   * Register event listeners for internal components
   * @private
   */
  _registerEventListeners() {
    // Task events
    this.taskManager.on('task:created', (task) => {
      this.emit('task:created', task);
    });
    
    this.taskManager.on('task:started', (task) => {
      this.emit('task:started', task);
    });
    
    this.taskManager.on('task:completed', (task, result) => {
      this.emit('task:completed', task, result);
    });
    
    this.taskManager.on('task:failed', (task, error) => {
      this.emit('task:failed', task, error);
    });
    
    // Agent events
    this.agentManager.on('agent:message', (agentId, message) => {
      this.emit('agent:message', agentId, message);
    });
    
    // Security events
    this.securityManager.on('security:threat', (threat) => {
      this.logger.warn('Security threat detected', threat);
      this.emit('security:threat', threat);
    });
    
    // API events
    this.apiManager.on('api:error', (error) => {
      this.logger.error('API error', error);
      this.emit('api:error', error);
    });
  }
}

module.exports = { AideonCore };
