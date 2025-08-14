/**
 * UserDashboard.js
 * 
 * User dashboard for monitoring and controlling all tools and integrations in Aideon AI Lite.
 * Provides a comprehensive interface for users to manage, monitor, and configure the system.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const path = require('path');
const express = require('express');
const cors = require('cors');
const http = require('http');
const socketIo = require('socket.io');
const fs = require('fs').promises;

/**
 * User Dashboard for Aideon AI Lite
 */
class UserDashboard extends EventEmitter {
  /**
   * Creates a new UserDashboard instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super();
    
    this.core = core;
    this.logger = core.getLogManager().getLogger('user-dashboard');
    this.configManager = core.getConfigManager();
    
    this.app = null;
    this.server = null;
    this.io = null;
    
    this.port = 0;
    this.isRunning = false;
    this.clients = new Set();
    
    this.metrics = {
      toolUsage: {},
      modelUsage: {},
      systemResources: {
        cpu: 0,
        memory: 0,
        disk: 0
      },
      activeAgents: [],
      activeTools: []
    };
    
    // Bind methods
    this._handleConnection = this._handleConnection.bind(this);
    this._handleDisconnection = this._handleDisconnection.bind(this);
    this._handleClientMessage = this._handleClientMessage.bind(this);
    this._updateMetrics = this._updateMetrics.bind(this);
  }
  
  /**
   * Initializes the user dashboard
   * 
   * @param {Object} options - Initialization options
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize(options = {}) {
    try {
      this.logger.info('Initializing User Dashboard');
      
      // Get configuration
      const config = this.configManager.getConfig();
      this.port = options.port || config.dashboard?.port || 3000;
      
      // Create Express app
      this.app = express();
      
      // Configure middleware
      this.app.use(cors());
      this.app.use(express.json());
      this.app.use(express.urlencoded({ extended: true }));
      
      // Create HTTP server
      this.server = http.createServer(this.app);
      
      // Create Socket.IO server
      this.io = socketIo(this.server, {
        cors: {
          origin: '*',
          methods: ['GET', 'POST']
        }
      });
      
      // Set up static files
      const staticDir = path.join(this.configManager.getAppDir(), 'dashboard', 'public');
      const staticExists = await fs.stat(staticDir).catch(() => null);
      
      if (staticExists && staticExists.isDirectory()) {
        this.app.use(express.static(staticDir));
      } else {
        // Create dashboard directory if it doesn't exist
        await fs.mkdir(path.join(this.configManager.getAppDir(), 'dashboard', 'public'), { recursive: true });
        
        // Create basic index.html
        const indexPath = path.join(this.configManager.getAppDir(), 'dashboard', 'public', 'index.html');
        await fs.writeFile(indexPath, this._generateDefaultDashboard());
      }
      
      // Set up API routes
      this._setupApiRoutes();
      
      // Set up Socket.IO events
      this.io.on('connection', this._handleConnection);
      
      // Start metrics collection
      this._startMetricsCollection();
      
      // Register event listeners
      this._registerEventListeners();
      
      this.logger.info('User Dashboard initialized successfully');
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize User Dashboard: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Starts the user dashboard server
   * 
   * @returns {Promise<boolean>} True if server was started successfully
   */
  async start() {
    try {
      if (this.isRunning) {
        this.logger.info('User Dashboard is already running');
        return true;
      }
      
      // Start server
      await new Promise((resolve, reject) => {
        this.server.listen(this.port, () => {
          this.isRunning = true;
          this.logger.info(`User Dashboard server started on port ${this.port}`);
          resolve();
        });
        
        this.server.on('error', (error) => {
          reject(error);
        });
      });
      
      // Emit started event
      this.emit('started', { port: this.port });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to start User Dashboard server: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Stops the user dashboard server
   * 
   * @returns {Promise<boolean>} True if server was stopped successfully
   */
  async stop() {
    try {
      if (!this.isRunning) {
        this.logger.info('User Dashboard is not running');
        return true;
      }
      
      // Stop server
      await new Promise((resolve) => {
        this.server.close(() => {
          this.isRunning = false;
          this.logger.info('User Dashboard server stopped');
          resolve();
        });
      });
      
      // Clear clients
      this.clients.clear();
      
      // Emit stopped event
      this.emit('stopped');
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to stop User Dashboard server: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Gets the dashboard URL
   * 
   * @returns {string} Dashboard URL
   */
  getDashboardUrl() {
    return `http://localhost:${this.port}`;
  }
  
  /**
   * Broadcasts a message to all connected clients
   * 
   * @param {string} event - Event name
   * @param {Object} data - Event data
   */
  broadcast(event, data) {
    if (this.io) {
      this.io.emit(event, data);
    }
  }
  
  /**
   * Updates dashboard metrics
   * 
   * @param {string} category - Metric category
   * @param {string} key - Metric key
   * @param {*} value - Metric value
   */
  updateMetric(category, key, value) {
    if (!this.metrics[category]) {
      this.metrics[category] = {};
    }
    
    this.metrics[category][key] = value;
    
    // Broadcast metric update
    this.broadcast('metric:update', {
      category,
      key,
      value
    });
  }
  
  /**
   * Sets up API routes
   * 
   * @private
   */
  _setupApiRoutes() {
    // API routes
    const apiRouter = express.Router();
    
    // Get system status
    apiRouter.get('/status', (req, res) => {
      res.json({
        status: 'ok',
        version: this.configManager.getConfig().version,
        uptime: process.uptime()
      });
    });
    
    // Get metrics
    apiRouter.get('/metrics', (req, res) => {
      res.json(this.metrics);
    });
    
    // Get tools
    apiRouter.get('/tools', (req, res) => {
      const toolManager = this.core.getToolManager();
      
      if (!toolManager) {
        return res.status(404).json({ error: 'Tool Manager not available' });
      }
      
      const tools = toolManager.getAllTools();
      res.json(tools);
    });
    
    // Execute tool
    apiRouter.post('/tools/:toolId/execute', async (req, res) => {
      try {
        const { toolId } = req.params;
        const { params } = req.body;
        
        const toolManager = this.core.getToolManager();
        
        if (!toolManager) {
          return res.status(404).json({ error: 'Tool Manager not available' });
        }
        
        const result = await toolManager.executeTool(toolId, params);
        res.json({ success: true, result });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });
    
    // Get models
    apiRouter.get('/models', (req, res) => {
      const modelManager = this.core.getModelManager();
      
      if (!modelManager) {
        return res.status(404).json({ error: 'Model Manager not available' });
      }
      
      const models = modelManager.getAllModels();
      res.json(models);
    });
    
    // Get agents
    apiRouter.get('/agents', (req, res) => {
      const agentManager = this.core.getAgentManager();
      
      if (!agentManager) {
        return res.status(404).json({ error: 'Agent Manager not available' });
      }
      
      const agents = agentManager.getAllAgents();
      res.json(agents);
    });
    
    // Get plugins
    apiRouter.get('/plugins', (req, res) => {
      const pluginArchitecture = this.core.getPluginArchitecture();
      
      if (!pluginArchitecture) {
        return res.status(404).json({ error: 'Plugin Architecture not available' });
      }
      
      const plugins = pluginArchitecture.getAllPlugins();
      res.json(plugins);
    });
    
    // Activate plugin
    apiRouter.post('/plugins/:pluginId/activate', async (req, res) => {
      try {
        const { pluginId } = req.params;
        
        const pluginArchitecture = this.core.getPluginArchitecture();
        
        if (!pluginArchitecture) {
          return res.status(404).json({ error: 'Plugin Architecture not available' });
        }
        
        const result = await pluginArchitecture.activatePlugin(pluginId);
        res.json({ success: result });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });
    
    // Deactivate plugin
    apiRouter.post('/plugins/:pluginId/deactivate', async (req, res) => {
      try {
        const { pluginId } = req.params;
        
        const pluginArchitecture = this.core.getPluginArchitecture();
        
        if (!pluginArchitecture) {
          return res.status(404).json({ error: 'Plugin Architecture not available' });
        }
        
        const result = await pluginArchitecture.deactivatePlugin(pluginId);
        res.json({ success: result });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });
    
    // Get IDE integrations
    apiRouter.get('/ide-integrations', (req, res) => {
      const ideManager = this.core.getIDEIntegrationManager();
      
      if (!ideManager) {
        return res.status(404).json({ error: 'IDE Integration Manager not available' });
      }
      
      const integrations = ideManager.getAllIntegrations();
      res.json(integrations);
    });
    
    // Get configuration
    apiRouter.get('/config', (req, res) => {
      const config = this.configManager.getConfig();
      
      // Filter sensitive information
      const filteredConfig = { ...config };
      delete filteredConfig.secrets;
      delete filteredConfig.apiKeys;
      
      res.json(filteredConfig);
    });
    
    // Update configuration
    apiRouter.post('/config', async (req, res) => {
      try {
        const { path, value } = req.body;
        
        if (!path) {
          return res.status(400).json({ error: 'Path is required' });
        }
        
        await this.configManager.updateConfig(path, value);
        res.json({ success: true });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });
    
    // Get logs
    apiRouter.get('/logs', async (req, res) => {
      try {
        const { level = 'info', limit = 100 } = req.query;
        
        const logManager = this.core.getLogManager();
        
        if (!logManager) {
          return res.status(404).json({ error: 'Log Manager not available' });
        }
        
        const logs = await logManager.getLogs(level, parseInt(limit, 10));
        res.json(logs);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });
    
    // Mount API router
    this.app.use('/api', apiRouter);
    
    // Catch-all route for SPA
    this.app.get('*', (req, res) => {
      res.sendFile(path.join(this.configManager.getAppDir(), 'dashboard', 'public', 'index.html'));
    });
  }
  
  /**
   * Handles new Socket.IO connections
   * 
   * @private
   * @param {Object} socket - Socket.IO socket
   */
  _handleConnection(socket) {
    this.logger.debug(`New client connected: ${socket.id}`);
    
    // Add client to set
    this.clients.add(socket.id);
    
    // Send initial data
    socket.emit('init', {
      metrics: this.metrics,
      config: this.configManager.getConfig()
    });
    
    // Set up event handlers
    socket.on('disconnect', () => this._handleDisconnection(socket));
    socket.on('message', (data) => this._handleClientMessage(socket, data));
    
    // Emit connection event
    this.emit('client:connected', { socketId: socket.id });
  }
  
  /**
   * Handles Socket.IO disconnections
   * 
   * @private
   * @param {Object} socket - Socket.IO socket
   */
  _handleDisconnection(socket) {
    this.logger.debug(`Client disconnected: ${socket.id}`);
    
    // Remove client from set
    this.clients.delete(socket.id);
    
    // Emit disconnection event
    this.emit('client:disconnected', { socketId: socket.id });
  }
  
  /**
   * Handles client messages
   * 
   * @private
   * @param {Object} socket - Socket.IO socket
   * @param {Object} data - Message data
   */
  _handleClientMessage(socket, data) {
    try {
      const { type, payload } = data;
      
      this.logger.debug(`Received message from client ${socket.id}: ${type}`);
      
      switch (type) {
        case 'execute:tool':
          this._handleToolExecution(socket, payload);
          break;
          
        case 'update:config':
          this._handleConfigUpdate(socket, payload);
          break;
          
        case 'request:metrics':
          socket.emit('metrics', this.metrics);
          break;
          
        default:
          // Emit custom message event
          this.emit('client:message', { socketId: socket.id, type, payload });
          break;
      }
    } catch (error) {
      this.logger.error(`Error handling client message: ${error.message}`, error);
      socket.emit('error', { message: error.message });
    }
  }
  
  /**
   * Handles tool execution requests
   * 
   * @private
   * @param {Object} socket - Socket.IO socket
   * @param {Object} payload - Request payload
   */
  async _handleToolExecution(socket, payload) {
    try {
      const { toolId, params } = payload;
      
      if (!toolId) {
        throw new Error('Tool ID is required');
      }
      
      const toolManager = this.core.getToolManager();
      
      if (!toolManager) {
        throw new Error('Tool Manager not available');
      }
      
      const result = await toolManager.executeTool(toolId, params);
      
      socket.emit('execute:tool:result', {
        toolId,
        success: true,
        result
      });
    } catch (error) {
      socket.emit('execute:tool:result', {
        toolId: payload.toolId,
        success: false,
        error: error.message
      });
    }
  }
  
  /**
   * Handles configuration update requests
   * 
   * @private
   * @param {Object} socket - Socket.IO socket
   * @param {Object} payload - Request payload
   */
  async _handleConfigUpdate(socket, payload) {
    try {
      const { path, value } = payload;
      
      if (!path) {
        throw new Error('Path is required');
      }
      
      await this.configManager.updateConfig(path, value);
      
      socket.emit('update:config:result', {
        path,
        success: true
      });
      
      // Broadcast config update to all clients
      this.broadcast('config:updated', {
        path,
        value
      });
    } catch (error) {
      socket.emit('update:config:result', {
        path: payload.path,
        success: false,
        error: error.message
      });
    }
  }
  
  /**
   * Starts metrics collection
   * 
   * @private
   */
  _startMetricsCollection() {
    // Update metrics every 5 seconds
    setInterval(this._updateMetrics, 5000);
  }
  
  /**
   * Updates system metrics
   * 
   * @private
   */
  async _updateMetrics() {
    try {
      // Update system resources
      this._updateSystemResources();
      
      // Update tool usage
      this._updateToolUsage();
      
      // Update model usage
      this._updateModelUsage();
      
      // Update active agents
      this._updateActiveAgents();
      
      // Broadcast metrics update
      this.broadcast('metrics', this.metrics);
    } catch (error) {
      this.logger.error(`Error updating metrics: ${error.message}`, error);
    }
  }
  
  /**
   * Updates system resource metrics
   * 
   * @private
   */
  _updateSystemResources() {
    try {
      // CPU usage
      const cpuUsage = process.cpuUsage();
      const totalCpuUsage = (cpuUsage.user + cpuUsage.system) / 1000000; // Convert to seconds
      
      // Memory usage
      const memoryUsage = process.memoryUsage();
      const totalMemoryUsage = memoryUsage.rss / 1024 / 1024; // Convert to MB
      
      // Update metrics
      this.metrics.systemResources = {
        cpu: totalCpuUsage,
        memory: totalMemoryUsage,
        uptime: process.uptime()
      };
    } catch (error) {
      this.logger.error(`Error updating system resources: ${error.message}`, error);
    }
  }
  
  /**
   * Updates tool usage metrics
   * 
   * @private
   */
  _updateToolUsage() {
    try {
      const toolManager = this.core.getToolManager();
      
      if (!toolManager) {
        return;
      }
      
      // Get tool usage statistics
      const toolUsage = toolManager.getToolUsageStats();
      
      // Update metrics
      this.metrics.toolUsage = toolUsage;
      
      // Update active tools
      this.metrics.activeTools = toolManager.getActiveTools();
    } catch (error) {
      this.logger.error(`Error updating tool usage: ${error.message}`, error);
    }
  }
  
  /**
   * Updates model usage metrics
   * 
   * @private
   */
  _updateModelUsage() {
    try {
      const modelManager = this.core.getModelManager();
      
      if (!modelManager) {
        return;
      }
      
      // Get model usage statistics
      const modelUsage = modelManager.getModelUsageStats();
      
      // Update metrics
      this.metrics.modelUsage = modelUsage;
    } catch (error) {
      this.logger.error(`Error updating model usage: ${error.message}`, error);
    }
  }
  
  /**
   * Updates active agents metrics
   * 
   * @private
   */
  _updateActiveAgents() {
    try {
      const agentManager = this.core.getAgentManager();
      
      if (!agentManager) {
        return;
      }
      
      // Get active agents
      const activeAgents = agentManager.getActiveAgents();
      
      // Update metrics
      this.metrics.activeAgents = activeAgents;
    } catch (error) {
      this.logger.error(`Error updating active agents: ${error.message}`, error);
    }
  }
  
  /**
   * Registers event listeners
   * 
   * @private
   */
  _registerEventListeners() {
    try {
      // Listen for tool execution events
      const toolManager = this.core.getToolManager();
      
      if (toolManager) {
        toolManager.on('tool:executed', (data) => {
          this.broadcast('tool:executed', data);
        });
        
        toolManager.on('tool:failed', (data) => {
          this.broadcast('tool:failed', data);
        });
      }
      
      // Listen for agent events
      const agentManager = this.core.getAgentManager();
      
      if (agentManager) {
        agentManager.on('agent:started', (data) => {
          this.broadcast('agent:started', data);
        });
        
        agentManager.on('agent:stopped', (data) => {
          this.broadcast('agent:stopped', data);
        });
        
        agentManager.on('agent:message', (data) => {
          this.broadcast('agent:message', data);
        });
      }
      
      // Listen for plugin events
      const pluginArchitecture = this.core.getPluginArchitecture();
      
      if (pluginArchitecture) {
        pluginArchitecture.on('plugin:registered', (data) => {
          this.broadcast('plugin:registered', data);
        });
        
        pluginArchitecture.on('plugin:activated', (data) => {
          this.broadcast('plugin:activated', data);
        });
        
        pluginArchitecture.on('plugin:deactivated', (data) => {
          this.broadcast('plugin:deactivated', data);
        });
        
        pluginArchitecture.on('plugin:error', (data) => {
          this.broadcast('plugin:error', data);
        });
      }
    } catch (error) {
      this.logger.error(`Error registering event listeners: ${error.message}`, error);
    }
  }
  
  /**
   * Generates default dashboard HTML
   * 
   * @private
   * @returns {string} HTML content
   */
  _generateDefaultDashboard() {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aideon AI Lite Dashboard</title>
  <style>
    :root {
      --primary-color: #4a6cf7;
      --secondary-color: #6c757d;
      --success-color: #28a745;
      --danger-color: #dc3545;
      --warning-color: #ffc107;
      --info-color: #17a2b8;
      --light-color: #f8f9fa;
      --dark-color: #343a40;
      --background-color: #f5f7fb;
      --card-bg: #ffffff;
      --text-color: #212529;
      --border-color: #e9ecef;
    }
    
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 0;
      background-color: var(--background-color);
      color: var(--text-color);
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border-color);
    }
    
    .header h1 {
      margin: 0;
      color: var(--primary-color);
    }
    
    .header .status {
      display: flex;
      align-items: center;
    }
    
    .status-indicator {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-right: 8px;
    }
    
    .status-online {
      background-color: var(--success-color);
    }
    
    .status-offline {
      background-color: var(--danger-color);
    }
    
    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .card {
      background-color: var(--card-bg);
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
      padding: 20px;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .card:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .card h2 {
      margin-top: 0;
      font-size: 18px;
      color: var(--primary-color);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 10px;
      margin-bottom: 15px;
    }
    
    .card-content {
      min-height: 200px;
    }
    
    .metrics {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
    }
    
    .metric {
      flex: 1;
      min-width: 120px;
      background-color: var(--light-color);
      border-radius: 6px;
      padding: 15px;
      text-align: center;
    }
    
    .metric h3 {
      margin: 0;
      font-size: 14px;
      color: var(--secondary-color);
    }
    
    .metric p {
      margin: 10px 0 0;
      font-size: 24px;
      font-weight: bold;
      color: var(--primary-color);
    }
    
    .list {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    
    .list-item {
      padding: 10px 0;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .list-item:last-child {
      border-bottom: none;
    }
    
    .badge {
      padding: 5px 10px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: bold;
    }
    
    .badge-primary {
      background-color: var(--primary-color);
      color: white;
    }
    
    .badge-success {
      background-color: var(--success-color);
      color: white;
    }
    
    .badge-danger {
      background-color: var(--danger-color);
      color: white;
    }
    
    .badge-warning {
      background-color: var(--warning-color);
      color: var(--dark-color);
    }
    
    .badge-info {
      background-color: var(--info-color);
      color: white;
    }
    
    .chart-container {
      height: 200px;
      position: relative;
    }
    
    .logs {
      height: 300px;
      overflow-y: auto;
      background-color: var(--dark-color);
      color: var(--light-color);
      border-radius: 6px;
      padding: 15px;
      font-family: monospace;
      font-size: 12px;
    }
    
    .log-entry {
      margin-bottom: 5px;
      padding-bottom: 5px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .log-time {
      color: var(--info-color);
    }
    
    .log-level-info {
      color: var(--info-color);
    }
    
    .log-level-warn {
      color: var(--warning-color);
    }
    
    .log-level-error {
      color: var(--danger-color);
    }
    
    .actions {
      display: flex;
      gap: 10px;
      margin-top: 15px;
    }
    
    .btn {
      padding: 8px 15px;
      border-radius: 4px;
      border: none;
      cursor: pointer;
      font-weight: bold;
      transition: background-color 0.2s;
    }
    
    .btn-primary {
      background-color: var(--primary-color);
      color: white;
    }
    
    .btn-primary:hover {
      background-color: #3a5bd9;
    }
    
    .btn-secondary {
      background-color: var(--secondary-color);
      color: white;
    }
    
    .btn-secondary:hover {
      background-color: #5a6268;
    }
    
    .btn-danger {
      background-color: var(--danger-color);
      color: white;
    }
    
    .btn-danger:hover {
      background-color: #c82333;
    }
    
    .footer {
      text-align: center;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid var(--border-color);
      color: var(--secondary-color);
    }
    
    /* Loading spinner */
    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100px;
    }
    
    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid rgba(0, 0, 0, 0.1);
      border-radius: 50%;
      border-top-color: var(--primary-color);
      animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    /* Responsive */
    @media (max-width: 768px) {
      .dashboard-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Aideon AI Lite Dashboard</h1>
      <div class="status">
        <div class="status-indicator status-offline" id="status-indicator"></div>
        <span id="status-text">Connecting...</span>
      </div>
    </div>
    
    <div class="dashboard-grid">
      <!-- System Overview -->
      <div class="card">
        <h2>System Overview</h2>
        <div class="card-content">
          <div class="metrics">
            <div class="metric">
              <h3>CPU Usage</h3>
              <p id="cpu-usage">0%</p>
            </div>
            <div class="metric">
              <h3>Memory</h3>
              <p id="memory-usage">0 MB</p>
            </div>
            <div class="metric">
              <h3>Uptime</h3>
              <p id="uptime">0s</p>
            </div>
          </div>
          
          <div class="chart-container" id="system-chart">
            <div class="loading">
              <div class="spinner"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Active Agents -->
      <div class="card">
        <h2>Active Agents</h2>
        <div class="card-content">
          <ul class="list" id="agents-list">
            <li class="list-item">Loading agents...</li>
          </ul>
        </div>
      </div>
      
      <!-- Tools -->
      <div class="card">
        <h2>Tools</h2>
        <div class="card-content">
          <ul class="list" id="tools-list">
            <li class="list-item">Loading tools...</li>
          </ul>
          
          <div class="actions">
            <button class="btn btn-primary" id="refresh-tools">Refresh</button>
          </div>
        </div>
      </div>
      
      <!-- Models -->
      <div class="card">
        <h2>AI Models</h2>
        <div class="card-content">
          <ul class="list" id="models-list">
            <li class="list-item">Loading models...</li>
          </ul>
          
          <div class="chart-container" id="models-chart">
            <div class="loading">
              <div class="spinner"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Plugins -->
      <div class="card">
        <h2>Plugins</h2>
        <div class="card-content">
          <ul class="list" id="plugins-list">
            <li class="list-item">Loading plugins...</li>
          </ul>
          
          <div class="actions">
            <button class="btn btn-primary" id="refresh-plugins">Refresh</button>
            <button class="btn btn-secondary" id="install-plugin">Install New</button>
          </div>
        </div>
      </div>
      
      <!-- IDE Integrations -->
      <div class="card">
        <h2>IDE Integrations</h2>
        <div class="card-content">
          <ul class="list" id="ide-list">
            <li class="list-item">Loading IDE integrations...</li>
          </ul>
          
          <div class="actions">
            <button class="btn btn-primary" id="configure-ide">Configure</button>
          </div>
        </div>
      </div>
      
      <!-- System Logs -->
      <div class="card" style="grid-column: span 2;">
        <h2>System Logs</h2>
        <div class="card-content">
          <div class="logs" id="system-logs">
            <div class="log-entry">
              <span class="log-time">[00:00:00]</span>
              <span class="log-level-info">[INFO]</span>
              Connecting to Aideon AI Lite...
            </div>
          </div>
          
          <div class="actions">
            <button class="btn btn-primary" id="refresh-logs">Refresh</button>
            <button class="btn btn-secondary" id="clear-logs">Clear</button>
            <select id="log-level" class="btn btn-secondary">
              <option value="debug">Debug</option>
              <option value="info" selected>Info</option>
              <option value="warn">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    
    <div class="footer">
      <p>Aideon AI Lite Dashboard v1.0.0</p>
    </div>
  </div>
  
  <script src="/socket.io/socket.io.js"></script>
  <script>
    // Connect to Socket.IO server
    const socket = io();
    
    // DOM elements
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const cpuUsage = document.getElementById('cpu-usage');
    const memoryUsage = document.getElementById('memory-usage');
    const uptime = document.getElementById('uptime');
    const agentsList = document.getElementById('agents-list');
    const toolsList = document.getElementById('tools-list');
    const modelsList = document.getElementById('models-list');
    const pluginsList = document.getElementById('plugins-list');
    const ideList = document.getElementById('ide-list');
    const systemLogs = document.getElementById('system-logs');
    
    // Button handlers
    document.getElementById('refresh-tools').addEventListener('click', () => {
      fetchTools();
    });
    
    document.getElementById('refresh-plugins').addEventListener('click', () => {
      fetchPlugins();
    });
    
    document.getElementById('install-plugin').addEventListener('click', () => {
      alert('Plugin installation will be available in the next update.');
    });
    
    document.getElementById('configure-ide').addEventListener('click', () => {
      alert('IDE configuration will be available in the next update.');
    });
    
    document.getElementById('refresh-logs').addEventListener('click', () => {
      fetchLogs();
    });
    
    document.getElementById('clear-logs').addEventListener('click', () => {
      systemLogs.innerHTML = '';
    });
    
    document.getElementById('log-level').addEventListener('change', (e) => {
      fetchLogs(e.target.value);
    });
    
    // Socket.IO event handlers
    socket.on('connect', () => {
      statusIndicator.classList.remove('status-offline');
      statusIndicator.classList.add('status-online');
      statusText.textContent = 'Connected';
      
      addLogEntry('info', 'Connected to Aideon AI Lite');
    });
    
    socket.on('disconnect', () => {
      statusIndicator.classList.remove('status-online');
      statusIndicator.classList.add('status-offline');
      statusText.textContent = 'Disconnected';
      
      addLogEntry('error', 'Disconnected from Aideon AI Lite');
    });
    
    socket.on('init', (data) => {
      updateMetrics(data.metrics);
      
      addLogEntry('info', 'Received initial data from server');
      
      // Fetch data
      fetchAgents();
      fetchTools();
      fetchModels();
      fetchPlugins();
      fetchIDEIntegrations();
      fetchLogs();
    });
    
    socket.on('metrics', (data) => {
      updateMetrics(data);
    });
    
    socket.on('tool:executed', (data) => {
      addLogEntry('info', `Tool executed: ${data.toolId}`);
    });
    
    socket.on('tool:failed', (data) => {
      addLogEntry('error', `Tool failed: ${data.toolId} - ${data.error}`);
    });
    
    socket.on('agent:started', (data) => {
      addLogEntry('info', `Agent started: ${data.agentId}`);
      fetchAgents();
    });
    
    socket.on('agent:stopped', (data) => {
      addLogEntry('info', `Agent stopped: ${data.agentId}`);
      fetchAgents();
    });
    
    socket.on('plugin:registered', (data) => {
      addLogEntry('info', `Plugin registered: ${data.plugin.name}`);
      fetchPlugins();
    });
    
    socket.on('plugin:activated', (data) => {
      addLogEntry('info', `Plugin activated: ${data.plugin.name}`);
      fetchPlugins();
    });
    
    socket.on('plugin:deactivated', (data) => {
      addLogEntry('info', `Plugin deactivated: ${data.plugin.name}`);
      fetchPlugins();
    });
    
    socket.on('plugin:error', (data) => {
      addLogEntry('error', `Plugin error: ${data.error}`);
    });
    
    socket.on('error', (data) => {
      addLogEntry('error', `Error: ${data.message}`);
    });
    
    // Helper functions
    function updateMetrics(metrics) {
      if (metrics.systemResources) {
        cpuUsage.textContent = metrics.systemResources.cpu.toFixed(2) + ' s';
        memoryUsage.textContent = metrics.systemResources.memory.toFixed(2) + ' MB';
        uptime.textContent = formatTime(metrics.systemResources.uptime);
      }
    }
    
    function formatTime(seconds) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = Math.floor(seconds % 60);
      
      return [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        secs.toString().padStart(2, '0')
      ].join(':');
    }
    
    function addLogEntry(level, message) {
      const now = new Date();
      const timeString = [
        now.getHours().toString().padStart(2, '0'),
        now.getMinutes().toString().padStart(2, '0'),
        now.getSeconds().toString().padStart(2, '0')
      ].join(':');
      
      const logEntry = document.createElement('div');
      logEntry.className = 'log-entry';
      
      const timeSpan = document.createElement('span');
      timeSpan.className = 'log-time';
      timeSpan.textContent = \`[\${timeString}]\`;
      
      const levelSpan = document.createElement('span');
      levelSpan.className = \`log-level-\${level}\`;
      levelSpan.textContent = \`[\${level.toUpperCase()}]\`;
      
      logEntry.appendChild(timeSpan);
      logEntry.appendChild(document.createTextNode(' '));
      logEntry.appendChild(levelSpan);
      logEntry.appendChild(document.createTextNode(' ' + message));
      
      systemLogs.appendChild(logEntry);
      systemLogs.scrollTop = systemLogs.scrollHeight;
      
      // Limit log entries
      while (systemLogs.children.length > 100) {
        systemLogs.removeChild(systemLogs.firstChild);
      }
    }
    
    // API functions
    async function fetchAgents() {
      try {
        const response = await fetch('/api/agents');
        const agents = await response.json();
        
        if (agents.length === 0) {
          agentsList.innerHTML = '<li class="list-item">No active agents</li>';
          return;
        }
        
        agentsList.innerHTML = '';
        
        agents.forEach(agent => {
          const li = document.createElement('li');
          li.className = 'list-item';
          
          const nameSpan = document.createElement('span');
          nameSpan.textContent = agent.name;
          
          const statusBadge = document.createElement('span');
          statusBadge.className = \`badge badge-\${agent.status === 'active' ? 'success' : 'secondary'}\`;
          statusBadge.textContent = agent.status;
          
          li.appendChild(nameSpan);
          li.appendChild(statusBadge);
          
          agentsList.appendChild(li);
        });
      } catch (error) {
        console.error('Error fetching agents:', error);
        addLogEntry('error', \`Failed to fetch agents: \${error.message}\`);
      }
    }
    
    async function fetchTools() {
      try {
        const response = await fetch('/api/tools');
        const tools = await response.json();
        
        if (tools.length === 0) {
          toolsList.innerHTML = '<li class="list-item">No tools available</li>';
          return;
        }
        
        toolsList.innerHTML = '';
        
        tools.forEach(tool => {
          const li = document.createElement('li');
          li.className = 'list-item';
          
          const nameSpan = document.createElement('span');
          nameSpan.textContent = tool.name;
          
          const categoryBadge = document.createElement('span');
          categoryBadge.className = 'badge badge-primary';
          categoryBadge.textContent = tool.category;
          
          li.appendChild(nameSpan);
          li.appendChild(categoryBadge);
          
          toolsList.appendChild(li);
        });
      } catch (error) {
        console.error('Error fetching tools:', error);
        addLogEntry('error', \`Failed to fetch tools: \${error.message}\`);
      }
    }
    
    async function fetchModels() {
      try {
        const response = await fetch('/api/models');
        const models = await response.json();
        
        if (models.length === 0) {
          modelsList.innerHTML = '<li class="list-item">No models available</li>';
          return;
        }
        
        modelsList.innerHTML = '';
        
        models.forEach(model => {
          const li = document.createElement('li');
          li.className = 'list-item';
          
          const nameSpan = document.createElement('span');
          nameSpan.textContent = model.name;
          
          const providerBadge = document.createElement('span');
          providerBadge.className = 'badge badge-info';
          providerBadge.textContent = model.provider;
          
          li.appendChild(nameSpan);
          li.appendChild(providerBadge);
          
          modelsList.appendChild(li);
        });
      } catch (error) {
        console.error('Error fetching models:', error);
        addLogEntry('error', \`Failed to fetch models: \${error.message}\`);
      }
    }
    
    async function fetchPlugins() {
      try {
        const response = await fetch('/api/plugins');
        const plugins = await response.json();
        
        if (plugins.length === 0) {
          pluginsList.innerHTML = '<li class="list-item">No plugins installed</li>';
          return;
        }
        
        pluginsList.innerHTML = '';
        
        plugins.forEach(plugin => {
          const li = document.createElement('li');
          li.className = 'list-item';
          
          const nameSpan = document.createElement('span');
          nameSpan.textContent = \`\${plugin.name} v\${plugin.version}\`;
          
          const statusBadge = document.createElement('span');
          statusBadge.className = \`badge badge-\${plugin.status === 'activated' ? 'success' : 'secondary'}\`;
          statusBadge.textContent = plugin.status;
          
          li.appendChild(nameSpan);
          li.appendChild(statusBadge);
          
          pluginsList.appendChild(li);
        });
      } catch (error) {
        console.error('Error fetching plugins:', error);
        addLogEntry('error', \`Failed to fetch plugins: \${error.message}\`);
      }
    }
    
    async function fetchIDEIntegrations() {
      try {
        const response = await fetch('/api/ide-integrations');
        const integrations = await response.json();
        
        if (integrations.length === 0) {
          ideList.innerHTML = '<li class="list-item">No IDE integrations available</li>';
          return;
        }
        
        ideList.innerHTML = '';
        
        integrations.forEach(integration => {
          const li = document.createElement('li');
          li.className = 'list-item';
          
          const nameSpan = document.createElement('span');
          nameSpan.textContent = integration.name;
          
          const statusBadge = document.createElement('span');
          statusBadge.className = \`badge badge-\${integration.connected ? 'success' : 'secondary'}\`;
          statusBadge.textContent = integration.connected ? 'Connected' : 'Disconnected';
          
          li.appendChild(nameSpan);
          li.appendChild(statusBadge);
          
          ideList.appendChild(li);
        });
      } catch (error) {
        console.error('Error fetching IDE integrations:', error);
        addLogEntry('error', \`Failed to fetch IDE integrations: \${error.message}\`);
      }
    }
    
    async function fetchLogs(level = 'info') {
      try {
        const response = await fetch(\`/api/logs?level=\${level}&limit=100\`);
        const logs = await response.json();
        
        systemLogs.innerHTML = '';
        
        logs.forEach(log => {
          const logEntry = document.createElement('div');
          logEntry.className = 'log-entry';
          
          const timeSpan = document.createElement('span');
          timeSpan.className = 'log-time';
          timeSpan.textContent = \`[\${new Date(log.timestamp).toLocaleTimeString()}]\`;
          
          const levelSpan = document.createElement('span');
          levelSpan.className = \`log-level-\${log.level}\`;
          levelSpan.textContent = \`[\${log.level.toUpperCase()}]\`;
          
          logEntry.appendChild(timeSpan);
          logEntry.appendChild(document.createTextNode(' '));
          logEntry.appendChild(levelSpan);
          logEntry.appendChild(document.createTextNode(' ' + log.message));
          
          systemLogs.appendChild(logEntry);
        });
        
        systemLogs.scrollTop = systemLogs.scrollHeight;
      } catch (error) {
        console.error('Error fetching logs:', error);
        addLogEntry('error', \`Failed to fetch logs: \${error.message}\`);
      }
    }
  </script>
</body>
</html>
    `;
  }
}

module.exports = { UserDashboard };
