/**
 * EclipseIntegration.js
 * 
 * Provides integration with Eclipse IDE for Aideon AI Lite,
 * enabling seamless interaction with this development environment.
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
 * Eclipse Integration for Aideon AI Lite
 * Supports Eclipse IDE and Eclipse-based environments
 */
class EclipseIntegration extends BaseIDEIntegration {
  /**
   * Creates a new EclipseIntegration instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super(core, 'eclipse');
    
    this.supportedIDEs = [
      'Eclipse IDE',
      'Eclipse JDT',
      'Eclipse CDT',
      'Eclipse PDT',
      'Spring Tool Suite',
      'Eclipse for Enterprise Java',
      'Eclipse for Web Developers',
      'Eclipse for Java EE Developers'
    ];
    
    this.pluginId = 'com.aideon.eclipse.integration';
    this.restClient = null;
    this.wsConnection = null;
    this.wsHeartbeatInterval = null;
    this.connectedIDE = null;
    this.workspaceInfo = null;
  }
  
  /**
   * Initializes the Eclipse integration
   * 
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize() {
    try {
      this.logger.info('Initializing Eclipse integration');
      
      // Load configuration
      const config = this.configManager.getConfig().ide?.eclipse || {};
      this.port = config.port || 8080;
      this.wsPort = config.wsPort || 8081;
      this.autoConnect = config.autoConnect !== false;
      
      // Set up REST client
      this.restClient = axios.create({
        baseURL: `http://localhost:${this.port}/aideon`,
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
      
      this.logger.info('Eclipse integration initialized successfully');
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Eclipse integration: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Connects to a running Eclipse IDE
   * 
   * @returns {Promise<boolean>} True if connection was successful
   */
  async connect() {
    try {
      this.logger.info('Connecting to Eclipse IDE');
      
      // Check if IDE is running by querying the REST API
      const response = await this.restClient.get('/api/status');
      
      if (response.status === 200) {
        this.connectedIDE = response.data;
        this.logger.info(`Connected to ${this.connectedIDE.name} ${this.connectedIDE.version}`);
        
        // Connect to WebSocket for real-time events
        await this._connectWebSocket();
        
        // Get current workspace info
        await this._fetchWorkspaceInfo();
        
        this.emit('connected', {
          ide: this.connectedIDE,
          workspace: this.workspaceInfo
        });
        
        return true;
      } else {
        throw new Error(`Unexpected response: ${response.status}`);
      }
    } catch (error) {
      this.logger.error(`Failed to connect to Eclipse IDE: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Disconnects from the Eclipse IDE
   * 
   * @returns {Promise<boolean>} True if disconnection was successful
   */
  async disconnect() {
    try {
      this.logger.info('Disconnecting from Eclipse IDE');
      
      // Close WebSocket connection
      if (this.wsConnection) {
        clearInterval(this.wsHeartbeatInterval);
        this.wsConnection.close();
        this.wsConnection = null;
      }
      
      this.connectedIDE = null;
      this.workspaceInfo = null;
      
      this.emit('disconnected');
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to disconnect from Eclipse IDE: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets information about the current workspace
   * 
   * @returns {Promise<Object>} Workspace information
   */
  async getWorkspaceInfo() {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      await this._fetchWorkspaceInfo();
      return this.workspaceInfo;
    } catch (error) {
      this.logger.error(`Failed to get workspace info: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets a list of projects in the current workspace
   * 
   * @returns {Promise<Array>} List of projects
   */
  async getProjects() {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.get('/api/projects');
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get projects: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets a list of files in a project
   * 
   * @param {string} projectName - Name of the project
   * @param {string} directory - Directory path (relative to project root)
   * @returns {Promise<Array>} List of files
   */
  async getProjectFiles(projectName, directory = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.get('/api/files', {
        params: {
          project: projectName,
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
   * @param {string} projectName - Name of the project
   * @param {string} filePath - Path to the file (relative to project root)
   * @param {number} line - Line number to navigate to (optional)
   * @returns {Promise<boolean>} True if file was opened successfully
   */
  async openFile(projectName, filePath, line = 0) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/file/open', {
        project: projectName,
        file: filePath,
        line
      });
      
      if (response.status === 200) {
        this.logger.info(`Opened file: ${projectName}/${filePath}`);
        return true;
      } else {
        throw new Error(`Failed to open file: ${response.statusText}`);
      }
    } catch (error) {
      this.logger.error(`Failed to open file ${projectName}/${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets the content of a file
   * 
   * @param {string} projectName - Name of the project
   * @param {string} filePath - Path to the file (relative to project root)
   * @returns {Promise<string>} File content
   */
  async getFileContent(projectName, filePath) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.get('/api/file/content', {
        params: {
          project: projectName,
          file: filePath
        }
      });
      
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get file content for ${projectName}/${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Updates the content of a file
   * 
   * @param {string} projectName - Name of the project
   * @param {string} filePath - Path to the file (relative to project root)
   * @param {string} content - New file content
   * @returns {Promise<boolean>} True if file was updated successfully
   */
  async updateFileContent(projectName, filePath, content) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/file/update', {
        project: projectName,
        file: filePath,
        content
      });
      
      if (response.status === 200) {
        this.logger.info(`Updated file: ${projectName}/${filePath}`);
        return true;
      } else {
        throw new Error(`Failed to update file: ${response.statusText}`);
      }
    } catch (error) {
      this.logger.error(`Failed to update file ${projectName}/${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Creates a new file
   * 
   * @param {string} projectName - Name of the project
   * @param {string} filePath - Path to the file (relative to project root)
   * @param {string} content - Initial file content
   * @returns {Promise<boolean>} True if file was created successfully
   */
  async createFile(projectName, filePath, content = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/file/create', {
        project: projectName,
        file: filePath,
        content
      });
      
      if (response.status === 200 || response.status === 201) {
        this.logger.info(`Created file: ${projectName}/${filePath}`);
        return true;
      } else {
        throw new Error(`Failed to create file: ${response.statusText}`);
      }
    } catch (error) {
      this.logger.error(`Failed to create file ${projectName}/${filePath}: ${error.message}`, error);
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
      throw new Error('Not connected to Eclipse IDE');
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
      throw new Error('Not connected to Eclipse IDE');
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
   * @param {string} projectName - Name of the project
   * @param {string} target - Target file or directory (relative to project root)
   * @returns {Promise<Object>} Analysis results
   */
  async runCodeAnalysis(projectName, target = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/analysis/run', {
        project: projectName,
        target
      });
      
      this.logger.info(`Ran code analysis on: ${projectName}/${target || 'entire project'}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to run code analysis: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Runs a build task
   * 
   * @param {string} projectName - Name of the project
   * @param {string} target - Build target (optional)
   * @returns {Promise<Object>} Build result
   */
  async runBuild(projectName, target = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/build/run', {
        project: projectName,
        target
      });
      
      this.logger.info(`Started build for ${projectName}: ${target || 'default target'}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to run build: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Runs a test configuration
   * 
   * @param {string} projectName - Name of the project
   * @param {string} configuration - Test configuration name
   * @returns {Promise<Object>} Test result
   */
  async runTests(projectName, configuration = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/test/run', {
        project: projectName,
        configuration
      });
      
      this.logger.info(`Started tests for ${projectName}: ${configuration || 'default configuration'}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to run tests: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets version control status
   * 
   * @param {string} projectName - Name of the project
   * @returns {Promise<Object>} Version control status
   */
  async getVcsStatus(projectName) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.get('/api/vcs/status', {
        params: {
          project: projectName
        }
      });
      
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get VCS status: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Commits changes to version control
   * 
   * @param {string} projectName - Name of the project
   * @param {string} message - Commit message
   * @param {Array<string>} files - Files to commit (relative to project root)
   * @returns {Promise<Object>} Commit result
   */
  async commitChanges(projectName, message, files = []) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/vcs/commit', {
        project: projectName,
        message,
        files
      });
      
      this.logger.info(`Committed changes for ${projectName}: ${message}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to commit changes: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Creates a new project
   * 
   * @param {string} projectName - Name of the project
   * @param {string} projectType - Type of project (e.g., 'java', 'cpp', 'web')
   * @param {Object} options - Project creation options
   * @returns {Promise<Object>} Project creation result
   */
  async createProject(projectName, projectType, options = {}) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Eclipse IDE');
    }
    
    try {
      const response = await this.restClient.post('/api/project/create', {
        name: projectName,
        type: projectType,
        options
      });
      
      this.logger.info(`Created ${projectType} project: ${projectName}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to create project: ${error.message}`, error);
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
      this.logger.info('Installing Aideon plugin for Eclipse IDE');
      
      // In a real implementation, this would:
      // 1. Check if plugin is already installed
      // 2. Download or generate the plugin JAR
      // 3. Install it using the Eclipse p2 update system
      
      // For simulation, we'll just log the steps
      this.logger.info('Checking for existing plugin installation...');
      this.logger.info('Generating plugin bundle...');
      this.logger.info('Installing plugin to Eclipse...');
      
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
      this.wsConnection = new WebSocket(`ws://localhost:${this.wsPort}/aideon/events`);
      
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
              
            case 'projectCreated':
              this.emit('projectCreated', message.data);
              break;
              
            case 'projectClosed':
              this.emit('projectClosed', message.data);
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
   * Fetches information about the current workspace
   * 
   * @private
   */
  async _fetchWorkspaceInfo() {
    try {
      const response = await this.restClient.get('/api/workspace/info');
      this.workspaceInfo = response.data;
      return this.workspaceInfo;
    } catch (error) {
      this.logger.error(`Failed to fetch workspace info: ${error.message}`, error);
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
      if (this.isConnected() && project.eclipseProject) {
        this.openFile(project.eclipseProject, project.mainFile)
          .catch(error => this.logger.error(`Failed to open project main file: ${error.message}`, error));
      }
    });
    
    this.core.on('codeGenerated', (code) => {
      if (this.isConnected() && code.eclipseProject && code.targetFile) {
        this.updateFileContent(code.eclipseProject, code.targetFile, code.content)
          .catch(error => this.logger.error(`Failed to update file with generated code: ${error.message}`, error));
      }
    });
  }
}

module.exports = { EclipseIntegration };
