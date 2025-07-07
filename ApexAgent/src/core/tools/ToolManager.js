/**
 * ToolManager.js
 * 
 * Core system for managing and orchestrating all tools in Aideon AI Lite.
 * Provides a unified interface for tool discovery, registration, execution,
 * validation, and monitoring across all supported domains.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');

// Import domain-specific tool providers
const { SoftwareDevelopmentTools } = require('./domains/SoftwareDevelopmentTools');
const { DataScienceTools } = require('./domains/DataScienceTools');
const { BusinessFinanceTools } = require('./domains/BusinessFinanceTools');
const { HealthcareTools } = require('./domains/HealthcareTools');
const { LegalTools } = require('./domains/LegalTools');
const { CreativeDesignTools } = require('./domains/CreativeDesignTools');
const { ContentCommunicationTools } = require('./domains/ContentCommunicationTools');
const { EngineeringTools } = require('./domains/EngineeringTools');
const { EducationResearchTools } = require('./domains/EducationResearchTools');
const { MarketingSalesTools } = require('./domains/MarketingSalesTools');
const { ProjectManagementTools } = require('./domains/ProjectManagementTools');
const { ScienceResearchTools } = require('./domains/ScienceResearchTools');
const { AgricultureEnvironmentalTools } = require('./domains/AgricultureEnvironmentalTools');
const { ArchitectureConstructionTools } = require('./domains/ArchitectureConstructionTools');
const { EnergyUtilitiesTools } = require('./domains/EnergyUtilitiesTools');

/**
 * ToolManager class for managing all tools in Aideon AI Lite
 */
class ToolManager extends EventEmitter {
  /**
   * Create a new ToolManager instance
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    super();
    
    this.config = config;
    this.options = {
      toolsDir: config.toolsPath || path.join(process.cwd(), 'src', 'core', 'tools'),
      cacheResults: config.cacheResults !== undefined ? config.cacheResults : true,
      validateResults: config.validateResults !== undefined ? config.validateResults : true,
      maxConcurrentExecutions: config.maxConcurrentExecutions || 10,
      defaultTimeout: config.defaultTimeout || 30000, // 30 seconds
      ...config
    };
    
    // Initialize tool registry
    this.registry = new Map();
    
    // Initialize domain providers
    this.domainProviders = new Map();
    
    // Initialize execution tracking
    this.executions = new Map();
    this.activeExecutions = 0;
    
    // Initialize result cache
    this.resultCache = new Map();
    
    // Initialize metrics
    this.metrics = {
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      averageExecutionTime: 0,
      domainUsage: new Map(),
      toolUsage: new Map()
    };
    
    console.log('ToolManager initialized');
  }
  
  /**
   * Initialize the ToolManager
   * @returns {Promise<void>}
   */
  async initialize() {
    try {
      console.log('Initializing ToolManager');
      
      // Initialize domain providers
      await this._initializeDomainProviders();
      
      // Discover and register all tools
      await this._discoverAndRegisterTools();
      
      // Initialize safety guardrails
      await this._initializeSafetyGuardrails();
      
      console.log(`ToolManager initialized with ${this.registry.size} tools across ${this.domainProviders.size} domains`);
      
      // Emit initialization complete event
      this.emit('initialized', {
        toolCount: this.registry.size,
        domainCount: this.domainProviders.size
      });
      
      return true;
    } catch (error) {
      console.error('Error initializing ToolManager:', error);
      throw error;
    }
  }
  
