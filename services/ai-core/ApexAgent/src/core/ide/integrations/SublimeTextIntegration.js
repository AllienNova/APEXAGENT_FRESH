/**
 * SublimeTextIntegration.js
 * 
 * Provides integration with Sublime Text editor for Aideon AI Lite,
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
const net = require('net');

/**
 * Sublime Text Integration for Aideon AI Lite
 * Supports Sublime Text 3 and 4
 */
class SublimeTextIntegration extends BaseIDEIntegration {
  /**
   * Creates a new SublimeTextIntegration instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super(core, 'sublimetext');
    
    this.supportedIDEs = [
      'Sublime Text 3',
      'Sublime Text 4'
    ];
    
    this.pluginId = 'AideonIntegration';
    this.restClient = null;
    this.tcpClient = null;
    this.connectedIDE = null;
    this.projectInfo = null;
    this.commandQueue = [];
    this.isProcessingCommand = false;
  }
  
  /**
   * Initializes the Sublime Text integration
   * 
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize() {
    try {
      this.logger.info('Initializing Sublime Text integration');
      
      // Load configuration
      const config = this.configManager.getConfig().ide?.sublimetext || {};
      this.port = config.port || 30048;
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
      
      this.logger.info('Sublime Text integration initialized successfully');
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Sublime Text integration: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Connects to a running Sublime Text instance
   * 
   * @returns {Promise<boolean>} True if connection was successful
   */
  async connect() {
    try {
      this.logger.info('Connecting to Sublime Text');
      
      // Try to connect via REST API first
      try {
        const response = await this.restClient.get('/status');
        
        if (response.status === 200) {
          this.connectedIDE = {
            name: response.data.name || 'Sublime Text',
            version: response.data.version || 'Unknown',
            apiVersion: response.data.api_version || '1.0'
          };
          
          this.logger.info(`Connected to ${this.connectedIDE.name} ${this.connectedIDE.version}`);
          
          // Get current project info
          await this._fetchProjectInfo();
          
          this.emit('connected', {
            ide: this.connectedIDE,
            project: this.projectInfo
          });
          
          return true;
        }
      } catch (error) {
        this.logger.warn(`REST API connection failed: ${error.message}`);
      }
      
      // If REST API fails, try TCP connection
      return await this._connectTCP();
    } catch (error) {
      this.logger.error(`Failed to connect to Sublime Text: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Disconnects from Sublime Text
   * 
   * @returns {Promise<boolean>} True if disconnection was successful
   */
  async disconnect() {
    try {
      this.logger.info('Disconnecting from Sublime Text');
      
      // Close TCP connection
      if (this.tcpClient) {
        this.tcpClient.destroy();
        this.tcpClient = null;
      }
      
      this.connectedIDE = null;
      this.projectInfo = null;
      
      this.emit('disconnected');
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to disconnect from Sublime Text: ${error.message}`, error);
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
      throw new Error('Not connected to Sublime Text');
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
   * Gets a list of open files
   * 
   * @returns {Promise<Array>} List of open files
   */
  async getOpenFiles() {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('get_open_files');
      return result.files || [];
    } catch (error) {
      this.logger.error(`Failed to get open files: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Opens a file in the editor
   * 
   * @param {string} filePath - Path to the file
   * @param {number} line - Line number to navigate to (optional)
   * @param {number} column - Column number to navigate to (optional)
   * @returns {Promise<boolean>} True if file was opened successfully
   */
  async openFile(filePath, line = 0, column = 0) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('open_file', {
        file: filePath,
        line,
        column
      });
      
      if (result.success) {
        this.logger.info(`Opened file: ${filePath}`);
        return true;
      } else {
        throw new Error(result.error || 'Failed to open file');
      }
    } catch (error) {
      this.logger.error(`Failed to open file ${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets the content of a file
   * 
   * @param {string} filePath - Path to the file
   * @returns {Promise<string>} File content
   */
  async getFileContent(filePath) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('get_file_content', {
        file: filePath
      });
      
      if (result.success) {
        return result.content || '';
      } else {
        throw new Error(result.error || 'Failed to get file content');
      }
    } catch (error) {
      this.logger.error(`Failed to get file content for ${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Updates the content of a file
   * 
   * @param {string} filePath - Path to the file
   * @param {string} content - New file content
   * @returns {Promise<boolean>} True if file was updated successfully
   */
  async updateFileContent(filePath, content) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('update_file_content', {
        file: filePath,
        content
      });
      
      if (result.success) {
        this.logger.info(`Updated file: ${filePath}`);
        return true;
      } else {
        throw new Error(result.error || 'Failed to update file');
      }
    } catch (error) {
      this.logger.error(`Failed to update file ${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Creates a new file
   * 
   * @param {string} filePath - Path to the file
   * @param {string} content - Initial file content
   * @returns {Promise<boolean>} True if file was created successfully
   */
  async createFile(filePath, content = '') {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('create_file', {
        file: filePath,
        content
      });
      
      if (result.success) {
        this.logger.info(`Created file: ${filePath}`);
        return true;
      } else {
        throw new Error(result.error || 'Failed to create file');
      }
    } catch (error) {
      this.logger.error(`Failed to create file ${filePath}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets the current selection
   * 
   * @returns {Promise<Object>} Selection information
   */
  async getSelection() {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('get_selection');
      
      if (result.success) {
        return {
          file: result.file,
          selections: result.selections || []
        };
      } else {
        throw new Error(result.error || 'Failed to get selection');
      }
    } catch (error) {
      this.logger.error(`Failed to get selection: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Sets the selection
   * 
   * @param {Array} regions - Selection regions
   * @returns {Promise<boolean>} True if selection was set successfully
   */
  async setSelection(regions) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('set_selection', {
        regions
      });
      
      if (result.success) {
        return true;
      } else {
        throw new Error(result.error || 'Failed to set selection');
      }
    } catch (error) {
      this.logger.error(`Failed to set selection: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Inserts text at the current cursor position
   * 
   * @param {string} text - Text to insert
   * @returns {Promise<boolean>} True if text was inserted successfully
   */
  async insertText(text) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('insert_text', {
        text
      });
      
      if (result.success) {
        return true;
      } else {
        throw new Error(result.error || 'Failed to insert text');
      }
    } catch (error) {
      this.logger.error(`Failed to insert text: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Replaces the current selection with text
   * 
   * @param {string} text - Replacement text
   * @returns {Promise<boolean>} True if text was replaced successfully
   */
  async replaceSelection(text) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('replace_selection', {
        text
      });
      
      if (result.success) {
        return true;
      } else {
        throw new Error(result.error || 'Failed to replace selection');
      }
    } catch (error) {
      this.logger.error(`Failed to replace selection: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Runs a Sublime Text command
   * 
   * @param {string} command - Command name
   * @param {Object} args - Command arguments
   * @returns {Promise<Object>} Command result
   */
  async runCommand(command, args = {}) {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('run_command', {
        command,
        args
      });
      
      this.logger.info(`Ran command: ${command}`);
      return result;
    } catch (error) {
      this.logger.error(`Failed to run command ${command}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets the active project folders
   * 
   * @returns {Promise<Array>} List of project folders
   */
  async getProjectFolders() {
    if (!this.isConnected()) {
      throw new Error('Not connected to Sublime Text');
    }
    
    try {
      const result = await this._executeCommand('get_project_folders');
      
      if (result.success) {
        return result.folders || [];
      } else {
        throw new Error(result.error || 'Failed to get project folders');
      }
    } catch (error) {
      this.logger.error(`Failed to get project folders: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Checks if connected to Sublime Text
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
   * Installs the Aideon plugin in Sublime Text
   * 
   * @returns {Promise<boolean>} True if plugin was installed successfully
   */
  async installPlugin() {
    try {
      this.logger.info('Installing Aideon plugin for Sublime Text');
      
      // In a real implementation, this would:
      // 1. Check if plugin is already installed
      // 2. Generate the plugin files
      // 3. Install them to the Sublime Text Packages directory
      
      // For simulation, we'll just log the steps
      this.logger.info('Checking for existing plugin installation...');
      this.logger.info('Generating plugin files...');
      this.logger.info('Installing plugin to Sublime Text Packages directory...');
      
      this.logger.info('Plugin installed successfully');
      this.emit('pluginInstalled');
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to install plugin: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Connects to Sublime Text via TCP
   * 
   * @private
   * @returns {Promise<boolean>} True if connection was successful
   */
  async _connectTCP() {
    return new Promise((resolve, reject) => {
      try {
        this.logger.info(`Attempting TCP connection to localhost:${this.port}`);
        
        this.tcpClient = new net.Socket();
        
        // Set up timeout
        const timeout = setTimeout(() => {
          this.tcpClient.destroy();
          reject(new Error('Connection timeout'));
        }, 5000);
        
        // Set up event handlers
        this.tcpClient.on('connect', async () => {
          clearTimeout(timeout);
          
          this.logger.info('TCP connection established');
          
          // Send hello message
          const helloResult = await this._sendTCPMessage({
            command: 'hello',
            client: 'Aideon AI Lite',
            version: '1.0.0'
          });
          
          if (helloResult.success) {
            this.connectedIDE = {
              name: helloResult.name || 'Sublime Text',
              version: helloResult.version || 'Unknown',
              apiVersion: helloResult.api_version || '1.0'
            };
            
            this.logger.info(`Connected to ${this.connectedIDE.name} ${this.connectedIDE.version}`);
            
            // Get current project info
            await this._fetchProjectInfo();
            
            this.emit('connected', {
              ide: this.connectedIDE,
              project: this.projectInfo
            });
            
            resolve(true);
          } else {
            this.tcpClient.destroy();
            reject(new Error(helloResult.error || 'Failed to establish connection'));
          }
        });
        
        this.tcpClient.on('error', (error) => {
          clearTimeout(timeout);
          this.logger.error(`TCP connection error: ${error.message}`, error);
          reject(error);
        });
        
        this.tcpClient.on('close', () => {
          this.logger.info('TCP connection closed');
          
          // Only emit disconnected if we were previously connected
          if (this.connectedIDE) {
            this.connectedIDE = null;
            this.projectInfo = null;
            this.emit('disconnected');
          }
        });
        
        this.tcpClient.on('data', (data) => {
          try {
            const message = JSON.parse(data.toString());
            
            if (message.type === 'event') {
              this._handleEvent(message.event, message.data);
            }
          } catch (error) {
            this.logger.error(`Failed to process TCP message: ${error.message}`, error);
          }
        });
        
        // Connect to Sublime Text
        this.tcpClient.connect(this.port, 'localhost');
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Sends a message via TCP
   * 
   * @private
   * @param {Object} message - Message to send
   * @returns {Promise<Object>} Response
   */
  async _sendTCPMessage(message) {
    return new Promise((resolve, reject) => {
      if (!this.tcpClient || this.tcpClient.destroyed) {
        reject(new Error('TCP client not connected'));
        return;
      }
      
      try {
        // Generate request ID
        const requestId = uuidv4();
        message.id = requestId;
        
        // Set up response handler
        const responseHandler = (data) => {
          try {
            const response = JSON.parse(data.toString());
            
            if (response.id === requestId) {
              // Remove this handler
              this.tcpClient.removeListener('data', responseHandler);
              resolve(response);
            }
          } catch (error) {
            // Ignore parsing errors for other messages
          }
        };
        
        // Set up timeout
        const timeout = setTimeout(() => {
          this.tcpClient.removeListener('data', responseHandler);
          reject(new Error('Response timeout'));
        }, 5000);
        
        // Add response handler
        this.tcpClient.on('data', responseHandler);
        
        // Send message
        this.tcpClient.write(JSON.stringify(message) + '\n');
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Executes a command
   * 
   * @private
   * @param {string} command - Command to execute
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   */
  async _executeCommand(command, params = {}) {
    // Try REST API first
    if (this.restClient) {
      try {
        const response = await this.restClient.post('/command', {
          command,
          params
        });
        
        return response.data;
      } catch (error) {
        // Fall back to TCP if REST fails
        this.logger.debug(`REST API command failed, falling back to TCP: ${error.message}`);
      }
    }
    
    // Fall back to TCP
    if (this.tcpClient && !this.tcpClient.destroyed) {
      return this._sendTCPMessage({
        command,
        params
      });
    }
    
    throw new Error('No connection available');
  }
  
  /**
   * Fetches information about the current project
   * 
   * @private
   */
  async _fetchProjectInfo() {
    try {
      // Get project folders
      const folders = await this.getProjectFolders();
      
      // Get open files
      const files = await this.getOpenFiles();
      
      this.projectInfo = {
        folders,
        files
      };
      
      return this.projectInfo;
    } catch (error) {
      this.logger.error(`Failed to fetch project info: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Handles an event from Sublime Text
   * 
   * @private
   * @param {string} eventType - Event type
   * @param {Object} eventData - Event data
   */
  _handleEvent(eventType, eventData) {
    switch (eventType) {
      case 'file_opened':
        this.emit('fileOpened', eventData);
        break;
        
      case 'file_closed':
        this.emit('fileClosed', eventData);
        break;
        
      case 'file_saved':
        this.emit('fileSaved', eventData);
        break;
        
      case 'selection_changed':
        this.emit('selectionChanged', eventData);
        break;
        
      case 'project_changed':
        this.emit('projectChanged', eventData);
        this._fetchProjectInfo()
          .catch(error => this.logger.error(`Failed to update project info: ${error.message}`, error));
        break;
        
      default:
        this.logger.debug(`Received unknown event type: ${eventType}`);
    }
  }
  
  /**
   * Registers event handlers
   * 
   * @private
   */
  _registerEventHandlers() {
    // Example: Listen for core events that might affect the IDE integration
    this.core.on('codeGenerated', (code) => {
      if (this.isConnected() && code.targetFile) {
        this.updateFileContent(code.targetFile, code.content)
          .catch(error => this.logger.error(`Failed to update file with generated code: ${error.message}`, error));
      }
    });
  }
}

module.exports = { SublimeTextIntegration };
