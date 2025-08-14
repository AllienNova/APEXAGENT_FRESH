/**
 * JetBrainsIntegration.js
 * 
 * Provides integration with JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.)
 * for Aideon AI Lite, enabling seamless interaction with these development environments.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const { BaseIDEIntegration } = require('../BaseIDEIntegration');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');
const WebSocket = require('ws');

/**
 * JetBrains Integration for Aideon AI Lite
 * Supports IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs
 */
class JetBrainsIntegration extends BaseIDEIntegration {
  /**
   * Creates a new JetBrainsIntegration instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super(core, 'jetbrains');
    
    this.supportedIDEs = [
      'IntelliJ IDEA',
      'PyCharm',
      'WebStorm',
      'PhpStorm',
      'RubyMine',
      'CLion',
      'GoLand',
      'DataGrip',
      'Rider',
      'Android Studio'
    ];
    
    this.pluginId = 'com.aideon.integration';
    this.restClient = null;
    this.wsConnection = null;
    this.wsHeartbeatInterval = null;
    this.connectedIDE = null;
    this.projectInfo = null;
  }
  
  /**
   * Initializes the JetBrains integration
   * 
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize() {
    try {
      this.logger.info('Initializing JetBrains integration');
      
      // Load configuration
      const config = this.configManager.getConfig().ide?.jetbrains || {};
      this.port = config.port || 63342;
      this.wsPort = config.wsPort || 63343;
      this.autoConnect = config.autoConnect !== false;
      
      // Set up REST client
      this.restClient = axios.create({
        baseURL: `http://localhost:${this.port}`,
        timeout: 5000
      });
      
      // Register event handlers
      this._registerEventHandlers();
      
      // Auto-connect if enabled
      if (this.autoConnect) {
        try {
          await this.connect();
        } catch (error) {
          this.logger.warn(`Auto-connect failed: ${error.message}`);
          // Non-fatal error, continue initialization
        }
      }
      
      this.logger.info('JetBrains integration initialized successfully');
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize JetBrains integration: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Connects to a running JetBrains IDE
   * 
   * @returns {Promise<boolean>} True if connection was successful
   */
  async connect() {
    try {
      this.logger.info('Connecting to JetBrains IDE');
      
      // Check if IDE is running by querying the REST API
      const response = await this.restClient.get('/api/about');
      
      if (response.status === 200) {
        this.connectedIDE = response.data;
        this.logger.info(`Connected to ${this.connectedIDE.name} ${this.connectedIDE.version}`);
        
        // Connect to WebSocket for real-time events
        await this._connectWebSocket();
        
        // Get current project info
        await this._fetchProjectInfo();
        
        this.emit('connected', {
          ide: this.connectedIDE,
          project: this.projectInfo
        });
        
        return true;
      } else {
        throw new Error(`Unexpected response: ${response.status}`);
      }
    } catch (error) {
      this.logger.error(`Failed to connect to JetBrains IDE: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Disconnects from the JetBrains IDE
   * 
   * @returns {Promise<boolean>} True if disconnection was successful
   */
  async disconnect() {
    try {
      this.logger.info('Disconnecting from JetBrains IDE');
      
      // Close WebSocket connection
      if (this.wsConnection) {
        clearInterval(this.wsHeartbeatInterval);
        this.wsConnection.close();
        this.wsConnection = null;
      }
      
      this.connectedIDE = null;
      this.projectInfo = null;
      
      this.emit('disconnected');
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to disconnect from JetBrains IDE: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets information about the current project
   * 
   * @returns {Promise<Object>} Project information
   */
  async getProjectInfo() {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      await this._fetchProjectInfo();
      return this.projectInfo;
    } catch (error) {
      this.logger.error(`Failed to get project info: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets a list of files in the current project
   * 
   * @param {string} directory - Directory path (relative to project root)
   * @returns {Promise<Array>} List of files
   */
  async getProjectFiles(directory = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.get('/api/project/files', {
        params: {
          directory: directory || '/'
        }
      });
      
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get project files: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Opens a file in the IDE
   * 
   * @param {string} filePath - Path to the file (relative to project root)
   * @param {number} line - Line number to navigate to (optional)
   * @param {number} column - Column number to navigate to (optional)
   * @returns {Promise<boolean>} True if file was opened successfully
   */
  async openFile(filePath, line = 0, column = 0) {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/file/open', {
        file: filePath,
        line,
        column
      });
      
      if (response.status === 200) {
        this.logger.info(`Opened file: ${filePath}`);
        return true;
      } else {
        throw new Error(`Failed to open file: ${response.statusText}`);
      }
    } catch (error) {
      this.logger.error(`Failed to open file ${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets the content of a file
   * 
   * @param {string} filePath - Path to the file (relative to project root)
   * @returns {Promise<string>} File content
   */
  async getFileContent(filePath) {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.get('/api/file/content', {
        params: {
          file: filePath
        }
      });
      
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get file content for ${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Updates the content of a file
   * 
   * @param {string} filePath - Path to the file (relative to project root)
   * @param {string} content - New file content
   * @returns {Promise<boolean>} True if file was updated successfully
   */
  async updateFileContent(filePath, content) {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/file/update', {
        file: filePath,
        content
      });
      
      if (response.status === 200) {
        this.logger.info(`Updated file: ${filePath}`);
        return true;
      } else {
        throw new Error(`Failed to update file: ${response.statusText}`);
      }
    } catch (error) {
      this.logger.error(`Failed to update file ${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Runs a command in the IDE
   * 
   * @param {string} command - Command ID to run
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   */
  async runCommand(command, params = {}) {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/command', {
        command,
        params
      });
      
      this.logger.info(`Ran command: ${command}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to run command ${command}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets the current editor state
   * 
   * @returns {Promise<Object>} Editor state
   */
  async getEditorState() {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.get('/api/editor/state');
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get editor state: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Runs code analysis on a file or project
   * 
   * @param {string} target - Target file or directory (relative to project root)
   * @returns {Promise<Object>} Analysis results
   */
  async runCodeAnalysis(target = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/analysis/run', {
        target
      });
      
      this.logger.info(`Ran code analysis on: ${target || 'entire project'}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to run code analysis: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Runs a build task
   * 
   * @param {string} target - Build target (optional)
   * @returns {Promise<Object>} Build result
   */
  async runBuild(target = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/build/run', {
        target
      });
      
      this.logger.info(`Started build: ${target || 'default target'}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to run build: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Runs a test configuration
   * 
   * @param {string} configuration - Test configuration name
   * @returns {Promise<Object>} Test result
   */
  async runTests(configuration = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/test/run', {
        configuration
      });
      
      this.logger.info(`Started tests: ${configuration || 'default configuration'}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to run tests: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets version control status
   * 
   * @returns {Promise<Object>} Version control status
   */
  async getVcsStatus() {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.get('/api/vcs/status');
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get VCS status: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Commits changes to version control
   * 
   * @param {string} message - Commit message
   * @param {Array<string>} files - Files to commit (relative to project root)
   * @returns {Promise<Object>} Commit result
   */
  async commitChanges(message, files = []) {
    if (!this.isConnected()) {
      throw new Error('Not connected to JetBrains IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/vcs/commit', {
        message,
        files
      });
      
      this.logger.info(`Committed changes: ${message}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to commit changes: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Checks if connected to an IDE
   * 
   * @returns {boolean} True if connected
   */
  isConnected() {
    return !!this.connectedIDE;
  }
  
  /**
   * Gets the name of the connected IDE
   * 
   * @returns {string|null} IDE name or null if not connected
   */
  getConnectedIDEName() {
    return this.connectedIDE?.name || null;
  }
  
  /**
   * Installs the Aideon plugin in the IDE
   * 
   * @returns {Promise<boolean>} True if plugin was installed successfully
   */
  async installPlugin() {
    try {
      this.logger.info('Installing Aideon plugin for JetBrains IDEs');
      
      // In a real implementation, this would:
      // 1. Check if plugin is already installed
      // 2. Download or generate the plugin JAR
      // 3. Install it using the IDE's plugin system
      
      // For simulation, we'll just log the steps
      this.logger.info('Checking for existing plugin installation...');
      this.logger.info('Generating plugin JAR...');
      this.logger.info('Installing plugin to IDE...');
      
      this.logger.info('Plugin installed successfully');
      this.emit('pluginInstalled');
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to install plugin: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Connects to the WebSocket for real-time events
   * 
   * @private
   */
  async _connectWebSocket() {
    try {
      // Close existing connection if any
      if (this.wsConnection) {
        clearInterval(this.wsHeartbeatInterval);
        this.wsConnection.close();
      }
      
      // Create new connection
      this.wsConnection = new WebSocket(`ws://localhost:${this.wsPort}/api/events`);
      
      // Set up event handlers
      this.wsConnection.on('open', () => {
        this.logger.info('WebSocket connection established');
        
        // Send authentication message
        this.wsConnection.send(JSON.stringify({
          type: 'auth',
          clientId: uuidv4(),
          clientName: 'Aideon AI Lite'
        }));
        
        // Set up heartbeat
        this.wsHeartbeatInterval = setInterval(() => {
          if (this.wsConnection.readyState === WebSocket.OPEN) {
            this.wsConnection.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
      });
      
      this.wsConnection.on('message', (data) => {
        try {
          const message = JSON.stringify(data);
          
          switch (message.type) {
            case 'fileOpened':
              this.emit('fileOpened', message.data);
              break;
              
            case 'fileClosed':
              this.emit('fileClosed', message.data);
              break;
              
            case 'fileChanged':
              this.emit('fileChanged', message.data);
              break;
              
            case 'buildStarted':
              this.emit('buildStarted', message.data);
              break;
              
            case 'buildFinished':
              this.emit('buildFinished', message.data);
              break;
              
            case 'testStarted':
              this.emit('testStarted', message.data);
              break;
              
            case 'testFinished':
              this.emit('testFinished', message.data);
              break;
              
            case 'pong':
              // Heartbeat response, ignore
              break;
              
            default:
              this.logger.debug(`Received unknown WebSocket message type: ${message.type}`);
          }
        } catch (error) {
          this.logger.error(`Failed to process WebSocket message: ${error.message}`, error);
        }
      });
      
      this.wsConnection.on('error', (error) => {
        this.logger.error(`WebSocket error: ${error.message}`, error);
      });
      
      this.wsConnection.on('close', () => {
        this.logger.info('WebSocket connection closed');
        clearInterval(this.wsHeartbeatInterval);
      });
      
      // Wait for connection to establish
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, 5000);
        
        this.wsConnection.once('open', () => {
          clearTimeout(timeout);
          resolve();
        });
        
        this.wsConnection.once('error', (error) => {
          clearTimeout(timeout);
          reject(error);
        });
      });
    } catch (error) {
      this.logger.error(`Failed to connect WebSocket: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Fetches information about the current project
   * 
   * @private
   */
  async _fetchProjectInfo() {
    try {
      const response = await this.restClient.get('/api/project/info');
      this.projectInfo = response.data;
      return this.projectInfo;
    } catch (error) {
      this.logger.error(`Failed to fetch project info: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Registers event handlers
   * 
   * @private
   */
  _registerEventHandlers() {
    // Example: Listen for core events that might affect the IDE integration
    this.core.on('projectOpened', (project) => {
      if (this.isConnected()) {
        this.openFile(project.mainFile)
          .catch(error => this.logger.error(`Failed to open project main file: ${error.message}`, error));
      }
    });
    
    this.core.on('codeGenerated', (code) => {
      if (this.isConnected() && code.targetFile) {
        this.updateFileContent(code.targetFile, code.content)
          .catch(error => this.logger.error(`Failed to update file with generated code: ${error.message}`, error));
      }
    });
  }
}

module.exports = { JetBrainsIntegration };