  /**
   * Initialize domain providers
   * @private
   * @returns {Promise<void>}
   */
  async _initializeDomainProviders() {
    try {
      console.log('Initializing domain providers');
      
      // Register all domain providers
      this.domainProviders.set('software_development', new SoftwareDevelopmentTools());
      this.domainProviders.set('data_science', new DataScienceTools());
      this.domainProviders.set('business_finance', new BusinessFinanceTools());
      this.domainProviders.set('healthcare', new HealthcareTools());
      this.domainProviders.set('legal', new LegalTools());
      this.domainProviders.set('creative_design', new CreativeDesignTools());
      this.domainProviders.set('content_communication', new ContentCommunicationTools());
      this.domainProviders.set('engineering', new EngineeringTools());
      this.domainProviders.set('education_research', new EducationResearchTools());
      this.domainProviders.set('marketing_sales', new MarketingSalesTools());
      this.domainProviders.set('project_management', new ProjectManagementTools());
      this.domainProviders.set('science_research', new ScienceResearchTools());
      this.domainProviders.set('agriculture_environmental', new AgricultureEnvironmentalTools());
      this.domainProviders.set('architecture_construction', new ArchitectureConstructionTools());
      this.domainProviders.set('energy_utilities', new EnergyUtilitiesTools());
      
      // Initialize each domain provider
      const initPromises = [];
      for (const [domain, provider] of this.domainProviders.entries()) {
        initPromises.push(
          provider.initialize()
            .then(() => {
              console.log(`Domain provider initialized: ${domain}`);
            })
            .catch(error => {
              console.error(`Error initializing domain provider ${domain}:`, error);
              throw error;
            })
        );
      }
      
      await Promise.all(initPromises);
      
      console.log('All domain providers initialized');
    } catch (error) {
      console.error('Error initializing domain providers:', error);
      throw error;
    }
  }
  
  /**
   * Discover and register all tools
   * @private
   * @returns {Promise<void>}
   */
  async _discoverAndRegisterTools() {
    try {
      console.log('Discovering and registering tools');
      
      // Register tools from each domain provider
      for (const [domain, provider] of this.domainProviders.entries()) {
        const tools = await provider.getTools();
        
        for (const tool of tools) {
          await this.registerTool(tool, domain);
        }
        
        console.log(`Registered ${tools.length} tools from domain: ${domain}`);
      }
      
      console.log(`Total tools registered: ${this.registry.size}`);
    } catch (error) {
      console.error('Error discovering and registering tools:', error);
      throw error;
    }
  }
  
  /**
   * Initialize safety guardrails
   * @private
   * @returns {Promise<void>}
   */
  async _initializeSafetyGuardrails() {
    try {
      console.log('Initializing safety guardrails');
      
      // Load safety configuration
      const safetyConfig = this.config.safety || {};
      
      // Initialize safety guardrails
      this.safetyGuardrails = {
        requireApprovalFor: new Set(safetyConfig.requireApprovalFor || [
          'system_modification',
          'data_deletion',
          'external_communication',
          'payment_processing',
          'credential_access'
        ]),
        blacklistedOperations: new Set(safetyConfig.blacklistedOperations || [
          'format_disk',
          'delete_system_files',
          'modify_network_config',
          'disable_security'
        ]),
        riskThresholds: safetyConfig.riskThresholds || {
          low: 0.3,
          medium: 0.6,
          high: 0.8
        },
        maxConsecutiveFailures: safetyConfig.maxConsecutiveFailures || 3,
        cooldownPeriod: safetyConfig.cooldownPeriod || 60000, // 1 minute
        ...safetyConfig
      };
      
      console.log('Safety guardrails initialized');
    } catch (error) {
      console.error('Error initializing safety guardrails:', error);
      throw error;
    }
  }
  
  /**
   * Register a tool with the ToolManager
   * @param {Object} tool - Tool definition
   * @param {string} domain - Domain the tool belongs to
   * @returns {Promise<boolean>} - True if registration was successful
   */
  async registerTool(tool, domain) {
    try {
      if (!tool || !tool.id || !tool.name || !tool.execute) {
        throw new Error('Invalid tool definition');
      }
      
      if (this.registry.has(tool.id)) {
        console.warn(`Tool with ID ${tool.id} is already registered`);
        return false;
      }
      
      // Add domain information to the tool
      tool.domain = domain;
      
      // Register the tool
      this.registry.set(tool.id, tool);
      
      // Initialize metrics for this tool
      if (!this.metrics.toolUsage.has(tool.id)) {
        this.metrics.toolUsage.set(tool.id, {
          executions: 0,
          successRate: 0,
          averageExecutionTime: 0,
          lastExecuted: null
        });
      }
      
      console.log(`Registered tool: ${tool.name} (${tool.id}) in domain: ${domain}`);
      
      // Emit tool registered event
      this.emit('tool-registered', {
        toolId: tool.id,
        toolName: tool.name,
        domain
      });
      
      return true;
    } catch (error) {
      console.error(`Error registering tool ${tool?.id || 'unknown'}:`, error);
      throw error;
    }
  }
  
