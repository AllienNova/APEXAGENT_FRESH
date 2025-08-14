/**
 * IDEIntegrationManager.js
 * 
 * Manages IDE integrations for Aideon AI Lite, allowing seamless operation
 * within various development environments like VS Code, Cursor, GitHub, etc.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const fs = require('fs').promises;
const path = require('path');
const { spawn, exec } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const WebSocket = require('ws');
const axios = require('axios');
const crypto = require('crypto');

class IDEIntegrationManager {
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger('ide:manager');
    this.config = core.configManager.getConfig().ide || {};
    this.integrations = new Map();
    this.activeConnections = new Map();
    this.extensionServers = new Map();
    this.securityManager = core.securityManager;
    this.supportedIDEs = ['vscode', 'cursor', 'github', 'intellij', 'pycharm', 'webstorm', 'atom', 'sublime'];
  }

  /**
   * Initialize the IDE Integration Manager
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    this.logger.info('Initializing IDE Integration Manager');
    
    try {
      // Load all IDE integration modules
      await this._loadIntegrationModules();
      
      // Initialize security for IDE connections
      await this._initializeSecurity();
      
      // Start extension servers for supported IDEs
      await this._startExtensionServers();
      
      this.logger.info(`IDE Integration Manager initialized with ${this.integrations.size} integrations`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize IDE Integration Manager: ${error.message}`, error);
      return false;
    }
  }

  /**
   * Load all IDE integration modules dynamically
   * @private
   */
  async _loadIntegrationModules() {
    const integrationDir = path.join(__dirname, 'integrations');
    
    try {
      // Ensure the integrations directory exists
      await fs.mkdir(integrationDir, { recursive: true });
      
      // Get all integration files
      const files = await fs.readdir(integrationDir);
      const integrationFiles = files.filter(file => file.endsWith('Integration.js'));
      
      for (const file of integrationFiles) {
        try {
          const IntegrationClass = require(path.join(integrationDir, file));
          const integration = new IntegrationClass(this.core);
          const ideName = integration.getIDEName().toLowerCase();
          
          if (this.supportedIDEs.includes(ideName)) {
            this.integrations.set(ideName, integration);
            this.logger.info(`Loaded integration for ${ideName}`);
          } else {
            this.logger.warn(`Skipping unsupported IDE integration: ${ideName}`);
          }
        } catch (error) {
          this.logger.error(`Failed to load integration from ${file}: ${error.message}`);
        }
      }
      
      this.logger.info(`Loaded ${this.integrations.size} IDE integrations`);
    } catch (error) {
      this.logger.error(`Error loading integration modules: ${error.message}`);
      throw error;
    }
  }

  /**
   * Initialize security for IDE connections
   * @private
   */
  async _initializeSecurity() {
    // Generate or load encryption keys for secure communication
    const keysDir = path.join(this.core.configManager.getConfigDir(), 'ide_keys');
    
    try {
      await fs.mkdir(keysDir, { recursive: true });
      
      // Check if keys exist, generate if not
      try {
        await fs.access(path.join(keysDir, 'private.pem'));
        await fs.access(path.join(keysDir, 'public.pem'));
        this.logger.info('Using existing IDE security keys');
      } catch (error) {
        // Generate new keys
        this.logger.info('Generating new IDE security keys');
        
        return new Promise((resolve, reject) => {
          exec('openssl genrsa -out private.pem 2048 && openssl rsa -in private.pem -pubout -out public.pem', 
            { cwd: keysDir }, 
            (error, stdout, stderr) => {
              if (error) {
                this.logger.error(`Failed to generate security keys: ${error.message}`);
                reject(error);
                return;
              }
              this.logger.info('Generated new IDE security keys successfully');
              resolve();
            }
          );
        });
      }
    } catch (error) {
      this.logger.error(`Error initializing security: ${error.message}`);
      throw error;
    }
  }

  /**
   * Start extension servers for supported IDEs
   * @private
   */
  async _startExtensionServers() {
    for (const [ideName, integration] of this.integrations.entries()) {
      try {
        if (typeof integration.startServer === 'function') {
          const port = await this._findAvailablePort(10000 + Math.floor(Math.random() * 1000));
          const server = await integration.startServer(port);
          this.extensionServers.set(ideName, { port, server });
          this.logger.info(`Started ${ideName} extension server on port ${port}`);
        }
      } catch (error) {
        this.logger.error(`Failed to start server for ${ideName}: ${error.message}`);
      }
    }
  }

  /**
   * Find an available port
   * @param {number} startPort - Port to start checking from
   * @returns {Promise<number>} Available port
   * @private
   */
  async _findAvailablePort(startPort) {
    return new Promise((resolve, reject) => {
      const server = require('net').createServer();
      server.on('error', () => {
        resolve(this._findAvailablePort(startPort + 1));
      });
      server.listen(startPort, () => {
        server.close(() => {
          resolve(startPort);
        });
      });
    });
  }

  /**
   * Connect to an IDE instance
   * @param {string} ideName - Name of the IDE to connect to
   * @param {Object} options - Connection options
   * @returns {Promise<Object>} Connection details
   */
  async connectToIDE(ideName, options = {}) {
    ideName = ideName.toLowerCase();
    
    if (!this.integrations.has(ideName)) {
      throw new Error(`Integration for ${ideName} not found`);
    }
    
    try {
      const integration = this.integrations.get(ideName);
      const connectionId = uuidv4();
      const connection = await integration.connect(options);
      
      this.activeConnections.set(connectionId, {
        ideName,
        connection,
        options,
        timestamp: Date.now()
      });
      
      this.logger.info(`Connected to ${ideName} with connection ID ${connectionId}`);
      
      return {
        connectionId,
        ideName,
        status: 'connected',
        capabilities: integration.getCapabilities()
      };
    } catch (error) {
      this.logger.error(`Failed to connect to ${ideName}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Disconnect from an IDE instance
   * @param {string} connectionId - ID of the connection to disconnect
   * @returns {Promise<boolean>} Success status
   */
  async disconnectFromIDE(connectionId) {
    if (!this.activeConnections.has(connectionId)) {
      throw new Error(`Connection ${connectionId} not found`);
    }
    
    try {
      const { ideName, connection } = this.activeConnections.get(connectionId);
      const integration = this.integrations.get(ideName);
      
      await integration.disconnect(connection);
      this.activeConnections.delete(connectionId);
      
      this.logger.info(`Disconnected from ${ideName} (connection ID: ${connectionId})`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to disconnect from IDE: ${error.message}`);
      throw error;
    }
  }

  /**
   * Execute an IDE-specific command
   * @param {string} connectionId - ID of the connection to use
   * @param {string} command - Command to execute
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   */
  async executeCommand(connectionId, command, params = {}) {
    if (!this.activeConnections.has(connectionId)) {
      throw new Error(`Connection ${connectionId} not found`);
    }
    
    try {
      const { ideName, connection } = this.activeConnections.get(connectionId);
      const integration = this.integrations.get(ideName);
      
      if (!integration.supportsCommand(command)) {
        throw new Error(`Command ${command} not supported by ${ideName}`);
      }
      
      const result = await integration.executeCommand(connection, command, params);
      
      this.logger.debug(`Executed command ${command} on ${ideName} (connection ID: ${connectionId})`);
      return result;
    } catch (error) {
      this.logger.error(`Failed to execute command ${command}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get the status of all IDE integrations
   * @returns {Object} Status of all integrations
   */
  getStatus() {
    const status = {
      activeConnections: this.activeConnections.size,
      integrations: {}
    };
    
    for (const [ideName, integration] of this.integrations.entries()) {
      status.integrations[ideName] = {
        available: true,
        version: integration.getVersion(),
        capabilities: integration.getCapabilities(),
        serverRunning: this.extensionServers.has(ideName)
      };
    }
    
    for (const ideName of this.supportedIDEs) {
      if (!this.integrations.has(ideName)) {
        status.integrations[ideName] = {
          available: false
        };
      }
    }
    
    return status;
  }

  /**
   * Install an IDE extension
   * @param {string} ideName - Name of the IDE
   * @param {Object} options - Installation options
   * @returns {Promise<Object>} Installation result
   */
  async installExtension(ideName, options = {}) {
    ideName = ideName.toLowerCase();
    
    if (!this.integrations.has(ideName)) {
      throw new Error(`Integration for ${ideName} not found`);
    }
    
    try {
      const integration = this.integrations.get(ideName);
      
      if (typeof integration.installExtension !== 'function') {
        throw new Error(`Extension installation not supported for ${ideName}`);
      }
      
      const result = await integration.installExtension(options);
      
      this.logger.info(`Installed extension for ${ideName}`);
      return result;
    } catch (error) {
      this.logger.error(`Failed to install extension for ${ideName}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get a list of supported IDEs
   * @returns {Array<string>} List of supported IDE names
   */
  getSupportedIDEs() {
    return [...this.supportedIDEs];
  }

  /**
   * Get capabilities of a specific IDE integration
   * @param {string} ideName - Name of the IDE
   * @returns {Object|null} Capabilities or null if not found
   */
  getIDECapabilities(ideName) {
    ideName = ideName.toLowerCase();
    
    if (!this.integrations.has(ideName)) {
      return null;
    }
    
    return this.integrations.get(ideName).getCapabilities();
  }

  /**
   * Register an event handler for IDE events
   * @param {string} connectionId - ID of the connection
   * @param {string} eventType - Type of event to listen for
   * @param {Function} handler - Event handler function
   * @returns {boolean} Success status
   */
  registerEventHandler(connectionId, eventType, handler) {
    if (!this.activeConnections.has(connectionId)) {
      throw new Error(`Connection ${connectionId} not found`);
    }
    
    try {
      const { ideName, connection } = this.activeConnections.get(connectionId);
      const integration = this.integrations.get(ideName);
      
      integration.registerEventHandler(connection, eventType, handler);
      
      this.logger.debug(`Registered handler for ${eventType} events on ${ideName} (connection ID: ${connectionId})`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to register event handler: ${error.message}`);
      throw error;
    }
  }

  /**
   * Shutdown the IDE Integration Manager
   * @returns {Promise<boolean>} Success status
   */
  async shutdown() {
    this.logger.info('Shutting down IDE Integration Manager');
    
    try {
      // Disconnect all active connections
      for (const connectionId of this.activeConnections.keys()) {
        try {
          await this.disconnectFromIDE(connectionId);
        } catch (error) {
          this.logger.warn(`Error disconnecting from IDE (connection ID: ${connectionId}): ${error.message}`);
        }
      }
      
      // Stop all extension servers
      for (const [ideName, { server }] of this.extensionServers.entries()) {
        try {
          if (server && typeof server.close === 'function') {
            await new Promise((resolve) => server.close(resolve));
            this.logger.info(`Stopped ${ideName} extension server`);
          }
        } catch (error) {
          this.logger.warn(`Error stopping ${ideName} extension server: ${error.message}`);
        }
      }
      
      this.logger.info('IDE Integration Manager shut down successfully');
      return true;
    } catch (error) {
      this.logger.error(`Error during IDE Integration Manager shutdown: ${error.message}`);
      return false;
    }
  }
}

module.exports = IDEIntegrationManager;