  /**
   * Unregister a tool from the ToolManager
   * @param {string} toolId - ID of the tool to unregister
   * @returns {Promise<boolean>} - True if unregistration was successful
   */
  async unregisterTool(toolId) {
    try {
      if (!this.registry.has(toolId)) {
        console.warn(`Tool with ID ${toolId} is not registered`);
        return false;
      }
      
      // Get tool information before unregistering
      const tool = this.registry.get(toolId);
      
      // Unregister the tool
      this.registry.delete(toolId);
      
      console.log(`Unregistered tool: ${tool.name} (${toolId})`);
      
      // Emit tool unregistered event
      this.emit('tool-unregistered', {
        toolId,
        toolName: tool.name,
        domain: tool.domain
      });
      
      return true;
    } catch (error) {
      console.error(`Error unregistering tool ${toolId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get a tool by ID
   * @param {string} toolId - ID of the tool to get
   * @returns {Object|null} - Tool definition or null if not found
   */
  getTool(toolId) {
    return this.registry.get(toolId) || null;
  }
  
  /**
   * Get all registered tools
   * @param {Object} filters - Optional filters
   * @param {string} filters.domain - Filter by domain
   * @param {string} filters.category - Filter by category
   * @param {string} filters.query - Search query for tool name or description
   * @returns {Array<Object>} - Array of tool definitions
   */
  getTools(filters = {}) {
    try {
      let tools = Array.from(this.registry.values());
      
      // Apply domain filter
      if (filters.domain) {
        tools = tools.filter(tool => tool.domain === filters.domain);
      }
      
      // Apply category filter
      if (filters.category) {
        tools = tools.filter(tool => tool.category === filters.category);
      }
      
      // Apply search query
      if (filters.query) {
        const query = filters.query.toLowerCase();
        tools = tools.filter(tool => 
          tool.name.toLowerCase().includes(query) || 
          (tool.description && tool.description.toLowerCase().includes(query))
        );
      }
      
      return tools;
    } catch (error) {
      console.error('Error getting tools:', error);
      throw error;
    }
  }
  
  /**
   * Get all available domains
   * @returns {Array<string>} - Array of domain names
   */
  getDomains() {
    return Array.from(this.domainProviders.keys());
  }
  
  /**
   * Get tools by domain
   * @param {string} domain - Domain to get tools for
   * @returns {Array<Object>} - Array of tool definitions
   */
  getToolsByDomain(domain) {
    return this.getTools({ domain });
  }
  
  /**
   * Execute a tool
   * @param {string} toolId - ID of the tool to execute
   * @param {Object} params - Parameters for the tool
   * @param {Object} context - Execution context
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} - Execution result
   */
  async executeTool(toolId, params = {}, context = {}, options = {}) {
    const executionId = uuidv4();
    const startTime = Date.now();
    
    try {
      // Check if we're at max concurrent executions
      if (this.activeExecutions >= this.options.maxConcurrentExecutions) {
        throw new Error('Maximum concurrent executions reached');
      }
      
      // Get the tool
      const tool = this.getTool(toolId);
      if (!tool) {
        throw new Error(`Tool not found: ${toolId}`);
      }
      
      // Check cache if enabled
      const cacheKey = this._generateCacheKey(toolId, params);
      if (this.options.cacheResults && this.resultCache.has(cacheKey)) {
        const cachedResult = this.resultCache.get(cacheKey);
        
        // Check if cache is still valid
        if (cachedResult.expiresAt > Date.now()) {
          console.log(`Using cached result for tool: ${tool.name} (${toolId})`);
          return { ...cachedResult.result, fromCache: true };
        }
        
        // Remove expired cache entry
        this.resultCache.delete(cacheKey);
      }
      
      // Perform safety checks
      await this._performSafetyChecks(tool, params, context);
      
      // Create execution record
      const execution = {
        id: executionId,
        toolId,
        toolName: tool.name,
        domain: tool.domain,
        params,
        context,
        startTime,
        status: 'running'
      };
      
      // Track execution
      this.executions.set(executionId, execution);
      this.activeExecutions++;
      
      // Emit execution started event
      this.emit('execution-started', {
        executionId,
        toolId,
        toolName: tool.name,
        domain: tool.domain,
        params
      });
      
      // Set timeout
      const timeout = options.timeout || tool.timeout || this.options.defaultTimeout;
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error(`Tool execution timed out after ${timeout}ms`));
        }, timeout);
      });
      
      // Execute the tool
      const executionPromise = tool.execute(params, context);
      
      // Wait for execution or timeout
      const result = await Promise.race([executionPromise, timeoutPromise]);
      
      // Validate result if enabled
      if (this.options.validateResults && tool.validate) {
        const validationResult = await tool.validate(result, params, context);
        if (!validationResult.valid) {
          throw new Error(`Tool result validation failed: ${validationResult.reason}`);
        }
      }
      
      // Update execution record
      const endTime = Date.now();
      const executionTime = endTime - startTime;
      
      execution.endTime = endTime;
      execution.executionTime = executionTime;
      execution.status = 'completed';
      execution.result = result;
      
      // Update metrics
      this._updateMetrics(tool, true, executionTime);
      
      // Cache result if enabled
      if (this.options.cacheResults && tool.cacheable !== false) {
        const cacheTtl = tool.cacheTtl || 60000; // Default: 1 minute
        this.resultCache.set(cacheKey, {
          result,
          createdAt: Date.now(),
          expiresAt: Date.now() + cacheTtl
        });
      }
      
      // Emit execution completed event
      this.emit('execution-completed', {
        executionId,
        toolId,
        toolName: tool.name,
        domain: tool.domain,
        executionTime,
        result
      });
      
      // Cleanup
      this.activeExecutions--;
      
      return result;
    } catch (error) {
      // Update execution record
      const execution = this.executions.get(executionId);
      if (execution) {
        execution.endTime = Date.now();
        execution.executionTime = Date.now() - startTime;
        execution.status = 'failed';
        execution.error = error.message;
      }
      
      // Update metrics
      const tool = this.getTool(toolId);
      if (tool) {
        this._updateMetrics(tool, false, Date.now() - startTime);
      }
      
      // Emit execution failed event
      this.emit('execution-failed', {
        executionId,
        toolId,
        error: error.message
      });
      
      // Cleanup
      this.activeExecutions--;
      
      throw error;
    }
  }
  
  /**
   * Perform safety checks before executing a tool
   * @param {Object} tool - Tool definition
   * @param {Object} params - Tool parameters
   * @param {Object} context - Execution context
   * @returns {Promise<void>}
   * @private
   */
  async _performSafetyChecks(tool, params, context) {
    // Check if tool is in blacklist
    if (this.safetyGuardrails.blacklistedOperations.has(tool.id)) {
      throw new Error(`Tool ${tool.id} is blacklisted`);
    }
    
    // Check if tool requires approval
    if (
      tool.requiresApproval ||
      this.safetyGuardrails.requireApprovalFor.has(tool.category) ||
      (tool.riskLevel && tool.riskLevel >= this.safetyGuardrails.riskThresholds.high)
    ) {
      // In a real implementation, this would check for approval
      // For now, we'll just log a warning
      console.warn(`Tool ${tool.id} requires approval`);
    }
    
    // Check consecutive failures
    const toolMetrics = this.metrics.toolUsage.get(tool.id);
    if (
      toolMetrics &&
      toolMetrics.consecutiveFailures >= this.safetyGuardrails.maxConsecutiveFailures
    ) {
      throw new Error(`Tool ${tool.id} has failed too many times consecutively`);
    }
    
    return true;
  }
  
  /**
   * Generate a cache key for a tool execution
   * @param {string} toolId - Tool ID
   * @param {Object} params - Tool parameters
   * @returns {string} - Cache key
   * @private
   */
  _generateCacheKey(toolId, params) {
    return `${toolId}:${JSON.stringify(params)}`;
  }
  
  /**
   * Update metrics after a tool execution
   * @param {Object} tool - Tool definition
   * @param {boolean} success - Whether the execution was successful
   * @param {number} executionTime - Execution time in milliseconds
   * @private
   */
  _updateMetrics(tool, success, executionTime) {
    // Update global metrics
    this.metrics.totalExecutions++;
    if (success) {
      this.metrics.successfulExecutions++;
    } else {
      this.metrics.failedExecutions++;
    }
    
    // Update average execution time
    const oldAvg = this.metrics.averageExecutionTime;
    const oldCount = this.metrics.totalExecutions - 1;
    this.metrics.averageExecutionTime = (oldAvg * oldCount + executionTime) / this.metrics.totalExecutions;
    
    // Update domain metrics
    if (!this.metrics.domainUsage.has(tool.domain)) {
      this.metrics.domainUsage.set(tool.domain, {
        executions: 0,
        successfulExecutions: 0,
        failedExecutions: 0,
        averageExecutionTime: 0
      });
    }
    
    const domainMetrics = this.metrics.domainUsage.get(tool.domain);
    domainMetrics.executions++;
    if (success) {
      domainMetrics.successfulExecutions++;
    } else {
      domainMetrics.failedExecutions++;
    }
    
    // Update domain average execution time
    const oldDomainAvg = domainMetrics.averageExecutionTime;
    const oldDomainCount = domainMetrics.executions - 1;
    domainMetrics.averageExecutionTime = (oldDomainAvg * oldDomainCount + executionTime) / domainMetrics.executions;
    
    // Update tool metrics
    if (!this.metrics.toolUsage.has(tool.id)) {
      this.metrics.toolUsage.set(tool.id, {
        executions: 0,
        successfulExecutions: 0,
        failedExecutions: 0,
        consecutiveFailures: 0,
        averageExecutionTime: 0,
        lastExecuted: null
      });
    }
    
    const toolMetrics = this.metrics.toolUsage.get(tool.id);
    toolMetrics.executions++;
    toolMetrics.lastExecuted = new Date();
    
    if (success) {
      toolMetrics.successfulExecutions++;
      toolMetrics.consecutiveFailures = 0;
    } else {
      toolMetrics.failedExecutions++;
      toolMetrics.consecutiveFailures++;
    }
    
    // Update tool success rate
    toolMetrics.successRate = toolMetrics.successfulExecutions / toolMetrics.executions;
    
    // Update tool average execution time
    const oldToolAvg = toolMetrics.averageExecutionTime;
    const oldToolCount = toolMetrics.executions - 1;
    toolMetrics.averageExecutionTime = (oldToolAvg * oldToolCount + executionTime) / toolMetrics.executions;
  }
  
  /**
   * Get metrics for all tools
   * @returns {Object} - Metrics
   */
  getMetrics() {
    return this.metrics;
  }
  
  /**
   * Get metrics for a specific tool
   * @param {string} toolId - Tool ID
   * @returns {Object} - Tool metrics
   */
  getToolMetrics(toolId) {
    return this.metrics.toolUsage.get(toolId) || null;
  }
  
  /**
   * Get metrics for a specific domain
   * @param {string} domain - Domain name
   * @returns {Object} - Domain metrics
   */
  getDomainMetrics(domain) {
    return this.metrics.domainUsage.get(domain) || null;
  }
  
  /**
   * Clear the result cache
   * @returns {number} - Number of cache entries cleared
   */
  clearCache() {
    const cacheSize = this.resultCache.size;
    this.resultCache.clear();
    return cacheSize;
  }
  
  /**
   * Shutdown the ToolManager
   * @returns {Promise<void>}
   */
  async shutdown() {
    try {
      console.log('Shutting down ToolManager');
      
      // Cancel all active executions
      for (const [executionId, execution] of this.executions.entries()) {
        if (execution.status === 'running') {
          execution.status = 'cancelled';
          execution.endTime = Date.now();
          execution.executionTime = execution.endTime - execution.startTime;
          
          this.emit('execution-cancelled', {
            executionId,
            toolId: execution.toolId,
            toolName: execution.toolName
          });
        }
      }
      
      // Shutdown domain providers
      for (const [domain, provider] of this.domainProviders.entries()) {
        if (provider.shutdown) {
          await provider.shutdown();
        }
      }
      
      // Clear cache
      this.clearCache();
      
      // Clear registries
      this.registry.clear();
      this.domainProviders.clear();
      this.executions.clear();
      
      console.log('ToolManager shutdown complete');
    } catch (error) {
      console.error('Error shutting down ToolManager:', error);
      throw error;
    }
  }
}

module.exports = { ToolManager };
